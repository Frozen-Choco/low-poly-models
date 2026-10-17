import bpy,bmesh,json,hashlib,math
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];rows=[]
for slug in ['toaster','electric_fan']:
 for ext in ['blend','glb']:
  p=R/'assets'/slug/(slug+'.'+ext);bpy.ops.wm.read_factory_settings(use_empty=True)
  if ext=='blend':bpy.ops.wm.open_mainfile(filepath=str(p))
  else:bpy.ops.import_scene.gltf(filepath=str(p))
  sc=bpy.context.scene;sc.frame_set(1);objects=[];vs=[]
  for o in sc.objects:
   if o.type!='MESH':continue
   bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-7);o.data.calc_loop_triangles();v=[o.matrix_world@v.co for v in o.data.vertices];vs+=v
   objects.append({'name':o.name,'vertices':len(o.data.vertices),'triangles':len(o.data.loop_triangles),'boundary_edges':sum(e.is_boundary for e in bm.edges),'nonmanifold_edges':sum(not e.is_manifold for e in bm.edges),'signed_volume':bm.calc_volume(signed=True),'uv_layers':len(o.data.uv_layers),'material_slots':len(o.data.materials),'zero_area_triangles':sum((v[t.vertices[1]]-v[t.vertices[0]]).cross(v[t.vertices[2]]-v[t.vertices[0]]).length<1e-14 for t in o.data.loop_triangles)})
   bm.free()
  row={'id':slug,'format':ext,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size,'finite':all(math.isfinite(c) for v in vs for c in v),'bounds':[[min(v[i] for v in vs) for i in range(3)],[max(v[i] for v in vs) for i in range(3)]],'objects':objects,'actions':[a.name for a in bpy.data.actions]};rows.append(row)
(R/'evidence/saved_validation.json').write_text(json.dumps(rows,indent=2)+'\n')
for row in rows:
 print(row['id'],row['format'],'nonmanifold',sum(o['nonmanifold_edges'] for o in row['objects']),'degenerate',sum(o['zero_area_triangles'] for o in row['objects']),'minZ',row['bounds'][0][2])
