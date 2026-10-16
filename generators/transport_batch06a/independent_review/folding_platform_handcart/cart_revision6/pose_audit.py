import sys,json,hashlib
from pathlib import Path
sys.path.insert(0,'/workspace/scratch/a456259dbd5d/lowpoly_batch06a/scripts')
import validate_saved as V
from mathutils import Vector
import bpy
R=Path('/workspace/scratch/a456259dbd5d'); out={}
for slug in ['folding_platform_handcart']:
 for ext in ['blend','glb']:
  p=R/'lowpoly_batch06a/assets'/slug/(slug+'.'+ext);obs=V.load(p);meta=json.loads(p.with_name('metadata.json').read_text());r={'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'actual_saved_general':V.general(obs)}
  r['actual_saved_pose_tests']=V.bike_tests(obs,meta) if slug=='city_bicycle' else V.cart_tests(obs,meta)
  if slug=='folding_platform_handcart':
   saved={o.name:o.matrix_world.copy() for o in obs};handle=V.group(obs,'handle');tongue=V.selection(obs,'Moving handle lock tongue');bar=V.group(obs,'lock_release');r['engaged_lock_blocks_fold']=[]
   for deg in [0,2,5,10,15]:
    xf=V.matrix_about(Vector(V.D['cart']['hinge_pivot']),(1,0,0),deg)
    for o in handle:o.matrix_world=xf@saved[o.name]
    bpy.context.view_layer.update();r['engaged_lock_blocks_fold'].append({'degrees':deg,'contacts':V.candidate_hits(tongue,bar)})
  out[slug+'.'+ext]=r
(R/'reviews/batch06a/cart_revision6/pose_audit.json').write_text(json.dumps(out,indent=2))
