"""Module 5 - WARRIORS & WEAPONS: the minifigures, horses and siege engines,
plus their positions in the battle scene across the whole diorama."""
import numpy as np
from lego import Model, rot_y, rot_x, COLORS
from minifig import Fig, horse_parts, _line
from kit import rect_cells

LANCE = rot_x(-45)       # item rotation so a lance is couched horizontally

# ---------------------------------------------------------------------------
# Figures: key -> (Fig, faction, role)
FIGS = {}

def fig(key, faction, role, **kw):
    FIGS[key] = (Fig(key, **kw), faction, role)

# House Aurelion - the Crimson Lions
fig('lion_duke', 'lions', 'Duke Aldric Aurelion, Lord of Lionhold', torso='red', legs='black', head='3626bp03',
    headgear=('71015', 'pearl_gold'), back=('4524', 'black'), right=('59', 'flat_silver'), arm_r=-70)
fig('lion_knight1', 'lions', 'Sir Leofric, knight of the Lion (mounted)', torso='red', legs='black', sit=True,
    headgear=('4503', 'flat_silver'), neck=('2587', 'flat_silver'), right=('3849', 'white'), right_rot=LANCE,
    left=('3846', 'red'), arm_r=-10)
fig('lion_knight2', 'lions', 'Sir Gawyn, knight of the Lion (mounted)', torso='red', legs='white', sit=True,
    headgear=('4503', 'flat_silver'), neck=('2587', 'flat_silver'), right=('3847', 'flat_silver'), arm_r=-80,
    left=('3846', 'white'))
fig('lion_soldier1', 'lions', 'Lion man-at-arms with sword', torso='red', legs='black', head='3626bp05',
    headgear=('3844', 'lbg'), right=('3847', 'flat_silver'), arm_r=-60, left=('3846', 'red'))
fig('lion_soldier2', 'lions', 'Lion halberdier', torso='red', legs='dark_tan', headgear=('3844', 'lbg'),
    neck=('2587', 'lbg'), right=('6123', 'flat_silver'), arm_r=-30)
fig('lion_soldier3', 'lions', 'Lion spearman', torso='white', arms='red', legs='red', headgear=('3844', 'lbg'),
    right=('4497', 'reddish_brown'), arm_r=-30, left=('2586', 'red'))
fig('lion_archer', 'lions', 'Lion archer', torso='red', legs='tan', head='3626bp05', headgear=('3901', 'reddish_brown'),
    left=('4499', 'reddish_brown'), arm_l=-60, right=None)

fig('lion_banner', 'lions', 'Lion standard-bearer', torso='red', legs='black', headgear=('3844', 'lbg'),
    neck=('2587', 'flat_silver'), right=('3957a', 'black'), arm_r=-15,
    extras=[('2335', 'red', 'r', (0, -80, 0), np.eye(3)), ('2335', 'yellow', 'r', (0, -40, 0), np.eye(3))])

# House Corvane - the Black Ravens
fig('raven_baroness', 'ravens', 'Baroness Morwen Corvane, Lady of Ravencrag', torso='dark_blue', legs='black',
    head='3626bp02', headgear=('4530', 'black'), back=('4524', 'black'), right=('98370', 'flat_silver'), arm_r=-60)
fig('raven_knight1', 'ravens', 'Sir Mordred, Raven knight (mounted)', torso='dark_blue', legs='black', sit=True,
    headgear=('3844', 'black'), visor=('2594', 'black'), neck=('2587', 'black'), right=('3849', 'black'),
    right_rot=LANCE, left=('3846', 'dark_blue'), arm_r=-10)
fig('raven_knight2', 'ravens', 'Sir Corwin, Raven knight (mounted)', torso='black', legs='dark_blue', sit=True,
    headgear=('3844', 'black'), visor=('2594', 'black'), neck=('2587', 'black'), right=('59', 'flat_silver'),
    arm_r=-80, left=('3846', 'black'))
fig('raven_soldier1', 'ravens', 'Raven axeman', torso='dark_blue', legs='black', head='3626bp05',
    headgear=('3844', 'dbg'), right=('3848', 'flat_silver'), arm_r=-70)
