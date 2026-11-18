"""Generates Tier2_XB_v1.pa.yaml: Holmdel Tier 2 SQDC built only from what the Tier 1 Excel boards capture.
Paste onto Screen1 of a blank 1920x1080 canvas app that has the flow 'MDI XB - Tier 2 Data' added.
"""
import sys
OUT = sys.argv[1]
FLOW = "'MDIXB-Tier2Data'"
DARK, TEAL, LIGHT, GREY, BG = "RGBA(7, 39, 45, 1)", "RGBA(0, 178, 169, 1)", "RGBA(176, 227, 228, 1)", "RGBA(217, 217, 214, 1)", "RGBA(244, 244, 242, 1)"
G, A, R, N = "RGBA(46, 160, 67, 1)", "RGBA(210, 153, 34, 1)", "RGBA(207, 34, 46, 1)", "RGBA(217, 217, 214, 1)"
MUTED = "RGBA(117, 120, 123, 1)"
def col(st): return f'Switch({st}, "G", {G}, "A", {A}, "R", {R}, {N})'
def fg(st): return f'If({st} = "N", {MUTED}, RGBA(255, 255, 255, 1))'

out = []
def emit(name, ctl, props, children=None, variant=None, ind=0):
    p = " " * ind
    out.append(f"{p}- {name}:")
    out.append(f"{p}    Control: {ctl}")
    if variant: out.append(f"{p}    Variant: {variant}")
    out.append(f"{p}    Properties:")
    for k, v in props.items():
        v = str(v)
        if "\n" in v or ": " in v or " #" in v or v.startswith(("'", '"')) and False:
            out.append(f"{p}      {k}: |-")
            for line in ("=" + v).split("\n"): out.append(f"{p}        {line}")
        else:
            out.append(f"{p}      {k}: ={v}")
    if children:
        out.append(f"{p}    Children:")
        for c in children: emit(*c, ind=ind + 6)

def label(text, x, y, w, h, size=12, color=DARK, bold=False, align="Align.Left", fill=None, vis=None, font="Font.Arial", wrap=None, extra=None):
    d = {"Text": text, "Font": font, "Size": size, "Color": color, "Align": align, "X": x, "Y": y, "Width": w, "Height": h}
    if bold: d["FontWeight"] = "FontWeight.Bold"
    if fill: d["Fill"] = fill
    if vis: d["Visible"] = vis
    if wrap is not None: d["Wrap"] = wrap
    if extra: d.update(extra)
    return d
def rect(x, y, w, h, fill, vis=None, extra=None):
    d = {"Fill": fill, "X": x, "Y": y, "Width": w, "Height": h}
    if vis: d["Visible"] = vis
    if extra: d.update(extra)
    return d
def button(text, onselect, x, y, w, h, fill="RGBA(0, 72, 81, 1)", color="RGBA(255, 255, 255, 1)", vis=None, size=12, extra=None):
    d = {"Text": text, "OnSelect": onselect, "Font": "Font.Arial", "Size": size, "FontWeight": "FontWeight.Bold", "Fill": fill, "Color": color,
         "HoverFill": "ColorFade(Self.Fill, -15%)", "BorderColor": "Self.Fill", "RadiusTopLeft": 6, "RadiusTopRight": 6, "RadiusBottomLeft": 6,
         "RadiusBottomRight": 6, "X": x, "Y": y, "Width": w, "Height": h}
    if vis: d["Visible"] = vis
    if extra: d.update(extra)
    return d

SHIFT_OK = '(ddShift.Selected.Value = "All" || Text(S) = ddShift.Selected.Value)'
DSEL = "ddDate.Selected.D"
def parse_dt(src, ln=None):
    lnpart = f"Ln: {ln}, " if ln else ""
    return (f'ForAll(Filter(Split({src}, "|"), !IsBlank(Value)) As p, {{{lnpart}R: Index(Split(p.Value, "~"), 1).Value, '
            f'M: Value(Index(Split(p.Value, "~"), 2).Value)}})')
def parse_sc(src, ln=None):
    lnpart = f"Ln: {ln}, " if ln else ""
    return f'ForAll(Filter(Split({src}, "|"), !IsBlank(Value)) As p, {{{lnpart}I: Index(Split(p.Value, "~"), 1).Value, Q: Value(Index(Split(p.Value, "~"), 2).Value)}})'

