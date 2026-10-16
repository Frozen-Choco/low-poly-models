import bpy, math,json,hashlib,os
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];W=R.parent
BASE={slug:R/'baseline'/slug for slug in ['traffic_signal','railway_crossing_lowered']}
EXPECTED={'traffic_signal':'48eae1558590d0877f9e2ba96a80bcc5c8c70729b2d0d178395b877ef3fd2162','railway_crossing_lowered':'9785c6d533c3f739576bc337dfc1d272cb957874808cfee71937be7ba899528c'}
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def material_snapshot():
 return {m.name:{k:list(v.default_value) if hasattr(v.default_value,'__len__') else v.default_value for k in ['Base Color','Metallic','Roughness','Emission Color','Emission Strength'] if (v:=m.node_tree.nodes.get('Principled BSDF').inputs.get(k))} for m in bpy.data.materials if m.use_nodes and m.node_tree.nodes.get('Principled BSDF')}
def relocate(o,col,root):
 for c in list(o.users_collection):c.objects.unlink(o)
 col.objects.link(o);o.parent=root
 return o

def cylinder(name,loc,r,depth,mat,col,root,rotation=(0,0,0)):
 bpy.ops.mesh.primitive_cylinder_add(vertices=48,radius=r,depth=depth,location=loc,rotation=rotation);o=bpy.context.object;o.name=name;o.data.materials.append(mat)
 for p in o.data.polygons:p.use_smooth=len(p.vertices)==4
 return relocate(o,col,root)
def stats(obs):
 pts=[];tris=0;bad=0
 for o in obs:
  me=o.data;me.calc_loop_triangles();tris+=len(me.loop_triangles)
  for t in me.loop_triangles:
   a,b,c=[o.matrix_world@me.vertices[i].co for i in t.vertices]
   bad+=(b-a).cross(c-a).length<1e-12
  pts.extend(o.matrix_world@v.co for v in me.vertices)
 lo=[min(v[i] for v in pts) for i in range(3)];hi=[max(v[i] for v in pts) for i in range(3)]
 return {'triangles':tris,'zero_area_triangles':bad,'finite_coordinates':all(math.isfinite(c) for p in pts for c in p),'bounds_min':lo,'bounds_max':hi,'dimensions_m':[hi[i]-lo[i] for i in range(3)]}
