"""Generate step-by-step building instruction booklets (HTML + PDF) for every module.

Pipeline:
  1. build module models, split over-full steps, export LDraw with STEP lines
  2. write render jobs (one image per step, new parts in full colour, earlier parts faded)
  3. render a gallery of part icons for the call-outs and inventories
  4. write HTML booklets and print them to PDF with headless Chromium
"""
import json, math, os, sys, html, subprocess
from collections import Counter, OrderedDict, defaultdict
import numpy as np

sys.path.insert(0, os.path.dirname(__file__))
from lego import Model, COLORS, rot_y
import lionhold, millbrook, ravencrag, warriors, diorama, bom, catalog, export
from minifig import horse_parts

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
BUILD = os.path.join(REPO, 'build')
WWW_MODELS = export.WWW
RENDER = ['node', os.environ.get('NOBLES_RENDER', '/home/user/tres_work/render.mjs')]

MODULES = OrderedDict([
    ('lionhold', dict(book=1, title='Lionhold', subtitle='Castle of House Aurelion - the Crimson Lions', mod=lionhold)),
    ('millbrook', dict(book=2, title='Millbrook', subtitle='Village of the Common Folk', mod=millbrook)),
    ('ravencrag', dict(book=3, title='Ravencrag Keep', subtitle='Stronghold of House Corvane - the Black Ravens', mod=ravencrag)),
    ('warriors', dict(book=4, title='Warriors & Weapons', subtitle='Knights, soldiers, villagers, horses and siege engines', mod=None)),
])


# ---------------------------------------------------------------------------
def warriors_model():
    """All figures, horses and catapults as one instruction model (each at the origin, own steps)."""
    m = Model('warriors', 'Warriors & Weapons')
    groups = []          # (section title, faction, [part indices])
    for key, (f, faction, role) in warriors.FIGS.items():
        m.new_section(role)
        start = len(m.parts)
        for part, col, pos, M in f.parts():
            m.add_free(part, col, pos, M)
        groups.append((role, faction, list(range(start, len(m.parts)))))
        m.step()
    for key, h in warriors.HORSES.items():
        title = 'Battle horse for ' + warriors.FIGS[h['rider']][2].split(',')[0].split(' (')[0]
        m.new_section(title)
        start = len(m.parts)
        for part, col, pos, M in horse_parts(h['color'], saddle=h['saddle'], barding=h['barding']):
            m.add_free(part, col, pos, M)
        groups.append((title, 'lions' if 'lion' in key else 'ravens', list(range(start, len(m.parts)))))
        m.step()
    for key, colors, title, faction in (('lion_catapult', ('reddish_brown', 'red'), 'Lion catapult', 'lions'),
                                        ('raven_catapult', ('reddish_brown', 'dark_blue'), 'Raven catapult', 'ravens')):
        m.new_section(title)
        c = warriors.catapult_model(key, *colors)
        start = len(m.parts)
        base = m.step_no
        for p in c.parts:
            i = m.add_free(p.ld, p.color, p.pos, p.M)
            m.parts[i].step = base + p.step
        m.step_no = base + max(p.step for p in c.parts)
        groups.append((title, faction, list(range(start, len(m.parts)))))
        m.step()
    return m, groups


def build_all():
    models = OrderedDict()
    for name, info in MODULES.items():
        if name == 'warriors':
            m, groups = warriors_model()
            info['groups'] = groups
        else:
            m = info['mod'].build()
            m.rebalance_steps(28)
        m.compact_steps()
        models[name] = m
    return models


# ---------------------------------------------------------------------------
def section_camera(m, idxs):
    """Pick a camera yaw/pitch that looks at a section from the outside of the module."""
    pts = np.array([m.parts[i].pos for i in idxs])
    allp = np.array([p.pos for p in m.parts if p.lvl is not None] or [p.pos for p in m.parts])
    c_mod = (allp.min(0) + allp.max(0)) / 2
    size = max(allp.max(0)[0] - allp.min(0)[0], allp.max(0)[2] - allp.min(0)[2], 1)
    c = pts.mean(0)
    dx, dz = c[0] - c_mod[0], c[2] - c_mod[2]
    if math.hypot(dx, dz) < 0.18 * size:
        return 30.0, 42.0
    yaw = math.degrees(math.atan2(dx, -dz))
    # prefer 3/4 views: rotate towards the front of the model
    yaw += -25 if yaw > 0 else 25
    return yaw, 32.0


