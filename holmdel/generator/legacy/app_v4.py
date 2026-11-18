"""Tier 2 app, v4 on top of v3: SQDC detail views inside the full line view.
  - header tabs: OVERVIEW (the v3 line view) | S SAFETY | Q QUALITY | D DELIVERY | C COST
  - every SQDC tab: trend window 7/14/30/40 days ending at the END date, 5 KPI tiles, a day-by-day trend chart
    (selected dates shaded, color levels drawn as lines), and two detail panels:
      S  safety cross (month calendar, green/amber/red per day) + event log
      Q  scrap Pareto by component (cumulative %) + worst shifts by scrap %
      D  hour-of-shift attainment + shift 1 vs shift 2, then the lowest shifts
      C  downtime Pareto by reason (cumulative %) + OEE by day
  - a metric drill-down's line button now opens the line view on the matching tab
Usage: python3 app_v4.py Tier2_XB_v3.pa.yaml Tier2_XB_v4.pa.yaml
"""
import sys, re, yaml
src, dst = sys.argv[1], sys.argv[2]
y = open(src, encoding="utf-8").read()

def rep(old, new, count=1):
    global y
    assert y.count(old) >= 1, "MISSING: " + old[:120]
    y = y.replace(old, new, count)

def block(formula, ind):
    pad = " " * ind
    return "|-\n" + "\n".join(pad + line for line in ("=" + formula).split("\n"))

def control(name, ctype, props, ind=0, children=None, variant=None):
    p = " " * ind
    out = f"{p}- {name}:\n{p}    Control: {ctype}\n"
    if variant: out += f"{p}    Variant: {variant}\n"
    out += f"{p}    Properties:\n"
    for k, v in props.items():
        out += f"{p}      {k}: {block(str(v), ind + 8)}\n"
    if children:
        out += f"{p}    Children:\n" + "".join(children)
    return out

def topblock(name):
    a = y.index(f"\n- {name}:\n") + 1
    b = y.find("\n- ", a + 3)
    return a, (b + 1 if b >= 0 else len(y))

GV = "BrowseLayout_Vertical_TwoTextOneImageVariant_ver5.0"
SFILT = '(ddShift.Selected.Value = "All" || Text(S) = ddShift.Selected.Value)'
TEAL, DARK, LIGHT, GREY, WHITE = "RGBA(0, 178, 169, 1)", "RGBA(7, 39, 45, 1)", "RGBA(244, 244, 242, 1)", "RGBA(117, 120, 123, 1)", "RGBA(255, 255, 255, 1)"
GREEN, AMBER, RED, NONE = "RGBA(46, 160, 67, 1)", "RGBA(210, 153, 34, 1)", "RGBA(207, 34, 46, 1)", "RGBA(217, 217, 214, 1)"
CLEAR = "RGBA(0, 0, 0, 0)"
STFILL = lambda x: f'Switch({x}, "G", {GREEN}, "A", {AMBER}, "R", {RED}, {NONE})'
SHIFTS = 'Upper(Text(r.D, "ddd m/d")) & "  ·  SHIFT " & r.S'
CTX = 'Trim(Coalesce(r.Prod, "") & If(IsBlank(r.WO), "", "   W/O " & r.WO) & If(IsBlank(r.Lead), "", "   " & r.Lead))'
LIST = lambda col, unit: f'Substitute(Substitute(r.{col}, "~", " "), "|", "{unit}, ") & "{unit}"'
TAB = "varDTab"
VIS = lambda *tabs: "varDet && " + ("(" + " || ".join(f'{TAB} = "{t}"' for t in tabs) + ")" if len(tabs) > 1 else f'{TAB} = "{tabs[0]}"')
SQDC = 'varDet && varDTab <> "O"'
TW = "Max(1, Coalesce(varTW, 30))"

# ---------- existing line view becomes the OVERVIEW tab ----------
a, _ = topblock("dShT"); b = y.index("\n- cDim:\n") + 1
seg = y[a:b]
n0 = seg.count("Visible: =varDet")
seg = seg.replace("Visible: =varDet", 'Visible: =varDet && varDTab = "O"')
assert n0 >= 10, n0
y = y[:a] + seg + y[b:]
# title shorter (tabs share the header)
a, b = topblock("dTitle")
blk = y[a:b]
blk = re.sub(r'\n      Text: =.*', '\n      Text: ="LINE " & varLine & "  ·  " & If(varFrom = varTo, Text(varFrom, "ddd m/d"), Text(varFrom, "m/d") & " – " & Text(varTo, "m/d"))', blk, count=1)
blk = blk.replace("      Width: =1400\n", "      Width: =700\n").replace("      Size: =20\n", "      Size: =18\n")
assert "Width: =700" in blk and "Size: =18" in blk
y = y[:a] + blk + y[b:]
# opening from a line number -> overview; from a metric drill-down -> that metric's tab
lh = y.index("      - lineHit:\n")
i = y.index("Set(varDet, true)", lh); assert i < y.index("      - mS:\n")
y = y[:i] + 'Set(varDTab, "O"); Set(varDet, true)' + y[i + len("Set(varDet, true)"):]
mf, mfe = topblock("mFull")
blk = y[mf:mfe]
assert blk.count("Set(varDet, true)") == 1
blk = blk.replace("Set(varDet, true)", 'Set(varDTab, Coalesce(varMetTab, "O")); If(varDTab <> "O", Select(btnLT)); Set(varDet, true)')
blk = blk.replace('="FULL LINE VIEW"', '=Switch(varMetTab, "S", "SAFETY VIEW  ›", "Q", "QUALITY VIEW  ›", "D", "DELIVERY VIEW  ›", "C", "COST VIEW  ›", "FULL LINE VIEW")')
y = y[:mf] + blk + y[mfe:]
for title, tab in [("SAFETY", "S"), ("QUALITY · SCRAP", "Q"), ("DELIVERY · UNITS VS TARGET", "D"), ("DOWNTIME", "C"),
                   ("OEE (BOARD OEE ACTUAL %)", "C"), ("PEOPLE · CREW (ACTUAL / STANDARD)", "C")]:
    rep(f'Set(varMetT, "LINE " & ThisItem.Line & "  ·  {title}");', f'Set(varMetTab, "{tab}"); Set(varMetT, "LINE " & ThisItem.Line & "  ·  {title}");')
rep('Set(varMetT, "LINE " & ThisItem.Line & "  ·  EFFICIENCY, LAST 7 DAYS TO "', 'Set(varMetTab, "D"); Set(varMetT, "LINE " & ThisItem.Line & "  ·  EFFICIENCY, LAST 7 DAYS TO "')
rep('Set(varLine, ""); Set(varMetT, "PLANT', 'Set(varLine, ""); Set(varMetTab, "O"); Set(varMetT, "PLANT', 6)
assert y.count('Set(varMetTab, "O"); Set(varMetT, "PLANT') == 6

