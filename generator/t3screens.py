# Tier 3 extra screens: BOWLER (scrBowler) and VARIANCES (scrVariance). Same app as T3_Board (Screen1 = PERFORMANCE).
# Scope (plant / value stream / vertical / line) and the reviewed day are set on PERFORMANCE; these screens read them.
import sys
OUTB, OUTV = sys.argv[1], sys.argv[2]
sys.argv = ["t3.py", __import__("os").environ["MDI_TMP"]+"/_t3_tmp.pa.yaml"]
exec(open(__import__("os").environ["MDI_GEN"]+"/t3.py").read())

SCOPEPATH = '"PLANT" & If(IsBlank(varVS), "", "  ›  " & varVS) & If(IsBlank(varVert), "", "  ›  " & varVert) & If(IsBlank(varLn), "", "  ›  LINE " & varLn)'
def header(pfx, title):
    o = [rect(f"{pfx}HdrBar", DARK, 0, 0, 1920, 90),
         label(f"{pfx}Brand", '"voyant"', 24, 6, 170, 52, size=34, color=WHITE, font="Georgia"),
         label(f"{pfx}BrandSub", '"NEW ALBANY"', 27, 56, 170, 24, size=10, bold=True, color=TEAL),
         label(f"{pfx}Title", f'"TIER 3  ·  {title}"', 190, 20, 700, 50, size=26, bold=True, color=AQUA, font="Georgia", extra={"Wrap": "=false"}),
         label(f"{pfx}Scope", TOPG + ' & Char(10) & "as of " & Text(varD, "ddd m/d")', 1300, 10, 608, 70, size=13, bold=True, color=AQUA, align="Right"),
         rect(f"{pfx}SubBar", LIGHT, 0, 90, 1920, 44),
         label(f"{pfx}Path", SCOPEPATH, 16, 96, 640, 32, size=11, bold=True, color=TEAL_D,
               extra={"Tooltip": '="Change the scope on PERFORMANCE (value stream, vertical or line)."'})]
    o += tabbar(pfx, {"b": "scrBowler", "v": "scrVariance"}[pfx])
    o.append(label(f"{pfx}NoData", 'If(IsBlank(varLoadedAt), "Open PERFORMANCE first: it loads the data for every screen.", "")', 12, 500, 1896, 60, size=18, color=G9, align="Center"))
    return o

# ============================ BOWLER ============================
out.clear()
out.extend(header("b", "BOWLER"))
BMS = 'SortByColumns(AddColumns(colMet, LO, Find(Ltr, "SQDCP")), "LO", SortOrder.Ascending, "Ord", SortOrder.Ascending)'
SWX = lambda fld, R: SWMR(fld, R, "ThisItem.Code")
NW = 300; TW = 70; MW = 150; YW = 200
mx = lambda j: NW + 6 + TW + 6 + j * (MW + 4)
YX = mx(7) + 4
MX2 = YX + YW + 4
LCOL = 'Switch(ThisItem.Ltr, "S", RGBA(207, 34, 46, 1), "Q", RGBA(130, 80, 223, 1), "D", RGBA(9, 105, 218, 1), "C", RGBA(26, 127, 55, 1), RGBA(191, 135, 0, 1))'
out.append(label("bHead", '"WEEK OF " & Upper(Text(varWk, "mmm d")) & "  ·  DAY BY DAY + WEEK TO DATE + MONTH TO DATE  ·  " & ' + TOPG + ' & "  ·  target / actual / variance for every metric  ·  green variance = favorable"', 12, 140, 1896, 32, size=13, bold=True, color=TEAL_D))
out.append(label("bhM", '"METRIC"', 12, 174, NW, 26, size=10, bold=True, color=G9, align="Center"))
for j in range(7):
    out.append(label(f"bhm{j}", f'Upper(Text(DateAdd(varWk, {j}, TimeUnit.Days), "ddd m/d"))', 12 + mx(j), 174, MW, 26, size=10, bold=True, align="Center",
                     extra={"Color": F(f'If(DateAdd(varWk, {j}, TimeUnit.Days) = varD, {DARK}, {G9})')}))
