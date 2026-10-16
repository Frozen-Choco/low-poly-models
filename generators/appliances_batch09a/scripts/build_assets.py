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


def ring_box(n,loc,outer,inner,m,b=.002):
 o=box(n,loc,outer,m,b);cut(o,box('ring tool',loc,inner,m,b));return o

def cable(x,y,z,metal,rubber):
 box('Power cable strain relief',(x,y,z),(.018,.026,.018),rubber,.004)
 tube('Unplugged power cable',[(x,y,z),(x+.03,y+.045,z*.7),(x+.025,y+.08,.004),(x-.08,y+.08,.004),(x-.14,y+.05,.004)],.003,rubber)
 box('Power plug',(x-.155,y+.05,.009),(.032,.022,.018),rubber,.003)
 for yy in [y+.044,y+.056]:box('Plug metal blade',(x-.178,yy,.009),(.018,.0016,.008),metal,.0004)

def refrigerator():
 white=mat('Warm white powder coated steel',(.77,.765,.735),0,.34);liner=mat('Ivory food compartment polymer',(.8,.8,.76),0,.35);steel=mat('Satin hinge steel',(.48,.51,.53),.85,.3);rubber=mat('Soft gray gasket',(.25,.26,.25),0,.7);black=mat('Dark base and cable rubber',(.025,.029,.03),0,.65);shelf=mat('Frosted pale shelf polymer',(.61,.69,.69),0,.23)
 body=box('Two compartment insulated cabinet',(0,.015,.63),(.497,.55,1.18),white,.011)
 # Generic insulated walls; inner face materials assigned directly to cavity boundary.
 for z,h in [(.875,.60),(.29,.38)]:
  cut(body,box('Cavity tool',(0,-.045,z),(.405,.53,h),liner,.010))
 body.data.materials.append(liner)
 for p in body.data.polygons:
  c=body.matrix_world@p.center
  if abs(c.x)<.205 and c.y<.223 and ((.572<c.z<1.178) or (.098<c.z<.482)):p.material_index=1
 # shelves fixed on side rails, setback from door bins.
 for z in [.76,.97]:
  for x in [-.195,.195]:box('Shelf support rail',(x,.045,z-.006),(.019,.35,.016),liner,.003)
  box('Refrigerator shelf',(0,.045,z+.004),(.389,.35,.007),shelf,.002)
  box('Shelf front trim',(0,-.131,z+.004),(.391,.006,.009),liner,.002)
 # Lower freezer two storage trays, deliberately matte not falsely transparent.
 for z in [.112,.302]:
  for x in [-.195,.195]:box('Freezer tray support',(x,.02,z),(.018,.39,.016),liner,.002)
  tray=box('Freezer tray',(0,.015,z+.063),(.383,.38,.12),shelf,.007)
  cut(tray,box('Freezer tray hollow',(0,.015,z+.078),(.369,.366,.13),shelf,.004))
  box('Freezer tray grip',(0,-.179,z+.089),(.13,.018,.018),liner,.004)
 # Bottom feet and recessed service cover.
 box('Lower plinth',(0,.005,.045),(.455,.50,.03),black,.005)
 for x in [-.199,.199]:
  for y in [-.215,.22]:cyl('Adjustable rubber foot',(x,y,.025),.018,.05,black)
 cut(body,box('Rear service recess tool',(0,.292,.22),(.37,.030,.285),white,.004))
 panel=box('Rear equipment cover',(0,.292,.22),(.394,.008,.31),steel,.004)
 for i in range(8):cut(panel,box('Rear slot tool',(0,.292,.115+i*.022),(.27,.03,.007),black,.002))
 box('Recessed vent baffle',(0,.286,.21),(.375,.006,.27),black,.002)
 for x in [-.18,.18]:
  for z in [.08,.36]:cyl('Service panel screw',(x,.297,z),.003,.002,steel,'Y')
 # Doors on independent coaxial left hinges. Front surfaces y=-.305; body front=-.260.
 for tag,z,h in [('Upper',.875,.654),('Lower',.29,.49)]:
  parts=[];door=box(tag+' insulated door',(0,-.287,z),(.493,.05,h),white,.009);parts.append(door)
  parts.append(box(tag+' door inner liner',(0,-.260,z),(.395,.012,h-(.082 if tag=='Upper' else .14)),liner,.006))
  parts.append(ring_box(tag+' compression gasket',(0,-.2645,z),(.431,.011,h-.045),(.408,.03,h-.068),rubber,.003))
  # Recessed edge pull in exposed opposite edge, real depression.
  handlez=z-h/2+.035 if tag=='Upper' else z+h/2-.035
  cut(door,box('Door grip tool',(.145,-.312,handlez),(.145,.028,.024),white,.007))
  # Shallow bins only upper chamber. Positive 3mm insertion into liner, 67mm deep.
  if tag=='Upper':
   for bz in [.66,.98]:
    bin=box('Door storage pocket',(0,-.222,bz),(.322,.070,.105),liner,.005)
    cut(bin,box('Pocket hollow',(0,-.218,bz+.012),(.309,.058,.111),liner,.003));parts.append(bin)
  for hz in [z-h/2+.020,z+h/2-.020]:
   parts.append(cyl(tag+' moving knuckle',(-.256,-.285,hz),.008,.016,steel))
   parts.append(box(tag+' moving hinge leaf',(-.240,-.287,hz),(.040,.012,.010),steel,.002))
  parent_parts(parts,(-.256,-.285,0),2,-100,tag+' door open close')
 # Three shared fixed stations sit fully outside both door envelopes in Z.
 for hz,depth in [(.031,.050),(.5415,.070),(1.216,.040)]:
  cyl('Shared hinge pin',(-.256,-.285,hz+(.015 if hz<.1 else -.012 if hz>1 else 0)),.003,depth,steel)
  cyl('Shared fixed knuckle',(-.256,-.285,hz),.008,.009,steel)
  box('Shared fixed hinge leaf',(-.248,-.266,hz),(.025,.046,.008),steel,.001)
 box('Lower fixed hinge support neck',(-.24,-.245,.039),(.022,.020,.022),steel,.002)
 cable(.16,.294,.075,steel,black)
 # Broad axis-aligned cavity and cabinet planes must not interpolate bevel normals.
 for face in body.data.polygons:face.use_smooth=max(abs(c) for c in face.normal)<.999
 return {'reference_dimensions_m':[.497,.595,1.220],'modeled_cabinet_dimensions_m':[.497,.55,1.18],'mechanism':'Two separately editable left-hinged doors rotate0–100 degrees together, frames1–151. Shelves and trays static, editable. Generic assumed inner construction; not an engineering replica.','references':['https://panasonic.jp/reizo/products/NR-B16C1/spec.html'],'description':'白い塗装鋼板の二ドア冷蔵庫。上部冷蔵室、下部冷凍室、棚と収納ポケット、パッキンを備えた開閉扉。'}