# ---------------- data load ----------------
REFRESH = f'''Set(varBusy, true);
Set(varErr, "");
IfError(Set(varR, {FLOW}.Run("GET", "")), Set(varErr, "Could not reach the flow MDI XB - Tier 2 Data. Is it on and added to this app? " & FirstError.Message));
If(IsBlank(varErr) && varR.ok <> "1", Set(varErr, Coalesce(varR.err, "No data returned.")));
If(IsBlank(varErr),
  Set(varJ, ParseJSON(varR.data));
  ClearCollect(colRows, ForAll(Table(varJ.rows) As x,
    {{K: Text(x.Value.k), L: Text(x.Value.l),
     D: With({{t: Text(x.Value.d)}}, Date(Value(Left(t, 4)), Value(Mid(t, 6, 2)), Value(Mid(t, 9, 2)))),
     S: Value(x.Value.s), WO: Text(x.Value.wo), Lead: Text(x.Value.lead), Prod: Text(x.Value.prod),
     HT: Value(x.Value.ht), Tgt: Value(x.Value.tgt), Act: Value(x.Value.act), H: Text(x.Value.h),
     A: Value(x.Value.a), P: Value(x.Value.p), Q: Value(x.Value.q), OEE: Value(x.Value.oee),
     DT: Value(x.Value.dt), DTR: Text(x.Value.dtr), HDT: Value(x.Value.hdt),
     Scrap: Value(x.Value.scrap), SCR: Text(x.Value.scr), SN: Value(x.Value.sN), SF: Value(x.Value.sF), SR: Value(x.Value.sR),
     CrS: Value(x.Value.crS), CrA: Value(x.Value.crA)}}));
  ClearCollect(colLines, ForAll(Table(varJ.lines) As x, {{Line: Text(x.Value.line), VS: Text(x.Value.vs), N: IfError(Value(Text(x.Value.line)), 999)}}));
  Collect(colLines, ForAll(Filter(Distinct(colRows, L), !(Value in colLines.Line)) As m, {{Line: m.Value, VS: "(not in a line folder)", N: IfError(Value(m.Value), 999)}}));
  ClearCollect(colWarn, Ungroup(ForAll(Table(varJ.warnings) As w, {{W: ForAll(Table(w.Value.items) As i, {{File: Text(w.Value.file), Line: Text(w.Value.line), Msg: Text(i.Value)}})}}), W));
  Set(varS, ParseJSON(If(IsBlank(varR.settings), "{{}}", varR.settings)));
  Set(varOG, Coalesce(Value(varS.oeeGreen), 65)); Set(varOA, Coalesce(Value(varS.oeeAmber), 50));
  Set(varEG, Coalesce(Value(varS.effGreen), 95)); Set(varEA, Coalesce(Value(varS.effAmber), 85));
  Set(varDA, Coalesce(Value(varS.dtAmber), 30)); Set(varDR, Coalesce(Value(varS.dtRed), 60));
  Set(varSA, Coalesce(Value(varS.scrapAmber), 0.5)); Set(varSR, Coalesce(Value(varS.scrapRed), 1));
  Set(varUpd, IfError(DateTimeValue(Text(varJ.lastRun)), Blank()));
  ClearCollect(colDates, ForAll(Sort(Distinct(colRows, D), Value, SortOrder.Descending) As dd, {{Value: Text(dd.Value, "ddd m/d"), D: dd.Value}}));
  Set(varD0, Coalesce(First(Filter(colDates, D < Today())).D, First(colDates).D, Today()));
  Reset(ddDate)
);
If(!IsBlank(varErr), Notify(varErr, NotificationType.Error));
Set(varBusy, false);
Select(btnCalc)'''

def day_eff(i):  # i = 0 (6 days before) .. 6 (selected day)
    return (f'With({{sh{i}: Filter(colRows, L = ln.Line && D = DateAdd({DSEL}, -{6 - i}, TimeUnit.Days) && {SHIFT_OK})}}, '
            f'If(Coalesce(Sum(sh{i}, Tgt), 0) > 0, Coalesce(Sum(sh{i}, Act), 0) / Sum(sh{i}, Tgt) * 100, Blank()))')

CALC = f'''ClearCollect(colFloor, SortByColumns(ForAll(Filter(colLines, ddVS.Selected.Value = "All value streams" || VS = ddVS.Selected.Value) As ln,
 With({{shs: Filter(colRows, L = ln.Line && D = {DSEL} && {SHIFT_OK})}},
 With({{tg: Coalesce(Sum(shs, Tgt), 0), ac: Coalesce(Sum(shs, Act), 0),
        ow: Coalesce(Sum(Filter(shs, !IsBlank(OEE)), Tgt), 0), os: Coalesce(Sum(Filter(shs, !IsBlank(OEE)), OEE * Tgt), 0),
        dtu: Coalesce(Sum(shs, DT), 0), sc: Coalesce(Sum(shs, Scrap), 0),
        sr: Coalesce(Sum(shs, SR), 0), sf: Coalesce(Sum(shs, SF), 0), sn: Coalesce(Sum(shs, SN), 0),
        cs: Coalesce(Sum(shs, CrS), 0), ca: Coalesce(Sum(shs, CrA), 0), n: CountRows(shs),
        dtt: {parse_dt('Concat(shs, DTR, "|")')}}},
  {{Line: ln.Line, N: ln.N, VS: ln.VS, Ran: n > 0, Shifts: n, Tgt: tg, Act: ac,
   Eff: If(tg > 0, ac / tg * 100, Blank()), OEE: If(ow > 0, os / ow * 100, Blank()),
   DTU: dtu, DTs: dtu / Max(n, 1),
   TopR: First(SortByColumns(AddColumns(GroupBy(dtt, R, G), Mn, Sum(G, M)), "Mn", SortOrder.Descending)).R,
   Scrap: sc, ScrapPct: If(ac > 0, sc / ac * 100, Blank()), SR: sr, SF: sf, SN: sn, CrS: cs, CrA: ca,
   StS: If(n = 0, "N", sr > 0, "R", sf > 0, "A", "G"),
   StQ: If(n = 0 || ac = 0, "N", sc / ac * 100 >= varSR, "R", sc / ac * 100 >= varSA, "A", "G"),
   StD: If(tg = 0, "N", ac / tg * 100 >= varEG, "G", ac / tg * 100 >= varEA, "A", "R"),
   StDT: If(n = 0, "N", dtu / Max(n, 1) >= varDR, "R", dtu / Max(n, 1) >= varDA, "A", "G"),
   StO: If(ow = 0, "N", os / ow * 100 >= varOG, "G", os / ow * 100 >= varOA, "A", "R"),
   StP: If(cs = 0 || ca = 0, "N", ca < cs, "R", ca > cs, "A", "G"),
   {", ".join(f"E{i}: {day_eff(i)}" for i in range(7))}}}))), "N", SortOrder.Ascending));
ClearCollect(colParRaw, Ungroup(ForAll(Filter(colRows, L in colFloor.Line && D = {DSEL} && {SHIFT_OK}) As r, {{X: {parse_dt("r.DTR", "r.L")}}}), X));
ClearCollect(colPar, FirstN(SortByColumns(AddColumns(GroupBy(colParRaw, R, G), Mn, Sum(G, M), Lns, Concat(Distinct(G, Ln), Value, ", ")), "Mn", SortOrder.Descending), 10));
ClearCollect(colScrRaw, Ungroup(ForAll(Filter(colRows, L in colFloor.Line && D = {DSEL} && {SHIFT_OK}) As r, {{X: {parse_sc("r.SCR", "r.L")}}}), X));
ClearCollect(colScr, FirstN(SortByColumns(AddColumns(GroupBy(colScrRaw, I, G), Qty, Sum(G, Q), Lns, Concat(Distinct(G, Ln), Value, ", ")), "Qty", SortOrder.Descending), 8));
Set(varTot, {{Tgt: Coalesce(Sum(colFloor, Tgt), 0), Act: Coalesce(Sum(colFloor, Act), 0), DTU: Coalesce(Sum(colFloor, DTU), 0),
  Scrap: Coalesce(Sum(colFloor, Scrap), 0), SR: Coalesce(Sum(colFloor, SR), 0), SF: Coalesce(Sum(colFloor, SF), 0), SN: Coalesce(Sum(colFloor, SN), 0),
  CrS: Coalesce(Sum(colFloor, CrS), 0), CrA: Coalesce(Sum(colFloor, CrA), 0), Ran: CountRows(Filter(colFloor, Ran)), Lines: CountRows(colFloor),
  OEE: If(Coalesce(Sum(Filter(colFloor, !IsBlank(OEE)), Tgt), 0) > 0, Sum(Filter(colFloor, !IsBlank(OEE)), OEE * Tgt) / Sum(Filter(colFloor, !IsBlank(OEE)), Tgt), Blank())}})'''

