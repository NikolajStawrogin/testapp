"""Data integrity checks; uses only Python's standard library."""

from collections import Counter
import hashlib
import json
import math
from pathlib import Path
import unittest
from zipfile import ZipFile


ROOT = Path(__file__).resolve().parents[1]


class StreetDataTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads((ROOT / "data/streets.js").read_text().split("=", 1)[1].strip().removesuffix(";"))
        cls.features = cls.data["features"]

    def test_every_district_and_required_street_type_is_represented(self):
        coverage = self.data["coverage"]
        self.assertEqual(len(coverage["districts"]), 41)
        self.assertTrue(all(row["streets"] > 0 and row["withEnglish"] > 0 for row in coverage["districts"]))
        self.assertEqual(set(coverage["byCity"]), {"taipei", "new-taipei"})
        self.assertEqual(set(coverage["byUnit"]), {"street", "section", "lane", "alley"})
        self.assertEqual(sum(coverage["byUnit"].values()), len(self.features))
        self.assertFalse(coverage["currentOfficialCompletenessVerified"])

    def test_ids_geometry_and_anchors_are_valid(self):
        ids = [feature["id"] for feature in self.features]
        self.assertEqual(len(ids), len(set(ids)))
        for feature in self.features:
            self.assertTrue(feature["nameZh"])
            self.assertTrue(feature["districtIds"])
            self.assertEqual(feature["geometry"]["type"], "MultiLineString")
            self.assertTrue(feature["geometry"]["coordinates"])
            closest = math.inf
            px, py = feature["anchor"]
            for part in feature["geometry"]["coordinates"]:
                self.assertGreaterEqual(len(part), 2)
                for x, y in part:
                    self.assertTrue(121.2 < x < 122.1 and 24.6 < y < 25.4)
                for (ax, ay), (bx, by) in zip(part, part[1:]):
                    dx, dy = bx - ax, by - ay
                    t = max(0, min(1, ((px - ax) * dx + (py - ay) * dy) / (dx * dx + dy * dy))) if dx or dy else 0
                    closest = min(closest, math.hypot(px - ax - t * dx, py - ay - t * dy))
            self.assertLess(closest, 0.00002, feature["id"])

    def test_english_provenance_and_known_names(self):
        for feature in self.features:
            self.assertEqual(bool(feature["nameEn"]), feature["nameSource"] != "missing")
        self.assertTrue(any(f["nameZh"] == "忠孝東路四段" and "Zhongxiao" in f["nameEn"] for f in self.features))
        self.assertTrue(any(f["nameZh"] == "羅斯福路一段" and "Roosevelt" in f["nameEn"] for f in self.features))
        self.assertTrue(any(f["unit"] == "alley" and f["nameSource"] == "postal-numbered" and "Aly." in f["nameEn"] for f in self.features))
        self.assertEqual(Counter(f["nameSource"] for f in self.features), self.data["coverage"]["names"])

    def test_all_archived_sources_match_the_manifest(self):
        with ZipFile(ROOT / "data/street-sources.zip") as archive:
            manifest = json.loads(archive.read("manifest.json"))
            self.assertGreater(len(manifest["entries"]), 500)
            for entry in manifest["entries"]:
                self.assertFalse(entry.get("missing"), entry["path"])
                self.assertEqual(hashlib.sha256(archive.read(entry["path"])).hexdigest(), entry["sha256"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
