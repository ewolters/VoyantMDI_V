# Generates HxH_Board_v10.pa.yaml (1920x1080)
exec(open(__import__("os").environ["MDI_GEN"]+"/theme.py").read())
DARK="RGBA(7, 39, 45, 1)"; TEAL_D="RGBA(0, 72, 81, 1)"; TEAL="RGBA(0, 178, 169, 1)"; AQUA="RGBA(176, 227, 228, 1)"
G9="RGBA(117, 120, 123, 1)"; G5="RGBA(177, 179, 179, 1)"; G1="RGBA(217, 217, 214, 1)"; WHITE="RGBA(255, 255, 255, 1)"
GREEN="RGBA(46, 160, 67, 1)"; MUTE="RGBA(243, 244, 244, 1)"; INK="RGBA(60, 64, 67, 1)"; NOW="RGBA(229, 243, 243, 1)"; AMBER="RGBA(210, 153, 34, 1)"; RED="RGBA(207, 34, 46, 1)"; CLEAR="RGBA(0, 0, 0, 0)"
out=[]
EXTRA={}
exec(open(__import__("os").environ["MDI_GEN"]+"/ux6.py").read())
def ind(s,n): return "\n".join((" "*n+l) if l else l for l in s.split("\n"))
def ctrl(name, ctype, props, indent=0, children=None, variant=None):
    p=" "*indent
    s=f"{p}- {name}:\n{p}    Control: {ctype}\n"
    if variant: s+=f"{p}    Variant: {variant}\n"
    s+=f"{p}    Properties:\n"
    props=dict(props); props.update(EXTRA.get(name, {}))
    for k,v in props.items():
        v=str(v)
        if "\n" in v or ": " in v or "#" in v or v.startswith("=\"") is False and False:
            s+=f"{p}      {k}: |-\n"+ind(v, indent+8)+"\n"
        else:
            s+=f"{p}      {k}: {v}\n"
    if children:
        s+=f"{p}    Children:\n"+"".join(children)
    return s
def F(v): return "="+v
def box(x,y,w,h): return {"X":F(str(x)),"Y":F(str(y)),"Width":F(str(w)),"Height":F(str(h))}
def label(name,text,x,y,w,h,size=12,bold=False,color=DARK,font="Arial",align=None,fill=None,valign=None,pb=None,indent=0,extra=None):
    d={"Text":F(text),"Font":F("Font."+font),"Size":F(str(size)),"Color":F(color)}
    if bold: d["FontWeight"]=F("FontWeight.Bold")
    if align: d["Align"]=F("Align."+align)
    if fill: d["Fill"]=F(fill)
    if valign: d["VerticalAlign"]=F("VerticalAlign."+valign)
    if pb is not None: d["PaddingBottom"]=F(str(pb))
    if extra: d.update(extra)
    d.update(box(x,y,w,h)); return ctrl(name,"Label@2.5.1",d,indent)
def cap(name,text,x,y,w,color=G9,indent=0): return label(name,f'"{text}"',x,y,w,20,size=9,bold=True,color=color,indent=indent)
def dd(name,items,x,y,w,h,default=None,onchange=None,size=14,bold=False,indent=0,extra=None):
    d={"Items":F(items)}
    if default: d["Default"]=F(default)
    if onchange: d["OnChange"]=F(onchange)
    d.update({"Font":F("Font.Arial"),"Size":F(str(size)),
      "ChevronBackground":F(WHITE),"ChevronFill":F(G9),"ChevronHoverBackground":F(G1),"ChevronHoverFill":F(DARK),
      "ChevronDisabledBackground":F(WHITE),"ChevronDisabledFill":F(G1),
      "SelectionFill":F(TEAL_D),"SelectionColor":F(WHITE),"HoverFill":F(AQUA),"PressedFill":F(AQUA),
      "FocusedBorderColor":F(TEAL_D),"HoverBorderColor":F(G9)})
    if bold: d["FontWeight"]=F("FontWeight.Bold")
    if extra: d.update(extra)
    d.update(box(x,y,w,h)); return ctrl(name,"Classic/DropDown@2.3.1",d,indent)
def ti(name,default,x,y,w,h,onchange,hint='""',size=14,bold=False,number=True,indent=0,extra=None):
    d={"Default":F(default),"HintText":F(hint)}
    if number: d["Format"]=F("TextFormat.Number")
    d.update({"Font":F("Font.Arial"),"Size":F(str(size)),"Align":F("Align.Center"),"BorderColor":F(G5),"FocusedBorderColor":F(TEAL_D),"HoverBorderColor":F(G9),"OnChange":F(onchange)})
    if bold: d["FontWeight"]=F("FontWeight.Bold")
    if extra: d.update(extra)
    d.update(box(x,y,w,h)); return ctrl(name,"Classic/TextInput@2.3.2",d,indent)
def btn(name,text,onselect,x,y,w,h,fill=TEAL,color=DARK,size=12,indent=0,extra=None):
    d={"Text":F(text),"OnSelect":F(onselect),"Font":F("Font.Arial"),"Size":F(str(size)),"FontWeight":F("FontWeight.Bold"),
       "Fill":F(fill),"Color":F(color),"HoverFill":F("ColorFade(Self.Fill, -15%)"),"BorderColor":F("Self.Fill")}
    if extra: d.update(extra)
    d.update(box(x,y,w,h)); return ctrl(name,"Classic/Button@2.2.0",d,indent)
def rect(name,fill,x,y,w,h): d={"Fill":F(fill)}; d.update(box(x,y,w,h)); return ctrl(name,"Rectangle@2.3.0",d)

