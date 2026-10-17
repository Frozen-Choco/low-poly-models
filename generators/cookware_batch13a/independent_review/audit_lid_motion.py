import bpy,json,sys,hashlib
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
p=Path(sys.argv[sys.argv.index('--')+1]);out=Path(sys.argv[sys.argv.index('--')+2]);bpy.ops.wm.read_factory_settings(use_empty=True)
if p.suffix=='.blend':bpy.ops.wm.open_mainfile(filepath=str(p))
else:bpy.ops.import_scene.gltf(filepath=str(p))
obs=[o for o in bpy.context.scene.objects if o.type=='MESH']
def mesh(items,dz):
 vv=[];tt=[]
 for o in items:
  o.data.calc_loop_triangles();off=len(vv);vv.extend(o.matrix_world@v.co+Vector((0,0,dz)) for v in o.data.vertices);tt.extend(tuple(off+i for i in t.vertices) for t in o.data.loop_triangles)
 return BVHTree.FromPolygons(vv,tt,all_triangles=True)
base=mesh([o for o in obs if not o.name.startswith('Lid')],0);lid=[o for o in obs if o.name.startswith('Lid')];rows=[]
for z in [.0001,.0005,.001,.002,.003,.005,.01,.02,.04,.08,.16]:rows.append({'lift_m':z,'lid_body_surface_intersections':len(mesh(lid,z).overlap(base))})
assert all(r['lid_body_surface_intersections']==0 for r in rows)
out.write_text(json.dumps({'source':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'decision':'PASS','sampled_vertical_lift':rows,'limit':'Static collision samples and axisymmetric skirt clearance; no force/thermal simulation.'},indent=2)+'\n')
