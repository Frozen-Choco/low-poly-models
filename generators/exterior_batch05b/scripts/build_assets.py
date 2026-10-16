import bpy, math, os, json, shutil, hashlib
import numpy as np
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1]; OUT=Path(os.environ.get('ASSET_OUTPUT_ROOT',str(R))); A=OUT/'assets';A.mkdir(parents=True,exist_ok=True)
bpy.context.preferences.filepaths.save_version=0

def clear():
 for o in list(bpy.data.objects):bpy.data.objects.remove(o,do_unlink=True)
 for datablocks in [bpy.data.meshes,bpy.data.materials,bpy.data.curves]:
  for block in list(datablocks):
   if block.users==0:datablocks.remove(block)
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
 sc=bpy.context.scene;sc.render.engine='CYCLES';sc.cycles.samples=20;sc.cycles.use_denoising=False;sc.render.threads_mode='FIXED';sc.render.threads=2;sc.render.resolution_x=720;sc.render.resolution_y=720;sc.render.resolution_percentage=100;sc.render.image_settings.file_format='JPEG';sc.render.image_settings.quality=94;sc.view_settings.view_transform='AgX';sc.world.color=(.25,.25,.25)
 floor=mat('Neutral studio plaster',(.34,.35,.34),0,.9);box('Studio ground',(0,0,-.012),(200,200,.02),floor,.0)
 for pos,power,sz in [((1,-1,2),120,1.5),((-1,-.3,1),80,1),((.4,1,1.5),150,1)]:
  bpy.ops.object.light_add(type='AREA',location=Vector(target)+Vector(pos)*size*3);o=bpy.context.object;o.data.energy=power*size*size*8;o.data.shape='DISK';o.data.size=sz*size*3;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()
 bpy.ops.object.camera_add();cam=bpy.context.object;cam.data.type='ORTHO';cam.data.ortho_scale=size*1.5;sc.camera=cam;return cam

def render_asset(slug):
 f=A/slug;clear();bpy.ops.import_scene.gltf(filepath=str(f/(slug+'.glb')));obs=[o for o in bpy.context.scene.objects if o.type=='MESH'];st=stats(obs);target=(Vector(st['bounds_min'])+Vector(st['bounds_max']))/2;size=max(st['dimensions_m']);cam=studio(target,size)
 for name,off in [('front_three_quarter',(2,-3,2)),('side',(3,0,1.1)),('rear',(-2,3,1.7)),('close_up',(2,-2,3)),('underside',(1,-2,-3))]:
  bpy.data.objects['Studio ground'].hide_render=name=='underside';cam.location=target+Vector(off)*size;cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=size*(1.45 if name!='close_up' else 1.12);bpy.context.scene.render.filepath=str(f/(name+'.jpg'));bpy.ops.render.render(write_still=True)
 shutil.copyfile(f/'front_three_quarter.jpg',f/'preview.jpg');shutil.copyfile(f/'rear.jpg',f/'back.jpg')
def cyl(n,p,r,depth,m,axis='Z',N=64):
 bpy.ops.mesh.primitive_cylinder_add(vertices=N,radius=r,depth=depth,location=p);o=bpy.context.object;o.name=n;o.data.materials.append(m)
 if axis=='Y':o.rotation_euler.x=math.pi/2
 if axis=='X':o.rotation_euler.y=math.pi/2
 for q in o.data.polygons:q.use_smooth=len(q.vertices)==4
 return o
def ring(n,p,r,t,m):
 bpy.ops.mesh.primitive_torus_add(major_segments=96,minor_segments=12,location=p,major_radius=r,minor_radius=t,rotation=(math.pi/2,0,0));o=bpy.context.object;o.name=n;o.data.materials.append(m)
 for q in o.data.polygons:q.use_smooth=True
 return o
def boolean(o,cut):
 bpy.context.view_layer.objects.active=o;q=o.modifiers.new('True manufactured aperture','BOOLEAN');q.object=cut;q.operation='DIFFERENCE';bpy.ops.object.modifier_apply(modifier=q.name);bpy.data.objects.remove(cut,do_unlink=True)
