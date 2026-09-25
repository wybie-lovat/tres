"""Turn rendered step images into printable instruction booklets (HTML -> PDF)."""
import html, json, os, subprocess, sys
from collections import Counter, OrderedDict

sys.path.insert(0, os.path.dirname(__file__))
from lego import COLORS
import bom, catalog, instructions as ins

REPO = ins.REPO
BUILD = ins.BUILD
SET_NAME = 'Nobles & Common Folk at Quarrel'
THEME = {'lionhold': ('#b40000', '#f2c200'), 'millbrook': ('#2f6b2a', '#d8b56a'),
         'ravencrag': ('#19325a', '#9aa7b8'), 'warriors': ('#5f3109', '#c9a227')}

CSS = r"""
@page { size: A4 landscape; margin: 0; }
* { box-sizing: border-box; }
body { margin: 0; font-family: 'DejaVu Sans', Arial, sans-serif; color: #1b1b1b; background: #fff; }
.page { width: 297mm; height: 210mm; position: relative; overflow: hidden; page-break-after: always; padding: 9mm 11mm 12mm; }
.page:last-child { page-break-after: auto; }
.foot { position: absolute; bottom: 4mm; left: 11mm; right: 11mm; font-size: 8pt; color: #666; display: flex; justify-content: space-between; }
.band { position: absolute; left: 0; right: 0; top: 0; height: 5mm; background: var(--c1); }
.band2 { position: absolute; left: 0; right: 0; top: 5mm; height: 1.5mm; background: var(--c2); }
/* cover */
.cover { padding: 0; }
.cover .hero { position: absolute; inset: 0; background: #fff; }
.cover .hero img { width: 100%; height: 100%; object-fit: contain; }
.cover .title { position: absolute; left: 0; right: 0; top: 0; padding: 7mm 12mm 5mm; background: var(--c1); color: #fff; }
.cover .title h1 { margin: 0; font-size: 26pt; letter-spacing: .5pt; }
.cover .title h2 { margin: 1mm 0 0; font-size: 15pt; font-weight: normal; color: var(--c2); }
.cover .badge { position: absolute; right: 12mm; bottom: 10mm; background: var(--c1); color: #fff; border-radius: 3mm; padding: 4mm 6mm; text-align: right; }
.cover .badge b { font-size: 22pt; display: block; }
.cover .book { position: absolute; left: 12mm; bottom: 10mm; font-size: 13pt; color: var(--c1); font-weight: bold; }
/* inventory */
h3 { margin: 4mm 0 3mm; font-size: 15pt; color: var(--c1); }
.inv { display: grid; grid-template-columns: repeat(9, 1fr); gap: 2mm; }
.inv .cell { border: .3mm solid #ddd; border-radius: 1.5mm; padding: 1mm; text-align: center; font-size: 6.2pt; line-height: 1.15; height: 29mm; }
.inv .cell img { height: 15mm; max-width: 100%; object-fit: contain; }
.inv .q { font-size: 10pt; font-weight: bold; }
.inv .id { color: #555; }
/* steps */
.steps { display: grid; grid-template-columns: 1fr 1fr; gap: 6mm; height: 181mm; margin-top: 3mm; }
.steps.four { grid-template-columns: 1fr 1fr; grid-template-rows: 1fr 1fr; gap: 4mm; }
.step { border: .35mm solid #e2e2e2; border-radius: 2mm; position: relative; display: flex; flex-direction: column; padding: 2.5mm; }
.step .num { position: absolute; left: 3mm; top: 2mm; font-size: 24pt; font-weight: bold; color: #1b1b1b; }
.four .step .num { font-size: 16pt; }
.step .sec { margin-left: 16mm; min-height: 6mm; font-size: 9pt; font-weight: bold; color: var(--c1); }
.four .step .sec { margin-left: 11mm; }
.call { margin: 1mm 0 1.5mm 16mm; background: #f3f6fb; border: .3mm solid #c9d4e6; border-radius: 1.5mm; padding: 1mm 1.5mm;
        display: flex; flex-wrap: wrap; gap: 1mm 2.5mm; align-self: flex-start; max-width: calc(100% - 16mm); }
.four .call { margin-left: 11mm; max-width: calc(100% - 11mm); }
.call .p { display: flex; flex-direction: column; align-items: center; font-size: 7.5pt; font-weight: bold; }
.call .p img { height: 11mm; width: 11mm; object-fit: contain; }
.four .call .p img { height: 9mm; width: 9mm; }
.step .img { flex: 1; min-height: 0; display: flex; align-items: center; justify-content: center; }
.step .img img { max-width: 100%; max-height: 100%; object-fit: contain; }
/* text pages */
.txt { columns: 2; column-gap: 10mm; font-size: 10pt; line-height: 1.45; }
.txt h4 { margin: 0 0 1.5mm; color: var(--c1); font-size: 11pt; }
.txt p { margin: 0 0 3mm; }
.final img { width: 100%; height: 160mm; object-fit: contain; }
"""


