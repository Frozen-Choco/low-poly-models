import bpy,bmesh,json,math,hashlib,sys,itertools
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
src=Path(sys.argv[sys.argv.index('--')+1]);out=Path(sys.argv[sys.argv.index('--')+2]);out.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
if src.suffix=='.blend': bpy.ops.wm.open_mainfile(filepath=str(src))
else:bpy.ops.import_scene.gltf(filepath=str(src))
obs=[o for o in bpy.context.scene.objects if o.type=='MESH']; rows=[]; vv=[];tt=[];owners=[]; mats=[]
for o in obs:
 me=o.data;me.calc_loop_triangles();verts=[o.matrix_world@v.co for v in me.vertices];offset=len(vv);vv+=verts
 tris=[tuple(offset+i for i in t.vertices) for t in me.loop_triangles];tt+=tris;owners += [(o.name,t.index) for t in me.loop_triangles]
 bm=bmesh.new();bm.from_mesh(me);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-7)
 unseen=set(bm.verts);components=[]
 while unseen:
  stack=[unseen.pop()];n=0
  while stack:
   v=stack.pop();n+=1
   for e in v.link_edges:
    w=e.other_vert(v)
    if w in unseen:unseen.remove(w);stack.append(w)
  components.append(n)
 rows.append(dict(name=o.name,vertices=len(me.vertices),triangles=len(tris),components=components,boundary_edges=sum(e.is_boundary for e in bm.edges),nonmanifold_edges=sum(not e.is_manifold for e in bm.edges),volume=bm.calc_volume(signed=True),bounds=[[min(v[k] for v in verts) for k in range(3)],[max(v[k] for v in verts) for k in range(3)]],uv_layers=len(me.uv_layers)))
 bm.free()
for m in bpy.data.materials:
 if m.use_nodes:
  p=next((n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED'),None)
  if p:mats.append(dict(name=m.name,base_color=list(p.inputs['Base Color'].default_value),metallic=p.inputs['Metallic'].default_value,roughness=p.inputs['Roughness'].default_value))
keys=[tuple(tuple(round(c,8) for c in vv[i]) for i in t) for t in tt]
duplicates=[];seen={}
for i,k in enumerate(keys):
 key=tuple(sorted(k))
 if key in seen:duplicates.append([owners[seen[key]],owners[i]])
 else:seen[key]=i
# Full triangle-pair surface candidate audit, including different components in a single object.
tree=BVHTree.FromPolygons(vv,tt,all_triangles=True,epsilon=1e-9);pairs=tree.overlap(tree);hits=[];coplanar=[]
for a,b in pairs:
 if a>=b:continue
 pa=[vv[i] for i in tt[a]];pb=[vv[i] for i in tt[b]]
 shared=set(keys[a])&set(keys[b])
 if shared:continue
 na=(pa[1]-pa[0]).cross(pa[2]-pa[0]);nb=(pb[1]-pb[0]).cross(pb[2]-pb[0])
 if na.length<1e-14 or nb.length<1e-14:continue
 na.normalize();nb.normalize();row=[owners[a],owners[b]]
 if abs(na.dot(nb))>1-1e-6 and max(abs(na.dot(p-pa[0])) for p in pb)<1e-7:coplanar.append(row)
 else:hits.append(row)
lo=[min(v[k] for v in vv) for k in range(3)];hi=[max(v[k] for v in vv) for k in range(3)]
data=dict(source=str(src),sha256=hashlib.sha256(src.read_bytes()).hexdigest(),bytes=src.stat().st_size,objects=rows,bounds=[lo,hi],dimensions=[hi[i]-lo[i] for i in range(3)],finite=all(math.isfinite(c) for v in vv for c in v),zero_area=sum((vv[t[1]]-vv[t[0]]).cross(vv[t[2]]-vv[t[0]]).length<1e-14 for t in tt),duplicate_triangles=duplicates,nonadjacent_surface_candidates=hits,nonadjacent_coplanar_candidates=coplanar,materials=mats,images=[dict(name=i.name,packed=bool(i.packed_file),size=list(i.size),filepath=i.filepath) for i in bpy.data.images],audit_limit='BVH candidates need individual classification; shared-coordinate adjacency excluded, geometric contacts not manufacturing assurance.')
(out/(src.stem+'_'+src.suffix[1:]+'.json')).write_text(json.dumps(data,indent=2));print('REVIEW',src.name,len(tt),'triangles',len(hits),'surface candidates',len(coplanar),'coplanar candidates')