DETAIL = f'''Set(varLine, ThisItem.Line);
ClearCollect(colDetSh, SortByColumns(Filter(colRows, L = ThisItem.Line && D = {DSEL}), "S", SortOrder.Ascending));
Set(varDS, First(colDetSh));
ClearCollect(colDetDT, SortByColumns(AddColumns(GroupBy({parse_dt('Concat(colDetSh, DTR, "|")')}, R, G), Mn, Sum(G, M)), "Mn", SortOrder.Descending));
ClearCollect(colDetSc, SortByColumns(AddColumns(GroupBy({parse_sc('Concat(colDetSh, SCR, "|")')}, I, G), Qty, Sum(G, Q)), "Qty", SortOrder.Descending));
Set(varDet, true)'''

CFG_FIELDS = [("cfgOG", "OEE GREEN AT OR ABOVE (%)", "varOG"), ("cfgOA", "OEE AMBER AT OR ABOVE (%)", "varOA"),
              ("cfgEG", "EFFICIENCY GREEN AT OR ABOVE (%)", "varEG"), ("cfgEA", "EFFICIENCY AMBER AT OR ABOVE (%)", "varEA"),
              ("cfgDA", "DOWNTIME AMBER AT (MIN / SHIFT)", "varDA"), ("cfgDR", "DOWNTIME RED AT (MIN / SHIFT)", "varDR"),
              ("cfgSA", "SCRAP AMBER AT (% OF UNITS)", "varSA"), ("cfgSR", "SCRAP RED AT (% OF UNITS)", "varSR")]
SAVE = f'''With({{og: Value(cfgOG.Text), oa: Value(cfgOA.Text), eg: Value(cfgEG.Text), ea: Value(cfgEA.Text), da: Value(cfgDA.Text), dr: Value(cfgDR.Text), sa: Value(cfgSA.Text), sr: Value(cfgSR.Text)}},
 If(IsBlank(og) || IsBlank(oa) || IsBlank(eg) || IsBlank(ea) || IsBlank(da) || IsBlank(dr) || IsBlank(sa) || IsBlank(sr) || oa > og || ea > eg || da > dr || sa > sr,
  Notify("Fill in every box. Amber must be at or below green (OEE, efficiency) and at or below red (downtime, scrap).", NotificationType.Warning),
  Set(varSaveErr, "");
  IfError(Set(varSave, {FLOW}.Run("SAVE", JSON({{oeeGreen: og, oeeAmber: oa, effGreen: eg, effAmber: ea, dtAmber: da, dtRed: dr, scrapAmber: sa, scrapRed: sr}}, JSONFormat.Compact))),
    Set(varSaveErr, FirstError.Message));
  If(IsBlank(varSaveErr) && varSave.ok = "1",
   Set(varOG, og); Set(varOA, oa); Set(varEG, eg); Set(varEA, ea); Set(varDA, da); Set(varDR, dr); Set(varSA, sa); Set(varSR, sr);
   Set(varCfg, false); Select(btnCalc); Notify("Targets saved. Every Tier 2 screen picks them up on its next refresh.", NotificationType.Success),
   Notify("Could not save the targets: " & Coalesce(varSaveErr, varSave.err), NotificationType.Error))))'''

