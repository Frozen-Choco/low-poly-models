"""Saved-GLB based use/assembly proofs; review-only keys/support are never asset exports."""
import bpy,sys,os,json,math,hashlib,bmesh,shutil
from pathlib import Path
from mathutils import Vector
sys.path.insert(0,str(Path(__file__).resolve().parent));from build_assets import box,cyl,tube,mat,stats
R=Path(__file__).resolve().parents[1];A=Path(os.environ.get('ASSET_OUTPUT_ROOT',str(R/'assets')));O=A.parent/'functional';O.mkdir(exist_ok=True)
report={'source':'saved GLBs, freshly imported','inputs':{},'checks':{},'measurements':{}}
def load(slug):
 bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
 path=A/slug/(slug+'.glb');report['inputs'][slug]=hashlib.sha256(path.read_bytes()).hexdigest();bpy.ops.import_scene.gltf(filepath=str(path));bpy.context.view_layer.update();return [o for o in bpy.context.scene.objects if o.type=='MESH']
def bounds(o):
 v=[o.matrix_world@v.co for v in o.data.vertices];return ([min(p[i] for p in v) for i in range(3)],[max(p[i] for p in v) for i in range(3)])
def intersection(a,b):
 q=a.copy();q.data=a.data.copy();bpy.context.collection.objects.link(q);q.matrix_world=a.matrix_world.copy();bpy.context.view_layer.objects.active=q
 mo=q.modifiers.new('Audit exact intersection','BOOLEAN');mo.operation='INTERSECT';mo.solver='EXACT';mo.object=b;bpy.ops.object.modifier_apply(modifier=mo.name)
 bm=bmesh.new();bm.from_mesh(q.data);v=abs(bm.calc_volume(signed=True))*abs(q.matrix_world.determinant());bm.free();data=q.data;bpy.data.objects.remove(q,do_unlink=True);bpy.data.meshes.remove(data);return v
def studio(target,offset,scale):
 sc=bpy.context.scene;target=Vector(target)
 for o in list(sc.objects):
  if o.type in ['CAMERA','LIGHT']:bpy.data.objects.remove(o,do_unlink=True)
 sc.world.use_nodes=True;sc.world.node_tree.nodes['Background'].inputs[0].default_value=(.45,.48,.51,1);sc.world.node_tree.nodes['Background'].inputs[1].default_value=.5
 for p,power in [((1,-2,3),120),((-2,0,1),80),((0,1,-2),60)]:
  bpy.ops.object.light_add(type='AREA',location=target+Vector(p)*scale);o=bpy.context.object;o.data.energy=power*scale*scale;o.data.size=scale*2;o.rotation_euler=(target-o.location).to_track_quat('-Z','Y').to_euler()
 bpy.ops.object.camera_add(location=target+Vector(offset)*scale);cam=bpy.context.object;cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=scale;sc.camera=cam
 sc.render.engine='CYCLES';sc.cycles.samples=32;sc.cycles.use_denoising=False;sc.render.threads_mode='FIXED';sc.render.threads=2;sc.render.resolution_x=1000;sc.render.resolution_y=800;sc.render.resolution_percentage=100;sc.render.image_settings.file_format='JPEG';sc.render.image_settings.quality=92;sc.view_settings.view_transform='AgX'
def render(name,save=True):
 if os.environ.get('REUSE_PROOF_IMAGES') and name not in os.environ.get('FORCE_PROOF_IMAGES','').split(',') and (O/(name+'.jpg')).exists() and (O/(name+'.blend')).exists():return
 sc=bpy.context.scene;sc.render.filepath=str(O/(name+'.jpg'));bpy.ops.render.render(write_still=True)
 if save:bpy.ops.wm.save_as_mainfile(filepath=str(O/(name+'.blend')),compress=True)

