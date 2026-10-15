"""Bounding/contact proxies for visual construction, not manufacturing tolerances."""
import bpy,json,os
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];A=Path(os.environ.get('ASSET_OUTPUT_ROOT',str(R/'assets')))
for o in list(bpy.data.objects):bpy.data.objects.remove(o,do_unlink=True)
bpy.ops.import_scene.gltf(filepath=str(A/'public_recycling_bin'/'public_recycling_bin.glb'))
obs=[o for o in bpy.context.scene.objects if o.type=='MESH']
def nearest(prefix,point):return min([o for o in obs if o.name.startswith(prefix)],key=lambda o:(o.matrix_world.translation-Vector(point)).length)
def bounds(o):
 v=[o.matrix_world@p.co for p in o.data.vertices];return ([min(p[i] for p in v) for i in range(3)],[max(p[i] for p in v) for i in range(3)])
def contact(a,b):
 aa,ab=bounds(a);ba,bb=bounds(b);return {'parts':[a.name,b.name],'axis_overlap_m':[min(ab[i],bb[i])-max(aa[i],ba[i]) for i in range(3)]}
pairs=[]
for z in [.25,.55]:
 fixed=nearest('Fixed hinge mounting return',(-.224,-.223,z));leaf=nearest('Hinge attachment leaf',(-.219,-.240,z));seat=nearest('Door hinge attachment seat',(-.195,-.236,z));moving=nearest('Hinge attachment leaf',(-.195,-.240,z));skin=nearest('Two millimetre painted door skin',(0,-.233,.405));ret=nearest('Side sheet folded return',(-.224,-.211,.52))
 pairs += [contact(fixed,ret),contact(fixed,leaf),contact(moving,seat),contact(seat,skin)]
report={'scope':'AABB overlap proxies for hinge mount-to-cabinet, leaves-to-seats and seat-to-door, plus true side-skin dimensions; not manufacturing clearances or manifold union checks. Hinge barrel/pin are separate visible hardware.','connection_proxies':pairs,'all_tested_mount_pairs_overlap':all(min(p['axis_overlap_m'])>=-1e-6 for p in pairs),'side_skin_dimensions_m':[list(o.dimensions) for o in obs if o.name.startswith('Two millimetre folded side sheet')]}
(R/'bin_construction_audit.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2));assert report['all_tested_mount_pairs_overlap']