# ---------------- header ----------------
emit("hdrBar", "Rectangle@2.3.0", rect(0, 0, 1920, 90, DARK))
emit("lblBrand", "Label@2.5.1", label('"voyant"', 24, 6, 170, 52, 34, "RGBA(255, 255, 255, 1)", font="Font.Georgia"))
emit("lblBrandSub", "Label@2.5.1", label('"HOLMDEL"', 27, 56, 170, 24, 10, TEAL, bold=True))
emit("lblTitle", "Label@2.5.1", label('"TIER 2 · SQDC"', 190, 20, 260, 50, 24, "RGBA(255, 255, 255, 1)", bold=True, font="Font.Georgia", wrap="false"))
for nm, txt, x, w in (("cVS", '"VALUE STREAM"', 460, 260), ("cDate", '"DATE"', 730, 180), ("cShift", '"SHIFT"', 920, 110)):
    emit(nm, "Label@2.5.1", label(txt, x, 6, w, 20, 9, "RGBA(177, 179, 179, 1)", bold=True))
emit("ddVS", "Classic/DropDown@2.3.1", {"Items": 'Ungroup(Table({t: Table({Value: "All value streams"})}, {t: Sort(Distinct(colLines, VS), Value)}), t)',
     "OnChange": "Select(btnCalc)", "Font": "Font.Arial", "Size": 15, "FontWeight": "FontWeight.Bold", "X": 460, "Y": 28, "Width": 260, "Height": 52})
emit("ddDate", "Classic/DropDown@2.3.1", {"Items": "colDates", "Default": 'Text(varD0, "ddd m/d")', "OnChange": "Select(btnCalc)",
     "Font": "Font.Arial", "Size": 15, "FontWeight": "FontWeight.Bold", "X": 730, "Y": 28, "Width": 180, "Height": 52})
emit("ddShift", "Classic/DropDown@2.3.1", {"Items": '["All", "1", "2"]', "OnChange": "Select(btnCalc)", "Font": "Font.Arial", "Size": 16,
     "FontWeight": "FontWeight.Bold", "X": 920, "Y": 28, "Width": 110, "Height": 52})
emit("btnRefresh", "Classic/Button@2.2.0", button('If(varBusy, "LOADING…", "REFRESH")', REFRESH, 1044, 28, 140, 52,
     extra={"DisplayMode": "If(varBusy, DisplayMode.Disabled, DisplayMode.Edit)", "Tooltip": '"Reload what the sync flow has read from the Tier 1 boards."'}))
emit("btnCfg", "Classic/Button@2.2.0", button('"⚙ TARGETS"', "Set(varCfg, true); " + "; ".join(f"Reset({c})" for c, _, _ in CFG_FIELDS), 1196, 28, 130, 52,
     extra={"Tooltip": '"OEE, efficiency, downtime and scrap color levels."'}))
emit("btnWarn", "Classic/Button@2.2.0", button('"⚠ " & CountRows(colWarn) & " BOARD NOTES"', "Set(varWarn, true)", 1338, 28, 190, 52,
     fill=A, vis="CountRows(colWarn) > 0", extra={"Tooltip": '"Things the sync noticed on the boards: blank line numbers, targets typed as shift totals, hourly vs shift downtime that disagree."'}))
emit("lblUpd", "Label@2.5.1", label('If(IsBlank(varUpd), "No data yet", "Boards read " & Text(varUpd, "ddd h:mm AM/PM")) & Char(10) & varTot.Ran & " of " & varTot.Lines & " lines ran"',
     1540, 10, 364, 70, 12, LIGHT, bold=True, align="Align.Right"))
# hidden calc button
emit("btnCalc", "Classic/Button@2.2.0", button('""', CALC, 0, 0, 1, 1, extra={"Visible": "false"}))

# ---------------- floor grid ----------------
emit("bgMain", "Rectangle@2.3.0", rect(0, 90, 1920, 990, BG))
COLS = [("hLine", '"LINE"', 16, 120), ("hS", '"SAFETY"', 140, 120), ("hQ", '"QUALITY · SCRAP"', 266, 170), ("hD", '"DELIVERY · UNITS VS TARGET"', 442, 240),
        ("hDT", '"DOWNTIME"', 688, 230), ("hO", '"OEE"', 924, 100), ("hP", '"PEOPLE · CREW"', 1030, 130), ("h7", '"EFFICIENCY · LAST 7 DAYS"', 1166, 280)]
for nm, txt, x, w in COLS:
    emit(nm, "Label@2.5.1", label(txt, x, 98, w, 30, 10, MUTED, bold=True))
ROWH = "Max(34, Min(64, 820 / Max(1, CountRows(colFloor))))"
def cell(nm, x, w, st, text, sub=None):
    kids = [(nm, "Label@2.5.1", label(text, x, 3, w, f"Self.Parent.TemplateHeight - 6", 15, fg(st), bold=True, align="Align.Center", fill=col(st),
                                         extra={"RadiusTopLeft": 4, "RadiusTopRight": 4, "RadiusBottomLeft": 4, "RadiusBottomRight": 4}))]
    return kids
