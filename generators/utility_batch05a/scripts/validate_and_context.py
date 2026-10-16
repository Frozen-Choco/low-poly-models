import bpy,json,os,sys,hashlib,math
from pathlib import Path
from mathutils import Vector,Matrix
sys.path.insert(0,str(Path(__file__).resolve().parent));from build_assets import *
P=OUT/'previews';P.mkdir(exist_ok=True);reports=[]
for slug in IDS:
 f=A/slug;bpy.ops.wm.open_mainfile(filepath=str(f/(slug+'.blend')));s=stats([o for o in bpy.context.scene.objects if o.type=='MESH']);clear();bpy.ops.import_scene.gltf(filepath=str(f/(slug+'.glb')));t=stats([o for o in bpy.context.scene.objects if o.type=='MESH']);checks={'finite_coordinates':all(math.isfinite(v) for o in bpy.context.scene.objects if o.type=='MESH' for vert in o.data.vertices for v in vert.co),'triangle_count_matches':s['triangles']==t['triangles'],'no_degenerate_triangles':s['zero_area_triangles']==t['zero_area_triangles']==0,'dimensions_match':max(abs(a-b) for a,b in zip(s['dimensions_m'],t['dimensions_m']))<.00001,'parts_match':s['mesh_objects']==t['mesh_objects'],'self_contained_images':all(im.packed_file or im.source!='FILE' for im in bpy.data.images),'under_100MB':all(p.stat().st_size<100000000 for p in f.iterdir()),'canonical_aliases':(f/'preview.jpg').read_bytes()==(f/'front_three_quarter.jpg').read_bytes() and (f/'back.jpg').read_bytes()==(f/'rear.jpg').read_bytes()};reports.append(dict(asset=slug,blend=s,glb=t,checks=checks,all_pass=all(checks.values())))
(OUT/'validation.json').write_text(json.dumps(reports,indent=2)+'\n')
clear();provenance=[]
for slug,offset in [('round_wooden_stool',(-.24,0,0)),('plastic_bail_bucket',(.23,-.04,0)),('wall_clock',(.12,.39,.95))]:
 f=A/slug/(slug+'.glb');bpy.ops.import_scene.gltf(filepath=str(f))
 for o in bpy.context.selected_objects:
  if o.parent is None:o.location+=Vector(offset)
 provenance.append(dict(asset=slug,sha256=hashlib.sha256(f.read_bytes()).hexdigest(),placement_m=offset))
floor=mat('Home floor natural warm gray',(.28,.26,.225),0,.72);plaster=mat('Home plaster warm offwhite',(.63,.61,.56),0,.92)
box('Floor physical support',(0,0,-.025),(2,1.8,.05),floor,.003);box('Home wall with clock contact',(0,.407,1),(2,.022,2.1),plaster,.001)
bpy.data.objects['Front glass disc'].visible_shadow=False
# Clock back feet are at y=.006 in local coordinates; wall front is .396.
box('Wall baseboard',(0,.381,.045),(2,.03,.09),mat('Painted baseboard',(.72,.70,.65),0,.52),.002)
sc=bpy.context.scene;sc.render.engine='CYCLES';sc.cycles.samples=32;sc.cycles.use_denoising=False;sc.render.threads_mode='FIXED';sc.render.threads=2;sc.render.resolution_x=950;sc.render.resolution_y=1100;sc.render.resolution_percentage=100;sc.render.image_settings.file_format='JPEG';sc.render.image_settings.quality=94;sc.view_settings.view_transform='AgX';sc.world.color=(.3,.3,.3)
bpy.ops.object.camera_add(location=(1.5,-2.6,1.65));cam=bpy.context.object;target=Vector((0,.10,.67));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=1.65;sc.camera=cam
bpy.ops.object.light_add(type='AREA',location=(-1,-1,2.4));key=bpy.context.object;key.data.energy=260;key.data.size=1.4;key.rotation_euler=(target-key.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.light_add(type='AREA',location=(1,-.3,1.8));fill=bpy.context.object;fill.data.energy=100;fill.data.size=1.1;fill.rotation_euler=(target-fill.location).to_track_quat('-Z','Y').to_euler()
for name,loc,col in [('context_daylight',(-1,-1,2.4),(1,1,1)),('context_alternate_light',(1,-.5,2),(1,.78,.54))]:
 key.location=loc;key.data.color=col;key.rotation_euler=(target-key.location).to_track_quat('-Z','Y').to_euler();sc.render.filepath=str(P/(name+'.jpg'));bpy.ops.render.render(write_still=True)
bpy.ops.wm.save_as_mainfile(filepath=str(P/'context_review.blend'),compress=True);(P/'input_provenance.json').write_text(json.dumps(provenance,indent=2)+'\n')
assert all(r['all_pass'] for r in reports),reports
