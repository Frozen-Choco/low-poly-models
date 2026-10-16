import bpy,json,os
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];A=Path(os.environ.get('ASSET_OUTPUT_ROOT',str(R/'assets')));O=A.parent
bpy.ops.wm.open_mainfile(filepath=str(O/'previews/context_review.blend'))
curbs=[o for o in bpy.context.scene.objects if o.type=='MESH' and o.name.startswith('Precast tapered curb')]
items=[]
for o in curbs:
 pts=[o.matrix_world@v.co for v in o.data.vertices];lo=[min(p[i] for p in pts) for i in range(3)];hi=[max(p[i] for p in pts) for i in range(3)];items.append({'name':o.name,'bounds_min':lo,'bounds_max':hi,'x_center':(lo[0]+hi[0])/2})
items.sort(key=lambda x:x['x_center']);expected=[-1.21,-.605,0,.605,1.21]
checks={'exactly_five_curb_segments':len(items)==5,'correct_spaced_centers':len(items)==5 and all(abs(x['x_center']-e)<1e-4 for x,e in zip(items,expected)),'correct_installation_height':all(abs(x['bounds_min'][2]+.14)<1e-4 and abs(x['bounds_max'][2]-.11)<1e-4 for x in items)}
block=next(o for o in bpy.context.scene.objects if o.name.startswith('Inferred solid concrete bollard foundation'))
bore_hits=[]
for x in [.55-.064,.55+.064]:
 for y in [.99-.064,.99+.064]:
  inv=block.matrix_world.inverted();hit,p,n,i=block.ray_cast(inv@Vector((x,y,.14)),inv.to_3x3()@Vector((0,0,-1)),distance=1);bore_hits.append((block.matrix_world@p).z if hit else None)
checks['saved_foundation_open_bores']=all(z is not None and abs(z-.006)<1e-5 for z in bore_hits)
report={'bore_bottom_hits':bore_hits,'checks':checks,'all_pass':all(checks.values()),'curbs':items};(O/'context_geometry_audit.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report));assert report['all_pass']
