"""Tier 2 app, v2 changes on top of the calendar version:
  1. date RANGE (default one day): varFrom/varTo replace varDate; calendar picks a start and an optional end; presets
  2. every metric cell on the floor (and the plant totals) opens a drill-down for that metric
  3. Board Notes button and overlay removed
Usage: python3 app_v2.py in.pa.yaml out.pa.yaml
"""
import sys, re, yaml
src, dst = sys.argv[1], sys.argv[2]
y = open(src, encoding="utf-8").read()

def rep(old, new, count=1):
    global y
    assert old in y, "MISSING: " + old[:100]
    y = y.replace(old, new, count)

def cut(start_marker, end_marker):
    """remove the top-level controls from start_marker up to (not including) end_marker"""
    global y
    a = y.index(start_marker); b = y.index(end_marker)
    y = y[:a] + y[b:]

def block(formula, ind):
    pad = " " * ind
    return "|-\n" + "\n".join(pad + line for line in ("=" + formula).split("\n"))

def control(name, ctype, props, ind=0, children=None, variant=None):
    p = " " * ind
    out = f"{p}- {name}:\n{p}    Control: {ctype}\n"
    if variant: out += f"{p}    Variant: {variant}\n"
    out += f"{p}    Properties:\n"
    for k, v in props.items():
        out += f"{p}      {k}: {block(v, ind + 8)}\n"
    if children:
        out += f"{p}    Children:\n" + "".join(children)
    return out

SF = '(ddShift.Selected.Value = "All" || Text(S) = ddShift.Selected.Value)'
RNG = "D >= varFrom && D <= varTo"
RTXT = 'If(varFrom = varTo, Text(varFrom, "dddd m/d"), Text(varFrom, "ddd m/d") & " – " & Text(varTo, "ddd m/d"))'
TEAL, DARK, LIGHT, GREY = "RGBA(0, 178, 169, 1)", "RGBA(7, 39, 45, 1)", "RGBA(244, 244, 242, 1)", "RGBA(117, 120, 123, 1)"
STFILL = 'Switch({x}, "G", RGBA(46, 160, 67, 1), "A", RGBA(210, 153, 34, 1), "R", RGBA(207, 34, 46, 1), RGBA(217, 217, 214, 1))'

# ---------- 3. Board Notes out ----------
cut("- btnWarn:\n", "- lblUpd:\n")
cut("- wDim:\n", "- cDim:\n")
y = re.sub(r"\n *ClearCollect\(colWarn,[^\n]*", "", y)
assert "colWarn" not in y and "varWarn" not in y

# ---------- 1. date range ----------
rep('Set(varDate, If(!IsBlank(varDate) && varDate in colDates.D, varDate, varD0))',
    'If(IsBlank(varFrom) || IsBlank(varTo), Set(varFrom, varD0); Set(varTo, varD0))')
y = y.replace("D = varDate", RNG)
y = re.sub(r"DateAdd\(varDate, (-\d), TimeUnit\.Days\)", r"DateAdd(varTo, \1, TimeUnit.Days)", y)
rep('SortByColumns(Filter(colRows, L = ThisItem.Line && ' + RNG + '), "S", SortOrder.Ascending)',
    'SortByColumns(Filter(colRows, L = ThisItem.Line && ' + RNG + '), "D", SortOrder.Descending, "S", SortOrder.Ascending)')
rep('Text: ="LINE " & varLine & "  ·  " & Text(varDate, "dddd m/d") & "  ·  from the Tier 1 board"',
    'Text: ="LINE " & varLine & "  ·  " & ' + RTXT + ' & "  ·  from the Tier 1 board"')
