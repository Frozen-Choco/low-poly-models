import os,json,hashlib
from pathlib import Path
R=Path(os.environ.get('ASSET_OUTPUT_ROOT',str(Path(__file__).resolve().parents[1])))
refs={
'round_wooden_stool':['https://www.pinefactory.jp/product.php?code=stool-s-na','https://www.pinefactory.jp/upload/images/dining/stool/s-na/tool-skumi_a.jpg'],
'plastic_bail_bucket':['https://www.risu.co.jp/products/search/detail/t000100014292/','https://www.risu.co.jp/group/search/cad/BR8.pdf'],
'wall_clock':['https://www.seiko-clock.co.jp/product-personal/wall_clock/standard/qxa709b.html','https://www.seiko-clock.co.jp/product-personal/QXA709B_back.jpg','https://www.seiko-clock.co.jp/product-personal/up_files/AKX-055P.pdf']}
catalog=[]
for slug,urls in refs.items():
 p=R/'assets'/slug/'metadata.json';m=json.loads(p.read_text());m['references']=urls;m['functional_validation_files']=['numeric_use_validation.json','use_validation.json'];m['glb_bytes']=(p.parent/(slug+'.glb')).stat().st_size;m['blend_bytes']=(p.parent/(slug+'.blend')).stat().st_size;m['review_status']='Geometry/function candidate complete; diagnostic photos only, standardized photographs pending';p.write_text(json.dumps(m,indent=2,ensure_ascii=False)+'\n');catalog.append(m)
(R/'catalog.json').write_text(json.dumps(catalog,indent=2,ensure_ascii=False)+'\n')
files={str(p.relative_to(R)):{'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in sorted(R.rglob('*')) if p.is_file() and p.name!='manifest.json' and p.suffix not in ['.log','.pyc'] and '__pycache__' not in p.parts and 'reference' not in p.relative_to(R).parts}
assert all(v['bytes']<100000000 for v in files.values())
(R/'manifest.json').write_text(json.dumps({'files':files},indent=2)+'\n');print('Frozen',len(files),'files')
