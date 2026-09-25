"""Export helpers: write module LDraw files and render jobs."""
import json, os
from lego import Model

WWW = os.environ.get('NOBLES_WWW', '/home/user/tres_work/www/models')

def write_ldr(m, path, subs=None):
    m.compact_steps()
    lines, order, steps = m.main_lines()
    if subs:
        out = [f'0 FILE {m.name}.ldr'] + lines
        for k, v in subs.items():
            out += ['0 NOFILE', f'0 FILE {k}.ldr'] + v
        out.append('0 NOFILE')
        text = '\n'.join(out) + '\n'
    else:
        text = '\n'.join(lines) + '\n'
    with open(path, 'w') as fh:
        fh.write(text.replace('\n', '\r\n'))
    return order, steps

def job(url, steps, shots, size=(1200, 900)):
    return {'size': list(size), 'models': [{'url': url, 'steps': steps, 'shots': shots}]}
