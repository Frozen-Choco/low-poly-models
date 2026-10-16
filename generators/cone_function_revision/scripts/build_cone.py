"""Original generic hollow/stackable Japanese-context PVC cone. Blender 4.3.2.
No downloaded geometry/textures. Dimensions are design estimates, not certification.
Run: blender -b --threads 3 --python scripts/build_cone.py
"""
import bpy,bmesh,math,json,os
from pathlib import Path
from mathutils import Vector
import numpy as np
SUPPORT=Path(__file__).resolve().parents[1]
ROOT=Path(os.environ.get('ASSET_OUTPUT_ROOT',str(SUPPORT)))
FOLDER=ROOT/'assets'/'street'/'traffic_cone'
N=192;PITCH=.040
OUTER=[(.145,.030),(.116640625,.180),(.097734375,.280),(.078828125,.380),(.059921875,.480),(.024,.670),(.022,.695),(.0215,.700)]
INNER=[(.149,0),(.148,.005),(.1418,.028)]+[(r-.0032,z) for r,z in OUTER if .03<=z<=.67]+[(.0188,.695),(.0188,.696),(0,.696)]
def material(n,c,rough):
 m=bpy.data.materials.new(n);m.use_nodes=True;m.diffuse_color=(*c,1);p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*c,1);p.inputs['Roughness'].default_value=rough;return m

def square_radius(theta,half=.180,corner=.025):
 c,s=abs(math.cos(theta)),abs(math.sin(theta));r=half/max(c,s)
 if min(c,s)*r<=half-corner:return r
 a=(half-corner)*(c+s);return a+math.sqrt(max(0,a*a-(2*(half-corner)**2-corner*corner)))