out.append(label("bhW", '"WTD"', 12 + YX, 174, YW, 26, size=11, bold=True, color=DARK, align="Center"))
out.append(label("bhY", '"MTD " & Upper(Text(varD, "mmm"))', 12 + MX2, 174, YW, 26, size=11, bold=True, color=DARK, align="Center"))
RH = 84
FMTSW = lambda code: 'Switch(' + code + ', ' + ", ".join(f'"{c}", "{FMT[c]}"' for c in CODES) + ', "0.0")'
def TAV(c, x, w, pfx, big=False):
    """target / actual / variance stacked in one cell; c = record expr (colM / colY row)"""
    v = SWX("v_", "c"); g = SWX("g_", "c"); st = SWX("s_", "c"); fm = FMTSW("ThisItem.Code")
    has = f'!IsBlank(c) && {st} <> "N"'
    tgt = f'If({has} && {g} >= 0, Text({g}, {fm}), "")'
    act = f'If({has}, Text({v}, {fm}), "")'
    var = f'If({has} && {g} >= 0, With({{d: {v} - {g}}}, If(d > 0, "+", "") & Text(d, {fm})), "")'
    good = f'If({has} && {g} >= 0, If(ThisItem.Hi, {v} - {g} >= 0, {v} - {g} <= 0), true)'
    W = lambda e: f'With({{c: {c}}}, {e})'
    return [rect(f"{pfx}a", W(f'If({has}, {COL(st)}, {G1})'), x, 28, w, 28, indent=I, extra=({"BorderColor": F(DARK), "BorderThickness": "=2"} if big else None)),
            label(f"{pfx}t", W(tgt), x, 2, w, 26, size=9, color=G9, align="Center", indent=I, extra={"Wrap": "=false"}),
            label(f"{pfx}v", W(act), x, 28, w, 28, size=11 if not big else 12, bold=True, color=WHITE, align="Center", indent=I, extra={"Wrap": "=false"}),
            label(f"{pfx}d", W(var), x, 56, w, 26, size=10, bold=True, align="Center", indent=I,
                  extra={"Wrap": "=false", "Color": F(W(f'If({good}, {GREEN}, {RED})'))})]
bk = [rect("bmL", LCOL, 0, 2, 34, RH - 4, indent=I),
      label("bmLt", 'ThisItem.Ltr', 0, 2, 34, RH - 4, size=14, bold=True, color=WHITE, align="Center", indent=I),
      rect("bmBg", DARK, 36, 2, NW - 36, RH - 4, indent=I),
      label("bmN", 'ThisItem.Nm', 44, 4, NW - 48, 40, size=12, bold=True, color=WHITE, indent=I),
      label("bmU", 'If(ThisItem.Code = "QUAL_NCR", "not yet collected", ThisItem.Un & "  ·  " & If(ThisItem.Hi, "higher is better", "lower is better"))', 44, 44, NW - 48, 34, size=9, color=AQUA, indent=I),
      label("bmRT", '"target"', NW + 6, 2, TW, 26, size=9, color=G9, align="Right", indent=I),
      label("bmRA", '"actual"', NW + 6, 28, TW, 28, size=10, bold=True, color=DARK, align="Right", indent=I),
      label("bmRV", '"variance"', NW + 6, 56, TW, 26, size=9, color=G9, align="Right", indent=I),
      rect("bmSep", G1, 0, RH - 2, 1896, 1, indent=I)]
for j in range(7):
    bk += TAV(f'LookUp(colDy, G = {TOPG} && i = {j})', mx(j), MW, f"bc{j}")
bk += TAV(f'LookUp(colWTD, G = {TOPG})', YX, YW, "bcW", big=True)
bk += TAV(f'LookUp(colMTD, G = {TOPG})', MX2, YW, "bcY", big=True)
out.append(gal("galBowl", BMS, 12, 202, 1896, 640, RH, bk))
# --- one metric by value stream / vertical / line
out.append(label("bKids", '"BY " & If(!IsBlank(varVert), "LINE", !IsBlank(varVS), "VERTICAL / LINE", "VALUE STREAM")', 12, 850, 400, 32, size=13, bold=True, color=TEAL_D))
out.append(dd("bDdMet", 'ForAll(SortByColumns(AddColumns(colMet, LO, Find(Ltr, "SQDCP")), "LO", SortOrder.Ascending, "Ord", SortOrder.Ascending), {Value: Ltr & "  ·  " & Nm, Code: Code})', 420, 848, 360, 36, size=12,
              extra={"Default": F('"D  ·  " & LookUp(colMet, Code = varHdD).Nm')}))
SWB = lambda fld, R: SWMR(fld, R, "bDdMet.Selected.Code")
kk = [rect("bkBg", f'If(ThisItem.K = "line", {DARK}, {TEAL_D})', 0, 2, NW + 6 + TW, 36, indent=I),
      label("bkN", 'ThisItem.G', 10, 2, NW + TW - 10, 36, size='If(Len(ThisItem.G) > 22, 11, 13)', bold=True, color=WHITE, indent=I)]
for j in range(7):
    c = f'LookUp(colDy, G = ThisItem.G && i = {j})'
    kk.append(rect(f"bkc{j}", f'With({{c: {c}}}, If(IsBlank(c), {G1}, {COL(SWB("s_", "c"))}))', mx(j), 2, MW, 36, indent=I))
    kk.append(label(f"bkt{j}", f'With({{c: {c}}}, If(IsBlank(c), "", {SWB("t_", "c")}))', mx(j), 2, MW, 36, size=10, bold=True, color=WHITE, align="Center", indent=I, extra={"Wrap": "=false"}))
