"""Decode allowlisted native DTX v-5 to PNG, preserving alpha and width/height."""
from pathlib import Path
import struct,io,json,hashlib
from PIL import Image
R=Path(__file__).resolve().parents[1];BASE=R/'art/3d/source/wolfteam-archive/textures';OUT=R/'art/3d/source/wolfteam-archive/decoded';reports=[]
for entry in json.loads((R/'docs/native-pair-review/texture-selection.json').read_text()):
 rel=Path(entry['path']);data=(BASE/rel).read_bytes();resource,version,width,height=struct.unpack_from('<IiHH',data)
 assert resource==0 and version==-5 and 0<width<=4096 and 0<height<=4096
 bpp=data[26];offset=164
 if bpp in (4,5,6):
  fourcc={4:b'DXT1',5:b'DXT3',6:b'DXT5'}[bpp];length=((width+3)//4)*((height+3)//4)*(8 if bpp==4 else 16);assert len(data)>=offset+length
  header=bytearray(128);header[:4]=b'DDS ';struct.pack_into('<IIIIIII',header,4,124,0x81007,height,width,length,0,1);struct.pack_into('<II',header,76,32,4);header[84:88]=fourcc;struct.pack_into('<I',header,108,0x1000)
  image=Image.open(io.BytesIO(header+data[offset:offset+length])).convert('RGBA')
 elif bpp==3:
  length=width*height*4;assert len(data)>=offset+length;image=Image.frombytes('RGBA',(width,height),data[offset:offset+length],'raw','BGRA')
 else:raise ValueError(f'Unsupported DTX format {bpp}: {rel}')
 target=(OUT/rel).with_suffix('.png');target.parent.mkdir(parents=True,exist_ok=True);image.save(target)
 reports.append({'source':str(rel),'png':str(target.relative_to(R)),'width':width,'height':height,'format':bpp,'alpha_range':image.getchannel('A').getextrema(),'rgba_sha256':hashlib.sha256(image.tobytes()).hexdigest()})
(R/'docs/native-pair-review/texture-decode.json').write_text(json.dumps(reports,indent=2));print('Converted',len(reports),'DTX textures')
