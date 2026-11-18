# Quality app (was QA Rework): Screen1 = REWORK (QA rework entry + dashboard), scrNCR = NCR log (ISO 9001:2015 8.7 + 10.2)
# usage: python3 quality.py OUT_REWORK OUT_NCR
import sys
OUTR, OUTN = sys.argv[1], sys.argv[2]
src = open(__import__("os").environ["MDI_GEN"]+"/qa.py").read()
TABS_CODE = r'''
QTABS = [("REWORK", "Screen1"), ("NCR LOG", "scrNCR")]
def qtabs(pfx, cur):
    r = []
    for i, (n, scr) in enumerate(QTABS):
        on = scr == cur
        r.append(btn(f"{pfx}Tab{i}", f'"{n}"', f'Navigate({scr}, ScreenTransition.None)', 640 + i * 168, 24, 160, 44, size=13,
                     fill=(TEAL if on else TEAL_D), color=(DARK if on else WHITE), extra=RAD))
    return r
out.extend(qtabs("q", "Screen1"))
'''
src = src.replace("\n'''\nfor _ in range(2):", TABS_CODE + "'''\nfor _ in range(2):")
src = src.replace('write_themed(__import__("os").environ["MDI_OUTDIR"]+"/QA_Rework_v4.pa.yaml", "".join(out))', 'write_themed(OUTR, "".join(out))')
assert 'write_themed(OUTR' in src and 'QTABS' in src
exec(src)

# ================================ NCR SCREEN ================================
out.clear(); EXTRA.clear()
exec(BODY.split("# ---------- LEFT")[0].split("# ---------- header")[0])   # tip() + RAD
exec(TABS_CODE.split("out.extend")[0])
FLOW = "'MDI-UploadPhoto'"
for n, t in {"nBtnNew": "Raise a new nonconformance report.", "nTxtFind": "Search NCR #, job, lot, product, defect, customer or supplier.", "n1Src": "Where the nonconformity was found.", "n1Line": "Line that made the product.", "n1Date": "Date the product was made.",
             "n1Job": "Job number (traceability).", "n1Lot": "Lot, batch or code date (traceability).", "n1Qty": "REQUIRED. How much is affected.",
             "n1Desc": "REQUIRED. The requirement, what was found, and how it was found."}.items():
    tip(n, t)
RED_ = "RGBA(207, 34, 46, 1)"; PURP = "RGBA(130, 80, 223, 1)"; BLUE = "RGBA(9, 105, 218, 1)"; AMB = "RGBA(191, 135, 0, 1)"
YEL = "RGBA(255, 242, 179, 1)"; YELB = "RGBA(210, 153, 34, 1)"
STCOL = lambda s: f'Switch({s}, "Open", {RED_}, "Contained", {AMB}, "Dispositioned", {PURP}, "CA in progress", {BLUE}, "Closed", {GREEN}, {G9})'
SEVCOL = lambda s: f'Switch({s}, "Critical", RGBA(130, 7, 30, 1), "Major", {RED_}, {AMB})'
RANK = lambda s: f'Switch({s}, "Open", 1, "Contained", 2, "Dispositioned", 3, "CA in progress", 4, "Closed", 5, 6)'
def adv(stage):
    """status after saving a stage: only moves forward"""
    return f'{{Value: If({RANK("varNc.Status.Value")} < {RANK(chr(34) + stage + chr(34))}, "{stage}", varNc.Status.Value)}}'
HAS = '(varNcNew || !IsBlank(varNc))'
LOCK = '(!varNcNew && !IsBlank(varNc) && (varNc.Status.Value = "Closed" || varNc.Status.Value = "Void"))'
DM = {"DisplayMode": F(f'If({LOCK}, DisplayMode.View, DisplayMode.Edit)')}
def vis(k): return f'{HAS} && varNcStep = {k}'
def VX(k, more=None, lock=True):
    d = {"Visible": F(vis(k))}
    if lock: d.update(DM)
    if more: d.update(more)
    return d
def vrect(name, fill, x, y, w, h, visible=None, extra=None):
    d = {"Fill": F(fill)}
    if visible: d["Visible"] = F(visible)
    if extra: d.update(extra)
    d.update(box(x, y, w, h)); return ctrl(name, "Rectangle@2.3.0", d)
def ML(more=None):
    d = {"Mode": "=TextMode.MultiLine", "Align": "=Align.Left"}
    if more: d.update(more)
    return d
YN = '["No", "Yes"]'
def ynd(b): return f'If(varNcNew || IsBlank(varNc), "No", If(varNc.{b}, "Yes", "No"))'

# ---------- header ----------
out.append(rect("nHdrBar", DARK, 0, 0, 1920, 90))
out.append(label("nBrand", '"voyant"', 24, 6, 170, 52, size=34, color=WHITE, font="Georgia"))
out.append(label("nBrandSub", '"NEW ALBANY"', 27, 56, 170, 24, size=10, bold=True, color=TEAL))
out.append(label("nTitle", '"QUALITY  ·  NCR"', 190, 20, 420, 50, size=24, bold=True, color=WHITE, font="Georgia"))
out.extend(qtabs("n", "scrNCR"))
out.append(label("nUser", '"Logged in: " & User().FullName', 1500, 20, 400, 50, size=12, color=G5, align="Right"))

# ---------- loader (hidden) ----------
LOAD = ('Set(varNc0, DateAdd(Today(), -365, TimeUnit.Days));\n'
        'IfError(ClearCollect(colNcr, Filter(NCR, RaisedAt >= varNc0)), Notify("Could not load NCR: " & FirstError.Message, NotificationType.Error), true);\n'
        'IfError(ClearCollect(colNcDef, Sort(Filter(Lookups, Category.Value = "NCR defect" && Active = true), SortOrder)), Notify("Could not load NCR defects from Lookups", NotificationType.Warning), true);\n'
        'Set(varNcDue, Coalesce(Value(LookUp(MDI_Config, Title = "NCR_DueDays").SettingValue), 30));\n'
        'Set(varNcNewsLink, LookUp(MDI_Config, Title = "App_Newspaper").SettingValue);\n'
        'If(!IsBlank(varNc), Set(varNc, LookUp(colNcr, ID = varNc.ID)));\n'
        'If(IsBlank(varNcStep), Set(varNcStep, 1));\n'
        'Set(varNcLoaded, Now())')
HELP = {"Color": F(CLEAR), "BorderColor": F(CLEAR), "HoverFill": F(CLEAR), "PressedFill": F(CLEAR), "TabIndex": "=-1"}
out.append(btn("nLoad", '""', LOAD, 0, 1079, 1, 1, fill=CLEAR, color=CLEAR, extra=HELP))
# refresh the linked photos + newspaper actions for the selected NCR
SIDE = ('If(IsBlank(varNc), Clear(colNcPh); Clear(colNcNews),\n'
        ' ClearCollect(colNcPh, Filter(TS_Photos, RefID = varNc.ID && Module.Value = "NCR"));\n'
        ' ClearCollect(colNcNews, Filter(Newspaper, RefKey = varNc.Title)))')
out.append(btn("nSide", '""', SIDE, 1, 1079, 1, 1, fill=CLEAR, color=CLEAR, extra=HELP))

