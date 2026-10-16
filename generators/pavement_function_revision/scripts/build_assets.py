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
import numpy as np
IDS=['cast_iron_manhole','concrete_curb_straight','steel_roadside_bollard']
def texture_material(name,color,rough,metal,amplitude=.08):
 m=mat(name,color,metal,rough);nodes=m.node_tree.nodes;links=m.node_tree.links;p=nodes.get('Principled BSDF');rng=np.random.default_rng(420+len(name));n=512
 # Original seeded texture raster: multi-scale aggregate/oxidation, with periodic edges.
 coarse=rng.random((32,32));field=np.repeat(np.repeat(coarse,16,0),16,1)
 for i in range(10):field=(field+np.roll(field,1,0)+np.roll(field,-1,0)+np.roll(field,1,1)+np.roll(field,-1,1))/5
 grain=rng.normal(0,1,(n,n));h=.6*field+.12*grain
 pores=rng.random((n,n))<.025;h[pores]-=.6
 if 'concrete' in name or 'enamel' in name:
  # Periodic Gaussian-filtered continuous noise, with no repeated grid cells.
  freq=np.fft.fftfreq(n);kernel=np.exp(-2*np.pi**2*24**2*(freq[:,None]**2+freq[None,:]**2))
  smooth=np.fft.ifft2(np.fft.fft2(rng.normal(size=(n,n)))*kernel).real
  smooth=(smooth-smooth.mean())/(smooth.std()+1e-9)
  h=.3+.035*smooth+.025*grain
  pores=rng.random((n,n))<.006;h[pores]-=.15
 def img(suffix,pixels,noncolor=False):
  im=bpy.data.images.new(name+' '+suffix,width=n,height=n,alpha=True);im.pixels.foreach_set(pixels.astype(np.float32).ravel());im.pack()
  if noncolor:im.colorspace_settings.name='Non-Color'
  node=nodes.new('ShaderNodeTexImage');node.image=im;node.interpolation='Linear';return node
 rgba=np.ones((n,n,4));rgba[:,:,:3]=np.clip(np.array(color)[None,None,:]*(1+amplitude*(h[:,:,None]-.3)*5),.005,.95)
 tex=img('basecolor baked',rgba);links.new(tex.outputs['Color'],p.inputs['Base Color'])
 rgba[:,:,:3]=np.clip(rough+(h[:,:,None]-.3)*.15,.1,1);tx=img('roughness baked',rgba,True);links.new(tx.outputs['Color'],p.inputs['Roughness'])
 dx=(np.roll(h,1,1)-np.roll(h,-1,1))*.12;dy=(np.roll(h,1,0)-np.roll(h,-1,0))*.12
 rgba[:,:,0]=dx+.5;rgba[:,:,1]=dy+.5;rgba[:,:,2]=1;tx=img('normal baked',rgba,True);nm=nodes.new('ShaderNodeNormalMap');links.new(tx.outputs['Color'],nm.inputs['Color']);links.new(nm.outputs['Normal'],p.inputs['Normal'])
 return m

def reset():
 bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
 for co in list(bpy.data.collections):
  if co.name!='Collection':bpy.data.collections.remove(co)
 for m in list(bpy.data.materials):bpy.data.materials.remove(m)
 bpy.context.scene.unit_settings.system='METRIC';bpy.context.scene.unit_settings.scale_length=1

def unwrap(ob):
 bpy.ops.object.select_all(action='DESELECT');ob.select_set(True);bpy.context.view_layer.objects.active=ob;bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.uv.smart_project(island_margin=.01);bpy.ops.object.mode_set(mode='OBJECT')
def bevel(ob,w,seg=3):
 bpy.context.view_layer.objects.active=ob;mod=ob.modifiers.new('Cast or fabricated eased edge','BEVEL');mod.width=w;mod.segments=seg;bpy.ops.object.modifier_apply(modifier=mod.name)
