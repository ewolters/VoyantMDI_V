# MDI Settings app: 6 screens editing the lists the other MDI apps read.
# Screen1 ESCALATION · scrDrop DROPDOWN LISTS · scrLines LINES & VALUE STREAMS · scrStd STANDARDS · scrCfg THRESHOLDS & LINKS · scrPeople PEOPLE
import sys
exec(open(__import__("os").environ["MDI_GEN"]+"/settings_helpers.py").read())
VER = sys.argv[1] if len(sys.argv) > 1 else "1"
import os
OUTD = os.environ.get("SETOUT", __import__("os").environ["MDI_OUTDIR"]+"/")
LIGHT = "RGBA(244, 245, 245, 1)"; SEL = "RGBA(229, 243, 243, 1)"
I = 6
ED = 'If(varCan, DisplayMode.Edit, DisplayMode.Disabled)'
SCREENS = [("Screen1", "ESCALATION"), ("scrDrop", "DROPDOWN LISTS"), ("scrLines", "LINES & VALUE STREAMS"),
           ("scrStd", "STANDARDS"), ("scrCfg", "THRESHOLDS & LINKS"), ("scrPeople", "PEOPLE")]
ME = ('Set(varMe, LookUp(People, Lower(Email) = Lower(User().Email)));\n'
      'Set(varNoAdmin, CountRows(Filter(People, MDIAdmin = true)) = 0);\n'
      'Set(varAdm, Coalesce(varMe.MDIAdmin, false) || varNoAdmin);\n'
      'Set(varCan, Coalesce(varMe.CanEditConfig, false) || varAdm)')
def SAVE(patch, load, ok="Saved"):
    return f'IfError({patch},\n Notify("NOT SAVED: " & FirstError.Message, NotificationType.Error),\n Notify("{ok}", NotificationType.Success); Select({load}))'

def gal(name, items, x, y, w, h, size, kids, onselect, selexpr):
    p = {"Items": F(items), "TemplateSize": F(str(size)), "TemplatePadding": "=0", "ShowScrollbar": "=true",
         "OnSelect": F(onselect), "TemplateFill": F(f'If({selexpr}, {SEL}, {WHITE})'), "BorderColor": F(G1), "BorderThickness": "=1"}
    p.update(box(x, y, w, h))
    return ctrl(name, "Gallery@2.15.0", p, 0, kids, variant="BrowseLayout_Vertical_TwoTextOneImageVariant_ver5.0")
def gl(name, text, x, w, size=12, bold=False, color=DARK, align=None, h=None, y=0, extra=None, fill=None):
    return label(name, text, x, y, w, h or 44, size=size, bold=bold, color=color, align=align, indent=I, extra=extra, fill=fill)
def txt(name, default, x, y, w, h=44, hint='""', number=False, size=13, extra=None):
    e = {"Align": "=Align.Left", "DisplayMode": F(ED)}
    if extra: e.update(extra)
    return ti(name, default, x, y, w, h, "false", hint=hint, size=size, number=number, extra=e)
def tog(name, var, text, x, y, w, h=40, disp=ED):
    return btn(name, f'If({var}, "✓  " & {text}, {text})', f'Set({var}, !{var})', x, y, w, h, size=11,
               fill=f'If({var}, {TEAL_D}, {WHITE})', color=f'If({var}, {WHITE}, {G9})',
               extra={"BorderColor": F(G5), "BorderThickness": "=1", "DisplayMode": F(disp)})
def hdr(pfx, cur, load):
    o = [rect(f"{pfx}HdrBar", DARK, 0, 0, 1920, 90),
         label(f"{pfx}Brand", '"voyant"', 24, 6, 170, 52, size=34, color=WHITE, font="Georgia"),
         label(f"{pfx}BrandSub", '"NEW ALBANY"', 27, 56, 170, 24, size=10, bold=True, color=TEAL),
         label(f"{pfx}Title", '"MDI SETTINGS"', 190, 20, 420, 50, size=26, bold=True, color=WHITE, font="Georgia", extra={"Wrap": "=false"}),
         label(f"{pfx}Badge", 'If(varNoAdmin, "SETUP MODE: nobody is an MDI admin yet. Open PEOPLE and tick MDI ADMIN on yourself.", varCan, "EDITOR  ·  " & User().FullName, "VIEW ONLY  ·  ask an MDI admin to tick CAN EDIT SETTINGS for you")',
               1000, 10, 900, 70, size=13, bold=True, align="Right", extra={"Color": F(f'If(varNoAdmin, {AMBER}, varCan, {AQUA}, {G5})')}),
         rect(f"{pfx}SubBar", LIGHT, 0, 90, 1920, 52)]
    for i, (scr, t) in enumerate(SCREENS):
        on = scr == cur
        o.append(btn(f"{pfx}Tab{i}", f'"{t}"', f'Navigate({scr}, ScreenTransition.None)', 12 + i * 312, 96, 304, 40, size=12,
                     fill=TEAL_D if on else WHITE, color=WHITE if on else TEAL_D, extra={"BorderColor": F(TEAL_D), "BorderThickness": "=1"}))
    o.append(btn(f"{pfx}Load", '"↻"', load, 1880, 98, 36, 36, size=14, fill=WHITE, color=TEAL_D,
                 extra={"Tooltip": '="Reload from SharePoint"', "BorderColor": F(G5), "BorderThickness": "=1"}))
    return o
def write(fname, out):
    write_themed(OUTD + fname, "".join(out)); print("wrote", fname)

# =============================== ESCALATION (Screen1) ===============================
out = hdr("e", "Screen1", ME + ';\nClearCollect(colEsc, Escalation_Contacts);\nClearCollect(colCfg, MDI_Config);\nSet(varELoaded, Now())')
out.append(label("eIntro", '"Each contact gets a Teams/e-mail alert when ONE downtime reason on ONE line and shift adds up to their LEVEL (minutes). Typical: 60 = first level, 120 = second, 240 = third. Retire someone by turning ACTIVE off: never delete."',
                 16, 148, 1888, 44, size=12, color=G9))
out.append(rect("eSetBg", LIGHT, 16, 196, 1888, 84))
out.append(cap("ecFirst", "FIRST LEVEL (MINUTES)", 32, 202, 220)); out.append(txt("eFirst", 'Coalesce(LookUp(colCfg, Title = "Escalation_FirstLevelMin").SettingValue, "60")', 32, 224, 200, number=True))
out.append(cap("ecAlert", "SEND FLOW-FAILURE ALERTS TO (E-MAIL, ; BETWEEN)", 260, 202, 520)); out.append(txt("eAlert", 'Coalesce(LookUp(colCfg, Title = "Alert_Email").SettingValue, "")', 260, 224, 640, hint='"name@company.com"'))
SETPATCH = lambda key, val, kind: f'Patch(MDI_Config, Coalesce(LookUp(MDI_Config, Title = "{key}"), Defaults(MDI_Config)), {{Title: "{key}", SettingValue: {val}, Kind: {{Value: "{kind}"}}}})'
out.append(btn("eSetSave", '"SAVE SETTINGS"', SAVE(SETPATCH("Escalation_FirstLevelMin", "eFirst.Text", "Threshold") + ';\n ' + SETPATCH("Alert_Email", "eAlert.Text", "Other"), "eLoad", "Settings saved"),
               930, 224, 200, 44, size=13, fill=TEAL_D, color=WHITE, extra={"DisplayMode": F(ED)}))