DT_OLD='["", "Machine - Filler", "Machine - Capper", "Machine - Labeler", "Machine - Coder", "Machine - Conveyor", "Machine - Tape machine", "Machine - Print & apply", "Machine - Unscrambler", "Machine - Utilities", "Materials - No Components", "Materials - No Bulk", "Quality Issue - Components", "Quality Issue - Batch", "Quality Issue - Rework", "Quality Issue - Quality Verification", "People - No People", "People - Unskilled Labor", "Other"]'
STAFF='colLkStaff'
SPEED='colLkSpeed'
SCRAP='colLkScrap'
DT_CODES='colLkDT'
TIMES='ForAll(Sequence(48, 0), {Value: Text(Time(0, Value * 30, 0), "h:mm AM/PM"), M: Value * 30})'

# shared summary math (reactive)
SUMW=('With({act: Max(colHours, Coalesce(Cum, 0)), tgt: Sum(colHours, Tgt),\n'
      '      bpm: If(CountRows(Filter(colHours, Coalesce(BPM, 0) > 0)) = 0, Blank(), Average(Filter(colHours, Coalesce(BPM, 0) > 0), BPM)),\n'
      '      avail: varDurM - Coalesce(Value(txtLunch.Text), 0) - Coalesce(Value(txtBreak.Text), 0),\n'
      '      scrap: Coalesce(Value(txtScrap.Text), 0),\n'
      '      rep: Sum(colHours, Coalesce(DT, 0) + Coalesce(DT2, 0))},\n'
      ' With({up: If(Coalesce(bpm, 0) > 0, act / bpm, Blank())},\n'
      '  With({A: If(avail > 0 && !IsBlank(up), up / avail, Blank()),\n'
      '        P: If(varTmax > 0 && Coalesce(bpm, 0) > 0, bpm / varTmax, Blank()),\n'
      '        Q: If(act > 0, 1 - scrap / act, Blank())},\n')
SUMEND=")))"
LAST=('With({last: Max(Filter(colHours, !IsBlank(Cum)), HourNo)},\n'
      ' With({ca: LookUp(colHours, HourNo = last).Cum, ct: Sum(Filter(colHours, HourNo <= last), Tgt)},\n')
LASTEND="))"

ROWSAVE='Set(varRow, LookUp(colHours, HourNo = ThisItem.HourNo));\nSelect(btnSaveRow)'
PH='"— PICK PRODUCT —"'
LINEKEY='If(varProd = '+PH+', "", ddLine.Selected.Value & "|" & varPB.Size & "|" & varPB.Form)'

# ---------- header ----------
out.append(rect("hdrBar",DARK,0,0,1920,90))
out.append(label("lblBrand",'"voyant"',24,6,170,52,size=34,color=WHITE,font="Georgia"))
out.append(label("lblBrandSub",'"NEW ALBANY"',27,56,170,24,size=10,bold=True,color=TEAL))
out.append(label("lblTitle",'"HOUR x HOUR"',190,20,240,50,size=26,bold=True,color=WHITE,font="Georgia"))
out.append(cap("cLine","LINE",440,6,120,color=G5)); out.append(dd("ddLine","Distinct(PLAYBOOK, Line)",440,28,120,52,default='"209"',onchange="Select(btnRefresh)",size=20,bold=True))
out.append(cap("cProd","PRODUCT  (SIZE | FORM)",570,6,340,color=G5))
out.append(dd("ddProduct",'Ungroup(Table({t: Table({Value: '+PH+', Size: "", Form: ""})}, {t: Filter(ForAll(Filter(PLAYBOOK, Line = ddLine.Selected.Value), {Value: Size & " | " & Form, Size: Size, Form: Form}), IsBlank(txtProdFind.Text) || txtProdFind.Text in Value)}), t)',570,28,256,52,
   default='Coalesce(varProdDef, '+PH+')',onchange="If(ddProduct.Selected.Value <> Coalesce(varProd, \"\"), Set(varProd, ddProduct.Selected.Value); Select(btnRefresh))",size=18,
   extra={"Fill":F('If(Coalesce(varProd, '+PH+') = '+PH+', RGBA(255, 236, 179, 1), '+WHITE+')'),"BorderColor":F('If(Coalesce(varProd, '+PH+') = '+PH+', '+AMBER+', '+G5+')')}))
