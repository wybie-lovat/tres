"""Assemble the complete diorama: 4 building modules side by side + the battle scene."""
import numpy as np
from lego import Model
import lionhold, millbrook, ravencrag, warriors

OFFSETS = {'lionhold': 0, 'millbrook': 32, 'ravencrag': 96}


def build_modules():
    return {'lionhold': lionhold.build(), 'millbrook': millbrook.build(), 'ravencrag': ravencrag.build()}


def merge(dst, src, ox):
    """Copy all placements of src into dst shifted by ox studs along x (grid + LDraw)."""
    base = len(dst.parts)
    for p in src.parts:
        q = type(p)()
        for a in type(p).__slots__:
            setattr(q, a, getattr(p, a))
        q.pos = p.pos + np.array([ox * 20, 0, 0])
        q.cells = [(c[0] + ox, c[1]) for c in p.cells]
        q.top_cells = {(c[0] + ox, c[1]) for c in p.top_cells}
        q.bottom_cells = {(c[0] + ox, c[1]) for c in p.bottom_cells}
        q.section = f'{src.name}: {p.section}'
        dst.parts.append(q)
    for (x, z, l), i in src.occ.items():
        dst.occ[(x + ox, z, l)] = base + i


def build(modules=None):
    modules = modules or build_modules()
    d = Model('nobles_and_common_folk', 'Nobles & Common Folk at Quarrel - complete diorama')
    for name, m in modules.items():
        merge(d, m, OFFSETS[name])
    d.new_section('Battle')
    placed = warriors.place_battle(d)
    for p in placed: print('  placed', p)
    return d, modules


if __name__ == '__main__':
    d, mods = build()
    print('diorama parts', len(d.parts))
