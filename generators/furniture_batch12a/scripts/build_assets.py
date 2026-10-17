import bpy,bmesh,math,json,hashlib,sys,numpy as np
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1]
def mat(n,c,rough=.5,metal=0):
 m=bpy.data.materials.new(n);m.diffuse_color=(*c,1);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*c,1);p.inputs['Roughness'].default_value=rough;p.inputs['Metallic'].default_value=metal;return m
def texture(m,kind):
 N=512;y,x=np.mgrid[0:N,0:N]/N;rng=np.random.default_rng(1241);v=np.zeros((N,N,4),np.float32);v[:,:,3]=1
 if kind=='wood':
  q=x+.009*np.sin(y*18+x*5)+.004*np.sin(y*43+x*15);a=.018*np.sin(q*340)+.009*np.sin(q*910)+.022*np.sin(q*45);base=(.69,.51,.32)
 elif kind=='end':a=.018*np.sin(130*np.sqrt((x-.4)**2+(y+1)**2));base=(.65,.47,.29)
 else:
  a=.009*np.sin(x*math.tau*128)*np.sin(y*math.tau*128)+rng.normal(0,.006,(N,N));base=kind
 for k,c in enumerate(base):v[:,:,k]=c+a
 im=bpy.data.images.new(m.name+' original texture',width=N,height=N);im.pixels.foreach_set(v.ravel());im.pack();n=m.node_tree.nodes.new('ShaderNodeTexImage');n.image=im;m.node_tree.links.new(n.outputs['Color'],m.node_tree.nodes.get('Principled BSDF').inputs['Base Color']);return m
def modifier(o,t,**args):
 bpy.context.view_layer.objects.active=o;m=o.modifiers.new(t,t)
 for k,v in args.items():setattr(m,k,v)
 bpy.ops.object.modifier_apply(modifier=m.name)
def finish(o,n,m,smooth=True):
 o.name=n;o.data.materials.append(m)
 for f in o.data.polygons:f.use_smooth=smooth
 return o
def box(n,loc,dim,m,b=.003):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.dimensions=dim;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 if b:modifier(o,'BEVEL',width=min(b,min(dim)*.45),segments=4)
 finish(o,n,m);modifier(o,'WEIGHTED_NORMAL',keep_sharp=True,weight=50);return o
def wood(n,loc,dim,axis=0,b=.003):
 o=box(n,loc,dim,WOOD,b);o.data.materials.append(END);uv=o.data.uv_layers.active or o.data.uv_layers.new();others=[i for i in range(3) if i!=axis]
 for f in o.data.polygons:
  end=abs(f.normal[axis])>.9
  if end:f.material_index=1
  for li in f.loop_indices:
   p=o.data.vertices[o.data.loops[li].vertex_index].co
   if end:uv.data[li].uv=(p[others[0]]/.1+.5,p[others[1]]/.1+.5)
   else:
    t=others[0] if abs(f.normal[others[1]])>.5 else others[1];uv.data[li].uv=(p[t]/.18+.23,p[axis]/1.4+.5)
 return o
def cyl(n,loc,r,d,m,axis='Z'):
 bpy.ops.mesh.primitive_cylinder_add(vertices=24,radius=r,depth=d,location=loc);o=bpy.context.object
 if axis=='X':o.rotation_euler.y=math.pi/2
 if axis=='Y':o.rotation_euler.x=math.pi/2
 modifier(o,'BEVEL',width=min(.0008,d/4),segments=2);finish(o,n,m);modifier(o,'WEIGHTED_NORMAL',keep_sharp=True);return o
def cushion(n,loc,dim,m,r=.035,puff=.008):
 # Shared-face lattice, analytic rounded-box mapping; flat supported lower center and softly crowned upper fabric.
 hs=[d/2 for d in dim];grids=[]
 for h in hs:
  rr=min(r,h*.85);mid=np.linspace(-h+rr,h-rr,9).tolist();grids.append([-h,-h+rr*.15,-h+rr*.45]+mid+[h-rr*.45,h-rr*.15,h])
 verts=[];faces=[];ids={}
 def vertex(p):
  key=tuple(round(v,9) for v in p)
  if key in ids:return ids[key]
  inner=Vector([max(-h+r,min(h-r,v)) for v,h in zip(p,hs)]);delta=Vector(p)-inner
  q=inner+delta.normalized()*r
  # Local Z is cushion thickness; dome vanishes continuously at rounded edge.
  if p[2]>0:q.z+=puff*(max(0,1-(q.x/hs[0])**2)*max(0,1-(q.y/hs[1])**2))**2
  ids[key]=len(verts);verts.append(tuple(q));return ids[key]
 for axis in range(3):
  a,b=[i for i in range(3) if i!=axis]
  for s in [-1,1]:
   table=[]
   for u in grids[a]:
    row=[]
    for v in grids[b]:p=[0,0,0];p[axis]=s*hs[axis];p[a]=u;p[b]=v;row.append(vertex(p))
    table.append(row)
   for i in range(len(table)-1):
    for j in range(len(table[0])-1):faces.append((table[i][j],table[i+1][j],table[i+1][j+1],table[i][j+1]))
 me=bpy.data.meshes.new(n);me.from_pydata(verts,[],faces);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();o=bpy.data.objects.new(n,me);bpy.context.collection.objects.link(o);o.location=loc;finish(o,n,m);o['organic_surface']=True;return o
