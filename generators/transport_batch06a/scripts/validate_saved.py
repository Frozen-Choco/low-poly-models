"""Saved-file structural and bounded-pose geometry audit. NEVER run until CPU release.
Checks actual separately reloaded GLB and native Blend. Does not render or save
large proof scenes. Diagnostic poses/measurements are portable JSON; optional
photos must use separately approved common renderer or labeled technical images.
Triangle intersections are candidate contacts, not force/safety simulation.
"""
import bpy, sys, json, math, hashlib, argparse
from pathlib import Path
from mathutils import Vector, Matrix
from mathutils.bvhtree import BVHTree
sys.path.insert(0,str(Path(__file__).resolve().parent))
import mechanics as M
ROOT=Path(__file__).resolve().parents[1];D=M.DESIGN

def load(path):
 if path.suffix=='.blend':bpy.ops.wm.open_mainfile(filepath=str(path))
 else:
  bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False);bpy.ops.import_scene.gltf(filepath=str(path))
 bpy.context.view_layer.update()
 return [o for o in bpy.context.scene.objects if o.type=='MESH']
def verts(o):return [o.matrix_world@v.co for v in o.data.vertices]
def bounds(objects):
 vv=[v for o in objects for v in verts(o)];return [[min(v[k] for v in vv) for k in range(3)],[max(v[k] for v in vv) for k in range(3)]]
def selection(obs,prefix):return [o for o in obs if o.name.startswith(prefix)]
def group(obs,g):return [o for o in obs if o.get('mechanical_group')==g]
def bvh(o):
 vv=verts(o);return BVHTree.FromPolygons(vv,[tuple(p.vertices) for p in o.data.polygons],all_triangles=False,epsilon=0)
def candidate_hits(aa,bb):
 out=[];trees={o.name:bvh(o) for o in aa+bb}
 for a in aa:
  ba=bounds([a])
  for b in bb:
   if a==b:continue
   bc=bounds([b])
   if any(ba[1][k]<bc[0][k] or bc[1][k]<ba[0][k] for k in range(3)):continue
   hit=trees[a.name].overlap(trees[b.name])
   if hit:out.append({'a':a.name,'b':b.name,'triangle_contact_candidates':len(hit)})
 return out

def matrix_about(origin,axis,deg):
 return Matrix.Translation(origin)@Matrix.Rotation(math.radians(deg),4,Vector(axis))@Matrix.Translation(-Vector(origin))
def general(obs):
 bad=[];tri=0;finite=True
 for o in obs:
  o.data.calc_loop_triangles();tri+=len(o.data.loop_triangles)
  for t in o.data.loop_triangles:
   a,b,c=[o.matrix_world@o.data.vertices[i].co for i in t.vertices]
   if (b-a).cross(c-a).length*.5<1e-14:bad.append([o.name,t.index])
  for v in verts(o):finite &= all(math.isfinite(x) for x in v)
 lo,hi=bounds(obs)
 return {'triangles':tri,'zero_area_triangles':bad,'finite_vertices':finite,'bounds_min_m':lo,'bounds_max_m':hi,'dimensions_m':[b-a for a,b in zip(lo,hi)],'mechanical_groups_present':sorted({o.get('mechanical_group','MISSING') for o in obs}),'materials':[{'name':m.name,'base_color':list(m.diffuse_color)} for m in bpy.data.materials if m.users]}

