"""Reusable building techniques: walls, towers, battlements, roofs, floors."""
from lego import *

MASONRY = '98283'   # Brick 1 x 2 with masonry profile
MASONRY_OK = {'lbg', 'dbg', 'tan', 'dark_tan', 'white', 'reddish_brown'}


def stone(m, main='lbg', alt='dbg', p_alt=0.12, p_mason=0.35, dark_below=0):
    """Returns a brick chooser for textured stone walls."""
    def choose(n, x, z, lvl):
        col = main
        r = m.rng.random()
        if lvl < dark_below * 3:
            col = alt if r < 0.55 else main
        elif r < p_alt:
            col = alt
        ld = BRICK_1xN[n]
        if n == 2 and m.rng.random() < p_mason and col in MASONRY_OK:
            ld = MASONRY
        return ld, col
    return choose


def solid(color):
    def choose(n, x, z, lvl):
        return BRICK_1xN[n], color
    return choose


def segments(m, cells, lvl, h=3):
    """Split an ordered list of cells into maximal runs of free cells."""
    segs, cur = [], []
    for c in cells:
        if m.free(c[0], c[1], lvl, 1, 1, h):
            cur.append(c)
        else:
            if cur:
                segs.append(cur)
            cur = []
    if cur:
        segs.append(cur)
    return segs


