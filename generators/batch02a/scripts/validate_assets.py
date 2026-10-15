import bpy,json,math,hashlib,struct,os
from pathlib import Path
SUPPORT=Path(__file__).resolve().parents[1]
ROOT=Path(os.environ.get('ASSET_OUTPUT_ROOT',str(SUPPORT)))
def stats(obs):
 pts=[];tri=zero=0;finite=True
 for o in obs:
  m=o.data;m.calc_loop_triangles();tri+=len(m.loop_triangles);zero+=sum(t.area<1e-14 for t in m.loop_triangles);pts.extend(o.matrix_world@v.co for v in m.vertices);finite &= all(math.isfinite(c) for v in m.vertices for c in v.co)
 return {'triangles':tri,'degenerate_triangles':zero,'finite_vertices':finite,'min':[min(p[i] for p in pts) for i in range(3)],'max':[max(p[i] for p in pts) for i in range(3)],'meshes':len(obs)}
IDS={'streetlight','park_bench','traffic_cone'}
results=[]
for slug in sorted(IDS):
 path=ROOT/'assets'/'street'/slug/(slug+'.blend')
 assert path.is_file(),f'Missing required asset: {path}'
 if os.environ.get('ONLY_ASSETS') and slug not in os.environ['ONLY_ASSETS'].split(','):continue
 bpy.ops.wm.open_mainfile(filepath=str(path));a=stats([o for o in bpy.data.collections['ASSET | '+slug].objects if o.type=='MESH']);packed=all(i.packed_file for i in bpy.data.images if i.source=='FILE');glb=path.with_suffix('.glb')
 raw=glb.read_bytes();length,typ=struct.unpack_from('<II',raw,12);doc=json.loads(raw[20:20+length]);assert all('uri' not in x for x in doc.get('buffers',[]));assert all('bufferView' in x for x in doc.get('images',[]))
 bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(glb));b=stats([o for o in bpy.context.scene.objects if o.type=='MESH']);err=max(abs(x-y) for k in ['min','max'] for x,y in zip(a[k],b[k]));assert err<1e-5;assert a['triangles']==b['triangles'];assert b['degenerate_triangles']==0 and b['finite_vertices'];assert packed
 files={p.name:{'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in path.parent.iterdir() if p.suffix in ['.blend','.glb','.jpg']};assert all(v['bytes']<100000000 for v in files.values())
 result={'id':slug,'blend_reopened':True,'glb_reimported':True,'bounds_max_error_m':err,'source':a,'imported':b,'packed_blend_images':packed,'embedded_glb_images':len(doc.get('images',[])),'glb_materials':[{'name':m.get('name'),'pbr':m.get('pbrMetallicRoughness',{})} for m in doc.get('materials',[])],'files':files,'passed':True};results.append(result);(path.parent/'validation.json').write_text(json.dumps(result,indent=2));meta=json.loads((path.parent/'metadata.json').read_text());meta['files']=files;meta['validated']=True;meta['title_ja']={'streetlight':'街路灯','park_bench':'公園ベンチ','traffic_cone':'三角コーン'}[slug];meta['category']='street';meta['glb_bytes']=glb.stat().st_size;meta['blend_bytes']=path.stat().st_size;(path.parent/'metadata.json').write_text(json.dumps(meta,indent=2));print('VALIDATED',slug,flush=True)
(SUPPORT/'validation.json').write_text(json.dumps(results,indent=2))

(SUPPORT/'catalog.json').write_text(json.dumps([json.loads((ROOT/'assets'/'street'/slug/'metadata.json').read_text()) for slug in sorted(IDS)],ensure_ascii=False,indent=2))