cw2 = 'LookUp(colWTD, G = ThisItem.G)'
kk.append(rect("bkcW", f'With({{c: {cw2}}}, If(IsBlank(c), {G1}, {COL(SWB("s_", "c"))}))', YX, 2, YW, 36, indent=I, extra={"BorderColor": F(DARK), "BorderThickness": "=3"}))
kk.append(label("bktW", f'With({{c: {cw2}}}, If(IsBlank(c), "", {SWB("t_", "c")}))', YX, 2, YW, 36, size=10, bold=True, color=WHITE, align="Center", indent=I, extra={"Wrap": "=false"}))
cy2 = 'LookUp(colMTD, G = ThisItem.G)'
kk.append(rect("bkcY", f'With({{c: {cy2}}}, If(IsBlank(c), {G1}, {COL(SWB("s_", "c"))}))', MX2, 2, YW, 36, indent=I, extra={"BorderColor": F(DARK), "BorderThickness": "=3"}))
kk.append(label("bktY", f'With({{c: {cy2}}}, If(IsBlank(c), "", {SWB("t_", "c")}))', MX2, 2, YW, 36, size=10, bold=True, color=WHITE, align="Center", indent=I, extra={"Wrap": "=false"}))
out.append(gal("galBowlKids", 'SortByColumns(Filter(colP, K <> "top"), "Ord", SortOrder.Ascending)', 12, 888, 1896, 180, 40, kk))
write_themed(OUTB, "".join(out)); print("wrote", OUTB)

# ============================ VARIANCES ============================
out.clear()
out.extend(header("v", "VARIANCE BOARD"))
SQC = 'Switch({x}, "Safety", RGBA(207, 34, 46, 1), "Quality", RGBA(130, 80, 223, 1), "Delivery", RGBA(9, 105, 218, 1), "Cost", RGBA(26, 127, 55, 1), "People", RGBA(191, 135, 0, 1), RGBA(117, 120, 123, 1))'
VSC = ('If(!IsBlank(varLn), Line = varLn, !IsBlank(varVert), ValueStream = varVert || Line in colScopeL.Title, '
       '!IsBlank(varVS), ValueStream = varVS || ValueStream in Filter(colVS, Up = varVS).Nm || Line in colScopeL.Title, true)')
VLOAD = ('Set(varV24, Value(Coalesce(LookUp(colCfg, Title = "T3_Var24Days").SettingValue, "7")));\n'
         'If(IsBlank(varVM), Set(varVM, Date(Year(Coalesce(varD, Today())), Month(Coalesce(varD, Today())), 1)));\n'
         'IfError(ClearCollect(colVar, Filter(Variances, RaisedDate >= DateAdd(Today(), -400, TimeUnit.Days))), Notify("Tier 3: could not load Variances", NotificationType.Error), true)')
