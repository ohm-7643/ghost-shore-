"""Catalog schema, migration, search, and filter tests."""

from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from src.feature_catalog import (
    ANNOTATIONS_PATH,
    CATALOG_PATH,
    FEATURE_FIELDS,
    CatalogValidationError,
    build_initial_catalog,
    filter_features,
    load_catalog,
    validate_catalog,
)


class FeatureCatalogTests(unittest.TestCase):
    def setUp(self) -> None:
        self.annotations = json.loads(ANNOTATIONS_PATH.read_text(encoding="utf-8"))
        self.catalog = load_catalog()

    def test_catalog_file_matches_dependency_free_schema_contract(self) -> None:
        schema_path = CATALOG_PATH.parent / "catalog.schema.json"
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        self.assertIn("feature_id", schema["$defs"]["feature"]["required"])
        self.assertIn("evidence_status", schema["$defs"]["feature"]["required"])
        self.assertIn("evidence_needed", schema["$defs"]["feature"]["required"])
        self.assertEqual(set(schema["$defs"]["feature"]["properties"]), FEATURE_FIELDS)
        self.assertEqual(validate_catalog(self.catalog), self.catalog)
        self.assertEqual(len(self.catalog["features"]), 3)

    def test_migration_preserves_candidate_ids_boxes_wording_confidence_and_status(self) -> None:
        migrated = build_initial_catalog(self.annotations)
        original = {item["candidate_id"]: item for item in self.annotations["candidates"]}
        result = {item["feature_id"]: item for item in migrated["features"]}
        self.assertEqual(set(result), set(original))
        for feature_id, annotation in original.items():
            with self.subTest(feature_id=feature_id):
                feature = result[feature_id]
                self.assertEqual(feature["bbox_xyxy"], annotation["bbox_xyxy"])
                self.assertEqual(feature["direct_observations"], [annotation["visible_evidence"]])
                self.assertEqual(feature["interpretation"], annotation["interpretation"])
                self.assertEqual(feature["annotation_confidence"], annotation["confidence"])
                self.assertEqual(feature["review_status"], annotation["review_status"])

    def test_search_matches_id_name_alternative_reading_and_category(self) -> None:
        self.assertEqual([item["feature_id"] for item in filter_features(self.catalog["features"], query="GS-1854-003")], ["GS-1854-003"])
        self.assertEqual([item["feature_id"] for item in filter_features(self.catalog["features"], query="lalbagh")], ["GS-1854-002"])
        self.assertEqual(len(filter_features(self.catalog["features"], query="tank")), 3)
        self.assertEqual(len(filter_features(self.catalog["features"], query="tank", category="tank")), 3)

    def test_category_and_review_status_filters_are_applied(self) -> None:
        pending = filter_features(self.catalog["features"], review_status="pending_human_review")
        reviewed = filter_features(self.catalog["features"], review_status="reviewed")
        non_tanks = filter_features(self.catalog["features"], category="stream")
        self.assertEqual(len(pending), 3)
        self.assertEqual(reviewed, [])
        self.assertEqual(non_tanks, [])
        with self.assertRaisesRegex(CatalogValidationError, "Unknown category"):
            filter_features(self.catalog["features"], category="lake")
        with self.assertRaisesRegex(CatalogValidationError, "Unknown review-status"):
            filter_features(self.catalog["features"], review_status="verified")

    def test_invalid_id_is_rejected(self) -> None:
        invalid = copy.deepcopy(self.catalog)
        invalid["features"][0]["feature_id"] = "tank-one"
        with self.assertRaisesRegex(CatalogValidationError, "feature_id must match"):
            validate_catalog(invalid)

    def test_duplicate_ids_are_rejected(self) -> None:
        invalid = copy.deepcopy(self.catalog)
        invalid["features"][1]["feature_id"] = invalid["features"][0]["feature_id"]
        with self.assertRaisesRegex(CatalogValidationError, "Duplicate feature ID"):
            validate_catalog(invalid)

    def test_invalid_bounding_boxes_are_rejected(self) -> None:
        for bbox in ([-1, 0, 10, 10], [0, 0, 1281, 10], [10, 10, 9, 11], [0, 0, 10.5, 10], [True, 0, 10, 10]):
            with self.subTest(bbox=bbox):
                invalid = copy.deepcopy(self.catalog)
                invalid["features"][0]["bbox_xyxy"] = bbox
                with self.assertRaisesRegex(CatalogValidationError, "bbox_xyxy"):
                    validate_catalog(invalid)

    def test_missing_feature_evidence_status_is_rejected(self) -> None:
        invalid = copy.deepcopy(self.catalog)
        del invalid["features"][0]["evidence_status"]
        with self.assertRaisesRegex(CatalogValidationError, "missing or unsupported fields"):
            validate_catalog(invalid)

    def test_missing_evidence_needed_is_rejected(self) -> None:
        invalid = copy.deepcopy(self.catalog)
        del invalid["features"][0]["evidence_needed"]
        with self.assertRaisesRegex(CatalogValidationError, "missing or unsupported fields"):
            validate_catalog(invalid)

    def test_missing_reference_or_history_evidence_status_is_rejected(self) -> None:
        for path in ("evidence_references", "annotation_history"):
            invalid = copy.deepcopy(self.catalog)
            if path == "evidence_references":
                del invalid["features"][0][path][0]["evidence_status"]
            else:
                del invalid["features"][0][path][0]["evidence_status"]
            with self.subTest(path=path), self.assertRaisesRegex(CatalogValidationError, "evidence_status"):
                validate_catalog(invalid)

    def test_invalid_reference_path_is_rejected(self) -> None:
        invalid = copy.deepcopy(self.catalog)
        invalid["features"][0]["evidence_references"][0]["source"] = "../../private.txt"
        with self.assertRaisesRegex(CatalogValidationError, "project-relative path"):
            validate_catalog(invalid)


if __name__ == "__main__":
    unittest.main()
