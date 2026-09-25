"""Print a JSON map {reference name: path} of the LDraw library (speeds up three.js loading)."""
import json, os, sys
lib = os.environ['LDRAW_LIB']
m = {}
for d, pre in [('parts', ''), ('p', ''), ('models', ''), ('parts/s', 's/'), ('p/48', '48/'), ('p/8', '8/')]:
    full = os.path.join(lib, d)
    if os.path.isdir(full):
        for f in os.listdir(full):
            if f.lower().endswith('.dat'):
                m.setdefault(pre + f.lower(), d + '/' + f)
json.dump(m, sys.stdout)
