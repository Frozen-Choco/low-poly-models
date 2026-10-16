import bpy,sys,json
from pathlib import Path
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree
sys.path.insert(0,str(Path(__file__).resolve().parent));from build_assets import *
clear();bpy.ops.import_scene.gltf(filepath=str(A/'plastic_bail_bucket/plastic_bail_bucket.glb'));bpy.context.view_layer.update()
def bvh(o):return BVHTree.FromPolygons([o.matrix_world@v.co for v in o.data.vertices],[list(p.vertices) for p in o.data.polygons])
body=bvh(bpy.data.objects['Continuous bucket wall rim and closed bottom']);moving=[o for o in bpy.context.scene.objects if o.name.startswith(('Swinging hooked','Swinging molded'))];original={o.name:o.matrix_world.copy() for o in moving};pivot=Vector((0,0,.229));results=[]
for deg in [90+i*.1 for i in range(51)]:
 M=Matrix.Translation(pivot)@Matrix.Rotation(math.radians(deg),4,'X')@Matrix.Translation(-pivot)
 for o in moving:o.matrix_world=M@original[o.name]
 bpy.context.view_layer.update();contacts={o.name:len(body.overlap(bvh(o))) for o in moving};results.append({'degrees':round(deg,1),'triangle_intersections':contacts})
 if any(contacts.values()):break
(OUT/'bail_contact_validation.json').write_text(json.dumps(results,indent=2)+'\n');print(results[-2:])
