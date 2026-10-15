"""Original street props, Blender 4.3+, reproducible without external dependencies.
Run blender -b --threads 4 --python scripts/build_assets.py
"""
import bpy, math, json, os
from pathlib import Path
from mathutils import Vector
import numpy as np
SUPPORT=Path(__file__).resolve().parents[1]
ROOT=Path(os.environ.get('ASSET_OUTPUT_ROOT',str(SUPPORT)))
def mat(name,c,rough=.6,metal=0):
 m=bpy.data.materials.new(name);m.diffuse_color=(*c,1);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*c,1);p.inputs['Roughness'].default_value=rough;p.inputs['Metallic'].default_value=metal
 if 'galvanized' in name.lower() or 'ballast' in name.lower():
  n=128;rng=np.random.default_rng(13);yy,xx=np.mgrid[0:n,0:n];noise=rng.normal(0,.009,(n,n))+.012*np.sin(xx*.31)*np.sin(yy*.43)
  rgb=np.array([min(1,1.055*(v**(1/2.4))-.055) for v in c]);pixels=np.empty((n,n,4),dtype=np.float32);pixels[:,:,:3]=np.clip(rgb+noise[:,:,None],0,1);pixels[:,:,3]=1
  im=bpy.data.images.new(name+' original finish',width=n,height=n);im.pixels.foreach_set(pixels.ravel());im.filepath_raw=str(SUPPORT/(name.replace(' ','_')+'.png'));im.file_format='PNG';im.save();im.pack();tex=m.node_tree.nodes.new('ShaderNodeTexImage');tex.image=im;m.node_tree.links.new(tex.outputs['Color'],p.inputs['Base Color'])
 return m

def assign(o,n,m):o.name=n;o.data.materials.append(m);return o

def cube(n,p,d,m,b=.005):
 bpy.ops.mesh.primitive_cube_add(size=1,location=p);o=bpy.context.object;o.dimensions=d;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);assign(o,n,m)
 if b:
  mod=o.modifiers.new('Manufactured edge radius','BEVEL');mod.width=b;mod.segments=8 if b>=.02 else 3;bpy.ops.object.modifier_apply(modifier=mod.name)
  for face in o.data.polygons:face.use_smooth=True
  mod=o.modifiers.new('Weighted corner normals','WEIGHTED_NORMAL');bpy.ops.object.modifier_apply(modifier=mod.name)
 return o

def cyl(n,p,r,h,m,rot=None,vertices=64):
 bpy.ops.mesh.primitive_cylinder_add(vertices=vertices,radius=r,depth=h,location=p);o=assign(bpy.context.object,n,m)
 if rot:o.rotation_euler=rot
 for f in o.data.polygons:f.use_smooth=len(f.vertices)==4
 return o

def tube(n,a,b,r,m):
 a,b=Vector(a),Vector(b);o=cyl(n,(a+b)/2,r,(b-a).length,m);o.rotation_euler=(b-a).to_track_quat('Z','Y').to_euler();return o

def beam(n,a,b,d,m):
 a,b=Vector(a),Vector(b);o=cube(n,(a+b)/2,(d,d,(b-a).length),m,.004);o.rotation_euler=(b-a).to_track_quat('Z','Y').to_euler();return o

