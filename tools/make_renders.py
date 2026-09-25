"""Hero renders for the README / viewer poster (soft shadows)."""
import json, os, subprocess, sys
import numpy as np
sys.path.insert(0, os.path.dirname(__file__))
import diorama, export, instructions as ins, warriors, viewer_data

REPO = ins.REPO
OUT = os.path.join(REPO, 'renders')


def main():
    os.makedirs(OUT, exist_ok=True)
    subs = warriors.submodels()
    d, mods = diorama.build()
    order, steps = export.write_ldr(d, os.path.join(export.WWW, 'diorama.mpd'), subs=subs)
    parts = [d.parts[i] for i in order]
    # the clash on the road: knights, soldiers and the barricade (diorama x 33..95)
    battle = [li for li, p in enumerate(parts) if p.sub and 33 * 20 <= p.pos[0] <= 95 * 20]
    battle += [li for li, p in enumerate(parts) if p.section.startswith("millbrook: The commoners' barricade")]
    lu, _ = viewer_data.lineup_model()
    lorder, lsteps = export.write_ldr(lu, os.path.join(export.WWW, 'lineup.mpd'), subs=subs)
    jpg = lambda name: os.path.join(OUT, name)
    job = {'size': [2400, 1150], 'models': [
        {'url': '/models/diorama.mpd', 'steps': steps, 'shots': [
            {'out': jpg('diorama_hero.jpg'), 'fmt': 'jpg', 'yaw': 16, 'pitch': 24, 'pad': 1.02, 'bg': '#f2f4f6', 'shadows': True, 'size': [2400, 1150]},
            {'out': jpg('diorama_overhead.jpg'), 'fmt': 'jpg', 'yaw': 0, 'pitch': 58, 'pad': 1.02, 'bg': '#f2f4f6', 'shadows': True, 'size': [2400, 1000]},
            {'out': jpg('diorama_from_ravencrag.jpg'), 'fmt': 'jpg', 'yaw': -118, 'pitch': 22, 'pad': 1.02, 'bg': '#f2f4f6', 'shadows': True, 'size': [2000, 1100]},
            {'out': jpg('battle_closeup.jpg'), 'fmt': 'jpg', 'yaw': 22, 'pitch': 13, 'pad': 0.98, 'focus': battle, 'bg': '#f2f4f6', 'shadows': True, 'size': [2000, 1100]},
        ]},
        {'url': '/models/instr_lionhold.ldr', 'steps': None, 'shots': [
            {'out': jpg('lionhold.jpg'), 'fmt': 'jpg', 'yaw': 58, 'pitch': 24, 'pad': 1.03, 'bg': '#f2f4f6', 'shadows': True, 'size': [1600, 1200]}]},
        {'url': '/models/instr_millbrook.ldr', 'steps': None, 'shots': [
            {'out': jpg('millbrook.jpg'), 'fmt': 'jpg', 'yaw': 14, 'pitch': 30, 'pad': 1.03, 'bg': '#f2f4f6', 'shadows': True, 'size': [2000, 1100]}]},
        {'url': '/models/instr_ravencrag.ldr', 'steps': None, 'shots': [
            {'out': jpg('ravencrag.jpg'), 'fmt': 'jpg', 'yaw': -58, 'pitch': 24, 'pad': 1.03, 'bg': '#f2f4f6', 'shadows': True, 'size': [1600, 1200]}]},
        {'url': '/models/lineup.mpd', 'steps': None, 'shots': [
            {'out': jpg('the_cast.jpg'), 'fmt': 'jpg', 'yaw': 0, 'pitch': 16, 'pad': 1.02, 'bg': '#f2f4f6', 'shadows': True, 'size': [2000, 1100]}]},
    ]}
    for mdl in job['models']:
        if mdl['steps'] is None:
            del mdl['steps']
    path = os.path.join(ins.BUILD, 'job_heroes.json')
    json.dump(job, open(path, 'w'))
    subprocess.run(ins.RENDER + [path], check=True)


if __name__ == '__main__':
    main()
