"""Verify the user's complete replacement reference survives the exported video."""
from pathlib import Path
from PIL import Image,ImageChops,ImageStat
from io import BytesIO
import subprocess,json,hashlib
R=Path(__file__).resolve().parents[3];D=R/'docs/bilge-roar-study-02';reports=[]
for name in ['comparison.mp4','front-side.mp4']:
 p=D/name;info=json.loads(subprocess.check_output(['ffprobe','-v','error','-count_frames','-show_entries','format=duration:stream=codec_name,width,height,nb_read_frames,avg_frame_rate','-of','json',str(p)],text=True));v=info['streams'][0]
 assert v['codec_name']=='h264' and int(v['nb_read_frames'])==267
 assert abs(float(info['format']['duration'])-8.9)<.01
 subprocess.run(['ffmpeg','-v','error','-i',str(p),'-f','null','-'],check=True,capture_output=True)
 reports.append({'file':name,'probe':info,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'all_frames_decode':'PASS'})
# 9 lead-in frames + source time 46/30 = output frame 55, beyond the old 1.2s cutoff.
b=subprocess.check_output(['ffmpeg','-v','error','-i',str(D/'comparison.mp4'),'-vf',r'select=eq(n\,55)','-frames:v','1','-f','image2pipe','-c:v','png','-'])
actual=Image.open(BytesIO(b)).convert('RGB').crop((0,32,610,1388))
expected=Image.open('/workspace/reference-review/roar-full-080429/038.jpg').convert('RGB')
error=sum(ImageStat.Stat(ImageChops.difference(actual,expected)).mean)/3
assert error<12,('final reference frame is missing or cropped',error)
report={'videos':reports,'last_source_frame_38_visible_after_old_cutoff':True,'sample_source_time_s':46/30,'sample_output_frame':55,'last_frame_mean_absolute_pixel_error':error,'source_frames_included':38,'source_temporal_trim':None,'source_spatial_crop':None}
(D/'video-verification.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