out.append(tap("vLoad", VLOAD, 2, 1079, 1, 1))
V24 = f'SortByColumns(Filter(colVar, Kind.Value = "24-hour" && Status.Value = "Open" && ShowUntil >= Today() && {VSC}), "RaisedDate", SortOrder.Descending)'
VMO = f'SortByColumns(Filter(colVar, Kind.Value = "Monthly" && Year(MonthOf) = Year(varVM) && Month(MonthOf) = Month(varVM) && {VSC}), "RaisedDate", SortOrder.Descending)'
PANEL_W = 940; LX = 12; RX2 = 12 + PANEL_W + 16; RW3 = 1908 - RX2
BLANKPRE = '{T: "", M: 0, U: "units", SQ: "Delivery", Ln: "", K: "", Mt: ""}'
RESETS = 'Reset(vTxtTitle); Reset(vTxtMag); Reset(vTxtDet); Reset(vTxtOwn); Reset(vDdSQ); Reset(vDdUnit); Reset(vDdLine); Reset(vDdLevel); Reset(vDdMet)'
def card(pfx, w, kind24):
    mag = 'If(Mod(ThisItem.Magnitude, 1) = 0, Text(ThisItem.Magnitude, "#,##0"), Text(ThisItem.Magnitude, "#,##0.0")) & " " & ThisItem.Unit.Value'
    foot = ('If(IsBlank(ThisItem.Metric), "", ThisItem.Metric & "  ·  ") & Coalesce(ThisItem.Line, ThisItem.ValueStream, "plant") & "  ·  " & Coalesce(ThisItem.Owner, "no owner") & "  ·  raised " & Text(ThisItem.RaisedDate, "m/d")'
            + (' & "  ·  " & Max(DateDiff(Today(), ThisItem.ShowUntil, TimeUnit.Days), 0) & "d left on board"' if kind24 else ' & If(ThisItem.Status.Value = "Closed", "  ·  CLOSED", "")'))
    TONEWS = ('If(IsBlank(ThisItem.NewspaperRef), IfError(\n'
              ' Patch(Newspaper, Defaults(Newspaper), {Action: Left(ThisItem.Title, 250), Line: ThisItem.Line, ValueStream: ThisItem.ValueStream,\n'
              '  SQDCP: {Value: ThisItem.SQDCP.Value}, Source: {Value: "Tier 3"}, Status: {Value: "Open"},\n'
              '  Problem: Text(ThisItem.Magnitude, "#,##0") & " " & ThisItem.Unit.Value & ". " & Coalesce(ThisItem.Detail, ""),\n'
              '  Owner: ThisItem.Owner, OwnerEmail: ThisItem.OwnerEmail, RaisedDate: Now(), DueDate: DateAdd(Today(), 7, TimeUnit.Days), RefKey: "VAR-" & ThisItem.ID});\n'
              ' Patch(Variances, LookUp(Variances, ID = ThisItem.ID), {NewspaperRef: "VAR-" & ThisItem.ID});\n'
              ' Notify("Action added to the Newspaper.", NotificationType.Success); Select(vLoad),\n'
              ' Notify("Not saved. Check your connection and try again.", NotificationType.Error), true))')
    CLOSE = ('IfError(Patch(Variances, LookUp(Variances, ID = ThisItem.ID), {Status: {Value: If(ThisItem.Status.Value = "Open", "Closed", "Open")}, ClosedDate: If(ThisItem.Status.Value = "Open", Now(), Blank())}); Select(vLoad),\n'
             ' Notify("Not saved. Check your connection and try again.", NotificationType.Error), true)')
    bw = 150
    return [rect(f"{pfx}Bg", f'If(ThisItem.Status.Value = "Closed", RGBA(244, 245, 245, 1), {WHITE})', 0, 3, w, 108, indent=I, extra={"BorderColor": F(G1), "BorderThickness": "=1"}),
            rect(f"{pfx}Sq", SQC.format(x="ThisItem.SQDCP.Value"), 10, 12, 44, 44, indent=I),
            label(f"{pfx}SqL", 'Left(ThisItem.SQDCP.Value, 1)', 10, 12, 44, 44, size=20, bold=True, color=WHITE, align="Center", indent=I, extra={"Tooltip": F('ThisItem.SQDCP.Value')}),
            label(f"{pfx}Mag", mag, 64, 6, 250, 40, size=20, bold=True, indent=I, extra={"Wrap": "=false", "Color": F(SQC.format(x="ThisItem.SQDCP.Value"))}),
            label(f"{pfx}Ti", 'ThisItem.Title', 320, 8, w - 320 - bw - 12, 36, size=13, bold=True, indent=I, extra={"Tooltip": F('ThisItem.Title')}),
            label(f"{pfx}De", 'Coalesce(ThisItem.Detail, "")', 64, 46, w - 64 - bw - 12, 40, size=10, color=G9, indent=I, extra={"VerticalAlign": "=VerticalAlign.Top", "Tooltip": F('Coalesce(ThisItem.Detail, "")')}),
            label(f"{pfx}Ft", foot, 64, 86, w - 64 - bw - 12, 22, size=9, bold=True, color=TEAL_D, indent=I),
            btn(f"{pfx}News", 'If(IsBlank(ThisItem.NewspaperRef), "→ NEWSPAPER", "IN NEWSPAPER ✓")', TONEWS, w - bw - 8, 8, bw, 30, size=9, fill=f'If(IsBlank(ThisItem.NewspaperRef), {TEAL}, {G1})', color=DARK, indent=I,
                extra={"Tooltip": '="Creates a Tier 3 Newspaper action from this variance (due in 7 days)."'}),
            btn(f"{pfx}Close", 'If(ThisItem.Status.Value = "Open", "CLOSE", "REOPEN")', CLOSE, w - bw - 8, 42, bw, 30, size=9, fill=G1, color=DARK, indent=I),
            btn(f"{pfx}Rca", '"ROOT CAUSE"', 'false', w - bw - 8, 76, bw, 28, size=9, fill=G1, color=G5, indent=I,
                extra={"DisplayMode": "=DisplayMode.Disabled", "DisabledFill": F(G1), "DisabledColor": F(G5), "Tooltip": '="Root cause analysis: coming soon"'})]
