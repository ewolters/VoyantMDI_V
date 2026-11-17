"""Tier 2 app, v6 on top of v5: the SQDC trend window follows the dates selected on the main screen.
  - new SELECTED window button (default every time the line view opens): START..END; a single day shows the 14 days ending on it
  - 7 / 14 / 30 / 40 stay as overrides
  - the header states the exact period the tiles, chart and Paretos cover
Usage: python3 app_v6.py Tier2_XB_v5.pa.yaml Tier2_XB_v6.pa.yaml
"""
import sys, re, yaml
src, dst = sys.argv[1], sys.argv[2]
y = open(src, encoding="utf-8").read()

def rep(old, new, count=1):
    global y
    assert y.count(old) == count, ("count", y.count(old), old[:120])
    y = y.replace(old, new)

def block(formula, ind):
    return "|-\n" + "\n".join(" " * ind + line for line in ("=" + formula).split("\n"))

def control(name, ctype, props, ind=0):
    p = " " * ind
    out = f"{p}- {name}:\n{p}    Control: {ctype}\n{p}    Properties:\n"
    for k, v in props.items():
        out += f"{p}      {k}: {block(str(v), ind + 8)}\n"
    return out

def topblock(name):
    a = y.index(f"\n- {name}:\n") + 1
    b = y.find("\n- ", a + 3)
    return a, (b + 1 if b >= 0 else len(y))

def setprop(name, prop, value):
    global y
    a, b = topblock(name)
    blk = y[a:b]
    new, n = re.subn(rf"(\n      {prop}: )(\|-\n\s+=.*|=.*)", lambda m: m.group(1) + "=" + value, blk, count=1)
    assert n == 1, (name, prop)
    y = y[:a] + new + y[b:]

# window: SELECTED (varTWSel) or a fixed number of days
rep("=If(IsBlank(varTW), Set(varTW, 30));\n        Set(varTW0, DateAdd(varTo, 1 - varTW, TimeUnit.Days));",
    "=If(IsBlank(varTWSel), Set(varTWSel, true));\n"
    "        If(varTWSel,\n"
    "          Set(varTW0, If(varFrom = varTo, DateAdd(varTo, -13, TimeUnit.Days), varFrom)); Set(varTW, DateDiff(varTW0, varTo, TimeUnit.Days) + 1),\n"
    "          Set(varTW0, DateAdd(varTo, 1 - Coalesce(varTW, 30), TimeUnit.Days)); Set(varTW, Coalesce(varTW, 30)));")
# every opening of the line view starts on the selected dates
rep('Set(varDTab, "O"); Set(varDet, true)', 'Set(varTWSel, true); Set(varDTab, "O"); Set(varDet, true)')
rep('Set(varDTab, Coalesce(varMetTab, "O")); If(varDTab <> "O", Select(btnLT)); Set(varDet, true)',
    'Set(varTWSel, true); Set(varDTab, Coalesce(varMetTab, "O")); If(varDTab <> "O", Select(btnLT)); Set(varDet, true)')
# fixed-length buttons switch SELECTED off; highlight only the active one
for n in (7, 14, 30, 40):
    rep(f"=Set(varTW, {n}); Select(btnLT)", f"=Set(varTWSel, false); Set(varTW, {n}); Select(btnLT)")
    rep(f"=If(varTW = {n}, RGBA(0, 72, 81, 1), RGBA(244, 244, 242, 1))", f"=If(!varTWSel && varTW = {n}, RGBA(0, 72, 81, 1), RGBA(244, 244, 242, 1))")
    rep(f"=If(varTW = {n}, RGBA(255, 255, 255, 1), RGBA(7, 39, 45, 1))", f"=If(!varTWSel && varTW = {n}, RGBA(255, 255, 255, 1), RGBA(7, 39, 45, 1))")
# layout: header 104..1104, WINDOW label, then SELECTED 7 14 30 40
setprop("lblLWin", "Width", "1000")
setprop("lblLWinT", "X", "1108"); setprop("lblLWinT", "Width", "94")
for i, n in enumerate((7, 14, 30, 40)):
    setprop(f"btnW{n}", "X", str(1332 + i * 122)); setprop(f"btnW{n}", "Width", "112")
sel = control("btnWSel", "Classic/Button@2.2.0", {
    "Text": '"SELECTED"', "OnSelect": "Set(varTWSel, true); Select(btnLT)",
    "Font": "Font.Arial", "Size": "10", "FontWeight": "FontWeight.Bold",
    "Fill": "If(varTWSel, RGBA(0, 72, 81, 1), RGBA(244, 244, 242, 1))", "Color": "If(varTWSel, RGBA(255, 255, 255, 1), RGBA(7, 39, 45, 1))",
    "HoverFill": "RGBA(230, 244, 244, 1)", "BorderColor": "RGBA(0, 72, 81, 1)", "BorderThickness": "1",
    "X": "1210", "Y": "144", "Width": "112", "Height": "38", "Visible": 'varDet && varDTab <> "O"',
    "Tooltip": '"The dates picked on the main screen (one day shows the 14 days ending on it)"'})
a, _ = topblock("btnW7")
y = y[:a] + sel + y[a:]
# header states the exact period
a, b = topblock("lblLWin")
blk = y[a:b]
old = '& "  ·  last " & varTW & " days to " & Text(varTo, "ddd m/d") &'
assert blk.count(old) == 1
blk = blk.replace(old, '& "  ·  " & Text(varTW0, "ddd m/d") & " – " & Text(varTo, "ddd m/d") & "  (" & varTW & " days" & '
                       'If(varTWSel, If(varFrom = varTo, ", ending on the selected day", ", the selected dates"), "") & ")" &')
y = y[:a] + blk + y[b:]
# shading only means something when the window is wider than the selection
for cell in ("TrSel", "O2Sel"):
    old = "=If(ThisItem.D >= varFrom && ThisItem.D <= varTo, RGBA(0, 178, 169, 0.14), RGBA(0, 0, 0, 0))"
    a = y.index(f"      - {cell}:\n"); b = y.index("      - ", a + 10)
    blk = y[a:b]; assert blk.count(old) == 1, cell
    y = y[:a] + blk.replace(old, "=If(ThisItem.D >= varFrom && ThisItem.D <= varTo && !(varTWSel && varFrom <> varTo), RGBA(0, 178, 169, 0.14), RGBA(0, 0, 0, 0))") + y[b:]
rep('& "     shaded = the dates selected on the main screen"',
    '& If(varTWSel && varFrom <> varTo, "", "     shaded = the dates selected on the main screen")')

open(dst, "w", encoding="utf-8").write(y)
doc = yaml.safe_load(open(dst, encoding="utf-8"))
names = []
def walk(lst):
    for it in lst:
        for k, v in it.items():
            names.append(k)
            for pk, pv in v["Properties"].items():
                f = str(pv); s = re.sub(r'"[^"]*"', '""', f)
                assert f.startswith("=") and s.count("(") == s.count(")") and s.count("{") == s.count("}") and f.count('"') % 2 == 0, (k, pk)
            if "Children" in v: walk(v["Children"])
walk(doc)
assert len(names) == len(set(names))
print("ok:", len(names), "controls")