def mirror():
 orange=mat('Muted safety orange powder coat',(.8,.16,.025),0,.36);silver=mat('Silvered convex mirror surface',(.91,.93,.94),1,.045);back=mat('Light gray molded FRP back',(.36,.38,.37),0,.51);metal=mat('Galvanized bracket steel',(.40,.43,.45),.85,.4);concrete=mat('Cast foundation concrete',(.35,.34,.31),0,.94)
 # Foundation visible above grade is a placement collar, not a complete civil engineering footing.
 box('Concrete footing visible collar',(0,.16,.04),(.34,.34,.08),concrete,.012)
 cyl('Orange steel support pole',(0,.16,1.46),.03815,2.88,orange);cyl('Pole top cap',(0,.16,2.902),.040, .012,orange)
 z=2.6;RADIUS=2.2;edge=.3
 # Smooth spherical cap, real 5mm closed shell; center fan avoids collapsed zero-area rings.
 v=[(0,-.02055,z)];f=[];N=128;nr=16
 for j in range(1,nr+1):
  r=edge*j/nr;y=math.sqrt(RADIUS*RADIUS-edge*edge)-math.sqrt(RADIUS*RADIUS-r*r)
  for i in range(N):a=2*math.pi*i/N;v.append((r*math.cos(a),y,z+r*math.sin(a)))
 for i in range(N):f.append((0,1+i,1+(i+1)%N))
 for j in range(nr-1):
  for i in range(N):a=1+j*N+i;b=1+j*N+(i+1)%N;f.append((a,a+N,b+N,b))
 o=mesh('Convex silvered 600mm mirror face',v,f,silver);q=o.modifiers.new('Five millimeter mirror thickness','SOLIDIFY');q.thickness=.005;bpy.context.view_layer.objects.active=o;bpy.ops.object.modifier_apply(modifier=q.name)
 cyl('Molded shallow FRP rear shell',(0,.034,z),.299,.06,back,'Y',128);ring('Rolled aluminum retaining rim',(0,.002,z),.300,.008,orange)
 # Rain hood around top hemisphere, enclosing rim, open bottom.
 v=[];f=[]
 for i in range(65):
  a=math.pi*i/64
  for r,y in [(.308,-.045),(.312,-.045),(.312,.06),(.308,.06)]:v.append((r*math.cos(a),y,z+r*math.sin(a)))
 for i in range(64):
  for j in range(4):f.append((4*i+j,4*i+(j+1)%4,4*(i+1)+(j+1)%4,4*(i+1)+j))
 f.extend([(3,2,1,0),tuple(256+j for j in range(4))]);mesh('Upper orange rain hood',v,f,orange)
 box('Rear steel attachment plate',(0,.067,z),(.16,.008,.16),metal,.006)
 for x in [-.06,.06]:
  for zz in [z-.06,z+.06]:cyl('Rear attachment bolt',(x,.075,zz),.008,.014,metal,'Y',6)
 for zz in [z-.04,z+.04]:
  box('Rear bracket arm',(0,.105,zz),(.04,.082,.008),metal,.002)
  cyl('Pole clamping band',(0,.16,zz),.044,.024,metal)
  # collar is annular rather than a solid disc through pole
  o=bpy.context.object;boolean(o,cyl('Collar bore',(0,.16,zz),.0382,.04,metal))
  box('Clamp front saddle',(0,.119,zz),(.085,.012,.025),metal,.002)
  for x in [-.034,.034]:cyl('Clamp screw',(x,.112,zz),.005,.022,metal,'Y',6)

def service_path(z0,dy):
 pts=[(.406,dy,z0),(.4145,dy,z0)]
 for i in range(17):
  a=-math.pi/2+math.pi/2*i/16;pts.append((.423+.04*math.cos(a),dy+.04+.04*math.sin(a),z0))
 pts.extend([(.463,dy+.04+(.20-dy-.04)*i/4,z0) for i in range(1,5)])
 controls=[Vector((.463,.20,z0)),Vector((.463,.28,z0)),Vector((.463,.34,z0+.08)),Vector((.463,.42,z0+.08))]
 for i in range(1,25):
  t=i/24;pts.append(tuple((1-t)**3*controls[0]+3*(1-t)**2*t*controls[1]+3*(1-t)*t*t*controls[2]+t**3*controls[3]))
 return pts

