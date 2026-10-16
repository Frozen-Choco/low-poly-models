"""Frozen product-photography renderer. Imports GLB; writes images/records only.
blender -b -t 2 --python render.py -- ASSET_ID VIEW
SOURCE_ROOT optionally resolves portable repository-relative inputs.
"""
import bpy,json,sys,os,hashlib,time,math
from pathlib import Path
from mathutils import Vector,Matrix
from PIL import Image
R=Path(__file__).resolve().parent
RENDERER_HASH=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
SPEC=json.loads((R/'standard.json').read_text());SPEC_HASH=hashlib.sha256((R/'standard.json').read_bytes()).hexdigest()
INPUTS=json.loads((R/'inputs.json').read_text());DETAILS=json.loads((R/'detail_targets.json').read_text())
DETAIL_HASH=hashlib.sha256((R/'detail_targets.json').read_bytes()).hexdigest()
asset,name=sys.argv[sys.argv.index('--')+1:][:2];entry=next(e for e in INPUTS if e['id']==asset)
src=(Path(os.environ['SOURCE_ROOT'])/entry['repo_path']) if os.environ.get('SOURCE_ROOT') else R.parents[1]/entry['repo_path']
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert sha(src)==entry['sha256'], 'Input hash mismatch'
output=R/'repo'/Path(entry['repo_path']).parent;output.mkdir(parents=True,exist_ok=True)
record_path=R/'records'/asset/(name+'.json');record_path.parent.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(src))
meshes=[o for o in bpy.context.scene.objects if o.type=='MESH']
points=[o.matrix_world@v.co for o in meshes for v in o.data.vertices]
lo=Vector([min(v[i] for v in points) for i in range(3)]);hi=Vector([max(v[i] for v in points) for i in range(3)])
factor=2/max(hi-lo);base=Vector(((lo.x+hi.x)/2,(lo.y+hi.y)/2,lo.z));transform=Matrix.Scale(factor,4)@Matrix.Translation(-base)
for o in list(bpy.context.scene.objects):
 if o.parent is None:o.matrix_world=transform@o.matrix_world
bpy.context.view_layer.update();points=[o.matrix_world@v.co for o in meshes for v in o.data.vertices];center=Vector((0,0,(hi.z-lo.z)*factor/2))
def aim(obj,target):obj.rotation_euler=(Vector(target)-obj.location).to_track_quat('-Z','Y').to_euler()
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.device='CPU';s.cycles.samples=SPEC['samples'];s.cycles.use_denoising=False;s.cycles.use_adaptive_sampling=True;s.cycles.adaptive_threshold=SPEC['adaptive_threshold']
for k in ['seed','use_animated_seed','adaptive_min_samples','max_bounces','diffuse_bounces','glossy_bounces','transmission_bounces','transparent_max_bounces','volume_bounces','sample_clamp_direct','sample_clamp_indirect','use_light_tree']:setattr(s.cycles,k,SPEC[k])
s.render.threads_mode='FIXED';s.render.threads=2;s.render.resolution_x=s.render.resolution_y=1200;s.render.resolution_percentage=100;s.render.filter_size=SPEC['pixel_filter_width']
s.view_settings.view_transform='AgX';s.view_settings.look=SPEC['look'];s.view_settings.exposure=0;s.view_settings.gamma=1;s.display_settings.display_device='sRGB'
s.world=bpy.data.worlds.new('Neutral world');s.world.use_nodes=True;bg=s.world.node_tree.nodes.get('Background');bg.inputs['Color'].default_value=(*SPEC['world_color'],1);bg.inputs['Strength'].default_value=SPEC['world_strength']
bpy.ops.mesh.primitive_plane_add(size=SPEC['floor_size'],location=(0,0,SPEC['floor_z']));floor=bpy.context.object;floor.name='Photography floor'
mat=bpy.data.materials.new('Neutral floor');mat.use_nodes=True;bs=mat.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=tuple(SPEC['floor_base_color']);bs.inputs['Roughness'].default_value=SPEC['floor_roughness'];floor.data.materials.append(mat)
for light in SPEC['lights']:
 data=bpy.data.lights.new(light['name'],'AREA');data.energy=light['energy'];data.shape='DISK';data.size=light['size'];data.color=(1,1,1);obj=bpy.data.objects.new(light['name'],data);s.collection.objects.link(obj)