# ================= LEFT: NCR log =================
LX = 12; LW = 640
out.append(rect("nListBg", PANEL, LX, 98, LW, 974))
out.append(label("nListT", '"NCR LOG"', LX + 16, 104, 300, 34, size=16, bold=True, color=DARK, font="Georgia"))
NEWNC = ('Set(varNc, Blank()); Set(varNcNew, true); Set(varNcStep, 1); Clear(colNcPh); Clear(colNcNews); Select(nReset)')
out.append(btn("nBtnNew", '"+  NEW NCR"', NEWNC, LX + LW - 196, 102, 180, 44, fill=RED_, color=WHITE, size=14, extra=RAD))
for i, (k, t) in enumerate([("open", "OPEN"), ("all", "ALL"), ("closed", "CLOSED")]):
    out.append(btn(f"nF{i}", f'"{t}"', f'Set(varNcF, "{k}")', LX + 16 + i * 108, 152, 102, 38, size=11,
                   fill=f'If(Coalesce(varNcF, "open") = "{k}", {TEAL_D}, {WHITE})', color=f'If(Coalesce(varNcF, "open") = "{k}", {WHITE}, {DARK})',
                   extra={"BorderColor": F(G5), "BorderThickness": "=1", **RAD}))
out.append(dd("nDdFLine", 'Ungroup(Table({t: Table({Value: "All lines"})}, {t: Distinct(PLAYBOOK, Line)}), t)', LX + 346, 152, 130, 38, default='"All lines"', size=12))
out.append(ti("nTxtFind", '""', LX + 484, 152, LW - 500, 38, 'false', hint='"search"', size=12, number=False, extra={"Align": "=Align.Left"}))
FILT = ('SortByColumns(Filter(colNcr,\n'
        '  Switch(Coalesce(varNcF, "open"), "open", !(Status.Value in ["Closed", "Void"]), "closed", Status.Value = "Closed", true),\n'
        '  nDdFLine.Selected.Value = "All lines" || Line = nDdFLine.Selected.Value,\n'
        '  IsBlank(nTxtFind.Text) || nTxtFind.Text in (Title & " " & Job & " " & Lot & " " & ProductForm & " " & DefectCategory & " " & Party & " " & Owner)),\n'
        ' "RaisedAt", SortOrder.Descending)')
OPEN = 'Filter(colNcr, !(Status.Value in ["Closed", "Void"]))'
def kpi(name, capt, val, x, w, col):
    out.append(label(name, val, x, 198, w, 60, size=24, bold=True, color=col, fill=WHITE, align="Center", valign="Bottom", pb=4))
    out.append(label(name + "C", f'"{capt}"', x, 200, w, 18, size=8, bold=True, color=G9, align="Center"))
KW = (LW - 32 - 24) // 4
kpi("nkOpen", "OPEN", f'Text(CountRows({OPEN}))', LX + 16, KW, DARK)
kpi("nkOver", "OVERDUE", f'Text(CountRows(Filter({OPEN}, !IsBlank(DueDate) && DueDate < Today())))', LX + 16 + (KW + 8), KW, RED_)
kpi("nkCrit", "CRITICAL / MAJOR OPEN", f'Text(CountRows(Filter({OPEN}, Severity.Value in ["Critical", "Major"])))', LX + 16 + 2 * (KW + 8), KW, RED_)
kpi("nkM", "RAISED THIS MONTH", 'Text(CountRows(Filter(colNcr, RaisedAt >= Date(Year(Today()), Month(Today()), 1) && Status.Value <> "Void")))', LX + 16 + 3 * (KW + 8), KW, DARK)
gk = [ctrl("gNcSel", "Rectangle@2.3.0", {"Fill": F(f'If(!IsBlank(varNc) && varNc.ID = ThisItem.ID, {AQUA}, {WHITE})'), **box(0, 0, LW - 20, 90)}, 6),
      ctrl("gNcBar", "Rectangle@2.3.0", {"Fill": F(STCOL("ThisItem.Status.Value")), **box(0, 0, 6, 90)}, 6),
      label("gNcNo", 'Coalesce(ThisItem.Title, "NCR #" & ThisItem.ID)', 14, 4, 200, 30, size=14, bold=True, color=DARK, indent=6),
      label("gNcSt", 'ThisItem.Status.Value', 214, 8, 130, 24, size=10, bold=True, color=WHITE, align="Center", indent=6,
            extra={"Fill": F(STCOL("ThisItem.Status.Value"))}),
      label("gNcSev", 'Upper(ThisItem.Severity.Value)', 352, 8, 90, 24, size=10, bold=True, color=WHITE, align="Center", indent=6,
            extra={"Fill": F(SEVCOL("ThisItem.Severity.Value"))}),
      label("gNcAge", 'If(ThisItem.Status.Value in ["Closed", "Void"], "closed " & Text(ThisItem.ClosedAt, "m/d"),\n'
            ' !IsBlank(ThisItem.DueDate) && ThisItem.DueDate < Today(), "OVERDUE " & DateDiff(ThisItem.DueDate, Today()) & "d",\n'
            ' DateDiff(ThisItem.RaisedAt, Now(), TimeUnit.Days) & "d open")', 446, 4, LW - 20 - 456, 30, size=11, bold=True, align="Right", indent=6,
            extra={"Color": F(f'If(!(ThisItem.Status.Value in ["Closed", "Void"]) && !IsBlank(ThisItem.DueDate) && ThisItem.DueDate < Today(), {RED_}, {G9})')}),
      label("gNcWhat", 'If(Coalesce(ThisItem.NCType.Value, "Product") <> "Product", Upper(ThisItem.NCType.Value) & If(IsBlank(ThisItem.Clause), "", "  ·  ISO " & ThisItem.Clause) & If(IsBlank(ThisItem.AuditRef), "", "  ·  " & ThisItem.AuditRef) & "  ·  ", "") & Coalesce(ThisItem.DefectCategory, "—") & If(Coalesce(ThisItem.QtyAffected, 0) > 0, "  ·  " & Text(ThisItem.QtyAffected, "#,##0") & " " & ThisItem.Unit.Value, "") & "  ·  " & ThisItem.Source.Value',
            14, 34, LW - 40, 26, size=12, color=DARK, indent=6, extra={"Wrap": "=false"}),
      label("gNcWhere", '"Line " & ThisItem.Line & If(IsBlank(ThisItem.ProductForm), "", "  ·  " & ThisItem.ProductForm) & If(IsBlank(ThisItem.Job), "", "  ·  job " & ThisItem.Job) & If(IsBlank(ThisItem.Lot), "", "  ·  lot " & ThisItem.Lot) & "  ·  " & Coalesce(ThisItem.Owner, "no owner")',
            14, 60, LW - 40, 24, size=10, color=G9, indent=6, extra={"Wrap": "=false"}),
      btn("gNcTap", '""', 'Set(varNcNew, false); Set(varNc, ThisItem); Set(varNcStep, Switch(ThisItem.Status.Value, "Open", 2, "Contained", 3, "Dispositioned", 4, "CA in progress", 5, 5)); Select(nReset); Select(nSide)',
          0, 0, LW - 20, 90, fill=CLEAR, color=CLEAR, indent=6, extra={"HoverFill": F("RGBA(0, 178, 169, 0.08)"), "PressedFill": F("RGBA(0, 178, 169, 0.15)"), "BorderColor": F(CLEAR)})]
