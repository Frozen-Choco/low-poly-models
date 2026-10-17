import bpy,sys,json,math,hashlib
from pathlib import Path
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree
p=Path(sys.argv[sys.argv.index('--')+1]);out=Path(sys.argv[sys.argv.index('--')+2]);bpy.ops.wm.read_factory_settings(use_empty=True)
if p.suffix=='.blend':bpy.ops.wm.open_mainfile(filepath=str(p))
else:bpy.ops.import_scene.gltf(filepath=str(p))
obs=[o for o in bpy.context.scene.objects if o.type=='MESH'];hub=next(o for o in obs if o.name=='Rotor hub');center=hub.matrix_world.translation.copy();center.y=0
blades=[o for o in obs if o.name.startswith('Rotor blade')];fixed=[o for o in obs if not o.name.startswith('Rotor') and o.name!='Motor shaft']
def data(os):
 vs=[];ts=[];owner=[]
 for o in os:
  o.data.calc_loop_triangles();k=len(vs);vs += [o.matrix_world@v.co for v in o.data.vertices];ts += [tuple(k+i for i in t.vertices) for t in o.data.loop_triangles];owner += [o.name]*len(o.data.loop_triangles)
 return vs,ts,owner
vs,ts,names=data(blades);fv,ft,fn=data(fixed);tree=BVHTree.FromPolygons(fv,ft,all_triangles=True,epsilon=1e-8);rows=[]
for angle in range(0,360,2):
 rot=Matrix.Rotation(math.radians(angle),3,'Y');rv=[center+rot@(v-center) for v in vs];rt=BVHTree.FromPolygons(rv,ts,all_triangles=True,epsilon=1e-8);hits=rt.overlap(tree)
 if hits:rows.append({'angle_degrees':angle,'pairs':sorted(set((names[a],fn[b]) for a,b in hits)),'triangle_pairs':len(hits)})
radii=[math.hypot(v.x-center.x,v.z-center.z) for v in vs];result={'source':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'center':list(center),'sample_step_degrees':2,'poses':180,'blade_radial_bounds_m':[min(radii),max(radii)],'blade_y_bounds_m':[min(v.y for v in vs),max(v.y for v in vs)],'collision_poses':rows,'method':'Independent saved-mesh blade rotation about Y. BVH triangle intersections against all fixed parts except coaxial motor shaft. Samples are supplemented by full-envelope bounds; not dynamics certification.'};out.write_text(json.dumps(result,indent=2));print('SWEEP',p.name,len(rows),'collision poses')
