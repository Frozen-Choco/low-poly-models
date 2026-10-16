import bpy,json,sys,math,hashlib,struct,os
from pathlib import Path
from mathutils import Vector
root=Path(__file__).resolve().parents[2];out=root/'original_function_revision/previews';results={}
for slug in ['open_shelf','mug']:
 if os.environ.get('ONLY_ASSETS') and slug not in os.environ['ONLY_ASSETS'].split(','):continue
 p=next((root/'original_function_revision/assets').rglob(slug+'.blend'))
 for typ in ['blend','glb']:
  src=p.with_suffix('.'+typ)
  if typ=='blend': bpy.ops.wm.open_mainfile(filepath=str(src))
  else:
   bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(src))
  for o in list(bpy.data.objects):
   if o.type!='MESH' or o.name=='Preview ground':bpy.data.objects.remove(o,do_unlink=True)
  obs=list(bpy.context.scene.objects)
  for c in bpy.data.collections:c.hide_viewport=False;c.hide_render=False
  stats={};pts=[]
  for o in obs:
   vs=[o.matrix_world@v.co for v in o.data.vertices];pts+=vs
   stats[o.name]={'min':[min(v[i] for v in vs) for i in range(3)],'max':[max(v[i] for v in vs) for i in range(3)],'materials':[m.name for m in o.data.materials]}
  results[slug+'_'+typ]={'source':str(src),'sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'bytes':src.stat().st_size,'objects':stats}
  lo=Vector([min(v[i] for v in pts) for i in range(3)]);hi=Vector([max(v[i] for v in pts) for i in range(3)]);center=(lo+hi)/2;size=max(hi-lo)
  sc=bpy.context.scene;sc.render.engine='CYCLES';sc.cycles.samples=8;sc.cycles.use_denoising=False;sc.render.threads_mode='FIXED';sc.render.threads=2;sc.render.resolution_x=500;sc.render.resolution_y=500;sc.render.resolution_percentage=100;sc.world=bpy.data.worlds.new('Audit world');sc.world.use_nodes=True;sc.world.node_tree.nodes['Background'].inputs[0].default_value=(.5,.5,.5,1);sc.world.node_tree.nodes['Background'].inputs[1].default_value=.6
  bpy.ops.object.camera_add();cam=bpy.context.object;sc.camera=cam;cam.data.type='ORTHO';cam.data.ortho_scale=size*1.4
  for loc,energy in [((2,-3,4),450),((-2,1,2),300)]:
   bpy.ops.object.light_add(type='AREA',location=center+Vector(loc)*size);l=bpy.context.object;l.data.energy=energy*size*size;l.data.size=size*2;l.rotation_euler=(center-l.location).to_track_quat('-Z','Y').to_euler()
  for name,loc in [('front',(1,-2,1)),('side',(2,0,.4)),('back',(-1,2,.8)),('under',(1,-2,-2)),('top',(0,-.2,3))]:
   cam.location=center+Vector(loc)*size;cam.rotation_euler=(center-cam.location).to_track_quat('-Z','Y').to_euler();sc.render.filepath=str(out/(slug+'_'+typ+'_'+name+'.png'));bpy.ops.render.render(write_still=True)
  details=[('joint',(.024,0,.024),(.4,-1,.1),.035),('aperture',(.033,0,.058),(0,-1,0),.12)] if slug=='mug' else [('joint',(.435,.18,1.41),(1,2,.5),.13),('board_clearance',(0,.18,1),(1,2,-.3),.7),('crossing',(0,.188,.795),(1,2,.5),.16)]
  for name,target,direction,scale in details:
   target=Vector(target);cam.data.ortho_scale=scale;cam.location=target+Vector(direction)*size;cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();sc.render.filepath=str(out/(slug+'_'+typ+'_'+name+'.png'));bpy.ops.render.render(write_still=True)
  sc.world.node_tree.nodes['Background'].inputs[0].default_value=(.32,.42,.6,1)
  sc.world.node_tree.nodes['Background'].inputs[1].default_value=.3
  cam.data.ortho_scale=size*1.4;cam.location=center+Vector((1,-2,1))*size;cam.rotation_euler=(center-cam.location).to_track_quat('-Z','Y').to_euler();sc.render.filepath=str(out/(slug+'_'+typ+'_cool_context.png'));bpy.ops.render.render(write_still=True)
(out/'geometry.json').write_text(json.dumps(results,indent=2))