kids = []
kids.append(("gLineBg", "Rectangle@2.3.0", rect(0, 3, 120, "Self.Parent.TemplateHeight - 6", "If(ThisItem.Ran, " + DARK + ", " + GREY + ")")))
kids.append(("gLine", "Label@2.5.1", label("ThisItem.Line", 0, 3, 120, "Self.Parent.TemplateHeight - 6", 20, "If(ThisItem.Ran, RGBA(255, 255, 255, 1), " + MUTED + ")", bold=True, align="Align.Center")))
kids += cell("gS", 124, 120, "ThisItem.StS", 'If(!ThisItem.Ran, "–", ThisItem.SR > 0, "REC " & ThisItem.SR, ThisItem.SF > 0, "FA " & ThisItem.SF, ThisItem.SN > 0, "OK · NM " & ThisItem.SN, "OK")')
kids += cell("gQ", 250, 170, "ThisItem.StQ", 'If(!ThisItem.Ran, "–", Text(ThisItem.Scrap, "#,##0") & "  ·  " & Text(Coalesce(ThisItem.ScrapPct, 0), "0.0") & "%")')
kids += cell("gD", 426, 240, "ThisItem.StD", 'If(ThisItem.Tgt = 0, If(ThisItem.Ran, "no target", "–"), Text(ThisItem.Act, "#,##0") & " / " & Text(ThisItem.Tgt, "#,##0") & "  ·  " & Text(ThisItem.Eff, "0") & "%")')
kids += cell("gDT", 672, 230, "ThisItem.StDT", 'If(!ThisItem.Ran, "–", Text(ThisItem.DTU, "#,##0") & " min" & If(IsBlank(ThisItem.TopR), "", "  ·  " & ThisItem.TopR))')
kids += cell("gO", 908, 100, "ThisItem.StO", 'If(IsBlank(ThisItem.OEE), "–", Text(ThisItem.OEE, "0") & "%")')
kids += cell("gP", 1014, 130, "ThisItem.StP", 'If(ThisItem.CrS = 0 || ThisItem.CrA = 0, "–", ThisItem.CrA & " / " & ThisItem.CrS)')
for i in range(7):
    st = f'If(IsBlank(ThisItem.E{i}), "N", ThisItem.E{i} >= varEG, "G", ThisItem.E{i} >= varEA, "A", "R")'
    kids.append((f"gE{i}", "Label@2.5.1", label(f'If(IsBlank(ThisItem.E{i}), "", Text(ThisItem.E{i}, "0"))', 1150 + i * 40, 3, 36, "Self.Parent.TemplateHeight - 6", 10,
        fg(st), bold=True, align="Align.Center", fill=col(st), extra={"Tooltip": f'Text(DateAdd({DSEL}, -{6 - i}, TimeUnit.Days), "ddd m/d") & ": efficiency " & If(IsBlank(ThisItem.E{i}), "no data", Text(ThisItem.E{i}, "0") & "%")'})))
kids.append(("gHit", "Classic/Button@2.2.0", button('""', DETAIL, 0, 0, 1430, "Self.Parent.TemplateHeight", fill="RGBA(0, 0, 0, 0)",
             extra={"HoverFill": "RGBA(0, 178, 169, 0.12)", "PressedFill": "RGBA(0, 178, 169, 0.2)", "Tooltip": '"Open line " & ThisItem.Line'})))
emit("galFloor", "Gallery@2.15.0", {"Items": "colFloor", "TemplateSize": ROWH, "TemplatePadding": 0, "ShowScrollbar": "true", "BorderThickness": 0,
     "TemplateFill": "RGBA(0, 0, 0, 0)", "X": 16, "Y": 130, "Width": 1440, "Height": 830}, children=kids, variant="BrowseLayout_Vertical_TwoTextOneImageVariant_ver5.0")
# plant total row
emit("totBar", "Rectangle@2.3.0", rect(16, 968, 1440, 96, DARK))
emit("totTitle", "Label@2.5.1", label('"PLANT"', 16, 968, 120, 96, 18, "RGBA(255, 255, 255, 1)", bold=True, align="Align.Center"))
emit("totS", "Label@2.5.1", label('"Recordable " & varTot.SR & Char(10) & "First aid " & varTot.SF & Char(10) & "Near miss " & varTot.SN', 140, 972, 120, 88, 11, "RGBA(255, 255, 255, 1)", bold=True))
emit("totQ", "Label@2.5.1", label('Text(varTot.Scrap, "#,##0") & " scrap" & Char(10) & If(varTot.Act > 0, Text(varTot.Scrap / varTot.Act * 100, "0.00") & "% of units", "")', 266, 972, 170, 88, 13, "RGBA(255, 255, 255, 1)", bold=True))
emit("totD", "Label@2.5.1", label('Text(varTot.Act, "#,##0") & " / " & Text(varTot.Tgt, "#,##0") & Char(10) & If(varTot.Tgt > 0, Text(varTot.Act / varTot.Tgt * 100, "0") & "% efficiency", "")', 442, 972, 240, 88, 15, "RGBA(255, 255, 255, 1)", bold=True))
emit("totDT", "Label@2.5.1", label('Text(varTot.DTU, "#,##0") & " min downtime" & Char(10) & "across " & varTot.Ran & " lines"', 688, 972, 230, 88, 13, "RGBA(255, 255, 255, 1)", bold=True))
emit("totO", "Label@2.5.1", label('If(IsBlank(varTot.OEE), "–", Text(varTot.OEE, "0") & "%")', 924, 972, 100, 88, 18, "RGBA(255, 255, 255, 1)", bold=True, align="Align.Center"))
emit("totP", "Label@2.5.1", label('If(varTot.CrS = 0, "–", varTot.CrA & " / " & varTot.CrS)', 1030, 972, 130, 88, 16, "RGBA(255, 255, 255, 1)", bold=True, align="Align.Center"))
emit("totNote", "Label@2.5.1", label('"Tap a line for its shifts, hour by hour and downtime."', 1166, 972, 280, 88, 11, LIGHT))
emit("lblEmpty", "Label@2.5.1", label('If(varBusy, "Loading…", "No lines to show. Press REFRESH, or run MDI XB - Sync Excel Boards if this is the first time.")',
     16, 400, 1440, 80, 16, MUTED, bold=True, align="Align.Center", vis="CountRows(colFloor) = 0"))

