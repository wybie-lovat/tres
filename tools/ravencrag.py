"""Module 4 - RAVENCRAG KEEP, stronghold of House Corvane (the Black Ravens).

Dark-grey stone fortress on a 32x32 baseplate. The gatehouse faces west (-x)
towards Millbrook village. A tall donjon on a sloped plinth dominates the
north-east corner; pepper-pot turrets with dark blue spires.
"""
from kit import *

WALL_H = 9


def build(seed=23):
    m = Model('ravencrag', 'Ravencrag Keep - Stronghold of House Corvane', seed=seed)
    ch = stone_mix(m, {'dbg': 0.80, 'black': 0.08, 'lbg': 0.08, 'sand_green': 0.04},
                   base_weights={'dbg': 0.5, 'black': 0.3, 'sand_green': 0.2}, base_courses=1)

    # --- 1. base ---------------------------------------------------------
    m.new_section('Baseplate, moat and courtyard paths')
    m.add('3811', 'green', 0, 0, -1, note='baseplate')
    m.step()
    for z in range(0, 32, 8):
        m.add('3035', 'blue', 1, z, 0, 1)
    m.step()
    for (x, z) in [(1, 2), (3, 6), (2, 9), (1, 21), (3, 24), (2, 28)]:
        m.add('3068b', 'trans_light_blue' if (x + z) % 3 else 'medium_blue', x, z, 1)
    m.add('3666', 'tan', 0, 13, 0, 1)                 # road stub on the bank
    m.step()
    m.add('3032', 'dark_tan', 5, 14, 0, 0)            # gate passage floor 6x4
    m.add('3035', 'dark_tan', 11, 14, 0, 0)           # courtyard path 8x4
    m.add('3020', 'dark_tan', 19, 16, 0, 0)
    m.step()

    # --- 2. gatehouse -----------------------------------------------------
    m.new_section('Gatehouse - lower level with gate passage')
    gx0, gz0, gx1, gz1 = 5, 11, 10, 20
    m.reserve(gx0, 14, 1, 1, 4, 23)
    m.reserve(gx1, 14, 1, 1, 4, 23)
    for c in range(8):
        lvl = c * 3
        ring_course(m, gx0, gz0, gx1, gz1, lvl, ch)
        wall_line(m, gx0 + 1, 13, 4, 'x', lvl, ch)
        wall_line(m, gx0 + 1, 18, 4, 'x', lvl, ch)
        if c % 2 == 1:
            m.step()
    m.add('3455', 'dbg', gx0, 13, 24, 1)
    m.add('3455', 'dbg', gx1, 13, 24, 1)
    ring_course(m, gx0, gz0, gx1, gz1, 24, ch)
    wall_line(m, gx0 + 1, 13, 4, 'x', 24, ch)
    wall_line(m, gx0 + 1, 18, 4, 'x', 24, ch)
    m.step()
    fill_area(m, rect_cells(gx0 + 1, gz0 + 1, 4, 8), 27, 'black')
    m.step()
    m.add('30055', 'black', gx0 + 1, 14, 21, 1, check=False, note='portcullis')
    m.add('30055', 'black', gx0 + 1, 14, 15, 1, check=False, note='portcullis')
    m.step()

    m.new_section('Gatehouse - upper level, turrets and spires')
    GH = 16
    for c in range(9, GH):
        lvl = c * 3
        if c == 10:
            for z in (14, 16):
                m.add('30044', 'dbg', gx0, z, lvl, 1); m.add('30046', 'black', gx0, z, lvl, 1, occupy=False, check=False)
                m.add('3023', 'dbg', gx0, z, lvl + 8, 1)
        ring_course(m, gx0, gz0, gx1, gz1, lvl, ch)
        if c % 2 == 0:
            m.step()
    m.step()
    top = GH * 3
    fill_area(m, rect_cells(gx0, gz0, 6, 10), top, 'black')
    m.step()
    # merlons between the two front turrets
    merlons_line(m, gx0 + 2, gz0, 4, 'x', top + 1, 'dbg', pattern=(1, 1))
    merlons_line(m, gx0 + 2, gz1, 4, 'x', top + 1, 'dbg', pattern=(1, 1))
    merlons_line(m, gx1, gz0 + 1, 8, 'z', top + 1, 'dbg', pattern=(1, 1))
    merlons_line(m, gx0, gz0 + 2, 6, 'z', top + 1, 'dbg', pattern=(1, 1))
    m.step()
    spire_turret(m, gx0, gz0, top + 1, 3, flag='dark_blue')
    spire_turret(m, gx0, gz1 - 1, top + 1, 3, flag='dark_blue')
    m.step()

    # --- 3. the great keep (donjon) on a sloped plinth ---------------------
    m.new_section('Great Keep - sloped plinth and entrance')
    kx0, kz0 = 22, 22               # keep 8x8 at 22..29
    door_cells = {(21, z) for z in range(24, 28)}
    talus_ring(m, kx0 - 1, kz0 - 1, 10, 0, 'dbg', skip=door_cells)
    m.add('3001', 'dbg', 21, 24, 0, 1)            # landing in front of the door (2x4)
    m.step()
    # door on the west face, raised above the plinth
    m.add('60596', 'black', kx0, 24, 3, 1)
    m.add('60616a', 'dark_brown', kx0, 24, 3, 1, occupy=False, check=False)
    # steps up to the landing
    m.add('3710', 'dbg', 19, 24, 0, 1); m.add('3710', 'dbg', 20, 24, 0, 1); m.add('3710', 'dbg', 20, 24, 1, 1)
    m.step()
    m.new_section('Great Keep - walls')
    KH = 18
    kch = stone_mix(m, {'dbg': 0.82, 'black': 0.09, 'lbg': 0.09}, p_mason=0.4)
    slits = [(kx0 + 7, kz0 + 3, 12), (kx0 + 3, kz0 + 7, 12), (kx0 + 4, kz0, 21), (kx0 + 7, kz0 + 4, 30)]
    for (x, z, l) in slits:
        m.reserve(x, z, l, 1, 1, 6)
    wins = [('s', kx0 + 2, 30), ('s', kx0 + 5, 30), ('w', kz0 + 2, 36), ('w', kz0 + 5, 36), ('s', kx0 + 3, 45),
            ('w', kz0 + 3, 45), ('n', kx0 + 3, 45), ('e', kz0 + 3, 45)]
    for (face, off, l) in wins:
        if face == 's':
            m.add('30044', 'black', off, kz0, l, 0); m.add('30046', 'black', off, kz0, l, 0, occupy=False, check=False)
            m.add('3023', 'dbg', off, kz0, l + 8, 0)
        elif face == 'n':
            m.add('30044', 'black', off, kz0 + 7, l, 2); m.add('30046', 'black', off, kz0 + 7, l, 2, occupy=False, check=False)
            m.add('3023', 'dbg', off, kz0 + 7, l + 8, 0)
        elif face == 'w':
            m.add('30044', 'black', kx0, off, l, 1); m.add('30046', 'black', kx0, off, l, 1, occupy=False, check=False)
            m.add('3023', 'dbg', kx0, off, l + 8, 1)
        else:
            m.add('30044', 'black', kx0 + 7, off, l, 3); m.add('30046', 'black', kx0 + 7, off, l, 3, occupy=False, check=False)
            m.add('3023', 'dbg', kx0 + 7, off, l + 8, 1)
    for c in range(1, KH + 1):
        lvl = c * 3
        if c == KH:
            for i in range(1, 7, 2):
                m.add('3665a', 'dbg', kx0 + i, kz0 - 1, lvl, 0)
                m.add('3665a', 'dbg', kx0 + i, kz0 + 7, lvl, 2)
                m.add('3665a', 'dbg', kx0 - 1, kz0 + i, lvl, 1)
                m.add('3665a', 'dbg', kx0 + 7, kz0 + i, lvl, 3)
        ring_course(m, kx0, kz0, kx0 + 7, kz0 + 7, lvl, kch)
        if c % 2 == 0:
            m.step()
    m.step()
    m.new_section('Great Keep - roof and spire')
    L = (KH + 1) * 3
    fill_area(m, rect_cells(kx0 - 1, kz0 - 1, 10, 10), L, 'black')
    m.step()
    out, Lt = pyramid_roof(m, kx0 - 1, kz0 - 1, 10, L + 1, 'dark_blue')
    flag_free(m, (kx0 + 3) * 20 + 20, (kz0 + 3) * 20 + 20, Lt + 6, 'dark_blue', poles=2)
    m.step()

    # --- 4. towers ----------------------------------------------------------
    m.new_section('South-east tower')
    tower(m, 25, 1, 6, 16, ch, top='battlement', top_color='dbg', floor_color='black',
          slits=[('s', 2, 4), ('e', 3, 4), ('s', 3, 10), ('e', 2, 10)], windows=[('n', 2, 6, 'dbg'), ('w', 3, 6, 'dbg')],
          flag='dark_blue')
    for name, z0 in (('South-west turret', 1), ('North-west turret', 27)):
        m.new_section(name)
        tower(m, 5, z0, 4, 13, ch, top='pyramid', top_color='dbg', roof_color='dark_blue', floor_color='black',
              slits=[('w', 1, 4), ('s' if z0 == 1 else 'n', 2, 4)], windows=[], flag='dark_blue', corbels=True)

    # --- 5. curtain walls -------------------------------------------------
    walls = [
        ('South curtain wall', 9, 1, 16, 'x', (0, 1)),
        ('North curtain wall', 9, 30, 12, 'x', (0, -1)),
        ('East curtain wall', 30, 7, 14, 'z', (-1, 0)),
        ('West curtain walls', 5, 5, 6, 'z', (1, 0)),
        (None, 5, 21, 6, 'z', (1, 0)),
    ]
    for name, x, z, n, axis, inner in walls:
        if name:
            m.new_section(name)
        for i in range(2, n - 1, 3):
            cx, cz = (x + i, z) if axis == 'x' else (x, z + i)
            m.reserve(cx, cz, 12, 1, 1, 6)
        for c in range(WALL_H):
            wall_line(m, x, z, n, axis, c * 3, ch, parity=c)
            if c % 3 == 2:
                m.step()
        m.step()
        cells = []
        for i in range(n):
            cx, cz = (x + i, z) if axis == 'x' else (x, z + i)
            cells += [(cx, cz), (cx + inner[0], cz + inner[1])]
        fill_area(m, cells, WALL_H * 3, 'black')
        m.step()
        merlons_line(m, x, z, n, axis, WALL_H * 3 + 1, 'dbg', pattern=(1, 1))
        m.step()

    # --- 6. barracks ---------------------------------------------------------
    m.new_section('Barracks')
    bx0, bz0, bx1, bz1 = 11, 3, 20, 8
    bch = stone_mix(m, {'black': 0.15, 'dbg': 0.25, 'reddish_brown': 0.3, 'dark_brown': 0.3}, p_mason=0.0,
                    base_weights={'dbg': 0.7, 'black': 0.3}, base_courses=2)
    m.add('60596', 'black', 14, bz1, 0, 0)
    m.add('60616a', 'reddish_brown', 14, bz1, 0, 0, occupy=False, check=False)
    for x in (12, 18):
        m.add('60592', 'black', x, bz1, 6, 0); m.add('60601', 'trans_clear', x, bz1, 6, 0, occupy=False, check=False)
    for c in range(6):
        ring_course(m, bx0, bz0, bx1, bz1, c * 3, bch)
        if c % 2 == 1:
            m.step()
    gable_roof(m, bx0, bz0, bx1 - bx0 + 1, bz1 - bz0 + 1, 18, 'dark_blue', ridge_axis='x',
               gable_chooser=solid('dark_brown'), ridge_color='black')
    m.step()
    # weapon crates and barrels in the courtyard
    m.add('2489', 'reddish_brown', 22, 9, 0, check=False)
    m.add('2489', 'reddish_brown', 24, 9, 0, check=False)
    m.add('3003', 'reddish_brown', 22, 12, 0); m.add('3068b', 'reddish_brown', 22, 12, 3)
    m.step()
    return m


if __name__ == '__main__':
    m = build()
    bad, _ = m.check_connectivity()
    print('parts', len(m.parts), 'unconnected', len(bad))
    for i in bad[:30]:
        p = m.parts[i]
        print('  ', p.ld, p.color, p.cells[:2], p.lvl, p.section)