out.append(ti("txtProdFind",'""',830,28,80,52,"Select(btnRefresh)",hint='"find"',size=14,number=False))
out.append(cap("cDate","DATE",920,6,190,color=G5))
out.append(dd("ddDate",'ForAll(Sequence(7, 0, -1), With({d: DateAdd(Today(), Value, TimeUnit.Days)}, {Value: Text(d, "ddd m/d"), D: d}))',920,28,190,52,onchange="Select(btnRefresh)",size=18))
out.append(cap("cShift","SHIFT",1120,6,90,color=G5)); out.append(dd("ddShift",'["1", "2"]',1120,28,90,52,onchange="Select(btnRefresh)",size=20,bold=True))
LOAD=('Select(btnFlush);\n'
 'ClearCollect(colLk, Filter(Lookups, Active = true));\n'
 'ClearCollect(colLkDT, {Value: " ", Help: ""}, ForAll(Sort(Filter(colLk, Category.Value = "Downtime"), SortOrder), {Value: Label, Help: Help}));\n'
 'ClearCollect(colLkScrap, {Value: "", Help: ""}, ForAll(Sort(Filter(colLk, Category.Value = "Scrap"), SortOrder), {Value: Label, Help: Help}));\n'
 'ClearCollect(colLkSpeed, {Value: "", Help: ""}, ForAll(Sort(Filter(colLk, Category.Value = "Speed loss"), SortOrder), {Value: Label, Help: Help}));\n'
 'ClearCollect(colLkStaff, {Value: "", Help: ""}, ForAll(Sort(Filter(colLk, Category.Value = "Extra headcount"), SortOrder), {Value: Label, Help: Help}));\n'
 'Set(varShiftKey, ddLine.Selected.Value & "-" & Text(ddDate.Selected.D, "yyyymmdd") & "-S" & ddShift.Selected.Value);\n'
 'Set(varKey, varShiftKey & "-H");\n'
 'ClearCollect(colRunHist, Filter(HxH_Hourly, Line = ddLine.Selected.Value && ShiftDate >= DateAdd(ddDate.Selected.D, -30, TimeUnit.Days) && ShiftDate <= ddDate.Selected.D));\n'
 'With({h: Filter(colRunHist, ShiftKey <> varShiftKey && Coalesce(RunRatePct, 0) > 0 && RunRatePct < 3 && Coalesce(HourlyTarget, 0) > 0)}, Set(varRunN, CountRows(h)); Set(varRunMean, Average(h, RunRatePct)); Set(varRunSD, StdevP(h, RunRatePct)));\n'
 'Set(varStarCut, If(varRunN >= 20, Max(1.05, varRunMean + 2 * varRunSD), 1.15));\n'
 'Set(varShiftRec, LookUp(HxH_Shift, Title = varShiftKey));\n'
 'If(varShiftKey <> Coalesce(varProdKey, ""), Set(varProdKey, varShiftKey); Set(varProd, If(IsBlank(varShiftRec.ProductForm), '+PH+', varShiftRec.ProductForm)); Set(varProdDef, varProd); Reset(ddProduct));\n'
 'Set(varPB, With({f: First(Filter(PLAYBOOK, Line = ddLine.Selected.Value))}, If(Coalesce(varProd, '+PH+') = '+PH+', f, Coalesce(LookUp(PLAYBOOK, Line = ddLine.Selected.Value && Size & " | " & Form = varProd), f))));\n'
 "Set(varUPH, Coalesce(Value(varPB.'Playbook Units per Hour'), 0));\n"
 'Set(varTmax, Coalesce(varPB.Rate, 0));\n'
 'Set(varStartM, If(IsBlank(varShiftRec.ActualStartTime), If(ddShift.Selected.Value = "1", 360, 990), Hour(TimeValue(varShiftRec.ActualStartTime)) * 60 + Minute(TimeValue(varShiftRec.ActualStartTime))));\n'
 'Set(varEndM, If(IsBlank(varShiftRec.ActualEndTime), If(ddShift.Selected.Value = "1", 990, 180), Hour(TimeValue(varShiftRec.ActualEndTime)) * 60 + Minute(TimeValue(varShiftRec.ActualEndTime))));\n'
 'Set(varDurM, With({d0: ddDate.Selected.D}, With({d1: If(varEndM <= varStartM, DateAdd(d0, 1, TimeUnit.Days), d0)}, DateDiff(DateTime(Year(d0), Month(d0), Day(d0), RoundDown(varStartM / 60, 0), Mod(varStartM, 60), 0), DateTime(Year(d1), Month(d1), Day(d1), RoundDown(varEndM / 60, 0), Mod(varEndM, 60), 0), TimeUnit.Minutes))));\n'
 'Set(varStart, DateTime(Year(ddDate.Selected.D), Month(ddDate.Selected.D), Day(ddDate.Selected.D), RoundDown(varStartM / 60, 0), Mod(varStartM, 60), 0));\n'
 'ClearCollect(colSaved, Filter(HxH_Hourly, StartsWith(Title, varKey)));\n'
 'ClearCollect(colHours,\n'
 '    ForAll(Sequence(Max(12, RoundUp(varDurM / 60, 0))),\n'
 '        With({h: Value},\n'
 '            With({s: LookUp(colSaved, HourNo = h), sm: Max(0, Min(60, varDurM - (h - 1) * 60))},\n'
 '                {HourNo: h,\n'
 '                 StartT: DateAdd(varStart, (h - 1) * 60, TimeUnit.Minutes),\n'
 '                 SlotMin: sm,\n'
 '                 InShift: sm > 0,\n'
 '                 Job: Coalesce(s.Job, ""),\n'
 '                 Cum: s.CumulativeUnits,\n'
 '                 BPM: s.SpeedBPM,\n'
 '                 Planned: Coalesce(s.PlannedMin, 0),\n'
 '                 Tgt: If(sm > 0, Max(0, varUPH * (sm - Coalesce(s.PlannedMin, 0)) / 60), 0),\n'
 '                 DT: s.DT_Minutes,\n'
 '                 Reason: Coalesce(s.DT_Reason, ""),\n'
 '                 DT2: s.DT2_Minutes,\n'
 '                 Reason2: Coalesce(s.DT2_Reason, ""),\n'
 '                 Safety: Coalesce(s.SafetyEvent, false),\n'
 '                 Notes: Coalesce(s.Notes, "")}))));\n'
 'Set(varLoadedAt, Now())')
out.append(btn("btnRefresh",'"REFRESH"',LOAD,1222,28,130,52,size=14,fill=TEAL_D,color=WHITE,extra={"RadiusTopLeft":"=6","RadiusTopRight":"=6","RadiusBottomLeft":"=6","RadiusBottomRight":"=6"}))
out.append(label("lblStd",'If(IsBlank(varPB), "No PLAYBOOK standard", "STD  " & Text(varPB.Rate) & " BPM  ·  " & Text(varUPH, "#,##0") & " /hr" & Char(10) & "Crew " & Text(Value(varPB.\'Total HC\')) & "  ·  Eff " & Text((varPB.\'Playbook Efficiency Target\') * 100, "0") & "%")',
   1548,10,360,70,size=13,bold=True,color=G5,align="Right"))

