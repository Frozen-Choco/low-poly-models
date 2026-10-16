import bpy,json
from pathlib import Path
from mathutils.bvhtree import BVHTree
p=Path(__file__).resolve().parents[2];r={}
for typ in ['blend','glb']:
 src=p/'original_function_revision/assets/household/mug'/('mug.'+typ)
 if typ=='blend':bpy.ops.wm.open_mainfile(filepath=str(src))
 else:bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(src))
 b=bpy.data.objects['Mug with open cavity'];h=bpy.data.objects['Rounded open handle'];bv=BVHTree.FromPolygons([b.matrix_world@v.co for v in b.data.vertices],[list(f.vertices) for f in b.data.polygons]);h.data.calc_loop_triangles();mn=1;count=0
 for t in h.data.loop_triangles:
  vs=[h.matrix_world@h.data.vertices[i].co for i in t.vertices]
  if min(v.z for v in vs)>.04:continue
  for i in range(21):
   for j in range(21-i):
    pt=vs[0]*(1-(i+j)/20)+vs[1]*i/20+vs[2]*j/20
    if pt.z>.04:continue
    co,n,idx,dist=bv.find_nearest(pt);signed=dist if (pt-co).dot(n)>0 else -dist
    if signed<mn:mn=signed;point=list(pt)
    count+=1
 r[typ]={'minimum_sampled_lower_surface_distance_m':mn,'closest_sample':point,'sample_count':count}
(p/'original_function_revision/mug_joint.json').write_text(json.dumps(r,indent=2))
