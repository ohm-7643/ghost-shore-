# Ghost Shore — Milestone 2C: Independent georeferencing validation

**Assessment:** No independent checkpoint has been verified. The existing evidence supports transfer of the Warper pixel locations to this raster, but does not independently validate geographic accuracy near the candidates. Do not publish candidate locations or treat the map alignment as validated.

## What the existing fit measures

The diagnostic uses 11 control points exported from [Wikimaps Warper map 2845](https://warper.wmflabs.org/maps/2845). Their source raster coordinates were transferred to the local 1280×1557 scan through the high-confidence raster similarity fit. A first-order affine transform was then fitted from the transferred local pixels to the Warper longitude/latitude values (projected to EPSG:32643 for the calculation). The individual points and errors are in [`gcp_residuals.csv`](../outputs/georeferencing_trial/gcp_residuals.csv).

The 80.35 m mean, 87.63 m RMSE, and 150.12 m maximum are residuals measured on the same 11 points that estimated the affine transformation. They describe how closely the model fits its inputs. They are not independent validation because no withheld, independently identified locations were measured against the fitted transform. Leave-one-out calculations on those same 11 points remain internal diagnostics; they do not create independent ground truth.

The controls occupy local-image x=264.5–739.0 and y=113.8–1141.7. Candidate centers are GS-1854-001 (127.5, 637.5), GS-1854-002 (242.5, 1210), and GS-1854-003 (1067.5, 1120), each outside that bounding rectangle. This means candidate positions require extrapolation beyond the control-point envelope. A bounding rectangle is only a coarse coverage check, but here it demonstrates that none of the candidate centers is surrounded by controls. The reported residuals therefore do not establish accuracy at any candidate location. They also do not measure source-map accuracy, Warper point-placement accuracy, paper distortion, or local scan deformation.

## Independent checkpoint search

I visually reviewed the local/public raster comparison and the GCP residual overlay, as well as the candidate annotations. The GCP CSV contains coordinates and blank names; the plotted controls cluster around the central mapped area. There is no point-by-point description establishing which landmark each control represents. Consequently, a proposed landmark cannot be declared independent merely because it looks recognizable: the exact historical point must first be selected and compared to all 11 existing control locations.

The following are **checkpoint leads for a human reviewer**, not verified correspondences. Pixel fields are blank because no unique matched point (such as a specific fort gate corner or fixed boundary junction) was directly and unambiguously identified. Broad area centroids would not be defensible checkpoint coordinates.

| Lead | Historical-map observation | Modern reference and what it establishes | Proximity / coverage | Status and Warper-fit use |
|---|---|---|---|---|
| Bangalore Fort enclosure | A distinctive enclosed/oval fort feature is visible toward the southwest of the sheet. No exact bastion, gate, or corner has been selected as a point. | [Bengaluru Urban District: Tipu Sultan's Summer Palace](https://bengaluruurban.nic.in/en/tourist-place/tipu-sultans-summer-palace/) says the palace lies within Bangalore Fort's walls and dates its completion to 1791. It supports the persistence of the Fort as a named historic place, not a precise match between a particular mapped wall point and a modern point. | Southwestern map margin; a useful outer-area lead, but not a close checkpoint for all candidates. | **proposed**; exact point not selected, so reuse/independence has not been established. |
| Lalbagh garden enclosure / boundary | The map contains a Lalbagh label and surrounding garden-like mapped area near the southwest. This is separate from treating candidate 002's uncertain “Lalbagh Tank” reading as a checkpoint. No fixed boundary corner has been matched. | [BBMP Horticulture Department: Lalbagh Botanical Garden](https://site.bbmp.gov.in/departmentwebsites/Horticulture/aboutus.html) describes the current garden and its development; [Karnataka Tourism: Lalbagh Botanical Garden](https://karnatakatourism.org/en/attractions/lalbagh-botanical-garden/) gives the garden's historical context. These support the named place, not continuity of a particular 1854 boundary or an exact modern control point. | Potentially near candidate 002; boundary may have changed. Could help test the south/southwest only after a specific stable point is matched. | **proposed**; exact point not selected, so reuse/independence has not been established. |
| Ulsoor Tank / lake shoreline | The historical sheet labels an Ulsoor tank feature in the central/eastern mapped area. A particular shoreline vertex has not been selected. | [Bengaluru Urban District tourism](https://bengaluruurban.nic.in/en/tourism/) identifies Ulsoor Lake as a current Bengaluru lake. This establishes a current named feature, not that a specific historic shoreline vertex is unchanged. | Central/east, but not a reliable margin checkpoint; some Warper controls lie in the same broad central/eastern area. | **unresolved**; likely-area overlap with existing controls must be checked before it can count as independent. |

No item above is `verified`. The first two are plausible visual and documentary leads only. The Ulsoor comparison is unresolved and must not be counted as independent until the exact point is compared with the Warper controls. There is no sufficiently supported, independently matched lead near GS-1854-003; the visible generic tank label cannot validate itself. No modern location coordinates were assigned to any candidate or checkpoint.

## Validation plan

1. Obtain a modern geospatial reference with stable, identifiable geometry (preferably an authoritative survey/cadastral/topographic layer or a government heritage/site plan). A place-name page alone is insufficient for point placement.
2. Have a reviewer independently mark exact, repeatable historical points on the original map—for example, a specific fort wall corner or a persistent garden boundary junction—and mark the corresponding modern point without viewing fitted residuals.
3. Compare each proposed point with all 11 Warper control locations. Any point reused by the Warper fit, or ambiguous with one, is not an independent checkpoint. Record its source, pixel location, reviewer, and selection rationale before evaluating the transform.
4. Seek checkpoints around each candidate region and near all four map margins, distributed across the full mapped area. Do not use candidate features or uncertain labels as checkpoints.
5. Evaluate the frozen existing transform against these hold-outs, report per-point and aggregate errors plus spatial pattern, and only then decide whether a more suitable transformation is justified. Candidate identity and disappearance remain separate historical questions.

## Recommendation

**CONDITIONAL GO** for continued validation research and human landmark review. **NO-GO** for candidate geospatial claims or candidate coordinate publication now. The available web sources verify that some plausible named landmarks exist today, but none supplies a securely matched, independently selected checkpoint on this scan. Stop before interpreting candidate positions geographically until a distributed set of hold-outs has been identified and tested.

No visual checkpoint overlay was created: placing markers would imply exact historical point picks that the evidence does not currently support. The existing source comparison and residual overlay remain unchanged.
