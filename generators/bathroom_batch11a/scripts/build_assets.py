import bpy,bmesh,math,json,hashlib,sys
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1]
bpy.context.preferences.filepaths.save_version=0

def mat(n,c,metal=0,rough=.4):
 m=bpy.data.materials.new(n);m.diffuse_color=(*c,1);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*c,1);p.inputs['Metallic'].default_value=metal;p.inputs['Roughness'].default_value=rough;return m

def apply(o,typ,**kw):
 bpy.context.view_layer.objects.active=o;q=o.modifiers.new(typ,typ)
 for k,v in kw.items():setattr(q,k,v)
 bpy.ops.object.modifier_apply(modifier=q.name)
def finish(o,n,m):
 o.name=n;o.data.materials.clear();o.data.materials.append(m)
 for p in o.data.polygons:p.use_smooth=True
 apply(o,'WEIGHTED_NORMAL',keep_sharp=True,weight=50)
 return o

def box(n,loc,dim,m,b=.002):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.dimensions=dim;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 if b:apply(o,'BEVEL',width=min(b,min(dim)*.4),segments=3)
 return finish(o,n,m)
def cyl(n,loc,r,depth,m,axis='Z',scale=(1,1)):
 bpy.ops.mesh.primitive_cylinder_add(vertices=48,radius=r,depth=depth,location=loc);o=bpy.context.object
 o.scale.x=scale[0];o.scale.y=scale[1]
 if axis=='X':o.rotation_euler[1]=math.pi/2
 if axis=='Y':o.rotation_euler[0]=math.pi/2
 bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);apply(o,'BEVEL',width=min(.0007,depth/5),segments=2);return finish(o,n,m)
def cut(o,c):
 apply(o,'BOOLEAN',operation='DIFFERENCE',solver='EXACT',object=c);bpy.data.objects.remove(c,do_unlink=True)
 for p in o.data.polygons:p.use_smooth=(max(abs(c) for c in p.normal)<.999 if o.name in ['Door surround','Case with open front cavity','Control fascia'] else abs(p.normal.z)<.999)
 apply(o,'WEIGHTED_NORMAL',keep_sharp=True,weight=50)
def tube(n,pts,r,m):
 cu=bpy.data.curves.new(n,'CURVE');cu.dimensions='3D';cu.resolution_u=12;cu.bevel_depth=r;cu.bevel_resolution=3;cu.use_fill_caps=True;s=cu.splines.new('BEZIER');s.bezier_points.add(len(pts)-1)
 for p,co in zip(s.bezier_points,pts):p.co=co;p.handle_left_type='AUTO';p.handle_right_type='AUTO'
 # Clamp each Bezier handle to its segment endpoint Z range: cable cannot sag through support plane.
 for i,p in enumerate(s.bezier_points):
  if n!='Unplugged power cable':continue
  left=p.handle_left.copy();right=p.handle_right.copy();prev=pts[max(0,i-1)][2];nxt=pts[min(len(pts)-1,i+1)][2];left.z=max(min(prev,p.co.z),min(max(prev,p.co.z),left.z));right.z=max(min(nxt,p.co.z),min(max(nxt,p.co.z),right.z));p.handle_left_type='FREE';p.handle_right_type='FREE';p.handle_left=left;p.handle_right=right
 o=bpy.data.objects.new(n,cu);bpy.context.collection.objects.link(o);cu.materials.append(m);bpy.context.view_layer.objects.active=o;o.select_set(True);bpy.ops.object.convert(target='MESH');o.select_set(False);return o

