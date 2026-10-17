from pathlib import Path
import json,struct,collections,hashlib
# Comparison against isolated byte-identical revision11 reproduction; optional explicit input paths.
import sys
A=Path(sys.argv[1] if len(sys.argv)>1 else '/tmp/batch14a_independent_rev11_3/assets/toaster/toaster.glb');B=Path(sys.argv[2] if len(sys.argv)>2 else 'lowpoly_batch14a/assets/toaster/toaster.glb')
def read(p):
 b=p.read_bytes();n=struct.unpack('<I',b[12:16])[0];return json.loads(b[20:20+n]),b[28+n:]
def acc(j,b,i):
 a=j['accessors'][i];v=j['bufferViews'][a['bufferView']];sz={'VEC3':3,'VEC2':2,'SCALAR':1,'VEC4':4}[a['type']];f={5126:'f',5125:'I',5123:'H'}[a['componentType']];s=v.get('byteOffset',0)+a.get('byteOffset',0);return list(struct.iter_unpack('<'+f*sz,b[s:s+a['count']*sz*struct.calcsize(f)]))
def mesh(j,b,node,normal):
 out=[]
 for p in j['meshes'][node['mesh']]['primitives']:
  attrs={k:acc(j,b,v) for k,v in p['attributes'].items() if k!='NORMAL' or normal};inds=[x[0] for x in acc(j,b,p['indices'])];vert=[tuple((k,attrs[k][i]) for k in sorted(attrs)) for i in range(len(attrs['POSITION']))];c=collections.Counter()
  for i in range(0,len(inds),3):
   t=tuple(vert[k] for k in inds[i:i+3]);c[min(t,t[1:]+t[:1],t[2:]+t[:2])]+=1
  out.append((p.get('material'),c))
 return out
j,b=read(A);k,c=read(B);assert j['nodes']==k['nodes'] and j['materials']==k['materials'];rows=[]
for n in j['nodes']:
 if 'mesh' not in n:continue
 normal=n['name']!='Continuous chrome shell';assert mesh(j,b,n,normal)==mesh(k,c,n,normal),n['name'];rows.append({'object':n['name'],'geometry_uv_material_exact':True,'normals_exact':normal})
node=next(n for n in k['nodes'] if n['name']=='Continuous chrome shell');group=collections.defaultdict(list)
for p in k['meshes'][node['mesh']]['primitives']:
 for v,n in zip(acc(k,c,p['attributes']['POSITION']),acc(k,c,p['attributes']['NORMAL'])):group[tuple(round(x,7) for x in v)].append(n)
import math
splits=[]
for v,ns in group.items():
 if abs(abs(v[0])-.079)>1e-6:continue
 angle=max(math.degrees(math.acos(max(-1,min(1,sum(x*y for x,y in zip(a,b)))))) for a in ns for b in ns)
 if angle>1:splits.append({'position':v,'angle':angle})
assert not [r for r in splits if r["position"][1] > -.06999]
r={'decision':'PASS','old_sha256':hashlib.sha256(A.read_bytes()).hexdigest(),'candidate_sha256':hashlib.sha256(B.read_bytes()).hexdigest(),'checks':['All named scene transforms and materials identical','Every oriented triangle with position and UV matches exactly; all non-shell normals also match exactly','Only shell split normals changed; previous8–9degree side-border discontinuities are absent'],'meshes':rows,'unexpected_side_split_discontinuities_above1degree':[r for r in splits if r['position'][1]>-.06999],'intentional_bottom_cut_sharp_edges':[r for r in splits if r['position'][1]<=-.06999]};Path('reviews/batch14a/saved_rev12/toaster_normal_change.json').write_text(json.dumps(r,indent=2)+'\n');print('PASS exact geometry;normal-only change')