def manhole():
 iron=texture_material('Dark weathered cast iron',(.085,.080,.072),.85,.45,.35);wear=texture_material('Raised iron grip wear',(.125,.12,.108),.73,.55,.22)
 tube('Outer support frame',(0,0,.04),.36,.307,.08,iron,axis='Z');tube('Internal cover seating ledge',(0,0,.040),.312,.285,.014,iron,axis='Z')
 cover=cyl('Separate cast cover plate',(0,0,.063),.302,.032,iron,N=128);bevel(cover,.0018)
 for y in [-.233,.233]:
  cut=box('Through lifting slot cutter',(0,y,.063),(.044,.018,.070),iron,.005)
  bpy.context.view_layer.objects.active=cover;mod=cover.modifiers.new('Through-slot for turn-key engagement','BOOLEAN');mod.operation='DIFFERENCE';mod.object=cut;bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(cut,do_unlink=True)
 tube('Cover raised perimeter rim',(0,0,.080),.298,.289,.003,wear,axis='Z')
 # Broken herringbone tread, no copied municipality emblem.
 for iy in range(-6,7):
  for ix in range(-6,7):
   x=ix*.041;y=iy*.041
   if x*x+y*y>.265**2 or (abs(x)<.05 and abs(y)>.19):continue
   ob=box('Integral cast anti-slip tread',(x,y,.081),(.031,.008,.004),wear,.002,3);ob.rotation_euler[2]=math.pi/4*(1 if (ix+iy)%2 else -1)
 for a in range(8):
  an=a*math.pi/4+math.pi/8;o=box('Underside cast radial reinforcement',(.155*math.cos(an),.155*math.sin(an),.039),(.25,.013,.016),iron,.002);o.rotation_euler[2]=an
 return ['https://hinodesuido.co.jp/cast_line/products/single-01_manhole.html','https://www.kaneso.co.jp/topnews/2022/img_121/catalog/19-1.pdf','https://www.kaneso.co.jp/onepoint/21_manhole/2018/P180831.htm'],'Generic 0.72 m outer frame, 0.604 m cover, 0.08 m overall depth; estimated scale, not a certified replica. Independent cover and frame, seating ledge, two genuine through-slots accepting turn keys, integral herringbone grip and clear underside reinforcing ribs. Flat bearing at Z 0.047 m, ribs stop at radius 0.2801 m inside 0.285 m ledge opening. Lift with both opposed keys; review geometry shows insertion, turn and parallel lift. Generic mechanism and dimensions, not a manufacturer replica; no lock, seal, flood restraint or road load-rating claim. No municipality logo.'
def curb():
 concrete=texture_material('Weathered fine aggregate concrete',(.43,.425,.40),.94,0,.34)
 # 600 mm long B-type tapered section, rounded road-facing shoulder.
 yz=[(-.1025,0),(.1025,0),(.090,.25),(-.060,.25)]
 # 30 mm quarter shoulder radius from upper plane into front battered face.
 for i in range(1,9):
  a=math.pi/2+i*math.pi/16;yz.append((-.060+.030*math.cos(a),.220+.030*math.sin(a)))
 v=[(x,y,z) for x in [-.30,.30] for y,z in yz];k=len(yz);f=[tuple(reversed(range(k))),tuple(k+i for i in range(k))]+[(i,(i+1)%k,(i+1)%k+k,i+k) for i in range(k)]
 ob=mesh('Precast tapered curb with rounded shoulder',v,f,concrete);bevel(ob,.0012,2);unwrap(ob)
 return ['https://kawamoto-con.jp/product/p0012/','https://www.toyo-con.co.jp/toyodb/catalogue.php?f=95be6a8eb9de4551277e69fd1f5a0b90'],'Generic Japanese B-type 600 mm length, 205 mm base width, 180 mm nominal top width, 250 mm height with 30 mm road-side rounded shoulder. Reference-informed nominal scale; bevels and seeded fine aggregate are original interpretation. Full depth block; rounded -Y face points toward road. Mount-up-like context embeds 140 mm and leaves 110 mm exposed, artistic assumptions. Curb bedding, foundation and drainage fall/outlet are omitted: context is a visual placement aid, not a functionally complete installation demonstration.'
