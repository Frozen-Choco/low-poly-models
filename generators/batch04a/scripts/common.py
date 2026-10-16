import bpy, math, os, json, shutil, hashlib
import numpy as np
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1]; A=Path(os.environ.get('ASSET_OUTPUT_ROOT',str(R/'assets')));A.mkdir(parents=True,exist_ok=True)
bpy.context.preferences.filepaths.save_version=0
IDS=['whole_red_apple']
def clear():
 for o in list(bpy.data.objects):bpy.data.objects.remove(o,do_unlink=True)
def mat(n,c,metal=0,rough=.5):
 m=bpy.data.materials.new(n);m.diffuse_color=(*c,1);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*c,1);p.inputs['Metallic'].default_value=metal;p.inputs['Roughness'].default_value=rough;return m
def mesh(n,v,f,m,smooth=True):
 d=bpy.data.meshes.new(n);d.from_pydata(v,[],f);d.update();o=bpy.data.objects.new(n,d);bpy.context.collection.objects.link(o);o.data.materials.append(m)
 for p in d.polygons:p.use_smooth=smooth
 return o
def lathe(n,profile,m,N=96):
 v=[];f=[]
 for r,z in profile:
  for i in range(N):a=i*2*math.pi/N;v.append((r*math.cos(a),r*math.sin(a),z))
 for k in range(len(profile)-1):
  for i in range(N):j=(i+1)%N;f.append((k*N+i,k*N+j,(k+1)*N+j,(k+1)*N+i))
 if profile[0][0]<.003:f.append(tuple(reversed(range(N))))
 if profile[-1][0]<.003:f.append(tuple((len(profile)-1)*N+i for i in range(N)))
 return mesh(n,v,f,m)
def box(n,p,s,m,b=.002):
 bpy.ops.mesh.primitive_cube_add(size=1,location=p);o=bpy.context.object;o.name=n;o.dimensions=s;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(m)
 if b:
  q=o.modifiers.new('Soft sanded manufactured edges','BEVEL');q.width=b;q.segments=4;bpy.context.view_layer.objects.active=o;bpy.ops.object.modifier_apply(modifier=q.name)
 return o
def path_tube(n,pts,rads,m,inner=None,N=32):
 v=[];f=[];L=len(pts)
 for k,pt in enumerate(pts):
  tangent=Vector(pts[min(k+1,L-1)])-Vector(pts[max(0,k-1)]);tangent.normalize();ref=Vector((1,0,0)) if max(p[0] for p in pts)-min(p[0] for p in pts)<1e-8 else Vector((0,1,0));u=tangent.cross(ref)
  if u.length<.1:u=tangent.cross(Vector((1,0,0)))
  u.normalize();w=tangent.cross(u)
  for r in ([rads[k],inner[k]] if inner else [rads[k]]):
   for i in range(N):v.append(tuple(Vector(pt)+r*(math.cos(i*2*math.pi/N)*u+math.sin(i*2*math.pi/N)*w)))
 rings=2 if inner else 1
 for k in range(L-1):
  for side in range(rings):
   for i in range(N):a=k*rings*N+side*N+i;b=k*rings*N+side*N+(i+1)%N;c=b+rings*N;d=a+rings*N;f.append((a,b,c,d) if side==0 else (d,c,b,a))
 if inner:
  for k in [0,L-1]:
   for i in range(N):a=k*2*N+i;b=k*2*N+(i+1)%N;f.append((a,a+N,b+N,b) if k==0 else (b,b+N,a+N,a))
 else:
  f += [tuple(reversed(range(N))),tuple((L-1)*N+i for i in range(N))]
 return mesh(n,v,f,m)
def stats(obs):
 verts=[o.matrix_world@v.co for o in obs for v in o.data.vertices];tri=0;bad=0
 for o in obs:
  o.data.calc_loop_triangles();tri+=len(o.data.loop_triangles)
  bad+=sum(t.area<1e-14 for t in o.data.loop_triangles)
 lo=[min(v[i] for v in verts) for i in range(3)];hi=[max(v[i] for v in verts) for i in range(3)]
 return dict(triangles=tri,zero_area_triangles=bad,bounds_min=lo,bounds_max=hi,dimensions_m=[hi[i]-lo[i] for i in range(3)],mesh_objects=len(obs))
def studio(target,size):
 sc=bpy.context.scene;sc.render.engine='CYCLES';sc.cycles.samples=40;sc.cycles.use_denoising=False;sc.render.threads_mode='FIXED';sc.render.threads=2;sc.render.resolution_x=800;sc.render.resolution_y=800;sc.render.resolution_percentage=100;sc.render.image_settings.file_format='JPEG';sc.render.image_settings.quality=94;sc.view_settings.view_transform='AgX';sc.world.color=(.25,.25,.25)
 floor=mat('Neutral studio plaster',(.34,.35,.34),0,.9);box('Studio ground',(0,0,-.01),(200,200,.02),floor,.0)
 for pos,power,sz in [((1,-1,2),120,1.5),((-1,-.3,1),80,1),((.4,1,1.5),150,1)]:
  bpy.ops.object.light_add(type='AREA',location=Vector(target)+Vector(pos)*size*3);o=bpy.context.object;o.data.energy=power*size*size*8;o.data.shape='DISK';o.data.size=sz*size*3;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()
 bpy.ops.object.camera_add();cam=bpy.context.object;cam.data.type='ORTHO';cam.data.ortho_scale=size*1.5;sc.camera=cam;return cam

def render_asset(slug):
 f=A/slug;clear();bpy.ops.import_scene.gltf(filepath=str(f/(slug+'.glb')));obs=[o for o in bpy.context.scene.objects if o.type=='MESH'];st=stats(obs);target=(Vector(st['bounds_min'])+Vector(st['bounds_max']))/2;size=max(st['dimensions_m']);cam=studio(target,size)
 for name,off in [('front_three_quarter',(2,-3,2)),('side',(0,-3,1.1)),('rear',(-2,3,1.7)),('close_up',(2,-2,3)),('underside',(1,-2,-3)),('alternate_light',(2,-3,2)),('underside_detail',(1,-1,-3))]:
  if os.environ.get('ONLY_VIEWS') and name not in os.environ['ONLY_VIEWS'].split(','):continue
  bpy.data.objects['Studio ground'].hide_render=name.startswith('underside')
  for light in [o for o in bpy.context.scene.objects if o.type=='LIGHT']:
   light.location.z=target.z+(-abs(light.location.z-target.z) if name.startswith('underside') else abs(light.location.z-target.z));light.rotation_euler=(target-light.location).to_track_quat('-Z','Y').to_euler()
  if name=='alternate_light':
   for light in [o for o in bpy.context.scene.objects if o.type=='LIGHT']:light.data.color=(1,.78,.55);light.location.x*=-1
  cam.location=target+Vector(off)*size;cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=size*(1.45 if name!='close_up' else 1.12);
  if name=='underside_detail':
   focus=target.copy();focus.z=st['bounds_min'][2]+.002;cam.location=focus+Vector(off)*size;cam.rotation_euler=(focus-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=size*.5
  bpy.context.scene.render.filepath=str(f/(name+'.jpg'));bpy.ops.render.render(write_still=True)
 shutil.copyfile(f/'front_three_quarter.jpg',f/'preview.jpg');shutil.copyfile(f/'rear.jpg',f/'back.jpg')
