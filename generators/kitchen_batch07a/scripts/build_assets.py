import bpy, bmesh, math, json, hashlib, sys
import numpy as np
from pathlib import Path
from mathutils import Vector, Matrix
from scipy.spatial import Delaunay, cKDTree
from scipy.interpolate import PchipInterpolator
R=Path(__file__).resolve().parents[1]
bpy.context.preferences.filepaths.save_version=0
TAU=math.tau

def clean():
 bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
 for m in list(bpy.data.materials):bpy.data.materials.remove(m)
def mat(n,c,metal=0,rough=.4):
 m=bpy.data.materials.new(n);m.use_nodes=True;m.diffuse_color=(*c,1);p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*c,1);p.inputs['Metallic'].default_value=metal;p.inputs['Roughness'].default_value=rough;return m
def mesh(n,v,f,m):
 d=bpy.data.meshes.new(n);d.from_pydata(v,[],f);d.update();o=bpy.data.objects.new(n,d);bpy.context.collection.objects.link(o);d.materials.append(m)
 bm=bmesh.new();bm.from_mesh(d);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(d);bm.free()
 for p in d.polygons:p.use_smooth=True
 return o
def apply(o,typ,**kw):
 bpy.context.view_layer.objects.active=o;q=o.modifiers.new(typ,typ)
 for k,v in kw.items():setattr(q,k,v)
 bpy.ops.object.modifier_apply(modifier=q.name)
def solid(o,t):apply(o,'SOLIDIFY',thickness=t,offset=-1,use_even_offset=True)
def cut(o,c):
 apply(o,'BOOLEAN',operation='DIFFERENCE',solver='EXACT',object=c);bpy.data.objects.remove(c,do_unlink=True)
def ground(o):
 z=min((o.matrix_world@v.co).z for v in o.data.vertices);o.location.z-=z

def stable_rest(o):
 from scipy.spatial import ConvexHull
 o.data.calc_loop_triangles();co=np.array([list(v.co) for v in o.data.vertices]);vol=0.;weighted=np.zeros(3)
 for tri in o.data.loop_triangles:
  a,b,c=co[list(tri.vertices)];w=float(np.dot(a,np.cross(b,c)))/6;vol+=w;weighted+=w*(a+b+c)/4
 com=weighted/vol;hull=ConvexHull(co);candidates=[]
 for inds,eq in zip(hull.simplices,hull.equations):
  normal=eq[:3]
  if normal[2]>-.8:continue
  a,b,c=co[inds];proj=com-(np.dot(normal,com)+eq[3])*normal;u=b-a;v=c-a;w=proj-a
  uu=np.dot(u,u);vv=np.dot(v,v);uv=np.dot(u,v);wu=np.dot(w,u);wv=np.dot(w,v);den=uu*vv-uv*uv
  if den<1e-22:continue
  beta=(vv*wu-uv*wv)/den;gamma=(uu*wv-uv*wu)/den
  if beta>=-1e-7 and gamma>=-1e-7 and beta+gamma<=1+1e-7:candidates.append((math.acos(-normal[2]),normal,inds))
 assert candidates,'No stable near-horizontal support facet'
 angle,normal,inds=min(candidates,key=lambda c:c[0]);rotation=Vector(normal).rotation_difference(Vector((0,0,-1)))
 for v in o.data.vertices:v.co=rotation@v.co
 o['rest_rotation_degrees']=math.degrees(angle);o['rest_method']='Minimum-rotation convex hull support facet contains projected exact solid-volume center of mass.'
 ground(o)