# ---------- shift strip ----------
SAVESH="Select(btnSaveShift)"
out.append(rect("shiftBar","RGBA(244, 245, 245, 1)",12,96,1528,80))
out.append(cap("cStart","START",20,98,150)); out.append(dd("ddStart",TIMES,20,120,150,48,default='If(IsBlank(varShiftRec.ActualStartTime), If(ddShift.Selected.Value = "1", "6:00 AM", "4:30 PM"), varShiftRec.ActualStartTime)',onchange='If(Self.Selected.Value <> If(IsBlank(varShiftRec.ActualStartTime), If(ddShift.Selected.Value = "1", "6:00 AM", "4:30 PM"), varShiftRec.ActualStartTime),\n    Select(btnSaveShift);\n    Select(btnRefresh))',size=15))
out.append(cap("cEnd","END",178,98,150)); out.append(dd("ddEnd",TIMES,178,120,150,48,default='If(IsBlank(varShiftRec.ActualEndTime), If(ddShift.Selected.Value = "1", "4:30 PM", "3:00 AM"), varShiftRec.ActualEndTime)',onchange='If(Self.Selected.Value <> If(IsBlank(varShiftRec.ActualEndTime), If(ddShift.Selected.Value = "1", "4:30 PM", "3:00 AM"), varShiftRec.ActualEndTime),\n    Select(btnSaveShift);\n    Select(btnRefresh))',size=15))
out.append(cap("cHrs","SHIFT HRS",336,98,90)); out.append(label("lblHrs",'Text(varDurM / 60, "0.0#")',336,120,90,48,size=20,bold=True))
out.append(cap("cLunch","LUNCH MIN",432,98,90)); out.append(ti("txtLunch",'Text(Coalesce(varShiftRec.LunchMin, 30))',432,120,84,48,SAVESH,size=16))
out.append(cap("cBreak","BREAK MIN",524,98,90)); out.append(ti("txtBreak",'Text(Coalesce(varShiftRec.BreakMin, 15))',524,120,84,48,SAVESH,size=16))
out.append(cap("cJob1","JOB 1 (PRIMARY)",616,98,160)); out.append(ti("txtJob1",'Coalesce(varShiftRec.Job1, "")',616,120,160,48,SAVESH,hint='"job #"',size=16,number=False))
out.append(cap("cStdCrew","STD CREW",784,98,90)); out.append(label("lblStdCrew","If(IsBlank(varPB), \"—\", Text(Value(varPB.'Total HC')))",784,120,90,48,size=20,bold=True,align="Center"))
out.append(cap("cCrew","ACTUAL CREW",882,98,110)); out.append(ti("txtCrew",'If(IsBlank(varShiftRec.ActualCrewSize), "", Text(varShiftRec.ActualCrewSize))',882,120,100,48,SAVESH,size=18,bold=True,
   extra={"Fill":F("If(Coalesce(Value(Self.Text), 0) > Value(varPB.'Total HC'), RGBA(253, 236, 200, 1), RGBA(255, 255, 255, 1))")}))
out.append(cap("cStaff","REASON FOR EXTRA HEADCOUNT",990,98,280)); out.append(dd("ddStaff",STAFF,990,120,280,48,default='Coalesce(varShiftRec.StaffingReasonCode, "")',onchange='If(Self.Selected.Value <> Coalesce(varShiftRec.StaffingReasonCode, ""), Select(btnSaveShift))',size=13))
out.append(cap("cPlanChk","PLANNED MIN IN ROWS vs LUNCH + BREAK",1280,98,256))
out.append(label("lblPlanChk",'Text(Sum(colHours, Planned)) & " / " & Text(Coalesce(Value(txtLunch.Text), 0) + Coalesce(Value(txtBreak.Text), 0)) & If(Sum(colHours, Planned) = Coalesce(Value(txtLunch.Text), 0) + Coalesce(Value(txtBreak.Text), 0), "  ✓", "  — mark lunch/break hours")',
   1280,120,256,48,size=13,bold=True,extra={"Color":F(f'If(Sum(colHours, Planned) = Coalesce(Value(txtLunch.Text), 0) + Coalesce(Value(txtBreak.Text), 0), {GREEN}, {AMBER})')}))

# ---------- column headers ----------
COLS=[("HOUR",6,136,None),("JOB",146,80,"Center"),("HR TGT",230,76,"Right"),("CUM TGT",310,86,"Right"),("COUNTER (CUM)",400,130,"Center"),("HR ACT",534,80,"Right"),
      ("RUN %",618,116,"Center"),("+/- CUM",738,70,"Center"),("BPM",812,64,"Center"),("PLAN MIN",880,56,"Center"),("DT1 MIN",940,56,"Center"),
      ("DT1 REASON",1000,160,None),("DT2 MIN",1164,56,"Center"),("DT2 REASON",1224,160,None),("SAFETY",1388,64,"Center"),("NOTES",1456,68,"Center")]
out.append(rect("colHdrBar",MUTE,12,182,1528,36))
for i,(t,x,w,a) in enumerate(COLS):
    out.append(label(f"h{i:02d}",f'"{t}"',12+x,182,w,36,size=10,bold=True,color=G9,align=a))

# ---------- gallery ----------
IN='If(ThisItem.InShift && Coalesce(Value(txtCrew.Text), 0) > 0, DisplayMode.Edit, DisplayMode.Disabled)'
INSAFE='If(ThisItem.InShift, DisplayMode.Edit, DisplayMode.Disabled)'
HRACT='If(IsBlank(ThisItem.Cum), Blank(), ThisItem.Cum - Coalesce(LookUp(colHours, HourNo = ThisItem.HourNo - 1).Cum, 0))'
CUMT='Sum(Filter(colHours, HourNo <= ThisItem.HourNo), Tgt)'
kids=[]
I=6
kids.append(label("gSlot",'If(ThisItem.InShift, Substitute(Substitute(Text(ThisItem.StartT, "h:mm AM/PM"), " AM", ""), " PM", "") & "–" & Text(DateAdd(ThisItem.StartT, ThisItem.SlotMin, TimeUnit.Minutes), "h:mm AM/PM"), Text(ThisItem.StartT, "h:mm AM/PM") & "  off")',
   6,4,136,52,size=13,bold=True,indent=I,extra={"Color":F(f"If(ThisItem.InShift, {DARK}, {G5})")}))
