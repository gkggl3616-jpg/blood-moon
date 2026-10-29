"""Measure source joint stance and root starts, without sampling all mesh vertices."""
import sys,json,struct,statistics,hashlib,argparse
from pathlib import Path
from mathutils import Matrix,Vector
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'tools'));import export_bilge_native_basis as e
parser=argparse.ArgumentParser();parser.add_argument('--asset',default='art/characters/premium-wolf-01/v2/wolf.glb');args=parser.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []);P=R/args.asset;b=e.Reader().from_file(str(R/'art/3d/source/wolfteam-archive/selected/wt_wolf_power_r.ltb'));m=e.Reader().from_file(str(R/'art/3d/source/pedro-native/new-motion/wt_new_wolf_ch.ltb'));ix={n.name:i for i,n in enumerate(b.nodes)};clips={a.name:a for a in m.animations};pts=[v.location for p in b.pieces for v in p.lods[0].vertices];low=min(v.y for v in pts);unit=2.4/(max(v.y for v in pts)-low)
def pose(a,k,upper=None):
 result=[]
 for i,n in enumerate(b.nodes):
  animation=clips[upper] if upper and n.name in upper_names else a;j=min(k,len(animation.keyframes)-1);t=animation.node_keyframe_transforms[i][j];local=Matrix.LocRotScale(t.location,t.rotation.normalized(),Vector((1,1,1)));result.append(result[ix[n.parent.name]]@local if n.parent else local)
 return result
upper_names=set()
for n in b.nodes:
 p=n
 while p:
  if p.name=='Bip01 Spine1':upper_names.add(n.name)
  p=p.parent
starts={}
for name,a in clips.items():
 p=pose(a,0)[ix['Bip01']].translation;starts[name]=[p.x*unit,(p.y-low)*unit,p.z*unit]
records=[]
for role,upper in [('LWF','UMWF'),('T_WallDash',None)]:
 a=clips[role];times=[k.time/1000 for k in a.keyframes];frames=[pose(a,k,upper) for k in range(len(times))];speeds=[]
 for name in ['Bip01 L Foot','Bip01 R Foot']+(['Bip01 L Hand','Bip01 R Hand'] if upper is None else []):
  points=[f[ix[name]].translation*unit for f in frames];minimum=min(p.y for p in points)
  for k,(p,q) in enumerate(zip(points,points[1:])):
   dt=times[k+1]-times[k]
   if max(p.y,q.y)<minimum+.065 and dt>0:
    speed=abs(q.z-p.z)/dt
    if speed>.05:speeds.append(speed)
 stride=statistics.median(speeds)*times[-1];records.append({'clip':role,'duration':times[-1],'stance_samples':len(speeds),'stride_m':stride})
raw=P.read_bytes();n=struct.unpack_from('<I',raw,12)[0];g=json.loads(raw[20:20+n]);binary=raw[28+n:];meta=g['scenes'][0]['extras'];before=hashlib.sha256(json.dumps(g['animations'],sort_keys=True).encode()).hexdigest();meta.update(nativeClipRootStarts=starts,nativeRollClearance=[[0,0],[1,0]],nativeGroundingMethod='Actual blended skin support probes; native vertical arc and source keys preserved',nativeLocomotion={'quadClip':'T_WallDash','walkStrideMeters':records[0]['stride_m'],'runStrideMeters':records[1]['stride_m']})
for material in g.get('materials',[]):
 if material.get('name')=='Premium_Fur':material['pbrMetallicRoughness'].update(baseColorFactor=[.8,.8,.8,1],metallicFactor=0,roughnessFactor=.95)
assert hashlib.sha256(json.dumps(g['animations'],sort_keys=True).encode()).hexdigest()==before
text=json.dumps(g,separators=(',',':')).encode();text+=b' '*(-len(text)%4);P.write_bytes(struct.pack('<4sII',b'glTF',2,28+len(text)+len(binary))+struct.pack('<II',len(text),0x4e4f534a)+text+struct.pack('<II',len(binary),0x004e4942)+binary);(R/'docs/premium-wolf-01/v2-source-contract.json').write_text(json.dumps({'source_stance':records,'root_starts':starts,'source_keys_unchanged':True},indent=2));print('NATIVE_CONTRACT',records)
