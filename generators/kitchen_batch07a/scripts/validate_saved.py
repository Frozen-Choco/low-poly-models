import bpy,bmesh,json,hashlib,math
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];results=[]
for folder in sorted((R/'assets').iterdir()):
 for ext in ['blend','glb']:
  p=folder/(folder.name+'.'+ext)
  if ext=='blend':bpy.ops.wm.open_mainfile(filepath=str(p))
  else:bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(p))
  rows=[];vs=[]
  for o in [o for o in bpy.context.scene.objects if o.type=='MESH']:
   vs.extend(o.matrix_world@v.co for v in o.data.vertices);bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-7);bm.verts.ensure_lookup_table();bm.faces.ensure_lookup_table()
   seen=set();components=[]
   for v in bm.verts:
    if v.index in seen:continue
    todo=[v];seen.add(v.index);n=0
    while todo:
     cur=todo.pop();n+=1
     for e in cur.link_edges:
      nxt=e.other_vert(cur)
      if nxt.index not in seen:seen.add(nxt.index);todo.append(nxt)
    components.append(n)
   face_keys=[tuple(sorted(tuple(round(c,8) for c in v.co) for v in f.verts)) for f in bm.faces]
   o.data.calc_loop_triangles()
   rows.append({'object':o.name,'vertices_welded':len(bm.verts),'edges':len(bm.edges),'faces':len(bm.faces),'triangles':len(o.data.loop_triangles),'zero_area_triangles':sum(t.area<1e-14 for t in o.data.loop_triangles),'nonmanifold_edges':sum(not e.is_manifold for e in bm.edges),'boundary_edges':sum(e.is_boundary for e in bm.edges),'wire_edges':sum(e.is_wire for e in bm.edges),'components':components,'duplicate_faces':len(face_keys)-len(set(face_keys)),'signed_volume_m3':bm.calc_volume(signed=True),'euler':len(bm.verts)-len(bm.edges)+len(bm.faces)})
   bm.free()
  result={'asset':folder.name,'format':ext,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size,'dimensions_m':[max(v[i] for v in vs)-min(v[i] for v in vs) for i in range(3)],'nonfinite':sum(not math.isfinite(c) for v in vs for c in v),'objects':rows,'images':[{'name':im.name,'packed':bool(im.packed_file),'size':list(im.size)} for im in bpy.data.images if im.type=='IMAGE']}
  result['pass_basic']=all(row['nonmanifold_edges']==row['zero_area_triangles']==row['duplicate_faces']==0 and len(row['components'])==1 and row['signed_volume_m3']>0 for row in rows) and result['nonfinite']==0 and result['bytes']<100_000_000
  results.append(result)
(R/'evidence/saved_validation.json').write_text(json.dumps(results,indent=2)+'\n');print(json.dumps([{k:r[k] for k in ['asset','format','pass_basic']} for r in results],indent=2))
