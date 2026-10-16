import json,hashlib,os
from pathlib import Path
R=Path(__file__).resolve().parents[1];A=Path(os.environ.get('ASSET_OUTPUT_ROOT',str(R/'assets')));IDS=['stainless_kitchen_kettle','ceramic_rice_bowl','wooden_cutting_board'];catalog=[];files=[]
for slug in IDS:
 f=A/slug;m=json.loads((f/'metadata.json').read_text());m['files_bytes']={p.name:p.stat().st_size for p in f.iterdir() if p.suffix in ['.glb','.blend','.jpg']};(f/'metadata.json').write_text(json.dumps(m,indent=2)+'\n');catalog.append(m)
 for name in [slug+'.glb',slug+'.blend','front_three_quarter.jpg','side.jpg','rear.jpg','close_up.jpg','preview.jpg','back.jpg','metadata.json']:
  files.append((f/name,'assets/household/'+slug+'/'+name))
(R/'catalog.json').write_text(json.dumps(catalog,indent=2)+'\n')
for name in ['README.md','catalog.json','validation.json','docs/design-notes.md','scripts/build_assets.py','scripts/validate_and_context.py','scripts/package_manifest.py','previews/context_daylight.jpg','previews/context_alternate_light.jpg','previews/context_review.blend','previews/input_provenance.json']:
 files.append((R/name,'generators/batch03a/'+name))
records=[]
for p,dest in sorted(files,key=lambda x:x[1]):
 assert p.is_file(),p
 assert p.stat().st_size<100000000,p
 records.append(dict(local_path=str(p.relative_to(R)) if p.is_relative_to(R) else str(p),repo_relative_path=dest,bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest()))
(R/'manifest.json').write_text(json.dumps(dict(revision='03a-r1',review_status='pending independent review; immutable candidate file hashes',files=records),indent=2)+'\n')
