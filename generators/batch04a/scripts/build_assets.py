import sys, random
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import *
IDS=['whole_red_apple']
TITLES=['りんご','スライス食パン','海苔巻きおにぎり']
def texmat(n,base,kind,N=1024):
 m=mat(n,base,0,.43 if kind=='apple' else .88);rng=np.random.default_rng(840+len(kind));y,x=np.mgrid[0:N,0:N]/N;rgb=np.zeros((N,N,3),np.float32)
 if kind=='apple':
  streak=.5+.5*np.sin(x*160+4*np.sin(y*9+x*25)+2*np.sin(y*21+x*8));patch=np.clip(.45+.4*np.sin(x*13+y*3)+.15*np.sin(x*37-y*8),0,1);v=.012*np.sin(x*460+2*np.sin(y*18+x*45))+.018*rng.normal(size=(N,N));rgb[:,:,0]=.48+.12*patch+.04*streak+v;rgb[:,:,1]=.035+.10*patch+.025*streak+v*.4;rgb[:,:,2]=.022+.018*patch+v*.2
  for _ in range(2200):
   a,b=rng.integers(4,N-4,2);r=int(rng.choice([1,2,3],p=[.25,.6,.15]));aa,bb=np.mgrid[-r:r+1,-r:r+1];alpha=(np.exp(-2.7*(aa*aa+bb*bb)/(r*r))*.65)[:,:,None];rgb[a-r:a+r+1,b-r:b+r+1]=rgb[a-r:a+r+1,b-r:b+r+1]*(1-alpha)+np.array([.65,.40,.22])*alpha
 elif kind=='crumb':
  noise=rng.normal(0,.018,(N,N))+.012*np.sin(x*55+y*44)
  for k,c in enumerate(base):rgb[:,:,k]=c+noise
  for _ in range(2000):
   a,b=rng.integers(16,N-16,2);r=int(rng.choice([2,3,5,8,12],p=[.25,.34,.27,.12,.02]));rx=r;ry=max(1,int(r*rng.uniform(.55,1.2)));aa,bb=np.mgrid[-ry:ry+1,-rx:rx+1];dist=(aa/ry)**2+(bb/rx)**2;alpha=np.clip((1-dist)*2.8,0,1)[:,:,None];shade=np.clip(.73+.16*dist+.06*aa/ry,.65,.96)[:,:,None]
   patch=rgb[a-ry:a+ry+1,b-rx:b+rx+1];patch[:]=patch*(1-alpha)+patch*shade*alpha
 elif kind=='crust':
  noise=rng.normal(0,.018,(N,N))+.045*np.sin(x*13)*np.sin(y*19)+.025*np.sin(x*37)*np.sin(y*53)-.13*np.clip((y-.65)*3,0,1)
  for k,c in enumerate(base):rgb[:,:,k]=c+noise*(1 if k==0 else .65)
 else:
  noise=rng.normal(0,.017,(N,N))+.01*np.sin(x*300+np.sin(y*55)*3)+.009*np.sin(y*250+x*40)
  for k,c in enumerate(base):rgb[:,:,k]=c+noise*(.8 if k==0 else 1)
 rgba=np.ones((N,N,4),np.float32);rgba[:,:,:3]=np.clip(rgb,0,1);im=bpy.data.images.new('Original baked '+kind,width=N,height=N);im.pixels.foreach_set(rgba.ravel());im.pack();n=m.node_tree.nodes.new('ShaderNodeTexImage');n.image=im;m.node_tree.links.new(n.outputs['Color'],m.node_tree.nodes.get('Principled BSDF').inputs['Base Color']);
 if kind in ['crumb','crust','nori']:
  h=rgb.mean(axis=2);dy,dx=np.gradient(h);strength=1.1 if kind=='crumb' else 1.0;normal=np.stack([-dx*strength,-dy*strength,np.ones_like(h)],axis=-1);normal/=np.linalg.norm(normal,axis=-1,keepdims=True);nr=np.ones((N,N,4),np.float32);nr[:,:,:3]=normal*.5+.5;nm=bpy.data.images.new('Original baked '+kind+' normal',width=N,height=N);nm.colorspace_settings.name='Non-Color';nm.pixels.foreach_set(nr.ravel());nm.pack();tn=m.node_tree.nodes.new('ShaderNodeTexImage');tn.image=nm;nn=m.node_tree.nodes.new('ShaderNodeNormalMap');m.node_tree.links.new(tn.outputs['Color'],nn.inputs['Color']);m.node_tree.links.new(nn.outputs['Normal'],m.node_tree.nodes.get('Principled BSDF').inputs['Normal'])
 return m