out.append(tog("eAll", "varEAll", '"SHOW RETIRED"', 1720, 228, 170))
# list
LX, LW, LY = 16, 1100, 292
for i, (t, x, w) in enumerate([("LEVEL", 0, 90), ("NAME", 100, 260), ("ROLE", 370, 220), ("E-MAIL", 600, 300), ("SHIFTS", 910, 110), ("", 1030, 60)]):
    out.append(label(f"eh{i}", f'"{t}"', LX + x, LY, w, 30, size=10, bold=True, color=G9))
ESEL = 'Set(varE, ThisItem); Set(varESS, Coalesce(ThisItem.ShiftSpecific, false)); Set(varES1, "1" in ThisItem.Shifts.Value); Set(varES2, "2" in ThisItem.Shifts.Value); Set(varES3, "3" in ThisItem.Shifts.Value); Set(varEA, Coalesce(ThisItem.Active, false))'
kids = [gl("geLvl", 'Text(ThisItem.Level) & " min"', 0, 90, size=13, bold=True, color=WHITE, align="Center", y=6, h=36, fill=f'Switch(ThisItem.Level, 60, {AMBER}, 120, RGBA(219, 109, 40, 1), {RED})'),
        gl("geName", 'ThisItem.Title', 100, 260, bold=True), gl("geRole", 'ThisItem.Role', 370, 220, color=G9),
        gl("geMail", 'ThisItem.Email', 600, 300, size=11, color=G9),
        gl("geSh", 'If(ThisItem.ShiftSpecific, "shift " & Concat(ThisItem.Shifts, Value, ", "), "all shifts")', 910, 110, size=11),
        gl("geAct", 'If(ThisItem.Active, "", "retired")', 1030, 60, size=10, color=RED)]
out.append(gal("galE", 'SortByColumns(Filter(colEsc, varEAll || Active), "Level", SortOrder.Ascending, "Title", SortOrder.Ascending)', LX, LY + 32, LW, 1070 - LY - 32, 48, kids, ESEL, "ThisItem.ID = varE.ID"))
# form
FX, FW = 1132, 772
out.append(rect("eFormBg", LIGHT, FX, LY, FW, 778))
out.append(label("eFormT", 'If(IsBlank(varE.ID), "NEW CONTACT", "EDIT CONTACT")', FX + 16, LY + 8, 500, 36, size=16, bold=True, color=TEAL_D))
y = LY + 56
for nm, capt, dflt, hint in [("eName", "NAME", 'Coalesce(varE.Title, "")', '"First Last"'), ("eMail", "E-MAIL (MUST MATCH THEIR MICROSOFT LOGIN)", 'Coalesce(varE.Email, "")', '"name@company.com"'),
                             ("eRole", "ROLE", 'Coalesce(varE.Role, "")', '"Maintenance Manager"')]:
    out.append(cap(nm + "C", capt, FX + 16, y, 600)); out.append(txt(nm, dflt, FX + 16, y + 22, FW - 32, hint=hint)); y += 80
out.append(cap("eLvlC", "LEVEL: MINUTES OF DOWNTIME (ONE REASON, ONE SHIFT) BEFORE THIS PERSON IS ALERTED", FX + 16, y, 700))
out.append(txt("eLvl", 'If(IsBlank(varE.Level), "60", Text(varE.Level))', FX + 16, y + 22, 160, number=True))
y += 80
out.append(cap("eShC", "SHIFTS", FX + 16, y, 300))
out.append(btn("eShAll", 'If(varESS, "ONLY THESE SHIFTS  →", "✓  ALL SHIFTS")', 'Set(varESS, !varESS)', FX + 16, y + 22, 240, 40, size=11,
               fill=f'If(varESS, {WHITE}, {TEAL_D})', color=f'If(varESS, {G9}, {WHITE})', extra={"BorderColor": F(G5), "BorderThickness": "=1", "DisplayMode": F(ED)}))
for j in (1, 2, 3):
    out.append(tog(f"eSh{j}", f"varES{j}", f'"SHIFT {j}"', FX + 270 + (j - 1) * 130, y + 22, 120, disp=f'If(varCan && varESS, DisplayMode.Edit, DisplayMode.Disabled)'))
y += 80
out.append(tog("eAct", "varEA", '"ACTIVE (GETS ALERTS)"', FX + 16, y, 260))
y += 70
EREC = ('{Title: eName.Text, Email: Trim(eMail.Text), Role: eRole.Text, Level: Value(eLvl.Text), ShiftSpecific: varESS,\n'
        '  Shifts: ForAll(Filter(Table({V: "1", On: varES1}, {V: "2", On: varES2}, {V: "3", On: varES3}), On), {Value: V}), Active: varEA}')
out.append(btn("eSave", '"SAVE CONTACT"',
               'If(IsBlank(eName.Text) || IsBlank(eMail.Text) || !IsNumeric(eLvl.Text), Notify("Name, e-mail and a level in minutes are required.", NotificationType.Warning),\n'
               + SAVE(f'Patch(Escalation_Contacts, If(IsBlank(varE.ID), Defaults(Escalation_Contacts), LookUp(Escalation_Contacts, ID = varE.ID)), {EREC})', "eLoad", "Contact saved") + ')',
               FX + 16, y, 240, 50, size=14, fill=TEAL_D, color=WHITE, extra={"DisplayMode": F(ED)}))
out.append(btn("eNew", '"+ NEW CONTACT"', 'Set(varE, Blank()); Set(varESS, false); Set(varES1, false); Set(varES2, false); Set(varES3, false); Set(varEA, true); Reset(eName); Reset(eMail); Reset(eRole); Reset(eLvl)',
               FX + 272, y, 220, 50, size=13, fill=WHITE, color=TEAL_D, extra={"BorderColor": F(TEAL_D), "BorderThickness": "=1", "DisplayMode": F(ED)}))
out.append(label("eNote", '"The HxH - Downtime Escalation flow reads this list on every save. Changes apply to the next alert."', FX + 16, y + 64, FW - 32, 50, size=10, color=G9))
write(f"Settings_Escalation_v{VER}.pa.yaml", out)

# =============================== DROPDOWN LISTS (scrDrop) ===============================
CATS = [("Downtime", "Hour x Hour: DT1 / DT2 reason. EquipType links a reason to troubleshooting."),
        ("Scrap", "Hour x Hour: primary scrap / defect reason"),
        ("Speed loss", "Hour x Hour: reason running below target speed"),
        ("Extra headcount", "Hour x Hour: reason for extra crew"),
        ("Rework", "Quality: rework reasons (the big buttons)"),
        ("Equipment", "TS Maintenance and TS Binder: machine types"),
        ("NCR defect", "Quality: NCR defect type")]
out = hdr("d", "scrDrop", ME + ';\nClearCollect(colLk, Lookups);\nIf(IsBlank(varCat), Set(varCat, "Downtime"))')
for i, (c, _) in enumerate(CATS):
    out.append(btn(f"dCat{i}", f'"{c.upper()}"', f'Set(varCat, "{c}"); Set(varL, Blank())', 16 + i * 214, 150, 206, 44, size=12,
                   fill=f'If(varCat = "{c}", {TEAL}, {WHITE})', color=DARK, extra={"BorderColor": F(G5), "BorderThickness": "=1"}))
out.append(label("dUse", 'Switch(varCat, ' + ", ".join(f'"{c}", "{u}"' for c, u in CATS) + ', "")', 16, 198, 1300, 34, size=12, bold=True, color=TEAL_D))
out.append(tog("dAll", "varDAll", '"SHOW RETIRED"', 1720, 196, 170))
DLIST = 'SortByColumns(Filter(colLk, Category.Value = varCat && (varDAll || Active)), "SortOrder", SortOrder.Ascending)'
DALL = 'SortByColumns(Filter(colLk, Category.Value = varCat), "SortOrder", SortOrder.Ascending)'
LY = 240
for i, (t, x, w) in enumerate([("ORDER", 0, 110), ("LABEL (WHAT PEOPLE PICK)", 120, 380), ("GROUP", 510, 160), ("HELP", 680, 330), ("", 1020, 70)]):
    out.append(label(f"dh{i}", f'"{t}"', 16 + x, LY, w, 30, size=10, bold=True, color=G9))
