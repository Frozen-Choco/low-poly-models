import bpy,json
from pathlib import Path
R=Path(__file__).resolve().parents[1];result={}
for typ in ['blend','glb']:
 p=R/'assets/furniture/open_shelf'/('open_shelf.'+typ)
 if typ=='blend':bpy.ops.wm.open_mainfile(filepath=str(p))
 else:bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(p))
 bounds={}
 for name in ['Rear diagonal A','Rear diagonal B']:
  o=bpy.data.objects[name];ys=[(o.matrix_world@v.co).y for v in o.data.vertices];bounds[name]=[min(ys),max(ys)];assert abs(max(ys)-min(ys)-.003)<1e-6
 gap=bounds['Rear diagonal B'][0]-bounds['Rear diagonal A'][1];clear=bounds['Rear diagonal A'][0]-.175;assert gap>.00199 and clear>.00949
 result[typ]={'brace_y_bounds':bounds,'crossing_clearance_m':gap,'board_clearance_m':clear}
(R/'brace_basis_check.json').write_text(json.dumps(result,indent=2)+'\n')