gp = {"Items": F(FILT), "TemplateSize": "=96", "TemplatePadding": "=0", "ShowScrollbar": "=true"}
gp.update(box(LX + 8, 268, LW - 16, 798))
out.append(ctrl("galNcr", "Gallery@2.15.0", gp, 0, gk, variant="BrowseLayout_Vertical_TwoTextOneImageVariant_ver5.0"))
out.append(label("nListE", 'If(IsBlank(varNcLoaded), "Loading…", "No NCRs match.")', LX + 16, 290, LW - 32, 40, size=12, color=G5,
                 extra={"Visible": F(f'CountRows({FILT}) = 0')}))

# ================= RIGHT: NCR record =================
RX = 664; RW = 1244
out.append(rect("nRecBg", WHITE, RX, 98, RW, 974))
out.append(label("nEmpty", '"Select an NCR on the left, or press + NEW NCR."' , RX, 480, RW, 60, size=18, color=G5, align="Center",
                 extra={"Visible": F(f'!{HAS}')}))
out.append(label("nRecNo", 'If(varNcNew, "NEW NCR", Coalesce(varNc.Title, "NCR #" & varNc.ID))', RX + 16, 104, 330, 40, size=22, bold=True, color=DARK, font="Georgia",
                 extra={"Visible": F(HAS)}))
out.append(label("nRecSt", 'If(varNcNew, "not saved yet", varNc.Status.Value)', RX + 350, 110, 160, 30, size=12, bold=True, color=WHITE, align="Center",
                 extra={"Visible": F(HAS), "Fill": F(f'If(varNcNew, {G9}, {STCOL("varNc.Status.Value")})')}))
STAMP = ('If(varNcNew || IsBlank(varNc), "Every stage you save is stamped with your name and the time (ISO 9001 8.7.2 / 10.2.2 evidence).",\n'
         ' "Raised " & Text(varNc.RaisedAt, "m/d h:mm AM/PM") & " by " & varNc.RaisedBy &\n'
         ' If(IsBlank(varNc.ContainedAt), "", "   ·   contained " & Text(varNc.ContainedAt, "m/d") & " by " & varNc.ContainedBy) &\n'
         ' If(IsBlank(varNc.DispositionAt), "", "   ·   disposition " & Text(varNc.DispositionAt, "m/d") & " by " & varNc.DispositionBy) &\n'
         ' If(IsBlank(varNc.CAAt), "", "   ·   CA " & Text(varNc.CAAt, "m/d") & " by " & varNc.CABy) &\n'
         ' If(IsBlank(varNc.ClosedAt), "", "   ·   closed " & Text(varNc.ClosedAt, "m/d") & " by " & varNc.ClosedBy))')
out.append(label("nStamp", STAMP, RX + 520, 100, RW - 536, 48, size=9, color=G9, extra={"Visible": F(HAS)}))
STAGES = [("1  IDENTIFY", "true"), ("2  CONTAIN", "!IsBlank(varNc.ContainedAt)"), ("3  DISPOSITION", "!IsBlank(varNc.DispositionAt)"),
          ("4  CORRECTIVE ACTION", "(!IsBlank(varNc.CAAt) || !varNc.CARequired)"), ("5  VERIFY & CLOSE", 'varNc.Status.Value = "Closed"')]
SW_ = (RW - 32 - 4 * 6) // 5
STIPS = ["What, where, how many. Traceability: line, date, product, job, lot (ISO 8.5.2 / 8.7.2a).",
         "Stop it going further: hold, segregate, tag, sort (ISO 8.7.1b).",
         "Decide what happens to the product, who authorized it, concessions, and re-verify after rework (ISO 8.7.1, 8.7.2).",
         "Why did it happen, could it happen elsewhere, and what will we change (ISO 10.2.1b-c).",
         "Did the fix work? Update risks and the QMS, then close (ISO 10.2.1d-f)."]
for i, (t, done) in enumerate(STAGES):
    k = i + 1
    dn = f'(!varNcNew && !IsBlank(varNc) && {done})'
    out.append(btn(f"nStg{k}", f'If({dn}, "✓  ", "") & "{t}"', f'If(varNcNew && {k} > 1, Notify("Save the NCR first (stage 1).", NotificationType.Warning), Set(varNcStep, {k}))',
                   RX + 16 + i * (SW_ + 6), 152, SW_, 44, size=12,
                   fill=f'If(varNcStep = {k}, {TEAL}, {dn}, {GREEN}, {G1})', color=f'If(varNcStep = {k}, {DARK}, {dn}, {WHITE}, {DARK})',
                   extra={"Visible": F(HAS), "Tooltip": F('"' + STIPS[i] + '"'), **RAD}))
out.append(label("nStgHelp", 'Switch(varNcStep, ' + ", ".join(f'{i + 1}, "{s}"' for i, s in enumerate(STIPS)) + ')', RX + 16, 198, RW - 32, 24, size=10, color=G9,
                 extra={"Visible": F(HAS)}))
C0 = RX + 16
def cv(name, text, x, y, w, k): return label(name, f'"{text}"', x, y, w, 20, size=9, bold=True, color=G9, extra={"Visible": F(vis(k))})
def req(empty):
    return {"Fill": F(f'If({empty}, {YEL}, {WHITE})'), "BorderColor": F(f'If({empty}, {YELB}, {G5})')}

# ---------- stage 1: IDENTIFY ----------
Y = 230
out.append(cv("n1cSrc", "FOUND AT", C0, Y, 230, 1))
out.append(dd("n1Src", '["In-process", "Final inspection", "Customer complaint", "Supplier / incoming", "Audit"]', C0, Y + 22, 230, 48,
              default='If(varNcNew || IsBlank(varNc), "In-process", varNc.Source.Value)', size=14, extra=VX(1)))
out.append(cv("n1cSev", "SEVERITY", C0 + 240, Y, 150, 1))
out.append(dd("n1Sev", '["Minor", "Major", "Critical"]', C0 + 240, Y + 22, 150, 48, default='If(varNcNew || IsBlank(varNc), "Minor", varNc.Severity.Value)', size=14,
              extra=VX(1, {"Tooltip": '="Minor: no customer/safety impact. Major: product would reach customer or big quantity. Critical: safety, regulatory or customer-reported."'})))
out.append(cv("n1cLine", "LINE", C0 + 400, Y, 120, 1))
out.append(dd("n1Line", 'Distinct(PLAYBOOK, Line)', C0 + 400, Y + 22, 120, 48, default='If(varNcNew || IsBlank(varNc), "209", varNc.Line)', size=16, bold=True, extra=VX(1)))
out.append(cv("n1cDate", "PRODUCTION DATE", C0 + 530, Y, 180, 1))
out.append(dd("n1Date", 'ForAll(Sequence(60, 0, -1), With({d: DateAdd(Today(), Value, TimeUnit.Days)}, {Value: Text(d, "ddd m/d/yy"), D: d}))', C0 + 530, Y + 22, 180, 48,
              default='If(varNcNew || IsBlank(varNc) || IsBlank(varNc.ShiftDate), Text(Today(), "ddd m/d/yy"), Text(varNc.ShiftDate, "ddd m/d/yy"))', size=14, extra=VX(1)))