def transport_tube(n,pts,r,m,N=32):
 # Parallel transport keeps corresponding vertices on each ring aligned through bends.
 vs=[];fs=[];previous_t=None;u=None
 for k,p in enumerate(pts):
  t=(Vector(pts[min(k+1,len(pts)-1)])-Vector(pts[max(0,k-1)])).normalized()
  if previous_t is None:u=t.cross(Vector((0,0,1))).normalized()
  else:u=previous_t.rotation_difference(t)@u;u=(u-t*u.dot(t)).normalized()
  w=t.cross(u).normalized();previous_t=t
  for i in range(N):vs.append(tuple(Vector(p)+r*(math.cos(2*math.pi*i/N)*u+math.sin(2*math.pi*i/N)*w)))
 for k in range(len(pts)-1):
  for i in range(N):a=k*N+i;b=k*N+(i+1)%N;fs.append((a,b,b+N,a+N))
 fs.extend([tuple(reversed(range(N))),tuple((len(pts)-1)*N+i for i in range(N))]);return mesh(n,vs,fs,m)

def condenser():
 enamel=mat('Warm offwhite appliance enamel',(.72,.73,.685),0,.38);steel=mat('Satin zinc hardware',(.43,.46,.46),.85,.43);black=mat('Fan molded dark polymer',(.026,.031,.029),0,.49);fins=mat('Oxidized aluminum fin pack',(.22,.28,.29),.7,.5);rubber=mat('Vibration isolator rubber',(.025,.026,.023),0,.85);pipe=mat('Ivory insulation wrap',(.61,.59,.49),0,.75);brass=mat('Service valve brass',(.43,.29,.095),.8,.35)
 # 740 x 343 x 556 mm cabinet above feet and blocks.
 for x in [-.235,.235]:
  box('Precast support rail',(x,0,.04),(.105,.43,.08),mat('Support concrete '+str(x),(.43,.43,.39),0,.92),.006)
  for y in [-.15,.15]:
   box('Rubber foot isolation pad',(x,y,.084),(.075,.06,.008),rubber,.002);box('Cabinet mounting foot',(x,y,.092),(.08,.082,.016),steel,.002);cyl('Foundation bolt',(x,y,.1),.005,.02,steel,N=6)
 box('Cabinet bottom pan',(0,0,.111),(.738,.339,.022),enamel,.003)
 pan=bpy.data.objects['Cabinet bottom pan'];boolean(pan,cyl('Drain opening tool',(.08,.075,.111),.012,.05,steel))
 box('Cabinet top',(0,0,.65),(.74,.343,.012),enamel,.006)
 box('Right cabinet side',(.366,0,.383),(.008,.33,.528),enamel,.003)
 # Left intake louvers are a true open bank with no backing slab.
 for yy in [-.162,.162]:box('Left intake edge rail',(-.366,yy,.381),(.008,.016,.53),enamel,.002)
 for i in range(21):
  o=box('Left open intake louver '+str(i),(-.365,0,.137+i*.024),(.006,.31,.013),enamel,.001);o.rotation_euler.y=.2
 # Rear fin coil: individual thin plates separated by air gaps, with horizontal tubes.
 for i in range(115):box('Rear condenser fin '+str(i),(-.344+i*.0059,.151,.382),(.0008,.026,.495),fins,.0001,1)
 for zz in [.16,.23,.30,.37,.44,.51,.58]:path_tube('Coil transverse tube',[(-.35,.151,zz),(.335,.151,zz)],[.004,.004],fins,N=12)
 for x in [-.357,.357]:box('Rear coil vertical frame',(x,.153,.38),(.012,.03,.53),enamel,.002)
 # Front sheet includes true round discharge hole; no dark decal behind grill.
 panel=box('Front formed cabinet panel',(0,-.167,.383),(.736,.008,.526),enamel,.003)
 boolean(panel,cyl('Fan hole tool',(-.11,-.17,.38),.22,.06,black,'Y',96))
 ring('Fan discharge rolled lip',(-.11,-.175,.38),.222,.006,enamel)
 cyl('Fan motor hub',(-.11,-.11,.38),.054,.05,black,'Y')
 cyl('Motor casing behind fan',(-.11,-.047,.38),.040,.08,steel,'Y')
 for zz in [.185,.575]:
  path_tube('Motor support strut',[(-.11,-.04,.38),(-.11,.015,zz),(-.11,.14,zz)],[.008,.008,.008],steel,N=20)
 box('Rear motor support spine',(-.11,.13,.38),(.025,.018,.530),steel,.002)
 for k in range(3):
  vs=[]
  # Cambered swept blade, connected root to 200mm radius; solid geometry.
  for r,angle,w in [(.038,0,.035),(.105,.12,.065),(.19,.29,.075),(.204,.38,.038)]:
   a=k*2*math.pi/3+angle
   for s in [-1,1]:vs.append((-.11+r*math.cos(a)-s*w/2*math.sin(a),-.109+s*.012,.38+r*math.sin(a)+s*w/2*math.cos(a)))
  o=mesh('Swept stationary fan blade '+str(k),vs,[(0,1,3,2),(2,3,5,4),(4,5,7,6)],black);q=o.modifiers.new('Blade thickness','SOLIDIFY');q.thickness=.003;bpy.context.view_layer.objects.active=o;bpy.ops.object.modifier_apply(modifier=q.name)
 for r in [.045,.075,.105,.135,.165,.195,.218]:ring('Concentric fan safety guard',(-.11,-.187,.38),r,.0024,enamel)
 for k in range(12):
  a=k*2*math.pi/12;path_tube('Guard radial spoke',[(-.11+.043*math.cos(a),-.187,.38+.043*math.sin(a)),(-.11+.22*math.cos(a),-.187,.38+.22*math.sin(a))],[.002,.002],enamel,N=12)
 for x,zz in [(-.338,.145),(-.338,.621),(.333,.145),(.333,.621)]:cyl('Front panel screw',(x,-.173,zz),.0035,.004,steel,'Y',16)
 box('Right service access cover',(.374,.055,.365),(.012,.19,.36),enamel,.006)
 for zz in [.205,.525]:cyl('Service cover screw',(.383,.055,zz),.004,.008,steel,'X',16)
 for z0,dy in [(.18,.065),(.23,.11)]:
  cyl('Service valve connection',(.393,dy,z0),.012,.028,brass,'X',12)
  pts=service_path(z0,dy)
  transport_tube('Insulated service pipe',pts,.013,pipe,N=32)
 box('Pipe wall penetration collar',(.463,.423,.285),(.09,.012,.18),enamel,.014)