def lathe(n,rings,mats,bands=None,N=96,closed=False):
 v=[(r*math.cos(i*math.tau/N),r*math.sin(i*math.tau/N),z) for r,z in rings for i in range(N)];faces=[]
 for k in range(len(rings) if closed else len(rings)-1):
  j=(k+1)%len(rings)
  for i in range(N):faces.append((k*N+i,k*N+(i+1)%N,j*N+(i+1)%N,j*N+i))
 me=bpy.data.meshes.new(n);me.from_pydata(v,[],faces);me.update();o=bpy.data.objects.new(n,me);bpy.context.collection.objects.link(o)
 for m in mats:me.materials.append(m)
 for f in me.polygons:f.use_smooth=True;f.material_index=bands.get(f.index//N,0) if bands else 0
 return o

def wood():
 global ENDGRAIN
 m=mat('Oiled outdoor timber',(.35,.17,.065),.57)
 rng=np.random.default_rng(43);w,h=1024,256;y,x=np.mgrid[0:h,0:w];xf=x/w
 # Irregular tapered fibres with independently varying spacing, curvature and length.
 grain=np.zeros((h,w),dtype=np.float32)
 for i in range(145):
  cy=rng.uniform(-15,h+15);amp=rng.uniform(.4,3.6);phase=rng.uniform(0,math.tau)
  line=cy+amp*np.sin(xf*rng.uniform(1,6)+phase)+.5*np.sin(xf*rng.uniform(9,25)+phase*2)
  start=rng.uniform(-.7,.75);span=rng.uniform(.15,1.6);window=np.clip((xf-start)*20,0,1)*np.clip((start+span-xf)*20,0,1)
  grain-=rng.uniform(.009,.055)*np.exp(-((y-line)/rng.uniform(.22,.85))**2)*window
 # Gentle broad, nonperiodic variation beneath the fine fibres.
 broad=np.interp(np.arange(h),np.linspace(0,h,19),rng.normal(0,.008,19))[:,None]
 grain+=broad+rng.normal(0,.0025,(h,w))
 def image_material(material,name,pixels,filename):
  im=bpy.data.images.new(name,width=pixels.shape[1],height=pixels.shape[0]);im.pixels.foreach_set(pixels.astype(np.float32).ravel());im.filepath_raw=str(SUPPORT/filename);im.file_format='PNG';im.save();im.pack();tex=material.node_tree.nodes.new('ShaderNodeTexImage');tex.image=im;material.node_tree.links.new(tex.outputs['Color'],material.node_tree.nodes.get('Principled BSDF').inputs['Base Color'])
 rgb=np.empty((h,w,4),dtype=np.float32);rgb[:,:,:3]=np.array([.48,.30,.16])+grain[:,:,None]*np.array([1,.72,.45]);rgb[:,:,3]=1;image_material(m,'Original irregular timber fibres 1024x256',rgb,'timber_grain.png')
 ENDGRAIN=mat('Oiled timber end grain',(.30,.14,.055),.64)
 ey,ex=np.mgrid[0:128,0:128]/128;radius=np.sqrt((ex+1.6)**2+(ey-.2)**2);rings=.014*np.sin(radius*95+2*np.sin(ey*3))+.005*rng.normal(size=(128,128));pixels=np.empty((128,128,4),dtype=np.float32);pixels[:,:,:3]=np.array([.43,.265,.135])+rings[:,:,None]*np.array([1,.7,.4]);pixels[:,:,3]=1;image_material(ENDGRAIN,'Original cut timber end grain 128',pixels,'timber_endgrain.png')
 return m

def wooduv(o):
 uv=o.data.uv_layers.active or o.data.uv_layers.new(name='Grain UV');o.data.materials.append(ENDGRAIN)
 dy=max(v.co.y for v in o.data.vertices)-min(v.co.y for v in o.data.vertices);dz=max(v.co.z for v in o.data.vertices)-min(v.co.z for v in o.data.vertices)
 for p in o.data.polygons:
  end=abs(p.normal.x)>.95
  if end:p.material_index=1
  for li in p.loop_indices:
   v=o.data.vertices[o.data.loops[li].vertex_index].co
   uv.data[li].uv=(v.y/dy+.5,v.z/dz+.5) if end else (v.x/1.8+.5,(v.y+v.z)*3+.5+sum(ord(c) for c in o.name)*.071)

def bench():
 timber=wood();steel=mat('Graphite powder coated steel',(.055,.058,.062),.68);zinc=mat('Dull galvanized fasteners',(.34,.35,.36),.74,.65);rubber=mat('Dark rubber foot pads',(.021,.022,.024),.92)
 for i in range(4):
  o=cube('Seat timber slat %02d'%i,(0,-.205+i*.12,.435),(1.8,.107,.038),timber,.006);wooduv(o)
 for i in range(3):
  z=.59+i*.105;y=.245+(z-.59)*.20;o=cube('Back timber slat %02d'%i,(0,y,z),(1.8,.035,.09),timber,.006);o.rotation_euler.x=math.radians(-11);wooduv(o)
 for x in [-.64,.64]:
  cube('Seat bearing rail',(x,-.025,.398),(.055,.47,.042),steel)
  for y in [-.20,.20]:
   beam('Splayed steel leg',(x,y*1.2,.023),(x,y,.40),.052,steel);cube('Foot plate',(x,y*1.2,.018),(.12,.12,.024),steel,.009);cube('Ground isolation pad',(x,y*1.2,.004),(.105,.105,.008),rubber,.005)
  beam('Backrest upright',(x,.18,.30),(x,.33,.86),.045,steel)
  for i in range(4):cyl('Seat flush fixing',(x,-.205+i*.12,.4555),.008,.003,zinc,vertices=24)
  for i in range(3):
   z=.59+i*.105;y=.245+(z-.59)*.20;cyl('Backrest fixing',(x,y-.020,z),.008,.003,zinc,(math.pi/2,0,0),24)
 cube('Lower transverse stiffener',(0,.217,.24),(1.32,.035,.055),steel)
 return (Vector((0,-.12,.48)),.7)

def streetlight():
 zinc=mat('Weathered galvanized steel',(.38,.39,.40),.82,.58);paint=mat('Light grey powder coated luminaire',(.64,.65,.66),.64);dark=mat('EPDM gasket',(.018,.019,.020),.9);bolt=mat('Dull zinc hardware',(.25,.26,.27),.75,.65);lens=mat('Frosted polycarbonate diffuser',(.77,.79,.80),.33)
 cube('Galvanized anchor foot',(0,0,.025),(.30,.30,.05),zinc,.018)
 for x in [-.103,.103]:
  for y in [-.103,.103]:cyl('Anchor nut',(x,y,.062),.014,.024,bolt,vertices=6);cyl('Anchor washer',(x,y,.052),.021,.004,bolt,vertices=32)
 bpy.ops.mesh.primitive_cone_add(vertices=64,radius1=.069,radius2=.045,depth=3.93,location=(0,0,2.015));o=assign(bpy.context.object,'Tapered galvanized mast',zinc)
 for p in o.data.polygons:p.use_smooth=len(p.vertices)==4
 cyl('Sealed mast cap',(0,0,3.991),.047,.022,zinc)
 cube('Service hatch gasket',(0,-.068,.58),(.072,.008,.26),dark,.012);cube('Service hatch cover',(0,-.075,.58),(.065,.007,.245),zinc,.01)
 for z in [.48,.68]:cyl('Hatch captive screw',(0,-.081,z),.005,.004,bolt,(math.pi/2,0,0),16)
 tube('Horizontal outreach arm',(0,0,3.85),(0,-.54,3.85),.033,zinc)
 for y in [-.06,-.13]:cube('Arm root bracket',(0,y,3.85),(.10,.035,.13),zinc)
 for x in [-.034,.034]:cyl('Arm bracket fastener',(x,-.152,3.85),.007,.008,bolt,(math.pi/2,0,0),24)
 cube('LED luminaire body',(0,-.68,3.86),(.28,.59,.105),paint,.045)
 cube('Lens perimeter seal',(0,-.71,3.803),(.228,.45,.009),dark,.035)
 cube('Recessed diffuser',(0,-.71,3.797),(.208,.428,.012),lens,.032)
 for x in [-.07,0,.07]:
  for y in [-.84,-.74,-.64]:cube('Diffuser optical cell',(x,y,3.788),(.048,.070,.008),lens,.013)
 for x in [-.09,.09]:
  for y in [-.91,-.49]:cyl('Luminaire cover screw',(x,y,3.798),.006,.006,bolt,vertices=20)
 for x in [-.08,-.04,0,.04,.08]:cube('Shallow heat sink rib',(x,-.65,3.918),(.012,.31,.014),paint,.004)
 return (Vector((0,-.51,3.83)),.82)

def cone():
 red=mat('Safety red flexible PVC',(.67,.035,.012),.43);white=mat('White reflective sleeve',(.82,.83,.82),.38);rubber=mat('Heavy rubber ballast base',(.028,.029,.031),.91)
 cube('Rounded square ballast base',(0,0,.025),(.38,.38,.05),rubber,.022)
 # Hollow tapered shell; sleeve bands are integrated, with no coincident overlays.
 zs=[.05,.065,.19,.29,.39,.49,.63,.675,.69,.70]
 rs=[.145,.148,.124,.104,.083,.063,.034,.024,.020,.018]
 rings=list(zip(rs,zs))+[(.013,.70),(.015,.68),(.027,.63),(.056,.49),(.076,.39),(.097,.29),(.117,.19),(.139,.065),(.136,.05)]
 lathe('Hollow cone with integrated white sleeves',rings,[red,white],{2:1,4:1},96,True)
 return (Vector((0,0,.60)),.25)

BUILDERS={'streetlight':streetlight,'park_bench':bench,'traffic_cone':cone}
REFS={'streetlight':['https://www.iwasaki.co.jp/lighting/road_tunnel/anticrime/'],'park_bench':['https://townscape.kotobuki.co.jp/product/bench/','https://townscape.kotobuki.co.jp/catalogs/images/KTB-42.pdf'],'traffic_cone':['https://www.sanko-kk.co.jp/products/safety/corn/']}
def build(slug,fun):
 bpy.ops.wm.read_factory_settings(use_empty=True);s=bpy.context.scene;s.unit_settings.system='METRIC';s.unit_settings.scale_length=1;detail,detail_size=fun();obs=list(s.objects)
 col=bpy.data.collections.new('ASSET | '+slug);s.collection.children.link(col);root=bpy.data.objects.new(slug,None);col.objects.link(root)
 for o in obs:
  for c in list(o.users_collection):c.objects.unlink(o)
  col.objects.link(o);o.parent=root;bpy.context.view_layer.objects.active=o;o.select_set(True);bpy.ops.object.transform_apply(location=False,rotation=True,scale=True);o.select_set(False)
 pts=[o.matrix_world@v.co for o in obs for v in o.data.vertices];lo=Vector([min(v[i] for v in pts) for i in range(3)]);hi=Vector([max(v[i] for v in pts) for i in range(3)]);center=(lo+hi)/2;size=max(hi-lo)
 for o in obs:o.data.calc_loop_triangles()
 folder=ROOT/'assets'/'street'/slug;folder.mkdir(parents=True,exist_ok=True)
 root['units']='meters';root['design']='Original generic Japanese street context; not engineering specification';root['origin']='ground at pole/base/bench center'
 bpy.ops.object.select_all(action='DESELECT')
 for o in col.objects:o.select_set(True)
 bpy.context.view_layer.objects.active=root;bpy.ops.export_scene.gltf(filepath=str(folder/(slug+'.glb')),export_format='GLB',use_selection=True,export_apply=True)
 # Neutral daylight studio, excluded from GLB.
 studio=bpy.data.collections.new('PREVIEW STUDIO');s.collection.children.link(studio)
 def move(o):
  for c in list(o.users_collection):c.objects.unlink(o)
  studio.objects.link(o)
 bpy.ops.mesh.primitive_plane_add(size=size*200,location=(0,0,-.002));o=assign(bpy.context.object,'Preview ground',mat('Neutral studio',(.42,.42,.42),.85));move(o)
 for offset,power in [((-3,-4,6),600),((4,-2,3),260),((1,4,5),450)]:
  bpy.ops.object.light_add(type='AREA',location=center+Vector(offset)*size);o=bpy.context.object;o.data.energy=power*size*size;o.data.shape='DISK';o.data.size=size*3;o.rotation_euler=(center-o.location).to_track_quat('-Z','Y').to_euler();move(o)
 s.world=bpy.data.worlds.new('Neutral environment');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs[0].default_value=(.8,.8,.8,1);s.world.node_tree.nodes['Background'].inputs[1].default_value=.3
 bpy.ops.object.camera_add();cam=bpy.context.object;move(cam);s.camera=cam;cam.data.type='ORTHO'
 s.render.engine='CYCLES';s.cycles.samples=64;s.cycles.use_denoising=False;s.render.resolution_x=1000;s.render.resolution_y=1000;s.render.resolution_percentage=100;s.render.image_settings.file_format='JPEG';s.render.image_settings.quality=93;s.view_settings.view_transform='AgX'
 for name,offset,target,scale in [('preview',(1.3,-2,1.05),center,size*1.32),('back',(-1.3,2,1.05),center,size*1.32),('detail',(1,-1.8,-.8 if slug=='streetlight' else .8),detail,detail_size)]:
  cam.location=target+Vector(offset)*size;cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=scale;s.render.filepath=str(folder/(name+'.jpg'));bpy.ops.render.render(write_still=True)
 cam.location=center+Vector((1.3,-2,1.05))*size;cam.rotation_euler=(center-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=size*1.32;studio.hide_viewport=True;bpy.ops.wm.save_as_mainfile(filepath=str(folder/(slug+'.blend')),compress=True)
 meta={'id':slug,'units':'meters','dimensions_m':list(hi-lo),'bounds_min':list(lo),'bounds_max':list(hi),'triangles':sum(len(o.data.loop_triangles) for o in obs),'origin':{'streetlight':'Ground plane at mast base center','park_bench':'Ground plane at bench footprint center','traffic_cone':'Ground plane at square base center'}[slug],'front_blend':'-Y','up_axis_blend':'Z','up_axis_glb':'Y','reference_urls':REFS[slug],'references_checked':'2026-10-15','design':'Original generic interpretation, estimated dimensions; not a replica or fabrication specification.','material_notes':{'streetlight':'Neutral lighting; original packed 128px galvanized finish, restrained metallic roughness, powder coat, EPDM seal and frosted polycarbonate.','park_bench':'Original packed 1024x256 irregular timber fibers and separate 128px end grain, graphite powder-coated steel, dull galvanized fixing heads and rubber isolation pads.','traffic_cone':'Red flexible PVC, white reflective-sheet PBR approximation, packed original 128px dark rubber ballast finish.'}[slug],'limitations':{'streetlight':'Unlit luminaire. No buried foundation, wiring or engineering internals. Estimated dimensions; no compliance claims.','park_bench':'Estimated dimensions; no structural certification. Underside fastening internals omitted. Wood grain is a compact original approximation.','traffic_cone':'Bands use standard PBR approximation, not retroreflection. Solid ballast base makes this prop non-stackable. Not a certified traffic control product. Estimated dimensions.'}[slug],'files':{p.name:p.stat().st_size for p in folder.iterdir() if p.is_file()}}
 (folder/'metadata.json').write_text(json.dumps(meta,indent=2));print('READY',slug,flush=True)
if __name__=='__main__':
 for slug,fn in BUILDERS.items():
  if not os.environ.get('ONLY_ASSETS') or slug in os.environ['ONLY_ASSETS'].split(','):build(slug,fn)
