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

def television():
 black=mat('Charcoal molded TV enclosure',(.025,.029,.033),0,.40);screen=mat('Unlit graphite screen glass',(.018,.027,.035),.15,.20);trim=mat('Satin dark bezel',(.046,.051,.055),.3,.31);rubber=mat('Rubber feet and cord',(.018,.021,.023),0,.72);metal=mat('Satin socket metal',(.4,.43,.46),.85,.32);dark=mat('Dark socket interior',(.007,.008,.009),0,.8)
 box('Thin panel back',(0,.005,.3485),(.972,.025,.567),black,.006)
 # Four bezel members surround a screen seated positively on panel body, no coplanar overlays.
 box('Screen optical layer',(0,-.009,.352),(.947,.005,.533),screen,.002)
 frame=box('Continuous satin bezel frame',(0,-.012,.3485),(.972,.009,.567),trim,.002)
 cut(frame,box('Screen frame aperture',(0,-.012,.351),(.948,.03,.538),trim,.001))
 box('Standby receiver',(0,-.016,.071),(.024,.003,.006),dark,.001)
 box('Rear electronics enclosure',(0,.0345,.25),(.74,.041,.35),black,.018)
 # Stand sockets join the thin panel and each splayed front/back foot.
 for x in [-.365,.365]:
  box('Stand chassis socket',(x,.014,.085),(.045,.040,.052),black,.006)
  for yy in [-.124,.124]:
   beam('Splayed stand leg',(x,.024,.065),(x+math.copysign(.027,x),yy,.010),.018,.018,trim)
   box('Non slip ground pad',(x+math.copysign(.027,x),yy,.003),(.026,.018,.006),rubber,.002)
  cyl('Stand mounting screw',(x,.036,.080),.004,.003,metal,'Y')
 # Real planar vent grille with open slots and recessed black interior.
 grille=box('Rear perforated vent grille',(0,.056,.353),(.46,.006,.064),black,.003)
 for i in range(18):cut(grille,box('Vent cutting tool',(-.212+i*.025,.056,.354),(.009,.024,.043),dark,.002))
 # matching broad enclosure recess behind slotted grille
 housing=bpy.data.objects['Rear electronics enclosure'];cut(housing,box('Vent cavity tool',(0,.054,.353),(.455,.022,.057),dark,.003));box('Recessed vent baffle',(0,.041,.353),(.454,.004,.056),dark,.002)
 # Input bay recess and individual real open sockets.
 cut(housing,box('Input bay cutting tool',(.21,.055,.195),(.18,.030,.17),black,.007));box('Input bay seat',(.21,.042,.195),(.174,.004,.164),dark,.005)
 for z in [.155,.182]:
  ring_box('HDMI socket',(.19,.047,z),(.018,.009,.008),(.014,.020,.004),metal,.001)
  box('HDMI inner tongue',(.19,.049,z),(.011,.005,.0012),black,.0002)
 ring_box('USB socket',(.19,.047,.215),(.015,.009,.008),(.011,.020,.004),metal,.0008)
 box('USB inner tongue',(.19,.050,.214),(.009,.006,.0018),black,.0003)
 ant=cyl('Antenna coaxial socket',(.247,.048,.226),.006,.013,metal,'Y');cut(ant,cyl('Coax bore',(.247,.048,.226),.003,.020,dark,'Y'))
 # Standard200 mm VESA positions, model-specific dimensions not engineering certification.
 for x in [-.1,.1]:
  for z in [.21,.41]:
   o=cyl('Wall mount threaded boss',(x,.056,z),.0055,.006,metal,'Y');cut(o,cyl('Wall mount recess tool',(x,.056,z),.0025,.020,dark,'Y'))
 for x in [-.34,.34]:
  for z in [.10,.405]:cyl('Rear cover screw',(x,.056,z),.003,.002,metal,'Y')
 box('Power button',(-.31,.056,.11),(.025,.004,.01),trim,.002)
 cable(.12,.056,.10,metal,rubber)
 return {'reference_dimensions_m':[.972,.266,.632],'mechanism':'Static editable TV, stand, sockets, enclosure, grounded disconnected cable. No swivel or electrical simulation.','references':['https://www.sony.jp/bravia/products/archive/KJ-X75WL/spec.html'],'description':'細い黒縁の薄型テレビ。左右の脚と接地パッド、背面通風口・端子、消灯した画面。'}

