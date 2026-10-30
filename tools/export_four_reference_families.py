import sys,json,struct,hashlib
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'tools'));from export_bilge_native_basis import Reader
O=R/'dist/bilge-four-models';O.mkdir(parents=True,exist_ok=True);selection=json.loads((R/'docs/four-character-rigs/selection.json').read_text())['characters'];rows=[]
for item,label in zip(selection,['Buz-40','Kan-54','Koz-42','Golge-58']):
 body=Reader().from_file(str(R/item['source']));motion=Reader().from_file(str(R/item['motion_source']));assert [n.name for n in body.nodes]==[n.name for n in motion.nodes];binary=bytearray();g={'asset':{'version':'2.0','generator':'Native rig reference export'},'buffers':[{}],'bufferViews':[],'accessors':[],'scenes':[{'name':label,'nodes':[0],'extras':{'source_body':Path(item['source']).name,'source_motion':Path(item['motion_source']).name,'purpose':'third-party source rig reference; not original authored game appearance'}}],'scene':0,'nodes':[],'meshes':[],'skins':[],'animations':[],'materials':[{'name':'AnatomiOnizleme','pbrMetallicRoughness':{'baseColorFactor':[.46,.5,.54,1],'metallicFactor':0,'roughnessFactor':.85}}]}
 def acc(values,kind,width,component=5126,bounds=False):
  while len(binary)%4:binary.append(0)
  flat=[x for v in values for x in (v if isinstance(v,(list,tuple,Vector)) else [v])];offset=len(binary);binary.extend(struct.pack('<'+{5126:'f',5123:'H',5125:'I'}[component]*len(flat),*flat));view=len(g['bufferViews']);g['bufferViews'].append({'buffer':0,'byteOffset':offset,'byteLength':len(binary)-offset});a={'bufferView':view,'componentType':component,'count':len(values),'type':kind}
  if bounds:a.update(min=[min(flat[j::width]) for j in range(width)],max=[max(flat[j::width]) for j in range(width)])
  index=len(g['accessors']);g['accessors'].append(a);return index
 points=[v.location for p in body.pieces for v in p.lods[0].vertices];low=min(p.y for p in points);scale=2.4/(max(p.y for p in points)-low);g['nodes'].append({'name':'ModelRoot','translation':[0,-low*scale,0],'scale':[scale]*3,'children':[]});ix={n.name:i for i,n in enumerate(body.nodes)}
 for i,n in enumerate(body.nodes):
  local=n.parent.bind_matrix.inverted()@n.bind_matrix if n.parent else n.bind_matrix;p,q,s=local.decompose();g['nodes'].append({'name':n.name,'translation':list(p),'rotation':[q.x,q.y,q.z,q.w],'children':[]});g['nodes'][ix[n.parent.name]+1 if n.parent else 0]['children'].append(i+1)
 inv=[[n.bind_matrix.inverted()[row][col] for col in range(4) for row in range(4)] for n in body.nodes];g['skins'].append({'joints':list(range(1,len(body.nodes)+1)),'inverseBindMatrices':acc(inv,'MAT4',16)});tris=0
 for pi,piece in enumerate(body.pieces):
  if piece.name.lower().startswith('tattoo'):continue
  lod=piece.lods[0];ps=[];ns=[];uv=[];js=[];ws=[]
  for face in lod.faces:
   for corner in face.vertices:
    v=lod.vertices[corner.vertex_index];ps.append(list(v.location));ns.append(list(v.normal));uv.append([corner.texcoord[0],1-corner.texcoord[1]]);w=sorted([(w.node_index,w.bias) for w in v.weights if w.bias>0],key=lambda x:-x[1])[:4] or [(0,1.)];total=sum(b for _,b in w);js.append([a for a,_ in w]+[0]*(4-len(w)));ws.append([b/total for _,b in w]+[0]*(4-len(w)))
  primitive={'attributes':{'POSITION':acc(ps,'VEC3',3,bounds=True),'NORMAL':acc(ns,'VEC3',3),'TEXCOORD_0':acc(uv,'VEC2',2),'JOINTS_0':acc(js,'VEC4',4,5123),'WEIGHTS_0':acc(ws,'VEC4',4)},'indices':acc(list(range(len(ps))),'SCALAR',1,5125),'material':0};g['meshes'].append({'name':'Yuzey-'+str(pi+1),'primitives':[primitive]});node=len(g['nodes']);g['nodes'].append({'name':'Yuzey-'+str(pi+1),'mesh':len(g['meshes'])-1,'skin':0});g['nodes'][0]['children'].append(node);tris+=len(lod.faces)
 for a in motion.animations:
  times=[k.time/1000 for k in a.keyframes];inp=acc(times,'SCALAR',1,bounds=True);out={'name':a.name,'samplers':[],'channels':[],'extras':{'events':[{'time_ms':k.time,'event':k.string} for k in a.keyframes if k.string]}}
  for j,n in enumerate(body.nodes):
   transforms=a.node_keyframe_transforms[j]
   for path,kind,width,values in [('translation','VEC3',3,[list(t.location) for t in transforms]),('rotation','VEC4',4,[[t.rotation.x,t.rotation.y,t.rotation.z,t.rotation.w] for t in transforms])]:
    assert len(values)==len(times);s=len(out['samplers']);out['samplers'].append({'input':inp,'output':acc(values,kind,width),'interpolation':'LINEAR'});out['channels'].append({'sampler':s,'target':{'node':j+1,'path':path}})
  g['animations'].append(out)
 g['buffers'][0]['byteLength']=len(binary);text=json.dumps(g,separators=(',',':')).encode();text+=b' '*((-len(text))%4);binary+=b'\0'*((-len(binary))%4);p=O/(label+'.glb');p.write_bytes(struct.pack('<4sII',b'glTF',2,28+len(text)+len(binary))+struct.pack('<II',len(text),0x4e4f534a)+text+struct.pack('<II',len(binary),0x004e4942)+binary);rows.append({'name':label,'bones':len(body.nodes),'clips':len(g['animations']),'triangles':tris,'body':item['source'],'motion':item['motion_source'],'sha256':hashlib.sha256(p.read_bytes()).hexdigest()});print(label,len(body.nodes),len(g['animations']),p.stat().st_size,flush=True)
(O/'four-models.json').write_text(json.dumps(rows,indent=2))
