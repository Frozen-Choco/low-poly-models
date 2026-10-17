import bpy,sys,json,hashlib,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
p=Path(sys.argv[sys.argv.index('--')+1]);out=Path(sys.argv[sys.argv.index('--')+2]);bpy.ops.wm.read_factory_settings(use_empty=True)
if p.suffix=='.blend':bpy.ops.wm.open_mainfile(filepath=str(p))
else:bpy.ops.import_scene.gltf(filepath=str(p))
obs={o.name:o for o in bpy.context.scene.objects if o.type=='MESH'}
def tree(name):
 o=obs[name];o.data.calc_loop_triangles();return BVHTree.FromPolygons([o.matrix_world@v.co for v in o.data.vertices],[tuple(t.vertices) for t in o.data.loop_triangles],all_triangles=True)
def ray(t,a,d):
 r=t.ray_cast(Vector(a),Vector(d),2);return list(r[0]) if r[0] is not None else None
checks={}
if 'Continuous chrome shell'in obs:
 t=tree('Continuous chrome shell');outer=ray(t,(.15,0,.12),(-1,0,0));inner=ray(t,(0,0,.12),(1,0,0));top=ray(t,(0,0,.3),(0,0,-1));under=ray(t,(0,0,.1),(0,0,1));checks={'side_outer':outer,'side_inner':inner,'side_wall_thickness_m':outer[0]-inner[0],'top_outer':top,'top_inner':under,'top_thickness_m':top[2]-under[2]}
else:
 vals=[]
 for n in obs:
  if n.startswith('Rotor blade'):
   t=tree(n);o=obs[n];vs=[o.matrix_world@v.co for v in o.data.vertices];v=min(vs,key=lambda v:abs(math.hypot(v.x,v.z-.655)-.098));a=ray(t,(v.x,-.1,v.z),(0,1,0));b=ray(t,(v.x,.1,v.z),(0,-1,0));vals.append({'object':n,'front':a,'back':b,'axial_thickness_m':b[1]-a[1] if a and b else None})
 checks={'blade_axial_thickness_samples':vals,'guard_spokes':len([n for n in obs if 'guard spoke' in n]),'blade_count':len(vals)}
out.write_text(json.dumps({'source':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'checks':checks,'method':'Independent saved geometry single-object opposing ray casts; dimensions in meters.'},indent=2));print(checks)
