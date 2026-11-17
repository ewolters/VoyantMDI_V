# Tier 3 Board v1 generator (1920x1080): plant leadership. SQDCP by value stream, period DAY / WEEK / MONTH to date,
# weekly (13) and monthly (12) trends vs target, drill PLANT -> VALUE STREAM -> LINE, KPI focus view.
# History: computes the last 7 days per line with the SAME formulas as Tier 2 and saves closed days to KPI_Daily.
exec(open("/tmp/claude-0/gen/theme.py").read())
import os, sys
HERE = "/tmp/claude-0/gen"
_src = open(os.path.join(HERE, "t2v2.py")).read().split("# =========================== SUB-BAR")[0]
_src = _src.replace('exec(open("/tmp/claude-0/gen/theme.py").read())', '')
exec(_src)          # T2 helpers, DOMS/DEF/TIPS, LOAD, DAYREC (same daily math as Tier 2)
out.clear()         # drop T2's header controls
OUT = sys.argv[1] if len(sys.argv) > 1 else "/mnt/user-data/outputs/T3_Board_v1.pa.yaml"

# all shifts at Tier 3
DAYREC = DAYREC.replace(SHM, "true").replace('(ddShift.Selected.Value = "All" || EndsWith(ShiftKey, "-S" & ddShift.Selected.Value))', "true")
assert "ddShift" not in DAYREC
DAYREC = DAYREC.replace('" Frontier"', '" safety audits"')
LOAD = LOAD.replace("(Frontier)", "(safety audits)")

exec(open("/tmp/claude-0/gen/t3_metrics.py").read())
KP = LETTERS
TOPG0 = 'If(!IsBlank(varLn), varLn, !IsBlank(varVert), varVert, !IsBlank(varVS), varVS, "PLANT")'
KN = LNAME
RAWF = ["Plan", "EffW", "Tgt", "Act", "OEEw", "Shifts", "Scrap", "CrewA", "CrewS", "DT", "RW", "Saf", "TSn", "TSop", "TSnr", "TSu", "MNt",
        "PCd", "PCf", "PCx", "Esc", "AO", "OV", "DTe", "DTl", "EscL", "Fz", "Fch", "FA"]
TIP3 = {L: LNAME[L].title() + ": " + "; ".join(m[2] for m in MET if m[1] == L) + ". Tile = worst metric; tap for each metric." for L in LETTERS}
def AGG(tbl, extra, nd="1"):
    return wrap_sums(AGGM(tbl, extra, nd))
SWM = lambda fld, codeexpr: 'Switch(' + codeexpr + ', ' + ", ".join(f'"{c}", {fld}{c}' for c in CODES) + ')'
SWMR = lambda fld, R, codeexpr: 'Switch(' + codeexpr + ', ' + ", ".join(f'"{c}", {R}.{fld}{c}' for c in CODES) + ')'

MEMBER = 'If(g.K = "top", If(!IsBlank(varLn), Line = varLn, !IsBlank(varVert), VS = varVert, !IsBlank(varVS), TVS = varVS, true), g.K = "vs", TVS = g.G, g.K = "vert", VS = g.G, Line = g.G)'
TOPOF = lambda X: f'With({{v_: LookUp(colVS, Nm = {X})}}, If(IsBlank(v_) || IsBlank(v_.Up), {X}, v_.Up))'
WKSTART = 'If(varWS = "Sunday", DateAdd(varD, -(Weekday(varD, StartOfWeek.Sunday) - 1), TimeUnit.Days), DateAdd(varD, -(Weekday(varD, StartOfWeek.Monday) - 1), TimeUnit.Days))'

# ============================ LOAD ============================
# Tier 2's LOAD (7 days of board data ending the reviewed day) + config + 13 months of KPI_Daily history, chunked by month (row limit)
LOAD = LOAD.replace("Tier 2:", "Tier 3:")
assert "Filter(PC_Results, Created >= varD0" in LOAD
LOAD = LOAD.replace("Filter(PC_Results, Created >= varD0", "Filter(PC_Results, Created >= varR0")
_w = 'ShiftDate >= varD0 && ShiftDate < varD1'
for _c in ("colShift, Filter(HxH_Shift, ", "colDTH, Filter(HxH_Hourly, ", "colSafe, Filter(HxH_Hourly, ", "colQA, Filter(QA_Rework, "):
    assert _c + _w in LOAD, _c
    LOAD = LOAD.replace(_c + _w, _c + _w.replace("varD0", "varR0"))
for _c in ("colFA, Filter(SAF_Audits, ", "colFR, Filter(SAF_Results, "):
    assert _c + "AuditDate >= varD0" in LOAD, _c
    LOAD = LOAD.replace(_c + "AuditDate >= varD0", _c + "AuditDate >= varR0")
assert LOAD.startswith("Set(varD, ddDate.Selected.D); Set(varD0, DateAdd(varD, -6, TimeUnit.Days));")
LOAD = LOAD.replace("Set(varD0, DateAdd(varD, -6, TimeUnit.Days));", "Set(varD0, DateAdd(varD, -6, TimeUnit.Days)); Set(varR0, If(Date(Year(varD), Month(varD), 1) < varD0, Date(Year(varD), Month(varD), 1), varD0));", 1)
LOAD3 = LOAD.replace('If(IsBlank(varLayer), Set(varLayer, "floor"));\n', '').replace('Set(varLoadedAt, Now());\nSelect(btnCalc)', '')
assert LOAD3 != LOAD
KDLOAD = ''.join(
    (f'With({{m0: DateAdd(Date(Year(varD), Month(varD), 1), -{i}, TimeUnit.Months), m1: DateAdd(Date(Year(varD), Month(varD), 1), -{i - 1}, TimeUnit.Months)}},\n'
     f' {"ClearCollect" if i == 12 else "Collect"}(colKD, Filter(KPI_Daily, KPIDate >= m0 && KPIDate < m1)));\n')
    for i in range(12, -1, -1))
LOAD3 += ('IfError(ClearCollect(colMet, ForAll(Sort(Filter(KPI_Metrics, Active), DisplayOrder), {Code: Title, Ltr: Letter.Value, Nm: MetricName, Sh: Short, Un: Unit, Hi: Better.Value = "Higher", Gr: Coalesce(Green, 0), Am: Coalesce(Amber, 0), Ord: Coalesce(DisplayOrder, 0)})), Notify("Tier 3: could not load KPI_Metrics", NotificationType.Error), true);\n'
          'If(CountRows(colMet) = 0, ClearCollect(colMet, ' + default_catalog_fx() + '));\n'
          + ''.join(f'Set(varHd{L}, First(SortByColumns(Filter(colMet, Ltr = "{L}"), "Ord", SortOrder.Ascending)).Code);\n' for L in LETTERS) +
          'IfError(ClearCollect(colVS, ForAll(Sort(Filter(ValueStreams, Active), DisplayOrder), {Nm: Title, Up: Coalesce(ParentVS, ""), Ord: Coalesce(DisplayOrder, 0), Leader: Coalesce(Leader, "")})), Notify("Tier 3: could not load ValueStreams", NotificationType.Error), true);\n'
          'Collect(colVS, ForAll(Filter(Distinct(colLines, ValueStream), !IsBlank(Value) && !(Value in colVS.Nm)), {Nm: Value, Up: "", Ord: 9000, Leader: ""}));\n'
          'Set(varWS, Coalesce(LookUp(colCfg, Title = "T3_WeekStart").SettingValue, "Monday"));\n'
          'Set(varT2Link, LookUp(colCfg, Title = "App_Tier2").SettingValue);\n'
          'Set(varNewsLink, LookUp(colCfg, Title = "App_Newspaper").SettingValue);\n'
          'IfError(\n' + KDLOAD + ' true, Notify("Tier 3: could not load KPI_Daily history. Run the list setup if the list is missing.", NotificationType.Error), true);\n'
          'Set(varLoadedAt, Now());\nSelect(btnCalc)')

