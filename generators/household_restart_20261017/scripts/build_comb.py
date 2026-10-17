"""Original generic 170 mm coarse comb. Blender 4.3.2, --threads 2. No render."""
import bpy, bmesh, math, json, hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'models'/'comb';OUT.mkdir(parents=True,exist_ok=True)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
bpy.context.preferences.filepaths.save_version=0
bpy.context.scene.unit_settings.system='METRIC'
bpy.context.scene.unit_settings.scale_length=1
# All coordinates below are millimetres; one uninterrupted plate has open tooth gaps.
outline=[(-85,14),(-84,15),(84,15),(85,14),(85,-14),(84,-15),(82,-15),(81,-14),(81,-4)]
for i in range(43):
    x=78-156*i/42
    outline += [(x+1.1,-4),(x+1.1,-13.9)]
    for j in range(1,19):
        a=-math.pi*j/18
        outline.append((x+1.1*math.cos(a),-13.9+1.1*math.sin(a)))
    outline.append((x-1.1,-4))
outline += [(-81,-4),(-81,-14),(-82,-15),(-84,-15),(-85,-14)]
n=len(outline)
v=[(x/1000,y/1000,z) for z in (0,.0032) for x,y in outline]
f=[tuple(reversed(range(n))),tuple(range(n,2*n))]
f += [(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
me=bpy.data.meshes.new('Continuous saw-cut acetate plate');me.from_pydata(v,[],f);me.update()
o=bpy.data.objects.new('comb',me);bpy.context.collection.objects.link(o)
bpy.context.view_layer.objects.active=o;o.select_set(True)
bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free()
m=bpy.data.materials.new('Warm brown cellulose acetate');m.diffuse_color=(.135,.052,.023,1);m.use_nodes=True
bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=m.diffuse_color;bs.inputs['Roughness'].default_value=.29
me.materials.append(m)
q=o.modifiers.new('Rounded polished edges','BEVEL');q.width=.00028;q.segments=3;q.limit_method='ANGLE';q.angle_limit=.15
bpy.ops.object.modifier_apply(modifier=q.name)
# Explicit triangulation gives stable non-convex caps in both saved formats.
q=o.modifiers.new('Stable triangulation','TRIANGULATE');bpy.ops.object.modifier_apply(modifier=q.name)
bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.dissolve_degenerate(bm,dist=1e-8,edges=list(bm.edges));bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(o.data)
report={'vertices':len(bm.verts),'triangles':len(bm.faces),'nonmanifold_edges':sum(not e.is_manifold for e in bm.edges),'signed_volume_m3':bm.calc_volume(signed=True),'degenerate_faces':sum(f.calc_area()<1e-14 for f in bm.faces)};bm.free()
assert report['nonmanifold_edges']==0 and report['degenerate_faces']==0 and report['signed_volume_m3']>0,report
# set_sharp_from_angle also enables smooth faces, so it must precede cap flags.
o.data.update()
o.data.set_sharp_from_angle(angle=math.radians(35))
cap_faces={}
for face in o.data.polygons:
    zs=[o.data.vertices[i].co.z for i in face.vertices]
    cap=(max(zs)-min(zs)<1e-8 and (abs(zs[0])<1e-8 or abs(zs[0]-.0032)<1e-8))
    face.use_smooth=not cap
    if cap:cap_faces[face.index]=(0,0,1 if zs[0]>.0016 else -1)
o.data.update()
normals=[tuple(n.vector) for n in o.data.corner_normals]
for index,normal in cap_faces.items():
    for loop in o.data.polygons[index].loop_indices:normals[loop]=normal
o.data.normals_split_custom_set(normals)
o.data.update()
assert all(abs(o.data.corner_normals[k].vector.z)>.999999 for i in cap_faces for k in o.data.polygons[i].loop_indices)
report['flat_cap_triangles']=len(cap_faces)
report['flat_cap_corner_normals_verified']=True
report['dimensions_m']=list(o.dimensions)
report['tip_semicircle_segments']=18
report['bevel_segments']=3
report['shading']='flat planar caps, smooth curved sides and bevels, sharp splits at35degrees'
o['asset_id']='comb';o['display_name']='くし';o['units']='metres';o['teeth_count']=43
o['assumptions']='43 teeth, 3.2 mm plate, 11 mm free tooth length and 0.28 mm edge radius are original authoring choices, not manufacturer specifications.'
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'comb.blend'))
bpy.ops.export_scene.gltf(filepath=str(OUT/'comb.glb'),export_format='GLB',use_selection=True,export_apply=True)
report['source_sha256']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
report['files']={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(OUT.iterdir()) if p.suffix in ('.blend','.glb')}
(ROOT/'evidence'/'comb_build.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
