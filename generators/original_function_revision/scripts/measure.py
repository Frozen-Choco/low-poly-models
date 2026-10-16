import bpy,json,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
root=Path(__file__).resolve().parents[2];r={}
for slug in ['mug','open_shelf']:
 for typ in ['blend','glb']:
  p=next((root/'original_function_revision/assets').rglob(slug+'.'+typ))
  if typ=='blend':bpy.ops.wm.open_mainfile(filepath=str(p))
  else:bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(p))
  obs=[o for o in bpy.context.scene.objects if o.type=='MESH' and o.name!='Preview ground'];d={}
  for o in obs:
   d[o.name]=BVHTree.FromPolygons([o.matrix_world@v.co for v in o.data.vertices],[list(f.vertices) for f in o.data.polygons])
  rr={}
  if slug=='mug':
   body=next(o for o in obs if 'cavity' in o.name);handle=next(o for o in obs if 'handle' in o.name);bv=d[body.name]
   verts=[handle.matrix_world@v.co for v in handle.data.vertices];values=[]
   for pt in verts:
    co,n,idx,dist=bv.find_nearest(pt);signed=dist if (pt-co).dot(n)>0 else -dist
    if pt.z<.04:values.append(signed)
   rr['lower_handle_surface_signed_distance_m']={'min':min(values),'max':max(values),'inside_vertex_count':sum(x<0 for x in values)}
   rr['body_handle_surface_intersections']=len(bv.overlap(d[handle.name]))
   # Exact ray intersections through handle gap, cavity and base.
   for name,start,direction in [('handle_gap_at_mid',(.025,0,.057),(1,0,0)),('cavity_center',( -.016,0,.2),(0,0,-1))]:
    hits=[];p=Vector(start);dr=Vector(direction)
    for k in range(8):
     cand=[(o.name,d[o.name].ray_cast(p,dr)) for o in obs];cand=[(n,h) for n,h in cand if h[0] is not None]
     if not cand:break
     n,h=min(cand,key=lambda z:z[1][3]);hits.append([n,list(h[0])]);p=h[0]+dr*.000001
    rr[name]=hits
  if slug=='open_shelf':
   rr['brace_board_surface_intersections']={a.name+' | '+b.name:len(d[a.name].overlap(d[b.name])) for a in obs if 'diagonal' in a.name for b in obs if 'Oak shelf' in b.name}
  rr['materials']={m.name:{key:m.node_tree.nodes.get('Principled BSDF').inputs[key].default_value for key in ['Metallic','Roughness','Coat Weight']} for m in bpy.data.materials if m.use_nodes and m.node_tree.nodes.get('Principled BSDF')}
  r[slug+'_'+typ]=rr
(root/'original_function_revision/measurements.json').write_text(json.dumps(r,indent=2))
