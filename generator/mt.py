# Generates TS_Maintenance_v5.pa.yaml (board-linked downtime) — phone (640x1136) troubleshooting app for maintenance
exec(open("/tmp/claude-0/gen/theme.py").read())
src=open('/tmp/claude-0/gen/build6.py').read()
exec(src[:src.index("DT_OLD=")])
EXTRA.clear()
MUTE="RGBA(243, 244, 244, 1)"; PANEL="RGBA(248, 249, 249, 1)"
YEL="RGBA(255, 242, 179, 1)"; YELB="RGBA(210, 153, 34, 1)"; AMBL="RGBA(253, 236, 200, 1)"
RAD={"RadiusTopLeft":"=8","RadiusTopRight":"=8","RadiusBottomLeft":"=8","RadiusBottomRight":"=8"}
W=640
FLOW="'MDI-UploadPhoto'"

BODY=r'''
def rect(name,fill,x,y,w,h,indent=0): d={"Fill":F(fill)}; d.update(box(x,y,w,h)); return ctrl(name,"Rectangle@2.3.0",d,indent)
def tip(name,text): EXTRA.setdefault(name,{})["Tooltip"]='="'+text.replace('"','""')+'"'
def vis(name,step):
    EXTRA.setdefault(name,{})["Visible"]=F(f'varStep = "{step}"')
def P(step, *ctrls):
    # register visibility for a list of control names
    for n in ctrls: vis(n,step)
def need(name, empty):
    EXTRA.setdefault(name,{}).update({"Fill":F(f'If({empty}, {YEL}, {WHITE})'),"BorderColor":F(f'If({empty}, {YELB}, {G5})'),"BorderThickness":F(f'If({empty}, 3, 1)')})

SHIFT='If(Hour(Now()) * 60 + Minute(Now()) >= 360 && Hour(Now()) * 60 + Minute(Now()) < 990, 1, 2)'
SDATE='If(Hour(Now()) < 6, DateAdd(Today(), -1, TimeUnit.Days), Today())'
EVLOAD=('ClearCollect(colEv, With({hr: Filter(HxH_Hourly, Line = ddMLine.Selected.Value && HourStart >= DateAdd(Now(), -24, TimeUnit.Hours)),\n'
 '  rs: Filter(colLk, Category.Value = "Downtime" && EquipType = varEquip)},\n'
 ' SortByColumns(ForAll(GroupBy(Filter(Ungroup(Table(\n'
 '   {t: ForAll(hr, {SK: ShiftKey, R: DT_Reason, M: Coalesce(DT_Minutes, 0), H: HourNo, St: StillDown, HS: HourStart})},\n'
 '   {t: ForAll(hr, {SK: ShiftKey, R: DT2_Reason, M: Coalesce(DT2_Minutes, 0), H: HourNo, St: false, HS: HourStart})}), t),\n'
 '   M > 0 && R in rs.Label), SK, R, G),\n'
 '  {Key: SK & "|" & R, SK: SK, R: R, Mn: Sum(G, M), H1: Min(G, H), H2: Max(G, H), Still: CountIf(G, St) > 0, Last: Max(G, HS), First: Min(G, HS)}),\n'
 '  "Last", SortOrder.Descending)))')
EV='LookUp(colEv, Key = varEventKey)'
ISS='LookUp(colIss, ID = varIssueID)'
FIX='LookUp(colFix, ID = varFixID)'

# ---------------- header ----------------
out.append(rect("hdrBar",DARK,0,0,W,118))
out.append(label("lblBrand",'"voyant"',16,4,140,40,size=22,color=WHITE,font="Georgia"))
out.append(label("lblTitle",'"TROUBLESHOOT"',150,8,330,36,size=18,bold=True,color=WHITE,font="Georgia"))
out.append(label("lblCtx",'ddMLine.Selected.Value & If(IsBlank(varEquip), "", "  ·  " & varEquip) & If(ddMAsset.Selected.Value = "(any)" || IsBlank(ddMAsset.Selected.Value), "", "  ·  " & ddMAsset.Selected.Value) & "  ·  S" & Text(' + SHIFT + ')',
   16,50,W-32,30,size=14,bold=True,color=AQUA))
out.append(label("lblUser",'User().FullName',16,82,W-200,26,size=11,color=G5))
out.append(btn("btnBack",'"‹ BACK"',
   'Switch(varStep, "event", Set(varStep, "where"), "issue", Set(varStep, "event"), "fix", Set(varStep, "issue"), "proc", Set(varStep, "fix"), "new", Set(varStep, If(varNewIssue, "issue", "fix")), "log", Set(varStep, If(varOutcome = "New fix added", "steps", "fix")), "steps", Set(varStep, "new"), Set(varStep, "where"))',
   W-170,72,90,38,fill=TEAL_D,color=WHITE,size=12,extra={**RAD,"Visible":F('varStep <> "where" && varStep <> "done"')}))
LOAD=('IfError(ClearCollect(colLk, Filter(Lookups, Active = true)), Notify("Could not load Lookups — " & FirstError.Message, NotificationType.Error));\n'
 'ClearCollect(colEq, ForAll(Sort(Filter(colLk, Category.Value = "Equipment"), SortOrder), {Value: Label}));\n'
 'ClearCollect(colLines, Lines);\n'
 'IfError(ClearCollect(colAssets, Filter(Assets, Active = true)), Notify("Could not load Assets", NotificationType.Warning));\n'
 'IfError(ClearCollect(colIss, Filter(TS_Issues, Active = true)), Notify("Could not load TS_Issues — " & FirstError.Message, NotificationType.Error));\n'
 'IfError(ClearCollect(colFix, Filter(TS_Fixes, Active = true)), Notify("Could not load TS_Fixes — " & FirstError.Message, NotificationType.Error));\n'
 'IfError(ClearCollect(colOcc, Filter(TS_Occurrences, OccurredAt >= DateAdd(Today(), -90, TimeUnit.Days))), Notify("Could not load TS_Occurrences", NotificationType.Warning));\n'
 'If(!varParamUsed && !IsBlank(Param("equip")), Set(varEquip, Param("equip")); ' + EVLOAD + '; Set(varStep, "event"));\n'
 'Set(varParamUsed, true);\n'
 'If(IsBlank(varStep), Set(varStep, "where"));\n'
 'Set(varLoaded, Now())')
out.append(btn("btnMRefresh",'"↻"',LOAD,W-70,72,54,38,fill=TEAL_D,color=WHITE,size=16,extra=RAD))
tip("btnMRefresh","Reload the guide from SharePoint.")

Y0=130
# ---------------- STEP: where ----------------
out.append(label("wT",'"WHERE ARE YOU?"',16,Y0,W-32,40,size=18,bold=True,color=DARK,font="Georgia"))
out.append(cap("wCL","LINE",16,Y0+50,200))
out.append(dd("ddMLine",'ForAll(SortByColumns(colLines, "DisplayOrder"), {Value: Line})',16,Y0+72,220,60,default='Coalesce(Param("line"), "209")',size=22,bold=True))
out.append(cap("wCA","ASSET  (OPTIONAL)",250,Y0+50,300))
out.append(dd("ddMAsset",'Ungroup(Table({t: Table({Value: "(any)"})}, {t: ForAll(Filter(colAssets, Line = ddMLine.Selected.Value && (IsBlank(varEquip) || EquipType = varEquip)), {Value: Asset})}), t)',250,Y0+72,W-266,60,
   default='Coalesce(Param("asset"), "(any)")',size=16))
out.append(label("wTE",'"WHAT MACHINE?  (TAP)"',16,Y0+150,W-32,30,size=12,bold=True,color=G9))
eq=[btn("gEq",'ThisItem.Value','Set(varEquip, ThisItem.Value); '+EVLOAD+'; Set(varEventKey, Blank()); Set(varLinkStatus, ""); Set(varStep, "event")',6,6,296,80,
        fill=f'If(varEquip = ThisItem.Value, {TEAL_D}, {WHITE})',color=f'If(varEquip = ThisItem.Value, {WHITE}, {DARK})',size=18,indent=6,
        extra={"BorderColor":F(G5),"BorderThickness":"=2",**RAD})]
gp={"Items":F("colEq"),"WrapCount":"=2","TemplateSize":"=92","TemplatePadding":"=0"}; gp.update(box(10,Y0+182,W-20,560))
out.append(ctrl("galEq","Gallery@2.15.0",gp,0,eq,variant="BrowseLayout_Vertical_TwoTextOneImageVariant_ver5.0"))
out.append(label("wNoEq",'"No equipment types loaded — tap ↻, or add rows to Lookups (Category = Equipment)."',16,Y0+190,W-32,60,size=13,color=G9,extra={"Visible":F('varStep = "where" && CountRows(colEq) = 0')}))
P("where","wT","wCL","ddMLine","wCA","ddMAsset","wTE","galEq")

# ---------------- STEP: event (link to the board's downtime) ----------------
out.append(label("eT",'"WHICH DOWNTIME IS THIS?"',16,Y0,W-32,40,size=18,bold=True,color=DARK,font="Georgia"))
out.append(label("eSub",'"Downtime on the hour-by-hour board for " & ddMLine.Selected.Value & " · " & varEquip & ", last 24 h. The board owns the minutes."',16,Y0+40,W-32,48,size=11,color=G9))
ek=[rect("gEBg",WHITE,6,4,W-32,128,indent=6),
    rect("gEStripe",f'If(ThisItem.Still, {RED}, {AMBER})',6,4,10,128,indent=6),
    label("gER",'Substitute(ThisItem.R, "Machine - ", "")',28,10,W-260,40,size=18,bold=True,color=DARK,indent=6),
    label("gEMin",'Text(ThisItem.Mn) & " min"',W-230,10,190,40,size=22,bold=True,color=DARK,align="Right",indent=6),
    label("gEWhen",'Right(ThisItem.SK, 2) & " · " & Text(ThisItem.First, "ddd h:mm AM/PM") & "  ·  hour " & ThisItem.H1 & If(ThisItem.H2 > ThisItem.H1, "–" & ThisItem.H2, "")',28,54,W-80,30,size=12,color=G9,indent=6),
    label("gEStill",'If(ThisItem.Still, "STILL DOWN", "")',28,88,200,32,size=12,bold=True,color=RED,indent=6),
    btn("gESel",'""','Set(varEventKey, ThisItem.Key); Set(varLinkStatus, "Linked at fix"); Set(varStep, "issue")',0,0,W-20,136,fill=CLEAR,color=CLEAR,indent=6,
        extra={"HoverFill":"=RGBA(0, 178, 169, 0.10)","PressedFill":"=RGBA(0, 178, 169, 0.20)","BorderColor":F(CLEAR)})]
ep={"Items":F("colEv"),"TemplateSize":"=140","TemplatePadding":"=0"}; ep.update(box(10,Y0+96,W-20,600))
out.append(ctrl("galEv","Gallery@2.15.0",ep,0,ek,variant="BrowseLayout_Vertical_TwoTextOneImageVariant_ver5.0"))
out.append(label("eNone",'"Nothing on the board for " & varEquip & " on line " & ddMLine.Selected.Value & " in the last 24 h."',16,Y0+120,W-32,60,size=13,color=G9,
   extra={"Visible":F('varStep = "event" && CountRows(colEv) = 0')}))
out.append(btn("btnENot",'"NOT ON THE BOARD YET  ›"','Set(varEventKey, Blank()); Set(varLinkStatus, "Not on board"); Set(varStep, "issue")',16,Y0+712,W-32,70,fill=WHITE,color=TEAL_D,size=15,
   extra={"BorderColor":F(TEAL_D),"BorderThickness":"=2",**RAD}))
out.append(label("eNote",'"Pick this if the line hasn\'t logged the stop yet. A supervisor links it to the board later."',16,Y0+788,W-32,48,size=11,color=G9,align="Center"))
P("event","eT","eSub","galEv","btnENot","eNote")

# ---------------- STEP: issue ----------------
out.append(label("iT",'"WHAT\'S HAPPENING?"',16,Y0,W-32,40,size=18,bold=True,color=DARK,font="Georgia"))
out.append(ti("txtISearch",'""',16,Y0+46,W-32,52,'false',hint='"search concerns…"',size=15,number=False,extra={"Align":"=Align.Left"}))
ISSITEMS=('SortByColumns(ForAll(Filter(colIss, EquipType = varEquip && (IsBlank(Line) || Line = ddMLine.Selected.Value) && (IsBlank(txtISearch.Text) || txtISearch.Text in Concern || txtISearch.Text in Appearance)) As i,\n'
          ' {ID: i.ID, Concern: i.Concern, Code: i.Code, Appearance: i.Appearance, N: CountIf(colOcc, IssueID = i.ID), NF: CountIf(colFix, IssueID = i.ID)}), "N", SortOrder.Descending)')
ik=[rect("gIBg",WHITE,0,0,W-20,112,indent=6),
    label("gIRank",'"#" & Text(ThisItem.N)',8,8,64,40,size=11,bold=True,color=G9,indent=6),
    label("gIName",'ThisItem.Concern',12,6,W-150,44,size=16,bold=True,color=DARK,indent=6),
    label("gIApp",'Coalesce(ThisItem.Appearance, "")',12,48,W-150,56,size=11,color=G9,indent=6,extra={"VerticalAlign":"=VerticalAlign.Top"}),
    label("gICnt",'Text(ThisItem.N) & "×" & Char(10) & "90 days"',W-130,10,100,60,size=13,bold=True,color=DARK,align="Center",indent=6),
    label("gINF",'Text(ThisItem.NF) & If(ThisItem.NF = 1, " fix", " fixes")',W-130,72,100,30,size=11,color=G9,align="Center",indent=6),
    btn("gISel",'""','Set(varIssueID, ThisItem.ID); Set(varNewIssue, false);\nClearCollect(colIssPh, Filter(TS_Photos, IssueID = ThisItem.ID));\nSet(varStep, "fix")',0,0,W-20,112,fill=CLEAR,color=CLEAR,indent=6,
        extra={"HoverFill":F("RGBA(0, 72, 81, 0.06)"),"PressedFill":F("RGBA(0, 72, 81, 0.12)"),"BorderColor":F(G1),"BorderThickness":"=1"})]
ik[1]=""  # rank label not needed (count shown on right)
gp={"Items":F(ISSITEMS),"TemplateSize":"=118","TemplatePadding":"=0"}; gp.update(box(10,Y0+106,W-20,750))
out.append(ctrl("galIss","Gallery@2.15.0",gp,0,[k for k in ik if k],variant="BrowseLayout_Vertical_TwoTextOneImageVariant_ver5.0"))
out.append(label("iNone",'"No concerns logged for " & varEquip & " yet."',16,Y0+120,W-32,40,size=13,color=G9,extra={"Visible":F('varStep = "issue" && CountRows(galIss.AllItems) = 0')}))
out.append(btn("btnNewIss",'"+  NEW CONCERN  (not in the list)"','Set(varNewIssue, true); Set(varIssueID, Blank()); Set(varDoneBy, ""); Set(varStep, "new")',16,Y0+870,W-32,70,fill=WHITE,color=TEAL_D,size=15,
   extra={"BorderColor":F(TEAL_D),"BorderThickness":"=2",**RAD}))
P("issue","iT","txtISearch","galIss","btnNewIss")

# ---------------- STEP: fix (ranked countermeasures) ----------------
out.append(label("fT",ISS+'.Concern',16,Y0,W-32,56,size=17,bold=True,color=DARK,font="Georgia"))
out.append(image("fImg",'LookUp(colIssPh, Kind.Value = "Appearance").Thumbnail.Large',W-136,Y0+58,120,90))
out.append(label("fApp",'Coalesce(' + ISS + '.Appearance, "")',16,Y0+58,W-170,90,size=12,color=G9,extra={"VerticalAlign":"=VerticalAlign.Top"}))
out.append(label("fHint",'"Try in this order — ranked by what has actually fixed it."',16,Y0+150,W-32,26,size=11,bold=True,color=G9))
FIXITEMS=('SortByColumns(ForAll(Filter(colFix, IssueID = varIssueID) As f,\n'
          ' {ID: f.ID, Cause: f.Cause, CM: f.Countermeasure, Chk: f.Check, NR: f.NormalRange, By: f.DoneBy.Value, Seq: Coalesce(f.SeqOrder, 999), Proc: f.ProcID,\n'
          '  Uses: CountIf(colOcc, FixID = f.ID)}), "Uses", SortOrder.Descending, "Seq", SortOrder.Ascending)')
fk=[rect("gFBg",WHITE,0,0,W-20,286,indent=6),
    label("gFRank",'Text(ThisItem.Uses) & "×"',8,10,70,40,size=16,bold=True,color=WHITE,align="Center",indent=6,fill=TEAL_D),
    label("gFCause",'ThisItem.Cause',86,6,W-230,48,size=14,bold=True,color=DARK,indent=6),
    label("gFBy",'ThisItem.By',W-140,12,110,30,size=11,bold=True,color=WHITE,align="Center",indent=6,
          fill=f'If(ThisItem.By = "Operator", {TEAL}, ThisItem.By = "Maintenance", {TEAL_D}, {G9})'),
    label("gFCM",'ThisItem.CM',12,58,W-44,120,size=12,color=DARK,indent=6,extra={"VerticalAlign":"=VerticalAlign.Top"}),
    label("gFNR",'If(IsBlank(ThisItem.NR) || ThisItem.NR = "NA", "", "Normal range: " & ThisItem.NR) & If(IsBlank(ThisItem.Chk), "", "   ·   Check: " & ThisItem.Chk)',12,178,W-44,40,size=10,color=G9,indent=6),
    btn("gFSteps",'"📷 STEPS"','Set(varViewProc, ThisItem.Proc); ClearCollect(colPh, Filter(TS_Photos, ProcID = ThisItem.Proc)); ClearCollect(colPSteps, Sort(Filter(TS_Steps, ProcID = ThisItem.Proc), StepNo)); Set(varStep, "proc")',
        12,226,150,50,fill=WHITE,color=TEAL_D,size=12,indent=6,extra={"BorderColor":F(TEAL_D),"BorderThickness":"=1","Visible":F('!IsBlank(ThisItem.Proc) && ThisItem.Proc > 0'),**RAD}),
    btn("gFUse",'"✓  THIS FIXED IT"','Set(varFixID, ThisItem.ID); Set(varDoneBy, ThisItem.By); Set(varOutcome, "Existing fix"); Set(varStep, "log")',
        W-300,226,268,50,fill=TEAL_D,color=WHITE,size=14,indent=6,extra=RAD)]
gp={"Items":F(FIXITEMS),"TemplateSize":"=296","TemplatePadding":"=0"}; gp.update(box(10,Y0+180,W-20,620))
out.append(ctrl("galFix","Gallery@2.15.0",gp,0,fk,variant="BrowseLayout_Vertical_TwoTextOneImageVariant_ver5.0"))
out.append(label("fNone",'"No countermeasures yet for this concern."',16,Y0+190,W-32,40,size=13,color=G9,extra={"Visible":F('varStep = "fix" && CountRows(galFix.AllItems) = 0')}))
out.append(label("fEsc",'Coalesce(' + ISS + '.Escalation, "")',16,Y0+802,W-32,30,size=10,color=G9))
out.append(btn("btnNewFix",'"NONE OF THESE WORKED — ADD NEW FIX"','Set(varNewIssue, false); Set(varDoneBy, ""); Set(varStep, "new")',16,Y0+836,W-32,64,fill=WHITE,color=TEAL_D,size=14,
   extra={"BorderColor":F(TEAL_D),"BorderThickness":"=2",**RAD}))
out.append(btn("btnEsc",'"NOT RESOLVED — ESCALATE"','Set(varFixID, Blank()); Set(varDoneBy, ""); Set(varOutcome, "Not resolved - escalated"); Set(varStep, "log")',16,Y0+908,W-32,52,fill=WHITE,color=RED,size=12,
   extra={"BorderColor":F(RED),"BorderThickness":"=1",**RAD}))
P("fix","fT","fImg","fApp","fHint","galFix","fEsc","btnNewFix","btnEsc")

# ---------------- STEP: proc (view steps) ----------------
out.append(label("pT",'Coalesce(LookUp(colFix, ProcID = varViewProc).Cause, "Procedure")',16,Y0,W-32,50,size=16,bold=True,color=DARK,font="Georgia"))
pk=[rect("gPBg",WHITE,0,0,W-20,330,indent=6),
    label("gPN",'Text(ThisItem.StepNo)',8,8,52,52,size=20,bold=True,color=WHITE,align="Center",indent=6,fill=TEAL_D),
    label("gPI",'ThisItem.Instruction',70,6,W-110,56,size=14,bold=True,color=DARK,indent=6),
    label("gPK",'Coalesce(ThisItem.KeyPoint, "")',70,60,W-110,40,size=11,color=G9,indent=6),
    image("gPImg",'LookUp(colPh, StepNo = ThisItem.StepNo).Thumbnail.Large',12,104,W-44,216,indent=6)]
gp={"Items":F("colPSteps"),"TemplateSize":"=340","TemplatePadding":"=0"}; gp.update(box(10,Y0+56,W-20,900))
out.append(ctrl("galProc","Gallery@2.15.0",gp,0,pk,variant="BrowseLayout_Vertical_TwoTextOneImageVariant_ver5.0"))
P("proc","pT","galProc")

# ---------------- STEP: new (digital 4C) ----------------
out.append(label("nT",'If(varNewIssue, "NEW CONCERN + FIX", "NEW FIX for: " & ' + ISS + '.Concern)',16,Y0,W-32,46,size=15,bold=True,color=DARK,font="Georgia"))
NY=Y0+50
out.append(cap("nC1","CONCERN — WHAT IS HAPPENING?",16,NY,W-32))
out.append(ti("txtNConcern",'""',16,NY+20,W-32,50,'false',hint='"e.g. Labels wrinkling at wipe-down"',size=14,number=False,extra={"Align":"=Align.Left"}))
out.append(cap("nC2","WHAT IT LOOKS LIKE  (optional photo)",16,NY+76,W-32))
out.append(ti("txtNApp",'""',16,NY+96,W-180,70,'false',hint='"appearance / symptom detail"',size=12,number=False,extra={"Align":"=Align.Left","Mode":"=TextMode.MultiLine"}))
out.append(ctrl("addNApp","AddMedia@2.2.1",{"X":F(str(W-156)),"Y":F(str(NY+96)),"Width":"=140","Height":"=70","Size":"=11","Text":'=If(IsBlank(Self.Media), "📷 photo", "✓ photo")',"Fill":F(MUTE),"Color":F(TEAL_D),"BorderColor":F(G5),"BorderThickness":"=1"}))
for n in ["nC1","txtNConcern","nC2","txtNApp","addNApp"]: EXTRA.setdefault(n,{})["Visible"]=F('varStep = "new" && varNewIssue')
CY=NY+176
out.append(cap("nC3","CAUSE — WHY IS IT HAPPENING?",16,CY,W-32))
out.append(ti("txtNCause",'""',16,CY+20,W-32,50,'false',hint='"e.g. Teflon pad worn"',size=14,number=False,extra={"Align":"=Align.Left"}))
out.append(cap("nC4","COUNTERMEASURE — HOW DID YOU FIX IT?",16,CY+76,W-32))
out.append(ti("txtNCM",'""',16,CY+96,W-32,110,'false',hint='"what you did, settings, adjustments"',size=13,number=False,extra={"Align":"=Align.Left","Mode":"=TextMode.MultiLine"}))
out.append(cap("nC5","CHECK — HOW DO WE KNOW IT'S FIXED?",16,CY+212,W-32))
out.append(ti("txtNCheck",'""',16,CY+232,W-32,50,'false',hint='"e.g. 10 bottles, no wrinkles"',size=13,number=False,extra={"Align":"=Align.Left"}))
out.append(cap("nC6","NORMAL RANGE  (optional)",16,CY+288,250))
out.append(ti("txtNNR",'""',16,CY+308,250,50,'false',hint='"e.g. 0.78 - 0.81"',size=13,number=False,extra={"Align":"=Align.Left"}))
out.append(cap("nC7","WHO CAN DO THIS FIX?",280,CY+288,W-296))
whoy=CY+308
for i,(w,c) in enumerate([("Operator",TEAL),("Maintenance",TEAL_D),("Engineering",G9)]):
    out.append(btn(f"btnWho{i}",f'"{w}"',f'Set(varDoneBy, "{w}")',280+i*116,whoy,110,50,fill=f'If(varDoneBy = "{w}", {c}, {WHITE})',color=f'If(varDoneBy = "{w}", {WHITE}, {DARK})',size=11,
       extra={"BorderColor":F(c),"BorderThickness":"=2",**RAD}))
NEWOK=('(!varNewIssue || !IsBlank(txtNConcern.Text)) && !IsBlank(txtNCause.Text) && !IsBlank(txtNCM.Text) && !IsBlank(varDoneBy)')
START=('IfError(\n'
 ' If(varNewIssue,\n'
 '  Set(varIssueID, Patch(TS_Issues, Defaults(TS_Issues), {Concern: txtNConcern.Text, EquipType: varEquip, Line: ddMLine.Selected.Value, Asset: If(ddMAsset.Selected.Value = "(any)", "", ddMAsset.Selected.Value),\n'
 '     Appearance: txtNApp.Text, Active: true, CreatedVia: {Value: "Maintenance phone"}, AddedBy: User().FullName}).ID);\n'
 '  If(!IsBlank(addNApp.Media), ' + FLOW + '.Run({contentBytes: addNApp.Media, name: "appearance.jpg"}, "I" & varIssueID & "-appearance.jpg", 0, 0, varIssueID, "Appearance", txtNConcern.Text, User().Email))\n'
 ' );\n'
 ' Set(varProcID, Patch(TS_Procedures, Defaults(TS_Procedures), {Procedure: txtNCause.Text, DocType: {Value: "Quick fix"}, EquipType: varEquip, Line: ddMLine.Selected.Value,\n'
 '    Active: false, CreatedVia: {Value: "Maintenance phone"}, AddedBy: User().FullName}).ID);\n'
 ' Set(varFixID, Patch(TS_Fixes, Defaults(TS_Fixes), {Cause: txtNCause.Text, IssueID: varIssueID, Countermeasure: txtNCM.Text, Check: txtNCheck.Text, NormalRange: txtNNR.Text,\n'
 '    DoneBy: {Value: varDoneBy}, SeqOrder: CountIf(colFix, IssueID = varIssueID) * 10 + 10, ProcID: varProcID, Active: false, CreatedVia: {Value: "Maintenance phone"}, AddedBy: User().FullName}).ID),\n'
 ' Notify("NOT SAVED — " & FirstError.Message, NotificationType.Error),\n'
 ' Set(varOutcome, "New fix added"); Set(varStepNo, 1); Clear(colStepsDone); Set(varStep, "steps"))')
out.append(btn("btnNStart",f'If({NEWOK}, "START STEP PHOTOS  ›", "FILL CONCERN · CAUSE · FIX · WHO")',START,16,CY+372,W-32,70,fill=f'If({NEWOK}, {TEAL_D}, {G1})',color=f'If({NEWOK}, {WHITE}, {G9})',size=15,
   extra={"DisplayMode":F(f'If({NEWOK}, DisplayMode.Edit, DisplayMode.Disabled)'),"DisabledFill":F(G1),"DisabledColor":F(G9),**RAD}))
need("txtNConcern","IsBlank(Self.Text)"); need("txtNCause","IsBlank(Self.Text)"); need("txtNCM","IsBlank(Self.Text)")
P("new","nT","nC3","txtNCause","nC4","txtNCM","nC5","txtNCheck","nC6","txtNNR","nC7","btnWho0","btnWho1","btnWho2","btnNStart")

# ---------------- STEP: steps (document while fixing) ----------------
out.append(label("sT",'"STEP " & Text(varStepNo) & "  —  document as you go"',16,Y0,W-32,44,size=16,bold=True,color=DARK,font="Georgia"))
out.append(cap("sC1","WHAT DID YOU DO?",16,Y0+50,W-32))
out.append(ti("txtSInstr",'""',16,Y0+70,W-32,80,'false',hint='"e.g. Loosen handle #1, rotate #2 a quarter turn"',size=14,number=False,extra={"Align":"=Align.Left","Mode":"=TextMode.MultiLine"}))
out.append(cap("sC2","KEY POINT / WHY  (optional)",16,Y0+156,W-32))
out.append(ti("txtSKey",'""',16,Y0+176,W-32,50,'false',hint='"e.g. 1/4 turns only"',size=12,number=False,extra={"Align":"=Align.Left"}))
out.append(ctrl("imgSPrev","Image@2.2.3",{"Image":F('If(IsBlank(addSPhoto.Media), SampleImage, addSPhoto.Media)'),"ImagePosition":"=ImagePosition.Fit","X":"=16","Y":F(str(Y0+236)),"Width":F(str(W-32)),"Height":"=260","Fill":F(MUTE)}))
out.append(ctrl("addSPhoto","AddMedia@2.2.1",{"X":"=16","Y":F(str(Y0+236)),"Width":F(str(W-32)),"Height":"=260","Size":"=16","Text":'="📷  TAP TO TAKE PHOTO OF THIS STEP"',"Fill":"=RGBA(0, 0, 0, 0)","Color":F(TEAL_D),"BorderColor":F(G5),"BorderThickness":"=1"}))
SAVESTEP=('IfError(\n'
 ' Patch(TS_Steps, Defaults(TS_Steps), {Instruction: txtSInstr.Text, ProcID: varProcID, StepNo: varStepNo, KeyPoint: txtSKey.Text});\n'
 ' If(!IsBlank(addSPhoto.Media), ' + FLOW + '.Run({contentBytes: addSPhoto.Media, name: "step.jpg"}, "P" & varProcID & "-S" & varStepNo & ".jpg", varProcID, varStepNo, varIssueID, "Step", txtSInstr.Text, User().Email)),\n'
 ' Notify("STEP NOT SAVED — " & FirstError.Message, NotificationType.Error),\n'
 ' Collect(colStepsDone, {N: varStepNo, T: txtSInstr.Text, Ph: !IsBlank(addSPhoto.Media)});\n'
 ' Notify("Step " & varStepNo & " saved", NotificationType.Success);\n'
 ' Set(varStepNo, varStepNo + 1); Reset(txtSInstr); Reset(txtSKey); Reset(addSPhoto))')
SOK='!IsBlank(txtSInstr.Text)'
out.append(btn("btnSSave",f'If({SOK}, "SAVE STEP " & varStepNo & "  +  NEXT", "DESCRIBE THE STEP")',SAVESTEP,16,Y0+506,W-32,66,fill=f'If({SOK}, {TEAL_D}, {G1})',color=f'If({SOK}, {WHITE}, {G9})',size=15,
   extra={"DisplayMode":F(f'If({SOK}, DisplayMode.Edit, DisplayMode.Disabled)'),"DisabledFill":F(G1),"DisabledColor":F(G9),**RAD}))
need("txtSInstr","IsBlank(Self.Text)")
sk=[label("gSD",'Text(ThisItem.N) & ".  " & ThisItem.T & If(ThisItem.Ph, "   📷", "")',8,2,W-50,36,size=12,color=DARK,indent=6)]
gp={"Items":F("colStepsDone"),"TemplateSize":"=38","TemplatePadding":"=0","BorderColor":F(G1),"BorderThickness":"=1"}; gp.update(box(10,Y0+584,W-20,250))
out.append(ctrl("galSDone","Gallery@2.15.0",gp,0,sk,variant="BrowseLayout_Vertical_TwoTextOneImageVariant_ver5.0"))
out.append(btn("btnSDone",'"✓  DONE — FIX WORKED  ›"','Set(varStep, "log")',16,Y0+846,W-32,70,fill=WHITE,color=TEAL_D,size=16,
   extra={"BorderColor":F(TEAL_D),"BorderThickness":"=2","DisplayMode":F('If(CountRows(colStepsDone) > 0, DisplayMode.Edit, DisplayMode.Disabled)'),"DisabledColor":F(G5),"DisabledBorderColor":F(G1),**RAD}))
P("steps","sT","sC1","txtSInstr","sC2","txtSKey","imgSPrev","addSPhoto","btnSSave","galSDone","btnSDone")

# ---------------- STEP: log ----------------
out.append(label("lT",'"LOG THIS OCCURRENCE"',16,Y0,W-32,44,size=18,bold=True,color=DARK,font="Georgia"))
out.append(label("lSum",'Coalesce(' + ISS + '.Concern, txtNConcern.Text) & Char(10) & Switch(varOutcome, "Existing fix", "Fix used: " & ' + FIX + '.Cause, "New fix added", "NEW fix: " & txtNCause.Text, "NOT RESOLVED — escalated")',
   16,Y0+48,W-32,100,size=14,bold=True,color=DARK,fill=MUTE,extra={"PaddingLeft":"=12","PaddingRight":"=12"}))
out.append(label("lOp",'"⚠  OPERATOR-LEVEL FIX — this is in the guide for operators. It will be flagged \'operator could have fixed it\'."',16,Y0+156,W-32,70,size=12,bold=True,color=DARK,fill=AMBL,
   extra={"PaddingLeft":"=12","PaddingRight":"=12","Visible":F('varStep = "log" && varOutcome = "Existing fix" && varDoneBy = "Operator"')}))
out.append(cap("lC1","REPAIR TIME  (min, hands-on)",16,Y0+236,250))
out.append(ti("txtLDT",'""',16,Y0+256,200,64,'false',hint='"min"',size=24,bold=True))
out.append(label("lBoard",'If(IsBlank(varEventKey), "Not on the board yet. A supervisor will link this to the board downtime.", "Board downtime: " & Text(' + EV + '.Mn) & " min  ·  " & Substitute(' + EV + '.R, "Machine - ", "") & "  ·  " & Right(' + EV + '.SK, 2) & " hour " & ' + EV + '.H1 & If(' + EV + '.H2 > ' + EV + '.H1, "–" & ' + EV + '.H2, ""))',
   16,Y0+188,W-32,44,size=11,bold=True,extra={"Color":F(f'If(IsBlank(varEventKey), {YELB}, {TEAL_D})')}))
out.append(cap("lC2","WORK ORDER #  (optional)",230,Y0+236,W-246))
out.append(ti("txtLWO",'""',230,Y0+256,W-246,64,'false',hint='"WO #"',size=16,number=False))
out.append(cap("lC3","NOTES  (optional)",16,Y0+330,W-32))
out.append(ti("txtLNotes",'""',16,Y0+350,W-32,100,'false',hint='"anything the next person should know"',size=13,number=False,extra={"Align":"=Align.Left","Mode":"=TextMode.MultiLine"}))
# open end: yellow tag (next build)
out.append(btn("btnLYellow",'"🏷  YELLOW TAG A PART  (coming soon)"','false',16,Y0+460,W-32,52,fill=WHITE,color=G5,size=12,
   extra={"DisplayMode":"=DisplayMode.Disabled","DisabledFill":F(WHITE),"DisabledColor":F(G5),"BorderColor":F(G1),"DisabledBorderColor":F(G1),**RAD}))
need("txtLDT","Coalesce(Value(Self.Text), -1) < 0")
LOK='!IsBlank(txtLDT.Text) && Coalesce(Value(txtLDT.Text), -1) >= 0'
SAVELOG=('If(varOutcome = "New fix added",\n'
 ' Patch(TS_Fixes, LookUp(TS_Fixes, ID = varFixID), {Active: true});\n'
 ' Patch(TS_Procedures, LookUp(TS_Procedures, ID = varProcID), {Active: true}));\n'
 'IfError(\n'
 ' Patch(TS_Occurrences, Defaults(TS_Occurrences), {\n'
 '  Ref: ddMLine.Selected.Value & "-" & Text(Now(), "yyyymmdd-hhmmss"), OccurredAt: Now(), Line: ddMLine.Selected.Value,\n'
 '  Asset: If(ddMAsset.Selected.Value = "(any)", "", ddMAsset.Selected.Value), EquipType: varEquip,\n'
 f'  ShiftDate: {SDATE}, Shift: {SHIFT},\n'
 f'  ShiftKey: ddMLine.Selected.Value & "-" & Text({SDATE}, "yyyymmdd") & "-S" & Text({SHIFT}),\n'
 '  IssueID: varIssueID, FixID: varFixID, Outcome: {Value: varOutcome}, FixLevel: varDoneBy,\n'
 '  OperatorCouldFix: varOutcome = "Existing fix" && varDoneBy = "Operator",\n'
 '  RepairMin: Value(txtLDT.Text), EventKey: varEventKey, LinkStatus: {Value: If(IsBlank(varEventKey), "Not on board", "Linked at fix")},\n'
 '  LinkedBy: If(IsBlank(varEventKey), "", User().Email), LinkedAt: If(IsBlank(varEventKey), Blank(), Now()),\n'
 '  LoggedBy: User().Email, Notes: txtLNotes.Text, WorkOrder: txtLWO.Text}),\n'
 ' Notify("NOT SAVED — " & FirstError.Message & "  (try again)", NotificationType.Error),\n'
 ' Notify("Logged. Guide ranking updated.", NotificationType.Success);\n'
 ' Reset(txtLDT); Reset(txtLWO); Reset(txtLNotes); Reset(txtNConcern); Reset(txtNApp); Reset(txtNCause); Reset(txtNCM); Reset(txtNCheck); Reset(txtNNR); Reset(addNApp);\n'
 ' Set(varStep, "done"); Select(btnMRefresh))')
out.append(btn("btnLSave",f'If({LOK}, "SAVE", "ENTER REPAIR TIME")',SAVELOG,16,Y0+530,W-32,76,fill=f'If({LOK}, {TEAL_D}, {G1})',color=f'If({LOK}, {WHITE}, {G9})',size=18,
   extra={"DisplayMode":F(f'If({LOK}, DisplayMode.Edit, DisplayMode.Disabled)'),"DisabledFill":F(G1),"DisabledColor":F(G9),**RAD}))
P("log","lT","lSum","lBoard","lC1","txtLDT","lC2","txtLWO","lC3","txtLNotes","btnLYellow","btnLSave")

# ---------------- STEP: done ----------------
out.append(label("dT",'"✓"',16,Y0+80,W-32,160,size=96,bold=True,color=TEAL_D,align="Center"))
out.append(label("dT2",'"LOGGED"',16,Y0+250,W-32,50,size=24,bold=True,color=DARK,align="Center",font="Georgia"))
out.append(label("dT3",'If(varOutcome = "New fix added", "Your fix is live in the guide — operators can see it now.", "Occurrence counted. The guide re-ranks on the next refresh.")',16,Y0+304,W-32,60,size=13,color=G9,align="Center"))
out.append(btn("btnDAgain",'"LOG ANOTHER"','Set(varStep, "where"); Set(varEquip, Blank()); Set(varEventKey, Blank()); Set(varIssueID, Blank()); Set(varFixID, Blank()); Set(varDoneBy, ""); Reset(txtISearch)',16,Y0+400,W-32,70,fill=TEAL_D,color=WHITE,size=16,extra=RAD))
P("done","dT","dT2","dT3","btnDAgain")
out.append(label("lblLoaded",'If(IsBlank(varLoaded), "Not loaded — tap ↻", "Loaded " & Text(varLoaded, "h:mm AM/PM"))',16,1100,W-32,26,size=10,color=G5,align="Center"))
'''
def image(name,img,x,y,w,h,indent=0):
    d={"Image":F(img),"ImagePosition":"=ImagePosition.Fit","Fill":F(MUTE)}; d.update(box(x,y,w,h)); return ctrl(name,"Image@2.2.3",d,indent)
for _ in range(2):
    out=[]
    exec(BODY)
write_themed(__import__("os").environ.get("MTOUT","/mnt/user-data/outputs/TS_Maintenance_v5.pa.yaml"), "".join(out))
print("ok", len(out))
