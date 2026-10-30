import sys; sys.path.insert(0, '../retarget')
from build_icewolf import *
from retarget import retarget
from anim import feet_lock
def sheet_fbx(path, out, nf=8, t0=0, t1=None, yaw=60):
    S, M = make_mesh(); fr, dur = retarget(path, S, t0=t0, t1=t1); n = len(fr); size = (260, 330)
    im = Image.new('RGB', (size[0] * nf, size[1]))
    for i in range(nf):
        pose, dy = fr[min(n - 1, int(i * n / nf))]; root = feet_lock(S, pose)
        im.paste(render(S, M, pose, root, yaw=yaw, pitch=8, size=size, ss=1, center=np.array([0, .9, 0]), scale=1.15), (i * size[0], 0))
    im.save(out); print(out, dur)
if __name__ == '__main__': sheet_fbx(sys.argv[1], sys.argv[2], t0=float(sys.argv[3]) if len(sys.argv) > 3 else 0, t1=float(sys.argv[4]) if len(sys.argv) > 4 else None)