data=bpy.data.cameras.new('Standard camera');camera=bpy.data.objects.new('Standard camera',data);s.collection.objects.link(camera);s.camera=camera;data.type='ORTHO';data.lens=50
mapping={'side':'right','underside_axial':'underside','alternate_light':'preview'};view=mapping.get(name,name)
detail=DETAILS.get(asset,{}).get(name);focus_points=points;target=center.copy();span=None
if detail:
 direction=Vector(detail['direction']).normalized()
 if 'mesh_name_contains' in detail:
  chosen=[o for o in meshes if any(term.lower() in o.name.lower() for term in detail['mesh_name_contains'])];assert chosen,(asset,name,'no focus meshes')
  focus_points=[o.matrix_world@v.co for o in chosen for v in o.data.vertices]
 elif 'target_m' in detail:target=transform@Vector(detail['target_m']);span=detail['span_m']*factor
 else:
  h=(hi.z-lo.z)*factor
  if asset in ['whole_red_apple','ceramic_rice_bowl','traffic_cone']:
   focus_points=[v for v in points if v.z>h*.55]
  elif asset=='wooden_cutting_board':
   target=Vector((.35,-.15,h*.7));span=1.1
  elif asset=='park_bench':target=transform@Vector((.55,-.1,.44));span=.5*factor
  elif asset=='office_stapler':target=transform@Vector((0,-.058,.022));span=.07*factor
  elif asset=='taped_shipping_box':target=Vector((0,0,h));span=1.1
  else:raise ValueError(('Undefined detail focus',asset,name))
 if span is None:target=Vector([(min(v[i] for v in focus_points)+max(v[i] for v in focus_points))/2 for i in range(3)])
else:direction=Vector(SPEC['views'][view]).normalized()
camera.location=target+direction*10;aim(camera,target);bpy.context.view_layer.update();inv=camera.matrix_world.inverted();p=[inv@v for v in focus_points];xmin,xmax=min(v.x for v in p),max(v.x for v in p);ymin,ymax=min(v.y for v in p),max(v.y for v in p)
if span is None:
 camera.location+=camera.matrix_world.to_3x3()@Vector(((xmin+xmax)/2,(ymin+ymax)/2,0));data.ortho_scale=max(xmax-xmin,ymax-ymin)/.8
else:data.ortho_scale=span/.8
full_projected=[camera.matrix_world.inverted()@v for v in points]
full_span=max(max(v.x for v in full_projected)-min(v.x for v in full_projected),max(v.y for v in full_projected)-min(v.y for v in full_projected))
closeup_magnification=(full_span/.8)/data.ortho_scale
if name=='close_up':assert closeup_magnification>=1.2,('Close-up has insufficient magnification',asset,closeup_magnification)
base_rotation=Vector(SPEC['views']['preview']).normalized().to_track_quat('Z','Y').to_matrix();rotation=camera.rotation_euler.to_matrix()@base_rotation.inverted()
actual_lights=[]
for light in SPEC['lights']:
 obj=bpy.data.objects[light['name']];pos=Vector(light['location'])-center;at=Vector(SPEC['light_aim'])-center
 if name=='alternate_light':pos.x=-pos.x;at.x=-at.x
 obj.location=center+rotation@pos;aim(obj,center+rotation@at);actual_lights.append({'name':obj.name,'location':list(obj.location),'rotation':list(obj.rotation_euler),'energy':obj.data.energy,'size':obj.data.size})
transparent=direction.z<=0.1;floor.hide_render=transparent;s.render.film_transparent=transparent
s.render.image_settings.file_format='PNG' if transparent else 'JPEG';s.render.image_settings.color_mode='RGBA' if transparent else 'RGB';s.render.image_settings.quality=95
raw=R/'raw'/asset/(name+'.png');raw.parent.mkdir(parents=True,exist_ok=True);dest=output/(name+'.jpg');s.render.filepath=str(raw if transparent else dest)
start=time.monotonic();bpy.ops.render.render(write_still=True);elapsed=time.monotonic()-start
if transparent:
 im=Image.open(raw).convert('RGBA');Image.alpha_composite(Image.new('RGBA',im.size,(184,184,184,255)),im).convert('RGB').save(dest,quality=95,subsampling=0)
assert sha(src)==entry['sha256']
record={'asset':asset,'view':name,'input_repo_path':entry['repo_path'],'input_sha256':entry['sha256'],'input_git_sha':entry['git_sha'],'spec_sha256':SPEC_HASH,'renderer_sha256':RENDERER_HASH,'detail_plan_sha256':DETAIL_HASH,'closeup_magnification_vs_full_fit':closeup_magnification,'blender_version':bpy.app.version_string,'output_path':str(dest),'output_sha256':sha(dest),'bytes':dest.stat().st_size,'elapsed_seconds':elapsed,'sample_ceiling':SPEC['samples'],'adaptive_threshold':SPEC['adaptive_threshold'],'render_only_normalization':factor,'source_bounds':[list(lo),list(hi)],'camera_location':list(camera.location),'camera_rotation':list(camera.rotation_euler),'ortho_scale':data.ortho_scale,'focus':detail or 'full object','focus_projected_width_height':[xmax-xmin,ymax-ymin],'full_object_fit':not bool(detail),'lights':actual_lights,'fixed_background_srgb':[184,184,184] if transparent else None,'floor_hidden':transparent,'diagnostic_only':False}
record_path.write_text(json.dumps(record,indent=2));print('VERIFIED_COMPLETE',asset,name,elapsed)
