"""Original batch06a mesh generator. Run only after parent CPU-slot release.
No downloaded mesh, external generator or renderer is used. Geometry is authored
here. Run with Blender 4.3.2 --background --threads 2 --python ... -- --asset all.
No rendering occurs in this script. Common canonical photography is separate.
"""
import bpy, math, json, hashlib, argparse, sys
from pathlib import Path
from mathutils import Vector, Matrix
sys.path.insert(0,str(Path(__file__).resolve().parent))
import mechanics as M
ROOT=Path(__file__).resolve().parents[1]
D=M.DESIGN
GROUP='fixed'
def clear():
 bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
 bpy.context.scene.unit_settings.system='METRIC';bpy.context.scene.unit_settings.scale_length=1
 bpy.context.preferences.filepaths.save_version=0

def mat(name,color,metal=0,rough=.5):
 m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);m.use_nodes=True
 p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*color,1);p.inputs['Metallic'].default_value=metal;p.inputs['Roughness'].default_value=rough
 return m

def register(o,material=None):
 o['mechanical_group']=GROUP
 if material:o.data.materials.append(material)
 return o

def mesh(name,verts,faces,material,smooth=False):
 me=bpy.data.meshes.new(name);me.from_pydata(verts,[],faces);me.update();o=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(o);register(o,material)
 for p in me.polygons:p.use_smooth=smooth
 return o

def bevel(o,width=.002,segments=3):
 bpy.context.view_layer.objects.active=o
 q=o.modifiers.new('Manufactured edge radii','BEVEL');q.width=width;q.segments=segments
 bpy.ops.object.modifier_apply(modifier=q.name)
 return o

def box(name,p,size,material,r=.001,segments=3):
 bpy.ops.mesh.primitive_cube_add(size=1,location=p);o=bpy.context.object;o.name=name;o.dimensions=size;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);register(o,material)
 if r:bevel(o,min(r,min(size)*.45),segments)
 return o

def cyl(name,a,b,r,material,n=48):
 a,b=Vector(a),Vector(b);vec=b-a
 bpy.ops.mesh.primitive_cylinder_add(vertices=n,radius=r,depth=vec.length,location=(a+b)/2)
 o=bpy.context.object;o.name=name;o.rotation_euler=vec.to_track_quat('Z','Y').to_euler();register(o,material)
 for p in o.data.polygons:p.use_smooth=len(p.vertices)==4
 return o

def tube(name,points,r,material,n=16,closed=False):
 # Parallel-transport frame avoids twisting rings at handle and frame curves.
 points=[Vector(p) for p in points];L=len(points);verts=[];faces=[];u=None
 for j,p in enumerate(points):
  tangent=(points[(j+1)%L]-points[(j-1)%L]) if closed else (points[min(L-1,j+1)]-points[max(0,j-1)])
  tangent.normalize()
  if u is None:
   ref=Vector((1,0,0)) if abs(tangent.x)<.9 else Vector((0,1,0));u=(ref-tangent*ref.dot(tangent)).normalized()
  else:
   u=u-tangent*u.dot(tangent)
   if u.length<1e-8:u=tangent.cross(Vector((0,0,1)))
   u.normalize()
  v=tangent.cross(u).normalized();rad=r[j] if isinstance(r,(list,tuple)) else r
  for k in range(n):a=2*math.pi*k/n;verts.append(tuple(p+rad*(math.cos(a)*u+math.sin(a)*v)))
 for j in range(L if closed else L-1):
  for k in range(n):faces.append((j*n+k,j*n+(k+1)%n,((j+1)%L)*n+(k+1)%n,((j+1)%L)*n+k))
 if not closed:faces += [tuple(reversed(range(n))),tuple((L-1)*n+k for k in range(n))]
 return mesh(name,verts,faces,material,True)

def smooth_path(pts,steps=8):
 p=[Vector(pts[0])]+[Vector(x) for x in pts]+[Vector(pts[-1])];out=[]
 for i in range(1,len(p)-2):
  a,b,c,d=p[i-1:i+3]
  for k in range(steps):
   t=k/steps;out.append(tuple(.5*((2*b)+(-a+c)*t+(2*a-5*b+4*c-d)*t*t+(-a+3*b-3*c+d)*t*t*t)))
 out.append(tuple(pts[-1]));return out

def ring_x(name,center,radius,section_r,material,N=112,n=12):
 pts=[(center[0],center[1]+radius*math.cos(2*math.pi*k/N),center[2]+radius*math.sin(2*math.pi*k/N)) for k in range(N)]
 return tube(name,pts,section_r,material,n,True)

def torus_z(name,p,r,minor,material,N=32):
 return tube(name,[(p[0]+r*math.cos(2*math.pi*i/N),p[1]+r*math.sin(2*math.pi*i/N),p[2]) for i in range(N)],minor,material,6,True)

def ellipsoid(name,p,scale,material,segments=40,rings=20):
 bpy.ops.mesh.primitive_uv_sphere_add(segments=segments,ring_count=rings,radius=1,location=p);o=bpy.context.object;o.name=name;o.scale=scale;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);register(o,material)
 for f in o.data.polygons:f.use_smooth=True
 return o