def shell(n,profile,m,sx=1,sy=1,cy=0):
 N=96;v=[];f=[];rings=[]
 for r,z in profile:
  if r==0:rings.append([len(v)]);v.append((0,cy,z))
  else:
   rings.append(list(range(len(v),len(v)+N)))
   for k in range(N):a=math.tau*k/N;v.append((r*math.cos(a)*sx,cy+r*math.sin(a)*sy,z))
 for j,a in enumerate(rings):
  b=rings[(j+1)%len(rings)]
  if len(a)==len(b)==1:continue
  for k in range(N):
   q=(k+1)%N
   if len(a)==1:f.append((a[0],b[q],b[k]))
   elif len(b)==1:f.append((a[k],a[q],b[0]))
   else:f.append((a[k],a[q],b[q],b[k]))
 me=bpy.data.meshes.new(n);me.from_pydata(v,[],f);me.update();o=bpy.data.objects.new(n,me);bpy.context.collection.objects.link(o);me.materials.append(m)
 bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free()
 for p in me.polygons:p.use_smooth=True
 return o

def parent_parts(parts,loc,axis,angle,n):
 e=bpy.data.objects.new(n,None);bpy.context.collection.objects.link(e);e.location=loc;bpy.context.view_layer.update()
 for o in parts:o.parent=e;o.matrix_parent_inverse=e.matrix_world.inverted()
 e.rotation_mode='XYZ';e.keyframe_insert('rotation_euler',frame=1);e.rotation_euler[axis]=math.radians(angle);e.keyframe_insert('rotation_euler',frame=61);e.keyframe_insert('rotation_euler',frame=91);e.rotation_euler[axis]=0;e.keyframe_insert('rotation_euler',frame=151)
 for fc in e.animation_data.action.fcurves:
  for p in fc.keyframe_points:p.interpolation='LINEAR'
 e['mechanism']='Rigid visual hinge; no electrical, thermal, latch or safety simulation';e['range_degrees']=[0,angle];return e


def ring_box(n,loc,outer,inner,m,b=.002):
 o=box(n,loc,outer,m,b);cut(o,box('ring tool',loc,inner,m,b));return o

def cable(x,y,z,metal,rubber):
 box('Power cable strain relief',(x,y,z),(.018,.026,.018),rubber,.004)
 tube('Unplugged power cable',[(x,y,z),(x+.03,y+.045,z*.7),(x+.025,y+.08,.004),(x-.08,y+.08,.004),(x-.14,y+.05,.004)],.003,rubber)
 box('Power plug',(x-.155,y+.05,.009),(.032,.022,.018),rubber,.003)
 for yy in [y+.044,y+.056]:box('Plug metal blade',(x-.178,yy,.009),(.018,.0016,.008),metal,.0004)


def beam(n,a,b,width,depth,m):
 a,b=Vector(a),Vector(b);o=box(n,(a+b)/2,(width,depth,(b-a).length),m,min(width,depth)*.25);o.rotation_euler=(b-a).to_track_quat('Z','Y').to_euler();return o

def axis_cyl(n,a,b,r,m):
 a,b=Vector(a),Vector(b);o=cyl(n,(a+b)/2,r,(b-a).length,m);o.rotation_euler=(b-a).to_track_quat('Z','Y').to_euler();return o

def axis_pipe(n,a,b,r,m,wall=.002):
 o=axis_cyl(n,a,b,r,m);a,b=Vector(a),Vector(b);v=(b-a).normalized();c=axis_cyl('Bore tool',a-v*.004,b+v*.004,r-wall,m);cut(o,c);return o

def hollow_tube(n,pts,r,m,wall=.002):
 o=tube(n,pts,r,m);bm=bmesh.new();bm.from_mesh(o.data);caps=[f for f in bm.faces if len(f.verts)==3];bmesh.ops.delete(bm,geom=caps,context='FACES');bm.to_mesh(o.data);bm.free();apply(o,'SOLIDIFY',thickness=wall,offset=-1);return o

def torus(n,loc,major,minor,m,normal=(0,0,1),segments=48):
 bpy.ops.mesh.primitive_torus_add(major_segments=segments,minor_segments=8,location=loc,major_radius=major,minor_radius=minor);o=bpy.context.object;o.rotation_euler=Vector(normal).to_track_quat('Z','Y').to_euler();return finish(o,n,m)

