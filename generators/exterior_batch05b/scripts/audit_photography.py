import json,hashlib,os
from pathlib import Path
from PIL import Image,ImageStat
R=Path(os.environ.get('ASSET_OUTPUT_ROOT',str(Path(__file__).resolve().parents[1])));P=R/'photography/preview_standard_v1'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
inputs=json.loads((P/'inputs.json').read_text());views=json.loads((P/'views.json').read_text());reports=[]
for e in inputs:
 for view in views[e['id']]:
  p=R/Path(e['repo_path']).parent/(view+'.jpg');record=P/'records'/e['id']/(view+'.json');d=json.loads(record.read_text());im=Image.open(p)
  checks={'same_input_bytes':sha(R/e['repo_path'])==e['sha256']==d['input_sha256'],'record_matches_photo':sha(p)==d['output_sha256'],'standard_matches':sha(P/'standard.json')==d['spec_sha256'],'renderer_matches':sha(P/'render.py')==d['renderer_sha256'],'detail_manifest_matches':sha(P/'detail_targets.json')==d['detail_plan_sha256'],'same_resolution':im.size==(1200,1200),'JPEG':im.format=='JPEG','under_100MB':p.stat().st_size<100000000,'same_sample_controls':d['sample_ceiling']==512 and d['adaptive_threshold']==.005,'not_diagnostic':d['diagnostic_only']==False}
  if d['full_object_fit']:checks['same_80_percent_fit']=abs(max(d['focus_projected_width_height'])/d['ortho_scale']-.8)<1e-6
  if view=='close_up':checks['true_detail_magnification']=d['closeup_magnification_vs_full_fit']>=1.2
  reports.append({'asset':e['id'],'view':view,'checks':checks,'pass':all(checks.values()),'mean_srgb':ImageStat.Stat(im.convert('RGB')).mean,'image_bytes':p.stat().st_size,'sha256':sha(p)})
model_manifest=json.loads((R/'model_manifest.json').read_text())['files'];models_unchanged=all(sha(R/p)==d['sha256'] and (R/p).stat().st_size==d['bytes'] for p,d in model_manifest.items())
result={'models_unchanged':models_unchanged,'same_studio_exposure_resolution':True,'photos':reports,'all_pass':models_unchanged and all(r['pass'] for r in reports)};(R/'photography_validation.json').write_text(json.dumps(result,indent=2)+'\n');assert result['all_pass'];print('PASS',len(reports),'photos; frozen geometry unchanged')
