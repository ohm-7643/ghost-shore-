"""Create a reproducible, human-reviewable evidence sheet for the 1854 map.

Run from any working directory with the project interpreter:
    .venv/bin/python src/ghost_shore_milestone1.py
"""

from __future__ import annotations

import hashlib
import json
import sys
import textwrap
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Literal

from PIL import Image, ImageDraw, ImageFont, UnidentifiedImageError


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SOURCE_MAP = PROJECT_ROOT / "data" / "raw" / "bangalore_1854.jpg"
OUTPUT_DIR = PROJECT_ROOT / "outputs" / "milestone_1"


@dataclass(frozen=True)
class Candidate:
    """A manually proposed feature box in original-map pixel coordinates."""

    candidate_id: str
    bbox_xyxy: tuple[int, int, int, int]
    visible_evidence: str
    interpretation: str
    confidence: Literal["low", "medium", "high"]
    review_status: str


# Boxes are hand-placed in the source map's 1280x1557 pixel coordinate space.
# The descriptions report what is visible; interpretations remain tentative.
CANDIDATES: tuple[Candidate, ...] = (
    Candidate(
        candidate_id="GS-1854-001",
        bbox_xyxy=(75, 585, 180, 690),
        visible_evidence=(
            'The printed label "Tank" appears inside a bounded, wedge-like area; '
            "the boundary and nearby stippled marks are visible on the map."
        ),
        interpretation=(
            "A feature labeled tank on the historical map; a water-body candidate, "
            "not evidence that it is a lake or that it later disappeared."
        ),
        confidence="medium",
        review_status="pending_human_review",
    ),
    Candidate(
        candidate_id="GS-1854-002",
        bbox_xyxy=(185, 1165, 300, 1255),
        visible_evidence=(
            'The label "Lalbagh Tank" is printed beside an irregular outlined area.'
        ),
        interpretation=(
            "A feature explicitly named as a tank on the historical map; current "
            "identity and water status are unverified."
        ),
        confidence="medium",
        review_status="pending_human_review",
    ),
    Candidate(
        candidate_id="GS-1854-003",
        bbox_xyxy=(1000, 1060, 1135, 1180),
        visible_evidence=(
            'The printed label "Tank" appears within a large irregular bounded area; '
            "nearby boundary and drainage-like linework are visible."
        ),
        interpretation=(
            "A feature labeled tank on the historical map; a water-body candidate "
            "whose exact extent and present-day status need review."
        ),
        confidence="medium",
        review_status="pending_human_review",
    ),
)


def sha256_file(path: Path) -> str:
    """Return the SHA-256 digest of a file, reading it in bounded chunks."""
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def inspect_map(path: Path) -> dict[str, object]:
    """Validate an image and return its file and decoded-image properties."""
    if not path.is_file():
        raise FileNotFoundError(
            f"Historical map not found: {path}. Expected data/raw/bangalore_1854.jpg "
            f"under project root {PROJECT_ROOT}."
        )
    try:
        with Image.open(path) as image:
            image.verify()
        with Image.open(path) as image:
            width, height = image.size
            image_format = image.format
            mode = image.mode
            if width <= 0 or height <= 0 or image_format is None:
                raise ValueError("decoded image has invalid dimensions or format")
    except (UnidentifiedImageError, OSError, ValueError) as exc:
        raise ValueError(f"Cannot read a valid image at {path}: {exc}") from exc

    return {
        "source_path": str(path.resolve().relative_to(PROJECT_ROOT)),
        "format": image_format,
        "width": width,
        "height": height,
        "dimensions_px": [width, height],
        "color_mode": mode,
        "file_size_bytes": path.stat().st_size,
        "sha256": sha256_file(path),
    }


def validate_candidates(candidates: tuple[Candidate, ...], width: int, height: int) -> None:
    """Reject malformed or out-of-image manually entered candidate boxes."""
    if len(candidates) < 3:
        raise ValueError(
            f"At least three candidates are required for a review sheet; found {len(candidates)}."
        )
    ids: set[str] = set()
    for candidate in candidates:
        if not candidate.candidate_id.strip() or candidate.candidate_id in ids:
            raise ValueError(f"Candidate IDs must be non-empty and unique: {candidate.candidate_id!r}.")
        ids.add(candidate.candidate_id)
        x1, y1, x2, y2 = candidate.bbox_xyxy
        if not (0 <= x1 < x2 <= width and 0 <= y1 < y2 <= height):
            raise ValueError(
                f"{candidate.candidate_id} box {candidate.bbox_xyxy} is outside the "
                f"{width}x{height} source image or has zero area."
            )
        if not candidate.visible_evidence.strip() or not candidate.interpretation.strip():
            raise ValueError(f"{candidate.candidate_id} needs both evidence and interpretation text.")


def save_preview(source_path: Path, destination: Path, max_width: int = 900) -> None:
    """Save a downsized derivative preview without touching the source image."""
    with Image.open(source_path) as source:
        preview = source.convert("RGB")
        if preview.width > max_width:
            target_height = round(preview.height * max_width / preview.width)
            preview = preview.resize((max_width, target_height), Image.Resampling.LANCZOS)
        preview.save(destination, format="JPEG", quality=90, optimize=True)


def _font(size: int) -> ImageFont.ImageFont:
    """Use a platform-independent Pillow font for report labels."""
    return ImageFont.load_default(size=size)


