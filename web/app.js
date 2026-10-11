"use strict";

const elements = {
  map: document.getElementById("historical-map"),
  mapLoading: document.getElementById("map-loading"),
  mapError: document.getElementById("map-error"),
  mapWindow: document.getElementById("map-window"),
  mapScene: document.getElementById("map-scene"),
  overlays: document.getElementById("candidate-overlays"),
  inspectRegion: document.getElementById("inspect-region"),
  search: document.getElementById("catalog-search"),
  category: document.getElementById("category-filter"),
  reviewStatus: document.getElementById("status-filter"),
  list: document.getElementById("catalog-list"),
  count: document.getElementById("catalog-count"),
  total: document.getElementById("catalog-total"),
  summary: document.getElementById("feature-status-summary"),
  empty: document.getElementById("detail-empty"),
  detail: document.getElementById("candidate-detail"),
  assistantButton: document.getElementById("assistant-run"),
  assistantFootnote: document.getElementById("assistant-footnote"),
  assistantEmpty: document.getElementById("assistant-empty"),
  assistantOutput: document.getElementById("assistant-output"),
  assistantError: document.getElementById("assistant-error")
};
elements.researchNote = document.getElementById("research-note");
elements.researchNoteStatus = document.getElementById("research-note-status");
elements.saveResearchNote = document.getElementById("save-research-note");
elements.fieldSiteSelect = document.getElementById("field-site-select");
elements.fieldLeadContext = document.getElementById("field-lead-context");
elements.checklistProgressBadge = document.getElementById("checklist-progress-badge");
elements.fieldNoteDate = document.getElementById("field-note-date");
elements.fieldNoteWeather = document.getElementById("field-note-weather");
elements.fieldVantagePoint = document.getElementById("field-vantage-point");
elements.fieldObservationsText = document.getElementById("field-observations-text");
elements.fieldQuestionsText = document.getElementById("field-questions-text");
elements.saveFieldNoteBtn = document.getElementById("save-field-note-btn");
elements.printFieldSheetBtn = document.getElementById("print-field-sheet-btn");
elements.resetFieldNoteBtn = document.getElementById("reset-field-note-btn");
elements.fieldNoteStatus = document.getElementById("field-note-status");
elements.printableFieldSheet = document.getElementById("printable-field-sheet");
elements.jumpToExpedition = document.getElementById("jump-to-expedition");

let visibleFeatures = [];
let selectedId = null;
let sourceDimensions = { width: 1280, height: 1557 };
let zoom = 1;
let panX = 0;
let panY = 0;
let dragStart = null;
let filterRevision = 0;
let searchTimer = null;
let checklistByFeature = new Map();

function titleCase(value) {
  return value.replaceAll("_", " ").replace(/\b\w/g, (letter) => letter.toUpperCase());
}

function setMapTransform() {
  elements.mapScene.style.transform = `translate(${panX}px, ${panY}px) scale(${zoom})`;
}

function showFullMap() {
  zoom = 1;
  panX = 0;
  panY = 0;
  setMapTransform();
}

function inspectRegion(feature) {
  if (!feature || !elements.mapWindow.clientWidth || !elements.mapScene.clientWidth) return;
  const [x1, y1, x2, y2] = feature.bbox_xyxy;
  const sceneWidth = elements.mapScene.clientWidth;
  const sceneHeight = elements.mapScene.clientHeight;
  const boxCenterX = ((x1 + x2) / 2 / sourceDimensions.width) * sceneWidth;
  const boxCenterY = ((y1 + y2) / 2 / sourceDimensions.height) * sceneHeight;
  const boxWidth = ((x2 - x1) / sourceDimensions.width) * sceneWidth;
  const boxHeight = ((y2 - y1) / sourceDimensions.height) * sceneHeight;
  const fitScale = Math.min(
    (elements.mapWindow.clientWidth * 0.68) / boxWidth,
    (elements.mapWindow.clientHeight * 0.68) / boxHeight
  );
  zoom = Math.max(1.35, Math.min(3.5, fitScale));
  panX = elements.mapWindow.clientWidth / 2 - sceneWidth / 2 - zoom * (boxCenterX - sceneWidth / 2);
  panY = elements.mapWindow.clientHeight / 2 - sceneHeight / 2 - zoom * (boxCenterY - sceneHeight / 2);
  setMapTransform();
  const reviewState = checklistByFeature.get(feature.feature_id) || { region: false, source: false, notes: false };
  reviewState.region = true;
  checklistByFeature.set(feature.feature_id, reviewState);
  const regionCheck = document.querySelector('[data-review-step="region"]');
  if (selectedId === feature.feature_id && regionCheck) regionCheck.checked = true;
}

function sourceEvidenceLabel(status) {
  const labels = {
    source_scan_context_only: "Consulted · original map scan",
    annotation_pending_human_review: "Consulted · annotation pending review",
    research_note_unverified: "Research lead · not independently verified",
    catalog_context_only: "Catalogue consulted · not candidate identification"
  };
  return labels[status] || "Evidence status not classified";
}

function localEvidenceHref(source) {
  const allowed = new Set([
    "data/raw/bangalore_1854.jpg",
    "outputs/milestone_1/candidate_annotations.json",
    "docs/candidate_research.md"
  ]);
  const path = source.split("#", 1)[0];
  return allowed.has(path) ? `/local-evidence?path=${encodeURIComponent(path)}` : null;
}