# ============================ CALC (7 days, write history, merge) ============================
ZERO = ", ".join(f"{k}: 0" for k in RAWF if k not in ("Fz", "Fch", "FA"))
FLOOR7 = ('ForAll(Sequence(7, 0) As k, With({dD: DateAdd(varD0, k.Value, TimeUnit.Days)}, With({dE: DateAdd(dD, 1, TimeUnit.Days)},\n'
          ' {Line: "FLOOR", VS: "Plant-wide", Ord: 99999, Day: dD, ' + ZERO + ',\n'
          '  Fz: CountRows(Filter(colFR, IsBlank(Line) && AuditDate >= dD && AuditDate < dE)),\n'
          '  Fch: CountRows(Filter(colFR, IsBlank(Line) && AuditDate >= dD && AuditDate < dE && (Severity.Value = "Critical" || Severity.Value = "High"))),\n'
          '  FA: CountRows(Filter(colFA, IsBlank(Line) && AuditDate >= dD && AuditDate < dE))})))')
DIFF = ' || '.join(f'Round(Coalesce(ex.{k}, 0), 0) <> Round({k}, 0)' for k in RAWF)
PATCHREC = ', '.join([f'{k}: r.{k}' for k in RAWF])
MAPKD = ', '.join(f'{k}: Coalesce({k}, 0)' for k in RAWF)
MAPD = ', '.join(f'{k}: {k}' for k in RAWF)
CALC3 = ('ClearCollect(colDaily, Ungroup(ForAll(colLines As ln,\n'
 '  With({nEv: CountRows(Filter(colCards, Frequency.Value = "Every shift" && (Line = "All" || ln.Title in Split(Line, ",")))),\n'
 '        nDy: CountRows(Filter(colCards, Frequency.Value = "Daily" && (Line = "All" || ln.Title in Split(Line, ","))))},\n'
 '   {rows: ForAll(Sequence(7, 0) As k,\n   ' + DAYREC + ')})), rows));\n'
 'Collect(colDaily, ' + FLOOR7 + ');\n'
 '// save closed days that are new or changed\n'
 'ClearCollect(colChg, Filter(AddColumns(Filter(colDaily, Day < Today() && (Shifts > 0 || FA > 0 || AO > 0 || Saf > 0)), Key, Line & "|" & Text(Day, "yyyymmdd")),\n'
 '  With({ex: LookUp(colKD, Title = Key)}, IsBlank(ex) || ' + DIFF + ')));\n'
 'Set(varWrote, CountRows(colChg));\n'
 'IfError(ForAll(colChg As r, With({ex: LookUp(colKD, Title = r.Key)},\n'
 '  Patch(KPI_Daily, If(IsBlank(ex), Defaults(KPI_Daily), LookUp(KPI_Daily, ID = ex.ID)),\n'
 '   {Title: r.Key, Line: r.Line, ValueStream: r.VS, KPIDate: r.Day, ' + PATCHREC + ', UpdatedAt: Now(), UpdatedBy: User().Email}))),\n'
 '  Set(varWrote, -1); Notify("Tier 3: history not saved (KPI_Daily). Check list permissions.", NotificationType.Warning), true);\n'
 '// history = saved days before the window + freshly computed window\n'
 'ClearCollect(colHist, Ungroup(Table({t: ForAll(Filter(colKD, KPIDate < varD0), {Line: Line, VS: ValueStream, TVS: ' + TOPOF('ValueStream') + ', Day: KPIDate, ' + MAPKD + '})},\n'
 '  {t: ForAll(colDaily, {Line: Line, VS: VS, TVS: ' + TOPOF('VS') + ', Day: Day, ' + MAPD + '})}), t));\n'
 'Set(varHistDays, CountRows(Distinct(colHist, Day)));\n'
 'Select(btnAgg)')

# ============================ AGG (groups, period tiles, weekly + monthly trends) ============================
TRP = ", ".join(f'tr{k}: Concat(LastN(Filter(colW As q, q.G = p.G), 8), st{k})' for k in KP)
AGG3 = ('Set(varWk, ' + WKSTART + ');\n'
 'ClearCollect(colScopeL, Filter(colLines, If(!IsBlank(varVert), ValueStream = varVert, IsBlank(varVS), true, ' + TOPOF('ValueStream') + ' = varVS)));\n'
 'Set(varP0, Switch(varPer, "WEEK", varWk, "MONTH", Date(Year(varD), Month(varD), 1), varD));\n'
 'If(!IsBlank(varLn), ClearCollect(colGroups, {G: varLn, K: "top", Ord: 0}),\n'
 ' !IsBlank(varVert), ClearCollect(colGroups, {G: varVert, K: "top", Ord: 0}); Collect(colGroups, ForAll(Filter(colLines, ValueStream = varVert) As l, {G: l.Title, K: "line", Ord: Coalesce(l.DisplayOrder, 0)})),\n'
 ' !IsBlank(varVS), ClearCollect(colGroups, {G: varVS, K: "top", Ord: 0}); Collect(colGroups, ForAll(Filter(colVS, Up = varVS) As v, {G: v.Nm, K: "vert", Ord: v.Ord}));\n'
 '  Collect(colGroups, ForAll(Filter(colLines, ValueStream = varVS) As l, {G: l.Title, K: "line", Ord: 100000 + Coalesce(l.DisplayOrder, 0)})),\n'
 ' ClearCollect(colGroups, {G: "PLANT", K: "top", Ord: 0}); Collect(colGroups, ForAll(Filter(colVS, IsBlank(Up)) As v, {G: v.Nm, K: "vs", Ord: v.Ord}));\n'
 '  If(CountRows(Filter(colHist, VS = "Plant-wide" && (Fz > 0 || FA > 0))) > 0, Collect(colGroups, {G: "Plant-wide", K: "vs", Ord: 99999})));\n'
 'ClearCollect(colW, Ungroup(ForAll(colGroups As g, {rows: ForAll(Sequence(13, 0) As w,\n'
 '  With({w0: DateAdd(varWk, -7 * (12 - w.Value), TimeUnit.Days)},\n   '
 + AGG('Filter(colHist, Day >= w0 && Day < DateAdd(w0, 7, TimeUnit.Days) && ' + MEMBER + ')', 'G: g.G, K: g.K, i: w.Value, P0: w0, L: Text(w0, "m/d"), Cur: w.Value = 12', 'If(w.Value = 12, DateDiff(w0, varD1, TimeUnit.Days), 7)') +
 '))}), rows));\n'
 'ClearCollect(colM, Ungroup(ForAll(colGroups As g, {rows: ForAll(Sequence(12, 0) As m,\n'
 '  With({m0: DateAdd(Date(Year(varD), Month(varD), 1), -(11 - m.Value), TimeUnit.Months)},\n   '
 + AGG('Filter(colHist, Day >= m0 && Day < DateAdd(m0, 1, TimeUnit.Months) && Day < varD1 && ' + MEMBER + ')', 'G: g.G, K: g.K, i: m.Value, P0: m0, L: Text(m0, "mmm"), Cur: m.Value = 11', 'DateDiff(m0, If(DateAdd(m0, 1, TimeUnit.Months) < varD1, DateAdd(m0, 1, TimeUnit.Months), varD1), TimeUnit.Days)') +
 '))}), rows));\n'
 'ClearCollect(colP, ForAll(colGroups As g,\n  '
 + AGG('Filter(colHist, Day >= varP0 && Day < varD1 && ' + MEMBER + ')', 'G: g.G, K: g.K, Ord: g.Ord', 'DateDiff(varP0, varD1, TimeUnit.Days)') + '));\n'
 'ClearCollect(colP, ForAll(colP As p, Patch(p, {' + TRP + '})));\n'
 'ClearCollect(colY, ForAll(colGroups As g,\n  ' + AGG('Filter(colHist, Year(Day) = Year(varD) && Day < varD1 && ' + MEMBER + ')', 'G: g.G', 'DateDiff(Date(Year(varD), 1, 1), varD1, TimeUnit.Days)') + '));\n'
 'ClearCollect(colDy, Ungroup(ForAll(colGroups As g, {rows: ForAll(Sequence(7, 0) As d,\n  With({d0: DateAdd(varWk, d.Value, TimeUnit.Days)},\n   ' + AGG('Filter(colHist, Day >= d0 && Day < DateAdd(d0, 1, TimeUnit.Days) && Day < varD1 && ' + MEMBER + ')', 'G: g.G, i: d.Value, P0: d0, L: Text(d0, "ddd m/d"), Cur: d0 = varD, Fut: d0 > varD', '1') + '))}), rows));\n'
 'ClearCollect(colWTD, ForAll(colGroups As g,\n  ' + AGG('Filter(colHist, Day >= varWk && Day < varD1 && ' + MEMBER + ')', 'G: g.G', 'DateDiff(varWk, varD1, TimeUnit.Days)') + '));\n'
 'ClearCollect(colMTD, ForAll(colGroups As g,\n  ' + AGG('Filter(colHist, Day >= Date(Year(varD), Month(varD), 1) && Day < varD1 && ' + MEMBER + ')', 'G: g.G', 'DateDiff(Date(Year(varD), Month(varD), 1), varD1, TimeUnit.Days)') + '));\n'
 'Set(varTop, LookUp(colP, K = "top"))')