def wall_line(m, x, z, n, axis, lvl, chooser, parity=None, h=3, start=None):
    """Fill a straight 1-stud wall course (bricks, h=3) or plate course (h=1)."""
    cells = [(x + i, z) if axis == 'x' else (x, z + i) for i in range(n)]
    parity = (lvl // 3) if parity is None else parity
    out = []
    for seg in segments(m, cells, lvl, h):
        for L, c0 in _lay(seg, parity, start):
            ld, col = chooser(L, c0[0], c0[1], lvl)
            if h == 1:
                ld = PLATE_1xN[L]
            rot = 0 if axis == 'x' else 1
            out.append(m.add(ld, col, c0[0], c0[1], lvl, rot))
    return out


def _lay(seg, parity, start=None):
    lens = split_run(len(seg), parity, start=start)
    i = 0
    res = []
    for L in lens:
        res.append((L, seg[i]))
        i += L
    return res


def ring_course(m, x0, z0, x1, z1, lvl, chooser, parity=None, h=3):
    """One course of a hollow rectangular 1-stud wall ring (x0..x1, z0..z1 inclusive) with interlocked corners."""
    c = (lvl // 3) if parity is None else parity
    out = []
    if c % 2 == 0:
        out += wall_line(m, x0, z0, x1 - x0 + 1, 'x', lvl, chooser, c, h)
        out += wall_line(m, x0, z1, x1 - x0 + 1, 'x', lvl, chooser, c + 1, h)
        out += wall_line(m, x0, z0 + 1, z1 - z0 - 1, 'z', lvl, chooser, c, h)
        out += wall_line(m, x1, z0 + 1, z1 - z0 - 1, 'z', lvl, chooser, c + 1, h)
    else:
        out += wall_line(m, x0, z0, z1 - z0 + 1, 'z', lvl, chooser, c, h)
        out += wall_line(m, x1, z0, z1 - z0 + 1, 'z', lvl, chooser, c + 1, h)
        out += wall_line(m, x0 + 1, z0, x1 - x0 - 1, 'x', lvl, chooser, c, h)
        out += wall_line(m, x0 + 1, z1, x1 - x0 - 1, 'x', lvl, chooser, c + 1, h)
    return out


def perimeter(x0, z0, x1, z1):
    """Ordered perimeter cells of a rectangle, clockwise from (x0,z0)."""
    cells = [(x, z0) for x in range(x0, x1 + 1)]
    cells += [(x1, z) for z in range(z0 + 1, z1 + 1)]
    cells += [(x, z1) for x in range(x1 - 1, x0 - 1, -1)]
    cells += [(x0, z) for z in range(z1 - 1, z0, -1)]
    return cells


def merlons_line(m, x, z, n, axis, lvl, color, cap='3070b', pattern=(1, 1)):
    """Battlement merlons along a line: `pattern` = (merlon length, gap)."""
    ml, gap = pattern
    i = 0
    out = []
    while i < n:
        L = min(ml, n - i)
        cx, cz = (x + i, z) if axis == 'x' else (x, z + i)
        if m.free(cx, cz, lvl, *(L, 1) if axis == 'x' else (1, L), 3):
            rot = 0 if axis == 'x' else 1
            out.append(m.add(BRICK_1xN[L], color, cx, cz, lvl, rot))
            if cap:
                out.append(m.add(TILE_1xN[L], color, cx, cz, lvl + 3, rot))
        i += L + gap
    return out


def battlement_ring(m, x0, z0, x1, z1, lvl, color, cap=True):
    """Merlons on a rectangular ring: corner merlons are 1x1 bricks, then alternating gaps."""
    out = []
    corners = [(x0, z0), (x1, z0), (x0, z1), (x1, z1)]
    for (cx, cz) in corners:
        out.append(m.add('3005', color, cx, cz, lvl))
        if cap:
            out.append(m.add('3070b', color, cx, cz, lvl + 3))
    # sides: pattern gap, merlon(1), gap, ...
    for (x, z, n, axis) in [(x0 + 1, z0, x1 - x0 - 1, 'x'), (x0 + 1, z1, x1 - x0 - 1, 'x'),
                            (x0, z0 + 1, z1 - z0 - 1, 'z'), (x1, z0 + 1, z1 - z0 - 1, 'z')]:
        # symmetric merlons: place at odd offsets
        for i in range(n):
            if i % 2 == 1 and i != n - 1 or (n % 2 == 1 and i == n // 2 and n > 2):
                cx, cz = (x + i, z) if axis == 'x' else (x, z + i)
                if m.free(cx, cz, lvl, 1, 1, 3):
                    out.append(m.add('3005', color, cx, cz, lvl))
                    if cap:
                        out.append(m.add('3070b', color, cx, cz, lvl + 3))
    return out


def plate_ring(m, x0, z0, x1, z1, lvl, color, width=1):
    """Ring of plates (e.g. walkway) of given width inside x0..x1/z0..z1."""
    cells = set()
    for x in range(x0, x1 + 1):
        for z in range(z0, z1 + 1):
            if x < x0 + width or x > x1 - width or z < z0 + width or z > z1 - width:
                cells.add((x, z))
    return fill_area(m, cells, lvl, color, max_len=8)


def rect_cells(x0, z0, w, d):
    return [(x, z) for x in range(x0, x0 + w) for z in range(z0, z0 + d)]


# ---------------------------------------------------------------------------
# Roofs
SLOPE45 = {1: '3040b', 2: '3039', 3: '3038', 4: '3037'}


def slope_row(m, x, z, n, axis, lvl, color, facing):
    """Row of 45° 2-deep slopes; `facing` is the direction the slope surface descends toward.
    axis x: the row runs along x; facing '-z' or '+z'. axis z: facing '-x' or '+x'."""
    # local: slope descends toward -Z, stud row at z=0..; footprint 2 deep
    rot = {'-z': 0, '-x': 1, '+z': 2, '+x': 3}[facing]
    out = []
    i = 0
    lens = split_run(n, 0, start=4)
    for L in lens:
        while L > 0:
            k = min(L, 4)
            cx, cz = (x + i, z) if axis == 'x' else (x, z + i)
            out.append(m.add(SLOPE45[k], color, cx, cz, lvl, rot))
            i += k; L -= k
    return out


def gable_roof(m, x0, z0, length, width, lvl, color, ridge_axis='x', gable_chooser=None, ridge_color=None,
               gable_color=None):
    """Pitched 45° roof. Footprint: length along ridge axis, width across (even).
    Returns list of indices. Gable ends are filled with bricks from gable_chooser."""
    out = []
    layers = width // 2 - 1
    for k in range(layers):
        L = lvl + 3 * k
        if ridge_axis == 'x':
            out += slope_row(m, x0, z0 + k, length, 'x', L, color, '-z')
            out += slope_row(m, x0, z0 + width - 2 - k, length, 'x', L, color, '+z')
            inner = width - 4 - 2 * k
            if inner > 0 and gable_chooser:
                for gx in (x0, x0 + length - 1):
                    out += wall_line(m, gx, z0 + k + 2, inner, 'z', L, gable_chooser)
        else:
            out += slope_row(m, x0 + k, z0, length, 'z', L, color, '-x')
            out += slope_row(m, x0 + width - 2 - k, z0, length, 'z', L, color, '+x')
            inner = width - 4 - 2 * k
            if inner > 0 and gable_chooser:
                for gz in (z0, z0 + length - 1):
                    out += wall_line(m, x0 + k + 2, gz, inner, 'x', L, gable_chooser)
        m.step()
    # ridge
    L = lvl + 3 * layers
    rc = ridge_color or color
    if ridge_axis == 'x':
        z = z0 + layers
        i = 0
        while i < length:
            if length - i >= 2:
                out.append(m.add('3043', rc, x0 + i, z, L, 0)); i += 2
            else:
                out.append(m.add('3044b', rc, x0 + i, z, L, 0)); i += 1
    else:
        x = x0 + layers
        i = 0
        while i < length:
            if length - i >= 2:
                out.append(m.add('3043', rc, x, z0 + i, L, 1)); i += 2
            else:
                out.append(m.add('3044b', rc, x, z0 + i, L, 1)); i += 1
    return out


# ---------------------------------------------------------------------------
# Towers
def corner_rot(outx, outz):
    """Rotation for 3045 (double convex) so that its slopes face outward (outx,outz in {-1,1})."""
    return {(1, -1): 0, (-1, -1): 1, (-1, 1): 2, (1, 1): 3}[(outx, outz)]


def pyramid_roof(m, x0, z0, size, lvl, color, top='3688', top_color=None):
    """Hollow pyramid roof of 45° slopes on a size x size square (size even)."""
    out = []
    k = 0
    while size - 2 * k >= 4:
        a0, b0 = x0 + k, z0 + k
        a1, b1 = x0 + size - 1 - k, z0 + size - 1 - k
        L = lvl + 3 * k
        out.append(m.add('3045', color, a1 - 1, b0, L, corner_rot(1, -1)))
        out.append(m.add('3045', color, a0, b0, L, corner_rot(-1, -1)))
        out.append(m.add('3045', color, a0, b1 - 1, L, corner_rot(-1, 1)))
        out.append(m.add('3045', color, a1 - 1, b1 - 1, L, corner_rot(1, 1)))
        side = size - 2 * k - 4
        if side > 0:
            out += slope_row(m, a0 + 2, b0, side, 'x', L, color, '-z')
            out += slope_row(m, a0 + 2, b1 - 1, side, 'x', L, color, '+z')
            out += slope_row(m, a0, b0 + 2, side, 'z', L, color, '-x')
            out += slope_row(m, a1 - 1, b0 + 2, side, 'z', L, color, '+x')
        m.step()
        k += 1
    L = lvl + 3 * k
    c = x0 + size // 2 - 1, z0 + size // 2 - 1
    if top:
        out.append(m.add(top, top_color or color, c[0], c[1], L))
    return out, L


def tower(m, x0, z0, size, courses, chooser, top='battlement', top_color='lbg', roof_color='red',
          slits=(), windows=(), corbels=True, floor_color='dbg', flag=None, steps_per=2, reserve=()):
    """Square hollow tower with 1-stud walls. `slits`: list of (face, offset, course).
    `windows`: list of (face, offset, course, frame_color). Returns top level."""
    x1, z1 = x0 + size - 1, z0 + size - 1

    def face_cell(face, off):
        return {'s': (x0 + off, z0), 'n': (x0 + off, z1), 'w': (x0, z0 + off), 'e': (x1, z0 + off)}[face]

    for (face, off, c) in slits:
        cx, cz = face_cell(face, off)
        m.reserve(cx, cz, c * 3, 1, 1, 6)
    for (x, z, l, w, d, h) in reserve:
        m.reserve(x, z, l, w, d, h)
    for (face, off, c, col) in windows:
        cx, cz = face_cell(face, off)
        rot = 0 if face in 's' else (2 if face == 'n' else (3 if face == 'e' else 1))
        if face in 'sn':
            m.add('30044', col, cx, cz, c * 3, 0 if face == 's' else 2)
            m.add('30046', 'black', cx, cz, c * 3, 0 if face == 's' else 2, occupy=False, check=False)
            m.add('3023', col, cx, cz, c * 3 + 8, 0)
        else:
            m.add('30044', col, cx, cz, c * 3, 1 if face == 'w' else 3)
            m.add('30046', 'black', cx, cz, c * 3, 1 if face == 'w' else 3, occupy=False, check=False)
            m.add('3023', col, cx, cz, c * 3 + 8, 1)
    for c in range(courses):
        lvl = c * 3
        if corbels and c == courses - 1 and top in ('battlement', 'pyramid', 'spire'):
            # corbels: inverted slopes sticking out on every other stud of each face
            for i in range(1, size - 1):
                if i % 2 == 1:
                    for face, (cx, cz), rot in (('s', (x0 + i, z0 - 1), 0), ('n', (x0 + i, z1), 2),
                                                ('w', (x0 - 1, z0 + i), 1), ('e', (x1, z0 + i), 3)):
                        m.add('3665a', top_color if top_color != 'none' else 'lbg', cx, cz, lvl, rot)
        ring_course(m, x0, z0, x1, z1, lvl, chooser)
        if (c + 1) % steps_per == 0:
            m.step()
    m.step()
    lvl = courses * 3
    if top in ('battlement', 'pyramid', 'spire'):
        big = PLATES.get((size + 2, size + 2))
        if big:
            m.add(big, floor_color, x0 - 1, z0 - 1, lvl)
        else:
            fill_area(m, rect_cells(x0 - 1, z0 - 1, size + 2, size + 2), lvl, floor_color)
        m.step()
        if top == 'battlement':
            battlement_ring(m, x0 - 1, z0 - 1, x1 + 1, z1 + 1, lvl + 1, top_color)
            m.step()
            if flag:
                c = (x0 + size // 2 - 1, z0 + size // 2 - 1)
                flagpole(m, c[0], c[1], lvl + 1, flag, poles=3)
            return lvl + 5
        else:
            out, L = pyramid_roof(m, x0 - 1, z0 - 1, size + 2, lvl + 1, roof_color)
            if flag:
                # the spire has a single centred stud -> pole sits half a stud off-grid
                cx, cz = (x0 + size // 2 - 1) * 20 + 20, (z0 + size // 2 - 1) * 20 + 20
                flag_free(m, cx, cz, L + 6, flag)
            m.step()
            return L + 6
    return lvl


def flagpole(m, x, z, lvl, color, poles=2, pole_color='reddish_brown', wave='4495b', rot=0):
    """Pole of 1x1 round bricks with a waving 4x1 flag and a cone on top."""
    for i in range(poles):
        m.add('3062b', pole_color, x, z, lvl + 3 * i)
    L = lvl + 3 * poles
    m.add(wave, color, x, z, L, rot)
    m.add('4589', 'pearl_gold', x, z, L + 3)
    return L + 6




def flag_free(m, cx, cz, lvl, color, pole_color='reddish_brown', rot=0, poles=1):
    """Flag pole on a centred stud (LDU centre cx,cz)."""
    y = -lvl * 8
    for i in range(poles):
        m.add_free('3062b', pole_color, [cx, y - 24 * (i + 1), cz])
    y -= 24 * poles
    m.add_free('4495b', color, [cx, y - 24, cz], rot_y(rot))
    m.add_free('4589', 'pearl_gold', [cx, y - 48, cz])


def stone_mix(m, weights, p_mason=0.35, base_weights=None, base_courses=1):
    """Stone chooser with weighted colours, e.g. {'dbg': .8, 'lbg': .1, 'black': .1}."""
    def pick(w):
        r = m.rng.random() * sum(w.values())
        for k, v in w.items():
            r -= v
            if r <= 0:
                return k
        return k
    def choose(n, x, z, lvl):
        w = base_weights if (base_weights and lvl < base_courses * 3) else weights
        col = pick(w)
        ld = BRICK_1xN[n]
        if n == 2 and m.rng.random() < p_mason and col in MASONRY_OK:
            ld = MASONRY
        return ld, col
    return choose


def talus_ring(m, x0, z0, size, lvl, color, skip=()):
    """Sloped plinth ring (2-deep 45° slopes facing out) around a size x size square.
    Returns the inner square origin (x0+1, z0+1) of size-2 whose ring sits on the slope studs."""
    x1, z1 = x0 + size - 1, z0 + size - 1
    m.add('3045', color, x1 - 1, z0, lvl, corner_rot(1, -1))
    m.add('3045', color, x0, z0, lvl, corner_rot(-1, -1))
    m.add('3045', color, x0, z1 - 1, lvl, corner_rot(-1, 1))
    m.add('3045', color, x1 - 1, z1 - 1, lvl, corner_rot(1, 1))
    for (x, z, n, axis, facing) in [(x0 + 2, z0, size - 4, 'x', '-z'), (x0 + 2, z1 - 1, size - 4, 'x', '+z'),
                                    (x0, z0 + 2, size - 4, 'z', '-x'), (x1 - 1, z0 + 2, size - 4, 'z', '+x')]:
        i = 0
        while i < n:
            cx, cz = (x + i, z) if axis == 'x' else (x, z + i)
            if (cx, cz) in skip:
                i += 1
                continue
            # longest run of non-skipped cells up to 4
            k = 0
            while k < 4 and i + k < n and ((x + i + k, z) if axis == 'x' else (x, z + i + k)) not in skip:
                k += 1
            k = 3 if k == 3 else (4 if k == 4 else k)
            rot = {'-z': 0, '-x': 1, '+z': 2, '+x': 3}[facing]
            m.add(SLOPE45[k], color, cx, cz, lvl, rot)
            i += k


def spire_turret(m, x, z, lvl, n_round, color='dbg', roof='dark_blue', flag=None):
    """Pepper-pot turret: stack of 2x2 round bricks topped by a 75° spire."""
    for i in range(n_round):
        m.add('3941', color, x, z, lvl + 3 * i)
    L = lvl + 3 * n_round
    m.add('3688', roof, x, z, L)
    if flag:
        flag_free(m, x * 20 + 20, z * 20 + 20, L + 6, flag, rot=0)
    return L + 6


# ---------------------------------------------------------------------------
# Village buildings
def timber_house(m, x0, z0, L, W, name, ground=None, g=6, u=3, frame='dark_brown', fill='white',
                 roof='reddish_brown', ridge=None, door_x=None, door_color='reddish_brown',
                 ground_windows=(), upper_windows=(), window_frame='reddish_brown', jetty=True,
                 back_windows=(), chimney=None, gable_fill=None):
    """Two-storey medieval house facing south (-z). Ground floor stone/logs, upper floor timber-framed.
    W must be odd when jetty=True (roof width W+3 must be even)."""
    x1, z1 = x0 + L - 1, z0 + W - 1
    ground = ground or stone_mix(m, {'tan': 0.55, 'dark_tan': 0.25, 'lbg': 0.2}, p_mason=0.45)
    m.new_section(f'{name} - ground floor')
    if door_x is not None:
        m.add('60596', door_color, door_x, z0, 0, 0)
        m.add('60616a', door_color, door_x, z0, 0, 0, occupy=False, check=False)
    for x in ground_windows:
        m.add('60592', window_frame, x, z0, 6, 0)
        m.add('60601', 'trans_clear', x, z0, 6, 0, occupy=False, check=False)
    for x in back_windows:
        m.add('60592', window_frame, x, z1, 6, 2)
        m.add('60601', 'trans_clear', x, z1, 6, 2, occupy=False, check=False)
    for c in range(g):
        ring_course(m, x0, z0, x1, z1, c * 3, ground)
        if c % 2 == 1:
            m.step()
    m.step()
    m.new_section(f'{name} - timber-framed upper floor')
    uz0 = z0 - 1 if jetty else z0
    F = g * 3
    fill_area(m, rect_cells(x0, uz0, L, z1 - uz0 + 1), F, 'reddish_brown')
    m.step()
    posts = set()
    for x in range(x0, x1 + 1):
        if (x - x0) % 3 == 0 or x == x1:
            posts.add((x, uz0)); posts.add((x, z1))
    for z in range(uz0, z1 + 1):
        if (z - uz0) % 3 == 0 or z == z1:
            posts.add((x0, z)); posts.add((x1, z))
    for x in upper_windows:
        m.add('60592', 'white' if fill != 'white' else window_frame, x, uz0, F + 1, 0)
        m.add('60601', 'trans_clear', x, uz0, F + 1, 0, occupy=False, check=False)
        posts.discard((x, uz0)); posts.discard((x + 1, uz0))
    fillch = solid(fill)
    for c in range(u):
        lvl = F + 1 + 3 * c
        for (px, pz) in sorted(posts):
            if m.free(px, pz, lvl, 1, 1, 3):
                m.add('3005', frame, px, pz, lvl)
        ring_course(m, x0, uz0, x1, z1, lvl, fillch)
        m.step()
    top = F + 1 + 3 * u
    plate_ring(m, x0, uz0, x1, z1, top, frame, width=1)
    m.step()
    m.new_section(f'{name} - roof')
    rz0 = uz0 - 1
    width = z1 - rz0 + 2
    gable_roof(m, x0, rz0, L, width, top + 1, roof, ridge_axis='x', gable_chooser=solid(gable_fill or fill),
               ridge_color=ridge or roof)
    m.step()
    if chimney:
        cx, cz = chimney
        # chimney rises through the roof at the back
        pass
    return top


def posts(m, cells, lvl, n, color='reddish_brown', part='3062b'):
    for (x, z) in cells:
        for i in range(n):
            m.add(part, color, x, z, lvl + 3 * i)
