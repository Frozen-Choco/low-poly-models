"""Reopen the saved service proof poses and compare actual mesh bounds to intended transforms."""
import bpy,json,math,os,hashlib
from pathlib import Path
from mathutils import Matrix,Vector
R=Path(__file__).resolve().parents[1];A=Path(os.environ.get('ASSET_OUTPUT_ROOT',str(R/'assets')))/'public_recycling_bin';E=R/'evidence'
bpy.ops.wm.open_mainfile(filepath=str(A/'public_recycling_bin.blend'))
base={o.name:{'vertices':[o.matrix_world@v.co for v in o.data.vertices],'group':o['service_group']} for o in bpy.context.scene.objects if o.type=='MESH' and 'service_group' in o}
def rot(p,a,axis):return Matrix.Translation(p)@Matrix.Rotation(a,4,axis)@Matrix.Translation(-p)
def bb(v):return [min(p[i] for p in v) for i in range(3)]+[max(p[i] for p in v) for i in range(3)]
T=rot(Vector((-.224,-.248,0)),-math.radians(110),'Z');U=rot(Vector((.16,-.206,.62)),math.pi/2,'Y');report={}
for pose in ['service_open','liner_removed']:
 for ext in ['blend','glb']:
  p=E/(pose+'.'+ext)
  if ext=='blend':bpy.ops.wm.open_mainfile(filepath=str(p))
  else:bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(p))
  differences={}
  for o in bpy.context.scene.objects:
   if o.type!='MESH' or 'service_group' not in o:continue
   b=base[o.name];g=b['group'];M=T if g=='door' else T@U if g=='latch' else Matrix.Translation((0,-.65,.002)) if g=='liner' and pose=='liner_removed' else Matrix.Identity(4)
   actual=bb([o.matrix_world@v.co for v in o.data.vertices]);expected=bb([M@v for v in b['vertices']]);differences[o.name]=max(abs(a-b) for a,b in zip(actual,expected))
  assert len(differences)==len(base)
  assert max(differences.values())<1e-5
  report[pose+'.'+ext]={'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'meshes':len(differences),'maximum_bound_difference_m':max(differences.values()),'pose_matches_intended_transforms':True}
(E/'saved_evidence_validation.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
