import bpy,json,os,sys,hashlib,math
from pathlib import Path
from mathutils import Vector
sys.path.insert(0,str(Path(__file__).resolve().parent));from build_assets import *
P=OUT/'previews';P.mkdir(exist_ok=True);reports=[]
for slug in IDS:
 f=A/slug;bpy.ops.wm.open_mainfile(filepath=str(f/(slug+'.blend')));s=stats([o for o in bpy.context.scene.objects if o.type=='MESH']);clear();bpy.ops.import_scene.gltf(filepath=str(f/(slug+'.glb')));t=stats([o for o in bpy.context.scene.objects if o.type=='MESH']);checks={'finite_coordinates':all(math.isfinite(v) for o in bpy.context.scene.objects if o.type=='MESH' for vert in o.data.vertices for v in vert.co),'triangle_count_matches':s['triangles']==t['triangles'],'no_degenerate_triangles':s['zero_area_triangles']==t['zero_area_triangles']==0,'dimensions_match':max(abs(a-b) for a,b in zip(s['dimensions_m'],t['dimensions_m']))<.00001,'parts_match':s['mesh_objects']==t['mesh_objects'],'self_contained_images':all(im.packed_file or im.source!='FILE' for im in bpy.data.images),'under_100MB':all(p.stat().st_size<100000000 for p in f.iterdir()),'canonical_aliases':(f/'preview.jpg').read_bytes()==(f/'front_three_quarter.jpg').read_bytes() and (f/'back.jpg').read_bytes()==(f/'rear.jpg').read_bytes()};reports.append(dict(asset=slug,blend=s,glb=t,checks=checks,all_pass=all(checks.values())))
(OUT/'validation.json').write_text(json.dumps(reports,indent=2)+'\n')
clear();provenance=[]
for slug,offset in [('taped_shipping_box',(.19,.11,0)),('a4_clipboard',(-.17,-.03,0)),('office_stapler',(.08,-.16,0))]:
 f=A/slug/(slug+'.glb');bpy.ops.import_scene.gltf(filepath=str(f))
 for o in bpy.context.selected_objects:
  if o.parent is None:o.location+=Vector(offset)
 provenance.append(dict(asset=slug,sha256=hashlib.sha256(f.read_bytes()).hexdigest(),placement_m=offset))
stone=mat('Office desktop satin laminate',(.21,.19,.16),0,.7);plaster=mat('Warm office wall',(.55,.54,.50),0,.9)
box('Desk physical support',(0,0,-.025),(1.5,.9,.05),stone,.008);box('Office backdrop wall',(0,.42,.40),(1.5,.025,.85),plaster,.001)
sc=bpy.context.scene;sc.render.engine='CYCLES';sc.cycles.samples=24;sc.cycles.use_denoising=False;sc.render.threads_mode='FIXED';sc.render.threads=2;sc.render.resolution_x=1100;sc.render.resolution_y=800;sc.render.resolution_percentage=100;sc.render.image_settings.file_format='JPEG';sc.render.image_settings.quality=94;sc.view_settings.view_transform='AgX';sc.world.color=(.3,.3,.3)
bpy.ops.object.camera_add(location=(.75,-1.18,.75));cam=bpy.context.object;target=Vector((0,0,.08));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=.94;sc.camera=cam
bpy.ops.object.light_add(type='AREA',location=(-.5,-.1,1));key=bpy.context.object;key.data.energy=75;key.data.size=.75;key.rotation_euler=(target-key.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.light_add(type='AREA',location=(.65,.1,.7));fill=bpy.context.object;fill.data.energy=30;fill.data.size=.7;fill.rotation_euler=(target-fill.location).to_track_quat('-Z','Y').to_euler()
for name,loc,col in [('context_daylight',(-.5,-.1,1),(1,1,1)),('context_alternate_light',(.5,.15,.9),(1,.78,.54))]:
 key.location=loc;key.data.color=col;key.rotation_euler=(target-key.location).to_track_quat('-Z','Y').to_euler();sc.render.filepath=str(P/(name+'.jpg'));bpy.ops.render.render(write_still=True)
bpy.ops.wm.save_as_mainfile(filepath=str(P/'context_review.blend'),compress=True);(P/'input_provenance.json').write_text(json.dumps(provenance,indent=2)+'\n')
assert all(r['all_pass'] for r in reports),reports