SWAP = lambda cmp, pick: (f'With({{o: {pick}(Filter({DALL}, SortOrder {cmp} ThisItem.SortOrder))}},\n If(!IsBlank(o.ID),\n'
                          '  Patch(Lookups, LookUp(Lookups, ID = ThisItem.ID), {SortOrder: o.SortOrder});\n'
                          '  Patch(Lookups, LookUp(Lookups, ID = o.ID), {SortOrder: ThisItem.SortOrder});\n  Select(dLoad)))')
kids = [btn("gdUp", '"▲"', SWAP("<", "Last"), 0, 6, 50, 34, size=11, fill=WHITE, color=TEAL_D, indent=I, extra={"BorderColor": F(G5), "BorderThickness": "=1", "DisplayMode": F(ED)}),
        btn("gdDn", '"▼"', SWAP(">", "First"), 56, 6, 50, 34, size=11, fill=WHITE, color=TEAL_D, indent=I, extra={"BorderColor": F(G5), "BorderThickness": "=1", "DisplayMode": F(ED)}),
        gl("gdLbl", 'ThisItem.Title', 120, 380, bold=True), gl("gdGrp", 'Coalesce(ThisItem.Group, "")', 510, 160, color=G9),
        gl("gdHelp", 'Coalesce(ThisItem.Help, "") & If(IsBlank(ThisItem.EquipType), "", "  [" & ThisItem.EquipType & "]")', 680, 330, size=10, color=G9),
        gl("gdAct", 'If(ThisItem.Active, "", "retired")', 1020, 70, size=10, color=RED)]
DSEL = 'Set(varL, ThisItem); Set(varLA, Coalesce(ThisItem.Active, false))'
out.append(gal("galD", DLIST, 16, LY + 32, 1100, 1070 - LY - 32, 46, kids, DSEL, "ThisItem.ID = varL.ID"))
out.append(rect("dFormBg", LIGHT, FX, LY, FW, 830))
out.append(label("dFormT", 'If(IsBlank(varL.ID), "NEW " & Upper(varCat) & " REASON", "EDIT " & Upper(varCat) & " REASON")', FX + 16, LY + 8, FW - 32, 36, size=16, bold=True, color=TEAL_D))
y = LY + 56
for nm, capt, dflt, hint in [("dLbl", "LABEL (WHAT PEOPLE PICK)", 'Coalesce(varL.Title, "")', '"Machine - Filler"'), ("dGrp", "GROUP (OPTIONAL, FOR REPORTS)", 'Coalesce(varL.Group, "")', '"Machine"'),
                             ("dHelp", "HELP (SHOWN AS A HINT)", 'Coalesce(varL.Help, "")', '""')]:
    out.append(cap(nm + "C", capt, FX + 16, y, 600)); out.append(txt(nm, dflt, FX + 16, y + 22, FW - 32, hint=hint)); y += 80
out.append(cap("dEqC", "EQUIPMENT TYPE (DOWNTIME ONLY: LINKS TO TROUBLESHOOTING)", FX + 16, y, 600))
out.append(dd("dEq", 'Ungroup(Table({t: Table({Value: ""})}, {t: ForAll(SortByColumns(Filter(colLk, Category.Value = "Equipment" && Active), "SortOrder", SortOrder.Ascending), {Value: Title})}), t)',
              FX + 16, y + 22, 360, 44, default='Coalesce(varL.EquipType, "")', size=13, extra={"DisplayMode": F(f'If(varCan && varCat = "Downtime", DisplayMode.Edit, DisplayMode.Disabled)')}))
y += 80
out.append(tog("dAct", "varLA", '"ACTIVE (SHOWS IN THE APPS)"', FX + 16, y, 300))
y += 70
DREC = '{Title: Trim(dLbl.Text), Category: {Value: varCat}, Group: dGrp.Text, Help: dHelp.Text, EquipType: If(varCat = "Downtime", dEq.Selected.Value, Coalesce(varL.EquipType, "")), Active: varLA,\n  SortOrder: If(IsBlank(varL.ID), Coalesce(Max(Filter(colLk, Category.Value = varCat), SortOrder), 0) + 10, varL.SortOrder)}'
out.append(btn("dSave", '"SAVE REASON"',
               'If(IsBlank(Trim(dLbl.Text)), Notify("A label is required.", NotificationType.Warning),\n'
               ' !IsBlank(LookUp(colLk, Category.Value = varCat && Lower(Title) = Lower(Trim(dLbl.Text)) && ID <> Coalesce(varL.ID, -1))), Notify("That label is already in " & varCat & ".", NotificationType.Warning),\n'
               + SAVE(f'Patch(Lookups, If(IsBlank(varL.ID), Defaults(Lookups), LookUp(Lookups, ID = varL.ID)), {DREC})', "dLoad", "Reason saved") + ')',
               FX + 16, y, 240, 50, size=14, fill=TEAL_D, color=WHITE, extra={"DisplayMode": F(ED)}))
out.append(btn("dNew", '"+ NEW REASON"', 'Set(varL, Blank()); Set(varLA, true); Reset(dLbl); Reset(dGrp); Reset(dHelp); Reset(dEq)',
               FX + 272, y, 220, 50, size=13, fill=WHITE, color=TEAL_D, extra={"BorderColor": F(TEAL_D), "BorderThickness": "=1", "DisplayMode": F(ED)}))
out.append(label("dNote", '"Renaming changes the choice from now on; records already saved keep the old wording. To stop using a reason, turn ACTIVE off (history stays readable). Use ▲ ▼ to set the order people see. New reasons go to the bottom."',
                 FX + 16, y + 64, FW - 32, 110, size=10, color=G9))
write(f"Settings_Dropdowns_v{VER}.pa.yaml", out)

# =============================== LINES & VALUE STREAMS (scrLines) ===============================
out = hdr("l", "scrLines", ME + ';\nClearCollect(colLn, Lines);\nClearCollect(colVS, ValueStreams)')
PW = 940; LXs = [16, 16 + PW + 8]
# --- lines (left)
out.append(label("lLnT", '"LINES"', 16, 148, 300, 36, size=16, bold=True, color=TEAL_D))
out.append(tog("lAll", "varLnAll", '"SHOW RETIRED"', 16 + PW - 170, 148, 170))
for i, (t, x, w) in enumerate([("LINE", 0, 150), ("VALUE STREAM", 160, 360), ("ORDER", 530, 100), ("", 640, 100)]):
    out.append(label(f"lh{i}", f'"{t}"', 16 + x, 188, w, 26, size=10, bold=True, color=G9))
kids = [gl("glLn", 'ThisItem.Title', 0, 150, size=14, bold=True), gl("glVS", 'Coalesce(ThisItem.ValueStream, "(none)")', 160, 360, color=G9),
        gl("glOrd", 'Text(ThisItem.DisplayOrder)', 530, 100, color=G9), gl("glAct", 'If(ThisItem.Active, "", "retired")', 640, 100, size=10, color=RED)]
out.append(gal("galLn", 'SortByColumns(Filter(colLn, varLnAll || Active), "DisplayOrder", SortOrder.Ascending, "Title", SortOrder.Ascending)', 16, 216, PW, 500, 44, kids,
               'Set(varLn, ThisItem); Set(varLnA, Coalesce(ThisItem.Active, false))', "ThisItem.ID = varLn.ID"))
