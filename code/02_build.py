"""Step 2: one table of named and holy wells for Britain, Ireland and the Isle of Man.

Sources (read in place, not copied):
  NMS  Irish National Monuments Service, Sites and Monuments Record, class
       'Ritual site - holy well' (Republic of Ireland), CC BY 4.0.
  OSM  OpenStreetMap features whose name matched a loose well regex, ODbL.
  WD   Wikidata items that are instances of 'holy well', CC0.
Writes data/wells.csv, data/osm_filter_steps.csv and work/build.json.
Run: python3 02_build.py
"""
import json, os, re, csv, math, collections
import numpy as np
from scipy.spatial import cKDTree
from shapely.geometry import shape, Point
from shapely import STRtree
from wellnames import saint, folk, language, norm

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(HERE, "..")
NMS = os.environ.get("NMS", "/home/claude/hist/_data6/ireland_nms_holy_wells.json")
OSM = os.environ.get("OSM", "/home/claude/hist/_data6/osm_named_wells_gb_ie_im.json")
WD = os.environ.get("WD", "/home/claude/hist/_data2/wikidata/holywells.json")
DEDUP_M = 150

# ---------- boundary units ----------
U = json.load(open(os.path.join(ROOT, "data", "geo", "units.geojson")))["features"]
geoms = [shape(f["geometry"]) for f in U]; tree = STRtree(geoms)


def locate(lon, lat):
    p = Point(lon, lat)
    hits = tree.query(p, predicate="intersects")
    if len(hits): i = int(hits[0])
    else:
        i = int(tree.nearest(p))
        if geoms[i].distance(p) > 0.03: return None, None  # about 2 to 3 km offshore: drop
    return U[i]["properties"]["unit"], U[i]["properties"]["nation"]


def xy(lon, lat):  # metres, local equirectangular (good enough for 150 m matching)
    lon, lat = np.asarray(lon, float), np.asarray(lat, float)
    return np.c_[lon * 111320 * np.cos(np.radians(54.5)), lat * 110540]


# ---------- NMS ----------
PLACEHOLDER = "The Archaeological Survey of Ireland (ASI) is in the process"


def clean_nms_name(x):
    s = (x.get("LATEST_EDI") or "").strip() or (x.get("FIRST_EDIT") or "").strip()
    if s.lower().startswith(("not indicated", "indicated", "outlined", "not named")) or not s: return ""
    s = re.sub(r"\(\s*\d{4}\s*\)", "", s)
    s = re.sub(r"\((?i:site of)\)", "", s)
    s = s.replace("’", "'").strip().strip("'\"").strip()
    s = re.sub(r"\s+", " ", s).strip(" '\"")
    return s


rows = []
nms = json.load(open(NMS))
for x in nms:
    notes = (x.get("WEB_NOTES") or "").strip()
    nm = clean_nms_name(x)
    unit, nation = locate(x["LONGITUDE"], x["LATITUDE"])
    rows.append({"src": "NMS", "id": x["SMRS"].strip("-").strip(), "name": nm, "lon": round(x["LONGITUDE"], 5), "lat": round(x["LATITUDE"], 5),
                 "unit": x["COUNTY"].title().replace("Tipperary North", "Tipperary North"), "nation": "Ireland", "nms_county": x["COUNTY"],
                 "townland": (x.get("TOWNLAND") or "").title(), "notes": "" if notes.startswith(PLACEHOLDER) else notes,
                 "placeholder": notes.startswith(PLACEHOLDER), "url": (x.get("WEBSITE_LI") or "").strip(), "located_unit": unit,
                 "holy": True, "tags": ""})

