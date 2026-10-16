"""Read-only audit of additive utility publication, runnable in a fresh root."""
from pathlib import Path
import json,hashlib
from PIL import Image
G=Path(__file__).resolve().parent;B=G.parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
version=json.loads((G/'version.json').read_text())
for n,h in version['files'].items():assert sha(G/n)==h,('configuration',n)
inputs=json.loads((G/'inputs.json').read_text());views=json.loads((G/'views.json').read_text());approval=json.loads((B/'reviews/batch05a/geometry_function_approval.json').read_text())
for a in approval['assets']:
 for f in a['files']:
  p=B/'assets/household'/a['asset']/Path(f['path']).name;assert sha(p)==f['sha256'],('approved binary',str(p))
for f in approval['source_files']:
 p=B/'generators/utility_batch05a/scripts'/Path(f['path']).name;assert sha(p)==f['sha256'],('original source',str(p))
for a in inputs:assert sha(B/a['repo_path'])==a['sha256']
for v in views:
 p=B/v['path'];im=Image.open(p);assert im.size==(1200,1200) and im.mode=='RGB' and im.format=='JPEG',(v['path'],im.size,im.mode)
 if v['alias_of']:assert sha(p)==sha(B/v['alias_of'])
 else:
  r=json.loads((G/'published'/v['asset']/(p.stem+'.json')).read_text());assert sha(p)==r['output_sha256'];assert r['renderer_sha256']==sha(G/'render.py') and r['spec_sha256']==sha(G/'standard.json') and r['detail_plan_sha256']==sha(G/'detail_targets.json')
  assert r['sample_ceiling']==512 and r['adaptive_threshold']==.005 and r['blender_version']=='4.3.2'
  if isinstance(r['focus'],dict):assert r['closeup_magnification_vs_full_fit']>=1.2
  else:assert abs(max(r['focus_projected_width_height'])/r['ortho_scale']-.8)<1e-6
for p in B.rglob('*'):
 if p.is_file():assert p.stat().st_size<100_000_000,str(p)
print(json.dumps({'pass':True,'assets':len(inputs),'canonical_paths':len(views),'distinct_renders':sum(not v['alias_of'] for v in views),'aliases':sum(bool(v['alias_of']) for v in views),'unchanged_main_binaries':6,'core_byte_identical':True},indent=2))