# left: 24-hour
out.append(label("v24T", '"24-HOUR VARIANCES  ·  biggest misses  ·  on the board " & varV24 & " days  (" & CountRows(' + V24 + ') & ")"', LX, 140, PANEL_W - 190, 34, size=13, bold=True, color=TEAL_D))
out.append(btn("v24Add", '"+ 24-HOUR"', f'Set(varPre, {BLANKPRE}); Select(vLoad); Set(varVK, "24-hour"); {RESETS}; Set(varVAdd, true)', LX + PANEL_W - 180, 140, 180, 34, size=11, fill=RED, color=WHITE))
out.append(gal("galV24", V24, LX, 178, PANEL_W, 284, 112, card("v24", PANEL_W - 20, True)))
out.append(label("v24E", f'If(!IsBlank(varLoadedAt) && CountRows({V24}) = 0, "No open 24-hour variances in this scope. Raise one from the biggest misses below.", "")', LX, 220, PANEL_W, 40, size=12, color=G9, align="Center"))
# suggestions: biggest misses of the reviewed day (from the boards)
# ---- BIGGEST MISSES of the reviewed day, every letter (top 3 per source), keyed so a raised miss drops off ----
DAYW = 'ShiftDate >= varD && ShiftDate < varD1'
SCP = 'Line in colScopeL.Title'
DS = 'Text(varD, "yyyymmdd")'
REC = lambda T, M, U, SQ, O, Ln, X, K, Mt: f'{{T: {T}, M: {M}, U: "{U}", SQ: "{SQ}", O: {O}, Ln: {Ln}, X: {X}, K: {K} & "|" & {DS}, Mt: "{Mt}"}}'
TOP = lambda tbl, col, n=3: f'FirstN(SortByColumns({tbl}, "{col}", SortOrder.Descending), {n})'
DTB = f'Filter(colDTH, {DAYW} && {SCP})'
SRC = [
 # safety: board events, audit hazards (worst first)
 f'ForAll(FirstN(Filter(colSafe, {DAYW} && {SCP}), 3), ' + REC('"Line " & Line & " · safety event S" & Shift & " H" & HourNo', '1', 'events', 'Safety', 1, 'Line', 'Left(Coalesce(SafetyNotes, "board"), 40)', '"SAF|" & Line & "|" & Shift & "|" & HourNo', 'SAF_EVENTS') + ')',
 f'ForAll(FirstN(SortByColumns(AddColumns(Filter(colFR, AuditDate >= varD && AuditDate < varD1 && (IsBlank(varVS) || {SCP})), Sv, Switch(Severity.Value, "Critical", 4, "High", 3, "Medium", 2, 1)), "Sv", SortOrder.Descending), 3), '
   + REC('Coalesce(Item, "audit finding") & " · " & ZoneID', '1', 'hazards', 'Safety', 1, 'Coalesce(Line, "")', 'Coalesce(Severity.Value, "") & " hazard"', '"HAZ|" & ZoneID & "|" & Coalesce(Item, "")', 'SAF_HAZ') + ')',
 # quality: rework and scrap by line + reason
 'ForAll(' + TOP(f'ForAll(GroupBy(Filter(colQA, {DAYW} && {SCP}), Line, Reason, G), {{Ln: Line, R: Reason, Q: Sum(G, Coalesce(ReworkQty, 0))}})', 'Q') + ', '
   + REC('"Line " & Ln & " · rework: " & Coalesce(R, "no reason")', 'Q', 'units', 'Quality', 2, 'Ln', '"rework"', '"RW|" & Ln & "|" & Coalesce(R, "")', 'QUAL_RW') + ')',
 'ForAll(' + TOP(f'ForAll(GroupBy(Filter(colShift, {DAYW} && {SCP} && Coalesce(FGScrapQty, 0) > 0), Line, ScrapReasonCode, G), {{Ln: Line, R: ScrapReasonCode, Q: Sum(G, Coalesce(FGScrapQty, 0))}})', 'Q') + ', '
   + REC('"Line " & Ln & " · scrap: " & Coalesce(R, "no reason")', 'Q', 'units', 'Quality', 2, 'Ln', '"scrap"', '"SC|" & Ln & "|" & Coalesce(R, "")', 'QUAL_SCRAP') + ')',
 # delivery: below plan, downtime
 f'ForAll(FirstN(SortByColumns(AddColumns(Filter(colDaily, Day = varD && {SCP} && Shifts > 0 && Plan > Act), Gap, Plan - Act), "Gap", SortOrder.Descending), 3), '
   + REC('"Line " & Line & " below plan"', 'Round(Gap, 0)', 'units', 'Delivery', 3, 'Line', 'Text(Act / Plan * 100, "0") & "% of plan"', '"SHORT|" & Line', 'DEL_ATT') + ')',
 'ForAll(' + TOP(f'ForAll(GroupBy(Filter(Ungroup(Table({{t: ForAll({DTB}, {{Ln: Line, R: DT_Reason, Mi: Coalesce(DT_Minutes, 0)}})}}, {{t: ForAll({DTB}, {{Ln: Line, R: DT2_Reason, Mi: Coalesce(DT2_Minutes, 0)}})}}), t), !IsBlank(R) && Mi > 0), Ln, R, G), {{Ln: Ln, R: R, Q: Sum(G, Mi)}})', 'Q') + ', '
   + REC('"Line " & Ln & " · " & Substitute(R, "Machine - ", "")', 'Q', 'minutes', 'Delivery', 3, 'Ln', '"downtime"', '"DT|" & Ln & "|" & R', 'DEL_DT') + ')',
 # cost: speed loss by line + reason
 'ForAll(' + TOP(f'ForAll(GroupBy(Filter(colShift, {DAYW} && {SCP} && !IsBlank(SpeedLossReasonCode) && Coalesce(TargetUnits, 0) > Coalesce(ActualUnits, 0)), Line, SpeedLossReasonCode, G), {{Ln: Line, R: SpeedLossReasonCode, Q: Sum(G, Coalesce(TargetUnits, 0) - Coalesce(ActualUnits, 0))}})', 'Q') + ', '
   + REC('"Line " & Ln & " · speed loss: " & R', 'Q', 'units', 'Cost', 4, 'Ln', '"below target rate"', '"SPD|" & Ln & "|" & R', 'COST_SPEED') + ')',
 # people: short crews, missed process confirmations
 f'ForAll(FirstN(Filter(colShift, {DAYW} && {SCP} && Coalesce(ActualCrewSize, 0) < Coalesce(StdCrewSize, 0)), 3), '
   + REC('"Line " & Line & " · shift " & Shift & " short staffed"', 'StdCrewSize - ActualCrewSize', 'people', 'People', 5, 'Line', 'Text(ActualCrewSize) & " of " & Text(StdCrewSize)', '"CREW|" & Line & "|" & Shift', 'PEO_CREW') + ')',
 'ForAll(' + TOP(f'ForAll(GroupBy(Filter(colRes, Answer.Value = "No" && Created >= varD && Created < varD1 && {SCP}), Line, ElementID, G), {{Ln: Line, R: ElementID, Q: CountRows(G)}})', 'Q') + ', '
   + REC('"Line " & Ln & " · PC miss: " & Coalesce(LookUp(colEl, ID = R).Title, "item " & R)', 'Q', 'events', 'People', 5, 'Ln', '"process confirmation"', '"PC|" & Ln & "|" & R', 'PEO_PC') + ')',
]
SUGG = 'SortByColumns(Filter(Ungroup(Table(' + ", ".join(f'{{t: {x}}}' for x in SRC) + '), t), !IsBlank(T) && !(K in colVar.SourceKey)), "O", SortOrder.Ascending, "M", SortOrder.Descending)'
SY = 470
out.append(rect("vSugBg", LIGHT, LX, SY, PANEL_W, 1068 - SY))
out.append(label("vSugT", '"BIGGEST MISSES  ·  " & Text(varD, "ddd m/d") & "  ·  every letter, from the boards and audits  ·  RAISE puts one on the board"', LX + 12, SY + 4, PANEL_W - 24, 30, size=11, bold=True, color=TEAL_D))
sk = [rect("vsSq", SQC.format(x="ThisItem.SQ"), 0, 6, 28, 28, indent=I),
      label("vsSqL", 'Left(ThisItem.SQ, 1)', 0, 6, 28, 28, size=12, bold=True, color=WHITE, align="Center", indent=I),
      label("vsT", 'ThisItem.T', 36, 0, 420, 40, size=11, bold=True, indent=I, extra={"Tooltip": F('ThisItem.T & "  ·  " & ThisItem.X')}),
      label("vsM", 'Text(ThisItem.M, "#,##0") & " " & ThisItem.U', 460, 0, 170, 40, size=12, bold=True, color=RED, align="Right", indent=I),
      label("vsX", 'ThisItem.X', 640, 0, 130, 40, size=9, color=G9, indent=I),
      btn("vsRaise", '"RAISE"', f'Set(varPre, {{T: ThisItem.T, M: ThisItem.M, U: ThisItem.U, SQ: ThisItem.SQ, Ln: ThisItem.Ln, K: ThisItem.K, Mt: ThisItem.Mt}}); Select(vLoad); Set(varVK, "24-hour"); {RESETS}; Set(varVAdd, true)',
          780, 5, 120, 30, size=10, fill=TEAL, color=DARK, indent=I)]
