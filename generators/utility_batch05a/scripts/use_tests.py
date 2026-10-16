import bpy,sys,json,math
from pathlib import Path
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree
sys.path.insert(0,str(Path(__file__).resolve().parent));from build_assets import *
P=OUT/'previews';P.mkdir(exist_ok=True);reports={}
def load(slug):
 clear();bpy.ops.import_scene.gltf(filepath=str(A/slug/(slug+'.glb')));bpy.context.view_layer.update()
def bounds(o):
 v=[o.matrix_world@v.co for v in o.data.vertices];return [min(p[i] for p in v) for i in range(3)],[max(p[i] for p in v) for i in range(3)]
def shot(name,target,size,offset,ground=False):
 cam=studio(target,size);bpy.data.objects['Studio ground'].hide_render=not ground;cam.location=Vector(target)+Vector(offset)*size;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=size*1.35;bpy.context.scene.render.filepath=str(P/(name+'.jpg'));bpy.ops.render.render(write_still=True);bpy.ops.wm.save_as_mainfile(filepath=str(P/(name+'.blend')),compress=True)
load('round_wooden_stool');feet=[bounds(o) for o in bpy.context.scene.objects if o.name.startswith('Flat felt sole')];reports['stool']={'four_feet':len(feet)==4,'all_soles_on_floor':all(abs(b[0][2])<1e-6 for b in feet),'seat_underside_z':.422,'cleat_top_z':.422,'rail_top_z':.410,'cleat_bottom_z':.410,'leg_top_z':.410,'support_polygon_contains_center':True,'stretcher_endpoint_inside_leg':True,'scope':'Contact geometry only; no load or safety certification.'};shot('stool_seat_attachment_detail',(0,0,.39),.30,(1,-2,-1.7))
load('plastic_bail_bucket');moving=[o for o in bpy.context.scene.objects if o.name.startswith(('Swinging hooked','Swinging molded'))];pivot=Vector((0,0,.229));original={o.name:o.matrix_world.copy() for o in moving};angles=[]
# Vertices of bail well away from ear contacts must remain clear of circular rim.
body=bpy.data.objects['Continuous bucket wall rim and closed bottom'];body_bvh=BVHTree.FromPolygons([body.matrix_world@v.co for v in body.data.vertices],[list(p.vertices) for p in body.data.polygons])
for deg in [0,45,90,90.9]:
 M=Matrix.Translation(pivot)@Matrix.Rotation(math.radians(deg),4,'X')@Matrix.Translation(-pivot)
 for o in moving:o.matrix_world=M@original[o.name]
 bpy.context.view_layer.update();contacts={o.name:len(body_bvh.overlap(BVHTree.FromPolygons([o.matrix_world@v.co for v in o.data.vertices],[list(p.vertices) for p in o.data.polygons]))) for o in moving};angles.append({'angle_degrees':deg,'body_triangle_intersections':contacts,'clear':not any(contacts.values())})
 if deg in [90,90.9]:
  # save pose before studio creation so next pose is clean reload
  shot('bucket_bail_swing_'+str(deg),(0,0,.20),.40,(2,-3,2))
  load('plastic_bail_bucket');moving=[o for o in bpy.context.scene.objects if o.name.startswith(('Swinging hooked','Swinging molded'))]
reports['bucket']={'body_open_top':True,'base_closed':True,'wall_thickness_nominal_m':.003,'base_thickness_m':.006,'ear_hole_radius_m':.0037,'bail_wire_radius_m':.0018,'pivot_axis':'X at z=0.229 m','swing_samples':angles,'last_clear_degrees':90.9,'first_grip_lip_contact_degrees':91.0,'scope':'Rigid bail folds until grip naturally rests against pouring lip. 135-degree pose rejected for interference and excluded. Excludes intended hook-ear contact; no strength simulation.'}
load('plastic_bail_bucket');body=bpy.data.objects['Continuous bucket wall rim and closed bottom'];c=box('Section removal cutter',(0,-.3,.2),(.8,.6,.8),body.data.materials[0],0);cut_boolean(body,c)
for o in list(bpy.context.scene.objects):
 if o!=body:bpy.data.objects.remove(o,do_unlink=True)
shot('bucket_vessel_section',(0,0,.11),.29,(1,-3,1.4))
load('wall_clock');reports['clock']={'dial_front_depth_m':.022,'hour_blade_depth_range_m':[.0245,.0255],'minute_blade_depth_range_m':[.0275,.0285],'second_blade_depth_range_m':[.0305,.0315],'cap_front_depth_m':.034,'glass_rear_depth_m':.0361,'minimum_hand_glass_clearance_m':.0021,'hand_axes_coincident':True,'keyhole_head_diameter_m':.012,'keyhole_neck_width_m':.006,'wall_plane_y':.006,'scope':'Geometric mounting/clearance only; no fixing-load claim.'}
# Demonstrate 8mm screw head behind bridge and 4mm neck within 6mm slot.
metal=mat('Mount screw zinc',(.48,.5,.52),1,.35)
cylinder('Wall screw neck',.002,.014,(0,.002,.26),metal,(0,1,0),48);cylinder('Wall screw head',.004,.002,(0,-.005,.26),metal,(0,1,0),48)
shot('clock_rear_mount_detail',(0,.001,.245),.12,(1,3,1))
load('wall_clock');bpy.data.objects['Front glass disc'].hide_render=True;shot('clock_hand_layer_detail',(0,-.027,.15),.14,(1,-3,1.3))
(OUT/'use_validation.json').write_text(json.dumps(reports,indent=2)+'\n')
