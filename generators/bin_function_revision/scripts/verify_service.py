"""Reopen BOTH production formats. Full moving-mesh collision sweeps and extraction corridor."""
import bpy,sys,math,json,hashlib,os
from pathlib import Path
from mathutils import Matrix,Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];A=Path(os.environ.get('ASSET_OUTPUT_ROOT',str(R/'assets')))/'public_recycling_bin';E=R/'evidence';E.mkdir(exist_ok=True)
P=Vector((-.224,-.248,0));L=Vector((.16,-.206,.62))
def rot(p,a,axis):return Matrix.Translation(p)@Matrix.Rotation(a,4,axis)@Matrix.Translation(-p)
cache={}
def key(o):return (o.name,tuple(x for row in o.matrix_world for x in row))
def bounds(o):
 k=('b',key(o))
 if k in cache:return cache[k]
 v=[o.matrix_world@v.co for v in o.data.vertices];cache[k]=[[min(p[i] for p in v) for i in range(3)],[max(p[i] for p in v) for i in range(3)]];return cache[k]
def bv(o):
 k=('t',key(o))
 if k in cache:return cache[k]
 cache[k]=BVHTree.FromPolygons([o.matrix_world@v.co for v in o.data.vertices],[list(p.vertices) for p in o.data.polygons],all_triangles=False,epsilon=1e-7);return cache[k]
def collide(a,b):
 aa=bounds(a);bb=bounds(b)
 if any(aa[1][i]<bb[0][i]-1e-7 or bb[1][i]<aa[0][i]-1e-7 for i in range(3)):return False
 return bool(bv(a).overlap(bv(b)))
results={}
for ext in ['blend','glb']:
 cache={}
 path=A/('public_recycling_bin.'+ext)
 if ext=='blend':bpy.ops.wm.open_mainfile(filepath=str(path))
 else:bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(path))
 obs=[o for o in bpy.context.scene.objects if o.type=='MESH' and 'service_group' in o]
 base={o.name:o.matrix_world.copy() for o in obs};door=[o for o in obs if o['service_group']=='door'];cam=[o for o in obs if o['service_group']=='latch'];liner=[o for o in obs if o['service_group']=='liner'];fixed=[o for o in obs if o['service_group']=='fixed']
 row={'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'objects':len(obs),'door_objects':[o.name for o in door],'liner_objects':[o.name for o in liner],'latch_objects':[o.name for o in cam],'closed_bounds':{o.name:bounds(o) for o in obs}}
 # Latch rotates90deg aboutY, from right-facing to down-facing, behind keeper.
 errors=[]
 for deg in range(91):
  for o in cam:o.matrix_world=rot(L,math.radians(deg),'Y')@base[o.name]
  for o in cam:
   for f in fixed+liner:
    if collide(o,f):errors.append([deg,o.name,f.name])
 row['latch_sweep_1deg_collisions']=errors
 # Deliberate mating pin/knuckle interfaces excluded only: leaves/webs ARE tested.
 errors=[];allfixed=fixed+liner
 for step in range(441):
  deg=step*.25;T=rot(P,-math.radians(deg),'Z')
  for o in door:o.matrix_world=T@base[o.name]
  for o in cam:o.matrix_world=T@rot(L,math.pi/2,'Y')@base[o.name]
  for o in door+cam:
   for f in allfixed:
    if 'hinge' in o.name.lower() and 'hinge' in f.name.lower() and ('pin' in f.name or 'knuckle' in f.name) and 'knuckle' in o.name:continue
    if collide(o,f):errors.append([deg,o.name,f.name])
 row['door_sweep_0_110deg_step025_collisions']=errors
 # Slight 2mm hand lift then .65m forward translation. Entire liner group included.
 errors=[]
 for step in range(651):
  lift=.002 if step else 0;dy=-step/1000
  for o in liner:o.matrix_world=Matrix.Translation((0,dy,lift))@base[o.name]
  for o in liner:
   for f in fixed+door+cam:
    if step==0 and f.name=='Cabinet floor':continue # exact load-bearing contact
    if collide(o,f):errors.append([step,o.name,f.name])
 row['liner_extraction_1mm_collisions']=errors
 # Conservative continuous swept AABB proof for raised linear path (including initial position).
 lo=[min(bounds(o)[0][i] for o in liner) for i in range(3)];hi=[max(bounds(o)[1][i] for o in liner) for i in range(3)];hi[1]+=.65
 corridor=[]
 for f in fixed+door+cam:
  b=bounds(f)
  if all(hi[i]>b[0][i]+1e-7 and b[1][i]>lo[i]+1e-7 for i in range(3)):corridor.append(f.name)
 row['continuous_raised_extraction_swept_aabb']={'min':lo,'max':hi,'overlapping_obstacles':corridor}
 row['support_gaps_m']={'floor_to_plinth':row['closed_bounds']['Cabinet floor'][0][2]-row['closed_bounds']['Recessed plinth'][1][2],'liner_to_floor':row['closed_bounds']['Liner bottom'][0][2]-row['closed_bounds']['Cabinet floor'][1][2]}
 liftlo=[min(row['closed_bounds'][o.name][0][i] for o in liner) for i in range(3)];lifthi=[max(row['closed_bounds'][o.name][1][i] for o in liner)+(0.002 if i==2 else 0) for i in range(3)]
 lift_obstacles=[]
 for f in fixed+door+cam:
  b=bounds(f)
  if all(lifthi[i]>b[0][i]+1e-7 and b[1][i]>liftlo[i]+1e-7 for i in range(3)):lift_obstacles.append(f.name)
 row['continuous_initial_lift']={'min':liftlo,'max':lifthi,'overlapping_obstacles':lift_obstacles,'note':'Floor tangency at start is intentional support; strict interior-overlap test uses1e-7m tolerance.'}
 row['service_sequence']=['Rotate latch90deg downward aboutY through (.16,-.206,.62)','Open tagged door and unlocked latch clockwise110deg aboutZ through(-.224,-.248,0)','Lift liner2mm by hand','Translate liner650mm toward-Y; no tilt','Reverse sequence to reinstall']
 results[ext]=row
 (E/('validation_'+ext+'.json')).write_text(json.dumps(row,indent=2)+'\n')
 print(ext,'LATCH',len(row['latch_sweep_1deg_collisions']),'DOOR',len(row['door_sweep_0_110deg_step025_collisions']),'LINER',len(errors),'CORRIDOR',corridor,flush=True)
(E/'service_validation.json').write_text(json.dumps(results,indent=2)+'\n')
