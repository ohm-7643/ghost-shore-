# Ghost Shore — Milestone 2A candidate research

**Status:** research review only. No candidate is identified as a confirmed lake or a disappeared water body. No source-image pixel coordinate below is treated as a geographic coordinate.

## Scope and source scan

I reviewed the project [README](../README.md), current [candidate annotations](../outputs/milestone_1/candidate_annotations.json), [candidate review sheet](../outputs/milestone_1/review/candidate_review_sheet.png), the original `data/raw/bangalore_1854.jpg`, and its enlarged candidate crops. The source scan is a 1280 × 1557 RGB JPEG. The candidate boxes are in top-left-origin source-image pixels, with exclusive right and bottom edges:

| Candidate | Source-image bbox `(x1, y1, x2, y2)` |
|---|---:|
| GS-1854-001 | `(75, 585, 180, 690)` |
| GS-1854-002 | `(185, 1165, 300, 1255)` |
| GS-1854-003 | `(1000, 1060, 1135, 1180)` |

The scan itself shows the title *Plan of Bangalore*, publisher text at the bottom, and a small printed number at upper right that appears to read “43.” The project filename calls it an 1854 map. The [British Library record for atlas item IOR/X/14628/48](https://searcharchives.bl.uk/catalog/041-002248113) describes “No.48. Plan Of Bangalore” and gives a scale of 650 yards to an inch (1:23,400). Its [parent atlas record](https://searcharchives.bl.uk/catalog/040-002248065) attributes the atlas to Pharoah & Co., Madras, engraved by J. & C. Walker, London, and dates the atlas approximately to 1854. This is strong corroboration for the map title, publisher, and scale, but the small “43” visible on this raster versus the catalogue's item number “48” remains unresolved; it may be a different numbering convention or a different issue. The catalogue record's digitised-content field is blank, so it does not itself provide a source image for pixel-level comparison.

The [Wikimedia Commons file record](https://commons.wikimedia.org/wiki/File:Bangalore_1854_Pharaoh.jpg) describes a 1854 Bangalore map by Pharoah & Co. and J. & C. Walker and provides a 2447 × 2977 image. That is a useful higher-resolution comparison lead, but Commons' file description is contributor metadata rather than the archive catalogue. The [Wikimaps Warper record](https://warper.wmflabs.org/maps/2845) identifies that Commons file and lists 11 control points. It establishes that a community georeferencing already exists for the Commons raster; it does not establish its transformation method, control-point accuracy, residual error, or equivalence to this project's raster.

## GS-1854-001

### Visible map evidence

Within the annotated box, the printed word “Tank” is legible. It sits inside or immediately adjacent to a bounded, wedge-like area. Stippled marks, linework, and neighboring map detail are also visible. The box does not contain a legible proper name for the feature.

### Possible reading or hypothesis

The map labels this feature “Tank.” That is a transcription of visible map text. It does not by itself establish the feature's name, function, water extent, modern identity, or later history.

### Unresolved questions

- Does the outline delimit the feature called “Tank,” or is it a boundary for another mapped area with the label placed inside it?
- Is a more specific name or symbol explanation present elsewhere in the atlas or a companion map?
- Which, if any, independently named historical feature corresponds to this box?

### Evidence needed to verify identity

Compare the box with a higher-resolution scan of the same atlas sheet and its full surrounding context. Check any atlas legend or companion sheets for the cartographic convention used for tanks and boundaries. To assign an identity, require a second dated map or archival record that links a distinct nearby toponym or landmark to this exact feature. Pixel position alone is insufficient.

## GS-1854-002

### Visible map evidence

The annotated area contains a two-line italic label beside an irregular outlined area. The lower line appears to read “Tank.” The upper place-name is less clear in this 1280-pixel-wide scan; on the enlarged crop it may read “Lalbagh,” but that transcription remains uncertain. Nearby roads, linework, and patterned areas provide context. The existing annotation's “Lalbagh Tank” wording is therefore a proposed reading, not a verified transcription.

### Possible reading or hypothesis

If the upper line is “Lalbagh,” the two-line label could read “Lalbagh Tank.” Meera Iyer, Harini Nagendra, and M. B. Rajani discuss a historical Lalbagh Tank in a 2012 *Current Science* article about interpreting earlier Bangalore maps and garden boundaries. They report that their analysis of 1791 maps places a garden plot north of, rather than adjacent to, the Lalbagh Tank. This supports the historical use of the name in the area as broader context; it does **not** prove that this particular 1854 map label says “Lalbagh,” or that this pixel box depicts the same feature.

### Unresolved questions

- What letters are present in the upper line on the best available scan, and is the word actually “Lalbagh”?
- Does the irregular outline represent the tank itself, its bund, a parcel, or another mapped boundary?
- Can a second period map or archival description connect this exact labelled feature to the historical Lalbagh Tank discussed in the article?
- Does the apparent “43” on the project's raster belong to a distinct page or edition from British Library atlas item No.48?

### Evidence needed to verify identity

First compare the label against a high-resolution archival or atlas scan whose edition and sheet numbering are documented. Record a human transcription and retain the ambiguous reading if letters remain unclear; do not use OCR as the deciding evidence. Then compare multiple contemporaneous maps using independently identifiable landmarks and toponyms. The 2012 article's historical discussion is contextual evidence only; its 1791-map analysis is not a direct identification of this 1854 feature.

## GS-1854-003

### Visible map evidence

The printed word “Tank” is legible within a large, irregular outlined area. The surrounding scan shows additional boundary-like lines and shaded or hatched marks. No distinct proper name for this feature is legible in the annotated box.

### Possible reading or hypothesis

The map labels the area “Tank.” The visible label does not establish whether the outline is the tank's water edge, a bund or precinct, or a separate area that contains the label. It provides no basis to classify the feature as a confirmed lake, identify it with a modern feature, or say it disappeared.

### Unresolved questions

- What exactly does the large outline enclose, and which strokes belong to the feature versus adjacent land or drainage linework?
- Is there a proper name in the surrounding map context or companion records?
- Does another historical source independently identify a tank at this same mapped location?

### Evidence needed to verify identity

Review the same sheet at archival resolution and consult its map key or related sheets. Seek a second historical source that matches more than the generic word “Tank”—for example, a distinctive name plus the same adjacent roads, settlements, or other fixed landmarks. Only after that identification should later maps be checked for continuity or change.

## Cross-candidate assessment

The scan directly supports one generic “Tank” label at GS-1854-001, an uncertain two-line label with “Tank” as the likely lower word at GS-1854-002, and another generic “Tank” label at GS-1854-003. These are observations about the image. The identification of GS-1854-002 with the historically discussed Lalbagh Tank is a hypothesis requiring a source-to-source match. GS-1854-001 and GS-1854-003 have no specific identities established by the sources reviewed here. None of the evidence reviewed establishes disappearance.

## Georeferencing recommendation: conditional GO for a diagnostic trial

**GO** for a limited trial to determine whether this map raster can be aligned reproducibly. The British Library catalog supplies a published scale, and Wikimaps Warper lists 11 control points for a Commons file described as this same Bangalore map. Those are useful starting materials, not validation of a successful alignment.

Before using any resulting coordinates for candidate claims:

1. Resolve the raster's edition and the apparent printed “43” versus catalogue item “No.48”; confirm the Warper image is the same scan or document the resize/crop relationship.
2. Inspect the Warper control-point coordinates and candidate transformation. Refit or independently reproduce the alignment against the project's source raster rather than inheriting an unexamined result.
3. Hold back independent, well-distributed landmarks as checkpoints. Report residuals and spatial pattern, not only fit points or the published map scale.
4. Keep candidate identity separate from spatial alignment. A successful transform would locate a pixel box; it would not prove what the historical feature was or whether it later disappeared.

This is not approval to publish modern coordinates or disappearance claims. GS-1854-002 still needs a secure transcription and identity crosswalk; GS-1854-001 and GS-1854-003 need distinctive names or landmark-based corroboration. A georeferencing trial can proceed as a technical diagnostic while those historical questions remain open.

## Sources reviewed

1. **British Library Archives and Manuscripts Catalogue, IOR/X/14628/48.** Exact URL: <https://searcharchives.bl.uk/catalog/041-002248113>. Establishes the catalogue title “No.48. Plan Of Bangalore,” scale 650 yards to an inch, and collection context. It does not supply a digitized image in the current record or identify the three candidate boxes.
2. **British Library Archives and Manuscripts Catalogue, parent atlas IOR/X/14628.** Exact URL: <https://searcharchives.bl.uk/catalog/040-002248065>. Establishes the atlas title, Pharoah & Co. and J. & C. Walker attribution, approximate c.1854 date, and its 67 numbered maps. It does not resolve the project's apparent printed “43” against item No.48.
3. **Wikimedia Commons, “File:Bangalore 1854 Pharaoh.jpg.”** Exact URL: <https://commons.wikimedia.org/wiki/File:Bangalore_1854_Pharaoh.jpg>. Provides contributor-supplied date/source/creator metadata and a higher-resolution image identified as this plan. Useful for visual comparison; not a substitute for the British Library's catalog record.
4. **Wikimaps Warper, Map 2845.** Exact URL: <https://warper.wmflabs.org/maps/2845>. Identifies the Commons file and reports 11 control points with KML/CSV export links. It does not report accuracy or prove alignment of the workspace raster.
5. **Meera Iyer, Harini Nagendra, and M. B. Rajani, “Using satellite imagery and historical maps to study the original contours of Lalbagh Botanical Garden,” *Current Science* 102(3), 507–509 (10 February 2012).** Exact URL: <https://www.researchgate.net/publication/230559312_Using_satellite_imagery_and_historical_maps_to_study_the_original_contours_of_Lalbagh_Botanical_Garden>. The article discusses historical maps, Lalbagh Tank, and garden boundaries; it reports analysis of 1791 maps and does not transcribe or identify this candidate's 1854 label. The linked page is ResearchGate-hosted author content, not the journal's own archive.

**Unverified:** the specific identities of all three candidate areas; the full transcription of GS-1854-002; whether any candidate persisted, changed, or disappeared; and the alignment accuracy of the Warper registration when applied to this project's raster.