for slug,base in BASE.items():
 if os.environ.get("ONLY_ASSETS") and slug not in os.environ["ONLY_ASSETS"].split(","):continue
 p=base/(slug+'.blend');assert digest(p)==EXPECTED[slug]
 bpy.ops.wm.open_mainfile(filepath=str(p));col=bpy.data.collections['ASSET | '+slug];root=bpy.data.objects[slug];before=material_snapshot();changes=[]
 if slug=='traffic_signal':
  for o in list(col.objects):
   if o.name.startswith(('Rear service gasket','Rear service panel','Rear service screw')):o.location.y-=.003
  for o in col.objects:
   if o.name.startswith('Rear service screw'):o.location.y-=.001
  old=bpy.data.objects['Rear conduit'];bpy.data.objects.remove(old,do_unlink=True)
  rubber=bpy.data.materials['Black lens gasket']
  cu=bpy.data.curves.new('Connected rear flexible cable','CURVE');cu.dimensions='3D';cu.bevel_depth=.009;cu.bevel_resolution=5;cu.resolution_u=16;cu.use_fill_caps=True
  pts=[(.67,.04,4.645),(.67,.09,4.56),(.67,.17,4.39),(.67,.18,4.16),(.67,.16,4.13),(.67,.14,4.19),(.67,.14,4.32),(.67,.113,4.34)]
  sp=cu.splines.new('BEZIER');sp.bezier_points.add(len(pts)-1)
  for bp,co in zip(sp.bezier_points,pts):bp.co=co;bp.handle_left_type='AUTO';bp.handle_right_type='AUTO'
  o=bpy.data.objects.new('Rear cable from support arm to service cover',cu);col.objects.link(o);o.parent=root;o.data.materials.append(rubber);bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o;bpy.ops.object.convert(target='MESH')
  cylinder('Support arm cable entry gland',(.67,.04,4.638),.018,.025,rubber,col,root)
  cylinder('Service cover cable entry gland',(.67,.1115,4.34),.023,.025,rubber,col,root,(math.pi/2,0,0))
  changes=['Floating rear conduit replaced by flexible cable connected to underside of support arm and rear cover gland, following photographed rear cable loop.','Rear gasket, cover and screws shifted 3 mm toward housing to seat gasket; screw heads seated a further 1 mm into cover. Palette and lamp phases preserved.']
 else:
  mast=bpy.data.objects['Continuous mast with alternating painted bands'];inv=mast.matrix_world.inverted()
  for v in mast.data.vertices:
   q=mast.matrix_world@v.co
   if q.z<.281:q.z=.27;v.co=inv@q
  # Manufacturer attachment principle: mounting plate and two U-bolts around mast.
  metal=bpy.data.objects['Mast base plate'].data.materials[0]
  bpy.ops.mesh.primitive_cube_add(size=1,location=(0,-.074,3.35));o=bpy.context.object;o.name='Crossbuck bolted mounting plate';o.dimensions=(.18,.010,.16);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(metal);relocate(o,col,root)
  for z in [3.30,3.40]:
   # Outer rear semicircle follows mast; 5 mm wire touches the 65 mm mast.
   pts=[(-.070,-.116,z),(-.070,0,z)]+[(.070*math.cos(a),.070*math.sin(a),z) for a in [math.pi-i*math.pi/32 for i in range(1,33)]]+[(.070,-.116,z)]
   cu=bpy.data.curves.new('Crossbuck U-bolt path','CURVE');cu.dimensions='3D';cu.bevel_depth=.0052;cu.bevel_resolution=3;cu.use_fill_caps=True
   sp=cu.splines.new('POLY');sp.points.add(len(pts)-1)
   for bp,co in zip(sp.points,pts):bp.co=(*co,1)
   o=bpy.data.objects.new('Crossbuck U-bolt around mast',cu);col.objects.link(o);o.parent=root;o.data.materials.append(metal);bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o;bpy.ops.object.convert(target='MESH')
   for x in [-.070,.070]:cylinder('Crossbuck U-bolt front nut',(x,-.112,z),.010,.012,metal,col,root,(math.pi/2,0,0))
  names=('Barrier concrete foundation','Drive pedestal','Drive enclosure','Drive rear cover gasket','Drive rear inspection lid','Drive cover screw','Drive shaft','Boom pivot hub','Boom socket clamp','Four metre tapered lowered striped boom','Boom clamp bolt')
  for o in col.objects:
   if o.name.startswith(names):o.location.x+=.10
  root['gate_pivot_m']=[.65,-.25,.88];root['design_pose']='Static lowered; geometric diagnostic swept 0–90 degrees, not operational rig'
  changes=['Mast bottom ring extended down 10 mm to contact base plate; all upper bands and attachments preserved.','Crossbuck mounting plate and two U-bolts added using documented manufacturer attachment principle; artist-estimated dimensions.', 'Complete separate barrier foundation, drive, pivot and boom assembly translated 100 mm outward to clear warning lamp hood through conventional upright diagnostic.']
 bpy.context.view_layer.update();assert material_snapshot()==before
 folder=R/'assets'/slug;folder.mkdir(parents=True,exist_ok=True);st=stats([o for o in col.objects if o.type=='MESH'])
 bpy.ops.object.select_all(action='DESELECT')
 for o in col.objects:o.select_set(True)
 bpy.context.view_layer.objects.active=root
 bpy.ops.export_scene.gltf(filepath=str(folder/(slug+'.glb')),export_format='GLB',use_selection=True,export_extras=True,export_apply=True)
 bpy.ops.wm.save_as_mainfile(filepath=str(folder/(slug+'.blend')),compress=True)
 meta=json.loads((base/'metadata.json').read_text());meta.update(st);meta['title_ja']={'traffic_signal':'信号機','railway_crossing_lowered':'踏切'}[slug];meta['review_status']='pending independent exact-file functional review';meta['attachment_revision']={'baseline_sha256':EXPECTED[slug],'changes':changes,'material_parameters_exactly_preserved':True};meta['notes']+=' Attachment/contact revision. Dimensions remain artist estimates; geometric tests are not manufacturing or safety certification.'
 if slug=='traffic_signal':meta['notes']=meta['notes'].replace('Geometry and lamp layout unchanged.','Lamp layout and palette preserved; rear cable geometry revised.')
 for ext in ['glb','blend']:meta[ext+'_bytes']=(folder/(slug+'.'+ext)).stat().st_size
 (folder/'metadata.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n')
 print('SAVED',slug,st,flush=True)
