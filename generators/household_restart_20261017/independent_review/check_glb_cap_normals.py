import struct,json,pathlib,math,hashlib,sys
p=pathlib.Path(sys.argv[1]);b=p.read_bytes();n,t=struct.unpack_from('<II',b,12);j=json.loads(b[20:20+n]);off=20+n;n,t=struct.unpack_from('<II',b,off);buf=b[off+8:off+8+n]
def ac(i):
 a=j['accessors'][i];v=j['bufferViews'][a['bufferView']];k={'VEC3':3,'SCALAR':1}[a['type']];fmt={5126:'f',5123:'H',5125:'I'}[a['componentType']];size=struct.calcsize(fmt)*k;start=v.get('byteOffset',0)+a.get('byteOffset',0);return [struct.unpack_from('<'+fmt*k,buf,start+x*v.get('byteStride',size))for x in range(a['count'])]
prim=j['meshes'][0]['primitives'][0];v=ac(prim['attributes']['POSITION']);nn=ac(prim['attributes']['NORMAL']);ix=[i[0]for i in ac(prim['indices'])];faces=[]
for h,sign in [(0,-1),(.0032,1)]:
 angles=[]
 for a in range(0,len(ix),3):
  ii=ix[a:a+3]
  if all(abs(v[i][1]-h)<1e-8 for i in ii):angles.append(max(math.degrees(math.acos(max(-1,min(1,sign*nn[i][1]))))for i in ii))
 faces.append({'y':h,'triangles':len(angles),'max_normal_angle_degrees':max(angles),'triangles_over_0_1degree':sum(a>.1 for a in angles)})
r={'file':str(p),'sha256':hashlib.sha256(b).hexdigest(),'caps':faces,'pass':all(a['triangles_over_0_1degree']==0 for a in faces)}
print(json.dumps(r,indent=2));out=pathlib.Path(sys.argv[2]);out.write_text(json.dumps(r,indent=2)+'\n')
