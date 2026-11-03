"""Collect pinned public OSM street sources for the two-city region.

Development dependency: shapely. Network is only needed for this build step.
The browser never calls this script or an external map service.
"""

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import hashlib
import json
import math
from pathlib import Path
import urllib.error
import urllib.request
from zipfile import ZipFile, ZIP_DEFLATED

from shapely.geometry import box, shape
from shapely.ops import unary_union


ROOT = Path(__file__).resolve().parents[1]
TILE_COMMIT = "c3d387948e48adc38440062b33a19e1aca1b8b36"
CENTRE_COMMIT = "96af2cbce0b40dd6120d2719ec7ee3b6027d94f3"
POST_COMMIT = "2a5923e5de751e24586901082a7df80653e7a96e"


def tile_position(lon, lat):
    return int((lon + 180) / 360 * 16384), int((1 - math.asinh(math.tan(math.radians(lat))) / math.pi) / 2 * 16384)


def tile_corner(x, y):
    return x / 16384 * 360 - 180, math.degrees(math.atan(math.sinh(math.pi * (1 - 2 * y / 16384))))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cache", type=Path, required=True)
    parser.add_argument("--workers", type=int, default=10)
    args = parser.parse_args()
    args.cache.mkdir(parents=True, exist_ok=True)
    districts = json.loads((ROOT / "data/districts.js").read_text().split("=", 1)[1].strip().removesuffix(";"))
    region = unary_union([shape(feature["geometry"]) for feature in districts["features"]])
    west, south, east, north = region.bounds
    x0, y0 = tile_position(west, north)
    x1, y1 = tile_position(east, south)
    jobs = []
    for x in range(x0, x1 + 1):
        for y in range(y0, y1 + 1):
            left, top = tile_corner(x, y)
            right, bottom = tile_corner(x + 1, y + 1)
            if region.intersects(box(left, bottom, right, top)):
                jobs.append((f"tiles/14/{x}/{y}.pbf", f"https://raw.githubusercontent.com/typebrook/mapstew/{TILE_COMMIT}/tiles/14/{x}/{y}.pbf"))
    jobs += [
        ("centre-osm.json", f"https://raw.githubusercontent.com/jpchen/taipei-3d-render/{CENTRE_COMMIT}/assets/map-source.json"),
        ("postal-roads.csv", f"https://raw.githubusercontent.com/sean1093/menpai/{POST_COMMIT}/data/source/roads.csv"),
        ("postal-villages.csv", f"https://raw.githubusercontent.com/sean1093/menpai/{POST_COMMIT}/data/source/villages.csv"),
    ]
    print(f"Prüfe {len(jobs) - 3} Kacheln und drei ergänzende Quellen", flush=True)

    def fetch(job):
        path, url = job
        local = args.cache / path
        local.parent.mkdir(parents=True, exist_ok=True)
        if local.exists():
            raw = local.read_bytes()
        else:
            try:
                with urllib.request.urlopen(url, timeout=40) as response:
                    raw = response.read()
            except urllib.error.HTTPError as error:
                if error.code == 404 and path.endswith(".pbf"):
                    return {"path": path, "url": url, "missing": True}
                raise
            local.write_bytes(raw)
        return {"path": path, "url": url, "bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest()}

    entries = []
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = [pool.submit(fetch, job) for job in jobs]
        for future in as_completed(futures):
            entries.append(future.result())
            if len(entries) % 100 == 0:
                print(f"{len(entries)}/{len(jobs)} geprüft", flush=True)
    manifest = {"tileCommit": TILE_COMMIT, "tileCommitDate": "2021-12-17", "centreCommit": CENTRE_COMMIT,
                "centreOsmDate": "2026-09-28T05:27:05Z", "postalCommit": POST_COMMIT,
                "entries": sorted(entries, key=lambda row: row["path"])}
    target = ROOT / "data/street-sources.zip"
    with ZipFile(target, "w", ZIP_DEFLATED) as archive:
        for entry in manifest["entries"]:
            if not entry.get("missing"):
                archive.write(args.cache / entry["path"], entry["path"])
        archive.writestr("manifest.json", json.dumps(manifest, ensure_ascii=False, indent=2))
    (ROOT / "data/street-source-manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Gesichert: {target.stat().st_size} Bytes; {sum(bool(row.get('missing')) for row in entries)} fehlende Randkacheln", flush=True)


if __name__ == "__main__":
    main()
