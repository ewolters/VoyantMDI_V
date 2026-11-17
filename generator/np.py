# Generates Newspaper_v7.pa.yaml — NEWSPAPER action register (1920x1080)
exec(open("/tmp/claude-0/gen/theme.py").read())
src=open('/tmp/claude-0/gen/build6.py').read()
exec(src[:src.index("DT_OLD=")])
EXTRA.clear()
MUTE="RGBA(243, 244, 244, 1)"; PANEL="RGBA(248, 249, 249, 1)"; YEL="RGBA(255, 242, 179, 1)"; YELB="RGBA(210, 153, 34, 1)"; AMBL="RGBA(253, 236, 200, 1)"
RAD={"RadiusTopLeft":"=6","RadiusTopRight":"=6","RadiusBottomLeft":"=6","RadiusBottomRight":"=6"}
FLOW="'MDI-UploadPhoto'"
exec(open("/tmp/claude-0/gen/harvey.py").read())

BODY=r'''
def rect(name,fill,x,y,w,h,indent=0,extra=None):
    d={"Fill":F(fill)}; d.update(box(x,y,w,h))
    if extra: d.update(extra)
    return ctrl(name,"Rectangle@2.3.0",d,indent)
def image(name,img,x,y,w,h,indent=0,extra=None):
    d={"Image":F(img),"ImagePosition":"=ImagePosition.Fit","Fill":F(MUTE)}; d.update(box(x,y,w,h))
    if extra: d.update(extra)
    return ctrl(name,"Image@2.2.3",d,indent)
def txt(name,default,x,y,w,h,hint='""',multi=False,size=13,onchange='false'):
    ex={"Align":"=Align.Left"}
    if multi: ex["Mode"]="=TextMode.MultiLine"
    return ti(name,default,x,y,w,h,onchange,hint=hint,size=size,number=False,extra=ex)
def tip(name,text): EXTRA.setdefault(name,{})["Tooltip"]='="'+text.replace('"','""')+'"'
OPEN='(Status.Value = "Open" || Status.Value = "In progress")'
OVER=f'({OPEN} && !IsBlank(DueDate) && DueDate < Today())'
SEL='LookUp(colNews, ID = varNID)'

# header
out.append(rect("hdrBar",DARK,0,0,1920,90))
out.append(label("lblBrand",'"voyant"',24,6,170,52,size=34,color=WHITE,font="Georgia"))
out.append(label("lblBrandSub",'"NEW ALBANY"',27,56,170,24,size=10,bold=True,color=TEAL))
out.append(label("lblTitle",'"NEWSPAPER"',190,20,260,50,size=26,bold=True,color=WHITE,font="Georgia"))
out.append(label("lblSub",'"action register  ·  who · what · by when"',430,32,360,30,size=12,color=G5))
LOAD=('IfError(ClearCollect(colNews, Filter(Newspaper, Status.Value = "Open" || Status.Value = "In progress" || ClosedDate >= DateAdd(Today(), -60, TimeUnit.Days))), Notify("Could not load Newspaper — " & FirstError.Message, NotificationType.Error));\n'
 'IfError(ClearCollect(colPeople, Filter(People, Active = true)), Notify("Could not load People", NotificationType.Warning));\n'
 'ClearCollect(colLines, Lines);\n'
 'Set(varLoaded, Now())')
out.append(btn("btnNRefresh",'"REFRESH"',LOAD,1500,22,130,48,fill=TEAL_D,color=WHITE,size=13,extra=RAD))
out.append(btn("btnNNew",'"+  NEW ACTION"','Set(varNID, Blank()); Set(varNNew, true); Clear(colActPh); Select(btnNReset)',1640,22,200,48,fill=TEAL,color=DARK,size=14,extra=RAD))
out.append(label("lblNLoaded",'If(IsBlank(varLoaded), "Not loaded", Text(varLoaded, "h:mm AM/PM"))',1846,30,70,30,size=9,color=G5))

# filters
FY=98
out.append(dd("ddFLine",'Ungroup(Table({t: Table({Value: "All lines"})}, {t: ForAll(SortByColumns(colLines, "DisplayOrder"), {Value: Line})}), t)',12,FY,170,44,default='Coalesce(Param("line"), "All lines")',size=13))
out.append(dd("ddFSrc",'["All sources", "Escalation", "Tier 2", "Board", "QA", "Maintenance", "Ops", "Troubleshooting", "Yellow tag", "Process confirmation", "HxH", "Other"]',190,FY,210,44,default='"All sources"',size=13))
out.append(dd("ddFQ",'["All SQDCP", "Safety", "Quality", "Delivery", "Cost", "People"]',408,FY,170,44,default='"All SQDCP"',size=13))
out.append(dd("ddFStat",'["Open + In progress", "All", "Open", "In progress", "Done", "Canceled"]',586,FY,210,44,default='"Open + In progress"',size=13))
out.append(txt("txtFSearch",'""',804,FY,300,44,hint='"search action, owner, problem…"'))
out.append(btn("btnFOver",'If(varOverOnly, "● OVERDUE ONLY", "○ OVERDUE ONLY")','Set(varOverOnly, !varOverOnly)',1112,FY,190,44,fill=f'If(varOverOnly, {RED}, {WHITE})',color=f'If(varOverOnly, {WHITE}, {RED})',size=12,extra={"BorderColor":F(RED),"BorderThickness":"=1",**RAD}))
out.append(btn("btnFMine",'If(varMine, "● MINE", "○ MINE")','Set(varMine, !varMine)',1310,FY,110,44,fill=f'If(varMine, {TEAL_D}, {WHITE})',color=f'If(varMine, {WHITE}, {TEAL_D})',size=12,extra={"BorderColor":F(TEAL_D),"BorderThickness":"=1",**RAD}))
FILT=('Filter(colNews,\n'
 ' (ddFLine.Selected.Value = "All lines" || Line = ddFLine.Selected.Value) &&\n'
 ' (ddFSrc.Selected.Value = "All sources" || Source.Value = ddFSrc.Selected.Value) &&\n'
 ' (ddFQ.Selected.Value = "All SQDCP" || SQDCP.Value = ddFQ.Selected.Value) &&\n'
 f' (ddFStat.Selected.Value = "All" || (ddFStat.Selected.Value = "Open + In progress" && {OPEN}) || Status.Value = ddFStat.Selected.Value) &&\n'
 f' (!varOverOnly || {OVER}) && (!varMine || OwnerEmail = User().Email) &&\n'
 ' (IsBlank(txtFSearch.Text) || txtFSearch.Text in Action || txtFSearch.Text in Owner || txtFSearch.Text in Problem || txtFSearch.Text in RefKey))')

# KPIs
KY=150; TW=228
def tile(name,capn,val,x,col=None):
    out.append(label(name,val,x,KY,TW,96,size=30,bold=True,color=DARK,fill=MUTE,align="Center",valign="Bottom",pb=8,extra=({"Color":F(col)} if col else None)))
    out.append(label(name+"C",f'"{capn}"',x,KY+6,TW,22,size=10,bold=True,color=G9,align="Center"))
LF='Filter(colNews, ddFLine.Selected.Value = "All lines" || Line = ddFLine.Selected.Value)'
tile("kNOpen","OPEN",f'Text(CountRows(Filter({LF}, {OPEN})))',12)
tile("kNOver","OVERDUE",f'Text(CountRows(Filter({LF}, {OVER})))',12+(TW+8),col=f'If(CountRows(Filter({LF}, {OVER})) > 0, {RED}, {DARK})')
tile("kNWeek","DUE NEXT 7 DAYS",f'Text(CountRows(Filter({LF}, {OPEN} && !IsBlank(DueDate) && DueDate >= Today() && DueDate <= DateAdd(Today(), 7, TimeUnit.Days))))',12+2*(TW+8))
tile("kNDone","CLOSED LAST 7 DAYS",f'Text(CountRows(Filter({LF}, Status.Value = "Done" && ClosedDate >= DateAdd(Today(), -7, TimeUnit.Days))))',12+3*(TW+8))
tile("kNAge","AVG DAYS TO CLOSE (30d)",f'With({{c: Filter({LF}, Status.Value = "Done" && ClosedDate >= DateAdd(Today(), -30, TimeUnit.Days) && !IsBlank(RaisedDate))}}, If(CountRows(c) = 0, "—", Text(Average(c, DateDiff(RaisedDate, ClosedDate, TimeUnit.Days)), "0.0")))',12+4*(TW+8))

# list
LY=256; LW=1180
hdr=[("SQDCP",0,64),("ACTION / PROBLEM",72,470),("LINE",548,70),("SOURCE",622,150),("OWNER",776,150),("DUE",930,110),("PROGRESS",1046,124)]
out.append(rect("lHdr",TEAL_D,12,LY,LW,30))
for i,(t,x,w) in enumerate(hdr): out.append(label(f"lh{i}",f'"{t}"',20+x,LY,w,30,size=9,bold=True,color=WHITE))
NSEL='(ThisItem.ID = varNID)'
DUECOL=f'If(!(ThisItem.Status.Value = "Open" || ThisItem.Status.Value = "In progress") || IsBlank(ThisItem.DueDate), {G9}, ThisItem.DueDate < Today(), {RED}, ThisItem.DueDate <= DateAdd(Today(), 2, TimeUnit.Days), {AMBER}, {DARK})'
STFILL=f'Switch(ThisItem.Status.Value, "Open", {TEAL}, "In progress", {TEAL_D}, "Done", {GREEN}, {G5})'
nk=[rect("gNBg",WHITE,0,0,LW,84,indent=6,extra={"Fill":F(f'If({NSEL}, RGBA(229, 243, 243, 1), {WHITE})'),"BorderColor":F(G1),"BorderThickness":"=1"}),
    label("gNQ",'Left(Coalesce(ThisItem.SQDCP.Value, "?"), 1)',8,12,56,56,size=24,bold=True,color=WHITE,align="Center",fill=DARK,indent=6),
    label("gNAct",'ThisItem.Action',80,4,466,40,size=13,bold=True,color=DARK,indent=6),
    label("gNProb",'Coalesce(ThisItem.Problem, "")',80,42,466,38,size=10,color=G9,indent=6,extra={"VerticalAlign":"=VerticalAlign.Top"}),
    label("gNLine",'ThisItem.Line',556,22,64,36,size=13,bold=True,color=DARK,indent=6),
    label("gNSrc",'ThisItem.Source.Value',630,22,146,36,size=11,color=G9,indent=6),
    label("gNOwn",'If(IsBlank(ThisItem.Owner), "— unassigned", ThisItem.Owner)',784,22,146,36,size=12,indent=6,extra={"Color":F(f'If(IsBlank(ThisItem.Owner), {RED}, {DARK})')}),
    label("gNDue",'If(IsBlank(ThisItem.DueDate), "—", Text(ThisItem.DueDate, "m/d") & If(ThisItem.DueDate < Today() && (ThisItem.Status.Value = "Open" || ThisItem.Status.Value = "In progress"), "  LATE", ""))',938,22,110,36,size=13,bold=True,indent=6,extra={"Color":F(DUECOL)}),
    btn("gNSel",'""','Set(varNID, ThisItem.ID); Set(varNNew, false); Select(btnNReset)',0,0,1050,84,fill=CLEAR,color=CLEAR,indent=6,
        extra={"HoverFill":F("RGBA(0, 72, 81, 0.05)"),"PressedFill":F("RGBA(0, 72, 81, 0.1)"),"BorderColor":F(CLEAR)}),
    ctrl("gNHb","Image@2.2.3",{"Image":F(HB_EXPR(PROG("ThisItem"), 'ThisItem.DueDate < Today() && (ThisItem.Status.Value = "Open" || ThisItem.Status.Value = "In progress")', "ThisItem.Status.Value")),"ImagePosition":"=ImagePosition.Fit","X":"=1060","Y":"=20","Width":"=44","Height":"=44"},6),
    label("gNPct",'If(ThisItem.Status.Value = "Canceled", "canceled", Text('+PROG("ThisItem")+') & "%")',1108,20,66,44,size=11,bold=True,color=DARK,indent=6),
    btn("gNStat",'""',CYCLE_PATCH("ThisItem",'Patch(colNews, LookUp(colNews, ID = ThisItem.ID), {Progress: nx, Status: {Value: st}, ClosedDate: If(nx = 100, Now(), Blank())})'),
        1054,14,120,56,fill=CLEAR,color=CLEAR,size=11,indent=6,extra={"HoverFill":F("RGBA(0, 72, 81, 0.08)"),"PressedFill":F("RGBA(0, 72, 81, 0.15)"),"BorderColor":F(CLEAR),"Tooltip":'="Tap to step progress: 0 → 25 → 50 → 75 → 100% (Done)"'})]
gp={"Items":F(f'SortByColumns(AddColumns({FILT}, Late, If({OVER}, 0, 1), DueSort, Coalesce(DueDate, Date(2099, 1, 1))), "Late", SortOrder.Ascending, "DueSort", SortOrder.Ascending)'),
    "TemplateSize":"=88","TemplatePadding":"=0"}; gp.update(box(12,LY+30,LW,780))
out.append(ctrl("galNews","Gallery@2.15.0",gp,0,nk,variant="BrowseLayout_Vertical_TwoTextOneImageVariant_ver5.0"))
out.append(label("lNone",'"Nothing matches these filters."',24,LY+50,LW-40,30,size=13,color=G5,extra={"Visible":"=CountRows(galNews.AllItems) = 0"}))

# detail / edit panel
DX=1204; DW=704
out.append(rect("dBg",PANEL,DX,150,DW,920))
VIS='(varNNew || !IsBlank(varNID))'
D=[]
out.append(label("dT",'If(varNNew, "NEW ACTION", If(IsBlank(varNID), "← Pick an action to see or update it", "ACTION #" & varNID))',DX+16,156,DW-32,32,size=15,bold=True,color=DARK,font="Georgia"))
DV=lambda f,d='""': f'If(varNNew, {d}, Coalesce({SEL}.{f}, {d}))'
def f(capn,name,ctrl_):
    out.append(cap("c"+name,capn,*ctrl_[1])); out.append(ctrl_[0]); D.extend(["c"+name,name])
out.append(cap("cNAct","ACTION — what will be done *",DX+16,192,DW-32)); out.append(txt("txtNAct",DV("Action"),DX+16,212,DW-32,44)); D+=["cNAct","txtNAct"]
out.append(cap("cNProb","PROBLEM — what happened",DX+16,262,DW-32)); out.append(txt("txtNProb",DV("Problem"),DX+16,282,DW-32,70,multi=True,size=12)); D+=["cNProb","txtNProb"]
out.append(cap("cNCM","COUNTERMEASURE / RESULT",DX+16,358,DW-32)); out.append(txt("txtNCM",DV("Countermeasure"),DX+16,378,DW-32,70,multi=True,size=12)); D+=["cNCM","txtNCM"]
out.append(cap("cNOwn","OWNER",DX+16,454,320))
out.append(dd("ddNOwn",'Ungroup(Table({t: Table({Value: "(unassigned)", Email: ""})}, {t: ForAll(SortByColumns(colPeople, "Title"), {Value: Title, Email: Email})}), t)',DX+16,474,320,44,
   default=f'If(varNNew || IsBlank({SEL}.Owner), "(unassigned)", {SEL}.Owner)',size=13)); D+=["cNOwn","ddNOwn"]
out.append(cap("cNDue","DUE (yyyy-mm-dd)",DX+346,454,170)); out.append(txt("txtNDue",f'If(varNNew, Text(DateAdd(Today(), 7, TimeUnit.Days), "yyyy-mm-dd"), If(IsBlank({SEL}.DueDate), "", Text({SEL}.DueDate, "yyyy-mm-dd")))',DX+346,474,170,44)); D+=["cNDue","txtNDue"]
out.append(cap("cNLine","LINE",DX+526,454,162)); out.append(txt("txtNLine",DV("Line",'If(ddFLine.Selected.Value = "All lines", "", ddFLine.Selected.Value)'),DX+526,474,162,44)); D+=["cNLine","txtNLine"]
out.append(cap("cNQ","SQDCP",DX+16,524,220)); out.append(dd("ddNQ",'["Safety", "Quality", "Delivery", "Cost", "People"]',DX+16,544,220,44,default=f'If(varNNew, "Quality", {SEL}.SQDCP.Value)',size=13)); D+=["cNQ","ddNQ"]
out.append(cap("cNSrc","SOURCE",DX+246,524,260)); out.append(dd("ddNSrc",'["Tier 2", "Board", "Escalation", "QA", "Maintenance", "Ops", "Troubleshooting", "Yellow tag", "Process confirmation", "HxH", "Other"]',DX+246,544,260,44,default=f'If(varNNew, "Tier 2", {SEL}.Source.Value)',size=13)); D+=["cNSrc","ddNSrc"]
out.append(label("lNRef",f'If(varNNew || IsBlank({SEL}.RefKey), "", "Ref: " & {SEL}.RefKey)',DX+516,544,172,44,size=9,color=G9)); D.append("lNRef")
out.append(cap("cNStat","PROGRESS  (tap a ball)",DX+16,594,DW-32)); D.append("cNStat")
for i,pv in enumerate((0,25,50,75,100)):
    out.append(ctrl(f"imgNP{i}","Image@2.2.3",{"Image":F(f'If(varNProg = {pv} && varNStat <> "Canceled", "{(HB_DONE if pv==100 else HB_OK[pv])}", "{_svg(pv, "#B1B3B3", "#B1B3B3")}")'),"ImagePosition":"=ImagePosition.Fit",
        "X":F(str(DX+16+i*96)),"Y":"=614","Width":"=48","Height":"=48"},0)); D.append(f"imgNP{i}")
    out.append(label(f"lNP{i}",f'"{pv}%"',DX+66+i*96,614,44,48,size=11,bold=True,extra={"Color":F(f'If(varNProg = {pv} && varNStat <> "Canceled", {DARK}, {G5})')})); D.append(f"lNP{i}")
    out.append(btn(f"btnNS{i}",'""',f'Set(varNProg, {pv}); Set(varNStat, If({pv} = 0, "Open", {pv} = 100, "Done", "In progress"))',DX+12+i*96,610,92,56,fill=CLEAR,color=CLEAR,size=11,
       extra={"HoverFill":F("RGBA(0, 72, 81, 0.08)"),"BorderColor":F(CLEAR)})); D.append(f"btnNS{i}")
out.append(btn("btnNS5",'"Canceled"','Set(varNStat, If(varNStat = "Canceled", If(varNProg = 0, "Open", varNProg = 100, "Done", "In progress"), "Canceled"))',DX+DW-170,614,154,48,
   fill=f'If(varNStat = "Canceled", {G5}, {WHITE})',color=f'If(varNStat = "Canceled", {WHITE}, {DARK})',size=13,extra={"BorderColor":F(G5),"BorderThickness":"=2",**RAD,"Tooltip":'="Mark canceled (tap again to undo)"'})); D.append("btnNS5")
NREC=('{Action: txtNAct.Text, Problem: txtNProb.Text, Countermeasure: txtNCM.Text,\n'
      ' Owner: If(ddNOwn.Selected.Value = "(unassigned)", "", ddNOwn.Selected.Value), OwnerEmail: ddNOwn.Selected.Email,\n'
      ' DueDate: If(IsBlank(txtNDue.Text), Blank(), DateValue(txtNDue.Text)), Line: txtNLine.Text,\n'
      ' ValueStream: Coalesce(LookUp(colLines, Line = txtNLine.Text).ValueStream, ""),\n'
      ' SQDCP: {Value: ddNQ.Selected.Value}, Source: {Value: ddNSrc.Selected.Value}, Status: {Value: varNStat}, Progress: varNProg,\n'
      ' ClosedDate: If(varNStat = "Done", Coalesce(' + SEL + '.ClosedDate, Now()), Blank())}')
SAVE=('IfError(\n'
 ' If(varNNew,\n'
 '  Set(varNID, Patch(Newspaper, Defaults(Newspaper), ' + NREC + ', {RaisedDate: Now(), RefKey: "N" & Text(Now(), "yyyymmdd-hhmmss")}).ID); Set(varNNew, false),\n'
 '  Patch(Newspaper, LookUp(Newspaper, ID = varNID), ' + NREC + '));\n'
 ' If(!IsBlank(addNPh.Media), Patch(TS_Photos, LookUp(TS_Photos, ID = Value(' + FLOW + '.Run({contentBytes: addNPh.Media, name: "act.jpg"}, "N" & varNID & ".jpg", varNID, 0, 0, "After", txtNAct.Text, User().Email).photoid)),\n'
 '   {Module: {Value: "Newspaper"}, RefID: varNID})),\n'
 ' Notify("NOT SAVED — " & FirstError.Message, NotificationType.Error),\n'
 ' Notify("Action saved", NotificationType.Success); Select(btnNRefresh); Select(btnNReset))')
NOK='!IsBlank(txtNAct.Text) && (IsBlank(txtNDue.Text) || !IsError(DateValue(txtNDue.Text)))'
out.append(btn("btnNSave",f'If({NOK}, "SAVE", "ACTION REQUIRED")',SAVE,DX+16,676,320,58,fill=f'If({NOK}, {TEAL_D}, {G1})',color=f'If({NOK}, {WHITE}, {G9})',size=15,
   extra={"DisplayMode":F(f'If({NOK}, DisplayMode.Edit, DisplayMode.Disabled)'),"DisabledFill":F(G1),"DisabledColor":F(G9),**RAD})); D.append("btnNSave")
out.append(ctrl("addNPh","AddMedia@2.2.1",{"X":F(str(DX+346)),"Y":"=676","Width":F(str(DW-362)),"Height":"=58","Size":"=12",
   "Text":F('If(IsBlank(Self.Media), "📷  ADD PHOTO (saved with SAVE)", "✓  PHOTO READY — press SAVE")'),"Fill":F(MUTE),"Color":F(TEAL_D),"BorderColor":F(G5),"BorderThickness":"=1"})); D.append("addNPh")
out.append(label("lNPhT",'"PHOTOS  (" & CountRows(colActPh) & ")"',DX+16,744,DW-32,24,size=10,bold=True,color=G9)); D.append("lNPhT")
pk=[image("gNPh",'ThisItem.Thumbnail.Large',4,4,212,150,indent=6)]
gp={"Items":F('SortByColumns(colActPh, "Created", SortOrder.Descending)'),"WrapCount":"=3","TemplateSize":"=160","TemplatePadding":"=0"}; gp.update(box(DX+10,768,DW-20,296))
out.append(ctrl("galNPh","Gallery@2.15.0",gp,0,pk,variant="BrowseLayout_Vertical_TwoTextOneImageVariant_ver5.0")); D.append("galNPh")
for n in D: EXTRA.setdefault(n,{})["Visible"]=F(VIS)

# helper: load selected action into the form + its photos (own photos, or the PC finding photo it came from)
RESET=('Reset(txtNAct); Reset(txtNProb); Reset(txtNCM); Reset(ddNOwn); Reset(txtNDue); Reset(txtNLine); Reset(ddNQ); Reset(ddNSrc); Reset(addNPh);\n'
 'Set(varNStat, If(varNNew, "Open", ' + SEL + '.Status.Value));\n'
 'Set(varNProg, If(varNNew, 0, ' + PROG(SEL) + '));\n'
 'If(varNNew || IsBlank(varNID), Clear(colActPh),\n'
 ' With({k: Coalesce(' + SEL + '.RefKey, "")},\n'
 '  If(' + SEL + '.Source.Value = "Process confirmation" && "-I" in k,\n'
 '   With({p: Last(Split(k, "-I")).Value, r: Left(k, Len(k) - Len(Last(Split(k, "-I")).Value) - 2)},\n'
 '    ClearCollect(colActPh, Filter(TS_Photos, Module.Value = "Process confirmation" && RefID = LookUp(PC_Audits, Ref = r).ID && StepNo = Value(p)))),\n'
 '   Clear(colActPh));\n'
 '  Collect(colActPh, Filter(TS_Photos, Module.Value = "Newspaper" && RefID = varNID))))')
HELP={"Color":F(CLEAR),"BorderColor":F(CLEAR),"HoverFill":F(CLEAR),"PressedFill":F(CLEAR),"TabIndex":"=-1"}
out.append(btn("btnNReset",'""',RESET,0,1079,1,1,fill=CLEAR,color=CLEAR,extra=HELP))
'''
for _ in range(2):
    out=[]
    exec(BODY)
write_themed("/mnt/user-data/outputs/Newspaper_v7.pa.yaml", "".join(out))
print("ok", len(out))
