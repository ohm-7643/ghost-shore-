"""Dependency-free local web server for the Ghost Shore map explorer."""

from __future__ import annotations

import json
import subprocess
import sys
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, unquote, urlparse

try:  # Package import in tests versus direct script launch.
    from .feature_catalog import CATEGORIES, REVIEW_STATUSES, CatalogValidationError, filter_features, load_catalog
except ImportError:  # pragma: no cover - exercised by direct script launch
    from feature_catalog import CATEGORIES, REVIEW_STATUSES, CatalogValidationError, filter_features, load_catalog


PROJECT_ROOT = Path(__file__).resolve().parents[1]
WEB_ROOT = PROJECT_ROOT / "web"
ANNOTATIONS_PATH = PROJECT_ROOT / "outputs/milestone_1/candidate_annotations.json"
ASSISTANT_PATH = PROJECT_ROOT / "src/ghost_shore_assistant.py"
EXAMPLE_SOURCES = PROJECT_ROOT / "examples/lalbagh_source_excerpt.json"
MAP_PATH = PROJECT_ROOT / "data/raw/bangalore_1854.jpg"
GEOREFERENCE_NOTES = PROJECT_ROOT / "docs/georeferencing_validation.md"
LOCAL_EVIDENCE_FILES = {
    "data/raw/bangalore_1854.jpg": (MAP_PATH, "image/jpeg"),
    "outputs/milestone_1/candidate_annotations.json": (ANNOTATIONS_PATH, "application/json; charset=utf-8"),
    "docs/candidate_research.md": (PROJECT_ROOT / "docs/candidate_research.md", "text/markdown; charset=utf-8"),
}


def load_candidates() -> list[dict[str, Any]]:
    """Read the existing annotations without changing review state or files."""
    document = json.loads(ANNOTATIONS_PATH.read_text(encoding="utf-8"))
    candidates = document.get("candidates") if isinstance(document, dict) else None
    if not isinstance(candidates, list):
        raise ValueError("Candidate annotations do not contain a candidates list.")
    ids = [row.get("candidate_id") for row in candidates if isinstance(row, dict)]
    required = {"GS-1854-001", "GS-1854-002", "GS-1854-003"}
    if (
        len(ids) != len(candidates)
        or not all(isinstance(candidate_id, str) for candidate_id in ids)
        or len(set(ids)) != len(ids)
        or not required.issubset(ids)
    ):
        raise ValueError("Candidate annotations must retain the three initial IDs and contain no malformed or duplicate IDs.")
    return candidates


def search_catalog(query: str = "", category: str = "all", review_status: str = "all") -> dict[str, Any]:
    """Return filtered catalog features and whether the legacy assistant supports each."""
    catalog = load_catalog()
    features = filter_features(catalog["features"], query=query, category=category, review_status=review_status)
    legacy_ids = {row["candidate_id"] for row in load_candidates()}
    results = [dict(feature, assistant_available=feature["feature_id"] in legacy_ids) for feature in features]
    return {
        "features": results,
        "total": len(results),
        "catalog_total": len(catalog["features"]),
        "categories": sorted(CATEGORIES),
        "review_statuses": sorted(REVIEW_STATUSES),
        "source_map": catalog["source_map"],
    }


def select_feature(feature_id: str) -> dict[str, Any]:
    """Return one catalog feature by stable ID, or reject an unknown selection."""
    if not isinstance(feature_id, str):
        raise ValueError("Feature ID must be a string.")
    catalog = load_catalog()
    feature = next((entry for entry in catalog["features"] if entry["feature_id"] == feature_id), None)
    if feature is None:
        raise ValueError(f"No catalog feature exists with ID {feature_id!r}.")
    legacy_ids = {row["candidate_id"] for row in load_candidates()}
    return {**feature, "assistant_available": feature_id in legacy_ids}


def run_offline_assistant(candidate_id: str) -> dict[str, Any]:
    """Run the existing CLI in mock mode for an allow-listed candidate only."""
    allowed = {row["candidate_id"] for row in load_candidates()}
    if not isinstance(candidate_id, str) or candidate_id not in allowed:
        raise ValueError("Choose one of the three existing candidate IDs.")
    completed = subprocess.run(
        [
            sys.executable,
            str(ASSISTANT_PATH),
            candidate_id,
            "--sources-json",
            str(EXAMPLE_SOURCES),
            "--mock",
        ],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        timeout=15,
        check=False,
    )
    if completed.returncode != 0:
        # CLI errors are already sanitized; return a concise local error.
        message = completed.stderr.strip().splitlines()
        raise RuntimeError(message[-1] if message else "Offline assistant could not prepare a note.")
    try:
        result = json.loads(completed.stdout)
    except json.JSONDecodeError:
        raise RuntimeError("Offline assistant returned an unreadable response.") from None
    return {
        "mode": "offline_demo",
        "notice": "Offline preview only. This is a deterministic local mock, not AI inference.",
        "result": result,
    }


