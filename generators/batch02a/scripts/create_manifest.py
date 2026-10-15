"""Freeze exactly this batch, including when models live at a shared published root.
ASSET_OUTPUT_ROOT selects canonical assets; support files stay beside this script.
"""
from pathlib import Path
import hashlib,json,os
SUPPORT=Path(__file__).resolve().parents[1]
OUTPUT=Path(os.environ.get('ASSET_OUTPUT_ROOT',str(SUPPORT))).resolve()
IDS=('streetlight','park_bench','traffic_cone')
SUPPORT_FILES=('README.md','catalog.json','validation.json','docs/asset-standard.md','docs/reference-notes.md','docs/construction-audit.md','scripts/build_assets.py','scripts/validate_assets.py','scripts/render_context.py','scripts/create_manifest.py','scripts/test_published_layout.py','scripts/render_bench_endgrain.py','context/daylight.jpg','context/alternate_light.jpg','context/context.blend','Weathered_galvanized_steel.png','Dull_galvanized_fasteners.png','Heavy_rubber_ballast_base.png','timber_grain.png','timber_endgrain.png')
files=[]
def add(p,destination):
 assert p.is_file(),f'Missing required file: {p}'
 assert p.stat().st_size<100_000_000
 files.append({'source':os.path.relpath(p,SUPPORT),'repository_relative_path':destination,'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
for slug in IDS:
 for name in (slug+'.glb',slug+'.blend','preview.jpg','back.jpg','detail.jpg','metadata.json','validation.json'):
  relative=Path('assets')/'street'/slug/name;add(OUTPUT/relative,str(relative))
add(OUTPUT/'assets'/'street'/'park_bench'/'endgrain.jpg','assets/street/park_bench/endgrain.jpg')
for relative in SUPPORT_FILES:add(SUPPORT/relative,'generators/batch02a/'+relative)
(SUPPORT/'review_manifest.json').write_text(json.dumps({'revision':'02a-r3','status':'ready_for_independent_review_not_approved','files':files},indent=2))
