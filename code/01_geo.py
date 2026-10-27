"""Step 1: boundary units for counting and density.

Builds data/geo/units.geojson: one polygon per county or area, with its nation
and land area in km2 (measured in ETRS89-LAEA, EPSG:3035, before simplifying).

- England, Scotland, Wales: ceremonial counties (England), preserved counties
  (Wales) and council areas (Scotland), from the ONS-based county file built for
  my 'How Roman is your road?' project (Office for National Statistics, contains
  OS data, Crown copyright, Open Government Licence v3).
- Republic of Ireland (26 counties, Tipperary split North/South as in the
  National Monuments Service records), Northern Ireland (one unit) and the Isle
  of Man: Natural Earth 10m admin-1 states and provinces (public domain),
  extracted to data/geo/ne_admin1_ie_ni_im.geojson. Cities are merged into their
  counties (Cork, Galway, Limerick, Waterford) and the four Dublin authorities
  into Dublin.
Run: python3 01_geo.py
"""
import json, os
from shapely.geometry import shape, mapping
from shapely.ops import unary_union, transform
from pyproj import Transformer

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(HERE, "..")
GB = "/home/claude/hist/how-roman-is-your-road/data/counties.geojson"
NE = os.path.join(ROOT, "data", "geo", "ne_admin1_ie_ni_im.geojson")
laea = Transformer.from_crs(4326, 3035, always_xy=True).transform

units = []
for f in json.load(open(GB))["features"]:
    units.append({"unit": f["properties"]["county"], "nation": f["properties"]["nation"], "geom": shape(f["geometry"])})

MERGE = {"D\u00fan Laoghaire\u2013Rathdown": "Dublin", "Fingal": "Dublin", "South Dublin": "Dublin", "Laoighis": "Laois",
         "North Tipperary": "Tipperary North", "South Tipperary": "Tipperary South"}
ie, ni, im = {}, [], []
for f in json.load(open(NE))["features"]:
    p = f["properties"]; g = shape(f["geometry"])
    if p["a3"] == "IRL":
        n = MERGE.get(p["name"], p["name"]); ie.setdefault(n, []).append(g)
    elif p["a3"] == "IMN": im.append(g)
    else: ni.append(g)
for n, gs in ie.items(): units.append({"unit": n, "nation": "Ireland", "geom": unary_union(gs)})
units.append({"unit": "Northern Ireland", "nation": "Northern Ireland", "geom": unary_union(ni)})
units.append({"unit": "Isle of Man", "nation": "Isle of Man", "geom": unary_union(im)})

feats = []
for u in units:
    km2 = transform(laea, u["geom"]).area / 1e6
    g = u["geom"].simplify(0.004, preserve_topology=True)
    feats.append({"type": "Feature", "properties": {"unit": u["unit"], "nation": u["nation"], "km2": round(km2, 1)},
                  "geometry": json.loads(json.dumps(mapping(g), default=float))})
os.makedirs(os.path.join(ROOT, "data", "geo"), exist_ok=True)


def rnd(o):
    if isinstance(o, float): return round(o, 4)
    if isinstance(o, (list, tuple)): return [rnd(x) for x in o]
    if isinstance(o, dict): return {k: rnd(v) for k, v in o.items()}
    return o


json.dump({"type": "FeatureCollection", "features": rnd(feats)}, open(os.path.join(ROOT, "data", "geo", "units.geojson"), "w"), separators=(",", ":"))
tot = {}
for f in feats: tot[f["properties"]["nation"]] = tot.get(f["properties"]["nation"], 0) + f["properties"]["km2"]
print(len(feats), "units", {k: round(v) for k, v in tot.items()})
