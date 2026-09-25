"""Tiny LEGO modelling kernel.

Parts are placed on a stud grid:
    x, z  -> stud columns (x to the right, z away from the viewer)
    lvl   -> height in plates (1 brick = 3 plates), 0 = top of the baseplate
Every placement is checked for collisions, and `check_connectivity()` verifies
that every part is connected (stud-to-tube) to the baseplate.

Output is LDraw (.ldr / .mpd) with STEP meta-commands, readable by
BrickLink Studio, LeoCAD, LDCad and the three.js LDrawLoader.
"""
import math, random
from collections import defaultdict, deque
import numpy as np
import ldgeom

# name: (LDraw code, BrickLink id, BrickLink name)
COLORS = {
    'black': (0, 11, 'Black'), 'blue': (1, 7, 'Blue'), 'green': (2, 6, 'Green'),
    'red': (4, 5, 'Red'), 'yellow': (14, 3, 'Yellow'), 'white': (15, 1, 'White'),
    'tan': (19, 2, 'Tan'), 'dark_tan': (28, 69, 'Dark Tan'), 'orange': (25, 4, 'Orange'),
    'lime': (27, 34, 'Lime'), 'bright_green': (10, 36, 'Bright Green'),
    'reddish_brown': (70, 88, 'Reddish Brown'), 'lbg': (71, 86, 'Light Bluish Gray'),
    'dbg': (72, 85, 'Dark Bluish Gray'), 'medium_blue': (73, 42, 'Medium Blue'),
    'light_nougat': (78, 90, 'Light Nougat'), 'medium_nougat': (84, 150, 'Medium Nougat'),
    'nougat': (92, 28, 'Nougat'), 'bright_light_orange': (191, 110, 'Bright Light Orange'),
    'dark_blue': (272, 63, 'Dark Blue'), 'dark_green': (288, 80, 'Dark Green'),
    'dark_brown': (308, 120, 'Dark Brown'), 'dark_red': (320, 59, 'Dark Red'),
    'medium_azure': (322, 156, 'Medium Azure'), 'olive_green': (330, 155, 'Olive Green'),
    'sand_green': (378, 48, 'Sand Green'), 'sand_blue': (379, 55, 'Sand Blue'),
    'dark_orange': (484, 68, 'Dark Orange'), 'pearl_gold': (297, 115, 'Pearl Gold'),
    'flat_silver': (179, 95, 'Flat Silver'), 'trans_clear': (47, 12, 'Trans-Clear'),
    'trans_orange': (57, 98, 'Trans-Orange'), 'trans_red': (36, 17, 'Trans-Red'),
    'trans_yellow': (46, 19, 'Trans-Yellow'), 'trans_light_blue': (43, 15, 'Trans-Light Blue'),
    'trans_dark_blue': (33, 14, 'Trans-Dark Blue'), 'trans_neon_orange': (38, 18, 'Trans-Neon Orange'),
}
LD2NAME = {v[0]: k for k, v in COLORS.items()}

def rot_y(r):
    """LDraw rotation matrix for r quarter turns about the vertical axis."""
    a = math.radians(90 * (r % 4))
    c, s = round(math.cos(a)), round(math.sin(a))
    return np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]], dtype=float)

def rot_x(deg):
    a = math.radians(deg); c, s = math.cos(a), math.sin(a)
    return np.array([[1, 0, 0], [0, c, -s], [0, s, c]])

def rot_z(deg):
    a = math.radians(deg); c, s = math.cos(a), math.sin(a)
    return np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]])

def rot_yd(deg):
    a = math.radians(deg); c, s = math.cos(a), math.sin(a)
    return np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]])

