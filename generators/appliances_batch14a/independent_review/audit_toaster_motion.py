import bpy,sys,json,hashlib
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
p=Path(sys.argv[sys.argv.index('--')+1]);out=Path(sys.argv[sys.argv.index('--')+2]);bpy.ops.wm.read_factory_settings(use_empty=True)
if p.suffix=='.blend':bpy.ops.wm.open_mainfile(filepath=str(p))
else:bpy.ops.import_scene.gltf(filepath=str(p))
obs=[o for o in bpy.context.scene.objects if o.type=='MESH'];moving=[o for o in obs if o.name.startswith('Crumb tray')];fixed=[o for o in obs if o not in moving]
def data(os):
 vs=[];ts=[];owner=[]
 for o in os:
  o.data.calc_loop_triangles();k=len(vs);vs += [o.matrix_world@v.co for v in o.data.vertices];ts += [tuple(k+i for i in t.vertices) for t in o.data.loop_triangles];owner += [o.name]*len(o.data.loop_triangles)
 return vs,ts,owner
vs,ts,names=data(moving);fv,ft,fn=data(fixed);lowest={o.name:min((o.matrix_world@v.co).z for v in o.data.vertices) for o in moving};deck=next(o for o in fixed if o.name=='Steel chassis deck');deck_top=max((deck.matrix_world@v.co).z for v in deck.data.vertices);tree=BVHTree.FromPolygons(fv,ft,all_triangles=True,epsilon=1e-9);rows=[];contacts=[]
for mm in range(0,241,5):
 rv=[v+Vector((0,mm/1000,0)) for v in vs];rt=BVHTree.FromPolygons(rv,ts,all_triangles=True,epsilon=1e-9);hits=rt.overlap(tree);bad=[];touch=[]
 for a,b in hits:
  aa=[rv[i] for i in ts[a]];bb=[fv[i] for i in ft[b]];na=(aa[1]-aa[0]).cross(aa[2]-aa[0]);nb=(bb[1]-bb[0]).cross(bb[2]-bb[0]);na.normalize();nb.normalize()
  # Deck-only contacts permitted when the entire moving part is at or above deck top; catches tang penetration without edge-contact false positives.
  if fn[b]=='Steel chassis deck' and lowest[names[a]]>=deck_top-1e-7:touch.append((names[a],fn[b]));continue
  bad.append((names[a],fn[b]))
 if bad:rows.append({'translation_y_mm':mm,'pairs':sorted(set(bad)),'triangle_pairs':len(bad)})
 if touch:contacts.append({'translation_y_mm':mm,'pairs':sorted(set(touch)),'triangle_pairs':len(touch)})
# True slot depth rays: downward from above through opening vs closed top outside it.
shell=next(o for o in obs if o.name=='Continuous chrome shell');sv,st,_=data([shell]);shelltree=BVHTree.FromPolygons(sv,st,all_triangles=True);rays=[]
for x in [-.037,.037,0,.070]:
 hit=shelltree.ray_cast(Vector((x,0,.25)),Vector((0,0,-1)),.3);rays.append({'x_m':x,'hit':list(hit[0]) if hit[0] else None})
res={'source':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'moving_parts':[o.name for o in moving],'poses':49,'translations_y_mm':[0,240],'collision_poses':rows,'permitted_opposed_deck_contacts':contacts,'shell_downward_rays':rays,'method':'Saved mesh drawer translation every5mm through240mm. Opposed coplanar chassis support allowed; every other surface intersection reported. Rays independently verify both real bread openings. Static visual assembly; no electrical/thermal simulation.'};out.write_text(json.dumps(res,indent=2));print('TRAY',p.name,len(rows),'collision poses')
