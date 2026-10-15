import bpy,json,os
from pathlib import Path
from collections import defaultdict
from mathutils import Vector
R=Path(__file__).resolve().parents[1];A=Path(os.environ.get('ASSET_OUTPUT_ROOT',str(R/'assets')))
for o in list(bpy.data.objects):bpy.data.objects.remove(o,do_unlink=True)
bpy.ops.import_scene.gltf(filepath=str(A/'railway_crossing_lowered'/'railway_crossing_lowered.glb'))
counts=defaultdict(int);parts=[];bounds={}
for o in bpy.context.scene.objects:
 if o.type!='MESH':continue
 o.data.calc_loop_triangles();n=len(o.data.loop_triangles);parts.append((n,o.name))
 key='Other hardware'
 for words,category in [(('lens','optical','Fresnel'),'Optics'),(('hood',),'Sun hoods'),(('conduit','saddle','clamp band','cable','junction'),'Cable routing and clamps'),(('housing','cover','gasket','warning'),'Lamp/sounder housings'),(('Mast','mast stripe'),'Mast and base'),(('boom','Boom','Drive','drive','Barrier'),'Barrier assembly')]:
  if any(w.lower() in o.name.lower() for w in words):key=category;break
 counts[key]+=n
 if any(w in o.name for w in ['saddle','clamp band']):
  v=[o.matrix_world@p.co for p in o.data.vertices];bounds[o.name]={'min':[min(p[i] for p in v) for i in range(3)],'max':[max(p[i] for p in v) for i in range(3)]}
report={'triangles_by_group':dict(counts),'top_parts':sorted(parts,reverse=True)[:20],'clamp_component_bounds_m':bounds,'contact_calculation':{'mast_band_radius_m':.068,'bridge_x_extent_abs_m':[.014,.022],'bridge_y_extent_m':[.055,.115],'bridge_front_outer_corner_radius_m':(.022**2+.055**2)**.5,'saddle_y_extent_m':[.0985,.1235],'bridge_saddle_overlap_y_m':.115-.0985,'bridge_conduit_lateral_clearance_m':.014-.011,'notes':'Bridge front corners lie inside band radius; bridge rear overlaps saddle by 16.5 mm. Branch cable ends overlap lower lamp-gland cylindrical bounds. Lower trunk end enters mast body. Fasteners overlap saddle rear.'}}
(R/'crossing_construction_audit.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
