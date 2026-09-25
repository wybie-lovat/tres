"""Write the deliverables that do not need rendering:
   models/*.ldr|mpd  (LDraw, open in BrickLink Studio / LeoCAD / LDCad)
   bricklink/*.xml   (BrickLink wanted lists)
   bricklink/parts_list.csv and budget summary (JSON used by README / viewer)
"""
import json, os, sys
from collections import Counter, OrderedDict
sys.path.insert(0, os.path.dirname(__file__))
import bom, catalog, diorama, export, instructions as ins, warriors
from lego import COLORS

REPO = ins.REPO


def main():
    models = ins.build_all()
    os.makedirs(os.path.join(REPO, 'models'), exist_ok=True)
    os.makedirs(os.path.join(REPO, 'bricklink'), exist_ok=True)

    # --- LDraw files -----------------------------------------------------
    subs = warriors.submodels()
    for name, m in models.items():
        book = ins.MODULES[name]['book']
        if name == 'warriors':
            # the cast lined up, every figure / horse / catapult as its own sub-model
            import viewer_data
            lu, _ = viewer_data.lineup_model()
            export.write_ldr(lu, os.path.join(REPO, 'models', f'{book}_{name}.mpd'), subs=subs)
            continue
        export.write_ldr(m, os.path.join(REPO, 'models', f'{book}_{name}.ldr'))
    d, mods = diorama.build()
    export.write_ldr(d, os.path.join(REPO, 'models', 'nobles_and_common_folk_diorama.mpd'), subs=subs)

    # --- BOM -------------------------------------------------------------
    counts = OrderedDict()
    for name, m in models.items():
        if name == 'warriors':
            counts[name] = bom.warriors_counts()
        else:
            counts[name] = bom.model_counts(m)
    total = Counter()
    for c in counts.values():
        total += c
    items = bom.rows(total)
    per_module_rows = {name: bom.rows(c) for name, c in counts.items()}
    # quantity per module for the CSV
    permod = {name: Counter({(r['bl'], r['color']): r['qty'] for r in rows}) for name, rows in per_module_rows.items()}
    extra = [(f'Qty {ins.MODULES[n]["title"]}', (lambda n: lambda it: permod[n].get((it['bl'], it['color']), 0))(n))
             for n in counts]
    bom.write_csv(items, os.path.join(REPO, 'bricklink', 'parts_list.csv'), extra)
    bom.write_wanted_xml(items, os.path.join(REPO, 'bricklink', 'wanted_list_complete.xml'))
    for name, rows in per_module_rows.items():
        book = ins.MODULES[name]['book']
        bom.write_wanted_xml(rows, os.path.join(REPO, 'bricklink', f'wanted_list_book{book}_{name}.xml'))

    summary = OrderedDict()
    for name, rows in per_module_rows.items():
        summary[name] = dict(title=ins.MODULES[name]['title'], pieces=sum(r['qty'] for r in rows), lots=len(rows),
                             est_usd=round(bom.total(rows), 2))
    summary['total'] = dict(title='Complete set', pieces=sum(r['qty'] for r in items), lots=len(items),
                            est_usd=round(bom.total(items), 2))
    summary['figures'] = len(warriors.FIGS)
    summary['horses'] = len(warriors.HORSES)
    summary['verify'] = [dict(bl=r['bl'], color=r['color_name'], qty=r['qty'], note=r['verify']) for r in items if r['verify']]
    with open(os.path.join(REPO, 'bricklink', 'budget_summary.json'), 'w') as fh:
        json.dump(summary, fh, indent=2)
    print(json.dumps({k: v for k, v in summary.items() if k != 'verify'}, indent=1))
    return summary


if __name__ == '__main__':
    main()
