"""Original generic diorama props. Reproduce: blender -b --python scripts/build_assets.py"""
import bpy, math, json, os, shutil
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1]
HIGH_CURVES=False
A=Path(os.environ.get('ASSET_OUTPUT_ROOT',str(R/'assets')))
bpy.context.preferences.filepaths.save_version=0
def mat(n,c,metal=0,rough=.6):
 m=bpy.data.materials.new(n);m.diffuse_color=(*c,1);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*c,1);p.inputs['Metallic'].default_value=metal;p.inputs['Roughness'].default_value=rough;return m
def mesh(n,v,f,m):
 d=bpy.data.meshes.new(n);d.from_pydata(v,[],f);d.update();o=bpy.data.objects.new(n,d);bpy.context.collection.objects.link(o);o.data.materials.append(m);return o
def box(n,p,s,m,b=.004,segments=3):
 bpy.ops.mesh.primitive_cube_add(size=1,location=p);o=bpy.context.object;o.name=n;o.dimensions=s;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(m)
 if b:
  q=o.modifiers.new('Manufactured radiused edges','BEVEL');q.width=min(b,min(s)*.45);q.segments=segments;bpy.context.view_layer.objects.active=o;bpy.ops.object.modifier_apply(modifier=q.name)
 return o
def cyl(n,p,r,h,m,rot=None,N=None):
 N=N or (96 if HIGH_CURVES else 64)
 bpy.ops.mesh.primitive_cylinder_add(vertices=N,radius=r,depth=h,location=p);o=bpy.context.object;o.name=n;o.data.materials.append(m)
 if rot:o.rotation_euler=rot
 for f in o.data.polygons:f.use_smooth=len(f.vertices)==4
 return o
def uv(n,p,s,m):
 bpy.ops.mesh.primitive_uv_sphere_add(segments=64,ring_count=32,location=p);o=bpy.context.object;o.name=n;o.scale=s;o.data.materials.append(m)
 for f in o.data.polygons:f.use_smooth=True
 return o
def tube(n,p,outer,inner,h,m,axis='Y',arc=2*math.pi):
 v=[];f=[];N=128;closed=arc==2*math.pi;steps=N if closed else N+1
 for y,r in [(-h/2,outer),(h/2,outer),(h/2,inner),(-h/2,inner)]:
  for i in range(steps):
   a=arc*i/N;pt=(r*math.cos(a),y,r*math.sin(a));v.append(tuple(Vector(p)+Vector(pt if axis=='Y' else (pt[0],pt[2],pt[1]))))
 for k in range(4):
  for i in range(N):f.append((k*steps+i,k*steps+(i+1)%steps,((k+1)%4)*steps+(i+1)%steps,((k+1)%4)*steps+i))
 if not closed:f.extend([(0,steps,2*steps,3*steps),(steps-1,2*steps-1,3*steps-1,4*steps-1)])
 o=mesh(n,v,f,m)
 for q in o.data.polygons:q.use_smooth=q.index//N in (0,2)
 return o
def reset():
 
 for ob in list(bpy.data.objects):bpy.data.objects.remove(ob,do_unlink=True)
 for col in list(bpy.data.collections):
  if col.name!='Collection':bpy.data.collections.remove(col)
 for m in list(bpy.data.materials):bpy.data.materials.remove(m)
 global yellow,black,steel,concrete,bolt,white
 yellow=mat('Safety yellow paint',(.83,.54,.008),0,.53);black=mat('Black outdoor coating',(.014,.017,.019),0,.63);steel=mat('Neutral dull galvanized steel',(.34,.35,.36),.45,.77);concrete=mat('Fine light gray concrete',(.37,.38,.38),0,.93);bolt=mat('Dull zinc fasteners',(.25,.26,.27),.5,.63);white=mat('Warm gray powder coat',(.62,.63,.62),.05,.57)
 bpy.context.scene.unit_settings.system='METRIC';bpy.context.scene.unit_settings.scale_length=1

