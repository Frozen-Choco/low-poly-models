"""Isolated original bin repair; blender -b --threads 2 --python scripts/build_bin.py."""
import bpy,sys,math,json,os
from pathlib import Path
from mathutils import Matrix,Vector
sys.path.insert(0,str(Path(__file__).resolve().parent))
import base_geometry as g
R=Path(__file__).resolve().parents[1]
g.A=Path(os.environ.get('ASSET_OUTPUT_ROOT',str(R/'assets')))

def revise():
 g.binprop()
 white=g.white;bolt=g.bolt;black=g.black;steel=g.steel
 doorpaint=bpy.data.materials['Gray painted steel service door'];interior=bpy.data.materials['Dark removable liner']
 # Replace plinth and floor with exact planar bearing contacts.
 for n in ['Recessed plinth','Cabinet floor','Front access door gasket']:
  bpy.data.objects.remove(bpy.data.objects[n],do_unlink=True)
 g.box('Recessed plinth',(0,0,.048),(.42,.38,.096),black,.006)
 g.box('Cabinet floor',(0,0,.105),(.466,.42,.018),steel,.0005)
 # All liner components bottom at floor top .114; generic revised height525mm.
 for o in list(bpy.data.objects):
  if o.name.startswith('Liner ') or any(o.name.startswith(n) for n in ['Fixed hinge','Door hinge','Hinge attachment','Vertical hinge','Separated hinge','Hinge leaf']):bpy.data.objects.remove(o,do_unlink=True)
 for x in [-.185,.185]:g.box('Liner side',(x,0,.3765),(.008,.35,.525),interior,.002)
 for y in [-.17,.17]:g.box('Liner front or rear',(0,y,.3765),(.37,.008,.525),interior,.002)
 g.box('Liner bottom',(0,0,.119),(.37,.35,.010),interior,.002)
 # Recessed grip cut-outs provide a real handhold, below the rim.
 for o in [o for o in bpy.data.objects if o.name.startswith('Liner front or rear')]:
  cut=g.box('Temporary handgrip cutter',(0,o.location.y,.609),(.10,.03,.024),interior,.007)
  bpy.context.view_layer.objects.active=o;q=o.modifiers.new('Through handgrip','BOOLEAN');q.operation='DIFFERENCE';q.object=cut;bpy.ops.object.modifier_apply(modifier=q.name);bpy.data.objects.remove(cut,do_unlink=True)
 # Give the door an actual 5mm top clearance below the fixed fascia.
 for o in list(bpy.data.objects):
  if o.name.startswith('Two millimetre painted door') or o.name.startswith('Door folded vertical'):
   for v in o.data.vertices:
    if v.co.z+o.location.z>.405:v.co.z-=.008*(v.co.z/.2825)
  if o.name.startswith('Door folded horizontal') and o.location.z>.4:o.location.z-=.008
 # Door inner perimeter seal moves with the skin, not a fixed solid blocker.
 for x in [-.200,.200]:g.box('Door moving perimeter seal',(x,-.216,.405),(.012,.008,.55),black,.002)
 for z in [.136,.674]:g.box('Door moving perimeter seal',(0,-.216,z),(.400,.008,.012),black,.002)
 # Two three-knuckle butt hinges. Fixed outside knuckles, moving middle knuckle.
 for z in [.25,.55]:
  g.box('Fixed hinge mounting return',(-.225,-.223,z),(.020,.030,.048),white,.001)
  g.box('Fixed hinge leaf',(-.232,-.240,z),(.010,.004,.048),bolt,.0005)
  g.box('Door hinge attachment seat',(-.2015,-.236,z),(.025,.006,.048),doorpaint,.0005)
  g.box('Door hinge leaf',(-.212,-.2405,z),(.020,.004,.048),bolt,.0005)
  # Short webs bridge leaves to the barrel tangency without detached hardware.
  
  for dz in [-.017,.017]:g.box('Fixed hinge barrel web',(-.2305,-.243,z+dz),(.004,.006,.015),bolt,.0003)
  g.box('Door hinge barrel web',(-.2175,-.243,z),(.004,.006,.015),bolt,.0003)
  for dz in [-.017,.017]:g.tube('Fixed hinge outer knuckle',(-.224,-.248,z+dz),.006,.0032,.015,bolt,axis='Z')
  g.tube('Door hinge middle knuckle',(-.224,-.248,z),.006,.0032,.015,bolt,axis='Z')
  g.cyl('Fixed hinge pin',(-.224,-.248,z),.003,.054,bolt,N=32)
  for x in [-.2345,-.210]:
   g.cyl('Fixed hinge screw' if x<-.224 else 'Door hinge screw',(x,-.244,z),(.0025 if x<-.224 else .0035),.005,bolt,(math.pi/2,0,0),12)
 # Simple visible lock barrel extends through the folded skin. Spring latch concealed
 # inside barrel is not claimed; rotating cam and strike are explicit service parts.
 g.cyl('Door lock barrel',(.16,-.224,.62),.010,.034,bolt,(math.pi/2,0,0),32)
 cam=g.box('Door quarter turn latch cam',(.184,-.206,.62),(.060,.004,.012),bolt,.001)
 # Right-side keeper blocks outward opening while cam points right; open-ended slot.
 g.box('Fixed latch keeper',(.220,-.212,.62),(.022,.004,.040),steel,.001)
 g.box('Fixed latch keeper return',(.230,-.202,.62),(.008,.024,.040),steel,.001)
 # Tag movable meshes; explicit grouping survives GLB export via extras.
 for o in bpy.data.objects:
  if o.type!='MESH':continue
  o['service_group']='liner' if o.name.startswith('Liner ') else ('door' if (o.name.startswith('Door ') or o.name.startswith('Two millimetre painted door') or o.name in ['Recessed door lock','Lock slot']) else 'fixed')
  if o.name=='Door quarter turn latch cam':o['service_group']='latch'
  o['design']='generic inferred geometry; not a branded replica'

refs=['https://www.teramoto.co.jp/products/7306/','https://www.teramoto.co.jp/trushbox_ft_series/','https://www.teramoto.co.jp/trashbox_ft_touchless_support/howtouse/']
notes='Generic sheltered-space can/bottle mixed recycling cabinet. Static closed deliverable; editable door, quarter-turn latch and 525mm liner. Both chutes feed one liner. Service proof is supplied separately. Original inferred dimensions and hardware; not a manufacturer replica or safety certification.'
g.build('public_recycling_bin',revise,refs,notes,((0,-.15,.84),.65))