# ---------------- right column: plant Pareto + scrap ----------------
emit("rpBg", "Rectangle@2.3.0", rect(1472, 98, 432, 966, "RGBA(255, 255, 255, 1)"))
emit("rpDTT", "Label@2.5.1", label('"DOWNTIME · TOP REASONS"', 1488, 106, 400, 30, 12, DARK, bold=True))
emit("rpDTS", "Label@2.5.1", label('Text(Coalesce(Sum(colPar, Mn), 0), "#,##0") & " min on the boards"', 1488, 134, 400, 22, 10, MUTED))
pk = [("pR", "Label@2.5.1", label("ThisItem.R", 0, 2, 400, 22, 12, DARK, bold=True)),
      ("pBarBg", "Rectangle@2.3.0", rect(0, 26, 300, 16, "RGBA(236, 236, 234, 1)")),
      ("pBar", "Rectangle@2.3.0", rect(0, 26, "300 * ThisItem.Mn / Max(1, Max(colPar, Mn))", 16, R)),
      ("pMin", "Label@2.5.1", label('Text(ThisItem.Mn, "#,##0") & " min"', 306, 22, 94, 24, 11, DARK, bold=True, align="Align.Right")),
      ("pLns", "Label@2.5.1", label('"Lines " & ThisItem.Lns', 0, 42, 400, 18, 9, MUTED))]
emit("galPar", "Gallery@2.15.0", {"Items": "colPar", "TemplateSize": 62, "TemplatePadding": 0, "ShowScrollbar": "true", "BorderThickness": 0,
     "X": 1488, "Y": 160, "Width": 400, "Height": 560}, children=pk, variant="BrowseLayout_Vertical_TwoTextOneImageVariant_ver5.0")
emit("rpScT", "Label@2.5.1", label('"SCRAP · TOP COMPONENTS"', 1488, 730, 400, 30, 12, DARK, bold=True))
sk = [("sI", "Label@2.5.1", label("ThisItem.I", 0, 2, 220, 34, 12, DARK, bold=True)),
      ("sBar", "Rectangle@2.3.0", rect(224, 12, "110 * ThisItem.Qty / Max(1, Max(colScr, Qty))", 14, A)),
      ("sQ", "Label@2.5.1", label('Text(ThisItem.Qty, "#,##0")', 336, 2, 64, 34, 12, DARK, bold=True, align="Align.Right"))]
emit("galScr", "Gallery@2.15.0", {"Items": "colScr", "TemplateSize": 36, "TemplatePadding": 0, "ShowScrollbar": "true", "BorderThickness": 0,
     "X": 1488, "Y": 762, "Width": 400, "Height": 296}, children=sk, variant="BrowseLayout_Vertical_TwoTextOneImageVariant_ver5.0")

# ---------------- line detail overlay ----------------
V = "varDet"
emit("dDim", "Rectangle@2.3.0", rect(0, 0, 1920, 1080, "RGBA(7, 39, 45, 0.55)", vis=V, extra={"OnSelect": "Set(varDet, false)"}))
emit("dPanel", "Rectangle@2.3.0", rect(80, 70, 1760, 960, "RGBA(255, 255, 255, 1)", vis=V))
emit("dHdr", "Rectangle@2.3.0", rect(80, 70, 1760, 64, DARK, vis=V))
emit("dTitle", "Label@2.5.1", label('"LINE " & varLine & "  ·  " & Text(' + DSEL + ', "dddd m/d") & "  ·  from the Tier 1 board"', 104, 70, 1400, 64, 20, "RGBA(255, 255, 255, 1)", bold=True, vis=V))
emit("dClose", "Classic/Button@2.2.0", button('"CLOSE"', "Set(varDet, false)", 1700, 80, 120, 44, fill=TEAL, vis=V))
emit("dShT", "Label@2.5.1", label('"SHIFTS  ·  tap one for its hours"', 104, 146, 800, 26, 11, MUTED, bold=True, vis=V))
shk = [("shBg", "Rectangle@2.3.0", rect(0, 4, 800, 132, "If(ThisItem.K = varDS.K, RGBA(176, 227, 228, 0.45), RGBA(244, 244, 242, 1))")),
       ("shT", "Label@2.5.1", label('"SHIFT " & ThisItem.S & "   " & Coalesce(ThisItem.Prod, "") & If(IsBlank(ThisItem.WO), "", "  ·  " & ThisItem.WO) & If(IsBlank(ThisItem.Lead), "", "  ·  " & ThisItem.Lead)', 16, 8, 770, 28, 13, DARK, bold=True)),
       ("shD", "Label@2.5.1", label('"Units " & Text(ThisItem.Act, "#,##0") & " / " & Text(ThisItem.Tgt, "#,##0") & If(ThisItem.Tgt > 0, "  (" & Text(ThisItem.Act / ThisItem.Tgt * 100, "0") & "%)", "") & "     Downtime " & ThisItem.DT & " min     Scrap " & ThisItem.Scrap', 16, 40, 770, 28, 12, DARK)),
       ("shO", "Label@2.5.1", label('If(IsBlank(ThisItem.OEE), "OEE –  (actual and standard speed not on the board)", "OEE " & Text(ThisItem.OEE * 100, "0") & "%   ·   A " & Text(ThisItem.A * 100, "0") & "  P " & Text(ThisItem.P * 100, "0") & "  Q " & Text(ThisItem.Q * 100, "0"))', 16, 70, 770, 28, 12, DARK)),
       ("shP", "Label@2.5.1", label('"Crew " & If(IsBlank(ThisItem.CrA), "–", ThisItem.CrA) & " / " & If(IsBlank(ThisItem.CrS), "–", ThisItem.CrS) & "     Safety: " & If(ThisItem.SR + ThisItem.SF + ThisItem.SN = 0, "none", "recordable " & ThisItem.SR & ", first aid " & ThisItem.SF & ", near miss " & ThisItem.SN) & If(ThisItem.HDT = 1, "     downtime logged by the hour", "")', 16, 100, 770, 28, 11, MUTED)),
       ("shHit", "Classic/Button@2.2.0", button('""', "Set(varDS, ThisItem)", 0, 0, 800, 136, fill="RGBA(0, 0, 0, 0)", extra={"HoverFill": "RGBA(0, 178, 169, 0.12)"}))]
