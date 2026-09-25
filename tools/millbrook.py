"""Module 3 - MILLBROOK, the village of the common folk, caught between two castles.

Two 32x32 baseplates side by side (x 0..63). The road runs west-east along
z 13..18 from Lionhold's drawbridge to Ravencrag's drawbridge.
"""
from kit import *


def road(m):
    cells = {(x, z) for x in range(64) for z in range(13, 19)}
    cells |= {(x, z) for x in range(24, 32) for z in range(8, 13)}          # village square
    paths = [(4, 19, 4, 4), (39, 19, 4, 4), (55, 19, 4, 4), (17, 19, 6, 4)]  # paths to the doors
    for (x, z, w, d) in paths:
        cells |= {(xx, zz) for xx in range(x, x + w) for zz in range(z, z + d)}
    west = {c for c in cells if c[0] < 32}
    east = cells - west
    col = lambda c: 'dark_tan' if m.rng.random() < 0.35 else 'tan'
    fill_area(m, west, 0, 'tan', color_fn=col, sizes=[(2, 8), (2, 6), (2, 4), (4, 4), (2, 3), (2, 2), (1, 4), (1, 3), (1, 2), (1, 1)])
    m.step()
    fill_area(m, east, 0, 'tan', color_fn=col, sizes=[(2, 8), (2, 6), (2, 4), (4, 4), (2, 3), (2, 2), (1, 4), (1, 3), (1, 2), (1, 1)])
    m.step()
    # cobbles and ruts
    for (x, z) in [(3, 14), (9, 17), (14, 15), (20, 13), (24, 10), (37, 16), (44, 14), (51, 17), (58, 15)]:
        m.add('3069b', 'dark_tan' if (x % 2) else 'lbg', x, z, 1, 0)
    m.step()