function appendEvidenceLink(container, source) {
  let href = localEvidenceHref(source);
  if (!href) {
    try {
      const url = new URL(source);
      if (url.protocol === "https:" && url.hostname) href = url.href;
    } catch { /* Unknown references remain visible as plain text. */ }
  }
  if (!href) return;
  const link = document.createElement("a");
  link.className = "evidence-open-link";
  link.href = href;
  link.target = "_blank";
  link.rel = "noopener noreferrer";
  link.textContent = localEvidenceHref(source) ? "Open local source ↗" : "Open source URL ↗";
  container.append(link);
}

function renderReviewWorkflow(feature) {
  const key = feature.feature_id;
  const state = checklistByFeature.get(key) || { region: false, source: false, notes: false };
  for (const checkbox of document.querySelectorAll("[data-review-step]")) {
    checkbox.checked = Boolean(state[checkbox.dataset.reviewStep]);
    checkbox.onchange = () => {
      state[checkbox.dataset.reviewStep] = checkbox.checked;
      checklistByFeature.set(key, state);
    };
  }
  const noteKey = `ghost-shore:research-note:${key}`;
  try {
    elements.researchNote.value = localStorage.getItem(noteKey) || "";
    elements.researchNoteStatus.textContent = elements.researchNote.value ? "Saved on this browser" : "Not saved";
  } catch {
    elements.researchNote.value = "";
    elements.researchNoteStatus.textContent = "Browser storage unavailable; note not saved";
  }
  elements.saveResearchNote.onclick = () => {
    const note = elements.researchNote.value.trim();
    if (!note) {
      elements.researchNoteStatus.textContent = "Enter a note before saving";
      return;
    }
    try {
      localStorage.setItem(noteKey, note);
      elements.researchNoteStatus.textContent = "Saved on this browser only";
      const stateNow = checklistByFeature.get(key) || { region: false, source: false, notes: false };
      stateNow.notes = true;
      checklistByFeature.set(key, stateNow);
      document.querySelector('[data-review-step="notes"]').checked = true;
    } catch {
      elements.researchNoteStatus.textContent = "Could not save in this browser";
    }
  };
}

function makeList(items, target, className = "") {
  target.replaceChildren();
  for (const item of items) {
    const li = document.createElement("li");
    if (className) li.className = className;
    li.textContent = item;
    target.append(li);
  }
}

async function requestSelection(featureId) {
  try {
    const response = await fetch(`/api/catalog/${encodeURIComponent(featureId)}`, { cache: "no-store" });
    const payload = await response.json();
    if (!response.ok) throw new Error(payload.error || "This catalog entry could not be selected.");
    showSelected(payload.feature);
  } catch (error) {
    elements.count.textContent = error.message;
  }
}

function showSelected(feature) {
  selectedId = feature.feature_id;
  elements.empty.classList.add("hidden");
  elements.detail.classList.remove("hidden");
  document.getElementById("candidate-index").textContent = "CATALOG FEATURE";
  document.getElementById("candidate-name").textContent = feature.display_name;
  document.getElementById("candidate-id").textContent = feature.feature_id;
  document.getElementById("review-state").textContent = titleCase(feature.review_status);
  document.getElementById("feature-category").textContent = titleCase(feature.category);
  document.getElementById("feature-evidence-status").textContent = titleCase(feature.evidence_status);
  const [x1, y1, x2, y2] = feature.bbox_xyxy;
  elements.inspectRegion.disabled = false;
  elements.inspectRegion.onclick = () => inspectRegion(feature);
  document.getElementById("pixel-coords").textContent = `SOURCE IMAGE PIXELS · (${x1}, ${y1})–(${x2}, ${y2}) · x₂/y₂ exclusive`;

  const readingsBlock = document.getElementById("readings-block");
  readingsBlock.classList.toggle("hidden", feature.alternative_readings.length === 0);
  makeList(feature.alternative_readings, document.getElementById("readings-list"));
  makeList(feature.direct_observations, document.getElementById("observation-list"));
  document.getElementById("interpretation-text").textContent = feature.interpretation;
  makeList(feature.uncertainty_notes, document.getElementById("uncertainty-list"));
  makeList(feature.evidence_needed, document.getElementById("evidence-needed-list"));

  const evidenceList = document.getElementById("evidence-list");
  evidenceList.replaceChildren();
  for (const reference of feature.evidence_references) {
    const li = document.createElement("li");
    li.className = "evidence-reference";
    const strong = document.createElement("strong");
    strong.textContent = `${titleCase(reference.reference_id)} · ${titleCase(reference.evidence_status)}`;
    const source = document.createElement("small");
    source.textContent = `${reference.source} — ${reference.scope_note}`;
    const status = document.createElement("span");
    status.className = `reference-status ${reference.evidence_status === "research_note_unverified" ? "unverified-lead" : "consulted-source"}`;
    status.textContent = sourceEvidenceLabel(reference.evidence_status);
    li.append(strong, status, source);
    appendEvidenceLink(li, reference.source);
    evidenceList.append(li);
  }

  const provenance = feature.provenance;
  document.getElementById("provenance-text").textContent =
    `Origin: ${provenance.origin_annotation_file}. Method: ${provenance.annotation_method}`;
  const historyList = document.getElementById("history-list");
  makeList(feature.annotation_history.map((event) =>
    `${titleCase(event.action)} · ${titleCase(event.evidence_status)} — ${event.note}`
  ), historyList);
  renderReviewWorkflow(feature);

  if (elements.jumpToExpedition) {
    elements.jumpToExpedition.onclick = () => {
      if (feature.feature_id === "GS-1854-002" && elements.fieldSiteSelect) {
        elements.fieldSiteSelect.value = "lead-lalbagh";
        elements.fieldSiteSelect.dispatchEvent(new Event("change"));
      }
      document.getElementById("field-expedition")?.scrollIntoView({ behavior: "smooth" });
    };
  }

  for (const button of elements.list.querySelectorAll(".catalog-entry")) {
    button.setAttribute("aria-selected", String(button.dataset.featureId === selectedId));
  }
  for (const marker of elements.overlays.querySelectorAll(".map-mark")) {
    const selected = marker.dataset.featureId === selectedId;
    marker.classList.toggle("selected", selected);
    marker.setAttribute("aria-pressed", String(selected));
  }

  elements.assistantButton.disabled = !feature.assistant_available;
  elements.assistantFootnote.textContent = feature.assistant_available
    ? "LOCAL MOCK · NO CREDITS · NO LIVE INFERENCE"
    : "OFFLINE ASSISTANT NOT LINKED TO THIS ENTRY";
  elements.assistantEmpty.textContent = feature.assistant_available
    ? "The offline preview will use the existing local CLI in mock mode."
    : "The existing local assistant CLI is linked only to the original three annotations.";
  elements.assistantEmpty.classList.remove("hidden");
  elements.assistantOutput.classList.add("hidden");
  elements.assistantError.classList.add("hidden");
}

