"""Build five original low-poly diorama assets. Blender 4.3.2, no external assets.
Run: blender -b --python scripts/build_assets.py
"""
import bpy, math, json, os
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1]
CATALOG=[]
def material(name,rgb,metallic=0,rough=.65):
 m=bpy.data.materials.new(name);m.diffuse_color=(*rgb,1);m.use_nodes=True
 p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*rgb,1);p.inputs['Roughness'].default_value=rough;p.inputs['Metallic'].default_value=metallic
 return m
def start():
 bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
 for block in list(bpy.data.materials):bpy.data.materials.remove(block)
 global oak,endgrain,steel,ivory,rubber,teal,terracotta
 oak=material('Warm oak',(.36,.175,.065),0,.40);endgrain=material('Oak edges',(.25,.10,.027),0,.48);steel=material('Charcoal coated steel',(.027,.034,.036),.15,.38);ivory=material('Warm porcelain',(.77,.73,.63),0,.24);rubber=material('Rubber feet',(.018,.023,.026));teal=material('Deep teal enamel',(.19,.235,.21),.15,.34);terracotta=material('Terracotta glaze',(.38,.075,.032),0,.20)
 for ceramic in [terracotta,ivory]:
  bs=ceramic.node_tree.nodes.get('Principled BSDF');bs.inputs['Coat Weight'].default_value=.3;bs.inputs['Coat Roughness'].default_value=.13;bs.inputs['IOR'].default_value=1.46
 scene=bpy.context.scene;scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1;scene.unit_settings.length_unit='METERS'
 bpy.context.scene['asset_convention']='Meters; Blender Z up, front -Y; origin at ground center. GLB standard Y up.'
def assign(ob,name,mat):
 ob.name=name;ob.data.materials.append(mat);return ob
def box(name,loc,scale,mat,bevel=0):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);ob=bpy.context.object;ob.dimensions=scale;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);assign(ob,name,mat)
 if bevel:
  mo=ob.modifiers.new('Low-poly edge bevel','BEVEL');mo.width=bevel;mo.segments=1;bpy.context.view_layer.objects.active=ob;bpy.ops.object.modifier_apply(modifier=mo.name)
 return ob
def cylinder(name,loc,r,depth,mat,n=32,rot=None):
 bpy.ops.mesh.primitive_cylinder_add(vertices=n,radius=r,depth=depth,location=loc);ob=bpy.context.object;assign(ob,name,mat)
 if rot:ob.rotation_euler=rot
 for face in ob.data.polygons:face.use_smooth=(len(face.vertices)==4)
 return ob
def beam(name,a,b,thickness,mat):
 a,b=Vector(a),Vector(b);ob=box(name,(a+b)/2,(thickness,thickness,(b-a).length),mat,.0015);ob.rotation_euler=(b-a).to_track_quat('Z','Y').to_euler();return ob
def geom(name,verts,faces,mat):
 me=bpy.data.meshes.new(name);me.from_pydata(verts,[],faces);me.update();ob=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(ob);assign(ob,name,mat);return ob

def table():
 box('Oak tabletop',(0,0,.731),(1.20,.70,.038),oak,.012)
 # A restrained dark reveal and aprons, visible from below.
 box('Undertop shadow reveal',(0,0,.703),(1.13,.63,.018),endgrain,.003)
 for y in [-.275,.275]:box('Long apron',(0,y,.667),(1.025,.032,.07),oak,.004)
 for x in [-.525,.525]:box('Short apron',(x,0,.667),(.032,.53,.07),oak,.004)
 for x in [-1,1]:
  for y in [-1,1]:
   beam('Tapered stance leg',(x*.54,y*.29,.022),(x*.50,y*.25,.70),.048,oak)
   box('Foot pad',(x*.54,y*.29,.012),(.048,.048,.024),rubber,.002)

