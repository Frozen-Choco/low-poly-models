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
def materials():
 global STEEL,COAT,BLUE,RESIN
 STEEL=mat('Brushed stainless steel',(.57,.59,.61),.27,1);COAT=mat('Dark nonstick cooking surface',(.032,.038,.039),.64);BLUE=mat('Midnight painted aluminium exterior',(.018,.027,.042),.37);RESIN=mat('Black phenolic resin grip',(.018,.020,.023),.42)
def pan():
 profile=[(0,.001),(.092,.001),(.100,.0018),(.106,.004),(.112,.010),(.118,.021),(.125,.039),(.1325,.0535),(.1325,.0545),(.1318,.055),(.1305,.0545),(.130,.0535),(.123,.039),(.116,.022),(.110,.012),(.104,.007),(.098,.005),(0,.005)]
 lathe('Pan continuous bowl wall and floor',profile,[BLUE,COAT,STEEL],[0]*8+[2]*3+[1]*6)
 cyl('Bonded induction base',(0,0,.0006),.091,.0012,STEEL)
 # Three wall rivets enter a single exterior bracket, below the lip.
 sector('Pan handle mounting bracket',[(.1185,.024),(.1298,.048),(.1335,.048),(.1222,.024)],.18,STEEL)
 for y,z in [(-.014,.041),(.014,.041),(0,.028)]:
  inner_r=.123+(z-.039)*(.007/.0145) if z>.039 else .116+(z-.022)*(.007/.017)
  x=math.sqrt(inner_r**2-y*y)
  cyl('Pan concealed rivet shaft '+str(y),(x+.0035,y,z),.0022,.006,STEEL,'X')
  bpy.ops.mesh.primitive_uv_sphere_add(segments=24,ring_count=12,radius=1,location=(x+.0002,y,z));head=bpy.context.object;head.scale=(.001,.0035,.0035);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);finish(head,'Pan shallow coated rivet head '+str(y),COAT);mod(head,'TRIANGULATE',quad_method='FIXED',ngon_method='CLIP')
 box('Pan handle welded receiver boss',(.137,0,.039),(.018,.022,.016),STEEL,.002)
 neck=box('Pan handle steel tang',(.159,0,.044),(.052,.023,.017),STEEL,.003);neck.rotation_euler.y=-.13
 handle=box('Pan phenolic handle',(.240,0,.061),(.155,.032,.026),RESIN,.010);handle.rotation_euler.y=-.12
 bpy.context.view_layer.update()
 hole=cyl('Temporary hanging hole',(.299,0,.068),.006,.070,RESIN);cut(handle,hole);mod(handle,'WEIGHTED_NORMAL',keep_sharp=True)
 cyl('Pan handle underside screw',(.176,0,.0405),.0038,.004,STEEL)
 return {'description':'浅い有底のフライパン。ノンスティック内面、金属底、リベット留めの柄と吊り穴。','reference_dimensions_m':[.45,.265,.08],'mechanism':'Static editable bowl, induction plate, rivets, tang and phenolic grip. No cooking or heat simulation.'}
