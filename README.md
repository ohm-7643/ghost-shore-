# Ghost Shore

Ghost Shore is an open-source cartographic research and exploration tool that investigates historical map evidence for water bodies beneath modern Bengaluru (Bangalore), starting with the c.1854 *Plan of Bangalore*. The project connects archival cartography, evidence-grounded AI analysis, and safe real-world ground exploration ("Touch Grass").

Candidate feature identities and modern locations remain unverified hypotheses. In keeping with strict epistemic standards, no candidate is claimed to be a confirmed lake, declared a "disappeared" water body, or tied to unverified modern GPS coordinates.

---

## Key Features

- **Interactive Historical Map Canvas:** A lightweight, dependency-free viewer providing smooth pan and zoom across high-resolution historical cartographic scans in native image pixel coordinates (`xyxy`).
- **Evidence-Grounded Feature Catalog:** A validated catalog (`data/catalog/features.json`) governed by a strict JSON schema (`data/catalog/catalog.schema.json`), supporting category/status filtering, region inspection, uncertainty documentation, and provenance tracking.
- **Dual AI Research Assistant:** Integrates open-weight model `Qwen/Qwen3.5-4B` via the Tinker API, alongside a 100% offline deterministic mock fallback. Enforces strict factual guardrails: claims must be verbatim substrings from user-supplied excerpts; hallucinated coordinates, unauthorized URLs, and disappearance claims are rejected.
- **Touch Grass Field Observation Companion:** Bridges desk research and the physical city with a guided 12-item ground observation checklist, daylight safety protocols, private client-side field notes, and a printable single-page A4 field worksheet.
- **Zero-External-Dependency Server:** A self-contained local web server built exclusively with Python's standard library (`http.server`), featuring strict loopback binding (`127.0.0.1`) and endpoint allowlisting.

---

## Touch Grass Field Expedition

Built for the Hacktoberfest Open-Source AI Challenge Week 1: “Touch Grass”, the Field Expedition companion gets researchers off the screen and into Bengaluru's landscape to observe topography, drainage patterns, and heritage markers safely and systematically.

### Field Safety Protocol
Field exploration must adhere strictly to physical safety guidelines:
1. **Public Thoroughfares Only:** Confine observations to public roads, sidewalks, and designated public parks. Never trespass on private property.
2. **Daylight Hours Only:** Visit observation points during clear daylight. Never conduct field checks at dusk, at night, or during severe rain.
3. **Hazard Avoidance:** Never enter storm drains (*rajakaluves*), canal beds, drainage channels, steep embankments, or active construction sites.
4. **Epistemic Humility:** Modern visual cues (e.g., low-lying terrain or drainage channels) are physical observations only; they do not prove historical continuity or candidate identity without archival corroboration.

### 12-Item Field Observation Checklist
The companion organizes ground observations into four structured categories:
- **Topography & Gradient:** Document natural elevation breaks, visible valley depressions, and surface runoff slopes.
- **Visible Surface Infrastructure:** Observe stormwater channels (*rajakaluves*), stone revetments, bund remnants, culverts, and sluice infrastructure.
- **Ecological & Heritage Indicators:** Note water-tolerant vegetation, depression flora, mature heritage trees, shrines, and traditional open wells (*kalyanis*).
- **Archival & Field Questions:** Record local street naming discrepancies, visible remnants versus modern grading, and open questions for archival follow-up.

### Private In-Browser Notes & Printable A4 Sheet
- **Client-Side Privacy:** Field notes (observation date, vantage point, weather, field notes, and unresolved questions) are saved exclusively to browser `localStorage`. No location tracking or telemetry is transmitted.
- **Single-Page A4 Printable Worksheet:** The interface includes a dedicated `@media print` stylesheet (`web/styles.css`). Triggering browser print (`Ctrl+P` / `Cmd+P` or the in-app button) formats an all-in-one, compact A4 field worksheet designed for pencil-and-paper field surveys without screen glare or battery dependency.

---

## Architecture

```text
ghost-shore/
├── data/
│   ├── raw/                  # Historical scan target (bangalore_1854.jpg)
│   └── catalog/              # features.json and catalog.schema.json
├── docs/                     # Archival desk reviews and georeferencing analyses
├── examples/                 # Sample research excerpts for offline testing
├── outputs/                  # Milestone 1 inspection crops and georeferencing trials
├── src/
│   ├── ghost_shore_web.py    # Local HTTP server with strict endpoint allowlist
│   ├── ghost_shore_assistant.py # Evidence-grounded AI assistant (Tinker & mock)
│   ├── feature_catalog.py    # Catalog validation and migration CLI
│   └── ghost_shore_milestone1.py # Historical map inspection and thumbnailing
├── tests/                    # Comprehensive unit tests (web, assistant, catalog)
└── web/                      # Vanilla HTML5/CSS/JS explorer & field companion
    ├── index.html
    ├── styles.css
    └── app.js
```

### Coordinate Boundary
Historical coordinates are maintained strictly in source-image pixel space ($xyxy$ with top-left origin). Because 19th-century cartographic sheets exhibit non-uniform distortion and lack verified local ground control points, modern latitude/longitude coordinates and map overlays are deliberately omitted from the catalog and UI.

---

## Quick Start