function drawMapMarkers(features) {
  elements.overlays.replaceChildren();
  for (const feature of features) {
    const [x1, y1, x2, y2] = feature.bbox_xyxy;
    const marker = document.createElement("button");
    marker.type = "button";
    marker.className = "map-mark";
    marker.dataset.featureId = feature.feature_id;
    marker.dataset.short = feature.feature_id.slice(-3);
    marker.setAttribute("aria-label", `${feature.feature_id}, ${feature.display_name}, source-image pixel box`);
    marker.setAttribute("aria-pressed", String(feature.feature_id === selectedId));
    marker.style.left = `${x1 / sourceDimensions.width * 100}%`;
    marker.style.top = `${y1 / sourceDimensions.height * 100}%`;
    marker.style.width = `${(x2 - x1) / sourceDimensions.width * 100}%`;
    marker.style.height = `${(y2 - y1) / sourceDimensions.height * 100}%`;
    if (feature.feature_id === selectedId) marker.classList.add("selected");
    marker.addEventListener("pointerdown", (event) => event.stopPropagation());
    marker.addEventListener("click", (event) => {
      event.stopPropagation();
      requestSelection(feature.feature_id);
    });
    elements.overlays.append(marker);
  }
}

function drawCatalogList(features) {
  elements.list.replaceChildren();
  if (!features.length) {
    const empty = document.createElement("div");
    empty.className = "catalog-empty";
    empty.textContent = "No catalog entries match these filters.";
    elements.list.append(empty);
    return;
  }
  features.forEach((feature, index) => {
    const button = document.createElement("button");
    button.type = "button";
    button.className = "catalog-entry";
    button.dataset.featureId = feature.feature_id;
    button.setAttribute("role", "option");
    button.setAttribute("aria-selected", String(feature.feature_id === selectedId));

    const number = document.createElement("span");
    number.className = "catalog-entry-index";
    number.textContent = String(index + 1).padStart(2, "0");
    const copy = document.createElement("span");
    copy.className = "catalog-entry-copy";
    const name = document.createElement("span");
    name.className = "catalog-entry-name";
    name.textContent = feature.display_name;
    const id = document.createElement("span");
    id.className = "catalog-entry-id";
    id.textContent = feature.feature_id;
    copy.append(name, id);
    const meta = document.createElement("span");
    meta.className = "catalog-entry-meta";
    const category = document.createElement("span");
    category.textContent = feature.category;
    const status = document.createElement("span");
    status.textContent = feature.review_status === "pending_human_review" ? "pending" : titleCase(feature.review_status);
    meta.append(category, status);
    button.append(number, copy, meta);
    button.addEventListener("click", () => requestSelection(feature.feature_id));
    elements.list.append(button);
  });
}

function populateFilters(payload) {
  const categoryValue = elements.category.value || "all";
  const statusValue = elements.reviewStatus.value || "all";
  elements.category.replaceChildren(new Option("All categories", "all"));
  for (const category of payload.categories) elements.category.add(new Option(titleCase(category), category));
  elements.category.value = payload.categories.includes(categoryValue) || categoryValue === "all" ? categoryValue : "all";
  elements.reviewStatus.replaceChildren(new Option("All statuses", "all"));
  for (const status of payload.review_statuses) elements.reviewStatus.add(new Option(titleCase(status), status));
  elements.reviewStatus.value = payload.review_statuses.includes(statusValue) || statusValue === "all" ? statusValue : "all";
}