def colander():
 m=mat('18-8 stainless satin',(.58,.61,.64),1,.29)
 # Unfolded radial developed coordinates preserve a near-even punched hole scale on the curved sheet.
 # Profile based on official silhouette; exact plate gauge and hole pitch are generic assumptions.
 S=np.array([0,.047,.057,.070,.090,.112,.137,.154]);RAD=np.array([0,.047,.056,.065,.077,.091,.108,.1165]);Z=np.array([.00065,.00065,.0022,.008,.025,.047,.073,.084])
 pr=PchipInterpolator(S,RAD);pz=PchipInterpolator(S,Z)
 pitch=.006;hr=.00135;centers=[]
 for j in range(-30,31):
  for i in range(-30,31):
   x=(i+.5*(j%2))*pitch;y=j*pitch*math.sqrt(3)/2
   if math.hypot(x,y)<.149:centers.append((x,y))
 points=[]
 for x,y in centers:
  for k in range(12):a=TAU*k/12;points.append((x+hr*math.cos(a),y+hr*math.sin(a)))
 nboundary=320;start=len(points)
 for k in range(nboundary):a=TAU*k/nboundary;points.append((.154*math.cos(a),.154*math.sin(a)))
 xy=np.array(points);tri=Delaunay(xy);cen=xy[tri.simplices].mean(axis=1);dist,_=cKDTree(centers).query(cen)
 faces=[tuple(t) for t,ok in zip(tri.simplices,dist>hr*.99) if ok]
 vertices=[]
 for x,y in points:
  s=math.hypot(x,y);r=float(pr(s));z=float(pz(s));vertices.append((x*r/s,y*r/s,z))
 # Integral lip rolls outward and down. No separate overlaid rim surface.
 last=start
 for r,z in [(.1174,.0845),(.1183,.0848),(.1188,.0845),(.119,.0840),(.1188,.0835),(.1184,.08325)]:
  this=len(vertices)
  for k in range(nboundary):a=TAU*k/nboundary;vertices.append((r*math.cos(a),r*math.sin(a),z))
  for k in range(nboundary):q=(k+1)%nboundary;faces.append((last+k,this+k,this+q,last+q))
  last=this
 o=mesh('Continuous punched bowl and rolled rim',vertices,faces,m);solid(o,.00055);o.data.set_sharp_from_angle(angle=math.radians(60));ground(o)
 o['hole_count']=len(centers);o['sheet_gauge_m']=.00055;o['hole_diameter_m']=2*hr;o['construction']='Single contiguous stamped perforated sheet and integral rolled rim; no separate attachments.'
 return {'references':['https://yanagi-design.or.jp/catalog/4163/'],'source_dimensions_m':[.238,.238,.086],'inferred':['0.55mm sheet gauge','2.7mm perforations on6mm developed hex pitch','Generic unfolded bowl curvature; no brand tracing'],'hole_count':len(centers)}

def ladle():
 m=mat('18-8 stainless brushed',(.6,.62,.64),1,.27)
 # Bowl surface center fan plus regularly spaced smooth radial rings, handle extends actual rim edge.
 N=96;nr=28;v=[(0,0,.0009)];f=[]
 for j in range(1,nr+1):
  t=j/nr;phi=t*math.pi/2;r=.037*math.sin(phi);z=.0009+.024*(1-math.cos(phi))
  for k in range(N):a=TAU*k/N;v.append((r*math.cos(a),r*math.sin(a),z))
 for k in range(N):f.append((0,1+k,1+(k+1)%N))
 for j in range(nr-1):
  for k in range(N):q=(k+1)%N;a=1+j*N;f.append((a+k,a+q,a+N+q,a+N+k))
 # Twelve-segment neck spans +/-11.4mm on rear rim, contracts into a13mm channeled grip.
 ids=[1+(nr-1)*N+k for k in range(19,30)];last=ids
 rows=[(.039,.030,.011),(.041,.037,.0085),(.042,.047,.0068)]
 for j in range(1,33):t=j/32;rows.append((.042+.026*t,.047+.194*t,.0068-.0006*t))
 # Tip returns through180 degrees, yielding a genuine open9mm hook throat.
 for j in range(1,19):a=math.pi*j/18;rows.append((.068+.006*(1-math.cos(a)),.241+.006*math.sin(a),.0062))
 rows.extend([(.080,.236,.0061),(.080,.231,.0058)])
 for rid,(cy,cz,w) in enumerate(rows):
  ids=[]
  for k in range(11):
   u=-1+2*k/10;ids.append(len(v));v.append((-u*w,cy+(.0012*(1-u*u) if rid>2 else 0),cz))
  for k in range(10):f.append((last[k],last[k+1],ids[k+1],ids[k]))
  last=ids
 o=mesh('One-piece pressed ladle bowl neck channeled handle and hook',v,f,m);solid(o,.0009)
 # Resting pose: rotate use-axis towards table until bowl exterior and handle hook nearly share support.
 from scipy.optimize import brentq
 coords=[vert.co.copy() for vert in o.data.vertices]
 bowl=[co for co in coords if co.z<=.225];hook=[co for co in coords if co.z>.225]
 def lowest(group,a):return min(co.y*math.sin(a)+co.z*math.cos(a) for co in group)
 angle=brentq(lambda a:lowest(hook,a)-lowest(bowl,a),math.radians(-85),math.radians(-70))
 o['rest_rotation_x_degrees']=math.degrees(angle)
 rot=Matrix.Rotation(angle,4,'X')
 for vert in o.data.vertices:
  vert.co=rot@vert.co;vert.co.x*=-1;vert.co.y*=-1
 o['front_blend']='-Y; open cavity visible from front'
 ground(o)
 o['sheet_gauge_m']=.0009;o['construction']='One connected pressed sheet; neck shares11rim vertices with bowl. Integral returned storage hook.'
 return {'references':['https://www.muji.com/sg/products/cmdty/detail/4550002882761'],'source_length_m':.27,'inferred':['0.9mm gauge','74mm bowl width and24mm depth','13mm grip and6mm hook bend radius','Resting table pose, not upright unsupported pose']}

