"""Minimal LDraw geometry reader: bounding boxes and stud positions of parts.

Used to derive footprints/orientation of parts so the generator can place
them on the stud grid correctly.
"""
import os, json, functools
import numpy as np

LIB = os.environ.get('LDRAW_LIB', '/home/user/gkjohnson/ldraw-parts-library/complete/ldraw')
SEARCH = ['parts', 'p', 'models', 'p/48', 'parts/s']

@functools.lru_cache(maxsize=None)
def _index():
    idx = {}
    for d in ['parts', 'p', 'models']:
        for f in os.listdir(os.path.join(LIB, d)):
            idx.setdefault(f.lower(), os.path.join(LIB, d, f))
    for d, pre in [('parts/s', 's/'), ('p/48', '48/'), ('p/8', '8/')]:
        full = os.path.join(LIB, d)
        if os.path.isdir(full):
            for f in os.listdir(full):
                idx.setdefault(pre + f.lower(), os.path.join(full, f))
    return idx

def find(name):
    n = name.strip().replace('\\', '/').lower()
    return _index().get(n)

@functools.lru_cache(maxsize=None)
def parse(name):
    path = find(name)
    if not path:
        raise FileNotFoundError(name)
    pts, subs, title = [], [], None
    with open(path, encoding='utf-8', errors='replace') as fh:
        for line in fh:
            t = line.split()
            if not t:
                continue
            if t[0] == '0' and title is None:
                title = line[2:].strip()
            elif t[0] == '1' and len(t) >= 15:
                v = list(map(float, t[2:14]))
                m = np.array([[v[3], v[4], v[5], v[0]], [v[6], v[7], v[8], v[1]], [v[9], v[10], v[11], v[2]], [0, 0, 0, 1]])
                subs.append((m, ' '.join(t[14:])))
            elif t[0] in ('3', '4'):
                n = int(t[0])
                c = list(map(float, t[2:2 + 3 * n]))
                for i in range(n):
                    pts.append(c[3 * i:3 * i + 3])
    return title, np.array(pts).reshape(-1, 3), subs

def is_stud(name):
    n = os.path.basename(name.lower().replace('\\', '/'))
    return n.startswith('stud') and not n.startswith(('stud3', 'stud4', 'stud6', 'stud12', 'stud16', 'stud18', 'stud22'))

def collect(name, m=np.eye(4), out=None, studs=None, depth=0):
    if out is None:
        out, studs = [], []
    title, pts, subs = parse(name)
    if len(pts):
        h = np.c_[pts, np.ones(len(pts))] @ m.T
        out.append(h[:, :3])
    for sm, sn in subs:
        mm = m @ sm
        if is_stud(sn):
            up = mm[:3, :3] @ np.array([0, -1, 0])
            studs.append((mm[:3, 3].round(2).tolist(), up.round(2).tolist()))
            continue
        try:
            collect(sn, mm, out, studs, depth + 1)
        except FileNotFoundError:
            pass
    return out, studs

@functools.lru_cache(maxsize=None)
def info(name):
    if not name.lower().endswith('.dat'):
        name += '.dat'
    title = parse(name)[0]
    out, studs = collect(name)
    allp = np.vstack(out) if out else np.zeros((1, 3))
    lo, hi = allp.min(0), allp.max(0)
    top = [s[0] for s in studs if s[1][1] < -0.9]
    return {'title': title, 'min': lo.round(2).tolist(), 'max': hi.round(2).tolist(), 'top_studs': top,
            'side_studs': [s for s in studs if abs(s[1][1]) < 0.1]}

if __name__ == '__main__':
    import sys
    for p in sys.argv[1:]:
        i = info(p)
        ts = i['top_studs']
        xs = sorted(set(round(s[0]) for s in ts)); zs = sorted(set(round(s[2]) for s in ts)); ys = sorted(set(round(s[1]) for s in ts))
        print(f"{p:10s} {i['title'][:48]:48s} min={i['min']} max={i['max']} studs={len(ts)} x={xs[:8]} y={ys} z={zs[:8]} side={len(i['side_studs'])}")