rep('Text: ="SHIFT " & ThisItem.S & "   "', 'Text: =Upper(Text(ThisItem.D, "ddd m/d")) & "  ·  SHIFT " & ThisItem.S & "   "')
# shift cards scroll when the range has more than two
_a = y.index("- galDetSh:\n"); _b = y.index("ShowScrollbar: =false", _a)
y = y[:_b] + "ShowScrollbar: =true" + y[_b + len("ShowScrollbar: =false"):]
rep('Text: ="Nothing entered on this board for the selected day."', 'Text: ="Nothing entered on this board for the selected dates."')
rep('Text: ="SHIFTS  ·  tap one for its hours"', 'Text: ="SHIFTS  ·  newest first  ·  tap one for its hours"')
# date button
a = y.index("- btnDate:\n"); b = y.index("- ddShift:\n")
y = y[:a] + control("btnDate", "Classic/Button@2.2.0", {
    "Text": 'If(IsBlank(varFrom), "NO DATES", If(varFrom = varTo, Text(varFrom, "ddd m/d/yyyy"), Text(varFrom, "m/d") & " – " & Text(varTo, "m/d/yy")))',
    "OnSelect": "Set(varCalM, Date(Year(Coalesce(varTo, Today())), Month(Coalesce(varTo, Today())), 1)); Set(varTmpFrom, Coalesce(varFrom, Today())); Set(varTmpTo, Coalesce(varTo, Today())); Set(varPick, 1); Set(varCal, true)",
    "Font": "Font.Arial", "Size": "13", "FontWeight": "FontWeight.Bold",
    "Fill": "RGBA(255, 255, 255, 1)", "Color": DARK, "HoverFill": "RGBA(230, 244, 244, 1)",
    "BorderColor": "RGBA(0, 72, 81, 1)", "BorderThickness": "2",
    "X": "730", "Y": "28", "Width": "180", "Height": "52",
    "Tooltip": '"Pick a day or a range. Days with board data are dark on the calendar."'}) + y[b:]
assert "varDate" not in y.split("- calShade:")[0], [l for l in y.split("- calShade:")[0].split("\n") if "varDate" in l]

# calendar: rebuild from calShade to the end
y = y[:y.index("- calShade:\n")]
RT = 'If(varTmpFrom = varTmpTo, Text(varTmpFrom, "ddd m/d"), Text(varTmpFrom, "m/d") & " – " & Text(varTmpTo, "m/d"))'
INR = "ThisItem.D >= varTmpFrom && ThisItem.D <= varTmpTo"
cal = control("calShade", "Rectangle@2.3.0", {"Fill": "RGBA(0, 0, 0, 0.35)", "OnSelect": "Set(varCal, false)",
        "X": "0", "Y": "0", "Width": "1920", "Height": "1080", "Visible": "varCal"})
cal += control("calPanel", "Rectangle@2.3.0", {"Fill": "RGBA(255, 255, 255, 1)", "BorderColor": "RGBA(0, 72, 81, 1)", "BorderThickness": "2",
        "X": "700", "Y": "88", "Width": "416", "Height": "548", "Visible": "varCal"})
navbtn = lambda n, t, step, x, extra=None: control(n, "Classic/Button@2.2.0", dict({"Text": f'"{t}"',
        "OnSelect": f"Set(varCalM, DateAdd(varCalM, {step}, TimeUnit.Months))", "Font": "Font.Arial", "Size": "18", "FontWeight": "FontWeight.Bold",
        "Fill": "RGBA(0, 72, 81, 1)", "Color": "RGBA(255, 255, 255, 1)", "X": str(x), "Y": "100", "Width": "56", "Height": "44", "Visible": "varCal"}, **(extra or {})))
cal += navbtn("calPrev", "<", -1, 712)
cal += control("calTitle", "Label@2.5.1", {"Text": 'Upper(Text(varCalM, "mmmm yyyy"))', "Font": "Font.Arial", "Size": "16", "FontWeight": "FontWeight.Bold",
        "Color": DARK, "Align": "Align.Center", "X": "768", "Y": "100", "Width": "280", "Height": "44", "Visible": "varCal"})
cal += navbtn("calNext", ">", 1, 1048, {"DisplayMode": "If(varCalM >= Date(Year(Today()), Month(Today()), 1), DisplayMode.Disabled, DisplayMode.Edit)"})
for i, dn in enumerate("SMTWTFS"):
    cal += control(f"calWd{i}", "Label@2.5.1", {"Text": f'"{dn}"', "Font": "Font.Arial", "Size": "12", "FontWeight": "FontWeight.Bold",
            "Color": GREY, "Align": "Align.Center", "X": str(712 + i * 56), "Y": "150", "Width": "56", "Height": "26", "Visible": "varCal"})
