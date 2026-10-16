import bpy, math, os, json, shutil, hashlib
import numpy as np
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1]; OUT=Path(os.environ.get('ASSET_OUTPUT_ROOT',str(R))); A=OUT/'assets';A.mkdir(parents=True,exist_ok=True)
bpy.context.preferences.filepaths.save_version=0

def clear():
 for o in list(bpy.data.objects):bpy.data.objects.remove(o,do_unlink=True)
def mat(n,c,metal=0,rough=.5):
 m=bpy.data.materials.new(n);m.diffuse_color=(*c,1);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*c,1);p.inputs['Metallic'].default_value=metal;p.inputs['Roughness'].default_value=rough;return m
def mesh(n,v,f,m,smooth=True):
 d=bpy.data.meshes.new(n);d.from_pydata(v,[],f);d.update();o=bpy.data.objects.new(n,d);bpy.context.collection.objects.link(o);o.data.materials.append(m)
 for p in d.polygons:p.use_smooth=smooth
 return o
def lathe(n,profile,m,N=96):
 v=[];f=[]
 for r,z in profile:
  for i in range(N):a=i*2*math.pi/N;v.append((r*math.cos(a),r*math.sin(a),z))
 for k in range(len(profile)-1):
  for i in range(N):j=(i+1)%N;f.append((k*N+i,k*N+j,(k+1)*N+j,(k+1)*N+i))
 if profile[0][0]<.003:f.append(tuple(reversed(range(N))))
 if profile[-1][0]<.003:f.append(tuple((len(profile)-1)*N+i for i in range(N)))
 return mesh(n,v,f,m)
def box(n,p,s,m,b=.002,segments=4):
 bpy.ops.mesh.primitive_cube_add(size=1,location=p);o=bpy.context.object;o.name=n;o.dimensions=s;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(m)
 if b:
  q=o.modifiers.new('Soft sanded manufactured edges','BEVEL');q.width=b;q.segments=segments;bpy.context.view_layer.objects.active=o;bpy.ops.object.modifier_apply(modifier=q.name)
 return o
def path_tube(n,pts,rads,m,inner=None,N=32):
 v=[];f=[];L=len(pts)
 for k,pt in enumerate(pts):
  tangent=Vector(pts[min(k+1,L-1)])-Vector(pts[max(0,k-1)]);tangent.normalize();ref=Vector((1,0,0)) if max(p[0] for p in pts)-min(p[0] for p in pts)<1e-8 else Vector((0,1,0));u=tangent.cross(ref)
  if u.length<.1:u=tangent.cross(Vector((1,0,0)))
  u.normalize();w=tangent.cross(u)
  for r in ([rads[k],inner[k]] if inner else [rads[k]]):
   for i in range(N):v.append(tuple(Vector(pt)+r*(math.cos(i*2*math.pi/N)*u+math.sin(i*2*math.pi/N)*w)))
 rings=2 if inner else 1
 for k in range(L-1):
  for side in range(rings):
   for i in range(N):a=k*rings*N+side*N+i;b=k*rings*N+side*N+(i+1)%N;c=b+rings*N;d=a+rings*N;f.append((a,b,c,d) if side==0 else (d,c,b,a))
 if inner:
  for k in [0,L-1]:
   for i in range(N):a=k*2*N+i;b=k*2*N+(i+1)%N;f.append((a,a+N,b+N,b) if k==0 else (b,b+N,a+N,a))
 else:
  f += [tuple(reversed(range(N))),tuple((L-1)*N+i for i in range(N))]
 return mesh(n,v,f,m)
def stats(obs):
 verts=[o.matrix_world@v.co for o in obs for v in o.data.vertices];tri=0;bad=0
 for o in obs:
  o.data.calc_loop_triangles();tri+=len(o.data.loop_triangles)
  bad+=sum(t.area<1e-14 for t in o.data.loop_triangles)
 lo=[min(v[i] for v in verts) for i in range(3)];hi=[max(v[i] for v in verts) for i in range(3)]
 return dict(triangles=tri,zero_area_triangles=bad,bounds_min=lo,bounds_max=hi,dimensions_m=[hi[i]-lo[i] for i in range(3)],mesh_objects=len(obs))