fig('raven_soldier2', 'ravens', 'Raven swordsman', torso='black', legs='dark_blue', headgear=('3844', 'dbg'),
    right=('3847', 'flat_silver'), arm_r=-50, left=('2586', 'dark_blue'))
fig('raven_soldier3', 'ravens', 'Raven spearman', torso='dark_blue', legs='dark_blue', headgear=('3844', 'dbg'),
    neck=('2587', 'black'), right=('4497', 'black'), arm_r=-30)
fig('raven_crossbow', 'ravens', 'Raven crossbowman', torso='dark_blue', legs='black', head='3626bp03',
    headgear=('3844', 'black'), right=('2570', 'black'), arm_r=-60, arm_l=-60)

fig('raven_banner', 'ravens', 'Raven standard-bearer', torso='dark_blue', legs='black', headgear=('3844', 'black'),
    neck=('2587', 'black'), right=('3957a', 'black'), arm_r=-15,
    extras=[('2335', 'dark_blue', 'r', (0, -80, 0), np.eye(3)), ('2335', 'black', 'r', (0, -40, 0), np.eye(3))])

# The common folk of Millbrook
fig('smith', 'folk', 'Bram the blacksmith', torso='reddish_brown', legs='black', head='3626bp03',
    headgear=('3901', 'black'), right=('4522', 'reddish_brown'), arm_r=-80)
fig('farmer', 'folk', 'Hob the farmer', torso='tan', legs='dark_brown', headgear=('30167', 'tan'),
    right=('4496', 'reddish_brown'), arm_r=-30)
fig('farmwife', 'folk', 'Maud the farmwife', torso='sand_green', legs='dark_tan', head='3626bp02',
    headgear=('3625', 'reddish_brown'), right=('3837', 'reddish_brown'), arm_r=-40)
fig('torchbearer', 'folk', 'Wat with a torch', torso='olive_green', legs='dark_tan', head='3626bp05',
    headgear=('3901', 'dark_brown'), right=('3959', 'reddish_brown'), arm_r=-90)
fig('digger', 'folk', 'Tom with a shovel', torso='dark_tan', legs='reddish_brown', headgear=('3901', 'dark_brown'),
    right=('3837', 'black'), arm_r=-40)
fig('merchant', 'folk', 'Guy the merchant', torso='dark_red', legs='black', head='3626bp03',
    headgear=('3901', 'reddish_brown'), right=('33054', 'reddish_brown'), arm_r=-40)
fig('alewife', 'folk', 'Agnes of the Quarrelsome Boar', torso='white', legs='dark_brown', head='3626bp02',
    headgear=('4530', 'dark_tan'), right=('33054', 'reddish_brown'), left=('3899', 'white'), arm_r=-40, arm_l=-40)
fig('child', 'folk', 'Pip the stable boy', torso='tan', legs='dark_brown', short=True, headgear=('3901', 'reddish_brown'),
    right=('33051', 'red'), arm_r=-40)
fig('friar', 'folk', 'Brother Anselm, the peacemaker', torso='reddish_brown', legs='reddish_brown', head='3626bp01',
    headgear=None, right=('2343', 'pearl_gold'), arm_r=-100, arm_l=-100, left=None)
fig('woodcutter', 'folk', 'Ned the woodcutter', torso='dark_green', legs='dark_brown', head='3626bp05',
    headgear=('3901', 'black'), right=('3835', 'flat_silver'), arm_r=-80)

HORSES = {
    'lion_horse1': dict(color='white', saddle='black', barding='red', rider='lion_knight1'),
    'lion_horse2': dict(color='white', saddle='black', barding='red', rider='lion_knight2'),
    'raven_horse1': dict(color='black', saddle='black', barding='black', rider='raven_knight1'),
    'raven_horse2': dict(color='black', saddle='black', barding='black', rider='raven_knight2'),
}
RIDER_OFFSET = np.array([0, -67.0, 10.0])