# ---------- the calculation behind the SQDC tabs ----------
PARETO = lambda col, out: (   # same parsing as the plant Pareto (colParRaw), which is proven on Holmdel data
    f'ClearCollect({out}R, Ungroup(ForAll(colLR As r, {{X: ForAll(Filter(Split(Coalesce(r.{col}, ""), "|"), !IsBlank(Value)) As p, '
    f'{{R: Index(Split(p.Value, "~"), 1).Value, M: IfError(Value(Index(Split(p.Value, "~"), 2).Value), 0)}})}}), X));\n'
    f'ClearCollect({out}0, SortByColumns(AddColumns(GroupBy({out}R, R, G), Q, Sum(G, M)), "Q", SortOrder.Descending));\n'
    f'Set(var{out}T, Max(1, Coalesce(Sum({out}0, Q), 0)));\n'
    f'ClearCollect({out}, ForAll(Sequence(CountRows({out}0)) As i, With({{r: Index({out}0, i.Value)}}, With({{cum: Sum(FirstN({out}0, i.Value), Q) / var{out}T * 100}}, '
    f'{{N: r.R, Q: r.Q, Cum: cum, VF: cum - r.Q / var{out}T * 100 < 80}}))));\n')
AVGP = lambda c: f'If(CountRows(Filter(colLR, !IsBlank({c}))) = 0, Blank(), Average(Filter(colLR, !IsBlank({c})), {c}) * 100)'
LT = (
 'If(IsBlank(varTW), Set(varTW, 30));\n'
 'Set(varTW0, DateAdd(varTo, 1 - varTW, TimeUnit.Days));\n'
 'Set(varSM, Date(Year(varTo), Month(varTo), 1));\n'
 f'ClearCollect(colLR, Filter(colRows, L = varLine && D >= varTW0 && D <= varTo && {SFILT}));\n'
 'ClearCollect(colTr, ForAll(Sequence(varTW) As k, With({dd: DateAdd(varTW0, k.Value - 1, TimeUnit.Days)}, With({sh: Filter(colLR, D = dd)},\n'
 ' With({n: CountRows(sh), tg: Coalesce(Sum(sh, Tgt), 0), ac: Coalesce(Sum(sh, Act), 0), sc: Coalesce(Sum(sh, Scrap), 0), dt: Coalesce(Sum(sh, DT), 0),\n'
 '   sr: Coalesce(Sum(sh, SR), 0), sf: Coalesce(Sum(sh, SF), 0), sn: Coalesce(Sum(sh, SN), 0),\n'
 '   ow: Coalesce(Sum(Filter(sh, !IsBlank(OEE)), Tgt), 0), os: Coalesce(Sum(Filter(sh, !IsBlank(OEE)), OEE * Tgt), 0)},\n'
 '  {D: dd, N: n, Tgt: tg, Act: ac, Scrap: sc, DT: dt, SR: sr, SF: sf, SN: sn,\n'
 '   Ev: If(n = 0, Blank(), sr + sf + sn), Eff: If(tg > 0, ac / tg * 100, Blank()), SP: If(ac > 0, sc / ac * 100, Blank()),\n'
 '   DTs: If(n = 0, Blank(), dt / n), OEE: If(ow > 0, os / ow * 100, Blank()),\n'
 '   StS: If(n = 0, "N", sr > 0, "R", sf > 0, "A", "G"),\n'
 '   StQ: If(n = 0 || ac = 0, "N", sc / ac * 100 >= varSR, "R", sc / ac * 100 >= varSA, "A", "G"),\n'
 '   StD: If(tg = 0, "N", ac / tg * 100 >= varEG, "G", ac / tg * 100 >= varEA, "A", "R"),\n'
 '   StDT: If(n = 0, "N", dt / n >= varDR, "R", dt / n >= varDA, "A", "G"),\n'
 '   StO: If(ow = 0, "N", os / ow * 100 >= varOG, "G", os / ow * 100 >= varOA, "A", "R")})))));\n'
 'Set(varTS, {S: Max(2, Coalesce(Max(colTr, Ev), 0)), Q: Max(varSR * 1.5, Coalesce(Max(colTr, SP), 0)), D: Max(110, Coalesce(Max(colTr, Eff), 0)),\n'
 '  C: Max(varDR * 1.3, Coalesce(Max(colTr, DTs), 0)), O: Max(100, Coalesce(Max(colTr, OEE), 0))});\n'
 'Set(varLW, With({tg: Coalesce(Sum(colLR, Tgt), 0), ac: Coalesce(Sum(colLR, Act), 0), ca: Coalesce(Sum(colLR, CrA), 0),\n'
 '   ow: Coalesce(Sum(Filter(colLR, !IsBlank(OEE)), Tgt), 0), os: Coalesce(Sum(Filter(colLR, !IsBlank(OEE)), OEE * Tgt), 0)},\n'
 '  {N: CountRows(colLR), Tgt: tg, Act: ac, Scrap: Coalesce(Sum(colLR, Scrap), 0), DT: Coalesce(Sum(colLR, DT), 0),\n'
 '   SR: Coalesce(Sum(colLR, SR), 0), SF: Coalesce(Sum(colLR, SF), 0), SN: Coalesce(Sum(colLR, SN), 0),\n'
 '   Eff: If(tg > 0, ac / tg * 100, Blank()), SP: If(ac > 0, Coalesce(Sum(colLR, Scrap), 0) / ac * 100, Blank()), OEE: If(ow > 0, os / ow * 100, Blank()),\n'
 '   UPP: If(ca > 0, ac / ca, Blank()), AtT: CountIf(colLR, Tgt > 0 && Act >= Tgt), WithT: CountIf(colLR, Tgt > 0),\n'
 '   Short: CountIf(colLR, Coalesce(CrA, 0) > 0 && Coalesce(CrS, 0) > 0 && CrA < CrS), Staffed: CountIf(colLR, Coalesce(CrA, 0) > 0 && Coalesce(CrS, 0) > 0),\n'
 f'   A: {AVGP("A")}, P: {AVGP("P")}, Q: {AVGP("Q")}}}));\n'
 + PARETO("DTR", "colLDT") + PARETO("SCR", "colLSc") +
 'ClearCollect(colLH, ForAll(Sequence(8) As i, With({hs: Filter(ForAll(Filter(colLR, HT > 0) As r, {U: IfError(Value(Index(Split(r.H, ","), i.Value).Value), Blank()), T: r.HT}), !IsBlank(U))},\n'
 '  {Hr: i.Value, N: CountRows(hs), U: Coalesce(Sum(hs, U), 0), T: Coalesce(Sum(hs, T), 0), Pct: If(Coalesce(Sum(hs, T), 0) > 0, Sum(hs, U) / Sum(hs, T) * 100, Blank())})));\n'
 # right-hand lists
 'If(varDTab = "S", ClearCollect(colLL, ForAll(SortByColumns(Filter(colLR, Coalesce(SR, 0) + Coalesce(SF, 0) + Coalesce(SN, 0) > 0), "D", SortOrder.Descending, "S", SortOrder.Ascending) As r,\n'
 f'  {{K: {SHIFTS}, K2: {CTX}, V: "Recordable " & Coalesce(r.SR, 0) & "     First aid " & Coalesce(r.SF, 0) & "     Near miss " & Coalesce(r.SN, 0),\n'
 '   V2: "From the board\'s safety box", St: If(r.SR > 0, "R", r.SF > 0, "A", "G")})));\n'
 'If(varDTab = "Q", ClearCollect(colLL, ForAll(FirstN(SortByColumns(AddColumns(Filter(colLR, Act > 0 && Scrap > 0), Pc, Scrap / Act * 100), "Pc", SortOrder.Descending), 15) As r,\n'
 f'  {{K: {SHIFTS}, K2: {CTX}, V: Text(r.Pc, "0.00") & "% scrap  ·  " & Text(r.Scrap, "#,##0") & " of " & Text(r.Act, "#,##0") & " units",\n'
 f'   V2: If(IsBlank(r.SCR), "", {LIST("SCR", "")}), St: If(r.Pc >= varSR, "R", r.Pc >= varSA, "A", "G")}})));\n'
 'If(varDTab = "D",\n'
 '  ClearCollect(colLL, ForAll(Sort(Distinct(colLR, S), Value) As s, With({sh: Filter(colLR, S = s.Value)}, With({tg: Coalesce(Sum(sh, Tgt), 0), ac: Coalesce(Sum(sh, Act), 0), n: CountRows(sh), dt: Coalesce(Sum(sh, DT), 0), sc: Coalesce(Sum(sh, Scrap), 0)},\n'
 '   {K: "SHIFT " & s.Value & "  ·  ALL DAYS", K2: n & " shift(s) in the window", V: Text(ac, "#,##0") & " / " & Text(tg, "#,##0") & If(tg > 0, "  ·  " & Text(ac / tg * 100, "0") & "%", ""),\n'
 '    V2: "Downtime " & Text(dt / Max(1, n), "0") & " min per shift   ·   scrap " & If(ac > 0, Text(sc / ac * 100, "0.00") & "%", "–") & "   ·   " & CountIf(sh, Tgt > 0 && Act >= Tgt) & " of " & CountIf(sh, Tgt > 0) & " at target",\n'
 '    St: If(tg = 0, "N", ac / tg * 100 >= varEG, "G", ac / tg * 100 >= varEA, "A", "R")}))));\n'
 '  Collect(colLL, ForAll(FirstN(SortByColumns(AddColumns(Filter(colLR, Tgt > 0), Ef, Act / Tgt * 100), "Ef", SortOrder.Ascending), 10) As r,\n'
 f'   {{K: {SHIFTS}, K2: {CTX}, V: Text(r.Act, "#,##0") & " / " & Text(r.Tgt, "#,##0") & "  ·  " & Text(r.Ef, "0") & "%",\n'
 '    V2: "Hours: " & Substitute(r.H, ",", " · ") & "   ·   downtime " & Coalesce(r.DT, 0) & " min", St: If(r.Ef >= varEG, "G", r.Ef >= varEA, "A", "R")})));\n'
 'If(varDTab = "C", Clear(colLL));\n'
 # KPI tiles
 'If(varDTab = "S", ClearCollect(colKpi, With({lr: First(SortByColumns(Filter(colRows, L = varLine && SR > 0), "D", SortOrder.Descending)).D},\n'
 '  Table({L: "RECORDABLES", V: Text(varLW.SR), Sb: "logged in the window", St: If(varLW.SR > 0, "R", "G")},\n'
 '   {L: "FIRST AIDS", V: Text(varLW.SF), Sb: "logged in the window", St: If(varLW.SF > 0, "A", "G")},\n'
 '   {L: "NEAR MISSES", V: Text(varLW.SN), Sb: "logged in the window", St: "N"},\n'
 '   {L: "DAYS SINCE LAST RECORDABLE", V: If(IsBlank(lr), "–", Text(DateDiff(lr, Today(), TimeUnit.Days))),\n'
 '    Sb: If(IsBlank(lr), "none in the board data on file" & If(CountRows(colDates) > 0, " (since " & Text(Last(colDates).D, "m/d") & ")", ""), "last one " & Text(lr, "ddd m/d")), St: If(IsBlank(lr), "G", "N")},\n'
 '   {L: "GREEN DAYS", V: CountIf(colTr, StS = "G") & " of " & CountIf(colTr, N > 0), Sb: "days run with no first aid or recordable",\n'
 '    St: If(CountIf(colTr, N > 0) = 0, "N", CountIf(colTr, StS = "R") > 0, "R", CountIf(colTr, StS = "A") > 0, "A", "G")}))));\n'
 'If(varDTab = "Q", ClearCollect(colKpi, With({wd: First(SortByColumns(Filter(colTr, !IsBlank(SP)), "SP", SortOrder.Descending))},\n'
 '  Table({L: "SCRAP", V: Text(varLW.Scrap, "#,##0"), Sb: "on " & Text(varLW.Act, "#,##0") & " units", St: "N"},\n'
 '   {L: "SCRAP % OF UNITS", V: If(IsBlank(varLW.SP), "–", Text(varLW.SP, "0.00") & "%"), Sb: "amber " & varSA & "%   ·   red " & varSR & "%",\n'
 '    St: If(IsBlank(varLW.SP), "N", varLW.SP >= varSR, "R", varLW.SP >= varSA, "A", "G")},\n'
 '   {L: "DAYS RED / AMBER / GREEN", V: CountIf(colTr, StQ = "R") & " / " & CountIf(colTr, StQ = "A") & " / " & CountIf(colTr, StQ = "G"), Sb: "of " & CountIf(colTr, N > 0) & " days run", St: "N"},\n'
 '   {L: "WORST DAY", V: If(IsBlank(wd), "–", Text(wd.D, "ddd m/d")), Sb: If(IsBlank(wd), "", Text(wd.SP, "0.00") & "% scrap"), St: If(IsBlank(wd), "N", wd.StQ)},\n'
 '   {L: "TOP COMPONENT", V: Coalesce(First(colLSc).N, "–"),\n'
 '    Sb: If(CountRows(colLSc) = 0, "no scrap logged", Text(First(colLSc).Q, "#,##0") & "  ·  " & Text(First(colLSc).Q / Max(1, Sum(colLSc, Q)) * 100, "0") & "% of the scrap"), St: "N"}))));\n'
 'If(varDTab = "D", ClearCollect(colKpi, With({wh: First(SortByColumns(Filter(colLH, !IsBlank(Pct)), "Pct", SortOrder.Ascending))},\n'
 '  Table({L: "UNITS / TARGET", V: Text(varLW.Act, "#,##0") & " / " & Text(varLW.Tgt, "#,##0"), Sb: varLW.N & " shift(s)", St: "N"},\n'
 '   {L: "EFFICIENCY", V: If(IsBlank(varLW.Eff), "–", Text(varLW.Eff, "0") & "%"), Sb: "green " & varEG & "%   ·   amber " & varEA & "%",\n'
 '    St: If(IsBlank(varLW.Eff), "N", varLW.Eff >= varEG, "G", varLW.Eff >= varEA, "A", "R")},\n'
 '   {L: "SHIFTS AT TARGET", V: varLW.AtT & " of " & varLW.WithT, Sb: If(varLW.WithT > 0, Text(varLW.AtT / varLW.WithT * 100, "0") & "% of shifts", "no targets on the boards"), St: "N"},\n'
 '   {L: "WEAKEST HOUR OF SHIFT", V: If(IsBlank(wh), "–", "Hour " & wh.Hr), Sb: If(IsBlank(wh), "", Text(wh.Pct, "0") & "% of the hourly target"),\n'
 '    St: If(IsBlank(wh), "N", wh.Pct >= varEG, "G", wh.Pct >= varEA, "A", "R")},\n'
 '   {L: "DAYS GREEN", V: CountIf(colTr, StD = "G") & " of " & CountIf(colTr, Tgt > 0), Sb: "days at or above " & varEG & "%", St: "N"}))));\n'
 'If(varDTab = "C", ClearCollect(colKpi,\n'
 '  Table({L: "DOWNTIME", V: Text(varLW.DT, "#,##0") & " min", Sb: If(varLW.N > 0, Text(varLW.DT / varLW.N, "0") & " min per shift", ""),\n'
 '    St: If(varLW.N = 0, "N", varLW.DT / varLW.N >= varDR, "R", varLW.DT / varLW.N >= varDA, "A", "G")},\n'
 '   {L: "TOP DOWNTIME REASON", V: Coalesce(First(colLDT).N, "–"),\n'
 '    Sb: If(CountRows(colLDT) = 0, "no downtime logged", Text(First(colLDT).Q, "#,##0") & " min  ·  " & Text(First(colLDT).Q / Max(1, Sum(colLDT, Q)) * 100, "0") & "% of the minutes"), St: "N"},\n'
 '   {L: "OEE", V: If(IsBlank(varLW.OEE), "–", Text(varLW.OEE, "0") & "%"),\n'
 '    Sb: If(IsBlank(varLW.A), "no Act. Speed on these boards", "A " & Text(varLW.A, "0") & "   P " & Text(varLW.P, "0") & "   Q " & Text(Coalesce(varLW.Q, 0), "0")),\n'
 '    St: If(IsBlank(varLW.OEE), "N", varLW.OEE >= varOG, "G", varLW.OEE >= varOA, "A", "R")},\n'
 '   {L: "UNITS PER PERSON", V: If(IsBlank(varLW.UPP), "–", Text(varLW.UPP, "#,##0")), Sb: "per person per shift", St: "N"},\n'
 '   {L: "SHIFTS SHORT-STAFFED", V: varLW.Short & " of " & varLW.Staffed, Sb: "actual crew below standard", St: If(varLW.Staffed = 0, "N", varLW.Short > 0, "A", "G")})))')

