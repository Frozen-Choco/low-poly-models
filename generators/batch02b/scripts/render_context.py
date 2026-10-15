import bpy,sys,math,os,json,hashlib
from pathlib import Path
from mathutils import Vector
sys.path.insert(0,str(Path(__file__).resolve().parent));from build_assets import box,mat
R=Path(__file__).resolve().parents[1];A=Path(os.environ.get('ASSET_OUTPUT_ROOT',str(R/'assets')));out=R/'previews';out.mkdir(exist_ok=True)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
provenance=[]
for slug,offset in [('railway_crossing_lowered',(0,0,0)),('public_recycling_bin',(-1.0,-.18,0))]:
 path=A/slug/(slug+'.glb');provenance.append({'id':slug,'glb_sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
 bpy.ops.import_scene.gltf(filepath=str(path))
 for o in bpy.context.selected_objects:
  if o.parent is None:o.location+=Vector(offset)
concrete=mat('Context concrete',(.32,.33,.34),0,.88);asphalt=mat('Context asphalt',(.075,.080,.087),0,.96);rail=mat('Context matte rail steel',(.15,.16,.17),.6,.5)
box('Road context',(2.45,0,-.075),(4.7,13,.15),asphalt,.0)
box('Pedestrian paved shoulder',(-.9,0,-.055),(2,13,.11),concrete,.0)
for y in range(-6,7):
 box('Paving joint',(-.9,y,-.001),(1.95,.008,.003),asphalt,0)
for y in [1.4,2.467]:
 box('Rail tread through crossing',(1.5,y,.006),(9,.06,.016),rail,.004)
 box('Rail flangeway',(1.5,y+.06,.003),(9,.035,.009),asphalt,0)
# Simple roadside posts communicate scale without importing third party assets.
for y in [-4,-2,4,6]:box('Shoulder edge marker',(.08,y,.30),(.10,.10,.60),concrete,.015)
sc=bpy.context.scene;sc.world.use_nodes=True;sc.world.node_tree.nodes['Background'].inputs[0].default_value=(.70,.75,.83,1);sc.world.node_tree.nodes['Background'].inputs[1].default_value=.6
bpy.ops.object.light_add(type='SUN',location=(-4,-7,9));sun=bpy.context.object;sun.data.energy=2.1;sun.data.angle=.12;sun.rotation_euler=(math.radians(26),math.radians(-23),math.radians(-28))
bpy.ops.object.camera_add(location=(7,-12,7));cam=bpy.context.object;target=Vector((1.2,.3,1.3));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=7.5;sc.camera=cam
sc.render.engine='CYCLES';sc.cycles.samples=64;sc.cycles.use_denoising=False;sc.render.resolution_x=1400;sc.render.resolution_y=1050;sc.render.resolution_percentage=100;sc.render.image_settings.file_format='JPEG';sc.render.image_settings.quality=92;sc.view_settings.view_transform='AgX'
for n,rot in [('context_daylight',(26,-23,-28)),('context_alternate_light',(42,35,110))]:
 sun.rotation_euler=tuple(math.radians(a) for a in rot);sc.render.filepath=str(out/(n+'.jpg'));bpy.ops.render.render(write_still=True)
bpy.ops.wm.save_as_mainfile(filepath=str(out/'context_review.blend'),compress=True)

(out/'input_provenance.json').write_text(json.dumps(provenance,indent=2)+'\n')
