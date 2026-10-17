import bpy,bmesh,math,json,hashlib,sys
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1]
def mat(n,c,rough=.5,metal=0):
 m=bpy.data.materials.new(n);m.diffuse_color=(*c,1);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*c,1);p.inputs['Roughness'].default_value=rough;p.inputs['Metallic'].default_value=metal;return m
def mod(o,t,**kw):
 bpy.context.view_layer.objects.active=o;m=o.modifiers.new(t,t)
 for k,v in kw.items():setattr(m,k,v)
 bpy.ops.object.modifier_apply(modifier=m.name)
def finish(o,n,m):
 o.name=n;o.data.materials.append(m)
 for p in o.data.polygons:p.use_smooth=True
 return o
def box(n,loc,dim,m,b=.002):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.dimensions=dim;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 if b:mod(o,'BEVEL',width=min(b,min(dim)*.45),segments=4)
 finish(o,n,m);mod(o,'WEIGHTED_NORMAL',keep_sharp=True);return o
def cyl(n,loc,r,d,m,axis='Z'):
 bpy.ops.mesh.primitive_cylinder_add(vertices=48,radius=r,depth=d,location=loc);o=bpy.context.object
 if axis=='X':o.rotation_euler.y=math.pi/2
 if axis=='Y':o.rotation_euler.x=math.pi/2
 mod(o,'BEVEL',width=min(.0005,d/5),segments=3);finish(o,n,m);mod(o,'WEIGHTED_NORMAL',keep_sharp=True);return o
def lathe(n,profile,mats,indices=None,N=96):
 # Profile travels around a solid cross-section. Axis points are welded fans.
 verts=[];rings=[];faces=[];mi=[]
 for r,z in profile:
  if r==0:rings.append([len(verts)]);verts.append((0,0,z))
  else:
   ring=[]
   for i in range(N):a=i*math.tau/N;ring.append(len(verts));verts.append((r*math.cos(a),r*math.sin(a),z))
   rings.append(ring)
 for j in range(len(rings)-1):
  a,b=rings[j:j+2]
  for i in range(N):
   k=(i+1)%N
   if len(a)==1:f=(a[0],b[i],b[k])
   elif len(b)==1:f=(a[i],b[0],a[k])
   else:f=(a[i],b[i],b[k],a[k])
   faces.append(f);mi.append(indices[j] if indices else 0)
 me=bpy.data.meshes.new(n);me.from_pydata(verts,[],faces);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();o=bpy.data.objects.new(n,me);bpy.context.collection.objects.link(o)
 for m in mats:me.materials.append(m)
 for p,j in zip(me.polygons,mi):p.material_index=j;p.use_smooth=abs(p.normal.z)<.999
 return o
def sector(n,profile,halfangle,m,N=24):
 verts=[];faces=[];K=len(profile)
 for j in range(N+1):
  a=-halfangle+2*halfangle*j/N
  for r,z in profile:verts.append((r*math.cos(a),r*math.sin(a),z))
 for j in range(N):
  for k in range(K):l=(k+1)%K;faces.append((j*K+k,j*K+l,(j+1)*K+l,(j+1)*K+k))
 faces.extend([tuple(reversed(range(K))),tuple(N*K+k for k in range(K))]);me=bpy.data.meshes.new(n);me.from_pydata(verts,[],faces);me.update();o=bpy.data.objects.new(n,me);bpy.context.collection.objects.link(o);finish(o,n,m);return o
def tube(n,points,rx,rz,m):
 verts=[];faces=[];N=16
 for j,p in enumerate(points):
  tangent=Vector(points[min(j+1,len(points)-1)])-Vector(points[max(j-1,0)]);tangent.z=0;tangent.normalize();side=Vector((-tangent.y,tangent.x,0))
  for i in range(N):a=i*math.tau/N;verts.append(tuple(Vector(p)+side*rx*math.cos(a)+Vector((0,0,rz*math.sin(a)))))
 for j in range(len(points)-1):
  for i in range(N):k=(i+1)%N;faces.append((j*N+i,j*N+k,(j+1)*N+k,(j+1)*N+i))
 faces += [tuple(reversed(range(N))),tuple((len(points)-1)*N+i for i in range(N))]
 me=bpy.data.meshes.new(n);me.from_pydata(verts,[],faces);me.update();o=bpy.data.objects.new(n,me);bpy.context.collection.objects.link(o);finish(o,n,m);return o