def studio(target,size):
 sc=bpy.context.scene;sc.render.engine='CYCLES';sc.cycles.samples=28;sc.cycles.use_denoising=False;sc.render.threads_mode='FIXED';sc.render.threads=2;sc.render.resolution_x=800;sc.render.resolution_y=800;sc.render.resolution_percentage=100;sc.render.image_settings.file_format='JPEG';sc.render.image_settings.quality=94;sc.view_settings.view_transform='AgX';sc.world.color=(.25,.25,.25)
 floor=mat('Neutral studio plaster',(.34,.35,.34),0,.9);box('Studio ground',(0,0,-.012),(200,200,.02),floor,.0)
 for pos,power,sz in [((1,-1,2),120,1.5),((-1,-.3,1),80,1),((.4,1,1.5),150,1)]:
  bpy.ops.object.light_add(type='AREA',location=Vector(target)+Vector(pos)*size*3);o=bpy.context.object;o.data.energy=power*size*size*8;o.data.shape='DISK';o.data.size=sz*size*3;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()
 bpy.ops.object.camera_add();cam=bpy.context.object;cam.data.type='ORTHO';cam.data.ortho_scale=size*1.5;sc.camera=cam;return cam

def render_asset(slug):
 f=A/slug;clear();bpy.ops.import_scene.gltf(filepath=str(f/(slug+'.glb')));obs=[o for o in bpy.context.scene.objects if o.type=='MESH'];st=stats(obs);target=(Vector(st['bounds_min'])+Vector(st['bounds_max']))/2;size=max(st['dimensions_m']);cam=studio(target,size)
 if slug=='wall_clock':
  bpy.data.objects['Front glass disc'].visible_shadow=False;bpy.context.scene.cycles.samples=64
 for name,off in [('front_three_quarter',(2,-3,2)),('side',(3,0,1.1)),('rear',(-2,3,1.7)),('close_up',(2,-2,3)),('underside',(1,-2,-3))]:
  bpy.data.objects['Studio ground'].hide_render=name=='underside';cam.location=target+Vector(off)*size;cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=size*(1.45 if name!='close_up' else 1.12);bpy.context.scene.render.filepath=str(f/(name+'.jpg'));bpy.ops.render.render(write_still=True)
 shutil.copyfile(f/'front_three_quarter.jpg',f/'preview.jpg');shutil.copyfile(f/'rear.jpg',f/'back.jpg')
def fiber(n,c,seed):
 m=mat(n,c,0,.83);N=512;rng=np.random.default_rng(seed);noise=rng.normal(0,.014,(N,N));fine=rng.random((N,N));noise+=np.where(fine>.98,-.055,0)
 arr=np.ones((N,N,4),np.float32)
 for k,col in enumerate(c):arr[:,:,k]=np.clip(col+noise,0,1)
 im=bpy.data.images.new(n+' original fiber albedo',width=N,height=N);im.pixels.foreach_set(arr.ravel());im.pack();nd=m.node_tree.nodes.new('ShaderNodeTexImage');nd.image=im;m.node_tree.links.new(nd.outputs['Color'],m.node_tree.nodes.get('Principled BSDF').inputs['Base Color']);return m

def cylinder(n,r,depth,loc,m,axis=(0,0,1),N=64):
 bpy.ops.mesh.primitive_cylinder_add(vertices=N,radius=r,depth=depth,location=loc);o=bpy.context.object;o.name=n;o.rotation_euler=Vector(axis).to_track_quat('Z','Y').to_euler();o.data.materials.append(m)
 for p in o.data.polygons:p.use_smooth=len(p.vertices)==4
 return o

def wood():
 m=mat('Original warm ash grain',(.53,.34,.17),0,.48);N=512;y,x=np.mgrid[0:N,0:N]/N;rng=np.random.default_rng(5101)
 phase=x*52+1.9*np.sin(y*5)+.35*np.sin(y*23+x*6);g=.022*np.sin(phase*6.28)+.009*np.sin(phase*19.2)+rng.normal(0,.004,(N,N))
 arr=np.ones((N,N,4),np.float32)
 for k,c in enumerate([.58,.39,.21]):arr[:,:,k]=np.clip(c+g,0,1)
 im=bpy.data.images.new('Original ash grain 512',width=N,height=N);im.pixels.foreach_set(arr.ravel());im.pack();nd=m.node_tree.nodes.new('ShaderNodeTexImage');nd.image=im;m.node_tree.links.new(nd.outputs['Color'],m.node_tree.nodes.get('Principled BSDF').inputs['Base Color']);return m

