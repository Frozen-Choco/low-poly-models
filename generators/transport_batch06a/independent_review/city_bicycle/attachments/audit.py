import bpy,sys,json,hashlib
from pathlib import Path
sys.path.insert(0,'/workspace/scratch/a456259dbd5d/lowpoly_batch06a/scripts')
import validate_saved as V
R=Path('/workspace/scratch/a456259dbd5d');out={}
for ext in ['blend','glb']:
 p=R/'lowpoly_batch06a/assets/city_bicycle'/('city_bicycle.'+ext);obs=V.load(p);trees={o.name:V.bvh(o) for o in obs};vv={o.name:V.verts(o) for o in obs};rows=[]
 def test(label,ap,bp):
  aa=[o for o in obs if any(o.name.startswith(x) for x in ap)];bb=[o for o in obs if any(o.name.startswith(x) for x in bp)]
  for a in aa:
   ds=[]
   for b in bb:
    if a==b:continue
    hits=len(trees[a.name].overlap(trees[b.name]));d=min(trees[b.name].find_nearest(v)[3] for v in vv[a.name]);ds.append({'target':b.name,'distance_m':d,'surface_contacts':hits})
   ds.sort(key=lambda x:x['distance_m']);rows.append({'joint':label,'part':a.name,'nearest':ds[:3],'any_surface_contact':any(d['surface_contacts'] for d in ds)})
 test('basket rear to basket',['Basket rear bracket'],['Basket continuous','Basket side','Basket end','Basket horizontal','Basket floor'])
 test('basket rear to head',['Basket rear bracket'],['Head tube','Continuous fork steerer','Handlebar stem'])
 test('basket axle stay to floor',['Basket axle mounting stay'],['Basket floor','Basket continuous rim 0.78'])
 test('basket axle stay to axle',['Basket axle mounting stay'],['Front wheel axle','Front wheel continuous axle','Front wheel hex','Front dropout'])
 for side in ['Front','Rear']:
  test(side+' mudguard stay to fender',[side+' mudguard stay'],[side+' curved steel fender'])
  test(side+' mudguard stay to axle',[side+' mudguard stay'],[side+' wheel axle',side+' wheel continuous axle',side+' wheel hex',side+' dropout'])
 test('carrier axle strut to axle',['Carrier axle strut'],['Rear wheel axle','Rear wheel continuous axle','Rear wheel hex','Rear dropout','Stand pivot sleeve'])
 test('carrier frame strut to frame',['Carrier frame strut'],['Seat tube','Seatstay','Seatpost collar'])
 test('carrier strut to rack',['Carrier axle strut','Carrier frame strut'],['Rear carrier perimeter','Carrier crossbar'])
 test('saddle rail to saddle',['Saddle supporting rail'],['Sculpted padded saddle'])
 test('saddle rail to clamp',['Saddle supporting rail'],['Saddle rail clamp'])
 test('saddle clamp to post',['Saddle rail clamp'],['Seatpost'])
 test('ring lock mounts to frame',['Ring lock frame clamp'],['Ring lock clamp seatstay bridge'])
 test('ring lock mounts to housing',['Ring lock frame clamp'],['Rear ring lock'])
 test('stand leg to hinge',['Paired stand leg'],['Stand pivot sleeve'])
 test('stand leg to foot',['Paired stand leg'],['Stand ground shoe'])
 test('stand hinge to axle',['Stand pivot sleeve'],['Rear wheel axle','Rear wheel continuous axle','Rear wheel hex','Rear dropout'])
 test('stand brace/tab to leg',['Stand transverse brace','Stand left foot press tab'],['Paired stand leg'])
 test('stand stop to stationary structure',['Stand stationary stop'],['Rear dropout','Rear wheel axle','Stand pivot sleeve'])
 test('front caliper support to fork',['Front caliper mounting bolt','Front caliper crown mounting bridge'],['Fork crown bridge','Continuous fork steerer'])
 test('front pad to arm',['Front rim brake pad'],['Front caliper arm'])
 test('dynamo clamp to fork',['Dynamo fork clamp'],['Swept fork blade'])
 test('dynamo clamp to body',['Dynamo fork clamp'],['Block dynamo body'])
 test('rear brake reaction to clamp',['Rear brake reaction arm'],['Brake reaction chainstay clamp'])
 test('rear brake clamp to stay',['Brake reaction chainstay clamp'],['Curved chainstay'])
 test('stand spring to fixed hook',['Stand return spring'],['Stand spring fixed upper hook'])
 test('fixed hook to stop',['Stand spring fixed upper hook'],['Stand stationary stop'])
 test('stand spring to moving hook',['Stand return spring'],['Stand spring moving lower hook'])
 test('moving hook to stand',['Stand spring moving lower hook'],['Paired stand leg'])
 test('stand lock lever to pivot',['Stand lock lever'],['Stand lock lever pivot fastener'])
 test('lever pivot to sleeve',['Stand lock lever pivot fastener'],['Stand pivot sleeve'])
 test('ring lock bridge to stay',['Ring lock clamp seatstay bridge'],['Seatstay'])
 test('frame seatstay to seat tube',['Seatstay'],['Seat tube','Seatpost collar'])
 test('frame main tube to head',['Low step continuous'],['Head tube'])
 test('fork blade to crown',['Swept fork blade'],['Fork crown bridge'])
 test('front dropout to fork',['Front dropout'],['Swept fork blade'])
 test('rear dropout to stays',['Rear dropout'],['Curved chainstay','Seatstay'])
 test('lamp hanger to housing',['Lamp basket hanger'],['Front lamp housing'])
 test('lamp hanger to basket',['Lamp basket hanger'],['Basket floor'])
 obstacles={}
 for label,prefixes in [('rear_frame',['Seatstay','Curved chainstay','Ring lock','Rear ring lock','Carrier frame strut','Carrier axle strut']),('front_frame',['Swept fork blade','Fork crown bridge','Front mudguard stay','Basket axle mounting stay'])]:
  aa=[o for o in obs if any(o.name.startswith(q) for q in prefixes)];side='Rear' if label=='rear_frame' else 'Front';bb=[o for o in obs if o.name.startswith(side+' wheel rubber tire')];obstacles[label+'_tire']=V.candidate_hits(aa,bb)
 aa=[o for o in obs if o.name.startswith(('Seatstay','Curved chainstay','Ring lock','Rear ring lock','Carrier frame strut','Carrier axle strut','Paired stand','Stand','Rear brake','Rear roller brake'))];bb=[o for o in obs if o.name.startswith('Rear wheel spoke')];obstacles['rear_supports_spokes']=V.candidate_hits(aa,bb)
 aa=[o for o in obs if o.name.startswith(('Rear mudguard stay','Paired stand','Stand','Rear brake','Rear roller brake','Rear curved steel fender'))];bb=[o for o in obs if o.name.startswith('Rear wheel rubber tire')];obstacles['rear_auxiliary_tire']=V.candidate_hits(aa,bb)
 out[ext]={'obstacle_checks':obstacles,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size,'rows':rows,'general':V.general(obs),'full_pose_regression':V.bike_tests(obs,json.loads(p.with_name('metadata.json').read_text()))}
(R/'reviews/batch06a/attachments/audit.json').write_text(json.dumps(out,indent=2))
