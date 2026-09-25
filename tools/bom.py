"""Bill of materials for every module + BrickLink wanted-list export."""
from collections import Counter, OrderedDict
import csv, os
from xml.sax.saxutils import escape
from lego import COLORS
import catalog
from minifig import horse_parts
import warriors

MODULE_TITLES = OrderedDict([
    ('lionhold', '1. Lionhold - Castle of House Aurelion'),
    ('millbrook', '2. Millbrook - Village of the Common Folk'),
    ('ravencrag', '3. Ravencrag Keep - Stronghold of House Corvane'),
    ('warriors', '4. Warriors & Weapons'),
])


def model_counts(m):
    """Counter of (ldraw part, colour) for a grid model (sub-model references excluded)."""
    c = Counter()
    for p in m.parts:
        if p.sub:
            continue
        ld = p.ld[:-4] if p.ld.endswith('.dat') else p.ld
        c[(ld, p.color)] += 1
    return c


def fig_counts(f):
    c = Counter()
    legs_done = False
    for part, col, pos, M in f.parts():
        if part in ('3815b', '3816b', '3817b', '73200-f2'):
            if not legs_done:
                c[('HIPSLEGS', col)] += 1
                legs_done = True
            continue
        c[(part, col)] += 1
    return c


def warriors_counts():
    c = Counter()
    for key, (f, faction, role) in warriors.FIGS.items():
        c += fig_counts(f)
    for key, h in warriors.HORSES.items():
        for part, col, pos, M in horse_parts(h['color'], saddle=h['saddle'], barding=h['barding']):
            c[(part, col)] += 1
    for key, colors in (('lion_catapult', ('reddish_brown', 'red')), ('raven_catapult', ('reddish_brown', 'dark_blue'))):
        c += model_counts(warriors.catapult_model(key, *colors))
    return c


def bl_item(ld):
    if ld == 'HIPSLEGS':
        return '970c00'
    return catalog.bl_id(ld)


def rows(counts):
    """Aggregate by BrickLink item + colour."""
    agg = OrderedDict()
    for (ld, col), n in sorted(counts.items(), key=lambda kv: (catalog.name(kv[0][0]) if kv[0][0] != 'HIPSLEGS' else 'Minifigure Hips', kv[0][1])):
        key = (bl_item(ld), col)
        if key not in agg:
            nm = catalog.NAMES.get(ld) or catalog.name(ld)
            agg[key] = dict(ld=ld, bl=key[0], color=col, bl_color=COLORS[col][1], color_name=COLORS[col][2],
                            name=nm, qty=0, unit=catalog.price(ld, col),
                            verify=catalog.VERIFY.get(ld, '') or catalog.VERIFY_COLOR.get((ld, col), ''))
        agg[key]['qty'] += n
    return list(agg.values())


def write_wanted_xml(items, path, wanted_list_name=None, condition='X'):
    """BrickLink wanted-list XML (upload at bricklink.com -> Wanted -> Upload)."""
    out = ['<INVENTORY>']
    for it in items:
        out.append('  <ITEM>')
        out.append(f"    <ITEMTYPE>P</ITEMTYPE>")
        out.append(f"    <ITEMID>{escape(it['bl'])}</ITEMID>")
        out.append(f"    <COLOR>{it['bl_color']}</COLOR>")
        out.append(f"    <MINQTY>{it['qty']}</MINQTY>")
        out.append(f"    <CONDITION>{condition}</CONDITION>")
        out.append(f"    <MAXPRICE>-1.0000</MAXPRICE>")
        out.append(f"    <NOTIFY>N</NOTIFY>")
        out.append('  </ITEM>')
    out.append('</INVENTORY>')
    with open(path, 'w') as fh:
        fh.write('\n'.join(out) + '\n')


def write_csv(items, path, extra_cols=()):
    with open(path, 'w', newline='') as fh:
        w = csv.writer(fh)
        w.writerow(['BrickLink Item', 'Name', 'BrickLink Color ID', 'Color', 'Qty', 'Est. unit price (USD)',
                    'Est. total (USD)', 'LDraw part'] + [c for c, _ in extra_cols] + ['Note'])
        for it in items:
            w.writerow([it['bl'], it['name'], it['bl_color'], it['color_name'], it['qty'], f"{it['unit']:.3f}",
                        f"{it['unit'] * it['qty']:.2f}", it['ld']] + [f(it) for _, f in extra_cols] + [it['verify']])


def total(items):
    return sum(it['unit'] * it['qty'] for it in items)
