"""Build the two-city street catalogue from the pinned local source archive.

Development dependencies: mapbox-vector-tile and shapely.
No network, API key or runtime Python dependency is required by the result.
"""

from collections import Counter, defaultdict
import csv
import hashlib
import io
import json
import math
from pathlib import Path
import re
import subprocess
import sys
import unicodedata
from zipfile import ZipFile

import mapbox_vector_tile
from shapely import make_valid
from shapely.geometry import LineString, MultiLineString, box, mapping, shape
from shapely.ops import unary_union
from shapely.strtree import STRtree


ROOT = Path(__file__).resolve().parents[1]
ROAD_TYPES = {"motorway", "motorway_link", "trunk", "trunk_link", "primary", "primary_link", "secondary", "secondary_link", "tertiary", "tertiary_link", "residential", "unclassified", "living_street", "service", "pedestrian", "road"}
RANK = {"motorway": 0, "trunk": 1, "primary": 2, "secondary": 3, "tertiary": 4, "residential": 5, "unclassified": 6, "living_street": 7, "service": 8, "pedestrian": 9, "road": 10}


def normalize(text):
    return unicodedata.normalize("NFKC", text).replace("臺", "台").replace(" ", "").strip()


def lines(geometry):
    if geometry.geom_type == "LineString":
        return [geometry] if geometry.length > 0.000012 else []
    if hasattr(geometry, "geoms"):
        return [line for child in geometry.geoms for line in lines(child)]
    return []


def canonical_geometry(geometry):
    return {"type": "MultiLineString", "coordinates": [[[round(x, 6), round(y, 6)] for x, y in line.simplify(0.000004).coords] for line in lines(geometry)]}


def merge_local_namesakes(features):
    """One postal street identity per name and district, even with mapped gaps."""
    parent = list(range(len(features)))

    def root(index):
        while parent[index] != index:
            parent[index] = parent[parent[index]]
            index = parent[index]
        return index

    seen = {}
    for index, feature in enumerate(features):
        for district in feature["districtIds"]:
            key = feature["cityId"], normalize(feature["nameZh"]), district
            if key in seen:
                parent[root(index)] = root(seen[key])
            else:
                seen[key] = index
    groups = defaultdict(list)
    for index, feature in enumerate(features):
        groups[root(index)].append(feature)
    result = []
    priority = {"postal-exact": 0, "postal-numbered": 1, "osm-name-en": 2, "missing": 3}
    for members in groups.values():
        if len(members) == 1:
            result.append(members[0])
            continue
        feature = min(members, key=lambda row: priority[row["nameSource"]]).copy()
        geometry = unary_union([shape(row["geometry"]) for row in members])
        anchor = max(lines(geometry), key=lambda line: line.length).interpolate(0.5, normalized=True)
        feature.update({"id": min(row["id"] for row in members), "districtIds": sorted({id for row in members for id in row["districtIds"]}),
                        "geometry": canonical_geometry(geometry), "anchor": [round(anchor.x, 6), round(anchor.y, 6)]})
        result.append(feature)
    return result


