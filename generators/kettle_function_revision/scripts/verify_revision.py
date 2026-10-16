import bpy,sys,os,json,math,shutil,hashlib
from pathlib import Path
from mathutils import Vector,Matrix
sys.path.insert(0,str(Path(__file__).resolve().parent));from build_kettle import *
P=R/'previews';P.mkdir(exist_ok=True);slug=IDS[0];f=A/slug
OLD=R/'baseline'/'stainless_kitchen_kettle_before.glb'
def load(path):
 clear();bpy.ops.import_scene.gltf(filepath=str(path));return [o for o in bpy.context.scene.objects if o.type=='MESH']
def shot(path,target,size,off):
 cam=studio(target,size);cam.location=Vector(target)+Vector(off)*size;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=size*1.45;sc=bpy.context.scene;sc.render.resolution_x=900;sc.render.resolution_y=900;sc.cycles.samples=64;sc.render.filepath=str(path);bpy.ops.render.render(write_still=True)
for version,path in [('before',OLD),('after',f/(slug+'.glb'))]:
 for name,off in [('top',(0,0,3)),('side',(0,-3,.3)),('three_quarter',(2,-3,2))]:
  if version=='before' and (P/(version+'_'+name+'.jpg')).exists():continue
  obs=load(path);shot(P/(version+'_'+name+'.jpg'),(.035,0,.135),.30,off)
for name,off in [('rear',(-2,3,1.7)),('close_up',(1,-3,2))]:
 obs=load(f/(slug+'.glb'));shot(f/(name+'.jpg'),(.02,0,.16),.27,off)
for src,dst in [('after_three_quarter','front_three_quarter'),('after_three_quarter','preview'),('after_side','side'),('after_top','top')]:shutil.copyfile(P/(src+'.jpg'),f/(dst+'.jpg'))
shutil.copyfile(f/'rear.jpg',f/'back.jpg')
# Mechanism inspection: lateral fold about shared X pin axis and unobstructed lid lift.
obs=load(f/(slug+'.glb'));pivot=Vector((0,0,.152));rot=Matrix.Rotation(math.pi/2,4,'X');fold=Matrix.Translation(pivot)@rot@Matrix.Translation(-pivot)
for o in obs:
 if 'Moving stainless' in o.name or 'Fore-aft insulated' in o.name:o.matrix_world=fold@o.matrix_world
 if 'Seated removable' in o.name or 'Lid insulated' in o.name:o.location.z+=.105
shot(P/'after_folded_lid_removed.jpg',(.015,-.02,.16),.34,(2,-3,2));bpy.ops.wm.save_as_mainfile(filepath=str(P/'fold_lid_review.blend'),compress=True)
# Kinematic pour pose. Lid is held in place for this test, as in the official in-use photo.
obs=load(f/(slug+'.glb'));grip=Vector((0,0,.259));rot=Matrix.Rotation(math.radians(35),4,'Y');pose=Matrix.Translation(grip+Vector((0,0,.10)))@rot@Matrix.Translation(-grip)
for o in obs:o.matrix_world=pose@o.matrix_world
end=pose@Vector((.172,0,.153));water=mat('Illustrative flow path, not fluid simulation',(.18,.40,.52),0,.26)
pts=[tuple(end+Vector((.09*t,0,.025*t-.14*t*t))) for t in [i/24 for i in range(25)]];path_tube('Illustrative water path',pts,[.0014]*25,water,N=16)
ceramic=mat('Context receiving cup',(.65,.63,.57),0,.25);cup=lathe('Context receiving cup',[(.001,0),(.033,0),(.039,.005),(.043,.075),(.042,.078),(.039,.078),(.036,.008),(.001,.008)],ceramic,64);cup.location=(end.x+.09,0,0)
shot(P/'after_pouring_pose.jpg',(.055,0,.17),.43,(1,-3,1.4));bpy.ops.wm.save_as_mainfile(filepath=str(P/'pouring_review.blend'),compress=True)
# Reopen source and compare the actual interchange artifact.
bpy.ops.wm.open_mainfile(filepath=str(f/(slug+'.blend')));s=stats([o for o in bpy.context.scene.objects if o.type=='MESH']);obs=load(f/(slug+'.glb'));t=stats(obs)
checks=dict(dimensions_match=max(abs(a-b) for a,b in zip(s['dimensions_m'],t['dimensions_m']))<1e-6,triangles_match=s['triangles']==t['triangles'],parts_match=s['mesh_objects']==t['mesh_objects'],no_degenerates=s['zero_area_triangles']==t['zero_area_triangles']==0,finite=all(math.isfinite(v) for o in obs for vert in o.data.vertices for v in vert.co),self_contained=all(i.packed_file or i.source!='FILE' for i in bpy.data.images))
validation=dict(blend=s,glb=t,checks=checks,all_pass=all(checks.values()),mechanism={'spout_axis':'+X','arch_plane':'XZ','coaxial_hinge_axis':'X','pour_rotation_axis':'Y','fold_rotation_degrees':90,'pour_pose_degrees':35,'lid_lift_m':.105,'grip_center_z_m':.259,'lid_knob_top_z_m':.176,'grip_underside_clearance_m':.073,'scope':'Kinematic and geometric illustration, not a safety, load, friction, manufacturing or fluid-dynamics certification. Loose lid must be retained during pouring, as shown in manufacturer use photograph.'})
(R/'validation.json').write_text(json.dumps(validation,indent=2)+'\n');assert validation['all_pass']