# ============================ HEADER ============================
out.append(rect("hdrBar", DARK, 0, 0, 1920, 90))
out.append(label("lblBrand", '"voyant"', 24, 6, 170, 52, size=34, color=WHITE, font="Georgia"))
out.append(label("lblBrandSub", '"NEW ALBANY"', 27, 56, 170, 24, size=10, bold=True, color=TEAL))
out.append(label("lblTitle", '"TIER 3"', 190, 20, 170, 50, size=26, bold=True, color=AQUA, font="Georgia", extra={"Wrap": "=false"}))
out.append(cap("cPer", "PERIOD", 380, 6, 400))
for i, (k, n) in enumerate([("DAY", "DAY"), ("WEEK", "WEEK TO DATE"), ("MONTH", "MONTH TO DATE")]):
    out.append(btn(f"btnPer{k}", f'"{n}"', f'Set(varPer, "{k}"); Select(btnAgg)', 380 + i * 150, 28, 144, 52, size=12,
                   fill=f'If(varPer = "{k}", {TEAL}, {TEAL_D})', color=f'If(varPer = "{k}", {DARK}, {WHITE})'))
out.append(cap("cDate", "DAY REVIEWED", 840, 6, 190))
out.append(dd("ddDate", 'ForAll(Sequence(30, 0), With({d: DateAdd(Today(), -Value, TimeUnit.Days)}, {Value: Text(d, "ddd m/d"), D: d}))', 840, 28, 190, 52,
              default='Text(DateAdd(Today(), -1, TimeUnit.Days), "ddd m/d")', onchange="Select(btnRefresh)", size=15, bold=True))
out.append(btn("btnRefresh", '"REFRESH"', 'If(IsBlank(varPer), Set(varPer, "DAY"));\n' + LOAD3, 1040, 28, 130, 52, size=14))
out.append(label("lblLoaded", 'If(IsBlank(varLoadedAt), "Tap REFRESH", "Updated " & Text(varLoadedAt, "h:mm AM/PM") & Char(10) & If(varWrote < 0, "history NOT saved", varWrote > 0, Text(varWrote) & " day-rows saved to history", "history up to date"))',
                 1180, 24, 260, 60, size=10, color=G5))
out.append(label("lblScope", 'If(!IsBlank(varLn), "Line " & varLn, !IsBlank(varVert), varVert, Coalesce(varVS, "Whole plant")) & Char(10) & Switch(varPer, "WEEK", "Week to date · " & Text(varWk, "m/d") & "–" & Text(varD, "m/d"), "MONTH", "Month to date · " & Text(varD, "mmmm"), Text(varD, "dddd m/d"))',
                 1450, 10, 458, 70, size=13, bold=True, color=AQUA, align="Right"))
out.append(tap("btnCalc", CALC3, 0, 1079, 1, 1))
out.append(tap("btnAgg", AGG3, 1, 1079, 1, 1))

# ============================ SUB-BAR ============================
GRID = 'IsBlank(varKPI)'; KPIV = '!IsBlank(varKPI)'
KNAME = 'Switch(varKPI, ' + ", ".join(f'"{k}", "{KN[k]}"' for k in KP) + ')'
out.append(rect("subBar", LIGHT, 0, 90, 1920, 44))
out.append(btn("bcPlant", '"PLANT"', 'Set(varVS, Blank()); Set(varVert, Blank()); Set(varLn, Blank()); Set(varKPI, Blank()); Select(btnAgg)', 12, 96, 110, 32, size=11,
               fill=f'If({TOPG0} = "PLANT" && IsBlank(varKPI), {DARK}, {G1})', color=f'If({TOPG0} = "PLANT" && IsBlank(varKPI), {WHITE}, {DARK})'))
out.append(V(btn("bcVS", '"›  " & varVS', 'Set(varKPI, Blank()); Set(varVert, Blank()); Set(varLn, Blank()); Select(btnAgg)', 128, 96, 180, 32, size=10,
                 fill=f'If({TOPG0} = varVS && IsBlank(varKPI), {DARK}, {G1})', color=f'If({TOPG0} = varVS && IsBlank(varKPI), {WHITE}, {DARK})'), '!IsBlank(varVS)'))
out.append(V(btn("bcVert", '"›  " & varVert', 'Set(varKPI, Blank()); Set(varLn, Blank()); Select(btnAgg)', 314, 96, 180, 32, size=10,
                 fill=f'If({TOPG0} = varVert && IsBlank(varKPI), {DARK}, {G1})', color=f'If({TOPG0} = varVert && IsBlank(varKPI), {WHITE}, {DARK})'), '!IsBlank(varVert)'))
