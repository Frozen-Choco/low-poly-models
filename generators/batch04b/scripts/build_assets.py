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
 for name,off in [('front_three_quarter',(2,-3,2)),('side',(3,0,1.1)),('rear',(-2,3,1.7)),('close_up',(2,-2,3)),('underside',(1,-2,-3))]:
  bpy.data.objects['Studio ground'].hide_render=name=='underside';cam.location=target+Vector(off)*size;cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=size*(1.45 if name!='close_up' else 1.12);bpy.context.scene.render.filepath=str(f/(name+'.jpg'));bpy.ops.render.render(write_still=True)
 shutil.copyfile(f/'front_three_quarter.jpg',f/'preview.jpg');shutil.copyfile(f/'rear.jpg',f/'back.jpg')
def fiber(n,c,seed):
 m=mat(n,c,0,.83);N=512;rng=np.random.default_rng(seed);noise=rng.normal(0,.014,(N,N));fine=rng.random((N,N));noise+=np.where(fine>.98,-.055,0)
 arr=np.ones((N,N,4),np.float32)
 for k,col in enumerate(c):arr[:,:,k]=np.clip(col+noise,0,1)
 im=bpy.data.images.new(n+' original fiber albedo',width=N,height=N);im.pixels.foreach_set(arr.ravel());im.pack();nd=m.node_tree.nodes.new('ShaderNodeTexImage');nd.image=im;m.node_tree.links.new(nd.outputs['Color'],m.node_tree.nodes.get('Principled BSDF').inputs['Base Color']);return m

def shipping_box():
 kraft=fiber('Recycled kraft board',(.45,.29,.155),401);edge=mat('Dark cut board edges',(.29,.175,.082),0,.93);tape=mat('Matte gummed packing tape',(.33,.22,.125),0,.62)
 # Six independent 3 mm board panels, overlapping folded top and bottom flaps.
 for y in [-.119,.119]:box('Long folded wall',(0,y,.1035),(.32,.003,.201),kraft,.0005)
 for x in [-.1585,.1585]:box('Short folded wall',(x,0,.102),(.003,.235,.198),kraft,.0005)
 for z in [.0045,.2015]:
  box('Underlapping end flap left',(-.099,0,z),(.118,.234,.003),kraft,.00025);box('Underlapping end flap right',(.099,0,z),(.118,.234,.003),kraft,.00025)
 for z in [.0015,.2045]:
  for y in [-.0595,.0595]:box('Meeting long closure flap',(0,y,z),(.317,.118,.003),kraft,.0003)
 # The dark 1 mm join stays physically beneath the tape.
 box('Top seam shadow',(0,0,.2045),(.316,.001,.002),edge,.0)
 for z in [-.00015,.20615]:box('Continuous seam tape',(0,0,z),(.3217,.048,.0003),tape,.0001)
 for x in [-.1607,.1607]:
  box('Tape folded over carton end',(x,0,.174),(.0003,.048,.064),tape,.0001)
  box('Bottom tape folded over carton end',(x,0,.01785),(.0003,.048,.036),tape,.0001)
 box('Interior glued manufacturer joint',(-.148,-.116,.102),(.022,.002,.194),kraft,.0003)
 # Tuck score lines and local folded corner compression are subtle geometry.
 for x in [-.155,.155]:
  box('Fold score at flap end',(x,0,.20602),(.00045,.235,.00008),edge,0)

def stapler():
 steel=mat('Zinc plated mechanism',(.54,.57,.59),1,.28);chrome=mat('Polished hinge pin',(.65,.66,.68),1,.19);body=mat('Satin dark burgundy enamel',(.12,.019,.026),.15,.29);rubber=mat('Rubber nonslip sole',(.019,.018,.017),0,.82)
 box('Molded rubber sole',(0,0,.0018),(.047,.158,.0036),rubber,.004)
 box('Stamped steel base',(0,0,.0063),(.047,.158,.006),steel,.004)
 box('Base painted insert',(0,.022,.010),(.040,.103,.004),body,.003)
 # front anvil sits flush and has two real formed staple channels.
 anvil=box('Stainless clinching anvil',(0,-.064,.011),(.025,.025,.003),chrome,.001)
 for x in [-.0048,.0048]:
  bpy.ops.mesh.primitive_uv_sphere_add(segments=20,ring_count=10,radius=1,location=(x,-.064,.0128));cut=bpy.context.object;cut.scale=(.004,.0012,.0009);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);bpy.context.view_layer.objects.active=anvil;mod=anvil.modifiers.new('Recessed clinch channel','BOOLEAN');mod.object=cut;mod.operation='DIFFERENCE';bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(cut,do_unlink=True)
 for x in [-.016,.016]:box('Rear hinge support',(x,.058,.019),(.003,.018,.023),steel,.0015)
 path_tube('Transverse steel hinge axle',[(-.022,.058,.027),(.022,.058,.027)],[.003,.003],chrome,N=32)
 # Magazine is a U channel with its front open and a separate driver nose.
 box('Magazine bottom',(0,.000,.0198),(.029,.125,.0012),steel,.0006)
 for x in [-.0145,.0145]:box('Magazine folded side rail',(x,-.002,.026),(.0015,.129,.009),steel,.0005)
 box('Staple support rail',(0,-.029,.0236),(.011,.066,.0063),steel,.0002)
 for i in range(100):
  y=-.061+i*.00065
  box('Staple crown '+str(i),(0,y,.027),(.0128,.0005,.0005),chrome,.00008,1)
  for x in [-.00615,.00615]:box('Staple leg',(x,y,.024),(.0005,.0005,.006),chrome,.00008,1)
 for x in [-.018,.018]:box('Pressure arm hinge ear',(x,.058,.030),(.003,.013,.012),body,.001)
 box('Front driver face',(0,-.064,.027),(.026,.002,.017),steel,.0007)
 # sculpted pressure arm uses lofted rectangular sections, rounded by bevel.
 prof=[(-.071,.031,.018),(-.062,.041,.021),(-.020,.047,.023),(.035,.047,.021),(.065,.037,.017),(.073,.030,.010)]
 v=[]
 for y,z,w in prof:v.extend([(-w,y,z-.009),(w,y,z-.009),(w,y,z),(-w,y,z)])
 fs=[(3,2,1,0)]
 for i in range(len(prof)-1):
  for j in range(4):fs.append((i*4+j,i*4+(j+1)%4,(i+1)*4+(j+1)%4,(i+1)*4+j))
 fs.append(tuple((len(prof)-1)*4+j for j in range(4)))
 o=mesh('Contoured enamel pressure arm',v,fs,body,False);bpy.context.view_layer.objects.active=o;mod=o.modifiers.new('Formed rounded edges','BEVEL');mod.width=.003;mod.segments=4;bpy.ops.object.modifier_apply(modifier=mod.name)

