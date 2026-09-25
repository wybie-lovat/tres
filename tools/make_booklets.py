"""Build the instruction booklets (HTML + PDF) from the rendered step images."""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
import instructions as ins, booklet

def main(only=None):
    models = ins.build_all()
    out = os.path.join(ins.REPO, 'instructions')
    os.makedirs(out, exist_ok=True)
    for name, m in models.items():
        if only and name not in only:
            continue
        lines, order, steps, table = ins.step_table(name, m)
        hero = os.path.join(ins.BUILD, 'steps', name, 'final.jpg')
        if name == 'warriors':
            hero = os.path.join(ins.REPO, 'renders', 'the_cast.jpg')
        h = booklet.make(name, m, table, hero)
        book = ins.MODULES[name]['book']
        pdf = os.path.join(out, f'book{book}_{name}.pdf')
        booklet.to_pdf(h, pdf)
        print(name, os.path.getsize(pdf) // 1024, 'KB')

if __name__ == '__main__':
    main(sys.argv[1:] or None)
