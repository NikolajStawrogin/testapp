"""Reproducible source copies, actual coverage and administrative hierarchy."""
from pathlib import Path
from zipfile import ZipFile
import hashlib
import json
import unittest
ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'data/duesseldorf'

class DuesseldorfDataTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        text=(ROOT/'data/duesseldorf.js').read_text();cls.data=json.loads(text.split('=',1)[1].strip().removesuffix(';'))
    def test_50_neighborhoods_and_10_boroughs_with_unique_ids(self):
        fs=self.data['districts']['features'];self.assertEqual(len(fs),60)
        self.assertEqual(sum(f['level']=='neighborhood' for f in fs),50)
        self.assertEqual(sum(f['level']=='borough' for f in fs),10)
        self.assertEqual(len({f['id'] for f in fs}),60)
        self.assertTrue({'Bilk','Altstadt','Knittkuhl','Garath'}.issubset({f['nameZh'] for f in fs}))
        for f in fs:
            self.assertTrue(f['geometry']['coordinates']);self.assertTrue(6.6<f['anchor'][0]<7.1);self.assertTrue(51<f['anchor'][1]<51.5)
    def test_every_neighborhood_has_streets_and_cross_boundary_roads_are_available(self):
        fs=self.data['streets']['features'];self.assertGreater(len(fs),2000)
        ids={f['id'] for f in self.data['districts']['features']}
        for f in fs:
            self.assertTrue(set(f['districtIds']).issubset(ids));self.assertTrue(f['geometry']['coordinates'])
            self.assertEqual(f['unit'],'street');self.assertEqual(f['nameEn'],'')
        self.assertTrue(all(self.data['coverage'].values()))
        ko=next(f for f in fs if f['nameZh']=='Königsallee')
        self.assertTrue({'dd-stadtmitte','dd-friedrichstadt','dd-bezirk-1','dd-bezirk-3'}.issubset(ko['districtIds']))
    def test_source_hashes_match_pinned_manifests(self):
        m=json.loads((SOURCE/'source-manifest.json').read_text())
        self.assertEqual(hashlib.sha256((SOURCE/'neighborhoods-source.geojson').read_bytes()).hexdigest(),m['neighborhoods']['sha256'])
        with ZipFile(SOURCE/'street-sources.zip') as z:
            self.assertIsNone(z.testzip())
            for row in m['streets']:self.assertEqual(hashlib.sha256(z.read(row['file'])).hexdigest(),row['sha256'])
    def test_unknown_street_classes_are_not_fabricated(self):
        if not (SOURCE/'streets-normalized.json').exists():
            self.assertEqual({f['category'] for f in self.data['streets']['features']},{'unclassified'})
        self.assertIn('amtlich',self.data['note'])
    def test_water_and_transit_layers_have_archived_sources(self):
        import gzip
        self.assertTrue(self.data['complete'])
        self.assertEqual({r['nameZh'] for r in self.data['rivers']['features']},{'Rhein','Düssel','Nördliche Düssel','Südliche Düssel','Itter','Kittelbach'})
        for river in self.data['rivers']['features']:
            self.assertTrue(river['cityIds']);self.assertTrue(river['sourceIds']);self.assertGreaterEqual(river['lengthMeters'],400)
            self.assertIn(river['geometry']['type'],['Polygon','MultiPolygon'])
        manifest=json.loads((SOURCE/'layers-source-manifest.json').read_text())
        for row in manifest['sources']:
            raw=(SOURCE/row['file']).read_bytes()
            self.assertEqual(hashlib.sha256(raw).hexdigest(),row['sha256'])
            if row.get('uncompressedSha256'):self.assertEqual(hashlib.sha256(gzip.decompress(raw)).hexdigest(),row['uncompressedSha256'])
    def test_transit_groups_and_schematic_links_match_source_stops(self):
        from collections import Counter
        metro=self.data['metro'];lines=metro['lines']
        self.assertEqual(Counter(line['kind'] for line in lines),{'metro':12,'suburban':6,'tram':7,'other':1})
        self.assertEqual(len({l['id'] for l in lines}),26)
        self.assertEqual(metro['geometryModel'],'gtfs-stop-links')
        self.assertTrue({'S1','S6','S8','S11','S28','S68','701','U79'}.issubset({l['id'] for l in lines}))
        stops=json.loads((SOURCE/'transit-stops-source.json').read_text())['stops']
        coords={(round(s['lon'],7),round(s['lat'],7)) for s in stops}
        ids={s['id'] for s in stops}
        for line in lines:
            self.assertTrue(set(line['stopIds']).issubset(ids));self.assertTrue(line['sourceRouteIds'])
        # Every rendered link has two endpoints; at least one is a real stop,
        # except very short pieces clipped from links at the city boundary.
        real=0;total=0
        for feature in metro['features']:
            for link in feature['geometry']['coordinates']:
                self.assertEqual(len(link),2)
                total+=1;real+=int(any(tuple(point) in coords for point in link))
        self.assertGreater(real/total,.95)
