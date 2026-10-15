"""Optional refresh of bin studio full views; geometry unchanged."""
import bpy,json,os,shutil
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];A=Path(os.environ.get('ASSET_OUTPUT_ROOT',str(R/'assets')));f=A/'public_recycling_bin';m=json.loads((f/'metadata.json').read_text());bpy.ops.wm.open_mainfile(filepath=str(f/'public_recycling_bin.blend'));bpy.context.preferences.filepaths.save_version=0
sc=bpy.context.scene;cam=sc.camera;studio=bpy.data.collections['PREVIEW STUDIO'];studio.hide_viewport=False
center=(Vector(m['bounds_min'])+Vector(m['bounds_max']))/2;sz=max(m['dimensions_m']);cam.data.ortho_scale=sz*1.65
for n,offset in [('front_three_quarter',(1,-2.7,.95)),('rear',(-1,2.7,.9))]:
 cam.location=center+Vector(offset)*sz;cam.rotation_euler=(center-cam.location).to_track_quat('-Z','Y').to_euler();sc.render.filepath=str(f/(n+'.jpg'));bpy.ops.render.render(write_still=True)
cam.location=center+Vector((1,-2.7,.95))*sz;cam.rotation_euler=(center-cam.location).to_track_quat('-Z','Y').to_euler();studio.hide_viewport=True;bpy.ops.wm.save_as_mainfile(filepath=str(f/'public_recycling_bin.blend'),compress=True)
shutil.copyfile(f/'front_three_quarter.jpg',f/'preview.jpg');shutil.copyfile(f/'rear.jpg',f/'back.jpg')
print('REFRAME_DONE',flush=True)
