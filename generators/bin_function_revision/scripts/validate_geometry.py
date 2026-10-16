import bpy,sys,json,math,hashlib,os
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];A=Path(os.environ.get('ASSET_OUTPUT_ROOT',str(R/'assets')))/'public_recycling_bin';result={}
for ext in ['blend','glb']:
 p=A/('public_recycling_bin.'+ext)
 if ext=='blend':bpy.ops.wm.open_mainfile(filepath=str(p))
 else:bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(p))
 obs=[o for o in bpy.context.scene.objects if o.type=='MESH' and 'service_group' in o];tri=0;bad=0;vertices=[]
 for o in obs:
  o.data.calc_loop_triangles();tri+=len(o.data.loop_triangles);vertices.extend([o.matrix_world@v.co for v in o.data.vertices])
  for t in o.data.loop_triangles:
   a,b,c=[o.matrix_world@o.data.vertices[i].co for i in t.vertices]
   if (b-a).cross(c-a).length<1e-12:bad+=1
 lo=[min(v[i] for v in vertices) for i in range(3)];hi=[max(v[i] for v in vertices) for i in range(3)]
 result[ext]={'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'triangles':tri,'zero_area_triangles':bad,'finite_coordinates':all(math.isfinite(x) for v in vertices for x in v),'bounds_min':lo,'bounds_max':hi,'dimensions_m':[hi[i]-lo[i] for i in range(3)],'mesh_count':len(obs),'external_textures':[im.filepath for im in bpy.data.images if im.source=='FILE' and not im.packed_file]}
 assert bad==0 and result[ext]['finite_coordinates']
(R/'evidence/geometry_validation.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
