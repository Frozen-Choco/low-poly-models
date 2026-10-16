"""Freeze curated material-source scope. Canonical photographs have their own manifest."""
import hashlib,json
from pathlib import Path
R=Path(__file__).resolve().parents[1]
source=['README.md','docs/diagnosis.md','scripts/revise_material.py','scripts/common.py','scripts/extract_material.py','scripts/validate_saved.py','scripts/package_manifest.py','inputs/approved_apple_geometry.blend','inputs/metadata.json','inputs/published_before.glb','material_revision.json','glb_pbr.json','validation.json','reproduction.json','previews/revised_albedo.png','previews/revised_metallic_roughness.png']
models=['assets/whole_red_apple/whole_red_apple.glb','assets/whole_red_apple/whole_red_apple.blend','assets/whole_red_apple/metadata.json']
records=[]
for rel in sorted(source+models):
 p=R/rel
 assert p.is_file(),p
 assert p.stat().st_size<100_000_000,p
 dest='assets/food/whole_red_apple/'+p.name if rel in models else 'generators/apple_material_revision/'+rel
 records.append(dict(local_path=rel,repo_relative_path=dest,bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest()))
(R/'model_source_manifest.json').write_text(json.dumps(dict(revision='apple-material-r2',scope='One existing apple model/material replacement and reproducible source; canonical photographs require separate frozen photography manifest. Held bread/onigiri and rejected/provisional renders excluded.',review_status='Model/material independently approved; full integration pending final photography approval.',files=records),indent=2)+'\n')
