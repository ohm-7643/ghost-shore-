"""Local smoke tests for the dependency-free Ghost Shore explorer."""

from __future__ import annotations

import hashlib
import json
import os
import threading
import unittest
import tempfile
from http.server import ThreadingHTTPServer
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from src.ghost_shore_web import ExplorerHandler, PROJECT_ROOT, load_candidates


class GhostShoreWebTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), ExplorerHandler)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.base_url = f"http://127.0.0.1:{cls.server.server_port}"

    @classmethod
    def tearDownClass(cls) -> None:
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=2)

    def get(self, path: str):
        return urlopen(self.base_url + path, timeout=5)

    def test_annotations_load_from_project_root_and_keep_review_status(self) -> None:
        candidates = load_candidates()
        self.assertEqual(
            {candidate["candidate_id"] for candidate in candidates},
            {"GS-1854-001", "GS-1854-002", "GS-1854-003"},
        )
        self.assertTrue(all(candidate["review_status"] == "pending_human_review" for candidate in candidates))

    def test_data_paths_do_not_depend_on_current_working_directory(self) -> None:
        original = Path.cwd()
        with tempfile.TemporaryDirectory(prefix="ghost-shore-cwd-") as temporary:
            try:
                os.chdir(temporary)
                self.assertEqual(len(load_candidates()), 3)
            finally:
                os.chdir(original)

    def test_root_and_frontend_assets_are_served(self) -> None:
        for path, expected in (
            ("/", "Ghost Shore"),
            ("/styles.css", "--paper"),
            ("/app.js", "refreshCatalog"),
        ):
            with self.subTest(path=path), self.get(path) as response:
                self.assertEqual(response.status, 200)
                self.assertIn(expected, response.read().decode("utf-8"))

    def test_original_map_is_served_unchanged(self) -> None:
        original_path = PROJECT_ROOT / "data/raw/bangalore_1854.jpg"
        original_digest = hashlib.sha256(original_path.read_bytes()).hexdigest()
        with self.get("/historical-map") as response:
            image_bytes = response.read()
            self.assertEqual(response.headers.get_content_type(), "image/jpeg")
        self.assertEqual(hashlib.sha256(image_bytes).hexdigest(), original_digest)

    def test_candidate_endpoint_returns_existing_source_coordinates(self) -> None:
        with self.get("/api/candidates") as response:
            payload = json.loads(response.read())
        self.assertEqual(len(payload["candidates"]), 3)
        self.assertEqual(payload["candidates"][1]["bbox_xyxy"], [185, 1165, 300, 1255])

    def test_catalog_api_search_and_filters(self) -> None:
        with self.get("/api/catalog?q=Lalbagh") as response:
            searched = json.loads(response.read())
        self.assertEqual([feature["feature_id"] for feature in searched["features"]], ["GS-1854-002"])
        with self.get("/api/catalog?category=tank&review_status=pending_human_review") as response:
            filtered = json.loads(response.read())
        self.assertEqual(filtered["total"], 3)
        self.assertTrue(all(feature["category"] == "tank" for feature in filtered["features"]))
        self.assertFalse(any("latitude" in feature or "longitude" in feature for feature in filtered["features"]))

    def test_catalog_loading_accepts_milestone_5_1_evidence_needed_field(self) -> None:
        with self.get("/api/catalog") as response:
            payload = json.loads(response.read())
        self.assertEqual(payload["total"], 3)
        feature = next(item for item in payload["features"] if item["feature_id"] == "GS-1854-002")
        self.assertTrue(feature["evidence_needed"])
        self.assertEqual(feature["review_status"], "pending_human_review")

    def test_catalog_failure_does_not_hide_the_map_with_map_error_overlay(self) -> None:
        app_script = (PROJECT_ROOT / "web/app.js").read_text(encoding="utf-8")
        refresh_block = app_script.split("async function refreshCatalog()", 1)[1].split("function clearSelection()", 1)[0]
        self.assertNotIn("elements.mapError.classList.remove", refresh_block)

    def test_catalog_selection_api_returns_one_matching_entry(self) -> None:
        with self.get("/api/catalog/GS-1854-002") as response:
            payload = json.loads(response.read())
        feature = payload["feature"]
        self.assertEqual(feature["feature_id"], "GS-1854-002")
        self.assertEqual(feature["bbox_xyxy"], [185, 1165, 300, 1255])
        self.assertTrue(feature["evidence_needed"])
        self.assertTrue(feature["assistant_available"])

    def test_catalog_selection_rejects_unknown_id(self) -> None:
        with self.assertRaises(HTTPError) as caught:
            self.get("/api/catalog/GS-1854-999")
        self.assertEqual(caught.exception.code, 404)

    def test_local_evidence_endpoint_serves_allowlisted_project_files(self) -> None:
        with self.get("/local-evidence?path=docs%2Fcandidate_research.md") as response:
            body = response.read().decode("utf-8")
            self.assertEqual(response.headers.get_content_type(), "text/markdown")
        self.assertIn("GS-1854-002", body)
        with self.assertRaises(HTTPError) as caught:
            self.get("/local-evidence?path=..%2FREADME.md")
        self.assertEqual(caught.exception.code, 404)

    def test_explorer_has_region_inspection_and_guided_review_controls(self) -> None:
        with self.get("/") as response:
            page = response.read().decode("utf-8")
        self.assertIn("INSPECT THIS REGION", page)
        self.assertIn("Show full map", page)
        self.assertIn("Evidence still needed", page)
        self.assertIn("Checklist does not change review status", page)
        with self.get("/app.js") as response:
            script = response.read().decode("utf-8")
        self.assertIn("function inspectRegion(feature)", script)
        self.assertIn("ghost-shore:research-note:", script)

    def test_offline_assistant_endpoint_is_explicitly_demo_only(self) -> None:
        request = Request(
            self.base_url + "/api/assistant",
            data=json.dumps({"candidate_id": "GS-1854-002"}).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urlopen(request, timeout=10) as response:
            payload = json.loads(response.read())
        self.assertEqual(payload["mode"], "offline_demo")
        self.assertIn("not AI inference", payload["notice"])
        self.assertEqual(payload["result"]["source_supported_claims"][0]["support_status"],
                         "Exact text match in a user-supplied excerpt; URL and source content are not independently verified.")

    def test_assistant_rejects_unknown_candidate(self) -> None:
        request = Request(
            self.base_url + "/api/assistant",
            data=b'{"candidate_id":"GS-UNKNOWN"}',
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with self.assertRaises(HTTPError) as caught:
            urlopen(request, timeout=5)
        self.assertEqual(caught.exception.code, 400)

    def test_research_links_resolve_locally(self) -> None:
        with self.get("/georeferencing-validation") as response:
            notes = response.read().decode("utf-8")
        self.assertIn("No independent checkpoint has been verified", notes)
        self.assertTrue((PROJECT_ROOT / "web/index.html").is_file())

    def test_field_expedition_controls_safety_and_print_sheet(self) -> None:
        with self.get("/") as response:
            page = response.read().decode("utf-8")
        self.assertIn("field-expedition", page)
        self.assertIn("Ground-Truthing Bengaluru’s", page)
        self.assertIn("EPISTEMIC SAFEGUARD", page)
        self.assertIn("Map Annotations ≠ Modern Ground Truth", page)
        self.assertIn("Mandatory Field Safety Protocols", page)
        self.assertIn("Daylight visits only", page)
        self.assertIn("Public pathways only", page)
        self.assertIn("Never enter drains or canals", page)
        self.assertIn("Guided Field Observation Checklist", page)
        self.assertIn("field-note-form", page)
        self.assertIn("Save Field Note in Browser", page)
        self.assertIn("Print Field Sheet", page)

        with self.get("/app.js") as response:
            script = response.read().decode("utf-8")
        self.assertIn("FIELD_LEADS", script)
        self.assertIn("lead-lalbagh", script)
        self.assertIn("lead-ulsoor", script)
        self.assertIn("ghost-shore:field-note:", script)
        self.assertIn("ghost-shore:field-checks:", script)
        self.assertIn("renderPrintableFieldSheet", script)

        with self.get("/styles.css") as response:
            styles = response.read().decode("utf-8")
        self.assertIn(".expedition-section", styles)
        self.assertIn("@media print", styles)
        self.assertIn(".printable-field-sheet", styles)


if __name__ == "__main__":
    unittest.main()
