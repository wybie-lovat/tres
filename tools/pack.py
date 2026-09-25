"""Pack LDraw models + every library file they use into ONE self-contained .mpd
(so the web viewer needs no parts library)."""
import os, re
import ldgeom


def _canon(ref):
    """Name under which three.js LDrawLoader looks an embedded file up."""
    r = ref.strip().replace('\\', '/').lower()
    if r.startswith('s/'):
        return 'parts/' + r
    if r.startswith('48/'):
        return 'p/' + r
    return r


def _refs(text):
    for line in text.splitlines():
        t = line.split()
        if len(t) >= 15 and t[0] == '1':
            yield ' '.join(line.strip().split()[14:])


def pack(models, out_path):
    """models: OrderedDict name -> list of LDraw lines (first one is the main model)."""
    local = {k.lower() if k.endswith('.ldr') else (k + '.ldr').lower() for k in models}
    seen, order = set(), []
    stack = []
    for lines in models.values():
        stack += list(_refs('\n'.join(lines)))
    while stack:
        ref = stack.pop()
        key = ref.replace('\\', '/').lower()
        if key in local or _canon(ref) in seen:
            continue
        path = ldgeom.find(ref)
        if not path:
            print('missing', ref)
            continue
        seen.add(_canon(ref))
        with open(path, encoding='utf-8', errors='replace') as fh:
            text = fh.read()
        # rewrite sub-file references to their canonical embedded names
        out_lines = []
        for line in text.splitlines():
            t = line.split()
            if len(t) >= 15 and t[0] == '1':
                sub = ' '.join(t[14:])
                stack.append(sub)
                line = ' '.join(t[:14] + [_canon(sub)])
            elif t and t[0] == '0' and len(t) > 1 and t[1] in ('FILE', 'NOFILE'):
                continue
            out_lines.append(line)
        order.append((_canon(ref), '\n'.join(out_lines)))
    chunks = []
    for name, lines in models.items():
        fname = name if name.endswith('.ldr') else name + '.ldr'
        body = []
        for line in lines:
            t = line.split()
            if len(t) >= 15 and t[0] == '1':
                sub = ' '.join(t[14:])
                if sub.lower() not in local:
                    line = ' '.join(t[:14] + [_canon(sub)])
            body.append(line)
        chunks.append(f'0 FILE {fname}\n' + '\n'.join(body))
    for name, text in order:
        chunks.append(f'0 FILE {name}\n{text}')
    data = '\n'.join(chunks) + '\n'
    with open(out_path, 'w') as fh:
        fh.write(data)
    return len(data), len(order)
