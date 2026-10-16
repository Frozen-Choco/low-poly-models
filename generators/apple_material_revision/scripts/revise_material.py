import bpy, numpy as np, math, os, json, hashlib, sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import stats
R=Path(__file__).resolve().parents[1]
A=Path(os.environ.get('ASSET_OUTPUT_ROOT',str(R/'assets')));F=A/'whole_red_apple';F.mkdir(parents=True,exist_ok=True)
SOURCE=Path(os.environ.get('APPLE_SOURCE_BLEND',str(R/'inputs/approved_apple_geometry.blend')))
bpy.ops.wm.open_mainfile(filepath=str(SOURCE));bpy.context.preferences.filepaths.save_version=0

def geo_hash():
 h=hashlib.sha256()
 for o in sorted([x for x in bpy.context.scene.objects if x.type=='MESH'],key=lambda x:x.name):
  h.update(o.name.encode());h.update(np.array(o.matrix_world,dtype=np.float64).tobytes());h.update(np.array([v.co[:] for v in o.data.vertices],dtype=np.float64).tobytes());h.update(json.dumps([list(p.vertices) for p in o.data.polygons]).encode())
 return h.hexdigest()
before=geo_hash();N=1024;rng=np.random.default_rng(240410);y,x=np.mgrid[0:N,0:N]/N;theta=math.pi*y;phi=math.tau*x
X=np.sin(theta)*np.cos(phi);Y=np.sin(theta)*np.sin(phi);Z=np.cos(theta)
def field(freq,count):
 a=np.zeros((N,N),np.float32)
 for _ in range(count):
  d=rng.normal(size=3);d/=np.linalg.norm(d);f=freq*rng.uniform(.7,1.5);a+=np.sin(f*(d[0]*X+d[1]*Y+d[2]*Z)+rng.uniform(0,math.tau))
 return np.tanh(a/math.sqrt(count)*.8)
broad=field(8,16);medium=field(48,20);fine=field(210,24);micro=field(700,12)
rgb=np.empty((N,N,3),np.float32);rgb[:,:,0]=.49+.080*broad+.025*medium+.009*fine;rgb[:,:,1]=.027+.012*(broad+1)+.004*medium+.0015*fine;rgb[:,:,2]=.018+.005*(broad+1)+.0015*medium
rough=np.clip(.375+.018*broad+.014*medium+.007*fine,.33,.42)
for _ in range(1550):
 t=math.acos(rng.uniform(-.985,.985));cy=int(t/math.pi*N);cx=int(rng.uniform(0,N));size=rng.uniform(.65,1.35);rx=1.0*size/max(.18,math.sin(t));ry=3.0*size;ix=int(math.ceil(rx*2.4));iy=int(math.ceil(ry*2.4));aa,bb=np.mgrid[-iy:iy+1,-ix:ix+1];dist=(bb/rx)**2+(aa/ry)**2;alpha=np.exp(-dist*1.7)*rng.uniform(.22,.55);yy=np.clip(cy+aa,0,N-1);xx=(cx+bb)%N;col=np.array([.68,.39,.19])*rng.uniform(.85,1.1);rgb[yy,xx]=rgb[yy,xx]*(1-alpha[:,:,None])+col*alpha[:,:,None];rough[yy,xx]+=.015*alpha
m=bpy.data.materials.get('Red apple skin with lenticels');assert m
m.node_tree.nodes.clear();nt=m.node_tree;out=nt.nodes.new('ShaderNodeOutputMaterial');p=nt.nodes.new('ShaderNodeBsdfPrincipled');nt.links.new(p.outputs['BSDF'],out.inputs['Surface']);p.inputs['Metallic'].default_value=0;p.inputs['Roughness'].default_value=.375;p.inputs['IOR'].default_value=1.5;p.inputs['Specular IOR Level'].default_value=.5
# Standard dielectric PBR only. Wax is expressed through roughness, not metallic or thick varnish.
def image(n,data,noncolor=False):
 rgba=np.ones((N,N,4),np.float32);rgba[:,:,:3]=data if data.ndim==3 else data[:,:,None];im=bpy.data.images.new(n,width=N,height=N);im.colorspace_settings.name='Non-Color' if noncolor else 'sRGB';im.pixels.foreach_set(rgba.ravel());im.pack();return im
im=image('Original isotropic apple blush and fine lenticels',np.clip(rgb,0,1));n=nt.nodes.new('ShaderNodeTexImage');n.image=im;nt.links.new(n.outputs['Color'],p.inputs['Base Color'])
im=image('Original spatially varied wax roughness',rough,True);n=nt.nodes.new('ShaderNodeTexImage');n.image=im;nt.links.new(n.outputs['Color'],p.inputs['Roughness'])
after=geo_hash();assert before==after
bpy.context.view_layer.update();s=stats([o for o in bpy.context.scene.objects if o.type=='MESH']);bpy.ops.object.select_all(action='SELECT');bpy.ops.export_scene.gltf(filepath=str(F/'whole_red_apple.glb'),export_format='GLB',use_selection=True,export_apply=True);bpy.ops.wm.save_as_mainfile(filepath=str(F/'whole_red_apple.blend'),compress=True)
meta=json.loads((SOURCE.parent/'metadata.json').read_text());meta.update(**s,title_ja='りんご',review_status='material revision pending independent review and photography standard',glb_bytes=(F/'whole_red_apple.glb').stat().st_size,blend_bytes=(F/'whole_red_apple.blend').stat().st_size);meta.pop('files_bytes',None);(F/'metadata.json').write_text(json.dumps(meta,indent=2)+'\n')
report=dict(source_blend=str(SOURCE.relative_to(R)) if SOURCE.is_relative_to(R) else 'explicit external input',source_sha256=hashlib.sha256(SOURCE.read_bytes()).hexdigest(),geometry_before_sha256=before,geometry_after_sha256=after,geometry_identical=before==after,material=dict(metallic=0,roughness_min=float(rough.min()),roughness_max=float(rough.max()),roughness_mean=float(rough.mean()),ior=1.5,specular_ior_level=.5,coat_weight=0,normal_map=False,base_color_min=rgb.min(axis=(0,1)).tolist(),base_color_max=rgb.max(axis=(0,1)).tolist()),texture_rationale='Seamless direction-balanced spherical noise replaces repeated longitude stripes; circular physical-scale lenticels are sampled uniformly over surface area. No longitudinal procedural term or deep groove normal map.')
(R/'material_revision.json').write_text(json.dumps(report,indent=2)+'\n')