out.append(V(btn("bcLn", '"›  LINE " & varLn', 'Set(varKPI, Blank())', '128 + If(IsBlank(varVS), 0, 186) + If(IsBlank(varVert), 0, 186)', 96, 130, 32, size=10,
                 fill=f'If(IsBlank(varKPI), {DARK}, {G1})', color=f'If(IsBlank(varKPI), {WHITE}, {DARK})'), '!IsBlank(varLn)'))
out.append(V(btn("bcKPI", '"›  " & ' + KNAME, 'false', '128 + If(IsBlank(varVS), 0, 186) + If(IsBlank(varVert), 0, 186) + If(IsBlank(varLn), 0, 136)', 96, 170, 32, size=10, fill=DARK, color=WHITE), KPIV))
TABS = [("PERFORMANCE", "Screen1"), ("BOWLER", "scrBowler"), ("VARIANCES", "scrVariance"), ("ROOT CAUSE", "")]
def tabbar(pfx, cur):
    r = []
    for i, (n, scr) in enumerate(TABS):
        on = (scr == cur)
        r.append(btn(f"{pfx}Tab{i}", f'"{n}"', f'Navigate({scr}, ScreenTransition.None)' if scr else 'false', 830 + i * 160, 96, 154, 32, size=10,
                     fill=(TEAL if on else (G1 if not scr else TEAL_D)), color=(DARK if (on or not scr) else WHITE),
                     extra=({"DisplayMode": "=DisplayMode.Disabled", "DisabledFill": F(G1), "DisabledColor": F(G5), "Tooltip": '="Root cause analysis: coming soon"'} if not scr else None)))
    return r
out.extend(tabbar("p", "Screen1"))
out.append(V(btn("btnT2", '"OPEN TIER 2  ↗"', 'Launch(varT2Link)', 1576, 96, 180, 32, size=11, fill=TEAL, color=DARK,
                 extra={"Tooltip": '="Opens the Tier 2 board (MDI_Config → App_Tier2)"'}), '!IsBlank(varT2Link)'))
out.append(btn("btnTrend", 'If(varTrend = "M", "TRENDS: MONTHS", "TRENDS: WEEKS")', 'Set(varTrend, If(varTrend = "M", "W", "M"))', 1762, 96, 146, 32, size=10, fill=TEAL_D, color=WHITE))

# ============================ GRID (plant or value stream) ============================
GX = 12; LWID = 260; CW = 318; CS = 326
def cx(i): return LWID + 8 + i * CS
TOPR = 'varTop'
COLS = lambda st: COL(st)
def DOT8(tr, i): return f'Switch(Mid({tr}, {i}, 1), "G", {GREEN}, "A", {AMBER}, "R", {RED}, {G1})'
for i, k in enumerate(KP):
    out.append(V(rect(f"gh{k}", TEAL_D, GX + cx(i), 138, CW, 32), GRID))
    _cat = LCAT[k]
    out.append(V(label(f"ghT{k}", f'"{KN[k]}" & With({{n: CountRows(Filter(colNews, SQDCP.Value = "{_cat}" && (Status.Value = "Open" || Status.Value = "In progress") && If(!IsBlank(varLn), Line = varLn, IsBlank(varVS), true, Line in colScopeL.Title)))}}, If(n > 0, "  ·  " & n & " open", "")) & "  ▸"', GX + cx(i), 138, CW, 32, size=11, bold=True, color=WHITE, align="Center"), GRID))
    out.append(tap(f"ghTap{k}", f'Set(varKPI, "{k}"); Set(varMet, varHd{k})', GX + cx(i), 138, CW, 32, vis=GRID, tip=f'"{TIP3[k]}"'))
out.append(V(label("ghName", 'If(!IsBlank(varVert), "LINE", !IsBlank(varVS), "VERTICAL / LINE", "VALUE STREAM")', GX, 138, LWID, 32, size=11, bold=True, color=TEAL_D, align="Center"), GRID))

def tiles(pfx, R, y0, h, indent, big=26, dots=True):
    ks = []
    for i, k in enumerate(KP):
        x = cx(i) + (GX if indent == 0 else 0)
        ks.append(rect(f"{pfx}b{k}", COL(f"{R}.st{k}"), x, y0, CW, h, indent=indent, extra={"Tooltip": F(f'"{TIP3[k]}" & Char(10) & {R}.sub{k}')}))
        ks.append(label(f"{pfx}v{k}", f"{R}.txt{k}", x + 10, y0 + 2, 176, h - 26, size=big, bold=True, color=WHITE, valign="Middle", indent=indent, extra={"Wrap": "=false"}))
        ks.append(label(f"{pfx}s{k}", f"{R}.sub{k}", x + 186, y0 + 4, CW - 192, h - 28, size=9, bold=True, color=WHITE, align="Right", valign="Middle", indent=indent))
        if dots:
            for d in range(1, 9):
                ks.append(rect(f"{pfx}d{k}{d}", DOT8(f"{R}.tr{k}", d), x + CW - 8 - (9 - d) * 22, y0 + h - 22, 18, 12, indent=indent,
                               extra={"BorderColor": F(f'If({d} = 8, {WHITE}, {CLEAR})'), "BorderThickness": F(f'If({d} = 8, 2, 0)')}))
            ks.append(label(f"{pfx}w{k}", '"8 wks"', x + 8, y0 + h - 26, 60, 20, size=8, color=WHITE, indent=indent))
    return ks
# top (plant or value-stream total)
out.append(V(rect("tNameBg", DARK, GX, 176, LWID, 88), GRID))
out.append(V(label("tName", TOPG0, GX + 6, 180, LWID - 12, 46, size=f'If(Len({TOPG0}) > 14, 16, Len({TOPG0}) > 10, 19, 22)', bold=True, color=WHITE, align="Center", font="Georgia"), GRID))
out.append(V(label("tSub", 'If(!IsBlank(varLn), LookUp(colLines, Title = varLn).ValueStream, !IsBlank(varVert), "in " & varVS & "  ·  " & CountRows(colScopeL) & " lines", Text(CountRows(colScopeL)) & " lines")', GX, 228, LWID, 24, size=10, color=AQUA, align="Center"), GRID))
for c in tiles("t", TOPR, 176, 88, 0, big=26):
    out.append(V(c, GRID))
# rows
RITEMS = 'SortByColumns(Filter(colP, K <> "top"), "Ord", SortOrder.Ascending)'
TAPROW = 'If(ThisItem.K = "vs" && ThisItem.G <> "Plant-wide", Set(varVS, ThisItem.G); Select(btnAgg), ThisItem.K = "vert", Set(varVert, ThisItem.G); Select(btnAgg), ThisItem.K = "line", Set(varLn, ThisItem.G); Select(btnAgg))'
gk = [rect("rNameBg", f'If(ThisItem.K = "line", {DARK}, {TEAL_D})', 0, 3, LWID, 72, indent=I),
      label("rName", 'ThisItem.G', 6, 5, LWID - 12, 42, size='If(Len(ThisItem.G) > 15, 15, 18)', bold=True, color=WHITE, align="Center", font="Georgia", indent=I),
      label("rSub", 'Switch(ThisItem.K, "vs", If(ThisItem.G = "Plant-wide", "zones with no line", With({nv: CountRows(Filter(colVS, Up = ThisItem.G))}, Text(CountRows(Filter(colLines, ' + TOPOF('ValueStream') + ' = ThisItem.G))) & " lines" & If(nv > 0, " · " & nv & " verticals", "") & "  ▸")), "vert", "vertical  ·  " & CountRows(Filter(colLines, ValueStream = ThisItem.G)) & " lines  ▸", LookUp(colLines, Title = ThisItem.G).ValueStream & "  ▸")',
            0, 46, LWID, 22, size=10, color=AQUA, align="Center", indent=I),
      ]
