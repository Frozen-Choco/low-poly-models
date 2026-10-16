import bpy,sys,json,math
from pathlib import Path
from mathutils import Vector
sys.path.insert(0,str(Path(__file__).resolve().parent));from build_assets import *
report={}
def load(slug):
 clear();bpy.ops.import_scene.gltf(filepath=str(A/slug/(slug+'.glb')));bpy.context.view_layer.update()
def hit(o,origin,direction):
 inv=o.matrix_world.inverted();org=inv@Vector(origin);d=inv.to_3x3()@Vector(direction);r=o.ray_cast(org,d);return list(o.matrix_world@r[1]) if r[0] else None
load('round_wooden_stool');legs=[o for o in bpy.data.objects if o.name.startswith('Square splayed leg')];seat=bpy.data.objects['Solid round seat'];cleats=[o for o in bpy.data.objects if o.name.startswith('Seat underside mounting cleat')];rails=[o for o in bpy.data.objects if o.name.startswith('Side frame upper rail')]
contact=[]
for x in [-.087,.087]:
 c=min(cleats,key=lambda o:abs(o.location.x-x));r=min(rails,key=lambda o:abs(o.location.x-x));s_hit=hit(seat,(x,0,.40),(0,0,1));c_top=hit(c,(x,0,.43),(0,0,-1));c_bot=hit(c,(x,0,.40),(0,0,1));r_top=hit(r,(x,0,.43),(0,0,-1));contact.append({'x':x,'seat_hit':s_hit,'cleat_top':c_top,'cleat_bottom':c_bot,'rail_top':r_top,'seat_cleat_gap':s_hit[2]-c_top[2],'cleat_rail_gap':c_bot[2]-r_top[2]})
report['stool_measured_contacts']=contact
load('plastic_bail_bucket');body=bpy.data.objects['Continuous bucket wall rim and closed bottom'];bottom_in=hit(body,(0,0,.15),(0,0,-1));bottom_out=hit(body,(0,0,-.1),(0,0,1));mouth=hit(body,(0,0,.15),(0,0,1));out=hit(body,(.3,0,.10),(-1,0,0));inside=hit(body,(0,0,.10),(1,0,0));report['bucket_measured_shell']={'bottom_inside_hit':bottom_in,'bottom_outside_hit':bottom_out,'base_thickness_m':bottom_in[2]-bottom_out[2],'upward_center_mouth_unobstructed':mouth is None,'midheight_wall_thickness_m':out[0]-inside[0]}
load('wall_clock');mount=bpy.data.objects['Hanging bridge with keyhole'];back=bpy.data.objects['Recessed back cover'];report['clock_measured_keyhole']={'head_entry_open':hit(mount,(0,.03,.246),(0,-1,0)) is None,'upper_neck_open':hit(mount,(0,.03,.26),(0,-1,0)) is None,'backing_recess_open':hit(back,(0,.03,.26),(0,-1,0)) is None,'solid_shoulder_exists':hit(mount,(.009,.03,.26),(0,-1,0)) is not None}
(OUT/'numeric_use_validation.json').write_text(json.dumps(report,indent=2)+'\n')
print(report)