def main():
    districts = json.loads((ROOT / "data/districts.js").read_text().split("=", 1)[1].strip().removesuffix(";"))
    district_features = districts["features"]
    district_shapes = [make_valid(shape(feature["geometry"])) for feature in district_features]
    district_index = STRtree(district_shapes)
    city_shapes = {city["id"]: unary_union([geometry for feature, geometry in zip(district_features, district_shapes) if feature["cityId"] == city["id"]]) for city in districts["cities"]}
    region = unary_union(list(city_shapes.values()))
    ways = {}
    postal = defaultdict(set)
    with ZipFile(ROOT / "data/street-sources.zip") as archive:
        manifest = json.loads(archive.read("manifest.json"))
        for source_number, entry in enumerate(manifest["entries"]):
            if source_number and source_number % 150 == 0:
                print(f"{source_number} Quellen dekodiert", flush=True)
            if entry.get("missing"):
                continue
            raw = archive.read(entry["path"])
            if hashlib.sha256(raw).hexdigest() != entry["sha256"]:
                raise ValueError("Quell-Prüfsumme stimmt nicht: " + entry["path"])
            if not entry["path"].endswith(".pbf"):
                continue
            _, _, x, filename = entry["path"].split("/")
            x, y = int(x), int(filename.removesuffix(".pbf"))
            layer = mapbox_vector_tile.decode(raw).get("road", {})
            size = layer.get("extent", 4096)

            def transform(point):
                px, py = point
                return [(x + px / size) / 16384 * 360 - 180,
                        math.degrees(math.atan(math.sinh(math.pi * (1 - 2 * (y + 1 - py / size) / 16384))))]

            for feature in layer.get("features", []):
                tags = feature["properties"]
                if tags.get("highway") not in ROAD_TYPES:
                    continue
                geometry = feature["geometry"]
                if geometry["type"] not in ["LineString", "MultiLineString"]:
                    continue
                parts = [geometry["coordinates"]] if geometry["type"] == "LineString" else geometry["coordinates"]
                record = ways.setdefault(tags["id"], {"tags": tags, "parts": [], "newer": False})
                record["parts"].extend(LineString([transform(point) for point in part]) for part in parts if len(part) >= 2)
        newer = json.loads(archive.read("centre-osm.json"))
        centre_box = box(121.475, 25.005, 121.615, 25.105)
        new_ways = {"way/" + str(row["id"]): row for row in newer["elements"] if row.get("t", {}).get("highway") in ROAD_TYPES and len(row.get("p", [])) >= 2}
        newer_classes = {row["t"]["highway"] for row in new_ways.values()}
        for id, record in ways.items():
            # The newer extract omits service roads and several other classes.
            # Missing ways may only be retired for classes actually covered there.
            if id not in new_ways and record["tags"]["highway"] in newer_classes:
                record["parts"] = [line for part in record["parts"] for line in lines(part.difference(centre_box))]
        for id, row in new_ways.items():
            ways[id] = {"tags": row["t"], "parts": [LineString(row["p"])], "newer": True}
        for filename in ["postal-roads.csv", "postal-villages.csv"]:
            for row in csv.reader(io.StringIO(archive.read(filename).decode("utf-8-sig"))):
                if len(row) == 1 and "," in row[0]:
                    row = next(csv.reader([row[0]]))
                if len(row) >= 2 and row[0] and re.search("[A-Za-z]", row[1]):
                    postal[normalize(row[0])].add(row[1].strip().strip('"'))

    def english(name, tags):
        options = postal.get(normalize(name), set())
        if len(options) == 1:
            return next(iter(options)), "postal-exact"
        # Numbered lanes/alleys use postal address grammar and an attested base name.
        match = re.fullmatch(r"(.+?)([0-9]+)巷(?:([0-9]+)弄)?", normalize(name))
        if match and len(postal.get(match[1], set())) == 1:
            prefix = (f"Aly. {match[3]}, " if match[3] else "") + f"Ln. {match[2]}, "
            return prefix + next(iter(postal[match[1]])), "postal-numbered"
        match = re.fullmatch(r"(.+?)([0-9]+)弄", normalize(name))
        if match and len(postal.get(match[1], set())) == 1:
            return f"Aly. {match[2]}, " + next(iter(postal[match[1]])), "postal-numbered"
        if tags.get("name:en") and re.search("[A-Za-z]", tags["name:en"]):
            return tags["name:en"], "osm-name-en"
        return "", "missing"

    groups = defaultdict(list)
    background = []
    raw_counts = Counter()
    for id, record in ways.items():
        if not record["parts"]:
            continue
        merged = unary_union(record["parts"]).intersection(region)
        if not lines(merged):
            continue
        tags = record["tags"]
        name = tags.get("name:zh") or tags.get("name", "")
        raw_counts["ways"] += 1
        if not re.search(r"[\u3400-\u9fff]", name) or not re.search(r"[路街巷弄道橋]", name) or any(word in name for word in ["停車道", "機車專用道", "停車場", "未命名", ";"]):
            background.extend(canonical_geometry(merged)["coordinates"])
            raw_counts["unnamedOrGenericWays"] += 1
            continue
        for city, area in city_shapes.items():
            clipped = merged.intersection(area)
            if lines(clipped):
                groups[(city, normalize(name))].append((id, clipped, tags, record["newer"]))
    features = []
    for group_number, ((city, name_key), records) in enumerate(sorted(groups.items())):
        if group_number and group_number % 2500 == 0:
            print(f"{group_number} Namensgruppen verarbeitet", flush=True)
        name = Counter(row[2].get("name:zh") or row[2].get("name", name_key) for row in records).most_common(1)[0][0]
        geometry = unary_union([row[1] for row in records])
        # Nearby carriageways form one street; remote namesakes remain separate tasks.
        neighbourhood = unary_union([line.buffer(0.0007) for line in lines(geometry)])
        components = [neighbourhood] if neighbourhood.geom_type == "Polygon" else list(neighbourhood.geoms)
        components.sort(key=lambda item: item.bounds)
        for component_number, component in enumerate(components):
            components_records = [row for row in records if row[1].intersects(component)]
            actual = unary_union([row[1] for row in components_records])
            actual_lines = lines(actual)
            if not actual_lines:
                continue
            indices = district_index.query(actual, predicate="intersects")
            ids = sorted(district_features[int(index)]["id"] for index in indices if district_features[int(index)]["cityId"] == city)
            if not ids:
                continue
            anchor = max(actual_lines, key=lambda line: line.length).interpolate(0.5, normalized=True)
            tags = next((row[2] for row in components_records if row[2].get("name:en")), components_records[0][2])
            name_en, name_source = english(name, tags)
            highway = min((row[2]["highway"].removesuffix("_link") for row in components_records), key=lambda value: RANK.get(value, 10))
            category = "major" if highway in ["motorway", "trunk", "primary", "secondary"] else "secondary" if highway == "tertiary" else "local"
            unit = "alley" if re.search(r"[0-9一二三四五六七八九十]+弄", name) else "lane" if "巷" in name else "section" if re.search(r"[0-9一二三四五六七八九十]+段", name) else "street"
            identity = f"{city}|{normalize(name)}|{component_number}"
            features.append({"id": "street-" + hashlib.sha1(identity.encode()).hexdigest()[:16], "kind": "street", "cityId": city,
                             "districtIds": ids, "nameZh": name, "nameEn": name_en, "nameSource": name_source,
                             "category": category, "unit": unit, "highway": highway,
                             "anchor": [round(anchor.x, 6), round(anchor.y, 6)], "geometry": canonical_geometry(actual),
                             "description": "Straßenverlauf in " + ", ".join(next(f["nameEn"] for f in district_features if f["id"] == id) for id in ids) + ".",
                             "sourceDate": "2026-09-28 / 2021-12-17" if any(row[3] for row in components_records) else "2021-12-17"})
    features = merge_local_namesakes(features)
    by_district = []
    for district in district_features:
        local = [f for f in features if district["id"] in f["districtIds"]]
        by_district.append({"id": district["id"], "cityId": district["cityId"], "nameZh": district["nameZh"], "nameEn": district["nameEn"],
                            "streets": len(local), "withEnglish": sum(bool(f["nameEn"]) for f in local),
                            "units": dict(Counter(f["unit"] for f in local))})
    coverage = {"streetUnits": len(features), "byCity": dict(Counter(f["cityId"] for f in features)),
                "byCategory": dict(Counter(f["category"] for f in features)), "byUnit": dict(Counter(f["unit"] for f in features)),
                "names": dict(Counter(f["nameSource"] for f in features)), "districts": by_district,
                "raw": dict(raw_counts), "missingTiles": [entry["path"] for entry in manifest["entries"] if entry.get("missing")],
                "currentOfficialCompletenessVerified": False}
    output = {"version": 1, "features": features, "background": background, "coverage": coverage,
              "source": {"copyright": "© OpenStreetMap contributors", "license": "ODbL-1.0", "tileCommit": manifest["tileCommit"],
                         "baseDate": "2021-12-17", "centreDate": "2026-09-28", "newerHighwayClasses": sorted(newer_classes),
                         "olderClassesPreserved": sorted(ROAD_TYPES - newer_classes), "postalCommit": manifest["postalCommit"]}}
    (ROOT / "data/streets.js").write_text("window.TAIPEI_STREETS = " + json.dumps(output, ensure_ascii=False, separators=(",", ":")) + ";\n", encoding="utf-8")
    (ROOT / "data/street-coverage.json").write_text(json.dumps(coverage, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({key: value for key, value in coverage.items() if key not in ["districts", "missingTiles"]}, ensure_ascii=False), flush=True)
    print("Unversorgte Bezirke:", [row["nameZh"] for row in by_district if not row["streets"]], flush=True)
    subprocess.run([sys.executable, str(ROOT / "tools/build_street_parents.py")], check=True)


if __name__ == "__main__":
    main()