gk += [c for c in tiles("r", "ThisItem", 3, 72, I, big=22)]
gk.append(tap("rTap", TAPROW, 0, 0, 1896, 78, indent=I, tip='If(ThisItem.K = "line", "Open line " & ThisItem.G & " trends", ThisItem.G = "Plant-wide", "Zones with no line", "Open " & ThisItem.G & " by line")'))
out.append(gal("galRows", RITEMS, GX, 272, 1896, 312, 78, gk, vis=GRID + ' && IsBlank(varLn)', extra={"TemplateFill": F(WHITE)}))
out.append(V(label("lblEmpty", 'If(!IsBlank(varLn), "", IsBlank(varLoadedAt), "Loading…", CountRows(Filter(colP, K <> "top")) = 0, "No value streams. Set ValueStream on the Lines list.", "")', GX, 400, 1896, 60, size=16, color=G9, align="Center"), GRID))

# ---- trend charts (grid view): one per KPI for the top row ----
HEX = {"G": "#2EA043", "A": "#D29922", "R": "#CF222E"}
def chartN(tbexpr, W, H, fs=11, vals=True):
    TOP = 26 if vals else 10; BOT = 22; PH = H - TOP - BOT
    col = 'Switch(S, "G", "%s", "A", "%s", "R", "%s", "#B1B3B3")' % (HEX["G"], HEX["A"], HEX["R"])
    f = lambda e: f'Text({e}, "0.0")'
    bh = f'Max(V / sc * {PH}, 2)'
    cxx = '(i * sw + sw / 2)'
    cyT = f'({TOP + PH} - T / sc * {PH})'
    svg = (f'"<svg xmlns=\'http://www.w3.org/2000/svg\' width=\'{W}\' height=\'{H}\' viewBox=\'0 0 {W} {H}\'>" & '
           f'Concat(Filter(tb, Cur), "<rect x=\'" & {f("i * sw + 1")} & "\' y=\'0\' width=\'" & {f("sw - 2")} & "\' height=\'{H}\' fill=\'#EEF6F6\'/>") & '
           f'"<line x1=\'0\' y1=\'{TOP + PH}\' x2=\'{W}\' y2=\'{TOP + PH}\' stroke=\'#D9D9D6\' stroke-width=\'1\'/>" & '
           f'Concat(tb, "<rect x=\'" & {f("i * sw + sw * 0.2")} & "\' y=\'" & {f(f"{TOP + PH} - {bh}")} & "\' width=\'" & {f("sw * 0.6")} & "\' height=\'" & {f(bh)} & "\' rx=\'2\' fill=\'" & {col} & "\'/>") & '
           f'If(CountRows(Filter(tb, T >= 0)) > 1, "<polyline fill=\'none\' stroke=\'#07272D\' stroke-width=\'2\' stroke-dasharray=\'5 4\' points=\'" & Concat(Filter(tb, T >= 0), {f(cxx)} & "," & {f(cyT)} & " ") & "\'/>", "") & '
           f'Concat(tb, "<text x=\'" & {f(cxx)} & "\' y=\'{H - 6}\' font-family=\'Arial\' font-size=\'{fs}\' text-anchor=\'middle\' fill=\'" & If(Cur, "#07272D", "#75787B") & "\' font-weight=\'" & If(Cur, "bold", "normal") & "\'>" & L & "</text>") & ')
    if vals:
        svg += (f'Concat(Filter(tb, Sh), "<text x=\'" & {f(cxx)} & "\' y=\'" & {f(f"{TOP + PH} - {bh} - 6")} & "\' font-family=\'Arial\' font-size=\'{fs}\' font-weight=\'bold\' text-anchor=\'middle\' fill=\'" & {col} & "\'>" & Substitute(Substitute(Tx, "&", "and"), "<", "") & "</text>") & ')
    svg += '"</svg>"'
    return ('With({tb0: ' + tbexpr + '},\n With({sc: Max(Coalesce(Max(tb0, V), 0), Coalesce(Max(tb0, T), 0), 0.0001) * 1.15, sw: ' + str(W) + ' / Max(CountRows(tb0), 1)},\n'
            '  With({tb: ForAll(Sequence(CountRows(tb0)), With({r: Index(tb0, Value)}, {i: Value - 1, V: Coalesce(r.V, 0), T: Coalesce(r.T, -1), S: r.S, Tx: r.Tx, L: r.L, Cur: r.Cur, Sh: r.Sh}))},\n'
            '   "data:image/svg+xml;utf8," & EncodeUrl(' + svg + '))))')
def TRENDM(codeexpr, G, show_all=True):
    src = f'SortByColumns(If(varTrend = "M", Filter(colM, G = {G}), Filter(colW, G = {G})), "P0", SortOrder.Ascending)'
    return f'ForAll({src}, {{V: {SWM("v_", codeexpr)}, T: {SWM("g_", codeexpr)}, S: {SWM("s_", codeexpr)}, Tx: {SWM("t_", codeexpr)}, L: L, Cur: Cur, Sh: {"true" if show_all else "Cur"}}})'
MNAME = lambda codeexpr: f'LookUp(colMet, Code = {codeexpr}).Nm'
TOPG = 'If(!IsBlank(varLn), varLn, !IsBlank(varVert), varVert, !IsBlank(varVS), varVS, "PLANT")'
CY = 596; CH = 472
CYE = lambda off: f'If(!IsBlank(varLn), 272, {CY}) + {off}'
for i, k in enumerate(KP):
    x = GX + i * 380
    out.append(V(rect(f"cBg{k}", WHITE, x, CYE(0), 372, CH, extra={"BorderColor": F(G1), "BorderThickness": "=2"}), GRID))
    out.append(V(label(f"cT{k}", f'"{KN[k]}  ·  " & Upper(Coalesce({MNAME(f"varHd{k}")}, "no metric")) & "  ·  " & If(varTrend = "M", "12 MO", "13 WK")', x + 12, CYE(6), 348, 26, size=10, bold=True, color=TEAL_D), GRID))
    out.append(V(label(f"cG{k}", f'With({{m: LookUp(colMet, Code = varHd{k})}}, If(IsBlank(m), "", "- - target " & If(m.Hi, "≥ ", "≤ ") & m.Gr & " " & m.Un))', x + 12, CYE(30), 348, 20, size=8, color=G9), GRID))
    out.append(svgimg(f"img{k}", chartN(TRENDM(f"varHd{k}", TOPG, show_all=False), 348, 400, fs=10), x + 12, CYE(56), 348, 400, GRID))
    out.append(tap(f"cTap{k}", f'Set(varKPI, "{k}"); Set(varMet, varHd{k})', x, CYE(0), 372, CH, vis=GRID, tip=f'"Open {KN[k].lower()} trends"'))