new = control("btnLT", "Classic/Button@2.2.0", {"Text": '""', "OnSelect": LT, "X": "0", "Y": "0", "Width": "1", "Height": "1", "Visible": "false"})

# ---------- header tabs ----------
for i, (k, t) in enumerate([("O", "OVERVIEW"), ("S", "S · SAFETY"), ("Q", "Q · QUALITY"), ("D", "D · DELIVERY"), ("C", "C · COST")]):
    new += control(f"tab{k}", "Classic/Button@2.2.0", {"Text": f'"{t}"',
        "OnSelect": f'Set(varDTab, "{k}")' + ("" if k == "O" else "; Select(btnLT)"),
        "Font": "Font.Arial", "Size": "12", "FontWeight": "FontWeight.Bold",
        "Fill": f'If(varDTab = "{k}", {TEAL}, RGBA(255, 255, 255, 0.08))', "Color": WHITE,
        "HoverFill": "RGBA(0, 178, 169, 0.6)", "BorderColor": f'If(varDTab = "{k}", {TEAL}, RGBA(255, 255, 255, 0.35))', "BorderThickness": "1",
        "X": str(812 + i * 172), "Y": "80", "Width": "164", "Height": "44", "Visible": "varDet"})

# ---------- window row ----------
NAME = 'Switch(varDTab, "S", "SAFETY", "Q", "QUALITY", "D", "DELIVERY", "COST  ·  DOWNTIME, OEE, LABOR")'
new += control("lblLWin", "Label@2.5.1", {"Text": f'{NAME} & "  ·  last " & varTW & " days to " & Text(varTo, "ddd m/d") & If(ddShift.Selected.Value = "All", "  ·  all shifts", "  ·  shift " & ddShift.Selected.Value)',
    "Font": "Font.Arial", "Size": "13", "FontWeight": "FontWeight.Bold", "Color": DARK, "Align": "Align.Left", "Wrap": "false",
    "X": "104", "Y": "144", "Width": "1100", "Height": "38", "Visible": SQDC})