async function refreshCatalog() {
  const revision = ++filterRevision;
  elements.count.textContent = "Updating catalog…";
  const params = new URLSearchParams({
    q: elements.search.value,
    category: elements.category.value || "all",
    review_status: elements.reviewStatus.value || "all"
  });
  try {
    const response = await fetch(`/api/catalog?${params}`, { cache: "no-store" });
    const payload = await response.json();
    if (!response.ok) throw new Error(payload.error || "The feature catalog could not be loaded.");
    if (revision !== filterRevision) return;
    visibleFeatures = payload.features;
    sourceDimensions = { width: payload.source_map.width_px, height: payload.source_map.height_px };
    populateFilters(payload);
    drawCatalogList(visibleFeatures);
    drawMapMarkers(visibleFeatures);
    const totalDot = document.createElement("span");
    const totalText = document.createTextNode(` ${payload.catalog_total} ENTRIES`);
    elements.total.replaceChildren(totalDot, totalText);
    elements.count.textContent = `${payload.total} ${payload.total === 1 ? "entry" : "entries"} shown`;
    elements.summary.textContent = `${payload.catalog_total} catalog entries · identities remain unverified`;
    if (selectedId && !visibleFeatures.some((feature) => feature.feature_id === selectedId)) clearSelection();
  } catch (error) {
    if (revision !== filterRevision) return;
    elements.count.textContent = error.message;
    elements.list.replaceChildren();
    const empty = document.createElement("div");
    empty.className = "catalog-empty";
    empty.textContent = "Catalog unavailable. Check the local server and retry.";
    elements.list.append(empty);
    // A catalog API failure must not cover the independently loaded map image.
  }
}

function clearSelection() {
  selectedId = null;
  elements.inspectRegion.disabled = true;
  elements.empty.classList.remove("hidden");
  elements.detail.classList.add("hidden");
  elements.assistantButton.disabled = true;
  elements.assistantFootnote.textContent = "LOCAL MOCK · NO CREDITS · NO LIVE INFERENCE";
  elements.assistantEmpty.textContent = "Choose a catalog entry above to prepare an offline note.";
  elements.assistantEmpty.classList.remove("hidden");
  elements.assistantOutput.classList.add("hidden");
  drawMapMarkers(visibleFeatures);
  drawCatalogList(visibleFeatures);
}

function showAssistantResult(payload) {
  const result = payload.result;
  elements.assistantOutput.replaceChildren();
  const notice = document.createElement("p");
  notice.className = "assistant-notice";
  notice.textContent = payload.notice;
  elements.assistantOutput.append(notice);
  const groups = [
    ["Observation from annotation", result.observations],
    ["Uncertain interpretation", result.hypotheses],
    ["Unresolved questions", result.unresolved_questions]
  ];
  for (const [label, lines] of groups) {
    const heading = document.createElement("h3");
    heading.textContent = label;
    elements.assistantOutput.append(heading);
    for (const line of lines) {
      const p = document.createElement("p");
      p.textContent = line;
      elements.assistantOutput.append(p);
    }
  }
  if (result.source_supported_claims.length) {
    const heading = document.createElement("h3");
    heading.textContent = "Text from user-supplied note";
    elements.assistantOutput.append(heading);
    for (const claim of result.source_supported_claims) {
      const p = document.createElement("p");
      p.textContent = `${claim.claim} — ${claim.support_status}`;
      elements.assistantOutput.append(p);
    }
  }
  const next = document.createElement("p");
  const label = document.createElement("span");
  label.className = "output-label";
  label.textContent = "Suggested human review: ";
  next.append(label, document.createTextNode(result.recommended_next_step));
  elements.assistantOutput.append(next);
  elements.assistantEmpty.classList.add("hidden");
  elements.assistantOutput.classList.remove("hidden");
}

elements.map.addEventListener("load", () => elements.mapLoading.classList.add("hidden"));
elements.map.addEventListener("error", () => {
  elements.mapLoading.classList.add("hidden");
  elements.mapError.classList.remove("hidden");
});
if (elements.map.complete && elements.map.naturalWidth > 0) elements.mapLoading.classList.add("hidden");

document.getElementById("zoom-in").addEventListener("click", () => { zoom = Math.min(zoom + 0.25, 3.5); setMapTransform(); });
document.getElementById("zoom-out").addEventListener("click", () => { zoom = Math.max(zoom - 0.25, 1); if (zoom === 1) panX = panY = 0; setMapTransform(); });
document.getElementById("zoom-reset").addEventListener("click", showFullMap);
elements.mapWindow.addEventListener("wheel", (event) => {
  event.preventDefault();
  zoom = Math.max(1, Math.min(3.5, zoom + (event.deltaY < 0 ? 0.15 : -0.15)));
  if (zoom === 1) panX = panY = 0;
  setMapTransform();
}, { passive: false });
elements.mapWindow.addEventListener("pointerdown", (event) => {
  if (event.target.closest(".zoom-controls") || event.target.closest(".map-mark")) return;
  dragStart = { x: event.clientX - panX, y: event.clientY - panY, pointer: event.pointerId };
  elements.mapWindow.classList.add("is-dragging");
  elements.mapWindow.setPointerCapture(event.pointerId);
});
elements.mapWindow.addEventListener("pointermove", (event) => {
  if (!dragStart || dragStart.pointer !== event.pointerId) return;
  panX = event.clientX - dragStart.x;
  panY = event.clientY - dragStart.y;
  setMapTransform();
});
function stopPan() { dragStart = null; elements.mapWindow.classList.remove("is-dragging"); }
elements.mapWindow.addEventListener("pointerup", stopPan);
elements.mapWindow.addEventListener("pointercancel", stopPan);

