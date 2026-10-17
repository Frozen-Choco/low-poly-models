import bpy,bmesh,json,math,hashlib
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parent
SRC=ROOT.parent/'comb_tissue/models/comb'
results=[]
for ext in ['blend','glb']:
 p=SRC/f'comb.{ext}'
 if ext=='blend':bpy.ops.wm.open_mainfile(filepath=str(p))
 else:
  bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(p))
 obs=[o for o in bpy.context.scene.objects if o.type=='MESH']
 assert len(obs)==1,len(obs)
 o=obs[0];bm=bmesh.new();bm.from_mesh(o.data)
 bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-8)
 nonman=sum(not e.is_manifold for e in bm.edges);volume=bm.calc_volume(signed=True)
 zeros=sum(f.calc_area()<1e-14 for f in bm.faces)
 components=0;remaining=set(bm.verts)
 while remaining:
  components+=1;todo=[remaining.pop()]
  while todo:
   v=todo.pop()
   for e in v.link_edges:
    n=e.other_vert(v)
    if n in remaining:remaining.remove(n);todo.append(n)
 bm.free()
 vs=[o.matrix_world@v.co for v in o.data.vertices]
 lo=[min(v[i] for v in vs) for i in range(3)];hi=[max(v[i] for v in vs) for i in range(3)]
 dims=[b-a for a,b in zip(lo,hi)]
 assert all(math.isfinite(c) for v in vs for c in v)
 assert nonman==0 and zeros==0 and volume>0 and components==1,(nonman,zeros,volume,components)
 assert all(abs(a-b)<1e-5 for a,b in zip(dims,[.17,.03,.0032])),dims
 assert abs(lo[2])<1e-6,lo
 # Rays through planar thickness independently validate each free gap and every tooth.
 inv=o.matrix_world.inverted()
 def hit(x,y,z=.012):
  return o.ray_cast(inv@Vector((x,y,z)),Vector((0,0,-1)))[0]
 tooth_x=[(78-156*i/42)/1000 for i in range(43)]
 gap_x=[(a+b)/2 for a,b in zip(tooth_x,tooth_x[1:])]
 assert all(hit(x,-.009) for x in tooth_x)
 assert not any(hit(x,-.009) for x in gap_x)
 assert all(hit(x,-.002) for x in gap_x)
 # Ends retain guards and spine carries uninterrupted grip area.
 assert hit(.083,-.009) and hit(-.083,-.009)
 assert all(hit(x/1000,.01) for x in range(-80,81))
 mats=[]
 for m in o.data.materials:
  bs=next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
  row={'name':m.name,'base_color':list(bs.inputs['Base Color'].default_value),'roughness':bs.inputs['Roughness'].default_value,'metallic':bs.inputs['Metallic'].default_value}
  assert row['metallic']==0 and .2<=row['roughness']<=.5,row
  mats.append(row)
 o.data.calc_loop_triangles()
 results.append({'format':ext,'path':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size,'dimensions_m':dims,'min':lo,'triangles':len(o.data.loop_triangles),'nonmanifold_edges_after_seam_weld':nonman,'connected_components':components,'zero_area_faces':zeros,'signed_volume_m3':volume,'43_teeth_and_42_through_gaps':True,'end_guards_and_solid_spine':True,'materials':mats})
(ROOT/'comb_geometry_checks.json').write_text(json.dumps(results,indent=2)+'\n')
print(json.dumps(results,indent=2))