new += control("lblLWinT", "Label@2.5.1", {"Text": '"WINDOW"', "Font": "Font.Arial", "Size": "10", "FontWeight": "FontWeight.Bold", "Color": GREY,
    "Align": "Align.Right", "X": "1240", "Y": "144", "Width": "120", "Height": "38", "Visible": SQDC})
for i, n in enumerate([7, 14, 30, 40]):
    new += control(f"btnW{n}", "Classic/Button@2.2.0", {"Text": f'"{n} DAYS"', "OnSelect": f"Set(varTW, {n}); Select(btnLT)",
        "Font": "Font.Arial", "Size": "10", "FontWeight": "FontWeight.Bold",
        "Fill": f"If(varTW = {n}, RGBA(0, 72, 81, 1), {LIGHT})", "Color": f"If(varTW = {n}, {WHITE}, {DARK})",
        "HoverFill": "RGBA(230, 244, 244, 1)", "BorderColor": "RGBA(0, 72, 81, 1)", "BorderThickness": "1",
        "X": str(1370 + i * 112), "Y": "144", "Width": "104", "Height": "38", "Visible": SQDC,
        "Tooltip": f'"Trend window: the {n} days ending on the END date"'})

# ---------- KPI tiles ----------
kpi = [control("kBg", "Rectangle@2.3.0", {"Fill": LIGHT, "X": "0", "Y": "0", "Width": "332", "Height": "92"}, ind=6),
       control("kSt", "Rectangle@2.3.0", {"Fill": STFILL("ThisItem.St"), "X": "0", "Y": "0", "Width": "8", "Height": "92"}, ind=6),
       control("kL", "Label@2.5.1", {"Text": "ThisItem.L", "Font": "Font.Arial", "Size": "10", "FontWeight": "FontWeight.Bold", "Color": GREY,
               "Align": "Align.Left", "Wrap": "false", "X": "20", "Y": "4", "Width": "306", "Height": "24"}, ind=6),
       control("kV", "Label@2.5.1", {"Text": "ThisItem.V", "Font": "Font.Arial", "Size": "22", "FontWeight": "FontWeight.Bold", "Color": DARK,
               "Align": "Align.Left", "Wrap": "false", "X": "20", "Y": "26", "Width": "306", "Height": "40", "Tooltip": "ThisItem.V"}, ind=6),
       control("kSb", "Label@2.5.1", {"Text": "ThisItem.Sb", "Font": "Font.Arial", "Size": "10", "Color": GREY,
               "Align": "Align.Left", "Wrap": "false", "X": "20", "Y": "64", "Width": "306", "Height": "24", "Tooltip": "ThisItem.Sb"}, ind=6)]
