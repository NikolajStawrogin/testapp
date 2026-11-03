"""Build local Düsseldorf regions and streets from pinned OSM source copies.

Development dependency: shapely==2.1.2. The generated app has no Python dependency.
Additional water and transit inputs use normalized GeoJSON in the source directory.
"""
from collections import defaultdict, Counter
from pathlib import Path
from zipfile import ZipFile
import hashlib
import json
import re
import unicodedata
from shapely.geometry import shape, mapping
from shapely.ops import unary_union
from shapely import make_valid
from shapely.strtree import STRtree

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'data/duesseldorf'
BOROUGHS = {
1: ['Altstadt','Carlstadt','Stadtmitte','Pempelfort','Derendorf','Golzheim'],
2: ['Flingern Nord','Flingern Süd','Düsseltal'],
3: ['Friedrichstadt','Unterbilk','Hafen','Hamm','Volmerswerth','Bilk','Oberbilk','Flehe'],
4: ['Oberkassel','Heerdt','Lörick','Niederkassel'],
5: ['Stockum','Lohausen','Kaiserswerth','Wittlaer','Angermund','Kalkum'],
6: ['Lichtenbroich','Unterrath','Rath','Mörsenbroich'],
7: ['Gerresheim','Grafenberg','Ludenberg','Hubbelrath','Knittkuhl'],
8: ['Lierenfeld','Eller','Vennhausen','Unterbach'],
9: ['Wersten','Holthausen','Reisholz','Benrath','Urdenbach','Itter','Himmelgeist','Hassels'],
10: ['Garath','Hellerhof']}

def slug(value):
    value=value.replace('ß','ss').replace('ö','oe').replace('ü','ue').replace('ä','ae')
    return re.sub(r'[^a-z0-9]+','-',unicodedata.normalize('NFKD',value.lower()).encode('ascii','ignore').decode()).strip('-')

def rounded(value):
    if isinstance(value,(list,tuple)): return [rounded(v) for v in value]
    if isinstance(value,float): return round(value,7)
    return value

def geometry(g):
    m=mapping(g);return {'type':m['type'],'coordinates':rounded(m['coordinates'])}

def lines(g):
    if g.geom_type=='LineString': return [g] if g.length>0.000005 else []
    return [line for part in getattr(g,'geoms',[]) for line in lines(part)]

