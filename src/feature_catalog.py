"""Dependency-free catalog migration, validation, search, and filtering."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path, PurePosixPath
from typing import Any, Iterable
from urllib.parse import urlparse


PROJECT_ROOT = Path(__file__).resolve().parents[1]
ANNOTATIONS_PATH = PROJECT_ROOT / "outputs/milestone_1/candidate_annotations.json"
CATALOG_PATH = PROJECT_ROOT / "data/catalog/features.json"
SCHEMA_PATH = PROJECT_ROOT / "data/catalog/catalog.schema.json"
SOURCE_IMAGE_PATH = "data/raw/bangalore_1854.jpg"
EXPECTED_DIMENSIONS = (1280, 1557)
FEATURE_ID_PATTERN = re.compile(r"^GS-1854-[0-9]{3,}$")
CATEGORIES = {"tank", "stream", "road", "garden", "settlement", "boundary", "other"}
REVIEW_STATUSES = {"pending_human_review", "reviewed", "rejected"}
EVIDENCE_STATUSES = {"unverified", "partially_supported", "supported"}
REFERENCE_STATUSES = {
    "annotation_pending_human_review",
    "source_scan_context_only",
    "research_note_unverified",
    "catalog_context_only",
}
TOP_FIELDS = {"schema_version", "source_map", "features"}
SOURCE_MAP_FIELDS = {"image_path", "width_px", "height_px", "coordinate_space", "sha256"}
FEATURE_FIELDS = {
    "feature_id",
    "display_name",
    "alternative_readings",
    "category",
    "annotation_confidence",
    "bbox_xyxy",
    "direct_observations",
    "interpretation",
    "uncertainty_notes",
    "evidence_needed",
    "evidence_status",
    "evidence_references",
    "review_status",
    "provenance",
    "annotation_history",
}
REFERENCE_FIELDS = {"reference_id", "source", "evidence_status", "scope_note"}
PROVENANCE_FIELDS = {"origin_annotation_file", "annotation_method"}
HISTORY_FIELDS = {"action", "source", "evidence_status", "note"}


class CatalogValidationError(ValueError):
    """Raised when a catalog or feature violates the catalog contract."""


def _require_string(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise CatalogValidationError(f"{label} must be a non-empty string.")
    return value


def _require_string_list(value: Any, label: str, *, non_empty: bool = False) -> list[str]:
    if not isinstance(value, list) or (non_empty and not value):
        suffix = " and must contain at least one item" if non_empty else ""
        raise CatalogValidationError(f"{label} must be an array{suffix}.")
    for index, item in enumerate(value, 1):
        _require_string(item, f"{label}[{index}]")
    return value


def _require_enum(value: Any, options: set[str], label: str) -> str:
    if not isinstance(value, str) or value not in options:
        raise CatalogValidationError(f"{label} must be one of: {', '.join(sorted(options))}.")
    return value


def _check_reference_source(source: str, label: str) -> None:
    parsed = urlparse(source)
    if parsed.scheme in {"http", "https"} and parsed.netloc and not any(ch.isspace() for ch in source):
        return
    if parsed.scheme:
        raise CatalogValidationError(f"{label} URL must be an absolute HTTP(S) URL.")
    path = PurePosixPath(source)
    if path.is_absolute() or ".." in path.parts or not path.parts:
        raise CatalogValidationError(f"{label} must be a project-relative path or absolute HTTP(S) URL.")


def validate_catalog(catalog: Any) -> dict[str, Any]:
    """Validate catalog structure, IDs, evidence status, and source-image boxes."""
    if not isinstance(catalog, dict) or set(catalog) != TOP_FIELDS:
        raise CatalogValidationError("Catalog must contain exactly schema_version, source_map, and features.")
    if type(catalog["schema_version"]) is not int or catalog["schema_version"] != 1:
        raise CatalogValidationError("Only catalog schema_version 1 is supported.")

    source_map = catalog["source_map"]
    if not isinstance(source_map, dict) or set(source_map) != SOURCE_MAP_FIELDS:
        raise CatalogValidationError("source_map has missing or unsupported fields.")
    if source_map["image_path"] != SOURCE_IMAGE_PATH:
        raise CatalogValidationError(f"source_map.image_path must be {SOURCE_IMAGE_PATH!r}.")
    if any(type(source_map[key]) is not int for key in ("width_px", "height_px")) or (source_map["width_px"], source_map["height_px"]) != EXPECTED_DIMENSIONS:
        raise CatalogValidationError(f"Source image dimensions must be {EXPECTED_DIMENSIONS[0]}×{EXPECTED_DIMENSIONS[1]} pixels.")
    if source_map["coordinate_space"] != "source_image_pixels_top_left_xyxy_exclusive":
        raise CatalogValidationError("source_map.coordinate_space must preserve original-image pixel coordinates.")
    digest = source_map["sha256"]
    if not isinstance(digest, str) or not re.fullmatch(r"[0-9a-f]{64}", digest):
        raise CatalogValidationError("source_map.sha256 must be a lowercase SHA-256 digest.")

    features = catalog["features"]
    if not isinstance(features, list):
        raise CatalogValidationError("features must be an array.")
    seen_ids: set[str] = set()
    for index, feature in enumerate(features, 1):
        label = f"features[{index}]"
        if not isinstance(feature, dict) or set(feature) != FEATURE_FIELDS:
            raise CatalogValidationError(f"{label} has missing or unsupported fields.")
        feature_id = _require_string(feature["feature_id"], f"{label}.feature_id")
        if not FEATURE_ID_PATTERN.fullmatch(feature_id):
            raise CatalogValidationError(f"{label}.feature_id must match GS-1854- followed by at least three digits.")
        if feature_id in seen_ids:
            raise CatalogValidationError(f"Duplicate feature ID: {feature_id}.")
        seen_ids.add(feature_id)
        _require_string(feature["display_name"], f"{label}.display_name")
        _require_string_list(feature["alternative_readings"], f"{label}.alternative_readings")
        _require_enum(feature["category"], CATEGORIES, f"{label}.category")
        _require_enum(feature["annotation_confidence"], {"low", "medium", "high"}, f"{label}.annotation_confidence")
        bbox = feature["bbox_xyxy"]
        if not isinstance(bbox, list) or len(bbox) != 4 or any(type(value) is not int for value in bbox):
            raise CatalogValidationError(f"{label}.bbox_xyxy must be four integer source-image pixel coordinates.")
        x1, y1, x2, y2 = bbox
        width, height = EXPECTED_DIMENSIONS
        if not (0 <= x1 < x2 <= width and 0 <= y1 < y2 <= height):
            raise CatalogValidationError(f"{label}.bbox_xyxy must be a non-empty box within the {width}×{height} source image.")
        _require_string_list(feature["direct_observations"], f"{label}.direct_observations", non_empty=True)
        _require_string(feature["interpretation"], f"{label}.interpretation")
        _require_string_list(feature["uncertainty_notes"], f"{label}.uncertainty_notes", non_empty=True)
        _require_string_list(feature["evidence_needed"], f"{label}.evidence_needed", non_empty=True)
        _require_enum(feature["evidence_status"], EVIDENCE_STATUSES, f"{label}.evidence_status")
        _require_enum(feature["review_status"], REVIEW_STATUSES, f"{label}.review_status")

        references = feature["evidence_references"]
        if not isinstance(references, list) or not references:
            raise CatalogValidationError(f"{label}.evidence_references must contain at least one reference.")
        reference_ids: set[str] = set()
        for ref_index, reference in enumerate(references, 1):
            ref_label = f"{label}.evidence_references[{ref_index}]"
            if not isinstance(reference, dict) or set(reference) != REFERENCE_FIELDS:
                raise CatalogValidationError(f"{ref_label} has missing or unsupported fields, including evidence_status.")
            reference_id = _require_string(reference["reference_id"], f"{ref_label}.reference_id")
            if reference_id in reference_ids:
                raise CatalogValidationError(f"Duplicate evidence reference ID {reference_id!r} in {feature_id}.")
            reference_ids.add(reference_id)
            source = _require_string(reference["source"], f"{ref_label}.source")
            _check_reference_source(source, f"{ref_label}.source")
            _require_enum(reference["evidence_status"], REFERENCE_STATUSES, f"{ref_label}.evidence_status")
            _require_string(reference["scope_note"], f"{ref_label}.scope_note")

        provenance = feature["provenance"]
        if not isinstance(provenance, dict) or set(provenance) != PROVENANCE_FIELDS:
            raise CatalogValidationError(f"{label}.provenance has missing or unsupported fields.")
        for field in PROVENANCE_FIELDS:
            _require_string(provenance[field], f"{label}.provenance.{field}")
        _check_reference_source(provenance["origin_annotation_file"], f"{label}.provenance.origin_annotation_file")

        history = feature["annotation_history"]
        if not isinstance(history, list) or not history:
            raise CatalogValidationError(f"{label}.annotation_history must contain at least one provenance event.")
        for event_index, event in enumerate(history, 1):
            event_label = f"{label}.annotation_history[{event_index}]"
            if not isinstance(event, dict) or set(event) != HISTORY_FIELDS:
                raise CatalogValidationError(f"{event_label} has missing or unsupported fields, including evidence_status.")
            for field in ("action", "source", "note"):
                _require_string(event[field], f"{event_label}.{field}")
            _check_reference_source(event["source"], f"{event_label}.source")
            _require_enum(event["evidence_status"], REFERENCE_STATUSES, f"{event_label}.evidence_status")
    return catalog


def build_initial_catalog(annotation_document: dict[str, Any]) -> dict[str, Any]:
    """Migrate the three existing annotations while retaining their core fields verbatim."""
    if not isinstance(annotation_document, dict) or not isinstance(annotation_document.get("candidates"), list):
        raise CatalogValidationError("Candidate annotations must contain a candidates array.")
    annotations = annotation_document["candidates"]
    expected_ids = {"GS-1854-001", "GS-1854-002", "GS-1854-003"}
    actual_ids = {item.get("candidate_id") for item in annotations if isinstance(item, dict)}
    if actual_ids != expected_ids or len(annotations) != 3:
        raise CatalogValidationError("Initial migration requires exactly the three existing candidate IDs.")

    candidate_notes = {
        "GS-1854-001": {
            "display_name": "Tank (unnamed)",
            "alternative_readings": ["“Tank” (generic printed label); no proper name recorded"],
            "uncertainty_notes": [
                "The label does not establish the feature's proper name, water extent, modern identity, or later history.",
                "The outline could delimit the labeled feature or a separate bounded area.",
            ],
            "evidence_needed": [
                "Compare the box with a higher-resolution scan of the same atlas sheet and its full surrounding context.",
                "Check an atlas legend or companion sheets for the cartographic convention used for tanks and boundaries.",
                "Seek a second dated map or archival record that links a distinct nearby toponym or landmark to this exact feature.",
            ],
        },
        "GS-1854-002": {
            "display_name": "Possible “Lalbagh Tank” label (uncertain)",
            "alternative_readings": [
                "“Lalbagh Tank” (proposed full reading; upper line uncertain)",
                "“Tank” (lower line appears legible; upper line unresolved)",
            ],
            "uncertainty_notes": [
                "The upper line is not securely transcribed; “Lalbagh” remains a possible reading.",
                "The reviewed 2012 article discusses 1791-map analysis and does not identify this specific 1854 feature.",
                "The outline could depict water, a bund, a parcel, or another boundary.",
            ],
            "evidence_needed": [
                "Compare the label with a high-resolution archival or atlas scan whose edition and sheet numbering are documented.",
                "Record a human transcription while retaining an ambiguous reading if letters remain unclear; do not use OCR as the deciding evidence.",
                "Compare multiple contemporaneous maps using independently identifiable landmarks and toponyms. The 2012 article is contextual evidence only and does not identify this 1854 feature.",
            ],
        },
        "GS-1854-003": {
            "display_name": "Tank (unnamed)",
            "alternative_readings": ["“Tank” (generic printed label); no proper name recorded"],
            "uncertainty_notes": [
                "The label does not establish whether the outline is a water edge, bund, precinct, or separate boundary.",
                "No distinct proper name or modern identity is established by the reviewed sources.",
            ],
            "evidence_needed": [
                "Review the same sheet at archival resolution and consult its map key or related sheets.",
                "Seek a second historical source that matches more than the generic word Tank, such as a distinctive name and the same adjacent roads, settlements, or fixed landmarks.",
            ],
        },
    }
    digest = annotation_document.get("source_sha256")
    actual_digest = hashlib.sha256((PROJECT_ROOT / SOURCE_IMAGE_PATH).read_bytes()).hexdigest()
    if digest != actual_digest:
        raise CatalogValidationError("Candidate annotation SHA-256 does not match the original historical map.")
    features: list[dict[str, Any]] = []
    for annotation in annotations:
        if not isinstance(annotation, dict):
            raise CatalogValidationError("Each existing annotation must be an object.")
        feature_id = annotation.get("candidate_id")
        details = candidate_notes[feature_id]
        features.append({
            "feature_id": feature_id,
            "display_name": details["display_name"],
            "alternative_readings": details["alternative_readings"],
            "category": "tank",
            "annotation_confidence": annotation.get("confidence"),
            "bbox_xyxy": annotation.get("bbox_xyxy"),
            "direct_observations": [annotation.get("visible_evidence")],
            "interpretation": annotation.get("interpretation"),
            "uncertainty_notes": details["uncertainty_notes"],
            "evidence_needed": details["evidence_needed"],
            "evidence_status": "unverified",
            "evidence_references": [
                {
                    "reference_id": "original-map-scan",
                    "source": SOURCE_IMAGE_PATH,
                    "evidence_status": "source_scan_context_only",
                    "scope_note": "Original raster containing the marked source-image pixels; it does not establish a modern location.",
                },
                {
                    "reference_id": "milestone-1-annotation",
                    "source": "outputs/milestone_1/candidate_annotations.json",
                    "evidence_status": "annotation_pending_human_review",
                    "scope_note": "Existing observation and interpretation are retained as annotation text and remain pending review.",
                },
                {
                    "reference_id": "candidate-research-note",
                    "source": "docs/candidate_research.md#" + feature_id.lower(),
                    "evidence_status": "research_note_unverified",
                    "scope_note": "Research summary of visible evidence and unresolved identity questions; not independent identity confirmation.",
                },
                {
                    "reference_id": "british-library-sheet-record",
                    "source": "https://searcharchives.bl.uk/catalog/041-002248113",
                    "evidence_status": "catalog_context_only",
                    "scope_note": "Catalogue context for No. 48 Plan Of Bangalore; it does not identify this candidate or resolve the printed-number discrepancy.",
                },
            ],
            "review_status": annotation.get("review_status"),
            "provenance": {
                "origin_annotation_file": "outputs/milestone_1/candidate_annotations.json",
                "annotation_method": annotation_document.get("annotation_method"),
            },
            "annotation_history": [{
                "action": "migrated_to_feature_catalog",
                "source": "outputs/milestone_1/candidate_annotations.json",
                "evidence_status": "annotation_pending_human_review",
                "note": "Schema adaptation only; feature ID, pixel bounding box, observation wording, interpretation wording, confidence, and review status retained verbatim.",
            }],
        })
    catalog = {
        "schema_version": 1,
        "source_map": {
            "image_path": SOURCE_IMAGE_PATH,
            "width_px": EXPECTED_DIMENSIONS[0],
            "height_px": EXPECTED_DIMENSIONS[1],
            "coordinate_space": "source_image_pixels_top_left_xyxy_exclusive",
            "sha256": digest,
        },
        "features": features,
    }
    return validate_catalog(catalog)


def load_catalog(path: Path = CATALOG_PATH) -> dict[str, Any]:
    """Read and validate the persistent map-wide feature catalog."""
    try:
        catalog = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise CatalogValidationError(f"Cannot read catalog at {path}: {exc}") from None
    validate_catalog(catalog)
    map_path = PROJECT_ROOT / SOURCE_IMAGE_PATH
    actual_digest = hashlib.sha256(map_path.read_bytes()).hexdigest()
    if catalog["source_map"]["sha256"] != actual_digest:
        raise CatalogValidationError("Catalog source-map SHA-256 does not match the original historical map.")
    return catalog


def filter_features(
    features: Iterable[dict[str, Any]],
    *,
    query: str = "",
    category: str = "all",
    review_status: str = "all",
) -> list[dict[str, Any]]:
    """Search IDs, names, readings, and categories; apply category/status filters."""
    if not isinstance(query, str):
        raise CatalogValidationError("Search query must be a string.")
    if category != "all" and (not isinstance(category, str) or category not in CATEGORIES):
        raise CatalogValidationError(f"Unknown category filter: {category}.")
    if review_status != "all" and (not isinstance(review_status, str) or review_status not in REVIEW_STATUSES):
        raise CatalogValidationError(f"Unknown review-status filter: {review_status}.")
    needle = query.strip().casefold()
    matches: list[dict[str, Any]] = []
    for feature in features:
        if category != "all" and feature["category"] != category:
            continue
        if review_status != "all" and feature["review_status"] != review_status:
            continue
        haystack = " ".join([
            feature["feature_id"],
            feature["display_name"],
            feature["category"],
            *feature["alternative_readings"],
        ]).casefold()
        if needle and needle not in haystack:
            continue
        matches.append(feature)
    return matches


def main(argv: list[str] | None = None) -> int:
    """Validate the catalog, or perform the guarded one-time annotation migration."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--catalog", type=Path, default=CATALOG_PATH, help="Catalog JSON path (defaults to data/catalog/features.json)")
    actions = parser.add_mutually_exclusive_group()
    actions.add_argument("--migrate-existing", action="store_true", help="Create the initial catalog from the three existing annotations; refuses to overwrite")
    actions.add_argument("--validate", action="store_true", help="Validate the catalog (the default action)")
    args = parser.parse_args(argv)
    try:
        if args.migrate_existing:
            if args.catalog.exists():
                raise CatalogValidationError(f"Refusing to overwrite existing catalog: {args.catalog}")
            source = json.loads(ANNOTATIONS_PATH.read_text(encoding="utf-8"))
            catalog = build_initial_catalog(source)
            args.catalog.parent.mkdir(parents=True, exist_ok=True)
            with args.catalog.open("x", encoding="utf-8") as output:
                json.dump(catalog, output, ensure_ascii=False, indent=2)
                output.write("\n")
        else:
            catalog = load_catalog(args.catalog)
        print(f"Catalog valid: {len(catalog['features'])} features; source pixels {catalog['source_map']['width_px']}×{catalog['source_map']['height_px']}.")
        return 0
    except (CatalogValidationError, OSError, json.JSONDecodeError) as exc:
        print(f"feature-catalog: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