def difference(o,tool):
 bpy.context.view_layer.objects.active=o;mod=o.modifiers.new('Actual through opening','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=tool;bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(tool,do_unlink=True)

def prism_yz(name,outline,xlo,xhi,material):
 n=len(outline);v=[(x,y,z) for x in (xlo,xhi) for y,z in outline];f=[tuple(reversed(range(n))),tuple(range(n,2*n))]
 for i in range(n):j=(i+1)%n;f.append((i,j,n+j,n+i))
 return mesh(name,v,f,material)

def capsule_outline(a,b,r1,r2,N=48):
 dy,dz=b[0]-a[0],b[1]-a[1];phi=math.atan2(dz,dy);alpha=math.acos((r1-r2)/math.hypot(dy,dz));v=[]
 for j in range(N+1):ang=phi+alpha+(2*math.pi-2*alpha)*j/N;v.append((a[0]+r1*math.cos(ang),a[1]+r1*math.sin(ang)))
 for j in range(N+1):ang=phi-alpha+2*alpha*j/N;v.append((b[0]+r2*math.cos(ang),b[1]+r2*math.sin(ang)))
 return v

def wheel(name,center,tire_r,tire_half,metal,rubber,spokes=True):
 # Rounded but subtly flattened tread cross section; radial profile is tire outer envelope.
 profile=[(-tire_half*.45,tire_r-.027),(-tire_half*.90,tire_r-.021),(-tire_half,tire_r-.012),(-tire_half*.84,tire_r-.004),(-tire_half*.45,tire_r-.0008),(0,tire_r),(tire_half*.45,tire_r-.0008),(tire_half*.84,tire_r-.004),(tire_half,tire_r-.012),(tire_half*.90,tire_r-.021),(tire_half*.45,tire_r-.027)]
 N=128;verts=[];faces=[]
 for x,r in profile:
  for k in range(N):a=2*math.pi*k/N;verts.append((center[0]+x,center[1]+r*math.cos(a),center[2]+r*math.sin(a)))
 for j in range(len(profile)):
  for k in range(N):faces.append((j*N+k,j*N+(k+1)%N,((j+1)%len(profile))*N+(k+1)%N,((j+1)%len(profile))*N+k))
 mesh(name+' rubber tire',verts,faces,rubber,True)
 if not spokes:return
 rr=D['bike']['rim_radius'];ring_x(name+' rolled rim',center,rr,.010,metal,N=128,n=16)
 cyl(name+' hub barrel',(center[0]-.032,center[1],center[2]),(center[0]+.032,center[1],center[2]),.017,metal)
 for side in [-1,1]:
  cyl(name+' hub flange '+str(side),(side*.028-.002,center[1],center[2]),(side*.028+.002,center[1],center[2]),.027,metal)
 # 36 spokes: 18 holes per flange, alternating leading/trailing endpoints, three-cross angular offset.
 for k in range(36):
  side=-1 if k%2 else 1;angle=2*math.pi*k/36;flange=angle+(1 if (k//2)%2 else -1)*math.radians(60)
  a=(side*.028,center[1]+.025*math.cos(flange),center[2]+.025*math.sin(flange));b=(side*.004,center[1]+rr*math.cos(angle),center[2]+rr*math.sin(angle))
  cyl(name+' spoke %02d'%k,a,b,.00085,metal,8)
  q=Vector(b);toward=(Vector(a)-q).normalized();cyl(name+' nipple %02d'%k,q,q+toward*.011,.0015,metal,10)
 for side in [-1,1]:cyl(name+' axle nut '+str(side),(side*.062,center[1],center[2]),(side*.072,center[1],center[2]),.008,metal,6)
 cyl(name+' continuous axle',(-.072,center[1],center[2]),(.072,center[1],center[2]),.0045,metal,24)
 cyl(name+' inflation valve',(0,center[1],center[2]-rr+.001),(0,center[1],center[2]-rr+.026),.0028,metal,12)


def bicycle():
 global GROUP
 b=D['bike'];clear();GROUP='frame'
 paint=mat('Muted deep green painted steel',(.105,.175,.150),0,.34);steel=mat('Satin stainless steel',(.49,.53,.53),.88,.28);black=mat('Black tire rubber',(.021,.024,.023),0,.85);grip=mat('Dark brown elastomer grips',(.105,.062,.038),0,.69);seat=mat('Warm dark brown saddle vinyl',(.17,.095,.052),0,.52);resin=mat('Basket and guard molded polymer',(.065,.075,.067),0,.65);red=mat('Red reflector polymer',(.46,.015,.009),0,.29);amber=mat('Amber pedal reflector',(.65,.21,.012),0,.30);lens=mat('Headlamp translucent-look lens',(.72,.76,.70),0,.22);chainmat=mat('Lubricated chain steel',(.15,.17,.16),.75,.40)
 rear=tuple(b['rear_axle']);front=tuple(b['front_axle']);bb=tuple(b['bottom_bracket']);hl=tuple(b['head_lower']);hu=tuple(b['head_upper'])
 tube('Low step continuous curved main frame',smooth_path([bb,(0,.035,.322),(0,-.08,.375),(0,-.17,.49),(0,-.30,.64),tuple(Vector(hl)+(Vector(hu)-Vector(hl)).normalized()*.05)],12),.021,paint,28)
 seatbase=(0,.30,.671);tube('Seat tube',[bb,seatbase],.016,paint,24);tube('Head tube',[hl,hu],.019,paint,28)
 cyl('Bottom bracket shell',(-.035,bb[1],bb[2]),(.035,bb[1],bb[2]),.024,paint)
 cyl('Bottom bracket spindle',(-.114,bb[1],bb[2]),(.114,bb[1],bb[2]),.008,steel)
 for side in [-1,1]:
  tube('Curved chainstay '+str(side),smooth_path([(side*.031,bb[1],bb[2]),(side*.052,.26,.294),(side*.057,.43,.315),(side*.058,rear[1],rear[2])],6),.0105,paint,20)
  tube('Seatstay '+str(side),smooth_path([(side*.012,seatbase[1],seatbase[2]-.025),(side*.045,.340,.610),(side*.055,.400,.530),(side*.058,rear[1],rear[2])],8),.009,paint,20)
  o=box('Rear dropout plate '+str(side),(side*.058,rear[1]-.008,rear[2]+.008),(.006,.044,.038),steel,.006);difference(o,cyl('Rear axle bore',(side*.058-.01,rear[1],rear[2]),(side*.058+.01,rear[1],rear[2]),.0047,steel,24))
 cyl('Seatpost',(0,.30,.66),(0,.344,.79),.0125,steel);cyl('Seatpost collar',(0,.297,.663),(0,.306,.690),.018,steel)
 tube('Seat clamp lever',[(.021,.303,.679),(.045,.32,.68),(.05,.35,.68)],.0035,steel,16)
 # Custom saddle: rounded closed loft with narrow nose toward -Y and full seated rear.
 saddle_y=[-.12,-.09,-.035,.025,.075,.105];widths=[.011,.025,.059,.095,.093,.06];heights=[.008,.017,.026,.029,.028,.014];v=[];f=[];N=32
 for y,w,h in zip(saddle_y,widths,heights):
  for k in range(N):a=2*math.pi*k/N;v.append((w*math.cos(a),.33+y,.792+h*math.sin(a)))
 for j in range(len(saddle_y)-1):
  for k in range(N):f.append((j*N+k,j*N+(k+1)%N,(j+1)*N+(k+1)%N,(j+1)*N+k))
 f += [tuple(reversed(range(N))),tuple((len(saddle_y)-1)*N+k for k in range(N))];mesh('Sculpted padded saddle',v,f,seat,True)
 for side in [-1,1]:tube('Saddle supporting rail '+str(side),smooth_path([(side*.021,.25,.78),(side*.031,.29,.759),(side*.031,.39,.76),(side*.05,.405,.78)],6),.0035,steel,12)
 box('Saddle rail clamp',(0,.344,.767),(.055,.034,.025),steel,.005)
 GROUP='rear_wheel';wheel('Rear wheel',rear,b['tire_radius'],b['tire_half_width'],steel,black)
 GROUP='steering';wheel('Front wheel',front,b['tire_radius'],b['tire_half_width'],steel,black)
 steer_top=M.add(hu,M.mul(M.unit(M.sub(hu,hl)),.068));tube('Continuous fork steerer',[hl,hu,steer_top],.0125,steel,24)
 tube('Fork crown bridge',[(-.035,hl[1],hl[2]),(.035,hl[1],hl[2])],.017,paint,24)
 for side in [-1,1]:
  tube('Swept fork blade '+str(side),smooth_path([(side*.031,hl[1],hl[2]),(side*.047,-.475,.52),(side*.049,-.55,.38),(side*.049,front[1],front[2])],10),[.013-(.006*k/30) for k in range(31)],paint,24)
  o=box('Front dropout plate '+str(side),(side*.049,front[1]+.006,front[2]+.008),(.006,.028,.036),steel,.005);difference(o,cyl('Front axle bore',(side*.049-.01,front[1],front[2]),(side*.049+.01,front[1],front[2]),.0047,steel,24))
 # Handlebar curved semi-upright sweep. Ends provide 100mm grip landing each side.
 handlebars=[(-.272,-.205,1.045),(-.20,-.25,1.034),(-.13,-.30,1.006),(-.065,-.303,.978),(0,-.275,.968),(.065,-.303,.978),(.13,-.30,1.006),(.20,-.25,1.034),(.272,-.205,1.045)]
 tube('Swept semi-upright handlebar',smooth_path(handlebars,7),.0105,steel,24)
 tube('Handlebar stem extension',smooth_path([steer_top,(0,-.33,.965),(0,-.275,.968)],7),.014,steel,24)
 for side in [-1,1]:
  tube('Rubber grip '+str(side),[(side*.184,-.26,1.031),(side*.272,-.205,1.045)],.0155,grip,24)
  cyl('Bar end plug '+str(side),(side*.270,-.207,1.044),(side*.279,-.201,1.046),.0157,resin,24)
  box('Brake lever clamp '+str(side),(side*.178,-.263,1.027),(.021,.027,.024),steel,.005)
  tube('Curved brake lever '+str(side),smooth_path([(side*.176,-.275,1.025),(side*.191,-.295,1.002),(side*.23,-.265,.992),(side*.26,-.235,.997)],7),.0045,steel,16)
 # Front two-pivot caliper arches around the tyre, pads meet side rim faces at upper/rear sector.
 cp=(0,-.440,.678)
 cyl('Front caliper mounting bolt',(0,-.425,.670),(0,-.455,.670),.0045,steel,16)
 tube('Front caliper crown mounting bridge',[(0,-.440,.670),(0,-.440,.678)],.006,steel,16)
 for side in [-1,1]:
  tube('Front caliper arm '+str(side),smooth_path([(side*.012,-.440,.678),(side*.039,-.451,.672),(side*.044,-.466,.632),(side*.022,-.474,.603)],6),.005,steel,16)
  box('Front rim brake pad '+str(side),(side*.015,-.474,.603),(.008,.028,.011),black,.002)
  cyl('Front caliper pivot '+str(side),(side*.012,-.434,.678),(side*.012,-.446,.678),.006,steel,20)
 tube('Front brake cable service loop',smooth_path([(.178,-.27,1.026),(.18,-.34,.96),(.10,-.43,.84),(.045,-.44,.73),(.035,-.445,.680)],10),.0027,black,12)
 # Bell on one side only; no gear shifter on this single speed.
 ellipsoid('Handlebar bell',(-.11,-.306,1.035),(.023,.023,.014),steel,segments=24,rings=12);tube('Bell thumb tab',[(-.10,-.294,1.028),(-.09,-.277,1.026)],.004,resin,12)
 cyl('Bell mounting neck',(-.11,-.306,.995),(-.11,-.306,1.027),.006,steel,16)
 # Generic open polymer basket, real rounded edge and sparse molded grid. Supports attach to steering assembly.
 basket_z=.80;bottom_z=.78;top_z=1.035;yb=-.68
 for zz,w,dep in [(bottom_z,.28,.235),(top_z,.36,.291)]:
  pts=[(-w/2,yb-dep/2,zz),(w/2,yb-dep/2,zz),(w/2,yb+dep/2,zz),(-w/2,yb+dep/2,zz)]
  tube('Basket continuous rim '+str(zz),pts,.005,resin,16,True)
 for side in [-1,1]:
  for i in range(11):
   t=i/10;bot=(side*.14,yb-.1175+t*.235,bottom_z);top=(side*.18,yb-.1455+t*.291,top_z);tube('Basket side upright '+str(side)+' '+str(i),[bot,top],.0022,resin,10)
 for end in [-1,1]:
  for i in range(13):
   t=i/12;bot=(-.14+t*.28,yb+end*.1175,bottom_z);top=(-.18+t*.36,yb+end*.1455,top_z);tube('Basket end upright '+str(end)+' '+str(i),[bot,top],.0022,resin,10)
 for k in range(1,10):
  t=k/10;zz=bottom_z+t*(top_z-bottom_z);w=.28+.08*t;dep=.235+.056*t;tube('Basket horizontal grid '+str(k),[(-w/2,yb-dep/2,zz),(w/2,yb-dep/2,zz),(w/2,yb+dep/2,zz),(-w/2,yb+dep/2,zz)],.0018,resin,10,True)
 for x in [-.12,-.08,-.04,0,.04,.08,.12]:tube('Basket floor longitudinal '+str(x),[(x,yb-.1175,bottom_z),(x,yb+.1175,bottom_z)],.0025,resin,10)
 for y in [yb-.10,yb-.05,yb,yb+.05,yb+.10]:tube('Basket floor crossrib '+str(y),[(-.14,y,bottom_z),(.14,y,bottom_z)],.0025,resin,10)
 for side in [-1,1]:
  tube('Basket axle mounting stay '+str(side),[(side*.065,front[1],front[2]),(side*.065,-.66,.76),(side*.11,-.68,.775)],.004,steel,16)
  # Attach at actual tapered corner/grid4, not un-tapered upper-rim coordinates.
  t=.4;mount=(side*(.28+.08*t)/2,yb+(.235+.056*t)/2,bottom_z+t*(top_z-bottom_z))
  tube('Basket rear bracket '+str(side),[(side*.012,-.3633,.90),(side*.08,-.53,mount[2]),mount],.004,steel,16)
  box('Basket rear bracket clamp '+str(side),mount,(.012,.012,.018),steel,.002)
  cyl('Basket rear bracket clamp screw '+str(side),(mount[0],mount[1]-.008,mount[2]),(mount[0],mount[1]+.008,mount[2]),.003,steel,12)
 box('Front lamp housing',(0,-.735,.747),(.06,.042,.04),resin,.012);box('Front lamp lens',(0,-.758,.747),(.05,.005,.029),lens,.009)
 tube('Lamp basket hanger',[(0,-.735,.78),(0,-.735,.76)],.004,steel,12)
 # Block dynamo at fork side, roller touches tire sidewall by design; no generator simulation.
 cyl('Block dynamo body',(-.064,-.435,.590),(-.064,-.460,.624),.014,steel);cyl('Dynamo tire roller',(-.035,-.460,.624),(-.016,-.460,.624),.007,black,24)
 cyl('Dynamo roller spindle',(-.064,-.460,.624),(-.028,-.460,.624),.0035,steel,16)
 tube('Dynamo fork clamp',[(-.047,-.460,.60),(-.064,-.440,.60)],.005,steel,12)
 # Front fender + attached stays rotate with steering; rear remains fixed.
 def fender(prefix,center,a0,a1):
  verts=[];faces=[];N=88;crossN=12
  for i in range(N+1):
   a=a0+(a1-a0)*i/N
   for j in range(crossN+1):
    t=-math.pi/2+math.pi*j/crossN;x=.024*math.sin(t);rad=.344+.006*math.cos(t);verts.append((x,center[1]+rad*math.cos(a),center[2]+rad*math.sin(a)))
  for i in range(N):
   for j in range(crossN):k=i*(crossN+1)+j;faces.append((k,k+1,k+crossN+2,k+crossN+1))
  o=mesh(prefix+' curved steel fender',verts,faces,paint,True);q=o.modifiers.new('Fender sheet thickness','SOLIDIFY');q.thickness=.0015;bpy.context.view_layer.objects.active=o;bpy.ops.object.modifier_apply(modifier=q.name)
 fender('Front',front,-.20,math.pi+.22)
 for side in [-1,1]:
  for ang in [.25,2.85]:tube('Front mudguard stay '+str(side)+' '+str(ang),[(side*.058,front[1],front[2]),(side*.025,front[1]+.347*math.cos(ang),front[2]+.347*math.sin(ang))],.0027,steel,12)
 GROUP='frame';fender('Rear',rear,-.28,math.pi+.08)
 for side in [-1,1]:
  for ang in [.12,2.9]:tube('Rear mudguard stay '+str(side)+' '+str(ang),[(side*.065,rear[1],rear[2]),(side*.025,rear[1]+.347*math.cos(ang),rear[2]+.347*math.sin(ang))],.0027,steel,12)
 # Rear rack and stays, generic open grid.
 rack=[(-.065,.35,.712),(.065,.35,.712),(.065,.81,.712),(-.065,.81,.712)]
 tube('Rear carrier perimeter',rack,.006,steel,16,True)
 for y in [.39,.47,.55,.63,.71,.77]:tube('Carrier crossbar '+str(y),[(-.065,y,.712),(.065,y,.712)],.0038,steel,12)
 for side in [-1,1]:
  tube('Carrier axle strut '+str(side),[(side*.07,rear[1],rear[2]),(side*.065,.76,.707)],.0045,steel,16)
  tube('Carrier frame strut '+str(side),[(side*.010,.298,.660),(side*.065,.39,.707)],.0045,steel,16)
 # Rear roller-brake exterior on left. Reaction arm attached to chainstay.
 cyl('Rear roller brake finned shell',(-.049,rear[1],rear[2]),(-.031,rear[1],rear[2]),.055,steel)
 ring_x('Rear brake cooling rim',(-.050,rear[1],rear[2]),.050,.004,steel,N=72)
 tube('Rear brake reaction arm',[(-.05,rear[1],rear[2]),(-.05,.39,.303)],.006,steel,16)
 box('Brake reaction chainstay clamp',(-.052,.39,.303),(.025,.024,.023),steel,.004)
 # Distinct fixed casing support and movable cable link, informed by Shimano SI-IM31D.
 # This is a generic static exterior, not a force/return-spring simulation.
 tube('Rear brake fixed casing stop support',[(-.042,.46,.312),(-.061,.46,.280)],.0035,steel,16)
 cyl('Rear brake cable adjuster barrel',(-.061,.440,.280),(-.061,.460,.280),.0045,steel,20)
 cyl('Rear brake cable adjuster locknut',(-.061,.455,.280),(-.061,.460,.280),.006,steel,6)
 cyl('Rear brake actuator bearing',(-.048,.580,.296),(-.061,.580,.296),.007,steel,24)
 tube('Rear brake movable actuator link',[(-.061,.580,.296),(-.061,.550,.287),(-.061,.527,.280)],.0045,steel,16)
 cyl('Rear brake inner cable fixing bolt',(-.066,.527,.280),(-.056,.527,.280),.005,steel,16)
 cyl('Rear brake inner cable fixing nut',(-.069,.527,.280),(-.065,.527,.280),.006,steel,6)
 tube('Rear brake exposed inner cable',[(-.061,.460,.280),(-.061,.527,.280),(-.061,.540,.279)],.00085,chainmat,8)
 cyl('Rear brake cable end cap',(-.061,.537,.2792),(-.061,.543,.2788),.0016,steel,12)
 tube('Rear brake cable housing',smooth_path([(-.178,-.27,1.026),(-.16,-.20,.89),(-.035,-.30,.75),(-.03,-.20,.46),(-.04,.03,.32),(-.058,.36,.284),(-.061,.440,.280)],8),.0027,black,12)
 # Ring lock behind seat stays, bolt left retracted to avoid meaningless spoke intersections.
 ringpts=[(.047*math.cos(a),.38,.58+.047*math.sin(a)) for a in [math.pi*k/36 for k in range(37)]]
 tube('Rear ring lock open shackle housing',ringpts,.008,resin,16)
 for side in [-1,1]:
  box('Ring lock frame clamp '+str(side),(side*.04,.38,.59),(.015,.023,.027),steel,.003)
  tube('Ring lock clamp seatstay bridge '+str(side),[(side*.04,.38,.59),(side*.045,.340,.610)],.004,steel,16)
 # Enclosed drivetrain retains real hidden route for proof view.
 GROUP='drivetrain';r1,r2=M.gear_radii();x=b['chainline_x']
 for name,center,r,teeth in [('Chainring',bb,r1,b['chainring_teeth']),('Rear sprocket',rear,r2,b['rear_teeth'])]:
  cyl(name+' web',(x-.003,center[1],center[2]),(x+.003,center[1],center[2]),r-.003,chainmat,64)
  for k in range(teeth):
   a=2*math.pi*k/teeth;ob=box(name+' tooth '+str(k),(x,center[1]+r*math.cos(a),center[2]+r*math.sin(a)),(.005,.005,.006),chainmat,.001);ob.rotation_euler.x=a-math.pi/2
 chain=M.chain_path(28);tube('Continuous enclosed chain roller path',chain,.0025,chainmat,8,True)
 # Short pin details give chain scale without thousands of independent links.
 for i in range(0,len(chain),3):p=chain[i];cyl('Chain rivet '+str(i),(p[0]-.0038,p[1],p[2]),(p[0]+.0038,p[1],p[2]),.0013,steel,8)
 GROUP='chain_guard';outline=capsule_outline(bb[1:],rear[1:],r1+.015,r2+.013)
 for name,xlo,xhi in [('inner',.070,.072),('outer',.094,.096)]:
  ob=prism_yz('Full chain guard '+name+' sheet',outline,xlo,xhi,paint)
  for center,r in [(bb,.010),(rear,.009)]:difference(ob,cyl('Spindle aperture',(xlo-.01,center[1],center[2]),(xhi+.01,center[1],center[2]),r,steel,32))
 # Connect front/back along outline with finite perimeter strip; not a solid capsule.
 n=len(outline);verts=[(xx,y,z) for xx in [.071,.095] for y,z in outline];faces=[]
 for i in range(n):j=(i+1)%n;faces.append((i,j,n+j,n+i))
 ob=mesh('Chain guard perimeter wall',verts,faces,paint,True);q=ob.modifiers.new('Case wall thickness','SOLIDIFY');q.thickness=.0015;bpy.context.view_layer.objects.active=ob;bpy.ops.object.modifier_apply(modifier=q.name)
 for yy,zz in [(bb[1]-.03,bb[2]+.05),(.48,.37)]:cyl('Chaincase fixing screw',(.093,yy,zz),(.095,yy,zz),.003,steel,16)
 GROUP='cranks'
 for side in [-1,1]:
  ang=math.radians(25)+(math.pi if side==-1 else 0);end=(side*b['crank_x'],bb[1]+b['crank_length']*math.sin(ang),bb[2]-b['crank_length']*math.cos(ang));start=(side*b['crank_x'],bb[1],bb[2]);tube('Opposed crank arm '+str(side),[start,end],[.010,.007],steel,20)
  cyl('Crank spindle cap '+str(side),(side*.100,bb[1],bb[2]),(side*.115,bb[1],bb[2]),.013,steel,32)
  pc=(side*.16,end[1],end[2]);cyl('Pedal axle '+str(side),end,(side*.202,end[1],end[2]),.004,steel,20)
  box('Platform pedal '+str(side),pc,(.094,.071,.022),resin,.005)
  for y in [-.026,-.013,0,.013,.026]:box('Pedal grip rib '+str(side)+' '+str(y),(pc[0],pc[1]+y,pc[2]+.012),(.083,.003,.003),black,.0005)
  for sy in [-1,1]:box('Pedal amber reflector '+str(side)+' '+str(sy),(pc[0],pc[1]+sy*.036,pc[2]),(.062,.003,.011),amber,.002)
 GROUP='frame';box('Rear red reflector',(0,.904,.43),(.042,.012,.04),red,.006)
 # Apply parked frame pitch about front ground point, then adjust to exact tire min.
 bpy.context.view_layer.update()
 for o in list(bpy.context.scene.objects):
  if o.type=='MESH':
   for v in o.data.vertices:v.co=o.matrix_world@v.co
   o.matrix_world=Matrix.Identity(4)
   for v in o.data.vertices:v.co=M.park(v.co)
 front_tire=bpy.data.objects['Front wheel rubber tire'];ground=min(v.co.z for v in front_tire.data.vertices)
 for o in bpy.context.scene.objects:
  if o.type=='MESH':
   for v in o.data.vertices:v.co.z-=ground
 # Stand geometry is authored in parked-world coordinates and attached at rear axle.
 GROUP='stand';pivot=M.park(rear);pivot=(pivot[0],pivot[1],pivot[2]-ground)
 feet=[(-b['stand_foot_half_width'],b['stand_foot_y'],.008),(b['stand_foot_half_width'],b['stand_foot_y'],.008)]
 for side,foot in zip([-1,1],feet):
  tube('Paired stand leg '+str(side),smooth_path([(side*.074,pivot[1],pivot[2]),(side*.106,.545,.22),(side*.145,.51,.04),foot],8),.008,steel,20)
  box('Stand ground shoe '+str(side),(foot[0],foot[1],.004),(.040,.027,.008),black,.002)
  cyl('Stand pivot sleeve '+str(side),(side*.069,pivot[1],pivot[2]),(side*.082,pivot[1],pivot[2]),.016,steel,32)
 tube('Stand transverse brace',[(-.14,.515,.055),(-.14,.40,.045),(.14,.40,.045),(.14,.515,.055)],.006,steel,16)
 tube('Stand left foot press tab',[(-.14,.51,.04),(-.205,.51,.04),(-.205,.57,.04)],.006,steel,16)
 # Explicit locked-position tab/stop; spring shape is visualization only.
 GROUP='frame';box('Stand stationary stop',(-.085,pivot[1]-.018,pivot[2]-.015),(.012,.026,.018),steel,.002)
 GROUP='stand';tube('Stand lock lever',[(-.086,pivot[1]-.015,pivot[2]-.012),(-.10,pivot[1]-.045,pivot[2]-.045),(-.12,pivot[1]-.045,pivot[2]-.045)],.0045,steel,12)
 cyl('Stand lock lever pivot fastener',(-.074,pivot[1]-.011,pivot[2]-.009),(-.092,pivot[1]-.011,pivot[2]-.009),.004,steel,20)
 spring=[]
 for i in range(73):t=i/72;spring.append((-.091+.004*math.cos(t*12*math.pi),pivot[1]-.018-t*.05,pivot[2]-.032-t*.07+.004*math.sin(t*12*math.pi)))
 tube('Stand return spring visual only',spring,.0012,steel,8)
 GROUP='frame';tube('Stand spring fixed upper hook',[(-.085,pivot[1]-.018,pivot[2]-.021),spring[0]],.0025,steel,12)
 GROUP='stand';tube('Stand spring moving lower hook',[spring[-1],(-.106,.545,.22)],.0025,steel,12)
 return {'park_ground_adjustment_m':ground,'parked_rear_axle':pivot,'stand_ground_contact_centres':[[-.155,.50,0],[.155,.50,0]],'front_contact_y':min(front_tire.data.vertices,key=lambda v:v.co.z).co.y,'inferences':b['inferred']}


def handcart():
 global GROUP
 c=D['cart'];clear();GROUP='deck'
 polymer=mat('Blue grey molded platform polymer',(.075,.19,.27),0,.61);forkmat=mat('Molded reinforced polymer caster forks',(.065,.15,.20),0,.60);rubber=mat('Low gloss grey rubber wheels',(.15,.16,.15),0,.84);steel=mat('Satin zinc plated hinge steel',(.48,.51,.50),.86,.31);paint=mat('Satin light grey coated handle',(.44,.47,.45),0,.36);pad=mat('Dark rubber deck pads',(.055,.065,.061),0,.9)
 # Deck is a finite top skin with open under-ribs and a perimeter wall, not a solid block.
 w,l=c['deck_size'];top=c['deck_top'];th=c['deck_thickness'];skin=.008
 box('Deck load bearing top skin',(0,0,top-skin/2),(w,l,skin),polymer,.005)
 # Perimeter stops inside skin: no coincident exposed z=top faces.
 wall_h=th-skin+.002;wall_z=top-th+wall_h/2
 for x in [-w/2+.008,w/2-.008]:box('Deck lateral perimeter wall '+str(x),(x,0,wall_z),(.016,l-.014,wall_h),polymer,.006)
 for y in [-l/2+.008,l/2-.008]:box('Deck end perimeter wall '+str(y),(0,y,wall_z),(w-.015,.016,wall_h),polymer,.006)
 for x in [-.14,-.07,0,.07,.14]:box('Deck inferred underside longitudinal rib '+str(x),(x,0,top-.0205),(.006,l-.031,.029),polymer,.0015)
 for y in [-.29,-.19,-.09,.01,.11,.21,.30]:box('Deck inferred underside crossrib '+str(y),(0,y,top-.0205),(w-.031,.006,.029),polymer,.0015)
 # One continuous molded deck; eliminate all exposed coincident faces at rib
 # crossings/perimeter corners and provide genuine skin-to-rib load paths.
 deck=bpy.data.objects['Deck load bearing top skin']
 for part in [o for o in list(bpy.context.scene.objects) if o.type=='MESH' and o!=deck and o.name.startswith('Deck ')]:
  bpy.context.view_layer.objects.active=deck
  mod=deck.modifiers.new('Continuous molded deck union','BOOLEAN');mod.operation='UNION';mod.solver='EXACT';mod.object=part
  bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(part,do_unlink=True)
 import bmesh
 bm=bmesh.new();bm.from_mesh(deck.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-7)
 bm.verts.index_update();seen=set();duplicates=[]
 for face in bm.faces:
  key=tuple(sorted(v.index for v in face.verts))
  if key in seen:duplicates.append(face)
  else:seen.add(key)
 if duplicates:bmesh.ops.delete(bm,geom=duplicates,context='FACES_ONLY')
 bmesh.ops.dissolve_degenerate(bm,edges=list(bm.edges),dist=1e-8)
 wire=[e for e in bm.edges if not e.link_faces]
 if wire:bmesh.ops.delete(bm,geom=wire,context='EDGES')
 bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
 print('DECK_TOPOLOGY',len(duplicates),'duplicate faces removed',[(len(e.link_faces),[list(v.co) for v in e.verts]) for e in bm.edges if len(e.link_faces)!=2])
 assert all(len(e.link_faces)==2 for e in bm.edges),'Molded deck is not manifold'
 bmesh.ops.triangulate(bm,faces=list(bm.faces));bm.to_mesh(deck.data);bm.free()
 deck['construction']='Unified skin, perimeter and crossing ribs; no separate coplanar exposed rib faces'
 for x in [-.135,.135]:
  for y in [-.19,.15]:cyl('Non slip inset deck pad '+str(x)+str(y),(x,y,top-.001),(x,y,top+.001),.018,pad,48)
 # Shallow raised ribs with real geometry, without branded deck embossing.
 for j in range(39):
  y=-.32+j*.015
  for s in [-1,1]:box('Deck traction rib '+str(j)+' '+str(s),(s*.115,y,top+.0006),(.18,.002,.0012),polymer,.0005,segments=1)
 def make_caster(front,side):
  global GROUP
  GROUP=('swivel' if front else 'fixed')+'_caster_'+str(side)
  pivot=(side*c['caster_x'],-c['caster_y'] if front else c['caster_y'],c['caster_mount_z']);ax=M.caster_axle(front,0,side);wx,wy,wz=ax
  pitch=(.071,.071) if front else (.080,.045)
  mount_size=(.091,.091) if front else (.10,.068)
  box(GROUP+' ribbed mounting plate',(pivot[0],pivot[1],pivot[2]-.006),(*mount_size,.012),forkmat,.006)
  # Bosses join under-ribs to caster plates; four through fasteners.
  for dx in [-pitch[0]/2,pitch[0]/2]:
   for dy in [-pitch[1]/2,pitch[1]/2]:
    px,py=pivot[0]+dx,pivot[1]+dy
    cyl(GROUP+' deck mounting boss',(px,py,top-.032),(px,py,top-.008),.008,polymer,20)
    cyl(GROUP+' plate bolt shank',(px,py,pivot[2]-.014),(px,py,top+.002),.0027,steel,16)
    cyl(GROUP+' upper bolt head',(px,py,top+.001),(px,py,top+.004),.005,steel,6)
    cyl(GROUP+' underside nut',(px,py,pivot[2]-.016),(px,py,pivot[2]-.010),.005,steel,6)
  if front:
   cyl(GROUP+' vertical swivel kingpin',(pivot[0],pivot[1],.094),(pivot[0],pivot[1],.129),.007,steel,24)
   cyl(GROUP+' upper swivel collar',(pivot[0],pivot[1],.116),(pivot[0],pivot[1],.125),.027,forkmat,48)
   torus_z(GROUP+' swivel parting seam',(pivot[0],pivot[1],.119),.026,.0012,steel)
   cyl(GROUP+' fork crown',(pivot[0],pivot[1]+.005,.108),(pivot[0],pivot[1]+.005,.119),.024,forkmat,48)
  else:box(GROUP+' fixed upright crown',(pivot[0],pivot[1],.118),(.047,.039,.022),forkmat,.005)
  # Two fork cheeks, explicit inner air gap wider than tire.
  for ss in [-1,1]:
   xx=wx+ss*.021
   outline=[(wy-.015,.039),(wy+.016,.038),(wy+.021,.057),(pivot[1]+.016,.117),(pivot[1]-.017,.117),(wy-.022,.063)]
   o=prism_yz(GROUP+' supporting fork cheek '+str(ss),outline,xx-.004,xx+.004,forkmat);bevel(o,.003)
   difference(o,cyl('Caster axle actual bore',(xx-.01,wy,wz),(xx+.01,wy,wz),.0041,steel,24))
   cyl(GROUP+' axle cap '+str(ss),(wx+ss*.024,wy,wz),(wx+ss*.028,wy,wz),.0125,forkmat,40)
  wheel(GROUP+' wheel',(wx,wy,wz),c['wheel_radius'],c['wheel_half_width'],steel,rubber,False)
  # Wheel profile helper uses city-tire radial depth; correct caster hub fills its center.
  cyl(GROUP+' polymer wheel hub',(wx-.014,wy,wz),(wx+.014,wy,wz),.032,forkmat,64)
  cyl(GROUP+' steel through axle',(wx-.029,wy,wz),(wx+.029,wy,wz),.004,steel,24)
  for ss in [-1,1]:ring_x(GROUP+' hub lip '+str(ss),(wx+ss*.015,wy,wz),.027,.002,forkmat,N=48,n=6)
 for front in [True,False]:
  for side in [-1,1]:make_caster(front,side)
 GROUP='hinge_fixed';py,pz=c['hinge_pivot'][1:]
 # The real slanted slot is cut through BOTH cheek plates. The separate lock pin
 # slides along it before rotation; stationary cheeks are never parented to handle.
 slot=capsule_outline(c['lock_slot_lower_yz'],c['lock_slot_upper_yz'],c['slot_radius'],c['slot_radius'],20)
 for side in [-1,1]:
  hx=side*c['handle_half_width'];box('Hinge base shoe '+str(side),(hx,.298,.177),(.056,.078,.014),steel,.003)
  for yy in [.276,.325]:
   cyl('Hinge deck anchor '+str(side)+' '+str(yy),(hx,yy,.135),(hx,yy,.187),.0035,steel,20)
   cyl('Hinge anchor nut '+str(side)+' '+str(yy),(hx,yy,.134),(hx,yy,.141),.006,steel,6)
   cyl('Hinge anchor head '+str(side)+' '+str(yy),(hx,yy,.183),(hx,yy,.188),.006,steel,6)
  for offset in c['cheek_x_offsets']:
   xx=hx+offset
   outline=[(.255,.181),(.340,.181),(.340,.221),(.327,.247),(.298,.249),(.272,.226)]
   ob=prism_yz('Stationary open slot cheek '+str(side)+' '+str(offset),outline,xx-.0025,xx+.0025,steel)
   difference(ob,prism_yz('Slanted slot through cutter',slot,xx-.008,xx+.008,steel))
   difference(ob,cyl('Upper pivot bore cutter',(xx-.01,py,pz),(xx+.01,py,pz),.0053,steel,32));bevel(ob,.0008,2)
  # Rear cradle stays low enough to clear rotating handle lower end.
  box('Stationary rear cradle '+str(side),(hx,.332,.183),(.036,.006,.010),steel,.002)
  cyl('Hinge upper pivot '+str(side),(hx-.027,py,pz),(hx+.027,py,pz),.005,steel,32)
  for ss in [-1,1]:cyl('Hinge pivot end cap '+str(side)+' '+str(ss),(hx+ss*.026,py,pz),(hx+ss*.030,py,pz),.008,steel,32)
 GROUP='handle';r=c['handle_tube_radius'];hw=c['handle_half_width'];zt=c['handle_top']-r;bend=.055
 pts=[(-hw,py,c['handle_lower_z']),(-hw,py,zt-bend)]
 for k in range(1,13):a=math.pi-math.pi/2*k/12;pts.append((-hw+bend+bend*math.cos(a),py,zt-bend+bend*math.sin(a)))
 pts.append((hw-bend,py,zt))
 for k in range(1,13):a=math.pi/2-math.pi/2*k/12;pts.append((hw-bend+bend*math.cos(a),py,zt-bend+bend*math.sin(a)))
 pts.append((hw,py,c['handle_lower_z']));tube('Continuous folding U handle',pts,r,paint,28)
 # Sheet brace leaves foot access to release bar well below it.
 box('Handle sheet cross brace',(0,py,.516),(.361,.006,.125),paint,.006)
 for zz in [.471,.56]:box('Handle brace rolled bead '+str(zz),(0,py-.004,zz),(.32,.005,.004),paint,.002)
 for side in [-1,1]:
  hx=side*hw
  for zz in [.47,.56]:cyl('Handle brace rivet '+str(side)+' '+str(zz),(hx,py-.009,zz),(hx,py+.009,zz),.0035,steel,16)
  # Generic lock tongue: upper pivot round bore and LOWER OPEN notch. Lower
  # release pin sits in notch upright, then translates down out of it.
  outline=c['lock_tongue_outline_yz']
  tongue=prism_yz('Moving handle lock tongue '+str(side),outline,hx-.008,hx+.008,steel)
  difference(tongue,cyl('Tongue pivot hole',(hx-.015,py,pz),(hx+.015,py,pz),.0053,steel,32))
  # notch at upper slot end, extended downward to open edge, not a closed lock bore
  sy,sz=c['lock_slot_upper_yz'];notch_outline=capsule_outline((sy-.008,sz-.025),(sy,sz),.0054,.0054,16)
  difference(tongue,prism_yz('Open lock engagement notch',notch_outline,hx-.015,hx+.015,steel))
  tube('Handle pivot sleeve connection '+str(side),[(hx,py,pz),(hx,py,.265)],.015,paint,24)
 GROUP='lock_release';lp=M.lock_pin(False)
 cyl('Foot operated transverse release bar',(-hw-.029,lp[1],lp[2]),(hw+.029,lp[1],lp[2]),c['lock_pin_radius'],steel,32)
 for side in [-1,1]:
  hx=side*hw
  for ss in [-1,1]:cyl('Release retaining washer '+str(side)+' '+str(ss),(hx+ss*.025,lp[1],lp[2]),(hx+ss*.028,lp[1],lp[2]),.007,steel,24)
 # Foot sleeve is central and clear of the two handle uprights / fixed cheeks.
 cyl('Release bar central foot sleeve',(-.075,lp[1],lp[2]),(.075,lp[1],lp[2]),.007,pad,32)
 return {'hinge_pivot_m':c['hinge_pivot'],'lock_release_path_m':[M.lock_pin(False),M.lock_pin(True)],'foot_access_region_m':{'x':[-.075,.075],'y':[.24,.30],'z':[.18,.42]},'inferences':c['inferred']}


def geometry_stats():
 verts=[];tris=0;bad=0
 for o in bpy.context.scene.objects:
  if o.type!='MESH':continue
  o.data.calc_loop_triangles();tris+=len(o.data.loop_triangles)
  for t in o.data.loop_triangles:
   if t.area<1e-14:bad+=1
  verts += [o.matrix_world@v.co for v in o.data.vertices]
 lo=[min(v[k] for v in verts) for k in range(3)];hi=[max(v[k] for v in verts) for k in range(3)]
 return {'triangles':tris,'zero_area_triangles':bad,'bounds_min_m':lo,'bounds_max_m':hi,'dimensions_m':[h-l for h,l in zip(hi,lo)],'mesh_objects':len([o for o in bpy.context.scene.objects if o.type=='MESH'])}

def save(slug,title,notes):
 out=ROOT/'assets'/slug;out.mkdir(parents=True,exist_ok=True);bpy.context.view_layer.update()
 meshes=[o for o in bpy.context.scene.objects if o.type=='MESH']
 # Apply object transforms, keep semantic parts separate and editable.
 for o in meshes:
  bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o;bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
 bpy.ops.object.select_all(action='DESELECT')
 for o in meshes:o.select_set(True)
 blend=out/(slug+'.blend');glb=out/(slug+'.glb');bpy.ops.wm.save_as_mainfile(filepath=str(blend))
 bpy.ops.export_scene.gltf(filepath=str(glb),export_format='GLB',use_selection=True,export_extras=True,export_apply=True)
 meta={'slug':slug,'title':title,'units':'metres','origin':'Ground plane at object-centred XY datum','original_authoring':'Procedural original mesh, manufacturer references for construction only','scope':'Static diorama prop; bounded geometry diagnostics, not certified mechanics','status':'unreviewed build',**geometry_stats(),'design_numeric_tests':M.numeric_design_tests(),'construction_notes':notes,'mechanical_groups':{g:[o.name for o in meshes if o.get('mechanical_group')==g] for g in sorted({o.get('mechanical_group') for o in meshes})},'files':{p.name:{'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in [blend,glb]}}
 (out/'metadata.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n')
 print('ASSET_WRITTEN',slug,json.dumps(meta['files']))

if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--asset',choices=['all','city_bicycle','folding_platform_handcart'],default='all');args=ap.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
 for slug,title,fn in [('city_bicycle','街乗りシティ自転車',bicycle),('folding_platform_handcart','折りたたみ平台車',handcart)]:
  if args.asset in ['all',slug]:save(slug,title,fn())
