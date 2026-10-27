"""Step 3: every number for the page, paper, blog and collage -> data/results.json.

Also writes data/nations.csv, data/counties.csv, data/saints.csv,
data/languages.csv, data/practices.csv, data/practice_examples.csv and the
compact page data work/site.json.
Run: python3 03_analyse.py
"""
import json, os, re, csv, collections, random
import numpy as np
from scipy.spatial import cKDTree
from shapely.geometry import shape, Point
from shapely import STRtree
from wellnames import saint, norm

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(HERE, "..")
WDDIR = os.environ.get("WD_DIR", "/home/claude/hist/_data2/wikidata")
B = json.load(open(os.path.join(ROOT, "work", "build.json")))
rows = B["rows"]
for _r in rows:  # SMR references in the descriptions end in runs of hyphens (CL003-032----); shorten them for display
    _r["notes"] = re.sub(r"-{2,}", "-", re.sub(r"(\w)-{2,}(?=[)\s.,;])", r"\1", _r["notes"]))
U = json.load(open(os.path.join(ROOT, "data", "geo", "units.geojson")))["features"]
AREA = {f["properties"]["unit"]: f["properties"]["km2"] for f in U}
NAT_AREA = collections.Counter()
for f in U: NAT_AREA[f["properties"]["nation"]] += f["properties"]["km2"]
NATIONS = ["Ireland", "Northern Ireland", "Wales", "England", "Scotland", "Isle of Man"]
NLABEL = {"Ireland": "Republic of Ireland", "Northern Ireland": "Northern Ireland", "Wales": "Wales", "England": "England", "Scotland": "Scotland", "Isle of Man": "Isle of Man"}
R = {}
r1 = lambda v, d=1: round(float(v), d)

# ---------- the study set ----------
# Republic of Ireland: the NMS inventory is the holy-well set; OSM and Wikidata extras there are kept in wells.csv but not counted.
holy = [r for r in rows if (r["src"] == "NMS") or (r["holy"] and r["nation"] != "Ireland")]
named_other = [r for r in rows if not r["holy"] and r["src"] != "NMS"]
R["n_nms"] = sum(1 for r in rows if r["src"] == "NMS")
R["n_holy"] = len(holy); R["n_holy_britain_ni_im"] = len(holy) - R["n_nms"]
R["n_named_other"] = len(named_other)
R["n_rows"] = len(rows)
R["osm_steps"] = [{"step": s, "n": n} for s, n in B["steps"]]
R["osm_input"] = B["steps"][0][1]; R["osm_kept_before_nms"] = B["steps"][-2][1]; R["osm_final"] = B["steps"][-1][1]
R["osm_why"] = B["why"]; R["wd"] = B["wd_steps"]
R["osm_ie"] = B["osm_ie"]; R["osm_ie_matched"] = B["osm_ie_matched"]; R["nms_matched_by_osm"] = B["nms_matched_by_osm"]
R["nms_share_in_osm"] = R["nms_matched_by_osm"] / R["n_nms"]
R["osm_extra_ie"] = sum(1 for r in rows if r["nation"] == "Ireland" and r["src"] == "OSM")
R["wd_extra_ie"] = sum(1 for r in rows if r["nation"] == "Ireland" and r["src"] == "Wikidata")
R["by_src_holy"] = dict(collections.Counter(r["src"] for r in holy))

# ---------- nations ----------
nat = []
for n in NATIONS:
    h = [r for r in holy if r["nation"] == n]; a = NAT_AREA[n]
    osm_h = B["osm_by_nation_holy"].get(n, 0); osm_all = B["osm_by_nation_all"].get(n, 0)
    allnamed = len(h) + sum(1 for r in named_other if r["nation"] == n)
    nat.append({"nation": n, "label": NLABEL[n], "km2": round(a), "holy": len(h), "per1000": len(h) / a * 1000,
                "source": "NMS inventory" if n == "Ireland" else "OpenStreetMap and Wikidata",
                "osm_holy": osm_h, "osm_holy_per1000": osm_h / a * 1000, "all_named": allnamed if n != "Ireland" else len(h) + R["osm_extra_ie"],
                "osm_all": osm_all, "osm_all_per1000": osm_all / a * 1000})
