import json,struct,collections,hashlib
from pathlib import Path
R=Path('lowpoly_batch14a');B=Path('/tmp/batch14a_independent_rev12_3');O=Path('reviews/batch14a');sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):
 b=p.read_bytes();n=struct.unpack('<I',b[12:16])[0];return json.loads(b[20:20+n]),b[28+n:]
def access(j,b,i):
 a=j['accessors'][i];v=j['bufferViews'][a['bufferView']];n={'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4}[a['type']];fmt={5123:'H',5125:'I',5126:'f'}[a['componentType']];st=v.get('byteOffset',0)+a.get('byteOffset',0);return list(struct.iter_unpack('<'+fmt*n,b[st:st+a['count']*struct.calcsize(fmt)*n]))
def tris(ii):
 x=[v[0] for v in ii];ts=[tuple(x[i:i+3]) for i in range(0,len(x),3)];return collections.Counter(min(t,t[1:]+t[:1],t[2:]+t[:2]) for t in ts)
rows=[]
for s in ['toaster','electric_fan']:
 a=R/'assets'/s/(s+'.glb');b=B/'assets'/s/(s+'.glb');j,A=read(a);k,C=read(b)
 for key in ['asset','scene','scenes','nodes','materials','extensionsUsed','extensionsRequired']:
  assert j.get(key)==k.get(key),(s,key)
 assert len(j['meshes'])==len(k['meshes'])
 for m,n in zip(j['meshes'],k['meshes']):
  assert m['name']==n['name'] and len(m['primitives'])==len(n['primitives'])
  for p,q in zip(m['primitives'],n['primitives']):
   assert p.get('material')==q.get('material') and p.get('mode',4)==q.get('mode',4) and p['attributes'].keys()==q['attributes'].keys()
   for attr in p['attributes']:assert access(j,A,p['attributes'][attr])==access(k,C,q['attributes'][attr]),(s,m['name'],attr)
   assert tris(access(j,A,p['indices']))==tris(access(k,C,q['indices'])),(s,m['name'],'oriented topology')
 rows.append({'asset':s,'delivered_sha256':sha(a),'regenerated_sha256':sha(b),'byte_identical':sha(a)==sha(b),'exact_geometry_material_equivalence':True,'checks':'Identical named scene graph/transforms/extras/materials and all vertex position, normal, UV arrays; exact oriented triangle multiset with winding preserved. Index ordering and buffer sharing ignored only.'})
assert sha(R/'scripts/build_assets.py')==sha(B/'scripts/build_assets.py')
d={'decision':'PASS','method':'Independent isolated source copy, fresh Blender process,1thread; exact semantic GLB equivalence. Byte equality or exact oriented geometry/material equality checked per asset.','script_sha256':sha(R/'scripts/build_assets.py'),'results':rows};(O/'source_reproduction.json').write_text(json.dumps(d,indent=2)+'\n');print(json.dumps(d,indent=2))