day = control("calDay", "Classic/Button@2.2.0", {
    "Text": "Text(Day(ThisItem.D))",
    "OnSelect": "If(varPick = 2 && ThisItem.D >= varTmpFrom, Set(varTmpTo, ThisItem.D); Set(varPick, 1), Set(varTmpFrom, ThisItem.D); Set(varTmpTo, ThisItem.D); Set(varPick, 2))",
    "DisplayMode": "If(ThisItem.D > Today(), DisplayMode.Disabled, DisplayMode.Edit)",
    "Font": "Font.Arial", "Size": "14", "FontWeight": "FontWeight.Bold",
    "Fill": f"If({INR}, {TEAL}, ThisItem.D in colDates.D, {DARK}, {LIGHT})",
    "Color": f"If({INR} || ThisItem.D in colDates.D, RGBA(255, 255, 255, 1), Month(ThisItem.D) = Month(varCalM), {GREY}, RGBA(205, 205, 205, 1))",
    "DisabledFill": LIGHT, "DisabledColor": "RGBA(205, 205, 205, 1)", "HoverFill": "RGBA(0, 178, 169, 0.75)",
    "BorderColor": "RGBA(255, 255, 255, 1)", "BorderThickness": "2",
    "X": "0", "Y": "0", "Width": "56", "Height": "50",
    "Tooltip": 'Text(ThisItem.D, "dddd m/d/yyyy") & If(ThisItem.D in colDates.D, "", " - no board data")'}, ind=6)
cal += control("galCal", "Gallery@2.15.0", {
    "Items": "ForAll(Sequence(42) As i, {D: DateAdd(varCalM, i.Value - Weekday(varCalM), TimeUnit.Days)})",
    "WrapCount": "7", "TemplateSize": "50", "TemplatePadding": "0", "ShowScrollbar": "false", "BorderThickness": "0",
    "TemplateFill": "RGBA(0, 0, 0, 0)", "X": "712", "Y": "178", "Width": "392", "Height": "300", "Visible": "varCal"},
    children=[day], variant="BrowseLayout_Vertical_TwoTextOneImageVariant_ver5.0")
cal += control("calNote", "Label@2.5.1", {"Text": '"Tap a day. Tap a later day to make it a range. Dark days have board data."',
        "Font": "Font.Arial", "Size": "11", "Color": GREY, "Align": "Align.Center", "X": "712", "Y": "482", "Width": "392", "Height": "34", "Visible": "varCal"})
presets = [("calPY", "YESTERDAY", "DateAdd(Today(), -1, TimeUnit.Days)", "DateAdd(Today(), -1, TimeUnit.Days)"),
           ("calP7", "LAST 7 DAYS", "DateAdd(Today(), -7, TimeUnit.Days)", "DateAdd(Today(), -1, TimeUnit.Days)"),
           ("calPM", "MONTH", "Date(Year(Today()), Month(Today()), 1)", "Today()"),
           ("calPL", "LATEST", "varD0", "varD0")]
for i, (n, t, f, to) in enumerate(presets):
    cal += control(n, "Classic/Button@2.2.0", {"Text": f'"{t}"',
        "OnSelect": f"Set(varTmpFrom, {f}); Set(varTmpTo, {to}); Set(varPick, 1); Set(varCalM, Date(Year(varTmpTo), Month(varTmpTo), 1))",
        "Font": "Font.Arial", "Size": "10", "FontWeight": "FontWeight.Bold", "Fill": LIGHT, "Color": DARK,
        "HoverFill": "RGBA(230, 244, 244, 1)", "BorderColor": "RGBA(0, 72, 81, 1)", "BorderThickness": "1",
        "X": str(712 + i * 100), "Y": "522", "Width": "92", "Height": "40", "Visible": "varCal"})
cal += control("calCancel", "Classic/Button@2.2.0", {"Text": '"CANCEL"', "OnSelect": "Set(varCal, false)", "Font": "Font.Arial", "Size": "12",
        "FontWeight": "FontWeight.Bold", "Fill": LIGHT, "Color": DARK, "BorderColor": "RGBA(0, 72, 81, 1)",
        "X": "712", "Y": "576", "Width": "120", "Height": "44", "Visible": "varCal"})
