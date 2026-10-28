"""Actual-time reference comparison and complete front/side study, no game edits."""
from PIL import Image,ImageOps,ImageDraw,ImageFont
from pathlib import Path
import json,subprocess,sys
R=Path(__file__).resolve().parents[3];S=R/'dist/roar-study-01';OUT=R/'docs/bilge-roar-study-01';OUT.mkdir(parents=True,exist_ok=True)
refroot=Path('/workspace/reference-review/20261028-run-roar')
meta=json.loads((refroot/'manifest.json').read_text());pts=[float(f['best_effort_timestamp_time']) for f in next(v for v in meta if v['video']==3)['frames']]
font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',16)
small=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',13)
sequence=[]
for speed in [1,1,.5]:
 sequence.extend([(0,speed)]*9)
 sequence.extend([(i*speed/30,speed) for i in range(round(36/speed))])
 sequence.extend([(1.2,speed)]*12)

def panel(im):return ImageOps.contain(im.convert('RGB'),(420,500))
modes=['comparison'] if '--comparison-only' in sys.argv else ['front-side'] if '--front-side-only' in sys.argv else ['comparison','front-side']
for mode in modes:
 folder=S/('composed-'+mode);folder.mkdir(exist_ok=True)
 for idx,(t,speed) in enumerate(sequence):
  frame=min(36,round(t*30));canvas=Image.new('RGB',(864,570),'#15191f');d=ImageDraw.Draw(canvas)
  if mode=='comparison':
   # Native source timestamps; no phase remapping. End pose held after source roar.
   refid=min(range(32,60),key=lambda i:abs(pts[i]-(pts[32]+t)))
   images=[Image.open(refroot/'v3'/f'{refid+1:03}.jpg').crop((40,350,540,1010)),Image.open(S/'reference'/f'{frame:03}.png')]
   titles=['REFERANS · özgün kayıt','BİLGE · efekt yok · çalışma 01']
  else:
   images=[Image.open(S/'front'/f'{frame:03}.png'),Image.open(S/'side'/f'{frame:03}.png')];titles=['ÖN · efekt yok','YAN · efekt yok']
  for i,(im,title) in enumerate(zip(images,titles)):
   im=panel(im);canvas.paste(im,(i*432+(420-im.width)//2,32+(500-im.height)//2));d.text((i*432+8,8),title,font=font,fill='white')
  d.text((10,540),f'{speed:g}× oynatım · hareket {t:.2f} sn · sessiz önizleme',font=font,fill='white')
  canvas.save(folder/f'{idx:03}.png')
 subprocess.run(['ffmpeg','-v','error','-y','-framerate','30','-i',str(folder/'%03d.png'),'-c:v','libx264','-preset','fast','-crf','20','-pix_fmt','yuv420p','-movflags','+faststart',str(OUT/(mode+'.mp4'))],check=True)
# Key pose strip for quick review.
strip=Image.new('RGB',(1260,1040),'#15191f');d=ImageDraw.Draw(strip)
for i,f in enumerate([0,5,9,17,27,36]):
 im=Image.open(S/'reference'/f'{f:03}.png');strip.paste(im,(i%3*420,i//3*520));d.text((i%3*420+8,i//3*520+501),f'{f/30:.2f} sn',font=font,fill='white')
strip.save(OUT/'key-poses.jpg')
for name in ['study-audit.json','authored-keys.json','weight-paint.json']:(OUT/name).write_bytes((S/name).read_bytes())
print('COMPOSED',OUT)
