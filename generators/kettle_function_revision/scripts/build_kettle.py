import bpy, math, os, json, shutil, hashlib
import numpy as np
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1]; A=Path(os.environ.get('ASSET_OUTPUT_ROOT',str(R/'assets')));A.mkdir(parents=True,exist_ok=True)
bpy.context.preferences.filepaths.save_version=0
IDS=['stainless_kitchen_kettle']
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
def kettle():
 steel=mat('Satin stainless steel',(.62,.66,.69),1,.24);dark=mat('Heat-resistant phenolic handle',(.025,.019,.015),0,.29)
 body=lathe('Formed hollow steel body',[(.002,0),(.066,0),(.079,.004),(.089,.014),(.096,.035),(.099,.065),(.095,.095),(.086,.119),(.070,.139),(.057,.145),(.055,.145),(.055,.142),(.068,.137),(.084,.117),(.093,.094),(.097,.065),(.094,.035),(.087,.016),(.077,.006),(.002,.004)],steel)
 # Open connection through the body into the hollow spout.
 bpy.ops.mesh.primitive_cylinder_add(vertices=64,radius=.017,depth=.075,location=(.090,0,.085),rotation=(0,math.pi/2,0));cut=bpy.context.object
 bpy.context.view_layer.objects.active=body;q=body.modifiers.new('Real open spout connection','BOOLEAN');q.operation='DIFFERENCE';q.object=cut;bpy.ops.object.modifier_apply(modifier=q.name);bpy.data.objects.remove(cut,do_unlink=True)
 pts=[];rs=[]
 for i in range(25):t=i/24;pts.append((.084+.088*t,0,.085+.068*t*t));rs.append(.019-.007*t)
 path_tube('Tapered hollow pouring spout',pts,rs,steel,[r-.0014 for r in rs],48)
 lathe('Seated removable domed lid',[(.002,.159),(.022,.158),(.043,.153),(.056,.1475),(.058,.147),(.058,.145002),(.054,.145002),(.0538,.1448),(.0538,.1375),(.0526,.1375),(.0526,.1448),(.041,.151),(.021,.156),(.002,.157)],steel)
 lathe('Lid insulated knob',[(.002,.157),(.010,.157),(.012,.162),(.012,.169),(.009,.175),(.002,.176)],dark,64)
 for sign in [-1,1]:
  box('Fixed shoulder mounting foot',(sign*.076,0,.132),(.022,.026,.004),steel,.001)
  cheek=box('Fixed hinge cheek',(sign*.080,0,.145),(.003,.020,.030),steel,.001)
  tang=box('Moving stainless handle tang',(sign*.085,0,.162),(.004,.018,.036),steel,.0015)
  bpy.ops.mesh.primitive_cylinder_add(vertices=48,radius=.00415,depth=.030,location=(sign*.083,0,.152),rotation=(0,math.pi/2,0));bore=bpy.context.object
  for plate in [cheek,tang]:
   bpy.context.view_layer.objects.active=plate;q=plate.modifiers.new('Real pivot bore with radial clearance','BOOLEAN');q.operation='DIFFERENCE';q.object=bore;bpy.ops.object.modifier_apply(modifier=q.name)
  bpy.data.objects.remove(bore,do_unlink=True)
  path_tube('Coaxial fore-aft hinge pin',[(sign*x,0,.152) for x in [.077,.0785,.0785,.087,.087,.0885]],[.0055,.0055,.004,.004,.0055,.0055],steel,N=32)
 pts=[(.085*math.cos(math.pi*i/64),0,.172+.087*math.sin(math.pi*i/64)) for i in range(65)]
 path_tube('Fore-aft insulated carrying arch',pts,[.0065+.0035*math.sin(math.pi*i/64) for i in range(65)],dark,N=32)
 # Small real vent hole in lid, off center.
 bpy.ops.mesh.primitive_cylinder_add(vertices=24,radius=.0018,depth=.015,location=(.030,0,.153));cut=bpy.context.object;lid=bpy.data.objects['Seated removable domed lid'];bpy.context.view_layer.objects.active=lid;q=lid.modifiers.new('Steam vent','BOOLEAN');q.object=cut;q.operation='DIFFERENCE';bpy.ops.object.modifier_apply(modifier=q.name);bpy.data.objects.remove(cut,do_unlink=True)