emit("galDetSh", "Gallery@2.15.0", {"Items": "colDetSh", "TemplateSize": 140, "TemplatePadding": 0, "ShowScrollbar": "false", "BorderThickness": 0,
     "Visible": V, "X": 104, "Y": 174, "Width": 800, "Height": 286}, children=shk, variant="BrowseLayout_Vertical_TwoTextOneImageVariant_ver5.0")
emit("dHrT", "Label@2.5.1", label('"HOUR BY HOUR  ·  shift " & varDS.S & "  ·  target " & Text(varDS.HT, "#,##0") & " / hr"', 104, 470, 800, 26, 11, MUTED, bold=True, vis=V))
HR_ITEMS = 'ForAll(Sequence(8) As i, {Hr: i.Value, U: IfError(Value(Index(Split(Coalesce(varDS.H, ",,,,,,,"), ","), i.Value).Value), Blank()), T: Coalesce(varDS.HT, 0)})'
SC = "Max(varDS.HT * 1.3, Max(" + HR_ITEMS + ", U), 1)"
hk = [("hrN", "Label@2.5.1", label('"HOUR " & ThisItem.Hr', 0, 4, 90, 44, 11, DARK, bold=True)),
      ("hrBg", "Rectangle@2.3.0", rect(96, 12, 560, 28, "RGBA(236, 236, 234, 1)")),
      ("hrBar", "Rectangle@2.3.0", rect(96, 12, f"If(IsBlank(ThisItem.U), 0, 560 * Min(ThisItem.U / {SC}, 1))", 28,
          f'If(IsBlank(ThisItem.U) || ThisItem.T = 0, {GREY}, ThisItem.U >= ThisItem.T, {G}, ThisItem.U >= ThisItem.T * 0.85, {A}, {R})')),
      ("hrTgt", "Rectangle@2.3.0", rect(f"96 + 560 * Min(ThisItem.T / {SC}, 1) - 1", 6, 3, 40, DARK, vis="ThisItem.T > 0")),
      ("hrV", "Label@2.5.1", label('If(IsBlank(ThisItem.U), "not entered", Text(ThisItem.U, "#,##0") & If(ThisItem.T > 0, "  ·  " & Text(ThisItem.U / ThisItem.T * 100, "0") & "%", ""))', 664, 4, 136, 44, 11, DARK, bold=True, align="Align.Right"))]
emit("galHr", "Gallery@2.15.0", {"Items": HR_ITEMS, "TemplateSize": 52, "TemplatePadding": 0, "ShowScrollbar": "false", "BorderThickness": 0,
     "Visible": V, "X": 104, "Y": 500, "Width": 800, "Height": 420}, children=hk, variant="BrowseLayout_Vertical_TwoTextOneImageVariant_ver5.0")
emit("dHrNote", "Label@2.5.1", label('"Dark tick = hourly target. Green at or above target, amber within 15%, red below."', 104, 924, 800, 26, 10, MUTED, vis=V))
emit("dDTT", "Label@2.5.1", label('"DOWNTIME BY REASON  ·  " & Coalesce(Sum(colDetDT, Mn), 0) & " min"', 940, 146, 860, 26, 11, MUTED, bold=True, vis=V))
dk = [("ddR", "Label@2.5.1", label('ThisItem.R', 0, 2, 300, 34, 12, DARK, bold=True)),
      ("ddBg", "Rectangle@2.3.0", rect(304, 12, 440, 16, "RGBA(236, 236, 234, 1)")),
      ("ddBar", "Rectangle@2.3.0", rect(304, 12, "440 * ThisItem.Mn / Max(1, Max(colDetDT, Mn))", 16, R)),
      ("ddM", "Label@2.5.1", label('ThisItem.Mn & " min"', 750, 2, 100, 34, 12, DARK, bold=True, align="Align.Right"))]