def chair():
 box('Oak seat',(0,-.012,.445),(.43,.425,.035),oak,.009)
 box('Seat support',(0,-.01,.416),(.355,.35,.025),steel,.003)
 for x in [-1,1]:
  beam('Front leg',(x*.195,-.19,.012),(x*.16,-.15,.431),.024,steel)
  beam('Rear leg',(x*.195,.19,.012),(x*.16,.15,.431),.024,steel)
  for y in [-.19,.19]:cylinder('Floor glide',(x*.195,y,.007),.016,.014,rubber,8)
  beam('Back upright',(x*.174,.16,.43),(x*.174,.215,.88),.023,steel)
  beam('Side lower brace',(x*.175,-.173,.22),(x*.175,.174,.22),.013,steel)
 for z,y in [(.665,.188),(.80,.206)]:
  ob=box('Oak back slat',(0,y,z),(.405,.028,.10),oak,.007);ob.rotation_euler[0]=math.radians(-7)

def shelf():
 for x in [-.435,.435]:
  for y in [-.155,.155]:
   box('Steel upright',(x,y,.755),(.025,.025,1.51),steel,.003)
   box('Adjustable foot',(x,y,.012),(.035,.035,.024),rubber,.003)
 for k,z in enumerate([.12,.56,1.00,1.455]):
  box('Oak shelf %d'%(k+1),(0,0,z),(.90,.35,.027),oak,.005)
  for y in [-.145,.145]:box('Shelf support rail',(0,y,z-.024),(.86,.018,.025),steel,.002)
 # Anti-racking cross braces at the rear.
 beam('Rear diagonal A',(-.425,.16,.15),(.425,.16,1.43),.012,steel)
 beam('Rear diagonal B',(.425,.163,.15),(-.425,.163,1.43),.012,steel)

