"""Freeze only this explicit asset and explicit supporting artifacts."""
import os,json,hashlib
from pathlib import Path
SUPPORT=Path(__file__).resolve().parents[1];ROOT=Path(os.environ.get('ASSET_OUTPUT_ROOT',str(SUPPORT)))
asset_names=['traffic_cone.glb','traffic_cone.blend','preview.jpg','back.jpg','detail.jpg','underside.jpg','underside_axial.jpg','metadata.json','validation.json']
support_names=['README.md','docs/construction-and-references.md','recycled_pvc.png','scripts/build_cone.py','scripts/validate_and_demonstrate.py','scripts/verify_evidence.py','scripts/create_manifest.py','evidence/nested_three.glb','evidence/nested_three.blend','evidence/nested_three.jpg','evidence/nested_section.blend','evidence/nested_section.jpg','evidence/nested_neck_clearance.jpg','evidence/saved_evidence_validation.json','scripts/render_context.py','evidence/context.blend','evidence/context_daylight.jpg','evidence/context_alternate_light.jpg','evidence/context_inputs.json']
files=[]
for name in asset_names:
 rel='assets/street/traffic_cone/'+name;p=ROOT/rel;data=p.read_bytes();assert len(data)<100_000_000;files.append({'source':str(p.relative_to(ROOT)),'repository_path':rel,'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest(),'source_root':'asset_output_root'})
for name in support_names:
 p=SUPPORT/name;data=p.read_bytes();assert len(data)<100_000_000;files.append({'source':name,'repository_path':'generators/cone_function_revision/'+name,'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest(),'source_root':'generator_root'})
manifest={'revision':'cone-functional-r1','status':'ready_for_independent_review','asset_ids':['traffic_cone'],'files':files,'total_bytes':sum(f['bytes'] for f in files),'note':'Replacing canonical traffic_cone requires parent integration approval. Prior frozen batch is unchanged. Manifest excludes itself and transient render logs/Blender backup files.'}
p=SUPPORT/'manifest.json';p.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n');print(hashlib.sha256(p.read_bytes()).hexdigest(),p)
