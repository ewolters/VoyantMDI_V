# Tier 2 BY FORM screen (scrForm). One row per FORM (from the product each shift picked on Hour x Hour:
# HxH_Shift.PlaybookKey = Line|Size|Form), for the day reviewed, with a 7-day attainment strip. Tap a form for its shifts.
# Reuses the Tier 2 metric formulas (t2v2.py DEF) so the numbers and colors match the daily board.
import os
_OUTD = os.environ.pop("MDI_OUTDIR", None) or os.environ["MDI_TMP"]
_SCR = os.environ["MDI_TMP"] + "/_t2f_tmp.yaml"
_OUT = os.environ.get("T2FOUT", _OUTD + "/T2_Form_v1.pa.yaml")
os.environ["T2OUT"] = _SCR
exec(open(os.environ["MDI_GEN"] + "/t2v2.py").read())
out = []   # fresh control list for the new screen

NOPROD = '"(no product)"'
FSHM = '(ddFShift.Selected.Value = "All" || Text(Shift) = ddFShift.Selected.Value)'
KEYS = ["D", "DT", "C", "Q", "P"]           # attainment, downtime, OEE, rework, crew (Tier 2 definitions)
COLS = [("D", "ATTAINMENT", 230), ("DT", "DOWNTIME", 230), ("C", "OEE", 200), ("Q", "REWORK", 210), ("P", "CREW", 200)]

# ---- one record per FORM per DAY (ff = form row, k = day offset from varF0) ----
FREC = ('With({dD: DateAdd(varF0, k.Value, TimeUnit.Days), F: ff.Value},\n'
 '  With({dE: DateAdd(dD, 1, TimeUnit.Days)},\n'
 '   With({shs: Filter(colFS, Fm = F && ShiftDate >= dD && ShiftDate < dE)},\n'
 '    With({qas: Filter(colFQA, ShiftKey in shs.Title), dth: Filter(colFDTH, ShiftKey in shs.Title)},\n'
 '     With({t: Sum(shs, Coalesce(TargetUnits, 0)), a: Sum(shs, Coalesce(ActualUnits, 0)), o: Sum(shs, Coalesce(OEE, 0) * Coalesce(TargetUnits, 0)),\n'
 '           sh: CountRows(shs), sc: Sum(shs, Coalesce(FGScrapQty, 0)), ca: Sum(shs, Coalesce(ActualCrewSize, 0)), cs: Sum(shs, Coalesce(StdCrewSize, 0)),\n'
 '           dt: Sum(shs, Coalesce(ReportedDowntimeMin, 0)), rw: Sum(qas, Coalesce(ReworkQty, 0)),\n'
 '           pt: Sum(shs, With({pb: LookUp(colPB, Title = PlaybookKey)}, If(IsBlank(pb), Coalesce(TargetUnits, 0), Coalesce(Value(Text(pb.UnitsPerHour)), 0) * Max(Coalesce(PlannedShiftHrs, pb.AvailableHrsShift, 0) - (Coalesce(LunchMin, 0) + Coalesce(BreakMin, 0)) / 60, 0)))),\n'
 '           effw: Sum(shs, Coalesce(LookUp(colPB, Title = PlaybookKey).EfficiencyTarget, 0) * Coalesce(TargetUnits, 0)),\n'
 '           escl: 0,\n'
 '           evs: GroupBy(Filter(Ungroup(Table({t: ForAll(dth, {K: ShiftKey & "|" & DT_Reason, R: DT_Reason, M: Coalesce(DT_Minutes, 0)})}, {t: ForAll(dth, {K: ShiftKey & "|" & DT2_Reason, R: DT2_Reason, M: Coalesce(DT2_Minutes, 0)})}), t), M > 0 && !IsBlank(R)), K, R, G)},\n'
 '      With({dte: CountRows(evs), dtl: Coalesce(Max(ForAll(evs, {v: Sum(G, M)}), v), 0)},\n'
 '       {Fm: F, Day: dD, Shifts: sh, Act: a, Plan: pt, DT: dt,\n'
 '        Lines: Concat(Sort(Distinct(shs, Line), Value), Value, "  "),\n'
 '        ' + ",\n        ".join(f'txt{k}: {DEF[k][0]}, sub{k}: {DEF[k][1]}, st{k}: {DEF[k][2]}' for k in KEYS) + '}))))))')