R["nations"] = nat
NA = {x["nation"]: x for x in nat}
R["ratio_roi_ni"] = NA["Ireland"]["per1000"] / NA["Northern Ireland"]["per1000"]
R["ratio_osm_roi_ni"] = NA["Ireland"]["osm_holy_per1000"] / NA["Northern Ireland"]["osm_holy_per1000"]
R["ratio_roi_nms_vs_osm"] = NA["Ireland"]["per1000"] / NA["Ireland"]["osm_holy_per1000"]
gb = [x for x in nat if x["nation"] in ("England", "Scotland", "Wales")]
R["britain_holy"] = sum(x["holy"] for x in gb); R["britain_km2"] = sum(x["km2"] for x in gb)
R["britain_per1000"] = R["britain_holy"] / R["britain_km2"] * 1000
R["ratio_roi_britain"] = NA["Ireland"]["per1000"] / R["britain_per1000"]
with open(os.path.join(ROOT, "data", "nations.csv"), "w", newline="") as f:
    w = csv.writer(f); w.writerow(["nation", "area_km2", "holy_wells", "per_1000_km2", "source_of_holy_wells", "osm_holy_wells", "osm_holy_per_1000_km2", "osm_named_wells_all", "osm_all_per_1000_km2"])
    for x in nat: w.writerow([x["label"], x["km2"], x["holy"], r1(x["per1000"], 2), x["source"], x["osm_holy"], r1(x["osm_holy_per1000"], 2), x["osm_all"], r1(x["osm_all_per1000"], 2)])

# ---------- counties ----------
cnt = collections.Counter();
NMS2UNIT = lambda c: c.title()
for r in holy:
    u = NMS2UNIT(r["nms_county"]) if r["src"] == "NMS" else r["unit"]
    cnt[u] += 1
unit_nation = {f["properties"]["unit"]: f["properties"]["nation"] for f in U}
missing = [u for u in cnt if u not in AREA]
assert not missing, missing
counties = []
for f in U:
    u = f["properties"]["unit"]; n = cnt.get(u, 0)
    counties.append({"unit": u, "nation": f["properties"]["nation"], "km2": f["properties"]["km2"], "holy": n, "per1000": n / f["properties"]["km2"] * 1000})
counties.sort(key=lambda x: -x["per1000"])
roi = [c for c in counties if c["nation"] == "Ireland"]
brit = [c for c in counties if c["nation"] in ("England", "Wales", "Scotland") and c["km2"] > 400]
R["roi_counties"] = [{k: (r1(v, 1) if k == "per1000" else v) for k, v in c.items()} for c in roi]
R["roi_top"] = R["roi_counties"][:5]; R["roi_bottom"] = R["roi_counties"][-3:]
R["britain_top_counties"] = [{"unit": c["unit"], "nation": c["nation"], "holy": c["holy"], "per1000": r1(c["per1000"], 1)} for c in sorted(brit, key=lambda x: -x["per1000"])[:8]]
R["britain_top_counts"] = [{"unit": c["unit"], "holy": c["holy"]} for c in sorted(brit, key=lambda x: -x["holy"])[:8]]
R["roi_most"] = max(roi, key=lambda x: x["holy"])["unit"]; R["roi_most_n"] = max(roi, key=lambda x: x["holy"])["holy"]
with open(os.path.join(ROOT, "data", "counties.csv"), "w", newline="") as f:
    w = csv.writer(f); w.writerow(["unit", "nation", "area_km2", "holy_wells", "per_1000_km2"])
    for c in counties: w.writerow([c["unit"], NLABEL[c["nation"]], c["km2"], c["holy"], r1(c["per1000"], 2)])

# ---------- saints ----------
GROUPS = {"Republic of Ireland": lambda r: r["src"] == "NMS", "Northern Ireland": lambda r: r["nation"] == "Northern Ireland",
          "Wales": lambda r: r["nation"] == "Wales", "England": lambda r: r["nation"] == "England", "Scotland": lambda r: r["nation"] == "Scotland"}
