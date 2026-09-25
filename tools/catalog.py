"""LDraw -> BrickLink catalog mapping and estimated prices.

Prices are ESTIMATES of typical BrickLink per-piece prices (USD, mixed new/used,
2025-26 market) used for budgeting. Real prices vary by seller, condition and
region; shipping is not included.
"""
from lego import COLORS
import ldgeom

# LDraw part id -> BrickLink item id (only where they differ)
BL_ID = {
    '3040b': '3040', '3044b': '3044c', '3665a': '3665', '3660a': '3660', '6141': '4073', '4032a': '4032',
    '3941': '3941', '4493c00': '4493c01', '3816b': '970c00', '3817b': '970c00', '3815b': '970c00',
    '73200-f2': '970c00', '41879a': '41879', '3818': '981', '3819': '982', '3820': '983', '2435': '2435',
    '60616a': '60616a', '3062b': '3062b', '4589': '4589', '3957a': '3957a', '4495b': '4495b', '4495a': '4495a',
    '33183': '33183', '3747b': '3747b', '4460b': '4460b', '6143': '3941',
}

# items worth double-checking on BrickLink when uploading (older or rarer catalog entries)
VERIFY = {'4495b': 'Flag 4 x 1 Wave Right - if not found search "Flag 4 x 1 Wave"',
          '2490': 'Horse Barding (plain) - optional decoration, skip if not available in this colour',
          '4524': 'Minifig Cape (plastic) - any cape works (cloth cape 522 is a fine substitute)',
          '973': 'Torso without arms - alternatively buy a plain torso with arms and hands assembled',
          '30167': 'Hat, Wide Brim Flat - any peasant hat works',
          '6123': 'Halberd - any pole arm works'}

# (part, colour) combinations that may be scarce -> suggested substitute
VERIFY_COLOR = {
    ('3045', 'dark_blue'): 'Dark Blue roof parts may be scarce - Blue or Black work too (change all roof parts together)',
    ('3037', 'dark_blue'): 'see Dark Blue roof note', ('3039', 'dark_blue'): 'see Dark Blue roof note',
    ('3688', 'dark_blue'): 'see Dark Blue roof note', ('3688', 'red'): 'Red spire - Dark Red also works',
    ('3043', 'dark_red'): 'Red also works', ('2587', 'lbg'): 'Flat Silver also works',
    ('4503', 'flat_silver'): 'Light Bluish Gray also works', ('2435', 'dark_green'): 'Green also works',
}

NAMES = {
    '4493c00': 'Horse with 2 x 2 Cutout (Movable Legs)', '973': 'Minifigure Torso (plain)',
    '3818': 'Minifigure Arm Right', '3819': 'Minifigure Arm Left', '3820': 'Minifigure Hand',
    'HIPSLEGS': 'Minifigure Hips and Legs (plain)', '41879a': 'Minifigure Legs Short',
}

# base price per piece (USD) for common colours
BASE = {
    # bricks
    '3005': .05, '3004': .05, '3622': .07, '3010': .08, '3009': .12, '3008': .16, '6111': .25, '6112': .30,
    '3003': .08, '3002': .10, '3001': .12, '2456': .20, '3007': .30, '98283': .10, '30136': .08, '30137': .15,
    '3062b': .05, '3941': .12, '4070': .06, '87087': .06,
    # plates
    '3024': .03, '3023': .03, '3623': .04, '3710': .05, '3666': .07, '3460': .10, '4477': .15, '60479': .18,
    '3022': .04, '3021': .06, '3020': .07, '3795': .10, '3034': .14, '3832': .18, '2445': .22, '4282': .35,
    '3031': .15, '3032': .18, '3035': .25, '3030': .32, '3029': .40, '3958': .30, '3036': .35, '3033': .45,
    '3028': .55, '3456': .60, '3027': .70, '41539': .70, '92438': 1.20, '91405': 2.50, '6141': .03, '4032a': .05,
    '33291': .05, '32607': .08,
    # tiles
    '3070b': .04, '3069b': .04, '63864': .07, '2431': .08, '6636': .12, '4162': .18, '3068b': .06, '26603': .15,
    '87079': .18,
    # slopes / roof
    '3040b': .06, '3039': .08, '3038': .14, '3037': .18, '3045': .20, '3043': .15, '3044b': .12, '3298': .15,
    '3665a': .08, '3660a': .12, '3688': .40,
    # arches, windows, doors
    '3455': .30, '3659': .15, '30044': .35, '30046': .30, '60592': .12, '60601': .08, '60596': .35, '60616a': .35,
    # misc
    '3811': 6.50, '30055': .30, '4495b': .45, '4589': .05, '2489': .25, '3470': 1.00, '3471': 1.00, '2435': .60,
    '33051': .10, '33172': .10, '33183': .08, '3899': .08, '2343': .15, '33054': .15,
    # minifig
    '973': .45, '3818': .08, '3819': .08, '3820': .04, 'HIPSLEGS': .35, '41879a': .35, '3626bp01': .25,
    '3626bp02': .40, '3626bp03': .40, '3626bp05': .30, '71015': .60, '4524': .60, '4503': .50, '3844': .30,
    '2594': .45, '2587': .40, '3901': .20, '4530': .30, '3625': .35, '30167': .35, '59': .20, '98370': .15,
    '3847': .10, '3849': .30, '3846': .25, '2586': .25, '6123': .30, '4497': .10, '4499': .25, '3848': .30,
    '2570': .30, '4522': .15, '4496': .15, '3837': .15, '3959': .08, '3835': .15,
    '4493c00': 4.50, '4491b': .40, '2490': 1.20,
}
# colour price multipliers
CMULT = {c: 1.0 for c in COLORS}
for c in ('dark_tan', 'dark_red', 'dark_blue', 'dark_green', 'dark_brown', 'sand_green', 'olive_green',
          'medium_nougat', 'orange', 'dark_orange', 'bright_green', 'pearl_gold', 'flat_silver', 'medium_blue',
          'lime', 'bright_light_orange', 'nougat', 'light_nougat', 'medium_azure', 'sand_blue'):
    CMULT[c] = 1.5
for c in COLORS:
    if c.startswith('trans_'):
        CMULT[c] = 1.3


def bl_id(ld):
    return BL_ID.get(ld, ld)


def name(ld):
    if ld in NAMES:
        return NAMES[ld]
    t = ldgeom.info(ld)['title']
    return ' '.join(t.replace('~', '').split())


def price(ld, color):
    base = BASE.get(ld)
    if base is None:
        base = 0.15
    return round(base * CMULT.get(color, 1.2), 3)