FREC = wrap_sums(FREC)

# ---- one record per SHIFT of the tapped form on the day reviewed ----
SREC = ('With({pb: LookUp(colPB, Title = s.PlaybookKey), hrs: Filter(colFDTH, ShiftKey = s.Title)},\n'
 '  With({pt: If(IsBlank(pb), Coalesce(s.TargetUnits, 0), Coalesce(Value(Text(pb.UnitsPerHour)), 0) * Max(Coalesce(s.PlannedShiftHrs, pb.AvailableHrsShift, 0) - (Coalesce(s.LunchMin, 0) + Coalesce(s.BreakMin, 0)) / 60, 0)),\n'
 '        a: Coalesce(s.ActualUnits, 0),\n'
 '        rs: GroupBy(Filter(Ungroup(Table({t: ForAll(hrs, {R: DT_Reason, M: Coalesce(DT_Minutes, 0)})}, {t: ForAll(hrs, {R: DT2_Reason, M: Coalesce(DT2_Minutes, 0)})}), t), M > 0 && !IsBlank(R)), R, G)},\n'
 '   With({top: First(SortByColumns(ForAll(rs, {Rn: R, Mn: Sum(G, M)}), "Mn", SortOrder.Descending))},\n'
 '    {Line: s.Line, Shift: s.Shift, Prod: Coalesce(s.ProductForm, "no product picked"), Act: a, Plan: pt,\n'
 '     Att: If(pt = 0, "—", Text(a / pt * 100, "0") & "%"), AttSt: If(pt = 0, "N", a / pt * 100 >= varAG, "G", a / pt * 100 >= varAA, "A", "R"),\n'
 '     DT: Coalesce(s.ReportedDowntimeMin, 0), Top: If(IsBlank(top), "—", top.Rn & "  (" & Text(top.Mn) & " min)"),\n'
 '     OEEt: If(IsBlank(s.OEE), "—", Text(s.OEE * 100, "0") & "%"),\n'
 '     Crew: If(Coalesce(s.StdCrewSize, 0) = 0, Text(Coalesce(s.ActualCrewSize, 0)), Text(Coalesce(s.ActualCrewSize, 0)) & " / " & Text(s.StdCrewSize))})))')
SREC = wrap_sums(SREC)

def LDF(coll, src, nm): return f'IfError(ClearCollect({coll}, {src}), Notify("By form: could not load {nm}", NotificationType.Error));\n'
FW = 'ShiftDate >= varF0 && ShiftDate < varF1'
LOADF = ('Set(varFBusy, true); Set(varFSel, false);\n'
 'Set(varFD, ddFDate.Selected.D); Set(varF0, DateAdd(varFD, -6, TimeUnit.Days)); Set(varF1, DateAdd(varFD, 1, TimeUnit.Days));\n'
 + LDF("colCfg", "MDI_Config", "MDI_Config")
 + CFG("varAG", "T2_AttainGreen", 90) + CFG("varAA", "T2_AttainAmber", 80) + CFG("varOG", "T2_OEEGreen", 65) + CFG("varOA", "T2_OEEAmber", 50)
 + CFG("varRA", "T2_ReworkAmber", 0.5) + CFG("varRR", "T2_ReworkRed", 2) + CFG("varDA", "T2_DTAmber", 30) + CFG("varDR", "T2_DTRed", 60)
 + LDF("colPB", "PLAYBOOK", "PLAYBOOK")
 + LDF("colFShiftAll", f"Filter(HxH_Shift, {FW})", "HxH_Shift")
 + LDF("colFDTH", f"Filter(HxH_Hourly, {FW} && (DT_Minutes > 0 || DT2_Minutes > 0))", "HxH_Hourly (downtime)")
 + LDF("colFQA", f"Filter(QA_Rework, {FW} && Voided = false)", "QA_Rework")
 + 'Set(varFLoadedAt, Now()); Set(varFBusy, false);\nSelect(btnFCalc)')