cal += control("calClose", "Classic/Button@2.2.0", {"Text": f'"SHOW " & Upper({RT})',
        "OnSelect": "Set(varFrom, varTmpFrom); Set(varTo, varTmpTo); Set(varCal, false); Select(btnCalc)",
        "Font": "Font.Arial", "Size": "12", "FontWeight": "FontWeight.Bold", "Fill": "RGBA(0, 72, 81, 1)", "Color": "RGBA(255, 255, 255, 1)",
        "BorderColor": "RGBA(0, 72, 81, 1)", "X": "844", "Y": "576", "Width": "260", "Height": "44", "Visible": "varCal"})

# ---------- 2. metric drill-downs ----------
ROWS = f'SortByColumns(Filter(colRows, L = ThisItem.Line && {RNG} && {SF}), "D", SortOrder.Descending, "S", SortOrder.Ascending)'
RS = f"Filter(colRows, L = ThisItem.Line && {RNG} && {SF})"
EMPTYB = 'Filter(Table({N: "", Q: 0}), false)'
def parse_b(col):   # "A~3|B~5" fields of the range -> {N, Q} by name, largest first
    return (f'SortByColumns(ForAll(GroupBy(ForAll(Filter(Split(Concat({RS}, {col}, "|"), "|"), !IsBlank(Value)) As p, '
            f'{{N: Index(Split(p.Value, "~"), 1).Value, M: Value(Index(Split(p.Value, "~"), 2).Value)}}), N, G) As g, {{N: g.N, Q: Sum(g.G, M)}}), "Q", SortOrder.Descending)')
