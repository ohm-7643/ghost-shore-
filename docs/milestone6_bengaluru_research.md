# Milestone 6 — Bengaluru historical water-feature research

**Purpose:** assemble sourced research leads for later human review against historical maps. This report does not add features to the catalog, identify any of the three existing candidate boxes, create pixel boxes, or assign modern coordinates.

**Research checked:** 10 October 2026. Sources below were accessed as pages or PDFs where stated. This is a targeted desk review, not an exhaustive archival survey. “Confidence” rates the usefulness of the lead and quality of the source support, not the certainty of a map-to-place identity.

## Existing project state inspected

- The [README](../README.md) describes the local explorer and its cautious, image-pixel-only catalog.
- Existing research is in [candidate_research.md](candidate_research.md). It leaves the identities of GS-1854-001, GS-1854-002, and GS-1854-003 unresolved.
- The catalog is governed by [catalog.schema.json](../data/catalog/catalog.schema.json); its three records are in [features.json](../data/catalog/features.json). The records remain `GS-1854-001`, `GS-1854-002`, and `GS-1854-003`, each `pending_human_review`, with their original image-pixel boxes and annotation text. No new catalog records were created.
- On visual inspection of the local `data/raw/bangalore_1854.jpg`, the printed labels **“Sampangi Tank”** and **“Ulsoor Tank”** are readable; **“Domloor Tank”** also appears legible. This is direct evidence about text visible on this raster only. It does not establish that any later source's named place is the same feature, nor does this report transcribe or box new regions.

## Evidence vocabulary and limits

- **Verified historical fact (source-scoped):** a statement explicitly made by a cited archival record, government page, or historical study. It means the source says it; it does not mean every underlying primary record was independently inspected here.
- **Direct map observation:** text/marks visible on the named raster. A printed label is not proof of identity, exact extent, function, or continuous survival.
- **Plausible interpretation:** a proposed relationship between sources or names requiring map-by-map verification.
- **Unsupported here:** a claim for which this review found no sufficient evidence. Lack of evidence in this review is not proof the claim is false.

The 2018 Azim Premji University working paper is especially useful for a city-history overview and cites National Archives and Karnataka State Archives material, but this review did not retrieve each archival file independently. The paper also places several Cantonment tanks in a broad 1860s–1890s construction period, whereas other sources give more specific dates. Where dates disagree, that disagreement is retained.

## Ranked research leads

Rank reflects a combination of source quality, usefulness for future map comparison, and relevance to an exploration experience. A lead can rank highly while its relationship to the 1854 map remains unproved.

### 1. Sampangi Tank / Sampangi Lake

- **Type and period:** tank/lake; discussed as an older city water body and in nineteenth- to twentieth-century records.
- **Source-established facts:** Unnikrishnan and Nagendra's 2014 NMML paper says it compares maps from 1884 onward and archival records from 1883–1935; it documents changing water availability, siltation, seasonality, and user conflicts. Its cited map narrative reports conversion toward carnival/stadium uses; a later related article describes the Kanteerava Stadium transition and a small remnant tank. The 2014 abstract itself calls it a “lost lake,” but this report does not adopt that shorthand as proof that no water feature survives.
- **1854-map evidence:** **Direct observation:** “Sampangi Tank” is readable on the local c.1854 scan. Whether the visible label corresponds to the later mapped and studied lake is a strong but still testable hypothesis.
- **Later status:** substantial alteration is documented in the studies; precise surviving-water status should be checked against current authoritative records and imagery. Do not describe it as wholly vanished.
- **Confidence / next check:** **High** as a research lead; **not verified** as a correspondence to any candidate box. Compare the 1854 label and adjacent named features against the 1884/1885 and 1935 maps reproduced/discussed in the study, then inspect later maps and records.

### 2. Dharmambudhi / Dharmambuddhi / Dharmamabudhi Lake or Tank