out.append(gal("galVSug", SUGG, LX + 12, SY + 38, PANEL_W - 24, 1068 - SY - 44, 40, sk))
out.append(label("vSugE", f'If(CountRows({SUGG}) = 0, "No misses logged for this day in this scope.", "")', LX + 12, SY + 60, PANEL_W - 24, 30, size=11, color=G9))
# right: monthly / MOR
out.append(label("vMoT", '"MONTHLY VARIANCES  ·  for the MOR  ·  " & Upper(Text(varVM, "mmmm yyyy")) & "  (" & CountRows(' + VMO + ') & ")"', RX2, 140, RW3 - 380, 34, size=13, bold=True, color=TEAL_D))
out.append(btn("vMoPrev", '"◀"', 'Set(varVM, DateAdd(varVM, -1, TimeUnit.Months))', RX2 + RW3 - 372, 140, 44, 34, size=12, fill=TEAL_D, color=WHITE))
out.append(btn("vMoNext", '"▶"', 'Set(varVM, DateAdd(varVM, 1, TimeUnit.Months))', RX2 + RW3 - 324, 140, 44, 34, size=12, fill=TEAL_D, color=WHITE))
out.append(btn("vMoAdd", '"+ MONTHLY"', f'Set(varPre, {BLANKPRE}); Select(vLoad); Set(varVK, "Monthly"); {RESETS}; Set(varVAdd, true)', RX2 + RW3 - 270, 140, 270, 34, size=11, fill="RGBA(9, 105, 218, 1)", color=WHITE))
out.append(gal("galVMo", VMO, RX2, 178, RW3, 890, 112, card("vmo", RW3 - 20, False)))
out.append(label("vMoE", f'If(!IsBlank(varLoadedAt) && CountRows({VMO}) = 0, "No monthly variances for " & Text(varVM, "mmmm") & " in this scope.", "")', RX2, 220, RW3, 40, size=12, color=G9, align="Center"))