def rel(p, base):
    return os.path.relpath(p, base)


def small(src, width=1000, quality=80):
    """Compressed copy of a step image for the PDF (keeps booklets small)."""
    from PIL import Image
    dst = src.replace(os.sep + 'steps' + os.sep, os.sep + 'steps_small' + os.sep)
    if not os.path.exists(dst) or os.path.getmtime(dst) < os.path.getmtime(src):
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        im = Image.open(src).convert('RGB')
        if im.width > width:
            im = im.resize((width, round(im.height * width / im.width)), Image.LANCZOS)
        im.save(dst, 'JPEG', quality=quality, optimize=True, progressive=True)
    return dst


def inventory_items(m):
    c = Counter()
    for p in m.parts:
        ld = p.ld[:-4] if p.ld.endswith('.dat') else p.ld
        if ld in ('3816b', '3817b'):
            continue
        if ld in ('3815b', '73200-f2'):
            c[('HIPSLEGS', p.color)] += 1
            continue
        if p.sub:
            continue
        c[(ld, p.color)] += 1
    return c


def part_label(ld):
    return '970c00' if ld == 'HIPSLEGS' else catalog.bl_id(ld)


def icon(ld, col):
    return os.path.join(BUILD, 'parts', ins.icon_name(ld, col))


def make(name, m, table, hero, extra_pages=None):
    info = ins.MODULES[name]
    c1, c2 = THEME[name]
    out_dir = os.path.join(BUILD, 'booklets')
    os.makedirs(out_dir, exist_ok=True)
    steps_dir = os.path.join(BUILD, 'steps', name)
    pages = []
    n_pieces = sum(inventory_items(m).values())
    foot = lambda n: f'<div class="foot"><span>{SET_NAME} &middot; Book {info["book"]} of 4 &middot; {html.escape(info["title"])}</span><span>{n}</span></div>'
    hero = small(hero, width=1600, quality=84)
    pages.append(f'''<div class="page cover"><div class="hero"><img src="{rel(hero, out_dir)}"></div>
      <div class="title"><h1>{SET_NAME.upper()}</h1><h2>Book {info["book"]} &middot; {html.escape(info["title"])} &mdash; {html.escape(info["subtitle"])}</h2></div>
      <div class="book">Building instructions</div>
      <div class="badge"><b>{n_pieces}</b>pieces &middot; {len(table)} steps</div></div>''')
    if extra_pages:
        pages += extra_pages
    # inventory
    inv = sorted(inventory_items(m).items(), key=lambda kv: (catalog.name(kv[0][0]) if kv[0][0] != 'HIPSLEGS' else 'Minifig Hips', kv[0][1]))
    per = 45
    for k in range(0, len(inv), per):
        cells = []
        for (ld, col), q in inv[k:k + per]:
            cells.append(f'<div class="cell"><img src="{rel(icon(ld, col), out_dir)}"><div class="q">{q}x</div>'
                         f'<div class="id">{part_label(ld)}</div><div>{html.escape(COLORS[col][2])}</div></div>')
        pages.append(f'<div class="page" style="--c1:{c1};--c2:{c2}"><div class="band"></div><div class="band2"></div>'
                     f'<h3>Parts for this book {"(continued)" if k else ""}</h3><div class="inv">{"".join(cells)}</div>{foot("Inventory")}</div>')
    # steps
    seen_sec = set()
    cards = []
    for t in table:
        sec = t['section']
        sec_html = html.escape(sec) if sec not in seen_sec else ''
        seen_sec.add(sec)
        callout = ''.join(f'<div class="p"><img src="{rel(icon(ld, col), out_dir)}">{q}x</div>'
                          for (ld, col), q in sorted(t['callout'].items(), key=lambda kv: (-kv[1], kv[0])))
        img = small(os.path.join(steps_dir, f'step_{t["step"] + 1:03d}.jpg'))
        cards.append((sec, f'<div class="step"><div class="num">{t["step"] + 1}</div><div class="sec">{sec_html}</div>'
                           f'<div class="call">{callout}</div><div class="img"><img src="{rel(img, out_dir)}"></div></div>'))
    four = name == 'warriors'
    per_page = 4 if four else 2
    i = 0
    while i < len(cards):
        chunk = [c for _, c in cards[i:i + per_page]]
        pages.append(f'<div class="page" style="--c1:{c1};--c2:{c2}"><div class="band"></div><div class="band2"></div>'
                     f'<div class="steps{" four" if four else ""}">{"".join(chunk)}</div>{foot(f"Steps {i + 1}-{min(i + per_page, len(cards))}")}</div>')
        i += per_page
    # final page
    nxt = {'lionhold': 'Continue with Book 2: Millbrook', 'millbrook': 'Continue with Book 3: Ravencrag Keep',
           'ravencrag': 'Continue with Book 4: Warriors & Weapons',
           'warriors': 'Set up the battle - see the diorama overview on the next page!'}[name]
    pages.append(f'<div class="page final" style="--c1:{c1};--c2:{c2}"><div class="band"></div><div class="band2"></div>'
                 f'<h3>{html.escape(info["title"])} is complete! &nbsp; <span style="font-weight:normal;color:#444">{nxt}</span></h3>'
                 f'<img src="{rel(hero, out_dir)}">{foot("")}</div>')
    if name == 'warriors':
        over = os.path.join(REPO, 'renders', 'diorama_overhead.jpg')
        clash = os.path.join(REPO, 'renders', 'battle_closeup.jpg')
        if os.path.exists(over):
            pages.append(f'<div class="page final" style="--c1:{c1};--c2:{c2}"><div class="band"></div><div class="band2"></div>'
                         f'<h3>Setting up the battle</h3>'
                         f'<p style="margin:0 0 3mm;font-size:10pt;max-width:250mm">Line the four baseplates up: Lionhold, Millbrook west, Millbrook east, Ravencrag. '
                         f'The Lion knights charge east along the road, the Raven knights charge west, and the villagers hold the barricade '
                         f'in the middle. Duke Aldric watches from the Lionhold gatehouse roof, Baroness Morwen from Ravencrag\'s. '
                         f'The archer and the crossbowman man the south wall-walks, and Brother Anselm stands in front of the barricade.</p>'
                         f'<img src="{rel(small(over, width=1800, quality=84), out_dir)}" style="height:140mm">{foot("Battle setup")}</div>')
        if os.path.exists(clash):
            pages.append(f'<div class="page final" style="--c1:{c1};--c2:{c2}"><div class="band"></div><div class="band2"></div>'
                         f'<h3>The quarrel at the barricade</h3><img src="{rel(small(clash, width=1800, quality=84), out_dir)}">{foot("")}</div>')
    doc = f'''<!doctype html><html><head><meta charset="utf-8"><title>{SET_NAME} - Book {info["book"]} - {html.escape(info["title"])}</title>
<style>{CSS}</style></head><body style="--c1:{c1};--c2:{c2}">{"".join(pages)}</body></html>'''
    path = os.path.join(out_dir, f'book{info["book"]}_{name}.html')
    with open(path, 'w') as fh:
        fh.write(doc)
    return path


def to_pdf(html_path, pdf_path):
    subprocess.run(['node', os.path.join(os.path.dirname(__file__), 'render', 'pdf.mjs'), html_path, pdf_path], check=True)
