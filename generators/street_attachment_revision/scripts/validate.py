import bpy,math,json,hashlib,sys
from pathlib import Path
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];OUT=R/'functional';results={}
def vs(o):return [o.matrix_world@v.co for v in o.data.vertices]
def tree(o,verts=None):return BVHTree.FromPolygons(vs(o) if verts is None else verts,[list(p.vertices) for p in o.data.polygons])
def bounds(o):
 v=vs(o);return [[min(p[i] for p in v) for i in range(3)],[max(p[i] for p in v) for i in range(3)]]
def render(name,campos,target,scale):
 s=bpy.context.scene;s.render.engine='BLENDER_WORKBENCH';s.display.shading.light='STUDIO';s.display.shading.color_type='MATERIAL';s.display.shading.show_shadows=True;s.display.shading.show_cavity=True;s.display.shading.background_type='WORLD';s.world=s.world or bpy.data.worlds.new('DiagnosticWorld');s.world.color=(.16,.16,.16)
 for o in s.objects:
  if o.type in ['LIGHT','CAMERA'] or o.name=='Plane':o.hide_render=True
 bpy.ops.object.camera_add(location=campos);c=bpy.context.object;c.hide_render=False;c.rotation_euler=(Vector(target)-c.location).to_track_quat('-Z','Y').to_euler();c.data.type='ORTHO';c.data.ortho_scale=scale;s.camera=c;s.render.resolution_x=800;s.render.resolution_y=800;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.render.filepath=str(OUT/(name+'.png'));bpy.ops.render.render(write_still=True)
for slug in ['traffic_signal','railway_crossing_lowered']:
 results[slug]={}
 for ext in ['blend','glb']:
  path=R/'assets'/slug/(slug+'.'+ext);b=path.read_bytes();row={'sha256':hashlib.sha256(b).hexdigest(),'git_blob':hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest(),'bytes':len(b)};results[slug][ext]=row
  if ext=='blend':bpy.ops.wm.open_mainfile(filepath=str(path))
  else:bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(path))
  obs={o.name:o for o in bpy.context.scene.objects if o.type=='MESH' and o.name!='Plane'}
  row['bounds']={n:bounds(o) for n,o in obs.items()};row['contact_intersections']={}
  if slug=='traffic_signal':
   pairs=[('Rear service gasket','White horizontal signal housing'),('Service cover cable entry gland','Rear service panel'),('Service cover cable entry gland','Rear cable from support arm to service cover'),('Support arm cable entry gland','Horizontal mounting arm'),('Support arm cable entry gland','Rear cable from support arm to service cover')]
   for a,c in pairs:row['contact_intersections'][a+' :: '+c]=len(tree(obs[a]).overlap(tree(obs[c])))
   row['gasket_housing_planar_gap_m']=bounds(obs['Rear service gasket'])[0][1]-bounds(obs['White horizontal signal housing'])[1][1]
   render(slug+'_'+ext+'_front',(2,-4,5),(.6,0,4.4),1.7);render(slug+'_'+ext+'_rear',(2,4,5),(.65,0,4.4),1.7);render(slug+'_'+ext+'_side',(3,.1,4.35),(.65,.08,4.35),.8);render(slug+'_'+ext+'_underside',(1,3,3.3),(.65,.05,4.35),1.7)
   render(slug+'_'+ext+'_cable_contact',(.9,2,4.35),(.67,.11,4.35),.7)
  else:
   row['mast_base_gap_m']=bounds(obs['Continuous mast with alternating painted bands'])[0][2]-bounds(obs['Mast base plate'])[1][2]
   pairs=[('Crossbuck bolted mounting plate','Crossbuck continuous yellow blade'),('Crossbuck U-bolt around mast','Continuous mast with alternating painted bands'),('Crossbuck U-bolt around mast','Crossbuck bolted mounting plate')]
   for a,c in pairs:row['contact_intersections'][a+' :: '+c]=len(tree(obs[a]).overlap(tree(obs[c])))
   boom=obs['Four metre tapered lowered striped boom'];orig=vs(boom);pivot=Vector((.65,-.25,.88));static={n:tree(o) for n,o in obs.items() if not n.startswith(('Four metre','Boom','Drive shaft'))};hits=[]
   # Quarter-degree tests: full boom tested against all non-moving assembly geometry.
   for k in range(361):
    deg=k/4;m=Matrix.Rotation(-math.radians(deg),3,'Y');bt=tree(boom,[pivot+m@(p-pivot) for p in orig])
    for n,t in static.items():
     p=bt.overlap(t)
     if p:hits.append({'deg':deg,'static':n,'pairs':len(p)})
   row['boom_0_to_90_quarter_degree_intersections']=hits
   # Conservative analytic X gap: boom x is never less than pivot_x - max radius.
   row['continuous_boom_warning_hood_x_gap_lower_bound_m']=.65-.057-max(bounds(o)[1][0] for n,o in obs.items() if n.startswith('Deep upper sun hood'))
   render(slug+'_'+ext+'_front',(5,-8,5),(2,0,1.8),6);render(slug+'_'+ext+'_rear',(5,8,5),(2,0,1.8),6);render(slug+'_'+ext+'_base',(1,-2,1),(.1,0,.35),.8);render(slug+'_'+ext+'_crossbuck_rear',(1,3,3.6),(0,0,3.35),.5)
   m=Matrix.Rotation(-math.pi/2,3,'Y');inv=boom.matrix_world.inverted()
   for v,p in zip(boom.data.vertices,orig):v.co=inv@(pivot+m@(p-pivot))
   for n,o in obs.items():
    if n.startswith(('Boom socket','Boom clamp')):o.matrix_world=Matrix.Translation(pivot)@m.to_4x4()@Matrix.Translation(-pivot)@o.matrix_world
   render(slug+'_'+ext+'_raised',(2,-4,3.1),(.5,-.2,2.65),1.1)
 (OUT/'validation.json').write_text(json.dumps(results,indent=2))
print('VALIDATION_COMPLETE',flush=True)
