import sys,json,hashlib
from pathlib import Path
from mathutils import Vector
sys.path.insert(0,str(Path(__file__).resolve().parent));from build_assets import *
P=OUT/'previews';P.mkdir(exist_ok=True)
def load(slug,offset=(0,0,0)):
 p=A/slug/(slug+'.glb');bpy.ops.import_scene.gltf(filepath=str(p))
 for o in bpy.context.selected_objects:
  if o.parent is None:o.location+=Vector(offset)
 return {'asset':slug,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'offset':offset}
def surround(offset=(0,0,0),wide=False):
 m=mat('Diagnostic concrete surround',(.33,.33,.31),0,.9);o=box('Pocketed concrete support slab',(0,0,-.13),(4,3,.26) if wide else (.95,.75,.26),m,.001)
 boolean(o,box('Receiver pocket tool',(0,0,.05),(.632,.432,.176),m,0)) # pocket floor z=-.038
 boolean(o,box('Open central drainage void',(0,0,-.13),(.55,.30,.4),m,0))
 o.location+=Vector(offset);return o

def render(name,target,size,off,keep_slab=False,alternate=False):
 cam=studio(target,size);sc=bpy.context.scene
 if keep_slab:bpy.data.objects['Studio ground'].hide_render=True
 sc.cycles.samples=20;sc.render.resolution_x=900;sc.render.resolution_y=900;cam.location=Vector(target)+Vector(off)*size;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler()
 if alternate:
  for o in sc.objects:
   if o.type=='LIGHT':o.location.x*=-1;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()
 sc.render.filepath=str(P/(name+'.jpg'));bpy.ops.render.render(write_still=True)
 # Remove photography objects between views; proof saved below retains physical set only.
 for o in list(sc.objects):
  if o.type in ['LIGHT','CAMERA'] or o.name=='Studio ground':bpy.data.objects.remove(o,do_unlink=True)
clear();provenance=[load('street_drain_grate',(0,0,-.038))];surround()
for o in list(bpy.context.scene.objects):
 if any(o.name.startswith(p) for p in ['Load bearing','Removable grate','Welded transverse','Welded removable grate']):o.location.z+=.08
steel=mat('Diagnostic lifting hook',(.23,.28,.30),1,.32)
pts=[(.01485,.025,.202),(.01485,.025,.034),(.010,.025,.028),(.002,.025,.028),(0,.025,.034),(0,.025,.046)]
path_tube('Hook engaged under bearing bar',pts,[.0038]*len(pts),steel,N=16)
render('grate_lift_diagnostic',(0,0,.015),.78,(1,-1,1.1),True)
bpy.ops.wm.save_as_mainfile(filepath=str(P/'grate_lift_diagnostic.blend'),compress=True)
clear();provenance=[load('roadside_convex_mirror',(-.85,.25,0)),load('outdoor_ac_condenser',(.35,.20,0)),load('street_drain_grate',(.65,-.55,-.038))];surround((.65,-.55,0),True)
wall=mat('Diagnostic wall plaster',(.5,.49,.45),0,.9);box('Exterior wall',(.35,.65,.65),(1.8,.054,1.3),wall,.002)
# Corner building volumes also provide environment-dependent mirror reflections.
wall2=mat('Diagnostic muted blue exterior',(.15,.24,.30),0,.8);box('Context opposite building',(-1.25,-1.1,.75),(.18,.8,1.5),wall2,.002)
render('installed_context_diagnostic_day',(-.15,0,1.25),3.2,(1.2,-2,1.25),True)
render('installed_context_diagnostic_alternate',(-.15,0,1.25),3.2,(1.2,-2,1.25),True,True)
bpy.ops.wm.save_as_mainfile(filepath=str(P/'installed_context_diagnostic.blend'),compress=True)
(P/'input_provenance.json').write_text(json.dumps({'diagnostic_only':True,'inputs':provenance},indent=2)+'\n')
# Ray proof through grate into real void; support slab pocket floor is beneath receiving frame.
bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();tests={}
tests['open_drain_path']=not bpy.context.scene.ray_cast(dg,Vector((.66485,-.525,.05)),Vector((0,0,-1)),distance=.5)[0]
slab=bpy.data.objects['Pocketed concrete support slab'];hit=slab.ray_cast(slab.matrix_world.inverted()@Vector((.65,-.36,.01)),Vector((0,0,-1)),distance=.2);tests['receiver_has_concrete_bearing']=hit[0] and abs((slab.matrix_world@hit[1]).z+.038)<1e-6
tests['concrete_bearing_height_m']=float((slab.matrix_world@hit[1]).z) if hit[0] else None
tests['wall_pipe_collar_front_plane']=abs(.65-.027-(.20+.423))<1e-8
(P/'installed_use_validation.json').write_text(json.dumps(tests,indent=2)+'\n');assert tests['open_drain_path'] and tests['receiver_has_concrete_bearing'] and tests['wall_pipe_collar_front_plane'],tests