kids.append(ti("gJob",'ThisItem.Job',146,9,80,42,'Patch(colHours, ThisItem, {Job: Self.Text});\n'+ROWSAVE,hint='txtJob1.Text',size=12,number=False,indent=I,extra={"DisplayMode":F(IN)}))
kids.append(label("gTgt",'If(ThisItem.InShift, Text(ThisItem.Tgt, "#,##0"), "")',230,4,76,52,size=15,color=G9,align="Right",indent=I))
kids.append(label("gCumTgt",f'If(ThisItem.InShift, Text({CUMT}, "#,##0"), "")',310,4,86,52,size=15,color=G9,align="Right",indent=I))
kids.append(ti("gCounter",'If(IsBlank(ThisItem.Cum), "", Text(ThisItem.Cum))',400,7,130,46,'Patch(colHours, ThisItem, {Cum: If(IsBlank(Self.Text), Blank(), Value(Self.Text))});\n'+ROWSAVE,
   hint='"counter"',size=20,bold=True,indent=I,extra={"DisplayMode":F(IN),"BorderColor":F(TEAL_D),"BorderThickness":"=2"}))
kids.append(label("gHrAct",f'If(IsBlank(ThisItem.Cum), "", Text({HRACT}, "#,##0"))',534,4,80,52,size=17,bold=True,color=DARK,align="Right",indent=I))
RUNR=f'If(IsBlank(ThisItem.Cum) || ThisItem.Tgt = 0, Blank(), {HRACT} / ThisItem.Tgt)'
STARTIP='"RUN % = units this hour / hour target. Green 100%+, amber 90-99%, red under 90%. ★ PURPLE = exceptional hour: " & Text(varStarCut * 100, "0") & "% or better (" & If(varRunN >= 20, "this line\'s typical hour " & Text(varRunMean * 100, "0") & "% plus 2 standard deviations, last 30 days, " & varRunN & " hours", "fixed 115% until this line has 20 hours of history") & ")."'
kids.append(label("gRun",f'With({{r: {RUNR}}}, If(IsBlank(r), "", If(r >= Coalesce(varStarCut, 1.15), "★ ", "") & Text(r * 100, "0") & "%"))',618,6,116,48,size=19,bold=True,color=WHITE,align="Center",indent=I,
   fill=f'With({{r: {RUNR}}}, If(IsBlank(r), If(ThisItem.InShift, {MUTE}, RGBA(0, 0, 0, 0)), r >= Coalesce(varStarCut, 1.15), RGBA(130, 80, 223, 1), r >= 1, {GREEN}, r >= 0.9, {AMBER}, {RED}))',
   extra={"Tooltip":F(STARTIP)}))
kids.append(label("gVar",f'If(IsBlank(ThisItem.Cum), "", If(ThisItem.Cum - {CUMT} >= 0, "+", "") & Text(ThisItem.Cum - {CUMT}, "#,##0"))',738,4,70,52,size=13,bold=True,align="Center",indent=I,
   extra={"Color":F(f'If(IsBlank(ThisItem.Cum), {G9}, ThisItem.Cum - {CUMT} >= 0, {GREEN}, {RED})')}))
kids.append(ti("gBPM",'If(IsBlank(ThisItem.BPM), "", Text(ThisItem.BPM))',812,9,64,42,'Patch(colHours, ThisItem, {BPM: If(IsBlank(Self.Text), Blank(), Value(Self.Text))});\n'+ROWSAVE,
   hint='"bpm"',size=14,indent=I,extra={"DisplayMode":F(IN),"Fill":F(f'If(!IsBlank(ThisItem.BPM) && ThisItem.BPM < varTmax, RGBA(253, 236, 200, 1), {WHITE})')}))
kids.append(ti("gPlan",'If(ThisItem.Planned = 0, "", Text(ThisItem.Planned))',880,9,56,42,
   'With({p: Coalesce(Value(Self.Text), 0)}, Patch(colHours, ThisItem, {Planned: p, Tgt: Max(0, varUPH * (ThisItem.SlotMin - p) / 60)}));\n'+ROWSAVE,hint='"0"',size=14,indent=I,extra={"DisplayMode":F(IN)}))
kids.append(ti("gDT1",'If(IsBlank(ThisItem.DT), "", Text(ThisItem.DT))',940,9,56,42,'Patch(colHours, ThisItem, {DT: If(IsBlank(Self.Text), Blank(), Value(Self.Text))});\n'+ROWSAVE,hint='"0"',size=14,indent=I,extra={"DisplayMode":F(IN)}))
kids.append(dd("gR1",DT_CODES,1000,9,160,42,default='Coalesce(ThisItem.Reason, " ")',onchange='With({v: Trim(Self.Selected.Value)},\n If(v <> Coalesce(ThisItem.Reason, ""),\n    Patch(colHours, ThisItem, {Reason: v});\n    Set(varRow, LookUp(colHours, HourNo = ThisItem.HourNo));\n    Select(btnSaveRow)))',size=11,indent=I,extra={"DisplayMode":F(IN)}))
kids.append(ti("gDT2",'If(IsBlank(ThisItem.DT2), "", Text(ThisItem.DT2))',1164,9,56,42,'Patch(colHours, ThisItem, {DT2: If(IsBlank(Self.Text), Blank(), Value(Self.Text))});\n'+ROWSAVE,hint='"0"',size=14,indent=I,extra={"DisplayMode":F(IN)}))
kids.append(dd("gR2",DT_CODES,1224,9,160,42,default='Coalesce(ThisItem.Reason2, " ")',onchange='With({v: Trim(Self.Selected.Value)},\n If(v <> Coalesce(ThisItem.Reason2, ""),\n    Patch(colHours, ThisItem, {Reason2: v});\n    Set(varRow, LookUp(colHours, HourNo = ThisItem.HourNo));\n    Select(btnSaveRow)))',size=11,indent=I,extra={"DisplayMode":F(IN)}))
kids.append(btn("gSafety",'If(ThisItem.Safety, "EVENT", "OK")','Patch(colHours, ThisItem, {Safety: !ThisItem.Safety});\n'+ROWSAVE,1388,10,64,40,
   fill=f'If(!ThisItem.InShift, {MUTE}, ThisItem.Safety, {RED}, {MUTE})',color=f'If(ThisItem.Safety, {WHITE}, {G5})',size=11,indent=I,extra={"DisplayMode":F(INSAFE)}))
