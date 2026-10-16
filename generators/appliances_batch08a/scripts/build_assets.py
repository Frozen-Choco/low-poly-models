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
 bpy.ops.mesh.primitive_cylinder_add(vertices=64,radius=r,depth=depth,location=loc);o=bpy.context.object
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

def microwave():
 white=mat('Warm white powder-coated steel',(.77,.765,.735),0,.32);black=mat('Graphite molded polymer',(.027,.032,.036),0,.34);steel=mat('Satin cavity steel',(.48,.51,.53),.9,.32);glass=mat('Dark smoked door window',(.014,.022,.027),0,.16);rubber=mat('Black rubber',(.017,.019,.021),0,.75);lcd=mat('Unlit LCD',(.12,.17,.15),0,.33)
 body=box('Case with open front cavity', (0,0,.163),(.488,.36,.27),white,.005)
 cut(body,box('cavity tool',(-.043,-.025,.164),(.35,.36,.218),white,.004))
 # Continuous thin visible metal cavity liner, open front.
 body.data.materials.append(steel)
 # Inner faces receive cavity metal; same connected boundary, no floating liner.
 for face in body.data.polygons:
  center=body.matrix_world@face.center
  if -.221<center.x<.134 and -.181<center.y<.156 and .054<center.z<.274:face.material_index=1
 box('Flat ceramic cavity floor',(-.043,-.012,.056),(.330,.321,.003),mat('Ivory ceramic base',(.65,.65,.61),0,.4),.001)
 for x in [-.19,.19]:
  for y in [-.13,.13]:cyl('Anti-slip foot',(x,y,.014),.013,.028,rubber)
 # Rear ventilation openings through case wall; internal equipment cavity intentionally opaque behind them.
 for i in range(10):cut(body,box('vent tool',(.16,.176,.105+i*.012),(.07,.025,.005),black,.001))
 box('Recessed rear ventilation baffle',(.16,.168,.16),(.078,.002,.13),black,.001)
 fascia=box('Control fascia',(.188,-.182,.164),(.102,.008,.252),black,.003)
 box('LCD bezel',(.188,-.187,.239),(.076,.004,.036),rubber,.002);box('Unlit display',(.188,-.1894,.239),(.065,.001,.025),lcd,.001)
 for row in range(4):
  for col in range(2):box('Inset control key',(.169+.038*col,-.188,.188-row*.027),(.029,.004,.017),white,.002)
 cyl('Start dial',(.188,-.192,.066),.016,.013,white,'Y')
 # Side-hinged door. Body front is -0.180; rear of door is -0.188, leaving 8mm sweep clearance.
 parts=[];door=box('Door surround',(-.049,-.200,.164),(.382,.024,.258),black,.004);cut(door,box('window tool',(-.066,-.20,.169),(.282,.05,.174),black,.003));parts.append(door)
 parts.append(box('Smoked window sealed panel',(-.066,-.20,.169),(.284,.006,.176),glass,.003))
 for z in [.095,.231]:parts.append(box('Handle foot',(.104,-.2255,z),(.018,.034,.016),white,.003))
 parts.append(box('Vertical door pull',(.104,-.2445,.163),(.019,.015,.154),white,.006))
 # Two slim closure tongues and swept-clear receiver recesses, visual latch only.
 for z in [.090,.236]:
  cut(body,box('Latch receiver tool',(.136,-.179,z),(.016,.026,.014),black,.001));cut(fascia,box('Fascia receiver tool',(.136,-.179,z),(.019,.027,.017),black,.001))
  parts.append(box('Door closure tongue',(.136,-.188,z),(.007,.016,.006),black,.001))
 # Two coaxial knuckle stations; fixed mount reaches case, moving mount reaches door.
 for z in [.070,.256]:
  cyl('Door hinge axle',(-.250,-.198,z+.0065),.002,.028,steel)
  cyl('Fixed hinge barrel',(-.250,-.198,z),.005,.012,steel)
  parts.append(cyl('Moving hinge barrel',(-.250,-.198,z+.013),.005,.012,steel))
  box('Fixed hinge leaf',(-.245,-.184,z),(.010,.028,.008),steel,.001)
  parts.append(box('Moving hinge leaf',(-.240,-.200,z+.013),(.034,.007,.008),steel,.001))
 parent_parts(parts,(-.250,-.198,0),2,-90,'Door hinge open close')
 box('Cord strain relief',(.190,.182,.055),(.015,.016,.014),rubber,.003)
 tube('Power cable',[(.19,.188,.055),(.22,.22,.035),(.19,.25,.004),(.11,.25,.004),(.066,.23,.004)],.003,rubber)
 box('Unplugged power plug',(.055,.23,.008),(.026,.017,.016),rubber,.003)
 for y in [.224,.236]:box('Plug blade',(.037,y,.008),(.013,.0015,.006),steel,.0003)
 return {'reference_dimensions_m':[.488,.380,.298],'modeled_case_dimensions_m':[.488,.360,.270],'modeled_cavity_dimensions_m':[.350,.335,.218],'mechanism':'Door rotates 0–90 degrees about left vertical hinge, animation frames1–151. Controls static. Opaque smoked window; complete open cavity. Cord rests on ground, unplugged.','references':['https://panasonic.jp/range/products/NE-FL1C/spec.html'],'description':'汎用の単機能電子レンジ。白い塗装鋼板、濃色の樹脂ドアと窓、金属庫内、フラットな底面。開閉する左ヒンジドア。'}