out.append(cv("n1cSh", "SHIFT", C0 + 720, Y, 90, 1))
out.append(dd("n1Shift", '["1", "2", "3"]', C0 + 720, Y + 22, 90, 48, default='If(varNcNew || IsBlank(varNc), "1", Text(varNc.Shift))', size=16, extra=VX(1)))
out.append(cv("n1cOwn", "NCR OWNER", C0 + 820, Y, RW - 32 - 820, 1))
out.append(ti("n1Own", 'If(varNcNew || IsBlank(varNc), User().FullName, varNc.Owner)', C0 + 820, Y + 22, RW - 32 - 820, 48, 'false', hint='"who drives it to closure"', size=14, number=False,
              extra=VX(1, {"Align": "=Align.Left", **req("IsBlank(Self.Text)")})))
Y = 316
PROD = ('Ungroup(Table({t: Table({Value: "(not product-specific)", Size: "", Form: ""})},\n'
        ' {t: ForAll(Filter(PLAYBOOK, Line = n1Line.Selected.Value), {Value: Size & " | " & Form, Size: Size, Form: Form})}), t)')
out.append(cv("n1cProd", "PRODUCT  (SIZE | FORM)", C0, Y, 420, 1))
out.append(dd("n1Prod", PROD, C0, Y + 22, 420, 48, default='If(varNcNew || IsBlank(varNc) || IsBlank(varNc.Size), "(not product-specific)", varNc.Size & " | " & varNc.Form)', size=14, extra=VX(1)))
out.append(cv("n1cJob", "JOB #", C0 + 430, Y, 160, 1))
out.append(ti("n1Job", 'If(varNcNew || IsBlank(varNc), "", varNc.Job)', C0 + 430, Y + 22, 160, 48, 'false', hint='"job"', size=14, number=False, extra=VX(1)))
out.append(cv("n1cLot", "LOT / BATCH / CODE DATE", C0 + 600, Y, 220, 1))
out.append(ti("n1Lot", 'If(varNcNew || IsBlank(varNc), "", varNc.Lot)', C0 + 600, Y + 22, 220, 48, 'false', hint='"lot or code date"', size=14, number=False, extra=VX(1)))
out.append(cv("n1cParty", "CUSTOMER / SUPPLIER  (IF ANY)", C0 + 830, Y, RW - 32 - 830, 1))
out.append(ti("n1Party", 'If(varNcNew || IsBlank(varNc), "", varNc.Party)', C0 + 830, Y + 22, RW - 32 - 830, 48, 'false', hint='"customer or supplier name"', size=14, number=False,
              extra=VX(1, {"Align": "=Align.Left"})))
Y = 402
out.append(cv("n1cDef", "DEFECT", C0, Y, 330, 1))
out.append(dd("n1Def", 'Ungroup(Table({t: Table({Value: "(pick a defect)"})}, {t: ForAll(colNcDef, {Value: Title})}), t)', C0, Y + 22, 330, 48,
              default='If(varNcNew || IsBlank(varNc) || IsBlank(varNc.DefectCategory), "(pick a defect)", varNc.DefectCategory)', size=14,
              extra=VX(1, {"Fill": F(f'If(Self.Selected.Value = "(pick a defect)" && n1Type.Selected.Value = "Product", {YEL}, {WHITE})'),
                           "Tooltip": '="Defect list = Lookups, Category NCR defect. Add or retire them there."'})))
out.append(cv("n1cQty", "QTY AFFECTED", C0 + 340, Y, 150, 1))
out.append(ti("n1Qty", 'If(varNcNew || IsBlank(varNc), "", Text(varNc.QtyAffected))', C0 + 340, Y + 22, 150, 48, 'false', hint='"0"', size=18, bold=True,
              extra=VX(1, req('n1Type.Selected.Value = "Product" && Coalesce(Value(Self.Text), 0) <= 0'))))
out.append(cv("n1cUnit", "UNIT", C0 + 500, Y, 130, 1))
out.append(dd("n1Unit", '["units", "cases", "pallets", "lbs", "kg", "gallons"]', C0 + 500, Y + 22, 130, 48, default='If(varNcNew || IsBlank(varNc), "units", varNc.Unit.Value)', size=14, extra=VX(1)))
out.append(cv("n1cDue", "CLOSE BY  (M/D/YYYY)", C0 + 640, Y, 180, 1))
out.append(cv("n1cType", "TYPE", C0 + 830, Y, RW - 32 - 830, 1))
out.append(dd("n1Type", '["Product", "QMS finding", "Customer complaint", "Supplier"]', C0 + 830, Y + 22, RW - 32 - 830, 48,
              default='If(varNcNew || IsBlank(varNc) || IsBlank(varNc.NCType.Value), "Product", varNc.NCType.Value)', size=14,
              extra=VX(1, {"Tooltip": '="QMS finding = a system nonconformity (internal audit, T-card pull). Product fields (defect, qty) are optional for it."'})))
out.append(ti("n1Due", f'If(varNcNew || IsBlank(varNc) || IsBlank(varNc.DueDate), Text(DateAdd(Today(), Coalesce(varNcDue, 30), TimeUnit.Days), "m/d/yyyy"), Text(varNc.DueDate, "m/d/yyyy"))',
              C0 + 640, Y + 22, 180, 48, 'false', size=14, number=False,
              extra=VX(1, {"Fill": F(f'If(IsError(DateValue(Self.Text)) || IsBlank(Self.Text), {YEL}, {WHITE})'),
                           "Tooltip": '="Target date to close. Default comes from MDI_Config NCR_DueDays."'})))
Y = 488
out.append(cv("n1cDesc", "WHAT IS WRONG  (REQUIREMENT vs WHAT WE FOUND, HOW IT WAS FOUND)", C0, Y, 820, 1))
out.append(ti("n1Desc", 'If(varNcNew || IsBlank(varNc), "", varNc.Description)', C0, Y + 22, 820, 230, 'false', hint='"Spec says … we found … found by …"', size=14, number=False,
              extra=VX(1, ML(req("IsBlank(Self.Text)")))))
PX = C0 + 830; PW = RW - 32 - 830
out.append(cv("n1cPh", "PHOTO  (OPTIONAL, ADDS ON SAVE)", PX, Y, PW, 1))
out.append(ctrl("n1Img", "Image@2.2.3", {"Image": F('If(IsBlank(n1AddPh.Media), SampleImage, n1AddPh.Media)'), "ImagePosition": "=ImagePosition.Fit",
                                          "Visible": F(vis(1)), "Fill": F(MUTE), **box(PX, Y + 22, PW, 230)}))
out.append(ctrl("n1AddPh", "AddMedia@2.2.1", {"Text": '=If(IsBlank(Self.Media), "📷  TAP TO ADD PHOTO", "")', "Size": "=13", "Fill": "=RGBA(0, 0, 0, 0)", "Color": F(TEAL_D),
                                              "BorderColor": F(G5), "BorderThickness": "=1", "Visible": F(vis(1)), **DM, **box(PX, Y + 22, PW, 230)}))
