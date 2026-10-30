import sys
from build_icewolf import *
def sheet(name, nf=8, yaw=60, size=(260, 330), out=None):
    S, M = make_mesh(); c = bake(S, name); fr = c['frames']; n = len(fr)
    im = Image.new('RGB', (size[0] * nf, size[1]))
    for i in range(nf):
        pose, root = fr[min(n - 1, int(i * n / nf))]
        a = render(S, M, pose, root, yaw=yaw, pitch=8, size=size, ss=1, center=np.array([0, .9, 0]), scale=1.15)
        im.paste(a, (i * size[0], 0))
    im.save(out or f'/tmp/sheet_{name}.png')
if __name__ == '__main__':
    for n in sys.argv[1:]: sheet(n)