def bollard():
 paint=texture_material('Muted warm ivory baked enamel',(.56,.55,.48),.48,.08,.07);zinc=texture_material('Dull zinc anchor hardware',(.24,.25,.245),.6,.65,.15);dark=mat('Painted circumferential weld bead',(.44,.43,.37),.08,.61)
 plate=box('Ten millimetre surface mounting flange',(0,0,.005),(.18,.18,.010),paint,.006,4)
 cyl('Steel tube 76.3 mm diameter',(0,0,.423),.03815,.826,paint,N=96)
 tube('Base circumferential weld',(0,0,.013),.0415,.037,.006,dark,axis='Z')
 cap=cyl('Pressed steel top cap',(0,0,.839),.0394,.022,paint,N=96);bevel(cap,.007,5)
 tube('Cap rolled seam',(0,0,.830),.040,.038,.003,paint,axis='Z')
 for i,(x,y) in enumerate([(x,y) for x in [-.064,.064] for y in [-.064,.064]],1):
  cut=cyl('Temporary through flange hole',(x,y,.005),.0065,.04,zinc,N=48)
  bpy.context.view_layer.objects.active=plate;mod=plate.modifiers.new('Drilled 13 mm through hole','BOOLEAN');mod.operation='DIFFERENCE';mod.object=cut;bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(cut,do_unlink=True)
  tube('Bored anchor washer '+str(i),(x,y,.0115),.0115,.0055,.003,zinc,axis='Z')
  nut=cyl('Bored hexagonal anchor nut '+str(i),(x,y,.017),.009815,.008,zinc,N=6)
  cut=cyl('Temporary nut bore',(x,y,.017),.005,.03,zinc,N=48)
  bpy.context.view_layer.objects.active=nut;mod=nut.modifiers.new('M10-like nut bore','BOOLEAN');mod.operation='DIFFERENCE';mod.object=cut;bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(cut,do_unlink=True)
  cyl('Continuous anchor shank '+str(i),(x,y,-.037),.005,.126,zinc,N=48)

 return ['https://www.sunpole.co.jp/product-detail/?no=397','https://www.sunpole.co.jp/product-detail/?no=407'],'Generic surface-mounted steel roadside bollard, 76.3 mm shaft diameter, 850 mm visible height above mounting plane; total mesh height 950 mm including 100 mm below-plane anchor continuations. Scale informed by Sunpole FPA-8 family; generic 180x180x10 mm flange and 128 mm square anchor pitch are explicitly NOT the manufacturer drawing flange. Four 13 mm bores, continuous M10-like shanks, bored washers and nuts form coherent attachment. Threads are simplified contact envelopes. The 100 mm buried anchor depth and concrete support demonstration are inferred visual assumptions, not an anchor specification. Internal tube wall and drain detail are omitted; no functional drainage claim. Weld bead and pressed cap remain estimated original construction. Muted ivory baked enamel; no logos, hooks or crash-rating claim.'
