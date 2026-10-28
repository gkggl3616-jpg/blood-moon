"""Full original reference against actual Three.js GLB playback, 1x/0.5x labelled."""
from PIL import Image,ImageOps,ImageDraw,ImageFont
from pathlib import Path
import json,subprocess
R=Path(__file__).resolve().parents[3];S=R/'dist/roar-study-03';OUT=R/'docs/bilge-roar-study-03';OUT.mkdir(exist_ok=True);REF=Path('/workspace/reference-review/roar-full-080429');pts=[float(x['best_effort_timestamp_time']) for x in json.loads((REF/'timestamps.json').read_text())['frames']]
font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',18);small=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',15)
seq=[]
for speed in [1,1,.5]:
 seq.extend([(0,speed)]*9);seq.extend([(i*speed/30,speed) for i in range(round(1.7*30/speed))]);seq.extend([(1.7,speed)]*12)
used=set()
for mode in ['comparison','front-side']:
 folder=S/('composed-'+mode);folder.mkdir(exist_ok=True)
 for i,(t,speed) in enumerate(seq):
  f=min(51,round(t*30));canvas=Image.new('RGB',(1244,1424) if mode=='comparison' else (1280,720),'#101922');d=ImageDraw.Draw(canvas)
  if mode=='comparison':
   refid=min(range(len(pts)),key=lambda q:abs(pts[q]-t));used.add(refid)
   im=Image.open(REF/f'{refid+1:03}.jpg');canvas.paste(im,(0,32))
   # Only the game camera canvas is reframed; reference is preserved in full.
   im=Image.open(S/'game-reference'/f'{f:03}.png').crop((150,0,810,960));im=ImageOps.contain(im,(610,1056));canvas.paste(im,(622,220))
   d.text((8,8),'TAM REFERANS · 38 kare',font=font,fill='white');d.text((630,8),'BİLGE · Three.js · çalışma 03',font=font,fill='white');d.text((630,56),'Gerçek GLB + el alevi + dövme parlaması',font=small,fill='#9cdbff');d.text((10,1394),f'{speed:g}× · zaman {t:.2f} sn · tam toparlanma',font=font,fill='white')
  else:
   for j,view in enumerate(['front','side']):
    im=ImageOps.contain(Image.open(S/('game-'+view)/f'{f:03}.png'),(632,632));canvas.paste(im,(j*640+4,40));d.text((j*640+12,10),'ÖN · efektli' if not j else 'YAN · efektli',font=font,fill='white')
   d.text((12,690),f'{speed:g}× · {t:.2f} sn · aynı GLB / aynı iskelet',font=font,fill='white')
  canvas.save(folder/f'{i:03}.png')
 subprocess.run(['ffmpeg','-v','error','-y','-framerate','30','-i',str(folder/'%03d.png'),'-c:v','libx264','-preset','fast','-crf','19','-pix_fmt','yuv420p','-movflags','+faststart',str(OUT/(mode+'.mp4'))],check=True)
assert len(used)==38,len(used)
strip=Image.new('RGB',(1440,1040),'#101922');d=ImageDraw.Draw(strip)
for i,f in enumerate([0,4,8,23,33,51]):
 im=Image.open(S/'game-reference'/f'{f:03}.png').resize((480,480));strip.paste(im,(i%3*480,i//3*520));d.text((i%3*480+8,i//3*520+484),f'{f/30:.2f} sn',font=font,fill='white')
strip.save(OUT/'key-poses.jpg',quality=93)
for view in ['front','side']:Image.open(S/f'game-no-fx-{view}.png').save(OUT/f'deformation-{view}.jpg',quality=93)
for name in ['rig-build','effects','four-weight-fit','pose-audit','export-audit','browser-audit']:
 (OUT/'audits'/f'{name}.json').write_bytes((S/f'{name}.json').read_bytes())
(OUT/'audits/composition.json').write_text(json.dumps({'source_frames_used':len(used),'reference_spatial_crop':False,'duration_s':len(seq)/30,'fps':30,'output_frames':len(seq),'speeds':[1,1,.5],'gameplay_capture':'Three.js from exported GLB, not Blender movie'},indent=2));print('COMPOSED03',len(seq),len(used))