class ExplorerHandler(SimpleHTTPRequestHandler):
    """Serve the explorer, catalog APIs, and a small allowlist of local evidence."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, directory=str(WEB_ROOT), **kwargs)

    def log_message(self, format: str, *args: Any) -> None:
        """Keep local requests quiet; do not log prompt text or request bodies."""
        return

    def _send_json(self, payload: Any, status: int = 200) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:  # noqa: N802 - stdlib handler API
        path = urlparse(self.path).path
        if path == "/api/candidates":
            try:
                self._send_json({"candidates": load_candidates()})
            except (OSError, json.JSONDecodeError, ValueError) as exc:
                self._send_json({"error": str(exc)}, status=500)
            return
        if path == "/api/catalog":
            parameters = parse_qs(urlparse(self.path).query, keep_blank_values=True)
            unknown = set(parameters) - {"q", "category", "review_status"}
            if unknown:
                self._send_json({"error": "Supported filters are q, category, and review_status."}, status=400)
                return
            try:
                result = search_catalog(
                    query=parameters.get("q", [""])[-1],
                    category=parameters.get("category", ["all"])[-1],
                    review_status=parameters.get("review_status", ["all"])[-1],
                )
                self._send_json(result)
            except (OSError, json.JSONDecodeError, CatalogValidationError, ValueError) as exc:
                self._send_json({"error": str(exc)}, status=400)
            return
        if path.startswith("/api/catalog/"):
            feature_id = unquote(path.removeprefix("/api/catalog/"))
            try:
                self._send_json({"feature": select_feature(feature_id)})
            except ValueError as exc:
                self._send_json({"error": str(exc)}, status=404)
            except (OSError, json.JSONDecodeError, CatalogValidationError) as exc:
                self._send_json({"error": str(exc)}, status=400)
            return
        if path == "/historical-map":
            try:
                body = MAP_PATH.read_bytes()
            except OSError:
                self.send_error(404, "Historical map not found")
                return
            self.send_response(200)
            self.send_header("Content-Type", "image/jpeg")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "public, max-age=3600")
            self.end_headers()
            self.wfile.write(body)
            return
        if path == "/local-evidence":
            parameters = parse_qs(urlparse(self.path).query, keep_blank_values=True)
            source = parameters.get("path", [""])[-1].split("#", 1)[0]
            evidence = LOCAL_EVIDENCE_FILES.get(source)
            if evidence is None:
                self._send_json({"error": "This local evidence file is not on the approved source list."}, status=404)
                return
            evidence_path, content_type = evidence
            try:
                body = evidence_path.read_bytes()
            except OSError:
                self.send_error(404, "Local evidence file not found")
                return
            self.send_response(200)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Content-Disposition", "inline")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(body)
            return
        if path == "/georeferencing-validation":
            try:
                body = GEOREFERENCE_NOTES.read_bytes()
            except OSError:
                self.send_error(404, "Validation notes not found")
                return
            self.send_response(200)
            self.send_header("Content-Type", "text/markdown; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(body)
            return
        super().do_GET()

    def do_POST(self) -> None:  # noqa: N802 - stdlib handler API
        if urlparse(self.path).path != "/api/assistant":
            self._send_json({"error": "Endpoint not found."}, status=404)
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if length < 1 or length > 2048:
                raise ValueError("Request body must be between 1 and 2048 bytes.")
            body = json.loads(self.rfile.read(length))
            if not isinstance(body, dict) or set(body) != {"candidate_id"}:
                raise ValueError("Request must contain only candidate_id.")
            result = run_offline_assistant(body["candidate_id"])
        except (UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
            self._send_json({"error": str(exc)}, status=400)
            return
        except (OSError, RuntimeError, subprocess.TimeoutExpired):
            self._send_json({"error": "The local offline assistant could not prepare a note. Please try again."}, status=503)
            return
        self._send_json(result)



def main():
    import os

    port = int(os.environ.get("PORT", "8000"))
    server = ThreadingHTTPServer(("0.0.0.0", port), ExplorerHandler)

    print(f"Ghost Shore explorer listening on 0.0.0.0:{port}", flush=True)

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
