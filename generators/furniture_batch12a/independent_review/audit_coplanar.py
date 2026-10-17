import bpy,sys,json,hashlib,collections
from pathlib import Path
from mathutils.bvhtree import BVHTree
p=Path(sys.argv[sys.argv.index('--')+1]);out=Path(sys.argv[sys.argv.index('--')+2]);bpy.ops.wm.read_factory_settings(use_empty=True)
if p.suffix=='.blend':bpy.ops.wm.open_mainfile(filepath=str(p))
else:bpy.ops.import_scene.gltf(filepath=str(p))
vv=[];tt=[];owners=[]
for o in bpy.context.scene.objects:
 if o.type!='MESH':continue
 o.data.calc_loop_triangles();offset=len(vv);vv.extend(o.matrix_world@v.co for v in o.data.vertices);tt.extend(tuple(offset+i for i in t.vertices) for t in o.data.loop_triangles);owners.extend((o.name,t.index) for t in o.data.loop_triangles)
def cross(a,b,c):return (b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])
def clip(subject,triangle):
 if cross(*triangle)<0:triangle=list(reversed(triangle))
 for i,a in enumerate(triangle):
  b=triangle[(i+1)%3];old=subject;subject=[]
  if not old:break
  prev=old[-1];dp=cross(a,b,prev)
  for cur in old:
   dc=cross(a,b,cur)
   if (dc>=-1e-12)!=(dp>=-1e-12):
    t=dp/(dp-dc);subject.append((prev[0]+t*(cur[0]-prev[0]),prev[1]+t*(cur[1]-prev[1])))
   if dc>=-1e-12:subject.append(cur)
   prev=cur;dp=dc
 return subject
bvh=BVHTree.FromPolygons(vv,tt,all_triangles=True,epsilon=1e-7);rows=[]
# BVH can miss exactly coplanar pairs. Group triangles by unoriented plane, then compare all group pairs.
planes=collections.defaultdict(list)
for i,t in enumerate(tt):
 a,b,c=[vv[j] for j in t];n=(b-a).cross(c-a)
 if n.length<1e-14:continue
 n.normalize();k=max(range(3),key=lambda k:abs(n[k]))
 if n[k]<0:n=-n
 key=tuple(round(x,5) for x in n)+(round(n.dot(a),5),)
 planes[key].append(i)
pairs=[]
for group in planes.values():
 for i,a in enumerate(group):
  for b in group[i+1:]:
   if any(max(vv[x][k] for x in tt[a])<min(vv[x][k] for x in tt[b])-1e-7 or max(vv[x][k] for x in tt[b])<min(vv[x][k] for x in tt[a])-1e-7 for k in range(3)):continue
   pairs.append((a,b))
for ia,ib in pairs:
 if ia==ib:continue
 a=[vv[i] for i in tt[ia]];b=[vv[i] for i in tt[ib]];na=(a[1]-a[0]).cross(a[2]-a[0]);nb=(b[1]-b[0]).cross(b[2]-b[0])
 if na.length<1e-14 or nb.length<1e-14:continue
 na.normalize();nb.normalize()
 if abs(na.dot(nb))<1-1e-7 or max(abs(na.dot(x-a[0])) for x in b)>1e-7:continue
 axis=max(range(3),key=lambda k:abs(na[k]));axes=[k for k in range(3) if k!=axis];aa=[tuple(x[k] for k in axes) for x in a];bb=[tuple(x[k] for k in axes) for x in b];poly=clip(aa,bb)
 if len(poly)<3:continue
 area=abs(sum(poly[i][0]*poly[(i+1)%len(poly)][1]-poly[(i+1)%len(poly)][0]*poly[i][1] for i in range(len(poly)))/2)/abs(na[axis])
 if area<1e-12:continue
 centroid=[sum(x[k] for x in a+b)/6 for k in range(3)];rows.append({'a':owners[ia],'b':owners[ib],'overlap_area_m2':area,'triangle_average_location':centroid,'normal_dot':na.dot(nb)})
out.write_text(json.dumps({'source':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'positive_area_coplanar_pairs':rows,'method':'Direct unoriented-plane grouped triangle pairs, including shared vertices, same mesh and opposite normals; exact 2D polygon clipping; area threshold1e-12m², plane tolerance1e-7m.'},indent=2));print('COPLANAR',p.name,len(rows),collections.Counter(tuple(sorted([r['a'][0],r['b'][0]])) for r in rows))
