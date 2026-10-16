import bpy,json,hashlib,math
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];rows=[]
for slug,tests in {
 'stainless_perforated_colander':[('center_drain_is_open',(0,0,.2),False),('adjacent_base_material_exists',(.003,0,.2),True)],
 'wood_cooking_spatula':[('hanging_bore_is_open',(0,.134,.05),False),('hanging_bore_has_surrounding_wood',(.006,.134,.05),True)]}.items():
 p=R/'assets'/slug/(slug+'.glb');bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(p));dg=bpy.context.evaluated_depsgraph_get();results=[]
 for name,origin,expected in tests:
  hit,*_=bpy.context.scene.ray_cast(dg,Vector(origin),Vector((0,0,-1)),distance=.5);results.append({'test':name,'origin':origin,'direction':[0,0,-1],'expected_hit':expected,'actual_hit':bool(hit),'pass':hit==expected})
 rows.append({'asset':slug,'source_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'checks':results})
(R/'evidence/use_checks.json').write_text(json.dumps(rows,indent=2)+'\n');print(json.dumps(rows,indent=2))
