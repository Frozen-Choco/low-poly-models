import json,hashlib,os
from pathlib import Path
R=Path(__file__).resolve().parents[1];A=Path(os.environ.get('ASSET_OUTPUT_ROOT',str(R/'assets')));slug='stainless_kitchen_kettle';f=A/slug
m=json.loads((f/'metadata.json').read_text());m.update(revision='functional-r2',review_status='pending independent factual and functional approval',reference_urls=['https://miyazaki-ss.co.jp/product/%E3%82%B1%E3%83%88%E3%83%AB-2/','https://miyazaki-ss.co.jp/wp-content/uploads/2022/12/kettle-scaled.jpg','https://miyazaki-ss.co.jp/wp-content/uploads/2022/12/020_d.jpg','https://www.yoshikawa-lifestyle.com/products/aikata-stainless-kettle/'],construction='Fore-aft XZ arch; coaxial X pivots; separate fixed shoulders/cheeks and moving metal tangs. Lateral folding, Y-axis pouring. Loose lid requires retention; no safety certification.',files_bytes={p.name:p.stat().st_size for p in f.iterdir() if p.suffix in ['.jpg','.blend','.glb']});(f/'metadata.json').write_text(json.dumps(m,indent=2)+'\n');(R/'catalog.json').write_text(json.dumps([m],indent=2)+'\n')
files=[]
for name in [slug+'.glb',slug+'.blend','metadata.json','front_three_quarter.jpg','preview.jpg','side.jpg','top.jpg','rear.jpg','back.jpg','close_up.jpg']:files.append((f/name,'assets/household/'+slug+'/'+name))
for name in ['README.md','baseline/stainless_kitchen_kettle_before.glb','catalog.json','validation.json','mechanism_audit.json','swept_fold_audit.json','lid_extraction_audit.json','scripts/audit_mechanism.py','scripts/diagnostic_grip_and_sweep.py','docs/research-and-functional-review.md','scripts/build_kettle.py','scripts/verify_revision.py','scripts/package_manifest.py']+[str(p.relative_to(R)) for p in (R/'previews').iterdir() if p.suffix in ['.jpg','.blend']]:files.append((R/name,'generators/kettle_function_revision/'+name))
records=[]
for p,d in sorted(files,key=lambda x:x[1]):
 assert p.is_file(),p
 assert p.stat().st_size<100000000,p
 records.append(dict(local_path=str(p.relative_to(R)) if p.is_relative_to(R) else str(p),repo_relative_path=d,bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest()))
(R/'manifest.json').write_text(json.dumps(dict(revision='kettle-functional-r2',review_status='pending independent factual and functional approval',files=records),indent=2)+'\n')
