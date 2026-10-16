import bpy,sys,math,json,os,shutil,hashlib
from pathlib import Path
from mathutils import Vector,Matrix
sys.path.insert(0,str(Path(__file__).resolve().parent));import base_geometry as g
R=Path(__file__).resolve().parents[1];A=Path(os.environ.get('ASSET_OUTPUT_ROOT',str(R/'assets')))/'public_recycling_bin';E=R/'evidence';E.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(A/'public_recycling_bin.blend'));bpy.context.preferences.filepaths.save_version=0
sc=bpy.context.scene;studio=bpy.data.collections['PREVIEW STUDIO'];studio.hide_viewport=False;cam=sc.camera
sc.render.resolution_x=1000;sc.render.resolution_y=1000;sc.cycles.samples=32
obs=[o for o in sc.objects if o.type=='MESH' and 'service_group' in o];base={o.name:o.matrix_world.copy() for o in obs}
def shot(name,target,offset,scale,dest=A):
 target=Vector(target);cam.location=target+Vector(offset);cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=scale;sc.render.filepath=str(dest/(name+'.jpg'));bpy.ops.render.render(write_still=True)
def turn(p,angle,axis):return Matrix.Translation(p)@Matrix.Rotation(angle,4,axis)@Matrix.Translation(-p)
def pose(angle=0,lift=0,dy=0,unlock=False):
 T=turn(Vector((-.224,-.248,0)),-math.radians(angle),'Z');U=turn(Vector((.16,-.206,.62)),math.pi/2 if unlock else 0,'Y')
 for o in obs:
  group=o['service_group'];o.matrix_world=(T if group=='door' else T@U if group=='latch' else Matrix.Translation((0,dy,lift)) if group=='liner' else Matrix.Identity(4))@base[o.name]
def saveproof(name):
 bpy.ops.object.select_all(action='DESELECT')
 for o in obs:o.select_set(True)
 bpy.ops.export_scene.gltf(filepath=str(E/(name+'.glb')),export_format='GLB',use_selection=True,export_extras=True)
 bpy.ops.wm.save_as_mainfile(filepath=str(E/(name+'.blend')),compress=True)
shot('front_three_quarter',(0,0,.5),(1,-2.7,.95),1.68)
shot('rear',(0,0,.5),(-1,2.7,.9),1.68)
shot('close_up',(0,-.15,.84),(.25,-2,.35),.65)
shutil.copyfile(A/'front_three_quarter.jpg',A/'preview.jpg');shutil.copyfile(A/'rear.jpg',A/'back.jpg')
# Real underside, not a view through an opaque studio floor.
for o in studio.objects:
 if o.type=='MESH':o.hide_render=True
shot('underside',(0,0,.20),(1,-2,-1.5),1.35)
for o in studio.objects:
 if o.type=='MESH':o.hide_render=False
pose(110,unlock=True)
shot('service_open',(0,-.15,.48),(1.2,-3,1.1),1.65,E);saveproof('service_open')
# Cutaway hides only the right side panel and its folded returns, leaving floor/support.
cut=[o for o in obs if o.name.startswith(('Two millimetre folded side sheet','Side sheet folded return')) and o.location.x>0]
for o in cut:o.hide_render=True
shot('service_cutaway',(0,0,.45),(1.4,-2.5,.6),1.60,E)
for o in cut:o.hide_render=False
pose(110,.002,-.65,True)
shot('liner_removed',(0,-.3,.45),(1.4,-2.7,1.3),1.85,E);saveproof('liner_removed')
pose()
# Self-contained sheltered service-area context, with clear door operating area.
for o in studio.objects:
 if o.type=='MESH':o.hide_render=True
floor=g.mat('Context pale concrete',(.37,.38,.37),0,.9);wall=g.mat('Context warm shelter wall',(.58,.58,.55),0,.9);dark=g.mat('Context paver joints',(.11,.12,.12),0,.9)
g.box('Context paved ground',(0,0,-.035),(5,5,.07),floor,0)
for x in range(-2,3):g.box('Context paving joint',(x,0,.001),(.006,5,.002),dark,0)
for y in range(-2,3):g.box('Context paving joint',(0,y,.001),(5,.006,.002),dark,0)
g.box('Context sheltered wall',(0,.8,1.2),(5,.10,2.4),wall,.008)
g.box('Context wall base trim',(0,.735,.06),(5,.03,.12),dark,.001)
g.box('Context overhead shelter',(0,.2,2.4),(5,1.3,.10),wall,.008)
shot('context_daylight',(0,0,.6),(2,-3,1.5),2.7,E)
for o in studio.objects:
 if o.type=='LIGHT':o.data.energy*=.7;o.location.x*=-1
sc.world.node_tree.nodes['Background'].inputs[0].default_value=(.83,.75,.65,1)
shot('context_alternate_light',(0,0,.6),(2,-3,1.5),2.7,E)
bpy.ops.wm.save_as_mainfile(filepath=str(E/'context_review.blend'),compress=True)
(E/'render_provenance.json').write_text(json.dumps({'source_blend_sha256':hashlib.sha256((A/'public_recycling_bin.blend').read_bytes()).hexdigest(),'source_glb_sha256':hashlib.sha256((A/'public_recycling_bin.glb').read_bytes()).hexdigest(),'render_engine':'Cycles','samples':32,'threads':2,'resolution':[1000,1000],'pose_coordinates':'Blender Z-up meters','cutaway_hidden':[o.name for o in cut]},indent=2)+'\n')