def clipboard():
 board=fiber('Compressed hardboard fibers',(.31,.205,.117),402);paper=fiber('Warm uncoated white paper',(.82,.815,.775),403);steel=mat('Brushed spring steel',(.58,.62,.65),1,.28);dark=mat('Clip contact pad',(.025,.027,.026),0,.75)
 box('Thin hardboard clipboard',(0,0,.0016),(.235,.34,.0032),board,.005)
 for i in range(5):box('A4 paper sheet '+str(i+1),(.00015*(i%2),-.012,.00328+i*.00013),(.210,.297,.000105),paper,.00001,1)
 # Backplate riveted through board; hinge barrel and bowed spring jaws rest on paper.
 box('Clip fixed steel backplate',(0,.151,.0040),(.084,.022,.0013),steel,.002)
 for x in [-.032,.032]:
  path_tube('Clip fixing rivet',[(x,.151,.0003),(x,.151,.006)],[.0023,.0023],steel,N=24)
 path_tube('Rolled spring hinge',[(-.038,.151,.008),(.038,.151,.008)],[.0033,.0033],steel,N=32)
 # Low-profile sprung wire jaw, matching the Saunders clip topology.
 pts=[(-.038,.151,.008),(-.039,.143,.008),(-.039,.130,.006),(-.035,.126,.0058),(-.014,.126,.0058),(-.009,.122,.0058),(.009,.122,.0058),(.014,.126,.0058),(.035,.126,.0058),(.039,.130,.006),(.039,.143,.008),(.038,.151,.008)]
 path_tube('Spring wire jaw with finger lift',pts,[.0011]*len(pts),steel,N=24)
 for x in [-.034,.034]:box('Clip jaw paper contact pad',(x,.126,.00535),(.012,.006,.003),dark,.001)
 # Two visible torsion spring coils are coaxial with the rolled hinge.
 for x in [-.030,.030]:
  pts=[(x+.006*(i/100-.5),.151+.0024*math.cos(i/100*math.pi*10),.008+.0024*math.sin(i/100*math.pi*10)) for i in range(101)]
  path_tube('Jaw torsion spring',pts,[.00035]*len(pts),steel,N=8)

IDS=['taped_shipping_box','office_stapler','a4_clipboard']
TITLES=['段ボール箱','ホチキス','クリップボード']
def main():
 for slug,title,fn in zip(IDS,TITLES,[shipping_box,stapler,clipboard]):
  if os.environ.get('ONLY_ASSETS') and slug not in os.environ['ONLY_ASSETS'].split(','):continue
  clear();fn();bpy.context.view_layer.update();lowest=min((o.matrix_world@v.co).z for o in bpy.context.scene.objects if o.type=='MESH' for v in o.data.vertices)
  for o in bpy.context.scene.objects:o.location.z-=lowest
  bpy.context.view_layer.update();obs=[o for o in bpy.context.scene.objects if o.type=='MESH'];st=stats(obs);f=A/slug;f.mkdir(exist_ok=True)
  bpy.ops.object.select_all(action='SELECT');bpy.ops.export_scene.gltf(filepath=str(f/(slug+'.glb')),export_format='GLB',use_selection=True,export_apply=True);bpy.ops.wm.save_as_mainfile(filepath=str(f/(slug+'.blend')),compress=True)
  meta=dict(id=slug,title_ja=title,category='household',units='meters',origin='bottom centered',front_blend='-Y',up_blend='Z',up_glb='Y',design='Original unbranded generic prop at plausible real-world scale; not a replica.',license='Original geometry and packed procedural fiber images. No external assets.',review_status='pending independent review',blender_version=bpy.app.version_string,glb_bytes=(f/(slug+'.glb')).stat().st_size,blend_bytes=(f/(slug+'.blend')).stat().st_size,**st);(f/'metadata.json').write_text(json.dumps(meta,indent=2,ensure_ascii=False)+'\n');print('EXPORTED',slug,flush=True)
  if not os.environ.get('SKIP_RENDER'):render_asset(slug)
if __name__=='__main__':main()
