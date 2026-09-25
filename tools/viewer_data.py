"""Build the packed model + step data for the interactive web viewer."""
import json, os, sys
from collections import OrderedDict
import numpy as np
sys.path.insert(0, os.path.dirname(__file__))
import diorama, export, instructions as ins, warriors, pack, bom
from lego import Model

def lineup_model():
    m = Model('lineup', 'The cast')
    rows = {'lions': [], 'ravens': [], 'folk': []}
    for key, (f, faction, role) in warriors.FIGS.items():
        rows[faction].append((key, role))
    meta = []
    for r, faction in enumerate(('lions', 'folk', 'ravens')):
        for i, (key, role) in enumerate(rows[faction]):
            x = (i - (len(rows[faction]) - 1) / 2) * 70
            m.add_free(key + '.ldr', 16, [x, 0, r * 110], np.eye(3), sub=True)
            meta.append(dict(key=key, role=role, faction=faction))
    for i, (key, h) in enumerate(warriors.HORSES.items()):
        x = (i - 1.5) * 150
        pos = np.array([x, 0, -170.0])
        m.add_free(key + '.ldr', 16, pos, np.eye(3), sub=True)
        m.add_free(h['rider'] + '.ldr', 16, pos + warriors.RIDER_OFFSET, np.eye(3), sub=True)
    for i, key in enumerate(('lion_catapult', 'raven_catapult')):
        m.add_free(key + '.ldr', 16, [(i - 0.5) * 520 - 60, 0, -170.0], np.eye(3), sub=True)
    return m, meta

def main(out_dir):
    os.makedirs(out_dir, exist_ok=True)
    models = ins.build_all()
    subs = warriors.submodels()
    d, mods = diorama.build()
    lu, lu_meta = lineup_model()
    data = OrderedDict()
    texts = OrderedDict()
    texts['index'] = ['0 Nobles & Common Folk at Quarrel - index']
    info = {}
    for name in ('lionhold', 'millbrook', 'ravencrag'):
        m = models[name]
        lines, order, steps = m.main_lines()
        texts[name] = lines
        secs = sorted(set((m.parts[i].section, m.parts[i].step) for i in order), key=lambda t: t[1])
        first = OrderedDict()
        for sname, st in secs:
            first.setdefault(sname, st)
        info[name] = dict(steps=steps, sections=[[k, v] for k, v in first.items()], n=len(steps))
    d.compact_steps()
    dl, dorder, dsteps = d.main_lines()
    texts['diorama'] = dl
    lu.compact_steps()
    texts['lineup'] = lu.main_lines()[0]
    for k, v in subs.items():
        texts[k] = v
    size, nfiles = pack.pack(texts, os.path.join(out_dir, 'nobles_pack.txt'))
    info['lineup'] = dict(figures=lu_meta)
    with open(os.path.join(out_dir, 'viewer_data.json'), 'w') as fh:
        json.dump(info, fh)
    print('pack bytes', size, 'library files', nfiles)

if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else '/home/user/tres/build/viewer')