def perforated_basket(m):
 # Grid walls with deliberately omitted cells; solidify provides true through openings and thickness.
 N=128;zs=[.29,.36,.366,.43,.436,.50,.506,.57,.576,.65,.72,.765];v=[];f=[]
 for z in zs:
  for i in range(N):a=math.tau*i/N;v.append((.190*math.cos(a),.190*math.sin(a),z))
 for j in range(len(zs)-1):
  for i in range(N):
   if j in [1,3,5,7] and i%4==0:continue
   k=(i+1)%N;f.append((j*N+i,j*N+k,(j+1)*N+k,(j+1)*N+i))
 me=bpy.data.meshes.new('Perforated basket wall');me.from_pydata(v,[],f);me.update();o=bpy.data.objects.new('Perforated stainless basket',me);bpy.context.collection.objects.link(o);o.data.materials.append(m)
 for p in o.data.polygons:p.use_smooth=True
 apply(o,'SOLIDIFY',thickness=.002,offset=0);return o

def washer():
 white=mat('Warm white coated cabinet',(.76,.755,.73),0,.34);ivory=mat('Ivory molded top and lid',(.8,.79,.75),0,.31);beige=mat('Warm beige control fascia',(.54,.50,.42),0,.38);steel=mat('Brushed stainless wash basket',(.48,.51,.53),.9,.33);rubber=mat('Dark rubber hoses feet cable',(.035,.04,.041),0,.68);gray=mat('Gray tub polymer',(.25,.28,.29),0,.46);lcd=mat('Unlit gray green display',(.10,.15,.145),0,.28)
 body=box('Rounded open-top steel cabinet',(0,0,.422),(.52,.53,.764),white,.025)
 cut(body,box('Cabinet hollow tool',(0,0,.49),(.487,.497,.84),white,.016))
 for x in [-.216,.216]:
  for y in [-.213,.213]:cyl('Adjustable rubber foot',(x,y,.027),.022,.054,rubber)
 box('Cabinet lower internal support',(0,0,.09),(.45,.45,.05),gray,.01)
 cyl('Tub fixed support seat',(0,0,.18),.09,.16,gray)
 shell('Closed bottom outer tub',[(0,.22),(.18,.22),(.211,.25),(.217,.69),(.214,.785),(.205,.79),(.202,.77),(.204,.28),(.18,.24),(0,.24)],gray)
 perforated_basket(steel)
 cyl('Basket central support spindle',(0,0,.265),.035,.056,steel)
 cyl('Basket bottom',(0,0,.291),.191,.009,steel)
 shell('Basket smooth top rim',[(.188,.755),(.195,.755),(.198,.768),(.193,.776),(.185,.776),(.184,.768)],steel)
 cyl('Basket bottom pulsator',(0,0,.305),.169,.020,ivory)
 cyl('Pulsator center cap',(0,0,.32),.033,.012,gray)
 for k in range(3):
  a=math.tau*k/3;o=box('Pulsator molded fin',(.092*math.cos(a),.092*math.sin(a),.324),(.136,.026,.024),ivory,.010);o.rotation_euler[2]=a
 top=box('Molded top deck',(0,0,.805),(.532,.542,.063),ivory,.023)
 cut(top,cyl('Top opening tool',(0,0,.81),.199,.15,ivory))
 shell('Top opening lip',[(.196,.778),(.204,.778),(.204,.824),(.198,.833),(.191,.833),(.190,.825),(.194,.815)],ivory)
 # Front control fascia separate from opening; key/display have actual positive seat.
 panel=box('Front control fascia',(0,-.234,.838),(.456,.069,.014),beige,.009)
 box('Display bezel',(-.06,-.235,.846),(.09,.036,.005),rubber,.003)
 box('Unlit LCD',(-.06,-.235,.849),(.075,.026,.003),lcd,.002)
 for x in [.025,.075,.125,.18]:cyl('Control push button',(x,-.235,.849),.012,.009,ivory)
 for x in [-.18,-.15,-.12]:cyl('Status indicator',(x,-.235,.847),.003,.004,gray)
 # Thick single-piece lid fits between front fascia and rear deck; underside is separate recessed molding.
 parts=[];parts.append(box('Single-piece washer lid',(0,.006,.853),(.446,.412,.027),ivory,.015))
 parts.append(box('Lid underside molding',(0,-.003,.842),(.392,.338,.008),gray,.010))
 # Actual recessed grip on top-front edge.
 cut(parts[0],box('Lid grip recess',(0,-.186,.866),(.14,.035,.020),ivory,.008))
 # Rear hinge at y=.219. Moving bridge joins lid, fixed brackets join deck.
 for x in [-.14,.14]:
  box('Lid hinge fixed bracket',(x,.262,.835),(.024,.040,.030),ivory,.006)
  cyl('Fixed rear hinge barrel',(x,.239,.854),.012,.025,gray,'X')
  cyl('Rear hinge axle',(x,.239,.854),.004,.065,steel,'X')
  for dx in [-.024,.024]:parts.append(cyl('Moving lid hinge barrel',(x+dx,.239,.854),.012,.018,ivory,'X'))
  for dx in [-.024,.024]:parts.append(box('Lid hinge fork finger',(x+dx,.224,.856),(.014,.044,.016),ivory,.003))
 parent_parts(parts,(0,.239,.854),0,-105,'Washer lid open close')
 # Inlet short connected hose, external free coupler; never implies plumbed installation.
 cyl('Water inlet pedestal',(.248,.236,.849),.019,.028,gray)
 cyl('Threaded water inlet',(.248,.236,.872),.013,.020,steel)
 for z in [.864,.87,.876]:cyl('Water inlet thread ring',(.248,.236,z),.014,.002,steel)
 supply=tube('Connected supply hose',[(.248,.236,.884),(.27,.28,.91),(.28,.32,.86),(.28,.33,.75)],.008,gray)
 bm=bmesh.new();bm.from_mesh(supply.data);bmesh.ops.delete(bm,geom=[f for f in bm.faces if len(f.verts)==3],context='FACES');bm.to_mesh(supply.data);bm.free();apply(supply,'SOLIDIFY',thickness=.003,offset=-1)
 coupler=cyl('Loose supply coupler',(.28,.33,.736),.015,.030,ivory);cut(coupler,cyl('Coupler bore tool',(.28,.33,.736),.006,.045,ivory))
 # Drain socket meets cabinet side, hose route drops to support plane and ends visibly open.
 cyl('Drain socket',(.267,.12,.12),.019,.035,gray,'X')
 drain=tube('Drain hose',[(.28,.12,.12),(.34,.12,.095),(.36,.15,.022),(.36,.25,.016),(.30,.31,.016)],.014,gray)
 # Remove only large end cap polygons then thicken surface inward to make continuous hollow hose.
 bm=bmesh.new();bm.from_mesh(drain.data);caps=[f for f in bm.faces if len(f.verts)==3];bmesh.ops.delete(bm,geom=caps,context='FACES');bm.to_mesh(drain.data);bm.free();apply(drain,'SOLIDIFY',thickness=.003,offset=-1)
 # Back service hatch with sealed recessed shadow seam.
 box('Rear service panel shadow',(0,.267,.39),(.40,.005,.54),rubber,.009)
 box('Rear service panel',(0,.271,.39),(.389,.006,.529),white,.008)
 for x in [-.177,.177]:
  for z in [.145,.635]:cyl('Rear panel screw',(x,.275,z),.003,.002,steel,'Y')
 cable(-.16,.27,.13,steel,rubber)
 return {'reference_dimensions_m':[.562,.572,.880],'modeled_cabinet_dimensions_m':[.520,.530,.764],'mechanism':'Single-piece lid rotates0–105 degrees, frames1–151. Basket/pulsator are static editable components. Supply/drain hoses attached to appliance but free at far end. No motor, water, latch or electrical simulation.','references':['https://panasonic.jp/wash/products/NA-F6B3/spec.html'],'description':'白い鋼板とアイボリー樹脂の縦型洗濯機。開閉ふた、ステンレス槽、パルセータ、給排水ホースと操作部。'}