def lathe_shape(n,profile,m,rx=.103,ry=.17,cy=0,power=.70):
 N=64;v=[];f=[];rings=[]
 for r,z in profile:
  if r==0:rings.append([len(v)]);v.append((0,cy,z));continue
  rings.append(list(range(len(v),len(v)+N)))
  for k in range(N):
   a=math.tau*k/N;c=math.cos(a);s=math.sin(a);v.append((r*rx*math.copysign(abs(c)**power,c),cy+r*ry*math.copysign(abs(s)**power,s),z))
 for j in range(len(rings)-1):
  a,b=rings[j:j+2]
  for k in range(N):
   q=(k+1)%N
   if len(a)==1:f.append((a[0],b[q],b[k]))
   elif len(b)==1:f.append((a[k],a[q],b[0]))
   else:f.append((a[k],a[q],b[q],b[k]))
 me=bpy.data.meshes.new(n);me.from_pydata(v,[],f);me.update();o=bpy.data.objects.new(n,me);bpy.context.collection.objects.link(o);me.materials.append(m);bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free()
 for p in me.polygons:p.use_smooth=True
 return o


def loft(n,rings,m,N=64,power=1):
 # Each ring is rx, ry, center_y, z; closed cross-section path gives a watertight solid.
 v=[];f=[]
 for rx,ry,cy,z in rings:
  for k in range(N):
   a=math.tau*k/N;c=math.cos(a);s=math.sin(a);pw=1 if rx<.04 else power;v.append((rx*math.copysign(abs(c)**pw,c),cy+ry*math.copysign(abs(s)**pw,s),z))
 for j in range(len(rings)):
  for k in range(N):q=(k+1)%N;b=(j+1)%len(rings);f.append((j*N+k,j*N+q,b*N+q,b*N+k))
 me=bpy.data.meshes.new(n);me.from_pydata(v,[],f);me.update();o=bpy.data.objects.new(n,me);bpy.context.collection.objects.link(o);me.materials.append(m)
 bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free()
 for p in me.polygons:p.use_smooth=True
 o['organic_surface']=True;return o

def hinge(parts,n,y,z,angle,t0,t1):
 e=bpy.data.objects.new(n,None);bpy.context.collection.objects.link(e);e.location=(0,y,z);bpy.context.view_layer.update()
 for o in parts:o.parent=e;o.matrix_parent_inverse=e.matrix_world.inverted()
 for frame,a in [(1,0),(t0,0),(t1,-angle),(91,-angle),(151,0)]:e.rotation_euler.x=math.radians(a);e.keyframe_insert('rotation_euler',frame=frame)
 for fc in e.animation_data.action.fcurves:
  for p in fc.keyframe_points:p.interpolation='LINEAR'
 e['range_degrees']=[0,angle];return e

def swept_pipe(n,pts,r,wall,m):
 # Analytic planar centerline, parallel frame; no auto-Bezier overshoot or solidify corners.
 N=32;v=[];f=[]
 for i,p in enumerate(pts):
  p=Vector(p);a=Vector(pts[max(0,i-1)]);b=Vector(pts[min(len(pts)-1,i+1)]);t=(b-a).normalized();u=Vector((1,0,0));w=t.cross(u).normalized()
  for rad in [r,r-wall]:
   for k in range(N):v.append(tuple(p+rad*(u*math.cos(k*math.tau/N)+w*math.sin(k*math.tau/N))))
 for i in range(len(pts)-1):
  for layer in range(2):
   for k in range(N):q=(k+1)%N;a=i*N*2+layer*N;b=(i+1)*N*2+layer*N;f.append((a+k,a+q,b+q,b+k))
 for i in [0,len(pts)-1]:
  for k in range(N):q=(k+1)%N;a=i*N*2;f.append((a+k,a+N+k,a+N+q,a+q))
 me=bpy.data.meshes.new(n);me.from_pydata(v,[],f);me.update();o=bpy.data.objects.new(n,me);bpy.context.collection.objects.link(o);me.materials.append(m)
 bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free()
 for q in me.polygons:q.use_smooth=True
 o['organic_surface']=True;return o

