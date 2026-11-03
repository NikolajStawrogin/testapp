"""Derive whole-road learning units from documented Section geometries.

Development dependency: shapely. Run after build_street_data.py.
"""

from collections import defaultdict
import csv
import hashlib
import io
import json
from pathlib import Path
import re
import unicodedata
from zipfile import ZipFile

from shapely.geometry import shape
from shapely.ops import unary_union


ROOT = Path(__file__).resolve().parents[1]


def normalize(value):
    return unicodedata.normalize("NFKC", value).replace("臺", "台").replace(" ", "")


def lines(geometry):
    if geometry.geom_type == "LineString":
        return [geometry]
    if hasattr(geometry, "geoms"):
        return [line for part in geometry.geoms for line in lines(part)]
    return []


def main():
    raw = (ROOT / "data/streets.js").read_bytes()
    source = json.loads(raw.decode().split("=", 1)[1].strip().removesuffix(";"))
    groups = defaultdict(list)
    existing = defaultdict(list)
    for feature in source["features"]:
        if feature["unit"] == "section":
            match = re.fullmatch(r"(.+?)[一二三四五六七八九十百0-9０-９]+段", feature["nameZh"])
            if match:
                groups[(feature["cityId"], normalize(match[1]))].append((feature, match[1]))
        elif feature["unit"] == "street":
            existing[(feature["cityId"], normalize(feature["nameZh"]))].append(feature)
    postal = defaultdict(set)
    with ZipFile(ROOT / "data/street-sources.zip") as archive:
        for row in csv.reader(io.StringIO(archive.read("postal-roads.csv").decode("utf-8-sig"))):
            if len(row) >= 2:
                postal[normalize(row[0])].add(row[1].strip())
    parents, replaced, aliases = [], set(), {}
    for (city, key), rows in sorted(groups.items()):
        children = [row[0] for row in rows]
        geometries = [shape(child["geometry"]) for child in children]
        roots = list(range(len(children)))

        def root(index):
            while roots[index] != index:
                roots[index] = roots[roots[index]]
                index = roots[index]
            return index

        for first in range(len(children)):
            for second in range(first):
                if set(children[first]["districtIds"]) & set(children[second]["districtIds"]) or geometries[first].distance(geometries[second]) <= 0.0008:
                    roots[root(first)] = root(second)
        components = defaultdict(list)
        for index, child in enumerate(children):
            components[root(index)].append(child)
        for members in components.values():
            district_ids = {district for child in members for district in child["districtIds"]}
            natives = [feature for feature in existing[(city, key)] if district_ids & set(feature["districtIds"])]
            # A native whole-road piece may connect previously separate Section groups.
            # Only one parent is emitted for an existing whole-road identity.
            if any(feature["id"] in replaced for feature in natives):
                previous = next(parent for parent in parents if set(parent.get("nativeIds", [])) & {feature["id"] for feature in natives})
                previous["children"] = sorted(set(previous["children"]) | {child["id"] for child in members})
                previous["districtIds"] = sorted(set(previous["districtIds"]) | district_ids)
                previous["geometry"]["coordinates"].extend(part for child in members for part in child["geometry"]["coordinates"])
                continue
            geometry = unary_union([shape(feature["geometry"]) for feature in members + natives])
            parts = lines(geometry)
            anchor = max(parts, key=lambda line: line.length).interpolate(0.5, normalized=True)
            name = next(base for child, base in rows if child["id"] == members[0]["id"])
            options = postal.get(key, set())
            name_en, name_source = "", "missing"
            if len(options) == 1:
                name_en, name_source = next(iter(options)), "postal-exact"
            else:
                attested = {re.sub(r"^Sec\.\s*\d+,\s*", "", child["nameEn"]) for child in members
                            if child["nameSource"] == "postal-exact" and re.match(r"^Sec\.\s*\d+,\s*", child["nameEn"])}
                if len(attested) == 1:
                    name_en, name_source = next(iter(attested)), "postal-parent"
            district_ids |= {district for feature in natives for district in feature["districtIds"]}
            id = min(feature["id"] for feature in natives) if natives else "street-whole-" + hashlib.sha1((city + "|" + key + "|" + ",".join(sorted(district_ids))).encode()).hexdigest()[:16]
            category = min((feature["category"] for feature in members + natives), key={"major": 0, "secondary": 1, "local": 2}.get)
            parents.append({"id": id, "kind": "street", "cityId": city, "districtIds": sorted(district_ids), "nameZh": name,
                            "nameEn": name_en, "nameSource": name_source, "unit": "street", "category": category,
                            "highway": members[0]["highway"], "anchor": [round(anchor.x, 6), round(anchor.y, 6)],
                            "geometry": {"type": "MultiLineString", "coordinates": [[[round(x, 6), round(y, 6)] for x, y in part.coords] for part in parts]},
                            "children": sorted(child["id"] for child in members), "nativeIds": sorted(feature["id"] for feature in natives),
                            "description": "Ganze Straße einschließlich der zugehörigen benannten Sections. Einzelne Sections bleiben zusätzlich als eigene Lernaufgaben wählbar.",
                            "sourceDate": "Aus den dokumentierten Section-Geometrien abgeleitet"})
            for feature in natives:
                replaced.add(feature["id"])
                if feature["id"] != id:
                    aliases[feature["id"]] = id
    output = {"version": 1, "sourceStreetSha256": hashlib.sha256(raw).hexdigest(), "features": parents,
              "replacedIds": sorted(replaced), "aliases": aliases,
              "coverage": {"wholeRoads": len(parents), "withEnglish": sum(bool(parent["nameEn"]) for parent in parents),
                           "learningUnits": len(source["features"]) - len(replaced) + len(parents)},
              "source": "Whole-road units derived from the documented Section geometries. Exact base-name matches or attested postal Section names with their numeric Section prefix removed; no generated Pinyin."}
    (ROOT / "data/street-parents.js").write_text("window.TAIPEI_STREET_PARENTS = " + json.dumps(output, ensure_ascii=False, separators=(",", ":")) + ";\n", encoding="utf-8")
    print(output["coverage"])


if __name__ == "__main__":
    main()