Y = 750
out.append(cv("n1cPhs", "PHOTOS ON THIS NCR", C0, Y, 400, 1))
pk = [ctrl("gNcPh", "Image@2.2.3", {"Image": F("ThisItem.Thumbnail.Large"), "ImagePosition": "=ImagePosition.Fill", **box(2, 2, 196, 132)}, 6)]
gpp = {"Items": F("colNcPh"), "WrapCount": "=6", "TemplateSize": "=140", "TemplatePadding": "=0", "Visible": F(vis(1))}
gpp.update(box(C0, Y + 22, RW - 32, 140))
out.append(ctrl("galNcPh", "Gallery@2.15.0", gpp, 0, pk, variant="BrowseLayout_Vertical_TwoTextOneImageVariant_ver5.0"))
out.append(label("n1NoPh", '"No photos yet."', C0, Y + 30, 400, 30, size=11, color=G5, extra={"Visible": F(vis(1) + ' && CountRows(colNcPh) = 0')}))
OK1 = ('!IsBlank(n1Own.Text) && (!(n1Type.Selected.Value = "Product") || (n1Def.Selected.Value <> "(pick a defect)" && Coalesce(Value(n1Qty.Text), 0) > 0)) && !IsBlank(n1Desc.Text) && !IsError(DateValue(n1Due.Text))')
REC1 = ('{NCType: {Value: n1Type.Selected.Value}, Source: {Value: n1Src.Selected.Value}, Severity: {Value: n1Sev.Selected.Value}, Line: n1Line.Selected.Value,\n'
        '   ValueStream: LookUp(Lines, Title = n1Line.Selected.Value).ValueStream, ShiftDate: n1Date.Selected.D, Shift: Value(n1Shift.Selected.Value),\n'
        '   Size: n1Prod.Selected.Size, Form: n1Prod.Selected.Form, ProductForm: If(n1Prod.Selected.Size = "", Blank(), n1Prod.Selected.Size & " " & n1Prod.Selected.Form),\n'
        '   Job: n1Job.Text, Lot: n1Lot.Text, Party: n1Party.Text, DefectCategory: If(n1Def.Selected.Value = "(pick a defect)", varNc.DefectCategory, n1Def.Selected.Value), Description: n1Desc.Text,\n'
        '   QtyAffected: Value(n1Qty.Text), Unit: {Value: n1Unit.Selected.Value}, Owner: n1Own.Text, DueDate: DateValue(n1Due.Text)}')
SAVE1 = ('IfError(\n'
         ' If(varNcNew,\n'
         '  Set(varNc, Patch(NCR, Defaults(NCR), ' + REC1 + ', {Status: {Value: "Open"}, RaisedBy: User().FullName, RaisedAt: Now(), CARequired: n1Sev.Selected.Value <> "Minor", Effective: {Value: "Pending"}}));\n'
         '  Set(varNc, Patch(NCR, varNc, {Title: "NCR-" & Text(Year(Today())) & "-" & Text(varNc.ID, "0000")})); Set(varNcNew, false),\n'
         '  Set(varNc, Patch(NCR, LookUp(NCR, ID = varNc.ID), ' + REC1 + ')));\n'
         ' If(!IsBlank(n1AddPh.Media), Patch(TS_Photos, LookUp(TS_Photos, ID = Value(' + FLOW + '.Run({contentBytes: n1AddPh.Media, name: "ncr.jpg"}, varNc.Title & ".jpg", 0, 0, 0, "Finding", n1Desc.Text, User().Email).photoid)),\n'
         '   {Module: {Value: "NCR"}, RefID: varNc.ID})),\n'
         ' Notify("NOT SAVED: " & FirstError.Message, NotificationType.Error),\n'
         ' Notify(varNc.Title & " saved. Next: contain it.", NotificationType.Success); Reset(n1AddPh); Select(nLoad); Select(nSide); If(varNcStep = 1 && IsBlank(varNc.ContainedAt), Set(varNcStep, 2)))')
out.append(btn("n1Save", f'If({OK1}, If(varNcNew, "RAISE NCR", "SAVE CHANGES"), "FILL THE YELLOW FIELDS")', SAVE1, RX + RW - 16 - 320, 990, 320, 64, size=16,
               fill=f'If({OK1}, {RED_}, {G1})', color=f'If({OK1}, {WHITE}, {G9})',
               extra=VX(1, {"DisplayMode": F(f'If({LOCK}, DisplayMode.Disabled, {OK1}, DisplayMode.Edit, DisplayMode.Disabled)'), "DisabledFill": F(G1), "DisabledColor": F(G9), **RAD})))

# ---------- stage 2: CONTAIN ----------
Y = 236
out.append(cv("n2cAct", "CONTAINMENT  (WHAT DID WE DO TO STOP IT GOING FURTHER?  HOLD, TAG, SEGREGATE, SORT, STOP LINE, PULL FROM WAREHOUSE)", C0, Y, RW - 32, 2))
out.append(ti("n2Act", 'If(IsBlank(varNc), "", varNc.Containment)', C0, Y + 22, RW - 32, 200, 'false', hint='"e.g. 14 pallets on QA hold in cage B, line purged, first-off check before restart"', size=14, number=False,
              extra=VX(2, ML(req("IsBlank(Self.Text)")))))
Y = 470
out.append(cv("n2cQty", "QTY ON HOLD", C0, Y, 200, 2))
out.append(ti("n2Qty", 'If(IsBlank(varNc), "", Text(varNc.QtyOnHold))', C0, Y + 22, 200, 52, 'false', hint='"0"', size=20, bold=True, extra=VX(2)))
out.append(label("n2Unit", 'varNc.Unit.Value', C0 + 206, Y + 22, 100, 52, size=13, color=G9, extra={"Visible": F(vis(2))}))
out.append(cv("n2cLoc", "WHERE IS IT HELD?", C0 + 320, Y, 500, 2))
out.append(ti("n2Loc", 'If(IsBlank(varNc), "", varNc.HoldLocation)', C0 + 320, Y + 22, 500, 52, 'false', hint='"QA cage, warehouse aisle, customer site"', size=14, number=False,
              extra=VX(2, {"Align": "=Align.Left"})))
out.append(label("n2Note", '"Tag every held unit or pallet with the NCR number so it can\'t be used by mistake (ISO 8.7.1). If nothing could be held (already shipped), say so above and inform the customer at disposition."',
                 C0, Y + 90, RW - 32, 50, size=11, color=G9, extra={"Visible": F(vis(2))}))
SAVE2 = ('IfError(Set(varNc, Patch(NCR, LookUp(NCR, ID = varNc.ID), {Containment: n2Act.Text, QtyOnHold: Value(n2Qty.Text), HoldLocation: n2Loc.Text,\n'
         '   ContainedBy: If(IsBlank(varNc.ContainedAt), User().FullName, varNc.ContainedBy), ContainedAt: Coalesce(varNc.ContainedAt, Now()), Status: ' + adv("Contained") + '})),\n'
         ' Notify("NOT SAVED: " & FirstError.Message, NotificationType.Error),\n'
         ' Notify("Containment saved.", NotificationType.Success); Select(nLoad); Set(varNcStep, 3))')
out.append(btn("n2Save", '"SAVE CONTAINMENT"', SAVE2, RX + RW - 16 - 320, 990, 320, 64, size=16, fill=AMB, color=WHITE,
               extra=VX(2, {"DisplayMode": F(f'If({LOCK} || IsBlank(n2Act.Text), DisplayMode.Disabled, DisplayMode.Edit)'), "DisabledFill": F(G1), "DisabledColor": F(G9), **RAD})))

