"""Fit the full existing growl+roar phrase to the pose, not just its quiet intro.
Remove the recorded gap, compress time without a pitch jump, leave headroom.
Runtime adapts this single decoded phrase to each source pose's duration.
"""
from pathlib import Path
import subprocess,wave,array,json
R=Path(__file__).resolve().parents[1];D=R/'docs/karahan-v0118';D.mkdir(exist_ok=True);tmp=D/'roar-phrase-pre-normalize.wav';output=R/'app/src/main/assets/media/roar-voice.wav'
subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-i',str(R/'app/src/main/assets/media/roar-deep.mp3'),'-filter_complex','[0:a]asplit=2[a][b];[a]atrim=start=0:end=1.36,asetpts=PTS-STARTPTS[a1];[b]atrim=start=1.8:end=3.11,asetpts=PTS-STARTPTS[b1];[a1][b1]concat=n=2:v=0:a=1,atempo=2.02,atrim=end=1.32,highpass=f=45,lowpass=f=6800,afade=t=in:d=0.015,afade=t=out:st=1.18:d=0.14[out]','-map','[out]','-ar','44100','-ac','1',str(tmp)],check=True)
with wave.open(str(tmp)) as w:params=w.getparams();samples=array.array('h',w.readframes(w.getnframes()))
peak=max(abs(v) for v in samples);gain=.62*32767/max(1,peak);samples=array.array('h',(round(v*gain) for v in samples))
with wave.open(str(output),'wb') as w:w.setparams(params);w.writeframes(samples.tobytes())
report={'source':'existing roar-deep.mp3, not archive audio','preserved_segments_seconds':[[0,1.36],[1.8,3.11]],'removed_gap_seconds':[1.36,1.8],'pitch_preserving_atempo':2.02,'buffer_seconds':len(samples)/44100,'normalized_peak':max(abs(v) for v in samples)/32768,'single_decoded_voice':True};(D/'roar-audio-processing.json').write_text(json.dumps(report,indent=2));print(report)
