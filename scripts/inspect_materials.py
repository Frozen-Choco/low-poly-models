"""Inspect the actual material values embedded in each exported binary glTF."""
import struct,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
records=[]
for p in sorted((ROOT/'assets').rglob('*.glb')):
 data=p.read_bytes();magic,version,total=struct.unpack('<4sII',data[:12]);assert magic==b'glTF' and version==2 and total==len(data)
 size,kind=struct.unpack('<I4s',data[12:20]);assert kind==b'JSON';g=json.loads(data[20:20+size])
 mats=[]
 for m in g.get('materials',[]):
  b=m.get('pbrMetallicRoughness',{});mats.append({'name':m.get('name'),'baseColorFactor':b.get('baseColorFactor'),'metallicFactor':b.get('metallicFactor',1),'roughnessFactor':b.get('roughnessFactor',1),'extensions':m.get('extensions',{}),'emissiveFactor':m.get('emissiveFactor',[0,0,0])})
 records.append({'id':p.stem,'embedded_materials':mats,'used_extensions':g.get('extensionsUsed',[]),'external_buffers':any('uri' in b for b in g.get('buffers',[]))})
 if p.stem=='mug':
  assert any('KHR_materials_clearcoat' in m['extensions'] for m in mats)
 if p.stem=='traffic_signal':
  lookup={m['name']:m for m in mats}
  assert lookup['Matte galvanized steel']['roughnessFactor']>=.8
  assert lookup['Matte galvanized steel']['metallicFactor']<=.4
  assert min(lookup['Warm white outdoor powder coat']['baseColorFactor'][:3])>=.68
  assert max(lookup['Red LED lit']['emissiveFactor'])>0
  assert max(lookup['Green LED off']['emissiveFactor'])==0
  assert max(lookup['Amber LED off']['emissiveFactor'])==0
(ROOT/'material-validation.json').write_text(json.dumps(records,ensure_ascii=False,indent=2)+'\n')
print('Material validation passed',len(records))