SAFE_B = lambda s: f'Table({{N: "Recordable", Q: Coalesce(Sum({s}, SR), 0)}}, {{N: "First aid", Q: Coalesce(Sum({s}, SF), 0)}}, {{N: "Near miss", Q: Coalesce(Sum({s}, SN), 0)}})'
PCT = lambda a, b: f'Text({a} / {b} * 100, "0")'
M = {  # key: (title, row value text, row status, breakdown, breakdown title, summary)
 "S": ("SAFETY", '"Recordable " & r.SR & "     First aid " & r.SF & "     Near miss " & r.SN', 'If(r.SR > 0, "R", r.SF > 0, "A", "G")',
       SAFE_B(RS), "BY TYPE", '"Recordable " & ThisItem.SR & "  ·  First aid " & ThisItem.SF & "  ·  Near miss " & ThisItem.SN'),
 "Q": ("QUALITY · SCRAP", 'Text(r.Scrap, "#,##0") & " scrap" & If(r.Act > 0, "  ·  " & Text(r.Scrap / r.Act * 100, "0.0") & "% of " & Text(r.Act, "#,##0"), "") & If(IsBlank(r.SCR), "", "  ·  " & Substitute(Substitute(r.SCR, "~", " "), "|", ", "))',
       'If(r.Act = 0, "N", r.Scrap / r.Act * 100 >= varSR, "R", r.Scrap / r.Act * 100 >= varSA, "A", "G")',
       parse_b("SCR"), "BY COMPONENT", 'Text(ThisItem.Scrap, "#,##0") & " scrap on " & Text(ThisItem.Act, "#,##0") & " units" & If(ThisItem.Act > 0, "  ·  " & Text(ThisItem.Scrap / ThisItem.Act * 100, "0.00") & "%", "")'),
 "D": ("DELIVERY · UNITS VS TARGET", 'Text(r.Act, "#,##0") & " / " & Text(r.Tgt, "#,##0") & If(r.Tgt > 0, "  ·  " & ' + PCT("r.Act", "r.Tgt") + ' & "%", "  ·  no target")',
       'If(r.Tgt = 0, "N", r.Act / r.Tgt * 100 >= varEG, "G", r.Act / r.Tgt * 100 >= varEA, "A", "R")',
       EMPTYB, "", 'Text(ThisItem.Act, "#,##0") & " / " & Text(ThisItem.Tgt, "#,##0") & If(ThisItem.Tgt > 0, "  ·  " & ' + PCT("ThisItem.Act", "ThisItem.Tgt") + ' & "% efficiency", "")'),
 "DT": ("DOWNTIME", 'r.DT & " min" & If(IsBlank(r.DTR), "", "  ·  " & Substitute(Substitute(r.DTR, "~", " "), "|", " min, ") & " min")',
        'If(r.DT >= varDR, "R", r.DT >= varDA, "A", "G")', parse_b("DTR"), "BY REASON",
        'Text(ThisItem.DTU, "#,##0") & " min over " & ThisItem.Shifts & " shift(s)  ·  " & Text(ThisItem.DTs, "0") & " min per shift"'),
 "O": ("OEE (BOARD OEE ACTUAL %)", 'If(IsBlank(r.OEE), "–  (no Act. Speed on the board)", Text(r.OEE * 100, "0") & "%" & If(IsBlank(r.A) || IsBlank(r.P), "", "     A " & Text(r.A * 100, "0") & "  P " & Text(r.P * 100, "0") & "  Q " & Text(Coalesce(r.Q, 0) * 100, "0")))',
       'If(IsBlank(r.OEE), "N", r.OEE * 100 >= varOG, "G", r.OEE * 100 >= varOA, "A", "R")', EMPTYB, "",
       'If(IsBlank(ThisItem.OEE), "OEE –", "OEE " & Text(ThisItem.OEE, "0") & "%  (weighted by target across the shifts)")'),
 "P": ("PEOPLE · CREW (ACTUAL / STANDARD)", '"Crew " & If(IsBlank(r.CrA), "–", Text(r.CrA)) & " / " & If(IsBlank(r.CrS), "–", Text(r.CrS))',
       'If(Coalesce(r.CrA, 0) = 0 || Coalesce(r.CrS, 0) = 0, "N", r.CrA < r.CrS, "R", r.CrA > r.CrS, "A", "G")', EMPTYB, "",
       '"Crew " & ThisItem.CrA & " / " & ThisItem.CrS & "  (summed over the shifts)"'),
}
def open_line(key):
    t, v, st, b, bt, s = M[key]
    return (f'Set(varLine, ThisItem.Line); Set(varMetT, "LINE " & ThisItem.Line & "  ·  {t}"); Set(varMetB, "{bt}"); Set(varMetSum, {s});\n'
            f'ClearCollect(colMet, ForAll({ROWS} As r, {{K: Upper(Text(r.D, "ddd m/d")) & "  ·  SHIFT " & r.S, V: {v}, St: {st}}}));\n'
            (f'ClearCollect(colMetB, {b});' if b != EMPTYB else 'Clear(colMetB);') + '\nSet(varMetOpen, true)')
SEVEN = (f'Set(varLine, ThisItem.Line); Set(varMetT, "LINE " & ThisItem.Line & "  ·  EFFICIENCY, LAST 7 DAYS TO " & Upper(Text(varTo, "ddd m/d"))); Set(varMetB, ""); '
         f'Set(varMetSum, "Units vs target per day, shift filter applied");\n'
         f'ClearCollect(colMet, ForAll(Sequence(7) As k, With({{dd: DateAdd(varTo, 1 - k.Value, TimeUnit.Days)}}, With({{sh: Filter(colRows, L = ThisItem.Line && D = dd && {SF})}}, '
         f'{{K: Upper(Text(dd, "ddd m/d")), V: If(Coalesce(Sum(sh, Tgt), 0) > 0, Text(Sum(sh, Act), "#,##0") & " / " & Text(Sum(sh, Tgt), "#,##0") & "  ·  " & Text(Sum(sh, Act) / Sum(sh, Tgt) * 100, "0") & "%", "no data"), '
         f'St: If(Coalesce(Sum(sh, Tgt), 0) = 0, "N", Sum(sh, Act) / Sum(sh, Tgt) * 100 >= varEG, "G", Sum(sh, Act) / Sum(sh, Tgt) * 100 >= varEA, "A", "R")}}))));\n'
         'Clear(colMetB);\nSet(varMetOpen, true)')