def bike_tests(obs,meta):
 b=D['bike'];ground=meta['construction_notes']['park_ground_adjustment_m'];park=lambda p:Vector(M.add(M.park(p),(0,0,-ground)))
 h0,h1=park(b['head_lower']),park(b['head_upper']);axis=h1-h0;bb=park(b['bottom_bracket']);saved={o.name:o.matrix_world.copy() for o in obs};out={}
 front=selection(obs,'Front wheel rubber tire');rear=selection(obs,'Rear wheel rubber tire');feet=selection(obs,'Stand ground shoe')
 out['ground_contacts']={o.name:min(v.z for v in verts(o)) for o in front+rear+feet}
 out['support_triangle_area_m2']=M.numeric_design_tests()['stand_support_triangle_area_m2']
 out['default_tire_fender_contact_candidates']=candidate_hits(front,selection(obs,'Front curved steel fender'))+candidate_hits(rear,selection(obs,'Rear curved steel fender'))
 out['chain_guard_contact_candidates']=candidate_hits(selection(obs,'Continuous enclosed chain'),group(obs,'chain_guard'))
 out['chain_frame_contact_candidates']=candidate_hits(group(obs,'drivetrain'),selection(obs,'Curved chainstay'))
 out['fork_tire_contact_candidates']=candidate_hits(front,selection(obs,'Swept fork blade')+selection(obs,'Fork crown bridge'))
 out['spoke_fork_contact_candidates']=candidate_hits(selection(obs,'Front wheel spoke'),selection(obs,'Swept fork blade'))
 brake_link=[o for o in obs if o.name.startswith(('Rear brake fixed casing','Rear brake cable adjuster','Rear brake actuator','Rear brake movable','Rear brake inner','Rear brake exposed','Rear brake cable end'))]
 out['rear_brake_linkage']={'parts':[o.name for o in brake_link],'fixed_support_reaction_arm_intended_contacts':candidate_hits(selection(obs,'Rear brake fixed casing stop support'),selection(obs,'Rear brake reaction arm')),'spoke_contact_candidates':candidate_hits(brake_link,selection(obs,'Rear wheel spoke')),'stand_contact_candidates':candidate_hits(brake_link,group(obs,'stand')),'chainstay_contact_candidates':candidate_hits(brake_link,selection(obs,'Curved chainstay')),'scope':'Static exterior linkage and clearance only; brake internals, cable tension and spring return are not simulated'}
 rear_supports=selection(obs,'Seatstay')+selection(obs,'Curved chainstay')+selection(obs,'Ring lock')+selection(obs,'Rear ring lock')+selection(obs,'Carrier')+selection(obs,'Stand')+selection(obs,'Paired stand')+selection(obs,'Rear brake')+selection(obs,'Rear roller brake')
 out['rear_support_spoke_contact_candidates']=candidate_hits(rear_supports,selection(obs,'Rear wheel spoke'))
 out['rear_frame_and_lock_obstacles']={'tire_contact_candidates':candidate_hits(selection(obs,'Ring lock')+selection(obs,'Rear ring lock')+selection(obs,'Seatstay')+selection(obs,'Curved chainstay'),rear),'spoke_contact_candidates':candidate_hits(selection(obs,'Ring lock')+selection(obs,'Rear ring lock')+selection(obs,'Seatstay')+selection(obs,'Curved chainstay'),selection(obs,'Rear wheel spoke'))}
 out['basket_rear_bracket_attachments']={str(side):{'bracket_grid_intended_contacts':candidate_hits([o for o in obs if o.name=='Basket rear bracket '+str(side)],selection(obs,'Basket horizontal grid 4')+[o for o in obs if o.name=='Basket side upright '+str(side)+' 10']),'clamp_grid_intended_contacts':candidate_hits([o for o in obs if o.name=='Basket rear bracket clamp '+str(side)],selection(obs,'Basket horizontal grid 4'))} for side in [-1,1]}
 out['steering_poses']=[]
 steering=group(obs,'steering');fixed=selection(obs,'Low step continuous')+selection(obs,'Seat tube')+selection(obs,'Head tube')
 # Headtube/steerer overlap is the intended bearing connection. We do not test
 # those against each other; only wheel/fender/basket versus fixed frame.
 moving=selection(obs,'Front wheel rubber tire')+selection(obs,'Front curved steel fender')+selection(obs,'Basket continuous rim')
 for deg in b['steer_test_degrees']:
  xf=matrix_about(h0,axis,deg)
  for o in steering:o.matrix_world=xf@saved[o.name]
  bpy.context.view_layer.update();out['steering_poses'].append({'degrees':deg,'frame_contact_candidates':candidate_hits(moving,fixed),'axis_m':[list(h0),list(h1)],'rear_brake_cable_note':'Flexible rear cable top loop is not asserted rigid-valid; must be regenerated for a supplied steered pose.'})
 for o in obs:o.matrix_world=saved[o.name]
 out['crank_poses']=[]
 crank=group(obs,'cranks');blockers=selection(obs,'Curved chainstay')+group(obs,'chain_guard')+selection(obs,'Seat tube')+selection(obs,'Paired stand leg')
 pedal_centres={}
 for side in [-1,1]:
  lo,hi=bounds(selection(obs,'Platform pedal '+str(side)));pedal_centres[side]=(Vector(lo)+Vector(hi))/2
 for deg in b['crank_test_degrees']:
  xf=matrix_about(bb,(1,0,0),deg)
  for o in crank:
   o.matrix_world=xf@saved[o.name]
   if o.name.startswith(('Platform pedal','Pedal grip rib','Pedal amber reflector')):
    side=-1 if '-1' in o.name else 1;pc=xf@pedal_centres[side];o.matrix_world=matrix_about(pc,(1,0,0),-deg)@o.matrix_world
  bpy.context.view_layer.update();out['crank_poses'].append({'added_rotation_degrees':deg,'pedal_orientation':'Counter-rotated around pedal axle to retain level platform','contact_candidates':candidate_hits(selection(obs,'Opposed crank arm')+selection(obs,'Platform pedal')+selection(obs,'Pedal axle'),blockers),'pedal_lowest_m':bounds(selection(obs,'Platform pedal'))[0][2]})
 for o in obs:o.matrix_world=saved[o.name]
 # Stand parked is actual saved geometry. Retraction around axle demonstrates
 # tire clearance; ground hits in intermediate motion are not treated as free
 # rotation while supported. Retracting a stand involves lifting/rolling frame.
 out['stand_poses']=[];pivot=Vector(meta['construction_notes']['parked_rear_axle']);stand=group(obs,'stand');legs=selection(obs,'Paired stand leg')+selection(obs,'Stand transverse brace')
 for deg in [0,25,50,75,95]:
  xf=matrix_about(pivot,(1,0,0),deg)
  for o in stand:o.matrix_world=xf@saved[o.name]
  bpy.context.view_layer.update();out['stand_poses'].append({'rotation_degrees':deg,'tire_contact_candidates':candidate_hits(legs,rear),'spoke_contact_candidates':candidate_hits(legs,selection(obs,'Rear wheel spoke')),'lowest_m':bounds(legs)[0][2],'scope':'No assertion that ground stays fixed during retraction'})
 for o in obs:o.matrix_world=saved[o.name]
 return out

