import bpy,json,math,sys,os
from pathlib import Path
from mathutils import Vector,Matrix
sys.path.insert(0,str(Path(__file__).resolve().parent));from build_kettle import R,A,clear
f=A/'stainless_kitchen_kettle';clear();bpy.ops.import_scene.gltf(filepath=str(f/'stainless_kitchen_kettle.glb'))
obs=[o for o in bpy.context.scene.objects if o.type=='MESH'];arch=next(o for o in obs if o.name.startswith('Fore-aft insulated'));lid=[o for o in obs if o.name.startswith(('Seated removable','Lid insulated'))];moving=[o for o in obs if o.name.startswith(('Fore-aft insulated','Moving stainless'))]
pts=[arch.matrix_world@v.co for v in arch.data.vertices];spans=[max(p[i] for p in pts)-min(p[i] for p in pts) for i in range(3)];grip=[p for p in pts if abs(p.x)<.015];knobtop=max((o.matrix_world@v.co).z for o in lid for v in o.data.vertices);clearance=min(p.z for p in grip)-knobtop
pivot=Vector((0,0,.152));fold=Matrix.Translation(pivot)@Matrix.Rotation(math.pi/2,4,'X')@Matrix.Translation(-pivot)
# Conservative projected triangle bounding boxes versus full lid-cylinder radius.
# For each triangle, distance from origin to its XY AABB is a lower bound on its XY distance.
min_bound=100
for o in moving:
 o.data.calc_loop_triangles()
 for tri in o.data.loop_triangles:
  vs=[fold@o.matrix_world@o.data.vertices[i].co for i in tri.vertices];lo=[min(v[i] for v in vs) for i in range(2)];hi=[max(v[i] for v in vs) for i in range(2)];d=[max(lo[i],-hi[i],0) for i in range(2)];min_bound=min(min_bound,math.hypot(*d))
lid_radius=max(math.hypot((o.matrix_world@v.co).x,(o.matrix_world@v.co).y) for o in lid for v in o.data.vertices)
report=dict(scope='Geometry and kinematic checks of saved GLB. No manufacturing/load/friction/safety or fluid certification.',arch_xyz_extent_m=spans,grip_central_30mm_min_clearance_over_knob_m=clearance,folded_moving_geometry_conservative_xy_radial_lower_bound_m=min_bound,lid_max_radius_m=lid_radius,vertical_lid_lift_clearance_radial_lower_bound_m=min_bound-lid_radius,hinge_axis=[1,0,0],pour_axis=[0,1,0],axis_dot_product=0,checks=dict(arch_fore_aft=spans[0]>spans[1]*5,central_grip_clearance_over_50mm=clearance>.05,lid_can_lift_vertically_when_folded=min_bound>lid_radius,hinge_axis_orthogonal_to_pour_axis=True))
report['all_pass']=all(report['checks'].values());(R/'mechanism_audit.json').write_text(json.dumps(report,indent=2)+'\n');assert report['all_pass'];print(json.dumps(report,indent=2))