elements.search.addEventListener("input", () => {
  clearTimeout(searchTimer);
  searchTimer = setTimeout(refreshCatalog, 160);
});
elements.category.addEventListener("change", refreshCatalog);
elements.reviewStatus.addEventListener("change", refreshCatalog);
elements.assistantButton.addEventListener("click", async () => {
  if (!selectedId || elements.assistantButton.disabled) return;
  elements.assistantButton.disabled = true;
  elements.assistantButton.setAttribute("aria-busy", "true");
  elements.assistantError.classList.add("hidden");
  elements.assistantOutput.classList.add("hidden");
  elements.assistantEmpty.classList.remove("hidden");
  elements.assistantEmpty.textContent = "Preparing a local mock note…";
  try {
    const response = await fetch("/api/assistant", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ candidate_id: selectedId })
    });
    const payload = await response.json();
    if (!response.ok) throw new Error(payload.error || "Offline preview could not be prepared.");
    showAssistantResult(payload);
  } catch (error) {
    elements.assistantEmpty.classList.add("hidden");
    elements.assistantError.textContent = `${error.message} You can retry the offline preview.`;
    elements.assistantError.classList.remove("hidden");
  } finally {
    elements.assistantButton.disabled = !selectedId || !visibleFeatures.find((feature) => feature.feature_id === selectedId)?.assistant_available;
    elements.assistantButton.removeAttribute("aria-busy");
  }
});

elements.category.value = "all";
elements.reviewStatus.value = "all";
refreshCatalog();

/* ==========================================================================
   Field Expedition & Touch Grass Ground-Observation Logic
   ========================================================================== */

const FIELD_LEADS = {
  "lead-lalbagh": {
    id: "lead-lalbagh",
    candidateId: "GS-1854-002",
    title: "Lalbagh Botanical Garden Precinct & Lake",
    category: "Public Botanical Garden & Lake",
    vantageSuggestion: "Lalbagh West Gate / Lotus Pond / Lake pedestrian path",
    contextSummary: "Historical map candidate GS-1854-002 carries an uncertain reading 'Lalbagh Tank' in 1854 scan pixels (185, 1165)–(300, 1255). Today, Lalbagh Botanical Garden is an official BBMP horticulture civic park containing a public lake, historic rain trees, and peninsular gneiss granite outcrops.",
    epistemicNote: "Visiting Lalbagh allows real-world observation of terrain depressions, granite elevations, and water retention. It does NOT prove that candidate GS-1854-002 was at this modern location or has vanished.",
    sources: [
      { name: "BBMP Horticulture: Lalbagh Botanical Garden", url: "https://site.bbmp.gov.in/departmentwebsites/Horticulture/aboutus.html" },
      { name: "Karnataka Tourism: Lalbagh Garden", url: "https://karnatakatourism.org/en/attractions/lalbagh-botanical-garden/" },
      { name: "Current Science (2012): Lalbagh Garden & Tank Analysis", url: "/local-evidence?path=docs%2Fcandidate_research.md" }
    ]
  },
  "lead-ulsoor": {
    id: "lead-ulsoor",
    candidateId: null,
    title: "Ulsoor / Halasuru Lake Public Promenade",
    category: "Public Lake & Civic Promenade",
    vantageSuggestion: "Ulsoor Lake northern pedestrian promenade / Kensington Road perimeter",
    contextSummary: "The label 'Ulsoor Tank' is readable directly on the c.1854 scan. Today Ulsoor Lake is maintained as an active municipal water body with an island and a paved public promenade.",
    epistemicNote: "Secondary histories (APU 2018, IISc 2002) cite conflicting construction chronologies (1860s–1890s vs older feature). Observing the modern lake bund shows contemporary water retention, while historical continuity remains an open archival question.",
    sources: [
      { name: "Bengaluru Urban Tourism: Ulsoor Lake", url: "https://bengaluruurban.nic.in/en/tourism/" },
      { name: "Azim Premji University (2018): Lakes of Bengaluru", url: "/local-evidence?path=docs%2Fcandidate_research.md" },
      { name: "WIT Transactions (2011): Bangalore Tank System", url: "https://doi.org/10.2495/RAV110351" }
    ]
  },
  "lead-sampangi": {
    id: "lead-sampangi",
    candidateId: null,
    title: "Sampangi / Kanteerava Civic Area",
    category: "Civic Stadium & Altered Basin",
    vantageSuggestion: "Kanteerava Stadium exterior public sidewalk / Raja Ram Mohan Roy Road",
    contextSummary: "The label 'Sampangi Tank' is clearly visible on the c.1854 scan. Studied by Unnikrishnan & Nagendra (2014) as a seasonal lake transformed during the mid-20th century into Kanteerava Stadium, with a small remnant water body preserved nearby.",
    epistemicNote: "Observing from public sidewalks reveals how a natural catchment was adapted for civic athletic use. It must not be cited as 'total disappearance' without consulting archival conversion records.",
    sources: [
      { name: "NMML / APU (2014): Unruly Commons — Sampangi Lake", url: "https://publications.azimpremjifoundation.org/196/" },
      { name: "Azim Premji University (2018): Working Paper No. 10", url: "/local-evidence?path=docs%2Fcandidate_research.md" }
    ]
  },
  "lead-fort": {
    id: "lead-fort",
    candidateId: null,
    title: "Bangalore Fort & Tipu Sultan’s Summer Palace Precinct",
    category: "Heritage Monument & Urban Ridge",
    vantageSuggestion: "Tipu Sultan’s Summer Palace public grounds / Albert Victor Road footpath",
    contextSummary: "A distinctive enclosed oval fort is mapped in the southwest quadrant of the 1854 sheet. The surviving Bangalore Fort gate and Tipu Sultan’s Summer Palace (completed 1791) represent stable historic structures.",
    epistemicNote: "Used as a key historical reference point. Useful for observing the relative elevation of the old Pete ridge compared to neighboring low-lying basins.",
    sources: [
      { name: "Bengaluru Urban District: Tipu Sultan’s Summer Palace", url: "https://bengaluruurban.nic.in/en/tourist-place/tipu-sultans-summer-palace/" },
      { name: "Independent Georeferencing Validation Notes", url: "/georeferencing-validation" }
    ]
  },
  "lead-general": {
    id: "lead-general",
    candidateId: null,
    title: "General Bengaluru Urban Ridge & Valley Corridor",
    category: "Topographic Valley Corridor",
    vantageSuggestion: "Any safe municipal sidewalk overlooking a visible street gradient",
    contextSummary: "Bengaluru is built along three major natural valleys (Vrishabhavathi, Challaghatta, and Hebbal). Historic tanks were interconnected cascading reservoirs following these natural slopes.",
    epistemicNote: "Observe natural dips in road grades and stormwater flow lines from safe sidewalks. Never enter canal channels or private land.",
    sources: [
      { name: "WIT Transactions (2011): Water Tank System Morphology", url: "https://doi.org/10.2495/RAV110351" }
    ]
  }
};