def build(slug,fn):
 if os.environ.get('ONLY_ASSETS') and slug not in os.environ['ONLY_ASSETS'].split(','):return
 reset();refs,notes=fn();sc=bpy.context.scene;obs=[o for o in sc.objects if o.type=='MESH']
 for ob in obs:
  if not ob.data.uv_layers:unwrap(ob)
 col=bpy.data.collections.new('ASSET | '+slug);sc.collection.children.link(col);root=bpy.data.objects.new(slug,None);col.objects.link(root)
 for ob in obs:
  for co in list(ob.users_collection):co.objects.unlink(ob)
  col.objects.link(ob);ob.parent=root
 st=stats(obs);folder=A/slug;folder.mkdir(parents=True,exist_ok=True)
 bpy.ops.object.select_all(action='DESELECT');root.select_set(True)
 for ob in obs:ob.select_set(True)
 bpy.ops.export_scene.gltf(filepath=str(folder/(slug+'.glb')),export_format='GLB',use_selection=True,export_extras=True)
 studio=bpy.data.collections.new('PREVIEW STUDIO');sc.collection.children.link(studio)
 def move(ob):
  for co in list(ob.users_collection):co.objects.unlink(ob)
  studio.objects.link(ob)
 lo=Vector(st['bounds_min']);hi=Vector(st['bounds_max']);center=(lo+hi)/2;sz=max(hi-lo)
 bpy.ops.mesh.primitive_plane_add(size=200,location=(0,0,-.003));ob=bpy.context.object;ob.data.materials.append(mat('Neutral studio ground',(.27,.29,.30),0,.9));move(ob)
 for p,power in [((-3,-4,6),450),((4,-1,4),180),((1,4,5),350)]:
  bpy.ops.object.light_add(type='AREA',location=center+Vector(p)*sz);ob=bpy.context.object;ob.data.energy=power*sz*sz;ob.data.shape='DISK';ob.data.size=sz*3;ob.rotation_euler=(center-ob.location).to_track_quat('-Z','Y').to_euler();move(ob)
 bpy.ops.object.camera_add();cam=bpy.context.object;move(cam);sc.camera=cam;cam.data.type='ORTHO'
 sc.world.use_nodes=True;sc.world.node_tree.nodes['Background'].inputs[0].default_value=(.65,.69,.75,1);sc.world.node_tree.nodes['Background'].inputs[1].default_value=.3
 sc.render.engine='CYCLES';sc.cycles.samples=40;sc.cycles.use_denoising=False;sc.render.threads_mode='FIXED';sc.render.threads=2;sc.render.resolution_x=1000;sc.render.resolution_y=850;sc.render.resolution_percentage=100;sc.render.image_settings.file_format='JPEG';sc.render.image_settings.quality=92;sc.view_settings.view_transform='AgX'
 detail=Vector((0,0,.064 if fn==manhole else .18 if fn==curb else .05));ds=.36 if fn==manhole else .36 if fn==curb else .25
 for name,off,target,scale in [('front_three_quarter',(1.7,-2.6,2.4),center,sz*1.35),('rear',(-1.7,2.6,2.2),center,sz*1.35),('side',(3,0,1.1),center,sz*1.35),('close_up',(.7,-1.2,1.2),detail,ds)]:
  cam.location=target+Vector(off)*sz;cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=scale;sc.render.filepath=str(folder/(name+'.jpg'));bpy.ops.render.render(write_still=True)
 shutil.copyfile(folder/'front_three_quarter.jpg',folder/'preview.jpg');shutil.copyfile(folder/'rear.jpg',folder/'back.jpg')
 cam.location=center+Vector((1.7,-2.6,2.4))*sz;cam.rotation_euler=(center-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=sz*1.35
 studio.hide_viewport=True;bpy.ops.wm.save_as_mainfile(filepath=str(folder/(slug+'.blend')),compress=True)
 meta={'id':slug,'category':'street','units':'meters','front_blend':'-Y','up_blend':'Z','up_glb':'Y','origin':'flange underside mounting plane; anchors extend 0.100 m below' if slug=='steel_roadside_bollard' else 'bottom center','reference_urls':refs,'notes':notes,'blender_version':bpy.app.version_string,'textures':'Original seeded raster base color, normal, and roughness; packed in blend and embedded in GLB. No external inputs.','review_status':'pending independent review',**st,'files_bytes':{p.name:p.stat().st_size for p in folder.iterdir() if p.is_file()}}
 (folder/'metadata.json').write_text(json.dumps(meta,indent=2)+'\n');print('READY',slug,st,flush=True)
if __name__=='__main__':
 for slug,fn in zip(IDS,[manhole,curb,bollard]):build(slug,fn)