kids.append(ti("gNotes",'ThisItem.Notes',1456,9,68,42,'Patch(colHours, ThisItem, {Notes: Self.Text});\n'+ROWSAVE,hint='"note"',size=10,number=False,indent=I,extra={"DisplayMode":F(IN)}))
gprops={"Items":F("colHours"),"TemplateSize":"=60","TemplatePadding":"=0","ShowScrollbar":"=false",
 "TemplateFill":F(f'If(!ThisItem.InShift, RGBA(236, 236, 234, 1),\n   Now() >= ThisItem.StartT && Now() < DateAdd(ThisItem.StartT, ThisItem.SlotMin, TimeUnit.Minutes), {NOW},\n   Mod(ThisItem.HourNo, 2) = 0, RGBA(247, 248, 248, 1), {WHITE})'),
 "BorderColor":F(G1),"BorderThickness":"=1"}
gprops.update(box(12,218,1528,720))
out.append(ctrl("galHours","Gallery@2.15.0",gprops,0,kids,variant="BrowseLayout_Vertical_TwoTextOneImageVariant_ver5.0"))

NOPROD='Coalesce(varProd, '+PH+') = '+PH
GATE=NOPROD+' || Coalesce(Value(txtCrew.Text), 0) <= 0'
out.append(label("lblCrewGate",'If('+NOPROD+', "▲  PICK THE PRODUCT RUNNING NOW" & Char(10) & "Choose it in PRODUCT (top), then enter ACTUAL CREW. Safety can always be logged.", "▲  ENTER ACTUAL CREW TO START THE SHIFT" & Char(10) & "Hour entry unlocks once crew is in. Safety can always be logged.")',12,218,1376,720,size=26,bold=True,color=DARK,align="Center",
   fill="RGBA(255, 255, 255, 0.82)",extra={"Visible":F(GATE),"Tooltip":'="Pick the PRODUCT and type the number of people actually on the line in ACTUAL CREW (top). Both are required before hourly entry."'}))
# ---------- bottom shift summary strip ----------
out.append(rect("botBar","RGBA(244, 245, 245, 1)",12,946,1528,124))
out.append(label("lblSumTitle",'"SHIFT SUMMARY"',20,950,300,24,size=11,bold=True,color=G9))
out.append(cap("cScrap","FG SCRAP QTY (UNITS)",20,976,160)); out.append(ti("txtScrap",'If(IsBlank(varShiftRec.FGScrapQty), "", Text(varShiftRec.FGScrapQty))',20,998,150,52,SAVESH,hint='"0"',size=18,bold=True))
out.append(cap("cScrapR","PRIMARY SCRAP / DEFECT REASON",180,976,260)); out.append(dd("ddScrapReason",SCRAP,180,998,260,52,default='Coalesce(varShiftRec.ScrapReasonCode, "")',onchange='If(Self.Selected.Value <> Coalesce(varShiftRec.ScrapReasonCode, ""), Select(btnSaveShift))',size=14))
out.append(cap("cScrapN","SCRAP NOTES",450,976,480)); out.append(ti("txtScrapNotes",'Coalesce(varShiftRec.ScrapNotes, "")',450,998,480,52,SAVESH,hint='"notes"',size=13,number=False,extra={"Align":"=Align.Left"}))
out.append(cap("cSpeed","REASON RUNNING BELOW TARGET SPEED",940,976,300)); out.append(dd("ddSpeedLoss",SPEED,940,998,300,52,default='Coalesce(varShiftRec.SpeedLossReasonCode, "")',onchange='If(Self.Selected.Value <> Coalesce(varShiftRec.SpeedLossReasonCode, ""), Select(btnSaveShift))',size=14))
out.append(cap("cAllow","EST. 3% SCRAP ALLOWANCE",1250,976,280))
out.append(label("lblAllow",'Text(Round(Max(colHours, Coalesce(Cum, 0)) * 0.03, 0), "#,##0") & " units"',1250,998,280,52,size=18,bold=True,color=G9))

# ---------- right KPI panel ----------
X=1548; W=360
out.append(label("kAttain",LAST+'  If(IsBlank(last) || ct = 0, "—", Text((ca / ct) * 100, "0") & "%")'+LASTEND,X,96,W,230,size=80,bold=True,color=WHITE,font="Georgia",align="Center",valign="Bottom",pb=10,
   fill=LAST+f'  If(IsBlank(last) || ct = 0, {G9}, ca / ct >= 1, {GREEN}, ca / ct >= 0.9, {AMBER}, {RED})'+LASTEND))
out.append(label("kAttainCap",'"SHIFT ATTAINMENT  (THROUGH LAST HOUR)"',X,104,W,26,size=11,bold=True,color=WHITE,align="Center"))
out.append(label("kUnits",LAST+'  If(IsBlank(last), "—", Text(ca, "#,##0") & "  /  " & Text(ct, "#,##0"))'+LASTEND+' & Char(10) & "shift target " & Text(Sum(colHours, Tgt), "#,##0")',
   X,334,W,130,size=24,bold=True,color=DARK,fill=MUTE,align="Center",valign="Bottom",pb=10))
out.append(label("kUnitsCap",'"UNITS  ACTUAL / TARGET"',X,340,W,26,size=11,bold=True,color=G9,align="Center"))
out.append(label("kOEE",SUMW+'   If(IsBlank(A) || IsBlank(P) || IsBlank(Q), "—", Text((A * P * Q) * 100, "0") & "%")'+SUMEND,
   X,472,W,200,size=44,bold=True,color=DARK,fill=MUTE,align="Center",valign="Bottom",pb=62))
