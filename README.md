# Ghost Shore

Ghost Shore explores historical map evidence for possible water features beneath modern Bengaluru. The local explorer and catalog let a human browse annotations on the c.1854 Plan of Bangalore. Candidate identities and modern locations remain unverified; no feature is called a disappeared lake.

## Milestone 1: inspect the historical map

From the project root, run:

```bash
.venv/bin/python src/ghost_shore_milestone1.py
```

The script resolves the source and output locations relative to its own file, so it also works when invoked from another current directory:

```bash
/absolute/path/to/ghost-shore/.venv/bin/python /absolute/path/to/ghost-shore/src/ghost_shore_milestone1.py
```

It reads `data/raw/bangalore_1854.jpg` and writes only new derived files under `outputs/milestone_1/`:

- `map_preview.jpg`: downsized display copy of the source scan.
- `inspection_report.json`: dimensions, format, color mode, byte size, and source SHA-256.
- `candidate_annotations.json`: three initial candidate boxes prepared for human review in source-image pixel coordinates (`xyxy`, with the far edges exclusive), along with visible evidence, cautious interpretation, confidence, and review status.
- `candidate_evidence_sheet.jpg`: full-map locations and detail crops for the candidates.

The candidate labels visible on the scan include “Tank” and “Lalbagh Tank.” These are annotations for review, not claims that a candidate is a confirmed lake, has disappeared, or maps to a particular modern location. All candidates begin as `pending_human_review`. Update the annotation JSON only after a human checks the boxes and interpretations against the original map.

The workflow requires Pillow from the existing `.venv`; it does not require MPS or modify the original map. No installation is needed when using the configured interpreter.

## Run the basic tests

```bash
.venv/bin/python -m unittest discover -s tests -v
```

The tests check the source properties and checksum, candidate box bounds, generated output files, pending review status, and preservation of the source bytes.

## Milestone 3: evidence-grounded research assistant

The assistant accepts one existing candidate annotation and a JSON file of explicitly supplied `{ "url", "excerpt" }` source records. At least one non-empty excerpt is required. It sends only the candidate ID, visible annotation text, interpretation, and those excerpts to Tinker; it does not send map images, bounding boxes, or unrelated project data. Observations are attributed to the unreviewed annotation and copied exactly; its interpretation remains explicitly labeled uncertain. Claim text must be an exact substring of its supplied excerpt, and every result labels that as a text match only: the URL and excerpt are not independently authenticated. This does not prove a source page contains the excerpt or that the excerpt is historically correct. Invalid JSON, extra fields, unsupported source URLs/claims, disappearance claims, and geographic coordinates in generated prose are rejected. Source excerpts are untrusted data. Output is validated independently of the prompt, but prompt wording alone is not a security guarantee.

### Offline mock example

From the project root:

```bash
.venv/bin/python src/ghost_shore_assistant.py GS-1854-002 \
  --sources-json examples/lalbagh_source_excerpt.json --mock
```

Mock mode is deterministic, requires no Tinker package or API key, and makes no network/API call. `examples/lalbagh_source_excerpt.json` explicitly labels its content as an **unverified user-supplied research note and paraphrase, not a quotation**. The linked URL and note have not been independently checked; the record is not evidence that the page contains that text or that the candidate has that identity.

### Live Tinker setup

