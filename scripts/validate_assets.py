"""Reopen every blend and GLB, check geometry/bounds, and record file sizes."""
import bpy,bmesh,json,math,os
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
results=[]
for blend in sorted((ROOT/'assets').rglob('*.blend')):
 slug=blend.stem;folder=blend.parent
 if os.environ.get("ONLY_ASSETS") and slug not in os.environ["ONLY_ASSETS"].split(","):continue
 bpy.ops.wm.open_mainfile(filepath=str(blend))
 col=bpy.data.collections['ASSET | '+slug];obs=[o for o in col.objects if o.type=='MESH'];cleaned=0
 for ob in obs:
  bm=bmesh.new();bm.from_mesh(ob.data);before=len(bm.verts)
  bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-7)
  bmesh.ops.dissolve_degenerate(bm,edges=list(bm.edges),dist=1e-9)
  bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));cleaned+=before-len(bm.verts);bm.to_mesh(ob.data);bm.free();ob.data.update()
 def stats(meshes):
  pts=[];tri=0;zero=0;finite=True;images=set()
  for o in meshes:
   me=o.data;me.calc_loop_triangles();tri+=len(me.loop_triangles)
   pts.extend(o.matrix_world@v.co for v in me.vertices)
   zero+=sum(1 for t in me.loop_triangles if t.area<1e-14)
   finite=finite and all(math.isfinite(c) for v in me.vertices for c in v.co)
  return {'mesh_count':len(meshes),'triangles':tri,'degenerate_triangles':zero,'finite_vertices':finite,'min':[min(p[i] for p in pts) for i in range(3)],'max':[max(p[i] for p in pts) for i in range(3)]}
 source=stats(obs)
 bpy.ops.object.select_all(action='DESELECT')
 for ob in col.objects:ob.select_set(True)
 bpy.context.view_layer.objects.active=bpy.data.objects[slug]
 bpy.ops.wm.save_as_mainfile(filepath=str(blend),compress=True)
 glb=folder/(slug+'.glb');bpy.ops.export_scene.gltf(filepath=str(glb),export_format='GLB',use_selection=True,export_apply=True)
 # Reload saved editable original.
 bpy.ops.wm.open_mainfile(filepath=str(blend));again=stats([o for o in bpy.data.collections['ASSET | '+slug].objects if o.type=='MESH'])
 assert again==source,(slug,'blend mismatch')
 # Import exported bytes into an empty scene.
 bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(glb));imp=stats([o for o in bpy.context.scene.objects if o.type=='MESH'])
 error=max(abs(a-b) for k in ['min','max'] for a,b in zip(source[k],imp[k]))
 assert error<1e-5,(slug,error)
 assert source['triangles']==imp['triangles'],(slug,'triangle mismatch')
 assert imp['finite_vertices'] and imp['degenerate_triangles']==0,(slug,'bad geometry')
 assert max(blend.stat().st_size,glb.stat().st_size)<100_000_000
 result={'id':slug,'blend_reopened':True,'glb_reimported':True,'source':source,'imported':imp,'max_bounds_error_m':error,'merged_duplicate_vertices':cleaned,'glb_bytes':glb.stat().st_size,'blend_bytes':blend.stat().st_size,'under_100MB':True}
 results.append(result)
 meta=json.loads((folder/'metadata.json').read_text());meta['triangles']=source['triangles'];meta['glb_bytes']=result['glb_bytes'];meta['blend_bytes']=result['blend_bytes'];meta['validated']=True;(folder/'metadata.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n')
if os.environ.get('ONLY_ASSETS') and (ROOT/'validation.json').exists():
 old=json.loads((ROOT/'validation.json').read_text());ids={r['id'] for r in results};results=[r for r in old if r['id'] not in ids]+results
(ROOT/'validation.json').write_text(json.dumps(results,ensure_ascii=False,indent=2)+'\n')
catalog=[json.loads(p.read_text()) for p in sorted((ROOT/'assets').rglob('metadata.json'))];(ROOT/'catalog.json').write_text(json.dumps(catalog,ensure_ascii=False,indent=2)+'\n')
print('VALIDATED_ALL',len(results))