def apply_uv(o,axes=(0,2)):
 uv=o.data.uv_layers.new(name='Wood grain UV')
 for p in o.data.polygons:
  for li in p.loop_indices:
   v=o.data.vertices[o.data.loops[li].vertex_index].co;uv.data[li].uv=(v[axes[0]]*3+.5,v[axes[1]]*2+.5)

def stool():
 w=wood();felt=mat('Charcoal felt foot pads',(.05,.045,.039),0,.96);steel=mat('Recessed steel screw heads',(.25,.26,.27),1,.4)
 lathe('Solid round seat',[(.001,.422),(.144,.422),(.148,.424),(.15,.429),(.15,.442),(.148,.448),(.144,.45),(.001,.45)],w,128)
 # Four square-section splayed legs; horizontal ring cuts keep feet coplanar.
 for sx in [-1,1]:
  for sy in [-1,1]:
   v=[]
   for z,c,r in [(.002,.111,.013),(.41,.087,.017)]:
    for dx,dy in [(-1,-1),(1,-1),(1,1),(-1,1)]:v.append((sx*c+dx*r,sy*c+dy*r,z))
   o=mesh('Square splayed leg %s %s'%(sx,sy),v,[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],w,False)
   bpy.context.view_layer.objects.active=o;q=o.modifiers.new('Soft leg arris','BEVEL');q.width=.0017;q.segments=3;bpy.ops.object.modifier_apply(modifier=q.name)
   box('Flat felt sole',(sx*.111,sy*.111,.001),(.025,.025,.002),felt,.0007)
 # Opposite side frames are fixed, upper rails contact underside seat cleats.
 for x in [-.087,.087]:
  box('Side frame upper rail',(x,0,.389),(.025,.176,.042),w,.002)
  box('Seat underside mounting cleat',(x,0,.416),(.036,.176,.012),w,.0015)
  for y in [-.056,.056]:
   cylinder('Seat cleat recessed screw',.0033,.0015,(x,y,.410),steel)
 for y in [-.087,.087]:box('Cross upper apron',(0,y,.394),(.174,.024,.032),w,.0018)
 for x in [-1,1]:
  z=.177;c=.111+(.087-.111)*(z-.002)/.408
  path_tube('Side frame round stretcher',[(x*c,-c,z),(x*c,c,z)],[.010,.010],w,N=40)
 for y in [-1,1]:
  z=.143;c=.111+(.087-.111)*(z-.002)/.408
  path_tube('Cross round stretcher',[(-c,y*c,z),(c,y*c,z)],[.009,.009],w,N=40)
 for o in bpy.context.scene.objects:
  if o.type=='MESH' and o.data.materials[0]==w:apply_uv(o,(0,1) if 'seat' in o.name.lower() else (0,2))

def cut_boolean(o,cut):
 bpy.context.view_layer.objects.active=o;q=o.modifiers.new('Real opening','BOOLEAN');q.operation='DIFFERENCE';q.object=cut;bpy.ops.object.modifier_apply(modifier=q.name);bpy.data.objects.remove(cut,do_unlink=True)