NONSAINT = {"Holy (no saint named)", "Trinity", "Christ", "Sunday", "All Saints"}
sg = {}
for g, fn in GROUPS.items():
    h = [r for r in holy if fn(r)]
    named = [r for r in h if r["name"]]
    withsaint = [r for r in named if r["saint"] and r["saint"] not in NONSAINT]
    relig = [r for r in named if r["saint"] in NONSAINT]
    c = collections.Counter(r["saint"] for r in withsaint)
    sg[g] = {"n": len(h), "named": len(named), "with_saint": len(withsaint), "religious_no_saint": len(relig),
             "unread": len(named) - len(withsaint) - len(relig), "share_saint": len(withsaint) / max(1, len(named)),
             "share_unread": (len(named) - len(withsaint) - len(relig)) / max(1, len(named)),
             "top": [{"key": k, "n": v, "share": v / len(withsaint)} for k, v in c.most_common(12)],
             "distinct": len(c), "how": dict(collections.Counter(r["saint_how"] for r in withsaint)),
             "holy_no_saint": sum(1 for r in relig if r["saint"] == "Holy (no saint named)")}
R["saints"] = sg
nms_named = [r for r in holy if r["src"] == "NMS" and r["name"]]
R["nms_named"] = len(nms_named); R["nms_unnamed"] = R["n_nms"] - len(nms_named)
# Brigid vs Patrick in Ireland
roi_c = collections.Counter(r["saint"] for r in nms_named if r["saint"])
R["roi_brigid"] = roi_c["Brigid"]; R["roi_patrick"] = roi_c["Patrick"]; R["roi_mary"] = roi_c["Mary"]
# Gaelic-form reading: how many saint readings came from Tober/Tobar compounds
R["roi_saint_from_gaelic"] = sum(1 for r in nms_named if r["saint_how"] == "gaelic")
# notes: 'dedicated to St X' as a second reading for unnamed or unread NMS wells
DED = re.compile(r"(?i)dedicated to (?:the )?(?:st\.?|saint|our lady|the blessed virgin)\s*([A-Z][a-záéíóú]+)?")
extra = collections.Counter(); n_extra = 0
for r in holy:
    if r["src"] != "NMS" or (r["saint"] and r["saint"] not in NONSAINT): continue
    m = DED.search(r["notes"])
    if m:
        txt = m.group(0)
        k, _ = saint("St " + m.group(1)) if m.group(1) else (("Mary", "") if re.search(r"(?i)our lady|virgin", txt) else (None, None))
        if k: extra[k] += 1; n_extra += 1
R["notes_dedication_extra"] = n_extra; R["notes_dedication_extra_top"] = extra.most_common(5)
all_roi = roi_c + extra
nm_saint_total = sum(v for k, v in all_roi.items() if k not in NONSAINT)
R["roi_name_or_notes_saint"] = nm_saint_total
R["roi_name_or_notes_top"] = [{"key": k, "n": v, "share": v / nm_saint_total} for k, v in all_roi.most_common(20) if k not in NONSAINT][:8]
with open(os.path.join(ROOT, "data", "saints.csv"), "w", newline="") as f:
    w = csv.writer(f); w.writerow(["group", "saint_or_dedication", "wells", "share_of_wells_with_a_saint_read"])
    for g in GROUPS:
        h = [r for r in holy if GROUPS[g](r) and r["name"] and r["saint"]]
        c = collections.Counter(r["saint"] for r in h); ns = sum(v for k, v in c.items() if k not in NONSAINT)
        for k, v in c.most_common(): w.writerow([g, k, v, "" if k in NONSAINT else round(v / ns, 4)])

# ---------- languages ----------
LANGS = ["English", "Irish (anglicised)", "Irish (Gaelic spelling)", "Welsh", "Scottish Gaelic", "Cornish", "Manx", "other"]
lg = {}
for n in NATIONS:
    h = [r for r in holy if r["nation"] == n and r["name"]] + ([r for r in named_other if r["nation"] == n] if n != "Ireland" else [])
    c = collections.Counter(r["language"] for r in h)
    lg[n] = {"n": len(h), "counts": {k: c.get(k, 0) for k in LANGS}}