def grate():
 zinc=mat('Weathered galvanized grate steel',(.34,.37,.38),.85,.49);frame=mat('Galvanized angle receiver frame',(.28,.31,.32),.85,.51)
 # Overall 630x430. Panel 600x400, bearing bars span Y. 4mm working gap.
 for y in [-.21,.21]:
  box('Frame upright long edge',(0,y,.019),(.63,.01,.038),frame,.001)
  box('Frame inward bearing shoulder',(0,y-math.copysign(.023,y),.004),(.61,.056,.008),frame,.0006)
 for x in [-.31,.31]:
  box('Frame upright end edge',(x,0,.019),(.01,.412,.038),frame,.001)
  box('Frame end shoulder',(x-math.copysign(.012,x),0,.004),(.032,.36,.008),frame,.0006)
 for y in [-.198,.198]:box('Removable grate end band',(0,y,.023),(.60,.004,.030),zinc,.0005)
 for i in range(21):box('Load bearing bar %02d'%i,(-.297+i*.0297,0,.023),(.005,.394,.030),zinc,.0005)
 for y in [-.15,-.10,-.05,0,.05,.10,.15]:box('Welded transverse tie',(0,y,.035),(.598,.005,.006),zinc,.0005)
 # Actual welded solids: exact unions remove coincident crossing/top/bottom faces.
 # The removable grid and fixed receiver remain separate assemblies.
 def weld(prefixes,name):
  # Axis-aligned constructive solid union, boundary meshing of exact box cells.
  # This removes every internal/coplanar surface without fragile coplanar booleans.
  parts=[o for o in bpy.context.scene.objects if o.type=='MESH' and any(o.name.startswith(p) for p in prefixes)]
  boxes=[]
  for o in parts:
   vv=[o.matrix_world@v.co for v in o.data.vertices]
   boxes.append(tuple(tuple(round(fn(v[k] for v in vv),6) for k in range(3)) for fn in [min,max]))
  coords=[sorted({p[k] for lohi in boxes for p in lohi}) for k in range(3)];occupied=set()
  for i in range(len(coords[0])-1):
   for j in range(len(coords[1])-1):
    for k in range(len(coords[2])-1):
     p=[(coords[a][v]+coords[a][v+1])/2 for a,v in enumerate((i,j,k))]
     if any(all(lo[a]<p[a]<hi[a] for a in range(3)) for lo,hi in boxes):occupied.add((i,j,k))
  verts=[];faces=[];lookup={}
  def vid(c):
   p=tuple(coords[a][c[a]] for a in range(3))
   if p not in lookup:lookup[p]=len(verts);verts.append(p)
   return lookup[p]
  for i,j,k in sorted(occupied):
   for neighbor,corners in [((i-1,j,k),[(i,j,k),(i,j,k+1),(i,j+1,k+1),(i,j+1,k)]),((i+1,j,k),[(i+1,j,k),(i+1,j+1,k),(i+1,j+1,k+1),(i+1,j,k+1)]),((i,j-1,k),[(i,j,k),(i+1,j,k),(i+1,j,k+1),(i,j,k+1)]),((i,j+1,k),[(i,j+1,k),(i,j+1,k+1),(i+1,j+1,k+1),(i+1,j+1,k)]),((i,j,k-1),[(i,j,k),(i,j+1,k),(i+1,j+1,k),(i+1,j,k)]),((i,j,k+1),[(i,j,k+1),(i+1,j,k+1),(i+1,j+1,k+1),(i,j+1,k+1)])]:
    if neighbor not in occupied:faces.append(tuple(vid(c) for c in corners))
  material=parts[0].data.materials[0]
  for o in parts:bpy.data.objects.remove(o,do_unlink=True)
  o=mesh(name,verts,faces,material,False)
  import bmesh
  bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.dissolve_limit(bm,angle_limit=.00001,verts=list(bm.verts),edges=list(bm.edges));bm.to_mesh(o.data);bm.free()
  bpy.context.view_layer.objects.active=o;q=o.modifiers.new('Soft edges on welded assembly','BEVEL');q.width=.0003;q.segments=2;q.limit_method='ANGLE';bpy.ops.object.modifier_apply(modifier=q.name)
  bm=bmesh.new();bm.from_mesh(o.data)
  for _ in range(3):
   bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-7);bmesh.ops.triangulate(bm,faces=list(bm.faces));bmesh.ops.dissolve_degenerate(bm,dist=1e-7,edges=list(bm.edges))
  bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free()
  return o
 weld(['Load bearing','Removable grate','Welded transverse'],'Welded removable grate')
 weld(['Frame upright','Frame inward','Frame end'],'Welded angle receiver frame')