def cart_tests(obs,meta):
 c=D['cart'];saved={o.name:o.matrix_world.copy() for o in obs};out={};wheels=[o for o in obs if o.name.endswith('wheel rubber tire')]
 out['wheel_ground_extrema_m']={o.name:min(v.z for v in verts(o)) for o in wheels}
 out['wheel_fork_contact_candidates']=[]
 for front in [True,False]:
  for side in [-1,1]:
   name=('swivel' if front else 'fixed')+'_caster_'+str(side)
   out['wheel_fork_contact_candidates']+=candidate_hits(selection(obs,name+' wheel rubber tire'),selection(obs,name+' supporting fork cheek')+selection(obs,name+' fixed upright crown')+selection(obs,name+' fork crown'))
 out['slot_meshes']={o.name:{'vertices':len(o.data.vertices),'polygons':len(o.data.polygons)} for o in selection(obs,'Stationary open slot cheek')}
 # A ray through each slot center along X must miss every stationary cheek.
 out['slot_rays']=[]
 for o in selection(obs,'Stationary open slot cheek'):
  tree=bvh(o)
  for frac in [.1,.5,.9]:
   a=M.lock_pin(True);b=M.lock_pin(False);p=Vector(M.add(a,M.mul(M.sub(b,a),frac)));p.x=-1
   hit=tree.ray_cast(p,Vector((1,0,0)),2)
   out['slot_rays'].append({'cheek':o.name,'slot_fraction':frac,'open':hit[0] is None})
 delta=Vector(M.sub(M.lock_pin(True),M.lock_pin(False)));release=group(obs,'lock_release');handle=group(obs,'handle')
 cheeks=selection(obs,'Stationary open slot cheek');deck=group(obs,'deck');socket=cheeks+selection(obs,'Hinge base shoe')+selection(obs,'Stationary rear cradle')
 # Verify release can traverse the real slot. Intended pin/tongue support has
 # design clearance; transverse release steel is the only moving latch proxy.
 out['release_poses']=[]
 for frac in [0,.25,.5,.75,1]:
  for o in release:o.matrix_world=Matrix.Translation(delta*frac)@saved[o.name]
  bpy.context.view_layer.update();out['release_poses'].append({'fraction':frac,'cheek_contact_candidates':candidate_hits(release,cheeks)})
 # Keep release pin at its fully released position for fold sequence.
 out['fold_poses']=[]
 for deg in c['fold_test_degrees']:
  xf=matrix_about(Vector(c['hinge_pivot']),(1,0,0),deg)
  for o in handle:o.matrix_world=xf@saved[o.name]
  bpy.context.view_layer.update();out['fold_poses'].append({'degrees':deg,'socket_contact_candidates':candidate_hits(handle,socket),'deck_contact_candidates':candidate_hits(handle,deck),'released_pin_contact_candidates':candidate_hits(selection(obs,'Moving handle lock tongue'),release),'handle_bounds_m':bounds(handle)})
 for o in obs:o.matrix_world=saved[o.name]
 out['caster_swivel_poses']=[]
 for side in [-1,1]:
  name='swivel_caster_'+str(side);assembly=group(obs,name)
  # Upper mounting plate, bolt/boss and upper collar are stationary; lower fork,
  # wheel and axle rotate about the vertical kingpin. Do not spin the deck bolts.
  moving=[o for o in assembly if any(k in o.name for k in ['supporting fork cheek','axle cap','wheel rubber tire','polymer wheel hub','steel through axle','hub lip','fork crown'])]
  pivot=Vector((side*c['caster_x'],-c['caster_y'],0))
  for deg in c['swivel_test_degrees']:
   xf=matrix_about(pivot,(0,0,1),deg)
   for o in moving:o.matrix_world=xf@saved[o.name]
   bpy.context.view_layer.update();out['caster_swivel_poses'].append({'side':side,'degrees':deg,'deck_contact_candidates':candidate_hits(moving,deck),'lowest_wheel_m':bounds(selection(obs,name+' wheel rubber tire'))[0][2]})
  for o in assembly:o.matrix_world=saved[o.name]
 out['load_proxy']={'dimensions_m':[.35,.50,.30],'centre_m':[0,-.025,.321],'bottom_m':.171,'deck_footprint_margin_m':[(.49-.35)/2,(.73-.50)/2],'scope':'Placement proxy only, no payload rating'}
 return out

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--asset',choices=['all','city_bicycle','folding_platform_handcart'],default='all');args=ap.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
 outdir=ROOT/'evidence';outdir.mkdir(exist_ok=True)
 for slug in ['city_bicycle','folding_platform_handcart']:
  if args.asset not in ['all',slug]:continue
  folder=ROOT/'assets'/slug;meta=json.loads((folder/'metadata.json').read_text());result={'scope':'Saved-file mesh checks and candidate intersections; independent reviewer decides acceptance','design_checks':M.numeric_design_tests(),'files':{}}
  for suffix in ['.blend','.glb']:
   path=folder/(slug+suffix);before=hashlib.sha256(path.read_bytes()).hexdigest();obs=load(path);rec=general(obs);rec['bytes']=path.stat().st_size;rec['sha256']=before
   rec['use_tests']=bike_tests(obs,meta) if slug=='city_bicycle' else cart_tests(obs,meta)
   rec['source_unchanged']=hashlib.sha256(path.read_bytes()).hexdigest()==before;rec['under_size_limit']=path.stat().st_size<100_000_000;result['files'][suffix]=rec
  (outdir/(slug+'_saved_mesh_checks.json')).write_text(json.dumps(result,indent=2)+'\n');print('AUDIT_WRITTEN',slug)
if __name__=='__main__':main()