H = "Max(34, Min(64, 820 / Max(1, CountRows(colFloor))))"
def hit(name, x, w, onselect, tip, ind=6):
    return control(name, "Classic/Button@2.2.0", {"Text": '""', "OnSelect": onselect, "Fill": "RGBA(0, 0, 0, 0)", "Color": "RGBA(255, 255, 255, 1)",
        "HoverFill": "RGBA(255, 255, 255, 0.18)", "PressedFill": "RGBA(255, 255, 255, 0.3)", "BorderColor": "RGBA(0, 0, 0, 0)",
        "X": str(x), "Y": "3", "Width": str(w), "Height": f"{H} - 6", "Tooltip": tip}, ind=ind)
DETAIL_OPEN = None
a = y.index("      - gHit:\n"); b = y.index("- totBar:\n")
ghit = y[a:b]
DETAIL_OPEN = re.search(r"OnSelect: \|-\n((?:              .*\n)+)", ghit).group(1)
DETAIL_OPEN = "\n".join(l[14:] for l in DETAIL_OPEN.rstrip("\n").split("\n"))   # formula text without the leading "="
DETAIL_OPEN = DETAIL_OPEN.lstrip("=")
cells = [("mS", 124, 120, "S", "Safety"), ("mQ", 250, 170, "Q", "Scrap"), ("mD", 426, 240, "D", "Units vs target"),
         ("mDT", 672, 230, "DT", "Downtime"), ("mO", 908, 100, "O", "OEE"), ("mP", 1014, 130, "P", "Crew")]
new = hit("lineHit", 0, 120, DETAIL_OPEN, '"Line " & ThisItem.Line & ": shifts, hour by hour, downtime and scrap"')
for n, x, w, k, tip in cells:
    new += hit(n, x, w, open_line(k), f'"{tip}, line " & ThisItem.Line')
new += hit("m7", 1150, 276, SEVEN, '"Efficiency by day, line " & ThisItem.Line')
y = y[:a] + new + y[b:]

# plant totals: one row per line
def open_plant(key):
    t = M[key][0]
    row = {"S": ('"Recordable " & f.SR & "     First aid " & f.SF & "     Near miss " & f.SN', "f.StS"),
           "Q": ('Text(f.Scrap, "#,##0") & " scrap" & If(f.Act > 0, "  ·  " & Text(f.Scrap / f.Act * 100, "0.0") & "%", "")', "f.StQ"),
           "D": ('Text(f.Act, "#,##0") & " / " & Text(f.Tgt, "#,##0") & If(f.Tgt > 0, "  ·  " & Text(f.Eff, "0") & "%", "")', "f.StD"),
           "DT": ('Text(f.DTU, "#,##0") & " min" & If(IsBlank(f.TopR), "", "  ·  top: " & f.TopR)', "f.StDT"),
           "O": ('If(IsBlank(f.OEE), "–", Text(f.OEE, "0") & "%")', "f.StO"),
           "P": ('If(f.CrS = 0 || f.CrA = 0, "–", f.CrA & " / " & f.CrS)', "f.StP")}[key]
    brk = {"S": SAFE_B("colFloor"),
           "Q": 'SortByColumns(ForAll(GroupBy(colScrRaw, I, G) As g, {N: g.I, Q: Sum(g.G, Q)}), "Q", SortOrder.Descending)',
           "DT": 'SortByColumns(ForAll(GroupBy(colParRaw, R, G) As g, {N: g.R, Q: Sum(g.G, M)}), "Q", SortOrder.Descending)'}.get(key, EMPTYB)
    bt = {"S": "BY TYPE", "Q": "BY COMPONENT", "DT": "BY REASON"}.get(key, "")
    return (f'Set(varLine, ""); Set(varMetT, "PLANT  ·  {t}"); Set(varMetB, "{bt}"); Set(varMetSum, "One row per line, " & varTot.Ran & " of " & varTot.Lines & " lines ran");\n'
            f'ClearCollect(colMet, ForAll(colFloor As f, {{K: "LINE " & f.Line, V: If(!f.Ran, "did not run", {row[0]}), St: {row[1]}}}));\n'
            (f'ClearCollect(colMetB, {brk});' if brk != EMPTYB else 'Clear(colMetB);') + '\nSet(varMetOpen, true)')