def cooker():
 ivory=mat('Satin warm ivory polymer',(.74,.72,.66),0,.32);black=mat('Charcoal heat-resistant polymer',(.026,.03,.032),0,.4);metal=mat('Brushed inner lid aluminum',(.6,.62,.63),.9,.33);pan=mat('Dark satin inner pot coating',(.045,.048,.05),0,.48);rubber=mat('Silicone gasket and feet',(.05,.052,.052),0,.72);lcd=mat('Unlit LCD gray green',(.17,.2,.17),0,.35)
 # Elliptical vessel outer walls and inset rim; no solid cap across opening.
 shell('Hollow cooker housing',[(0,.017),(.084,.017),(.108,.027),(.1175,.055),(.1175,.135),(.111,.157),(.103,.161),(.100,.154),(.107,.132),(.107,.050),(.08,.032),(0,.032)],ivory,1,1.28)
 shell('Dark inner cavity liner',[(0,.033),(.075,.033),(.098,.050),(.100,.151),(.097,.155),(.094,.150),(.092,.055),(.073,.039),(0,.039)],black,1,1.1)
 shell('Removable inner cooking pot',[(0,.045),(.065,.045),(.086,.06),(.091,.148),(.093,.161),(.089,.163),(.087,.150),(.082,.063),(.062,.050),(0,.050)],pan,1,1.1)
 cyl('Pot heater support seat',(0,0,.038),.065,.016,metal,scale=(1,1.1))
 # Flat feet share plane and are buried positively into floor, not floating.
 for x in [-.066,.066]:
  for y in [-.083,.083]:cyl('Rubber support foot',(x,y,.015),.011,.030,rubber)
 # Control cluster placed on integral front housing ledge outside inner opening.
 box('Front controls housing',(0,-.145,.138),(.12,.055,.036),ivory,.009)
 box('Control inset',(0,-.149,.157),(.105,.037,.003),black,.006)
 box('LCD window',(0,-.149,.159),(.045,.018,.001),lcd,.002)
 for x in [-.040,.040]:box('Control button',(x,-.149,.160),(.015,.021,.003),ivory,.003)
 # Back hinge is outside ellipse; axis beyond rear body. Lid underside entirely above rim in closed pose.
 parts=[]
 parts.append(shell('Lid shell',[(0,.193),(.07,.193),(.101,.188),(.114,.176),(.115,.166),(.109,.163),(0,.163)],ivory,1,1.24))
 parts.append(shell('Lid sealing gasket',[(.089,.162),(.094,.162),(.095,.164),(.094,.166),(.089,.166)],rubber,1,1.1))
 plate=cyl('Inner lid plate',(0,0,.1634),.087,.0015,metal,scale=(1,1.1));parts.append(plate)
 # Steam vent is actual through lid with recessed black tube. Lid mesh cut only, separate tube bore.
 vent=parts[0];cut(vent,cyl('steam vent tool',(0,.072,.184),.009,.06,black));cut(plate,cyl('inner steam bore tool',(0,.072,.162),.009,.02,black))
 parts.append(shell('Steam vent lining',[(.0092,.161),(.0092,.187),(.007,.187),(.007,.161)],black,cy=.072))
 parts.append(box('Release button',(0,-.112,.191),(.038,.025,.010),black,.004))
 for x in [-.038,.038]:
  cyl('Fixed hinge barrel',(x,.151,.169),.008,.025,black,'X')
  box('Rear hinge fixed bracket',(x,.151,.145),(.021,.036,.026),ivory,.003)
  box('Rear hinge bracket neck',(x,.157,.160),(.021,.010,.018),ivory,.002)
 cyl('Lid hinge axle',(0,.151,.169),.003,.105,metal,'X')
 parts.append(cyl('Moving center hinge',(0,.151,.169),.008,.048,black,'X'))
 parts.append(box('Lid hinge bridge',(0,.136,.172),(.046,.034,.012),ivory,.003))
 parent_parts(parts,(0,.151,.169),0,-100,'Lid hinge open close')
 box('Rear cord relief',(.066,.127,.045),(.013,.028,.012),rubber,.003)
 tube('Power cable',[(.066,.139,.045),(.105,.18,.025),(.105,.205,.003),(.04,.215,.003),(0,.195,.003)],.0025,rubber)
 box('Unplugged power plug',(-.012,.195,.008),(.025,.017,.016),rubber,.003)
 for y in [.189,.201]:box('Plug blade',(-.030,y,.008),(.013,.0015,.006),metal,.0003)
 return {'reference_dimensions_m':[.235,.325,.195],'modeled_body_envelope_m':[.235,.3415,.196],'mechanism':'Rear lid rotates 0–100 degrees, frames1–151; removable pot is separate editable mesh but no extraction animation. Steam bore and visible inner lid provided; no thermal, electrical, pressure or latch simulation.','references':['https://www.zojirushi.co.jp/syohin/rice/ricecooker/nl-bx/'],'description':'汎用の小型炊飯器。アイボリーの樹脂外装、濃色の内釜、金属内ぶた。後方ヒンジで開閉するふた、蒸気穴、操作部、電源コード付き。'}