### Prerequisites
- Python 3.10+ (tested on Python 3.12 and 3.13)
- Pillow (`pip install pillow`)

### Setup
1. Clone the repository and navigate to the project directory:
   ```bash
   git clone https://github.com/<owner>/ghost-shore.git
   cd ghost-shore
   ```
2. Create and activate a virtual environment:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```
3. Install required dependencies:
   ```bash
   python -m pip install -r requirements.txt
   ```
   *(Or install Pillow directly: `python -m pip install pillow`)*

### Historical Map Asset Notice
> **Important:** The original historical scan is **excluded from this repository** because public redistribution rights are being verified with archival custodians.
>
> The web explorer and inspection scripts expect a scan file at `data/raw/bangalore_1854.jpg` (1280 × 1557 px). You must obtain a lawfully reusable copy of the c.1854 *Plan of Bangalore* and place it at this path before launching the image-dependent views.
>
> *Fresh Clone Note:* On a fresh clone without this asset, raster-dependent operations (map canvas rendering, crop generation, and raster image checksum tests) will not execute. The catalog validator and core offline schema tests do not require the raster image.

### Launching the Web Explorer
Start the local server:
```bash
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python src/ghost_shore_web.py
```
Open <http://127.0.0.1:8000> in your browser. Stop the server with `Ctrl+C`.

### Validating the Feature Catalog
Validate the integrity and schema of `data/catalog/features.json`:
```bash
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python src/feature_catalog.py --validate
```

### Inspecting the Historical Map (Asset Required)
If `data/raw/bangalore_1854.jpg` is present, generate the milestone inspection outputs and crops:
```bash
.venv/bin/python src/ghost_shore_milestone1.py
```

---

## Configuration and AI Fallback

Ghost Shore includes an evidence-grounded research assistant in [`src/ghost_shore_assistant.py`](src/ghost_shore_assistant.py). It queries open-weight model `Qwen/Qwen3.5-4B` through [Tinker](https://tinker-docs.thinkingmachines.ai).

### 1. Offline Deterministic Mock Mode (Default in Web UI)
The web explorer and offline CLI run in deterministic mock mode. This requires no Tinker package, no API key, makes zero network requests, and incurs zero token costs:
```bash
.venv/bin/python src/ghost_shore_assistant.py GS-1854-002 \
  --sources-json examples/lalbagh_source_excerpt.json --mock
```

### 2. Live Tinker Setup (Optional)
To run live sampling with `Qwen/Qwen3.5-4B` via Tinker:
1. Install the Tinker SDK:
   ```bash
   .venv/bin/python -m pip install tinker
   ```
2. Set your `TINKER_API_KEY` securely in your shell:
   ```zsh
   read -s "TINKER_API_KEY?Tinker API key: "
   export TINKER_API_KEY
   printf '\n'
   ```
3. Request one live sample:
   ```bash
   .venv/bin/python src/ghost_shore_assistant.py GS-1854-002 \
     --sources-json examples/lalbagh_source_excerpt.json --live
   ```

*Safety & Reliability:*
- The assistant issues a single request and does not retry automatically.
- Tinker exception details are sanitized to prevent API credentials, prompt contents, or headers from leaking into terminal logs.
- Sampling rate for `Qwen/Qwen3.5-4B` on Tinker is listed at ~$1.005 per million generated tokens and ~$0.33 per million input tokens (checked October 2026).

---

## Tests

Run the full test suite (checks catalog schema, web endpoints, assistant validation, and image bounds if the raster asset is present):
```bash
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m unittest discover -s tests -v
```

Run focused offline assistant validation tests:
```bash
.venv/bin/python -m unittest discover -s tests -p 'test_ghost_shore_assistant.py' -v
```

Run georeferencing diagnostic tests:
```bash
.venv/bin/python -m unittest discover -s outputs/georeferencing_trial -p 'test_*.py' -v
```

---

## Historical Research Methodology and Limitations

1. **Candidates are Research Leads, Not Proven Facts:** Feature records (`GS-1854-001`, `GS-1854-002`, `GS-1854-003`) are preliminary annotations marked `pending_human_review`. Visible labels such as “Tank” or “Lalbagh Tank” are historical cartographic observations; they do not establish identity, boundary extent, or continuity into modern water bodies.
2. **Georeferencing is Approximate:** Historical cartography from the 1850s was drawn prior to standardized modern projections and suffers from non-linear spatial distortion. Global or local coordinate warping can misplace features by hundreds of meters. Modern coordinates are therefore omitted from the catalog to prevent inaccurate real-world claims.
3. **AI Output is Not Historical Evidence:** The assistant synthesizes user-provided research excerpts only. Supported claims reflect text matches within caller-provided excerpts; the assistant does not verify primary archival sources or confirm historical truth.
4. **Physical Field Safety and Ethics:** Field observations are restricted to public thoroughfares during daylight. Observers must never trespass or enter drainage infrastructure. Ground evidence (e.g., surface depressions or stone walls) indicates landscape characteristics but cannot confirm historical lake identity without independent archival corroboration.

---

## License

The code and documentation in this repository are licensed under the [MIT License](LICENSE).

Historical cartographic images, archival scans, and third-party research excerpts remain the property of their respective creators and custodians and are referenced for educational and research purposes under fair dealing principles.