# ---------- OSM filter ----------
osm = json.load(open(OSM))
steps = [("All OSM features with a loose well-like name (input extract)", len(osm))]
WELLWORD = re.compile(r"(?i)\bwells?\b|ladywell\b|holywell\b|halliwell\b|^ffynnon\b|\bffynnon\b|^(tobar|tobair|tober|tobber|tubber|tubbrid|tiobraid|tipra|fuaran|chibbyr|chibber)|\bclootie\b|\bventon\b")
s1 = [x for x in osm if WELLWORD.search(x["name"])]
steps.append(("Name has a well word (well, wells, ffynnon, tobar, tober, tubber, fuaran, chibbyr, venton, clootie) as a word, which drops Wellington, Bridewell, Powell, Maxwell, Cromwell, Boswell, spa and spring names", len(s1)))
NOTFEATURE = re.compile(r"(?i)\b(street|st\.?$|road|rd|lane|avenue|ave|close|drive|way|terrace|crescent|gardens?|court|house|farm|farmhouse|hall|park|place|grove|walk|row|view|rise|mews|square|cottages?|cott|school|surgery|centre|center|primary|academy|college|church|chapel|inn|hotel|pub|bar|tavern|arms|cafe|café|restaurant|shop|stores?|garage|estate|bridge|station|halt|stop|reservoir|works|nursery|medical|pharmacy|chemist|practice|clinic|care|home|lodge|manor|mill|barn|ltd|limited|plc|club|f\.?c\.?|golf|rugby|cricket|football|bowls|tennis|harbour|branch|transformer|substation|pumping|sewage|drain|path|track|trail|footpath|bridleway|car park|parking|playground|allotments?|meadow|wood|plantation|copse|quarry|colliery|pit|mine|level|shaft|oil|gas|borehole|nant|afon|cwm|cae|plas|bryn|bron|maes|erw|llain|llwyn|tyddyn|bwthyn|cwrt|parc|heol|stryd|ffordd|lôn|lon|upper|lower|east|west|north|south|road|village|town|city|tunbridge|builth|llandrindod|llanwrtyd|llangammarch|royal|harrogate|bath|spa|surgery|dental|dentist|vets?|veterinary|hairdressers?|salon|beauty|spa|gym|fitness|church hall|community|baptist|methodist|chapel|cemetery|crematorium|graveyard|memorial hall|post office|library|museum|gallery|theatre|cinema|bank|hostel|camp|campsite|caravan|holiday|b&b|guest|apartments|flats|court|tower|towers|castle|hill|hills|moor|common|green|end|bank|field|fields|bottom|dale|valley|glen|cleugh|burn|beck|brook|stream|river|loch|lough|pond|pool|lake|bay|point|head|cliff|rock|island|well road|well lane)\b")
HARD = re.compile(r"(?i)\b(street|road|lane|avenue|close|drive|terrace|crescent|gardens?|court|house|farm|farmhouse|hall|park|place|mews|square|cottages?|school|surgery|centre|center|primary|academy|college|church|inn|hotel|pub|bar|tavern|cafe|café|restaurant|shop|stores?|garage|estate|station|nursery|medical|pharmacy|chemist|practice|clinic|care|home|lodge|manor|mill|barn|ltd|limited|plc|club|golf|rugby|cricket|football|transformer|substation|pumping|sewage|path|track|trail|footpath|car park|parking|playground|allotments?|cemetery|crematorium|graveyard|library|museum|theatre|cinema|hostel|caravan|holiday|apartments|flats|tunbridge|builth|llandrindod|llanwrtyd|llangammarch|power|pit|mine|shaft|oil|borehole|plas|tyddyn|bwthyn|cwrt|heol|stryd|ffordd)\b")
ENDW = re.compile(r"(?i)(\bwells?|ladywell|holywell)\s*(\(.*\))?$|^ffynnon [a-z\u00c0-\u017f]+$|^(tobar|tober|tubber|fuaran|chibbyr)\S*( \S+)?$")
s2 = [x for x in s1 if not HARD.search(x["name"]) and (ENDW.search(x["name"].strip()) or not NOTFEATURE.search(x["name"]))]
steps.append(("Not a road, building, business, organisation or settlement by name; topographic words (hill, green, head ...) drop a name only when it does not end in the well word (word lists in code)", len(s2)))
OK_NAT = {"", "spring", "water", "wetland"}
OK_MM = {"", "water_well", "spring_box", "well"}
OK_AMEN = {"", "place_of_worship", "drinking_water", "fountain", "watering_place", "water_point"}
s3 = [x for x in s2 if x["nat"] in OK_NAT and x["mm"] in OK_MM and x["amen"] in OK_AMEN]
steps.append(("Tags not those of a different kind of feature (natural only spring, water or wetland; man_made only water_well; amenity only place_of_worship, drinking_water, fountain or watering_place)", len(s3)))
WATER = lambda x: x["nat"] in ("spring", "water", "wetland") or x["mm"] in ("water_well", "spring_box", "well") or x["hist"] in ("well", "holy_well", "water_well", "spring") or x["amen"] in ("drinking_water", "fountain", "watering_place", "water_point")
RELIG = lambda x: bool(x["rel"]) and x["rel"] != "none" or x["amen"] == "place_of_worship" or x["hist"] in ("wayside_shrine", "holy_well")
HERIT = lambda x: x["hist"] in ("archaeological_site", "ruins", "memorial", "monument", "yes", "heritage") or bool(x["heritage"])
ENDSWELL = re.compile(r"(?i)(\bwells?|ladywell|holywell)\s*(\(.*\))?$|^ffynnon\b|^(tobar|tober|tubber|fuaran|chibbyr)")