def submodels():
    """LDraw sub-models for every figure, horse (with rider) and siege engine."""
    subs = {}
    for key, (f, faction, role) in FIGS.items():
        subs[key] = f.ldraw()
    for key, h in HORSES.items():
        lines = [f'0 {key}', f'0 Name: {key}.ldr', '']
        for part, col, pos, M in horse_parts(h['color'], saddle=h['saddle'], barding=h['barding']):
            lines.append(_line(col, pos, M, part))
        subs[key] = lines
    for key, colors in (('lion_catapult', ('reddish_brown', 'red')), ('raven_catapult', ('reddish_brown', 'dark_blue'))):
        subs[key] = catapult_lines(key, *colors)
    return subs


def catapult_model(key, wood, accent):
    """A small mangonel built on the stud grid (local 6 x 4)."""
    m = Model(key, key)
    m.add('3032', wood, 0, 0, 0)                        # 6x4 base (lvl 0)
    m.step()
    m.add('3009', wood, 0, 0, 1); m.add('3009', wood, 0, 3, 1)   # side beams
    m.add('3062b', 'dbg', 0, 1, 1); m.add('3062b', 'lbg', 1, 2, 1); m.add('3062b', 'dbg', 0, 2, 1)  # ammo pile
    m.step()
    m.add('3010', wood, 2, 0, 4, 1)                     # cross beam carrying the arm
    m.add('3069b', accent, 0, 0, 4); m.add('3069b', accent, 0, 3, 4)
    m.add('3069b', accent, 4, 0, 4); m.add('3069b', accent, 4, 3, 4)
    m.step()
    m.add('3795', wood, 0, 1, 7)                        # throwing arm 2x6
    m.add('4032a', 'dbg', 4, 1, 8)                      # bucket
    m.add('3062b', 'lbg', 4, 1, 9); m.add('3062b', 'dbg', 5, 2, 9)   # stones in the bucket
    m.step()
    return m


def catapult_lines(key, wood, accent):
    m = catapult_model(key, wood, accent)
    lines = [f'0 {key}', f'0 Name: {key}.ldr', '']
    for p in m.parts:
        lines.append(m.ldraw_line(p))
    return lines


# ---------------------------------------------------------------------------
# Battle positions in DIORAMA coordinates (Lionhold x 0..31, Millbrook x 32..95, Ravencrag x 96..127)
# (key, x, z, lvl, facing) ; facing: rot quarter turns (0 = toward viewer/south, 1 = west, 2 = north, 3 = east)
FIG_POS = [
    ('lion_duke', 23, 15, 52, 3),            # on the Lionhold gatehouse roof
    ('lion_soldier1', 47, 15, 1, 3),
    ('lion_soldier2', 50, 12, 1, 3),
    ('lion_soldier3', 44, 17, 1, 3),
    ('lion_archer', 16, 1, 25, 0),            # on the Lionhold south wall-walk
    ('lion_banner', 35, 18, 1, 3),
    ('raven_banner', 92, 13, 1, 1),
    ('friar', 64, 11, 0, 0),
    ('raven_baroness', 104, 15, 49, 1),      # on the Ravencrag gatehouse roof
    ('raven_soldier1', 76, 15, 1, 1),
    ('raven_soldier2', 79, 17, 1, 1),
    ('raven_soldier3', 81, 13, 1, 1),
    ('raven_crossbow', 113, 1, 28, 0),        # on the Ravencrag south wall-walk
    ('smith', 55, 21, 0, 0),
    ('farmer', 64, 13, 1, 1),
    ('farmwife', 66, 18, 1, 3),
    ('torchbearer', 63, 16, 1, 3),
    ('digger', 84, 9, 0, 0),
    ('merchant', 38, 9, 0, 0),
    ('alewife', 72, 20, 0, 0),
    ('child', 60, 9, 1, 0),
    ('woodcutter', 86, 20, 0, 1),
]
HORSE_POS = [
    ('lion_horse1', 38, 14, 1, 3),
    ('lion_horse2', 41, 17, 1, 3),
    ('raven_horse1', 84, 14, 1, 1),
    ('raven_horse2', 88, 17, 1, 1),
]
CATAPULT_POS = [
    ('lion_catapult', 50, 20, 0, 0),
    ('raven_catapult', 66, 1, 0, 1),
]