# ============================ LETTER PAGE (every metric: trend, Pareto, Newspaper) ============================
KV = KPIV
SWT = lambda fld, R: 'Switch(varKPI, ' + ", ".join(f'"{k}", {R}.{fld}{k}' for k in KP) + ')'
out.append(V(label("kTitle", KNAME + ' & "  ·  " & ' + TOPG + ' & "  ·  " & CountRows(Filter(colMet, Ltr = varKPI)) & " metrics  ·  tap a metric for its Pareto and comparison"', GX, 140, 1500, 40, size=18, bold=True, color=TEAL_D, font="Georgia"), KV))
CAT = 'Switch(varKPI, "S", "Safety", "Q", "Quality", "D", "Delivery", "C", "Cost", "People")'
SCL = 'If(!IsBlank(varLn), Line = varLn, IsBlank(varVS), true, Line in colScopeL.Title)'
WSP = 'ShiftDate >= varP0 && ShiftDate < varD1'
WAP = 'AuditDate >= varP0 && AuditDate < varD1'
WCP = 'Created >= varP0 && Created < varD1'
PERW = 'Switch(varPer, "WEEK", "week to date", "MONTH", "month to date", Text(varD, "ddd m/d"))'
LW2 = 1180; RX = GX + LW2 + 12; RW2 = 1908 - RX
# metric rows
MROW = 150
mk = [rect("mBg", f'If(ThisItem.Code = varMet, RGBA(238, 246, 246, 1), {WHITE})', 0, 2, LW2, MROW - 6, indent=I, extra={"BorderColor": F(f'If(ThisItem.Code = varMet, {TEAL_D}, {G1})'), "BorderThickness": F('If(ThisItem.Code = varMet, 3, 1)')}),
      rect("mSt", COL(SWMR("s_", "varTop", "ThisItem.Code")), 0, 2, 10, MROW - 6, indent=I),
      label("mNm", 'ThisItem.Nm', 22, 8, 300, 30, size=14, bold=True, indent=I),
      label("mVal", SWMR("t_", "varTop", "ThisItem.Code"), 22, 40, 300, 50, size=24, bold=True, indent=I, extra={"Color": F(COL(SWMR("s_", "varTop", "ThisItem.Code"))), "Wrap": "=false"}),
      label("mTg", '"target " & If(ThisItem.Hi, "≥ ", "≤ ") & ThisItem.Gr & " " & ThisItem.Un & "  ·  amber " & ThisItem.Am', 22, 92, 300, 22, size=9, color=G9, indent=I),
      label("mPer", PERW, 22, 114, 300, 22, size=9, color=G9, indent=I)]
def svgimg_i(name, expr, x, y, w, h):
    d = {"Image": F(expr), "ImagePosition": "=ImagePosition.Fit"}; d.update(box(x, y, w, h))
    return ctrl(name, "Image@2.2.3", d, I)
mk.append(svgimg_i("mImg", chartN(TRENDM("ThisItem.Code", TOPG, show_all=True), 840, 136, fs=10), 330, 4, 840, 136))
mk.append(tap("mTap", 'Set(varMet, ThisItem.Code)', 0, 0, LW2, MROW, indent=I, tip='ThisItem.Nm & ": " & Switch(ThisItem.Code, ' + ", ".join(f'"{c}", "{TIPM[c]}"' for c in CODES) + ')'))
out.append(gal("galMet", 'SortByColumns(Filter(colMet, Ltr = varKPI), "Ord", SortOrder.Ascending)', GX, 184, LW2, 3 * MROW, MROW, mk, vis=KV, extra={"ShowScrollbar": "=true"}))
# heatmap for the selected metric
HM_ITEMS = 'SortByColumns(Filter(colP, K <> "top"), "Ord", SortOrder.Ascending)'
HMN = 13; HW = 70; HNW = 200; HY = 184 + 3 * MROW + 10
def HMCELL(j): return f'LookUp(If(varTrend = "M", colM, colW), G = ThisItem.G && i = {j})'
hk = [rect("hNameBg", TEAL_D, 0, 2, HNW, 36, indent=I),
      label("hName", 'ThisItem.G', 8, 2, HNW - 12, 36, size='If(Len(ThisItem.G) > 15, 10, 12)', bold=True, color=WHITE, indent=I),
      tap("hTap", TAPROW, 0, 2, HNW, 36, indent=I)]
for j in range(HMN):
    x = HNW + 6 + j * (HW + 4)
    rec = HMCELL(j)
    hk.append(rect(f"hc{j}", f'With({{c: {rec}}}, If(IsBlank(c), {G1}, ' + COL(SWMR("s_", "c", "varMet")) + '))', x, 2, HW, 36, indent=I,
                   extra={"Visible": F(f'varTrend <> "M" || {j} < 12')}))
    hk.append(label(f"ht{j}", f'With({{c: {rec}}}, If(IsBlank(c), "", ' + SWMR("t_", "c", "varMet") + '))', x, 2, HW, 36, size=9, bold=True, color=WHITE, align="Center", indent=I,
                    extra={"Visible": F(f'varTrend <> "M" || {j} < 12'), "Wrap": "=false"}))
out.append(V(label("hmHdr", '"BY " & If(!IsBlank(varVert), "LINE", IsBlank(varVS), "VALUE STREAM", "VERTICAL / LINE") & "  ·  " & Upper(Coalesce(' + MNAME("varMet") + ', ""))', GX, HY, HNW + 300, 28, size=10, bold=True, color=TEAL_D), KV))
for j in range(HMN):
    x = GX + HNW + 6 + j * (HW + 4)
    out.append(label(f"hh{j}", f'With({{c: LookUp(If(varTrend = "M", colM, colW), G = {TOPG} && i = {j})}}, If(IsBlank(c), "", c.L))', x, HY + 28, HW, 22, size=9, bold=True,
                     color=G9, align="Center", extra={"Visible": F(f'!IsBlank(varKPI) && (varTrend <> "M" || {j} < 12)')}))
out.append(gal("galHM", HM_ITEMS, GX, HY + 52, LW2, 1068 - HY - 52, 40, hk, vis=KV))
out.append(V(label("hmEmpty", 'If(CountRows(Filter(colP, K <> "top")) = 0, "Line view: no sub-levels to compare.", "")', GX, HY + 60, LW2, 30, size=11, color=G9), KV))

# ---- Pareto for the selected metric ----
def DTREASON(count=False):
    base = f'Filter(colDTH, {SCL} && {WSP})'
    return (f'ForAll(GroupBy(Filter(Ungroup(Table({{t: ForAll({base}, {{R: DT_Reason, M: Coalesce(DT_Minutes, 0)}})}}, {{t: ForAll({base}, {{R: DT2_Reason, M: Coalesce(DT2_Minutes, 0)}})}}), t), !IsBlank(R) && M > 0), R, G), '
            '{R: Substitute(R, "Machine - ", ""), N: ' + ('CountRows(G)' if count else 'Sum(G, M)') + ', Sub: Text(Sum(G, M)) & " min"})')
