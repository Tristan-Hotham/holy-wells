# From Saint to Wish

The holy and wishing wells of Britain and Ireland: where they are, who they are dedicated to, the language of their names, and the cures, rags, offerings and patterns recorded at Irish holy wells.

**Interactive version:** https://tristan-hotham.github.io/holy-wells/
**Blog post:** https://blog.tristanhotham.com/2026/10/27/holy-wells/
**Paper and archived data:** https://doi.org/10.5281/zenodo.23688019

By Dr Tristan Hotham (Independent researcher, ORCID 0000-0003-4931-9349). Companion project: [my earlier map of saints and holy wells across Western Europe](https://tristan-hotham.github.io/saints-and-wells/) (church dedications from Wikidata).

## Headline results

- 3,440 holy wells mapped: the 3,025 in the Republic of Ireland's official inventory (National Monuments Service) and 415 in Northern Ireland, Britain and the Isle of Man from OpenStreetMap and Wikidata, plus 1,107 other named wells.
- The Republic has 43.6 recorded holy wells per 1,000 km². Northern Ireland's open data show 2.7, 15.9 times fewer: the gap is the source, not the tradition. Britain's 373 mapped holy wells (1.6 per 1,000 km²) are a floor, not a count.
- Densest Irish counties: Dublin (120.7 per 1,000 km²), Kilkenny, Wexford and Clare. In Britain's open data, Cornwall leads (57 holy wells, 16.0 per 1,000 km²).
- Of 2,142 named Irish inventory wells, 1,007 (47%) name a saint: Mary 162, Patrick 161, Brigid 113. 42% of names are not read.
- 45% of named Irish holy wells have Irish-language names (mostly anglicised Tober forms); 63% of named wells in Wales are a Ffynnon; 14% in Scotland are Gaelic.
- In the first 254 characters of 2,628 Irish descriptions: 12.2% mention a pattern, pilgrimage, rounds or stations; 5.3% a cure (eyes most often, 52); 2.8% offerings (14 with coins); 1.2% rags; 19% at least one of cure, rags, offerings or pattern. These are lower bounds.
- 15% of Irish holy wells are within 500 m of a Wikidata church (2.6% of random points); where a well and a church within 2 km both name a saint, they share it 36% of the time (8% if shuffled).
- Of 81 OpenStreetMap features called "Wishing Well", 38 are wells or springs; the rest are pubs, cafes, nurseries, cottages and other things.

## Files

- `index.html`: the interactive page (Leaflet map, charts); `header.png`: social card.
- `data/wells.csv`: one row per well: source (NMS, OSM, Wikidata), id, name, lon, lat, nation, county or area, townland (Ireland), holy (true/false), saint read from the name, how it was read, language of the generic word, folk name type, OpenStreetMap tags, source URL.
- `data/practices.csv`: one row per described Irish holy well, with 0/1 flags for each practice found in the description.
- `data/practice_examples.csv`: short quoted examples for each practice, with record links.
- `data/nations.csv`, `data/counties.csv`: counts, areas and densities.
- `data/saints.csv`, `data/languages.csv`: saint and language counts by country.
- `data/osm_filter_steps.csv`: the OpenStreetMap filter, step by step, with the number kept and dropped.
- `data/geo/units.geojson`: counties and areas used for counting (simplified), with land area in km²; `data/geo/ne_admin1_ie_ni_im.geojson`: the Natural Earth admin-1 polygons for Ireland, Northern Ireland and the Isle of Man it is built from.
- `data/results.json`: every number quoted on the page, in the paper, the blog post and the collage.
- `code/`: Python scripts, run in order: `01_geo.py`, `02_build.py`, `03_analyse.py`, `04_build_site.py`, `05_header.py`. `wellnames.py` holds the name reader (saints, languages, folk names). `release/` holds the paper, blog figures and Zenodo files; `reddit/` the collage.

## Method in brief

Republic of Ireland: every National Monuments Service record classed "Ritual site, holy well", with names from the Ordnance Survey maps as recorded. Elsewhere: OpenStreetMap features with a well-like name, filtered in the steps of `data/osm_filter_steps.csv` (well word as a word, not a road, building or business, tags of a spring, well or religious feature, duplicates removed), plus Wikidata holy wells; features within 150 m of a well already held were treated as the same well. A well is holy outside the Republic if its name gives a saint or says holy, or its tags or Wikidata say so. Saints are read only from plain forms (St X's Well, Tobar Phádraig, Ffynnon Fair) and a fixed table of name forms; anglicised Irish forms such as Tobermurry are read only where the inventory's descriptions give the saint. Practices are found by word lists in the descriptions, ignoring negated mentions.

Caveats: the Irish inventory is an official survey and the rest is volunteer mapping, so densities across that line compare sources as much as wells; Scotland's Canmore and Wales's Coflein records were not used. The open Irish data carry only the first 254 characters of each description (86% reach that limit), so practice shares are lower bounds. Recorded is not surviving. Wikidata's churches are uneven by country. OS Open Names was checked and holds almost no named wells, so it is not used.

## Sources and licences

- Irish holy wells: National Monuments Service, Department of Housing, Local Government and Heritage, Sites and Monuments Record (Archaeological Survey of Ireland), via the "National_Monuments_Service_Holy_Wells" ArcGIS feature service. CC BY 4.0 (Government of Ireland open data).
- Wells in Britain, Northern Ireland and the Isle of Man: © OpenStreetMap contributors, ODbL 1.0, retrieved via the QLever OSM planet endpoint.
- Holy wells and churches: Wikidata, CC0.
- Boundaries: Office for National Statistics local authority boundaries (counties built for my "How Roman is your road?" project), contains OS data © Crown copyright and database right, Open Government Licence v3; Natural Earth 10m admin-1 (public domain) for Ireland, Northern Ireland and the Isle of Man.
- Base map tiles on the page: Esri. Map library: Leaflet.

`data/wells.csv` contains OpenStreetMap data and is released under the ODbL 1.0. Other derived data, text and figures: CC BY 4.0. Code: MIT (see `LICENSE`).

## Rerun

Python 3 with numpy, scipy, shapely and pyproj (matplotlib for the figures). Set `NMS`, `OSM`, `WD` to the three source extracts and `WD_DIR` to the folder with the Wikidata church extracts (`ch_GB.json`, `ch_IE.json`), then run the scripts in order.

## Citation

Hotham, T. (2026) *From Saint to Wish: mapping the holy and wishing wells of Britain and Ireland*. Zenodo. https://doi.org/10.5281/zenodo.23688019

I wrote the text, with drafting and editing assistance from Claude (Anthropic), which also helped prepare the analysis code. I reviewed and checked all text and results.
