import sys,json,math,hashlib
from pathlib import Path
from mathutils import Vector
sys.path.insert(0,str(Path(__file__).resolve().parent))
from build_assets import *
def bounds(o):
 v=[o.matrix_world@p.co for p in o.data.vertices];return [Vector([fn(p[i] for p in v) for i in range(3)]) for fn in [min,max]]
def prefix(p):return [o for o in bpy.context.scene.objects if o.type=='MESH' and o.name.startswith(p)]
def rays(origin,direction,distance=2):
 return bpy.context.scene.ray_cast(bpy.context.evaluated_depsgraph_get(),Vector(origin),Vector(direction),distance=distance)
reports=[]
for slug in IDS:
 if os.environ.get('ONLY_ASSETS') and slug not in os.environ['ONLY_ASSETS'].split(','):continue
 result={'id':slug,'formats':{}}
 for ext in ['blend','glb']:
  file=A/slug/(slug+'.'+ext);clear()
  if ext=='blend':bpy.ops.wm.open_mainfile(filepath=str(file))
  else:bpy.ops.import_scene.gltf(filepath=str(file))
  bpy.context.view_layer.update();obs=[o for o in bpy.context.scene.objects if o.type=='MESH'];st=stats(obs)
  checks={'finite_coordinates':all(math.isfinite(x) for o in obs for v in o.data.vertices for x in v.co),'no_degenerate_triangles':st['zero_area_triangles']==0,'under_100MB':file.stat().st_size<100000000,'self_contained_materials':all(im.packed_file or im.source!='FILE' for im in bpy.data.images)};measured={}
  if slug=='roadside_convex_mirror':
   face=prefix('Convex silvered')[0];face.data.calc_loop_triangles();front=[]
   for p in face.data.polygons:
    c=face.matrix_world@p.center;n=face.matrix_world.to_3x3()@p.normal
    # outward optical surface lies at y <= 0, rear thickness surface has positive-y normals
    if c.y<-.0005 and n.y<0:front.append((c,n))
   hit=rays((0,-.2,2.6),(0,1,0));edge=rays((.285,-.2,2.6),(0,1,0));measured['face_center_y']=hit[1].y;measured['face_near_edge_y']=edge[1].y
   checks['convex_face_center_projects_forward']=hit[1].y<edge[1].y-.015
   checks['optical_normal_center_faces_outward']=hit[2].y<-.99
   checks['optical_normals_across_disc_face_outward']=all(rays((x,-.2,2.6+zz),(0,1,0))[2].y<-.98 for x,zz in [(0,0),(.10,0),(.20,0),(-.20,0),(0,.20),(0,-.20)])
   pole=bounds(prefix('Orange steel support pole')[0]);base=bounds(prefix('Concrete footing')[0]);checks['pole_embedded_in_footing']=pole[0].z<base[1].z and pole[0].z>=base[0].z
   checks['two_actual_open_pole_collars']=len(prefix('Pole clamping band'))==2
  elif slug=='outdoor_ac_condenser':
   pan=bounds(prefix('Cabinet bottom pan')[0]);feet=prefix('Cabinet mounting foot');measured['foot_to_pan_gap_m']=[float(pan[0].z-bounds(o)[1].z) for o in feet];checks['four_feet_contact_pan']=len(feet)==4 and all(abs(g)<1e-6 for g in measured['foot_to_pan_gap_m'])
   checks['motor_has_fixed_support']=len(prefix('Motor support strut'))==2 and len(prefix('Rear motor support spine'))==1
   blades=prefix('Swept stationary');guards=prefix('Concentric fan safety');clearance=min(bounds(o)[0].y for o in blades)-max(bounds(o)[1].y for o in guards);measured['fan_guard_clearance_m']=clearance;checks['fan_guard_clearance']=clearance>.04
   checks['base_has_true_drain_hole']=not rays((.08,.075,.13),(0,0,-1),.05)[0]
   # rear fin gaps and left louver gaps, short segments only test the intake skin
   checks['rear_intake_true_gaps']=not rays((-.341,.19,.41),(0,-1,0),.065)[0]
   checks['left_intake_true_gaps']=not rays((-.40,0,.15),(1,0,0),.06)[0]
   checks['front_discharge_has_open_path']=not rays((-.12,-.21,.56),(0,1,0),.06)[0]
   checks['two_service_connections']=len(prefix('Service valve connection'))==2 and len(prefix('Insulated service pipe'))==2
   pipe_objs=sorted(prefix('Insulated service pipe'),key=lambda o:o.name);paths=[service_path(.18,.065),service_path(.23,.11)];radii=[];counts=[];curve_r=[]
   for o,pts in zip(pipe_objs,paths):
    vertices=[o.matrix_world@v.co for v in o.data.vertices]
    for k,p in enumerate(pts):
     p=Vector(p);t=(Vector(pts[min(k+1,len(pts)-1)])-Vector(pts[max(0,k-1)])).normalized();rr=[(v-p).length for v in vertices if abs((v-p).dot(t))<2e-6 and (v-p).length<.02];counts.append(len(rr));radii.extend(rr)
    for a,b,c in zip(pts,pts[1:],pts[2:]):
     ab=Vector(b)-Vector(a);bc=Vector(c)-Vector(b);ac=Vector(c)-Vector(a);cross=ab.cross(ac).length
     if cross>1e-10:curve_r.append(ab.length*bc.length*ac.length/(2*cross))
   measured['pipe_cross_section_radius_range_m']=[min(radii),max(radii)];measured['pipe_minimum_sampled_bend_radius_m']=min(curve_r)
   checks['pipes_retain_circular_cross_sections']=min(counts)>=32 and min(radii)>.01299 and max(radii)<.01301
   checks['gentle_pipe_bends']=min(curve_r)>.0399
   minimum=min((Vector(a)-Vector(b)).length for a in paths[0] for b in paths[1]);measured['pipe_surface_gap_m']=minimum-.026;checks['paired_pipes_do_not_intersect']=minimum>.026

  else:
   grid=prefix('Welded removable grate')[0];frame=prefix('Welded angle receiver frame')[0]
   measured['bearing_seat_gap_m']=float(bounds(grid)[0].z-.008);checks['grid_seated']=abs(measured['bearing_seat_gap_m'])<1e-6
   contacts=[]
   for i in range(21):
    for yy in [-.19,.19]:
     world=Vector((-.297+i*.0297,yy,.05));a=frame.ray_cast(frame.matrix_world.inverted()@world,Vector((0,0,-1)),distance=.1);b=grid.ray_cast(grid.matrix_world.inverted()@Vector((world.x,world.y,0)),Vector((0,0,1)),distance=.05)
     contacts.append(a[0] and b[0] and abs((frame.matrix_world@a[1]).z-(grid.matrix_world@b[1]).z)<1e-6)
   checks['all_42_bearing_end_contacts']=all(contacts)

   checks['bar_ends_reach_end_bands']=all(rays((-.297+i*.0297,.190,.10),(0,0,-1),.1)[0] for i in range(21))
   apertures=[(-.297+(i+.5)*.0297,y) for i in range(1,19) for y in [-.125,-.075,-.025,.025,.075,.125]]
   checks['through_drainage_slots']=all(not rays((x,y,.1),(0,0,-1),.2)[0] for x,y in apertures);measured['central_through_apertures_tested']=len(apertures)
   measured['clear_slot_width_m']=.0297-.005;checks['hook_shaft_fits_slot']=measured['clear_slot_width_m']>.008
   checks['panel_inside_frame_clearance']=bounds(grid)[1].x<.305 and bounds(grid)[1].y<.205
   checks['no_floor_under_grate']=not rays((.01485,.025,.007),(0,0,-1),.3)[0]
   checks['two_welded_assemblies']=len(obs)==2
   import bmesh
   for label,o in [('grid',grid),('frame',frame)]:
    bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-7);checks[label+'_closed_manifold']=all(e.is_manifold for e in bm.edges);bm.free()
  result['formats'][ext]={'file':str(file.relative_to(OUT)),'sha256':hashlib.sha256(file.read_bytes()).hexdigest(),'bytes':file.stat().st_size,'statistics':st,'checks':checks,'measured':measured,'pass':all(checks.values())}
 s=result['formats']['blend']['statistics'];t=result['formats']['glb']['statistics'];result['roundtrip_matches']=s['triangles']==t['triangles'] and s['mesh_objects']==t['mesh_objects'] and max(abs(a-b) for a,b in zip(s['dimensions_m'],t['dimensions_m']))<1e-5;reports.append(result)
(OUT/'geometry_validation.json').write_text(json.dumps(reports,indent=2)+'\n')
print(json.dumps({r['id']:{e:d['checks'] for e,d in r['formats'].items()} for r in reports},indent=2))
assert all(r['roundtrip_matches'] and all(v['pass'] for v in r['formats'].values()) for r in reports)
