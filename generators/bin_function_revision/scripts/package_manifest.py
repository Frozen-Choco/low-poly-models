"""Freeze reviewed deliverables and canonical repository paths. Run after rendering/validation."""
from pathlib import Path
import json,hashlib,os
R=Path(__file__).resolve().parents[1];A=Path(os.environ.get('ASSET_OUTPUT_ROOT',str(R/'assets')))/'public_recycling_bin';E=R/'evidence'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
m=json.loads((A/'metadata.json').read_text());v=json.loads((E/'service_validation.json').read_text())
for ext in ['blend','glb']:
 assert v[ext]['sha256']==sha(A/('public_recycling_bin.'+ext))
 for k in ['latch_sweep_1deg_collisions','door_sweep_0_110deg_step025_collisions','liner_extraction_1mm_collisions']:assert not v[ext][k],(ext,k)
 assert not v[ext]['continuous_initial_lift']['overlapping_obstacles']
 assert not v[ext]['continuous_raised_extraction_swept_aabb']['overlapping_obstacles']
 assert all(abs(x)<1e-6 for x in v[ext]['support_gaps_m'].values())
m.update({'revision':'bin_function_revision','glb_bytes':(A/'public_recycling_bin.glb').stat().st_size,'blend_bytes':(A/'public_recycling_bin.blend').stat().st_size,'source':'generators/bin_function_revision/scripts/build_bin.py','service_door_pivot_m':[-.224,-.248,0],'service_door_open_degrees':110,'liner_height_m':.525,'review_status':'independently reviewed exact production binary hashes; static and service geometry checks passed','sha256':{e:sha(A/('public_recycling_bin.'+e)) for e in ['blend','glb']},'limitations':['Generic inferred design, not a brand replica','One mixed can/bottle collection stream','Static closed production files; service poses supplied separately','No manufacturing, structural, accessibility, weatherproofing or installation certification']})
m['files_bytes']={p.name:p.stat().st_size for p in A.iterdir() if p.suffix in ['.glb','.blend','.jpg']}
(A/'metadata.json').write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n')
row={k:m[k] for k in ['id','title_ja','category','dimensions_m','triangles','glb_bytes','blend_bytes']};row.update({'preview':'assets/street/public_recycling_bin/preview.jpg','back':'assets/street/public_recycling_bin/back.jpg','glb':'assets/street/public_recycling_bin/public_recycling_bin.glb','blend':'assets/street/public_recycling_bin/public_recycling_bin.blend'})
(R/'catalog_entry.json').write_text(json.dumps(row,ensure_ascii=False,indent=2)+'\n')
files=[]
# Production assets can be outside the generator tree in published layout.
# Always enumerate the selected A explicitly, avoiding stale local assets.
asset_paths=[p for p in A.rglob('*') if p.is_file()]
support_paths=[p for p in R.rglob('*') if p.is_file() and not p.is_relative_to(R/'assets') and not p.is_relative_to(A)]
for p in sorted(set(asset_paths+support_paths)):
 if '__pycache__' in p.parts or 'reference' in p.parts or p.suffix=='.log' or p.name=='manifest.json':continue
 if p.is_relative_to(A):
  tail=p.relative_to(A).as_posix();rel='assets/public_recycling_bin/'+tail;dest='assets/street/public_recycling_bin/'+tail
 else:
  rel=p.relative_to(R).as_posix();dest='generators/bin_function_revision/'+rel
 files.append({'source':str(p.resolve()),'relative_path':rel,'repository_path':dest,'bytes':p.stat().st_size,'sha256':sha(p)})
manifest={'revision':'bin_function_revision','production_state':'closed static','canonical_asset':'assets/street/public_recycling_bin','files':files,'excluded':'Private manufacturer reference images, logs and Python caches'}
(R/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
print('MANIFEST_SHA256',sha(R/'manifest.json'));print('FILES',len(files))
