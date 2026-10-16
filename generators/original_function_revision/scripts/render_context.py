import bpy,math,os
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1]
def box(name,loc,size,color):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.name=name;o.dimensions=size;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);m.use_nodes=True;m.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(*color,1);m.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value=.65;o.data.materials.append(m)
for slug,cat in [('open_shelf','furniture'),('mug','household')]:
 if os.environ.get('ONLY_ASSETS') and slug not in os.environ['ONLY_ASSETS'].split(','):continue
 bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(R/'assets'/cat/slug/(slug+'.glb')))
 if slug=='open_shelf':
  size=1.5;center=Vector((0,0,.72));box('Context floor',(0,0,-.02),(5,5,.04),(.46,.43,.38));box('Context wall',(0,.6,1.4),(5,.06,2.8),(.68,.65,.59))
  for i in range(6):box('Book resting on shelf',(-.28+i*.034,-.01,1.1135),(.03,.22,.2),(.13+i*.018,.20+i*.012,.22))
  box('Storage box resting on shelf',(.14,-.015,.6635),(.32,.25,.18),(.42,.38,.32));campos=(2,-3,1.8)
 else:
  size=.15;center=Vector((0,0,.05));box('Context wood tabletop',(0,0,-.022),(.6,.5,.044),(.32,.17,.08));box('Context wall',(0,.25,.2),(1,.03,.6),(.64,.61,.55));campos=(.18,-.26,.17)
 sc=bpy.context.scene;sc.render.engine='CYCLES';sc.cycles.samples=32;sc.cycles.use_denoising=False;sc.render.threads_mode='FIXED';sc.render.threads=2;sc.render.resolution_x=700;sc.render.resolution_y=700;sc.render.resolution_percentage=100;sc.world=bpy.data.worlds.new('Context world');sc.world.use_nodes=True;sc.world.node_tree.nodes['Background'].inputs[1].default_value=.35
 for pos,power,col in [((-2,-3,4),450,(1,.87,.7)),((2,1,3),220,(.7,.83,1))]:
  bpy.ops.object.light_add(type='AREA',location=center+Vector(pos)*size);o=bpy.context.object;o.data.energy=power*size*size;o.data.color=col;o.data.size=size*2;o.rotation_euler=(center-o.location).to_track_quat('-Z','Y').to_euler()
 bpy.ops.object.camera_add(location=campos);cam=bpy.context.object;sc.camera=cam;cam.data.type='ORTHO';cam.data.ortho_scale=size*1.5;cam.rotation_euler=(center-cam.location).to_track_quat('-Z','Y').to_euler();sc.render.filepath=str(R/'previews'/(slug+'_placement.png'));bpy.ops.render.render(write_still=True)
