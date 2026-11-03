"""Build Düsseldorf water and transit layers offline from pinned public archives.

Requires shapely==2.1.2. Uses OSM waterway centerlines and VRR GTFS stop sequences;
transit links are explicitly schematic, not reconstructed railway track geometry.
"""
from collections import defaultdict
from pathlib import Path
import gzip
import hashlib
import json
import math
import re
from shapely.geometry import shape, LineString
from shapely.ops import unary_union, transform
from shapely import make_valid

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'data/duesseldorf'

def parts(g):
    if g.geom_type=='LineString':return [g] if g.length>0.000005 else []
    return [line for sub in getattr(g,'geoms',[]) for line in parts(sub)]

def pack(g):
    from shapely.geometry import mapping
    def rounded(value):
        if isinstance(value,(tuple,list)):return [rounded(v) for v in value]
        return round(value,7) if isinstance(value,float) else value
    return {'type':g.geom_type,'coordinates':rounded(mapping(g)['coordinates'])}

def main():
    manifest=json.loads((SOURCE/'layers-source-manifest.json').read_text())
    for row in manifest['sources']:
        raw=(SOURCE/row['file']).read_bytes()
        if hashlib.sha256(raw).hexdigest()!=row['sha256']:raise ValueError('Changed source: '+row['file'])
        if row.get('uncompressedSha256') and hashlib.sha256(gzip.decompress(raw)).hexdigest()!=row['uncompressedSha256']:raise ValueError('Changed compressed content')
    area=unary_union([make_valid(shape(f['geometry'])) for f in json.loads((SOURCE/'neighborhoods-source.geojson').read_text())['features']])
    sy=111320;sx=sy*math.cos(math.radians(51.23))
    project=lambda x,y,z=None:(x*sx,y*sy)
    unproject=lambda x,y,z=None:(x/sx,y/sy)
    groups=defaultdict(list);ids=defaultdict(set)
    water=json.loads(gzip.decompress((SOURCE/'waterways-source.geojson.gz').read_bytes()))
    for feature in water['features']:
        name=feature['properties'].get('river','').strip()
        if not name or feature['properties'].get('waterway')!='river':continue
        g=shape(feature['geometry']).intersection(area)
        if not parts(g):continue
        groups[name].append(g);ids[name].add(feature['properties']['osm_id'])
    rivers=[]
    for name,geometries in sorted(groups.items()):
        center=unary_union(geometries);length=transform(project,center).length
        if length<400:continue
        radius=180 if name=='Rhein' else 7
        water_area=transform(unproject,transform(project,center).buffer(radius,quad_segs=5)).intersection(area)
        water_area=make_valid(water_area)
        # A point within the rendered area is essential for click and quiz accessibility.
        anchor=max(parts(center),key=lambda g:g.length).interpolate(.5,normalized=True)
        if not water_area.contains(anchor):anchor=water_area.representative_point()
        rivers.append({'id':'dd-river-'+hashlib.sha256(name.encode()).hexdigest()[:12],'kind':'river','nameZh':name,'nameEn':'','cityIds':[],
            'anchor':[round(anchor.x,7),round(anchor.y,7)],'geometry':pack(water_area),'centerline':pack(center),'sourceIds':sorted(ids[name]),'lengthMeters':round(length),
            'description':'Gewässerverlauf im Stadtgebiet von Düsseldorf. Aus OSM-Mittellinien abgeleitete Darstellung; die blaue Fläche ist keine vermessene Ufergrenze.'})
    assert {'Rhein','Düssel','Nördliche Düssel','Südliche Düssel','Itter','Kittelbach'}.issubset({r['nameZh'] for r in rivers})
    lines_source=json.loads((SOURCE/'transit-lines-source.json').read_text())
    stops_source=json.loads((SOURCE/'transit-stops-source.json').read_text())
    stops={s['id']:s for s in stops_source['stops']};routes={}
    for line in lines_source['lines']:
        ref=line['name'].strip()
        kind='metro' if re.fullmatch(r'U\d+',ref) else 'suburban' if re.fullmatch(r'S\d+',ref) else 'tram' if line['mode']=='tram' and re.fullmatch(r'\d+',ref) else 'other' if ref=='SkyT' else None
        if not kind:continue
        route=routes.setdefault(ref,{'kind':kind,'edges':{},'routeIds':set(),'stops':set()})
        route['routeIds'].add(line['id'])
        for pattern in line['patterns']:
            for a,b in zip(pattern['stops'],pattern['stops'][1:]):
                if a not in stops or b not in stops:raise ValueError('Unresolved GTFS stop')
                if a==b:continue
                p,q=stops[a],stops[b];pa=(p['lon'],p['lat']);pb=(q['lon'],q['lat'])
                if pa==pb:continue
                clipped=parts(LineString([pa,pb]).intersection(area))
                if clipped:route['edges'][tuple(sorted((a,b)))]=clipped;route['stops'].update((a,b))
    palette={'metro':'#2765a6','suburban':'#29804c','tram':'#bf4851','other':'#8260a6'}
    kind_names={'metro':'Stadtbahn / U-Bahn','suburban':'S-Bahn','tram':'Straßenbahn','other':'SkyTrain'}
    metro_lines=[];features=[]
    for ref,route in sorted(routes.items(),key=lambda item:(list(palette).index(item[1]['kind']),int(re.search(r'\d+',item[0])[0]) if re.search(r'\d+',item[0]) else 0)):
        if not route['edges']:continue
        metro_lines.append({'id':ref,'code':ref,'kind':route['kind'],'nameZh':kind_names[route['kind']],'nameEn':'','color':palette[route['kind']],
            'sourceRouteIds':sorted(route['routeIds']),'stopIds':sorted(route['stops'])})
        features.append({'type':'Feature','properties':{'line':ref,'kind':route['kind'],'relation':'gtfs:'+ref},
            'geometry':{'type':'MultiLineString','coordinates':[pack(g)['coordinates'] for edges in route['edges'].values() for g in edges]}})
    assert len([l for l in metro_lines if l['kind']=='metro'])>=8
    assert {'S1','S6','S8','S11','S28','S68'}.issubset({l['id'] for l in metro_lines})
    metro={'lines':metro_lines,'features':features,'geometryModel':'gtfs-stop-links','sourceVersion':stops_source['source']['version'],
        'note':'Schematische Verbindungen zwischen VRR-Haltestellen, Stand 25.08.2026, auf das Stadtgebiet begrenzt. Keine exakten Gleiskurven und kein aktueller Fahrplan. Farben unterscheiden Verkehrsarten.'}
    (SOURCE/'rivers-normalized.json').write_text(json.dumps({'features':rivers},ensure_ascii=False,separators=(',',':'))+'\n')
    (SOURCE/'metro-normalized.json').write_text(json.dumps(metro,ensure_ascii=False,separators=(',',':'))+'\n')
    print('Rivers:',', '.join(r['nameZh'] for r in rivers))
    print('Transit:',len(metro_lines),{kind:sum(l['kind']==kind for l in metro_lines) for kind in palette})

if __name__=='__main__':main()
