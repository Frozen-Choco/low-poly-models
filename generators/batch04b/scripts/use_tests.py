import bpy,sys,json,math,os
from pathlib import Path
from mathutils import Vector,Matrix
sys.path.insert(0,str(Path(__file__).resolve().parent));from build_assets import *
P=OUT/'previews';P.mkdir(exist_ok=True);reports=[]
def bounds(o):
 v=[o.matrix_world@x.co for x in o.data.vertices];return [min(p[i] for p in v) for i in range(3)],[max(p[i] for p in v) for i in range(3)]
def rotate(obs,pivot,angle):
 tr=Matrix.Translation(Vector(pivot))@Matrix.Rotation(angle,4,'X')@Matrix.Translation(-Vector(pivot))
 for o in obs:o.matrix_world=tr@o.matrix_world
 bpy.context.view_layer.update()
def evidence(slug,name,mutate):
 clear();bpy.ops.import_scene.gltf(filepath=str(A/slug/(slug+'.glb')));meshes=[o for o in bpy.context.scene.objects if o.type=='MESH'];mutate(meshes);bpy.context.view_layer.update();s=stats(meshes);target=(Vector(s['bounds_min'])+Vector(s['bounds_max']))/2;size=max(s['dimensions_m']);cam=studio(target,size);cam.location=target+Vector((2,-3,2))*size;cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();bpy.context.scene.render.filepath=str(P/(name+'.jpg'));bpy.ops.render.render(write_still=True);bpy.ops.wm.save_as_mainfile(filepath=str(P/(name+'.blend')),compress=True)
# Saved meshes are inspected, rather than recreated geometry.
for slug in IDS:
 clear();bpy.ops.import_scene.gltf(filepath=str(A/slug/(slug+'.glb')))
 if slug=='taped_shipping_box':
  tape=[o for o in bpy.context.scene.objects if o.name.startswith('Continuous seam tape')];zs=sorted(bounds(o)[0][2] for o in tape);checks={'bottom_tape_exposed':zs[0]<.00001,'top_tape_above_box':zs[-1]>.20,'manufacturer_joint_present':any(o.name.startswith('Interior glued') for o in bpy.context.scene.objects)}
 elif slug=='office_stapler':
  an=bpy.data.objects['Stainless clinching anvil'];dr=bpy.data.objects['Front driver face'];ab=bounds(an);db=bounds(dr);checks={'driver_and_anvil_center_aligned':abs(an.location.y-dr.location.y)<1e-5,'paper_entry_clearance_over_4mm':db[0][2]-ab[1][2]>.004,'hinge_transverse':bounds(bpy.data.objects['Transverse steel hinge axle'])[1][0]-bounds(bpy.data.objects['Transverse steel hinge axle'])[0][0]>.04 and bounds(bpy.data.objects['Transverse steel hinge axle'])[1][1]-bounds(bpy.data.objects['Transverse steel hinge axle'])[0][1]<.007}
 else:
  pa=bounds(bpy.data.objects['A4 paper sheet 5']);board=bounds(bpy.data.objects['Thin hardboard clipboard']);pad=bounds(bpy.data.objects['Clip jaw paper contact pad']);checks={'paper_supported':all(pa[0][i]>=board[0][i] and pa[1][i]<=board[1][i] for i in [0,1]),'pad_contacts_paper':abs(pad[0][2]-pa[1][2])<.00005,'paper_clear_of_rivets':pa[1][1]<.148}
 reports.append({'id':slug,'checks':checks,'all_pass':all(checks.values())})
def carton_pose(obs):
 for o in obs:
  if o.name.startswith('Continuous seam tape') and bounds(o)[0][2]>.20:o.hide_render=True
  if o.name.startswith('Meeting long closure flap') and bounds(o)[0][2]>.20:
   y=o.location.y;rotate([o],(0,math.copysign(.119,y),.2048),-math.copysign(math.radians(70),y))
def staple_pose(obs):
 static=['Molded rubber sole','Stamped steel base','Base painted insert','Stainless clinching anvil','Rear hinge support','Transverse steel hinge axle']
 moving=[o for o in obs if not any(o.name.startswith(n) for n in static)];rotate(moving,(0,.058,.027),math.radians(-35))
def pressing_pose(obs):
 static=['Molded rubber sole','Stamped steel base','Base painted insert','Stainless clinching anvil','Rear hinge support','Transverse steel hinge axle']
 moving=[o for o in obs if not any(o.name.startswith(n) for n in static)];rotate(moving,(0,.058,.027),math.radians(2.5))
 an=bounds(bpy.data.objects['Stainless clinching anvil']);dr=bounds(bpy.data.objects['Front driver face']);projection=(dr[0][1]+dr[1][1])/2
 checks={'pressed_driver_over_anvil':an[0][1]<projection<an[1][1],'pressed_driver_not_through_anvil':dr[0][2]>an[1][2],'pressed_magazine_clear_of_base':min(bounds(o)[0][2] for o in moving if o.name.startswith('Magazine'))>.012}
 reports.append({'id':'office_stapler_press','checks':checks,'all_pass':all(checks.values())})
def clip_pose(obs):
 moving=[o for o in obs if o.name.startswith(('Spring wire jaw with finger lift','Clip jaw paper contact pad'))];rotate(moving,(0,.151,.008),math.radians(-23))
for slug,name,fn in [('taped_shipping_box','carton_open_flap_test',carton_pose),('office_stapler','stapler_raised_arm_test',staple_pose),('a4_clipboard','clipboard_open_jaw_test',clip_pose),('office_stapler','stapler_press_test',pressing_pose)]:evidence(slug,name,fn)
(OUT/'use_validation.json').write_text(json.dumps(reports,indent=2)+'\n');assert all(r['all_pass'] for r in reports),reports