def woodmat():
 m=mat('Light rubberwood subtle longitudinal fibers',(.68,.48,.26),0,.52)
 # Original finite raster grain: sparse discontinuous pores and irregular longitudinal fibers.
 # No tiled sine bands, shader noise, fake geometry grooves, logos or downloaded texture.
 from PIL import Image,ImageDraw,ImageFilter
 rng=np.random.default_rng(707);N=1024
 arr=np.empty((N,N,3),dtype=np.uint8);arr[:]=[207,171,119]
 arr=np.clip(arr.astype(float)+rng.normal(0,.6,(N,N,1)),0,255).astype('uint8');im=Image.fromarray(arr);draw=ImageDraw.Draw(im)
 for i in range(3100):
  x=float(rng.uniform(0,N));y=float(rng.uniform(-100,N));le=float(rng.uniform(4,130));dr=float(rng.uniform(-2,2));c=int(rng.uniform(-17,8));col=tuple(int(a+c) for a in [207,171,119]);draw.line([(x,y),(x+dr*.3,y+le*.5),(x+dr,y+le)],fill=col,width=1)
 im=im.filter(ImageFilter.GaussianBlur(.35));pix=np.asarray(im).astype('float32')/255;alpha=np.ones((N,N,1),dtype='float32');rgba=np.concatenate([pix,alpha],2)
 image=bpy.data.images.new('Original restrained rubberwood longitudinal albedo',width=N,height=N);image.pixels.foreach_set(rgba[::-1].ravel());image.pack();nd=m.node_tree.nodes.new('ShaderNodeTexImage');nd.image=image;m.node_tree.links.new(nd.outputs['Color'],m.node_tree.nodes.get('Principled BSDF').inputs['Base Color']);return m