def named_marker(x):
    k, how = saint(x["name"])
    return k is not None or bool(folk(x["name"]))


def keep4(x):
    if WATER(x) or RELIG(x): return "tagged water or religious feature"
    if HERIT(x) and ENDSWELL.search(x["name"]): return "historic or heritage feature named as a well"
    if not (x["nat"] or x["mm"] or x["hist"] or x["amen"]) and ENDSWELL.search(x["name"]) and named_marker(x) and not re.match(r"(?i)^(tobar|tober|tubber)", x["name"]) and " " in x["name"].strip() and not re.search(r"(?i)\bbus\b|=>|->", x["name"]):
        return "untagged here but named as a saint's, holy or folk well"
    return None


s4 = []
why = collections.Counter()
for x in s3:
    r = keep4(x)
    if r: why[r] += 1; s4.append(dict(x, why=r))
steps.append(("Evidence it is a well: tagged as a spring or well, or as religious, or historic and named as a well, or (if untagged in the extract) named as a saint's, holy or folk well in two or more words; untagged one-word names (Holywell, Ladywell) and untagged Tober and Tobar names are dropped because most are places or townlands", len(s4)))
# within-OSM duplicates (same normalised name within 150 m; node plus way)
P = xy([x["lon"] for x in s4], [x["lat"] for x in s4]); t = cKDTree(P)
drop = set()
for i, j in sorted(t.query_pairs(DEDUP_M)):
    if i in drop or j in drop: continue
    if norm(s4[i]["name"]) == norm(s4[j]["name"]):
        drop.add(j if s4[i]["osm"].startswith("node") or not s4[j]["osm"].startswith("node") else i)
s5 = [x for k, x in enumerate(s4) if k not in drop]
steps.append(("After removing OSM duplicates (same name within 150 m)", len(s5)))
s6 = []
for x in s5:
    unit, nation = locate(x["lon"], x["lat"])
    if unit is None: continue
    s6.append(dict(x, unit=unit, nation=nation))
steps.append(("Inside the study area (land of Britain, Ireland and the Isle of Man, within about 3 km of the coast)", len(s6)))

# match OSM against NMS (Republic of Ireland)
NP = xy([r["lon"] for r in rows], [r["lat"] for r in rows]); nt = cKDTree(NP)
osm_ie = [x for x in s6 if x["nation"] == "Ireland"]
matched_nms = set(); osm_ie_matched = 0
for x in osm_ie:
    d, i = nt.query(xy([x["lon"]], [x["lat"]])[0])
    if d <= DEDUP_M: matched_nms.add(int(i)); osm_ie_matched += 1; x["nms_match"] = rows[int(i)]["id"]
s7 = [x for x in s6 if not x.get("nms_match")]
steps.append((f"After removing OSM features within {DEDUP_M} m of an NMS holy well", len(s7)))

def is_holy(x):
    return saint(x["name"])[0] is not None or RELIG(x) or x["hist"] == "holy_well" or bool(re.search(r"(?i)holy|saint|pilgrim|sacred|blessed|patron", x["desc"] or ""))


for x in s7:
    holy = is_holy(x)
    tags = ";".join(f"{a}={x[b]}" for a, b in (("natural", "nat"), ("man_made", "mm"), ("historic", "hist"), ("amenity", "amen"), ("religion", "rel"), ("heritage", "heritage")) if x[b])
    rows.append({"src": "OSM", "id": x["osm"], "name": x["name"], "lon": round(x["lon"], 5), "lat": round(x["lat"], 5), "unit": x["unit"], "nation": x["nation"],
                 "nms_county": "", "townland": "", "notes": (x["desc"] or "")[:300], "placeholder": False, "url": "https://www.openstreetmap.org/" + x["osm"],
                 "located_unit": x["unit"], "holy": holy, "tags": tags, "wd": x.get("wd", "")})

