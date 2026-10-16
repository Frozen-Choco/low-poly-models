import bpy,math,json,hashlib
from pathlib import Path
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];result={}
def verts(o):return [o.matrix_world@v.co for v in o.data.vertices]
def tree(o,v=None):return BVHTree.FromPolygons(verts(o) if v is None else v,[list(p.vertices) for p in o.data.polygons])
for slug in ['traffic_signal','railway_crossing_lowered']:
 result[slug]={}
 for ext in ['blend','glb']:
  p=R/'assets'/slug/(slug+'.'+ext)
  if ext=='blend':bpy.ops.wm.open_mainfile(filepath=str(p));objects=list(bpy.data.collections['ASSET | '+slug].objects)
  else:bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(p));objects=list(bpy.context.scene.objects)
  objects=[o for o in objects if o.type=='MESH'];bad=[];tris=0;finite=True
  for o in objects:
   m=o.data;m.calc_loop_triangles();tris+=len(m.loop_triangles)
   for t in m.loop_triangles:
    a,b,c=[o.matrix_world@m.vertices[i].co for i in t.vertices]
    if (b-a).cross(c-a).length<1e-12:bad.append([o.name,t.index])
   finite=finite and all(math.isfinite(c) for v in verts(o) for c in v)
  row={'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'triangles':tris,'zero_area_triangles':bad,'finite':finite};result[slug][ext]=row
  if slug=='railway_crossing_lowered':
   moving=[o for o in objects if o.name.startswith(('Four metre','Boom'))];static=[o for o in objects if o not in moving and not o.name.startswith('Drive shaft')];trees={o.name:tree(o) for o in static};vv={o.name:verts(o) for o in moving};pivot=Vector((.65,-.25,.88));hits=[]
   for k in range(361):
    angle=k/4;m=Matrix.Rotation(-math.radians(angle),3,'Y')
    for o in moving:
     t=tree(o,[pivot+m@(v-pivot) for v in vv[o.name]])
     for n,tt in trees.items():
      pairs=t.overlap(tt)
      if pairs:hits.append({'angle':angle,'moving':o.name,'static':n,'pairs':len(pairs)})
   row['moving_parts']=[o.name for o in moving];row['shaft_contact_excluded']='Drive shaft intentionally couples to rotating hub';row['full_assembly_361_pose_intersections']=hits
(R/'functional/assembly_test.json').write_text(json.dumps(result,indent=2));print('DONE',result)