def stats(obs):
 verts=[o.matrix_world@v.co for o in obs for v in o.data.vertices];tri=0;bad=0
 for o in obs:
  o.data.calc_loop_triangles();tri+=len(o.data.loop_triangles)
  bad+=sum(t.area<1e-14 for t in o.data.loop_triangles)
 lo=[min(v[i] for v in verts) for i in range(3)];hi=[max(v[i] for v in verts) for i in range(3)]
 return dict(triangles=tri,zero_area_triangles=bad,bounds_min=lo,bounds_max=hi,dimensions_m=[hi[i]-lo[i] for i in range(3)],mesh_objects=len(obs))
def studio(target,size):
 sc=bpy.context.scene;sc.render.engine='CYCLES';sc.cycles.samples=40;sc.cycles.use_denoising=False;sc.render.threads_mode='FIXED';sc.render.threads=2;sc.render.resolution_x=800;sc.render.resolution_y=800;sc.render.resolution_percentage=100;sc.render.image_settings.file_format='JPEG';sc.render.image_settings.quality=94;sc.view_settings.view_transform='AgX';sc.world.color=(.25,.25,.25)
 floor=mat('Neutral studio plaster',(.34,.35,.34),0,.9);box('Studio ground',(0,0,-.012),(200,200,.02),floor,.0)
 for pos,power,sz in [((1,-1,2),120,1.5),((-1,-.3,1),80,1),((.4,1,1.5),150,1)]:
  bpy.ops.object.light_add(type='AREA',location=Vector(target)+Vector(pos)*size*3);o=bpy.context.object;o.data.energy=power*size*size*8;o.data.shape='DISK';o.data.size=sz*size*3;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()
 bpy.ops.object.camera_add();cam=bpy.context.object;cam.data.type='ORTHO';cam.data.ortho_scale=size*1.5;sc.camera=cam;return cam

def render_asset(slug):
 f=A/slug;clear();bpy.ops.import_scene.gltf(filepath=str(f/(slug+'.glb')));obs=[o for o in bpy.context.scene.objects if o.type=='MESH'];st=stats(obs);target=(Vector(st['bounds_min'])+Vector(st['bounds_max']))/2;size=max(st['dimensions_m']);cam=studio(target,size)
 for name,off in [('front_three_quarter',(2,-3,2)),('side',(0,-3,1.1)),('rear',(-2,3,1.7)),('close_up',(2,-2,3))]:
  cam.location=target+Vector(off)*size;cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=size*(1.45 if name!='close_up' else 1.12);bpy.context.scene.render.filepath=str(f/(name+'.jpg'));bpy.ops.render.render(write_still=True)
 shutil.copyfile(f/'front_three_quarter.jpg',f/'preview.jpg');shutil.copyfile(f/'rear.jpg',f/'back.jpg')
def main():
 for slug,fn in zip(IDS,[kettle]):
  if os.environ.get('ONLY_ASSETS') and slug not in os.environ['ONLY_ASSETS'].split(','):continue
  clear();fn();obs=[o for o in bpy.context.scene.objects if o.type=='MESH'];st=stats(obs);f=A/slug;f.mkdir(exist_ok=True)
  bpy.ops.object.select_all(action='SELECT');bpy.ops.export_scene.gltf(filepath=str(f/(slug+'.glb')),export_format='GLB',use_selection=True,export_apply=True);bpy.ops.wm.save_as_mainfile(filepath=str(f/(slug+'.blend')),compress=True)
  meta=dict(id=slug,category='household',units='meters',origin='ground at object center',front_blend='-Y',up_blend='Z',up_glb='Y',design='Original generic Japanese household prop; artist-selected plausible dimensions, not an exact manufacturer copy.',license='Original geometry and procedural textures; no third-party image assets.',review_status='pending independent review',blender_version=bpy.app.version_string,**st);(f/'metadata.json').write_text(json.dumps(meta,indent=2)+'\n');print('EXPORTED',slug,flush=True)
if __name__=='__main__':main()
