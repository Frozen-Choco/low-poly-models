import bpy,sys,json,hashlib
from pathlib import Path
from mathutils.bvhtree import BVHTree
folder=Path(sys.argv[sys.argv.index('--')+1]);out=Path(sys.argv[sys.argv.index('--')+2]);slug=folder.name
snap={}
for ext in ['blend','glb']:
 p=folder/(slug+'.'+ext);bpy.ops.wm.read_factory_settings(use_empty=True)
 if ext=='blend':bpy.ops.wm.open_mainfile(filepath=str(p))
 else:bpy.ops.import_scene.gltf(filepath=str(p))
 frames={}
 for fr in [1]:
  bpy.context.scene.frame_set(fr);bpy.context.view_layer.update();rows={}
  for o in bpy.context.scene.objects:
   if o.type!='MESH':continue
   o.data.calc_loop_triangles();vs=[o.matrix_world@v.co for v in o.data.vertices];ts=[tuple(t.vertices) for t in o.data.loop_triangles]
   rows[o.name]=(vs,BVHTree.FromPolygons(vs,ts,all_triangles=True),len(ts))
  frames[fr]=rows
 snap[ext]=frames
result=[]
for fr in snap['blend']:
 a,b=snap['blend'][fr],snap['glb'][fr];rs=[]
 for name in sorted(set(a)&set(b)):
  av,at,ac=a[name];bv,bt,bc=b[name];d=max(max(bt.find_nearest(v)[3] for v in av),max(at.find_nearest(v)[3] for v in bv));rs.append({'name':name,'max_bidirectional_vertex_to_surface_distance_m':d,'triangles_blend':ac,'triangles_glb':bc})
 result.append({'frame':fr,'missing_names':list(set(a)^set(b)),'objects':rs,'max_distance_m':max(r['max_bidirectional_vertex_to_surface_distance_m'] for r in rs)})
out.write_text(json.dumps({'asset':slug,'source_hashes':{e:hashlib.sha256((folder/(slug+'.'+e)).read_bytes()).hexdigest() for e in ['blend','glb']},'poses':result},indent=2));print('FORMAT',slug,[(r['frame'],r['max_distance_m']) for r in result])