# ---- add-variance overlay
VA = {"Visible": "=varVAdd"}
def vx(d=None): d = dict(d or {}); d.update(VA); return d
out.append(rect("vOvDim", "RGBA(7, 39, 45, 0.55)", 0, 0, 1920, 1080, extra=VA))
out.append(rect("vOvPanel", WHITE, 520, 120, 880, 820, extra=VA))
out.append(rect("vOvHdr", DARK, 520, 120, 880, 60, extra=VA))
out.append(label("vOvTitle", '"NEW " & Upper(varVK) & " VARIANCE" & If(varVK = "Monthly", "  ·  " & Upper(Text(varVM, "mmmm yyyy")), "")', 544, 120, 820, 60, size=18, bold=True, color=AQUA, font="Georgia", extra=VA))
cv = lambda n, t, x, y, w: label(n, f'"{t}"', x, y, w, 20, size=9, bold=True, color=G9, extra=VA)
for i, k in enumerate(["24-hour", "Monthly"]):
    out.append(btn(f"vKind{i}", f'"{k.upper()}"', f'Set(varVK, "{k}")', 544 + i * 170, 196, 160, 40, size=12,
                   fill=f'If(varVK = "{k}", {TEAL}, {G1})', color=DARK, extra=vx()))
out.append(cv("vcT", "HEADLINE (WHAT WAS MISSED / WHAT HIT US)", 544, 250, 820))
out.append(ti("vTxtTitle", 'Coalesce(varPre.T, "")', 544, 272, 832, 48, hint='"e.g. Line 205 lost 2 hours to filler valve"', size=15, extra=vx()))
out.append(cv("vcM", "MAGNITUDE", 544, 334, 200))
out.append(ti("vTxtMag", 'If(Coalesce(varPre.M, 0) = 0, "", Text(varPre.M))', 544, 356, 200, 48, hint='"number"', size=15, number=True, extra=vx()))
out.append(cv("vcU", "UNIT", 756, 334, 160))
out.append(dd("vDdUnit", '["units", "cases", "minutes", "hours", "%", "points", "events", "shifts", "people"]', 756, 356, 160, 48, size=15, extra=vx({"Default": F('Coalesce(varPre.U, "units")')})))
out.append(cv("vcS", "SQDCP", 928, 334, 180))
out.append(dd("vDdSQ", '["Safety", "Quality", "Delivery", "Cost", "People"]', 928, 356, 180, 48, size=15, extra=vx({"Default": F('Coalesce(varPre.SQ, "Delivery")')})))
out.append(cv("vcO", "OWNER", 1120, 334, 256))
out.append(ti("vTxtOwn", '""', 1120, 356, 256, 48, hint='"name"', size=15, extra=vx()))
out.append(cv("vcMe", "METRIC (OPTIONAL)", 1170, 418, 206))
out.append(dd("vDdMet", 'Ungroup(Table({t: Table({Value: "(none)", Code: "", Ltr: ""})}, {t: ForAll(SortByColumns(AddColumns(Filter(colMet, With({m: LookUp(colMTD, G = ' + TOPG + ')}, !IsBlank(m) && ' + SWMR('s_', 'm', 'Code') + ' <> "N")), LO, Find(Ltr, "SQDCP")), "LO", SortOrder.Ascending, "Ord", SortOrder.Ascending), {Value: Ltr & "  ·  " & Nm, Code: Code, Ltr: Ltr})}), t)', 1170, 440, 206, 48, size=12,
              extra=vx({"Default": F('If(IsBlank(varPre.Mt) || varPre.Mt = "", "(none)", With({m: LookUp(colMet, Code = varPre.Mt)}, m.Ltr & "  ·  " & m.Nm))'), "Tooltip": '="Only metrics with data in this scope are listed. Picking one sets SQDCP."'})))