R["languages"] = lg
L_ie = lg["Ireland"]["counts"]; nie = lg["Ireland"]["n"]
R["roi_irish_share"] = (L_ie["Irish (anglicised)"] + L_ie["Irish (Gaelic spelling)"]) / nie
R["roi_english_share"] = L_ie["English"] / nie
L_w = lg["Wales"]["counts"]; R["wales_welsh_share"] = L_w["Welsh"] / lg["Wales"]["n"]
L_s = lg["Scotland"]["counts"]; R["scot_gaelic_share"] = L_s["Scottish Gaelic"] / lg["Scotland"]["n"]
L_ni = lg["Northern Ireland"]["counts"]; R["ni_irish_share"] = (L_ni["Irish (anglicised)"] + L_ni["Irish (Gaelic spelling)"]) / lg["Northern Ireland"]["n"]
with open(os.path.join(ROOT, "data", "languages.csv"), "w", newline="") as f:
    w = csv.writer(f); w.writerow(["nation", "named_wells"] + LANGS)
    for n in NATIONS: w.writerow([NLABEL[n], lg[n]["n"]] + [lg[n]["counts"][k] for k in LANGS])
# English-form vs Irish-form names among ROI wells with a saint: language of the saint's wells
R["roi_saint_english_form"] = sum(1 for r in nms_named if r["saint"] and r["saint"] not in NONSAINT and r["language"] == "English")
R["roi_saint_irish_form"] = sum(1 for r in nms_named if r["saint"] and r["saint"] not in NONSAINT and r["language"].startswith("Irish"))

# ---------- folk names (all named wells in the study set, holy or not) ----------
FN = ["wishing", "rag or clootie", "pin", "cursing", "eye", "wart", "fever or ague"]
pool = holy + named_other
fc = {k: [r for r in pool if k in r["folk_name"].split(";")] for k in FN}
R["folk_names"] = {k: {"n": len(v), "by_nation": dict(collections.Counter(r["nation"] for r in v)), "examples": sorted({r["name"] for r in v})[:8]} for k, v in fc.items()}
R["folk_names_total"] = len({id(r) for v in fc.values() for r in v})
R["wishing_holy"] = sum(1 for r in fc["wishing"] if r["holy"])
R["n_named_pool"] = sum(1 for r in pool if r["name"])


# 'Wishing Well' as a name in the raw OSM extract: wells against businesses and other things
raw = json.load(open(os.environ.get("OSM", "/home/claude/hist/_data6/osm_named_wells_gb_ie_im.json")))
ww = [x for x in raw if re.search(r"(?i)\bwishing well", x["name"])]
kept_ids = {r["id"] for r in rows if r["src"] == "OSM"}
BUS = re.compile(r"(?i)\b(pub|inn|bar|cafe|caf\u00e9|tea|restaurant|hotel|guest|house|cottage|barn|nursery|childcare|kindergarten|centre|family|fitness|health|mobility|close|green|caravan|halt|road|shop|day)\b")
cat = collections.Counter()
for x in ww:
    if x["osm"] in kept_ids: cat["well"] += 1
    elif x["amen"] in ("pub", "bar", "cafe", "restaurant", "fast_food") or re.search(r"(?i)\b(pub|inn|bar|cafe|tea gardens|restaurant)\b", x["name"]): cat["pub, cafe or restaurant"] += 1
    elif x["amen"] in ("kindergarten", "childcare", "social_facility", "school") or re.search(r"(?i)nursery|family centre|kindergarten", x["name"]): cat["nursery, childcare or care"] += 1
    elif re.search(r"(?i)hotel|guest house|cottage|barn|caravan", x["name"]): cat["hotel, cottage or holiday let"] += 1
    else: cat["other or unclear"] += 1
R["wishing_raw"] = len(ww); R["wishing_raw_cat"] = dict(cat)

