"""Prepare the documented local OSM Metro data for the two-city region."""

import argparse
import hashlib
import json
from pathlib import Path


EXTRA = {
    "A": ("機場捷運", "Airport MRT", "#8246AF", "d1a9ce38d96954fb906490355167a4ccedbf2a3757de6bebe1c158f6d02451dc"),
    "V": ("淡海輕軌", "Danhai LRT", "#FEBEB5", "4c0bbd0a38b5a4ff10e38720e8f69cbc0ad0e1a54035d4abc8aaa57401277b53"),
    "K": ("安坑輕軌", "Ankeng LRT", "#c3b091", "b12cd19c2c634c1eeee29e1ba151c54855bcb71747e3452917aac2e2f0b8456f"),
    "LB": ("三鶯線", "Sanying", "#6DB7D0", "bbece03cb63dd1f79aa1254f0b09460cd4b95d1743a18a1ec5eea2dffb80ff03")
}
COMMIT = "aaaa1d71ce30ebb4371c13ed83f6e199a2e8cfcd"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--research", type=Path, required=True)
    args = parser.parse_args()
    data_dir = Path(__file__).resolve().parents[1] / "data"
    existing = json.loads((data_dir / "metro.js").read_text().removeprefix("window.TAIPEI_METRO = ").strip().removesuffix(";"))
    original_bytes = (data_dir / "metro-routes-source.geojson").read_bytes()
    if hashlib.sha256(original_bytes).hexdigest() != existing["source"]["sourceSha256"]:
        raise ValueError("Prüfsumme des ursprünglichen Metro-Datensatzes stimmt nicht")
    original = json.loads(original_bytes)
    network = json.loads((args.research / "pinned-network.txt").read_text())
    metadata = {line["id"]: line for line in network["lines"]}
    lines = []
    for code in ["BR", "R", "G", "O", "BL", "Y"]:
        line = metadata[code]
        lines.append({"id": code, "code": code, "nameZh": line["name"]["zh"], "nameEn": line["name"]["en"].removesuffix(" Line"), "color": line["color"]})
    features = original["features"][:]
    additional = []
    archive = data_dir / "metro-extra-source"
    archive.mkdir(exist_ok=True)
    for code, (name_zh, name_en, color, expected_hash) in EXTRA.items():
        raw = (args.research / f"{code}-extra.json").read_bytes()
        if hashlib.sha256(raw).hexdigest() != expected_hash:
            raise ValueError(f"Prüfsumme der Zusatzquelle {code} stimmt nicht")
        source = json.loads(raw)
        segments, seen = [], set()
        for relation in source["elements"]:
            if relation.get("tags", {}).get("type") != "route":
                continue
            for member in relation.get("members", []):
                if member["type"] != "way" or member.get("role", "") not in ["", "forward", "backward"] or member["ref"] in seen:
                    continue
                geometry = member.get("geometry", [])
                if len(geometry) < 2:
                    continue
                coordinates = [[point["lon"], point["lat"]] for point in geometry]
                if not all(120 < point[0] < 123 and 24 < point[1] < 26 for point in coordinates):
                    raise ValueError(f"Unerwartete Koordinaten für {code}")
                segments.append(coordinates)
                seen.add(member["ref"])
        if not segments:
            raise ValueError(f"Keine geografischen Strecken für {code}")
        features.append({"type": "Feature", "properties": {"line": code, "relation": source["elements"][0]["id"]}, "geometry": {"type": "MultiLineString", "coordinates": segments}})
        lines.append({"id": code, "code": code, "nameZh": name_zh, "nameEn": name_en, "color": color})
        (archive / f"{code}.json").write_bytes(raw)
        additional.append({"line": code, "sourceSha256": expected_hash, "commit": COMMIT,
                           "url": f"https://github.com/rareone0602/taipei-mrt-minecraft/blob/{COMMIT}/data/lines/{code}.json",
                           "osmTimestamp": source["osm3s"]["timestamp_osm_base"], "license": "ODbL-1.0"})
    for code, display_code in [("RA", "R22A"), ("GA", "G03A")]:
        line = metadata[code]
        lines.append({"id": code, "code": display_code, "nameZh": line["name"]["zh"], "nameEn": line["name"]["en"], "color": line["color"]})
    existing.update({"version": 2, "scope": "Taipei City + New Taipei City; display clipped to the regional district boundaries",
                     "lines": lines, "features": features, "additionalSources": additional})
    (data_dir / "metro.js").write_text("window.TAIPEI_METRO = " + json.dumps(existing, ensure_ascii=False, separators=(",", ":")) + ";\n")
    print(f"Gespeichert: {len(lines)} Linienkennungen, {len(features)} geografische Routen; unverknüpfte Teilstücke bleiben getrennt.")


if __name__ == "__main__":
    main()