out.append(label("kAPQ",SUMW+'   "A " & If(IsBlank(A), "—", Text(A * 100, "0") & "%") & "    P " & If(IsBlank(P), "—", Text(P * 100, "0") & "%") & "    Q " & If(IsBlank(Q), "—", Text(Q * 100, "0") & "%")'+SUMEND,
   X,620,W,44,size=20,bold=True,color=DARK,align="Center",extra={"Wrap":"=false"}))
out.append(label("kOEECap",'"OEE  (AVAIL × PERF × QUAL)"',X,480,W,26,size=11,bold=True,color=G9,align="Center"))
out.append(label("kDT",SUMW+'   "Reported " & Text(rep) & "  ·  Calc " & If(IsBlank(up), "—", Text(avail - up, "0")) & " min" & Char(10) &\n   If(IsBlank(up) || avail - up <= 0, "", Text((rep / (avail - up)) * 100, "0") & "%" & " of downtime reported")'+SUMEND+' & Char(10) &\n'
   'Coalesce(First(SortByColumns(AddColumns(GroupBy(Filter(Ungroup(Table({t: ForAll(colHours, {R: Reason, M: Coalesce(DT, 0)})}, {t: ForAll(colHours, {R: Reason2, M: Coalesce(DT2, 0)})}), t), !IsBlank(R) && R <> "" && M > 0), R, G), Mins, Sum(G, M)), "Mins", SortOrder.Descending)).R, "no reasons logged")',
   X,680,W,200,size=16,bold=True,color=DARK,fill=MUTE,align="Center",valign="Bottom",pb=12))
out.append(label("kDTCap",'"DOWNTIME  ·  TOP REASON"',X,688,W,26,size=11,bold=True,color=G9,align="Center"))
out.append(label("kSafety",'If(CountIf(colHours, Safety) = 0, "NO EVENTS", Text(CountIf(colHours, Safety)) & " EVENT(S)")',X,888,W,120,size=28,bold=True,color=WHITE,align="Center",valign="Bottom",pb=12,
   fill=f'If(CountIf(colHours, Safety) = 0, {GREEN}, {RED})'))
out.append(label("kSafetyCap",'"SAFETY THIS SHIFT"',X,896,W,26,size=11,bold=True,color=WHITE,align="Center"))
out.append(label("lblSaved",'If(IsBlank(varSavedAt), "Loaded " & Text(varLoadedAt, "h:mm AM/PM"), "Saved " & Text(varSavedAt, "h:mm:ss AM/PM")) & "  ·  " & User().FullName',X,1016,W,40,size=11,color=G9,align="Center"))

# ---------- hidden-ish helpers (1px, transparent, so Select() always works) ----------
HELP={"Color":F(CLEAR),"BorderColor":F(CLEAR),"HoverFill":F(CLEAR),"PressedFill":F(CLEAR),"TabIndex":"=-1"}
SAVEROW=('Select(btnFlush);\nIf(IsBlank(varPB), Select(btnRefresh));\nWith({r: varRow, k: ddLine.Selected.Value & "-" & Text(ddDate.Selected.D, "yyyymmdd") & "-S" & ddShift.Selected.Value & "-H" & Text(varRow.HourNo, "00")},\n'
 ' With({cumT: Sum(Filter(colHours, HourNo <= r.HourNo), Tgt), prev: Coalesce(LookUp(colHours, HourNo = r.HourNo - 1).Cum, 0),\n'
 '       c1: If(IsBlank(r.Reason), 0, Sum(Filter(colHours, Reason = r.Reason), Coalesce(DT, 0)) + Sum(Filter(colHours, Reason2 = r.Reason), Coalesce(DT2, 0))),\n'
 '       c2: If(IsBlank(r.Reason2), 0, Sum(Filter(colHours, Reason = r.Reason2), Coalesce(DT, 0)) + Sum(Filter(colHours, Reason2 = r.Reason2), Coalesce(DT2, 0)))},\n'
 '  With({rec: {Title: k, Line: ddLine.Selected.Value, ShiftDate: ddDate.Selected.D, Shift: Value(ddShift.Selected.Value),\n'
 '    HourNo: r.HourNo, HourStart: r.StartT, SlotMin: r.SlotMin,\n'
 '    ProductForm: If(varProd = '+PH+', "", varPB.Size & " " & varPB.Form),\n'
 f'    PlaybookKey: {LINEKEY},\n'
 '    Job: If(IsBlank(r.Job), txtJob1.Text, r.Job),\n'
 '    HourlyTarget: r.Tgt, CumTarget: cumT, CumulativeUnits: r.Cum,\n'
 '    HourlyActual: If(IsBlank(r.Cum), Blank(), r.Cum - prev),\n'
 '    RunRatePct: If(IsBlank(r.Cum) || r.Tgt = 0, Blank(), (r.Cum - prev) / r.Tgt),\n'
 '    SpeedBPM: r.BPM, PlannedMin: r.Planned,\n'
 '    DT_Minutes: r.DT, DT_Reason: r.Reason, DT2_Minutes: r.DT2, DT2_Reason: r.Reason2,\n'
 '    SafetyEvent: r.Safety, Notes: r.Notes, EnteredBy: User().Email,\n'
 '    ShiftKey: ddLine.Selected.Value & "-" & Text(ddDate.Selected.D, "yyyymmdd") & "-S" & ddShift.Selected.Value,\n'
 '    EscReason: If(c2 > c1, r.Reason2, r.Reason), EscCumMin: Max(c1, c2)}},\n'
 '   IfError(Patch(HxH_Hourly, Coalesce(LookUp(HxH_Hourly, Title = k), Defaults(HxH_Hourly)), rec),\n'
 '    RemoveIf(colPending, K = k); Collect(colPending, {K: k, HourNo: r.HourNo, Rec: rec, At: Now()});\n'
 '    Notify("Hour " & r.HourNo & " NOT saved (no connection?). It is kept on this tablet and will retry. Keep this app open.", NotificationType.Warning),\n'
 '    RemoveIf(colPending, K = k)))));\n'
 'If(CountRows(colPending) = 0, Set(varSavedAt, Now()));\n'
 'Select(btnSaveShift)')