# ---------- Wikidata holy wells ----------
wd = json.load(open(WD)); wd_steps = {"input": len(wd)}
wd_in = []
for x in wd:
    m = re.match(r"Point\(([-\d.eE]+) ([-\d.eE]+)\)", x["c"]);
    if not m: continue
    lon, lat = float(m.group(1)), float(m.group(2))
    if not (-11 < lon < 2.2 and 49.8 < lat < 61): continue
    unit, nation = locate(lon, lat)
    if unit is None: continue
    wd_in.append({"q": x["w"].rsplit("/", 1)[-1], "name": x.get("wLabel", ""), "lon": lon, "lat": lat, "unit": unit, "nation": nation})
wd_steps["in_study_area"] = len(wd_in)
seen = set(); wd_u = []
for x in wd_in:
    if x["q"] in seen: continue
    seen.add(x["q"]); wd_u.append(x)
wd_steps["unique_items"] = len(wd_u)
cur = xy([r["lon"] for r in rows], [r["lat"] for r in rows]); ct = cKDTree(cur)
osm_wd = {r.get("wd") for r in rows if r.get("wd")}
added = 0; wd_matched = collections.Counter()
for x in wd_u:
    d, i = ct.query(xy([x["lon"]], [x["lat"]])[0])
    if d <= DEDUP_M or x["q"] in osm_wd:
        wd_matched[rows[int(i)]["src"] if d <= DEDUP_M else "OSM"] += 1
        if rows[int(i)]["src"] == "OSM" and d <= DEDUP_M: rows[int(i)]["holy"] = True  # Wikidata says it is a holy well
        continue
    if re.match(r"^Q\d+$", x["name"] or ""): x["name"] = ""
    rows.append({"src": "Wikidata", "id": x["q"], "name": x["name"], "lon": round(x["lon"], 5), "lat": round(x["lat"], 5), "unit": x["unit"], "nation": x["nation"],
                 "nms_county": "", "townland": "", "notes": "", "placeholder": False, "url": "https://www.wikidata.org/wiki/" + x["q"],
                 "located_unit": x["unit"], "holy": True, "tags": ""}); added += 1
wd_steps["matched"] = dict(wd_matched); wd_steps["added"] = added

# ---------- readings ----------
for r in rows:
    k, how = saint(r["name"]); r["saint"] = k or ""; r["saint_how"] = how or ""
    r["folk_name"] = ";".join(folk(r["name"]))
    r["language"] = language(r["name"], r["nation"], r["unit"])
    if r["folk_name"] and not r["holy"]: r["holy"] = False  # folk names alone are kept as 'named wells', reported separately

cols = ["src", "id", "name", "lon", "lat", "nation", "unit", "townland", "holy", "saint", "saint_how", "language", "folk_name", "tags", "url"]
with open(os.path.join(ROOT, "data", "wells.csv"), "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore"); w.writeheader(); [w.writerow(r) for r in rows]
with open(os.path.join(ROOT, "data", "osm_filter_steps.csv"), "w", newline="") as f:
    w = csv.writer(f); w.writerow(["step", "features_remaining", "dropped"]); prev = None
    for s, n in steps: w.writerow([s, n, "" if prev is None else prev - n]); prev = n
json.dump({"rows": rows, "steps": steps, "why": why, "wd_steps": wd_steps, "osm_ie": len(osm_ie), "osm_ie_matched": osm_ie_matched,
           "nms_matched_by_osm": len(matched_nms), "osm_ie_holy": sum(1 for x in osm_ie if is_holy(x)), "osm_by_nation_all": collections.Counter(x["nation"] for x in s6), "osm_by_nation_holy": collections.Counter(x["nation"] for x in s6 if is_holy(x)),
           "nms_located_mismatch": sum(1 for r in rows if r["src"] == "NMS" and r["located_unit"] and r["located_unit"].upper() != r["nms_county"])},
          open(os.path.join(ROOT, "work", "build.json"), "w"), ensure_ascii=False)
for s, n in steps: print(n, s[:90])
print("why", why); print("wd", wd_steps); print(collections.Counter((r["src"], r["nation"], r["holy"]) for r in rows))
