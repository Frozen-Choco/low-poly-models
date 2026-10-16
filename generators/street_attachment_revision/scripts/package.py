from pathlib import Path
import json,hashlib,shutil
R=Path(__file__).resolve().parents[1]
for slug in ['traffic_signal','railway_crossing_lowered']:
 f=R/'assets'/slug
 for a,b in [('preview.jpg','front_three_quarter.jpg'),('back.jpg','rear.jpg'),('detail.jpg','close_up.jpg')]:
  if (f/a).exists():shutil.copyfile(f/a,f/b)
 m=json.loads((f/'metadata.json').read_text())
 if 'palette_revision' in m and 'geometry_sha256' in m['palette_revision']:m['palette_revision']['historical_palette_input_geometry_sha256']=m['palette_revision'].pop('geometry_sha256')
 m['files_bytes']={p.name:p.stat().st_size for p in sorted(f.iterdir()) if p.suffix in ['.glb','.blend','.jpg']};m['functional_evidence']='../../functional/validation.json and ../../functional/assembly_test.json';m['construction_notes']='../../docs/attachment-revision.md'
 (f/'metadata.json').write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n')
rows=[]
for parent in ['assets','scripts','docs','baseline','functional','previews']:
 for p in sorted((R/parent).rglob('*')):
  if not p.is_file() or p.suffix not in ['.blend','.glb','.jpg','.png','.json','.md','.py','.sha256']:continue
  b=p.read_bytes();rows.append({'path':str(p.relative_to(R)),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest(),'git_blob':hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()})
(R/'manifest.json').write_text(json.dumps({'scope':['traffic_signal','railway_crossing_lowered'],'publication':'not performed; independent exact-file review required','files':rows},indent=2)+'\n')
print('Packaged',len(rows),'files')