def step_table(name, m):
    """Per-step info: new parts, call-out counts, camera."""
    lines, order, steps = m.main_lines()
    line_of = {pi: li for li, pi in enumerate(order)}
    by_step = defaultdict(list)
    by_sec = defaultdict(list)
    for pi, p in enumerate(m.parts):
        by_step[p.step].append(pi)
        by_sec[p.section].append(pi)
    table = []
    cams = {}
    for sec, idxs in by_sec.items():
        yaw, pitch = section_camera(m, idxs)
        if name == 'millbrook':
            # every village building faces the road (south): always look from the front
            yaw, pitch = (32.0 if yaw >= 0 else -32.0), 34.0
        cams[sec] = (yaw, pitch)
    # focus = the section itself plus everything built earlier underneath/around it
    sec_focus = {}
    for sec, idxs in by_sec.items():
        cells = [c for i in idxs for c in m.parts[i].cells]
        if not cells:
            sec_focus[sec] = idxs
            continue
        x0 = min(c[0] for c in cells) - 1; x1 = max(c[0] for c in cells) + 1
        z0 = min(c[1] for c in cells) - 1; z1 = max(c[1] for c in cells) + 1
        first = min(m.parts[i].step for i in idxs)
        extra = [i for i, p in enumerate(m.parts) if p.step < first and p.lvl is not None and p.lvl >= 0
                 and p.ld not in ('3811',) and any(x0 <= c[0] <= x1 and z0 <= c[1] <= z1 for c in p.cells)]
        sec_focus[sec] = sorted(set(idxs) | set(extra))
    for s in sorted(by_step):
        new = by_step[s]
        sec = m.parts[new[0]].section
        cnt = Counter()
        for pi in new:
            p = m.parts[pi]
            ld = p.ld[:-4] if p.ld.endswith('.dat') else p.ld
            if ld in ('3815b', '3816b', '3817b', '73200-f2'):
                if ld in ('3815b', '73200-f2'):
                    cnt[('HIPSLEGS', p.color)] += 1
                continue
            cnt[(ld, p.color)] += 1
        table.append(dict(step=s, section=sec, new=[line_of[pi] for pi in new], callout=cnt,
                          focus=[line_of[pi] for pi in sec_focus[sec]], cam=cams[sec]))
    return lines, order, steps, table


# ---------------------------------------------------------------------------
def gallery(keys):
    """Model with one entry per (part, colour) used in call-outs; returns (model lines, {key: [line idx]})."""
    m = Model('gallery', 'Parts gallery')
    idx = {}
    for n, (ld, col) in enumerate(sorted(keys)):
        base = np.array([(n % 20) * 500.0, 0, (n // 20) * 500.0])
        start = len(m.parts)
        if ld == 'HIPSLEGS':
            for part, dy in (('3815b', 32), ('3816b', 44), ('3817b', 44)):
                m.add_free(part, col, base + [0, dy - 72, 0])
        elif ld == '3811':
            m.add_free(ld, col, base + [0, 0, 20000])
        else:
            m.add_free(ld, col, base)
        idx[(ld, col)] = list(range(start, len(m.parts)))
    lines, order, steps = m.main_lines()
    assert order == list(range(len(m.parts)))
    return lines, steps, idx


def icon_name(ld, col):
    return f'{ld}_{col}.png'


# ---------------------------------------------------------------------------
def run(job, path):
    with open(path, 'w') as fh:
        json.dump(job, fh)
    env = dict(os.environ, QUIET='1')
    subprocess.run(RENDER + [path], check=True, env=env)


def render_all(models, only=None):
    os.makedirs(BUILD, exist_ok=True)
    tables = {}
    allkeys = set()
    for name, m in models.items():
        lines, order, steps, table = step_table(name, m)
        tables[name] = (lines, order, steps, table)
        for t in table:
            allkeys |= set(t['callout'])
    if only in (None, 'parts'):
        glines, gsteps, gidx = gallery(allkeys)
        with open(os.path.join(WWW_MODELS, 'gallery.ldr'), 'w') as fh:
            fh.write('\n'.join(glines) + '\n')
        shots = []
        for key, li in gidx.items():
            shots.append({'only': li, 'focus': li, 'yaw': 35, 'pitch': 30, 'pad': 1.12,
                          'out': os.path.join(BUILD, 'parts', icon_name(*key)), 'size': [220, 220]})
        run({'size': [220, 220], 'models': [{'url': '/models/gallery.ldr', 'steps': gsteps, 'shots': shots}]},
            os.path.join(BUILD, 'job_parts.json'))
    for name, m in models.items():
        if only not in (None, name):
            continue
        lines, order, steps, table = tables[name]
        subs = warriors.submodels() if name == 'warriors' else None
        export.write_ldr(m, os.path.join(WWW_MODELS, f'instr_{name}.ldr'), subs=None)
        shots = []
        outdir = os.path.join(BUILD, 'steps', name)
        for t in table:
            s = t['step']
            shot = {'step': s, 'mode': 'fade', 'fmt': 'jpg', 'bg': '#ffffff',
                    'out': os.path.join(outdir, f'step_{s + 1:03d}.jpg'), 'size': [1200, 900]}
            if name == 'warriors':
                grp = next(g for g in MODULES['warriors']['groups'] if t['new'][0] in [order.index(i) for i in g[2]])
                li = [order.index(i) for i in grp[2]]
                shot.update(only=li, focus=li, focusHidden=True, yaw=-25, pitch=12, pad=1.1)
            else:
                shot.update(focus=t['focus'], focusHidden=True, yaw=t['cam'][0], pitch=t['cam'][1], pad=1.04)
            shots.append(shot)
        # cover image: finished module
        shots.append({'fmt': 'jpg', 'bg': '#ffffff', 'yaw': 30, 'pitch': 28, 'pad': 1.03,
                      'out': os.path.join(outdir, 'final.jpg'), 'size': [1600, 1100]})
        run({'size': [1200, 900], 'models': [{'url': f'/models/instr_{name}.ldr', 'steps': steps, 'shots': shots}]},
            os.path.join(BUILD, f'job_{name}.json'))
    return tables


if __name__ == '__main__':
    only = sys.argv[1] if len(sys.argv) > 1 else None
    models = build_all()
    for n, m in models.items():
        print(n, len(m.parts), 'parts', max(p.step for p in m.parts) + 1, 'steps')
    if only != 'none':
        render_all(models, only)