SAVESHIFT=(SUMW.replace("varDurM","With({d0: ddDate.Selected.D}, With({d1: If(ddEnd.Selected.M <= ddStart.Selected.M, DateAdd(d0, 1, TimeUnit.Days), d0)}, DateDiff(DateTime(Year(d0), Month(d0), Day(d0), RoundDown(ddStart.Selected.M / 60, 0), Mod(ddStart.Selected.M, 60), 0), DateTime(Year(d1), Month(d1), Day(d1), RoundDown(ddEnd.Selected.M / 60, 0), Mod(ddEnd.Selected.M, 60), 0), TimeUnit.Minutes)))")+
 '   IfError(Patch(HxH_Shift,\n'
 '    Coalesce(LookUp(HxH_Shift, Title = ddLine.Selected.Value & "-" & Text(ddDate.Selected.D, "yyyymmdd") & "-S" & ddShift.Selected.Value), Defaults(HxH_Shift)),\n'
 '    {Title: ddLine.Selected.Value & "-" & Text(ddDate.Selected.D, "yyyymmdd") & "-S" & ddShift.Selected.Value, Line: ddLine.Selected.Value, ShiftDate: ddDate.Selected.D, Shift: Value(ddShift.Selected.Value),\n'
 '     ProductForm: If(varProd = '+PH+', "", varProd),\n'
 f'     PlaybookKey: {LINEKEY},\n'
 '     Job1: txtJob1.Text,\n'
 '     Job2: Coalesce(Last(Filter(colHours, !IsBlank(Job) && Job <> txtJob1.Text)).Job, ""),\n'
 '     PlannedShiftHrs: With({d0: ddDate.Selected.D}, With({d1: If(ddEnd.Selected.M <= ddStart.Selected.M, DateAdd(d0, 1, TimeUnit.Days), d0)}, DateDiff(DateTime(Year(d0), Month(d0), Day(d0), RoundDown(ddStart.Selected.M / 60, 0), Mod(ddStart.Selected.M, 60), 0), DateTime(Year(d1), Month(d1), Day(d1), RoundDown(ddEnd.Selected.M / 60, 0), Mod(ddEnd.Selected.M, 60), 0), TimeUnit.Minutes))) / 60,\n'
 '     ActualStartTime: ddStart.Selected.Value, ActualEndTime: ddEnd.Selected.Value,\n'
 '     LunchMin: Coalesce(Value(txtLunch.Text), 0), BreakMin: Coalesce(Value(txtBreak.Text), 0),\n'
 '     TargetUnits: tgt, ActualUnits: act, AvgBPM: bpm, TmaxBPM: varTmax,\n'
 '     ReportedDowntimeMin: rep, CalculatedDowntimeMin: If(IsBlank(up), Blank(), avail - up), MachineUptimeMin: up,\n'
 '     Availability: A, Performance: P, FGScrapQty: scrap, Quality: Q, OEE: If(IsBlank(A) || IsBlank(P) || IsBlank(Q), Blank(), A * P * Q),\n'
 '     ScrapReasonCode: ddScrapReason.Selected.Value, ScrapNotes: txtScrapNotes.Text,\n'
 "     StdCrewSize: Value(varPB.'Total HC'), ActualCrewSize: Value(txtCrew.Text),\n"
 '     StaffingReasonCode: ddStaff.Selected.Value, SpeedLossReasonCode: ddSpeedLoss.Selected.Value,\n'
 '     EnteredBy: User().Email}), Notify("Shift totals not saved yet (no connection?). They update on the next save.", NotificationType.Warning))'+SUMEND+';\n'
 'Set(varSavedAt, Now())')
exec(open(__import__("os").environ["MDI_GEN"]+"/ux_tail6.py").read())
FLUSH=('If(CountRows(colPending) > 0,\n'
 ' IfError(ForAll(colPending As p, Patch(HxH_Hourly, Coalesce(LookUp(HxH_Hourly, Title = p.K), Defaults(HxH_Hourly)), p.Rec)),\n'
 '  Notify("Still not connected: " & CountRows(colPending) & " hour(s) waiting on this tablet. Keep the app open.", NotificationType.Warning),\n'
 '  Clear(colPending); Notify("Waiting hours saved.", NotificationType.Success)))')
out.append(btn("btnFlush",'""',FLUSH,4,1079,1,1,fill=CLEAR,color=CLEAR,extra=HELP))
out.append(label("lblPending",'"⚠  " & CountRows(colPending) & If(CountRows(colPending) = 1, " HOUR", " HOURS") & " NOT SAVED YET (hour " & Concat(Sort(colPending, HourNo), Text(HourNo), ", ") & ")  ·  kept on this tablet, retrying on every save. KEEP THIS APP OPEN."',
   12,92,1180,44,size=14,bold=True,color=WHITE,fill=RED,extra={"Visible":"=CountRows(colPending) > 0","PaddingLeft":"=16"}))
out.append(btn("btnRetry",'"RETRY NOW"','Select(btnFlush)',1196,94,150,40,size=13,fill=WHITE,color=RED,extra={"Visible":"=CountRows(colPending) > 0","BorderColor":F(RED),"BorderThickness":"=2"}))
out.append(btn("btnSaveRow",'""',SAVEROW,0,1079,1,1,fill=CLEAR,color=CLEAR,extra=HELP))
out.append(btn("btnSaveShift",'""',SAVESHIFT,2,1079,1,1,fill=CLEAR,color=CLEAR,extra=HELP))
write_themed(__import__("os").environ["MDI_OUTDIR"]+"/HxH_Board_v22.pa.yaml", "".join(out))
print("ok", sum(len(x) for x in out))
