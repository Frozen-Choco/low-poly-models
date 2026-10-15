import bpy,json,math,sys,os
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from build_assets import stats
R=Path(__file__).resolve().parents[1];A=Path(os.environ.get('ASSET_OUTPUT_ROOT',str(R/'assets')));reports=[]
for asset_id in ['public_recycling_bin','railway_crossing_lowered']:
 folder=A/asset_id
 slug=folder.name
 if os.environ.get('ONLY_ASSETS') and slug not in os.environ['ONLY_ASSETS'].split(','):continue
 meta=json.loads((folder/'metadata.json').read_text());rec={'asset':slug,'checks':{}}
 bpy.ops.wm.open_mainfile(filepath=str(folder/(slug+'.blend')))
 obs=list(bpy.data.collections['ASSET | '+slug].objects);s=stats([o for o in obs if o.type=='MESH']);rec['blend_reopened']=s
 
 for o in list(bpy.data.objects):bpy.data.objects.remove(o,do_unlink=True)
 bpy.ops.import_scene.gltf(filepath=str(folder/(slug+'.glb')))
 objs=[o for o in bpy.context.scene.objects if o.type=='MESH'];s2=stats(objs);rec['glb_reimported']=s2
 rec['checks']['finite']=s['finite_coordinates'] and s2['finite_coordinates'];rec['checks']['no_degenerate_triangles']=s['zero_area_triangles']==s2['zero_area_triangles']==0
 rec['checks']['triangle_count_matches']=s['triangles']==s2['triangles']==meta['triangles'];rec['checks']['dimensions_match']=max(abs(a-b) for a,b in zip(s['dimensions_m'],s2['dimensions_m']))<.0001
 rec['checks']['all_files_under_100MB']=all(p.stat().st_size<100000000 for p in folder.iterdir() if p.is_file());rec['checks']['no_external_image_dependency']=all(im.packed_file or im.source!='FILE' for im in bpy.data.images)
 rec['checks']['canonical_preview_aliases_match']=(folder/'preview.jpg').read_bytes()==(folder/'front_three_quarter.jpg').read_bytes() and (folder/'back.jpg').read_bytes()==(folder/'rear.jpg').read_bytes()
 rec['all_pass']=all(rec['checks'].values());reports.append(rec)
(R/('validation_'+os.environ['ONLY_ASSETS']+'.json' if os.environ.get('ONLY_ASSETS') else 'validation.json')).write_text(json.dumps(reports,indent=2)+'\n');print(json.dumps(reports,indent=2))
assert all(r['all_pass'] for r in reports)
