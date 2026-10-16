import bpy, math, os, json, shutil, hashlib
import numpy as np
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1]; A=Path(os.environ.get('ASSET_OUTPUT_ROOT',str(R/'assets')));A.mkdir(parents=True,exist_ok=True)
bpy.context.preferences.filepaths.save_version=0
IDS=['stainless_kitchen_kettle','ceramic_rice_bowl','wooden_cutting_board']
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
 lathe('Seated removable domed lid',[(.002,.159),(.022,.158),(.043,.153),(.056,.147),(.057,.145),(.057,.143),(.054,.142),(.052,.146),(.041,.151),(.021,.156),(.002,.157)],steel)
 lathe('Lid insulated knob',[(.002,.157),(.010,.157),(.012,.162),(.012,.169),(.009,.175),(.002,.176)],dark,64)
 for y in [-.083,.083]:
  box('Handle mounting ear',(0,y,.119),(.025,.007,.028),steel,.004)
  path_tube('Pivot rivet',[(0,y-.005,.127),(0,y+.005,.127)],[.005,.005],steel,N=32)
 pts=[(0,.084*math.cos(math.pi*i/48),.128+.113*math.sin(math.pi*i/48)) for i in range(49)]
 path_tube('Continuous raised carrying handle',pts,[.007]*49,dark,N=24)
 # Small real vent hole in lid, off center.
 bpy.ops.mesh.primitive_cylinder_add(vertices=24,radius=.0018,depth=.015,location=(.030,0,.153));cut=bpy.context.object;lid=bpy.data.objects['Seated removable domed lid'];bpy.context.view_layer.objects.active=lid;q=lid.modifiers.new('Steam vent','BOOLEAN');q.object=cut;q.operation='DIFFERENCE';bpy.ops.object.modifier_apply(modifier=q.name);bpy.data.objects.remove(cut,do_unlink=True)
def bowl():
 glaze=mat('Warm ivory feldspathic glaze',(.72,.69,.59),0,.22);blue=mat('Indigo underglaze bands',(.022,.068,.105),0,.25);clay=mat('Unglazed foot clay',(.48,.40,.29),0,.85)
 profile=[(.002,.008),(.022,.008),(.024,.002),(.025,0),(.030,0),(.032,.003),(.032,.011),(.036,.014),(.043,.024),(.051,.037),(.058,.053),(.0592,.056),(.0596,.057),(.060,.058),(.0604,.059),(.0608,.060),(.0612,.061),(.0616,.062),(.062,.063),(.0625,.066),(.061,.0675),(.0595,.0665),(.059,.063),(.055,.052),(.048,.037),(.040,.025),(.031,.018),(.020,.015),(.002,.015)]
 o=lathe('Wheel thrown bowl with integrated glaze bands and unglazed foot',profile,glaze);o.data.materials.append(blue);o.data.materials.append(clay)
 for p in o.data.polygons:
  # The lathe connects profile segment k to k+1, with 96 faces each.
  segment=p.index//96
  if segment in [11,14,17]:p.material_index=1
  elif segment in [2,3,4]:p.material_index=2
def wood_image():
 N=1024;y,x=np.mgrid[0:N,0:N]/N;rng=np.random.default_rng(3107)
 # Seamless long-grain field; original generated image, no source photos.
 warp=x+.012*np.sin(y*9+x*5)+.006*np.sin(y*29+x*13)
 grain=np.sin(warp*420+2*np.sin(warp*37))*.017+np.sin(warp*1100)*.007+rng.normal(0,.004,(N,N))
 broad=.035*np.sin(warp*38)+.016*np.sin(warp*87)
 rgba=np.ones((N,N,4),np.float32)
 for i,c in enumerate([.60,.40,.215]):rgba[:,:,i]=c+broad+grain
 im=bpy.data.images.new('Original hinoki-style long grain',width=N,height=N);im.pixels.foreach_set(rgba.ravel());im.pack();return im
def board():
 m=mat('Sanded unvarnished pale wood',(.60,.40,.215),0,.64);im=wood_image();nt=m.node_tree;n=nt.nodes.new('ShaderNodeTexImage');n.image=im;nt.links.new(n.outputs['Color'],nt.nodes.get('Principled BSDF').inputs['Base Color'])
 o=box('Solid edge-grain cutting board',(0,0,.012),(.34,.205,.024),m,.005)
 for layer in list(o.data.uv_layers):o.data.uv_layers.remove(layer)
 uv=o.data.uv_layers.new(name='Portable wood coordinates');uv.active_render=True
 for p in o.data.polygons:
  for li in p.loop_indices:
   co=o.data.vertices[o.data.loops[li].vertex_index].co
   # Grain runs X: end faces use a tighter tangential slice.
   if abs(p.normal.x)>.7:uv.data[li].uv=(co.y/.205+.5,co.z/.024*.12+.3)
   else:uv.data[li].uv=(co.y/.205+.5,co.x/.34+.5)
 # End grain is a separate packed texture on actual end faces.
 end=mat('Exposed end-grain wood',(.58,.38,.20),0,.72);N=512;y,x=np.mgrid[0:N,0:N]/N;v=.018*np.sin(100*np.sqrt((x-.4)**2+(y*2+1)**2))+.008*np.sin(x*500);rgba=np.ones((N,N,4),np.float32)
 for i,c in enumerate([.57,.375,.195]):rgba[:,:,i]=c+v
 im2=bpy.data.images.new('Original end grain growth rings',width=N,height=N);im2.pixels.foreach_set(rgba.ravel());im2.pack();n=end.node_tree.nodes.new('ShaderNodeTexImage');n.image=im2;end.node_tree.links.new(n.outputs['Color'],end.node_tree.nodes.get('Principled BSDF').inputs['Base Color']);o.data.materials.append(end)
 for p in o.data.polygons:
  if abs(p.normal.x)>.7:p.material_index=1

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
 for slug,fn in zip(IDS,[kettle,bowl,board]):
  if os.environ.get('ONLY_ASSETS') and slug not in os.environ['ONLY_ASSETS'].split(','):continue
  clear();fn();obs=[o for o in bpy.context.scene.objects if o.type=='MESH'];st=stats(obs);f=A/slug;f.mkdir(exist_ok=True)
  bpy.ops.object.select_all(action='SELECT');bpy.ops.export_scene.gltf(filepath=str(f/(slug+'.glb')),export_format='GLB',use_selection=True,export_apply=True);bpy.ops.wm.save_as_mainfile(filepath=str(f/(slug+'.blend')),compress=True)
  meta=dict(id=slug,category='household',units='meters',origin='ground at object center',front_blend='-Y',up_blend='Z',up_glb='Y',design='Original generic Japanese household prop; artist-selected plausible dimensions, not an exact manufacturer copy.',license='Original geometry and procedural textures; no third-party image assets.',review_status='pending independent review',blender_version=bpy.app.version_string,**st);(f/'metadata.json').write_text(json.dumps(meta,indent=2)+'\n');print('EXPORTED',slug,flush=True);render_asset(slug)
if __name__=='__main__':main()