function renderFieldLeadContext(leadId) {
  const lead = FIELD_LEADS[leadId];
  if (!lead || !elements.fieldLeadContext) return;
  elements.fieldLeadContext.replaceChildren();

  const titleEl = document.createElement("h4");
  titleEl.textContent = `${lead.title} · ${lead.category}`;

  const descEl = document.createElement("p");
  descEl.textContent = lead.contextSummary;

  const vantageEl = document.createElement("p");
  const vantageStrong = document.createElement("strong");
  vantageStrong.textContent = "Suggested Safe Vantage Point: ";
  vantageEl.append(vantageStrong, document.createTextNode(lead.vantageSuggestion));

  const epistemicEl = document.createElement("p");
  epistemicEl.className = "field-epistemic-callout";
  const epistemicStrong = document.createElement("strong");
  epistemicStrong.textContent = "Epistemic Note: ";
  epistemicEl.append(epistemicStrong, document.createTextNode(lead.epistemicNote));

  const sourcesDiv = document.createElement("div");
  sourcesDiv.className = "field-lead-sources";
  const sourcesLabel = document.createElement("span");
  sourcesLabel.textContent = "Source References: ";
  sourcesDiv.append(sourcesLabel);

  lead.sources.forEach((src, idx) => {
    if (idx > 0) sourcesDiv.append(document.createTextNode(" · "));
    const a = document.createElement("a");
    a.href = src.url;
    a.target = "_blank";
    a.rel = "noopener noreferrer";
    a.textContent = src.name;
    sourcesDiv.append(a);
  });

  elements.fieldLeadContext.append(titleEl, descEl, vantageEl, epistemicEl, sourcesDiv);
}

function updateChecklistProgress(leadId) {
  const checkboxes = document.querySelectorAll("[data-field-check]");
  const total = checkboxes.length;
  let checked = 0;
  const checkedKeys = [];

  checkboxes.forEach((cb) => {
    if (cb.checked) {
      checked++;
      checkedKeys.push(cb.dataset.fieldCheck);
    }
  });

  if (elements.checklistProgressBadge) {
    elements.checklistProgressBadge.textContent = `${checked} / ${total} observed`;
  }

  if (leadId) {
    try {
      localStorage.setItem(`ghost-shore:field-checks:${leadId}`, JSON.stringify(checkedKeys));
    } catch { /* LocalStorage failures handled gracefully */ }
  }
}

