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
    def test_pending_layers_are_explicit_or_have_real_data(self):
        if self.data['complete']:
            self.assertTrue(any(f['nameZh']=='Rhein' for f in self.data['rivers']['features']))
            self.assertTrue(any('Düssel' in f['nameZh'] for f in self.data['rivers']['features']))
            self.assertGreaterEqual(len(self.data['metro']['lines']),8)
            self.assertTrue((SOURCE/'overpass-manifest.json').exists())
        else:
            self.assertFalse(self.data['rivers']['features']);self.assertFalse(self.data['metro']['features'])