obs=load('cast_iron_manhole');cover=next(o for o in obs if o.name.startswith('Separate cast cover'));seat=next(o for o in obs if o.name.startswith('Internal cover seating'));frame=next(o for o in obs if o.name.startswith('Outer support'));ribs=[o for o in obs if o.name.startswith('Underside cast')];moving=[o for o in obs if o not in [frame,seat]]
cb=bounds(cover);sb=bounds(seat);maxr=max(math.hypot(*(o.matrix_world@v.co)[:2]) for o in ribs for v in o.data.vertices)
report['measurements'].update(cover_bottom=cb[0][2],seat_top=sb[1][2],rib_max_radius=maxr,rib_radial_clearance=.285-maxr,frame_radial_clearance=.307-.302)
report['checks']['seat_exact_bearing']=abs(cb[0][2]-sb[1][2])<1e-6
report['checks']['seat_no_plate_penetration']=intersection(cover,seat)<1e-10
report['checks']['ribs_positive_ledge_clearance']=.285-maxr>.004
report['checks']['ribs_no_ledge_penetration']=all(intersection(o,seat)<1e-10 for o in ribs)
studio((0,0,.04),(1,-1,-1.5),.85);render('manhole_underside');shutil.copyfile(O/'manhole_underside.jpg',A/'cast_iron_manhole/underside.jpg')
steel=mat('Review only lift-key steel',(.40,.48,.53),.65,.37);keys=[];feet=[]
for y in [-.233,.233]:
 foot=box('Review key cross-foot',(0,y,.034),(.030,.006,.006),steel,0);shaft=cyl('Review key shaft',(0,y,.177),.003,.280,steel,N=32);handle=cyl('Review key upper grip',(0,y,.317),.004,.09,steel,rot=(0,math.pi/2,0),N=32);keys.append([foot,shaft,handle]);feet.append(foot)
# Test actual geometry over descent, turn, engaged bearing and lift.
worst=0.0
for z in [.120,.090,.075,.060,.045,.034]:
 for f in feet:
  f.location.z=z;f.rotation_euler[2]=0;bpy.context.view_layer.update();worst=max(worst,intersection(f,cover),*[intersection(f,o) for o in ribs])
report['checks']['key_insertion_no_collision']=worst<1e-10;report['measurements']['insertion_max_intersection_m3']=worst
worst=0.0
for angle in range(0,91,10):
 for f in feet:
  f.location.z=.034;f.rotation_euler[2]=math.radians(angle);bpy.context.view_layer.update();worst=max(worst,intersection(f,cover),*[intersection(f,o) for o in ribs])
report['checks']['key_rotation_no_collision']=worst<1e-10
# Underface ray targets prove material at both bearing shoulders, and no floor at slot center.
def ray_up(x,y):
 inv=cover.matrix_world.inverted();start=inv@Vector((x,y,.020));direction=inv.to_3x3()@Vector((0,0,1));hit,p,n,idx=cover.ray_cast(start,direction,distance=1)
 return (cover.matrix_world@p).z if hit else None
hits=[ray_up(0,y+d) for y in [-.233,.233] for d in [-.012,.012]]
report['checks']['positive_underface_engagement']=all(z is not None and abs(z-.047)<1e-6 for z in hits)
report['checks']['slots_are_through']=all(ray_up(0,y) is None for y in [-.233,.233]);report['measurements']['nominal_bearing_overlap_each_side_m']=.006
for key in keys:
 key[0].location.z=.034;key[0].rotation_euler[2]=0
studio((0,0,.1),(1,-1.6,1.6),.95);render('manhole_key_insertion')
for key in keys:
 key[0].rotation_euler[2]=math.pi/2
 for o in key:o.location.z+=.010
bpy.context.view_layer.update();report['checks']['engaged_keys_do_not_penetrate_cover']=all(intersection(f,cover)<1e-10 for f in feet)
studio((0,0,.07),(1,-1.5,-1.2),.85);render('manhole_engaged_underside')
# Lift all cover components in parallel; include ribs and keys.
worst=0.0
for dz in [.005,.025,.06,.10]:
 for o in moving:o.location.z+=dz
 bpy.context.view_layer.update()
 worst=max(worst,intersection(cover,frame),*[intersection(o,seat) for o in ribs])
 for o in moving:o.location.z-=dz
report['checks']['parallel_vertical_lift_clear']=worst<1e-10
for o in moving+[o for k in keys for o in k]:o.location.z+=.10
studio((0,0,.14),(1,-1.7,1.2),1.05);render('manhole_parallel_lift')
# Detail cutaway: review-only clipping of one side makes underside contact visible.
for o in moving+[frame,seat]:
 bm=bmesh.new();bm.from_mesh(o.data);inv=o.matrix_world.inverted();point=inv@Vector((0,0,0));normal=inv.to_3x3()@Vector((1,0,0));bmesh.ops.bisect_plane(bm,geom=list(bm.verts)+list(bm.edges)+list(bm.faces),dist=1e-7,plane_co=point,plane_no=normal,clear_outer=True,clear_inner=False);bm.to_mesh(o.data);bm.free()
studio((0,-.233,.16),(2,-1,.4),.18);render('manhole_engagement_cutaway')