def model():
 red=material('Red flexible PVC',(.58,.022,.008),.43);inside=material('Uncoated inner PVC',(.48,.018,.006),.64);white=material('White reflective sheeting approximation',(.81,.81,.81),.38);black=material('Recycled PVC ballast ring',(.025,.025,.026),.86)
 im=bpy.data.images.new('Original recycled PVC finish 128',width=128,height=128);rng=np.random.default_rng(17);v=np.clip(.17+rng.normal(0,.008,(128,128)),0,1);pixels=np.stack([v,v,v,np.ones_like(v)],axis=-1).astype(np.float32);im.pixels.foreach_set(pixels.ravel());im.filepath_raw=str(SUPPORT/'recycled_pvc.png');im.file_format='PNG';im.save();im.pack();t=black.node_tree.nodes.new('ShaderNodeTexImage');t.image=im;black.node_tree.links.new(t.outputs['Color'],black.node_tree.nodes.get('Principled BSDF').inputs['Base Color'])
 vertices=[];faces=[];material_ids=[];rings=[]
 def ring(coords):
  ids=list(range(len(vertices),len(vertices)+len(coords)));vertices.extend(coords);rings.append(ids)
 def circle(r,z):
  ring([(r*math.cos(i*math.tau/N),r*math.sin(i*math.tau/N),z) for i in range(N)] if r else [(0,0,z)])
 # Profile starts at the underside aperture, travels up the interior, over a closed
 # 4 mm top cap, down the outer shell, across the weighted base and back underneath.
 for r,z in INNER:circle(r,z)
 circle(0,.700)
 for r,z in reversed(OUTER):circle(r,z)
 circle(.154,.028)
 # Four integrated stacking lands on the annular upper base. All vertices belong
 # to the one continuous solid surface. Their planar tops are Z=0.040 m.
 for fraction in [.30,.40,.60,.70,1.0]:
  coords=[]
  for i in range(N):
   a=i*math.tau/N;outer=square_radius(a,half=.177,corner=.024);r=.154+(outer-.154)*fraction
   d=abs(((a-math.pi/4+math.pi/4)%(math.pi/2))-math.pi/4)
   angular=max(0,min(1,(math.radians(13)-d)/math.radians(7)))
   radial=1 if fraction in [.40,.60] else 0
   z=.028+.012*angular*radial;coords.append((r*math.cos(a),r*math.sin(a),z))
  ring(coords)
 for z,half,corner in [(.025,.180,.025),(.003,.180,.025),(0,.177,.024)]:
  ring([(square_radius(i*math.tau/N,half,corner)*math.cos(i*math.tau/N),square_radius(i*math.tau/N,half,corner)*math.sin(i*math.tau/N),z) for i in range(N)])
 # Shallow molded underside pockets leave outer/inner bearing rims and eight
 # radial stiffening ribs. Diagonal ribs align with the upper stacking lands.
 for fraction in [.90,.82,.22,.12]:
  coords=[]
  for i in range(N):
   a=i*math.tau/N;outer=square_radius(a,half=.177,corner=.024);r=.149+(outer-.149)*fraction
   d=abs(((a+math.pi/8)%(math.pi/4))-math.pi/8)
   angular=max(0,min(1,(d-math.radians(3))/math.radians(4)))
   depth=.004*angular if fraction in [.82,.22] else 0
   coords.append((r*math.cos(a),r*math.sin(a),depth))
  ring(coords)
 for k in range(len(rings)):
  a,b=rings[k],rings[(k+1)%len(rings)]
  if len(a)==len(b)==1:continue
  local=[]
  if len(a)==1:local=[(a[0],b[(i+1)%N],b[i]) for i in range(N)]
  elif len(b)==1:local=[(a[i],a[(i+1)%N],b[0]) for i in range(N)]
  else:local=[(a[i],a[(i+1)%N],b[(i+1)%N],b[i]) for i in range(N)]
  for f in local:
   z=sum(vertices[j][2] for j in f)/len(f)
   midx=1 if k<len(INNER)-1 else 0
   if k>=len(INNER)+1 and z>.03:midx=2 if .18<z<.28 or .38<z<.48 else 0
   if z<.029:midx=3
   # Top stacking lands also belong to the black recycled PVC base.
   if k>=len(INNER)+1+len(OUTER):midx=3
   faces.append(f);material_ids.append(midx)
 me=bpy.data.meshes.new('Continuous hollow cone and annular base');me.from_pydata(vertices,[],faces);me.update();ob=bpy.data.objects.new('Continuous hollow PVC shell with open ballast ring',me);bpy.context.collection.objects.link(ob)
 for m in [red,inside,white,black]:me.materials.append(m)
 for p,idx in zip(me.polygons,material_ids):p.material_index=idx;p.use_smooth=idx!=3
 # Recalculate normals of a single manifold, not disconnected nested skins.
 bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();me.update()
 uv=me.uv_layers.new(name='Original finish UV')
 for p in me.polygons:
  for li in p.loop_indices:
   v=me.vertices[me.loops[li].vertex_index].co;uv.data[li].uv=(v.x/.36+.5,v.y/.36+.5)
 ob['nominal_radial_wall_thickness_m']=.0032;ob['closed_top_cap_thickness_m']=.004;ob['stack_pitch_m']=PITCH
 return ob

def studio(scene,center,size):
 col=bpy.data.collections.new('PREVIEW STUDIO');scene.collection.children.link(col)
 def move(o):
  for c in list(o.users_collection):c.objects.unlink(o)
  col.objects.link(o)
 floor_mat=material('Neutral studio',(.37,.37,.37),.9)
 bpy.ops.mesh.primitive_plane_add(size=200,location=(0,0,-.002));floor=bpy.context.object;floor.name='Preview floor';floor.data.materials.append(floor_mat);move(floor)
 for offset,power in [((-3,-4,6),600),((4,-2,3),240),((1,4,5),350)]:
  bpy.ops.object.light_add(type='AREA',location=center+Vector(offset)*size);o=bpy.context.object;o.data.energy=power*size*size;o.data.shape='DISK';o.data.size=size*3;o.rotation_euler=(center-o.location).to_track_quat('-Z','Y').to_euler();move(o)
 scene.world=bpy.data.worlds.new('Neutral daylight');scene.world.use_nodes=True;scene.world.node_tree.nodes['Background'].inputs[0].default_value=(.8,.8,.8,1);scene.world.node_tree.nodes['Background'].inputs[1].default_value=.4
 bpy.ops.object.camera_add();cam=bpy.context.object;move(cam);scene.camera=cam;cam.data.type='ORTHO'
 scene.render.engine='CYCLES';scene.cycles.samples=48;scene.cycles.use_denoising=False;scene.render.resolution_x=1000;scene.render.resolution_y=1000;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='JPEG';scene.render.image_settings.quality=94;scene.view_settings.view_transform='AgX'
 return col,floor,cam

