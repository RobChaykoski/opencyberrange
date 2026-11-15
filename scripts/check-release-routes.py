"""Compare the API surface of a built release against the source tree.

Stripping a tier removes routes on purpose, so a smaller number is expected.
What is not expected is a route disappearing because a tier symbol happened to
appear somewhere in its body: get_lab_details mentioned the SIEM panel in one
key of its response and the whole lab-detail endpoint went with it, which no
syntax check and no table count would ever notice.

Usage:
    python3 scripts/check-release-routes.py <source-tree> <release-tree>

Every route it lists under "NOT obviously tier" needs a human decision. Routes
belonging to a feature the release excludes on purpose (Exercise Studio) show
up here too, which is correct: the point is that a person confirms each one.
"""
import ast
import os
import re
import sys

dev, rel = sys.argv[1], sys.argv[2]
def routes(root):
    out = {}
    base = os.path.join(root, "platform/backend/app")
    for dirpath, dirs, files in os.walk(base):
        dirs[:] = [d for d in dirs if d != "__pycache__"]
        for fn in files:
            if not fn.endswith(".py"): continue
            fp = os.path.join(dirpath, fn)
            try:
                with open(fp, encoding="utf-8") as handle:
                    tree = ast.parse(handle.read())
            except (SyntaxError, UnicodeDecodeError, OSError):  # skip unparseable files
                continue
            for n in ast.walk(tree):
                if not isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)): continue
                for d in n.decorator_list:
                    if not isinstance(d, ast.Call): continue
                    f = d.func
                    if not (isinstance(f, ast.Attribute) and isinstance(f.value, ast.Name)
                            and f.value.id in ("router", "app")): continue
                    if d.args and isinstance(d.args[0], ast.Constant):
                        out[(f.attr.upper(), d.args[0].value, os.path.relpath(fp, base))] = n.name
    return out
a, b = routes(dev), routes(rel)
gone = sorted(set(a) - set(b))
print(f"dev routes: {len(a)} | lite routes: {len(b)} | removed: {len(gone)}")
TIER = re.compile(r"soc|siem|dfir|shared|wazuh|reboot|onion", re.IGNORECASE)
susp = [g for g in gone if not TIER.search(g[1] + a[g] + g[2])]
print(f"\nremoved but NOT obviously tier ({len(susp)}) -- these need a human look:")
for m, p, f in susp: print(f"   {m:<6} {p:<52} {f} :: {a[(m,p,f)]}")
