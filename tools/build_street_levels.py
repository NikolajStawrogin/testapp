"""Precompute approximate main-course lengths for street learning levels.

Offline development dependency: shapely==2.1.2. Parallel carriageways are not
simply added: each clipped street is measured by its longest connected graph
course. Broad closed loops use their circumference; thin parallel loops use
main-course span. Estimates are for learning order, not official measurements.
"""
from pathlib import Path
import hashlib,heapq,json,math
from shapely.geometry import shape,Polygon
from shapely.ops import unary_union,transform
from shapely import make_valid
ROOT=Path(__file__).resolve().parents[1]

def read(name):
 return json.loads((ROOT/name).read_text().split('=',1)[1].strip().removesuffix(';'))
def lines(g):
 if g.geom_type=='LineString':return [g] if g.length>.01 else []
 return [p for sub in getattr(g,'geoms',[]) for p in lines(sub)]
def main_course(g):
 graph={}
 for line in lines(unary_union(g)):
  points=[(round(x,1),round(y,1)) for x,y in line.coords]
  for a,b in zip(points,points[1:]):
   if a==b:continue
   w=math.dist(a,b);graph.setdefault(a,{})[b]=w;graph.setdefault(b,{})[a]=w
 if not graph:return 0
 def distances(start):
  dist={start:0};queue=[(0,start)]
  while queue:
   d,a=heapq.heappop(queue)
   if d!=dist[a]:continue
   for b,w in graph[a].items():
    nd=d+w
    if nd<dist.get(b,float('inf')):dist[b]=nd;heapq.heappush(queue,(nd,b))
  return dist
 pending=set(graph);best=0;protected_loop=False
 while pending:
  first=distances(min(pending));component=set(first);pending.difference_update(component)
  furthest=max(first,key=first.get);second=distances(furthest);length=max(second.values())
  # Recognize actual broad ring streets without treating narrow dual-carriageway
  # loops as a road twice its actual length.
  broad_loop=False
  if len(component)>2 and all(len(graph[p])==2 for p in component):
   perimeter=sum(sum(graph[p].values()) for p in component)/2
   start=min(component);ordered=[start];previous=None;current=start
   while True:
    candidates=sorted(point for point in graph[current] if point!=previous)
    following=candidates[0]
    if following==start:break
    ordered.append(following);previous,current=current,following
    if len(ordered)>len(component):break
   # Compactness uses the actual enclosed area, not the bounding box: a
   # curving motorway's two carriageways can have a wide bounding box while
   # still enclosing only a thin strip. They must not count twice.
   if len(ordered)>=3 and len(ordered)<=len(component) and Polygon(ordered).area/(perimeter*perimeter)>.01:
    length=perimeter;broad_loop=True
  if length>best:best=length;protected_loop=broad_loop
 # Remove the width contribution of nearby parallel curves. For a long
 # corridor, its buffered area is roughly 2*r*L + width*L + end caps.
 # Extrapolating two radii cancels that width term. Only apply a substantial
 # correction, retaining the graph estimate for ordinary paths and rings.
 if best>100 and not protected_loop:
  estimates=[]
  for radius in (30,60):
   buffered=g.buffer(radius,quad_segs=8)
   polygons=list(buffered.geoms) if buffered.geom_type=='MultiPolygon' else [buffered]
   caps=sum(not polygon.interiors for polygon in polygons)
   estimates.append((buffered.area-caps*math.pi*radius*radius)/(2*radius))
  corridor=2*estimates[1]-estimates[0]
  if best*.35<corridor<best/1.15:best=corridor
 return round(best)

def build(region):
 if region=='duesseldorf':
  data=read('data/duesseldorf.js');areas=[f for f in data['districts']['features'] if f['level']=='neighborhood'];streets=data['streets']['features'];files=['data/duesseldorf.js']
 else:
  data=read('data/districts.js');areas=data['features'];raw=read('data/streets.js');parents=read('data/street-parents.js');replaced=set(parents['replacedIds']);streets=[f for f in raw['features'] if f['id'] not in replaced]+parents['features'];files=['data/districts.js','data/streets.js','data/street-parents.js']
 latitude=sum(f['anchor'][1] for f in areas)/len(areas);sy=111320;sx=sy*math.cos(math.radians(latitude));project=lambda x,y,z=None:(x*sx,y*sy)
 polygons={f['id']:transform(project,make_valid(shape(f['geometry']))) for f in areas}
 region_polygon=unary_union(list(polygons.values()))
 city_polygons={} if region=='duesseldorf' else {id:unary_union([polygons[f['id']] for f in areas if f['cityId']==id]) for id in {f['cityId'] for f in areas}}
 result={}
 for f in streets:
  if f['unit']!='street':continue
  g=transform(project,shape(f['geometry']));districts={}
  for id in f['districtIds']:
   if id in polygons:
    districts[id]=main_course(g.intersection(polygons[id]))
  cities={id:main_course(g.intersection(polygon)) for id,polygon in city_polygons.items() if any(a['id'] in districts and a['cityId']==id for a in areas)}
  result[f['id']]={'length':main_course(g.intersection(region_polygon)),'districts':districts,'cities':cities}
 hashes={name:hashlib.sha256((ROOT/name).read_bytes()).hexdigest() for name in files}
 output={'version':1,'region':region,'metric':'approximate-main-course-with-parallel-corridor-normalization','sourceSha256':hashes,'streets':result}
 path=ROOT/f'data/levels-{region}.js';path.write_text('window.STREET_LEVEL_DATA = '+json.dumps(output,ensure_ascii=False,separators=(',',':'))+';\n')
 print(region,len(result),'whole streets',path.stat().st_size,'bytes',flush=True)
if __name__=='__main__':
 for region in ['duesseldorf','taipei']:build(region)
