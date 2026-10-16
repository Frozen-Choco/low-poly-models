import bpy,math,json,hashlib,sys
from pathlib import Path
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];OUT=R/'functional';results={}
def vs(o):return [o.matrix_world@v.co for v in o.data.vertices]
def tree(o,verts=None):return BVHTree.FromPolygons(vs(o) if verts is None else verts,[list(p.vertices) for p in o.data.polygons])
def bounds(o):
 v=vs(o);return [[min(p[i] for p in v) for i in range(3)],[max(p[i] for p in v) for i in range(3)]]
def render(name,campos,target,scale):
 s=bpy.context.scene;s.render.engine='BLENDER_WORKBENCH';s.display.shading.light='STUDIO';s.display.shading.color_type='MATERIAL';s.display.shading.show_shadows=True;s.display.shading.show_cavity=True;s.display.shading.background_type='WORLD';s.world=s.world or bpy.data.worlds.new('DiagnosticWorld');s.world.color=(.16,.16,.16)
 for o in s.objects:
  if o.type in ['LIGHT','CAMERA'] or o.name=='Plane':o.hide_render=True
 bpy.ops.object.camera_add(location=campos);c=bpy.context.object;c.hide_render=False;c.rotation_euler=(Vector(target)-c.location).to_track_quat('-Z','Y').to_euler();c.data.type='ORTHO';c.data.ortho_scale=scale;s.camera=c;s.render.resolution_x=800;s.render.resolution_y=800;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.render.filepath=str(OUT/(name+'.png'));bpy.ops.render.render(write_still=True)
for ext in ['blend','glb']:
 slug='railway_crossing_lowered';path=R/'assets'/slug/(slug+'.'+ext)
 if ext=='blend':bpy.ops.wm.open_mainfile(filepath=str(path))
 else:bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(path))
 render(slug+'_'+ext+'_side',(9,-.15,2.4),(2,0,1.8),4.6)
 render(slug+'_'+ext+'_underside',(3,-3,-5),(2,0,.7),6)