# ---------- stage 3: DISPOSITION ----------
Y = 236
REWK = '(n3Disp.Selected.Value in ["Rework", "Repair", "Regrade"])'
out.append(cv("n3cDisp", "DISPOSITION", C0, Y, 300, 3))
out.append(dd("n3Disp", '["(choose)", "Use as is", "Rework", "Repair", "Regrade", "Scrap", "Return to supplier", "Not product (QMS finding)"]', C0, Y + 22, 300, 52,
              default='If(IsBlank(varNc) || IsBlank(varNc.Disposition.Value), "(choose)", varNc.Disposition.Value)', size=16, bold=True,
              extra=VX(3, {"Fill": F(f'If(Self.Selected.Value = "(choose)", {YEL}, {WHITE})'),
                           "Tooltip": '="Use as is needs a concession. Rework / repair / regrade must be re-verified before release (ISO 8.7.1)."'})))
out.append(cv("n3cQty", "QTY", C0 + 310, Y, 160, 3))
out.append(ti("n3Qty", 'If(IsBlank(varNc), "", Text(Coalesce(varNc.DispQty, varNc.QtyAffected)))', C0 + 310, Y + 22, 160, 52, 'false', size=18, bold=True, extra=VX(3)))
out.append(cv("n3cInf", "CUSTOMER INFORMED?", C0 + 480, Y, 190, 3))
out.append(dd("n3Inf", YN, C0 + 480, Y + 22, 190, 52, default=ynd("CustomerInformed"), size=16,
              extra=VX(3, {"Tooltip": '="Yes if the customer was told (required when product reached them or for a concession, ISO 8.7.1c)."'})))
out.append(cv("n3cCon", "CONCESSION / DEVIATION  (REF + WHO APPROVED)", C0 + 680, Y, RW - 32 - 680, 3))
out.append(ti("n3Con", 'If(IsBlank(varNc), "", varNc.Concession)', C0 + 680, Y + 22, RW - 32 - 680, 52, 'false', hint='"needed for Use as is"', size=14, number=False,
              extra=VX(3, {"Align": "=Align.Left", **req('n3Disp.Selected.Value = "Use as is" && IsBlank(Self.Text)')})))
Y = 330
out.append(cv("n3cNotes", "DISPOSITION DETAIL  (WHAT EXACTLY HAPPENS TO THE PRODUCT, BY WHEN)", C0, Y, RW - 32, 3))
out.append(ti("n3Notes", 'If(IsBlank(varNc), "", varNc.DispNotes)', C0, Y + 22, RW - 32, 140, 'false', hint='"e.g. rework on line 209 2nd shift: relabel 640 cases, QA to check 100%"', size=14, number=False,
              extra=VX(3, ML())))
out.append(label("n3Auth", 'If(IsBlank(varNc.DispositionAt), "Authorized by: " & User().FullName & " (you), stamped when you save.", "Authorized by " & varNc.DispositionBy & " on " & Text(varNc.DispositionAt, "m/d/yyyy h:mm AM/PM"))',
                 C0, Y + 170, RW - 32, 30, size=12, bold=True, color=DARK, extra={"Visible": F(vis(3))}))
Y = 560
out.append(vrect("n3RvBg", MUTE, C0, Y, RW - 32, 330, visible=vis(3) + f' && {REWK}'))
out.append(label("n3RvT", '"RE-VERIFY AFTER CORRECTION  (ISO 8.7.1)  ·  product that was reworked, repaired or regraded must be checked again before it ships"',
                 C0 + 12, Y + 8, RW - 56, 30, size=11, bold=True, color=PURP, extra={"Visible": F(vis(3) + f' && {REWK}')}))
out.append(cv("n3cRv", "RE-VERIFIED OK?", C0 + 12, Y + 46, 200, 3).replace(f'Visible: ={vis(3)}', f'Visible: ={vis(3)} && {REWK}'))
out.append(dd("n3Rv", YN, C0 + 12, Y + 68, 200, 52, default=ynd("Reverified"), size=16, extra=VX(3, {"Visible": F(vis(3) + f' && {REWK}')})))
out.append(cv("n3cRvN", "HOW IT WAS CHECKED / RESULT", C0 + 222, Y + 46, 600, 3).replace(f'Visible: ={vis(3)}', f'Visible: ={vis(3)} && {REWK}'))
out.append(ti("n3RvN", 'If(IsBlank(varNc), "", varNc.ReverifyNotes)', C0 + 222, Y + 68, RW - 32 - 234, 140, 'false', hint='"100% sort by QA, 0 defects found in 640 cases"', size=14, number=False,
              extra=VX(3, ML({"Visible": F(vis(3) + f' && {REWK}')}))))
out.append(label("n3RvBy", 'If(IsBlank(varNc.ReverifiedAt), "", "Re-verified by " & varNc.ReverifiedBy & " on " & Text(varNc.ReverifiedAt, "m/d h:mm AM/PM"))',
                 C0 + 12, Y + 220, 600, 30, size=11, color=G9, extra={"Visible": F(vis(3) + f' && {REWK}')}))
OK3 = f'n3Disp.Selected.Value <> "(choose)" && (n3Disp.Selected.Value <> "Use as is" || !IsBlank(n3Con.Text))'
SAVE3 = ('IfError(Set(varNc, Patch(NCR, LookUp(NCR, ID = varNc.ID), {Disposition: {Value: n3Disp.Selected.Value}, DispQty: Value(n3Qty.Text), DispNotes: n3Notes.Text,\n'
         '   CustomerInformed: n3Inf.Selected.Value = "Yes", Concession: n3Con.Text,\n'
         '   DispositionBy: If(IsBlank(varNc.DispositionAt), User().FullName, varNc.DispositionBy), DispositionAt: Coalesce(varNc.DispositionAt, Now()),\n'
         '   Reverified: ' + REWK + ' && n3Rv.Selected.Value = "Yes", ReverifyNotes: n3RvN.Text,\n'
         '   ReverifiedBy: If(' + REWK + ' && n3Rv.Selected.Value = "Yes", Coalesce(varNc.ReverifiedBy, User().FullName), Blank()),\n'
         '   ReverifiedAt: If(' + REWK + ' && n3Rv.Selected.Value = "Yes", Coalesce(varNc.ReverifiedAt, Now()), Blank()),\n'
         '   Status: ' + adv("Dispositioned") + '})),\n'
         ' Notify("NOT SAVED: " & FirstError.Message, NotificationType.Error),\n'
         ' Notify("Disposition saved.", NotificationType.Success); Select(nLoad); If(!' + REWK + ' || n3Rv.Selected.Value = "Yes", Set(varNcStep, 4)))')
out.append(btn("n3Save", f'If({OK3}, "SAVE DISPOSITION", "CHOOSE A DISPOSITION")', SAVE3, RX + RW - 16 - 320, 990, 320, 64, size=16, fill=PURP, color=WHITE,
               extra=VX(3, {"DisplayMode": F(f'If({LOCK}, DisplayMode.Disabled, {OK3}, DisplayMode.Edit, DisplayMode.Disabled)'), "DisabledFill": F(G1), "DisabledColor": F(G9), **RAD})))

# ---------- stage 4: CORRECTIVE ACTION ----------
Y = 236
out.append(cv("n4cReq", "CORRECTIVE ACTION NEEDED?", C0, Y, 240, 4))
out.append(dd("n4Req", YN, C0, Y + 22, 240, 52, default='If(IsBlank(varNc), "Yes", If(varNc.CARequired, "Yes", "No"))', size=16,
              extra=VX(4, {"Tooltip": '="No only when it is a one-off with a known cause that is already gone. Say why in the root cause box."'})))
