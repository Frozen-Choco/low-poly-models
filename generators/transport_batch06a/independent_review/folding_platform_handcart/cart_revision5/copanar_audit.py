import json,struct,hashlib,collections,math
from pathlib import Path
p=Path('lowpoly_batch06a/assets/folding_platform_handcart/folding_platform_handcart.glb');b=p.read_bytes();n=struct.unpack_from('<I',b,12)[0];j=json.loads(b[20:20+n]);data=b[28+n:]
def arr(i):
 a=j['accessors'][i];v=j['bufferViews'][a['bufferView']];code={5126:'f',5125:'I',5123:'H',5121:'B'}[a['componentType']];count={'VEC3':3,'SCALAR':1}[a['type']];stride=v.get('byteStride',struct.calcsize(code)*count);start=v.get('byteOffset',0)+a.get('byteOffset',0);return [struct.unpack_from('<'+code*count,data,start+k*stride) for k in range(a['count'])]
def cross(a,b,c):return (b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])
def area(v):return abs(sum(a[0]*b[1]-b[0]*a[1] for a,b in zip(v,v[1:]+v[:1])))/2

def clip(subject,tri):
 if cross(*tri)<0:tri=tri[::-1]
 for a,b in zip(tri,tri[1:]+tri[:1]):
  if not subject:return []
  old=subject;subject=[]
  for p,q in zip(old,old[1:]+old[:1]):
   dp=cross(a,b,p);dq=cross(a,b,q)
   if dp>=-1e-10:subject.append(p)
   if (dp>=0)!=(dq>=0):
    t=dp/(dp-dq);subject.append((p[0]+t*(q[0]-p[0]),p[1]+t*(q[1]-p[1])))
 return subject
planes=collections.defaultdict(list)
for node in j['nodes']:
 if 'mesh' not in node:continue
 assert not any(k in node for k in ['matrix','translation','rotation','scale'])
 for prim in j['meshes'][node['mesh']]['primitives']:
  vv=arr(prim['attributes']['POSITION']);ii=[x[0] for x in arr(prim['indices'])]
  for k in range(0,len(ii),3):
   t=[vv[v] for v in ii[k:k+3]]
   for axis in range(3):
    if max(v[axis] for v in t)-min(v[axis] for v in t)>1e-8:continue
    axes=[x for x in range(3) if x!=axis];v=[(p[axes[0]],p[axes[1]]) for p in t];c=cross(*v)
    if abs(c)<1e-12:continue
    planes[(axis,round(t[0][axis],7),c>0)].append((node['name'],v))
res=collections.defaultdict(float)
for plane,ts in planes.items():
 for i,(a,t) in enumerate(ts):
  for b,u in ts[i+1:]:
   # Include nonadjacent triangles within unioned objects.
   if any(max(v[k] for v in t)<=min(v[k] for v in u) or max(v[k] for v in u)<=min(v[k] for v in t) for k in range(2)):continue
   z=clip(t,u);ar=area(z) if z else 0
   if ar>1e-10:res[(a,b,*plane)]+=ar
out={'source_sha256':hashlib.sha256(b if isinstance(b,bytes) else p.read_bytes()).hexdigest(),'scope':'Axis-aligned same-facing coplanar triangle overlap candidates; internal buried contacts must be distinguished by review','pairs':[{'a':k[0],'b':k[1],'gltf_axis':k[2],'plane':k[3],'orientation':k[4],'overlap_m2':v} for k,v in res.items()]};Path('reviews/batch06a/canonical/coplanar_candidates.json').write_text(json.dumps(out,indent=2));print(len(out['pairs']));print(json.dumps(out['pairs'],indent=2))
