"""Data-source and loop checks for a .pa.yaml screen.

  - the first argument of Filter/LookUp/Patch/Collect/Remove/RemoveIf/UpdateIf/Sort/SortByColumns/
    CountRows/AddColumns/ShowColumns/Search/Defaults/Refresh/Distinct/CountIf/Sum/Max/Min/Average
    is a SharePoint list from newalbany/deploy/mdi_package.json, a collection (col...), a control
    (gal.../cmb.../dd...), a variable (var/loc...), a With() name, or an inline table/expression
    -> a typo such as HxH_Hourlyy is reported
  - Set() / UpdateContext() / Navigate() inside ForAll() (Studio refuses these)
Usage: python3 sources.py file.pa.yaml [...]   exit 1 if anything is reported
"""
import json, os, re, sys, yaml

HERE = os.path.dirname(os.path.abspath(__file__))
PKG = os.path.join(HERE, "..", "..", "deploy", "mdi_package.json")
LISTS = set(json.load(open(PKG, encoding="utf-8"))["schema"])
FUNCS = ("Filter|LookUp|Patch|Collect|ClearCollect|Remove|RemoveIf|UpdateIf|Sort|SortByColumns|CountRows|AddColumns|"
         "ShowColumns|DropColumns|Search|Defaults|Refresh|Distinct|CountIf|Sum|Max|Min|Average|First|Last|FirstN|LastN|GroupBy")
OK_PREFIX = ("col", "var", "loc", "gal", "cmb", "dd", "lst", "tbl", "_")

def close(s, i):
    """s[i] == '(' -> index of the matching ')' (skips strings and 'quoted names')."""
    d = 0; j = i
    while j < len(s):
        c = s[j]
        if c == '"':
            j = s.index('"', j + 1)
            while j + 1 < len(s) and s[j + 1] == '"': j = s.index('"', j + 2)
        elif c == "'": j = s.index("'", j + 1)
        elif c == "(": d += 1
        elif c == ")":
            d -= 1
            if d == 0: return j
        j += 1
    return len(s)

def check(name, prop, s, out):
    s = s[1:] if s.startswith("=") else s
    withnames = set(re.findall(r"With\(\s*\{\s*(\w+)\s*:", s)) | set(re.findall(r"[{,]\s*(\w+)\s*:", s)) \
        | set(re.findall(r"\bAs\s+(\w+)", s)) | set(re.findall(r'"(\w+)"', s))   # As-aliases, GroupBy/AddColumns names
    for m in re.finditer(r"(?<![\w.])(" + FUNCS + r")\(\s*([A-Za-z_]\w*)\s*[,)]", s):
        fn, src = m.group(1), m.group(2)
        if fn == "Collect" and src.startswith("col"): continue
        if src in LISTS or src.startswith(OK_PREFIX) or src in withnames: continue
        if src in ("Self", "Parent", "ThisItem", "ThisRecord", "Table", "Sequence", "Split", "Choices", "true", "false"): continue
        if src[0].islower() or len(src) <= 2: continue   # locals/aliases such as r, L, G
        out.append(f"{name}.{prop}: {fn}({src} ...): '{src}' is not a list in mdi_package.json")
    for m in re.finditer(r"(?<![\w.])ForAll\(", s):
        body = s[m.end() - 1: close(s, m.end() - 1) + 1]
        for bad in ("Set", "UpdateContext", "Navigate"):
            if re.search(r"(?<![\w.])" + bad + r"\(", body):
                out.append(f"{name}.{prop}: {bad}() inside ForAll() (Studio rejects it; collect into a collection and act after the loop)")

def walk(items, out):
    for it in items or []:
        for n, v in it.items():
            for k, p in (v.get("Properties") or {}).items():
                if isinstance(p, str): check(n, k, p, out)
            walk(v.get("Children"), out)

bad = 0
for f in sys.argv[1:]:
    out = []
    doc = yaml.safe_load(open(f, encoding="utf-8"))
    walk(doc if isinstance(doc, list) else [], out)
    for o in out: print("  " + o)
    bad += len(out)
print("sources issues:", bad)
sys.exit(1 if bad else 0)