CALCF = ('Set(varFBusy, true); Set(varFSel, false);\n'
 # the form of a shift = the Form part of the PlaybookKey saved from the PRODUCT pick
 f'ClearCollect(colFS, AddColumns(Filter(colFShiftAll, {FSHM}), Fm, If(IsBlank(PlaybookKey), {NOPROD}, Last(Split(PlaybookKey, "|")).Value)));\n'
 f'ClearCollect(colFForms, Sort(Distinct(colFS, Fm), If(Value = {NOPROD}, "zzz", Value)));\n'
 'ClearCollect(colFDay, Ungroup(ForAll(colFForms As ff, {rows: ForAll(Sequence(7, 0) As k,\n  ' + FREC + ')}), rows));\n'
 'ClearCollect(colFRows, ForAll(colFForms As ff, With({x: LookUp(colFDay, Fm = ff.Value && Day = varFD)},\n'
 '  {Fm: ff.Value, Lines: x.Lines, Shifts: x.Shifts, Tr: Concat(Sort(Filter(colFDay, Fm = ff.Value), Day), stD),\n   '
 + ",\n   ".join(f'txt{k}: x.txt{k}, sub{k}: x.sub{k}, st{k}: x.st{k}' for k in KEYS) + '})));\n'
 'Set(varFBusy, false)')

OPENF = (f'ClearCollect(colFDet, ForAll(SortByColumns(Filter(colFS, Fm = varFForm && ShiftDate >= varFD && ShiftDate < DateAdd(varFD, 1, TimeUnit.Days)), "Line", SortOrder.Ascending, "Shift", SortOrder.Ascending) As s,\n  '
 + SREC + '));\n'
 'Set(varFSel, true)')

# =========================== HEADER ===========================
out.append(rect("fHdrBar", DARK, 0, 0, 1920, 90))
out.append(label("fBrand", '"voyant"', 24, 6, 170, 52, size=34, color=WHITE, font="Georgia"))
out.append(label("fBrandSub", '"NEW ALBANY"', 27, 56, 170, 24, size=10, bold=True, color=TEAL))
out.append(label("fTitle", '"TIER 2"', 190, 6, 170, 40, size=26, bold=True, color=AQUA, font="Georgia", extra={"Wrap": "=false"}))
out.append(label("fTitleSub", '"BY FORM"', 192, 50, 180, 24, size=10, bold=True, color=WHITE))
out.append(cap("fcDate", "DAY REVIEWED", 380, 6, 200))
out.append(dd("ddFDate", 'ForAll(Sequence(30, 0), With({d: DateAdd(Today(), -Value, TimeUnit.Days)}, {Value: Text(d, "ddd m/d"), D: d}))', 380, 28, 200, 52,
   default='Text(DateAdd(Today(), -1, TimeUnit.Days), "ddd m/d")', onchange="Select(btnFLoad)", size=15, bold=True))
out.append(cap("fcShift", "SHIFT", 590, 6, 110))
out.append(dd("ddFShift", '["All", "1", "2", "3"]', 590, 28, 110, 52, onchange="If(!IsEmpty(colFShiftAll), Select(btnFCalc))", size=16, bold=True))
out.append(btn("btnFLoad", 'If(varFBusy, "LOADING…", "REFRESH")', LOADF, 710, 28, 140, 52, size=14,
   extra={"Tooltip": '="Load the day reviewed and the 6 days before it"'}))