def create_contact_sheet(
    source_path: Path, destination: Path, candidates: tuple[Candidate, ...]
) -> None:
    """Render overview boxes and enlarged candidate details for human review."""
    with Image.open(source_path) as image:
        source = image.convert("RGB")
        overview_width = 900
        overview_height = round(source.height * overview_width / source.width)
        overview = source.resize((overview_width, overview_height), Image.Resampling.LANCZOS)

        card_width = 690
        card_height = 400
        margin = 28
        header_height = 70
        sheet_height = max(overview_height, header_height + margin + len(candidates) * (card_height + 18))
        sheet = Image.new("RGB", (overview_width + card_width + margin * 3, sheet_height + margin * 2), "#f4f1e9")
        draw = ImageDraw.Draw(sheet)
        draw.text((margin, 18), "1854 Bangalore map · candidate review", fill="#202020", font=_font(22))
        overview_x, overview_y = margin, header_height
        sheet.paste(overview, (overview_x, overview_y))
        draw.rectangle(
            (overview_x, overview_y, overview_x + overview_width - 1, overview_y + overview_height - 1),
            outline="#333333",
            width=2,
        )

        sidebar_x = overview_x + overview_width + margin
        draw.text((sidebar_x, 18), "Evidence crops · pending human review", fill="#202020", font=_font(18))
        scale_x = overview_width / source.width
        scale_y = overview_height / source.height

        for index, candidate in enumerate(candidates):
            x1, y1, x2, y2 = candidate.bbox_xyxy
            mapped_box = (
                round(overview_x + x1 * scale_x),
                round(overview_y + y1 * scale_y),
                round(overview_x + x2 * scale_x),
                round(overview_y + y2 * scale_y),
            )
            draw.rectangle(mapped_box, outline="#d62828", width=4)
            label_y = max(overview_y, mapped_box[1] - 22)
            draw.rectangle((mapped_box[0], label_y, mapped_box[0] + 140, label_y + 20), fill="#d62828")
            draw.text((mapped_box[0] + 4, label_y + 2), candidate.candidate_id, fill="white", font=_font(13))

            card_y = header_height + margin + index * (card_height + 18)
            draw.rounded_rectangle(
                (sidebar_x, card_y, sidebar_x + card_width, card_y + card_height),
                radius=10,
                fill="white",
                outline="#b9b3a8",
                width=2,
            )
            padding = 12
            crop_pad = 55
            crop_box = (
                max(0, x1 - crop_pad),
                max(0, y1 - crop_pad),
                min(source.width, x2 + crop_pad),
                min(source.height, y2 + crop_pad),
            )
            crop = source.crop(crop_box)
            crop.thumbnail((card_width - padding * 2, 215), Image.Resampling.LANCZOS)
            crop_x = sidebar_x + padding
            crop_y = card_y + padding
            sheet.paste(crop, (crop_x, crop_y))
            draw.text(
                (crop_x, crop_y + 212),
                f"{candidate.candidate_id}  bbox xyxy: {candidate.bbox_xyxy}",
                fill="#202020",
                font=_font(15),
            )
            draw.multiline_text(
                (crop_x, crop_y + 236),
                "\n".join(textwrap.wrap(candidate.visible_evidence, width=105)),
                fill="#333333",
                font=_font(13),
                spacing=2,
            )
            draw.multiline_text(
                (crop_x, crop_y + 286),
                "\n".join(textwrap.wrap(f"Interpretation: {candidate.interpretation}", width=105)),
                fill="#634b16",
                font=_font(12),
                spacing=2,
            )
            draw.text(
                (crop_x, card_y + card_height - 24),
                f"Confidence: {candidate.confidence} · Status: {candidate.review_status}",
                fill="#754c24",
                font=_font(13),
            )

        sheet.save(destination, format="JPEG", quality=92, optimize=True)


def run(source_path: Path = SOURCE_MAP, output_dir: Path = OUTPUT_DIR) -> dict[str, object]:
    """Create preview, inspection JSON, candidate annotations, and review sheet."""
    source_path = source_path.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    report = inspect_map(source_path)
    validate_candidates(CANDIDATES, int(report["width"]), int(report["height"]))

    save_preview(source_path, output_dir / "map_preview.jpg")
    report["preview_path"] = "map_preview.jpg"
    report["candidate_annotation_path"] = "candidate_annotations.json"
    report["evidence_sheet_path"] = "candidate_evidence_sheet.jpg"
    report["notes"] = [
        "The preview and evidence sheet are derived files; the source map is never written.",
        "Candidates are initial manual annotations and remain pending human review.",
        "A map label does not verify present-day identity, lake status, or disappearance.",
    ]
    (output_dir / "inspection_report.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    annotations = {
        "schema_version": 1,
        "source_sha256": report["sha256"],
        "coordinate_system": {
            "origin": "top_left",
            "units": "source_image_pixels",
            "bbox_format": "xyxy; x2 and y2 are exclusive",
            "source_dimensions_px": report["dimensions_px"],
        },
        "annotation_method": (
            "initial visual review of the source map and existing crops; proposed boxes "
            "are pending human review"
        ),
        "candidates": [asdict(candidate) for candidate in CANDIDATES],
    }
    (output_dir / "candidate_annotations.json").write_text(
        json.dumps(annotations, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    create_contact_sheet(source_path, output_dir / "candidate_evidence_sheet.jpg", CANDIDATES)
    return report


def main() -> int:
    """Run the map inspection and present concise output paths and source identity."""
    try:
        report = run()
    except (FileNotFoundError, ValueError, OSError) as exc:
        print(f"Map inspection failed: {exc}", file=sys.stderr)
        return 1
    print(f"Source: {report['source_path']}")
    print(f"Dimensions: {report['width']} x {report['height']} px ({report['color_mode']})")
    print(f"File size: {report['file_size_bytes']} bytes")
    print(f"SHA-256: {report['sha256']}")
    print(f"Outputs: {OUTPUT_DIR.relative_to(PROJECT_ROOT)}")
    print(f"Candidates awaiting human review: {len(CANDIDATES)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
