"""Module 1 - LIONHOLD, seat of House Aurelion (the Crimson Lions).

Light-grey stone castle on a 32x32 baseplate. Gatehouse faces east (+x),
towards Millbrook village. Moat + drawbridge on the east edge.
"""
from kit import *

WALL_H = 8          # curtain wall courses
TOWER_H = 15        # tower courses
GATE_H = 17


def build(seed=11):
    m = Model('lionhold', 'Lionhold - Castle of House Aurelion', seed=seed)
    ch = stone(m, 'lbg', 'dbg', p_alt=0.10, p_mason=0.35, dark_below=1)

    # --- 1. base ---------------------------------------------------------
    m.new_section('Baseplate, moat and courtyard paths')
    m.add('3811', 'green', 0, 0, -1, note='baseplate')
    m.step()
    # moat along the east edge: x 27..30, z 0..31
    for z in range(0, 32, 8):
        m.add('3035', 'blue', 27, z, 0, 1)
    m.step()
    # water surface: scattered tiles, leaving the bridge landing free
    for (x, z) in [(27, 1), (29, 4), (28, 8), (27, 11), (29, 20), (27, 23), (28, 27), (29, 29)]:
        m.add('3068b', 'trans_light_blue' if (x + z) % 3 else 'medium_blue', x, z, 1)
    m.step()
    # gate passage floor + courtyard path to the Great Hall
    m.add('3032', 'dark_tan', 21, 14, 0, 0)          # 6x4 under the gatehouse
    m.add('3035', 'dark_tan', 13, 14, 0, 0)          # 8x4 courtyard path
    m.add('3666', 'tan', 31, 13, 0, 1)               # road stub on the bank
    m.step()
    # a few loose stones and grass tufts in the courtyard
    for (x, z) in [(15, 4), (18, 9), (8, 24), (16, 23)]:
        m.add('3024', 'dark_tan', x, z, 0)
    m.step()

    # --- 2. gatehouse ---------------------------------------------------
    m.new_section('Gatehouse - lower level with gate passage')
    gx0, gz0, gx1, gz1 = 21, 11, 26, 20
    # gate openings (east and west faces) z 14..17
    m.reserve(gx1, 14, 1, 1, 4, 23)
    m.reserve(gx0, 14, 1, 1, 4, 23)
    for c in range(WALL_H):
        lvl = c * 3
        ring_course(m, gx0, gz0, gx1, gz1, lvl, ch)
        # passage side walls
        wall_line(m, gx0 + 1, 13, 4, 'x', lvl, ch)
        wall_line(m, gx0 + 1, 18, 4, 'x', lvl, ch)
        if c % 2 == 1:
            m.step()
    # arches over the gate openings
    m.add('3455', 'lbg', gx1, 13, 24, 1)
    m.add('3455', 'lbg', gx0, 13, 24, 1)
    ring_course(m, gx0, gz0, gx1, gz1, 24, ch)
    wall_line(m, gx0 + 1, 13, 4, 'x', 24, ch)
    wall_line(m, gx0 + 1, 18, 4, 'x', 24, ch)
    m.step()
    # ceiling of the passage / floor of the gate room
    fill_area(m, rect_cells(gx0 + 1, gz0 + 1, 4, 8), 27, 'dbg')
    m.step()
    # portcullis (black spindled fences hanging from the ceiling)
    m.add('30055', 'black', gx1 - 1, 14, 21, 1, check=False, note='portcullis')
    m.add('30055', 'black', gx1 - 1, 14, 15, 1, check=False, note='portcullis')
    m.step()

    m.new_section('Gatehouse - upper gate room and battlements')
    # windows in the gate room
    for c in range(9, GATE_H):
        lvl = c * 3
        if c == 10:
            m.add('30044', 'lbg', gx1, 14, lvl, 3); m.add('30046', 'black', gx1, 14, lvl, 3, occupy=False, check=False)
            m.add('30044', 'lbg', gx1, 16, lvl, 3); m.add('30046', 'black', gx1, 16, lvl, 3, occupy=False, check=False)
            m.add('3023', 'lbg', gx1, 14, lvl + 8, 1); m.add('3023', 'lbg', gx1, 16, lvl + 8, 1)
            m.add('30044', 'lbg', gx0, 15, lvl, 1); m.add('30046', 'black', gx0, 15, lvl, 1, occupy=False, check=False)
            m.add('3023', 'lbg', gx0, 15, lvl + 8, 1)
        ring_course(m, gx0, gz0, gx1, gz1, lvl, ch)
        if c % 2 == 0:
            m.step()
    m.step()
    top = GATE_H * 3
    # roof floor with a hatch
    cells = set(rect_cells(gx0, gz0, 6, 10))
    fill_area(m, cells, top, 'dbg')
    m.step()
    battlement_ring(m, gx0, gz0, gx1, gz1, top + 1, 'lbg')
    m.step()
    flagpole(m, gx1 - 1, gz0 + 1, top + 1, 'red', poles=2, rot=1)
    flagpole(m, gx1 - 1, gz1 - 1, top + 1, 'red', poles=2, rot=1)
    m.step()

    # --- 3. towers ------------------------------------------------------
    specs = [
        ('South-east tower', 21, 1, 'battlement', TOWER_H, [('s', 2, 4), ('s', 3, 10), ('e', 2, 4), ('e', 3, 10)], [('n', 2, 5, 'lbg')]),
        ('North-east tower', 21, 25, 'battlement', TOWER_H, [('n', 3, 4), ('n', 2, 10), ('e', 3, 4), ('e', 2, 10)], [('s', 2, 5, 'lbg')]),
        ('South-west tower', 1, 1, 'pyramid', TOWER_H + 3, [('s', 2, 4), ('w', 2, 4)], [('s', 2, 11, 'lbg'), ('w', 2, 11, 'lbg'), ('e', 2, 11, 'lbg')]),
        ('North-west tower', 1, 25, 'pyramid', TOWER_H + 3, [('n', 3, 4), ('w', 3, 4)], [('n', 2, 11, 'lbg'), ('w', 2, 11, 'lbg'), ('e', 2, 11, 'lbg')]),
    ]
    for name, x0, z0, top_kind, h, slits, wins in specs:
        m.new_section(name)
        tower(m, x0, z0, 6, h, ch, top=top_kind, top_color='lbg', roof_color='red', slits=slits,
              windows=wins, floor_color='dbg', flag='red' if top_kind == 'pyramid' else 'yellow')

    # --- 4. curtain walls with wall-walks --------------------------------
    walls = [
        ('South curtain wall', 7, 1, 14, 'x', 'out-z'),
        ('North curtain wall', 7, 30, 14, 'x', 'out+z'),
        ('West curtain wall', 1, 7, 18, 'z', 'out-x'),
        ('East curtain walls', 26, 7, 4, 'z', 'out+x'),
        (None, 26, 21, 4, 'z', 'out+x'),
    ]
    for name, x, z, n, axis, out in walls:
        if name:
            m.new_section(name)
        # arrow slits every 4 studs in courses 3-4
        for i in range(n // 2 - 4 if n > 8 else 1, n, 4 if n > 8 else 2):
            if 0 < i < n - 1:
                cx, cz = (x + i, z) if axis == 'x' else (x, z + i)
                m.reserve(cx, cz, 12, 1, 1, 6)
        for c in range(WALL_H):
            wall_line(m, x, z, n, axis, c * 3, ch, parity=c)
            if c % 3 == 2:
                m.step()
        m.step()
        # wall-walk: 2 wide, inner row overhangs the courtyard
        inner = {'out-z': (0, 1), 'out+z': (0, -1), 'out-x': (1, 0), 'out+x': (-1, 0)}[out]
        cells = []
        for i in range(n):
            cx, cz = (x + i, z) if axis == 'x' else (x, z + i)
            cells += [(cx, cz), (cx + inner[0], cz + inner[1])]
        fill_area(m, cells, WALL_H * 3, 'dbg')
        m.step()
        merlons_line(m, x, z, n, axis, WALL_H * 3 + 1, 'lbg', pattern=(2, 1))
        m.step()

    # --- 5. great hall ---------------------------------------------------
    m.new_section('Great Hall - walls')
    hx0, hz0, hx1, hz1 = 3, 10, 12, 21
    hall = stone(m, 'lbg', 'dbg', p_alt=0.08, p_mason=0.25, dark_below=1)
    # main entrance: open archway on the east side (z 14..17)
    m.reserve(hx1, 14, 0, 1, 4, 15)
    m.add('3455', 'lbg', hx1, 13, 15, 1)
    # lattice windows
    for (face_x, z) in [(hx1, 11), (hx1, 19), (hx0, 11), (hx0, 15), (hx0, 19)]:
        rot = 3 if face_x == hx1 else 1
        m.add('30044', 'white', face_x, z, 6, rot); m.add('30046', 'black', face_x, z, 6, rot, occupy=False, check=False)
        m.add('3023', 'white', face_x, z, 14, 1)
    for x in (5, 9):
        m.add('30044', 'white', x, hz0, 6, 0); m.add('30046', 'black', x, hz0, 6, 0, occupy=False, check=False)
        m.add('3023', 'white', x, hz0, 14, 0)
        m.add('30044', 'white', x, hz1, 6, 2); m.add('30046', 'black', x, hz1, 6, 2, occupy=False, check=False)
        m.add('3023', 'white', x, hz1, 14, 0)
    for c in range(WALL_H):
        ring_course(m, hx0, hz0, hx1, hz1, c * 3, hall)
        if c % 2 == 1:
            m.step()
    # interior: throne dais and long table
    m.add('3035', 'red', 4, 13, 0, 1)                   # carpet 4x8 along x? -> 8 long in z
    m.step()
    m.new_section('Great Hall - roof')
    # tie beams (plates across the top so the roof sits on a solid rim)
    plate_ring(m, hx0, hz0, hx1, hz1, WALL_H * 3, 'dbg', width=1)
    m.step()
    gable_roof(m, hx0, hz0, hz1 - hz0 + 1, hx1 - hx0 + 1, WALL_H * 3 + 1, 'red', ridge_axis='z',
               gable_chooser=solid('lbg'), ridge_color='dark_red')
    m.step()

    # --- 6. courtyard details --------------------------------------------
    m.new_section('Stable lean-to and courtyard details')
    # stable against the north wall: back wall z=28, posts z=25, flat plank roof
    for c in range(5):
        wall_line(m, 9, 28, 10, 'x', c * 3, solid('reddish_brown') if c else solid('dbg'), parity=c)
    for x in (9, 13, 18):
        for c in range(5):
            m.add('3062b', 'reddish_brown', x, 25, c * 3)
    m.step()
    m.add('3030', 'reddish_brown', 9, 25, 15, 0)
    m.step()
    # hay and barrels in the stable
    m.add('3003', 'tan', 10, 26, 0); m.add('3022', 'yellow', 10, 26, 3)
    m.add('2489', 'reddish_brown', 15, 26, 0, check=False)
    m.step()
    # drawbridge across the moat (lowered)
    m.add('3031', 'reddish_brown', 27, 14, 1, note='drawbridge')
    for x in range(27, 31):
        m.add('2431', 'reddish_brown' if x % 2 else 'dark_brown', x, 14, 2, 1)
    m.step()
    return m


if __name__ == '__main__':
    import json, sys
    m = build()
    bad, _ = m.check_connectivity()
    print('parts', len(m.parts), 'unconnected', len(bad))
    for i in bad[:30]:
        p = m.parts[i]
        print('  ', p.ld, p.color, p.cells[:2], p.lvl, p.section)