out.append(label("fLoaded", 'If(varFBusy, "Working…", IsBlank(varFLoadedAt), "Tap REFRESH", "Updated " & Text(varFLoadedAt, "h:mm AM/PM"))', 860, 28, 200, 52, size=11, color=G5))
out.append(label("fScope", '"Forms from the PRODUCT picked on each Hour x Hour shift" & Char(10) & Text(varFD, "ddd m/d") & "  ·  " & If(ddFShift.Selected.Value = "All", "all shifts", "shift " & ddFShift.Selected.Value)',
   1070, 10, 590, 70, size=12, bold=True, color=AQUA, align="Right"))
out.append(btn("btnFBack", '"◂  DAILY"', 'Back()', 1676, 28, 120, 52, size=13, fill=AQUA, color=DARK, extra={"Tooltip": '="Back to the daily Tier 2 board"'}))
out.append(tap("btnFCalc", CALCF, 0, 1079, 1, 1))
out.append(tap("btnFOpen", OPENF, 2, 1079, 1, 1))

# =========================== GRID ===========================
out.append(rect("fSubBar", LIGHT, 0, 90, 1920, 48))
out.append(label("fHint", 'If(IsEmpty(colFRows), "", "Tap a form to see its lines and shifts for the day.  Hover a tile for detail.  (no product) = shifts where PRODUCT was not picked.")',
   12, 96, 1896, 36, size=11, color=G9))
X0 = 12; WF = 250; WL = 300; WS = 90
xs = {}; x = X0 + WF + WL + WS
for k, n, w in COLS:
    xs[k] = (x, w); x += w + 4
XT = x; WT = 1908 - XT
HV = '!IsEmpty(colFRows)'
heads = [("fhF", '"FORM"', X0, WF), ("fhL", '"LINES RUN"', X0 + WF, WL), ("fhS", '"SHIFTS"', X0 + WF + WL, WS)] + \
        [(f"fh{k}", f'"{n}"', xs[k][0], xs[k][1]) for k, n, w in COLS] + [("fhT", '"7-DAY ATTAINMENT  (oldest → day reviewed)"', XT, WT)]
for nm, tx, hx, hw in heads:
    out.append(V(rect(nm + "Bg", TEAL_D, hx, 142, hw - 2, 40), HV))
    out.append(V(label(nm, tx, hx, 142, hw - 2, 40, size=10, bold=True, color=WHITE, align="Center"), HV))
NOD = 'ThisItem.Shifts = 0'
kids = [rect("frBg", WHITE, 0, 0, 1896, 62, indent=I, extra={"BorderColor": F(G1), "BorderThickness": "=1"}),
        label("frF", 'ThisItem.Fm', 8, 2, WF - 12, 58, size=16, bold=True, color=f'If(ThisItem.Fm = {NOPROD}, {G9}, {DARK})', font="Georgia", indent=I),
        label("frL", 'If(IsBlank(ThisItem.Lines), "—", ThisItem.Lines)', WF, 2, WL - 6, 58, size=13, color=DARK, indent=I),
        label("frS", 'Text(ThisItem.Shifts)', WF + WL, 2, WS - 6, 58, size=15, bold=True, color=DARK, align="Center", indent=I)]
for k, n, w in COLS:
    cx_ = xs[k][0] - X0
    kids.append(rect(f"fr{k}Bg", f'If({NOD}, {G1}, ' + COL(f"ThisItem.st{k}") + ')', cx_, 2, w - 2, 58, indent=I, extra={"Tooltip": F(f"ThisItem.sub{k}")}))
    kids.append(label(f"fr{k}Tx", f'If({NOD}, "—", ThisItem.txt{k})', cx_, 2, w - 2, 34, size=17, bold=True, color=WHITE, align="Center", indent=I, extra={"Wrap": "=false"}))
    kids.append(label(f"fr{k}Sb", f'If({NOD}, "", ThisItem.sub{k})', cx_ + 2, 34, w - 6, 26, size=8, color=WHITE, align="Center", indent=I))
DW = (WT - 12) // 7
for i in range(7):
    kids.append(rect(f"frT{i}", DOT("ThisItem.Tr", i + 1), XT - X0 + 4 + i * DW, 14, DW - 4, 34, indent=I,
        extra={"BorderColor": F(DARK), "BorderThickness": "=3" if i == 6 else "=0"}))
