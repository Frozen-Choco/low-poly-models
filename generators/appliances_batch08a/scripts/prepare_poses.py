"""Derive render-only open poses from exact delivered GLBs, without modifying source files."""
import bpy,json,hashlib,sys
from pathlib import Path
R=Path(__file__).resolve().parents[1];out=R/'evidence/poses';out.mkdir(exist_ok=True)
args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
rows=json.loads((out/'provenance.json').read_text()) if args and (out/'provenance.json').exists() else []
rows=[r for r in rows if r['asset'] not in args]
for slug in ['microwave_oven','rice_cooker']:
 if args and slug not in args:continue
 src=R/'assets'/slug/(slug+'.glb')
 if not src.exists():src=R.parents[1]/'assets/appliances'/slug/(slug+'.glb')
 h=hashlib.sha256(src.read_bytes()).hexdigest();bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(src));bpy.context.scene.frame_set(61);bpy.context.view_layer.update()
 # Freeze evaluated world matrices, then remove animation and parenting. Geometry/materials unchanged.
 objects=[o for o in bpy.context.scene.objects if o.type=='MESH'];matrices={o.name:o.matrix_world.copy() for o in objects}
 for o in objects:o.animation_data_clear();o.parent=None;o.matrix_world=matrices[o.name]
 bpy.ops.object.select_all(action='DESELECT')
 for o in objects:o.select_set(True)
 (out/slug).mkdir(exist_ok=True);dst=out/slug/(slug+'_open.glb');bpy.ops.export_scene.gltf(filepath=str(dst),export_format='GLB',use_selection=True,export_animations=False,export_extras=True)
 assert hashlib.sha256(src.read_bytes()).hexdigest()==h
 rows.append({'asset':slug,'source':str(src),'source_sha256':h,'frame':61,'derived':str(dst.relative_to(R)),'derived_sha256':hashlib.sha256(dst.read_bytes()).hexdigest(),'purpose':'Render-only pose; same saved model geometry and material, rigid transform only. Not a second catalog asset.'})
(out/'provenance.json').write_text(json.dumps(rows,indent=2)+'\n')