def main():
    raw=json.loads((SOURCE/'neighborhoods-source.geojson').read_text())
    assign={name:n for n,names in BOROUGHS.items() for name in names}
    assert {f['properties']['name'] for f in raw['features']}==set(assign)
    neighborhoods=[];polygons=[]
    for f in sorted(raw['features'],key=lambda f:(assign[f['properties']['name']],f['properties']['name'])):
        name=f['properties']['name'];n=assign[name];g=make_valid(shape(f['geometry']));p=g.representative_point()
        neighborhoods.append({'id':'dd-'+slug(name),'nameZh':name,'nameEn':'','level':'neighborhood','cityId':f'dd-b{n}', 'description':f'Stadtteil im Stadtbezirk {n} von Düsseldorf.','anchor':[round(p.x,7),round(p.y,7)],'geometry':geometry(g)})
        polygons.append(g)
    area=unary_union(polygons);features=list(neighborhoods)
    for n in BOROUGHS:
        g=unary_union([polygons[i] for i,f in enumerate(neighborhoods) if f['cityId']==f'dd-b{n}']);p=g.representative_point()
        features.append({'id':f'dd-bezirk-{n}','cityId':f'dd-b{n}','nameZh':f'Stadtbezirk {n}','nameEn':'','level':'borough','description':'Zugehörige Stadtteile: '+', '.join(BOROUGHS[n])+'.','anchor':[round(p.x,7),round(p.y,7)],'geometry':geometry(g)})
    tree=STRtree(polygons);named=defaultdict(list);background=[];seen=set();original_ids=defaultdict(set);classes=defaultdict(set)
    modern=SOURCE/'streets-normalized.json'
    if modern.exists():
        raw_features=json.loads(modern.read_text())['features']
    else:
        with ZipFile(SOURCE/'street-sources.zip') as z:
            raw_features=[f for name in sorted(z.namelist()) for f in json.loads(z.read(name))['features']]
    for f in raw_features:
        oid=str(f.get('id') or f['properties']['id'])
        if oid in seen:continue
        seen.add(oid)
        g=shape(f['geometry'])
        if not g.intersects(area):continue
        parts=lines(g.intersection(area))
        label=f['properties'].get('name','').strip()
        if not label:
            background.extend(rounded(list(line.simplify(.000006).coords)) for line in parts);continue
        named[label].extend(parts);original_ids[label].add(oid)
        if f['properties'].get('highway'):classes[label].add(f['properties']['highway'].removesuffix('_link'))
    streets=[]
    for name,parts in sorted(named.items()):
        if not parts:continue
        g=unary_union(parts);indices=sorted({int(i) for i in tree.query(g,predicate='intersects') if g.intersection(polygons[int(i)]).length>.00001})
        if not indices:continue
        district_ids=[neighborhoods[i]['id'] for i in indices];city_ids=sorted({neighborhoods[i]['cityId'] for i in indices})
        district_ids += [f'dd-bezirk-{int(cid[4:])}' for cid in city_ids]
        ls=lines(g);anchor=max(ls,key=lambda line:line.length).interpolate(.5,normalized=True)
        identity=hashlib.sha256(name.encode()).hexdigest()[:16]
        streets.append({'id':'dd-street-'+identity,'kind':'street','nameZh':name,'nameEn':'','unit':'street','category':('major' if classes[name]&{'motorway','trunk','primary'} else 'secondary' if classes[name]&{'secondary','tertiary'} else 'local' if classes[name] else 'unclassified'),'cityId':city_ids[0],'cityIds':city_ids,'districtIds':district_ids,'description':'Benannter OSM-Verlauf in Düsseldorf.'+(' Straßenklasse im Quellauszug nicht enthalten.' if not classes[name] else ''),'anchor':[round(anchor.x,7),round(anchor.y,7)],'sourceIds':sorted(original_ids[name]),'geometry':{'type':'MultiLineString','coordinates':[rounded(list(line.simplify(.000004).coords)) for line in ls]}})
    coverage={f['id']:sum(f['id'] in s['districtIds'] for s in streets) for f in neighborhoods}
    assert len(neighborhoods)==50 and len(features)==60 and all(coverage.values()),coverage
    sources=[{'name':'Stadtteile und Stadtbezirke','url':'https://github.com/codeforgermany/click_that_hood/tree/48ba05ad4c6969e3b3c25735492169227ae411f1/public/data','note':'50 OSM-Stadtteilflächen aus Click That ’Hood, Metadaten verweisen auf OpenStreetMap; im Auszug Zeitstempel Juni 2015. Stadtbezirke sind Vereinigungen der zugeordneten Stadtteile. © OpenStreetMap contributors, ODbL 1.0.'}, {'name':'Straßen und Wege','url':'https://github.com/ckrey/stressmap/tree/78230754655af475a492de0af267722869d3afe1/app/data/duesseldorf','note':'Fest versionierter OSM-Auszug aus Cycling Level of Stress Map, Repository-Stand 23. März 2023; älterer tatsächlicher Datenstand möglich. Die zehn Qualitätsdateien werden zusammengeführt, an der Stadtgrenze abgeschnitten und je Name als ganze Einheit gebildet. Verkehrs- und Größenklassen fehlen im Auszug und werden nicht aus der Fahrradqualität erfunden. © OpenStreetMap contributors, ODbL 1.0.'}]
    # These actual data inputs are supplied by the documented collector, never invented.
    river_file=SOURCE/'rivers-normalized.json';metro_file=SOURCE/'metro-normalized.json'
    rivers=json.loads(river_file.read_text()) if river_file.exists() else {'features':[]}
    metro=json.loads(metro_file.read_text()) if metro_file.exists() else {'lines':[],'features':[],'note':'Originaldatenabruf noch ausstehend.'}
    for river in rivers['features']:
        river['cityIds']=[city['id'] for city in [{'id':f'dd-b{n}'} for n in BOROUGHS] if any(river_geo.intersects(shape(f['geometry'])) for f in neighborhoods if f['cityId']==city['id'])] if (river_geo:=shape(river['geometry'])) else []
        river['districtIds']=[f['id'] for f in neighborhoods if river_geo.intersection(shape(f['geometry'])).area>0]
        nearby=sorted([(river_geo.intersection(shape(f['geometry'])).area,f['nameZh']) for f in neighborhoods if river_geo.intersection(shape(f['geometry'])).area>0],reverse=True)[:4]
        river['description']='Im Düsseldorfer Stadtgebiet verläuft dieses Gewässer unter anderem bei '+', '.join(name for _,name in nearby)+'.'
    if (SOURCE/'layers-source-manifest.json').exists():
        sources.extend([{'name':'Flüsse: archivierte OSM-Mittellinien','url':'https://github.com/3ddruck12/flowtrail-pegel/blob/93b556e4314df05c6b2e887bc13721cb468f5ab2/osm-waterways.geojson','note':'OSM-Gewässerauszug vom 27. Mai 2026, unveränderlich archiviert. Auf Düsseldorf begrenzt; kleine Randfragmente unter 400 Metern entfallen. Blaue Flächen sind aus echten Mittellinien abgeleitet und keine vermessenen Ufergrenzen. © OpenStreetMap contributors, ODbL 1.0.'},{'name':'Bahnlinien: VRR-Haltestellen und Haltefolgen','url':'https://github.com/n3koBomb/linienblick/tree/b71ba453fb72696120ae591caeacae074768d6d2/site/public/data','note':'VRR-GTFS-Auszug, Version 25.08.2026, archiviert via n3koBomb/linienblick. U-Bahn, S-Bahn, Straßenbahn und SkyTrain werden schematisch zwischen den belegten Haltestellen verbunden. Keine exakten Gleisgeometrien und kein aktueller Fahrplan; Darstellungsfarben unterscheiden Verkehrsarten. Quelle: Verkehrsverbund Rhein-Ruhr (VRR), CC-BY-Angabe laut dokumentiertem Verkehrsverbund-Katalog; dort keine Versionsangabe.'}])
    if modern.exists():
        sources.append({'name':'Aktueller OSM-Auszug: Straßen, Flüsse und Stadtbahn','url':'https://www.openstreetmap.org/copyright','note':'Einmaliger Overpass-Abruf, Originalantwort mit Zeitstempel, Abfrage und SHA-256 im Datenpaket. Flussflächen sind angenäherte Flächen um echte Mittellinien, keine vermessenen Ufer. © OpenStreetMap contributors, ODbL 1.0.'})
    note=f'{len(streets):,} benannte Straßen- und Wegeeinheiten aus OSM; alle 50 Stadtteile besitzen Einträge. Quellen sind historische Auszüge, kein aktuelles amtliches Straßenverzeichnis und keine Vollständigkeitszusage. Straßenklasse im Auszug nicht enthalten.'.replace(f'{len(streets):,}',f'{len(streets):,}'.replace(',','.'))
    if modern.exists():
        note=f'{len(streets):,} benannte Straßen- und Wegeeinheiten aus einem dokumentierten OSM-Abruf; alle 50 Stadtteile besitzen Einträge. Kein amtlich geprüftes Straßenverzeichnis und keine Zusage vollständiger Abdeckung. Straßenklassen folgen den vorhandenen OSM-highway-Tags.'.replace(f'{len(streets):,}',f'{len(streets):,}'.replace(',','.'))
    result={'districts':{'version':2 if rivers['features'] and metro['features'] else 1,'features':features,'cities':[{'id':f'dd-b{n}','nameZh':f'Stadtbezirk {n}','nameEn':''} for n in BOROUGHS]},'streets':{'features':streets,'background':background},'rivers':rivers,'metro':metro,'sources':sources,'note':note,'coverage':coverage,'complete':bool(rivers['features'] and metro['features'])}
    (ROOT/'data/duesseldorf.js').write_text('window.DUESSELDORF_DATA = '+json.dumps(result,ensure_ascii=False,separators=(',',':'))+';\n')
    (SOURCE/'coverage.json').write_text(json.dumps({'streetUnits':len(streets),'neighborhoods':50,'boroughs':10,'byNeighborhood':coverage,'rivers':len(rivers['features']),'metroLines':len(metro['lines'])},ensure_ascii=False,indent=2)+'\n')
    print(note,'rivers',len(rivers['features']),'metro',len(metro['lines']))

if __name__=='__main__':main()
