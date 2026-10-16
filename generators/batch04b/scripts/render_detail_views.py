import bpy,sys
from pathlib import Path
from mathutils import Vector
sys.path.insert(0,str(Path(__file__).resolve().parent));from build_assets import *
for slug,tgt,scale in [('taped_shipping_box',(.125,0,.192),.18),('office_stapler',(0,-.051,.024),.085),('a4_clipboard',(0,.142,.007),.12)]:
 clear();f=A/slug;bpy.ops.import_scene.gltf(filepath=str(f/(slug+'.glb')));s=stats([o for o in bpy.context.scene.objects if o.type=='MESH']);target=Vector(tgt);size=max(s['dimensions_m']);cam=studio(target,size);cam.location=target+Vector((2,-3,3))*size;cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=scale;bpy.context.scene.cycles.samples=56;bpy.context.scene.render.filepath=str(f/'detail.jpg');bpy.ops.render.render(write_still=True)