def seam(n,xy,z,m,loc=(0,0,0),rotation=None,r=.0015):
 # Closed round rectangular sewn piping, seated partly in upholstery.
 w,d,corner=xy;pts=[]
 for cx,cy,start in [(w/2-corner,d/2-corner,0),(-w/2+corner,d/2-corner,90),(-w/2+corner,-d/2+corner,180),(w/2-corner,-d/2+corner,270)]:
  for j in range(9):a=math.radians(start+j*90/8);pts.append((cx+corner*math.cos(a),cy+corner*math.sin(a),z))
 cu=bpy.data.curves.new(n,'CURVE');cu.dimensions='3D';cu.bevel_depth=r;cu.bevel_resolution=2;s=cu.splines.new('POLY');s.points.add(len(pts)-1)
 for v,p in zip(s.points,pts):v.co=(*p,1)
 s.use_cyclic_u=True;o=bpy.data.objects.new(n,cu);bpy.context.collection.objects.link(o);o.location=loc
 if rotation:o.rotation_euler=rotation
 bpy.context.view_layer.objects.active=o;o.select_set(True);bpy.ops.object.convert(target='MESH');o.select_set(False);o.data.materials.append(m)
 for p in o.data.polygons:p.use_smooth=True
 return o
def materials():
 global WOOD,END,METAL,FABRIC,WHITE,SEAM,DARK
 WOOD=texture(mat('Natural pale wood',(.55,.36,.18),.58),'wood');END=texture(mat('Exposed wood end grain',(.5,.3,.15),.67),'end');METAL=mat('Zinc steel hardware',(.36,.38,.39),.3,.8);FABRIC=texture(mat('Warm gray woven upholstery',(.34,.30,.25),.86),(.54,.51,.46));WHITE=texture(mat('Ivory cotton ticking',(.8,.77,.69),.92),(.86,.84,.78));SEAM=texture(mat('Sewn fabric welt',(.25,.23,.20),.9),(.47,.44,.39));DARK=mat('Dark underside dust cloth',(.045,.045,.04),.98)
def bed():
 for x in [-.47,.47]:
  wood('Headboard post '+str(x),(x,1.0175,.46),(.040,.055,.92),2)
  wood('Foot post '+str(x),(x,-1.0175,.16),(.040,.055,.32),2)
  wood('Side rail '+str(x),(x,0,.258),(.035,1.990,.116),1)
  wood('Slat support ledger '+str(x),(x*.947,0,.263),(.035,1.98,.034),1,.002)
 for y in [-1.0175,1.0175]:wood('End rail '+str(y),(0,y,.258),(.915,.035,.116),0)
 for z in [.58,.72,.86]:wood('Headboard horizontal '+str(z),(0,1.0175,z),(.915,.027,.10),0)
 for i in range(16):
  y=-.94+i*1.88/15;wood('Mattress support slat %02d'%i,(0,y,.2895),(.91,.067,.022),0,.002)
 for x in [-.47,.47]:
  for y in [-1.0175,1.0175]:
   for z in [.235,.285]:cyl('Bed rail bolt',(x+(1 if x>0 else -1)*.0195,y,z),.005,.003,METAL,'X')
 mattress=cushion('Supported mattress',(0,0,.390),(.90,2,.18),WHITE,.026,.005)
 seam('Mattress upper welt',(.897,1.997,.040),.061,WHITE,loc=(0,0,.390),r=.0018)
 pillow=cushion('Cotton pillow',(0,.70,.525),(.60,.36,.10),WHITE,.043,.016)
 seam('Pillow stitched edge',(.59,.35,.05),0,WHITE,loc=(0,.70,.525),r=.0014)
 return {'description':'木枠とすのこで支えるシングルベッド。独立した厚手マットレスと枕。','reference_dimensions_m':[.98,2.09,.92],'mechanism':'Static separately editable frame, slats, mattress and pillow; no deformation or load certification.'}
