"""Freeze the explicit three-asset batch. Does not inspect or write unrelated assets."""
from pathlib import Path
import json,hashlib,os
R=Path(__file__).resolve().parents[1];A=Path(os.environ.get('ASSET_OUTPUT_ROOT',str(R/'assets')));O=A.parent
assert not (R/'NEEDS_TEXTURE_REBUILD').exists(), 'Texture rebuild still pending'
IDS=['cast_iron_manhole','concrete_curb_straight','steel_roadside_bollard'];titles=['鋳鉄製マンホール蓋と受枠','歩車道境界ブロック','鋼製車止めボラード'];cat=[]
for slug,title in zip(IDS,titles):
 f=A/slug;m=json.loads((f/'metadata.json').read_text());m.update(review_status='pending independent functional review',title_ja=title,glb_bytes=(f/(slug+'.glb')).stat().st_size,blend_bytes=(f/(slug+'.blend')).stat().st_size)
 m['reference_urls']=[s.replace('?no=401','?no=407') for s in m['reference_urls']]
 m['files_bytes']={p.name:p.stat().st_size for p in f.iterdir() if p.suffix in ['.glb','.blend','.jpg']};(f/'metadata.json').write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n');cat.append(m)
(O/'catalog.json').write_text(json.dumps(cat,ensure_ascii=False,indent=2)+'\n')
assert all(x['all_pass'] for x in json.loads((O/'validation.json').read_text())), 'Validation failed'
root_files=['README.md','docs/reference_notes.md','docs/functional_revision.md','scripts/build_assets.py','scripts/validate_assets.py','scripts/render_context.py','scripts/package_manifest.py','scripts/audit_context.py','scripts/functional_proof.py']
outputs=['context_geometry_audit.json','catalog.json','validation.json','previews/context_daylight.jpg','previews/context_alternate_light.jpg','previews/context_review.blend','previews/input_provenance.json']
proof_names=['manhole_underside','manhole_key_insertion','manhole_engaged_underside','manhole_parallel_lift','manhole_engagement_cutaway','bollard_drilled_underside','bollard_anchor_cutaway','curb_underside']
outputs += ['functional/'+n+ext for n in proof_names for ext in ['.jpg','.blend']]+['functional/functional_validation.json']
assert json.loads((O/'functional/functional_validation.json').read_text())['all_pass']
candidates=[(R/n,'generators/pavement_function_revision/'+n) for n in root_files]+[(O/n,'generators/pavement_function_revision/'+n) for n in outputs]
for slug in IDS:
 for n in [slug+'.glb',slug+'.blend','preview.jpg','back.jpg','front_three_quarter.jpg','rear.jpg','side.jpg','close_up.jpg','underside.jpg','metadata.json']:candidates.append((A/slug/n,'assets/street/'+slug+'/'+n))
files=[]
for p,dest in sorted(candidates,key=lambda x:x[1]):
 assert p.is_file(),str(p)
 assert p.stat().st_size<100000000,str(p)
 files.append({'local_path':str(p.relative_to(O)) if p.is_relative_to(O) else str(p),'repo_relative_path':dest,'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
(O/'manifest.json').write_text(json.dumps({'revision':'pavement-functional-r2','review_status':'pending independent review; frozen candidate','files':files},indent=2)+'\n')
print(hashlib.sha256((O/'manifest.json').read_bytes()).hexdigest())
