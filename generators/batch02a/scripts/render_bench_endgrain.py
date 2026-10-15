"""Additional close-up of real slat end-grain and supporting joints."""
import bpy,os
from pathlib import Path
from mathutils import Vector
SUPPORT=Path(__file__).resolve().parents[1];ROOT=Path(os.environ.get('ASSET_OUTPUT_ROOT',str(SUPPORT)));folder=ROOT/'assets'/'street'/'park_bench'
bpy.ops.wm.open_mainfile(filepath=str(folder/'park_bench.blend'));s=bpy.context.scene;bpy.data.collections['PREVIEW STUDIO'].hide_viewport=False
center=Vector((.80,-.03,.47));cam=s.camera;cam.location=center+Vector((1.4,-.8,.65));cam.rotation_euler=(center-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=.45;s.render.filepath=str(folder/'endgrain.jpg');bpy.ops.render.render(write_still=True)