# Per-part geometry overrides: (minx, maxx, minz, maxz, top_y, bottom_y) in local LDU
BODY = {
    '3811': (-320, 320, -320, 320, 0, 8),
    '60596': (-40, 40, -10, 10, 0, 144),
    '60623': (-40, 40, -10, 10, 0, 144),
    '60621': (-40, 40, -10, 10, 0, 144),
    '54200': (-10, 10, -10, 10, -16, 0),
    '3665a': (-10, 10, -30, 10, 0, 24),
    '3660a': (-20, 20, -30, 10, 0, 24),
    '2489': (-20, 20, -20, 20, 0, 40),
    '4739a': (-40, 40, -20, 20, 0, 24),
    '4738a': (-40, 40, -20, 20, 0, 32),
    '6064': (-20, 20, -20, 20, -32, 0),   # bush: 2x2 base
    '3470': (-20, 20, -20, 20, -8, 8),     # tree: attach 2x2 bottom (trunk base)
    '3471': (-20, 20, -20, 20, -8, 8),
    '2435': (-20, 20, -20, 20, -8, 8),
    '2417': (-50, 50, -70, 50, 0, 8),
    '2423': (-30, 30, -70, 10, 0, 8),
    '4495a': (-10, 10, -10, 10, 0, 24),
    '4495b': (-10, 10, -10, 10, 0, 24),
    '3665a': (-10, 10, -30, 10, 0, 24),
}
# parts whose bottom only connects at some cells (local cell centres). None = full footprint
BOTTOM_CELLS = {}
# parts whose underside only connects at some local cell centres (LDU)
BOTTOM_LOCAL = {
    '3665a': [(0, 0)], '3660a': [(-10, 0), (10, 0)],
    '3659': [(-30, 0), (30, 0)], '3455': [(-50, 0), (50, 0)], '6182': [(-30, 0), (30, 0)],
    '3308': [(-70, 0), (70, 0)],
}
# parts that should never be treated as a connection partner (decor)
NO_STUDS_TOP = {'3068b', '3069b', '3070b', '2431', '6636', '4162', '63864', '87079', '26603', '98138', '14769',
                '2412b', '3044b', '3043', '3048', '60481', '3185', '3633', '30055', '33303', '6005'}

class Placement:
    __slots__ = ('ld', 'color', 'M', 'pos', 'step', 'section', 'cells', 'lvl', 'h', 'top_cells', 'bottom_cells',
                 'check', 'sub', 'note', 'group')