new += control("galKpi", "Gallery@2.15.0", {"Items": "colKpi", "WrapCount": "5", "TemplateSize": "96", "TemplatePadding": "0", "ShowScrollbar": "false",
    "BorderThickness": "0", "TemplateFill": CLEAR, "X": "104", "Y": "190", "Width": "1712", "Height": "96", "Visible": SQDC},
    children=kpi, variant=GV)

# ---------- trend chart (one gallery, value by tab) ----------
def chart(prefix, x, y0, w, val, st, scale, fmt, vis, tip, small=False):
    cw = f"({w} / {TW})"
    v = f"({val})"
    bh = f'If(IsBlank({v}), 0, Max({2 if small else "If(varDTab = " + chr(34) + "S" + chr(34) + ", 6, 2)"}, Min(1, {v} / Max(0.0001, {scale})) * 190))'
    kids = [control(f"{prefix}Sel", "Rectangle@2.3.0", {"Fill": f"If(ThisItem.D >= varFrom && ThisItem.D <= varTo, RGBA(0, 178, 169, 0.14), {CLEAR})",
                    "X": "0", "Y": "0", "Width": f"{cw}", "Height": "248"}, ind=6),
            control(f"{prefix}Bar", "Rectangle@2.3.0", {"Fill": STFILL(st), "X": f"Min(3, {cw} * 0.1)", "Y": f"214 - {bh}",
                    "Width": f"Max(2, {cw} - 2 * Min(3, {cw} * 0.1))", "Height": bh}, ind=6),
            control(f"{prefix}Val", "Label@2.5.1", {"Text": f'If(IsBlank({v}), "", {fmt})', "Font": "Font.Arial", "Size": "8", "FontWeight": "FontWeight.Bold",
                    "Color": DARK, "Align": "Align.Center", "Wrap": "false", "X": "0", "Y": f"214 - {bh} - 18", "Width": cw, "Height": "16",
                    "Visible": f"!IsBlank({v}) && {cw} >= {26 if small else 30}"}, ind=6),
            control(f"{prefix}Day", "Label@2.5.1", {"Text": 'Text(ThisItem.D, "d")', "Font": "Font.Arial", "Size": "8" if small else "9",
                    "FontWeight": "If(Weekday(ThisItem.D) = 2, FontWeight.Bold, FontWeight.Normal)",
                    "Color": f"If(ThisItem.N = 0, RGBA(170, 170, 170, 1), {DARK})", "Align": "Align.Center", "Wrap": "false",
                    "X": "0", "Y": "216", "Width": cw, "Height": "28",
                    "Tooltip": f'Text(ThisItem.D, "dddd m/d") & ":  " & If(IsBlank({v}), "no board data", {fmt}) & "  ·  " & ThisItem.N & " shift(s)"'}, ind=6)]
    return control(f"gal{prefix}", "Gallery@2.15.0", {"Items": "colTr", "WrapCount": TW, "TemplateSize": "248", "TemplatePadding": "0",
        "ShowScrollbar": "false", "BorderThickness": "0", "TemplateFill": CLEAR, "X": str(x), "Y": str(y0), "Width": str(w), "Height": "248", "Visible": vis},
        children=kids, variant=GV)

VAL = 'Switch(varDTab, "S", ThisItem.Ev, "Q", ThisItem.SP, "D", ThisItem.Eff, ThisItem.DTs)'
STV = 'Switch(varDTab, "S", ThisItem.StS, "Q", ThisItem.StQ, "D", ThisItem.StD, ThisItem.StDT)'
SCALE = 'Switch(varDTab, "S", varTS.S, "Q", varTS.Q, "D", varTS.D, varTS.C)'
FMTV = f'Switch(varDTab, "Q", Text({VAL}, "0.0") & "%", "D", Text({VAL}, "0") & "%", "S", Text({VAL}, "0"), Text({VAL}, "0") & " min")'
TRT = ('Switch(varDTab, "S", "SAFETY EVENTS PER DAY  ·  recordable + first aid + near miss  ·  bar color = worst event that day", '
       '"Q", "SCRAP % OF UNITS, BY DAY", "D", "EFFICIENCY % (UNITS VS TARGET), BY DAY", "DOWNTIME MINUTES PER SHIFT, BY DAY") & "     shaded = the dates selected on the main screen"')
new += control("lblTrT", "Label@2.5.1", {"Text": TRT, "Font": "Font.Arial", "Size": "11", "FontWeight": "FontWeight.Bold", "Color": GREY,
    "Align": "Align.Left", "Wrap": "false", "X": "104", "Y": "298", "Width": "1712", "Height": "26", "Visible": SQDC})