def solid_pipe_tool(pts,r,m):
 o=swept_pipe('Drain clearance tool',pts,r,r*.5,m);src=o.data;N=32;v=[tuple(src.vertices[i*64+k].co) for i in range(len(pts)) for k in range(N)];f=[]
 for i in range(len(pts)-1):
  for k in range(N):q=(k+1)%N;f.append((i*N+k,i*N+q,(i+1)*N+q,(i+1)*N+k))
 f.append(tuple(range(N-1,-1,-1)));f.append(tuple((len(pts)-1)*N+k for k in range(N)))
 me=bpy.data.meshes.new('Drain clearance solid');me.from_pydata(v,[],f);me.update();o.data=me
 bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();return o

def toilet():
 ceramic=mat('Warm white glazed ceramic',(.84,.825,.79),0,.24);seat=mat('Ivory molded seat',(.81,.80,.765),0,.32);chrome=mat('Satin chrome',(.58,.62,.64),.85,.23);rubber=mat('Seat bumper rubber',(.42,.43,.41),0,.73);dark=mat('Shadowed connection',(.075,.08,.075),0,.7)
 # Sculpted skirt supports bowl, with an open underside and rear drain zone.
 loft('Ceramic floor skirt',[(.125,.23,-.11,.0),(.13,.235,-.11,.012),(.126,.228,-.11,.030),(.106,.19,-.10,.12),(.097,.165,-.09,.23),(.118,.18,-.11,.29),(.10,.16,-.11,.29),(.079,.145,-.09,.23),(.089,.171,-.10,.12),(.109,.207,-.11,.018),(.109,.207,-.11,.0)],ceramic,power=.85)
 # Continuous ceramic bowl from outer drain neck, to rim, and back down true hollow interior.
 loft('Continuous hollow ceramic bowl',[(.040,.045,-.13,.215),(.080,.13,-.17,.24),(.137,.215,-.195,.29),(.169,.263,-.20,.36),(.1775,.28,-.20,.398),(.1775,.28,-.20,.408),(.172,.275,-.20,.414),(.151,.2232,-.222,.414),(.146,.2178,-.222,.402),(.143,.2133,-.222,.38),(.119,.1746,-.212,.32),(.075,.125,-.17,.27),(.028,.033,-.13,.238),(.028,.033,-.13,.215)],ceramic)
 # Lower hollow trap and floor socket, partially protected by skirt.
 pts=[(0,-.13,.22)]+[(0,-.07+.06*math.cos(a),.18+.06*math.sin(a)) for a in [math.pi+i*math.pi/24 for i in range(25)]]+[(0,.055+.065*math.cos(a),.18+.065*math.sin(a)) for a in [math.pi-i*math.pi/24 for i in range(1,25)]]+[(0,.12,.045)]
 swept_pipe('Simplified connected ceramic trap',pts,.039,.009,ceramic)
 cut(bpy.data.objects['Ceramic floor skirt'],box('Rear trap service opening',(0,.16,.15),(.13,.26,.34),ceramic,.006))
 axis_pipe('Floor drain outlet',(0,.12,.006),(0,.12,.072),.052,ceramic,.012)
 box('Rear ceramic tank deck',(0,.132,.384),(.31,.216,.052),ceramic,.025)
 for x in [-.084,.084]:cyl('Floor fastening cap',(x,.08,.032),.017,.014,ceramic)
 # Distinct tank seated on rubber and ceramic deck. Fully modelled shell, not filled block.
 box('Tank seating gasket',(0,.147,.416),(.16,.09,.012),rubber,.008)
 tank=box('Hollow cistern',(0,.157,.58),(.405,.166,.322),ceramic,.028)
 cut(tank,box('Cistern inner cavity',(0,.157,.62),(.367,.128,.35),ceramic,.018))
 box('Cistern cover',(0,.157,.752),(.436,.178,.028),ceramic,.014)
 cyl('Flush lever spindle',(-.204,.118,.685),.012,.018,chrome,'X');box('Flush lever',(-.218,.089,.685),(.015,.065,.014),chrome,.006)
 # Tank supply and wall stop: endpoints at rear installation plane y=.246.
 axis_cyl('Tank inlet shank',(-.13,.157,.414),(-.13,.157,.382),.009,chrome)
 tube('Flexible supply line',[(-.13,.157,.385),(-.15,.20,.30),(-.17,.225,.20)],.006,chrome)
 cyl('Wall supply escutcheon',(-.17,.244,.20),.026,.004,chrome,'Y');axis_cyl('Supply stop body',(-.17,.244,.20),(-.17,.213,.20),.012,chrome);axis_cyl('Supply stop spindle',(-.17,.215,.20),(-.17,.205,.20),.005,chrome);cyl('Supply stop wheel',(-.17,.207,.20),.018,.006,chrome,'Y')
 # Separate coaxial seat/lid hinge stations and rigid carriers.
 for x in [-.07,.07]:
  cyl('Hinge mounting foot',(x,.006,.421),.016,.014,chrome);cyl('Fixed hinge pin',(x,.01,.44),.004,.056,chrome,'X');box('Hinge pedestal',(x,.006,.432),(.010,.023,.025),seat,.004)
 parts=[]
 parts.append(loft('Raised ring seat',[(rx,ry*.89,-.231,z) for rx,ry,cy,z in [( .171,.263,0,.43),(.177,.269,0,.438),(.176,.268,0,.450),(.169,.261,0,.457),(.119,.206,0,.457),(.112,.199,0,.449),(.113,.20,0,.437),(.120,.207,0,.43)]],seat))
 for x in [-.07,.07]:
  parts.append(cyl('Seat hinge barrel',(x-math.copysign(.017,x),.01,.44),.010,.016,seat,'X'));parts.append(box('Seat hinge arm',(x-math.copysign(.017,x),-.019,.441),(.017,.064,.018),seat,.005))
 for x in [-.15,.15]:
  for y in [-.31,-.14]:parts.append(box('Seat support bumper',(x if y==-.31 else math.copysign(.152,x),y,.422),(.016 if y==-.31 else .010,.020,.016),rubber,.003))
 hinge(parts,'Seat hinge 82 degrees',.01,.44,82,31,61)
 lid=[]
 # Thin convex slab with tiny center disk topology hidden on broad continuous surface.
 lid.append(lathe_shape('Seat lid',[(0,.474),(.45,.474),(.78,.471),(.97,.466),(1,.460),(1,.454),(.97,.451),(.78,.457),(.45,.461),(0,.461)],seat,rx=.18,ry=.239,cy=-.23,power=1))
 for x in [-.07,.07]:
  lid.append(cyl('Lid hinge barrel',(x+math.copysign(.017,x),.01,.44),.009,.016,seat,'X'));lid.append(box('Lid hinge arm',(x+math.copysign(.017,x),-.018,.459),(.018,.063,.014),seat,.004));lid.append(box('Lid support bumper',(x*13/7,-.32,.465),(.02,.028,.023),rubber,.003))
 for o in lid:
  if not o.name.startswith('Lid hinge barrel'):o.location.z+=(.0035 if o.name.startswith('Lid support bumper') else .016)
 for x in [-.07,.07]:lid.append(beam('Lid hinge rising connector',(x+math.copysign(.017,x),.01,.44),(x+math.copysign(.017,x),-.018,.475),.010,.010,seat))
 hinge(lid,'Lid hinge 88 degrees',.01,.44,88,1,31)
 return {'reference_dimensions_m':[.436,.720,.766],'description':'タンク付き洋式便器。丸みのある陶器、独立開閉する便座と蓋、給水栓と排水接続。','mechanism':'Independent lid 0–88° frames1–31 and seat0–82° frames31–61. Reverse closure frames91–151 is visual only; full sweep checked. No fluid simulation.','references':['https://www.totousa.com/filemanager_uploads/product_assets/SpecSheet/SS-02049_CST776CEF(R)(G).pdf']}

