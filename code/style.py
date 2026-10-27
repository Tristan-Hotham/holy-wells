"""Shared matplotlib house style for the header, paper and blog figures and the collage.

Fonts: Fraunces, Source Serif 4 and IBM Plex Mono (Google Fonts, SIL OFL) from FONT_DIR;
falls back to DejaVu if they are missing.
"""
import os, json, csv
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
from matplotlib.patches import Polygon as MPoly
from matplotlib.collections import PatchCollection

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(HERE, "..")
FD = os.environ.get("FONT_DIR", "/tmp/claude-0/-home-claude/c232619d-81e0-53f3-9de6-41e973630753/scratchpad/fonts/")
DISP = None
try:
    for f in ["FrauncesVar.ttf", "IBMPlexMono-Regular.ttf", "IBMPlexMono-Medium.ttf", "SourceSerif4-Regular.ttf", "SourceSerif4-Semibold.ttf", "SourceSerif4-It.ttf"]:
        fm.fontManager.addfont(os.path.join(FD, f))
    DISP = fm.FontProperties(fname=os.path.join(FD, "FrauncesVar.ttf"), weight=900)
    SER, MONO = "Source Serif 4", "IBM Plex Mono"
except Exception:
    SER, MONO = "DejaVu Serif", "DejaVu Sans Mono"; DISP = fm.FontProperties(family="DejaVu Serif", weight="bold")

BG = "#F1EFE8"; PANEL = "#E6E3D8"; FG = "#17232B"; MUT = "#5F6A6E"; RULE = "#D5D1C4"; LAND = "#E2DFD3"; LANDEDGE = "#C9C4B5"
HOT = "#0E7C86"; RAG = "#C0412B"; PAT = "#2F7D4A"; MARY = "#2F5DA6"; COL = "#7B4F9E"; GOLD = "#A87A12"; MOSS = "#6E8A3A"; OTHER = "#8C857A"; NONE = "#BDB8AC"; DOT = "#8D8A80"
SAINTCOL = {"Brigid": RAG, "Patrick": PAT, "Mary": MARY, "Colmcille": COL, "Ciaran": GOLD}
LANGCOL = {"English": MARY, "Irish (anglicised)": PAT, "Irish (Gaelic spelling)": MOSS, "Welsh": RAG, "Scottish Gaelic": COL, "Cornish": GOLD, "Manx": HOT, "other": OTHER, "unnamed": NONE}
NONS = {"Holy (no saint named)", "Trinity", "Christ", "Sunday", "All Saints"}
plt.rcParams.update({"font.family": SER, "axes.edgecolor": MUT, "axes.labelcolor": FG, "xtick.color": MUT, "ytick.color": MUT, "text.color": FG,
                     "axes.spines.top": False, "axes.spines.right": False, "savefig.facecolor": BG, "figure.facecolor": BG, "axes.facecolor": BG})

R = json.load(open(os.path.join(ROOT, "data", "results.json")))
COS = np.cos(np.radians(54.5))


def P(lon, lat):
    return np.asarray(lon, float) * COS, np.asarray(lat, float)


def wells():
    rows = list(csv.DictReader(open(os.path.join(ROOT, "data", "wells.csv"))))
    for r in rows:
        r["lon"] = float(r["lon"]); r["lat"] = float(r["lat"]); r["holy"] = r["holy"] == "True"
    return rows


def holy_set(rows):
    return [r for r in rows if r["src"] == "NMS" or (r["holy"] and r["nation"] != "Ireland")]


def other_set(rows):
    return [r for r in rows if not r["holy"] and r["src"] != "NMS"]


def land(ax, fc=LAND, ec=LANDEDGE, lw=0.3, nations=None):
    U = json.load(open(os.path.join(ROOT, "data", "geo", "units.geojson")))["features"]
    patches = []
    for f in U:
        if nations and f["properties"]["nation"] not in nations: continue
        g = f["geometry"]; gs = g["geometries"] if g["type"] == "GeometryCollection" else [g]
        polys = [p for h in gs if h["type"] in ("Polygon", "MultiPolygon") for p in (h["coordinates"] if h["type"] == "MultiPolygon" else [h["coordinates"]])]
        for poly in polys:
            ring = np.array(poly[0]); x, y = P(ring[:, 0], ring[:, 1])
            patches.append(MPoly(np.c_[x, y], closed=True))
    ax.add_collection(PatchCollection(patches, facecolor=fc, edgecolor=ec, linewidth=lw, zorder=0))
    ax.set_aspect("equal"); ax.axis("off")


def saint_colour(r):
    if not r["saint"]: return NONE
    if r["saint"] in NONS: return HOT
    return SAINTCOL.get(r["saint"], MOSS)