class Model:
    def __init__(self, name, title, seed=1):
        self.name, self.title = name, title
        self.parts = []
        self.occ = {}
        self.reserved = set()
        self.step_no = 0
        self.section = 'Build'
        self.sections = []
        self.rng = random.Random(seed)
        self.submodels = {}   # name -> list of lines (for MPD)
        self.group = None

    # --- steps / sections -------------------------------------------------
    def step(self):
        if any(p.step == self.step_no for p in self.parts):
            self.step_no += 1

    def new_section(self, name):
        self.step()
        self.section = name
        self.sections.append((name, self.step_no))

    # --- geometry ------------------------------------------------------------
    def body(self, ld):
        if ld in BODY:
            return BODY[ld]
        i = ldgeom.info(ld)
        return (i['min'][0], i['max'][0], i['min'][2], i['max'][2], i['min'][1], i['max'][1])

    def footprint(self, ld, rot):
        minx, maxx, minz, maxz, top, bot = self.body(ld)
        R = rot_y(rot)
        corners = np.array([[minx, 0, minz], [maxx, 0, minz], [minx, 0, maxz], [maxx, 0, maxz]]) @ R.T
        rminx, rmaxx = corners[:, 0].min(), corners[:, 0].max()
        rminz, rmaxz = corners[:, 2].min(), corners[:, 2].max()
        w = int(round((rmaxx - rminx) / 20)); d = int(round((rmaxz - rminz) / 20))
        h = max(1, int(round((bot - top) / 8)))
        return w, d, h, rminx, rminz, top, bot, R

    def add(self, ld, color, x, z, lvl, rot=0, check=True, occupy=True, note=None, allow_overlap=False):
        w, d, h, rminx, rminz, top, bot, R = self.footprint(ld, rot)
        pos = np.array([x * 20 - rminx, -lvl * 8 - bot, z * 20 - rminz], dtype=float)
        cells = [(x + i, z + k) for i in range(w) for k in range(d)]
        if occupy:
            for (cx, cz) in cells:
                for l in range(lvl, lvl + h):
                    if (cx, cz, l) in self.occ and not allow_overlap:
                        o = self.parts[self.occ[(cx, cz, l)]]
                        raise ValueError(f'collision placing {ld} at {(x, z, lvl)} rot{rot}: cell {(cx, cz, l)} used by {o.ld} ({o.note or o.section})')
        p = Placement()
        p.ld, p.color, p.M, p.pos = ld, color, R, pos
        p.step, p.section, p.cells, p.lvl, p.h = self.step_no, self.section, cells, lvl, h
        p.check, p.sub, p.note, p.group = check, False, note, self.group
        # top studs -> grid cells
        p.top_cells = set()
        if ld not in NO_STUDS_TOP:
            for s in ldgeom.info(ld)['top_studs']:
                wp = R @ np.array(s) + pos
                if abs(wp[1] - (-(lvl + h) * 8)) < 2.5:
                    p.top_cells.add((int(math.floor(wp[0] / 20)), int(math.floor(wp[2] / 20))))
        if ld in BOTTOM_LOCAL:
            p.bottom_cells = set()
            for (lx, lz) in BOTTOM_LOCAL[ld]:
                wp = R @ np.array([lx, 0.0, lz]) + pos
                p.bottom_cells.add((int(math.floor(wp[0] / 20)), int(math.floor(wp[2] / 20))))
        else:
            p.bottom_cells = set(cells)
        idx = len(self.parts)
        self.parts.append(p)
        if occupy:
            for (cx, cz) in cells:
                for l in range(lvl, lvl + h):
                    self.occ[(cx, cz, l)] = idx
        return idx

    def add_free(self, ld, color, pos, M=np.eye(3), note=None, sub=False):
        """Decorative / sub-assembly placement with explicit LDraw transform (not grid checked)."""
        p = Placement()
        p.ld, p.color, p.M, p.pos = ld, color, np.array(M, dtype=float), np.array(pos, dtype=float)
        p.step, p.section, p.cells, p.lvl, p.h = self.step_no, self.section, [], None, 0
        p.check, p.sub, p.note, p.group = False, sub, note, self.group
        p.top_cells, p.bottom_cells = set(), set()
        self.parts.append(p)
        return len(self.parts) - 1

    def grid_pos(self, x, z, lvl):
        """LDraw coordinates of the top-left corner of cell (x,z) at level lvl."""
        return np.array([x * 20, -lvl * 8, z * 20], dtype=float)

    def free(self, x, z, lvl, w=1, d=1, h=1):
        return all((cx, cz, l) not in self.occ and (cx, cz, l) not in self.reserved
                   for cx in range(x, x + w) for cz in range(z, z + d) for l in range(lvl, lvl + h))

    def reserve(self, x, z, lvl, w=1, d=1, h=1):
        for cx in range(x, x + w):
            for cz in range(z, z + d):
                for l in range(lvl, lvl + h):
                    self.reserved.add((cx, cz, l))

    def occupy_block(self, idx, x, z, lvl, w, d, h):
        """Mark extra cells as used by an existing (free) placement."""
        for cx in range(x, x + w):
            for cz in range(z, z + d):
                for l in range(lvl, lvl + h):
                    if (cx, cz, l) in self.occ:
                        o = self.parts[self.occ[(cx, cz, l)]]
                        raise ValueError(f'collision (block) at {(cx, cz, l)} with {o.ld} {o.note or o.section}')
                    self.occ[(cx, cz, l)] = idx

    # --- validation -------------------------------------------------------
    def check_connectivity(self, extra_roots=()):
        """Every grid part must be connected to the baseplate through stud connections."""
        graph = defaultdict(set)
        by_bottom = defaultdict(list)
        for i, p in enumerate(self.parts):
            if p.lvl is None:
                continue
            for c in p.bottom_cells:
                by_bottom[(c[0], c[1], p.lvl)].append(i)
        for i, p in enumerate(self.parts):
            if p.lvl is None:
                continue
            top = p.lvl + p.h
            for c in p.top_cells:
                for j in by_bottom.get((c[0], c[1], top), []):
                    graph[i].add(j); graph[j].add(i)
        roots = [i for i, p in enumerate(self.parts) if p.ld in ('3811', '4186', '3867', '3857') or i in extra_roots]
        seen = set(roots)
        dq = deque(roots)
        while dq:
            i = dq.popleft()
            for j in graph[i]:
                if j not in seen:
                    seen.add(j); dq.append(j)
        bad = [i for i, p in enumerate(self.parts) if p.lvl is not None and p.check and i not in seen]
        return bad, graph

    # --- output -----------------------------------------------------------
    def ldraw_line(self, p):
        code = COLORS[p.color][0] if isinstance(p.color, str) else p.color
        M, pos = p.M, p.pos
        f = lambda v: ('%.3f' % v).rstrip('0').rstrip('.') if abs(v) > 1e-9 else '0'
        vals = [pos[0], pos[1], pos[2]] + [M[0, 0], M[0, 1], M[0, 2], M[1, 0], M[1, 1], M[1, 2], M[2, 0], M[2, 1], M[2, 2]]
        fn = p.ld if p.ld.endswith(('.dat', '.ldr')) else p.ld + '.dat'
        return f'1 {code} ' + ' '.join(f(v) for v in vals) + f' {fn}'

    def main_lines(self, offset=(0, 0, 0)):
        lines = [f'0 {self.title}', f'0 Name: {self.name}.ldr', '0 Author: Nobles & Common Folk at Quarrel generator',
                 '0 !LICENSE Redistributable under CCAL version 2.0 : see CAreadme.txt', '']
        order = sorted(range(len(self.parts)), key=lambda i: (self.parts[i].step, i))
        cur, steps = None, []
        sec = None
        for i in order:
            p = self.parts[i]
            if cur is not None and p.step != cur:
                lines.append('0 STEP')
            if p.section != sec:
                lines.append(f'0 // {p.section}')
                sec = p.section
            cur = p.step
            q = Placement()
            for a in Placement.__slots__:
                setattr(q, a, getattr(p, a))
            q.pos = p.pos + np.array(offset)
            lines.append(self.ldraw_line(q))
            steps.append(p.step)
        lines.append('0 STEP')
        return lines, order, steps

    def rebalance_steps(self, max_parts=28):
        """Split over-full steps into several (bottom-up, then front-to-back)."""
        from collections import defaultdict
        by = defaultdict(list)
        for i, p in enumerate(self.parts):
            by[p.step].append(i)
        new_step = {}
        cur = 0
        for s in sorted(by):
            idx = by[s]
            if len(idx) <= max_parts:
                for i in idx:
                    new_step[i] = cur
                cur += 1
                continue
            key = lambda i: ((self.parts[i].lvl if self.parts[i].lvl is not None else 999),
                             self.parts[i].pos[2], self.parts[i].pos[0])
            idx = sorted(idx, key=key)
            # keep decorations (occupy-free parts placed right after their frame) with their frame
            n = (len(idx) + max_parts - 1) // max_parts
            size = (len(idx) + n - 1) // n
            for k, i in enumerate(idx):
                new_step[i] = cur + k // size
            cur += n
        for i, p in enumerate(self.parts):
            p.step = new_step[i]
        # sections start steps
        first = {}
        for p in self.parts:
            first.setdefault(p.section, p.step)
            first[p.section] = min(first[p.section], p.step)
        self.sections = [(n, first.get(n, s)) for n, s in self.sections]

    def compact_steps(self):
        """Renumber steps 0..n-1 (skipping empty ones)."""
        used = sorted(set(p.step for p in self.parts))
        remap = {s: i for i, s in enumerate(used)}
        for p in self.parts:
            p.step = remap[p.step]
        self.sections = [(n, remap.get(s, s)) for n, s in self.sections if s in remap]