def sink():
 ceramic=mat('Warm white basin ceramic',(.84,.825,.79),0,.24);chrome=mat('Satin chrome fittings',(.58,.62,.64),.88,.22);dark=mat('Dark inner aerator',(.045,.05,.05),0,.65);rubber=mat('Connection rubber',(.12,.13,.12),0,.7)
 # Rectangular continuous rim and smoothly tapering bowl with true drain bore.
 loft('Hollow ceramic basin',[(.023,.023,-.02,.712),(.08,.075,-.02,.725),(.18,.14,-.018,.765),(.277,.228,0,.846),(.300,.254,0,.867),(.304,.2595,0,.887),(.300,.256,0,.895),(.230,.185,-.025,.895),(.210,.155,-.03,.878),(.195,.142,-.03,.850),(.150,.108,-.03,.805),(.085,.060,-.025,.785),(.022,.022,-.02,.777),(.022,.022,-.02,.712)],ceramic,power=.50)
 ref=bpy.data.objects['Hollow ceramic basin'].data.copy();ref.name='Uncut basin shading reference';ref.use_fake_user=True
 # Rear deck is integrated into basin perimeter by concealed overlap.
 deck=box('Faucet mounting deck',(0,.201,.879),(.43,.105,.031),ceramic,.012)
 cut(deck,cyl('Faucet drilled mount',(0,.197,.88),.0175,.08,ceramic))
 # Open-backed flared pedestal. Back service cut is below sink attachment.
 ped=loft('Pedestal open back',[(.113,.108,0,0),(.119,.113,0,.014),(.10,.102,0,.06),(.082,.082,0,.20),(.077,.075,0,.64),(.095,.09,0,.708),(.11,.10,0,.724),(.088,.078,0,.724),(.06,.052,0,.64),(.06,.06,0,.20),(.082,.084,0,.055),(.094,.087,0,0)],ceramic,power=.60)
 cut(ped,box('Pedestal rear service opening',(0,.125,.40),(.135,.17,.79),ceramic,.004))
 # Basin supported on curved pedestal crown; two hidden wall brackets at wall plane.
 for x in [-.22,.22]:
  box('Wall fixing bracket',(x,.247,.84),(.035,.020,.07),chrome,.003);cyl('Wall fixing screw',(x,.258,.84),.005,.008,chrome,'Y')
 # Real drain annulus and visible inset perforated strainer.
 axis_pipe('Drain flange',(0,-.02,.774),(0,-.02,.785),.029,chrome,.010)
 axis_pipe('Drain tailpiece',(0,-.02,.61),(0,-.02,.779),.020,chrome,.003)
 for x in [-.010,0,.010]:box('Drain strainer bar',(x,-.02,.775),(.003,2*math.sqrt(.020**2-x*x),.003),chrome,.0007)
 pts=[(0,-.02,.62)]+[(0,.025+.045*math.cos(a),.57+.045*math.sin(a)) for a in [math.pi+i*math.pi/24 for i in range(25)]]+[(0,.07,.585)]+[(0,.10+.03*math.cos(a),.585+.03*math.sin(a)) for a in [math.pi-i*math.pi/48 for i in range(1,25)]]+[(0,.259,.615)]
 swept_pipe('P trap return',pts,.020,.003,chrome)
 for y,z,axis in [(-.02,.65,'Z'),(.14,.615,'Y')]:
  o=cyl('Trap union nut',(0,y,z),.025,.025,chrome,axis);cut(o,cyl('Union bore',(0,y,z),.0195,.05,chrome,axis))
 axis_pipe('Waste wall escutcheon',(0,.255,.615),(0,.260,.615),.037,chrome,.017)
 # Overflow is a small separate pierced planar insert on inner rear slope.
 cut(bpy.data.objects['Hollow ceramic basin'],axis_cyl('Overflow bore',(0,.10,.87),(0,.175,.839),.009,ceramic))
 ov=axis_pipe('Overflow opening',(0,.114,.864),(0,.17,.841),.010,chrome,.002)
 pts=[(0,.17,.841),(0,.18,.80)]+[(0,.12+.06*math.cos(a),.80+.06*math.sin(a)) for a in [-i*math.pi/48 for i in range(1,25)]]+[(0,.001,.74)]
 swept_pipe('Overflow return passage',pts,.010,.003,ceramic)
 cut(bpy.data.objects['Hollow ceramic basin'],solid_pipe_tool(pts,.011,ceramic))
 cut(bpy.data.objects['Drain tailpiece'],axis_cyl('Overflow tailpiece inlet',(0,.015,.74),(0,-.025,.74),.007,ceramic))
 # Faucet single lever body, swept spout, downward real aerator mouth.
 cyl('Faucet base',(0,.197,.900),.029,.012,chrome)
 cyl('Faucet shank',(0,.197,.872),.015,.060,chrome)
 cyl('Mixer body',(0,.197,.960),.022,.115,chrome)
 pts=[(0,.197,.99)]+[(0,.131+.066*math.cos(a),1.025+.066*math.sin(a)) for a in [i*math.pi/32 for i in range(33)]]+[(0,.065,1.014)]
 swept_pipe('Curved faucet spout',pts,.015,.003,chrome)
 axis_pipe('Spout aerator outlet',(0,.065,1.008),(0,.065,1.025),.016,chrome,.003)
 axis_pipe('Aerator internal sleeve',(0,.065,1.009),(0,.065,1.020),.012,dark,.002)
 axis_cyl('Mixer lever pivot',(.015,.197,.97),(.038,.197,.97),.009,chrome)
 box('Single mixer lever',(.038,.197,1.002),(.009,.018,.075),chrome,.004)
 for x in [-.055,.055]:
  tube('Hot cold flexible feed',[(x/4,.197,.87),(x,.17,.73),(x,.20,.60)],.006,chrome)
  axis_cyl('Hot cold stop', (x,.20,.60),(x,.258,.60),.010,chrome);cyl('Supply wall escutcheon',(x,.258,.60),.022,.004,chrome,'Y');cyl('Supply shutoff knob',(x,.194,.60),.014,.006,chrome,'Y')
 return {'reference_dimensions_m':[.608,.519,.895],'description':'独立脚の陶器洗面台。厚い縁と鉢、金属蛇口、排水口、背面の給排水管。','mechanism':'Static editable plumbing. Rear wall mounting plane y=.2595m; wall not supplied. Pedestal supports basin; brackets require wall. Fluid simulation excluded.','references':['https://resources.kohler.com/webassets/kpna/catalog/pdf/en/K-2359-1_spec_US-CA_Kohler_en.pdf']}
