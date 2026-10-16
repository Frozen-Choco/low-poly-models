# Read-only section diagnostics; never save a modified model.
import bpy,bmesh,json,hashlib
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1]
for slug in ['traffic_signal','railway_crossing_lowered']:
 for ext in ['blend','glb']:
  p=R/'assets'/slug/(slug+'.'+ext)
  if ext=='blend':bpy.ops.wm.open_mainfile(filepath=str(p));obs=list(bpy.data.collections['ASSET | '+slug].objects)
  else:bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(p));obs=list(bpy.context.scene.objects)
  if slug=='traffic_signal':point=Vector((.67,0,0));normal=Vector((1,0,0));target=(.67,.04,4.38);position=(3,.8,4.45);scale=.85
  else:point=Vector((0,0,0));normal=Vector((0,-1,0));target=(0,0,.26);position=(.4,-2,.5);scale=.57
  for o in obs:
   if o.type!='MESH':continue
   bm=bmesh.new();bm.from_mesh(o.data);inv=o.matrix_world.inverted();bmesh.ops.bisect_plane(bm,geom=list(bm.verts)+list(bm.edges)+list(bm.faces),dist=1e-7,plane_co=inv@point,plane_no=o.matrix_world.to_3x3().transposed()@normal,clear_outer=True,clear_inner=False);bm.to_mesh(o.data);bm.free()
  s=bpy.context.scene;s.render.engine='BLENDER_WORKBENCH';s.display.shading.light='STUDIO';s.display.shading.color_type='MATERIAL';s.display.shading.show_cavity=True;s.display.shading.show_shadows=True
  for o in s.objects:
   if o.type in ['CAMERA','LIGHT'] or o.name=='Plane':o.hide_render=True
  bpy.ops.object.camera_add(location=position);cam=bpy.context.object;cam.hide_render=False;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=scale;s.camera=cam;s.render.resolution_x=800;s.render.resolution_y=800;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.render.filepath=str(R/'functional'/f'{slug}_{ext}_section.png');bpy.ops.render.render(write_still=True)