def clock():
 shell=mat('Satin charcoal clock rim',(.045,.052,.055),0,.32);back=mat('Textured rear ABS',(.027,.03,.032),0,.68);face=mat('Warm white dial',(.82,.805,.75),0,.74);ink=mat('Printed charcoal indices',(.014,.018,.02),0,.63);red=mat('Muted red seconds hand',(.42,.025,.018),0,.4);metal=mat('Clock screw steel',(.5,.52,.54),1,.3)
 # Build face-up in XY, depth Z; transform as a unit to front -Y at end.
 lathe('Clock circular molded frame',[(.136,0),(.148,0),(.15,.003),(.15,.039),(.147,.043),(.133,.043),(.131,.041),(.131,.030),(.134,.028),(.136,0)],shell,128)
 cylinder('Dial plate',.135,.002,(0,0,.021),face,N=128)
 rear=cylinder('Recessed back cover',.143,.002,(0,0,.005),back,N=128)
 # Keyhole is a real cut through upper bridge, cavity behind it remains clear.
 mount=box('Hanging bridge with keyhole',(0,.105,.002),(.036,.048,.004),back,.003)
 cut_boolean(mount,cylinder('Screw head entry cutter',.006,.02,(0,.096,.002),back,N=48))
 cut_boolean(mount,box('Screw neck channel cutter',(0,.104,.002),(.006,.017,.02),back,.0015))
 cut_boolean(rear,box('Hanging cavity behind bridge',(0,.102,.005),(.028,.039,.018),back,.004))
 # Recessed movement enclosure with externally accessible AA cradle.
 box('Quartz movement casing',(0,-.003,.006),(.056,.058,.012),back,.003)
 box('Battery cradle back',(0,-.038,.009),(.058,.020,.003),back,.001)
 for x in [-.028,.028]:box('Battery terminal cradle',(x,-.038,.002),(.003,.020,.015),back,.001)
 cell=cylinder('Unbranded AA battery',.0072,.049,(0,-.038,.0015),metal,(1,0,0),48)
 cylinder('Time setting wheel',.007,.004,(.016,.010,-.002),back,N=40)
 for a in range(0,360,60):
  t=math.radians(a);cylinder('Back cover fastening screw',.0022,.001,(.14*math.cos(t),.14*math.sin(t),.0035),metal,N=24)
 for i in range(60):
  a=i*math.tau/60;major=i%5==0;l=.013 if major else .0055;r=.118-l/2
  o=box('Hour index' if major else 'Minute index',(math.sin(a)*r,math.cos(a)*r,.0222),(.0036 if major else .0011,l,.0003),ink,.00005,2);o.rotation_euler.z=-a
 for name,length,width,z,angle,m in [('Hour hand',.075,.006,.025,-55,ink),('Minute hand',.103,.004,.028,60,ink),('Seconds hand',.114,.0014,.031,190,red)]:
  # Tapered pointer extends behind shared axis for a short counterweight.
  pts=[(-width/2,-.016),(width/2,-.016),(width/2,length*.72),(0,length),(-width/2,length*.72)]
  v=[(x,y,zz) for zz in [z-.0005,z+.0005] for x,y in pts];fs=[tuple(reversed(range(5))),tuple(range(5,10))]+[(i,(i+1)%5,(i+1)%5+5,i+5) for i in range(5)]
  o=mesh(name,v,fs,m,False);o.rotation_euler.z=math.radians(-angle)
 cylinder('Coaxial hand spindle',.002,.013,(0,0,.027),metal,N=40);cylinder('Hand retaining cap',.004,.002,(0,0,.033),shell,N=48)
 glass=mat('Clear protective glass',(.94,.97,.99),0,.06);p=glass.node_tree.nodes.get('Principled BSDF');p.inputs['Transmission Weight'].default_value=1;p.inputs['IOR'].default_value=1.45
 cylinder('Front glass disc',.133,.0018,(0,0,.037),glass,N=128)
 # Rear contact bosses set the wall plane behind battery and setting wheel.
 for x,y in [(-.08,-.09),(.08,-.09),(0,.129)]:cylinder('Rear wall contact foot',.006,.006,(x,y,-.003),back,N=32)
 from mathutils import Matrix
 rot=Matrix.Rotation(math.pi/2,4,'X')
 for o in list(bpy.context.scene.objects):o.matrix_world=rot@o.matrix_world;o.location.z+=.15
