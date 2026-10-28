import sys,tempfile,threading,time,tkinter
from pathlib import Path
sys.path.insert(0,'/workspace/rogue-blood-moon/desktop/xfs_browser')
from app import Browser
from test_core import make_archive
import xfs_core as core
with tempfile.TemporaryDirectory() as directory:
 root=Path(directory);path=make_archive(root/'sample.xfs',[('model.ltb',b'model'*1000,0)])
 archive=core.open_archive(path);started=threading.Event();app=Browser();app.withdraw()
 def work(cancel,progress):
  def part(*_):started.set();cancel.wait(3)
  core.extract_entry(archive,archive.entries[0],root/'out',cancel,part)
 app.job('main',work,lambda _:None)
 deadline=time.monotonic()+4
 while not started.is_set() and time.monotonic()<deadline:app.update();time.sleep(.003)
 assert started.is_set()
 app.close();deadline=time.monotonic()+4
 while time.monotonic()<deadline:
  try:
   app.update()
   if not app.winfo_exists():break
  except tkinter.TclError:break
  time.sleep(.003)
 else:raise RuntimeError('Close did not complete')
 assert not list((root/'out').rglob('*.part'))
 assert not (root/'out/Root/model.ltb').exists()
 print('ACTIVE_CLOSE_OK: worker cancelled and partial removed before window closed')