def sofa():
 # Four legs positively enter lower cross rails; bottom centers lie at Z0.
 for x in [-.60,.60]:
  for y in [-.30,.28]:
   wood('Sofa leg '+str((x,y)),(x,y,.10),(.060,.060,.20),2,.005)
   cyl('Leg mounting screw '+str((x,y)),(x,y,.201),.007,.055,METAL)
 for y in [-.30,.28]:wood('Lower cross rail '+str(y),(0,y,.205),(1.28,.07,.07),0)
 for x in [-.60,.60]:wood('Lower side rail '+str(x),(x,-.01,.207),(.07,.58,.07),1)
 wood('Center support crossmember',(0,-.01,.227),(1.24,.07,.035),0)
 box('Underseat support deck',(0,-.01,.249),(1.26,.64,.025),WOOD,.003)
 box('Underside dust cover',(0,-.01,.182),(1.16,.54,.004),DARK,.001)
 box('Upholstered lower frame',(0,-.005,.294),(1.31,.72,.10),FABRIC,.025)
 for x in [-.663,.663]:
  wood('Arm internal support '+str(x),(x,.015,.395),(.07,.67,.38),2)
  cushion('Upholstered arm '+str(x),(x,.005,.437),(.124,.77,.48),FABRIC,.045,.006)
 # Rear structural back lies behind padded cushions; frame is buried by upholstery.
 for x in [-.56,.56]:wood('Back upright '+str(x),(x,.303,.48),(.055,.06,.51),2)
 wood('Back upper crossbar',(0,.325,.72),(1.18,.055,.055),0)
 back=cushion('Upholstered back shell',(0,.325,.545),(1.30,.145,.49),FABRIC,.05,.006)
 for i,x in enumerate([-.307,.307]):
  seat=cushion('Seat cushion '+str(i),(x,-.055,.400),(.604,.62,.120),FABRIC,.043,.012)
  seam('Seat cushion sewn welt '+str(i),(.599,.615,.048),.023,SEAM,loc=(x,-.055,.400))
  # Local Z is thickness, rotated to face toward front with 9 degree recline.
  rot=(math.radians(81),0,0)
  ob=cushion('Back cushion '+str(i),(x,.235,.631),(.604,.33,.13),FABRIC,.047,.014);ob.rotation_euler=rot
  seam('Back cushion sewn welt '+str(i),(.595,.321,.052),.034,SEAM,loc=(x,.235,.631),rotation=rot)
 return {'description':'丸みのある布張りの2人掛けソファ。2組の座・背クッションと木脚、内部支持枠。','reference_dimensions_m':[1.37,.805,.77],'mechanism':'Static editable two-seat sofa. Four legs, cross rails, seat deck, arm and back structure; no recliner or cloth physics.'}
def save(slug,fn):
 bpy.ops.wm.read_factory_settings(use_empty=True);bpy.context.preferences.filepaths.save_version=0;materials();meta=fn();sc=bpy.context.scene;sc.unit_settings.system='METRIC';sc.render.threads_mode='FIXED';sc.render.threads=2
 for o in sc.objects:
  if o.type!='MESH':continue
  o['assembly_role']='fixed';o['attachment_note']='Concealed seating and fabric overlap are intentional; no exposed coplanar overlays.'
  if o.data.uv_layers:continue
  bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o;bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.uv.smart_project(island_margin=.01);bpy.ops.object.mode_set(mode='OBJECT')
 bpy.ops.object.select_all(action='SELECT');out=R/'assets'/slug;out.mkdir(parents=True,exist_ok=True);blend=out/(slug+'.blend');glb=out/(slug+'.glb');bpy.ops.wm.save_as_mainfile(filepath=str(blend),compress=True);bpy.ops.export_scene.gltf(filepath=str(glb),export_format='GLB',export_yup=True,export_animations=False,export_extras=True)
 obs=[o for o in sc.objects if o.type=='MESH'];vs=[o.matrix_world@v.co for o in obs for v in o.data.vertices];lo=[min(v[i] for v in vs) for i in range(3)];hi=[max(v[i] for v in vs) for i in range(3)];tris=0
 for o in obs:o.data.calc_loop_triangles();tris+=len(o.data.loop_triangles)
 meta.update(id=slug,title_ja={'bed':'ベッド','sofa':'ソファ'}[slug],revision=2,dimensions_m=[hi[i]-lo[i] for i in range(3)],triangles=tris,units='meter',up_axis_blend='Z',up_axis_glb='Y',review_status='Independent saved geometry and original-resolution gate pending',photography_status='Not authorized',files={p.suffix[1:]:{'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in [blend,glb]})
 (out/'metadata.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n');print('ASSET_DONE',slug,tris,flush=True)
if __name__=='__main__':
 args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
 for slug,fn in [('bed',bed),('sofa',sofa)]:
  if not args or slug in args:save(slug,fn)
