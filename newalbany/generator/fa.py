# Generates Frontier_Audit_v2.pa.yaml: phone (640x1136) Frontier safety + 5S audit (lite), modeled on DuPont STOP.
# D-S-O-I-R: zone -> decide/stop -> observe safety (19 items, S/AR/U/N/A) -> observe 5S vs the zone's 5S standard
# -> interact (4 questions, comfort) -> record (close the loop) -> submit.
import os, sys
exec(open(__import__("os").environ["MDI_GEN"]+"/theme.py").read())
src = open(__import__("os").environ["MDI_GEN"]+"/build6.py").read()
exec(src[:src.index("DT_OLD=")])
EXTRA.clear()
OUT = sys.argv[1] if len(sys.argv) > 1 else __import__("os").environ["MDI_OUTDIR"]+"/Frontier_Audit_v2.pa.yaml"
MUTE = "RGBA(243, 244, 244, 1)"; YEL = "RGBA(255, 242, 179, 1)"; YELB = "RGBA(210, 153, 34, 1)"
LGREEN = "RGBA(220, 242, 225, 1)"; ORANGE = "RGBA(227, 98, 9, 1)"
RAD = {"RadiusTopLeft": "=8", "RadiusTopRight": "=8", "RadiusBottomLeft": "=8", "RadiusBottomRight": "=8"}
W = 640; FLOW = "'MDI-UploadPhoto'"