def spatula():
 m=woodmat()
 # Sampled asymmetrical rubberwood paddle perimeter: broad near-flat bevelled leading edge, thin neck, comfortable straight grip.
 # PCHIP smooth width/center and ellipse corners avoid straight polygon transitions.
 ys=np.array([-.145,-.143,-.138,-.128,-.11,-.09,-.07,-.05,-.025,0,.04,.09,.13,.143,.145])
 left=np.array([-.026,-.031,-.034,-.035,-.035,-.032,-.023,-.014,-.009,-.008,-.0087,-.0095,-.0102,-.0102,-.0089])
 right=np.array([.017,.025,.030,.033,.035,.034,.029,.018,.010,.008,.0087,.0095,.0102,.0102,.0089])
 pl=PchipInterpolator(ys,left);pr=PchipInterpolator(ys,right)
 # Smooth longitudinal top and underside with a real tapered scraping edge.
 th=PchipInterpolator([-.145,-.13,-.10,-.05,0,.10,.14,.145],[.0007,.0023,.0037,.0045,.005,.006,.005,.005])
 count=180;N=32;v=[];f=[]
 for j in range(count+1):
  y=-.145+.29*j/count;l=float(pl(y));r=float(pr(y));c=(l+r)/2;w=max(.0002,(r-l)/2);t=float(th(y))
  for k in range(N):a=TAU*k/N;sn=math.sin(a);co=math.cos(a);v.append((c+w*math.copysign(abs(co)**.55,co),y,.006+t*math.copysign(abs(sn)**.55,sn)))
 for j in range(count):
  for k in range(N):q=(k+1)%N;a=j*N;f.append((a+k,a+N+k,a+N+q,a+q))
 f.extend([tuple(reversed(range(N))),tuple(count*N+k for k in range(N))]);o=mesh('One-piece tapered asymmetric rubberwood paddle',v,f,m)
 bpy.ops.mesh.primitive_cylinder_add(vertices=64,radius=.004,depth=.05,location=(0,.134,.006));cut(o,bpy.context.object)
 apply(o,'BEVEL',width=.00065,segments=4,limit_method='ANGLE',angle_limit=.6)
 apply(o,'TRIANGULATE')
 bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-7);bmesh.ops.dissolve_degenerate(bm,edges=list(bm.edges),dist=1e-7);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free()
 for old_uv in list(o.data.uv_layers):o.data.uv_layers.remove(old_uv)
 uv=o.data.uv_layers.new(name='Longitudinal wood grain');uv.active_render=True;o.data.uv_layers.active=uv
 for p in o.data.polygons:
  for li in p.loop_indices:
   vert=o.data.vertices[o.data.loops[li].vertex_index].co;uv.data[li].uv=((vert.x+.045)/.09,(vert.y+.15)/.30)
 stable_rest(o);o['construction']='One carved solid rubberwood piece with real through hanging hole and tapered scraping tip.'
 return {'references':['https://www.muji.com/sg/products/cmdty/detail/4550512963073'],'source_dimensions_m':[.07,.012,.29],'inferred':['8mm hanging hole','Paddle curve and tip taper','Subtle original generic rubberwood grain, not a photographic replica']}

def save(slug,fn):
 clean();detail=fn();sc=bpy.context.scene;sc.unit_settings.system='METRIC';sc.unit_settings.scale_length=1
 obs=[o for o in sc.objects if o.type=='MESH'];bpy.ops.object.select_all(action='DESELECT')
 for o in obs:o.select_set(True)
 bpy.context.view_layer.objects.active=obs[0];bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
 out=R/'assets'/slug;out.mkdir(parents=True,exist_ok=True)
 blend=out/(slug+'.blend');glb=out/(slug+'.glb');bpy.ops.wm.save_as_mainfile(filepath=str(blend),compress=True)
 bpy.ops.export_scene.gltf(filepath=str(glb),export_format='GLB',use_selection=True,export_yup=True,export_apply=True,export_extras=True)
 vs=[o.matrix_world@v.co for o in obs for v in o.data.vertices];lo=[min(v[i] for v in vs) for i in range(3)];hi=[max(v[i] for v in vs) for i in range(3)]
 tris=0
 for o in obs:o.data.calc_loop_triangles();tris+=len(o.data.loop_triangles)
 detail.update(id=slug,title_ja={'stainless_ladle': 'お玉', 'stainless_perforated_colander': 'ざる', 'wood_cooking_spatula': '木べら'}[slug],revision={'stainless_ladle':5,'stainless_perforated_colander':2,'wood_cooking_spatula':5}[slug],dimensions_m=[hi[i]-lo[i] for i in range(3)],bounds_min=lo,bounds_max=hi,triangles=tris,mesh_objects=len(obs),units='meter',up_axis_blend='Z',up_axis_glb='Y',photography_status='Not authorized; independent gate pending',files={p.suffix[1:]:{'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in [blend,glb]})
 (out/'metadata.json').write_text(json.dumps(detail,indent=2)+'\n');print('ASSET_DONE',slug,tris)
if __name__=='__main__':
 assets={'stainless_ladle':ladle,'stainless_perforated_colander':colander,'wood_cooking_spatula':spatula}
 args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
 for slug,fn in assets.items():
  if not args or slug in args:save(slug,fn)