def vacuum():
 ivory=mat('Warm ivory molded polymer',(.77,.75,.69),0,.33);rim=mat('Warm gray protective trim',(.36,.35,.32),0,.50);dark=mat('Dark internal polymer',(.055,.061,.064),0,.62);rubber=mat('Gray flexible hose and tires',(.18,.19,.19),0,.63);metal=mat('Satin steel wand and axles',(.52,.56,.59),.86,.26);paper=mat('Warm paper dust bag',(.57,.46,.30),0,.92);bristle=mat('Dark brush fiber',(.065,.078,.077),0,.9)
 # Quad-ring closed-bottom hollow body: thin upper rim, no curved boolean topology.
 body=lathe_shape('Hollow rounded canister chassis',[(0,.035),(.73,.035),(.9,.048),(1,.080),(1,.135),(.96,.151),(.90,.151),(.92,.133),(.92,.080),(.83,.057),(0,.057)],ivory)
 cut(body,axis_cyl('Chassis hose opening',(0,-.20,.109),(0,-.13,.109),.016,ivory))
 lathe_shape('Lid seated gasket',[(.90,.149),(.958,.149),(.958,.153),(.90,.153),(.90,.149)],dark)
 # Rear motor enclosure occupies back of chamber; dust bag leaves clearance under lid.
 box('Motor compartment',(0,.083,.097),(.145,.085,.075),dark,.016)
 box('Motor support foot',(0,.09,.058),(.12,.07,.012),dark,.004)
 box('Motor filter frame',(0,.038,.10),(.148,.008,.064),rim,.003)
 for i in range(11):box('Pleated motor filter',(-.065+i*.013,.032,.101),(.005,.009,.052),paper,.001)
 box('Paper bag support tray',(0,-.06,.058),(.12,.10,.012),dark,.004)
 bag=box('Seated paper dust bag',(0,-.065,.096),(.145,.14,.068),paper,.022)
 collar=box('Paper bag collar',(0,-.137,.109),(.075,.005,.06),paper,.003)
 cut(collar,axis_cyl('Collar bore',(0,-.15,.109),(0,-.12,.109),.016,paper))
 cut(bag,axis_cyl('Paper bag inlet recess',(0,-.15,.109),(0,-.108,.109),.016,paper))
 axis_pipe('Bag inlet duct',(0,-.179,.109),(0,-.130,.109),.018,dark)
 # Rear wheel shafts and paired wheels with separate tire/hub.
 axis_cyl('Continuous rear axle',(-.12,.087,.075),(.12,.087,.075),.006,metal)
 for x in [-.112,.112]:
  cyl('Rear rubber tire',(x,.087,.075),.075,.018,rubber,'X')
  cyl('Ivory wheel face',(x+math.copysign(.010,x),.087,.075),.065,.006,ivory,'X')
  cyl('Wheel axle cap',(x+math.copysign(.014,x),.087,.075),.013,.003,rim,'X')
 # Front swivel caster, two fork sides and top bearing seat.
 cyl('Caster swivel seat',(0,-.12,.044),.018,.016,dark)
 cyl('Caster swivel spindle',(0,-.12,.044),.005,.016,metal)
 for x in [-.013,.013]:box('Caster fork',(x,-.12,.024),(.005,.027,.026),rim,.003)
 cyl('Caster axle',(0,-.12,.017),.003,.033,metal,'X');cyl('Caster wheel',(0,-.12,.017),.017,.020,rubber,'X')
 # Lid domed thin cap with actual closed underside and rear fixed hinge stations.
 parts=[];parts.append(lathe_shape('Domed maintenance lid',[(0,.189),(.45,.186),(.78,.175),(.94,.157),(.956,.153),(.90,.153),(.73,.169),(.42,.180),(0,.183)],ivory))
 for x in [-.056,.056]:
  box('Fixed lid hinge pedestal',(x,.171,.127),(.014,.022,.039),ivory,.005)
  cyl('Fixed hinge barrel',(x,.18,.153),.008,.019,rim,'X');cyl('Lid hinge pin',(x,.18,.153),.003,.047,metal,'X')
  for dx in [-.016,.016]:
   parts.append(cyl('Moving lid knuckle',(x+dx,.18,.153),.008,.011,ivory,'X'))
   parts.append(box('Moving lid hinge finger',(x+dx,.169,.166),(.010,.028,.012),ivory,.003))
   parts.append(beam('Moving lid upper bridge',(x+dx,.164,.166),(x+dx,.10,.171),.008,.008,ivory))
 parent_parts(parts,(0,.18,.153),0,-100,'Bag chamber lid open close')
 # Fixed carry handle bridges front chassis, with real open finger space.
 for x in [-.065,.065]:beam('Carry handle riser',(x,-.145,.11),(x,-.185,.185),.017,.022,ivory)
 beam('Carry handle bridge',(-.065,-.185,.185),(.065,-.185,.185),.020,.022,ivory)
 # Front hose connection remains fixed to chassis independently of lid.
 axis_pipe('Fixed hose socket',(0,-.160,.11),(0,-.199,.11),.024,rim,wall=.003)
 axis_pipe('Hose coupling',(0,-.187,.11),(0,-.219,.11),.022,ivory,wall=.0055)
 bpy.context.view_layer.update();canister_vs=[o.matrix_world@v.co for o in bpy.context.scene.objects if o.type=='MESH' for v in o.data.vertices];canister_dimensions=[max(v[i] for v in canister_vs)-min(v[i] for v in canister_vs) for i in range(3)]
 # Smooth connected hose centerline with explicit corrugation rings sampled from Bezier curve.
 pts=[(0,-.213,.11),(0,-.29,.085),(.12,-.30,.07),(.20,-.17,.16),(.21,.01,.43),(.29,.015,.66),(.35,-.06,.69)]
 hose=hollow_tube('Flexible vacuum hose',pts,.017,rubber)
 # Evaluate a parallel curve for evenly spaced corrugation rings, solid base remains underneath.
 cu=bpy.data.curves.new('Hose rib guide','CURVE');cu.dimensions='3D';cu.resolution_u=12;s=cu.splines.new('BEZIER');s.bezier_points.add(len(pts)-1)
 for p,co in zip(s.bezier_points,pts):p.co=co;p.handle_left_type='AUTO';p.handle_right_type='AUTO'
 from mathutils.geometry import interpolate_bezier
 samples=[]
 for i in range(len(pts)-1):
  a,b=s.bezier_points[i:i+2];samples+=interpolate_bezier(a.co,a.handle_right,b.handle_left,b.co,40)[:-1]
 samples.append(Vector(pts[-1]));dist=0
 for i in range(1,len(samples)-1):
  dist+=(samples[i]-samples[i-1]).length
  if dist>.0075:torus('Hose corrugation',samples[i],.017,.0017,rubber,samples[i+1]-samples[i-1],24);dist=0
 bpy.data.curves.remove(cu)
 # Curved hollow handgrip and supported control thumb keys.
 hollow_tube('Handgrip air passage',[(.35,-.06,.69),(.35,-.10,.71),(.35,-.15,.68),(.35,-.19,.63)],.018,ivory)
 tube('Handgrip handle loop',[(.35,-.075,.705),(.35,-.075,.755),(.35,-.16,.79),(.35,-.23,.72),(.35,-.19,.64)],.012,ivory)
 o=box('Handgrip control panel',(.35,-.15,.802),(.020,.04,.005),dark,.003)
 for y in [-.14,-.16]:box('Handgrip push button',(.35,y,.806),(.013,.011,.004),rim,.002)
 # Wand is two overlapping concentric metallic sections with collar; closed ends hidden inside fittings.
 A=Vector((.35,-.19,.63));B=Vector((.35,-.67,.075));V=(B-A).normalized();mid=A+(B-A)*.52
 axis_pipe('Outer telescopic wand',A,mid+V*.018,.015,metal);axis_pipe('Inner telescopic wand',mid,B,.0125,metal)
 axis_pipe('Telescopic adjustment collar',mid-V*.02,mid+V*.018,.019,ivory,wall=.005)
 box('Telescopic lock',tuple(mid+Vector((0,-.013,.009))),(.025,.026,.013),rim,.003)
 axis_pipe('Upper wand grip collar',A-V*.018,A+V*.050,.021,ivory,wall=.0065)
 # Low grounded floor head with genuinely recessed underside suction chamber.
 head=box('Floor head shell',(.35,-.70,.029),(.265,.115,.045),ivory,.016)
 cut(head,box('Head underside cavity tool',(.35,-.712,.015),(.222,.064,.044),dark,.007))
 cut(head,box('Intake throat tool',(.35,-.691,.023),(.025,.048,.050),dark,.004))
 cut(head,axis_cyl('Head inlet bore',B+V*.10,B-V*.05,.012,dark))
 box('Floor head bumper',(.35,-.755,.027),(.252,.009,.027),rubber,.004)
 # Rear neck pivots and yoke visibly join head and wand.
 
 for x in [.323,.377]:cyl('Head tilt axle',(x,-.691,.051),.004,.014,metal,'X')
 for x in [.321,.379]:box('Head fixed yoke',(x,-.691,.046),(.013,.03,.034),ivory,.004)
 pivot=cyl('Head pivot barrel',(.35,-.691,.051),.018,.038,rim,'X')
 cut(pivot,axis_cyl('Pivot airflow bore',B+V*.07,B-V*.05,.012,rim))
 axis_pipe('Head wand socket',B+V*.032,B-V*.040,.019,ivory,wall=.007)
 for x in [.252,.448]:
  cyl('Head rear roller',(x,-.66,.012),.012,.025,rubber,'X')
  box('Head front glide',(x,-.74,.004),(.032,.010,.008),rim,.003)
 cyl('Brush roll axle',(.35,-.713,.018),.003,.228,metal,'X')
 cyl('Brush roll core',(.35,-.713,.018),.009,.212,dark,'X')
 for i in range(18):
  x=.25+i*.0118
  for j in range(5):
   a=math.tau*j/5+i*.45;beam('Brush tuft',(x,-.713+.007*math.cos(a),.018+.007*math.sin(a)),(x,-.713+.012*math.cos(a),.018+.012*math.sin(a)),.006,.004,bristle)
 # Guard ribs stay above ground, across true open intake.
 for x in [.28,.35,.42]:
  beam('Intake safety guard front anchor',(x,-.750,.015),(x,-.733,.004),.003,.003,rim)
  beam('Intake safety guard',(x,-.733,.004),(x,-.686,.004),.003,.003,rim)
  beam('Intake safety guard rear anchor',(x,-.686,.004),(x,-.660,.015),.003,.003,rim)
 # Rear exhaust assembly: separate planar grille, no punched curved hull.
 box('Rear exhaust recess',(0,.171,.10),(.128,.008,.047),dark,.005)
 ring_box('Continuous exhaust grille surround',(0,.176,.10),(.144,.010,.054),(.128,.03,.042),ivory,.002)
 for i in range(9):box('Exhaust vertical louver',(-.056+i*.014,.176,.1),(.005,.006,.043),ivory,.001)
 cyl('Cord rewind pedal',(.068,.135,.141),.016,.008,rim)
 # Short partly extended rear cord and plug, not a misleading retract animation.
 cable(-.06,.155,.063,metal,rubber)
 return {'reference_dimensions_m':[.242,.348,.195],'modeled_canister_assembly_dimensions_m':canister_dimensions,'mechanism':'Rear-hinged bag lid rotates100 degrees frames1–151. Wheel, caster, telescopic wand and pivoting head are separate editable components but static pose. Hose and cord static; no suction, motor or hose-deformation simulation.','references':['https://panasonic.jp/soji/products/MC-PJ24G/spec.html'],'description':'アイボリーのキャニスター掃除機。大きな車輪、蛇腹ホース、伸縮管、床ノズル、開閉する紙パック室。'}

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
  if not any(k in o.name for k in ['Hollow rounded','Domed maintenance','Lid seated gasket','Flexible vacuum','Handgrip','Hose corrugation']):
   apply(o,'WEIGHTED_NORMAL',keep_sharp=True,weight=50);normals=[tuple(n.vector) for n in o.data.corner_normals]
   for face in o.data.polygons:
    if max(abs(c) for c in face.normal)>.99999:
     for i in face.loop_indices:normals[i]=tuple(face.normal)
   o.data.normals_split_custom_set(normals)
 bpy.ops.object.select_all(action='SELECT');out=R/'assets'/slug;out.mkdir(parents=True,exist_ok=True);blend=out/(slug+'.blend');glb=out/(slug+'.glb');bpy.ops.wm.save_as_mainfile(filepath=str(blend),compress=True);bpy.ops.export_scene.gltf(filepath=str(glb),export_format='GLB',export_yup=True,export_animations=True,export_animation_mode='ACTIVE_ACTIONS',export_extras=True)
 obs=[o for o in sc.objects if o.type=='MESH'];vs=[o.matrix_world@v.co for o in obs for v in o.data.vertices];lo=[min(v[i] for v in vs) for i in range(3)];hi=[max(v[i] for v in vs) for i in range(3)];tris=0
 for o in obs:o.data.calc_loop_triangles();tris+=len(o.data.loop_triangles)
 detail.update(id=slug,title_ja={'television':'テレビ','vacuum_cleaner':'掃除機'}[slug],revision=(6 if slug=='television' else 9),dimensions_m=[hi[i]-lo[i] for i in range(3)],triangles=tris,units='meter',up_axis_blend='Z',up_axis_glb='Y',review_status='Independent saved geometry and cheap view gate pending',photography_status='Not authorized',files={p.suffix[1:]:{'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in [blend,glb]})
 (out/'metadata.json').write_text(json.dumps(detail,ensure_ascii=False,indent=2)+'\n');print('ASSET_DONE',slug,tris,flush=True)

if __name__=='__main__':
 args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
 for slug,fn in [('television',television),('vacuum_cleaner',vacuum)]:
  if not args or slug in args:save(slug,fn)
