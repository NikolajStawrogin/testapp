"""Extract four named WRA river areas from a pinned, published GIS snapshot.

Build dependency: shapely. Runtime has no Python/package dependency.
Usage: python tools/build_river_data.py /path/to/interactive_risk_map_light.html
"""

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path

from shapely import make_valid
from shapely.geometry import MultiPolygon, Point, mapping, shape
from shapely.ops import unary_union


ROOT = Path(__file__).resolve().parents[1]
COMMIT = "89dbc71b78a3c1b9cb6896f4b3d59576942685e3"
SOURCE_SHA256 = "3ac4f7b7728f7aec29aa95c1cca03e73c16aa3a7dac8e5b75af237a4cadabe78"
SOURCE_URL = f"https://github.com/hankc0215/ARIA/blob/{COMMIT}/interactive_risk_map_light.html"
NAMES = [
    ("tamsui", "淡水河", "Tamsui River", [121.47, 25.13],
     "Der breite Unterlauf führt westlich von Taipei bis zur Mündung bei Tamsui und Bali."),
    ("keelung", "基隆河", "Keelung River", [121.55, 25.075],
     "Der Keelung-Fluss zieht durch Xizhi und am Norden des Stadtzentrums entlang, bevor er in den Tamsui mündet."),
    ("xindian", "新店溪", "Xindian River", [121.515, 25.005],
     "Der Xindian-Fluss begrenzt den Südwesten von Taipei und trifft westlich der Innenstadt auf den Dahan."),
    ("dahan", "大漢溪", "Dahan River", [121.46, 25.03],
     "Der Dahan-Fluss führt aus dem Südwesten durch New Taipei. Ab dem Zusammenfluss mit dem Xindian heißt der Fluss Tamsui."),
]


def polygons(geometry):
    if geometry.geom_type == "Polygon":
        return [geometry]
    if hasattr(geometry, "geoms"):
        return [poly for child in geometry.geoms for poly in polygons(child)]
    return []


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    args = parser.parse_args()
    raw = args.source.read_bytes()
    if hashlib.sha256(raw).hexdigest() != SOURCE_SHA256:
        raise ValueError("Der Datenauszug stimmt nicht mit der dokumentierten festen Version überein")
    text = raw.decode("utf-8")
    start = text.rfind('{"features"', 0, text.index('"RIVER_NAME"'))
    collection, _ = json.JSONDecoder().raw_decode(text, start)
    wanted = {row[1] for row in NAMES}
    source_features = [f for f in collection["features"] if f["properties"].get("RIVER_NAME") in wanted]
    assert set(Counter(f["properties"]["RIVER_NAME"] for f in source_features)) == wanted
    archive = {"type": "FeatureCollection", "features": source_features}
    (ROOT / "data/river-areas-source.geojson").write_text(json.dumps(archive, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    districts = json.loads((ROOT / "data/districts.js").read_text().split("=", 1)[1].strip().removesuffix(";"))
    city_shapes = {city["id"]: unary_union([make_valid(shape(f["geometry"])) for f in districts["features"] if f["cityId"] == city["id"]]) for city in districts["cities"]}
    region = unary_union(list(city_shapes.values()))
    features = []
    for id, zh, en, preferred_anchor, description in NAMES:
        original = unary_union([make_valid(shape(f["geometry"])) for f in source_features if f["properties"]["RIVER_NAME"] == zh])
        clipped = original.intersection(region)
        geometry = MultiPolygon(polygons(clipped))
        assert not geometry.is_empty
        # Keep an identifiable inner-city reach visible at the Taipei city zoom.
        preferred = Point(preferred_anchor)
        nearest = min(geometry.geoms, key=lambda polygon: polygon.distance(preferred))
        nearby = polygons(nearest.intersection(preferred.buffer(nearest.distance(preferred) + 0.003)))
        anchor = max(nearby, key=lambda polygon: polygon.area).representative_point()
        features.append({"id": "river-" + id, "kind": "river", "nameZh": zh, "nameEn": en,
                         "cityIds": [city for city, area in city_shapes.items() if original.intersection(area).area > 0.0000001],
                         "anchor": [round(anchor.x, 6), round(anchor.y, 6)], "description": description,
                         "geometry": json.loads(json.dumps(mapping(geometry)), parse_float=lambda n: round(float(n), 6))})
    output = {"version": 1, "source": {"provider": "Taiwan Water Resources Agency (WRA)",
              "originalUrl": "https://gic.wra.gov.tw/Gis/gic/API/Google/DownLoad.aspx?fname=RIVERPOLY&filetype=SHP",
              "snapshotUrl": SOURCE_URL, "commit": COMMIT, "snapshotSha256": hashlib.sha256(raw).hexdigest(),
              "changes": "Select by RIVER_NAME; dissolve by name; repair and clip to the two-city region; round WGS84 coordinates to six decimals. Published source already simplified by 0.0001 degrees.",
              "currentPrimarySourceVerified": False}, "features": features}
    (ROOT / "data/rivers.js").write_text("window.TAIPEI_RIVERS = " + json.dumps(output, ensure_ascii=False, separators=(",", ":")) + ";\n", encoding="utf-8")
    print([(f["nameZh"], f["cityIds"], len(f["geometry"]["coordinates"])) for f in features])


if __name__ == "__main__":
    main()