# ---------- practices in NMS descriptions ----------
desc = [r for r in rows if r["src"] == "NMS" and r["notes"]]
R["nms_described"] = len(desc); R["nms_placeholder"] = sum(1 for r in rows if r["src"] == "NMS" and r["placeholder"])
R["nms_blank"] = R["n_nms"] - R["nms_described"] - R["nms_placeholder"]
R["notes_max_chars"] = max(len(r["notes"]) for r in desc)
R["notes_at_limit"] = sum(1 for r in desc if len(r["notes"]) >= 250)
R["notes_at_limit_share"] = R["notes_at_limit"] / len(desc)
NOTSTATION = r"(?<!coastguard )(?<!railway )(?<!police )(?<!garda )(?<!pumping )(?<!radar )(?<!lifeboat )"
P = [
    ("cure", "A cure or healing", r"\bcur(?:e|es|ed|ing|ative)\b|\bheal(?:ing|s|ed)?\b|\bailments?\b|\bsore\b|\bwarts?\b|\beyes?\b|\bheadaches?\b|\btoothache\b|\bbackache\b|rheumati|\bsprains?\b|\bfevers?\b|\blameness\b|\bmiracul"),
    ("eyes", "Eyes (a cure, or a well of the eyes)", r"\beyes?\b|\bsight\b|\bblind"),
    ("warts", "Warts (cure)", r"\bwarts?\b"),
    ("head_teeth", "Headache or toothache (cure)", r"\bheadaches?\b|\btoothache\b|\bteeth\b"),
    ("rags", "Rags, cloth or a rag tree", r"\brags?\b|\brag[- ]?trees?\b|\bcloths?\b|\bribbons?\b|\bclooties?\b|strips of (?:cloth|material)"),
    ("offerings", "Offerings or votive objects", r"\bvotive\b|\bofferings?\b|\bcoins?\b|\bpins?\b|\bmedals?\b|\brosar(?:y|ies)\b|\bmoney\b|\bbeads\b|holy pictures|mass cards|\bbuttons?\b|\bpennies\b|\bcandles?\b|statuettes|\btrinkets\b|\bmementoe?s\b|religious objects|\bcups?\b|\bmugs?\b|\bdevotional (?:items|objects)"),
    ("coins", "Coins or money", r"\bcoins?\b|\bpennies\b|\bpenny\b|\bmoney\b"),
    ("pattern", "Pattern, pilgrimage, rounds or stations", r"\bpatterns?\b|\bpatron day\b|\bpilgrim|\brounds\b|\bturas\b|" + NOTSTATION + r"\bstations?\b|\bfeast day\b|\bsaint'?s day\b|\bfeast of\b"),
    ("still", "Still visited, venerated or tended", r"\bstill (?:visited|venerated|frequented|in (?:holy )?use|used|attended|held|takes? place|resorted|popular|revered|honoured|maintained|tended)|annual mass|mass is (?:said|celebrated)|well[- ]kept|well[- ]maintained|\bis maintained\b|\bpilgrims still\b|\bcontinues to be (?:visited|venerated)"),
    ("tree", "A tree at the well", r"\btrees?\b|\bhawthorn|\bwhitethorn|\bblackthorn|\bash\b|\bsycamore|\bholly\b|\belder\b|\bthorn bush"),
    ("church", "A church, graveyard or church site nearby", r"\bchurch|\bgraveyard|burial ground|ecclesiastical|\bmonast|\bchapel|\babbey\b|\bfriary\b|\bpriory\b|\bkilleen\b|\bcill[ií]n\b"),
    ("statue", "A statue, shrine, grotto or cross at the well", r"\bstatues?\b|\bgrotto\b|\bshrines?\b|\bcrucifix|\bcross(?:es)? (?:on|atop|above|erected|set)\b|(?:wooden|iron|metal|concrete|stone|small) cross\b"),
    ("lost", "Dry, lost or site only", r"\bdry\b|\bdried\b|no (?:visible )?(?:surface )?trace|no longer|filled in|\binfilled\b|\bdestroyed\b|\blevell?ed\b|\bculverted\b|location (?:is )?not known|\bsite of\b|\bpiped\b|\bdrained\b"),
]
NEG = re.compile(r"(?i)\b(no|not|nor|without|never|none)\b[^.;]{0,25}$")


def positive(c, text, use_neg=True):
    """First match of c in text that is not negated just before it ('no votive offerings', 'No devotions now')."""
    for m in c.finditer(text):
        if use_neg and NEG.search(text[max(0, m.start() - 30):m.start()]): continue
        return m
    return None


