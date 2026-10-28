import os
import tempfile
import time
import unittest
from pathlib import Path
from test_core import make_archive

@unittest.skipUnless(os.name=='nt' or os.environ.get('DISPLAY'), 'A graphical session is required')
class InterfaceTests(unittest.TestCase):
    def test_worker_filter_paging_preview_and_heartbeat(self):
        from app import Browser, PAGE_SIZE
        app=Browser();app.withdraw();beats=[]
        def beat():
            beats.append(time.monotonic())
            if not app.closing:app.after(15,beat)
        app.after(1,beat)
        def wait_for(predicate,timeout=8):
            deadline=time.monotonic()+timeout
            while time.monotonic()<deadline:
                app.update()
                if predicate():return
                time.sleep(.003)
            self.fail('GUI worker timed out')
        try:
            with tempfile.TemporaryDirectory() as folder:
                path=make_archive(Path(folder)/'gui.xfs',[(f'pedro_{i:05}.ltb' if i%2 else f'pedro_{i:05}.dtx',b'native',1) for i in range(40000)])
                import xfs_core
                def opened(archive):
                    app.archive=archive;app.ext.set('.ltb');app.start_search()
                app.job('main',lambda c,p:xfs_core.open_archive(path,c,p),opened)
                wait_for(lambda:app.archive is not None and len(app.matches)==20000 and not app.jobs)
                self.assertLessEqual(len(app.tree.get_children()),PAGE_SIZE)
                first=app.tree.get_children()[0];app.turn_page(1)
                self.assertNotEqual(first,app.tree.get_children()[0])
                app.query.set('pedro_000');wait_for(lambda:len(app.matches)==50 and not app.jobs and app.search_timer is None)
                app.tree.selection_set(app.tree.get_children()[0]);app.show_selected()
                wait_for(lambda:'hex' in app.details.get('1.0','end') and not app.jobs)
                self.assertGreater(len(beats),10)
                maximum=max(b-a for a,b in zip(beats,beats[1:]));self.assertLess(maximum,1.0)
                print(f'GUI: 40000 entries, 200 visible max, {len(beats)} heartbeats, max gap {maximum:.3f}s')
        finally:app.close()

if __name__=='__main__':unittest.main(verbosity=2)