emit("galDetDT", "Gallery@2.15.0", {"Items": "colDetDT", "TemplateSize": 38, "TemplatePadding": 0, "ShowScrollbar": "true", "BorderThickness": 0,
     "Visible": V, "X": 940, "Y": 174, "Width": 860, "Height": 420}, children=dk, variant="BrowseLayout_Vertical_TwoTextOneImageVariant_ver5.0")
emit("dScT", "Label@2.5.1", label('"SCRAP BY COMPONENT  ·  " & Coalesce(Sum(colDetSc, Qty), 0)', 940, 610, 860, 26, 11, MUTED, bold=True, vis=V))
ck = [("dsI", "Label@2.5.1", label("ThisItem.I", 0, 2, 300, 34, 12, DARK, bold=True)),
      ("dsBar", "Rectangle@2.3.0", rect(304, 12, "440 * ThisItem.Qty / Max(1, Max(colDetSc, Qty))", 16, A)),
      ("dsQ", "Label@2.5.1", label("ThisItem.Qty", 750, 2, 100, 34, 12, DARK, bold=True, align="Align.Right"))]
emit("galDetSc", "Gallery@2.15.0", {"Items": "colDetSc", "TemplateSize": 38, "TemplatePadding": 0, "ShowScrollbar": "true", "BorderThickness": 0,
     "Visible": V, "X": 940, "Y": 638, "Width": 860, "Height": 280}, children=ck, variant="BrowseLayout_Vertical_TwoTextOneImageVariant_ver5.0")
emit("dNoData", "Label@2.5.1", label('"Nothing entered on this board for the selected day."', 104, 400, 1700, 60, 16, MUTED, bold=True, align="Align.Center",
     vis="varDet && CountRows(colDetSh) = 0"))

# ---------------- board notes overlay ----------------
W = "varWarn"
emit("wDim", "Rectangle@2.3.0", rect(0, 0, 1920, 1080, "RGBA(7, 39, 45, 0.55)", vis=W, extra={"OnSelect": "Set(varWarn, false)"}))
emit("wPanel", "Rectangle@2.3.0", rect(260, 120, 1400, 840, "RGBA(255, 255, 255, 1)", vis=W))
emit("wHdr", "Rectangle@2.3.0", rect(260, 120, 1400, 64, A, vis=W))
emit("wTitle", "Label@2.5.1", label('"BOARD NOTES  ·  fix these on the Tier 1 board; the next sync picks it up"', 284, 120, 1200, 64, 16, "RGBA(255, 255, 255, 1)", bold=True, vis=W))
emit("wClose", "Classic/Button@2.2.0", button('"CLOSE"', "Set(varWarn, false)", 1520, 130, 120, 44, fill=DARK, vis=W))
wk = [("wL", "Label@2.5.1", label('"Line " & ThisItem.Line', 0, 2, 120, 40, 12, DARK, bold=True)),
      ("wM", "Label@2.5.1", label("ThisItem.Msg", 124, 2, 900, 40, 11, DARK)),
      ("wF", "Label@2.5.1", label("ThisItem.File", 1030, 2, 320, 40, 9, MUTED))]
emit("galWarn", "Gallery@2.15.0", {"Items": "colWarn", "TemplateSize": 44, "TemplatePadding": 0, "ShowScrollbar": "true", "BorderThickness": 0,
     "Visible": W, "X": 284, "Y": 196, "Width": 1352, "Height": 740}, children=wk, variant="BrowseLayout_Vertical_TwoTextOneImageVariant_ver5.0")

# ---------------- targets overlay ----------------
C = "varCfg"
emit("cDim", "Rectangle@2.3.0", rect(0, 0, 1920, 1080, "RGBA(7, 39, 45, 0.55)", vis=C))
emit("cPanel", "Rectangle@2.3.0", rect(560, 150, 800, 700, "RGBA(255, 255, 255, 1)", vis=C))
emit("cHdr", "Rectangle@2.3.0", rect(560, 150, 800, 64, DARK, vis=C))
emit("cTitle", "Label@2.5.1", label('"TARGETS  ·  TIER 2 COLORS"', 584, 150, 700, 64, 16, "RGBA(255, 255, 255, 1)", bold=True, vis=C))
for i, (nm, cap, var) in enumerate(CFG_FIELDS):
    x = 584 + (i % 2) * 380; y = 236 + (i // 2) * 120
    emit(nm + "L", "Label@2.5.1", label(f'"{cap}"', x, y, 360, 22, 9, MUTED, bold=True, vis=C))
    emit(nm, "Classic/TextInput@2.3.2", {"Default": f"Text({var})", "Format": "TextFormat.Number", "Font": "Font.Arial", "Size": 16,
         "BorderColor": "RGBA(177, 179, 179, 1)", "Visible": C, "X": x, "Y": y + 24, "Width": 360, "Height": 52})
emit("cNote", "Label@2.5.1", label('"Saved next to the boards (Production / _Tier2 / tier2_settings.json), so every Tier 2 screen uses the same levels."', 584, 720, 752, 44, 10, MUTED, vis=C))
emit("cCancel", "Classic/Button@2.2.0", button('"CANCEL"', "Set(varCfg, false)", 1004, 776, 160, 52, fill="RGBA(217, 217, 214, 1)", color=DARK, vis=C))
emit("cSave", "Classic/Button@2.2.0", button('"SAVE TARGETS"', SAVE, 1176, 776, 160, 52, fill=G, vis=C))

open(OUT, "w", encoding="utf-8").write("\n".join(out) + "\n")
print("controls:", sum(1 for l in out if l.strip().startswith("- ")), "lines:", len(out))
