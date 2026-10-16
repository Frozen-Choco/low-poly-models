import bpy,math,json,sys
from pathlib import Path
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree
sys.path.insert(0,str(Path(__file__).resolve().parent));from build_kettle import *
P=R/'previews';f=A/'stainless_kitchen_kettle';clear();bpy.ops.import_scene.gltf(filepath=str(f/'stainless_kitchen_kettle.glb'));obs=[o for o in bpy.context.scene.objects if o.type=='MESH'];moving=[o for o in obs if o.name.startswith(('Fore-aft insulated','Moving stainless'))];fixed=[o for o in obs if o.name.startswith(('Formed hollow','Seated removable','Lid insulated','Tapered hollow','Fixed shoulder'))]
def bvh(o,M):return BVHTree.FromPolygons([M@o.matrix_world@v.co for v in o.data.vertices],[p.vertices[:] for p in o.data.polygons],all_triangles=False)
fixedb=[(o.name,bvh(o,Matrix.Identity(4))) for o in fixed];pivot=Vector((0,0,.152));sweep=[]
for deg in range(-90,91,1):
 M=Matrix.Translation(pivot)@Matrix.Rotation(math.radians(deg),4,'X')@Matrix.Translation(-pivot);hits=[]
 for o in moving:
  B=bvh(o,M)
  for n,F in fixedb:
   if B.overlap(F):hits.append([o.name,n])
 sweep.append(dict(degrees=deg,intersecting_pairs=hits))
report=dict(scope='Sampled triangle-surface intersection test, every 1 degree from -90 to +90 degree lateral fold. Excludes deliberate pin/bore bearing contacts and moving-to-moving overlap. Not a continuous collision proof.',sweep=sweep,all_sampled_clear=all(not x['intersecting_pairs'] for x in sweep));(R/'swept_fold_audit.json').write_text(json.dumps(report,indent=2)+'\n');assert report['all_sampled_clear'],report
# Full initial lid extraction, then full lift, against the actual saved body mesh.
body=next(o for o in obs if o.name.startswith('Formed hollow'));bodyb=bvh(body,Matrix.Identity(4));lidparts=[o for o in obs if o.name.startswith(('Seated removable','Lid insulated'))];extraction=[]
for mm in sorted(set([i*.1 for i in range(51)]+[i*.25 for i in range(21,61)]+list(range(16,106)))):
 M=Matrix.Translation((0,0,mm/1000));pairs=[]
 for o in lidparts:
  overlaps=bvh(o,M).overlap(bodyb)
  if overlaps:pairs.append(dict(part=o.name,pairs=len(overlaps)))
 extraction.append(dict(lift_mm=mm,intersections=pairs))
extract_report=dict(scope='Saved-GLB triangle-surface intersection test: 0–5 mm at 0.1 mm intervals, 5.25–15 mm at 0.25 mm intervals, then 16–105 mm at 1 mm intervals. 2 micrometre numerical gap at seated flange avoids contact-only overlap ambiguity; not manufacturing tolerances.',positions=extraction,all_sampled_clear=all(not p['intersections'] for p in extraction));(R/'lid_extraction_audit.json').write_text(json.dumps(extract_report,indent=2)+'\n');assert extract_report['all_sampled_clear'],extract_report
# Diagnostic hand envelopes are clearly colored and excluded from main asset.
blue=mat('BLUE grip clearance envelope - not a modeled hand',(.04,.24,.44),0,.65);orange=mat('ORANGE lid retention contact envelope',(.7,.22,.03),0,.6)
proxies=[]
for x in [-.027,-.009,.009,.027]:
 z=.172+.087*math.sqrt(1-(x/.085)**2)
 bpy.ops.mesh.primitive_torus_add(major_radius=.018,minor_radius=.004,major_segments=32,minor_segments=12,location=(x,0,z),rotation=(0,math.pi/2,0));o=bpy.context.object;o.name='Grip finger clearance envelope';o.data.materials.append(blue);proxies.append(o)
proxies.append(box('Grip palm envelope',(0,0,.283),(.079,.027,.022),blue,.006))
proxies.append(path_tube('Lid retaining fingertip contact envelope',[(0,0,.176),(0,0,.215)],[.006,.006],orange,N=24))
grip=Vector((0,0,.259));pose=Matrix.Translation(grip+Vector((0,0,.10)))@Matrix.Rotation(math.radians(35),4,'Y')@Matrix.Translation(-grip)
for o in obs+proxies:o.matrix_world=pose@o.matrix_world
cam=studio((.04,0,.22),.43);cam.location=(.55,-1.1,.65);cam.rotation_euler=(Vector((.04,0,.22))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=.60
for text,pos,material in [('BLUE: grip clearance',(-.18,0,.46),blue),('ORANGE: lid held',(-.18,0,.43),orange),('Diagnostic envelopes, not hand anatomy',(-.18,0,.015),blue)]:
 bpy.ops.object.text_add(location=pos);o=bpy.context.object;o.data.body=text;o.data.size=.012;o.rotation_euler=cam.rotation_euler;o.data.materials.append(material)
sc=bpy.context.scene;sc.render.resolution_x=1000;sc.render.resolution_y=1000;sc.cycles.samples=64;sc.render.filepath=str(P/'grip_and_lid_contact_diagnostic.jpg');bpy.ops.render.render(write_still=True);bpy.ops.wm.save_as_mainfile(filepath=str(P/'grip_diagnostic.blend'),compress=True)