out.append(cv("vcL", "VALUE STREAM / VERTICAL", 544, 418, 400))
LEVELS = 'Ungroup(Table({t: Table({Value: "Plant"})}, {t: ForAll(Filter(colVS, !IsBlank(Nm)), {Value: Nm})}), t)'
out.append(dd("vDdLevel", LEVELS, 544, 440, 400, 48, size=14,
              extra=vx({"Default": F('If(!IsBlank(varPre.Ln) && varPre.Ln <> "", LookUp(colLines, Title = varPre.Ln).ValueStream, Coalesce(varVert, varVS, "Plant"))')})))
out.append(cv("vcLn", "LINE (OPTIONAL)", 956, 418, 200))
out.append(dd("vDdLine", 'Ungroup(Table({t: Table({Value: "(none)"})}, {t: ForAll(Filter(colLines, !IsBlank(Title)), {Value: Title})}), t)', 956, 440, 200, 48, size=14,
              extra=vx({"Default": F('If(IsBlank(varPre.Ln) || varPre.Ln = "", Coalesce(varLn, "(none)"), varPre.Ln)')})))
out.append(cv("vcD", "WHAT HAPPENED / WHY IT MATTERS", 544, 502, 820))
out.append(ti("vTxtDet", '""', 544, 524, 832, 220, hint='"Facts, where, when, what we know so far"', size=14, extra=vx({"Mode": "=TextMode.MultiLine"})))
SAVEV = ('IfError(Patch(Variances, Defaults(Variances), {Title: vTxtTitle.Text, Kind: {Value: varVK},\n'
         '  SQDCP: {Value: If(vDdMet.Selected.Code = "", vDdSQ.Selected.Value, Switch(vDdMet.Selected.Ltr, "S", "Safety", "Q", "Quality", "D", "Delivery", "C", "Cost", "People"))},\n'
         '  SourceKey: If(IsBlank(varPre.K) || varPre.K = "", Blank(), varPre.K),\n'
         '  ValueStream: If(vDdLevel.Selected.Value = "Plant", Blank(), vDdLevel.Selected.Value), Line: If(vDdLine.Selected.Value = "(none)", Blank(), vDdLine.Selected.Value),\n'
         '  Metric: If(vDdMet.Selected.Code = "", Blank(), LookUp(colMet, Code = vDdMet.Selected.Code).Nm),\n'
         '  Magnitude: Value(vTxtMag.Text), Unit: {Value: vDdUnit.Selected.Value}, Detail: vTxtDet.Text, Owner: vTxtOwn.Text,\n'
         '  RaisedDate: Now(), ShowUntil: If(varVK = "24-hour", DateAdd(Today(), If(Coalesce(varV24, 0) > 0, varV24, 7), TimeUnit.Days), Blank()),\n'
         '  MonthOf: If(varVK = "Monthly", Coalesce(varVM, Date(Year(Coalesce(varD, Today())), Month(Coalesce(varD, Today())), 1)), Date(Year(Today()), Month(Today()), 1)), Status: {Value: "Open"}, RaisedBy: User().Email});\n'
         ' Set(varVAdd, false); Select(vLoad); Notify("Variance on the board.", NotificationType.Success),\n'
         ' Notify("Not saved. Check your connection and try again.", NotificationType.Error), true)')
out.append(btn("vSave", '"PUT ON THE BOARD"', SAVEV, 1176, 860, 200, 52, size=13, color=WHITE, fill=GREEN,
               extra=vx({"DisplayMode": F('If(IsBlank(vTxtTitle.Text) || IsBlank(vTxtMag.Text) || IsBlank(vTxtOwn.Text), DisplayMode.Disabled, DisplayMode.Edit)')})))
out.append(btn("vCancel", '"CANCEL"', 'Set(varVAdd, false)', 1004, 860, 160, 52, size=13, color=DARK, fill=G1, extra=vx()))
out.append(label("vReq", '"Headline, magnitude and owner are required. Magnitude is in operational units, not dollars."', 544, 870, 450, 40, size=10, color=G9, extra=VA))
write_themed(OUTV, "".join(out)); print("wrote", OUTV)