BODY = r'''
def rect(name, fill, x, y, w, h, indent=0, extra=None):
    d = {"Fill": F(fill)}; d.update(box(x, y, w, h))
    if extra: d.update(extra)
    return ctrl(name, "Rectangle@2.3.0", d, indent)
def image(name, img, x, y, w, h, indent=0, extra=None):
    d = {"Image": F(img), "ImagePosition": "=ImagePosition.Fit", "Fill": F(MUTE)}; d.update(box(x, y, w, h))
    if extra: d.update(extra)
    return ctrl(name, "Image@2.2.3", d, indent)
def P(step, *names):
    for n in names: EXTRA.setdefault(n, {})["Visible"] = F(f'varStep = "{step}" && IsBlank(varPanel)')
def PN(panel, *names):
    for n in names: EXTRA.setdefault(n, {})["Visible"] = F(f'varPanel = "{panel}"')
def outline(col): return {"BorderColor": F(col), "BorderThickness": "=2", **RAD}
SEVCOL = f'Switch(@S, "Critical", {RED}, "High", {ORANGE}, "Medium", {AMBER}, "Low", {GREEN}, {G5})'
def sevcol(expr): return SEVCOL.replace("@S", expr)
SHIFT = 'If(Hour(Now()) * 60 + Minute(Now()) >= 360 && Hour(Now()) * 60 + Minute(Now()) < 990, 1, 2)'
ZONE = 'varZone'
CUR = 'LookUp(colAns, ItemNo = varItem)'
SEC = 'LookUp(colSec, ElNo = varSec)'
DUE = 'Coalesce(Value(LookUp(colCfg, Setting = "SAF_DueDays_" & @S).SettingValue), Switch(@S, "Critical", 1, "High", 1, "Medium", 30, "Low", 90, 30))'
def due(expr): return DUE.replace("@S", expr)
Y0 = 130

# ---------------- header ----------------
out.append(rect("hdrBar", DARK, 0, 0, W, 118))
out.append(label("lblBrand", '"voyant"', 16, 4, 140, 40, size=22, color=WHITE, font="Georgia"))
out.append(label("lblTitle", '"FRONTIER AUDIT"', 150, 8, 400, 36, size=17, bold=True, color=WHITE, font="Georgia"))
out.append(label("lblCtx", 'If(IsBlank(varZone), "Safety + 5S observation  ·  STOP", varZone.ZoneID & "  ·  " & varZone.ZoneName)', 16, 50, W - 32, 30, size=13, bold=True, color=AQUA))
out.append(label("lblUser", 'User().FullName & "  ·  S" & ' + SHIFT, 16, 82, W - 240, 26, size=11, color=G5))
LOAD = ('IfError(ClearCollect(colZoneRaw, Filter(SAF_Zones, Active = true)), Notify("Could not load SAF_Zones: " & FirstError.Message, NotificationType.Error));\n'
 'IfError(ClearCollect(colRecent, Filter(SAF_Audits, AuditDate >= DateAdd(Today(), -120, TimeUnit.Days))), Notify("Could not load SAF_Audits", NotificationType.Warning));\n'
 'IfError(ClearCollect(colItems, Sort(Filter(SAF_Items, Active = true), ItemNo)), Notify("Could not load SAF_Items", NotificationType.Error));\n'
 'IfError(ClearCollect(colCfg, Filter(MDI_Config, StartsWith(Setting, "SAF_"))), Notify("Could not load MDI_Config", NotificationType.Warning));\n'
 'ClearCollect(colZones, ForAll(colZoneRaw As z,\n'
 '  With({last: Max(Filter(colRecent, ZoneID = z.ZoneID), AuditDate), every: Switch(z.Frequency.Value, "Weekly", 7, "Biweekly", 14, "Quarterly", 92, 31)},\n'
 '   {ID: z.ID, ZoneID: z.ZoneID, ZoneName: z.ZoneName, ZoneType: z.ZoneType.Value, Line: z.Line, Area: z.Area, Risk: z.RiskLevel.Value,\n'
 '    Freq: z.Frequency.Value, PPE: z.RequiredPPE, Hazards: z.PrimaryHazards, StandardID: z.StandardID, Owner: z.Owner, OwnerEmail: z.OwnerEmail,\n'
 '    Last: last, Due: IsBlank(last) || DateDiff(last, Today(), TimeUnit.Days) >= every,\n'
 '    RiskN: Switch(z.RiskLevel.Value, "High", 1, "Medium", 2, 3)})));\n'
 'If(!varParamUsed && !IsBlank(Param("zone")), Set(varZone, LookUp(colZones, ZoneID = Param("zone"))); If(!IsBlank(varZone), Select(btnFStart), Notify("Zone " & Param("zone") & " is not in SAF_Zones (or not Active).", NotificationType.Warning)));\n'
 'Set(varParamUsed, true);\n'
 'If(IsBlank(varStep), Set(varStep, "zone"));\n'
 'Set(varLoaded, Now())')
out.append(btn("btnFRefresh", '"↻"', LOAD, W - 70, 72, 54, 38, fill=TEAL_D, color=WHITE, size=16, extra=RAD))
out.append(btn("btnFZones", '"‹ ZONES"', 'Set(varStep, "zone"); Set(varPanel, Blank())', W - 190, 72, 110, 38, fill=TEAL_D, color=WHITE, size=12,
   extra={**RAD, "Visible": F('varStep <> "zone" && varStep <> "done" && IsBlank(varPanel)')}))

# step bar (D S O O I R)
STEPS = [("decide", "DECIDE"), ("safety", "SAFETY"), ("fives", "5S"), ("interact", "INTERACT"), ("record", "RECORD")]
sw = (W - 32) // len(STEPS)
for i, (k, t) in enumerate(STEPS):
    cur = f'With({{now: Switch(varStep, "decide", 0, "safety", 1, "fives", 2, "interact", 3, "record", 4, -1)}}, If({i} = now, 2, {i} < now, 1, 0))'
    out.append(label(f"st{i}", f'"{t}"', 16 + i * sw, Y0 - 8, sw - 4, 26, size=9, bold=True, align="Center",
        color=f'If({cur} = 0, {G9}, {WHITE})', fill=f'Switch({cur}, 2, {TEAL_D}, 1, {TEAL}, {G1})',
        extra={"Visible": F('varStep <> "zone" && varStep <> "done" && IsBlank(varPanel)')}))
Y1 = Y0 + 26

# ---------------- zone ----------------
out.append(label("zT", '"WHICH ZONE?"', 16, Y0, 300, 40, size=18, bold=True, color=DARK, font="Georgia"))
out.append(btn("btnDueOnly", 'If(varAllZones, "SORT: A–Z", "SORT: DUE FIRST")', 'Set(varAllZones, !varAllZones)', W - 216, Y0, 200, 40, fill=WHITE, color=TEAL_D, size=12, extra=outline(TEAL_D)))
zk = [rect("gZBg", WHITE, 0, 0, W - 20, 120, indent=6, extra={"BorderColor": F(G1), "BorderThickness": "=1"}),
      rect("gZTab", f'If(ThisItem.Due, {RED}, {GREEN})', 0, 0, 14, 120, indent=6),
      label("gZName", 'ThisItem.ZoneName', 26, 4, W - 210, 50, size=15, bold=True, color=DARK, indent=6),
      label("gZSub", 'ThisItem.ZoneID & "  ·  " & ThisItem.ZoneType & "  ·  " & ThisItem.Risk & " risk"', 26, 54, W - 210, 28, size=11, color=G9, indent=6),
      label("gZLast", 'If(IsBlank(ThisItem.Last), "Never audited", "Last audit " & Text(ThisItem.Last, "m/d") & " (" & DateDiff(ThisItem.Last, Today(), TimeUnit.Days) & " d ago)") & "  ·  " & ThisItem.Freq', 26, 82, W - 210, 28, size=11, color=G9, indent=6),
      label("gZState", 'If(ThisItem.Due, "DUE", "OK")', W - 160, 38, 120, 44, size=14, bold=True, align="Center", indent=6, color=WHITE,
            fill=f'If(ThisItem.Due, {RED}, {GREEN})'),
      btn("gZSel", '""', 'Set(varZone, ThisItem); Select(btnFStart)', 0, 0, W - 20, 120, fill=CLEAR, color=CLEAR, indent=6,
          extra={"HoverFill": F("RGBA(0, 72, 81, 0.06)"), "PressedFill": F("RGBA(0, 72, 81, 0.12)"), "BorderColor": F(CLEAR)})]
gp = {"Items": F('If(varAllZones, SortByColumns(colZones, "ZoneID", SortOrder.Ascending), SortByColumns(colZones, "Due", SortOrder.Descending, "RiskN", SortOrder.Ascending, "ZoneID", SortOrder.Ascending))'),
      "TemplateSize": "=128", "TemplatePadding": "=0"}; gp.update(box(10, Y0 + 50, W - 20, 900))
out.append(ctrl("galZones", "Gallery@2.15.0", gp, 0, zk, variant="BrowseLayout_Vertical_TwoTextOneImageVariant_ver5.0"))
out.append(label("zNone", '"No zones yet. Add them to the SAF_Zones list (ZoneID, name, type, risk, frequency, 5S standard)."', 16, Y0 + 60, W - 32, 80, size=13, color=G9,
   extra={"Visible": F('varStep = "zone" && CountRows(colZones) = 0')}))
P("zone", "zT", "btnDueOnly", "galZones")

# ---------------- decide + stop ----------------
out.append(label("dName", ZONE + '.ZoneName', 16, Y1 + 4, W - 32, 44, size=19, bold=True, color=DARK, font="Georgia"))
out.append(label("dInfo", ZONE + '.ZoneID & "  ·  " & ' + ZONE + '.ZoneType & "  ·  " & ' + ZONE + '.Risk & " risk" & If(IsBlank(' + ZONE + '.Line), "", "  ·  Line " & ' + ZONE + '.Line)', 16, Y1 + 48, W - 32, 28, size=12, color=G9))
out.append(label("dPPE", '"PPE:  " & Coalesce(' + ZONE + '.PPE, "(not set)") & Char(10) & "HAZARDS:  " & Coalesce(' + ZONE + '.Hazards, "(not set)")', 16, Y1 + 80, W - 32, 96, size=12, bold=True, color=DARK, fill=YEL,
   extra={"PaddingLeft": "=12", "PaddingRight": "=12", "VerticalAlign": "=VerticalAlign.Top", "PaddingTop": "=8"}))
out.append(cap("dC1", "AUDIT TYPE", 16, Y1 + 186, 300))
out.append(dd("ddClass", '["Routine", "Deep dive", "Post-incident", "New process", "Seasonal"]', 16, Y1 + 206, 300, 48, default='"Routine"', size=15))
out.append(cap("dC2", "DECIDE: WHY THIS ZONE, WHY NOW?  (required)", 16, Y1 + 266, W - 32, color=TEAL_D))
out.append(ti("txtWhy", '""', 16, Y1 + 286, W - 32, 90, 'false', hint='"e.g. due; near-miss reported; changeover this week; never audited"', size=14, number=False,
   extra={"Align": "=Align.Left", "Mode": "=TextMode.MultiLine", "Fill": F(f'If(IsBlank(Self.Text), {YEL}, {WHITE})')}))
out.append(cap("dC3", "STOP: 60 SECONDS AT THE THRESHOLD. FIRST IMPRESSIONS", 16, Y1 + 388, W - 32, color=TEAL_D))
out.append(label("dStopHint", '"Before you walk in: odors, lighting, noise, clutter, traffic, postures. Look up, look down, look behind."', 16, Y1 + 408, W - 32, 48, size=11, color=G9))
out.append(ti("txtStop", '""', 16, Y1 + 456, W - 32, 110, 'false', hint='"what you notice before entering"', size=14, number=False,
   extra={"Align": "=Align.Left", "Mode": "=TextMode.MultiLine"}))
OKD = '!IsBlank(Trim(txtWhy.Text))'
out.append(btn("btnDNext", f'If({OKD}, "START OBSERVING ›", "SAY WHY THIS ZONE")', 'Set(varStep, "safety")', 16, Y1 + 590, W - 32, 80,
   fill=f'If({OKD}, {TEAL_D}, {G1})', color=f'If({OKD}, {WHITE}, {G9})', size=20,
   extra={"DisplayMode": F(f'If({OKD}, DisplayMode.Edit, DisplayMode.Disabled)'), "DisabledFill": F(G1), "DisabledColor": F(G9), **RAD}))
P("decide", "dName", "dInfo", "dPPE", "dC1", "ddClass", "dC2", "txtWhy", "dC3", "dStopHint", "txtStop", "btnDNext")

# ---------------- observe: safety ----------------
NRATED = 'CountRows(Filter(colAns, !IsBlank(Rating)))'
BAD = '(a.Rating = "AR" || a.Rating = "U")'
INCOMPLETE = f'(IsBlank(a.Rating) || ({BAD} && (IsBlank(a.Sev) || IsBlank(Trim(a.Finding)) || !a.HasPh || ((a.Sev = "Critical" || a.Sev = "High") && IsBlank(Trim(a.Imm))))))'
SAFE_OK = f'CountRows(Filter(colAns As a, {INCOMPLETE})) = 0'
out.append(label("sT", '"OBSERVE · SAFETY"', 16, Y1 + 4, 330, 40, size=18, bold=True, color=DARK, font="Georgia"))
out.append(label("sCount", NRATED + ' & " / " & CountRows(colAns) & " rated"', W - 236, Y1 + 8, 220, 32, size=13, bold=True, align="Right", color=TEAL_D))
out.append(label("sHint", '"S = safe  ·  AR = at risk  ·  U = unsafe  ·  N/A = not here. AR/U needs severity, what you saw and a photo."', 16, Y1 + 46, W - 32, 44, size=10, color=G9))
def rb(name, txt, val, x, w, col):
    sel = f'ThisItem.Rating = "{val}"'
    onsel = (f'Patch(colAns, LookUp(colAns, ItemNo = ThisItem.ItemNo), {{Rating: "{val}"}})' +
             (f'; Set(varItem, ThisItem.ItemNo); Reset(txtFind); Reset(txtImm); Reset(addF); Set(varPanel, "find")' if val in ("AR", "U") else
              f'; Patch(colAns, LookUp(colAns, ItemNo = ThisItem.ItemNo), {{Sev: "", Finding: "", Imm: "", HasPh: false}}); RemoveIf(colPhotos, Key = "S" & ThisItem.ItemNo)'))
    return btn(name, f'"{txt}"', onsel, x, 64, w, 50, fill=f'If({sel}, {col}, {WHITE})', color=f'If({sel}, {WHITE}, {col})', size=15, indent=6,
               extra={"BorderColor": F(col), "BorderThickness": "=2", **RAD})
ROWBAD = f'(ThisItem.Rating = "AR" || ThisItem.Rating = "U")'
ROWINC = f'With({{a: ThisItem}}, {INCOMPLETE.replace("a.", "a.")})'
sk = [rect("gSBg", f'If({ROWBAD} && {ROWINC}, {YEL}, {WHITE})', 0, 0, W - 20, 178, indent=6, extra={"BorderColor": F(G1), "BorderThickness": "=1"}),
      label("gSCat", 'Upper(ThisItem.Category) & "  ·  " & ThisItem.ItemNo', 12, 2, W - 60, 22, size=9, bold=True, color=TEAL_D, indent=6),
      label("gSItem", 'ThisItem.Item', 12, 22, W - 60, 40, size=15, bold=True, color=DARK, indent=6),
      rb("gSs", "S", "S", 12, 130, GREEN), rb("gSar", "AR", "AR", 152, 130, AMBER), rb("gSu", "U", "U", 292, 130, RED), rb("gSna", "N/A", "N/A", 432, 140, G9),
      label("gSFind", 'If(' + ROWBAD + ', If(IsBlank(ThisItem.Sev), "Tap to add the finding", ThisItem.Sev & ":  " & Coalesce(ThisItem.Finding, "(describe it)")) & If(ThisItem.HasPh, "   📷", "   (no photo)"), "")', 12, 120, W - 110, 50, size=11, bold=True, indent=6,
            color=f'If(IsBlank(ThisItem.Sev), {RED}, {DARK})'),
      btn("gSEdit", '"✎"', 'Set(varItem, ThisItem.ItemNo); Reset(txtFind); Reset(txtImm); Reset(addF); Set(varPanel, "find")', W - 90, 120, 60, 46, fill=WHITE, color=TEAL_D, size=16, indent=6,
          extra={"Visible": F(ROWBAD), **outline(TEAL_D)})]
gp = {"Items": F("colAns"), "TemplateSize": "=184", "TemplatePadding": "=0"}; gp.update(box(10, Y1 + 92, W - 20, 760))
out.append(ctrl("galSafety", "Gallery@2.15.0", gp, 0, sk, variant="BrowseLayout_Vertical_TwoTextOneImageVariant_ver5.0"))
out.append(btn("btnSNext", f'If({SAFE_OK}, "5S ›", "RATE EVERY ITEM (" & CountRows(Filter(colAns As a, {INCOMPLETE})) & " LEFT)")', 'Set(varStep, "fives")', 16, Y1 + 862, W - 32, 76,
   fill=f'If({SAFE_OK}, {TEAL_D}, {G1})', color=f'If({SAFE_OK}, {WHITE}, {G9})', size=18,
   extra={"DisplayMode": F(f'If({SAFE_OK}, DisplayMode.Edit, DisplayMode.Disabled)'), "DisabledFill": F(G1), "DisabledColor": F(G9), **RAD}))
P("safety", "sT", "sCount", "sHint", "galSafety", "btnSNext")

# ---------- finding panel (safety AR/U) ----------
out.append(rect("fBg", WHITE, 0, 118, W, 1018))
out.append(label("fItem", CUR + '.Item', 16, Y0, W - 32, 44, size=18, bold=True, color=DARK, font="Georgia"))
out.append(label("fLook", '"LOOK FOR:  " & ' + CUR + '.LookFor', 16, Y0 + 44, W - 32, 70, size=11, color=G9))
def fr(name, txt, val, x, col):
    sel = f'{CUR}.Rating = "{val}"'
    return btn(name, f'"{txt}"', f'Patch(colAns, {CUR}, {{Rating: "{val}"}})', x, Y0 + 118, 296, 50, fill=f'If({sel}, {col}, {WHITE})', color=f'If({sel}, {WHITE}, {col})', size=15,
               extra={"BorderColor": F(col), "BorderThickness": "=2", **RAD})
out.append(fr("fAR", "AT RISK", "AR", 16, AMBER)); out.append(fr("fU", "UNSAFE", "U", 328, RED))
out.append(cap("fC1", "SEVERITY  (required)", 16, Y0 + 178, W - 32, color=TEAL_D))
SEVS = [("Critical", "C", "Stop work. Teams alert now."), ("High", "H", "Action within 24 hours"), ("Medium", "M", "Within 30 days"), ("Low", "L", "Next maintenance window")]
for i, (s, c, hint) in enumerate(SEVS):
    col = {"Critical": RED, "High": ORANGE, "Medium": AMBER, "Low": GREEN}[s]
    sel = f'{CUR}.Sev = "{s}"'
    out.append(btn(f"fSev{c}", f'"{c}"', f'Patch(colAns, {CUR}, {{Sev: "{s}", Act: If("{s}" = "Critical" || "{s}" = "High", true, {CUR}.Act)}})', 16 + i * 152, Y0 + 198, 144, 56,
       fill=f'If({sel}, {col}, {WHITE})', color=f'If({sel}, {WHITE}, {col})', size=22, extra={"BorderColor": F(col), "BorderThickness": "=3", **RAD}))
out.append(label("fSevHint", 'Switch(' + CUR + '.Sev, ' + ", ".join(f'"{s}", "{s.upper()}: {h}"' for s, _, h in SEVS) + ', "C critical · H high · M medium · L low")', 16, Y0 + 258, W - 32, 28, size=11, bold=True,
   color=sevcol(CUR + '.Sev')))
out.append(cap("fC2", "WHAT DID YOU SEE?  (required)", 16, Y0 + 292, W - 32, color=TEAL_D))
out.append(ti("txtFind", CUR + '.Finding', 16, Y0 + 312, W - 32, 100, 'Patch(colAns, ' + CUR + ', {Finding: Self.Text})', hint='"condition or behavior, where exactly"', size=14, number=False,
   extra={"Align": "=Align.Left", "Mode": "=TextMode.MultiLine", "Fill": F(f'If(IsBlank(Self.Text), {YEL}, {WHITE})')}))
out.append(cap("fC3", 'IMMEDIATE ACTION TAKEN' , 16, Y0 + 420, W - 32, color=TEAL_D))
EXTRA.setdefault("fC3", {})["Text"] = F('"IMMEDIATE ACTION TAKEN" & If(' + CUR + '.Sev = "Critical" || ' + CUR + '.Sev = "High", "  (required for C/H)", "  (optional)")')
out.append(ti("txtImm", CUR + '.Imm', 16, Y0 + 440, W - 32, 80, 'Patch(colAns, ' + CUR + ', {Imm: Self.Text})', hint='"e.g. stopped the job, barricaded, told supervisor"', size=14, number=False,
   extra={"Align": "=Align.Left", "Mode": "=TextMode.MultiLine",
          "Fill": F(f'If(IsBlank(Self.Text) && ({CUR}.Sev = "Critical" || {CUR}.Sev = "High"), {YEL}, {WHITE})')}))
out.append(ctrl("addF", "AddMedia@2.2.1", {"X": "=16", "Y": F(str(Y0 + 532)), "Width": "=300", "Height": "=150", "Size": "=13",
   "Text": F('If(' + CUR + '.HasPh, "✓ PHOTO TAKEN (tap to retake)", "📷  PHOTO (required)")'),
   "Fill": F(f'If({CUR}.HasPh, {MUTE}, {YEL})'), "Color": F(TEAL_D), "BorderColor": F(G5), "BorderThickness": "=1",
   "OnChange": F('RemoveIf(colPhotos, Key = "S" & varItem); Collect(colPhotos, {Key: "S" & varItem, No: varItem, Kind: "Safety", Ph: Self.Media}); Patch(colAns, ' + CUR + ', {HasPh: true})')}))
out.append(image("fPh", 'LookUp(colPhotos, Key = "S" & varItem).Ph', 328, Y0 + 532, W - 344, 150))
out.append(btn("fAct", 'If(' + CUR + '.Act, "☑  ADD TO NEWSPAPER", "☐  ADD TO NEWSPAPER")', 'If(' + CUR + '.Sev = "Critical" || ' + CUR + '.Sev = "High", Notify("Critical and High findings always get an action.", NotificationType.Information), Patch(colAns, ' + CUR + ', {Act: !' + CUR + '.Act}))',
   16, Y0 + 694, W - 32, 56, fill=WHITE, color=TEAL_D, size=14, extra={**outline(TEAL_D), "Tooltip": '="Creates a NEWSPAPER action with a due date set by severity."'}))
FOK = f'With({{a: {CUR}}}, !{INCOMPLETE.replace("IsBlank(Trim(a.Finding))", "IsBlank(Trim(txtFind.Text))").replace("IsBlank(Trim(a.Imm))", "IsBlank(Trim(txtImm.Text))")})'
out.append(btn("fDone", f'If({FOK}, "DONE ›", "SEVERITY + WHAT YOU SAW + PHOTO")', 'Patch(colAns, ' + CUR + ', {Finding: txtFind.Text, Imm: txtImm.Text}); Set(varPanel, Blank())', 16, Y0 + 762, W - 32, 76,
   fill=f'If({FOK}, {TEAL_D}, {G1})', color=f'If({FOK}, {WHITE}, {G9})', size=17,
   extra={"DisplayMode": F(f'If({FOK}, DisplayMode.Edit, DisplayMode.Disabled)'), "DisabledFill": F(G1), "DisabledColor": F(G9), **RAD}))
out.append(btn("fUndo", '"Not a finding: clear rating"', 'Patch(colAns, ' + CUR + ', {Rating: "", Sev: "", Finding: "", Imm: "", HasPh: false}); RemoveIf(colPhotos, Key = "S" & varItem); Set(varPanel, Blank())',
   16, Y0 + 850, W - 32, 50, fill=WHITE, color=G9, size=12, extra={"BorderColor": F(WHITE)}))
PN("find", "fBg", "fItem", "fLook", "fAR", "fU", "fC1", "fSevC", "fSevH", "fSevM", "fSevL", "fSevHint", "fC2", "txtFind", "fC3", "txtImm", "addF", "fPh", "fAct", "fDone", "fUndo")

# ---------------- observe: 5S against the zone standard ----------------
DEFINC = '(IsBlank(s.Rating) || (s.Rating = "Deficient" && (IsBlank(s.Pillar) || IsBlank(Trim(s.Finding)) || !s.HasPh || (s.SafetyRel && IsBlank(s.Sev)))))'
FIVE_OK = f'CountRows(Filter(colSec As s, {DEFINC})) = 0'
out.append(label("vT", '"OBSERVE · 5S"', 16, Y1 + 4, 300, 40, size=18, bold=True, color=DARK, font="Georgia"))
out.append(label("vStd", 'If(IsBlank(varStd), "No 5S standard linked to this zone: general 5S check. (Link one in SAF_Zones → StandardID.)", "Against: " & varStd.Standard & If(IsBlank(varStd.DocNo), "", "  (" & varStd.DocNo & " rev " & varStd.Rev & ")"))',
   16, Y1 + 46, W - 32, 48, size=11, bold=True, color=f'If(IsBlank(varStd), {AMBER}, {TEAL_D})'))
def vb(name, txt, val, x, w, col):
    sel = f'ThisItem.Rating = "{val}"'
    onsel = (f'Patch(colSec, LookUp(colSec, ElNo = ThisItem.ElNo), {{Rating: "{val}"}})' +
             (f'; Set(varSec, ThisItem.ElNo); Reset(txtDef); Reset(addD); Set(varPanel, "def")' if val == "Deficient" else
              f'; Patch(colSec, LookUp(colSec, ElNo = ThisItem.ElNo), {{Pillar: If(varStdID = 0, ThisItem.Pillar, ""), Finding: "", HasPh: false, SafetyRel: false, Sev: ""}}); RemoveIf(colPhotos, Key = "F" & ThisItem.ElNo)'))
    return btn(name, f'"{txt}"', onsel, x, 122, w, 48, fill=f'If({sel}, {col}, {WHITE})', color=f'If({sel}, {WHITE}, {col})', size=13, indent=6,
               extra={"BorderColor": F(col), "BorderThickness": "=2", **RAD})
ROWDEF = 'ThisItem.Rating = "Deficient"'
vk = [rect("gVBg", f'If({ROWDEF} && With({{s: ThisItem}}, {DEFINC}), {YEL}, {WHITE})', 0, 0, W - 20, 232, indent=6, extra={"BorderColor": F(G1), "BorderThickness": "=1"}),
      image("gVPh", 'LookUp(colStdPh, StepNo = ThisItem.ElNo).Thumbnail.Large', 8, 8, 170, 108, indent=6),
      label("gVNo", '"STANDARD"', 8, 92, 170, 24, size=9, bold=True, color=WHITE, align="Center", fill="RGBA(0, 72, 81, 0.75)", indent=6,
            extra={"Visible": F('!IsBlank(LookUp(colStdPh, StepNo = ThisItem.ElNo))')}),
      label("gVNoPh", '"no standard photo"', 8, 50, 170, 24, size=10, color=G5, align="Center", indent=6, extra={"Visible": F('IsBlank(LookUp(colStdPh, StepNo = ThisItem.ElNo))')}),
      label("gVSec", 'ThisItem.Section', 188, 4, W - 220, 32, size=15, bold=True, color=DARK, indent=6),
      label("gVGood", 'ThisItem.Good', 188, 36, W - 220, 82, size=11, color=G9, indent=6, extra={"VerticalAlign": "=VerticalAlign.Top"}),
      vb("gVok", "MEETS", "OK", 8, 190, GREEN), vb("gVdef", "DEFICIENT", "Deficient", 206, 230, RED), vb("gVna", "N/A", "N/A", 444, 156, G9),
      label("gVFind", 'If(' + ROWDEF + ', Coalesce(ThisItem.Pillar, "Pick the pillar") & ":  " & Coalesce(ThisItem.Finding, "(describe it)") & If(ThisItem.HasPh, "   📷", "   (no photo)") & If(ThisItem.SafetyRel, "   ⚠ " & ThisItem.Sev, ""), "")',
            8, 176, W - 110, 50, size=11, bold=True, color=DARK, indent=6),
      btn("gVEdit", '"✎"', 'Set(varSec, ThisItem.ElNo); Reset(txtDef); Reset(addD); Set(varPanel, "def")', W - 90, 176, 60, 46, fill=WHITE, color=TEAL_D, size=16, indent=6,
          extra={"Visible": F(ROWDEF), **outline(TEAL_D)})]
gp = {"Items": F("colSec"), "TemplateSize": "=240", "TemplatePadding": "=0"}; gp.update(box(10, Y1 + 96, W - 20, 756))
out.append(ctrl("galFive", "Gallery@2.15.0", gp, 0, vk, variant="BrowseLayout_Vertical_TwoTextOneImageVariant_ver5.0"))
out.append(btn("btnVNext", f'If({FIVE_OK}, "INTERACT ›", "RATE EVERY SECTION (" & CountRows(Filter(colSec As s, {DEFINC})) & " LEFT)")', 'Set(varStep, "interact")', 16, Y1 + 862, W - 32, 76,
   fill=f'If({FIVE_OK}, {TEAL_D}, {G1})', color=f'If({FIVE_OK}, {WHITE}, {G9})', size=18,
   extra={"DisplayMode": F(f'If({FIVE_OK}, DisplayMode.Edit, DisplayMode.Disabled)'), "DisabledFill": F(G1), "DisabledColor": F(G9), **RAD}))
P("fives", "vT", "vStd", "galFive", "btnVNext")

# ---------- deficiency panel (5S) ----------
out.append(rect("xBg", WHITE, 0, 118, W, 1018))
out.append(label("xSec", SEC + '.Section', 16, Y0, W - 32, 40, size=18, bold=True, color=DARK, font="Georgia"))
out.append(image("xStd", 'LookUp(colStdPh, StepNo = varSec).Thumbnail.Large', 16, Y0 + 44, 296, 190))
out.append(label("xStdL", '"STANDARD"', 16, Y0 + 210, 296, 24, size=9, bold=True, color=WHITE, align="Center", fill="RGBA(0, 72, 81, 0.75)"))
out.append(image("xPh", 'LookUp(colPhotos, Key = "F" & varSec).Ph', 328, Y0 + 44, 296, 190, extra={"Visible": F(f'varPanel = "def" && {SEC}.HasPh'), "Fill": F(CLEAR)}))
out.append(ctrl("addD", "AddMedia@2.2.1", {"X": "=328", "Y": F(str(Y0 + 44)), "Width": "=296", "Height": "=190", "Size": "=13",
   "Text": F('If(' + SEC + '.HasPh, "", "📷  PHOTO OF WHAT YOU SEE (required)")'),
   "Fill": F(f'If({SEC}.HasPh, {CLEAR}, {YEL})'), "Color": F(TEAL_D), "BorderColor": F(G5), "BorderThickness": "=1",
   "OnChange": F('RemoveIf(colPhotos, Key = "F" & varSec); Collect(colPhotos, {Key: "F" & varSec, No: varSec, Kind: "5S", Ph: Self.Media}); Patch(colSec, ' + SEC + ', {HasPh: true})')}))
out.append(label("xNow", '"NOW (tap to retake)"', 328, Y0 + 210, 296, 24, size=9, bold=True, color=WHITE, align="Center", fill="RGBA(207, 34, 46, 0.8)",
   extra={"Visible": F(f'varPanel = "def" && {SEC}.HasPh')}))
out.append(label("xGood", '"GOOD LOOKS LIKE:  " & ' + SEC + '.Good', 16, Y0 + 240, W - 32, 70, size=12, bold=True, color=DARK, fill=LGREEN,
   extra={"PaddingLeft": "=10", "PaddingRight": "=10"}))
out.append(cap("xC1", "WHICH 5S PILLAR FAILED?  (required)", 16, Y0 + 318, W - 32, color=TEAL_D))
PILL = [("Sort", "SORT"), ("Set in order", "SET"), ("Shine", "SHINE"), ("Standardize", "STD"), ("Sustain", "SUST")]
for i, (v, t) in enumerate(PILL):
    sel = f'{SEC}.Pillar = "{v}"'
    out.append(btn(f"xP{i}", f'"{t}"', f'Patch(colSec, {SEC}, {{Pillar: "{v}"}})', 16 + i * 122, Y0 + 338, 114, 50,
       fill=f'If({sel}, {TEAL_D}, {WHITE})', color=f'If({sel}, {WHITE}, {TEAL_D})', size=13, extra=outline(TEAL_D)))
out.append(label("xPHint", 'Switch(' + SEC + '.Pillar, "Sort", "Unneeded items, red-tag candidates, hoarding, broken or expired items", "Set in order", "No home or label, shadow board gaps, no FIFO, wrong height, no min/max, unclear return", "Shine", "Dirt or build-up, no cleaning schedule, blocked drains/vents, pests, hidden inspection points", "Standardize", "No visual instruction, inconsistent colors, no standard photo, unclear ownership, abnormal not obvious", "Sustain", "No sign of prior checks, operator can\'t explain the standard, no improvement tracking, does not recover", "")',
   16, Y0 + 392, W - 32, 44, size=10, color=G9))
out.append(cap("xC2", "WHAT IS DIFFERENT FROM THE STANDARD?  (required)", 16, Y0 + 440, W - 32, color=TEAL_D))
out.append(ti("txtDef", SEC + '.Finding', 16, Y0 + 460, W - 32, 90, 'Patch(colSec, ' + SEC + ', {Finding: Self.Text})', hint='"e.g. 3 empty outlines, no sign-out tag"', size=14, number=False,
   extra={"Align": "=Align.Left", "Mode": "=TextMode.MultiLine", "Fill": F(f'If(IsBlank(Self.Text), {YEL}, {WHITE})')}))
out.append(btn("xSafe", 'If(' + SEC + '.SafetyRel, "☑  SAFETY HAZARD TOO (goes to FMEA / severity)", "☐  ALSO A SAFETY HAZARD?")', 'Patch(colSec, ' + SEC + ', {SafetyRel: !' + SEC + '.SafetyRel, Sev: If(' + SEC + '.SafetyRel, "", ' + SEC + '.Sev)})',
   16, Y0 + 560, W - 32, 52, fill=f'If({SEC}.SafetyRel, {YEL}, {WHITE})', color=DARK, size=13, extra=outline(AMBER)))
for i, (s, c, hint) in enumerate(SEVS):
    col = {"Critical": RED, "High": ORANGE, "Medium": AMBER, "Low": GREEN}[s]
    sel = f'{SEC}.Sev = "{s}"'
    out.append(btn(f"xSev{c}", f'"{c}"', f'Patch(colSec, {SEC}, {{Sev: "{s}", Act: If("{s}" = "Critical" || "{s}" = "High", true, {SEC}.Act)}})', 16 + i * 152, Y0 + 620, 144, 50,
       fill=f'If({sel}, {col}, {WHITE})', color=f'If({sel}, {WHITE}, {col})', size=20,
       extra={"BorderColor": F(col), "BorderThickness": "=3", **RAD, "Visible": F(f'varPanel = "def" && {SEC}.SafetyRel')}))
out.append(btn("xAct", 'If(' + SEC + '.Act, "☑  ADD TO NEWSPAPER", "☐  ADD TO NEWSPAPER")', 'Patch(colSec, ' + SEC + ', {Act: !' + SEC + '.Act})', 16, Y0 + 682, W - 32, 52, fill=WHITE, color=TEAL_D, size=14, extra=outline(TEAL_D)))
XOK = f'With({{s: {SEC}}}, !{DEFINC.replace("IsBlank(Trim(s.Finding))", "IsBlank(Trim(txtDef.Text))")})'
out.append(btn("xDone", f'If({XOK}, "DONE ›", "PILLAR + WHAT\'S DIFFERENT + PHOTO")', 'Patch(colSec, ' + SEC + ', {Finding: txtDef.Text}); Set(varPanel, Blank())', 16, Y0 + 746, W - 32, 76,
   fill=f'If({XOK}, {TEAL_D}, {G1})', color=f'If({XOK}, {WHITE}, {G9})', size=17,
   extra={"DisplayMode": F(f'If({XOK}, DisplayMode.Edit, DisplayMode.Disabled)'), "DisabledFill": F(G1), "DisabledColor": F(G9), **RAD}))
out.append(btn("xUndo", '"Meets standard after all: clear"', 'Patch(colSec, ' + SEC + ', {Rating: "", Finding: "", HasPh: false, SafetyRel: false, Sev: ""}); RemoveIf(colPhotos, Key = "F" & varSec); Set(varPanel, Blank())',
   16, Y0 + 834, W - 32, 50, fill=WHITE, color=G9, size=12, extra={"BorderColor": F(WHITE)}))
PN("def", "xBg", "xSec", "xStd", "xStdL", "addD", "xGood", "xC1", "xP0", "xP1", "xP2", "xP3", "xP4", "xPHint", "xC2", "txtDef", "xSafe", "xAct", "xDone", "xUndo")

# ---------------- interact ----------------
QS = ["What's the most hazardous thing about working here?", "What part of your body is most tired at the end of the shift?",
      "If you could change one thing here, what would it be?", "Has anyone had a close call here recently?"]
out.append(label("iT", '"INTERACT"', 16, Y1 + 4, 300, 40, size=18, bold=True, color=DARK, font="Georgia"))
out.append(label("iHint", '"Required. Introduce yourself; you are a guest. Systems, not blame. Ask all four, listen more than you talk."', 16, Y1 + 44, W - 32, 44, size=10, color=G9))
out.append(cap("iC0", "OPERATOR (name or role)  (required)", 16, Y1 + 90, W - 32, color=TEAL_D))
out.append(ti("txtOp", '""', 16, Y1 + 110, W - 32, 48, 'false', hint='"e.g. Line 209 lead, maintenance tech"', size=14, number=False,
   extra={"Align": "=Align.Left", "Fill": F(f'If(IsBlank(Self.Text), {YEL}, {WHITE})')}))
for i, q in enumerate(QS):
    y = Y1 + 166 + i * 128
    out.append(label(f"iQ{i}", f'"{i + 1}.  {q}"', 16, y, W - 32, 40, size=12, bold=True, color=DARK))
    out.append(ti(f"txtQ{i}", '""', 16, y + 40, W - 32, 78, 'false', hint='"their words"', size=13, number=False,
       extra={"Align": "=Align.Left", "Mode": "=TextMode.MultiLine", "Fill": F(f'If(IsBlank(Self.Text), {YEL}, {WHITE})')}))
yc = Y1 + 166 + 4 * 128
out.append(cap("iC5", "HOW OPEN WAS THE CONVERSATION?  1 = guarded · 5 = engaged", 16, yc, W - 32, color=TEAL_D))
for k in range(1, 6):
    sel = f'varComfort = {k}'
    out.append(btn(f"iCf{k}", f'"{k}"', f'Set(varComfort, {k})', 16 + (k - 1) * 122, yc + 20, 114, 50, fill=f'If({sel}, {TEAL_D}, {WHITE})', color=f'If({sel}, {WHITE}, {TEAL_D})', size=18, extra=outline(TEAL_D)))
OKI = 'Len(Trim(txtOp.Text)) > 0 && Len(Trim(txtQ0.Text)) > 0 && Len(Trim(txtQ1.Text)) > 0 && Len(Trim(txtQ2.Text)) > 0 && Len(Trim(txtQ3.Text)) > 0 && varComfort > 0'
out.append(btn("btnINext", f'If({OKI}, "RECORD ›", "OPERATOR, 4 ANSWERS, COMFORT")', 'Set(varStep, "record")', 16, yc + 84, W - 32, 72,
   fill=f'If({OKI}, {TEAL_D}, {G1})', color=f'If({OKI}, {WHITE}, {G9})', size=17,
   extra={"DisplayMode": F(f'If({OKI}, DisplayMode.Edit, DisplayMode.Disabled)'), "DisabledFill": F(G1), "DisabledColor": F(G9), **RAD}))
P("interact", "iT", "iHint", "iC0", "txtOp", *[f"iQ{i}" for i in range(4)], *[f"txtQ{i}" for i in range(4)], "iC5", *[f"iCf{k}" for k in range(1, 6)], "btnINext")

# ---------------- record ----------------
NS = 'CountRows(Filter(colAns, Rating = "S"))'; NAR = 'CountRows(Filter(colAns, Rating = "AR"))'; NU = 'CountRows(Filter(colAns, Rating = "U"))'; NNA = 'CountRows(Filter(colAns, Rating = "N/A"))'
SAFEPCT = f'If({NS} + {NAR} + {NU} = 0, 1, {NS} / ({NS} + {NAR} + {NU}))'
NOK = 'CountRows(Filter(colSec, Rating = "OK"))'; NDEF = 'CountRows(Filter(colSec, Rating = "Deficient"))'
ALLSEV = 'Ungroup(Table({t: ForAll(Filter(colAns, Rating = "AR" || Rating = "U"), {S: Sev})}, {t: ForAll(Filter(colSec, Rating = "Deficient" && SafetyRel), {S: Sev})}), t)'
TOP = f'With({{v: {ALLSEV}}}, If(CountRows(Filter(v, S = "Critical")) > 0, "Critical", CountRows(Filter(v, S = "High")) > 0, "High", CountRows(Filter(v, S = "Medium")) > 0, "Medium", CountRows(Filter(v, S = "Low")) > 0, "Low", "None"))'
NACT = 'CountRows(Filter(colAns, (Rating = "AR" || Rating = "U") && Act)) + CountRows(Filter(colSec, Rating = "Deficient" && Act))'
out.append(label("rT", '"RECORD"', 16, Y1 + 4, 300, 40, size=18, bold=True, color=DARK, font="Georgia"))
out.append(label("rPct", 'Text(' + SAFEPCT + ' * 100, "0") & "% SAFE"', 16, Y1 + 50, 300, 90, size=34, bold=True, color=WHITE, align="Center",
   fill=f'If({SAFEPCT} >= 0.95, {GREEN}, {SAFEPCT} >= 0.85, {AMBER}, {RED})'))
out.append(label("rTop", '"TOP SEVERITY" & Char(10) & Upper(' + TOP + ')', 328, Y1 + 50, W - 344, 90, size=18, bold=True, color=WHITE, align="Center", fill=sevcol(TOP)))
out.append(label("rCounts", '"Safety:  " & ' + NS + ' & " S  ·  " & ' + NAR + ' & " AR  ·  " & ' + NU + ' & " U  ·  " & ' + NNA + ' & " N/A" & Char(10) & "5S:  " & ' + NOK + ' & " meet  ·  " & ' + NDEF + ' & " deficient" & Char(10) & ' + NACT + ' & " NEWSPAPER action(s) will be created"',
   16, Y1 + 148, W - 32, 96, size=13, bold=True, color=DARK, fill=MUTE, extra={"PaddingLeft": "=12"}))
out.append(cap("rC1", "CLOSE THE LOOP: DID YOU TELL THE OPERATOR WHAT YOU SAW AND WHAT HAPPENS NEXT?", 16, Y1 + 256, W - 32, color=TEAL_D))
LOOPS = ["On the spot", "Within 24 hours", "Pending", "Not done"]
for i, v in enumerate(LOOPS):
    sel = f'varLoop = "{v}"'
    col = RED if v == "Not done" else TEAL_D
    out.append(btn(f"rL{i}", f'"{v.upper()}"', f'Set(varLoop, "{v}")', 16 + (i % 2) * 308, Y1 + 278 + (i // 2) * 60, 300, 52,
       fill=f'If({sel}, {col}, {WHITE})', color=f'If({sel}, {WHITE}, {col})', size=14, extra=outline(col)))
out.append(cap("rC2", "FOLLOW-UP DATE", 16, Y1 + 404, 300, color=TEAL_D))
out.append(dd("dpFollow", 'ForAll(Sequence(14) As n, {Value: Text(DateAdd(Today(), n.Value, TimeUnit.Days), "ddd m/d"), D: DateAdd(Today(), n.Value, TimeUnit.Days)})', 16, Y1 + 424, 300, 50, size=15))
for n in ["rC2", "dpFollow"]: EXTRA.setdefault(n, {})["Visible"] = F('varStep = "record" && IsBlank(varPanel) && (varLoop = "Within 24 hours" || varLoop = "Pending")')
out.append(cap("rC3", "KEY CONCERN THE OPERATOR RAISED  (required)", 16, Y1 + 484, W - 32, color=TEAL_D))
out.append(ti("txtConcern", '""', 16, Y1 + 504, W - 32, 70, 'false', hint='"in one line"', size=14, number=False,
   extra={"Align": "=Align.Left", "Mode": "=TextMode.MultiLine", "Fill": F(f'If(IsBlank(Self.Text), {YEL}, {WHITE})')}))
out.append(cap("rC4", "AUDITOR NOTES  (optional)", 16, Y1 + 582, W - 32))
out.append(ti("txtNotes", '""', 16, Y1 + 602, W - 32, 70, 'false', hint='"follow-ups, context"', size=13, number=False, extra={"Align": "=Align.Left", "Mode": "=TextMode.MultiLine"}))
SEVW = 'Switch(@, "Critical", "C", "High", "H", "Medium", "M", "Low", "L", "")'
SUBMIT = ('IfError(\n'
 ' Set(varAud, Patch(SAF_Audits, Defaults(SAF_Audits), {\n'
 '   Ref: "FA-" & varZone.ZoneID & "-" & Text(Now(), "yyyymmdd-hhmmss"), ZoneID: varZone.ZoneID, ZoneName: varZone.ZoneName, ZoneType: varZone.ZoneType,\n'
 '   Line: varZone.Line, Area: varZone.Area, AuditDate: Today(), Shift: ' + SHIFT + ', Classification: {Value: ddClass.Selected.Value},\n'
 '   AuditedBy: User().Email, AuditorName: User().FullName, WhyZone: txtWhy.Text, FirstLook: txtStop.Text, StartedAt: varStart, CompletedAt: Now(),\n'
 f'   NS: {NS}, NAR: {NAR}, NU: {NU}, NNA: {NNA}, SafePct: {SAFEPCT}, N5SOK: {NOK}, N5SDef: {NDEF}, StandardID: varStdID,\n'
 f'   TopSeverity: {{Value: {TOP}}}, OperatorRole: txtOp.Text, Q1: txtQ0.Text, Q2: txtQ1.Text, Q3: txtQ2.Text, Q4: txtQ3.Text, Comfort: varComfort,\n'
 '   KeyConcern: txtConcern.Text, LoopMethod: {Value: varLoop}, FollowUpDate: If(varLoop = "Within 24 hours" || varLoop = "Pending", dpFollow.Selected.D, Blank()), Notes: txtNotes.Text}));\n'
 ' ForAll(colAns As a, Patch(SAF_Results, Defaults(SAF_Results), {Ref: varAud.Ref & "-S" & a.ItemNo, AuditID: varAud.ID, ZoneID: varZone.ZoneID, Line: varZone.Line, AuditDate: Today(),\n'
 '   Kind: {Value: "Safety"}, ItemNo: a.ItemNo, Category: a.Category, Item: a.Item, Rating: {Value: a.Rating},\n'
 '   Severity: If((a.Rating = "AR" || a.Rating = "U") && !IsBlank(a.Sev), {Value: a.Sev}, Blank()), Finding: a.Finding, ImmediateAction: a.Imm,\n'
 '   ActionCreated: (a.Rating = "AR" || a.Rating = "U") && a.Act, NewspaperRef: If((a.Rating = "AR" || a.Rating = "U") && a.Act, varAud.Ref & "-S" & a.ItemNo, ""), ZoneOwnerEmail: varZone.OwnerEmail}));\n'
 ' ForAll(colSec As s, Patch(SAF_Results, Defaults(SAF_Results), {Ref: varAud.Ref & "-F" & s.ElNo, AuditID: varAud.ID, ZoneID: varZone.ZoneID, Line: varZone.Line, AuditDate: Today(),\n'
 '   Kind: {Value: "5S"}, ItemNo: s.ElNo, ElementID: s.ElementID, Category: "5S", Item: s.Section, Rating: {Value: s.Rating},\n'
 '   Pillar: If(s.Rating = "Deficient" && !IsBlank(s.Pillar), {Value: s.Pillar}, Blank()), Severity: If(s.Rating = "Deficient" && s.SafetyRel && !IsBlank(s.Sev), {Value: s.Sev}, Blank()),\n'
 '   SafetyRelevant: s.Rating = "Deficient" && s.SafetyRel, Finding: s.Finding, ActionCreated: s.Rating = "Deficient" && s.Act,\n'
 '   NewspaperRef: If(s.Rating = "Deficient" && s.Act, varAud.Ref & "-F" & s.ElNo, ""), ZoneOwnerEmail: varZone.OwnerEmail}));\n'
 ' ForAll(Filter(colAns, (Rating = "AR" || Rating = "U") && Act) As a, Patch(Newspaper, Defaults(Newspaper), {\n'
 '   Action: Left("FRONTIER " & ' + SEVW.replace("@", "a.Sev") + ' & ": " & a.Item & " at " & varZone.ZoneName & " | " & a.Finding, 250), Line: varZone.Line,\n'
 '   SQDCP: {Value: "Safety"}, Source: {Value: "Frontier audit"}, Owner: varZone.Owner, OwnerEmail: varZone.OwnerEmail,\n'
 '   Problem: "Frontier audit " & varAud.Ref & " (" & varZone.ZoneID & "), item " & a.ItemNo & " " & a.Item & ", " & a.Rating & ", " & a.Sev & ": " & a.Finding & If(IsBlank(a.Imm), "", Char(10) & "Immediate action: " & a.Imm),\n'
 '   RaisedDate: Today(), DueDate: DateAdd(Today(), ' + due("a.Sev") + ', TimeUnit.Days), Status: {Value: "Open"}, Progress: 0, RefKey: varAud.Ref & "-S" & a.ItemNo}));\n'
 ' ForAll(Filter(colSec, Rating = "Deficient" && Act) As s, Patch(Newspaper, Defaults(Newspaper), {\n'
 '   Action: Left("FRONTIER 5S " & s.Pillar & If(s.SafetyRel, " (" & ' + SEVW.replace("@", "s.Sev") + ' & ")", "") & ": " & s.Section & " at " & varZone.ZoneName & " | " & s.Finding, 250), Line: varZone.Line,\n'
 '   SQDCP: {Value: If(s.SafetyRel, "Safety", "Quality")}, Source: {Value: "Frontier audit"}, Owner: varZone.Owner, OwnerEmail: varZone.OwnerEmail,\n'
 '   Problem: "Frontier audit " & varAud.Ref & " (" & varZone.ZoneID & "), 5S section " & s.Section & " does not meet " & Coalesce(varStd.DocNo, "the 5S standard") & " (" & s.Pillar & "): " & s.Finding,\n'
 '   RaisedDate: Today(), DueDate: DateAdd(Today(), If(s.SafetyRel, ' + due("s.Sev") + ', Coalesce(Value(LookUp(colCfg, Setting = "SAF_DueDays_5S").SettingValue), 30)), TimeUnit.Days),\n'
 '   Status: {Value: "Open"}, Progress: 0, RefKey: varAud.Ref & "-F" & s.ElNo}));\n'
 ' ForAll(colPhotos As p, Patch(TS_Photos, LookUp(TS_Photos, ID = Value(' + FLOW + '.Run({contentBytes: p.Ph, name: "fa.jpg"}, varAud.Ref & "-" & p.Key & ".jpg",\n'
 '    varAud.ID, If(p.Kind = "5S", 100 + p.No, p.No), 0, "Finding",\n'
 '    Left(If(p.Kind = "5S", "5S " & LookUp(colSec, ElNo = p.No).Section & ": " & LookUp(colSec, ElNo = p.No).Finding, LookUp(colAns, ItemNo = p.No).Item & ": " & LookUp(colAns, ItemNo = p.No).Finding), 250), User().Email).photoid)),\n'
 '    {Module: {Value: "Frontier audit"}, RefID: varAud.ID})),\n'
 ' Notify("NOT SUBMITTED: " & FirstError.Message & "  (check signal, try again)", NotificationType.Error),\n'
 ' Set(varDoneTop, ' + TOP + '); Set(varDoneActs, ' + NACT + '); Set(varDonePct, ' + SAFEPCT + '); Set(varStep, "done"); Select(btnFRefresh))')
OKR = '!IsBlank(varLoop) && Len(Trim(txtConcern.Text)) > 0'
out.append(btn("btnSubmit", f'If({OKR}, "SUBMIT AUDIT", "CLOSE THE LOOP + KEY CONCERN")', SUBMIT, 16, Y1 + 690, W - 32, 80,
   fill=f'If({OKR}, {TEAL_D}, {G1})', color=f'If({OKR}, {WHITE}, {G9})', size=19,
   extra={"DisplayMode": F(f'If({OKR}, DisplayMode.Edit, DisplayMode.Disabled)'), "DisabledFill": F(G1), "DisabledColor": F(G9), **RAD}))
P("record", "rT", "rPct", "rTop", "rCounts", "rC1", "rL0", "rL1", "rL2", "rL3", "rC3", "txtConcern", "rC4", "txtNotes", "btnSubmit")

# ---------------- done ----------------
out.append(rect("dnCard", sevcol('varDoneTop'), 40, Y0 + 40, W - 80, 440))
out.append(label("dnPct", 'Text(varDonePct * 100, "0") & "% SAFE"', 40, Y0 + 90, W - 80, 110, size=48, bold=True, color=WHITE, align="Center", font="Georgia"))
out.append(label("dnSub", 'If(varDoneTop = "None", "No safety findings. ", "Top severity: " & Upper(varDoneTop) & ". ") & varDoneActs & " action(s) added to NEWSPAPER." & If(varDoneTop = "Critical", Char(10) & Char(10) & "CRITICAL: make sure work is stopped and the area is safe. The safety coordinator and zone owner get a Teams alert.", "")',
   60, Y0 + 210, W - 120, 250, size=15, bold=True, color=WHITE, align="Center"))
out.append(btn("btnDnNext", '"NEXT ZONE"', 'Set(varStep, "zone"); Set(varZone, Blank())', 16, Y0 + 510, W - 32, 76, fill=TEAL_D, color=WHITE, size=18, extra=RAD))
P("done", "dnCard", "dnPct", "dnSub", "btnDnNext")

# ---------------- start an audit: load items, the zone's 5S standard + photos ----------------
GEN5S = ('Table({ElNo: 1, Section: "Sort", Good: "Only what this area needs is here. No red-tag candidates, hoarding, personal items or broken/expired items.", P: "Sort"},\n'
         '      {ElNo: 2, Section: "Set in order", Good: "Everything has a labeled home, shadow boards complete, FIFO dates, min/max visible, obvious return path.", P: "Set in order"},\n'
         '      {ElNo: 3, Section: "Shine", Good: "Clean for its function. Cleaning schedule posted and followed; drains, vents and inspection points clear; no pests.", P: "Shine"},\n'
         '      {ElNo: 4, Section: "Standardize", Good: "Visual instructions and standard-condition photo posted; colors consistent; owner named; abnormal is obvious at a glance.", P: "Standardize"},\n'
         '      {ElNo: 5, Section: "Sustain", Good: "Evidence of recent checks; operators can explain the standard; improvements tracked; area recovers after disruption.", P: "Sustain"})')
START = ('Set(varStdID, Coalesce(varZone.StandardID, 0));\n'
 'Set(varStd, If(varStdID > 0, LookUp(SW_Standards, ID = varStdID), Blank()));\n'
 'If(varStdID > 0, IfError(ClearCollect(colEl, Sort(Filter(SW_Elements, StandardID = varStdID), ElementNo)), Notify("Could not load the 5S standard sections", NotificationType.Warning)), Clear(colEl));\n'
 'ClearCollect(colStdPh, If(varStdID > 0, Filter(TS_Photos, Module.Value = "Standard work" && RefID = varStdID)));\n'
 'ClearCollect(colAns, ForAll(colItems As i, {ItemNo: i.ItemNo, Category: i.Category.Value, Item: i.Check, LookFor: i.LookFor, Rating: "", Sev: "", Finding: "", Imm: "", HasPh: false, Act: true}));\n'
 'ClearCollect(colSec, If(CountRows(Filter(colEl, Coalesce(Active, true))) > 0,\n'
 '   ForAll(Filter(colEl, Coalesce(Active, true)) As e, {ElNo: e.ElementNo, ElementID: e.ID, Section: e.Element, Good: e.GoodLooksLike, Pillar: "", Rating: "", Finding: "", HasPh: false, SafetyRel: e.PointType.Value = "Safety", Sev: "", Act: true}),\n'
 '   ForAll(' + GEN5S + ' As g, {ElNo: g.ElNo, ElementID: 0, Section: g.Section, Good: g.Good, Pillar: g.P, Rating: "", Finding: "", HasPh: false, SafetyRel: false, Sev: "", Act: true})));\n'
 'If(CountRows(Filter(colEl, Coalesce(Active, true))) = 0, Set(varStdID, 0));\n'
 'Clear(colPhotos); Set(varComfort, 0); Set(varLoop, ""); Set(varPanel, Blank()); Set(varStart, Now());\n'
 'Reset(txtWhy); Reset(txtStop); Reset(txtOp); Reset(txtQ0); Reset(txtQ1); Reset(txtQ2); Reset(txtQ3); Reset(txtConcern); Reset(txtNotes); Reset(ddClass);\n'
 'If(CountRows(colAns) = 0, Notify("SAF_Items is empty. Run the list setup again.", NotificationType.Error), Set(varStep, "decide"))')
HELP = {"Color": F(CLEAR), "BorderColor": F(CLEAR), "HoverFill": F(CLEAR), "PressedFill": F(CLEAR), "TabIndex": "=-1"}
out.append(btn("btnFStart", '""', START, 0, 1135, 1, 1, fill=CLEAR, color=CLEAR, extra=HELP))
out.append(label("lblLoaded", 'If(IsBlank(varLoaded), "Not loaded: tap ↻", "Loaded " & Text(varLoaded, "h:mm AM/PM"))', 16, 1104, W - 32, 26, size=10, color=G5, align="Center",
   extra={"Visible": F('IsBlank(varPanel)')}))
'''
for _ in range(2):
    out = []
    exec(BODY)
write_themed(OUT, "".join(out))
print("ok", len(out), OUT)
