"""Build the local 41-district dataset from the documented reference files."""

import argparse
import hashlib
import json
from pathlib import Path
import re
import xml.etree.ElementTree as ET


def in_ring(x, y, ring):
    inside = False
    for a, b in zip(ring, ring[1:] + ring[:1]):
        if (a[1] > y) != (b[1] > y) and x < (b[0] - a[0]) * (y - a[1]) / (b[1] - a[1]) + a[0]:
            inside = not inside
    return inside


def inside(point, rings):
    return sum(in_ring(*point, ring) for ring in rings) % 2 == 1


def distance_squared(x, y, a, b):
    dx, dy = b[0] - a[0], b[1] - a[1]
    t = max(0, min(1, ((x - a[0]) * dx + (y - a[1]) * dy) / (dx * dx + dy * dy))) if dx or dy else 0
    return (x - a[0] - t * dx) ** 2 + (y - a[1] - t * dy) ** 2


def polygon_area(rings):
    ring = rings[0]
    return abs(sum(a[0] * b[1] - b[0] * a[1] for a, b in zip(ring, ring[1:] + ring[:1])))


def label_point(geometry):
    polygons = geometry["coordinates"] if geometry["type"] == "MultiPolygon" else [geometry["coordinates"]]
    rings = max(polygons, key=polygon_area)
    edges = [(a, b) for ring in rings for a, b in zip(ring, ring[1:] + ring[:1])]
    xs, ys = [p[0] for p in rings[0]], [p[1] for p in rings[0]]
    low_x, high_x, low_y, high_y = min(xs), max(xs), min(ys), max(ys)
    best, score = None, -1
    for divisions in [12, 6, 6, 6]:
        step_x, step_y = (high_x - low_x) / divisions, (high_y - low_y) / divisions
        for i in range(divisions + 1):
            for j in range(divisions + 1):
                point = [low_x + i * step_x, low_y + j * step_y]
                if not inside(point, rings):
                    continue
                candidate = min(distance_squared(*point, a, b) for a, b in edges)
                if candidate > score:
                    best, score = point, candidate
        if best is None:
            raise ValueError("Kein Beschriftungspunkt innerhalb der Fläche gefunden")
        low_x, high_x = best[0] - step_x, best[0] + step_x
        low_y, high_y = best[1] - step_y, best[1] + step_y
    result = [round(number, 6) for number in best]
    if not inside(result, rings):
        raise ValueError("Gerundeter Beschriftungspunkt außerhalb der Fläche")
    return result


def rounded(coordinates):
    if isinstance(coordinates[0], (float, int)):
        return [round(number, 6) for number in coordinates]
    return [rounded(child) for child in coordinates]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--boundaries", type=Path, required=True)
    parser.add_argument("--names", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=Path(__file__).resolve().parents[1] / "data" / "districts.js")
    args = parser.parse_args()
    previous = json.loads(args.output.read_text().removeprefix("window.TAIPEI_DATA = ").strip().removesuffix(";"))
    source_bytes = args.boundaries.read_bytes()
    if hashlib.sha256(source_bytes).hexdigest() != previous["source"]["sourceSha256"]:
        raise ValueError("Die Bezirksquelle stimmt nicht mit der dokumentierten Prüfsumme überein")
    names_bytes = args.names.read_bytes()
    if hashlib.sha256(names_bytes).hexdigest() != "24acfe52023f0ddc2149a2f8368910cd0968584913f3ac17678abb3048cba1b9":
        raise ValueError("Die Namensdatei stimmt nicht mit der dokumentierten Prüfsumme überein")
    names = [{child.tag: child.text for child in element} for element in ET.fromstring(names_bytes)]
    boundaries = json.loads(source_bytes)["features"]
    taipei = [feature for feature in previous["features"] if feature.get("cityId", "taipei") == "taipei"]
    if len(taipei) != 12:
        raise ValueError("Die zwölf vorhandenen Taipei-Identitäten müssen erhalten bleiben")
    for feature in taipei:
        feature["cityId"] = "taipei"
    new_taipei = []
    for row in names:
        if not row["欄位2"].startswith("新北市"):
            continue
        name_zh = row["欄位2"].removeprefix("新北市")
        name_en = row["欄位3"].removesuffix(", New Taipei City")
        matches = [f for f in boundaries if f["properties"].get("COUNTYNAME") == "新北市" and f["properties"].get("TOWNNAME") == name_zh]
        if len(matches) != 1:
            raise ValueError(f"Keine eindeutige Fläche für {name_zh}")
        geometry = matches[0]["geometry"]
        geometry["coordinates"] = rounded(geometry["coordinates"])
        slug = re.sub(r"[^a-z0-9]+", "-", name_en.removesuffix(" Dist.").lower()).strip("-")
        new_taipei.append({
            "id": "nt-" + slug, "cityId": "new-taipei", "nameZh": name_zh, "nameEn": name_en,
            "description": "Ein Bezirk von New Taipei City. Die markierte Fläche zeigt seine Lage in der Region.",
            "anchor": label_point(geometry), "geometry": geometry
        })
    if len(new_taipei) != 29 or len({f["id"] for f in taipei + new_taipei}) != 41:
        raise ValueError("Erwartet werden 12 + 29 eindeutig identifizierte Bezirke")
    previous.update({
        "version": 2, "scope": "Taipei City + New Taipei City",
        "cities": [
            {"id": "taipei", "nameZh": "臺北市", "nameEn": "Taipei City"},
            {"id": "new-taipei", "nameZh": "新北市", "nameEn": "New Taipei City"}
        ],
        "nameSource": {
            "edition": "109/06", "sourceSha256": hashlib.sha256(names_bytes).hexdigest(),
            "url": "https://github.com/sean1093/menpai/blob/2a5923e5de751e24586901082a7df80653e7a96e/data/source/county.xml",
            "note": "Öffentliche Kopie des Postverzeichnisses; aktueller Primärabgleich steht aus."
        },
        "features": taipei + new_taipei
    })
    args.output.write_text("window.TAIPEI_DATA = " + json.dumps(previous, ensure_ascii=False, separators=(",", ":")) + ";\n")
    print(f"Gespeichert: {len(taipei)} + {len(new_taipei)} Bezirke, {args.output.stat().st_size} Bytes")


if __name__ == "__main__":
    main()