def render(scene,cam,name,target,offset,scale,folder=FOLDER):
 cam.location=Vector(target)+Vector(offset);cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=scale;scene.render.filepath=str(folder/(name+'.jpg'));bpy.ops.render.render(write_still=True)

def main():
 FOLDER.mkdir(parents=True,exist_ok=True);bpy.ops.wm.read_factory_settings(use_empty=True);s=bpy.context.scene;s.unit_settings.system='METRIC';s.unit_settings.scale_length=1;o=model();col=bpy.data.collections.new('ASSET | traffic_cone');s.collection.children.link(col)
 for c in list(o.users_collection):c.objects.unlink(o)
 col.objects.link(o);root=bpy.data.objects.new('traffic_cone',None);col.objects.link(root);o.parent=root
 bpy.ops.object.select_all(action='DESELECT');o.select_set(True);root.select_set(True);bpy.context.view_layer.objects.active=o
 bpy.ops.export_scene.gltf(filepath=str(FOLDER/'traffic_cone.glb'),export_format='GLB',use_selection=True,export_apply=True)
 st,floor,cam=studio(s,Vector((0,0,.35)),.7)
 render(s,cam,'preview',(0,0,.35),(.85,-1.2,.7),.95)
 render(s,cam,'back',(0,0,.35),(-.85,1.2,.7),.95)
 # True underside: no floor occluding the open base and interior.
 floor.hide_render=True
 bpy.ops.object.light_add(type='AREA',location=(0,-.4,-.8));fill=bpy.context.object;fill.data.energy=25;fill.data.size=.5;fill.rotation_euler=(Vector((0,0,.25))-fill.location).to_track_quat('-Z','Y').to_euler()
 render(s,cam,'underside',(0,0,.20),(.30,-.40,-.85),.75)
 bpy.data.objects.remove(fill,do_unlink=True);floor.hide_render=False
 render(s,cam,'detail',(0,0,.64),(.3,-.5,.3),.22)
 cam.location=(.85,-1.2,1.05);cam.rotation_euler=(Vector((0,0,.35))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=.95;st.hide_viewport=True
 bpy.ops.wm.save_as_mainfile(filepath=str(FOLDER/'traffic_cone.blend'),compress=True)
 me=o.data;me.calc_loop_triangles();meta={'id':'traffic_cone','title_ja':'中空・積み重ね可能な三角コーン','category':'street','units':'meters','dimensions_m':[.36,.36,.7],'triangles':len(me.loop_triangles),'origin':'Ground plane at base center','up_axis_blend':'Z','up_axis_glb':'Y','front_blend':'-Y','construction':'One continuous manifold solid with open underside, flared annular base bore, nominal 3.2 mm radial shell wall and closed 4 mm top cap; four integrated stacking lands set a 40 mm pitch.','functional_claim_scope':'Three-instance rigid geometry nesting demonstrated and checked. Design estimates, not measured product tolerances, load certification or manufacturing approval.','limitations':'Standard PBR reflective band approximation, not optical retroreflection. Original generic design rather than a brand replica. Real flexible PVC deformation, friction and load behavior are not simulated.','reference_urls':['https://www.idc-daiichi.co.jp/products/smartcone/','https://www.idc-daiichi.co.jp/wp/wp-content/uploads/2025/07/smartcone-06.png','https://www.idc-daiichi.co.jp/products/pvcecocone/','https://topsplan-kanto.jp/rental/ks0070.html'],'reference_checked':'2026-10-16','revision':'cone-functional-r1','glb_bytes':(FOLDER/'traffic_cone.glb').stat().st_size,'blend_bytes':(FOLDER/'traffic_cone.blend').stat().st_size}
 (FOLDER/'metadata.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