def save(slug,fn):
 bpy.ops.wm.read_factory_settings(use_empty=True);detail=fn();sc=bpy.context.scene;sc.frame_end=151;sc.frame_set(1);sc.unit_settings.system='METRIC'
 for o in sc.objects:
  if o.type=='MESH':
   o['assembly_role']='moving' if o.parent else 'fixed';o['attachment_note']='Purposeful concealed positive assembly engagements allowed; no exposed coplanar overlays.'
   # Remove Boolean-generated zero-length edges before saved triangulation.
   bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-8);bmesh.ops.dissolve_degenerate(bm,edges=list(bm.edges),dist=1e-8);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free()
   if not o.data.uv_layers:
    bpy.context.view_layer.objects.active=o;bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.uv.smart_project(island_margin=.02);bpy.ops.object.mode_set(mode='OBJECT')
 # Rebuild cabinet corner normals only AFTER all BMesh/UV operations.
 # Keeping explicit normals on smooth-tagged faces avoids glTF flat/ngon split ambiguity.
 if slug=='refrigerator':
  o=bpy.data.objects['Two compartment insulated cabinet'];bpy.context.view_layer.objects.active=o
  if o.data.has_custom_normals:bpy.ops.mesh.customdata_custom_splitnormals_clear()
  for face in o.data.polygons:face.use_smooth=True
  apply(o,'WEIGHTED_NORMAL',keep_sharp=True,weight=50)
  normals=[tuple(n.vector) for n in o.data.corner_normals]
  for face in o.data.polygons:
   if max(abs(c) for c in face.normal)>.999:
    for i in face.loop_indices:normals[i]=tuple(face.normal)
  o.data.normals_split_custom_set(normals)
 # Cylinder wall and punched thickness edges require separate analytical normals.
 if slug=='washing_machine':
  o=bpy.data.objects['Perforated stainless basket'];bpy.context.view_layer.objects.active=o
  if o.data.has_custom_normals:bpy.ops.mesh.customdata_custom_splitnormals_clear()
  normals=[(0,0,1)]*len(o.data.loops)
  for face in o.data.polygons:
   face.use_smooth=True;radial=Vector((face.center.x,face.center.y,0)).normalized();dot=face.normal.dot(radial)
   for i in face.loop_indices:
    v=o.data.vertices[o.data.loops[i].vertex_index].co
    normals[i]=tuple(Vector((v.x,v.y,0)).normalized()*(1 if dot>0 else -1)) if abs(face.normal.z)<.1 and abs(dot)>.9 else tuple(face.normal)
  o.data.normals_split_custom_set(normals)
 bpy.ops.object.select_all(action='SELECT');out=R/'assets'/slug;out.mkdir(parents=True,exist_ok=True);blend=out/(slug+'.blend');glb=out/(slug+'.glb');bpy.ops.wm.save_as_mainfile(filepath=str(blend),compress=True);bpy.ops.export_scene.gltf(filepath=str(glb),export_format='GLB',export_yup=True,export_animations=True,export_animation_mode='ACTIVE_ACTIONS',export_extras=True)
 obs=[o for o in sc.objects if o.type=='MESH'];vs=[o.matrix_world@v.co for o in obs for v in o.data.vertices];lo=[min(v[i] for v in vs) for i in range(3)];hi=[max(v[i] for v in vs) for i in range(3)];tris=0
 for o in obs:o.data.calc_loop_triangles();tris+=len(o.data.loop_triangles)
 detail.update(id=slug,title_ja={'refrigerator':'冷蔵庫','washing_machine':'洗濯機'}[slug],revision=7,dimensions_m=[hi[i]-lo[i] for i in range(3)],triangles=tris,units='meter',up_axis_blend='Z',up_axis_glb='Y',review_status='Independent saved geometry and cheap view gate pending',photography_status='Not authorized',files={p.suffix[1:]:{'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in [blend,glb]})
 (out/'metadata.json').write_text(json.dumps(detail,ensure_ascii=False,indent=2)+'\n');print('ASSET_DONE',slug,tris)

if __name__=="__main__":
 args=sys.argv[sys.argv.index("--")+1:] if "--" in sys.argv else []
 for slug,fn in [("refrigerator",refrigerator),("washing_machine",washer)]:
  if not args or slug in args:save(slug,fn)
