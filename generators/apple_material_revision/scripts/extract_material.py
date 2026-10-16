import pathlib,struct,json,hashlib
R=pathlib.Path(__file__).resolve().parents[1];P=R/'assets/whole_red_apple/whole_red_apple.glb';out=R/'previews';out.mkdir(exist_ok=True);data=P.read_bytes();n,t=struct.unpack_from('<II',data,12);j=json.loads(data[20:20+n]);off=20+n;n,t=struct.unpack_from('<II',data,off);blob=data[off+8:off+8+n]
for m in j['materials']:
 if 'apple skin' not in m.get('name',''):continue
 for label,key in [('revised_albedo','baseColorTexture'),('revised_metallic_roughness','metallicRoughnessTexture')]:
  tex=j['textures'][m['pbrMetallicRoughness'][key]['index']];im=j['images'][tex['source']];v=j['bufferViews'][im['bufferView']];(out/(label+'.png')).write_bytes(blob[v.get('byteOffset',0):v.get('byteOffset',0)+v['byteLength']])
 (R/'glb_pbr.json').write_text(json.dumps(dict(glb_sha256=hashlib.sha256(data).hexdigest(),material=m,extensions_used=j.get('extensionsUsed',[])),indent=2)+'\n')
