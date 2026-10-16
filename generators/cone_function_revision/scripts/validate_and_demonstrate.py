"""Reopen actual saved files, test hollow bore, solids and nesting; render GLB evidence."""
import bpy,bmesh,math,json,os,sys,hashlib
from pathlib import Path
from mathutils import Vector
sys.path.insert(0,str(Path(__file__).resolve().parent))
from build_cone import studio,render,OUTER,INNER,PITCH,N
SUPPORT=Path(__file__).resolve().parents[1];ROOT=Path(os.environ.get('ASSET_OUTPUT_ROOT',str(SUPPORT)));FOLDER=ROOT/'assets'/'street'/'traffic_cone';EVIDENCE=SUPPORT/'evidence';EVIDENCE.mkdir(exist_ok=True)
def stats(o):
 m=o.data;m.calc_loop_triangles();pts=[o.matrix_world@v.co for v in m.vertices];bm=bmesh.new();bm.from_mesh(m)
 result={'triangles':len(m.loop_triangles),'zero_area_triangles':sum(t.area<1e-14 for t in m.loop_triangles),'finite_vertices':all(math.isfinite(c) for v in pts for c in v),'nonmanifold_edges':sum(not e.is_manifold for e in bm.edges),'signed_volume_m3':bm.calc_volume(signed=True),'min':[min(v[i] for v in pts) for i in range(3)],'max':[max(v[i] for v in pts) for i in range(3)]};bm.free();return result
bpy.ops.wm.open_mainfile(filepath=str(FOLDER/'traffic_cone.blend'));o=[o for o in bpy.data.collections['ASSET | traffic_cone'].objects if o.type=='MESH'][0];a=stats(o);assert a['nonmanifold_edges']==0 and a['zero_area_triangles']==0 and a['signed_volume_m3']>0
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(FOLDER/'traffic_cone.glb'));original=[o for o in bpy.context.scene.objects if o.type=='MESH'][0];me=original.data.copy();me.transform(original.matrix_world)
for ob in list(bpy.context.scene.objects):bpy.data.objects.remove(ob,do_unlink=True)
o=bpy.data.objects.new('Decoded saved GLB cone',me);bpy.context.collection.objects.link(o);bpy.context.view_layer.update();raw_import=stats(o)
# glTF splits vertices at material/normal/UV seams. Weld coincident positions only
# in the verification/evidence mesh; the actual exported asset is not rewritten.
bm=bmesh.new();bm.from_mesh(me);before=len(bm.verts);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-7);welded=before-len(bm.verts);bm.to_mesh(me);bm.free();me.update();b=stats(o)
assert b['nonmanifold_edges']==0 and b['zero_area_triangles']==0 and b['finite_vertices'],b
assert a['triangles']==b['triangles'];err=max(abs(x-y) for k in ['min','max'] for x,y in zip(a[k],b[k]));assert err<1e-6
hit,loc,normal,idx=o.ray_cast(Vector((0,0,-.1)),Vector((0,0,1)));assert hit and abs(loc.z-.696)<1e-5
# Radial clearance in the overlapping region. Sample source breakpoints on both
# profiles, neighborhoods of each breakpoint, and dense intervening heights.
def ray_radius(z,angle,outer):
 d=Vector((math.cos(angle),math.sin(angle),0));origin=d*.4+Vector((0,0,z)) if outer else Vector((0,0,z));direction=-d if outer else d
 hit,p,n,index=o.ray_cast(origin,direction);assert hit,(z,angle,outer);return math.hypot(p.x,p.y)
clearances=[]
for pitch in [PITCH,2*PITCH]:
 zs={pitch+1e-6,.7-1e-6}
 for r,z in INNER+OUTER:
  for zz in [z,z+pitch]:
   for delta in [-1e-6,1e-6]:
    if pitch<zz+delta<.7:zs.add(zz+delta)
 for i in range(1,1000):zs.add(pitch+(.7-pitch)*i/1000)
 minimum=(1,None,None)
 for z in sorted(zs):
  for angle in [0,math.pi/N,math.pi/4]:
   gap=ray_radius(z-pitch,angle,False)-ray_radius(z,angle,True)
   if gap<minimum[0]:minimum=(gap,z,angle)
 assert minimum[0]>.0005,minimum
 clearances.append({'vertical_offset_m':pitch,'minimum_sampled_radial_clearance_m':minimum[0],'at_global_height_m':minimum[1],'angle_rad':minimum[2],'height_samples':len(zs),'angular_samples_per_height':3})
# Exact CSG intersection of saved mesh instances. Contact faces may remain, but
# their enclosed volume must be zero. This is not inferred from AABBs.
intersections=[]
for pitch in [PITCH,2*PITCH]:
 test=bpy.data.objects.new('Intersection test',me.copy());bpy.context.collection.objects.link(test)
 other=bpy.data.objects.new('Upper intersection operand',me);bpy.context.collection.objects.link(other);other.location.z=pitch;bpy.context.view_layer.update()
 mod=test.modifiers.new('Exact intersect','BOOLEAN');mod.operation='INTERSECT';mod.solver='EXACT';mod.object=other;bpy.context.view_layer.objects.active=test;test.select_set(True);bpy.ops.object.modifier_apply(modifier=mod.name)
 bm=bmesh.new();bm.from_mesh(test.data);volume=abs(bm.calc_volume(signed=True));faces=len(bm.faces);bm.free();assert volume<1e-10,(pitch,volume)
 intersections.append({'vertical_offset_m':pitch,'exact_boolean_intersection_volume_m3':volume,'contact_or_residual_faces':faces});bpy.data.objects.remove(test,do_unlink=True);bpy.data.objects.remove(other,do_unlink=True)
