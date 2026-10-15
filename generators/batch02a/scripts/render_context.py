"""Render the exported GLBs together at real scale under two neutral light angles."""
import bpy,sys,os
from pathlib import Path
from mathutils import Vector
sys.path.insert(0,str(Path(__file__).resolve().parent))
from build_assets import mat,cube
SUPPORT=Path(__file__).resolve().parents[1]
ROOT=Path(os.environ.get('ASSET_OUTPUT_ROOT',str(SUPPORT)))
bpy.ops.wm.read_factory_settings(use_empty=True)
s=bpy.context.scene;s.unit_settings.system='METRIC';s.unit_settings.scale_length=1
for slug,offset in [('streetlight',(-1.6,.55,0)),('park_bench',(.2,.45,0)),('traffic_cone',(1.5,-.85,0))]:
 old=set(s.objects);bpy.ops.import_scene.gltf(filepath=str(ROOT/'assets'/'street'/slug/(slug+'.glb')))
 for o in set(s.objects)-old:
  if o.parent is None:o.location+=Vector(offset)
pave=mat('Fine neutral concrete',(.24,.245,.25),.91);kerb=mat('Concrete curb',(.37,.37,.36),.90);road=mat('Asphalt surface',(.075,.076,.078),.97)
for x in range(-4,4):
 for y in range(-2,3):cube('Pavement slab',(x*.6+.3,y*.6+.3,-.065),(.594,.594,.13),pave,.004)
for x in range(-4,4):cube('Curb edge',(x*.6+.3,-1.29,-.06),(.595,.18,.14),kerb,.008)
cube('Road plane',(0,-2.1,-.18),(4.8,1.45,.10),road,.005)
s.world=bpy.data.worlds.new('Neutral daylight');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs[0].default_value=(.8,.8,.8,1);s.world.node_tree.nodes['Background'].inputs[1].default_value=.45
bpy.ops.object.light_add(type='AREA',location=(-3,-4,8));key=bpy.context.object;key.data.energy=1700;key.data.size=5
bpy.ops.object.camera_add(location=(6,-9,6));cam=bpy.context.object;target=Vector((0,0,1.6));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=7.0;s.camera=cam
s.render.engine='CYCLES';s.cycles.samples=64;s.cycles.use_denoising=False;s.render.resolution_x=1200;s.render.resolution_y=1100;s.render.resolution_percentage=100;s.render.image_settings.file_format='JPEG';s.render.image_settings.quality=94;s.view_settings.view_transform='AgX'
folder=SUPPORT/'context';folder.mkdir(exist_ok=True)
for name,pos in [('daylight',(-3,-4,8)),('alternate_light',(4,2,7))]:
 key.location=pos;key.rotation_euler=(Vector((0,0,1))-key.location).to_track_quat('-Z','Y').to_euler();s.render.filepath=str(folder/(name+'.jpg'));bpy.ops.render.render(write_still=True)
bpy.ops.wm.save_as_mainfile(filepath=str(folder/'context.blend'),compress=True)
