"""Pure Python design geometry. No bpy import and no external dependency.
All returned bicycle coordinates are in unparked frame unless park() is applied.
"""
import json, math
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
DESIGN=json.loads((ROOT/'configs/design.json').read_text())
def add(a,b):return tuple(x+y for x,y in zip(a,b))
def sub(a,b):return tuple(x-y for x,y in zip(a,b))
def mul(a,s):return tuple(x*s for x in a)
def dot(a,b):return sum(x*y for x,y in zip(a,b))
def norm(a):return math.sqrt(dot(a,a))
def unit(a):return mul(a,1/norm(a))
def cross(a,b):return (a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0])
def rotate(p,origin,axis,angle):
 p=sub(p,origin);a=unit(axis);c=math.cos(angle);s=math.sin(angle)
 return add(origin,add(add(mul(p,c),mul(cross(a,p),s)),mul(a,dot(a,p)*(1-c))))
def steering(p,degrees):
 b=DESIGN['bike'];return rotate(p,b['head_lower'],sub(b['head_upper'],b['head_lower']),math.radians(degrees))
def park(p):
 b=DESIGN['bike'];origin=(0,b['front_axle'][1],0);angle=math.asin(b['park_rear_lift']/(b['rear_axle'][1]-b['front_axle'][1]))
 # Rotation around ground contact tips wheels minutely: final global ground offset
 # is applied by builder after measuring actual saved tire vertices.
 return rotate(p,origin,(1,0,0),angle)
def gear_radii():
 b=DESIGN['bike'];pitch=b['chain_pitch'];return tuple(pitch/(2*math.sin(math.pi/t)) for t in (b['chainring_teeth'],b['rear_teeth']))
def chain_path(narc=40):
 """Closed external-tangent capsule in YZ, with different pitch radii."""
 b=DESIGN['bike'];cy,cz=b['bottom_bracket'][1:];dy,dz=b['rear_axle'][1:];r1,r2=gear_radii();D=math.hypot(dy-cy,dz-cz);phi=math.atan2(dz-cz,dy-cy);alpha=math.acos((r1-r2)/D)
 # Start first circle lower side; long first outer arc, short rear outer arc.
 pts=[]
 for k in range(narc+1):
  a=phi+alpha+(2*math.pi-2*alpha)*k/narc;pts.append((b['chainline_x'],cy+r1*math.cos(a),cz+r1*math.sin(a)))
 for k in range(narc+1):
  a=phi-alpha+2*alpha*k/narc;pts.append((b['chainline_x'],dy+r2*math.cos(a),dz+r2*math.sin(a)))
 return pts

def cart_handle_point(p,degrees):
 return rotate(p,DESIGN['cart']['hinge_pivot'],(1,0,0),math.radians(degrees))
def lock_pin(released=False):
 c=DESIGN['cart'];y,z=c['lock_slot_lower_yz' if released else 'lock_slot_upper_yz'];return (0,y,z)
def caster_axle(front=True,angle_deg=0,xsign=1):
 c=DESIGN['cart'];pivot=(xsign*c['caster_x'],-c['caster_y'] if front else c['caster_y'],c['wheel_radius'])
 return rotate(add(pivot,(0,c['swivel_offset'],0)),pivot,(0,0,1),math.radians(angle_deg)) if front else pivot

def segment_distance(p,a,b):
 ab=sub(b,a);t=max(0,min(1,dot(sub(p,a),ab)/dot(ab,ab)));return norm(sub(p,add(a,mul(ab,t))))
def sample_segment(a,b,n=20):return [add(a,mul(sub(b,a),i/n)) for i in range(n+1)]

def numeric_design_tests():
 b=DESIGN['bike'];c=DESIGN['cart'];r1,r2=gear_radii();chain=chain_path();front=b['front_axle'];rear=b['rear_axle'];bb=b['bottom_bracket'];out={}
 out['chainline_constant_x']=max(abs(p[0]-b['chainline_x']) for p in chain)<1e-12
 out['chain_gear_separation_m']=norm(sub(rear,bb))-r1-r2
 out['chainstay_lateral_clearance_m']=b['chainline_x']-.055-.012-.004
 out['minimum_pedal_ground_m']=bb[2]-b['crank_length']-.014
 out['wheelbase_m']=rear[1]-front[1]
 out['steering_axis_tilt_degrees']=math.degrees(math.atan2(abs(b['head_upper'][1]-b['head_lower'][1]),b['head_upper'][2]-b['head_lower'][2]))
 axis=sub(b['head_upper'],b['head_lower'])
 ground_y=b['head_lower'][1]-b['head_lower'][2]*axis[1]/axis[2]
 axle_axis_y=b['head_lower'][1]+(front[2]-b['head_lower'][2])*axis[1]/axis[2]
 out['positive_steering_trail_m']=front[1]-ground_y
 out['fork_axle_forward_offset_m']=axle_axis_y-front[1]
 out['steer_axis_invariant']=all(norm(sub(steering(p,a),p))<1e-10 for a in b['steer_test_degrees'] for p in [b['head_lower'],b['head_upper']])
 out['stand_support_triangle_area_m2']=(b['stand_foot_y']-front[1])*b['stand_foot_half_width']
 # Conservative swept caster envelope, independent from mesh detail.
 out['caster_pair_clearance_m']=2*c['caster_x']-2*(c['wheel_radius']+c['swivel_offset']+.009)
 out['caster_underdeck_clearance_m']=c['deck_top']-c['deck_thickness']-2*c['wheel_radius']
 top=(0,c['hinge_pivot'][1],c['handle_top']-c['handle_tube_radius']);fold=cart_handle_point(top,90)
 out['folded_grip_front_margin_m']=fold[1]-c['handle_tube_radius']+c['deck_size'][1]/2
 out['folded_handle_deck_clearance_m']=c['hinge_pivot'][2]-c['handle_tube_radius']-c['deck_top']
 out['slot_pin_radial_clearance_m']=c['slot_radius']-c['lock_pin_radius']
 out['lock_release_travel_m']=norm(sub(lock_pin(True),lock_pin(False)))
 out['lock_tongue_base_clearance_m']=min(cart_handle_point((0,y,z),a)[2] for y,z in c['lock_tongue_outline_yz'] for a in range(91))-.184
 out['design_only_not_mesh_approval']=True
 out['all_numeric_design_checks_pass']=all([out['chainline_constant_x'],out['steer_axis_invariant'],.02<out['positive_steering_trail_m']<.10,out['chainstay_lateral_clearance_m']>0,out['minimum_pedal_ground_m']>.05,out['caster_pair_clearance_m']>.05,out['caster_underdeck_clearance_m']>.02,out['folded_grip_front_margin_m']>0,out['slot_pin_radial_clearance_m']>0,out['lock_tongue_base_clearance_m']>.002])
 return out
if __name__=='__main__':print(json.dumps(numeric_design_tests(),indent=2))
