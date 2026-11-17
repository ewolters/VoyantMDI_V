# Generates PC_Audit_v2.pa.yaml — phone (640x1136) process confirmation (T-card) audits
exec(open("/tmp/claude-0/gen/theme.py").read())
src=open('/tmp/claude-0/gen/build6.py').read()
exec(src[:src.index("DT_OLD=")])
EXTRA.clear()
MUTE="RGBA(243, 244, 244, 1)"; YEL="RGBA(255, 242, 179, 1)"; YELB="RGBA(210, 153, 34, 1)"
LGREEN="RGBA(220, 242, 225, 1)"; LRED="RGBA(249, 214, 213, 1)"
RAD={"RadiusTopLeft":"=8","RadiusTopRight":"=8","RadiusBottomLeft":"=8","RadiusBottomRight":"=8"}
W=640; FLOW="'MDI-UploadPhoto'"

BODY=r'''
def rect(name,fill,x,y,w,h,indent=0,extra=None):
    d={"Fill":F(fill)}; d.update(box(x,y,w,h))
    if extra: d.update(extra)
    return ctrl(name,"Rectangle@2.3.0",d,indent)
def image(name,img,x,y,w,h,indent=0,extra=None):
    d={"Image":F(img),"ImagePosition":"=ImagePosition.Fit","Fill":F(MUTE)}; d.update(box(x,y,w,h))
    if extra: d.update(extra)
    return ctrl(name,"Image@2.2.3",d,indent)
def tip(name,text): EXTRA.setdefault(name,{})["Tooltip"]='="'+text.replace('"','""')+'"'
def P(step,*names):
    for n in names: EXTRA.setdefault(n,{})["Visible"]=F(f'varStep = "{step}"')
SHIFT='If(Hour(Now()) * 60 + Minute(Now()) >= 360 && Hour(Now()) * 60 + Minute(Now()) < 990, 1, 2)'
SDATE='If(Hour(Now()) < 6, DateAdd(Today(), -1, TimeUnit.Days), Today())'
SKEY=f'ddPLine.Selected.Value & "-" & Text({SDATE}, "yyyymmdd") & "-S" & Text({SHIFT})'
CARD='LookUp(colCards, ID = varCardID)'
CUR='LookUp(colItems, ItemNo = varItem)'
ANS='LookUp(colAns, ItemNo = varItem)'
N='CountRows(colItems)'

# header
out.append(rect("hdrBar",DARK,0,0,W,118))
out.append(label("lblBrand",'"voyant"',16,4,140,40,size=22,color=WHITE,font="Georgia"))
out.append(label("lblTitle",'"PROCESS CONFIRMATION"',150,8,400,36,size=17,bold=True,color=WHITE,font="Georgia"))
out.append(label("lblCtx",'ddPLine.Selected.Value & "  ·  S" & Text(' + SHIFT + ') & "  ·  " & Text(' + SDATE + ', "ddd m/d") & If(IsBlank(varCardID), "", "  ·  Tier " & ' + CARD + '.Tier)',16,50,W-32,30,size=14,bold=True,color=AQUA))
out.append(label("lblUser",'User().FullName',16,82,W-240,26,size=11,color=G5))
LOAD=('IfError(ClearCollect(colCards, Filter(PC_Cards, Active = true)), Notify("Could not load PC_Cards — " & FirstError.Message, NotificationType.Error));\n'
 'ClearCollect(colLines, Lines);\n'
 'IfError(ClearCollect(colDone, Filter(PC_Audits, ShiftDate >= DateAdd(Today(), -8, TimeUnit.Days))), Notify("Could not load PC_Audits", NotificationType.Warning));\n'
 'If(!varParamUsed && !IsBlank(Param("card")), Set(varCardID, Value(Param("card"))); Select(btnPStart));\n'
 'Set(varParamUsed, true);\n'
 'If(IsBlank(varStep), Set(varStep, "pick"));\n'
 'Set(varLoaded, Now())')
out.append(btn("btnPRefresh",'"↻"',LOAD,W-70,72,54,38,fill=TEAL_D,color=WHITE,size=16,extra=RAD))
out.append(btn("btnPBack",'"‹ CARDS"','Set(varStep, "pick")',W-190,72,110,38,fill=TEAL_D,color=WHITE,size=12,extra={**RAD,"Visible":F('varStep = "audit" || varStep = "review"')}))

Y0=130
# ---- pick ----
out.append(label("kT",'"WHICH CARD?"',16,Y0,300,40,size=18,bold=True,color=DARK,font="Georgia"))
out.append(dd("ddPLine",'Ungroup(Table({t: Table({Value: "All"})}, {t: ForAll(SortByColumns(colLines, "DisplayOrder"), {Value: Line})}), t)',W-216,Y0,200,48,default='Coalesce(Param("line"), "All")',size=16,bold=True))
CARDS=('SortByColumns(ForAll(Filter(colCards, ddPLine.Selected.Value = "All" || Line = "All" || IsBlank(Line) || Line = ddPLine.Selected.Value) As c,\n'
       ' {ID: c.ID, Card: c.Card, Tier: c.Tier, Freq: c.Frequency.Value, Line: c.Line, Area: c.Area,\n'
       '  DoneNow: CountRows(Filter(colDone, CardID = c.ID && ShiftKey = ' + SKEY + ')) > 0}), "DoneNow", SortOrder.Ascending, "Tier", SortOrder.Ascending)')
ck=[rect("gKBg",WHITE,0,0,W-20,112,indent=6,extra={"BorderColor":F(G1),"BorderThickness":"=1"}),
    rect("gKTab","If(ThisItem.DoneNow, RGBA(46, 160, 67, 1), RGBA(207, 34, 46, 1))",0,0,14,112,indent=6),
    label("gKName",'ThisItem.Card',26,6,W-200,52,size=15,bold=True,color=DARK,indent=6),
    label("gKSub",'"Tier " & ThisItem.Tier & "  ·  " & ThisItem.Freq & "  ·  " & Coalesce(ThisItem.Line, "") & If(IsBlank(ThisItem.Area), "", " · " & ThisItem.Area)',26,58,W-200,40,size=11,color=G9,indent=6),
    label("gKState",'If(ThisItem.DoneNow, "DONE ✓", "DUE")',W-160,30,120,44,size=14,bold=True,align="Center",indent=6,
          color=WHITE,fill='If(ThisItem.DoneNow, RGBA(46, 160, 67, 1), RGBA(207, 34, 46, 1))'),
    btn("gKSel",'""','Set(varCardID, ThisItem.ID); Select(btnPStart)',0,0,W-20,112,fill=CLEAR,color=CLEAR,indent=6,
        extra={"HoverFill":F("RGBA(0, 72, 81, 0.06)"),"PressedFill":F("RGBA(0, 72, 81, 0.12)"),"BorderColor":F(CLEAR)})]
gp={"Items":F(CARDS),"TemplateSize":"=120","TemplatePadding":"=0"}; gp.update(box(10,Y0+58,W-20,900))
out.append(ctrl("galCards","Gallery@2.15.0",gp,0,ck,variant="BrowseLayout_Vertical_TwoTextOneImageVariant_ver5.0"))
out.append(label("kNone",'"No cards for this line. Cards are built in the Standard Work app."',16,Y0+70,W-32,60,size=13,color=G9,extra={"Visible":F('varStep = "pick" && CountRows(galCards.AllItems) = 0')}))
P("pick","kT","ddPLine","galCards")

# ---- audit ----
out.append(label("aCard",CARD+'.Card',16,Y0,W-32,40,size=14,bold=True,color=G9))
out.append(rect("aBarBg",G1,16,Y0+42,W-32,10))
out.append(rect("aBar",TEAL_D,16,Y0+42,1,10,extra={"Width":F(f'(W_-32) * (varItem - 1) / Max(1, {N})'.replace("W_",str(W)))}))
out.append(label("aCount",'"ITEM " & varItem & " OF " & ' + N,16,Y0+56,300,30,size=12,bold=True,color=TEAL_D))
out.append(label("aType",CUR+'.PType',W-160,Y0+56,144,28,size=11,bold=True,color=WHITE,align="Center",
   fill=f'If({CUR}.PType = "Safety", {RED}, {CUR}.PType = "Quality", {TEAL_D}, {G9})'))
out.append(label("aSection",CUR+'.Section',16,Y0+88,W-32,52,size=18,bold=True,color=DARK,font="Georgia"))
out.append(label("aCheck",'If(' + CUR + '.Check = ' + CUR + '.Good, "", ' + CUR + '.Check)',16,Y0+140,W-32,40,size=14,color=DARK))
out.append(image("aRef",'First(SortByColumns(Filter(colRefPh, StepNo = ' + CUR + '.ElNo), "Created", SortOrder.Descending)).Thumbnail.Large',16,Y0+182,W-32,250))
out.append(label("aRefNone",'"(no standard photo yet)"',16,Y0+290,W-32,30,size=11,color=G5,align="Center",extra={"Visible":F(f'varStep = "audit" && IsBlank(LookUp(colRefPh, StepNo = {CUR}.ElNo))')}))
out.append(label("aGood",'"GOOD:  " & ' + CUR + '.Good',16,Y0+438,W-32,92,size=13,bold=True,color=DARK,fill=LGREEN,extra={"PaddingLeft":"=12","PaddingRight":"=12","VerticalAlign":"=VerticalAlign.Top","PaddingTop":"=8"}))
def ab(name,txt,val,x,w,col):
    sel=f'{ANS}.Answer = "{val}"'
    out.append(btn(name,f'"{txt}"',f'Patch(colAns, {ANS}, {{Answer: "{val}"}})',x,Y0+540,w,84,fill=f'If({sel}, {col}, {WHITE})',color=f'If({sel}, {WHITE}, {col})',size=22,
       extra={"BorderColor":F(col),"BorderThickness":"=3",**RAD}))
ab("btnYes","YES","Yes",16,250,GREEN); ab("btnNo","NO","No",276,230,RED); ab("btnNA","N/A","N/A",516,108,G9)
ISNO=f'{ANS}.Answer = "No"'
out.append(cap("aCMiss","IF NO — WHAT WAS MISSED?",16,Y0+632,W-32,color=RED))
out.append(ti("txtMiss",ANS+'.Missed',16,Y0+652,W-32,80,f'Patch(colAns, {ANS}, {{Missed: Self.Text}})',hint='"what was missing or wrong"',size=14,number=False,
   extra={"Align":"=Align.Left","Mode":"=TextMode.MultiLine","Fill":F(f'If(IsBlank(Self.Text), {YEL}, {WHITE})'),"BorderColor":F(f'If(IsBlank(Self.Text), {YELB}, {G5})'),"BorderThickness":F('If(IsBlank(Self.Text), 3, 1)')}))
out.append(ctrl("addPh","AddMedia@2.2.1",{"X":"=16","Y":F(str(Y0+740)),"Width":"=300","Height":"=60","Size":"=13",
   "Text":F('If(IsEmpty(Filter(colPhotos, ItemNo = varItem)), "📷  PHOTO OF THE FINDING", "✓  PHOTO TAKEN (tap to retake)")'),
   "Fill":F(MUTE),"Color":F(TEAL_D),"BorderColor":F(G5),"BorderThickness":"=1",
   "OnChange":F('RemoveIf(colPhotos, ItemNo = varItem); Collect(colPhotos, {ItemNo: varItem, Ph: Self.Media})')}))
out.append(btn("btnAct",'If(' + ANS + '.Act, "☑  CREATE ACTION", "☐  CREATE ACTION")','Patch(colAns, ' + ANS + ', {Act: !' + ANS + '.Act})',330,Y0+740,W-346,60,
   fill=WHITE,color=TEAL_D,size=13,extra={"BorderColor":F(TEAL_D),"BorderThickness":"=1",**RAD,"Tooltip":'="Adds a NEWSPAPER action for this finding when the card is submitted."'}))
for n in ["aCMiss","txtMiss","addPh","btnAct"]: EXTRA.setdefault(n,{})["Visible"]=F(f'varStep = "audit" && {ISNO}')
OKI=f'!IsBlank({ANS}.Answer) && ({ANS}.Answer <> "No" || !IsBlank(txtMiss.Text))'
out.append(btn("btnPrev",'"‹ PREV"',f'Patch(colAns, {ANS}, {{Missed: txtMiss.Text}}); Set(varItem, Max(1, varItem - 1)); Reset(addPh); Reset(txtMiss)',16,Y0+820,180,74,fill=WHITE,color=TEAL_D,size=16,
   extra={"BorderColor":F(TEAL_D),"BorderThickness":"=2","DisplayMode":F('If(varItem > 1, DisplayMode.Edit, DisplayMode.Disabled)'),"DisabledColor":F(G5),"DisabledBorderColor":F(G1),**RAD}))
out.append(btn("btnNext",f'If(varItem < {N}, "NEXT ›", "REVIEW ›")',f'Patch(colAns, {ANS}, {{Missed: txtMiss.Text}}); If(varItem < {N}, Set(varItem, varItem + 1), Set(varStep, "review")); Reset(addPh); Reset(txtMiss)',
   210,Y0+820,W-226,74,fill=f'If({OKI}, {TEAL_D}, {G1})',color=f'If({OKI}, {WHITE}, {G9})',size=18,
   extra={"DisplayMode":F(f'If({OKI}, DisplayMode.Edit, DisplayMode.Disabled)'),"DisabledFill":F(G1),"DisabledColor":F(G9),**RAD}))
P("audit","aCard","aBarBg","aBar","aCount","aType","aSection","aCheck","aRef","aGood","btnYes","btnNo","btnNA","btnPrev","btnNext")

# ---- review ----
NO='CountRows(Filter(colAns, Answer = "No"))'; YESN='CountRows(Filter(colAns, Answer = "Yes"))'; NAN='CountRows(Filter(colAns, Answer = "N/A"))'
SCORE=f'If({YESN} + {NO} = 0, 1, {YESN} / ({YESN} + {NO}))'
out.append(label("rT",'"REVIEW  ·  " & ' + CARD + '.Card',16,Y0,W-32,48,size=15,bold=True,color=DARK,font="Georgia"))
out.append(label("rScore",f'If({NO} = 0, "PASS", "FAIL")' + ' & "   " & Text(' + SCORE + ' * 100, "0") & "%"',16,Y0+52,W-32,70,size=28,bold=True,color=WHITE,align="Center",
   fill=f'If({NO} = 0, {GREEN}, {RED})'))
rk=[label("gRN",'Text(ThisItem.ItemNo)',6,4,36,44,size=14,bold=True,color=G9,indent=6),
    label("gRS",'LookUp(colItems, ItemNo = ThisItem.ItemNo).Section & If(IsBlank(ThisItem.Missed), "", Char(10) & "Missed: " & ThisItem.Missed)',44,2,W-200,62,size=12,color=DARK,indent=6),
    label("gRA",'ThisItem.Answer',W-150,12,90,36,size=13,bold=True,color=WHITE,align="Center",indent=6,
          fill=f'If(ThisItem.Answer = "Yes", {GREEN}, ThisItem.Answer = "No", {RED}, {G5})'),
    btn("gRGo",'"✎"','Set(varItem, ThisItem.ItemNo); Set(varStep, "audit")',W-56,12,36,36,fill=WHITE,color=TEAL_D,size=12,indent=6,extra={"BorderColor":F(G1)})]
gp={"Items":F("colAns"),"TemplateSize":"=68","TemplatePadding":"=0","BorderColor":F(G1),"BorderThickness":"=1"}; gp.update(box(10,Y0+132,W-20,430))
out.append(ctrl("galRev","Gallery@2.15.0",gp,0,rk,variant="BrowseLayout_Vertical_TwoTextOneImageVariant_ver5.0"))
out.append(cap("rC1","WHO / WHAT WAS OBSERVED  (crew, operator)",16,Y0+572,W-32))
out.append(ti("txtObs",'""',16,Y0+592,W-32,50,'false',hint='"e.g. Crew B, J. Smith"',size=14,number=False,extra={"Align":"=Align.Left"}))
out.append(cap("rC2","NOTES  (optional)",16,Y0+648,W-32))
out.append(ti("txtPNotes",'""',16,Y0+668,W-32,70,'false',hint='"coaching given, context"',size=13,number=False,extra={"Align":"=Align.Left","Mode":"=TextMode.MultiLine"}))
SUBMIT=('IfError(\n'
 ' Set(varAud, Patch(PC_Audits, Defaults(PC_Audits), {\n'
 '   Ref: "PC" & varCardID & "-" & Text(Now(), "yyyymmdd-hhmmss"), CardID: varCardID, StandardID: ' + CARD + '.StandardID,\n'
 '   Line: If(ddPLine.Selected.Value = "All", ' + CARD + '.Line, ddPLine.Selected.Value), Area: ' + CARD + '.Area,\n'
 f'   ShiftDate: {SDATE}, Shift: {SHIFT}, ShiftKey: {SKEY}, Tier: ' + CARD + '.Tier,\n'
 '   AuditedBy: User().Email, AuditorName: User().FullName, Observed: txtObs.Text, StartedAt: varStart, CompletedAt: Now(),\n'
 f'   Result: {{Value: If({NO} = 0, "Pass", "Fail")}}, Score: {SCORE}, NYes: {YESN}, NNo: {NO}, NNA: {NAN}, Notes: txtPNotes.Text}}));\n'
 ' ForAll(colAns As a, Patch(PC_Results, Defaults(PC_Results), {Ref: varAud.Ref & "-I" & a.ItemNo, AuditID: varAud.ID, CardID: varCardID, ItemNo: a.ItemNo, ElementID: a.ElementID,\n'
 f'   Answer: {{Value: a.Answer}}, Missed: a.Missed, ActionCreated: a.Answer = "No" && a.Act, NewspaperRef: If(a.Answer = "No" && a.Act, varAud.Ref & "-I" & a.ItemNo, ""), Line: varAud.Line, ShiftKey: varAud.ShiftKey}}));\n'
 ' ForAll(Filter(colAns, Answer = "No" && Act) As a, Patch(Newspaper, Defaults(Newspaper), {\n'
 '   Action: Left("PC: " & LookUp(colItems, ItemNo = a.ItemNo).Section & " — " & a.Missed, 250), Line: varAud.Line,\n'
 '   SQDCP: {Value: If(LookUp(colItems, ItemNo = a.ItemNo).PType = "Safety", "Safety", "Quality")}, Source: {Value: "Process confirmation"},\n'
 '   Problem: "Process confirmation " & ' + CARD + '.Card & ", item " & a.ItemNo & ": " & a.Missed, RaisedDate: Today(), DueDate: DateAdd(Today(), 7, TimeUnit.Days),\n'
 '   Status: {Value: "Open"}, RefKey: varAud.Ref & "-I" & a.ItemNo}));\n'
 ' ForAll(colPhotos As p, Patch(TS_Photos, LookUp(TS_Photos, ID = Value(' + FLOW + '.Run({contentBytes: p.Ph, name: "pc.jpg"}, varAud.Ref & "-I" & p.ItemNo & ".jpg",\n'
 '    varAud.ID, p.ItemNo, 0, If(LookUp(colAns, ItemNo = p.ItemNo).Answer = "No", "Finding", "Step"), LookUp(colAns, ItemNo = p.ItemNo).Missed, User().Email).photoid)),\n'
 '    {Module: {Value: "Process confirmation"}, RefID: varAud.ID})),\n'
 ' Notify("NOT SUBMITTED — " & FirstError.Message & "  (check signal, try again)", NotificationType.Error),\n'
 ' Set(varResult, If(' + NO + ' = 0, "Pass", "Fail")); Set(varStep, "done"); Reset(txtObs); Reset(txtPNotes); Select(btnPRefresh))')
ALLDONE='CountRows(Filter(colAns, IsBlank(Answer) || (Answer = "No" && IsBlank(Missed)))) = 0'
out.append(btn("btnSubmit",f'If({ALLDONE}, "SUBMIT CARD", "ANSWER EVERY ITEM")',SUBMIT,16,Y0+750,W-32,80,fill=f'If({ALLDONE}, {TEAL_D}, {G1})',color=f'If({ALLDONE}, {WHITE}, {G9})',size=20,
   extra={"DisplayMode":F(f'If({ALLDONE}, DisplayMode.Edit, DisplayMode.Disabled)'),"DisabledFill":F(G1),"DisabledColor":F(G9),**RAD}))
P("review","rT","rScore","galRev","rC1","txtObs","rC2","txtPNotes","btnSubmit")

# ---- done (the T-card flips) ----
out.append(rect("dCard",'If(varResult = "Pass", RGBA(46, 160, 67, 1), RGBA(207, 34, 46, 1))',60,Y0+60,W-120,420))
out.append(label("dRes",'If(varResult = "Pass", "PASS", "FAIL")',60,Y0+140,W-120,120,size=60,bold=True,color=WHITE,align="Center",font="Georgia"))
out.append(label("dSub",'If(varResult = "Pass", "Card flipped GREEN for this shift.", "Card flipped RED. " & CountRows(Filter(colAns, Answer = "No" && Act)) & " action(s) added to NEWSPAPER.")',80,Y0+280,W-160,120,size=15,bold=True,color=WHITE,align="Center"))
out.append(btn("btnDNext",'"NEXT CARD"','Set(varStep, "pick"); Set(varCardID, Blank())',16,Y0+520,W-32,76,fill=TEAL_D,color=WHITE,size=18,extra=RAD))
P("done","dCard","dRes","dSub","btnDNext")

# helper: start a card (loads items, standard photos, answers)
START=('Set(varCard, ' + CARD + ');\n'
 'IfError(ClearCollect(colEl, Filter(SW_Elements, StandardID = varCard.StandardID)), Notify("Could not load SW_Elements", NotificationType.Warning));\n'
 'ClearCollect(colItems, ForAll(Sort(Filter(PC_CardItems, CardID = varCardID && Active = true), ItemNo) As c,\n'
 '  With({e: LookUp(colEl, ID = c.ElementID)},\n'
 '   {ItemNo: c.ItemNo, ElementID: c.ElementID, ElNo: Coalesce(e.ElementNo, c.ItemNo), Section: Coalesce(e.Element, c.Check), Check: c.Check,\n'
 '    Good: Coalesce(c.GoodLooksLike, e.GoodLooksLike, ""), PType: Coalesce(e.PointType.Value, "Quality")})));\n'
 'ClearCollect(colRefPh, Filter(TS_Photos, Module.Value = "Standard work" && RefID = varCard.StandardID));\n'
 'ClearCollect(colAns, ForAll(colItems, {ItemNo: ItemNo, ElementID: ElementID, Answer: "", Missed: "", Act: true}));\n'
 'Clear(colPhotos); Set(varItem, 1); Set(varStart, Now());\n'
 'If(CountRows(colItems) = 0, Notify("This card has no items yet — build it in the Standard Work app.", NotificationType.Warning), Set(varStep, "audit"))')
HELP={"Color":F(CLEAR),"BorderColor":F(CLEAR),"HoverFill":F(CLEAR),"PressedFill":F(CLEAR),"TabIndex":"=-1"}
out.append(btn("btnPStart",'""',START,0,1135,1,1,fill=CLEAR,color=CLEAR,extra=HELP))
out.append(label("lblLoaded",'If(IsBlank(varLoaded), "Not loaded — tap ↻", "Loaded " & Text(varLoaded, "h:mm AM/PM"))',16,1100,W-32,26,size=10,color=G5,align="Center"))
'''
for _ in range(2):
    out=[]
    exec(BODY)
write_themed("/mnt/user-data/outputs/PC_Audit_v4.pa.yaml", "".join(out))
print("ok", len(out))