tot = ""
for n, x, w, k in [("tS", 140, 120, "S"), ("tQ", 266, 170, "Q"), ("tD", 442, 240, "D"), ("tDT", 688, 230, "DT"), ("tO", 924, 100, "O"), ("tP", 1030, 130, "P")]:
    tot += control(n, "Classic/Button@2.2.0", {"Text": '""', "OnSelect": open_plant(k), "Fill": "RGBA(0, 0, 0, 0)", "Color": "RGBA(255, 255, 255, 1)",
        "HoverFill": "RGBA(255, 255, 255, 0.15)", "PressedFill": "RGBA(255, 255, 255, 0.25)", "BorderColor": "RGBA(0, 0, 0, 0)",
        "X": str(x), "Y": "972", "Width": str(w), "Height": "88", "Tooltip": '"Every line, this metric"'})
rep('Text: ="Tap a line for its shifts, hour by hour and downtime."', 'Text: ="Tap any cell for its detail. Tap a line number for the full line view."')
y = y.replace("- lblEmpty:\n", tot + "- lblEmpty:\n", 1)

# the drill-down overlay (before the calendar, after everything else)
mrow = [control("mrBg", "Rectangle@2.3.0", {"Fill": LIGHT, "X": "0", "Y": "3", "Width": "820", "Height": "46"}, ind=6),
        control("mrK", "Label@2.5.1", {"Text": "ThisItem.K", "Font": "Font.Arial", "Size": "12", "FontWeight": "FontWeight.Bold", "Color": DARK,
                "Align": "Align.Left", "X": "14", "Y": "3", "Width": "220", "Height": "46"}, ind=6),
        control("mrV", "Label@2.5.1", {"Text": "ThisItem.V", "Font": "Font.Arial", "Size": "12", "Color": DARK, "Align": "Align.Left",
                "X": "240", "Y": "3", "Width": "520", "Height": "46", "Tooltip": "ThisItem.V"}, ind=6),
        control("mrSt", "Rectangle@2.3.0", {"Fill": STFILL.format(x="ThisItem.St"), "X": "772", "Y": "13", "Width": "34", "Height": "26"}, ind=6)]
brow = [control("mbN", "Label@2.5.1", {"Text": "ThisItem.N", "Font": "Font.Arial", "Size": "12", "Color": DARK, "Align": "Align.Left",
                "X": "0", "Y": "0", "Width": "260", "Height": "48", "Tooltip": "ThisItem.N"}, ind=6),
        control("mbQ", "Label@2.5.1", {"Text": 'Text(ThisItem.Q, "#,##0")', "Font": "Font.Arial", "Size": "12", "FontWeight": "FontWeight.Bold",
                "Color": DARK, "Align": "Align.Right", "X": "262", "Y": "0", "Width": "80", "Height": "48"}, ind=6),
        control("mbBar", "Rectangle@2.3.0", {"Fill": TEAL, "X": "352", "Y": "16",
                "Width": "Max(4, ThisItem.Q / Max(1, Max(colMetB, Q)) * 150)", "Height": "16"}, ind=6)]
V = "varMetOpen"
ov = control("mDim", "Rectangle@2.3.0", {"Fill": "RGBA(7, 39, 45, 0.55)", "OnSelect": "Set(varMetOpen, false)", "X": "0", "Y": "0", "Width": "1920", "Height": "1080", "Visible": V})
ov += control("mPanel", "Rectangle@2.3.0", {"Fill": "RGBA(255, 255, 255, 1)", "X": "260", "Y": "110", "Width": "1400", "Height": "860", "Visible": V})
ov += control("mHdr", "Rectangle@2.3.0", {"Fill": DARK, "X": "260", "Y": "110", "Width": "1400", "Height": "64", "Visible": V})
ov += control("mTitle", "Label@2.5.1", {"Text": f'varMetT & "  ·  " & {RTXT} & If(ddShift.Selected.Value = "All", "", "  ·  shift " & ddShift.Selected.Value)',
        "Font": "Font.Arial", "Size": "18", "FontWeight": "FontWeight.Bold", "Color": "RGBA(255, 255, 255, 1)", "Align": "Align.Left",
        "X": "284", "Y": "110", "Width": "1000", "Height": "64", "Visible": V})
