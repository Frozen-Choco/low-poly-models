"""Reopen the delivered stack evidence, not only its in-memory source."""
import bpy,bmesh,json,math,os,struct
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];E=ROOT/'evidence'
result={}
for ext in ['blend','glb']:
 bpy.ops.wm.read_factory_settings(use_empty=True)
 if ext=='blend':bpy.ops.wm.open_mainfile(filepath=str(E/'nested_three.blend'))
 else:bpy.ops.import_scene.gltf(filepath=str(E/'nested_three.glb'))
 objects=[o for o in bpy.context.scene.objects if o.type=='MESH' and 'floor' not in o.name.lower()]
 assert len(objects)==3,(ext,[o.name for o in objects])
 bounds=[]
 for o in objects:
  pts=[o.matrix_world@v.co for v in o.data.vertices];bounds.append({'min':[min(v[i] for v in pts) for i in range(3)],'max':[max(v[i] for v in pts) for i in range(3)]})
 bounds.sort(key=lambda a:a['min'][2]);assert all(abs(b['min'][2]-i*.04)<1e-6 and abs(b['max'][2]-(.7+i*.04))<1e-6 for i,b in enumerate(bounds))
 result[ext]={'reopened':True,'cone_instances':3,'world_bounds_m':bounds}
 # Repeat solid-intersection checks on actual reopened evidence instances.
 objects.sort(key=lambda o:min((o.matrix_world@v.co).z for v in o.data.vertices))
 volumes=[]
 for lower,upper in [(objects[0],objects[1]),(objects[0],objects[2]),(objects[1],objects[2])]:
  copies=[]
  for src in [lower,upper]:
   mesh=src.data.copy();mesh.transform(src.matrix_world);bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-7);bm.to_mesh(mesh);bm.free();ob=bpy.data.objects.new('Reopen intersection',mesh);bpy.context.collection.objects.link(ob);copies.append(ob)
  test,other=copies;mod=test.modifiers.new('Exact saved evidence intersection','BOOLEAN');mod.operation='INTERSECT';mod.solver='EXACT';mod.object=other;bpy.context.view_layer.objects.active=test;bpy.context.view_layer.update();bpy.ops.object.modifier_apply(modifier=mod.name);bm=bmesh.new();bm.from_mesh(test.data);vol=abs(bm.calc_volume(signed=True));bm.free();assert vol<1e-10;volumes.append(vol)
  for ob in copies:bpy.data.objects.remove(ob,do_unlink=True)
 result[ext]['all_pair_exact_intersection_volumes_m3']=volumes
asset_root=Path(os.environ.get('ASSET_OUTPUT_ROOT',str(ROOT)))
data=(asset_root/'assets/street/traffic_cone/traffic_cone.glb').read_bytes();length=struct.unpack_from('<I',data,12)[0];gltf=json.loads(data[20:20+length]);assert all('bufferView' in i and 'uri' not in i for i in gltf.get('images',[]));assert all(m.get('pbrMetallicRoughness',{}).get('metallicFactor',1)==0 for m in gltf['materials'])
result['production_glb_materials']={'embedded_images':len(gltf.get('images',[])),'external_images':False,'materials':[{'name':m['name'],'pbr':m.get('pbrMetallicRoughness')} for m in gltf['materials']]}
(E/'saved_evidence_validation.json').write_text(json.dumps(result,indent=2));print('SAVED_STACK_EVIDENCE_PASSED')
