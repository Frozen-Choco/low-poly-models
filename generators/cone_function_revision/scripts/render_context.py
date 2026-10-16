"""Render exact revised saved GLB beside approved props; record every input hash."""
import bpy,sys,os,json,hashlib
from pathlib import Path
from mathutils import Vector
sys.path.insert(0,str(Path(__file__).resolve().parent))
from build_cone import material
SUPPORT=Path(__file__).resolve().parents[1];ROOT=Path(os.environ.get('ASSET_OUTPUT_ROOT',str(SUPPORT)));REF=Path(os.environ.get('REFERENCE_ASSET_ROOT',str(ROOT)));E=SUPPORT/'evidence'
bpy.ops.wm.read_factory_settings(use_empty=True);s=bpy.context.scene;s.unit_settings.system='METRIC';s.unit_settings.scale_length=1
inputs=[]
for slug,offset in [('streetlight',(-1.6,.55,0)),('park_bench',(.2,.45,0)),('traffic_cone',(1.2,-.75,0))]:
 root=ROOT if slug=='traffic_cone' else REF;p=root/'assets'/'street'/slug/(slug+'.glb');inputs.append({'asset':slug,'canonical_path':'assets/street/'+slug+'/'+slug+'.glb','sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size,'translation_m':offset})
 old=set(s.objects);bpy.ops.import_scene.gltf(filepath=str(p))
 for o in set(s.objects)-old:
  if o.parent is None:o.location+=Vector(offset)
def cube(name,loc,size,mat,bevel):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.name=name;o.dimensions=size;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(mat);m=o.modifiers.new('Small edge radius','BEVEL');m.width=bevel;m.segments=3
pave=material('Neutral concrete',(.24,.245,.25),.91);kerb=material('Concrete curb',(.37,.37,.36),.90);road=material('Asphalt',(.075,.076,.078),.97)
for x in range(-4,4):
 for y in range(-2,3):cube('Pavement slab',(x*.6+.3,y*.6+.3,-.065),(.594,.594,.13),pave,.004)
for x in range(-4,4):cube('Curb edge',(x*.6+.3,-1.29,-.06),(.595,.18,.14),kerb,.008)
cube('Road',(0,-2.1,-.18),(4.8,1.45,.10),road,.005)
s.world=bpy.data.worlds.new('Neutral daylight');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs[0].default_value=(.8,.8,.8,1);s.world.node_tree.nodes['Background'].inputs[1].default_value=.45
bpy.ops.object.light_add(type='AREA',location=(-3,-4,8));key=bpy.context.object;key.data.energy=1700;key.data.size=5
bpy.ops.object.camera_add(location=(5,-8,4.5));cam=bpy.context.object;target=Vector((0,0,1.5));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=6;s.camera=cam
s.render.engine='CYCLES';s.cycles.samples=48;s.cycles.use_denoising=False;s.render.resolution_x=1200;s.render.resolution_y=1100;s.render.resolution_percentage=100;s.render.image_settings.file_format='JPEG';s.render.image_settings.quality=94;s.view_settings.view_transform='AgX'
for name,pos in [('context_daylight',(-3,-4,8)),('context_alternate_light',(4,2,7))]:
 key.location=pos;key.rotation_euler=(Vector((0,0,1))-key.location).to_track_quat('-Z','Y').to_euler();s.render.filepath=str(E/(name+'.jpg'));bpy.ops.render.render(write_still=True)
bpy.ops.wm.save_as_mainfile(filepath=str(E/'context.blend'),compress=True)
(E/'context_inputs.json').write_text(json.dumps({'inputs':inputs,'scale':'meters, imported without resizing','lighting':'neutral daylight and alternate area-light direction','scope':'Exact revised cone with already-reviewed streetlight and park bench; context scene only, not a new production asset.'},indent=2))