new += control("galTrBg", "Rectangle@2.3.0", {"Fill": "RGBA(250, 250, 248, 1)", "X": "104", "Y": "326", "Width": "1712", "Height": "248", "Visible": SQDC})
new += chart("Tr", 104, 326, 1712, VAL, STV, SCALE, FMTV, SQDC, "")
new += control("trBase", "Rectangle@2.3.0", {"Fill": "RGBA(190, 190, 186, 1)", "X": "104", "Y": "540", "Width": "1712", "Height": "1", "Visible": SQDC})
# level lines
T1 = 'Switch(varDTab, "Q", varSA, "D", varEG, "C", varDA, Blank())'
T2 = 'Switch(varDTab, "Q", varSR, "D", varEA, "C", varDR, Blank())'
C1 = f'Switch(varDTab, "D", {GREEN}, {AMBER})'
C2 = f'Switch(varDTab, "D", {AMBER}, {RED})'
L1 = 'Switch(varDTab, "Q", "amber " & varSA & "%", "D", "green " & varEG & "%", "amber " & varDA & " min")'
L2 = 'Switch(varDTab, "Q", "red " & varSR & "%", "D", "amber " & varEA & "%", "red " & varDR & " min")'
for n, t, c, l in [("trL1", T1, C1, L1), ("trL2", T2, C2, L2)]:
    yy = f"326 + 214 - Min(1, {t} / Max(0.0001, {SCALE})) * 190"
    new += control(n, "Rectangle@2.3.0", {"Fill": c, "X": "104", "Y": f"{yy} - 1", "Width": "1712", "Height": "2",
        "Visible": f'{SQDC} && varDTab <> "S" && !IsBlank({t})'})
    new += control(n + "T", "Label@2.5.1", {"Text": l, "Font": "Font.Arial", "Size": "9", "FontWeight": "FontWeight.Bold", "Color": c,
        "Align": "Align.Right", "Wrap": "false", "X": "1656", "Y": f"{yy} - 18", "Width": "160", "Height": "16",
        "Visible": f'{SQDC} && varDTab <> "S" && !IsBlank({t})'})

# ---------- lower panels: titles ----------
BL = ('Switch(varDTab, "S", "SAFETY CROSS  ·  " & Upper(Text(varSM, "mmmm yyyy")), "Q", "SCRAP BY COMPONENT  ·  PARETO OVER THE WINDOW", '
      '"D", "HOUR OF SHIFT  ·  UNITS VS HOURLY TARGET OVER THE WINDOW", "DOWNTIME BY REASON  ·  PARETO OVER THE WINDOW")')
BR = ('Switch(varDTab, "S", "SAFETY EVENTS IN THE WINDOW  ·  newest first", "Q", "WORST SHIFTS BY SCRAP %", '
      '"D", "SHIFT 1 VS SHIFT 2, THEN THE LOWEST SHIFTS", "OEE % BY DAY  ·  the board\'s OEE Actual")')
new += control("lblBL", "Label@2.5.1", {"Text": BL, "Font": "Font.Arial", "Size": "11", "FontWeight": "FontWeight.Bold", "Color": GREY,
    "Align": "Align.Left", "Wrap": "false", "X": "104", "Y": "600", "Width": "600", "Height": "34", "Visible": SQDC})
new += control("lblBR", "Label@2.5.1", {"Text": BR, "Font": "Font.Arial", "Size": "11", "FontWeight": "FontWeight.Bold", "Color": GREY,
    "Align": "Align.Left", "Wrap": "false", "X": "986", "Y": "600", "Width": "830", "Height": "34", "Visible": SQDC})

# ---------- S: safety cross ----------
VS_ = VIS("S")
for n, t, step, x in [("scPrev", "<", -1, 724), ("scNext", ">", 1, 776)]:
    new += control(n, "Classic/Button@2.2.0", {"Text": f'"{t}"', "OnSelect": f"Set(varSM, DateAdd(varSM, {step}, TimeUnit.Months))",
        "Font": "Font.Arial", "Size": "14", "FontWeight": "FontWeight.Bold", "Fill": "RGBA(0, 72, 81, 1)", "Color": WHITE,
        "X": str(x), "Y": "600", "Width": "44", "Height": "34", "Visible": VS_,
        **({"DisplayMode": "If(varSM >= Date(Year(Today()), Month(Today()), 1), DisplayMode.Disabled, DisplayMode.Edit)"} if step > 0 else {})})
for i, dn in enumerate("SMTWTFS"):
    new += control(f"scWd{i}", "Label@2.5.1", {"Text": f'"{dn}"', "Font": "Font.Arial", "Size": "10", "FontWeight": "FontWeight.Bold", "Color": GREY,
        "Align": "Align.Center", "X": f"104 + {i} * 830 / 7", "Y": "638", "Width": "830 / 7", "Height": "24", "Visible": VS_})
SCW = "(830 / 7)"
scfill = (f'If(Month(ThisItem.D) <> Month(varSM), {CLEAR}, ThisItem.D > Today(), RGBA(250, 250, 248, 1), ThisItem.N = 0, {NONE}, '
          f'ThisItem.SR > 0, {RED}, ThisItem.SF > 0, {AMBER}, {GREEN})')
sckids = [control("scBg", "Rectangle@2.3.0", {"Fill": scfill, "X": "3", "Y": "3", "Width": f"{SCW} - 6", "Height": "46"}, ind=6),
          control("scDay", "Label@2.5.1", {"Text": "Text(Day(ThisItem.D))", "Font": "Font.Arial", "Size": "13", "FontWeight": "FontWeight.Bold",
                  "Color": f"If(Month(ThisItem.D) <> Month(varSM), RGBA(205, 205, 205, 1), ThisItem.N = 0 || ThisItem.D > Today(), {GREY}, {WHITE})",
                  "Align": "Align.Center", "X": "3", "Y": "3", "Width": f"{SCW} - 6", "Height": "46",
                  "Tooltip": ('Text(ThisItem.D, "dddd m/d") & ":  " & If(ThisItem.N = 0, "no board data", "recordable " & ThisItem.SR & ", first aid " & ThisItem.SF & '
                              '", near miss " & ThisItem.SN & "  ·  " & ThisItem.N & " shift(s)")')}, ind=6),
          control("scNM", "Label@2.5.1", {"Text": 'If(ThisItem.SN > 0, "NM " & ThisItem.SN, "")', "Font": "Font.Arial", "Size": "8", "FontWeight": "FontWeight.Bold",
                  "Color": WHITE, "Align": "Align.Right", "Wrap": "false", "X": "3", "Y": "30", "Width": f"{SCW} - 12", "Height": "18",
                  "Visible": "Month(ThisItem.D) = Month(varSM) && ThisItem.SN > 0"}, ind=6)]