def cut(o,c):
 mod(o,'BOOLEAN',object=c,operation='DIFFERENCE',solver='EXACT');bpy.data.objects.remove(c,do_unlink=True)

def wire(n,points,r,m,N=8,closed=False):
 verts=[];faces=[];L=len(points)
 for j,p in enumerate(points):
  prev=points[(j-1)%L] if closed else points[max(0,j-1)];nxt=points[(j+1)%L] if closed else points[min(L-1,j+1)];t=(Vector(nxt)-Vector(prev)).normalized();u=t.cross(Vector((0,1,0)))
  if u.length<.01:u=t.cross(Vector((0,0,1)))
  if j>0:u=last_u-t*last_u.dot(t)
  u.normalize();last_u=u.copy();v=t.cross(u).normalized()
  for k in range(N):a=math.tau*k/N;verts.append(tuple(Vector(p)+r*(math.cos(a)*u+math.sin(a)*v)))
 for j in range(L if closed else L-1):
  jj=(j+1)%L
  for k in range(N):kk=(k+1)%N;faces.append((j*N+k,j*N+kk,jj*N+kk,jj*N+k))
 if not closed:faces.extend([tuple(reversed(range(N))),tuple((L-1)*N+k for k in range(N))])
 me=bpy.data.meshes.new(n);me.from_pydata(verts,[],faces);me.update();o=bpy.data.objects.new(n,me);bpy.context.collection.objects.link(o);finish(o,n,m);return o
def materials():
 global STEEL,RESIN,WHITE,BLADE,MICA,RUBBER,RED
 STEEL=mat('Chrome plated steel',(.64,.66,.68),.22,1);RESIN=mat('Charcoal polypropylene',(.022,.026,.029),.38);WHITE=mat('Warm white ABS',(.72,.74,.72),.38);BLADE=mat('Grey polypropylene blade',(.18,.22,.23),.4);MICA=mat('Mica heater substrate',(.20,.14,.10),.8);RUBBER=mat('Dark elastomer foot',(.014,.016,.018),.78);RED=mat('Unlit indicator lens',(.12,.008,.004),.25)