EMPTY = 'Filter(Table({R: "", N: 0, Sub: ""}), false)'
PSRC = {
 "SAF_EVENTS": f'ForAll(GroupBy(Filter(colSafe, {SCL} && {WSP}), Line, G), {{R: "Line " & Line, N: CountRows(G), Sub: ""}})',
 "SAF_HAZ": f'ForAll(GroupBy(Filter(colFR, {SCL} && {WAP}), Item, G), {{R: Coalesce(Item, "audit finding"), N: CountRows(G), Sub: Text(CountIf(G, Severity.Value = "Critical" || Severity.Value = "High")) & " C/H"}})',
 "SAF_AUD": f'ForAll(GroupBy(Filter(colFA, {SCL} && {WAP}), ZoneID, G), {{R: ZoneID, N: CountRows(G), Sub: ""}})',
 "QUAL_RW": f'ForAll(GroupBy(Filter(colQA, {SCL} && {WSP}), Reason, G), {{R: Coalesce(Reason, "(no reason)"), N: Sum(G, Coalesce(ReworkQty, 0)), Sub: Text(CountRows(G)) & " entries"}})',
 "QUAL_SCRAP": f'ForAll(GroupBy(Filter(colShift, {SCL} && {WSP} && !IsBlank(ScrapReasonCode)), ScrapReasonCode, G), {{R: ScrapReasonCode, N: Sum(G, Coalesce(FGScrapQty, 0)), Sub: Text(CountRows(G)) & " shifts"}})',
 "QUAL_NCR": EMPTY,
 "DEL_ATT": f'ForAll(GroupBy(Filter(colShift, {SCL} && {WSP}), Line, G), {{R: "Line " & Line, N: Sum(G, Max(Coalesce(TargetUnits, 0) - Coalesce(ActualUnits, 0), 0)), Sub: "units short"}})',
 "DEL_DT": DTREASON(),
 "DEL_DTE": DTREASON(count=True),
 "COST_OEE": DTREASON(),
 "COST_SPEED": f'ForAll(GroupBy(Filter(colShift, {SCL} && {WSP} && !IsBlank(SpeedLossReasonCode)), SpeedLossReasonCode, G), {{R: SpeedLossReasonCode, N: Sum(G, Max(Coalesce(TargetUnits, 0) - Coalesce(ActualUnits, 0), 0)), Sub: Text(CountRows(G)) & " shifts"}})',
 "PEO_CREW": f'ForAll(GroupBy(Filter(ForAll(Filter(colShift, {SCL} && {WSP}), {{R: If(ActualCrewSize < StdCrewSize, "Short staffed", ActualCrewSize > StdCrewSize, "Over standard: " & Coalesce(StaffingReasonCode, "no reason"), "")}}), !IsBlank(R)), R, G), {{R: R, N: CountRows(G), Sub: ""}})',
 "PEO_PC": f'ForAll(GroupBy(Filter(colRes, Answer.Value = "No" && {SCL} && {WCP}), ElementID, G), {{R: Coalesce(LookUp(colEl, ID = ElementID).Title, "Item " & ElementID), N: CountRows(G), Sub: "times missed"}})',
}
PTITLE = {"SAF_EVENTS": "EVENTS BY LINE", "SAF_HAZ": "HAZARDS BY ITEM", "SAF_AUD": "AUDITS BY ZONE", "QUAL_RW": "REWORK BY REASON (units)", "QUAL_SCRAP": "SCRAP BY REASON (units)",
          "QUAL_NCR": "NCRS (coming with the NCR app)", "DEL_ATT": "UNITS SHORT BY LINE", "DEL_DT": "DOWNTIME BY REASON (minutes)", "DEL_DTE": "DOWNTIME EVENTS BY REASON",
          "COST_OEE": "OEE LOSS: DOWNTIME BY REASON (minutes)", "COST_SPEED": "SPEED LOSS BY REASON (units)", "PEO_CREW": "STAFFING GAPS (shifts)", "PEO_PC": "MISSED PC ITEMS"}
PAR = lambda t: ('With({tb: SortByColumns(Filter(' + t + ', N > 0), "N", SortOrder.Descending)}, With({tot: Sum(tb, N)},\n'
                 ' ForAll(Sequence(Min(CountRows(tb), 10)), With({r: Index(tb, Value)}, {R: r.R, N: r.N, Sub: r.Sub, P: r.N / Max(First(tb).N, 1), Cum: Sum(FirstN(tb, Value), N) / Max(tot, 1)}))))')
PITEMS = 'Switch(varMet, ' + ", ".join(f'"{c}", {PAR(PSRC[c])}' for c in CODES) + ')'
out.append(V(rect("pBg", WHITE, RX, 184, RW2, 430, extra={"BorderColor": F(G1), "BorderThickness": "=2"}), KV))
out.append(V(label("pT", '"PARETO · " & Switch(varMet, ' + ", ".join(f'"{c}", "{PTITLE[c]}"' for c in CODES) + ')', RX + 14, 190, RW2 - 28, 26, size=11, bold=True, color=TEAL_D), KV))
out.append(V(label("pS", 'Coalesce(' + MNAME("varMet") + ', "") & "  ·  " & ' + PERW + ' & "  ·  " & ' + TOPG + ' & "  ·  % = cumulative"', RX + 14, 214, RW2 - 28, 20, size=9, color=G9), KV))
PRW = 250; PBW = RW2 - PRW - 150
pk = [label("pR", 'ThisItem.R', 0, 0, PRW, 34, size=11, bold=True, indent=I, extra={"Tooltip": F('ThisItem.R & If(IsBlank(ThisItem.Sub), "", "  ·  " & ThisItem.Sub)')}),
      rect("pB", TEAL_D, PRW + 6, 8, f'Max(ThisItem.P * {PBW}, 2)', 18, indent=I),
      label("pN", 'Text(ThisItem.N, "#,##0")', PRW + 12, 0, 90, 34, size=10, bold=True, indent=I, extra={"X": F(f'{PRW} + 12 + ThisItem.P * {PBW}')}),
      label("pC", 'Text(ThisItem.Cum * 100, "0") & "%"', RW2 - 28 - 60, 0, 56, 34, size=10, color=G9, align="Right", indent=I,
            extra={"Color": F(f'If(ThisItem.Cum <= 0.8, {DARK}, {G5})'), "FontWeight": F('If(ThisItem.Cum <= 0.8, FontWeight.Bold, FontWeight.Normal)')})]
out.append(gal("galPar", PITEMS, RX + 14, 238, RW2 - 28, 370, 34, pk, vis=KV, extra={"ShowScrollbar": "=false"}))
out.append(V(label("pE", f'If(varMet = "QUAL_NCR", "NCRs will appear here once the NCR app is live.", CountRows({PITEMS}) = 0, "Nothing logged for " & {PERW} & ".", "")', RX + 14, 270, RW2 - 28, 30, size=11, color=G9), KV))

# ---- Newspaper actions for this metric ----
NEWSF = f'SortByColumns(Filter(colNews, SQDCP.Value = {CAT} && (Status.Value = "Open" || Status.Value = "In progress") && {SCL}), "DueDate", SortOrder.Ascending)'
out.append(V(rect("nBg", WHITE, RX, 622, RW2, 446, extra={"BorderColor": F(G1), "BorderThickness": "=2"}), KV))
out.append(V(label("nT", '"NEWSPAPER · " & Upper(' + CAT + ') & " ACTIONS  (" & CountRows(' + NEWSF + ') & " open, " & CountRows(Filter(' + NEWSF + ', DueDate < Today())) & " overdue)"',
                   RX + 14, 628, RW2 - 330, 30, size=11, bold=True, color=TEAL_D), KV))