- **Type and period:** tank/lake; described in sources as an important water body by the sixteenth-century foundation period and through the colonial era. Spelling varies in publications.
- **Source-established facts:** The APU 2018 working paper pp. 13–14 describes Dharmambudhi as a water source for the Pete, reports archival concerns about falling levels from 1888, says it had gone dry in 1888, and says water was later channelled into it. Nagendra and Unnikrishnan's 2019 Arcadia article describes an 1885 map, drainage in the early 1900s, and filling of the maidan for the central bus terminus in the early 1960s.
- **1854-map evidence:** This visual pass did not identify a secure “Dharmambudhi” label on the local raster. An 1885 image is shown in the Arcadia article, but it does not prove a match to a particular mark on the 1854 scan.
- **Later status:** documented transformation to bus-terminal land use; the sources also note wells and flooding in the former bed. “Disappeared lake” must not be inferred as “no water remains anywhere in the area.”
- **Confidence / next check:** **High** as a historically documented transformation lead; no 1854 pixel identity. Compare the 1885 figure and other dated maps with a verified high-resolution 1854 sheet and stable landmarks.

### 3. Ulsoor / Halasur / Halasuru Lake or Tank

- **Type and period:** tank/lake. Name variants are used in the 2018 APU paper and government tourism material.
- **Source-established facts:** the 2018 paper p. 13 groups Halasur (also called Ulsoor) with tanks built for the Cantonment between the 1860s and 1890s. The Government of Karnataka Bengaluru Urban tourism page lists Ulsoor Lake as a current attraction. A 2002 IISc introductory talk instead dates an “ulsoor tank” to around 1867. These sources do not establish a single uncontested origin date.
- **1854-map evidence:** **Direct observation:** “Ulsoor Tank” is readable on the local c.1854 raster. This conflicts with a simple reading of the later-source construction dates; possible explanations include a pre-existing feature, differing referents, or source error, none resolved here.
- **Later status:** the government page identifies a present-day Ulsoor Lake; that naming alone does not prove uninterrupted identity with the 1854 mapped tank. A 2011 WIT paper mentions recreational use on dry parts of Ulsoor tank bed, which signals alteration, not disappearance.
- **Confidence / next check:** **High** as a map-review lead, **medium** on historical continuity because chronology is inconsistent. Compare the 1854 sheet with dated Survey of India/municipal maps and primary construction records.

### 4. Domloor / Domlur Tank

- **Type and period:** tank; the 1854 map spelling appears as “Domloor,” while later literature uses “Domlur.”
- **Source-established facts:** a 2011 WIT Transactions paper's p. 386 discussion says recreational spaces were laid on dry parts of Ulsoor and Domlur tank beds; its table on p. 387 lists Domlur tank and later land uses. The source is a secondary synthesis, not a cadastral identity record.
- **1854-map evidence:** **Direct observation:** “Domloor Tank” appears readable on the local raster. Similar spelling is suggestive, not conclusive evidence of continuity.
- **Later status:** the WIT paper supports alteration of at least part of the tank bed; this review did not independently verify the named current land use or remaining water area.
- **Confidence / next check:** **Medium.** Compare the label and neighboring named features against period maps and the specific historical maps/data underlying the WIT paper before linking “Domloor” and “Domlur.”

### 5. Karanji / Karanjikere Tank

- **Type and period:** tank/kere; included in historical accounts of the older Pete water system. The exact spelling and referent should be checked against original records.
- **Source-established facts:** APU 2018 p. 13 says Karanji supplied the Pete with Dharmambudhi; pp. 13–14 report falling water levels and later capacity works in archival records. The 2011 WIT paper's p. 387 table associates “Karanji Tank” with later school/residential uses.
- **1854-map evidence:** not identified by name in this visual scan review; no claim that it appears on the 1854 map.
- **Later status:** the WIT table indicates substantial land-use change. The cited wording does not establish that the whole tank disappeared or settle present-day water status.
- **Confidence / next check:** **Medium-high** as a historical lead, lower for precise site continuity. Locate original archival references and compare maps bearing the name and surrounding landmarks.