kids.append(tap("frTap", 'Set(varFForm, ThisItem.Fm); Select(btnFOpen)', 0, 0, 1896, 62, indent=I, tip='"Open " & ThisItem.Fm & ": its lines and shifts"'))
out.append(gal("galForm", 'colFRows', 12, 186, 1896, 'If(varFSel, 380, 880)', 64, kids, extra={"ShowScrollbar": "=true"}))
out.append(label("fEmpty", 'If(varFBusy, "Loading…", IsEmpty(colFShiftAll), "Tap REFRESH to load the day reviewed.", "No Hour x Hour shifts on this day.")',
   12, 300, 1896, 80, size=18, color=G9, align="Center", extra={"Visible": F('IsEmpty(colFRows) || varFBusy')}))

# =========================== DETAIL (the tapped form's shifts) ===========================
VP = 'varFSel'
def vp(s): return V(s, VP)
out.append(vp(rect("fdBg", WHITE, 0, 572, 1920, 508, extra={"BorderColor": F(TEAL), "BorderThickness": "=3"})))
out.append(vp(label("fdTitle", 'Upper(varFForm) & "  ·  " & Text(varFD, "ddd m/d") & "  ·  " & If(ddFShift.Selected.Value = "All", "all shifts", "shift " & ddFShift.Selected.Value) & "  ·  " & Text(CountRows(colFDet)) & If(CountRows(colFDet) = 1, " shift", " shifts")',
   16, 578, 1500, 40, size=20, bold=True, color=DARK, font="Georgia")))
out.append(vp(btn("fdClose", '"✕  CLOSE"', 'Set(varFSel, false)', 1786, 582, 120, 36, size=11, fill=G1, color=DARK)))
DC = [("LINE", 120), ("SHIFT", 80), ("PRODUCT", 330), ("ACTUAL / PLAN", 250), ("ATTAIN", 150), ("DOWNTIME", 140), ("TOP DOWNTIME REASON", 430), ("OEE", 140), ("CREW / STD", 250)]
dx = []; x = 12
for n, w in DC:
    dx.append(x); x += w + 4
for i, (n, w) in enumerate(DC):
    out.append(vp(rect(f"fdh{i}Bg", TEAL_D, dx[i], 624, w, 34)))
    out.append(vp(label(f"fdh{i}", f'"{n}"', dx[i], 624, w, 34, size=10, bold=True, color=WHITE, align="Center")))
dvals = ['ThisItem.Line', '"S" & Text(ThisItem.Shift)', 'ThisItem.Prod', 'Text(ThisItem.Act, "#,##0") & " / " & Text(ThisItem.Plan, "#,##0")',
         'ThisItem.Att', 'Text(ThisItem.DT) & " min"', 'ThisItem.Top', 'ThisItem.OEEt', 'ThisItem.Crew']
dk = [rect("fdrBg", WHITE, 0, 0, 1896, 44, indent=I, extra={"BorderColor": F(G1), "BorderThickness": "=1"})]
for i, (n, w) in enumerate(DC):
    if i == 4:
        dk.append(rect("fdrAttBg", COL("ThisItem.AttSt"), dx[i] - 12, 4, w, 36, indent=I))
        dk.append(label("fdrAtt", dvals[i], dx[i] - 12, 4, w, 36, size=14, bold=True, color=WHITE, align="Center", indent=I))
    else:
        dk.append(label(f"fdr{i}", dvals[i], dx[i] - 12, 2, w, 40, size=13, bold=i == 0, color=DARK, align="Center" if i not in (2, 6) else None, indent=I))
out.append(vp(gal("galFDet", 'colFDet', 12, 662, 1896, 408, 46, dk, extra={"ShowScrollbar": "=true"})))

yaml = "".join(out)
write_themed(_OUT, yaml)
print("ok", len(yaml), "controls", yaml.count("    Control:"))
