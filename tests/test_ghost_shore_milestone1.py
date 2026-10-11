"""Basic safety and output tests for the Milestone 1 map workflow."""

from __future__ import annotations

import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from ghost_shore_milestone1 import (  # noqa: E402
    CANDIDATES,
    SOURCE_MAP,
    inspect_map,
    run,
    validate_candidates,
)


class MapInspectionTests(unittest.TestCase):
    def test_inspection_reports_actual_source_properties(self) -> None:
        report = inspect_map(SOURCE_MAP)
        expected_hash = hashlib.sha256(SOURCE_MAP.read_bytes()).hexdigest()

        self.assertEqual(report["dimensions_px"], [1280, 1557])
        self.assertEqual(report["color_mode"], "RGB")
        self.assertEqual(report["format"], "JPEG")
        self.assertEqual(report["file_size_bytes"], SOURCE_MAP.stat().st_size)
        self.assertEqual(report["sha256"], expected_hash)

    def test_candidate_boxes_are_inside_source_dimensions(self) -> None:
        validate_candidates(CANDIDATES, width=1280, height=1557)

    def test_invalid_candidate_box_has_actionable_error(self) -> None:
        from dataclasses import replace

        invalid = (replace(CANDIDATES[0], bbox_xyxy=(-1, 0, 20, 20)), *CANDIDATES[1:])
        with self.assertRaisesRegex(ValueError, "outside the 1280x1557 source image"):
            validate_candidates(invalid, width=1280, height=1557)

    def test_workflow_writes_reports_and_preserves_source_bytes(self) -> None:
        before_hash = hashlib.sha256(SOURCE_MAP.read_bytes()).hexdigest()
        with tempfile.TemporaryDirectory(prefix="ghost-shore-test-") as temporary:
            output_dir = Path(temporary) / "milestone_1"
            report = run(output_dir=output_dir)

            self.assertEqual(report["sha256"], before_hash)
            for filename in (
                "map_preview.jpg",
                "inspection_report.json",
                "candidate_annotations.json",
                "candidate_evidence_sheet.jpg",
            ):
                self.assertTrue((output_dir / filename).is_file(), filename)
            annotations = json.loads((output_dir / "candidate_annotations.json").read_text())
            self.assertEqual(len(annotations["candidates"]), 3)
            self.assertTrue(
                all(candidate["review_status"] == "pending_human_review" for candidate in annotations["candidates"])
            )

        self.assertEqual(hashlib.sha256(SOURCE_MAP.read_bytes()).hexdigest(), before_hash)


if __name__ == "__main__":
    unittest.main()