# ----------------------------------------------------------------------------
# Brick helpers
BRICK_1xN = {1: '3005', 2: '3004', 3: '3622', 4: '3010', 6: '3009', 8: '3008', 10: '6111', 12: '6112'}
PLATE_1xN = {1: '3024', 2: '3023', 3: '3623', 4: '3710', 6: '3666', 8: '3460', 10: '4477', 12: '60479'}
TILE_1xN = {1: '3070b', 2: '3069b', 3: '63864', 4: '2431', 6: '6636', 8: '4162'}
PLATES = {(1, 1): '3024', (1, 2): '3023', (1, 3): '3623', (1, 4): '3710', (1, 6): '3666', (1, 8): '3460',
          (1, 10): '4477', (1, 12): '60479',
          (2, 2): '3022', (2, 3): '3021', (2, 4): '3020', (2, 6): '3795', (2, 8): '3034', (2, 10): '3832',
          (2, 12): '2445', (2, 16): '4282', (4, 4): '3031', (4, 6): '3032', (4, 8): '3035', (4, 10): '3030',
          (4, 12): '3029', (6, 6): '3958', (6, 8): '3036', (6, 10): '3033', (6, 12): '3028', (6, 14): '3456',
          (6, 16): '3027', (8, 8): '41539', (8, 16): '92438', (16, 16): '91405'}