SCITEMS = (f'ForAll(Sequence(42) As i, With({{dd: DateAdd(varSM, i.Value - Weekday(varSM), TimeUnit.Days)}}, '
           f'With({{sh: Filter(colRows, L = varLine && D = dd && {SFILT})}}, '
           '{D: dd, N: CountRows(sh), SR: Coalesce(Sum(sh, SR), 0), SF: Coalesce(Sum(sh, SF), 0), SN: Coalesce(Sum(sh, SN), 0)})))')
new += control("galSC", "Gallery@2.15.0", {"Items": SCITEMS, "WrapCount": "7", "TemplateSize": "52", "TemplatePadding": "0", "ShowScrollbar": "false",
    "BorderThickness": "0", "TemplateFill": CLEAR, "X": "104", "Y": "664", "Width": "830", "Height": "312", "Visible": VS_}, children=sckids, variant=GV)
new += control("scLeg", "Label@2.5.1", {"Text": '"Green: ran, no first aid or recordable   ·   Amber: first aid   ·   Red: recordable   ·   Grey: no board data   ·   NM = near misses"',
    "Font": "Font.Arial", "Size": "9", "Color": GREY, "Align": "Align.Left", "Wrap": "false", "X": "104", "Y": "980", "Width": "830", "Height": "24", "Visible": VS_})

# ---------- Q / C: Pareto ----------
VPA = VIS("Q", "C")
PITEMS = 'If(varDTab = "Q", colLSc, colLDT)'
PMAX = 'Max(1, If(varDTab = "Q", Max(colLSc, Q), Max(colLDT, Q)))'
pakids = [control("paRow", "Rectangle@2.3.0", {"Fill": f"If(ThisItem.VF, RGBA(0, 178, 169, 0.10), {CLEAR})", "X": "0", "Y": "2", "Width": "820", "Height": "38"}, ind=6),
          control("paN", "Label@2.5.1", {"Text": "ThisItem.N", "Font": "Font.Arial", "Size": "11", "FontWeight": "FontWeight.Bold", "Color": DARK,
                  "Align": "Align.Left", "Wrap": "false", "X": "8", "Y": "2", "Width": "250", "Height": "38", "Tooltip": "ThisItem.N"}, ind=6),
          control("paBg", "Rectangle@2.3.0", {"Fill": "RGBA(236, 236, 234, 1)", "X": "264", "Y": "13", "Width": "360", "Height": "16"}, ind=6),
          control("paBar", "Rectangle@2.3.0", {"Fill": f'If(varDTab = "Q", {AMBER}, {RED})', "X": "264", "Y": "13",
                  "Width": f"Max(3, 360 * ThisItem.Q / {PMAX})", "Height": "16"}, ind=6),
          control("paQ", "Label@2.5.1", {"Text": 'Text(ThisItem.Q, "#,##0") & If(varDTab = "C", " min", "")', "Font": "Font.Arial", "Size": "11",
                  "FontWeight": "FontWeight.Bold", "Color": DARK, "Align": "Align.Right", "Wrap": "false", "X": "628", "Y": "2", "Width": "96", "Height": "38"}, ind=6),
          control("paCum", "Label@2.5.1", {"Text": 'Text(ThisItem.Cum, "0") & "%"', "Font": "Font.Arial", "Size": "10", "Color": GREY,
                  "Align": "Align.Right", "Wrap": "false", "X": "728", "Y": "2", "Width": "84", "Height": "38", "Tooltip": '"Cumulative share"'}, ind=6)]
new += control("paHdr", "Label@2.5.1", {"Text": '"Shaded rows = the few that make up 80% of the total.   Right: quantity, then cumulative %."',
    "Font": "Font.Arial", "Size": "9", "Color": GREY, "Align": "Align.Left", "Wrap": "false", "X": "112", "Y": "638", "Width": "820", "Height": "22", "Visible": VPA})
new += control("galPa", "Gallery@2.15.0", {"Items": PITEMS, "TemplateSize": "42", "TemplatePadding": "0", "ShowScrollbar": "true", "BorderThickness": "0",
    "TemplateFill": CLEAR, "X": "104", "Y": "662", "Width": "830", "Height": "340", "Visible": VPA}, children=pakids, variant=GV)
new += control("paEmpty", "Label@2.5.1", {"Text": 'If(varDTab = "Q", "No scrap logged in the window.", "No downtime logged in the window.")',
    "Font": "Font.Arial", "Size": "13", "Color": GREY, "Align": "Align.Center", "X": "104", "Y": "760", "Width": "830", "Height": "50",
    "Visible": f"{VPA} && CountRows({PITEMS}) = 0"})

# ---------- D: hour of shift ----------
VD_ = VIS("D")
lhkids = [control("lhN", "Label@2.5.1", {"Text": '"HOUR " & ThisItem.Hr', "Font": "Font.Arial", "Size": "11", "FontWeight": "FontWeight.Bold", "Color": DARK,
                  "Align": "Align.Left", "X": "8", "Y": "2", "Width": "90", "Height": "38"}, ind=6),
          control("lhBg", "Rectangle@2.3.0", {"Fill": "RGBA(236, 236, 234, 1)", "X": "104", "Y": "11", "Width": "540", "Height": "20"}, ind=6),
          control("lhBar", "Rectangle@2.3.0", {"Fill": f"If(IsBlank(ThisItem.Pct), {NONE}, ThisItem.Pct >= varEG, {GREEN}, ThisItem.Pct >= varEA, {AMBER}, {RED})",
                  "X": "104", "Y": "11", "Width": "If(IsBlank(ThisItem.Pct), 0, 540 * Min(1, ThisItem.Pct / 130))", "Height": "20"}, ind=6),
          control("lhTgt", "Rectangle@2.3.0", {"Fill": DARK, "X": "104 + 540 * 100 / 130 - 1", "Y": "5", "Width": "3", "Height": "32"}, ind=6),
          control("lhV", "Label@2.5.1", {"Text": 'If(IsBlank(ThisItem.Pct), "nothing entered", Text(ThisItem.Pct, "0") & "%   ·   avg " & Text(ThisItem.U / Max(1, ThisItem.N), "#,##0") & " / hr")',
                  "Font": "Font.Arial", "Size": "10", "FontWeight": "FontWeight.Bold", "Color": DARK, "Align": "Align.Right", "Wrap": "false",
                  "X": "650", "Y": "2", "Width": "170", "Height": "38",
                  "Tooltip": '"Hour " & ThisItem.Hr & ":  " & Text(ThisItem.U, "#,##0") & " units vs " & Text(ThisItem.T, "#,##0") & " target over " & ThisItem.N & " shift(s)"'}, ind=6)]
