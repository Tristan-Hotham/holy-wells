"""r/dataisbeautiful collage: ../reddit/saint_to_wish.png (2400 x 3000 px).
Every number comes from ../data/results.json and ../data/*.csv.
Run from reddit/: python3 collage.py
"""
import os, sys, csv
CHERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(CHERE, "..", "code"))
from style import *

BGC = "#E8F0EC"; LANDC = "#D3DDD6"; LANDE = "#BFCBC3"
rows = wells(); H = holy_set(rows); O = other_set(rows)
prac = list(csv.DictReader(open(os.path.join(ROOT, "data", "practices.csv"))))
fig = plt.figure(figsize=(12, 15), dpi=200, facecolor=BGC)

# title
fig.text(0.045, 0.962, "From saint to wish", fontproperties=DISP, fontsize=60, color=FG, va="top")
fig.text(0.047, 0.902, f"Where did the coin in the wishing well come from? {R['n_holy']:,} holy wells in Britain and Ireland,\nthe saints and languages in their names, and what people left behind at Irish wells.",
         family=SER, fontsize=15.5, color=FG, va="top", linespacing=1.4)

# hero map
ax = fig.add_axes([0.0, 0.305, 0.6, 0.53]); land(ax, fc=LANDC, ec=LANDE, lw=.3)
x, y = P([r["lon"] for r in O], [r["lat"] for r in O]); ax.scatter(x, y, s=2.5, c=DOT, lw=0, alpha=.4)
order = sorted(H, key=lambda r: 0 if not r["saint"] else 1 if r["saint"] not in SAINTCOL else 2)
x, y = P([r["lon"] for r in order], [r["lat"] for r in order])
ax.scatter(x, y, s=7, c=[saint_colour(r) for r in order], lw=.15, edgecolor=BGC, alpha=.95)
ax.set_xlim(-10.7 * COS, 1.9 * COS); ax.set_ylim(49.85, 58.75)
ax.annotate(f"Republic of Ireland:\nofficial inventory,\n{R['nations'][0]['per1000']:.1f} wells per 1,000 km²", xy=(-8.3 * COS, 51.75), xytext=(-10.6 * COS, 50.35), family=MONO, fontsize=10.5, color=FG,
            arrowprops=dict(arrowstyle="-", color=FG, lw=.8))
ax.annotate(f"Northern Ireland:\nvolunteer mapping,\n{R['nations'][1]['per1000']:.1f} per 1,000 km²", xy=(-6.6 * COS, 54.75), xytext=(-10.5 * COS, 57.6), family=MONO, fontsize=10.5, color=FG,
            arrowprops=dict(arrowstyle="-", color=FG, lw=.8))

# legend
items = [(MARY, "Mary"), (PAT, "Patrick"), (RAG, "Brigid"), (COL, "Colmcille"), (GOLD, "Ciarán"), (MOSS, "other saint"), (HOT, "holy, no saint named"), (NONE, "saint not read"), (DOT, "other named well")]
for i, (c, t) in enumerate(items):
    fig.patches.append(plt.Circle((0.622, 0.838 - i * 0.0152), 0.0045, color=c, transform=fig.transFigure, figure=fig))
    fig.text(0.635, 0.838 - i * 0.0152, t, family=MONO, fontsize=11, color=FG, va="center")

# big numbers
NUM = "#0B6670"
notes = [(f"{R['roi_mary']} v {R['roi_patrick']}", f"Irish holy wells named for Mary and\nfor Patrick: a dead heat. Brigid has {R['roi_brigid']}.\nIn Britain Mary leads everywhere."),
         (f"{R['any_folk_share']*100:.0f}%", f"of {R['nms_described']:,} described Irish wells mention\na cure, rags, offerings or a pattern day,\nin just the first {R['notes_max_chars']} characters of text."),
         (f"{R['roi_irish_share']*100:.0f}%", f"of named Irish wells have Irish names\n(Tober, Tobar). In Wales {R['wales_welsh_share']*100:.0f}% are\na Ffynnon."),
         (f"{R['wishing_raw_cat']['well']} of {R['wishing_raw']}", f"places called \"Wishing Well\" on\nOpenStreetMap are wells. The rest\ninclude {R['wishing_raw_cat']['pub, cafe or restaurant']} pubs and cafes and {R['wishing_raw_cat']['nursery, childcare or care']} nurseries.")]
for k, (big, small) in enumerate(notes):
    yb = 0.705 - k * 0.1
    fig.text(0.615, yb, big, fontproperties=DISP, fontsize=31, color=NUM, va="top")
    fig.text(0.617, yb - 0.04, small, family=SER, fontsize=12.2, color=FG, va="top", linespacing=1.3)

# small multiples: practices at Irish wells
fig.text(0.045, 0.285, f"WHAT THE IRISH RECORDS MENTION  ·  {R['nms_described']:,} described holy wells, first {R['notes_max_chars']} characters (lower bounds)", family=MONO, fontsize=11.5, color=MUT)
SM = [(["pattern"], "pattern, rounds,\npilgrimage", PAT), (["cure"], "a cure\n(eyes most often)", MARY), (["rags", "offerings"], "rags, coins\nor offerings", RAG), (["lost"], "dry, lost or\nsite only", "#7A776E")]
allx, ally = P([float(p["lon"]) for p in prac], [float(p["lat"]) for p in prac])
for i, (keys, lab, c) in enumerate(SM):
    a = fig.add_axes([0.02 + i * 0.245, 0.105, 0.23, 0.125]); land(a, fc=LANDC, ec=LANDE, lw=.25, nations={"Ireland", "Northern Ireland"})
    a.scatter(allx, ally, s=1.2, c="#AEB7B1", lw=0)
    sel = [p for p in prac if any(p[k] == "1" for k in keys)]
    sx, sy = P([float(p["lon"]) for p in sel], [float(p["lat"]) for p in sel]); a.scatter(sx, sy, s=6, c=c, lw=0, alpha=.95)
    a.set_xlim(-10.6 * COS, -5.4 * COS); a.set_ylim(51.35, 55.45)
    n = len(sel)
    fig.text(0.03 + i * 0.245, 0.268, lab, family=MONO, fontsize=11, color=FG, va="top", linespacing=1.15)
    fig.text(0.03 + i * 0.245, 0.236, f"{n:,}  ({n / R['nms_described'] * 100:.0f}%)", family=MONO, fontsize=11.5, color=c, va="top", weight="medium")

# footer
fig.text(0.045, 0.088, "Data: National Monuments Service (Ireland), Sites and Monuments Record, holy wells, CC BY 4.0.\nOpenStreetMap contributors, ODbL. Wikidata, CC0. ONS boundaries (OGL v3). Natural Earth.\nBritain's wells are volunteer-mapped and far from complete; Ireland's are an official inventory.\nAnalysis and chart: Tristan Hotham, with Python and matplotlib.  tristan-hotham.github.io/holy-wells",
         family=MONO, fontsize=10, color=MUT, va="top", linespacing=1.4)
fig.savefig(os.path.join(CHERE, "saint_to_wish.png"), dpi=200, facecolor=BGC)
print("saint_to_wish.png written")