def mug():
 n=64;verts=[]
 # Continuous closed cross-section of wall, lip, interior floor and underside.
 rings=[(.034,0),(.038,.005),(.043,.102),(.042,.108),(.037,.108),(.037,.102),(.032,.013),(.0,.013),(.0,0)]
 for r,z in rings:
  for i in range(n):a=2*math.pi*i/n;verts.append((r*math.cos(a),r*math.sin(a),z))
 faces=[]
 for k in range(len(rings)-1):
  for i in range(n):faces.append((k*n+i,k*n+(i+1)%n,(k+1)*n+(i+1)%n,(k+1)*n+i))
 for i in range(n):faces.append(((len(rings)-1)*n+i,(len(rings)-1)*n+(i+1)%n,(i+1)%n,i))
 ob=geom('Mug with open cavity',verts,faces,terracotta);ob.data.materials.append(ivory)
 for p in ob.data.polygons:
  if 4<=p.index//n<=6:p.material_index=1
  p.use_smooth=(p.index//n in [0,1,2,4,5])
 # Faceted C-shaped handle: its endpoints meet the wall, not the interior.
 vv=[];ff=[];steps=32;sides=12
 for i in range(steps+1):
  a=math.radians(-100+200*i/steps);c=Vector((.045+.029*math.cos(a),0,.057+.034*math.sin(a)));normal=Vector((math.cos(a),0,math.sin(a)))
  for j in range(sides):
   t=2*math.pi*j/sides;p=c+normal*(.006*math.cos(t))+Vector((0,.006*math.sin(t),0));vv.append(tuple(p))
 for i in range(steps):
  for j in range(sides):ff.append((i*sides+j,i*sides+(j+1)%sides,(i+1)*sides+(j+1)%sides,(i+1)*sides+j))
 ff.extend([tuple(reversed(range(sides))),tuple(steps*sides+j for j in range(sides))]);handle=geom('Rounded open handle',vv,ff,terracotta)
 for face in list(handle.data.polygons)[:-2]:face.use_smooth=True
 # Center total footprint on the ground origin while keeping transforms applied.
 for ob in list(bpy.context.scene.objects):
  if ob.type=='MESH':ob.location.x-=.016

def signal():
 # Generic Japanese-style hooded LED signal, red phase. Not a specific product replica.
 concrete=material('Concrete base',(.35,.36,.33),0,.92)
 pole=material('Matte galvanized steel',(.34,.345,.35),.35,.86)
 pole.node_tree.nodes.get('Principled BSDF').inputs['Specular IOR Level'].default_value=.25
 housing=material('Neutral light-gray outdoor powder coat',(.43,.425,.415),0,.72)
 hood_inside=material('Dark visor interior',(.025,.028,.028),0,.84)
 bezel=material('Black lens gasket',(.012,.015,.016),0,.72)
 board=material('Dark optical array backing',(.009,.011,.012),0,.45)
 fastener=material('Dull stainless fastener',(.18,.19,.19),.5,.72)
 box('Foundation block',(0,0,.13),(.36,.36,.26),concrete,.025)
 cylinder('Anchor plate',(0,0,.273),.16,.026,steel,8)
 for x in [-.095,.095]:
  for y in [-.095,.095]:cylinder('Anchor bolt',(x,y,.30),.015,.03,fastener,6)
 cylinder('Vertical mast',(0,0,2.60),.065,4.64,pole,48)
 cylinder('Mast cap',(0,0,4.933),.074,.035,pole,48)
 beam('Horizontal mounting arm',(0,.04,4.67),(1.10,.04,4.67),.065,pole)
 for x in [.38,.92]:beam('Rear hanging bracket',(x,.04,4.67),(x,.04,4.43),.035,fastener)
 box('White horizontal signal housing',(.67,-.035,4.34),(1.13,.23,.38),housing,.035)
 # Small cover fasteners add believable serviceable structure without a logo.
 for x in [.14,1.20]:
  for z in [4.205,4.475]:cylinder('Front cover screw',(x,-.153,z),.008,.006,fastener,12,(math.pi/2,0,0))
 lamps=[('Green',.30,(.023,.033,.029),False),('Amber',.67,(.035,.030,.020),False),('Red',1.04,(.52,.015,.006),True)]
 for name,x,rgb,lit in lamps:
  diode=material(name+(' LED lit' if lit else ' LED off'),rgb,0,.32 if lit else .48)
  if lit:
   bs=diode.node_tree.nodes.get('Principled BSDF');bs.inputs['Emission Color'].default_value=(.8,.008,.002,1);bs.inputs['Emission Strength'].default_value=1.8
  cylinder(name+' retaining gasket',(x,-.163,4.34),.145,.028,bezel,64,(math.pi/2,0,0))
  cylinder(name+' optical backing',(x,-.181,4.34),.124,.008,board,64,(math.pi/2,0,0))
  # Hex-packed visible LED faces, one combined mesh per lamp. Hidden package backs are omitted.
  vv=[];ff=[];count=0;pitch=.015
  for row in range(-9,10):
   dz=row*pitch*math.sqrt(3)/2
   for col in range(-9,10):
    dx=(col+(.5 if row%2 else 0))*pitch
    if dx*dx+dz*dz>.112**2:continue
    base=len(vv);count+=1
    for k in range(8):
     t=2*math.pi*k/8;vv.append((x+dx+.0045*math.cos(t),-.190,4.34+dz+.0045*math.sin(t)))
    ff.append(tuple(base+k for k in range(8)))
  array=geom(name+' LED array',vv,ff,diode);array['led_count']=count;array['phase']='lit' if lit else 'off'
  # Visor: white outer finish, dark interior, visible thin lip and open lower half.
  vv=[];nn=32
  for yy,r in [(-.17,.153),(-.39,.153),(-.39,.145),(-.17,.145)]:
   for i in range(nn+1):
    t=math.pi*i/nn;vv.append((x+r*math.cos(t),yy,4.34+r*math.sin(t)))
  ff=[]
  for k in range(4):
   for i in range(nn):ff.append((k*(nn+1)+i,k*(nn+1)+i+1,((k+1)%4)*(nn+1)+i+1,((k+1)%4)*(nn+1)+i))
  ff += [(0,nn+1,2*(nn+1),3*(nn+1)),(nn,2*nn+1,3*nn+2,4*nn+3)]
  visor=geom(name+' white sun visor',vv,ff,housing);visor.data.materials.append(hood_inside)
  for face in visor.data.polygons:
   face.use_smooth=(face.index//nn in [0,2])
   if face.index//nn==2:face.material_index=1
 box('Rear service gasket',(.67,.089,4.34),(.41,.012,.27),bezel,.01)
 box('Rear service panel',(.67,.099,4.34),(.39,.015,.25),housing,.01)
 for x in [.50,.84]:
  for z in [4.25,4.43]:cylinder('Rear service screw',(x,.109,z),.006,.004,fastener,12,(math.pi/2,0,0))
 cylinder('Rear conduit',(.10,.10,4.21),.019,.45,pole,24)

def evaluated_stats(obs):
 dg=bpy.context.evaluated_depsgraph_get();pts=[];tris=0;verts=0
 for o in obs:
  e=o.evaluated_get(dg);m=e.to_mesh();m.calc_loop_triangles();tris+=len(m.loop_triangles);verts+=len(m.vertices);pts.extend(o.matrix_world@v.co for v in m.vertices);e.to_mesh_clear()
 return {'triangles':tris,'vertices':verts,'dimensions_m':[round(max(v[i] for v in pts)-min(v[i] for v in pts),5) for i in range(3)],'bounds_min':[min(v[i] for v in pts) for i in range(3)],'bounds_max':[max(v[i] for v in pts) for i in range(3)]}
def publish_local(slug,title,category,build):
 start();build();scene=bpy.context.scene
 models=[o for o in scene.objects if o.type=='MESH'];asset=bpy.data.collections.new('ASSET | '+slug);scene.collection.children.link(asset)
 for ob in models:
  for c in list(ob.users_collection):c.objects.unlink(ob)
  asset.objects.link(ob)
  bpy.context.view_layer.objects.active=ob;ob.select_set(True);bpy.ops.object.transform_apply(location=False,rotation=True,scale=True);ob.select_set(False)
 stats=evaluated_stats(models)
 folder=ROOT/'assets'/category/slug;folder.mkdir(parents=True,exist_ok=True)
 # GLB has a single named root at ground origin, facilitating scene placement.
 root=bpy.data.objects.new(slug,None);asset.objects.link(root)
 for ob in models:ob.parent=root
 bpy.ops.object.select_all(action='DESELECT');root.select_set(True)
 for ob in models:ob.select_set(True)
 bpy.context.view_layer.objects.active=root
 bpy.ops.export_scene.gltf(filepath=str(folder/(slug+'.glb')),export_format='GLB',use_selection=True,export_apply=True)
 # Studio collection is hidden in normal viewport and omitted from GLB.
 studio=bpy.data.collections.new('PREVIEW STUDIO');scene.collection.children.link(studio)
 lo=Vector(stats['bounds_min']);hi=Vector(stats['bounds_max']);center=(lo+hi)/2;size=max(hi-lo)
 def studio_link(ob):
  for c in list(ob.users_collection):c.objects.unlink(ob)
  studio.objects.link(ob)
 bpy.ops.mesh.primitive_plane_add(size=size*200,location=(0,0,-.002));floor=bpy.context.object;floor.name='Preview ground';floor.data.materials.append(material('Studio sand',(.65,.63,.57)));studio_link(floor)
 for name,offset,power in [('Key',(-3,-4,6),500),('Fill',(4,-2,4),160),('Rim',(2,4,5),350)]:
  bpy.ops.object.light_add(type='AREA',location=center+Vector(offset)*size);ob=bpy.context.object;ob.name=name;ob.data.energy=power*size*size;ob.data.shape='DISK';ob.data.size=size*2.5;ob.rotation_euler=(center-ob.location).to_track_quat('-Z','Y').to_euler();studio_link(ob)
 bpy.ops.object.camera_add(location=center+Vector((1.4,-1.8,1.1))*size);cam=bpy.context.object;cam.name='Preview camera';cam.data.type='ORTHO';cam.data.ortho_scale=size*1.65;cam.rotation_euler=(center-cam.location).to_track_quat('-Z','Y').to_euler();studio_link(cam);scene.camera=cam
 scene.world.use_nodes=True;scene.world.node_tree.nodes['Background'].inputs[0].default_value=(.75,.78,.83,1);scene.world.node_tree.nodes['Background'].inputs[1].default_value=.25
 scene.render.engine='CYCLES';scene.cycles.samples=96;scene.cycles.use_denoising=False;scene.render.resolution_x=900;scene.render.resolution_y=900;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG';scene.view_settings.view_transform='AgX'
 # Named metadata on root is useful without textures or brand-specific assets.
 root['title_ja']=title;root['category']=category;root['scale']='meters';root['design']='Original generic low-poly interpretation, not a measured replica.'
 bpy.ops.object.select_all(action='DESELECT');root.select_set(True);bpy.context.view_layer.objects.active=root
 for screen in bpy.data.screens:
  for area in screen.areas:
   if area.type=='VIEW_3D':
    area.spaces.active.region_3d.view_location=center;area.spaces.active.region_3d.view_distance=size*2;area.spaces.active.region_3d.view_rotation=cam.rotation_euler.to_quaternion();area.spaces.active.region_3d.view_perspective='ORTHO'
 studio.hide_viewport=True
 bpy.ops.wm.save_as_mainfile(filepath=str(folder/(slug+'.blend')),compress=True)
 studio.hide_viewport=False
 for view,offset in [('preview',(1.4,-1.8,1.1)),('back',(-1.4,1.8,1.0))]:
  cam.location=center+Vector(offset)*size;cam.rotation_euler=(center-cam.location).to_track_quat('-Z','Y').to_euler();scene.render.filepath=str(folder/(view+'.png'));bpy.ops.render.render(write_still=True)
 meta={'id':slug,'title_ja':title,'category':category,'units':'meter','up_axis_blend':'Z','up_axis_glb':'Y','front_blend':'-Y','origin':'ground plane; approximate footprint center (signal mast base)','style':'lightweight geometry with smooth curved surfaces; solid-color materials; no image textures','blender_version':bpy.app.version_string,**stats}
 if slug=='traffic_signal':meta['notes']='Generic Japanese-style neutral light-gray hooded LED signal in red phase. Green and amber are dark. Matte galvanized mast, separate LED packages and lens retainers. Dimensions estimated; not an engineering specification.'
 if slug=='traffic_signal':meta['reference_urls']=['https://sales.signal.co.jp/traffic_signal/','https://www.nippon-tsushin.jp/wp/wp-content/themes/nippontsushin/file/business/electric/singou.pdf']
 if slug=='mug':meta['notes']='Open cavity with wall and bottom thickness; rounded C-shaped handle. Decorative model, not a fabrication-ready design.'
 (folder/'metadata.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n');CATALOG.append(meta)
 print('ASSET_COMPLETE',slug,stats,flush=True)
for args in [('oak_table','テーブル','furniture',table),('dining_chair','椅子','furniture',chair),('open_shelf','棚','furniture',shelf),('mug','マグカップ','household',mug),('traffic_signal','信号機','street',signal)]:
 if not os.environ.get('ONLY_ASSETS') or args[0] in os.environ['ONLY_ASSETS'].split(','):publish_local(*args)
CATALOG=[json.loads(p.read_text()) for p in sorted((ROOT/'assets').rglob('metadata.json'))]
(ROOT/'catalog.json').write_text(json.dumps(CATALOG,ensure_ascii=False,indent=2)+'\n')
print('BATCH_COMPLETE',flush=True)