IDS=['roadside_convex_mirror','outdoor_ac_condenser','street_drain_grate']
TITLES=['支柱付きカーブミラー','エアコン室外機','受枠付き排水グレーチング']
def main():
 for slug,title,fn in zip(IDS,TITLES,[mirror,condenser,grate]):
  if os.environ.get('ONLY_ASSETS') and slug not in os.environ['ONLY_ASSETS'].split(','):continue
  clear();fn();bpy.context.view_layer.update();obs=[o for o in bpy.context.scene.objects if o.type=='MESH'];st=stats(obs);f=A/slug;f.mkdir(exist_ok=True)
  bpy.ops.object.select_all(action='SELECT');bpy.ops.export_scene.gltf(filepath=str(f/(slug+'.glb')),export_format='GLB',use_selection=True,export_apply=True);bpy.ops.wm.save_as_mainfile(filepath=str(f/(slug+'.blend')),compress=True)
  meta=dict(id=slug,title_ja=title,category='exterior',units='meters',origin=({'roadside_convex_mirror':'Grade plane at Z=0 below mirror face; pole and footing center X=0,Y=0.16 m','outdoor_ac_condenser':'Ground plane at Z=0 below cabinet center; supports included','street_drain_grate':'Bottom receiver plane Z=0, centered X/Y; lower by 0.038 m for flush grade installation'}[slug]),front_blend='-Y',up_blend='Z',up_glb='Y',design='Original unbranded generic diorama prop; not a dimension-perfect product replica or certified equipment.',license='Original geometry and PBR materials. No reference images embedded.',review_status='pending independent review',review_standard_revision='2026-10-16 real-world construction and use',blender_version=bpy.app.version_string,glb_bytes=(f/(slug+'.glb')).stat().st_size,blend_bytes=(f/(slug+'.blend')).stat().st_size,preview='preview.jpg',back='back.jpg',**st);(f/'metadata.json').write_text(json.dumps(meta,indent=2,ensure_ascii=False)+'\n');print('EXPORTED',slug,flush=True)
  if not os.environ.get('SKIP_RENDER'):render_asset(slug)
if __name__=='__main__':main()