def pot():
 profile=[(0,0),(.075,0),(.085,.001),(.093,.004),(.098,.010),(.101,.019),(.102,.031),(.102,.092),(.103,.096),(.103,.098),(.1025,.099),(.101,.099),(.100,.098),(.100,.096),(.100,.032),(.099,.020),(.096,.012),(.091,.007),(.083,.004),(0,.003)]
 lathe('Pot continuous three-layer steel exterior',profile,[STEEL])
 for sign in [-1,1]:
  for y in [-.027,.027]:
   box('Pot handle welded mounting seat '+str((sign,y)),(sign*.108,y,.078),(.020,.018,.025),STEEL,.004)
   cyl('Pot handle fixing screw '+str((sign,y)),(sign*.115,y,.077),.0035,.014,STEEL,'X')
  pts=[]
  for i in range(25):
   a=-math.pi/2+math.pi*i/24;pts.append((sign*(.111+.029*math.cos(a)),.027*math.sin(a),.084+.005*math.cos(a)))
  tube('Pot open phenolic loop handle '+str(sign),pts,.008,.009,RESIN)
 # Flanged lid with downward locating skirt fits inside mouth, removable upward.
 lidprof=[(0,.121),(.020,.1205),(.045,.118),(.070,.113),(.091,.105),(.098,.105),(.1015,.101),(.103,.1005),(.103,.099),(.1005,.099),(.099,.099),(.099,.094),(.0975,.094),(.0975,.100),(.098,.103),(.090,.103),(.069,.111),(.044,.116),(.020,.1185),(0,.119)]
 lid=lathe('Lid removable steel dome and locating skirt',lidprof,[STEEL])
 for x in [-.006,.006]:
  cutter=cyl('Temporary lid steam vent',(x,-.094,.104),.0012,.015,STEEL);cut(lid,cutter)
 mod(lid,'WEIGHTED_NORMAL',keep_sharp=True)
 lathe('Lid phenolic graspable knob',[(0,.121),(.016,.121),(.018,.123),(.017,.127),(.012,.130),(.012,.140),(.020,.145),(.023,.150),(.023,.156),(.021,.161),(.015,.165),(0,.167)],[RESIN])
 cyl('Lid knob metal seating washer',(0,0,.121),.017,.001,STEEL)
 cyl('Lid knob underside fixing screw',(0,0,.1185),.004,.003,STEEL)
 return {'description':'両手取っ手のステンレス鍋。丸み底、有底の内槽、外せる金属蓋とつまみ。','reference_dimensions_m':[.295,.206,.170],'mechanism':'Static separately editable pot, loop handles, fasteners, removable lid and knob. Full-clad reference steel represented as solid visible shell, internal lamination not modeled; no thermal certification.'}
def save(slug,fn):
 bpy.ops.wm.read_factory_settings(use_empty=True);bpy.context.preferences.filepaths.save_version=0;materials();meta=fn();sc=bpy.context.scene;sc.unit_settings.system='METRIC';sc.render.threads_mode='FIXED';sc.render.threads=2
 for o in list(sc.objects):
  if o.type!='MESH':continue
  bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free()
  o['assembly_role']='removable_lid' if o.name.startswith('Lid') else 'fixed';o['attachment_note']='Concealed positive engagement at fasteners and handles; lid skirt clear of pot inner wall.'
  bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o;bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.uv.smart_project(island_margin=.01);bpy.ops.object.mode_set(mode='OBJECT')
 bpy.ops.object.select_all(action='SELECT');out=R/'assets'/slug;out.mkdir(parents=True,exist_ok=True);blend=out/(slug+'.blend');glb=out/(slug+'.glb');bpy.ops.wm.save_as_mainfile(filepath=str(blend),compress=True);bpy.ops.export_scene.gltf(filepath=str(glb),export_format='GLB',export_yup=True,export_animations=False,export_extras=True)
 obs=[o for o in sc.objects if o.type=='MESH'];vs=[o.matrix_world@v.co for o in obs for v in o.data.vertices];lo=[min(v[i] for v in vs) for i in range(3)];hi=[max(v[i] for v in vs) for i in range(3)];tris=0
 for o in obs:o.data.calc_loop_triangles();tris+=len(o.data.loop_triangles)
 meta.update(id=slug,title_ja={'frying_pan':'フライパン','cooking_pot':'鍋'}[slug],revision=(6 if slug=='frying_pan' else 3),dimensions_m=[hi[i]-lo[i] for i in range(3)],triangles=tris,units='meter',up_axis_blend='Z',up_axis_glb='Y',review_status='Pending independent geometry gate',photography_status='Not authorized',files={p.suffix[1:]:{'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in [blend,glb]});(out/'metadata.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n');print('ASSET_DONE',slug,tris,flush=True)
if __name__=='__main__':
 args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
 for slug,fn in [('frying_pan',pan),('cooking_pot',pot)]:
  if not args or slug in args:save(slug,fn)
