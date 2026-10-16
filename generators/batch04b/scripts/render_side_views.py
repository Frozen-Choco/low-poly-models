import bpy,sys
from pathlib import Path
from mathutils import Vector
sys.path.insert(0,str(Path(__file__).resolve().parent));from build_assets import *
for slug in IDS:
 clear();f=A/slug;bpy.ops.import_scene.gltf(filepath=str(f/(slug+'.glb')));s=stats([o for o in bpy.context.scene.objects if o.type=='MESH']);target=(Vector(s['bounds_min'])+Vector(s['bounds_max']))/2;size=max(s['dimensions_m']);cam=studio(target,size);cam.location=target+Vector((3,0,1.1))*size;cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();bpy.context.scene.render.filepath=str(f/'side.jpg');bpy.ops.render.render(write_still=True)
