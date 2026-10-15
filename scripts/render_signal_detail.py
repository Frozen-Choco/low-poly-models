"""Render the signal head close-up so roundness is visible, not hidden by distance."""
import bpy
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1]
f=ROOT/'assets/street/traffic_signal'
bpy.ops.wm.open_mainfile(filepath=str(f/'traffic_signal.blend'))
bpy.data.collections['PREVIEW STUDIO'].hide_viewport=False
s=bpy.context.scene;c=s.camera;target=Vector((.67,-.05,4.36));c.location=target+Vector((1.15,-2.4,.55));c.rotation_euler=(target-c.location).to_track_quat('-Z','Y').to_euler();c.data.ortho_scale=1.6
s.cycles.samples=128;s.cycles.use_denoising=False;s.render.filepath=str(f/'detail.png');bpy.ops.render.render(write_still=True)