def save(slug,fn):
 bpy.ops.wm.read_factory_settings(use_empty=True);bpy.context.preferences.filepaths.save_version=0;detail=fn();sc=bpy.context.scene;sc.frame_end=151;sc.frame_set(1);sc.unit_settings.system='METRIC'
 for o in sc.objects:
  if o.type!='MESH':continue
  o['assembly_role']='moving' if o.parent else 'fixed';o['attachment_note']='Positive concealed seating; no exposed coplanar layers.'
  bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-8);bmesh.ops.dissolve_degenerate(bm,edges=list(bm.edges),dist=1e-8);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free()
  bpy.context.view_layer.objects.active=o
  if o.data.has_custom_normals:bpy.ops.mesh.customdata_custom_splitnormals_clear()
  bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.uv.smart_project(island_margin=.02);bpy.ops.object.mode_set(mode='OBJECT')
  for p in o.data.polygons:p.use_smooth=True
  # Weighted bevel normals then exact normals for broad axis-aligned planes.
  if not o.get('organic_surface',False) and not any(k in o.name for k in ['Seat lid','trap','spout','supply','feed']):
   apply(o,'WEIGHTED_NORMAL',keep_sharp=True,weight=50);normals=[tuple(n.vector) for n in o.data.corner_normals]
   for face in o.data.polygons:
    if max(abs(c) for c in face.normal)>.99999:
     for i in face.loop_indices:normals[i]=tuple(face.normal)
   o.data.normals_split_custom_set(normals)
  if o.name=='Hollow ceramic basin':
   from mathutils.bvhtree import BVHTree
   from mathutils.geometry import barycentric_transform
   ref=bpy.data.meshes['Uncut basin shading reference'];ref.calc_loop_triangles();triangles=[tuple(t.vertices) for t in ref.loop_triangles];vertices=[v.co.copy() for v in ref.vertices];vn=[v.normal.copy() for v in ref.vertices];tree=BVHTree.FromPolygons(vertices,triangles,all_triangles=True);normals=[tuple(n.vector) for n in o.data.corner_normals]
   for face in o.data.polygons:
    hit,normal,idx,dist=tree.find_nearest(face.center)
    if idx is None or dist>.001 or normal.dot(face.normal)<.8:continue
    for li in face.loop_indices:
     co=o.data.vertices[o.data.loops[li].vertex_index].co;hit,normal,idx,dist=tree.find_nearest(co)
     if dist>.001:continue
     a,b,c=triangles[idx];n=barycentric_transform(hit,vertices[a],vertices[b],vertices[c],vn[a],vn[b],vn[c]).normalized();normals[li]=tuple(n)
   o.data.normals_split_custom_set(normals)
  if o.name=='Continuous hollow ceramic bowl':
   normals=[tuple(n.vector) for n in o.data.corner_normals]
   for face in o.data.polygons:
    if face.normal.z>.99999 and all(abs(o.data.vertices[i].co.z-.414)<1e-6 for i in face.vertices):
     for i in face.loop_indices:normals[i]=tuple(face.normal)
   o.data.normals_split_custom_set(normals)
 bpy.ops.object.select_all(action='SELECT');out=R/'assets'/slug;out.mkdir(parents=True,exist_ok=True);blend=out/(slug+'.blend');glb=out/(slug+'.glb');bpy.ops.wm.save_as_mainfile(filepath=str(blend),compress=True);bpy.ops.export_scene.gltf(filepath=str(glb),export_format='GLB',export_yup=True,export_animations=True,export_animation_mode='ACTIVE_ACTIONS',export_extras=True)
 obs=[o for o in sc.objects if o.type=='MESH'];vs=[o.matrix_world@v.co for o in obs for v in o.data.vertices];lo=[min(v[i] for v in vs) for i in range(3)];hi=[max(v[i] for v in vs) for i in range(3)];tris=0
 for o in obs:o.data.calc_loop_triangles();tris+=len(o.data.loop_triangles)
 detail.update(id=slug,title_ja={'toilet':'トイレ','washbasin':'洗面台'}[slug],revision=(10 if slug=='toilet' else 8),dimensions_m=[hi[i]-lo[i] for i in range(3)],triangles=tris,units='meter',up_axis_blend='Z',up_axis_glb='Y',review_status='Independent saved geometry and cheap view gate pending',photography_status='Not authorized',files={p.suffix[1:]:{'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in [blend,glb]})
 (out/'metadata.json').write_text(json.dumps(detail,ensure_ascii=False,indent=2)+'\n');print('ASSET_DONE',slug,tris,flush=True)

if __name__=='__main__':
 args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
 for slug,fn in [('toilet',toilet),('washbasin',sink)]:
  if not args or slug in args:save(slug,fn)