pr = {}; flags = {r["id"]: [] for r in desc}
ex = []
random.seed(11)
for key, label, rx in P:
    c = re.compile(rx, re.I)
    hit = [r for r in desc if positive(c, r["notes"], key != "lost")]
    for r in hit: flags[r["id"]].append(key)
    bycty = collections.Counter(r["nms_county"] for r in hit); tot = collections.Counter(r["nms_county"] for r in desc)
    pr[key] = {"label": label, "n": len(hit), "share": len(hit) / len(desc),
               "by_county": {k.title(): {"n": bycty.get(k, 0), "of": v, "share": bycty.get(k, 0) / v} for k, v in tot.items()}}
    # examples: short, clean windows around the first hit
    cand = sorted(hit, key=lambda r: (len(r["notes"]), r["id"]))
    random.shuffle(cand)
    picked = 0
    for r in cand:
        m = positive(c, r["notes"], key != "lost"); a = max(0, m.start() - 70); b = min(len(r["notes"]), m.end() + 80)
        a = r["notes"].rfind(" ", 0, a) + 1 if a > 0 else 0
        b2 = r["notes"].find(" ", b); b = b2 if b2 > 0 else len(r["notes"])
        snip = ("..." if a > 0 else "") + r["notes"][a:b].strip() + ("..." if (b < len(r["notes"]) or len(r["notes"]) >= 250) else "")
        snip = snip.replace("–", "-").replace("—", "-").replace("--", "-")
        if "Archaeological Inventory" in snip or "Compiled by" in snip: continue
        ex.append({"practice": key, "smr": r["id"], "county": r["nms_county"].title(), "name": r["name"], "snippet": snip, "url": r["url"]})
        picked += 1
        if picked == 3: break
R["practices"] = pr
R["practice_examples"] = ex
anyfolk = [r for r in desc if set(flags[r["id"]]) & {"cure", "rags", "offerings", "pattern"}]
R["any_folk"] = len(anyfolk); R["any_folk_share"] = len(anyfolk) / len(desc)
R["rags_or_offerings"] = sum(1 for r in desc if set(flags[r["id"]]) & {"rags", "offerings"}); R["rags_or_offerings_share"] = R["rags_or_offerings"] / len(desc)
# do practice mentions go with a named saint?
withs = [r for r in desc if r["saint"] and r["saint"] not in NONSAINT]; nos = [r for r in desc if not (r["saint"] and r["saint"] not in NONSAINT)]
R["folk_given_saint"] = sum(1 for r in withs if r in anyfolk) / len(withs); R["folk_given_nosaint"] = sum(1 for r in nos if r in anyfolk) / len(nos)
R["n_desc_with_saint"] = len(withs); R["n_desc_no_saint"] = len(nos)
with open(os.path.join(ROOT, "data", "practices.csv"), "w", newline="") as f:
    w = csv.writer(f); w.writerow(["smr", "county", "townland", "name", "lon", "lat"] + [k for k, _, _ in P])
    for r in desc: w.writerow([r["id"], r["nms_county"].title(), r["townland"], r["name"], r["lon"], r["lat"]] + [int(k in flags[r["id"]]) for k, _, _ in P])