ov += control("mFull", "Classic/Button@2.2.0", {"Text": '"FULL LINE VIEW"', "OnSelect": "Set(varMetOpen, false);\n" + DETAIL_OPEN.replace("Set(varLine, ThisItem.Line);\n", "").replace("ThisItem.Line", "varLine"),
        "Font": "Font.Arial", "Size": "12", "FontWeight": "FontWeight.Bold", "Fill": "RGBA(255, 255, 255, 1)", "Color": DARK, "BorderColor": "RGBA(255, 255, 255, 1)",
        "X": "1330", "Y": "120", "Width": "180", "Height": "44", "Visible": f'{V} && !IsBlank(varLine)'})
ov += control("mClose", "Classic/Button@2.2.0", {"Text": '"CLOSE"', "OnSelect": "Set(varMetOpen, false)", "Font": "Font.Arial", "Size": "12",
        "FontWeight": "FontWeight.Bold", "Fill": TEAL, "Color": "RGBA(255, 255, 255, 1)", "BorderColor": TEAL,
        "X": "1520", "Y": "120", "Width": "120", "Height": "44", "Visible": V})
ov += control("mSum", "Label@2.5.1", {"Text": "varMetSum", "Font": "Font.Arial", "Size": "15", "FontWeight": "FontWeight.Bold", "Color": DARK,
        "Align": "Align.Left", "X": "284", "Y": "186", "Width": "1350", "Height": "40", "Visible": V})
ov += control("galMet", "Gallery@2.15.0", {"Items": "colMet", "TemplateSize": "52", "TemplatePadding": "0", "ShowScrollbar": "true", "BorderThickness": "0",
        "TemplateFill": "RGBA(0, 0, 0, 0)", "X": "284", "Y": "236", "Width": "830", "Height": "716", "Visible": V},
        children=mrow, variant="BrowseLayout_Vertical_TwoTextOneImageVariant_ver5.0")
ov += control("mEmpty", "Label@2.5.1", {"Text": '"No shifts on the boards for these dates."', "Font": "Font.Arial", "Size": "15", "Color": GREY,
        "Align": "Align.Center", "X": "284", "Y": "400", "Width": "830", "Height": "60", "Visible": f"{V} && CountRows(colMet) = 0"})
ov += control("mBT", "Label@2.5.1", {"Text": "varMetB", "Font": "Font.Arial", "Size": "12", "FontWeight": "FontWeight.Bold", "Color": GREY,
        "Align": "Align.Left", "X": "1140", "Y": "236", "Width": "500", "Height": "30", "Visible": f"{V} && CountRows(colMetB) > 0"})
ov += control("galMetB", "Gallery@2.15.0", {"Items": "colMetB", "TemplateSize": "48", "TemplatePadding": "0", "ShowScrollbar": "true", "BorderThickness": "0",
        "TemplateFill": "RGBA(0, 0, 0, 0)", "X": "1140", "Y": "270", "Width": "510", "Height": "682", "Visible": f"{V} && CountRows(colMetB) > 0"},
        children=brow, variant="BrowseLayout_Vertical_TwoTextOneImageVariant_ver5.0")
y = y.rstrip("\n") + "\n" + ov + cal
open(dst, "w", encoding="utf-8").write(y)

# ---- sanity ----
doc = yaml.safe_load(open(dst, encoding="utf-8"))
names = []
def walk(lst):
    for it in lst:
        for k, v in it.items():
            names.append(k)
            for pk, pv in v["Properties"].items():
                assert str(pv).startswith("="), (k, pk, pv)
                f = str(pv)
                assert f.count("(") == f.count(")"), (k, pk, "parens")
                assert f.count("{") == f.count("}"), (k, pk, "braces")
                assert f.count('"') % 2 == 0, (k, pk, "quotes")
            if "Children" in v: walk(v["Children"])
walk(doc)
dupes = {n for n in names if names.count(n) > 1}
assert not dupes, dupes
for gone in ("varDate", "colWarn", "varWarn", "btnWarn", "gHit", "ddDate"):
    assert gone not in y, gone
print("ok:", len(names), "controls")