def crossing():
 # One roadside unit; 4 m lowered boom extends +X. No road, track or second gate.
 box('Mast concrete foundation',(0,0,.12),(.42,.42,.24),concrete,.018)
 box('Mast base plate',(0,0,.255),(.27,.27,.03),steel)
 for x in [-.10,.10]:
  for y in [-.10,.10]:cyl('Mast anchor nut',(x,y,.284),.014,.025,bolt,N=6)
 # Continuous striped shell: no hidden cap faces between paint bands.
 mv=[];mf=[];nn=96
 for k in range(19):
  for j in range(nn):a=2*math.pi*j/nn;mv.append((.065*math.cos(a),.065*math.sin(a),.28+k*.19))
 for k in range(18):
  for j in range(nn):mf.append((k*nn+j,k*nn+(j+1)%nn,(k+1)*nn+(j+1)%nn,(k+1)*nn+j))
 mf.extend([tuple(reversed(range(nn))),tuple(18*nn+j for j in range(nn))]);mo=mesh('Continuous mast with alternating painted bands',mv,mf,black);mo.data.materials.append(yellow)
 for q in mo.data.polygons:q.material_index=(q.index//nn)%2 if q.index<18*nn else 0;q.use_smooth=q.index<18*nn
 cyl('Mast top cap',(0,0,3.71),.07,.035,black)
 # Crossmark boards in X, with alternating bands along each blade, front and back.
 for angle in [-math.pi/4,math.pi/4]:
  o=box('Crossbuck continuous yellow blade',(0,-.09,3.35),(1.12,.035,.13),yellow,.007);o.rotation_euler[1]=angle
  for t in [-.44,0,.44]:
   for y in [-.110,.0-.07]:
    o=box('Crossbuck black marking',(t*math.cos(angle),y,3.35-t*math.sin(angle)),(.18,.003,.131),black,.001);o.rotation_euler[1]=angle
 cyl('Crossbuck central attachment',(0,-.116,3.35),.017,.012,bolt,(math.pi/2,0,0),16)
 box('Lamp mounting crossarm',(0,.025,2.65),(.87,.07,.07),steel)
 for x in [-.33,.33]:
  box('Rear lamp bracket',(x,.02,2.60),(.055,.18,.16),steel)
  cyl('Round black warning housing',(x,-.09,2.65),.176,.20,black,(math.pi/2,0,0))
  cyl('Rear removable cover',(x,.018,2.65),.151,.025,black,(math.pi/2,0,0))
  tube('Raised weatherproof lens bezel',(x,-.205,2.65),.157,.137,.035,black)
  lens=mat('Red lamp '+('illuminated' if x<0 else 'unlit'),(.40,.007,.003) if x<0 else (.085,.005,.003),0,.24)
  if x<0:
   p=lens.node_tree.nodes.get('Principled BSDF');p.inputs['Emission Color'].default_value=(.70,.006,.002,1);p.inputs['Emission Strength'].default_value=.6
  # Convex front optics with one flat hidden back, rather than an unseen rear hemisphere.
  lv=[(x,-.235,2.65)];lf=[];ln=64;lr=16
  for k in range(1,lr+1):
   phi=(math.pi/2)*k/lr;r=.136*math.sin(phi);yy=-.211-.024*math.cos(phi)
   for j in range(ln):a=2*math.pi*j/ln;lv.append((x+r*math.cos(a),yy,2.65+r*math.sin(a)))
  for j in range(ln):lf.append((0,1+j,1+(j+1)%ln))
  for k in range(lr-1):
   for j in range(ln):lf.append((1+k*ln+j,1+(k+1)*ln+j,1+(k+1)*ln+(j+1)%ln,1+k*ln+(j+1)%ln))
  lf.append(tuple(reversed([1+(lr-1)*ln+j for j in range(ln)])));lo=mesh('Convex red optical lens',lv,lf,lens)
  for q in lo.data.polygons:q.use_smooth=q.index<len(lf)-1
  # concentric optical mouldings create real relief, not a flat coloured disc.
  for rr in [.038,.066,.094,.121]:
   tube('Concentric Fresnel lens rib',(x,-.2125-.024*math.sqrt(1-(rr/.136)**2),2.65),rr,rr-.0025,.0025,lens)
  tube('Deep upper sun hood',(x,-.275,2.65),.181,.171,.30,black,arc=math.pi)
  for dx in [-.125,.125]:cyl('Housing rear screw',(x+dx,.034,2.65),.006,.006,bolt,(math.pi/2,0,0),12)
  cyl('Rear cable gland',(x,.06,2.56),.014,.065,black)
 # Small loudspeaker with open horn and grille beneath lamps.
 cyl('Warning sounder housing',(0,-.085,2.21),.095,.16,black,(math.pi/2,0,0))
 tube('Sounder rim',(0,-.177,2.21),.094,.072,.025,black)
 cyl('Recessed sounder diaphragm',(0,-.168,2.21),.071,.008,steel,(math.pi/2,0,0))
 for x in [-.04,-.02,0,.02,.04]:box('Sounder grille',(x,-.193,2.21),(.004,.006,2*math.sqrt(.067**2-x*x)),black,.001)
 # Continuous rear conduit, mast entry elbow, junction and wired lamp glands.
 def conduit(name,pts,r=.011):
  cu=bpy.data.curves.new(name,'CURVE');cu.dimensions='3D';cu.resolution_u=12;cu.bevel_depth=r;cu.bevel_resolution=5;cu.use_fill_caps=True
  sp=cu.splines.new('BEZIER');sp.bezier_points.add(len(pts)-1)
  for bp,p in zip(sp.bezier_points,pts):bp.co=p;bp.handle_left_type='AUTO';bp.handle_right_type='AUTO'
  ob=bpy.data.objects.new(name,cu);bpy.context.collection.objects.link(ob);ob.data.materials.append(black);bpy.context.view_layer.objects.active=ob;ob.select_set(True);bpy.ops.object.convert(target='MESH');ob.select_set(False)
 conduit('Continuous rear mast conduit with entry elbow',[(0,.04,.55),(0,.10,.59),(0,.10,.75),(0,.10,2.40),(0,.10,2.51)])
 box('Rear conduit junction box',(0,.105,2.50),(.09,.07,.11),black,.008)
 for xx in [-.33,.33]:conduit('Lamp cable from junction to gland',[(0,.12,2.52),(xx*.45,.12,2.52),(xx,.10,2.49),(xx,.06,2.54)],.009)
 for zz in [.80,1.45,2.12]:
  cyl('Mast conduit clamp band',(0,0,zz),.068,.018,steel,N=96)
  for xx in [-.018,.018]:box('Conduit saddle bridge leg',(xx,.085,zz),(.008,.060,.030),steel,.002)
  box('Rear conduit retaining saddle',(0,.111,zz),(.045,.025,.035),steel,.004)
  for xx in [-.016,.016]:cyl('Conduit saddle fastener',(xx,.127,zz),.004,.006,bolt,(math.pi/2,0,0),12)
 # Separate drive unit; restrained gray housing, realistic flange/pivot and cover fasteners.
 gx=.55;gy=.05
 box('Barrier concrete foundation',(gx,gy,.10),(.55,.48,.20),concrete,.018)
 box('Drive pedestal',(gx,gy,.43),(.25,.26,.46),steel,.018)
 box('Drive enclosure',(gx,gy,.80),(.46,.34,.38),white,.035)
 box('Drive rear cover gasket',(gx,.229,.8),(.35,.009,.27),black,.015)
 box('Drive rear inspection lid',(gx,.237,.8),(.33,.012,.25),white,.013)
 for x in [gx-.13,gx+.13]:
  for z in [.71,.89]:cyl('Drive cover screw',(x,.246,z),.009,.006,bolt,(math.pi/2,0,0),12)
 cyl('Drive shaft',(gx,-.175,.88),.067,.13,steel,(math.pi/2,0,0))
 cyl('Boom pivot hub',(gx,-.25,.88),.115,.065,black,(math.pi/2,0,0))
 box('Boom socket clamp',(gx+.16,-.25,.88),(.37,.12,.13),steel,.009)
 # Continuous tapered round fibreglass arm with contrasting material slots.
 v=[];f=[];N=64;segments=16
 for k in range(segments+1):
  x=gx+.12+4*k/segments;r=.057-.025*k/segments
  for j in range(N):a=2*math.pi*j/N;v.append((x,-.25+r*math.cos(a),.88+r*math.sin(a)))
 for k in range(segments):
  for j in range(N):f.append((k*N+j,k*N+(j+1)%N,(k+1)*N+(j+1)%N,(k+1)*N+j))
 f.extend([tuple(reversed(range(N))),tuple(segments*N+j for j in range(N))]);o=mesh('Four metre tapered lowered striped boom',v,f,yellow);o.data.materials.append(black)
 for p in o.data.polygons:p.material_index=(p.index//N)%2 if p.index<segments*N else 0;p.use_smooth=p.index<segments*N
 for x in [gx+.12,gx+.28]:cyl('Boom clamp bolt',(x,-.32,.88),.012,.018,bolt,(math.pi/2,0,0),6)


def binprop():
 blue=mat('Muted blue recycling insert',(.035,.16,.29),0,.55);interior=mat('Dark removable liner',(.035,.038,.041),0,.8)
 # Hollow cabinet, actual front aperture and internal liner; front service door below.
 box('Recessed plinth',(0,0,.045),(.42,.38,.09),black,.01)
 for x in [-.233,.233]:
  box('Two millimetre folded side sheet',(x,0,.52),(.002,.44,.94),white,.0008)
  for y in [-.211,.211]:box('Side sheet folded return',(x+(.009 if x<0 else -.009),y,.52),(.020,.002,.94),white,.0008)
 box('Rear cabinet panel',(0,.211,.52),(.44,.018,.94),white,.007)
 box('Cabinet floor',(0,0,.105),(.44,.42,.018),steel)
 box('Weather cap',(0,0,1.00),(.48,.47,.035),white,.012,8)
 box('Front access door gasket',(0,-.213,.405),(.43,.012,.58),black,.006)
 doorpaint=mat('Gray painted steel service door',(.27,.29,.31),0,.43)
 doorpaint.node_tree.nodes.get('Principled BSDF').inputs['Coat Weight'].default_value=.12
 box('Two millimetre painted door skin',(0,-.233,.405),(.415,.002,.565),doorpaint,.0008)
 for x in [-.201,.201]:box('Door folded vertical return',(x,-.226,.405),(.012,.012,.565),doorpaint,.001)
 for z in [.128,.682]:box('Door folded horizontal return',(0,-.226,z),(.402,.012,.012),doorpaint,.001)
 # upper insertion panel with real round holes.
 plate=box('Blue sorting aperture fascia',(0,-.218,.835),(.432,.026,.30),blue,.009)
 for x in [-.105,.105]:
  cut=cyl('Temporary aperture cutter',(x,-.218,.86),.066,.10,black,(math.pi/2,0,0))
  bpy.context.view_layer.objects.active=plate;mod=plate.modifiers.new('True insertion opening','BOOLEAN');mod.operation='DIFFERENCE';mod.object=cut;bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(cut,do_unlink=True)
  tube('Rounded insertion collar',(x,-.236,.86),.073,.063,.027,black)
  tube('Deep insertion chute',(x,-.178,.86),.064,.060,.10,interior)
 # actual hollow liner visible through openings, lower down.
 for x in [-.185,.185]:box('Liner side',(x,0,.42),(.008,.35,.60),interior,.002)
 for y in [-.17,.17]:box('Liner front or rear',(0,y,.42),(.37,.008,.60),interior,.002)
 box('Liner bottom',(0,0,.125),(.37,.35,.01),interior,.002)
 for z in [.25,.55]:
  box('Fixed hinge mounting return',(-.224,-.223,z),(.022,.030,.042),white,.002)
  box('Door hinge attachment seat',(-.195,-.236,z),(.020,.006,.042),doorpaint,.001)
  for x in [-.219,-.195]:box('Hinge attachment leaf',(x,-.240,z),(.020,.004,.042),bolt,.001)
  cyl('Vertical hinge pin',(-.207,-.248,z),.003,.052,bolt,N=32)
  for dz in [-.017,0,.017]:cyl('Separated hinge barrel knuckle',(-.207,-.248,z+dz),.006,.015,bolt,N=48)
  for x in [-.220,-.194]:cyl('Hinge leaf screw',(x,-.244,z),.0035,.005,bolt,(math.pi/2,0,0),12)
 cyl('Recessed door lock',( .16,-.239,.62),.014,.008,bolt,(math.pi/2,0,0),32)
 box('Lock slot',(.16,-.244,.62),(.002,.001,.012),black,.0005)
 # Simple formed pictograms: can (left), PET-style bottle (right), no lettering.
 pict=mat('Ivory pictogram',(.8,.82,.81),0,.65)
 box('Can pictogram',(-.105,-.236,.744),(.025,.002,.035),pict,.004)
 for z in [.727,.761]:box('Can pictogram rim',(-.105,-.238,z),(.027,.002,.003),pict,.001)
 box('Bottle pictogram body',(.105,-.236,.742),(.022,.002,.032),pict,.005)
 box('Bottle pictogram shoulder',(.105,-.236,.760),(.014,.002,.011),pict,.003)
 box('Bottle pictogram neck',(.105,-.236,.768),(.009,.002,.01),pict,.001)
 for x in [-.18,.18]:
  for y in [-.155,.155]:cyl('Adjustable rubber foot',(x,y,.012),.018,.024,black,N=32)
 for z in [.16,.89]:
  for x in [-.18,.18]:cyl('Rear panel fastener',(x,.224,z),.004,.004,bolt,(math.pi/2,0,0),12)


def stats(obs):
 pts=[];tri=0;bad=0
 for o in obs:
  m=o.data;m.calc_loop_triangles();tri+=len(m.loop_triangles)
  for t in m.loop_triangles:
   a,b,c=[o.matrix_world@m.vertices[i].co for i in t.vertices]
   if (b-a).cross(c-a).length<1e-12:bad+=1
  pts += [o.matrix_world@v.co for v in m.vertices]
 lo=[min(p[i] for p in pts) for i in range(3)];hi=[max(p[i] for p in pts) for i in range(3)]
 return dict(triangles=tri,zero_area_triangles=bad,finite_coordinates=all(math.isfinite(c) for p in pts for c in p),bounds_min=lo,bounds_max=hi,dimensions_m=[hi[i]-lo[i] for i in range(3)])
def build(slug,fn,refs,notes,close):
 global HIGH_CURVES
 HIGH_CURVES=fn==crossing
 
 if os.environ.get('ONLY_ASSETS') and slug not in os.environ['ONLY_ASSETS'].split(','):return
 reset();fn();sc=bpy.context.scene;obs=[o for o in sc.objects if o.type=='MESH'];col=bpy.data.collections.new('ASSET | '+slug);sc.collection.children.link(col)
 root=bpy.data.objects.new(slug,None);col.objects.link(root);root['units']='meters';root['notes']=notes
 for o in obs:
  for c in list(o.users_collection):c.objects.unlink(o)
  col.objects.link(o);
  if o.parent is None:o.parent=root
 st=stats(obs);folder=A/slug;folder.mkdir(parents=True,exist_ok=True)
 bpy.ops.object.select_all(action='DESELECT');root.select_set(True)
 for o in obs:o.select_set(True)
 bpy.ops.export_scene.gltf(filepath=str(folder/(slug+'.glb')),export_format='GLB',use_selection=True,export_extras=True)
 studio=bpy.data.collections.new('PREVIEW STUDIO');sc.collection.children.link(studio)
 def move(o):
  for c in list(o.users_collection):c.objects.unlink(o)
  studio.objects.link(o)
 lo=Vector(st['bounds_min']);hi=Vector(st['bounds_max']);center=(lo+hi)/2;sz=max(hi-lo)
 bpy.ops.mesh.primitive_plane_add(size=200,location=(0,0,-.004));o=bpy.context.object;o.data.materials.append(mat('Preview neutral ground',(.32,.34,.37),0,.85));move(o)
 for p,power in [((-3,-4,6),450),((4,-1,4),180),((1,4,5),350)]:
  bpy.ops.object.light_add(type='AREA',location=center+Vector(p)*sz);o=bpy.context.object;o.data.energy=power*sz*sz;o.data.shape='DISK';o.data.size=sz*3;o.rotation_euler=(center-o.location).to_track_quat('-Z','Y').to_euler();move(o)
 bpy.ops.object.camera_add();cam=bpy.context.object;move(cam);sc.camera=cam;cam.data.type='ORTHO'
 sc.world.use_nodes=True;sc.world.node_tree.nodes['Background'].inputs[0].default_value=(.65,.69,.75,1);sc.world.node_tree.nodes['Background'].inputs[1].default_value=.3
 sc.render.engine='CYCLES';sc.cycles.samples=48;sc.cycles.use_denoising=False;sc.render.resolution_x=1200;sc.render.resolution_y=1000;sc.render.resolution_percentage=100;sc.render.image_settings.file_format='JPEG';sc.render.image_settings.quality=92;sc.view_settings.view_transform='AgX'
 for name,offset,target,scale in ([] if os.environ.get('SKIP_RENDER') else [('front_three_quarter',(1,-2.7,.95),center,sz*(1.35 if fn==crossing else 1.65)),('rear',(-1,2.7,.9),center,sz*(1.35 if fn==crossing else 1.65)),('close_up',(.25,-2,.35),Vector(close[0]),close[1])]):
  cam.location=target+Vector(offset)*sz;cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=scale;sc.render.filepath=str(folder/(name+'.jpg'));bpy.ops.render.render(write_still=True)
 
 if not os.environ.get('SKIP_RENDER'):
  shutil.copyfile(folder/'front_three_quarter.jpg',folder/'preview.jpg');shutil.copyfile(folder/'rear.jpg',folder/'back.jpg')
 cam.location=center+Vector((1,-2.7,.95))*sz;cam.rotation_euler=(center-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=sz*(1.35 if fn==crossing else 1.65)
 studio.hide_viewport=True;bpy.ops.wm.save_as_mainfile(filepath=str(folder/(slug+'.blend')),compress=True)
 meta={'id':slug,'title_ja':'踏切' if fn==crossing else '分別ごみ箱','category':'street','glb_bytes':(folder/(slug+'.glb')).stat().st_size,'blend_bytes':(folder/(slug+'.blend')).stat().st_size,'units':'meters','front_blend':'-Y','up_blend':'Z','up_glb':'Y','origin':'ground at mast center' if fn==crossing else 'ground at cabinet center','reference_urls':refs,'notes':notes,'blender_version':bpy.app.version_string,'textures':'none; all PBR materials embedded','review_status':'pending independent review',**st}
 meta['files_bytes']={p.name:p.stat().st_size for p in folder.iterdir() if p.is_file() and p.suffix in ['.glb','.blend','.jpg']};(folder/'metadata.json').write_text(json.dumps(meta,indent=2)+'\n')
 print('READY',slug,st,flush=True)