### 6. Siddikatte / Siddikatte Tank

- **Type and period:** tank; described in accounts of the older city market area.
- **Source-established facts:** the IISc 2002 talk identifies Siddikatte tank with the present city market area. The News Minute's 2017 article reports that the area was formerly a lake and quotes historian Harini Nagendra describing a 7 January 1914 City Improvement Committee decision concerning low-lying Siddikatte streets and the market opened in 1921. The article is secondary reporting; the minutes themselves were not inspected here. The WIT 2011 table lists Siddikatte Tank and KR Market as later use.
- **1854-map evidence:** not securely identified by name on the local 1854 raster in this review.
- **Later status:** the market history indicates alteration/filling, but this review did not verify the tank footprint against primary maps or cadastral records.
- **Confidence / next check:** **Medium.** Retrieve the 1914 proceedings and compare period market plans and historical map labels; do not use the current market location as a substitute for map evidence.

### 7. Kempambudhi / Kempambuddhi Tank

- **Type and period:** tank; the IISc talk attributes construction to Kempegowda in the sixteenth century. The spelling varies across sources.
- **Source-established facts:** the 2002 IISc talk makes this attribution. The WIT 2011 paper reports that the 1965 Master Plan proposed conserving Kempambuddhi Tank. A 2025 ISEC working-paper page describes a study of an eco-restoration project at Kempambudhi Lake, indicating a modern restoration context, not proving historical continuity by itself.
- **1854-map evidence:** no secure name match identified in this pass.
- **Later status:** evidence supports later conservation planning/restoration discussion; current extent and hydrological condition were not assessed here. Not a vanished-water-body claim.
- **Confidence / next check:** **Medium.** Check the original 1965 plan, historic survey sheets, and the ISEC study's primary evidence; map name variants before any crosswalk.

### 8. Shoolay / Shule Tank

- **Type and period:** tank. “Shoolay” appears in the APU and IISc sources; the WIT table uses “Shule.”
- **Source-established facts:** the APU 2018 paper places Shoolay among Cantonment tanks constructed between the 1860s and 1890s. The 2002 IISc talk says “around 1867.” The WIT 2011 table lists Shule Tank with commercial and football/hockey stadium uses. These are secondary sources and their precision differs.
- **1854-map evidence:** no name match identified in this visual review. If the 1860s construction date is correct, the feature would post-date the c.1854 scan; the chronology still needs primary-source checking.
- **Later status:** the WIT table reports changed land use. The exact relationship to a current stadium or any residual water was not independently verified.
- **Confidence / next check:** **Medium.** Compare dated 1860s–1900s Cantonment maps and archival works records; keep both spellings in searches.

### 9. Miller's Tank series / Miller's Tanks I–III

- **Type and period:** series of tanks; APU 2018 places their construction between the 1860s and 1890s. Later sources sometimes use singular “Miller Tank.”
- **Source-established facts:** the APU working paper p. 13 lists a Miller's Tank series among Cantonment water infrastructure; pp. 13–14 discuss works to improve capacity. The WIT 2011 table p. 387 lists Miller's Tank with later public/institutional land uses.
- **1854-map evidence:** no evidence on the 1854 map established here; the cited construction period begins later than the map date.
- **Later status:** published sources describe substantial land-use change and interlinked tank functions; this review did not establish whether any water remnant survives or which individual tank corresponds to which present parcel.
- **Confidence / next check:** **Medium-high** for a historical system lead; lower for each tank's separate identity. Find a dated Cantonment map showing all three and reconcile spellings and numbering.

### 10. Hesaraghatta / Hessarghatta Lake or Reservoir

