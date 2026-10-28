"""Actual-time reference comparison and complete front/side study, no game edits."""
from PIL import Image,ImageOps,ImageDraw,ImageFont
from pathlib import Path
import json,subprocess,sys
R=Path(__file__).resolve().parents[3];STUDY='02' if '--study02' in sys.argv else '01';END=51 if STUDY=='02' else 36;S=R/('dist/roar-study-'+STUDY);OUT=R/('docs/bilge-roar-study-'+STUDY);OUT.mkdir(parents=True,exist_ok=True)
refroot=Path('/workspace/reference-review/roar-full-080429')
pts=[float(f['best_effort_timestamp_time']) for f in json.loads((refroot/'timestamps.json').read_text())['frames']]
# User supplied complete replacement: all 38 frames, no temporal/spatial crop.
REFERENCE_DURATION=1.671792
CYCLE=max(1.7,REFERENCE_DURATION)
font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',16)
small=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',13)
sequence=[]
for speed in [1,1,.5]:
 sequence.extend([(0,speed)]*9)
 sequence.extend([(i*speed/30,speed) for i in range(round(CYCLE*30/speed))])
 sequence.extend([(CYCLE,speed)]*12)

def panel(im):return ImageOps.contain(im.convert('RGB'),(420,500))
modes=['comparison'] if '--comparison-only' in sys.argv else ['front-side'] if '--front-side-only' in sys.argv else ['comparison','front-side']
for mode in modes:
 folder=S/('composed-'+mode);folder.mkdir(exist_ok=True)
 for idx,(t,speed) in enumerate(sequence):
  frame=min(END,round(t*30));canvas=Image.new('RGB',(1244,1424) if mode=='comparison' else (864,570),'#15191f');d=ImageDraw.Draw(canvas)
  if mode=='comparison':
   # Full source timeline. Existing study is held at its last pose, never reset early.
   refid=min(range(len(pts)),key=lambda i:abs(pts[i]-t))
   images=[Image.open(refroot/f'{refid+1:03}.jpg'),Image.open(S/'reference'/f'{frame:03}.png')]
   titles=['YENİ REFERANS · tamamı','BİLGE · tam süre · çalışma 02' if STUDY=='02' else 'BİLGE · önceki çalışma 01']
  else:
   images=[Image.open(S/'front'/f'{frame:03}.png'),Image.open(S/'side'/f'{frame:03}.png')];titles=['ÖN · efekt yok','YAN · efekt yok']
  for i,(im,title) in enumerate(zip(images,titles)):
   if mode=='comparison':
    im=ImageOps.contain(im.convert('RGB'),(610,1356) if i==0 else (610,726));canvas.paste(im,(i*622+(610-im.width)//2,32 if i==0 else 312));d.text((i*622+8,8),title,font=font,fill='white')
   else:
    im=panel(im);canvas.paste(im,(i*432+(420-im.width)//2,32+(500-im.height)//2));d.text((i*432+8,8),title,font=font,fill='white')
  d.text((10,1394 if mode=='comparison' else 540),f'{speed:g}× · kayıt {min(t,REFERENCE_DURATION):.2f} sn · çalışma {min(t,END/30):.2f} sn',font=font,fill='white')
  canvas.save(folder/f'{idx:03}.png')
 # Each source frame must appear in the comparison; no truncated recovery.
 if mode=='comparison':
  used={min(range(len(pts)),key=lambda i:abs(pts[i]-t)) for t,_ in sequence}
  assert len(used)==len(pts),(len(used),len(pts))
 subprocess.run(['ffmpeg','-v','error','-y','-framerate','30','-i',str(folder/'%03d.png'),'-c:v','libx264','-preset','fast','-crf','20','-pix_fmt','yuv420p','-movflags','+faststart',str(OUT/(mode+'.mp4'))],check=True)
# Key pose strip for quick review.
strip=Image.new('RGB',(1260,1040),'#15191f');d=ImageDraw.Draw(strip)
for i,f in enumerate([0,4,8,23,30,51] if STUDY=='02' else [0,5,9,17,27,36]):
 im=Image.open(S/'reference'/f'{f:03}.png');strip.paste(im,(i%3*420,i//3*520));d.text((i%3*420+8,i//3*520+501),f'{f/30:.2f} sn',font=font,fill='white')
strip.save(OUT/'key-poses.jpg')
for name in ['study-audit.json','authored-keys.json','weight-paint.json']:(OUT/name).write_bytes((S/name).read_bytes())
print('COMPOSED',OUT)