function loadFieldExpedition(leadId) {
  renderFieldLeadContext(leadId);
  const lead = FIELD_LEADS[leadId];

  if (elements.fieldNoteDate && !elements.fieldNoteDate.value) {
    elements.fieldNoteDate.value = new Date().toISOString().split("T")[0];
  }

  if (elements.fieldVantagePoint) {
    elements.fieldVantagePoint.placeholder = `e.g. ${lead ? lead.vantageSuggestion : "Public sidewalk"}`;
  }

  const noteKey = `ghost-shore:field-note:${leadId}`;
  try {
    const rawNote = localStorage.getItem(noteKey);
    if (rawNote) {
      const data = JSON.parse(rawNote);
      if (elements.fieldNoteDate && data.date) elements.fieldNoteDate.value = data.date;
      if (elements.fieldNoteWeather && data.weather) elements.fieldNoteWeather.value = data.weather;
      if (elements.fieldVantagePoint && data.vantagePoint) elements.fieldVantagePoint.value = data.vantagePoint;
      if (elements.fieldObservationsText && data.observations) elements.fieldObservationsText.value = data.observations;
      if (elements.fieldQuestionsText && data.questions) elements.fieldQuestionsText.value = data.questions;

      const savedTime = data.savedAt ? new Date(data.savedAt).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }) : "";
      if (elements.fieldNoteStatus) {
        elements.fieldNoteStatus.textContent = `Saved on this browser (${savedTime || "previously"})`;
      }
    } else {
      if (elements.fieldObservationsText) elements.fieldObservationsText.value = "";
      if (elements.fieldQuestionsText) elements.fieldQuestionsText.value = "";
      if (elements.fieldVantagePoint) elements.fieldVantagePoint.value = "";
      if (elements.fieldNoteWeather) elements.fieldNoteWeather.value = "";
      if (elements.fieldNoteStatus) elements.fieldNoteStatus.textContent = "Not saved yet for this site";
    }
  } catch {
    if (elements.fieldNoteStatus) elements.fieldNoteStatus.textContent = "Browser storage unavailable";
  }

  const checkKey = `ghost-shore:field-checks:${leadId}`;
  try {
    const rawChecks = localStorage.getItem(checkKey);
    const checkedKeys = rawChecks ? new Set(JSON.parse(rawChecks)) : new Set();
    document.querySelectorAll("[data-field-check]").forEach((cb) => {
      cb.checked = checkedKeys.has(cb.dataset.fieldCheck);
    });
  } catch {
    document.querySelectorAll("[data-field-check]").forEach((cb) => { cb.checked = false; });
  }

  updateChecklistProgress(null);
}

function saveFieldExpedition(leadId) {
  const vantage = elements.fieldVantagePoint ? elements.fieldVantagePoint.value.trim() : "";
  const observations = elements.fieldObservationsText ? elements.fieldObservationsText.value.trim() : "";

  if (!vantage || !observations) {
    if (elements.fieldNoteStatus) {
      elements.fieldNoteStatus.textContent = "Please fill in a public vantage point and observations before saving.";
    }
    return;
  }

  const payload = {
    leadId,
    date: elements.fieldNoteDate ? elements.fieldNoteDate.value : "",
    weather: elements.fieldNoteWeather ? elements.fieldNoteWeather.value.trim() : "",
    vantagePoint: vantage,
    observations,
    questions: elements.fieldQuestionsText ? elements.fieldQuestionsText.value.trim() : "",
    savedAt: new Date().toISOString()
  };

  try {
    localStorage.setItem(`ghost-shore:field-note:${leadId}`, JSON.stringify(payload));
    if (elements.fieldNoteStatus) {
      elements.fieldNoteStatus.textContent = `Saved in this browser only (private) at ${new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}`;
    }
  } catch {
    if (elements.fieldNoteStatus) {
      elements.fieldNoteStatus.textContent = "Could not save in browser storage.";
    }
  }
}

function resetFieldExpedition(leadId) {
  if (elements.fieldObservationsText) elements.fieldObservationsText.value = "";
  if (elements.fieldQuestionsText) elements.fieldQuestionsText.value = "";
  if (elements.fieldVantagePoint) elements.fieldVantagePoint.value = "";
  if (elements.fieldNoteWeather) elements.fieldNoteWeather.value = "";
  if (elements.fieldNoteDate) elements.fieldNoteDate.value = new Date().toISOString().split("T")[0];

  document.querySelectorAll("[data-field-check]").forEach((cb) => { cb.checked = false; });
  updateChecklistProgress(leadId);

  try {
    localStorage.removeItem(`ghost-shore:field-note:${leadId}`);
    localStorage.removeItem(`ghost-shore:field-checks:${leadId}`);
  } catch { /* graceful */ }

  if (elements.fieldNoteStatus) elements.fieldNoteStatus.textContent = "Form and checklist reset";
}

