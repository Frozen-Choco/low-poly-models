"""Freeze minimal distribution. Local diagnostics and duplicate proof scenes stay local."""
import json,hashlib,os
from pathlib import Path
R=Path(os.environ.get('ASSET_OUTPUT_ROOT',str(Path(__file__).resolve().parents[1])))
ids=['roadside_convex_mirror','outdoor_ac_condenser','street_drain_grate']
refs={ids[0]:['https://tsubame-shinko.co.jp/wp-content/uploads/2022/10/G600-TD-Z36.pdf'],ids[1]:['https://www.daikin.ie/content/dam/document-library/installation-manuals/ac/split/rxf-f/RXF20-42F_Installation%20manual_3PEN748643-15S_English.pdf'],ids[2]:['https://www.takara-kizai.com/product/grating/steel/','https://www.kaneso.co.jp/seihin/zumen/HXC-6638_DK-600-Z.pdf']}
views={s:['preview','back','side','underside','close_up','alternate_light']+({'roadside_convex_mirror':['bracket_detail'],'outdoor_ac_condenser':['service_detail']}.get(s,[])) for s in ids}
files=[];catalog=[]
for s in ids:
 d=R/'assets'/s;p=d/'metadata.json';m=json.loads(p.read_text());m['references']=refs[s];m['functional_validation_files']=['geometry_validation.json','previews/installed_use_validation.json'];m['view_files']=[v+'.jpg' for v in views[s]];m['glb_sha256']=hashlib.sha256((d/(s+'.glb')).read_bytes()).hexdigest();m['blend_sha256']=hashlib.sha256((d/(s+'.blend')).read_bytes()).hexdigest();m['preview_standard']='preview_standard_v1';m['photography_config']='photography/preview_standard_v1';m['view_semantics']={'preview':'standard front three-quarter','back':'opposing three-quarter','side':'axial side','underside':'axial bottom','close_up':'declared functional detail target','alternate_light':'standard preview under second lighting direction'};m['review_status']='Candidate complete; independent package review pending';p.write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n');catalog.append(m)
 files.extend([d/(s+'.glb'),d/(s+'.blend'),p]+[d/(v+'.jpg') for v in views[s]])
(R/'catalog.json').write_text(json.dumps(catalog,ensure_ascii=False,indent=2)+'\n')
files += [R/p for p in ['README.md','catalog.json','geometry_validation.json','photography_validation.json','reproduction_validation.json','model_manifest.json','previews/installed_use_validation.json','previews/input_provenance.json','photography/README.md','photography/run_canonical.py']]
files += list((R/'docs').glob('*.md'))+list((R/'scripts').glob('*.py'))
files += list((R/'photography/preview_standard_v1').glob('*.json'))+[R/'photography/preview_standard_v1/render.py']+list((R/'photography/preview_standard_v1/records').rglob('*.json'))
# Include only small use-proof JPEGs; scripts regenerate the full local proof scenes.
files += [R/'previews'/p for p in ['grate_lift_diagnostic.jpg','installed_context_diagnostic_day.jpg','installed_context_diagnostic_alternate.jpg']]
assert all(p.is_file() for p in files)
data={str(p.relative_to(R)):{'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in sorted(set(files))};assert all(v['bytes']<100000000 for v in data.values())
(R/'manifest.json').write_text(json.dumps({'scope':'Minimal distribution; excludes reference downloads, duplicate proof Blend scenes and raw render intermediates','files':data},indent=2)+'\n');print('Frozen',len(data),'files',sum(v['bytes'] for v in data.values()),'bytes')