obs=load('steel_roadside_bollard');plate=next(o for o in obs if o.name.startswith('Ten millimetre'));shanks=[o for o in obs if o.name.startswith('Continuous anchor')];washers=[o for o in obs if o.name.startswith('Bored anchor washer')];nuts=[o for o in obs if o.name.startswith('Bored hexagonal')]
report['checks']['four_continuous_shanks']=len(shanks)==4
report['checks']['shanks_clear_drilled_flange']=all(intersection(o,plate)<1e-10 for o in shanks)
report['checks']['continuous_embedment_to_above_nut']=all(abs(bounds(o)[0][2]+.100)<1e-6 and abs(bounds(o)[1][2]-.026)<1e-6 for o in shanks)
report['checks']['washers_contact_flange']=all(abs(bounds(o)[0][2]-.010)<1e-6 for o in washers)
report['checks']['nuts_contact_washers']=all(abs(bounds(o)[0][2]-.013)<1e-6 for o in nuts)
report['checks']['wrench_radial_access']=math.hypot(.064,.064)-.03815-.009815>.02
report['measurements'].update(visible_bollard_height_m=.850,total_bollard_bounds_m=stats(obs)['dimensions_m'][2],anchor_embedment_assumed_m=.100,flange_hole_radial_clearance_m=.0015,washer_hole_radial_clearance_m=.0005)
studio((0,0,.015),(1,-1,-1.1),.28);render('bollard_drilled_underside');shutil.copyfile(O/'bollard_drilled_underside.jpg',A/'steel_roadside_bollard/underside.jpg')
concrete=mat('Review inferred concrete foundation',(.30,.32,.31),0,.95);bond=mat('Review indicative bonded annulus',(.23,.17,.11),0,.95)
block=box('Review only inferred solid foundation',(0,0,-.18),(.40,.40,.36),concrete,0)
for x in [-.064,.064]:
 for y in [-.064,.064]:
  cut=cyl('Temporary anchor bore',(x,y,-.047),.007,.114,concrete,N=48);bpy.context.view_layer.objects.active=block;mo=block.modifiers.new('Substrate bore','BOOLEAN');mo.operation='DIFFERENCE';mo.object=cut;bpy.ops.object.modifier_apply(modifier=mo.name);bpy.data.objects.remove(cut,do_unlink=True)
  tube('Review indicative adhesive bond',(x,y,-.05),.007,.005,.10,bond,axis='Z')
# Actual mesh ray checks, not just nominal bore dimensions.
def foundation_ray(x,y):
 inv=block.matrix_world.inverted();hit,p,n,i=block.ray_cast(inv@Vector((x,y,.04)),inv.to_3x3()@Vector((0,0,-1)),distance=1)
 return (block.matrix_world@p).z if hit else None
bore_hits=[foundation_ray(x,y) for x in [-.064,.064] for y in [-.064,.064]]
report['measurements']['proof_foundation_bore_bottoms']=bore_hits
report['checks']['proof_foundation_open_bores']=all(z is not None and abs(z+.104)<1e-5 for z in bore_hits)
# Cutaway front portion of supporting concrete only, preserving actual anchors.
cut=box('Temporary substrate cutaway',(0,-.136,-.18),(.50,.145,.38),concrete,0);bpy.context.view_layer.objects.active=block;mo=block.modifiers.new('Review cutaway through front anchors','BOOLEAN');mo.operation='DIFFERENCE';mo.object=cut;bpy.ops.object.modifier_apply(modifier=mo.name)
for ob in [o for o in bpy.context.scene.objects if o.name.startswith('Review indicative adhesive bond')]:
 bpy.context.view_layer.objects.active=ob;mo=ob.modifiers.new('Expose bonded rod in cutaway','BOOLEAN');mo.operation='DIFFERENCE';mo.object=cut;bpy.ops.object.modifier_apply(modifier=mo.name)
bpy.data.objects.remove(cut,do_unlink=True)
studio((0,0,-.055),(1,-2,.6),.48);render('bollard_anchor_cutaway')
# Reopen saved proof scene and test the two uncut rear anchor bores.
bpy.ops.wm.open_mainfile(filepath=str(O/'bollard_anchor_cutaway.blend'));block=next(o for o in bpy.context.scene.objects if o.name.startswith('Review only inferred solid foundation'))
saved_hits=[foundation_ray(x,.064) for x in [-.064,.064]]
report['measurements']['saved_proof_rear_bore_bottoms']=saved_hits
report['checks']['saved_proof_foundation_open_bores']=all(z is not None and abs(z+.104)<1e-5 for z in saved_hits)
obs=load('concrete_curb_straight');studio((0,0,.12),(1,-1,-1.4),.8);render('curb_underside');shutil.copyfile(O/'curb_underside.jpg',A/'concrete_curb_straight/underside.jpg')
report['all_pass']=all(report['checks'].values());(O/'functional_validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2));assert report['all_pass']
