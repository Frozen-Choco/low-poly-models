import bpy,sys,math,os,json,hashlib
from pathlib import Path
from mathutils import Vector
sys.path.insert(0,str(Path(__file__).resolve().parent));from build_assets import box,mat,texture_material,cyl,tube
R=Path(__file__).resolve().parents[1];A=Path(os.environ.get('ASSET_OUTPUT_ROOT',str(R/'assets')));out=A.parent/'previews';out.mkdir(exist_ok=True)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
provenance=[]
for slug,offset in [('cast_iron_manhole',(-.3,-.35,-.080)),('concrete_curb_straight',(0,.65,-.14)),('steel_roadside_bollard',(.55,.99,.11))]:
 path=A/slug/(slug+'.glb');provenance.append({'id':slug,'glb_sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
 bpy.ops.import_scene.gltf(filepath=str(path));roots=[o for o in bpy.context.selected_objects if o.parent is None]
 for o in roots:o.location+=Vector(offset)
 bpy.context.view_layer.update()
 # Duplicate curb only for installation context. Not additional catalog assets.
 if slug=='concrete_curb_straight':
  original_curbs=[ob for ob in bpy.context.selected_objects if ob.type=='MESH']
  for x in [-1.21,-.605,.605,1.21]:
   for ob in original_curbs:
    if ob.type=='MESH':
     cp=ob.copy();cp.data=ob.data.copy();bpy.context.collection.objects.link(cp);cp.parent=None;cp.matrix_world=ob.matrix_world.copy();cp.location.x+=x
asphalt=texture_material('Context asphalt fine stone',(.055,.06,.065),.98,0,.33);conc=texture_material('Context concrete paving',(.30,.31,.30),.93,0,.2)
road=box('Asphalt with actual manhole opening',(0,-.8,-.075),(5,3,.15),asphalt,0)
cut=cyl('Temporary road opening cutter',(-.3,-.35,-.04),.359,.3,asphalt,N=128);bpy.context.view_layer.objects.active=road;mod=road.modifiers.new('Road opening around frame','BOOLEAN');mod.operation='DIFFERENCE';mod.object=cut;bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(cut,do_unlink=True)
for x in range(-3,4):
 for y in range(4):
  if x==1 and y==0:
   block=box('Inferred solid concrete bollard foundation',(x*.5,.99,-.07),(.496,.496,.36),conc,.002)
   bond=mat('Inferred buried adhesive bond',(.23,.17,.11),0,.95)
   for ax in [.55-.064,.55+.064]:
    for ay in [.99-.064,.99+.064]:
     cut=cyl('Temporary buried anchor bore',(ax,ay,.063),.007,.114,conc,N=48);bpy.context.view_layer.objects.active=block;mo=block.modifiers.new('Inferred concrete anchor bore','BOOLEAN');mo.operation='DIFFERENCE';mo.object=cut;bpy.ops.object.modifier_apply(modifier=mo.name);bpy.data.objects.remove(cut,do_unlink=True)
     tube('Inferred buried anchor bonding annulus',(ax,ay,.06),.007,.005,.10,bond,axis='Z')
  else:box('Sidewalk paving slab',(x*.5,.99+y*.5,.055),(.496,.496,.11),conc,.002)
sc=bpy.context.scene;sc.world.use_nodes=True;sc.world.node_tree.nodes['Background'].inputs[0].default_value=(.70,.75,.83,1);sc.world.node_tree.nodes['Background'].inputs[1].default_value=.5
bpy.ops.object.light_add(type='SUN',location=(-4,-7,9));sun=bpy.context.object;sun.data.energy=2;sun.data.angle=.12
bpy.ops.object.camera_add(location=(2.8,-4,3));cam=bpy.context.object;target=Vector((0,.35,.18));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=2.8;sc.camera=cam
sc.render.engine='CYCLES';sc.cycles.samples=48;sc.cycles.use_denoising=False;sc.render.threads_mode='FIXED';sc.render.threads=2;sc.render.resolution_x=1200;sc.render.resolution_y=950;sc.render.resolution_percentage=100;sc.render.image_settings.file_format='JPEG';sc.render.image_settings.quality=93;sc.view_settings.view_transform='AgX'
for n,rot in [('context_daylight',(26,-23,-28)),('context_alternate_light',(42,35,110))]:
 sun.rotation_euler=tuple(math.radians(a) for a in rot);sc.render.filepath=str(out/(n+'.jpg'));bpy.ops.render.render(write_still=True)
bpy.ops.wm.save_as_mainfile(filepath=str(out/'context_review.blend'),compress=True)
(out/'input_provenance.json').write_text(json.dumps(provenance,indent=2)+'\n')
