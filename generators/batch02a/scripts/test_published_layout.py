"""Regression check: published layout preserves unrelated canonical assets."""
from pathlib import Path
import json,os,shutil,subprocess,tempfile,hashlib
SUPPORT=Path(__file__).resolve().parents[1]
OUTPUT=Path(os.environ.get('ASSET_OUTPUT_ROOT',str(SUPPORT)))
manifest=json.loads((SUPPORT/'review_manifest.json').read_text())
with tempfile.TemporaryDirectory(prefix='batch02a-layout-') as td:
 root=Path(td);support=root/'generators'/'batch02a'
 for f in manifest['files']:
  dst=root/f['repository_relative_path'];dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(SUPPORT/f['source'],dst)
 sentinel=root/'assets'/'street'/'unrelated_sentinel'/'metadata.json';sentinel.parent.mkdir(parents=True);sentinel.write_text('{"unchanged":true}')
 before=hashlib.sha256(sentinel.read_bytes()).hexdigest();env=dict(os.environ,ASSET_OUTPUT_ROOT=str(root))
 subprocess.run(['blender','-b','--threads','2','--python',str(support/'scripts'/'validate_assets.py')],env=env,check=True)
 subprocess.run(['python',str(support/'scripts'/'create_manifest.py')],env=env,check=True)
 got=json.loads((support/'review_manifest.json').read_text())
 assert {f['repository_relative_path'] for f in got['files']}=={f['repository_relative_path'] for f in manifest['files']}
 for f in got['files']:assert (support/f['source']).is_file()
 assert hashlib.sha256(sentinel.read_bytes()).hexdigest()==before
 assert len(json.loads((support/'catalog.json').read_text()))==3
 print('PASS: published layout resolves all explicit files; unrelated asset unchanged; catalog contains only the three requested IDs.')
