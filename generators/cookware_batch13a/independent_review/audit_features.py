import bpy,json,sys,math,hashlib
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
src=Path(sys.argv[sys.argv.index('--')+1]);out=Path(sys.argv[sys.argv.index('--')+2]);bpy.ops.wm.read_factory_settings(use_empty=True)
if src.suffix=='.blend':bpy.ops.wm.open_mainfile(filepath=str(src))
else:bpy.ops.import_scene.gltf(filepath=str(src))
obs={o.name:o for o in bpy.context.scene.objects if o.type=='MESH'}
def tree(o):
 o.data.calc_loop_triangles();return BVHTree.FromPolygons([o.matrix_world@v.co for v in o.data.vertices],[tuple(t.vertices) for t in o.data.loop_triangles],all_triangles=True)
def ray(o,p,d):
 a=tree(o).ray_cast(Vector(p),Vector(d));return None if a[0] is None else list(a[0])
rs={}
if 'frying_pan' in src.name:
 rs['hanging_hole_center_ray_no_handle_hit']=ray(obs['Pan phenolic handle'],(.299,0,.2),(0,0,-1)) is None
 for name in ['Pan handle mounting bracket','Pan handle steel tang','Pan handle welded receiver boss']:
  vv=[obs[name].matrix_world@v.co for v in obs[name].data.vertices]
  # Compare outer attachments against interpolated inner cooking-wall radial profile.
  pr=[(.005,.098),(.007,.104),(.012,.110),(.022,.116),(.039,.123),(.0535,.130)]
  vals=[]
  for v in vv:
   for (z0,r0),(z1,r1) in zip(pr,pr[1:]):
    if z0<=v.z<=z1:vals.append(math.hypot(v.x,v.y)-(r0+(r1-r0)*(v.z-z0)/(z1-z0)))
  rs[name+'_minimum_clearance_outside_inner_cavity_m']=min(vals)
else:
 lid=obs['Lid removable steel dome and locating skirt']
 rs['steam_holes_vertical_rays_no_lid_hit']=[ray(lid,(x,-.094,.2),(0,0,-1)) is None for x in [-.006,.006]]
 for name,o in obs.items():
  if 'mounting seat' in name:
   rs[name+'_minimum_radial_position_m']=min(math.hypot(v.x,v.y) for v in [o.matrix_world@p.co for p in o.data.vertices])
 rs['lid_skirt_outer_radius_m']=.099;rs['pot_inner_radius_at_skirt_m']=.100
 rs['pot_lid_rim_support_measured_rays']={}
 for x in [.1015,-.1015]:
  rs['pot_lid_rim_support_measured_rays'][str(x)]={'pot_top':ray(obs['Pot continuous three-layer steel exterior'],(x,0,.15),(0,0,-1)),'lid_underside':ray(lid,(x,0,.09),(0,0,1))}
out.write_text(json.dumps({'source':str(src),'sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'features':rs},indent=2)+'\n');print(rs)