def save(slug,fn):
 bpy.ops.wm.read_factory_settings(use_empty=True);detail=fn();sc=bpy.context.scene;sc.frame_end=151;sc.frame_set(1);sc.unit_settings.system='METRIC'
 for o in sc.objects:
  if o.type=='MESH':
   o['assembly_role']='moving' if o.parent else 'fixed';o['attachment_note']='Purposeful concealed positive assembly engagements allowed; no exposed coplanar overlays.'
   # Remove Boolean-generated zero-length edges before saved triangulation.
   bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-8);bmesh.ops.dissolve_degenerate(bm,edges=list(bm.edges),dist=1e-8);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free()
   if not o.data.uv_layers:
    bpy.context.view_layer.objects.active=o;bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.uv.smart_project(island_margin=.02);bpy.ops.object.mode_set(mode='OBJECT')
 bpy.ops.object.select_all(action='SELECT');out=R/'assets'/slug;out.mkdir(parents=True,exist_ok=True);blend=out/(slug+'.blend');glb=out/(slug+'.glb');bpy.ops.wm.save_as_mainfile(filepath=str(blend),compress=True);bpy.ops.export_scene.gltf(filepath=str(glb),export_format='GLB',export_yup=True,export_animations=True,export_extras=True)
 obs=[o for o in sc.objects if o.type=='MESH'];vs=[o.matrix_world@v.co for o in obs for v in o.data.vertices];lo=[min(v[i] for v in vs) for i in range(3)];hi=[max(v[i] for v in vs) for i in range(3)];tris=0
 for o in obs:o.data.calc_loop_triangles();tris+=len(o.data.loop_triangles)
 detail.update(id=slug,title_ja={'microwave_oven':'電子レンジ','rice_cooker':'炊飯器'}[slug],revision=(12 if slug=='microwave_oven' else 11),dimensions_m=[hi[i]-lo[i] for i in range(3)],triangles=tris,units='meter',up_axis_blend='Z',up_axis_glb='Y',review_status='Independent saved geometry and cheap view gate pending',photography_status='Not authorized',files={p.suffix[1:]:{'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in [blend,glb]})
 (out/'metadata.json').write_text(json.dumps(detail,ensure_ascii=False,indent=2)+'\n');print('ASSET_DONE',slug,tris)
if __name__=='__main__':
 args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
 for slug,fn in [('microwave_oven',microwave),('rice_cooker',cooker)]:
  if not args or slug in args:save(slug,fn)