def bucket():
 plastic=mat('Warm white PE EVA bucket',(.72,.735,.71),0,.37);steel=mat('Stainless steel bail',(.58,.62,.65),1,.25);grip=mat('Gray polypropylene grip',(.22,.25,.26),0,.37)
 # Continuous watertight section from bottom underside through rim into interior floor.
 profile=[(.001,.004),(.086,.004),(.090,0),(.093,0),(.094,.005),(.094,.010),(.136,.208),(.14,.214),(.14,.217),(.136,.217),(.133,.211),(.091,.014),(.088,.010),(.001,.010)]
 body=lathe('Continuous bucket wall rim and closed bottom',profile,plastic,160)
 # Integral pointed pour lip smoothly deforms upper front rings only.
 for v in body.data.vertices:
  if v.co.z>.14:
   a=math.atan2(v.co.y,v.co.x);d=abs((a+math.pi/2+math.pi)%(math.tau)-math.pi);factor=max(0,1-d/.25)**1.2*max(0,(v.co.z-.14)/.077)
   v.co.y-=.021*factor
 for sx in [-1,1]:
  ear=box('Raised integral pierced bail ear '+str(sx),(sx*.137,0,.224),(.006,.025,.027),plastic,.006)
  cut_boolean(ear,cylinder('Bail ear through hole cutter',.0037,.022,(sx*.137,0,.229),plastic,(1,0,0),48))
 # Bail outer arch uses an ellipse above rim, pivot axis X at z=.229.
 pts=[]
 # left hook: open tip rises on inner side, low bend threads through ear.
 pts.extend([(-.129,0,.249),(-.130,0,.237),(-.132,0,.230),(-.137,0,.228),(-.145,0,.229),(-.149,0,.234)])
 for i in range(1,80):
  a=math.pi-i*math.pi/80;pts.append((.15*math.cos(a),0,.229+.165*math.sin(a)))
 pts.extend([(.149,0,.234),(.145,0,.229),(.137,0,.228),(.132,0,.230),(.130,0,.237),(.129,0,.249)])
 o=path_tube('Swinging hooked steel bail',pts,[.0018]*len(pts),steel,N=24);o['pivot_axis']='X';o['pivot_z']=.229
 # Center grip envelops the near-horizontal crown; original small ridges.
 gp=[(.001,-.042),(.009,-.042),(.011,-.039),(.009,-.034),(.0085,-.030)]
 for x in np.linspace(-.030,.030,25):gp.append((.0085+.0008*(.5+.5*math.cos(x*math.pi/.008)),float(x)))
 gp.extend([(.009,.034),(.011,.039),(.009,.042),(.001,.042)])
 o=lathe('Swinging molded hand grip',gp,grip,48);o.rotation_euler.y=math.pi/2;o.location.z=.391

def repair_normals():
 for o in list(bpy.context.scene.objects):
  if o.type!='MESH':continue
  bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o;bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.mesh.normals_make_consistent(inside=False);bpy.ops.object.mode_set(mode='OBJECT')
IDS=['round_wooden_stool','plastic_bail_bucket','wall_clock']
TITLES=['スツール','バケツ','掛け時計']
def main():
 for slug,title,fn in zip(IDS,TITLES,[stool,bucket,clock]):
  if os.environ.get('ONLY_ASSETS') and slug not in os.environ['ONLY_ASSETS'].split(','):continue
  clear();fn();repair_normals();bpy.context.view_layer.update();obs=[o for o in bpy.context.scene.objects if o.type=='MESH'];st=stats(obs);f=A/slug;f.mkdir(exist_ok=True)
  bpy.ops.object.select_all(action='SELECT');bpy.ops.export_scene.gltf(filepath=str(f/(slug+'.glb')),export_format='GLB',use_selection=True,export_apply=True);bpy.ops.wm.save_as_mainfile(filepath=str(f/(slug+'.blend')),compress=True)
  meta=dict(id=slug,title_ja=title,category='household',units='meters',origin='bottom centered; clock front -Y',front_blend='-Y',up_blend='Z',up_glb='Y',design='Original unbranded diorama prop informed by real construction. No manufacturing or safety certification.',license='Original geometry and packed original grain image. No external asset content.',review_status='pending independent review',blender_version=bpy.app.version_string,glb_bytes=(f/(slug+'.glb')).stat().st_size,blend_bytes=(f/(slug+'.blend')).stat().st_size,**st);(f/'metadata.json').write_text(json.dumps(meta,indent=2,ensure_ascii=False)+'\n');print('EXPORTED',slug,st,flush=True)
  if not os.environ.get('SKIP_RENDER'):render_asset(slug)
if __name__=='__main__':main()