out.append(label("n4ReqN", '"Raised automatically for Major and Critical NCRs. ISO 10.2.1b: evaluate the need for action to eliminate the cause so it does not recur or occur elsewhere."',
                 C0 + 260, Y + 22, RW - 32 - 260, 52, size=11, color=G9, extra={"Visible": F(vis(4))}))
Y = 320
out.append(cv("n4cRc", "ROOT CAUSE  (WHY DID IT HAPPEN?  ASK WHY UNTIL YOU REACH SOMETHING YOU CAN FIX)", C0, Y, RW - 32, 4))
out.append(ti("n4Rc", 'If(IsBlank(varNc), "", varNc.RootCause)', C0, Y + 22, 610, 220, 'false', hint='"Why 1 … Why 2 … root cause"', size=14, number=False,
              extra=VX(4, ML(req('n4Req.Selected.Value = "Yes" && IsBlank(Self.Text)')))))
out.append(cv("n4cSim", "COULD IT HAPPEN ELSEWHERE?  (OTHER LINES, PRODUCTS, SHIFTS)", C0 + 620, Y, RW - 32 - 620, 4))
out.append(ti("n4Sim", 'If(IsBlank(varNc), "", varNc.SimilarCheck)', C0 + 620, Y + 22, RW - 32 - 620, 220, 'false', hint='"checked lines 204 and 211: same capper, same risk"', size=14, number=False,
              extra=VX(4, ML())))
Y = 580
out.append(label("n4ActT", '"ACTIONS  (tracked in the Newspaper, Source = NCR)  ·  " & CountRows(colNcNews) & " linked"', C0, Y, 700, 30, size=12, bold=True, color=DARK,
                 extra={"Visible": F(vis(4))}))
NEWSA = ('IfError(Patch(Newspaper, Defaults(Newspaper), {Action: "Corrective action " & varNc.Title & ": " & Coalesce(varNc.DefectCategory, "NCR"),\n'
         '   Line: varNc.Line, ValueStream: varNc.ValueStream, SQDCP: {Value: "Quality"}, Source: {Value: "NCR"}, Status: {Value: "Open"},\n'
         '   Problem: varNc.Description, Countermeasure: n4Rc.Text, Owner: varNc.Owner, RaisedDate: Now(), DueDate: varNc.DueDate, RefKey: varNc.Title});\n'
         ' Patch(NCR, LookUp(NCR, ID = varNc.ID), {NewspaperRef: varNc.Title}); Select(nSide),\n'
         ' Notify("Action not created: " & FirstError.Message, NotificationType.Error),\n'
         ' Notify("Action added to the Newspaper. Edit owner, due date and detail there.", NotificationType.Success))')
out.append(btn("n4News", '"+  ADD ACTION TO NEWSPAPER"', NEWSA, C0, Y + 36, 300, 48, size=12, fill=TEAL_D, color=WHITE,
               extra=VX(4, {"Tooltip": '="Creates a Quality action in the Newspaper, linked to this NCR (RefKey = NCR number)."', **RAD})))
out.append(btn("n4Open", '"OPEN NEWSPAPER  ↗"', 'Launch(varNcNewsLink)', C0 + 310, Y + 36, 220, 48, size=12, fill=TEAL, color=DARK,
               extra={"Visible": F(vis(4) + ' && !IsBlank(varNcNewsLink)'), **RAD}))
out.append(btn("n4Rca", '"ROOT CAUSE ANALYSIS  (COMING)"', 'false', C0 + 540, Y + 36, 300, 48, size=12, fill=G1, color=G5,
               extra={"Visible": F(vis(4)), "DisplayMode": "=DisplayMode.Disabled", "DisabledFill": F(G1), "DisabledColor": F(G5), **RAD}))
nk = [label("gNnA", 'ThisItem.Action', 8, 2, 760, 36, size=12, bold=True, color=DARK, indent=6, extra={"Wrap": "=false"}),
      label("gNnO", 'Coalesce(ThisItem.Owner, "no owner") & "  ·  due " & Text(ThisItem.DueDate, "m/d")', 770, 2, 280, 36, size=11, color=G9, indent=6),
      label("gNnS", 'ThisItem.Status.Value', 1060, 6, 140, 28, size=10, bold=True, color=WHITE, align="Center", indent=6,
            extra={"Fill": F(f'Switch(ThisItem.Status.Value, "Closed", {GREEN}, "In progress", {BLUE}, {RED_})')})]
gpn = {"Items": F("colNcNews"), "TemplateSize": "=40", "TemplatePadding": "=0", "Visible": F(vis(4))}
gpn.update(box(C0, Y + 94, RW - 32, 280))
out.append(ctrl("galNcNews", "Gallery@2.15.0", gpn, 0, nk, variant="BrowseLayout_Vertical_TwoTextOneImageVariant_ver5.0"))
OK4 = '(n4Req.Selected.Value = "No" || !IsBlank(n4Rc.Text))'
SAVE4 = ('IfError(Set(varNc, Patch(NCR, LookUp(NCR, ID = varNc.ID), {CARequired: n4Req.Selected.Value = "Yes", RootCause: n4Rc.Text, SimilarCheck: n4Sim.Text,\n'
         '   CABy: If(IsBlank(varNc.CAAt), User().FullName, varNc.CABy), CAAt: Coalesce(varNc.CAAt, Now()),\n'
         '   Status: If(n4Req.Selected.Value = "Yes", ' + adv("CA in progress") + ', {Value: varNc.Status.Value})})),\n'
         ' Notify("NOT SAVED: " & FirstError.Message, NotificationType.Error),\n'
         ' Notify("Corrective action saved.", NotificationType.Success); Select(nLoad); Set(varNcStep, 5))')
out.append(btn("n4Save", f'If({OK4}, "SAVE CORRECTIVE ACTION", "ENTER THE ROOT CAUSE")', SAVE4, RX + RW - 16 - 320, 990, 320, 64, size=15, fill=BLUE, color=WHITE,
               extra=VX(4, {"DisplayMode": F(f'If({LOCK}, DisplayMode.Disabled, {OK4}, DisplayMode.Edit, DisplayMode.Disabled)'), "DisabledFill": F(G1), "DisabledColor": F(G9), **RAD})))

# ---------- stage 5: VERIFY & CLOSE ----------
Y = 236
out.append(cv("n5cEff", "DID THE FIX WORK?", C0, Y, 240, 5))
out.append(dd("n5Eff", '["Pending", "Yes", "No"]', C0, Y + 22, 240, 52, default='If(IsBlank(varNc) || IsBlank(varNc.Effective.Value), "Pending", varNc.Effective.Value)', size=16, bold=True,
              extra=VX(5, {"Tooltip": '="No = it came back. Re-open the root cause (stage 4) with new actions."'})))
out.append(cv("n5cEv", "EVIDENCE  (HOW YOU KNOW: NO REPEAT IN X WEEKS, AUDIT, DATA)", C0 + 250, Y, RW - 32 - 250, 5))
out.append(ti("n5Ev", 'If(IsBlank(varNc), "", varNc.EffectNotes)', C0 + 250, Y + 22, RW - 32 - 250, 150, 'false', hint='"0 repeats in 6 weeks of HxH and QA data"', size=14, number=False,
              extra=VX(5, ML(req('n5Eff.Selected.Value = "Yes" && IsBlank(Self.Text)')))))