BRICKS = {(1, 1): '3005', (1, 2): '3004', (1, 3): '3622', (1, 4): '3010', (1, 6): '3009', (1, 8): '3008',
          (2, 2): '3003', (2, 3): '3002', (2, 4): '3001', (2, 6): '2456', (2, 8): '3007', (2, 10): '3006'}
TILES = {(1, 1): '3070b', (1, 2): '3069b', (1, 3): '63864', (1, 4): '2431', (1, 6): '6636', (1, 8): '4162',
         (2, 2): '3068b', (2, 3): '26603', (2, 4): '87079'}


def place_rect(m, table, x, z, w, d, lvl, color, **kw):
    """Place a rectangular element (w along x, d along z) from a size table."""
    a, b = min(w, d), max(w, d)
    ld = table[(a, b)]
    # parts are defined with the long side along local X; for w<d rotate 90 degrees
    rot = 0 if w >= d else 1
    return m.add(ld, color, x, z, lvl, rot, **kw)


def fill_area(m, cells, lvl, color, table=PLATES, h=1, max_len=None, prefer=None, seed_order=None, color_fn=None,
              sizes=None):
    """Greedy cover of a set of (x,z) cells with rectangular elements from `table`."""
    cells = set(cells)
    todo = sorted(cells, key=lambda c: (c[1], c[0])) if seed_order is None else seed_order
    sizes = sizes or sorted(table.keys(), key=lambda s: -s[0] * s[1])
    placed = []
    for c in todo:
        if c not in cells:
            continue
        for (a, b) in sizes:
            if max_len and b > max_len:
                continue
            done = False
            for (w, d) in ((b, a), (a, b)):
                blk = [(c[0] + i, c[1] + k) for i in range(w) for k in range(d)]
                if all(bc in cells for bc in blk) and all(m.free(bc[0], bc[1], lvl, 1, 1, h) for bc in blk):
                    col = color_fn(c) if color_fn else color
                    placed.append(place_rect(m, table, c[0], c[1], w, d, lvl, col))
                    for bc in blk:
                        cells.discard(bc)
                    done = True
                    break
            if done:
                break
        else:
            raise ValueError(f'fill_area: could not cover {c} at lvl {lvl}')
    return placed


def split_run(n, parity, lens=(4, 3, 2, 6, 1), start=None):
    """Split a run of n studs into brick lengths, offset by course parity (running bond)."""
    out = []
    if n <= 0:
        return out
    first = start if start is not None else (2 if parity % 2 else 4)
    first = min(first, n)
    if first == 5:
        first = 4
    out.append(first)
    rest = n - first
    while rest > 0:
        if rest >= 8:
            out.append(4); rest -= 4
        elif rest in (4, 3, 2, 1, 6):
            out.append(rest); rest = 0
        elif rest == 5:
            out += [3, 2]; rest = 0
        elif rest == 7:
            out += [4, 3]; rest = 0
    return out
