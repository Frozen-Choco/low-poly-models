"""Reproduce additive canonical photos. Each worker runs one 2-thread Blender job.
Run one worker by default. A second may be started only with an authorized free slot.
Atomic per-view locks prevent duplicate work; remove a stale lock only after verifying its job stopped.
"""
import os,subprocess,json,shutil,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];R=ROOT/'photography/preview_standard_v1'
inputs=json.loads((R/'inputs.json').read_text());views=json.loads((R/'views.json').read_text());(R/'locks').mkdir(exist_ok=True)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def complete(rec,dst,e):
 if not(rec.exists() and dst.exists()):return False
 d=json.loads(rec.read_text());return d['input_sha256']==e['sha256'] and d['output_sha256']==sha(dst) and d['renderer_sha256']==sha(R/'render.py') and d['spec_sha256']==sha(R/'standard.json') and d['detail_plan_sha256']==sha(R/'detail_targets.json')
for e in inputs:
 if os.environ.get("PHOTO_ONLY_ASSETS") and e["id"] not in os.environ["PHOTO_ONLY_ASSETS"].split(","):continue
 for view in views[e['id']]:
  rec=R/'records'/e['id']/(view+'.json');dst=R/'repo'/Path(e['repo_path']).parent/(view+'.jpg');final=ROOT/Path(e['repo_path']).parent/(view+'.jpg')
  if complete(rec,dst,e):shutil.copyfile(dst,final);continue
  lock=R/'locks'/(e['id']+'_'+view)
  try:lock.mkdir()
  except FileExistsError:continue
  try:
   if not complete(rec,dst,e):
    log=R/(e['id']+'_'+view+'.log')
    with log.open('w') as f:subprocess.run(['blender','-b','-t','2','--python',str(R/'render.py'),'--',e['id'],view],env={**os.environ,'SOURCE_ROOT':str(ROOT)},stdout=f,stderr=subprocess.STDOUT,check=True)
    assert complete(rec,dst,e),str(log)
   shutil.copyfile(dst,final);print('COMPLETE',e['id'],view,flush=True)
  finally:lock.rmdir()