def uv_project(o,axes=(0,2),scale=(.1,.1)):
 uv=o.data.uv_layers.new(name='Baked portable UV')
 for p in o.data.polygons:
  for li in p.loop_indices:
   co=o.data.vertices[o.data.loops[li].vertex_index].co;uv.data[li].uv=(co[axes[0]]/scale[0]+.5,co[axes[1]]/scale[1])

def apple():
 skin=texmat('Red apple skin with lenticels',(.5,.06,.025),'apple');v=[];f=[];N=96;L=49
 for j in range(L):
  t=.008+(math.pi-.016)*j/(L-1);z=.041+.039*math.cos(t)-.010*math.exp(-(t/.38)**2)+.006*math.exp(-((math.pi-t)/.18)**2)
  r=.042*math.sin(t)*(1+.10*math.cos(t))
  for i in range(N):
   a=2*math.pi*i/N;rr=r*(1+.018*math.cos(a*5+.4)*abs(math.cos(t))**3+.012*math.sin(3*a+t));v.append((rr*math.cos(a),rr*math.sin(a),z))
 for j in range(L-1):
  for i in range(N):f.append((j*N+i,j*N+(i+1)%N,(j+1)*N+(i+1)%N,(j+1)*N+i))
 f.extend([tuple(reversed(range(N))),tuple((L-1)*N+i for i in range(N))]);o=mesh('Gently asymmetric apple skin',v,f,skin);uv=o.data.uv_layers.new()
 for p in o.data.polygons:
  inds=[o.data.loops[li].vertex_index%N for li in p.loop_indices];seam=0 in inds and N-1 in inds
  for li in p.loop_indices:
   idx=o.data.loops[li].vertex_index;i=idx%N;uv.data[li].uv=(1 if seam and i==0 else i/N,idx//N/(L-1))
 brown=mat('Dry woody stem',(.115,.055,.021),0,.89);path_tube('Curved short stalk',[(0,0,.068),(.001,0,.073),(.002,.0005,.079),(.0035,.001,.083)],[.0018,.0015,.0012,.001],brown,N=12)
 calyx=mat('Shriveled dry brown calyx',(.020,.007,.0025),0,.98)
 core=mat('Deep irregular calyx recess',(.007,.0025,.001),0,1)
 vs=[(.00015,-.0001,.0077)];fs=[]
 for j in range(17):
  a=math.tau*j/17;r=.00135*(1+.19*math.sin(j*2.7)+.09*math.cos(j*1.3));vs.append((r*math.cos(a),r*math.sin(a),.0070+.0002*math.sin(j*3.1)))
 for j in range(17):fs.append((0,1+j,1+(j+1)%17))
 mesh('Irregular recessed dry floral core',vs,fs,core)
 for i in range(5):
  a=i*math.tau/5+[.0,.12,-.07,.11,-.09][i];length=[.0027,.0034,.0022,.0038,.0028][i];vs=[];fs=[]
  for j in range(9):
   t=j/8;r=.0009+length*t;width=.00038*(1-.88*t)*(1+.28*math.sin(j*2.4+i));bend=.0003*math.sin(t*7+i)*t
   for k in [-1,0,1]:
    tang=k*width+bend;z=.0067-.0010*t+.00027*math.sin(t*10+i)*t+.00038*abs(k)*math.sin(t*6+i);vs.append((r*math.cos(a)-tang*math.sin(a),r*math.sin(a)+tang*math.cos(a),z))
  for j in range(8):
   for k in range(2):q=j*3+k;fs.append((q,q+1,q+4,q+3))
  mesh('Uneven shriveled sepal '+str(i+1),vs,fs,calyx)
 # Put the lowest actual point exactly on the support plane.
 lo=min(v.co.z for o in bpy.context.scene.objects if o.type=='MESH' for v in o.data.vertices)
 for o in bpy.context.scene.objects:o.location.z-=lo

def bread():
 crust=texmat('Baked golden thin crust',(.52,.235,.075),'crust');crumb=texmat('Cream bread crumb with irregular pores',(.92,.87,.74),'crumb')
 # Rounded square shokupan silhouette, softer and wider upper shoulders.
 N=64;outline=[]
 for i in range(N):
  a=math.tau*i/N;cx=math.copysign(abs(math.cos(a))**.36,math.cos(a));sz=math.copysign(abs(math.sin(a))**.36,math.sin(a));outline.append((.057*cx*(1+.035*sz),.060+.057*sz+.003*math.cos(a*2)))
 def piece(n,y,depth,flat=False):
  v=[]
  for yy,s in [(y, .94),(y+.001,1),(y+depth-.001,1),(y+depth,.94)]:
   for x,z in outline:v.append((x*s+.00045*math.sin(z*70+y*75),yy,.060+(z-.060)*s+.00035*math.sin(x*62+y*85)))
  f=[]
  for j in range(3):
   for i in range(N):f.append((j*N+i,j*N+(i+1)%N,(j+1)*N+(i+1)%N,(j+1)*N+i))
  # Front/back inset crumb polygon, crust is side and perimeter bevel.
  f += [tuple(reversed(range(N))),tuple(3*N+i for i in range(N))];o=mesh(n,v,f,crust,False);o.data.materials.append(crumb)
  for p in o.data.polygons:
   p.material_index=1 if p.index>=3*N else 0;p.use_smooth=p.index<3*N
  uv_project(o,(0,2),(.114,.12))
  if flat:
   # One slice lies flat beside the loaf, not floating upright.
   for vert in o.data.vertices:
    x,yy,z=vert.co;vert.co=(x+.145,z-.10,yy-y)
  return o
 for i in range(4):
  ob=piece('Loaf slice %02d'%(i+1),-.035+i*.022,.0215)
  if i==3:ob.data.polygons[-1].material_index=0
 piece('Separate resting slice',0,.019,True)
 # Normalize bottom after contour construction.
 for o in bpy.context.scene.objects:
  low=min(v.co.z for v in o.data.vertices);o.location.z=-low

def onigiri():
 rice=mat('Cooked short grain rice',(.85,.82,.69),0,.57);white=mat('Rice slight ivory variation',(.77,.75,.64),0,.63);nori=texmat('Thin matte toasted nori',(.025,.037,.018),'nori')
 # Bevelled triangular prism with rounded corners, real width and depth.
 v=[(-.046,-.023,.006),(.046,-.023,.006),(0,-.023,.085),(-.046,.023,.006),(.046,.023,.006),(0,.023,.085)];f=[(0,2,1),(3,4,5),(0,1,4,3),(1,2,5,4),(2,0,3,5)];o=mesh('Rounded compact rice body',v,f,rice)
 bpy.context.view_layer.objects.active=o;o.select_set(True);q=o.modifiers.new('Hand pressed rounded edges','BEVEL');q.width=.009;q.segments=5;bpy.ops.object.modifier_apply(modifier=q.name)
 # Grain geometry on the body surface, generated by area weighted triangle samples.
 o.data.calc_loop_triangles();tris=list(o.data.loop_triangles);weights=[t.area for t in tris];rng=random.Random(41);vs=[];fs=[]
 for k in range(3500):
  t=rng.choices(tris,weights=weights)[0];a,b,c=[o.data.vertices[i].co.copy() for i in t.vertices];u=rng.random();w=rng.random()
  if u+w>1:u=1-u;w=1-w
  pos=a+(b-a)*u+(c-a)*w
  if abs(pos.x)<.0205 and pos.z<(.053 if pos.y<0 else .048) and abs(pos.y)>.019:continue
  normal=t.normal.normalized();ref=Vector((0,0,1));axis=normal.cross(ref)
  if axis.length<.1:axis=normal.cross(Vector((1,0,0)))
  axis.normalize();other=normal.cross(axis);ang=rng.random()*math.tau;long=axis*math.cos(ang)+other*math.sin(ang);short=normal.cross(long);start=len(vs);length=rng.uniform(.0018,.0026);wid=rng.uniform(.00115,.00165)
  # Low segment ellipsoid, half embedded into the compact rice body.
  for j in range(3):
   theta=.03+(math.pi-.06)*j/2
   for i in range(5):
    a=math.tau*i/5;vs.append(tuple(pos+long*length*math.cos(theta)+math.sin(theta)*(short*wid*math.cos(a)+normal*.00075*math.sin(a))))
  for j in range(2):
   for i in range(5):fs.append((start+j*5+i,start+j*5+(i+1)%5,start+(j+1)*5+(i+1)%5,start+(j+1)*5+i))
  fs.extend([tuple(start+i for i in reversed(range(5))),tuple(start+10+i for i in range(5))])
 grains=mesh('Visible individually shaped rice grains',vs,fs,rice);grains.data.materials.append(white)
 for p in grains.data.polygons:p.material_index=int((p.index//26)%7==0)
 # Wrapper travels front, under base and back. Wavy thin edges with a .18mm shell.
 vs=[];fs=[];rows=40;cols=22
 for j in range(rows):
  t=j/(rows-1)
  if t<.30:y=-.02365;z=.051-.036*t/.30
  elif t<.45:a=(t-.30)/.15*math.pi/2;y=-.014-.00965*math.cos(a);z=.015-.00965*math.sin(a)
  elif t<.55:y=-.014+.028*(t-.45)/.10;z=.00535
  elif t<.70:a=(t-.55)/.15*math.pi/2;y=.014+.00965*math.sin(a);z=.015-.00965*math.cos(a)
  else:y=.02365;z=.015+.031*(t-.70)/.30
  for i in range(cols):
   u=i/(cols-1);xx=(u-.5)*.037;wr=.00032*math.sin(u*36+t*63)+.00017*math.sin(u*82-t*37);vs.append((xx,y+(wr if t<.42 or t>.58 else 0),z+(.0006*math.sin(u*19+.8) if j in [0,rows-1] else 0)))
 for j in range(rows-1):
  for i in range(cols-1):a=j*cols+i;fs.append((a,a+1,a+cols+1,a+cols))
 no=mesh('Wrinkled thin seaweed wrap',vs,fs,nori);uv=no.data.uv_layers.new()
 for p in no.data.polygons:
  for li in p.loop_indices:k=no.data.loops[li].vertex_index;uv.data[li].uv=(k%cols/(cols-1),k//cols/(rows-1))
 bpy.context.view_layer.objects.active=no;q=no.modifiers.new('Paper thin nori thickness','SOLIDIFY');q.thickness=.00018;bpy.ops.object.modifier_apply(modifier=q.name)
 # Origin at physical support.
 lo=min(v.co.z for ob in bpy.context.scene.objects for v in ob.data.vertices)
 for ob in bpy.context.scene.objects:ob.location.z=-lo

def main():
 for slug,title,fn in zip(IDS,TITLES,[apple,bread,onigiri]):
  if os.environ.get('ONLY_ASSETS') and slug not in os.environ['ONLY_ASSETS'].split(','):continue
  clear();fn();bpy.ops.object.select_all(action='SELECT');bpy.context.view_layer.objects.active=next(o for o in bpy.context.scene.objects if o.type=='MESH');bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.mesh.normals_make_consistent(inside=False);bpy.ops.object.mode_set(mode='OBJECT');bpy.context.view_layer.update();obs=[o for o in bpy.context.scene.objects if o.type=='MESH'];st=stats(obs);folder=A/slug;folder.mkdir(exist_ok=True)
  bpy.ops.object.select_all(action='SELECT');bpy.ops.export_scene.gltf(filepath=str(folder/(slug+'.glb')),export_format='GLB',use_selection=True,export_apply=True);bpy.ops.wm.save_as_mainfile(filepath=str(folder/(slug+'.blend')),compress=True)
  meta=dict(id=slug,title_ja=title,category='food',units='meters',origin='support plane',front_blend='-Y',up_blend='Z',up_glb='Y',design='Original generic food; plausible artist chosen dimensions; not a brand replica',license='Original geometry and baked procedural texture pixels',review_status='pending independent review',blender_version=bpy.app.version_string,glb_bytes=(folder/(slug+'.glb')).stat().st_size,blend_bytes=(folder/(slug+'.blend')).stat().st_size,**st);(folder/'metadata.json').write_text(json.dumps(meta,indent=2)+'\n');print('EXPORTED',slug,flush=True);render_asset(slug)
if __name__=='__main__':main()