def toaster():
 # Long axis Y; control face -Y. Outer casting is a real hollow shell, not a solid block.
 for x in [-.056,.056]:
  for y in [-.108,.108]:box('Foot '+str((x,y)),(x,y,.005),(.018,.022,.010),RUBBER,.003)
 base=box('Moulded base',(0,0,.026),(.165,.281,.036),RESIN,.009)
 cut(base,box('Temporary base recess',(0,0,.072),(.150,.252,.082),RESIN,.004))
 cut(base,box('Temporary tray exit',(0,.140,.0375),(.141,.040,.008),RESIN,.001))
 for x in [-.060,.060]:
  for y in [-.108,.108]:box('Chassis support boss '+str((x,y)),(x,y,.033),(.010,.010,.006),RESIN,.001)
 body=box('Continuous chrome shell',(0,0,.112),(.158,.267,.196),STEEL,.025)
 cut(body,box('Temporary flat shell bottom',(0,0,-.100),(.4,.5,.284),RESIN,0))
 cavity=box('Temporary hollow interior',(0,0,.060),(.154,.263,.293),RESIN,.023);cut(body,cavity)
 for x in [-.037,.037]:
  cutter=box('Temporary bread aperture',(x,0,.207),(.033,.177,.05),RESIN,.006);cut(body,cutter)
 # A genuine vertical slot. Lever stem is narrower and has clearance for travel.
 cut(body,box('Temporary lever aperture',(0,-.133,.130),(.007,.03,.105),RESIN,.003))
 mod(body,'TRIANGULATE',quad_method='FIXED',ngon_method='CLIP')
 # Lower structural deck supports cage, shell and tray; tray handle is distinct from base.
 box('Steel chassis deck',(0,0,.035),(.149,.251,.003),STEEL,.001)
 tray=box('Crumb tray pan',(0,0,.0375),(.137,.168,.002),STEEL,.0007)
 box('Crumb tray rear grip',(0,.151,.0375),(.065,.014,.010),RESIN,.003)
 box('Crumb tray connecting tang',(0,.111,.0375),(.028,.074,.0015),STEEL,.001)
 for x in [-.056,-.018,.018,.056]:
  box('Mica heating panel '+str(x),(x,0,.112),(.0015,.183,.143),MICA,.0004)
  for z in [.053,.075,.097,.119,.141,.163,.179]:
   # Coils represented as subdued supported ribbons, cold and unpowered.
   box('Cold heater ribbon '+str((x,z)),(x+(.001 if x<0 else -.001),0,z),(.0006,.172,.0012),STEEL,.0001)
 for x in [-.037,.037]:
  box('Bread carrier floor '+str(x),(x,0,.062),(.028,.180,.002),STEEL,.0005)
  for y in [-.092,.092]:
   box('Bread cage end plate '+str((x,y)),(x,y,.115),(.041,.002,.148),STEEL,.0007)
  for sign in [-1,1]:
   xx=x+sign*.013
   wire('Bread centering rail '+str((x,sign)),[(xx,-.091,.159),(xx,.091,.159)],.0008,STEEL)
   for y in [-.068,0,.068]:wire('Bread cage vertical wire '+str((x,sign,y)),[(xx,y,.062),(xx,y,.181)],.0007,STEEL)
 for y in [-.092,.092]:
  box('Cage bridge above tray '+str(y),(0,y,.0415),(.150,.006,.003),STEEL,.0005)
  for x in [-.0718,.0718]:box('Cage outer support '+str((x,y)),(x,y,.038),(.005,.005,.008),STEEL,.0005)
 # Internal slide rail and crossbar give the visible lever a structural path.
 box('Lever guide rail',(0,-.116,.105),(.005,.008,.142),STEEL,.001)
 box('Carrier connecting crossbar',(0,-.095,.062),(.100,.020,.004),STEEL,.0008)
 box('Carrier lift link',(0,-.110,.108),(.008,.014,.092),STEEL,.001)
 box('Lever slider',(0,-.118,.152),(.011,.014,.015),RESIN,.002)
 box('Lever horizontal stem',(0,-.136,.152),(.004,.029,.006),STEEL,.001)
 box('Lever thumb pad',(0,-.153,.152),(.045,.021,.012),RESIN,.005)
 cyl('Browning dial spindle',(-.028,-.130,.057),.004,.016,STEEL,'Y')
 cyl('Browning dial',(-.028,-.142,.057),.013,.014,RESIN,'Y')
 box('Dial raised index',(-.028,-.1495,.066),(.002,.001,.006),WHITE,.0004)
 for x in [.012,.037]:cyl('Function button '+str(x),(x,-.133,.054),.0055,.011,RESIN,'Y')
 cyl('Unlit status lens',(.025,-.132,.071),.0025,.005,RED,'Y')
 # Cord omitted beyond strain relief, for placement without a sprawling cable footprint.
 cyl('Rear cable strain relief',(.045,.135,.026),.0045,.012,RUBBER,'Y')
 return {'description':'2枚差しの金属トースター。実開口スロット、内側の支持枠、レバー、ダイヤル、パン屑トレイ。','reference_dimensions_m':[.165,.310,.210],'mechanism':'Static unpowered generic toaster. Separate tray and lever, no animation or thermal/electrical certification. Power cable beyond rear strain relief intentionally omitted.'}
