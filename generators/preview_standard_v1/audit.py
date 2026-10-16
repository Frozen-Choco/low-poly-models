"""Audit version files and asset records. python audit.py REPOSITORY_ROOT"""
from pathlib import Path
import sys,json,hashlib
from PIL import Image
R=Path(__file__).resolve().parent;ROOT=Path(sys.argv[1]).resolve()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
version=json.loads((R/'version.json').read_text())
for name,h in version['files'].items():assert sha(R/name)==h, name
inputs={e['id']:e for e in json.loads((R/'inputs.json').read_text())}
views=json.loads((R/'views.json').read_text())
for file in sorted((R/'published').glob('*.json')):
 rec=json.loads(file.read_text());entry=inputs[rec['asset']];assert sha(ROOT/entry['repo_path'])==entry['sha256']
 assert rec['reproduction_renderer_sha256']==sha(R/'render.py')
 assert rec['reproduction_spec_sha256']==sha(R/'standard.json')
 assert rec['detail_targets_sha256']==sha(R/'detail_targets.json')
 expected={v['path'] for v in views if v['asset']==rec['asset']}
 actual=[o['path'] for o in rec['outputs']]
 assert len(actual)==len(set(actual)), 'Duplicate output paths'
 assert set(actual)==expected, ('Incomplete or unexpected output paths', expected-set(actual), set(actual)-expected)
 assert rec['input']==entry
 declared={v['path']:v for v in views if v['asset']==rec['asset']}
 for out in rec['outputs']:
  assert out.get('alias_of')==declared[out['path']]['alias_of']
  assert out['original_render_record']['input_sha256']==entry['sha256']
  p=ROOT/out['path'];assert sha(p)==out['sha256'];im=Image.open(p);assert im.size==(1200,1200) and im.mode=='RGB'
  if out.get('alias_of'):
   target=ROOT/out['alias_of']
   if p.suffix=='.png':assert im.tobytes()==Image.open(target).convert('RGB').tobytes()
   else:assert p.read_bytes()==target.read_bytes()
 print('VERIFIED',rec['asset'],len(rec['outputs']))
print('VERSION_VERIFIED',version['version'])