- **Type and period:** man-made reservoir/lake on the Arkavathi system; late nineteenth century.
- **Source-established facts:** the Government of Karnataka Bengaluru Urban tourism page says the lake was made in 1894 to store Arkavathi water and supply Bengaluru, and notes water levels often low to nil after monsoon. The APU paper pp. 13–14 says the scheme was initiated in 1892, filtered water was delivered in 1896, and archival records say the lake went completely dry in 1925. These descriptions may refer to different project milestones; the discrepancy should remain explicit.
- **1854-map evidence:** it post-dates the c.1854 map according to these sources; do not treat it as an 1854-map feature.
- **Later status:** low/seasonal water and a documented 1925 dry episode do not establish permanent disappearance. The government tourism page still presents it as a lake.
- **Confidence / next check:** **High** for the water-supply infrastructure lead; **not eligible** as an 1854 feature unless new evidence revises the chronology. Consult engineering records and dated maps to reconcile 1892/1894/1896 milestones.

## Three best leads for manual historical-map review

These are research priorities only; no IDs, catalog entries, or pixel boxes are assigned.

1. **Sampangi:** directly named on the local 1854 raster and supported by a focused map-and-archive study spanning 1884 onward. It offers the clearest bridge between the current source map and documented later change.
2. **Ulsoor/Halasur:** directly named on the local raster and named on the current government tourism page, but secondary histories give a conflicting construction chronology. The disagreement makes it valuable for source criticism and map comparison.
3. **Dharmambudhi:** unusually strong written and later-map evidence for transformation, including an 1885 map figure, but no secure name match was identified on the local 1854 scan. It is a good controlled exercise in not projecting written history onto an unlabelled pixel region.

Domloor/Domlur is a close alternate because its label is visible on the 1854 raster and a published synthesis discusses the tank bed. Manual review should first resolve the historical spelling and source-map sequence.

## Source register