def fan():
 # Circular housing profile, a metal weighted base concealed by polymer cover.
 for a in range(4):
  t=math.tau*a/4+math.pi/4;cyl('Base rubber foot '+str(a),(.123*math.cos(t),.123*math.sin(t),.004),.013,.008,RUBBER)
 lathe('Base weighted steel plate',[(0,.008),(.143,.008),(.149,.011),(.149,.020),(0,.020)],[STEEL],N=64)
 lathe('Base moulded cover',[(0,.018),(.146,.018),(.158,.024),(.161,.032),(.157,.040),(.145,.046),(.08,.052),(0,.052)],[WHITE],N=64)
 cyl('Column lower socket',(0,.115,.081),.026,.070,WHITE)
 cyl('Column steel core',(0,.115,.298),.012,.490,STEEL)
 cyl('Column white sleeve',(0,.115,.290),.017,.430,WHITE)
 cyl('Column joint collar',(0,.115,.499),.021,.024,WHITE)
 cyl('Column upper sleeve',(0,.115,.552),.016,.093,WHITE)
 # Head tilt trunnion carried by stem and a thick molded neck.
 box('Neck head carrier',(0,.115,.590),(.038,.050,.054),WHITE,.012)
 cyl('Head tilt axle',(0,.115,.603),.010,.052,STEEL,'X')
 for s in [-1,1]:cyl('Tilt pivot cap '+str(s),(s*.025,.115,.603),.014,.010,WHITE,'X')
 Z=.655
 cyl('Motor casing',(0,.085,Z),.044,.115,WHITE,'Y')
 cyl('Rear motor cap',(0,.145,Z),.038,.012,WHITE,'Y')
 cyl('Motor shaft',(0,.006,Z),.005,.063,STEEL,'Y')
 cyl('Rear guard mounting boss',(0,.032,Z),.025,.018,WHITE,'Y')
 # Dense but genuinely open guards, original radial pattern simplified from spiral reference.
 for side in [-1,1]:
  for j in range(40):
   a=math.tau*j/40;pts=[]
   for i in range(7):
    r=.024+(.144*i/6);y=side*(.058-.044*(r/.168)**2)
    pts.append((r*math.sin(a),y,Z+r*math.cos(a)))
   wire(('Front' if side<0 else 'Rear')+' guard spoke '+str(j),pts,.00105,WHITE,N=6)
  for r in [.080,.125,.168]:
   y=side*(.058-.044*(r/.168)**2)
   wire(('Front' if side<0 else 'Rear')+' guard hoop '+str(r),[(r*math.sin(math.tau*i/64),y,Z+r*math.cos(math.tau*i/64)) for i in range(64)],.0014,WHITE,N=8,closed=True)
 # The front and rear outer hoops connect into the thick retaining rim through clips.
 for y in [-.014,.014]:
  wire('Guard retaining rim '+str(y),[(.168*math.sin(math.tau*i/64),y,Z+.168*math.cos(math.tau*i/64)) for i in range(64)],.0035,WHITE,N=8,closed=True)
 for j in range(4):
  a=math.tau*j/4;wire('Guard rim clip '+str(j),[(.169*math.sin(a),-.016,Z+.169*math.cos(a)),(.170*math.sin(a),0,Z+.170*math.cos(a)),(.169*math.sin(a),.016,Z+.169*math.cos(a))],.003,RESIN,N=8)
 cyl('Front guard centre badge',(0,-.057,Z),.027,.007,WHITE,'Y')
 cyl('Rotor hub',(0,-.003,Z),.029,.034,BLADE,'Y')
 cyl('Rotor spindle cap',(0,-.023,Z),.017,.009,WHITE,'Y')
 # Seven sweep-pitched solid blades with explicit 2 mm thickness. Root merges into hub.
 for j in range(7):
  angle=math.tau*j/7;verts=[];faces=[];rows=6;cols=5
  for layer in [-1,1]:
   for i in range(rows):
    t=i/(rows-1);r=.023+.125*t;mid=angle+.47*t;width=.12+.35*math.sin(math.pi*t*.8)
    for k in range(cols):
     u=k/(cols-1)-.5;a=mid+u*width;y=.014*u*2 + .003*math.sin(math.pi*t)+layer*.001
     verts.append((r*math.sin(a),y,Z+r*math.cos(a)))
  K=rows*cols
  for i in range(rows-1):
   for k in range(cols-1):
    q=i*cols+k;faces += [(q,q+1,q+cols+1,q+cols),(K+q,K+q+cols,K+q+cols+1,K+q+1)]
  edge=list(range(cols))+[i*cols+cols-1 for i in range(1,rows)]+list(range(K-2,K-cols-1,-1))+[i*cols for i in range(rows-2,0,-1)]
  for q,p in zip(edge,edge[1:]+edge[:1]):faces.append((q,K+q,K+p,p))
  me=bpy.data.meshes.new('Pitched blade');me.from_pydata(verts,[],faces);me.update();o=bpy.data.objects.new('Rotor blade '+str(j+1),me);bpy.context.collection.objects.link(o);finish(o,o.name,BLADE);mod(o,'TRIANGULATE',quad_method='FIXED',ngon_method='CLIP')
 cyl('Oscillation selector stem',(0,.112,.701),.003,.018,STEEL)
 cyl('Oscillation selector cap',(0,.112,.709),.007,.007,WHITE)
 for i in range(4):cyl('Base speed button '+str(i),((i-1.5)*.025,-.085,.051),.008,.008,RESIN)
 cyl('Rear base strain relief',(0,.158,.025),.005,.018,RUBBER,'Y')
 return {'description':'7枚羽根の床置き扇風機。実厚の開いたガード、ピッチ付き羽根、支柱、首振りつまみと台座。','reference_dimensions_m':[.345,.340,.965],'mechanism':'Fixed-height static generic fan. Rotor parts separately editable; clearance must accommodate full rotation. Tilt and oscillation represented mechanically but not rigged. Spiral grille generalized to radial wires; cable beyond strain relief omitted.'}