function renderPrintableFieldSheet(leadId) {
  const lead = FIELD_LEADS[leadId];
  if (!lead || !elements.printableFieldSheet) return;

  const dateVal = (elements.fieldNoteDate && elements.fieldNoteDate.value) || new Date().toISOString().split("T")[0];
  const weatherVal = (elements.fieldNoteWeather && elements.fieldNoteWeather.value.trim()) || "_________________________";
  const vantageVal = (elements.fieldVantagePoint && elements.fieldVantagePoint.value.trim()) || lead.vantageSuggestion;
  const observationsVal = (elements.fieldObservationsText && elements.fieldObservationsText.value.trim()) || "";
  const questionsVal = (elements.fieldQuestionsText && elements.fieldQuestionsText.value.trim()) || "";

  elements.printableFieldSheet.replaceChildren();

  const headDiv = document.createElement("div");
  headDiv.className = "print-head";
  headDiv.innerHTML = `
    <div class="print-title">
      <h1>GHOST SHORE — FIELD EXPEDITION WORKSHEET</h1>
      <p>Touch Grass Week 1 · Safe &amp; Evidence-Grounded Historical Bengaluru Fieldwork</p>
    </div>
    <div class="print-badge">
      <strong>SOURCE MAP: Plan of Bangalore (c. 1854)</strong><br>
      British Library IOR/X/14628
    </div>
  `;

  const discDiv = document.createElement("div");
  discDiv.className = "print-disclaimer";
  discDiv.innerHTML = `
    <div class="print-disclaimer-item">
      <strong>EPISTEMIC SAFEGUARD:</strong> All 1854 map annotations exist strictly in historical scan pixels (xyxy). Modern field observations record current urban topography and civic morphology. Visiting a public park does NOT prove an 1854 candidate location or continuous survival.
    </div>
    <div class="print-disclaimer-item print-safety-bar">
      <strong>SAFETY PROTOCOL:</strong> Public pathways only • Daylight visits • Zero trespassing • Never enter drains or construction sites.
    </div>
  `;

  const metaGrid = document.createElement("div");
  metaGrid.className = "print-meta-grid";
  metaGrid.innerHTML = `
    <div><strong>Target Reference:</strong> ${lead.title}</div>
    <div><strong>Date of Observation:</strong> ${dateVal}</div>
    <div><strong>Public Vantage Point:</strong> ${vantageVal}</div>
    <div><strong>Weather / Conditions:</strong> ${weatherVal}</div>
  `;

  const checkSection = document.createElement("div");
  checkSection.className = "print-checklist-section";
  checkSection.innerHTML = `<h3>Guided Field Observation Checklist (12 criteria)</h3>`;

  const checkColumns = document.createElement("div");
  checkColumns.className = "print-checklist-columns";

  const groups = Array.from(document.querySelectorAll(".checklist-group"));
  const col1 = document.createElement("div");
  col1.className = "print-checklist-col";
  const col2 = document.createElement("div");
  col2.className = "print-checklist-col";

  groups.forEach((grp, idx) => {
    const targetCol = idx < 2 ? col1 : col2;
    const title = grp.querySelector("h5")?.textContent || "";
    const groupHead = document.createElement("div");
    groupHead.className = "print-group-head";
    groupHead.textContent = title;
    targetCol.append(groupHead);

    grp.querySelectorAll(".field-check").forEach((fc) => {
      const isChecked = fc.querySelector("input")?.checked;
      const text = fc.querySelector("span")?.textContent || "";
      const row = document.createElement("div");
      row.className = "print-check-row";
      row.innerHTML = `<span class="print-check-box">${isChecked ? "✓" : ""}</span><span>${text}</span>`;
      targetCol.append(row);
    });
  });

  checkColumns.append(col1, col2);
  checkSection.append(checkColumns);

  const notesGrid = document.createElement("div");
  notesGrid.className = "print-notes-grid";

  const obsSec = document.createElement("div");
  obsSec.className = "print-notes-section";
  obsSec.innerHTML = `
    <h3>Tangible Physical Landscape Observations</h3>
    <div class="print-notes-body">${observationsVal || "\n\n_________________________________________________________________________________\n\n_________________________________________________________________________________\n\n_________________________________________________________________________________"}</div>
  `;

  const qSec = document.createElement("div");
  qSec.className = "print-notes-section";
  qSec.innerHTML = `
    <h3>Unresolved Questions &amp; Next Archival Steps</h3>
    <div class="print-notes-body">${questionsVal || "\n\n_________________________________________________________________________________\n\n_________________________________________________________________________________"}</div>
  `;

  notesGrid.append(obsSec, qSec);

  const footDiv = document.createElement("div");
  footDiv.className = "print-foot";
  footDiv.innerHTML = `Ghost Shore Project • Private Local Field Record • Preserving Historical Uncertainty in Bengaluru Map Research`;

  elements.printableFieldSheet.append(headDiv, discDiv, metaGrid, checkSection, notesGrid, footDiv);
  window.print();
}

function initFieldExpedition() {
  if (!elements.fieldSiteSelect) return;

  const currentLeadId = () => elements.fieldSiteSelect.value || "lead-lalbagh";

  elements.fieldSiteSelect.addEventListener("change", () => {
    loadFieldExpedition(currentLeadId());
  });

  document.querySelectorAll("[data-field-check]").forEach((cb) => {
    cb.addEventListener("change", () => {
      updateChecklistProgress(currentLeadId());
    });
  });

  if (elements.saveFieldNoteBtn) {
    elements.saveFieldNoteBtn.addEventListener("click", () => {
      saveFieldExpedition(currentLeadId());
    });
  }

  if (elements.resetFieldNoteBtn) {
    elements.resetFieldNoteBtn.addEventListener("click", () => {
      resetFieldExpedition(currentLeadId());
    });
  }

  if (elements.printFieldSheetBtn) {
    elements.printFieldSheetBtn.addEventListener("click", () => {
      renderPrintableFieldSheet(currentLeadId());
    });
  }

  loadFieldExpedition(currentLeadId());
}

initFieldExpedition();

