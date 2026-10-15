"""Prepare catalog and reproducible transfer manifest after review artifacts/tests exist."""
from pathlib import Path
import json,hashlib,os
R=Path(__file__).resolve().parents[1]
A=Path(os.environ.get('ASSET_OUTPUT_ROOT',str(R/'assets')))
IDS=['public_recycling_bin','railway_crossing_lowered']
cat=[]
for asset_id in IDS:
 f=A/asset_id
 m=json.loads((f/'metadata.json').read_text());m.update(title_ja='踏切警報機・遮断機（下降）' if f.name.startswith('railway') else '公共用分別回収ボックス',category='street',glb_bytes=(f/(f.name+'.glb')).stat().st_size,blend_bytes=(f/(f.name+'.blend')).stat().st_size)
 m['files_bytes']={p.name:p.stat().st_size for p in f.iterdir() if p.suffix in ['.glb','.blend','.jpg']};(f/'metadata.json').write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n');cat.append(m)
(R/'catalog.json').write_text(json.dumps(cat,ensure_ascii=False,indent=2)+'\n')
files=[]
# Explicit deliverable allowlist: never traverse a shared repository assets directory.
root_files=['README.md','catalog.json','validation.json','crossing_construction_audit.json','bin_construction_audit.json','docs/design-notes.md','scripts/build_assets.py','scripts/validate_assets.py','scripts/render_context.py','scripts/package_manifest.py','scripts/reframe_bin.py','scripts/audit_crossing.py','scripts/audit_bin.py','previews/context_daylight.jpg','previews/context_alternate_light.jpg','previews/context_review.blend','previews/input_provenance.json']
candidates=[(R/name,'generators/batch02b/'+name) for name in root_files]
for asset_id in IDS:
 for filename in [asset_id+'.glb',asset_id+'.blend','front_three_quarter.jpg','rear.jpg','preview.jpg','back.jpg','close_up.jpg','metadata.json']:
  candidates.append((A/asset_id/filename,'assets/street/'+asset_id+'/'+filename))
for p,dest in sorted(candidates,key=lambda item:item[1]):
 if not p.is_file():raise FileNotFoundError('Missing explicit deliverable: '+str(p))
 files.append({'local_path':str(p.relative_to(R)) if p.is_relative_to(R) else str(p),'repo_relative_path':dest,'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
(R/'manifest.json').write_text(json.dumps({'revision':'02b-r5','review_status':'pending independent review; hashes identify reviewed candidate only','files':files},indent=2)+'\n')