def shell_normals(o):
 # Analytic normals for a rounded-box steel shell: exact planar directions and
 # continuous tangent normals on the curved edges. Cuts retain crisp walls.
 me=o.data
 def rounded(p,center,half,r):
  q=Vector(p)-Vector(center);core=Vector(tuple(h-r for h in half));clamped=Vector(tuple(max(-core[i],min(core[i],q[i])) for i in range(3)));d=q-clamped
  return d.length,d.normalized()
 normals=[None]*len(me.loops)
 for face in me.polygons:
  vv=[me.vertices[i].co for i in face.vertices]
  outer=[rounded(v,(0,0,0),(.079,.1335,.098),.025) for v in vv]
  inner=[rounded(v,(0,0,-.052),(.077,.1315,.1465),.023) for v in vv]
  outside=all(abs(d-.025)<.00003 for d,n in outer)
  inside=all(abs(d-.023)<.00003 for d,n in inner)
  face.use_smooth=True
  for idx,li in enumerate(face.loop_indices):
   normals[li]=tuple(outer[idx][1] if outside else -inner[idx][1] if inside else face.normal)
 me.normals_split_custom_set(normals)

def save(slug,fn):
 bpy.ops.wm.read_factory_settings(use_empty=True);bpy.context.preferences.filepaths.save_version=0;materials();meta=fn();sc=bpy.context.scene;sc.unit_settings.system='METRIC';sc.render.threads_mode='FIXED';sc.render.threads=2
 for o in list(sc.objects):
  if o.type!='MESH':continue
  bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free()
  o['assembly_role']='rotor' if o.name.startswith('Rotor') else 'fixed';o['attachment_note']='Static assembly with positive embedded joints; see configs/attachments.json.'
  bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o;bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.uv.smart_project(island_margin=.01);bpy.ops.object.mode_set(mode='OBJECT')
 if slug=='toaster':shell_normals(bpy.data.objects['Continuous chrome shell'])
 bpy.ops.object.select_all(action='SELECT');out=R/'assets'/slug;out.mkdir(parents=True,exist_ok=True);blend=out/(slug+'.blend');glb=out/(slug+'.glb');bpy.ops.wm.save_as_mainfile(filepath=str(blend),compress=True);bpy.ops.export_scene.gltf(filepath=str(glb),export_format='GLB',export_yup=True,export_animations=False,export_extras=True)
 obs=[o for o in sc.objects if o.type=='MESH'];vs=[o.matrix_world@v.co for o in obs for v in o.data.vertices];lo=[min(v[i] for v in vs) for i in range(3)];hi=[max(v[i] for v in vs) for i in range(3)];tris=0
 for o in obs:o.data.calc_loop_triangles();tris+=len(o.data.loop_triangles)
 meta.update(id=slug,title_ja={'toaster':'トースター','electric_fan':'扇風機'}[slug],revision=(12 if slug=='toaster' else 3),dimensions_m=[hi[i]-lo[i] for i in range(3)],triangles=tris,units='meter',up_axis_blend='Z',up_axis_glb='Y',review_status='Pending independent geometry gate',photography_status='Not authorized',files={p.suffix[1:]:{'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in [blend,glb]});(out/'metadata.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n');print('ASSET_DONE',slug,tris,flush=True)

if __name__=='__main__':
 args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
 for slug,fn in [('toaster',toaster),('electric_fan',fan)]:
  if not args or slug in args:save(slug,fn)
