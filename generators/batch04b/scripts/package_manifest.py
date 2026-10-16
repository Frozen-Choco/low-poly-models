import os,json,hashlib
from pathlib import Path
R=Path(os.environ.get('ASSET_OUTPUT_ROOT',str(Path(__file__).resolve().parents[1])))
ids=['taped_shipping_box','office_stapler','a4_clipboard'];catalog=[]
for slug in ids:
 p=R/'assets'/slug/'metadata.json';m=json.loads(p.read_text());m['glb_bytes']=(p.parent/(slug+'.glb')).stat().st_size;m['blend_bytes']=(p.parent/(slug+'.blend')).stat().st_size;catalog.append(m);p.write_text(json.dumps(m,indent=2,ensure_ascii=False)+'\n')
(R/'catalog.json').write_text(json.dumps(catalog,indent=2,ensure_ascii=False)+'\n')
files={str(p.relative_to(R)):{'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in sorted(R.rglob('*')) if p.is_file() and p.name!='manifest.json' and p.suffix not in ['.log','.pyc'] and '__pycache__' not in p.parts}
(R/'manifest.json').write_text(json.dumps({'files':files},indent=2)+'\n');print('Frozen',len(files),'files')
