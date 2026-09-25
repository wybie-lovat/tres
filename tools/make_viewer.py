"""Assemble viewer/ : index.html (from the template), packed model, step data, colours, poster."""
import html, json, os, shutil, sys
sys.path.insert(0, os.path.dirname(__file__))
import viewer_data, warriors, instructions as ins, ldgeom

REPO = ins.REPO


def main():
    out = os.path.join(REPO, 'viewer')
    os.makedirs(out, exist_ok=True)
    viewer_data.main(out)
    shutil.copy(os.path.join(ldgeom.LIB, 'LDConfig.ldr'), os.path.join(out, 'ldconfig.txt'))
    poster = os.path.join(REPO, 'renders', 'diorama_hero.jpg')
    if os.path.exists(poster):
        shutil.copy(poster, os.path.join(out, 'poster.jpg'))
    summ = json.load(open(os.path.join(REPO, 'bricklink', 'budget_summary.json')))
    steps = {}
    for name in ('lionhold', 'millbrook', 'ravencrag', 'warriors'):
        d = os.path.join(ins.BUILD, 'steps', name)
        steps[name] = len([f for f in os.listdir(d) if f.startswith('step_')]) if os.path.isdir(d) else ''
    rows = []
    for name in ('lionhold', 'millbrook', 'ravencrag', 'warriors'):
        s = summ[name]
        rows.append(f'<tr><td><span class="book">{ins.MODULES[name]["book"]}</span>{html.escape(s["title"])}</td>'
                    f'<td class="n">{s["pieces"]:,}</td><td class="n">{steps[name]}</td><td class="n">${s["est_usd"]:.2f}</td></tr>')
    t = summ['total']
    rows.append(f'<tr class="total"><td>Complete set</td><td class="n">{t["pieces"]:,}</td>'
                f'<td class="n">{sum(v for v in steps.values() if v)}</td><td class="n">${t["est_usd"]:.2f}</td></tr>')
    houses = [('lions', 'House Aurelion', 'The Crimson Lions of Lionhold'),
              ('folk', 'Millbrook', 'The common folk and their barricade'),
              ('ravens', 'House Corvane', 'The Black Ravens of Ravencrag')]
    cast = []
    for key, name, motto in houses:
        items = []
        for fk, (f, faction, role) in warriors.FIGS.items():
            if faction == key:
                items.append(f'<li>{html.escape(role)}</li>')
        if key != 'folk':
            items.append('<li>2 armoured battle horses</li><li>A catapult</li>')
        cast.append(f'<div class="house {key}"><h3>{name}</h3><p class="motto">{motto}</p><ul>{"".join(items)}</ul></div>')
    tpl = open(os.path.join(os.path.dirname(__file__), 'viewer_template.html')).read()
    page = (tpl.replace('__PIECES__', f'{t["pieces"]:,}').replace('__FIGS__', str(summ['figures']))
            .replace('__HORSES__', str(summ['horses'])).replace('__ROWS__', '\n'.join(rows))
            .replace('__CAST__', '\n'.join(cast)).replace('__HEADROOM__', f'{500 - t["est_usd"]:.0f}'))
    # artifact.html: body fragment for the hosted page; index.html: standalone document for local use
    os.makedirs(ins.BUILD, exist_ok=True)
    with open(os.path.join(ins.BUILD, 'viewer_artifact.html'), 'w') as fh:
        fh.write(page)
    with open(os.path.join(out, 'index.html'), 'w') as fh:
        fh.write('<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
                 '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
                 '</head>\n<body>\n' + page + '\n</body>\n</html>\n')
    print('viewer written', out)


if __name__ == '__main__':
    main()