out.append(V(btn("nAdd", '"+ ADD ACTION"', 'Set(varAdd, true)', RX + RW2 - 310, 628, 140, 32, size=11, fill=GREEN, color=WHITE), KV))
out.append(V(btn("nOpen", '"NEWSPAPER  ↗"', 'Launch(varNewsLink)', RX + RW2 - 162, 628, 148, 32, size=11, fill=TEAL, color=DARK,
                 extra={"DisplayMode": F('If(IsBlank(varNewsLink), DisplayMode.Disabled, DisplayMode.Edit)'), "Tooltip": '="Opens the Newspaper app (MDI_Config → App_Newspaper)"'}), KV))
nk = [rect("nSt", f'If(ThisItem.DueDate < Today(), {RED}, ThisItem.Status.Value = "In progress", {AMBER}, {G5})', 0, 4, 6, 46, indent=I),
      label("nTi", 'ThisItem.Action', 14, 2, RW2 - 28 - 150, 26, size=12, bold=True, indent=I, extra={"Tooltip": F('Coalesce(ThisItem.Problem, "") & If(IsBlank(ThisItem.Countermeasure), "", Char(10) & "CM: " & ThisItem.Countermeasure)')}),
      label("nSb", 'Coalesce(ThisItem.Line, ThisItem.ValueStream, "plant") & "  ·  " & Coalesce(ThisItem.Owner, "no owner") & "  ·  " & ThisItem.Source.Value', 14, 26, RW2 - 28 - 150, 24, size=10, color=G9, indent=I),
      label("nDu", 'If(IsBlank(ThisItem.DueDate), "no due date", If(ThisItem.DueDate < Today(), "OVERDUE ", "due ") & Text(ThisItem.DueDate, "m/d"))', RW2 - 28 - 140, 2, 136, 26, size=10, bold=True, align="Right", indent=I,
            extra={"Color": F(f'If(ThisItem.DueDate < Today(), {RED}, {DARK})')}),
      label("nSs", 'ThisItem.Status.Value & If(IsBlank(ThisItem.Progress), "", "  " & ThisItem.Progress & "%")', RW2 - 28 - 140, 26, 136, 24, size=10, color=G9, align="Right", indent=I)]
out.append(gal("galNews", NEWSF, RX + 14, 666, RW2 - 28, 396, 54, nk, vis=KV))
out.append(V(label("nE", f'If(CountRows({NEWSF}) = 0, "No open " & Lower({CAT}) & " actions in this scope.", "")', RX + 14, 690, RW2 - 28, 30, size=11, color=G9), KV))

# ---- ADD-ACTION OVERLAY (Source = Tier 3) ----
VA = {"Visible": "=varAdd"}
def vx(d=None): d = dict(d or {}); d.update(VA); return d
out.append(rect("ovDim", "RGBA(7, 39, 45, 0.55)", 0, 0, 1920, 1080, extra=VA))
out.append(rect("ovPanel", WHITE, 560, 170, 800, 700, extra=VA))
out.append(rect("ovHdr", DARK, 560, 170, 800, 60, extra=VA))
out.append(label("ovTitle", '"NEW NEWSPAPER ACTION  ·  TIER 3"', 584, 170, 700, 60, size=18, bold=True, color=AQUA, font="Georgia", extra=VA))
cv = lambda n, t, x, y, w: label(n, f'"{t}"', x, y, w, 20, size=9, bold=True, color=G9, extra=VA)
out.append(cv("ocA", "ACTION (WHAT WILL BE DONE)", 584, 246, 700))
out.append(ti("txtAAction", '""', 584, 268, 752, 48, hint='"e.g. Rebuild filler valve #14"', size=15, extra=vx()))
out.append(cv("ocL", "LINE", 584, 330, 150))
out.append(dd("ddALine", 'Ungroup(Table({t: Table({Value: "(value stream)"})}, {t: ForAll(If(!IsBlank(varLn), Filter(colLines, Title = varLn), colScopeL), {Value: Title})}), t)', 584, 352, 150, 48, size=15,
              extra=vx({"Default": F('If(!IsBlank(varLn), varLn, "(value stream)")')})))
out.append(cv("ocS", "SQDCP", 746, 330, 200))
out.append(dd("ddASQ", '["Safety", "Quality", "Delivery", "Cost", "People"]', 746, 352, 200, 48, size=15, extra=vx({"Default": F(CAT)})))
out.append(cv("ocD", "DUE", 958, 330, 200))
out.append(dd("ddADue", 'ForAll(Sequence(30, 1), With({d: DateAdd(Today(), Value, TimeUnit.Days)}, {Value: Text(d, "ddd m/d"), D: d}))', 958, 352, 200, 48, size=15,
              extra=vx({"Default": F('Text(DateAdd(Today(), 7, TimeUnit.Days), "ddd m/d")')})))
out.append(cv("ocO", "OWNER", 1170, 330, 170))
out.append(ti("txtAOwner", '""', 1170, 352, 166, 48, hint='"name"', size=15, extra=vx()))
out.append(cv("ocP", "PROBLEM (WHAT HAPPENED)", 584, 414, 700))
out.append(ti("txtAProblem", '""', 584, 436, 752, 140, hint='"What happened, where, how much"', size=14, extra=vx({"Mode": "=TextMode.MultiLine"})))
out.append(cv("ocC", "COUNTERMEASURE (OPTIONAL)", 584, 590, 700))
out.append(ti("txtACM", '""', 584, 612, 752, 110, hint='"Containment / root-cause fix"', size=14, extra=vx({"Mode": "=TextMode.MultiLine"})))
SAVEA = ('IfError(Patch(Newspaper, Defaults(Newspaper),\n'
 '  {Action: txtAAction.Text, Line: If(ddALine.Selected.Value = "(value stream)", Blank(), ddALine.Selected.Value),\n'
 '   ValueStream: If(ddALine.Selected.Value = "(value stream)", Coalesce(varVert, varVS), LookUp(colLines, Title = ddALine.Selected.Value).ValueStream),\n'
 '   SQDCP: {Value: ddASQ.Selected.Value}, Source: {Value: "Tier 3"}, Status: {Value: "Open"},\n'
 '   Problem: txtAProblem.Text, Countermeasure: txtACM.Text, Owner: txtAOwner.Text,\n'
 '   RaisedDate: Now(), DueDate: ddADue.Selected.D, RefKey: "T3-" & Text(Now(), "yyyymmddhhmmss")});\n'
 ' Reset(txtAAction); Reset(txtAProblem); Reset(txtACM); Reset(txtAOwner); Set(varAdd, false);\n'
 ' ClearCollect(colNews, Filter(Newspaper, Status.Value = "Open" || Status.Value = "In progress" || ClosedDate >= varD0)),\n'
 ' Notify("Action not saved. Check your connection and try again.", NotificationType.Error), true)')
out.append(btn("btnASave", '"SAVE ACTION"', SAVEA, 1176, 790, 160, 52, size=14, color=WHITE, fill=GREEN,
               extra=vx({"DisplayMode": F('If(IsBlank(txtAAction.Text) || IsBlank(txtAOwner.Text), DisplayMode.Disabled, DisplayMode.Edit)')})))
out.append(btn("btnACancel", '"CANCEL"', 'Set(varAdd, false)', 1004, 790, 160, 52, size=14, color=DARK, fill=G1, extra=vx()))
out.append(label("ocReq", '"Action and owner are required."', 584, 800, 400, 30, size=11, color=G9, extra=VA))

yaml = "".join(out)
write_themed(OUT, yaml)
print("wrote", OUT, len(yaml), "controls", yaml.count("    Control: "))