def _supported(m, x, z, lvl, w, d):
    for cx in range(x, x + w):
        for cz in range(z, z + d):
            if lvl == 0:
                continue
            i = m.occ.get((cx, cz, lvl - 1))
            if i is None or (cx, cz) not in m.parts[i].top_cells:
                return False
    return True


def find_spot(m, x, z, lvl, w, d, h, radius=4, need_support=True):
    """Nearest free spot (with studs underneath) to the wanted position."""
    cands = sorted(((dx, dz) for dx in range(-radius, radius + 1) for dz in range(-radius, radius + 1)),
                   key=lambda t: (abs(t[0]) + abs(t[1]), t))
    for dx, dz in cands:
        for L in (lvl, lvl + 1, lvl - 1):
            if L < 0:
                continue
            if not (0 <= x + dx and x + dx + w <= 128 and 0 <= z + dz and z + dz + d <= 32):
                continue
            if m.free(x + dx, z + dz, L, w, d, h) and (not need_support or _supported(m, x + dx, z + dz, L, w, d)):
                return x + dx, z + dz, L
    raise ValueError(f'no free spot near {(x, z, lvl)}')


def place_battle(m):
    """Add references to all figures/horses/engines to diorama model m, registering their space."""
    placed = []
    for key, x, z, lvl, rot in FIG_POS:
        w, d = (2, 1) if rot % 2 == 0 else (1, 2)
        x, z, lvl = find_spot(m, x, z, lvl, w, d, 12)
        placed.append((key, x, z, lvl))
        R = rot_y(rot)
        # 2 studs across the hips: centre of the 2x1 footprint
        if rot % 2 == 0:
            cx, cz, w, d = x * 20 + 20, z * 20 + 10, 2, 1
        else:
            cx, cz, w, d = x * 20 + 10, z * 20 + 20, 1, 2
        idx = m.add_free(key + '.ldr', 16, [cx, -lvl * 8, cz], R, sub=True, note=key)
        m.occupy_block(idx, x, z, lvl, w, d, 12)
    for key, x, z, lvl, rot in HORSE_POS:
        R = rot_y(rot)
        if rot % 2 == 0:
            fx, fz, fw, fd = x, z - 4, 2, 9
        else:
            fx, fz, fw, fd = x - 4, z, 9, 2
        nx, nz, lvl = find_spot(m, fx, fz, lvl, fw, fd, 18)
        x, z = nx - fx + x, nz - fz + z
        placed.append((key, x, z, lvl))
        if rot % 2 == 0:
            cx, cz = x * 20 + 20, z * 20 + 10
        else:
            cx, cz = x * 20 + 10, z * 20 + 20
        idx = m.add_free(key + '.ldr', 16, [cx, -lvl * 8, cz], R, sub=True, note=key)
        rider = HORSES[key]['rider']
        m.add_free(rider + '.ldr', 16, np.array([cx, -lvl * 8, cz]) + R @ RIDER_OFFSET, R, sub=True, note=rider)
        # footprint of the horse: 2 wide, 8 long
        if rot % 2 == 0:
            m.occupy_block(idx, x, z - 4, lvl, 2, 9, 18)
        else:
            m.occupy_block(idx, x - 4, z, lvl, 9, 2, 18)
    for key, x, z, lvl, rot in CATAPULT_POS:
        R = rot_y(rot)
        w, d = (6, 4) if rot % 2 == 0 else (4, 6)
        x, z, lvl = find_spot(m, x, z, lvl, w, d, 10)
        placed.append((key, x, z, lvl))
        # catapult local origin is its min corner; rotate about its centre
        c_local = np.array([60.0, 0, 40.0])
        c_world = np.array([x * 20 + w * 10, -lvl * 8, z * 20 + d * 10])
        pos = c_world - R @ c_local
        idx = m.add_free(key + '.ldr', 16, pos, R, sub=True, note=key)
        m.occupy_block(idx, x, z, lvl, w, d, 10)
    return placed
