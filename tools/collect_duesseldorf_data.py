"""Collect reproducible OSM streets, named waterways and U-lines for Düsseldorf.

Run only when overpass-api.de is allowed by the environment network policy.
All downloaded source data is retained with query, retrieval time and SHA-256.
The browser never contacts Overpass or any other external map service.
"""
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json
import urllib.parse
import urllib.request
from shapely.geometry import LineString, shape, mapping
from shapely.ops import unary_union, transform
from shapely import make_valid
import math

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'data/duesseldorf'
URL='https://overpass-api.de/api/interpreter'

def lines(g):
    if g.geom_type=='LineString':return [g] if g.length>.000005 else []
    return [v for p in getattr(g,'geoms',[]) for v in lines(p)]

def main():
    area=unary_union([make_valid(shape(f['geometry'])) for f in json.loads((SOURCE/'neighborhoods-source.geojson').read_text())['features']])
    west,south,east,north=area.bounds
    bbox=f'{south-.002:.6f},{west-.002:.6f},{north+.002:.6f},{east+.002:.6f}'
    query=f'''[out:json][timeout:180];(
way["highway"]["name"]({bbox});
way["waterway"~"^(river|stream)$"]["name"]({bbox});
relation["route"~"^(light_rail|subway|tram)$"]["ref"~"^U[0-9]+$"]({bbox});
);out geom;'''
    raw_path=SOURCE/'overpass-source.json'
    if not raw_path.exists():
        body=urllib.parse.urlencode({'data':query}).encode()
        request=urllib.request.Request(URL,data=body,headers={'User-Agent':'StadtKennen/0.9 (open-source geography learning; one-time local data collection)'})
        with urllib.request.urlopen(request,timeout=240) as response:raw=response.read()
        data=json.loads(raw)
        if data.get('remark') or not data.get('elements'):raise ValueError('Overpass returned incomplete data: '+str(data.get('remark')))
        raw_path.write_bytes(raw)
        manifest={'url':URL,'query':query,'retrievedAt':datetime.now(timezone.utc).isoformat(),'sha256':hashlib.sha256(raw).hexdigest(),'osmBaseTimestamp':data.get('osm3s',{}).get('timestamp_osm_base'),'license':'ODbL-1.0','attribution':'© OpenStreetMap contributors'}
        (SOURCE/'overpass-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
    data=json.loads(raw_path.read_text())
    named_water={};street_features=[];metro_features=[];metro_lines={}
    allowed={'motorway','motorway_link','trunk','trunk_link','primary','primary_link','secondary','secondary_link','tertiary','tertiary_link','residential','unclassified','living_street','service','pedestrian','road','footway','cycleway','path','steps'}
    for item in data['elements']:
        tags=item.get('tags',{})
        if item['type']=='way':
            coordinates=[(p['lon'],p['lat']) for p in item.get('geometry',[])]
            if len(coordinates)<2:continue
            g=LineString(coordinates).intersection(area)
            if not lines(g):continue
            if tags.get('highway') in allowed and tags.get('name'):
                street_features.append({'id':'way/'+str(item['id']),'properties':{'name':tags['name'],'highway':tags['highway']},'geometry':mapping(g)})
            if tags.get('waterway') in {'river','stream'} and tags.get('name'):
                named_water.setdefault(tags['name'],[]).append((g,tags))
        elif item['type']=='relation':
            if tags.get('state') in {'proposed','construction'} or tags.get('proposed') or tags.get('construction'):continue
            ref=tags.get('ref','');parts=[]
            for member in item.get('members',[]):
                if member.get('type')!='way' or member.get('role','') not in {'','forward','backward'}:continue
                coords=[(p['lon'],p['lat']) for p in member.get('geometry',[]) if p]
                if len(coords)>1:parts.extend(lines(LineString(coords).intersection(area)))
            if not parts:continue
            color=tags.get('colour','#326e9c')
            if not color.startswith('#') or len(color) not in {4,7}:color='#326e9c'
            metro_lines[ref]={'id':ref,'code':ref,'nameZh':tags.get('name',ref),'nameEn':'','color':color}
            metro_features.append({'type':'Feature','properties':{'line':ref,'relation':item['id']},'geometry':{'type':'MultiLineString','coordinates':[list(p.coords) for p in parts]}})
    # Approximate visual water areas around actual centerlines; not surveyed banks.
    sy=111320;sx=sy*math.cos(math.radians(51.23))
    project=lambda x,y,z=None:(x*sx,y*sy)
    unproject=lambda x,y,z=None:(x/sx,y/sy)
    rivers=[]
    for index,(name,items) in enumerate(sorted(named_water.items())):
        center=unary_union([g for g,tags in items])
        if transform(project,center).length<400:continue
        radius=180 if name=='Rhein' else 6
        widths=[]
        for g,tags in items:
            try:widths.append(float(tags.get('width','').split()[0])/2)
            except (ValueError,IndexError):pass
        if widths:radius=max(3,min(300,sum(widths)/len(widths)))
        g=transform(unproject,transform(project,center).buffer(radius)).intersection(area)
        if g.is_empty:continue
        anchor=max(lines(center),key=lambda line:line.length).interpolate(.5,normalized=True)
        city_ids=[]
        # The build step assigns intersected borough groups from district polygons.
        rivers.append({'id':'dd-river-'+hashlib.sha256(name.encode()).hexdigest()[:12],'kind':'river','nameZh':name,'nameEn':'','cityIds':city_ids,'anchor':[anchor.x,anchor.y],'geometry':mapping(g),'description':'OSM-Gewässerverlauf in Düsseldorf. Blaue Flächen sind eine angenäherte Darstellung um die erfasste Mittellinie, keine vermessenen Ufergrenzen.'})
    if not any(r['nameZh']=='Rhein' for r in rivers) or not any('Düssel' in r['nameZh'] for r in rivers):raise ValueError('Rhein and Düssel coverage required')
    if len(metro_lines)<8:raise ValueError('At least eight actual Düsseldorf U-lines required')
    (SOURCE/'streets-normalized.json').write_text(json.dumps({'features':street_features},ensure_ascii=False,separators=(',',':'))+'\n')
    (SOURCE/'rivers-normalized.json').write_text(json.dumps({'features':rivers},ensure_ascii=False,separators=(',',':'))+'\n')
    (SOURCE/'metro-normalized.json').write_text(json.dumps({'lines':sorted(metro_lines.values(),key=lambda x:x['id']),'features':metro_features,'note':'OSM-Stadtbahnlinien innerhalb der Stadtgrenze. Linienauszug und Datenstand sind unter Datenquellen dokumentiert; kein aktueller Fahrplan.'},ensure_ascii=False,separators=(',',':'))+'\n')
    print('Collected',len(street_features),'street segments,',len(rivers),'waterways,',len(metro_lines),'U-lines')

if __name__=='__main__':main()