contacts=[]
for k in range(4):
 angle=math.pi/4+k*math.pi/2;r=.197;x,y=r*math.cos(angle),r*math.sin(angle)
 hit,p,_,_=o.ray_cast(Vector((x,y,.05)),Vector((0,0,-1)));assert hit and abs(p.z-PITCH)<1e-6
 hit2,q,_,_=o.ray_cast(Vector((x,y,-.01)),Vector((0,0,1)));assert hit2 and abs(q.z)<1e-6
 contacts.append({'x_m':x,'y_m':y,'lower_land_top_m':p.z,'upper_base_underside_local_m':q.z,'gap_at_stack_pitch_m':q.z+PITCH-p.z})
result={'revision':'cone-functional-r1','blend_reopened':True,'glb_reimported':True,'blend':a,'imported_glb':b,'raw_glb_vertex_seam_topology':raw_import,'coincident_seam_vertices_welded_for_geometric_tests':welded,'max_bounds_error_m':err,'open_bottom_axis_first_hit_m':loc.z,'axis_hit_explanation':'Ray starts 0.1 m below the cone; the first surface is the inner closed top cap at 0.696 m. No base cap blocks the cavity.','nesting_pitch_m':PITCH,'instance_offsets_m':[0,PITCH,2*PITCH],'radial_clearance':clearances,'exact_intersections':intersections,'stack_support_contacts':contacts,'solid_volume_sanity':{'enclosed_material_volume_m3':b['signed_volume_m3'],'assumed_density_kg_per_m3':[1200,1600],'estimated_mass_range_kg':[b['signed_volume_m3']*1200,b['signed_volume_m3']*1600],'density_status':'Illustrative assumed range for filled/flexible PVC, not measured for this model. Actual reference product mass is 3.5 kg; no modeled mass certification.'},'scope':'Rigid geometric fit only; no material elasticity, loading, friction or real-product tolerance certification.'}
(FOLDER/'validation.json').write_text(json.dumps(result,indent=2));print('FUNCTIONAL_VALIDATION_PASSED',flush=True)
if os.environ.get('VALIDATE_ONLY'):sys.exit(0)
# Three nested copies of the decoded GLB, saved as both a review GLB and Blend.
s=bpy.context.scene;s.unit_settings.system='METRIC';cones=[o]
for i in [1,2]:
 clone=bpy.data.objects.new('Nested cone %d'%(i+1),me);s.collection.objects.link(clone);clone.location.z=i*PITCH;cones.append(clone)
bpy.ops.object.select_all(action='DESELECT')
for c in cones:c.select_set(True)
bpy.context.view_layer.objects.active=o;bpy.ops.export_scene.gltf(filepath=str(EVIDENCE/'nested_three.glb'),export_format='GLB',use_selection=True)
st,floor,cam=studio(s,Vector((0,0,.39)),.78)
# Axial underside evidence uses one decoded saved cone and a light below it.
for c in cones[1:]:c.hide_render=True
floor.hide_render=True
bpy.ops.object.light_add(type='AREA',location=(.15,-.20,-.60));under=bpy.context.object;under.data.energy=12;under.data.size=.4;under.rotation_euler=(Vector((0,0,.3))-under.location).to_track_quat('-Z','Y').to_euler()
render(s,cam,'underside_axial',(0,0,.35),(0,0,-1.5),.43,FOLDER)
bpy.data.objects.remove(under,do_unlink=True);floor.hide_render=False
for c in cones[1:]:c.hide_render=False
render(s,cam,'nested_three',(0,0,.39),(.9,-1.3,.65),1.03,EVIDENCE)
st.hide_viewport=True;bpy.ops.wm.save_as_mainfile(filepath=str(EVIDENCE/'nested_three.blend'),compress=True);st.hide_viewport=False
# Section is made from copies of decoded GLB geometry. It is never substituted
# for the production model. Three slightly distinct diagnostic colors separate walls.
for i,c in enumerate(cones):
 c.data=c.data.copy();bm=bmesh.new();bm.from_mesh(c.data);bmesh.ops.bisect_plane(bm,geom=list(bm.verts)+list(bm.edges)+list(bm.faces),dist=1e-8,plane_co=(0,0,0),plane_no=(0,1,0),clear_inner=True,clear_outer=False);bm.to_mesh(c.data);bm.free()
 for slot in c.material_slots:
  slot.material=slot.material.copy()
  p=slot.material.node_tree.nodes.get('Principled BSDF')
  if 'PVC' in slot.material.name and 'Recycled' not in slot.material.name:p.inputs['Base Color'].default_value=([( .55,.02,.01,1),(.80,.17,.02,1),(.50,.04,.15,1)][i])
render(s,cam,'nested_section',(0,0,.39),(.2,-1.8,.6),.98,EVIDENCE)
render(s,cam,'nested_neck_clearance',(0,0,.71),(.08,-1,.10),.20,EVIDENCE)
bpy.ops.wm.save_as_mainfile(filepath=str(EVIDENCE/'nested_section.blend'),compress=True)
# Store only exact current file sizes/hashes; no mutation of approved old bundle.
meta=json.loads((FOLDER/'metadata.json').read_text());meta['validated']=True;meta['stack_pitch_m']=PITCH;meta['min_tested_shell_clearance_m']=min(x['minimum_sampled_radial_clearance_m'] for x in clearances);meta['files']={p.name:{'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in FOLDER.iterdir() if p.suffix in ['.blend','.glb','.jpg']};(FOLDER/'metadata.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2))
