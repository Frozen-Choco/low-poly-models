import bpy,bmesh,json,sys,hashlib
from pathlib import Path
sys.path.insert(0,'/workspace/scratch/a456259dbd5d/lowpoly_batch06a/scripts');import validate_saved as V
R=Path('/workspace/scratch/a456259dbd5d');out={}
for ext in ['blend','glb']:
 p=R/'lowpoly_batch06a/assets/folding_platform_handcart'/('folding_platform_handcart.'+ext);obs=V.load(p);o=next(o for o in obs if o.name=='Deck load bearing top skin');m=o.data;m.calc_loop_triangles();area=sum(t.area for t in m.loop_triangles);vol=0
 for t in m.loop_triangles:
  a,b,c=[o.matrix_world@m.vertices[i].co for i in t.vertices];vol+=a.dot(b.cross(c))/6
 bm=bmesh.new();bm.from_mesh(m);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-7);out[ext]={'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'deck_triangles':len(m.loop_triangles),'area_m2':area,'signed_volume_m3':vol,'edge_face_counts':{str(n):sum(len(e.link_faces)==n for e in bm.edges) for n in [0,1,2,3,4,5,6]},'boundary_edges':sum(e.is_boundary for e in bm.edges),'nonmanifold_edges':sum(not e.is_manifold for e in bm.edges),'deck_vertices':len(m.vertices)};bm.free()
(R/'reviews/batch06a/cart_revision6/deck_audit.json').write_text(json.dumps(out,indent=2))