out.append(rect("lLnFormBg", LIGHT, 16, 726, PW, 344))
out.append(label("lLnFormT", 'If(IsBlank(varLn.ID), "NEW LINE", "EDIT LINE " & varLn.Title)', 32, 732, 600, 34, size=14, bold=True, color=TEAL_D))
out.append(cap("lLnNC", "LINE (AS PEOPLE SAY IT: 209)", 32, 772, 300)); out.append(txt("lLnN", 'Coalesce(varLn.Title, "")', 32, 794, 200))
out.append(cap("lLnVC", "VALUE STREAM", 250, 772, 300))
out.append(dd("lLnV", 'Ungroup(Table({t: Table({Value: ""})}, {t: ForAll(SortByColumns(Filter(colVS, Active), "DisplayOrder", SortOrder.Ascending), {Value: Title})}), t)', 250, 794, 400, 44,
              default='Coalesce(varLn.ValueStream, "")', size=13, extra={"DisplayMode": F(ED)}))
out.append(cap("lLnOC", "ORDER ON BOARDS", 670, 772, 200)); out.append(txt("lLnO", 'If(IsBlank(varLn.DisplayOrder), "", Text(varLn.DisplayOrder))', 670, 794, 140, number=True))
out.append(tog("lLnAct", "varLnA", '"ACTIVE"', 32, 852, 160))
LNREC = '{Title: Trim(lLnN.Text), ValueStream: lLnV.Selected.Value, DisplayOrder: If(IsNumeric(lLnO.Text), Value(lLnO.Text), Blank()), Active: varLnA}'
out.append(btn("lLnSave", '"SAVE LINE"',
               'If(IsBlank(Trim(lLnN.Text)), Notify("A line name is required.", NotificationType.Warning),\n !IsBlank(LookUp(colLn, Title = Trim(lLnN.Text) && ID <> Coalesce(varLn.ID, -1))), Notify("That line already exists.", NotificationType.Warning),\n'
               + SAVE(f'Patch(Lines, If(IsBlank(varLn.ID), Defaults(Lines), LookUp(Lines, ID = varLn.ID)), {LNREC})', "lLoad", "Line saved") + ')',
               32, 906, 200, 48, size=13, fill=TEAL_D, color=WHITE, extra={"DisplayMode": F(ED)}))
out.append(btn("lLnNew", '"+ NEW LINE"', 'Set(varLn, Blank()); Set(varLnA, true); Reset(lLnN); Reset(lLnV); Reset(lLnO)', 248, 906, 180, 48, size=12, fill=WHITE, color=TEAL_D,
               extra={"BorderColor": F(TEAL_D), "BorderThickness": "=1", "DisplayMode": F(ED)}))
out.append(label("lLnNote", '"Renaming a line does not rename it in past board entries or the PLAYBOOK: add a new line and retire the old one instead. Products and rates for a line are on STANDARDS."',
                 32, 962, PW - 32, 90, size=10, color=G9))
# --- value streams (right)
RX = LXs[1]
out.append(label("lVsT", '"VALUE STREAMS  (TIER 3 ROWS)"', RX, 148, 500, 36, size=16, bold=True, color=TEAL_D))
for i, (t, x, w) in enumerate([("VALUE STREAM", 0, 260), ("PART OF", 270, 220), ("LEADER", 500, 250), ("ORDER", 760, 80), ("", 850, 80)]):
    out.append(label(f"lvh{i}", f'"{t}"', RX + x, 188, w, 26, size=10, bold=True, color=G9))
kids = [gl("gvN", 'ThisItem.Title', 0, 260, size=13, bold=True), gl("gvP", 'If(IsBlank(ThisItem.ParentVS), "(top level)", ThisItem.ParentVS)', 270, 220, color=G9),
        gl("gvL", 'Coalesce(ThisItem.Leader, "")', 500, 250, color=G9), gl("gvO", 'Text(ThisItem.DisplayOrder)', 760, 80, color=G9),
        gl("gvA", 'If(ThisItem.Active, "", "retired")', 850, 80, size=10, color=RED)]
out.append(gal("galVS", 'SortByColumns(colVS, "DisplayOrder", SortOrder.Ascending, "Title", SortOrder.Ascending)', RX, 216, PW, 500, 44, kids,
               'Set(varVs, ThisItem); Set(varVsA, Coalesce(ThisItem.Active, false))', "ThisItem.ID = varVs.ID"))
out.append(rect("lVsFormBg", LIGHT, RX, 726, PW, 344))
out.append(label("lVsFormT", 'If(IsBlank(varVs.ID), "NEW VALUE STREAM", "EDIT " & Upper(varVs.Title))', RX + 16, 732, 600, 34, size=14, bold=True, color=TEAL_D))
out.append(cap("lVsNC", "NAME (MATCHES THE LINES' VALUE STREAM)", RX + 16, 772, 400)); out.append(txt("lVsN", 'Coalesce(varVs.Title, "")', RX + 16, 794, 300))
out.append(cap("lVsPC", "PART OF (BLANK = TOP LEVEL)", RX + 336, 772, 300))
out.append(dd("lVsP", 'Ungroup(Table({t: Table({Value: ""})}, {t: ForAll(Filter(colVS, IsBlank(ParentVS) && Title <> Coalesce(varVs.Title, "") && Active), {Value: Title})}), t)', RX + 336, 794, 300, 44,
              default='Coalesce(varVs.ParentVS, "")', size=13, extra={"DisplayMode": F(ED)}))
out.append(cap("lVsOC", "ORDER", RX + 656, 772, 120)); out.append(txt("lVsO", 'If(IsBlank(varVs.DisplayOrder), "", Text(varVs.DisplayOrder))', RX + 656, 794, 120, number=True))
out.append(cap("lVsLC", "LEADER", RX + 16, 850, 300)); out.append(txt("lVsL", 'Coalesce(varVs.Leader, "")', RX + 16, 872, 300))
out.append(cap("lVsEC", "LEADER E-MAIL", RX + 336, 850, 300)); out.append(txt("lVsE", 'Coalesce(varVs.LeaderEmail, "")', RX + 336, 872, 440))
out.append(tog("lVsAct", "varVsA", '"ACTIVE"', RX + 16, 930, 160))
VSREC = '{Title: Trim(lVsN.Text), ParentVS: lVsP.Selected.Value, Leader: lVsL.Text, LeaderEmail: Trim(lVsE.Text), DisplayOrder: If(IsNumeric(lVsO.Text), Value(lVsO.Text), Blank()), Active: varVsA}'
out.append(btn("lVsSave", '"SAVE VALUE STREAM"',
               'If(IsBlank(Trim(lVsN.Text)), Notify("A name is required.", NotificationType.Warning),\n'
               + SAVE(f'Patch(ValueStreams, If(IsBlank(varVs.ID), Defaults(ValueStreams), LookUp(ValueStreams, ID = varVs.ID)), {VSREC})', "lLoad", "Value stream saved") + ')',
               RX + 200, 926, 240, 48, size=13, fill=TEAL_D, color=WHITE, extra={"DisplayMode": F(ED)}))
out.append(btn("lVsNew", '"+ NEW VALUE STREAM"', 'Set(varVs, Blank()); Set(varVsA, true); Reset(lVsN); Reset(lVsP); Reset(lVsO); Reset(lVsL); Reset(lVsE)', RX + 456, 926, 240, 48, size=12,
               fill=WHITE, color=TEAL_D, extra={"BorderColor": F(TEAL_D), "BorderThickness": "=1", "DisplayMode": F(ED)}))