1. **“Lakes of Bengaluru: The Once Living, But Now Endangered Peri-Urban Commons,”** Seema Mundoli, B. Manjunatha, and Harini Nagendra, Azim Premji University Working Paper Series No. 10 (2018), especially pp. 13–14 (PDF pages 13–14). [PDF](https://publications.azimpremjiuniversity.edu.in/5169/1/WP%2010_APU-181213-Working-Paper-Series-10-28.03.2018.pdf). Its historical overview names Sampangi, Karanji, Dharmambudhi, Miller's tanks, Shoolay, Sankey, Halasur/Ulsoor and documents water-supply episodes from cited archives. The archive references are reported by the authors; the underlying files were not individually checked here.
2. **“The Lake That Became a Bus Terminus,”** Hita Unnikrishnan and Harini Nagendra, *Environment & Society Portal, Arcadia*, Spring 2019, no. 2. [Article](https://www.environmentandsociety.org/arcadia/lake-became-bus-terminus). It describes Dharmambudhi and includes an 1885 map figure; it reports early-twentieth-century drainage and filling for the bus terminus in the early 1960s. It is a scholarly public-history article, not a substitute for primary files.
3. **“Unruly Commons: Contestations around Sampangi Lake in Bangalore,”** Hita Unnikrishnan and Harini Nagendra, Nehru Memorial Museum and Library Occasional Paper / Azim Premji University repository (2014), particularly its abstract's scope statement (maps 1884 onward; archival data 1883–1935). [Repository record](https://publications.azimpremjiuniversity.edu.in/196/) and [PDF](https://publications.azimpremjifoundation.org/196/1/Unruly%20commons_contestations%20around%20Sampangi%20lake%20in%20Bangalore.pdf). Supports the existence of a sustained map/record study; later stadium/remnant details should be checked against the paper's figures and original records.
4. **“Evolution of Bangalore City's Water Tank System,”** F. S. Saidoddin, A. Suseelan, and A. Krishna, *WIT Transactions on Ecology and the Environment* 148 (2011), pp. 381–390, DOI [10.2495/RAV110351](https://doi.org/10.2495/RAV110351). [Publisher record](https://www.witpress.com/elibrary/wit-transactions-on-ecology-and-the-environment/148/22986); [accessible manuscript copy](https://www.researchgate.net/publication/271422939_Evolution_of_Bangalore_city%27s_water_tank_system). Relevant details include dry tank beds (printed pp. 385–386) and a later land-use table (printed p. 387). The ResearchGate copy is not the publisher; this is a secondary synthesis and should be corroborated for individual site boundaries.
5. **“Lakes of Bangalore – A Peep into History,”** S. V. Subramanyam, introductory talk page, Indian Institute of Science Centre for Ecological Sciences, 2002. [IISc page](https://wgbis.ces.iisc.ac.in/energy/lake2002/proceedings/introtalk.html). It names Kempambudhi, Dharmambudhi, Sampangi, Siddikatte, Karanjikere, Miller, Shoolay, Ulsoor, Sankey, and Hesarghatta. This is an institutional talk page, not a peer-reviewed article or primary record; use as a lead index, not sole proof.
6. **“Tourism,” Bengaluru Urban District, Government of Karnataka**, current web page, accessed 10 October 2026. [Government page](https://bengaluruurban.nic.in/en/tourism/). It describes Hesaraghatta's 1894 purpose, seasonal low-to-nil post-monsoon water levels, and currently lists Ulsoor Lake and Sankey Tank among Bengaluru water attractions. It establishes what this government page currently states, not historical continuity or exact boundaries.
7. **“From a thriving bazaar to a garbage-strewn dump: Tracing the history of Bengaluru's KR Market,”** The News Minute, 29 July 2017. [Article](https://www.thenewsminute.com/karnataka/thriving-bazaar-garbage-strewn-dump-tracing-history-bengalurus-kr-market-65970). It reports the Siddikatte history and quotes Harini Nagendra on the 1914 City Improvement Committee decision. The article is secondary journalism; obtain the quoted proceedings before treating that detail as independently verified.
8. **“Imperilled Waterscapes: The Social-Ecological Transformation of Lakes in Bengaluru,”** Amrita Sen, Hita Unnikrishnan, and Harini Nagendra, *Ecology, Economy and Society – the INSEE Journal* 3(2) (2020), pp. 125–134, DOI [10.37773/ees.v3i2.229](https://doi.org/10.37773/ees.v3i2.229). [Azim Premji University repository record](https://publications.azimpremjiuniversity.edu.in/2359/). Its abstract uses Bellandur Lake as a case for transformation from semi-arid/open to agrarian and later concretized waterscape. This supports Bellandur as a broad future research lead, but does not provide a verified bridge to the 1854 map; it was not ranked among the ten detailed leads because map-period identity evidence was not established.
9. **“Rejuvenating the Commons or Reinforcing Exclusion? Power Dynamics and Marginalisation in the Eco-restoration of Bengaluru's Lake,”** Akash Jash, Institute for Social and Economic Change working paper (2025). [ISEC record](https://www.isec.ac.in/rejuvenating-the-commons-or-reinforcing-exclusion-power-dynamics-and-marginalisation-in-the-eco-restoration-of-bengalurus-lake/). The record identifies a contemporary Kempambudhi restoration study; it is a lead to current research, not proof of historic identity or continuous water extent.

## Evidence gaps and recommendation

- None of the written sources reviewed here proves which, if any, unlabelled candidate box in the project catalog corresponds to one of these named features.
- No new map annotations, image-pixel boxes, latitude/longitude, routes, or modern placements have been made.
- Several source claims are secondary reports of archival material. The relevant original archive files, maps, map legends, and exact editions should be retrieved before promoting any lead to a catalog annotation.
- **Recommendation:** proceed with manual source-map review of the three ranked leads, not catalog migration. Add a feature only after a reviewer records direct evidence on a cited historical map, retains ambiguous readings, and links that map observation to independent, dated evidence. No disappearance claim is warranted by this report alone.