The recommended model is `Qwen/Qwen3.5-4B`. Tinker's [current model pricing](https://tinker-docs.thinkingmachines.ai/tinker/models/models_and_pricing/) lists sampling at **$1.005 per million generated tokens** and prefill at $0.33 per million input tokens (checked 2026-10-10; prices may change). Tinker's [quickstart](https://tinker-docs.thinkingmachines.ai/tinker/quickstart/) documents `ServiceClient`, `create_sampling_client`, `sample`, and `TINKER_API_KEY` authentication.

The existing `.venv` does not currently include the `tinker` SDK. Live mode requires that SDK; it has not been installed in this milestone. After confirming account balance and model access in the Tinker console, install it into the project interpreter, if approved:

```bash
.venv/bin/python -m pip install tinker
```

In zsh, enter the key through a hidden prompt so it is not echoed or added to shell history:

```zsh
read -s "TINKER_API_KEY?Tinker API key: "
export TINKER_API_KEY
printf '\n'
```

Then request one live sample explicitly:

```bash
.venv/bin/python src/ghost_shore_assistant.py GS-1854-002 \
  --sources-json examples/lalbagh_source_excerpt.json --live
```

The key remains in the current shell environment and is never printed by the assistant. Do not use `--live` until the account balance is confirmed. The SDK is not installed in the current environment, so its documented timeout support has not been verified locally. The assistant does not pass a timeout parameter or claim that a live request is bounded; it makes one request and does not retry automatically. Tinker exceptions are replaced with a generic actionable message to avoid exposing headers, prompt contents, or sensitive exception details. This milestone made no Tinker inference request and did not train or fine-tune a model.

Run the focused offline tests with:

```bash
.venv/bin/python -m unittest discover -s tests -p 'test_ghost_shore_assistant.py' -v
```

## Milestone 4: local historical-map explorer

Launch the dependency-free explorer from the project root:

```bash
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python src/ghost_shore_web.py
```

Open <http://127.0.0.1:8000>. The server binds only to loopback and reads the original map and annotations from paths resolved relative to the Python module, so it can also be launched by its absolute path from another working directory. Stop it with `Ctrl+C`.

The page displays `data/raw/bangalore_1854.jpg` as-is, with selectable source-image annotation boxes and mouse/touch zoom and pan. Candidate details keep map observations, possible interpretations, unverified hypotheses, and missing evidence separate. The candidate boxes remain in source-image pixels; no modern map, candidate geographic coordinates, disappearance claims, or validated routes are shown. The British Library sheet/parent-atlas records are linked with the unresolved printed “43” versus catalogue “No. 48” discrepancy.

The research companion is explicitly an **offline demo**. Its button invokes the existing assistant CLI with `--mock` and the example note; it makes no model request, spends no Tinker credits, and does not verify the paraphrase or linked page. The deterministic response displays this limitation beside the note. The page does not include an API key or live inference path.

The standard-library web smoke tests run with the existing full suite:

```bash
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m unittest discover -s tests -v
```

## Milestone 5: historical feature catalog

The map-wide catalog is `data/catalog/features.json`; its machine-readable schema is `data/catalog/catalog.schema.json`. It currently contains **only** GS-1854-001, GS-1854-002, and GS-1854-003 migrated from the existing human-review annotations. The migration retains each feature ID, source-image pixel bounding box, visible-evidence wording, interpretation wording, annotation confidence value, and `pending_human_review` status. Added display names/readings, uncertainty notes, evidence still needed, evidence scope/status, and migration provenance do not upgrade the source annotations or establish feature identity.

Validate the catalog with the project interpreter:

```bash
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python src/feature_catalog.py --validate
```

The one-time migration command is `PYTHONDONTWRITEBYTECODE=1 .venv/bin/python src/feature_catalog.py --migrate-existing`. It creates the initial catalog and refuses to overwrite an existing file.

### Adding a future feature

Add an entry to `features` in `data/catalog/features.json` only after a reviewer has documented an observation from the actual source map. Copy the field structure of an existing entry, assign the next unused ID matching `GS-1854-NNN`, and provide:

- a display name, category, and any alternative readings, clearly preserving uncertainty;
- a non-empty `bbox_xyxy` in the original 1280 × 1557 image, with top-left origin and exclusive x2/y2 edges;
- direct observation text, an interpretation, and at least one uncertainty note;
- at least one `evidence_needed` item stating what evidence would address the open identity or reading questions;
- top-level `evidence_status`, plus an `evidence_status` and scope note for every evidence reference and history item;
- project-relative source paths or absolute HTTP(S) reference strings, with provenance and at least one annotation-history event;
- a review status. New entries should begin as `pending_human_review`.

Run `PYTHONDONTWRITEBYTECODE=1 .venv/bin/python src/feature_catalog.py --validate` before using the catalog. Validation rejects malformed or duplicate IDs, duplicate evidence-reference IDs, missing status/provenance fields, malformed references, unsupported categories/statuses, and boxes outside the source image. It does not authenticate source URLs or establish that an interpretation is historically correct. The browser search covers feature ID, display name, alternative readings, and category, with independent category/review-status filters; selecting a result highlights its image-pixel box.

Milestone 5.1 adds “Inspect this region” and “Show full map” controls. They operate only in original-image pixels. Evidence links open the known local map, annotation JSON, or research note through a server allowlist, or open an HTTPS URL already present in the catalog. The interface labels map/annotation/catalog context separately from the research note lead marked unverified; a link does not authenticate a page or establish candidate identity.

Each feature has a guided review checklist and a research-note field. Checklist checks are session-only; notes save in browser `localStorage` for this browser and feature only. They are not uploaded or written to the catalog, and completing the checklist does not change `pending_human_review`, verify a source, or promote a feature status. Direct observations, alternative readings, interpretations, uncertainties, and evidence still needed remain in separate catalog fields.

The original image pixels remain the only coordinate system in this catalog. Latitude/longitude, modern-place matching, map routes, and georeferencing claims are not part of the schema or UI because the existing alignment lacks independent validation near the candidates.

## Historical map asset and reuse

The original historical scan is not included in this repository while its
redistribution rights are being verified. The explorer currently expects
`data/raw/bangalore_1854.jpg`; obtain a lawfully reusable copy and place it
there before launching the web app. Do not assume that catalogue attribution
alone grants permission to redistribute the scan.