out.append(label("lVsNote", '"A value stream with PART OF set is a vertical under that value stream on Tier 3. Renaming does not rename it on the lines: change each line\'s VALUE STREAM too."',
                 RX + 16, 982, PW - 32, 70, size=10, color=G9))
write(f"Settings_Lines_v{VER}.pa.yaml", out)

# =============================== STANDARDS / PLAYBOOK (scrStd) ===============================
HC = [("Line Lead", "LINE LEAD"), ("Filler Machine Operator", "FILLER OP"), ("Case Pack Machine Operator", "CASE PACK OP"), ("Bottle / Cap Feeder", "BOTTLE/CAP FEEDER"),
      ("Box Maker", "BOX MAKER"), ("Packer", "PACKER"), ("Palletizer", "PALLETIZER"), ("Inspector", "INSPECTOR"), ("Bottle Flipper", "BOTTLE FLIPPER"),
      ("Tube Feeder", "TUBE FEEDER"), ("Partition Placer (211 and 209)", "PARTITION PLACER"), ("Taper Machine Pusher", "TAPER PUSHER"), ("Unscrambler Inspector", "UNSCRAMBLER INSP")]
q = lambda n: "'" + n + "'" if (" " in n or "/" in n or "(" in n) else n
out = hdr("s", "scrStd", ME + ';\nClearCollect(colPB, PLAYBOOK);\nClearCollect(colSLn, Lines)')
out.append(cap("sFLC", "LINE", 16, 150, 160))
out.append(dd("sFL", 'Ungroup(Table({t: Table({Value: "All lines"})}, {t: Sort(Distinct(colPB, Line), Value)}), t)', 16, 172, 200, 44, size=13))
out.append(cap("sFSC", "SEARCH SIZE OR FORM", 232, 150, 300)); out.append(ti("sFS", '""', 232, 172, 300, 44, "false", hint='"10 oz, wash…"', size=13, number=False, extra={"Align": "=Align.Left"}))
out.append(tog("sAll", "varSAll", '"SHOW RETIRED"', 946, 174, 170))
SLIST = ('SortByColumns(Filter(colPB, (sFL.Selected.Value = "All lines" || Line = sFL.Selected.Value) && (IsBlank(sFS.Text) || sFS.Text in Size || sFS.Text in Form) && (varSAll || Active)),'
         ' "Line", SortOrder.Ascending, "Size", SortOrder.Ascending, "Form", SortOrder.Ascending)')
for i, (t, x, w) in enumerate([("LINE", 0, 80), ("SIZE", 90, 200), ("FORM", 300, 240), ("RATE BPM", 550, 110), ("UNITS / HR", 670, 130), ("CREW", 810, 80), ("", 900, 100)]):
    out.append(label(f"sh{i}", f'"{t}"', 16 + x, 222, w, 26, size=10, bold=True, color=G9))
kids = [gl("gsL", 'ThisItem.Line', 0, 80, bold=True), gl("gsS", 'ThisItem.Size', 90, 200), gl("gsF", 'ThisItem.Form', 300, 240),
        gl("gsR", 'Text(ThisItem.Rate)', 550, 110, align="Right"), gl("gsU", "Text(Value(ThisItem.'Playbook Units per Hour'), \"#,##0\")", 670, 130, align="Right", color=G9),
        gl("gsC", "Text(Value(ThisItem.'Total HC'))", 810, 80, align="Right", color=G9), gl("gsA", 'If(ThisItem.Active, "", "retired")', 900, 100, size=10, color=RED)]
SSEL = 'Set(varP, ThisItem); Set(varPA, Coalesce(ThisItem.Active, false))'
out.append(gal("galS", SLIST, 16, 250, 1100, 820, 42, kids, SSEL, "ThisItem.ID = varP.ID"))
out.append(rect("sFormBg", LIGHT, FX, 150, FW, 920))
out.append(label("sFormT", 'If(IsBlank(varP.ID), "NEW PRODUCT STANDARD", "LINE " & varP.Line & "  ·  " & varP.Size & " | " & varP.Form)', FX + 16, 156, FW - 32, 36, size=15, bold=True, color=TEAL_D))
out.append(cap("sLC", "LINE", FX + 16, 198, 140))
out.append(dd("sL", 'ForAll(SortByColumns(Filter(colSLn, Active), "DisplayOrder", SortOrder.Ascending), {Value: Title})', FX + 16, 220, 140, 44, default='Coalesce(varP.Line, "")', size=13, extra={"DisplayMode": F(ED)}))
out.append(cap("sSC", "SIZE", FX + 172, 198, 200)); out.append(txt("sS", 'Coalesce(varP.Size, "")', FX + 172, 220, 220, hint='"10 oz"'))
out.append(cap("sFC", "FORM", FX + 408, 198, 300)); out.append(txt("sF", 'Coalesce(varP.Form, "")', FX + 408, 220, FW - 424, hint='"Body Wash"'))
NUMS = [("sRate", "RATE (BOTTLES / MIN)", "Rate"), ("sEff", "EFFICIENCY TARGET (0.75 = 75%)", "Playbook Efficiency Target"),
        ("sHrs", "AVAILABLE HRS / SHIFT", "Available Hrs/Shift"), ("sUps", "SCHEDULED UNITS / SHIFT", "units_per_shift")]
for j, (nm, capt, fld) in enumerate(NUMS):
    x = FX + 16 + j * 186
    out.append(cap(nm + "C", capt, x, 276, 180)); out.append(txt(nm, f'If(IsBlank(varP.{q(fld)}), "", Text(varP.{q(fld)}))', x, 298, 170, number=True))
out.append(label("sCalc", "\"UNITS / HR \" & If(IsBlank(varP.ID), \"—\", Text(Value(varP.'Playbook Units per Hour'), \"#,##0\")) & \"   ·   TOTAL CREW \" & If(IsBlank(varP.ID), \"—\", Text(Value(varP.'Total HC'))) & \"   (calculated by SharePoint after save)\"",
                 FX + 16, 350, FW - 32, 30, size=11, bold=True, color=G9))