new += control("galLH", "Gallery@2.15.0", {"Items": "colLH", "TemplateSize": "42", "TemplatePadding": "0", "ShowScrollbar": "false", "BorderThickness": "0",
    "TemplateFill": CLEAR, "X": "104", "Y": "640", "Width": "830", "Height": "336", "Visible": VD_}, children=lhkids, variant=GV)
new += control("lhNote", "Label@2.5.1", {"Text": '"Dark tick = the hourly target. Slow starts, breaks and shift changes show up here."',
    "Font": "Font.Arial", "Size": "9", "Color": GREY, "Align": "Align.Left", "Wrap": "false", "X": "104", "Y": "980", "Width": "830", "Height": "24", "Visible": VD_})

# ---------- S / Q / D: list ----------
VLL = VIS("S", "Q", "D")
llkids = [control("llBg", "Rectangle@2.3.0", {"Fill": LIGHT, "X": "0", "Y": "3", "Width": "810", "Height": "58"}, ind=6),
          control("llK", "Label@2.5.1", {"Text": "ThisItem.K", "Font": "Font.Arial", "Size": "11", "FontWeight": "FontWeight.Bold", "Color": DARK,
                  "Align": "Align.Left", "Wrap": "false", "X": "12", "Y": "6", "Width": "236", "Height": "26"}, ind=6),
          control("llK2", "Label@2.5.1", {"Text": "ThisItem.K2", "Font": "Font.Arial", "Size": "9", "Color": GREY, "Align": "Align.Left", "Wrap": "false",
                  "X": "12", "Y": "32", "Width": "236", "Height": "24", "Tooltip": "ThisItem.K2"}, ind=6),
          control("llV", "Label@2.5.1", {"Text": "ThisItem.V", "Font": "Font.Arial", "Size": "12", "FontWeight": "FontWeight.Bold", "Color": DARK,
                  "Align": "Align.Left", "Wrap": "false", "X": "254", "Y": "6", "Width": "500", "Height": "26", "Tooltip": "ThisItem.V"}, ind=6),
          control("llV2", "Label@2.5.1", {"Text": "ThisItem.V2", "Font": "Font.Arial", "Size": "9", "Color": GREY, "Align": "Align.Left", "Wrap": "false",
                  "X": "254", "Y": "32", "Width": "500", "Height": "24", "Tooltip": "ThisItem.V2"}, ind=6),
          control("llSt", "Rectangle@2.3.0", {"Fill": STFILL("ThisItem.St"), "X": "764", "Y": "19", "Width": "34", "Height": "26"}, ind=6)]
new += control("galLL", "Gallery@2.15.0", {"Items": "colLL", "TemplateSize": "64", "TemplatePadding": "0", "ShowScrollbar": "true", "BorderThickness": "0",
    "TemplateFill": CLEAR, "X": "986", "Y": "640", "Width": "830", "Height": "364", "Visible": VLL}, children=llkids, variant=GV)
new += control("llEmpty", "Label@2.5.1", {"Text": 'Switch(varDTab, "S", "No safety events logged in the window.", "Q", "No scrap logged in the window.", "No shifts in the window.")',
    "Font": "Font.Arial", "Size": "13", "Color": GREY, "Align": "Align.Center", "X": "986", "Y": "760", "Width": "830", "Height": "50",
    "Visible": f"{VLL} && CountRows(colLL) = 0"})

# ---------- C: OEE by day ----------
VC_ = VIS("C")
new += control("galO2Bg", "Rectangle@2.3.0", {"Fill": "RGBA(250, 250, 248, 1)", "X": "986", "Y": "640", "Width": "830", "Height": "248", "Visible": VC_})
new += chart("O2", 986, 640, 830, "ThisItem.OEE", "ThisItem.StO", "varTS.O", 'Text(ThisItem.OEE, "0") & "%"', VC_, "", small=True)
for n, t, c, l in [("oL1", "varOG", GREEN, '"green " & varOG & "%"'), ("oL2", "varOA", AMBER, '"amber " & varOA & "%"')]:
    yy = f"640 + 214 - Min(1, {t} / Max(0.0001, varTS.O)) * 190"
    new += control(n, "Rectangle@2.3.0", {"Fill": c, "X": "986", "Y": f"{yy} - 1", "Width": "830", "Height": "2", "Visible": VC_})
    new += control(n + "T", "Label@2.5.1", {"Text": l, "Font": "Font.Arial", "Size": "9", "FontWeight": "FontWeight.Bold", "Color": c,
        "Align": "Align.Right", "Wrap": "false", "X": "1676", "Y": f"{yy} - 18", "Width": "140", "Height": "16", "Visible": VC_})
new += control("oNote", "Label@2.5.1", {"Text": ('If(IsBlank(varLW.OEE), "No OEE on these boards: Act. Speed (E4) is blank.", "Window: OEE " & Text(varLW.OEE, "0") & "%   ·   A " & '
                                                  'Text(Coalesce(varLW.A, 0), "0") & "   P " & Text(Coalesce(varLW.P, 0), "0") & "   Q " & Text(Coalesce(varLW.Q, 0), "0") & "   (averages of the shifts)")'),
    "Font": "Font.Arial", "Size": "11", "FontWeight": "FontWeight.Bold", "Color": DARK, "Align": "Align.Left", "Wrap": "false",
    "X": "986", "Y": "900", "Width": "830", "Height": "30", "Visible": VC_})
new += control("oNote2", "Label@2.5.1", {"Text": '"Cost here means what drives it: lost minutes, OEE and labor per unit. The boards carry no dollar figures."',
    "Font": "Font.Arial", "Size": "9", "Color": GREY, "Align": "Align.Left", "Wrap": "false", "X": "986", "Y": "934", "Width": "830", "Height": "24", "Visible": VC_})

y = y.replace("\n- cDim:\n", "\n" + new + "- cDim:\n", 1)
open(dst, "w", encoding="utf-8").write(y)

# ---- sanity ----
doc = yaml.safe_load(open(dst, encoding="utf-8"))
names = []
def walk(lst):
    for it in lst:
        for k, v in it.items():
            names.append(k)
            for pk, pv in v["Properties"].items():
                f = str(pv)
                assert f.startswith("="), (k, pk, pv)
                s = re.sub(r'"[^"]*"', '""', f)
                assert s.count("(") == s.count(")"), (k, pk, "parens")
                assert s.count("{") == s.count("}"), (k, pk, "braces")
                assert f.count('"') % 2 == 0, (k, pk, "quotes")
            if "Children" in v: walk(v["Children"])
walk(doc)
dupes = {n for n in names if names.count(n) > 1}
assert not dupes, dupes
print("ok:", len(names), "controls")
