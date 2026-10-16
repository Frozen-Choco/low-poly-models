"""Low-sample geometry inspection, not canonical photography."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent));from build_assets import *
clear();bpy.ops.import_scene.gltf(filepath=str(A/'street_drain_grate/street_drain_grate.glb'));target=Vector((.20,.14,.025));cam=studio(target,.24);sc=bpy.context.scene;sc.cycles.samples=48;sc.render.resolution_x=sc.render.resolution_y=720
for name,off in [('welded_grid_top',(1,-1,1.3)),('welded_frame_underside',(1,-1,-1.3))]:
 if os.environ.get('DIAGNOSTIC_VIEW') and os.environ['DIAGNOSTIC_VIEW'] not in name:continue
 if 'underside' in name:
  for light in [o for o in bpy.context.scene.objects if o.type=='LIGHT']:
   light.location.z=2*target.z-light.location.z;light.rotation_euler=(target-light.location).to_track_quat('-Z','Y').to_euler()
 bpy.data.objects['Studio ground'].hide_render='underside' in name;cam.location=target+Vector(off)*.5;cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=.34;sc.render.filepath=str(OUT/(name+'_diagnostic.jpg'));bpy.ops.render.render(write_still=True)