out.append(label("sHcT", '"CREW BY POSITION (PEOPLE)"', FX + 16, 384, 400, 26, size=11, bold=True, color=TEAL_D))
for j, (fld, capt) in enumerate(HC):
    x = FX + 16 + (j % 4) * 186; yy = 414 + (j // 4) * 72
    out.append(cap(f"sHc{j}C", capt, x, yy, 180)); out.append(txt(f"sHc{j}", f'If(IsBlank(varP.{q(fld)}), "", Text(varP.{q(fld)}))', x, yy + 22, 170, number=True))
yy = 414 + 4 * 72 + 8
out.append(tog("sAct", "varPA", '"ACTIVE (SHOWS IN HOUR x HOUR)"', FX + 16, yy, 320))
NV = lambda c: f'If(IsNumeric({c}.Text), Value({c}.Text), Blank())'
PREC = ('{Title: sL.Selected.Value & "|" & Trim(sS.Text) & "|" & Trim(sF.Text), Line: sL.Selected.Value, Size: Trim(sS.Text), Form: Trim(sF.Text), Active: varPA,\n  '
        + ", ".join(f"{q(fld)}: {NV(nm)}" for nm, _, fld in NUMS) + ",\n  " + ", ".join(f"{q(fld)}: {NV(f'sHc{j}')}" for j, (fld, _) in enumerate(HC)) + "}")
out.append(btn("sSave", '"SAVE STANDARD"',
               'If(IsBlank(sL.Selected.Value) || IsBlank(Trim(sS.Text)) || IsBlank(Trim(sF.Text)) || !IsNumeric(sRate.Text), Notify("Line, size, form and rate are required.", NotificationType.Warning),\n'
               ' !IsBlank(LookUp(colPB, Line = sL.Selected.Value && Size = Trim(sS.Text) && Form = Trim(sF.Text) && ID <> Coalesce(varP.ID, -1))), Notify("That line already has this size and form.", NotificationType.Warning),\n'
               + SAVE(f'Patch(PLAYBOOK, If(IsBlank(varP.ID), Defaults(PLAYBOOK), LookUp(PLAYBOOK, ID = varP.ID)), {PREC})', "sLoad", "Standard saved") + ')',
               FX + 16, yy + 56, 230, 50, size=14, fill=TEAL_D, color=WHITE, extra={"DisplayMode": F(ED)}))
out.append(btn("sCopy", '"COPY AS NEW"', 'Set(varP, Patch(varP, {ID: Blank()})); Notify("Copied: change size or form, then SAVE.", NotificationType.Information)', FX + 262, yy + 56, 200, 50, size=12,
               fill=WHITE, color=TEAL_D, extra={"BorderColor": F(TEAL_D), "BorderThickness": "=1", "DisplayMode": F(f'If(varCan && !IsBlank(varP.ID), DisplayMode.Edit, DisplayMode.Disabled)')}))
out.append(btn("sNew", '"+ NEW"', 'Set(varP, Blank()); Set(varPA, true); Reset(sL); Reset(sS); Reset(sF); ' + "; ".join(f"Reset({nm})" for nm, _, _ in NUMS) + "; " + "; ".join(f"Reset(sHc{j})" for j in range(len(HC))),
               FX + 478, yy + 56, 140, 50, size=12, fill=WHITE, color=TEAL_D, extra={"BorderColor": F(TEAL_D), "BorderThickness": "=1", "DisplayMode": F(ED)}))
out.append(label("sNote", '"Hour x Hour reads RATE, UNITS / HR and TOTAL CREW for the product picked on the board. A rate change applies to hours entered after the next REFRESH; saved hours keep their target."',
                 FX + 16, yy + 116, FW - 32, 60, size=10, color=G9))
write(f"Settings_Standards_v{VER}.pa.yaml", out)

# =============================== THRESHOLDS & LINKS (scrCfg) ===============================
out = hdr("c", "scrCfg", ME + ';\nClearCollect(colCfg, MDI_Config);\nClearCollect(colKM, KPI_Metrics);\nIf(IsBlank(varCMode), Set(varCMode, "S"))')
out.append(btn("cM0", '"SETTINGS & APP LINKS"', 'Set(varCMode, "S")', 16, 150, 300, 44, size=12, fill=f'If(varCMode = "S", {TEAL}, {WHITE})', color=DARK, extra={"BorderColor": F(G5), "BorderThickness": "=1"}))
out.append(btn("cM1", '"TIER 3 METRICS"', 'Set(varCMode, "M")', 324, 150, 300, 44, size=12, fill=f'If(varCMode = "M", {TEAL}, {WHITE})', color=DARK, extra={"BorderColor": F(G5), "BorderThickness": "=1"}))
out.append(btn("cImp", '"IMPORT HISTORY  ▸"', 'Navigate(scrImport, ScreenTransition.None)', 1604, 150, 300, 44, size=12, fill=WHITE, color=TEAL_D,
               extra={"BorderColor": F(TEAL_D), "BorderThickness": "=1", "Tooltip": '="Back-fill Hour x Hour and Tier 2 history from the line data-entry workbooks"'}))
VS_ = 'varCMode = "S"'; VM_ = 'varCMode = "M"'
KINDS = ["All", "Threshold", "App link", "Flow", "Site", "Other"]
for j, k in enumerate(KINDS):
    out.append(btn(f"cK{j}", f'"{k.upper()}"', f'Set(varKind, "{k}")', 650 + j * 140, 152, 132, 40, size=10,
                   fill=f'If(Coalesce(varKind, "All") = "{k}", {TEAL_D}, {WHITE})', color=f'If(Coalesce(varKind, "All") = "{k}", {WHITE}, {TEAL_D})',
                   extra={"BorderColor": F(G5), "BorderThickness": "=1", "Visible": F(VS_)}))
CLIST = 'SortByColumns(Filter(colCfg, (Coalesce(varKind, "All") = "All" || Kind.Value = varKind) && Title <> "Setup_Code"), "Title", SortOrder.Ascending)'
for i, (t, x, w) in enumerate([("SETTING", 0, 300), ("VALUE", 310, 380), ("WHAT IT DOES", 700, 390)]):
    out.append(label(f"ch{i}", f'"{t}"', 16 + x, 204, w, 26, size=10, bold=True, color=G9, extra={"Visible": F(VS_)}))
kids = [gl("gcN", 'ThisItem.Title', 0, 300, bold=True, size=11), gl("gcV", 'Coalesce(ThisItem.SettingValue, "(blank)")', 310, 380, size=11, extra={"Color": F(f'If(IsBlank(ThisItem.SettingValue), {AMBER}, {DARK})')}),
        gl("gcD", 'Coalesce(ThisItem.Notes, "")', 700, 390, size=9, color=G9)]
p = gal("galC", CLIST, 16, 232, 1100, 838, 50, kids, 'Set(varC, ThisItem)', "ThisItem.ID = varC.ID")
out.append(p.replace("    Properties:\n", "    Properties:\n      Visible: =" + VS_ + "\n", 1))
out.append(rect("cFormBg", LIGHT, FX, 204, FW, 866).replace("    Properties:\n", "    Properties:\n      Visible: =" + VS_ + "\n", 1))
out.append(label("cFormT", 'If(IsBlank(varC.ID), "PICK A SETTING", varC.Title)', FX + 16, 212, FW - 32, 36, size=16, bold=True, color=TEAL_D, extra={"Visible": F(VS_)}))
out.append(label("cFormN", 'Coalesce(varC.Notes, "")', FX + 16, 252, FW - 32, 120, size=11, color=G9, extra={"Visible": F(VS_)}))
out.append(cap("cValC", "VALUE", FX + 16, 380, 200).replace("Properties:\n", "Properties:\n      Visible: =" + VS_ + "\n", 1))
out.append(txt("cVal", 'Coalesce(varC.SettingValue, "")', FX + 16, 402, FW - 32, h=150, extra={"Mode": "=TextMode.MultiLine", "Visible": F(VS_),
               "DisplayMode": F('If(varCan && !IsBlank(varC.ID), DisplayMode.Edit, DisplayMode.Disabled)')}))
out.append(label("cHint", 'Switch(varC.Kind.Value, "App link", "Paste the app\'s web link (Power Apps → app → Details → Web link). Add &hidenavbar=true for TVs.", "Threshold", "A number. Boards read it on their next REFRESH.", "Flow", "Leave as installed unless your MDI contact says otherwise.", "")',
                 FX + 16, 560, FW - 32, 50, size=10, color=TEAL_D, extra={"Visible": F(VS_)}))
out.append(btn("cSave", '"SAVE SETTING"', SAVE('Patch(MDI_Config, LookUp(MDI_Config, ID = varC.ID), {SettingValue: Trim(cVal.Text)})', "cLoad", "Setting saved"),
               FX + 16, 620, 240, 50, size=14, fill=TEAL_D, color=WHITE, extra={"DisplayMode": F('If(varCan && !IsBlank(varC.ID), DisplayMode.Edit, DisplayMode.Disabled)'), "Visible": F(VS_)}))
out.append(btn("cOpen", '"OPEN LINK"', 'Launch(cVal.Text)', FX + 272, 620, 200, 50, size=12, fill=WHITE, color=TEAL_D,
               extra={"BorderColor": F(TEAL_D), "BorderThickness": "=1", "Visible": F(VS_ + ' && StartsWith(cVal.Text, "http")')}))
# --- metrics mode
for i, (t, x, w) in enumerate([("", 0, 44), ("METRIC", 54, 380), ("BETTER", 444, 100), ("GREEN", 554, 110), ("AMBER", 674, 110), ("ORDER", 794, 90), ("", 894, 100)]):
    out.append(label(f"cmh{i}", f'"{t}"', 16 + x, 204, w, 26, size=10, bold=True, color=G9, extra={"Visible": F(VM_)}))
LC = 'Switch(ThisItem.Letter.Value, "S", RGBA(207, 34, 46, 1), "Q", RGBA(130, 80, 223, 1), "D", RGBA(9, 105, 218, 1), "C", RGBA(26, 127, 55, 1), RGBA(191, 135, 0, 1))'
kids = [gl("gmL", 'ThisItem.Letter.Value', 0, 44, size=14, bold=True, color=WHITE, align="Center", y=6, h=36, fill=LC),
        gl("gmN", 'ThisItem.MetricName & "  (" & ThisItem.Unit & ")"', 54, 380, bold=True, size=11), gl("gmB", 'ThisItem.Better.Value', 444, 100, color=G9),
        gl("gmG", 'Text(ThisItem.Green)', 554, 110, color=GREEN, bold=True), gl("gmA", 'Text(ThisItem.Amber)', 674, 110, color=AMBER, bold=True),
        gl("gmO", 'Text(ThisItem.DisplayOrder)', 794, 90, color=G9), gl("gmAc", 'If(ThisItem.Active, "", "off")', 894, 100, size=10, color=RED)]
p = gal("galM", 'SortByColumns(AddColumns(colKM, LO, Find(Letter.Value, "SQDCP")), "LO", SortOrder.Ascending, "DisplayOrder", SortOrder.Ascending)', 16, 232, 1100, 838, 48, kids,
        'Set(varM, ThisItem); Set(varMA, Coalesce(ThisItem.Active, false))', "ThisItem.ID = varM.ID")
out.append(p.replace("    Properties:\n", "    Properties:\n      Visible: =" + VM_ + "\n", 1))
out.append(rect("cmFormBg", LIGHT, FX, 204, FW, 866).replace("    Properties:\n", "    Properties:\n      Visible: =" + VM_ + "\n", 1))
out.append(label("cmFormT", 'If(IsBlank(varM.ID), "PICK A METRIC", varM.Letter.Value & "  ·  " & varM.MetricName)', FX + 16, 212, FW - 32, 36, size=16, bold=True, color=TEAL_D, extra={"Visible": F(VM_)}))
out.append(label("cmNotes", 'Coalesce(varM.Notes, "")', FX + 16, 252, FW - 32, 80, size=11, color=G9, extra={"Visible": F(VM_)}))
MV = {"Visible": F(VM_), "DisplayMode": F('If(varCan && !IsBlank(varM.ID), DisplayMode.Edit, DisplayMode.Disabled)')}
for nm, capt, dflt, x, w, num in [("cmName", "NAME ON THE BOARD", 'Coalesce(varM.MetricName, "")', 16, 440, False), ("cmShort", "SHORT LABEL", 'Coalesce(varM.Short, "")', 472, 270, False)]:
    out.append(cap(nm + "C", capt, FX + x, 340, w).replace("Properties:\n", "Properties:\n      Visible: =" + VM_ + "\n", 1)); out.append(txt(nm, dflt, FX + x, 362, w, extra=MV, number=num))
out.append(cap("cmBC", "BETTER WHEN", FX + 16, 420, 200).replace("Properties:\n", "Properties:\n      Visible: =" + VM_ + "\n", 1))
out.append(dd("cmB", '["Higher", "Lower"]', FX + 16, 442, 200, 44, default='Coalesce(varM.Better.Value, "Higher")', size=13, extra=MV))
for nm, capt, fld, x in [("cmG", "GREEN AT", "Green", 232), ("cmA", "AMBER AT", "Amber", 408), ("cmO", "ORDER", "DisplayOrder", 584)]:
    out.append(cap(nm + "C", capt, FX + x, 420, 160).replace("Properties:\n", "Properties:\n      Visible: =" + VM_ + "\n", 1))
    out.append(txt(nm, f'If(IsBlank(varM.{fld}), "", Text(varM.{fld}))', FX + x, 442, 160, number=True, extra=MV))
out.append(label("cmRule", 'If(cmB.Selected.Value = "Higher", "Green when the value is " & cmG.Text & " or more; amber from " & cmA.Text & "; red below that.", "Green when the value is " & cmG.Text & " or less; amber up to " & cmA.Text & "; red above that.")',
                 FX + 16, 496, FW - 32, 40, size=12, bold=True, color=TEAL_D, extra={"Visible": F(VM_)}))
out.append(btn("cmAct", 'If(varMA, "✓  SHOWN ON TIER 3", "HIDDEN ON TIER 3")', 'Set(varMA, !varMA)', FX + 16, 548, 280, 40, size=11, fill=f'If(varMA, {TEAL_D}, {WHITE})', color=f'If(varMA, {WHITE}, {G9})',
               extra={"BorderColor": F(G5), "BorderThickness": "=1", **MV}))
MREC = '{MetricName: cmName.Text, Short: cmShort.Text, Better: {Value: cmB.Selected.Value}, Green: Value(cmG.Text), Amber: Value(cmA.Text), DisplayOrder: If(IsNumeric(cmO.Text), Value(cmO.Text), Blank()), Active: varMA}'
out.append(btn("cmSave", '"SAVE METRIC"', 'If(!IsNumeric(cmG.Text) || !IsNumeric(cmA.Text), Notify("Green and amber must be numbers.", NotificationType.Warning),\n'
               + SAVE(f'Patch(KPI_Metrics, LookUp(KPI_Metrics, ID = varM.ID), {MREC})', "cLoad", "Metric saved") + ')',
               FX + 16, 606, 240, 50, size=14, fill=TEAL_D, color=WHITE, extra=MV))
out.append(label("cmNote", '"Tier 3 calculates each metric; here you only set targets, order and whether it shows. A letter tile shows its worst metric."',
                 FX + 16, 670, FW - 32, 50, size=10, color=G9, extra={"Visible": F(VM_)}))
write(f"Settings_Thresholds_v{VER}.pa.yaml", out)

# =============================== PEOPLE (scrPeople) ===============================
ROLES = ["Operator lead", "Supervisor", "Coordinator", "Ops Manager", "Maintenance", "Maintenance Manager", "QA", "QA Manager", "Compounding", "Director", "GM", "OpEx", "Other"]
out = hdr("p", "scrPeople", ME + ';\nClearCollect(colPpl, People)')
out.append(label("pIntro", '"People drives owners in the Newspaper, who may link downtime on Tier 2, and who may change settings here. SharePoint access follows automatically (MDI - Sync Permissions flow)."',
                 16, 148, 1500, 44, size=12, color=G9))
out.append(cap("pFC", "SEARCH", 16, 194, 200)); out.append(ti("pF", '""', 16, 216, 300, 44, "false", hint='"name, role, line…"', size=13, number=False, extra={"Align": "=Align.Left"}))
out.append(tog("pAll", "varPAll", '"SHOW INACTIVE"', 946, 218, 170))
PLIST = 'SortByColumns(Filter(colPpl, (varPAll || Active) && (IsBlank(pF.Text) || pF.Text in Title || pF.Text in Email || pF.Text in Role.Value || pF.Text in Lines)), "Title", SortOrder.Ascending)'
for i, (t, x, w) in enumerate([("NAME", 0, 260), ("ROLE", 270, 200), ("TIER", 480, 60), ("LINES", 550, 170), ("CAN", 730, 270), ("", 1010, 80)]):
    out.append(label(f"ph{i}", f'"{t}"', 16 + x, 266, w, 26, size=10, bold=True, color=G9))
kids = [gl("gpN", 'ThisItem.Title', 0, 260, bold=True), gl("gpR", 'ThisItem.Role.Value', 270, 200, color=G9), gl("gpT", 'Text(ThisItem.Tier)', 480, 60, color=G9),
        gl("gpL", 'Coalesce(ThisItem.Lines, "all")', 550, 170, size=11, color=G9),
        gl("gpC", 'Concatenate(If(ThisItem.MDIAdmin, "ADMIN  ", ""), If(ThisItem.CanEditConfig, "SETTINGS  ", ""), If(ThisItem.CanLinkDowntime, "LINK DT", ""))', 730, 270, size=10, bold=True, color=TEAL_D),
        gl("gpA", 'If(ThisItem.Active, "", "inactive")', 1010, 80, size=10, color=RED)]
PSEL = ('Set(varPp, ThisItem); Set(varPpA, Coalesce(ThisItem.Active, false)); Set(varPp1, "1" in ThisItem.Shifts.Value); Set(varPp2, "2" in ThisItem.Shifts.Value); Set(varPp3, "3" in ThisItem.Shifts.Value);'
        ' Set(varPpL, Coalesce(ThisItem.CanLinkDowntime, false)); Set(varPpC, Coalesce(ThisItem.CanEditConfig, false)); Set(varPpM, Coalesce(ThisItem.MDIAdmin, false))')
out.append(gal("galP", PLIST, 16, 294, 1100, 776, 46, kids, PSEL, "ThisItem.ID = varPp.ID"))
out.append(rect("pFormBg", LIGHT, FX, 194, FW, 876))
out.append(label("pFormT", 'If(IsBlank(varPp.ID), "NEW PERSON", "EDIT " & Upper(varPp.Title))', FX + 16, 200, FW - 32, 36, size=16, bold=True, color=TEAL_D))
out.append(cap("pNC", "NAME", FX + 16, 242, 300)); out.append(txt("pN", 'Coalesce(varPp.Title, "")', FX + 16, 264, 360))
out.append(cap("pEC", "E-MAIL (THEIR MICROSOFT LOGIN)", FX + 392, 242, 360)); out.append(txt("pE", 'Coalesce(varPp.Email, "")', FX + 392, 264, FW - 408))
out.append(cap("pRC", "ROLE", FX + 16, 320, 300))
out.append(dd("pR", "[" + ", ".join(f'"{r}"' for r in ROLES) + "]", FX + 16, 342, 260, 44, default='Coalesce(varPp.Role.Value, "Supervisor")', size=13, extra={"DisplayMode": F(ED)}))
out.append(cap("pTC", "TIER (1 FLOOR · 2 AREA · 3 PLANT)", FX + 292, 320, 300))
out.append(dd("pT", '["1", "2", "3"]', FX + 292, 342, 120, 44, default='Coalesce(Text(varPp.Tier), "1")', size=13, extra={"DisplayMode": F(ED)}))
out.append(cap("pLC", "LINES (BLANK = ALL; 209, 211)", FX + 428, 320, 320)); out.append(txt("pL", 'Coalesce(varPp.Lines, "")', FX + 428, 342, FW - 444))
out.append(cap("pAC", "AREA", FX + 16, 398, 300)); out.append(txt("pAr", 'Coalesce(varPp.Area, "")', FX + 16, 420, 360))
out.append(cap("pShC", "SHIFTS", FX + 392, 398, 200))
for j in (1, 2, 3):
    out.append(tog(f"pSh{j}", f"varPp{j}", f'"{j}"', FX + 392 + (j - 1) * 80, 420, 70))
out.append(cap("pNoC", "NOTES", FX + 16, 476, 300)); out.append(txt("pNo", 'Coalesce(varPp.Notes, "")', FX + 16, 498, FW - 32, h=80, extra={"Mode": "=TextMode.MultiLine"}))
out.append(label("pPermT", '"PERMISSIONS"', FX + 16, 590, 300, 26, size=11, bold=True, color=TEAL_D))
out.append(tog("pPL", "varPpL", '"CAN LINK DOWNTIME (TIER 2)"', FX + 16, 620, 340))
out.append(tog("pPC", "varPpC", '"CAN EDIT SETTINGS (THIS APP)"', FX + 16, 668, 340, disp='If(varAdm, DisplayMode.Edit, DisplayMode.Disabled)'))
out.append(tog("pPM", "varPpM", '"MDI ADMIN"', FX + 16, 716, 340, disp='If(varAdm, DisplayMode.Edit, DisplayMode.Disabled)'))
out.append(label("pPermN", '"Only an MDI admin can grant settings or admin rights."', FX + 372, 668, FW - 388, 80, size=10, color=G9))
out.append(tog("pAct", "varPpA", '"ACTIVE"', FX + 16, 774, 200))
PPREC = ('{Title: Trim(pN.Text), Email: Trim(pE.Text), Role: {Value: pR.Selected.Value}, Tier: Value(pT.Selected.Value), Lines: pL.Text, Area: pAr.Text, Notes: pNo.Text, Active: varPpA,\n'
         '  Shifts: ForAll(Filter(Table({V: "1", On: varPp1}, {V: "2", On: varPp2}, {V: "3", On: varPp3}), On), {Value: V}),\n'
         '  CanLinkDowntime: varPpL, CanEditConfig: If(varAdm, varPpC, Coalesce(varPp.CanEditConfig, false)), MDIAdmin: If(varAdm, varPpM, Coalesce(varPp.MDIAdmin, false))}')
out.append(btn("pSave", '"SAVE PERSON"',
               'If(IsBlank(Trim(pN.Text)) || IsBlank(Trim(pE.Text)), Notify("Name and e-mail are required.", NotificationType.Warning),\n'
               ' !IsBlank(LookUp(colPpl, Lower(Email) = Lower(Trim(pE.Text)) && ID <> Coalesce(varPp.ID, -1))), Notify("Someone already has that e-mail.", NotificationType.Warning),\n'
               + SAVE(f'Patch(People, If(IsBlank(varPp.ID), Defaults(People), LookUp(People, ID = varPp.ID)), {PPREC})', "pLoad", "Person saved") + ')',
               FX + 16, 830, 240, 50, size=14, fill=TEAL_D, color=WHITE, extra={"DisplayMode": F(ED)}))
out.append(btn("pNew", '"+ NEW PERSON"', 'Set(varPp, Blank()); Set(varPpA, true); Set(varPp1, false); Set(varPp2, false); Set(varPp3, false); Set(varPpL, false); Set(varPpC, false); Set(varPpM, false);'
               ' Reset(pN); Reset(pE); Reset(pR); Reset(pT); Reset(pL); Reset(pAr); Reset(pNo)', FX + 272, 830, 220, 50, size=13, fill=WHITE, color=TEAL_D,
               extra={"BorderColor": F(TEAL_D), "BorderThickness": "=1", "DisplayMode": F(ED)}))
out.append(label("pNote", '"Turn ACTIVE off when someone leaves: never delete, the boards keep their name on old actions."', FX + 16, 892, FW - 32, 40, size=10, color=G9))
write(f"Settings_People_v{VER}.pa.yaml", out)