Y = 430
out.append(cv("n5cRk", "RISKS / QMS UPDATED?", C0, Y, 240, 5))
out.append(dd("n5Rk", YN, C0, Y + 22, 240, 52, default=ynd("RiskQMSUpdated"), size=16,
              extra=VX(5, {"Tooltip": '="ISO 10.2.1e-f: update risks (PFMEA), control plan, SOPs, standard work, training as needed."'})))
out.append(cv("n5cRkN", "WHAT CHANGED  (PFMEA, CONTROL PLAN, SOP, STANDARD WORK, TRAINING)  OR WHY NOTHING NEEDED TO", C0 + 250, Y, RW - 32 - 250, 5))
out.append(ti("n5RkN", 'If(IsBlank(varNc), "", varNc.RiskQMSNotes)', C0 + 250, Y + 22, RW - 32 - 250, 120, 'false', hint='"SOP QA-14 rev C, operators retrained 10/24"', size=14, number=False,
              extra=VX(5, ML())))
REWV = '(varNc.Disposition.Value in ["Rework", "Repair", "Regrade"])'
CHECKS = [("Contained", '!IsBlank(varNc.ContainedAt)'),
          ("Disposition decided and authorized", '!IsBlank(varNc.DispositionAt)'),
          ("Re-verified after rework / repair / regrade", f'(!{REWV} || varNc.Reverified)'),
          ("Concession recorded for Use as is", '(varNc.Disposition.Value <> "Use as is" || !IsBlank(varNc.Concession))'),
          ("Root cause recorded", '(!varNc.CARequired || !IsBlank(varNc.RootCause))'),
          ("Fix proven effective", '(!varNc.CARequired || n5Eff.Selected.Value = "Yes")'),
          ("Linked Newspaper actions closed", 'CountRows(Filter(colNcNews, Status.Value <> "Closed")) = 0')]
Y = 600
out.append(label("n5ChT", '"READY TO CLOSE?"', C0, Y, 400, 30, size=13, bold=True, color=DARK, extra={"Visible": F(vis(5))}))
for i, (t, c) in enumerate(CHECKS):
    out.append(label(f"n5Ch{i}", f'If(!IsBlank(varNc) && {c}, "✓   ", "✗   ") & "{t}"', C0 + (i // 4) * 600, Y + 36 + (i % 4) * 34, 590, 32, size=13, bold=True,
                     extra={"Visible": F(vis(5)), "Color": F(f'If(!IsBlank(varNc) && {c}, {GREEN}, {RED_})')}))
READY = '(!IsBlank(varNc) && ' + " && ".join(c for _, c in CHECKS) + ')'
REC5 = '{Effective: {Value: n5Eff.Selected.Value}, EffectNotes: n5Ev.Text, RiskQMSUpdated: n5Rk.Selected.Value = "Yes", RiskQMSNotes: n5RkN.Text'
SAVE5 = ('IfError(Set(varNc, Patch(NCR, LookUp(NCR, ID = varNc.ID), ' + REC5 + ', VerifiedBy: If(n5Eff.Selected.Value = "Pending", varNc.VerifiedBy, User().FullName),\n'
         '   VerifiedAt: If(n5Eff.Selected.Value = "Pending", varNc.VerifiedAt, Now())})),\n'
         ' Notify("NOT SAVED: " & FirstError.Message, NotificationType.Error), Notify("Saved.", NotificationType.Success); Select(nLoad))')
CLOSE = ('IfError(Set(varNc, Patch(NCR, LookUp(NCR, ID = varNc.ID), ' + REC5 + ', VerifiedBy: User().FullName, VerifiedAt: Now(),\n'
         '   Status: {Value: "Closed"}, ClosedBy: User().FullName, ClosedAt: Now()})),\n'
         ' Notify("NOT CLOSED: " & FirstError.Message, NotificationType.Error), Notify(varNc.Title & " closed.", NotificationType.Success); Select(nLoad))')
out.append(btn("n5Save", '"SAVE"', SAVE5, RX + RW - 16 - 320 - 196, 990, 180, 64, size=15, fill=G1, color=DARK,
               extra=VX(5, {"DisplayMode": F(f'If({LOCK}, DisplayMode.Disabled, DisplayMode.Edit)'), **RAD})))
out.append(btn("n5Close", f'If({READY}, "CLOSE NCR", "NOT READY TO CLOSE")', CLOSE, RX + RW - 16 - 320, 990, 320, 64, size=16,
               fill=f'If({READY}, {GREEN}, {G1})', color=f'If({READY}, {WHITE}, {G9})',
               extra={"Visible": F(vis(5) + ' && !' + LOCK), "DisplayMode": F(f'If({READY}, DisplayMode.Edit, DisplayMode.Disabled)'), "DisabledFill": F(G1), "DisabledColor": F(G9), **RAD}))
REOPEN = ('IfError(Set(varNc, Patch(NCR, LookUp(NCR, ID = varNc.ID), {Status: {Value: If(IsBlank(varNc.DispositionAt), "Open", "CA in progress")}, ClosedBy: Blank(), ClosedAt: Blank()})),\n'
          ' Notify("NOT REOPENED: " & FirstError.Message, NotificationType.Error), Notify("Reopened.", NotificationType.Success); Select(nLoad))')
out.append(btn("n5Reopen", '"REOPEN"', REOPEN, RX + RW - 16 - 320, 990, 320, 64, size=16, fill=AMB, color=WHITE,
               extra={"Visible": F(f'{HAS} && {LOCK}'), "Tooltip": '="Reopen a closed or voided NCR (the history stamps are kept)."', **RAD}))
VOID = ('IfError(Set(varNc, Patch(NCR, LookUp(NCR, ID = varNc.ID), {Status: {Value: "Void"}, ClosedBy: User().FullName, ClosedAt: Now()})),\n'
        ' Notify("NOT VOIDED: " & FirstError.Message, NotificationType.Error), Notify("Voided. It stays in the log for audit but is excluded from counts.", NotificationType.Success); Select(nLoad))')
out.append(btn("n5Void", '"VOID (RAISED BY MISTAKE)"', VOID, C0, 1006, 240, 40, size=10, fill=WHITE, color=G9,
               extra={"Visible": F(f'{vis(5)} && !{LOCK} && !varNcNew'), "BorderColor": F(G5), "BorderThickness": "=1", **RAD}))

# reset helper: puts every input back to its Default (the selected NCR)
INPUTS = ["n1Src", "n1Sev", "n1Line", "n1Date", "n1Shift", "n1Own", "n1Prod", "n1Job", "n1Lot", "n1Party", "n1Def", "n1Qty", "n1Unit", "n1Due", "n1Desc", "n1AddPh", "n1Type",
          "n2Act", "n2Qty", "n2Loc", "n3Disp", "n3Qty", "n3Inf", "n3Con", "n3Notes", "n3Rv", "n3RvN", "n4Req", "n4Rc", "n4Sim", "n5Eff", "n5Ev", "n5Rk", "n5RkN"]
out.append(btn("nReset", '""', "; ".join(f"Reset({n})" for n in INPUTS), 2, 1079, 1, 1, fill=CLEAR, color=CLEAR, extra=HELP))
out.append(label("nLoaded", 'If(IsBlank(varNcLoaded), "", "Loaded " & Text(varNcLoaded, "h:mm AM/PM") & "  ·  last 12 months")', LX + 16, 1050, 300, 20, size=9, color=G9))
write_themed(OUTN, "".join(out)); print("wrote", OUTN)