def build(seed=37):
    m = Model('millbrook', 'Millbrook - Village of the Common Folk', seed=seed)
    m.new_section('Baseplates and the road')
    m.add('3811', 'green', 0, 0, -1, note='baseplate west')
    m.add('3811', 'green', 32, 0, -1, note='baseplate east')
    m.step()
    road(m)

    # --- houses -------------------------------------------------------------
    timber_house(m, 2, 23, 10, 7, "Miller's cottage", door_x=4, door_color='reddish_brown',
                 ground_windows=[9], upper_windows=[3, 9], back_windows=[5], roof='tan', ridge='reddish_brown',
                 fill='white', frame='dark_brown')
    tav_ground = stone_mix(m, {'lbg': 0.5, 'tan': 0.2, 'dbg': 0.15, 'dark_tan': 0.15}, p_mason=0.5)
    timber_house(m, 36, 23, 12, 7, 'The Quarrelsome Boar tavern', ground=tav_ground, door_x=39,
                 door_color='dark_brown', ground_windows=[37, 44], upper_windows=[37, 41, 45], back_windows=[40, 44],
                 roof='dark_red', ridge='dark_red', fill='white', frame='dark_brown')
    logs = lambda n, x, z, lvl: ({1: '3005', 2: '30136', 3: '3622', 4: '30137', 6: '3009', 8: '3008'}[n],
                                 'reddish_brown' if n in (2, 4) else 'dark_brown')
    timber_house(m, 52, 23, 10, 7, "Woodcutter's house", ground=logs, door_x=55, door_color='dark_brown',
                 ground_windows=[53, 60], upper_windows=[54, 58], roof='reddish_brown', ridge='reddish_brown',
                 fill='tan', frame='dark_brown', window_frame='dark_brown')

    # --- blacksmith's forge --------------------------------------------------
    m.new_section("Blacksmith's forge - walls and hearth")
    fx0, fz0, fx1, fz1 = 15, 23, 24, 30
    fst = stone_mix(m, {'dbg': 0.5, 'lbg': 0.35, 'black': 0.15}, p_mason=0.4)
    fill_area(m, rect_cells(fx0 + 1, fz0 + 1, 8, 6), 0, 'dbg')             # workshop floor
    m.reserve(16, fz0, 0, 3, 1, 15)
    m.reserve(21, fz0, 0, 3, 1, 15)
    m.step()
    for c in range(5):
        ring_course(m, fx0, fz0, fx1, fz1, c * 3, fst)
        if c % 2 == 1:
            m.step()
    m.add('6111', 'reddish_brown', fx0, fz0, 15, 0)                              # oak lintel over the front
    ring_course(m, fx0, fz0, fx1, fz1, 15, fst)
    ring_course(m, fx0, fz0, fx1, fz1, 18, fst)
    m.step()
    # hearth with fire, anvil and quench barrel
    m.add('3002', 'dbg', 21, 27, 1, 0)
    for (x, z, col) in [(21, 27, 'trans_orange'), (22, 27, 'trans_red'), (23, 27, 'trans_orange'), (22, 28, 'trans_orange')]:
        m.add('6141', col, x, z, 4)
    m.add('3004', 'dbg', 18, 26, 1, 0); m.add('3069b', 'black', 18, 26, 4, 0)       # anvil
    m.add('2489', 'reddish_brown', 16, 28, 1, check=False)
    m.step()
    m.new_section("Blacksmith's forge - slate roof")
    plate_ring(m, fx0, fz0, fx1, fz1, 21, 'dark_brown', width=1)
    m.step()
    gable_roof(m, fx0, fz0 - 1, fx1 - fx0 + 1, 10, 22, 'dbg', ridge_axis='x', gable_chooser=fst, ridge_color='black')
    m.step()

    # --- market stalls -------------------------------------------------------
    for i, (x0, stripes) in enumerate([(3, ('red', 'white')), (12, ('yellow', 'dark_green'))]):
        m.new_section(f'Market stall {i + 1}')
        z0 = 5
        posts(m, [(x0, z0), (x0 + 5, z0), (x0, z0 + 3), (x0 + 5, z0 + 3)], 0, 4)
        m.add('3010', 'reddish_brown', x0 + 1, z0, 0, 0)
        m.add('3710', 'tan', x0 + 1, z0, 3, 0)
        m.step()
        m.add('3032', 'reddish_brown', x0, z0, 12, 0)
        for k in range(4):
            m.add('6636', stripes[k % 2], x0, z0 + k, 13, 0)
        m.step()
    # goods on the counters (decor)
    for (x, z, part, col) in [(4, 5, '33051', 'red'), (5, 5, '33051', 'lime'), (6, 5, '33172', 'orange'),
                              (7, 5, '33051', 'red'), (13, 5, '3899', 'white'), (14, 5, '2343', 'pearl_gold'),
                              (15, 5, '33054', 'reddish_brown'), (16, 5, '3899', 'white')]:
        m.add_free(part, col, [x * 20 + 10, -4 * 8, z * 20 + 10])
    m.step()

    # --- village well --------------------------------------------------------
    m.new_section('Village well')
    wch = stone_mix(m, {'lbg': 0.7, 'dbg': 0.3}, p_mason=0.8)
    m.add('3068b', 'blue', 27, 9, 1)
    for c in range(2):
        ring_course(m, 26, 8, 29, 11, 1 + c * 3, wch, parity=c)
    m.step()
    posts(m, [(26, 9), (29, 9), (26, 10), (29, 10)], 7, 3)
    m.add('3031', 'reddish_brown', 26, 8, 16)
    gable_roof(m, 26, 8, 4, 4, 17, 'reddish_brown', ridge_axis='x', ridge_color='reddish_brown')
    m.step()

    # --- farm field --------------------------------------------------------
    m.new_section('Farm field and fence')
    for k in range(4):
        for x in (44, 52):
            m.add('3034', 'reddish_brown' if k % 2 == 0 else 'dark_brown', x, 2 + 2 * k, 0, 0)
    m.step()
    for k in range(4):
        z = 3 + 2 * k
        for x in range(45, 60, 2):
            if k == 2:
                # carrots: leafy tops poking out of the soil
                m.add('33291', 'green', x, z, 1)
                m.add_free('33183', 'bright_green', [x * 20 + 10, -16, z * 20 + 10])
            else:
                m.add('32607', 'bright_green' if k % 2 else 'green', x, z, 1)
    m.step()
    for x in range(44, 60, 4):
        m.add('30055', 'reddish_brown', x, 11, 0, 0)
    m.add('3003', 'tan', 61, 3, 0); m.add('3068b', 'yellow', 61, 3, 3)          # hay bales
    m.add('3003', 'tan', 61, 6, 0); m.add('3068b', 'yellow', 61, 6, 3)
    m.step()

    # --- trees ------------------------------------------------------------
    m.new_section('Trees')
    for (x, z, part, col) in [(12, 27, '3471', 'green'), (21, 2, '3470', 'green'), (40, 3, '2435', 'dark_green'),
                              (62, 0, '2435', 'green'), (49, 27, '3470', 'green'), (0, 1, '3471', 'green'),
                              (33, 27, '2435', 'dark_green')]:
        m.add(part, col, x, z, 0)
    m.step()

    # --- the commoners' barricade in the middle of the road ------------------
    m.new_section("The commoners' barricade")
    for z in (13, 17):
        m.add('2489', 'reddish_brown', 33, z, 1, check=False)
    m.add('3003', 'reddish_brown', 33, 15, 1); m.add('3068b', 'dark_brown', 33, 15, 4)
    for c in range(2):
        m.add('30137', 'reddish_brown' if c == 0 else 'dark_brown', 35, 13, 1 + 3 * c, 1)
        m.add('30136', 'dark_brown' if c == 0 else 'reddish_brown', 35, 17, 1 + 3 * c, 1)
    m.step()
    # gardens: flowers and bushes
    m.new_section('Gardens, flowers and bushes')
    flower_cols = ['red', 'yellow', 'white', 'bright_light_orange', 'medium_azure']
    k = 0
    for (x, z) in [(2, 21), (3, 20), (10, 21), (11, 20), (13, 21), (26, 21), (27, 20), (35, 21), (36, 20),
                   (47, 21), (48, 20), (51, 21), (62, 20), (63, 21), (1, 11), (2, 10), (20, 9), (22, 11),
                   (41, 9), (42, 11), (60, 11), (31, 3), (33, 5), (9, 1)]:
        if m.free(x, z, 0):
            m.add('33291', flower_cols[k % len(flower_cols)], x, z, 0)
            k += 1
    m.step()
    for (x, z, rot) in [(28, 22, 0), (0, 25, 0), (30, 0, 2), (60, 20, 0)]:
        w, d, h = m.footprint('2423', rot)[:3]
        if m.free(x, z, 0, w, d, 1):
            m.add('2423', 'green' if rot else 'bright_green', x, z, 0, rot)
    m.step()
    # log pile by the woodcutter's house
    for i, (x, lvl) in enumerate([(50, 0), (50, 3)]):
        m.add('30137', 'reddish_brown', x, 20, lvl, 1)
    m.step()
    return m


if __name__ == '__main__':
    m = build()
    bad, _ = m.check_connectivity()
    print('parts', len(m.parts), 'unconnected', len(bad))
    for i in bad[:30]:
        p = m.parts[i]
        print('  ', p.ld, p.color, p.cells[:2], p.lvl, p.section)