with open(os.path.join(ROOT, "data", "practice_examples.csv"), "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=["practice", "smr", "county", "name", "snippet", "url"]); w.writeheader(); [w.writerow(e) for e in ex]
# county league for the folk measures (counties with 40+ described wells)
lg2 = []
for k, v in pr["cure"]["by_county"].items():
    if v["of"] >= 40: lg2.append({"county": k, "of": v["of"], "cure": v["share"], "rags_off": sum(1 for r in desc if r["nms_county"].title() == k and set(flags[r["id"]]) & {"rags", "offerings"}) / v["of"], "pattern": pr["pattern"]["by_county"][k]["share"], "still": pr["still"]["by_county"][k]["share"]})
R["practice_counties"] = sorted(lg2, key=lambda x: -x["cure"])

# ---------- churches nearby ----------
def load_ch(cc):
    out = []
    for x in json.load(open(os.path.join(WDDIR, f"ch_{cc}.json"))):
        m = re.match(r"Point\(([-\d.eE]+) ([-\d.eE]+)\)", x.get("c", ""))
        if m: out.append((float(m.group(1)), float(m.group(2)), x.get("lab") or x.get("en") or ""))
    return out
ch = load_ch("GB") + load_ch("IE")
ch = [c for c in ch if -11 < c[0] < 2.2 and 49.8 < c[1] < 61]
def xy(lon, lat):
    lon, lat = np.asarray(lon, float), np.asarray(lat, float)
    return np.c_[lon * 111320 * np.cos(np.radians(lat)), lat * 110540]
CT = cKDTree(xy([c[0] for c in ch], [c[1] for c in ch]))
R["n_churches"] = len(ch); R["n_random"] = 20000
geoms = {n: [shape(f["geometry"]).buffer(0) for f in U if f["properties"]["nation"] == n] for n in NATIONS}
rng = np.random.default_rng(42)
def random_points(n_list, k):
    from shapely.ops import unary_union
    g = unary_union(sum((geoms[n] for n in n_list), [])); minx, miny, maxx, maxy = g.bounds
    from shapely import prepared; pg = prepared.prep(g); pts = []
    while len(pts) < k:
        xs = rng.uniform(minx, maxx, 4000); ys = rng.uniform(miny, maxy, 4000)
        pts += [(a, b) for a, b in zip(xs, ys) if pg.contains(Point(a, b))]
    return np.array(pts[:k])
chres = {}
for g, nl, fn in [("Republic of Ireland", ["Ireland"], lambda r: r["src"] == "NMS"), ("Britain", ["England", "Wales", "Scotland"], lambda r: r["nation"] in ("England", "Wales", "Scotland"))]:
    h = [r for r in holy if fn(r)]
    d, _ = CT.query(xy([r["lon"] for r in h], [r["lat"] for r in h]))
    rp = random_points(nl, R["n_random"]); dr, _ = CT.query(xy(rp[:, 0], rp[:, 1]))
    o = [r for r in named_other if r["nation"] in nl]
    do = CT.query(xy([r["lon"] for r in o], [r["lat"] for r in o]))[0] if o else np.array([])
    chres[g] = {"n": len(h), "median_m": float(np.median(d)), "random_median_m": float(np.median(dr)),
                "within_500": float(np.mean(d <= 500)), "random_within_500": float(np.mean(dr <= 500)),
                "within_1000": float(np.mean(d <= 1000)), "random_within_1000": float(np.mean(dr <= 1000)),
                "other_n": len(o), "other_within_500": float(np.mean(do <= 500)) if len(do) else None, "other_within_1000": float(np.mean(do <= 1000)) if len(do) else None,
                "other_median_m": float(np.median(do)) if len(do) else None}
    chres[g]["ratio_500"] = chres[g]["within_500"] / chres[g]["random_within_500"]
R["churches"] = chres
# same dedication: well with a saint, nearest church within 2 km, does the church name carry the same saint?
chkey = []
for c in ch:
    k, how = saint(c[2]); chkey.append(k if how in ("st", "mary") else None)
sd = {}
for g, fn in [("Republic of Ireland", lambda r: r["src"] == "NMS"), ("Britain", lambda r: r["nation"] in ("England", "Wales", "Scotland"))]:
    h = [r for r in holy if fn(r) and r["saint"] and r["saint"] not in NONSAINT]
    pairs = []
    for r in h:
        idx = CT.query_ball_point(xy([r["lon"]], [r["lat"]])[0], 2000)
        ks = {chkey[i] for i in idx if chkey[i]}
        if ks: pairs.append((r["saint"], ks))
    obs = np.mean([s in ks for s, ks in pairs]) if pairs else 0
    sims = []
    keys = [s for s, _ in pairs]
    for _ in range(500):
        perm = rng.permutation(len(keys)); sims.append(np.mean([keys[perm[i]] in pairs[i][1] for i in range(len(keys))]))
    sd[g] = {"wells_with_saint": len(h), "with_named_church_2km": len(pairs), "same_saint": float(obs), "shuffled_mean": float(np.mean(sims)), "shuffled_p95": float(np.percentile(sims, 95)),
             "n_same": int(round(obs * len(pairs)))}
R["same_saint"] = sd

# ---------- headline odds and ends ----------
R["roi_per1000"] = NA["Ireland"]["per1000"]; R["ni_per1000"] = NA["Northern Ireland"]["per1000"]
R["dens_rows"] = [{"label": x["label"], "per1000": x["per1000"], "osm": x["osm_holy_per1000"]} for x in nat]
R["n_sites_on_map"] = len(holy) + len(named_other)
R["nms_site_of"] = sum(1 for x in json.load(open(os.environ.get("NMS", "/home/claude/hist/_data6/ireland_nms_holy_wells.json"))) if re.search(r"(?i)site of", (x.get("LATEST_EDI") or "") + (x.get("FIRST_EDIT") or "")))

# ---------- companion project (my earlier map of saints and holy wells across Western Europe) ----------
C = json.load(open(os.environ.get("COMPANION", "/home/claude/hist/saints-and-wells/data/results.json")))["wells"]
R["companion"] = {"wd_ie_wells": C["ie_n"], "wd_ie_identified": C["ie_identified"], "brigid_share": C["ie_top"][0]["share"], "brigid_n": C["ie_top"][0]["n"],
                  "mary_n": C["ie_top"][1]["n"], "patrick_n": C["ie_top"][2]["n"], "doi": "10.5281/zenodo.23677171", "url": "https://tristan-hotham.github.io/saints-and-wells/"}
s_ie = R["saints"]["Republic of Ireland"]
R["roi_brigid_share"] = R["roi_brigid"] / s_ie["with_saint"]; R["roi_mary_share"] = R["roi_mary"] / s_ie["with_saint"]; R["roi_patrick_share"] = R["roi_patrick"] / s_ie["with_saint"]
R["roi_saint_share_named"] = s_ie["with_saint"] / s_ie["named"]
R["nms_named_share"] = R["nms_named"] / R["n_nms"]
R["roi_saint_irish_form_share"] = R["roi_saint_irish_form"] / s_ie["with_saint"]
R["n_holy_gb"] = R["britain_holy"]

# ---------- page data ----------
SK = ["Brigid", "Patrick", "Mary", "Ciaran", "Colmcille", "Brendan", "John", "Anne", "Michael", "Helen", "Winifred", "David", "Holy (no saint named)"]
LI = {k: i for i, k in enumerate(LANGS + ["unnamed"])}
units_i = {u: i for i, u in enumerate(sorted({r["unit"] for r in holy + named_other}))}
PK = ["cure", "rags", "offerings", "pattern", "still"]
site = {"langs": LANGS + ["unnamed"], "units": sorted(units_i, key=units_i.get), "pk": PK, "w": []}
for r in holy + named_other:
    fl = flags.get(r["id"], []) if r["src"] == "NMS" else []
    pbits = sum(1 << i for i, k in enumerate(PK) if k in fl)
    site["w"].append([round(r["lat"], 4), round(r["lon"], 4), r["name"], {"NMS": 0, "OSM": 1, "Wikidata": 2}[r["src"]], 1 if (r["src"] == "NMS" or r["holy"]) else 0,
                      r["saint"], LI[r["language"]], r["folk_name"], units_i[r["unit"]], pbits, r["id"], r["notes"] if r["src"] == "NMS" else ""])
site["R"] = R
json.dump(site, open(os.path.join(ROOT, "work", "site.json"), "w"), ensure_ascii=False, separators=(",", ":"), default=float)


def clean(o):
    if isinstance(o, float): return round(o, 6)
    if isinstance(o, dict): return {k: clean(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)): return [clean(v) for v in o]
    return o


json.dump(clean(R), open(os.path.join(ROOT, "data", "results.json"), "w"), indent=1, ensure_ascii=False, default=float)
print(json.dumps({k: R[k] for k in ["n_holy", "n_holy_britain_ni_im", "n_named_other", "nms_share_in_osm", "ratio_roi_ni", "ratio_osm_roi_ni", "ratio_roi_britain", "roi_irish_share", "wales_welsh_share", "scot_gaelic_share", "nms_described", "notes_at_limit_share", "any_folk_share", "rags_or_offerings_share", "folk_given_saint", "folk_given_nosaint", "notes_dedication_extra"]}, indent=0, default=float))
for x in nat: print(x["label"], x["holy"], round(x["per1000"], 2), x["osm_holy"], round(x["osm_holy_per1000"], 2))
for g, v in sg.items(): print(g, v["n"], v["named"], v["with_saint"], round(v["share_unread"], 3), [(t["key"], t["n"]) for t in v["top"][:8]])
for k, v in pr.items(): print(k, v["n"], round(v["share"], 3))
print({k: (v["n"], v["by_nation"]) for k, v in R["folk_names"].items()})
print(json.dumps(chres, indent=0)); print(sd)
print(R["roi_top"], R["britain_top_counties"][:5])
print(lg); print(R["wishing_raw"], R["wishing_raw_cat"], R["roi_name_or_notes_top"])
