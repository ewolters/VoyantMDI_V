# Generates SW_Manager_v2.pa.yaml — Standard Work manager (1920x1080): standards library, element photos, PC card builder, adherence
exec(open(__import__("os").environ["MDI_GEN"]+"/theme.py").read())
src=open(__import__("os").environ["MDI_GEN"]+"/build6.py").read()
exec(src[:src.index("DT_OLD=")])
EXTRA.clear()
MUTE="RGBA(243, 244, 244, 1)"; PANEL="RGBA(248, 249, 249, 1)"; YEL="RGBA(255, 242, 179, 1)"; YELB="RGBA(210, 153, 34, 1)"
RAD={"RadiusTopLeft":"=6","RadiusTopRight":"=6","RadiusBottomLeft":"=6","RadiusBottomRight":"=6"}
FLOW="'MDI-UploadPhoto'"

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
def T(tab,*names):
    for n in names: EXTRA.setdefault(n,{})["Visible"]=F(f'varTab = "{tab}"')
def pill_label(name,text,x,y,w,h,fill,indent=0,size=10):
    return label(name,text,x,y,w,h,size=size,bold=True,color=WHITE,align="Center",fill=fill,indent=indent)
def txt(name,default,x,y,w,h,hint='""',multi=False,size=13):
    ex={"Align":"=Align.Left"}
    if multi: ex["Mode"]="=TextMode.MultiLine"
    return ti(name,default,x,y,w,h,'false',hint=hint,size=size,number=False,extra=ex)
STD='LookUp(colStd, ID = varStdID)'
EL='LookUp(colEl, ID = varElID)'
CARDR='LookUp(colCards, ID = varCardID)'
LATEST=lambda filt: f'First(SortByColumns(Filter(colStdPh, {filt}), "Created", SortOrder.Descending)).Thumbnail.Large'
STATUSFILL='If({s} = "Active", RGBA(46, 160, 67, 1), {s} = "Under review", RGBA(210, 153, 34, 1), {s} = "Draft", RGBA(177, 179, 179, 1), RGBA(117, 120, 123, 1))'

# ---------- header + tabs ----------
out.append(rect("hdrBar",DARK,0,0,1920,90))
out.append(label("lblBrand",'"voyant"',24,6,170,52,size=34,color=WHITE,font="Georgia"))
out.append(label("lblBrandSub",'"NEW ALBANY"',27,56,170,24,size=10,bold=True,color=TEAL))
out.append(label("lblTitle",'"STANDARD WORK"',190,20,330,50,size=24,bold=True,color=WHITE,font="Georgia"))
for i,(k,t) in enumerate([("std","STANDARDS"),("card","PC CARDS"),("res","RESULTS")]):
    out.append(btn(f"tab{i}",f'"{t}"',f'Set(varTab, "{k}")',560+i*200,22,190,48,fill=f'If(varTab = "{k}", {TEAL}, {TEAL_D})',color=f'If(varTab = "{k}", {DARK}, {WHITE})',size=14,extra=RAD))
LOAD=('IfError(ClearCollect(colStd, SW_Standards), Notify("Could not load SW_Standards — " & FirstError.Message, NotificationType.Error));\n'
 'IfError(ClearCollect(colAllEl, SW_Elements), Notify("Could not load SW_Elements", NotificationType.Error));\n'
 'IfError(ClearCollect(colCards, PC_Cards), Notify("Could not load PC_Cards", NotificationType.Error));\n'
 'IfError(ClearCollect(colStdPh, Filter(TS_Photos, Module.Value = "Standard work")), Notify("Could not load photos", NotificationType.Warning));\n'
 'IfError(ClearCollect(colCfg, MDI_Config), Notify("Could not load MDI_Config", NotificationType.Warning));\n'
 'IfError(ClearCollect(colLk, Filter(Lookups, Active = true)), Notify("Could not load Lookups", NotificationType.Warning));\n'
 'ClearCollect(colEq, Ungroup(Table({t: Table({Value: ""})}, {t: ForAll(Sort(Filter(colLk, Category.Value = "Equipment"), SortOrder), {Value: Label})}), t));\n'
 'Set(varFrom, DateAdd(Today(), -Coalesce(ddRPer.Selected.N, 30), TimeUnit.Days));\n'
 'IfError(ClearCollect(colAud, Filter(PC_Audits, ShiftDate >= varFrom)), Notify("Could not load PC_Audits", NotificationType.Warning));\n'
 'IfError(ClearCollect(colRes, Filter(PC_Results, Created >= varFrom)), Notify("Could not load PC_Results", NotificationType.Warning));\n'
 'ClearCollect(colEl, Filter(colAllEl, StandardID = varStdID));\n'
 'If(IsBlank(varTab), Set(varTab, "std"));\n'
 'Set(varLoaded, Now())')
out.append(btn("btnSRefresh",'"REFRESH"',LOAD,1640,22,130,48,fill=TEAL_D,color=WHITE,size=13,extra=RAD))
out.append(label("lblSLoaded",'If(IsBlank(varLoaded), "Not loaded", "Loaded " & Text(varLoaded, "h:mm AM/PM"))',1780,30,130,30,size=10,color=G5))

# =================== TAB: STANDARDS ===================
out.append(rect("sListBg",PANEL,12,100,520,970))
out.append(txt("txtSSearch",'""',22,108,300,44,hint='"search standards…"'))
out.append(dd("ddSStatus",'["All", "Active", "Draft", "Under review", "Retired"]',330,108,192,44,default='"All"',size=13))
STDITEMS=('SortByColumns(Filter(colStd, (ddSStatus.Selected.Value = "All" || Status.Value = ddSStatus.Selected.Value)\n'
          '  && (IsBlank(txtSSearch.Text) || txtSSearch.Text in Standard || txtSSearch.Text in DocNo || txtSSearch.Text in Area || txtSSearch.Text in EquipType)), "DocNo", SortOrder.Ascending)')
SSEL='(ThisItem.ID = varStdID)'
sk=[rect("gSBg",WHITE,0,0,500,106,indent=6,extra={"BorderColor":F(f'If({SSEL}, {TEAL_D}, {G1})'),"BorderThickness":F(f'If({SSEL}, 3, 1)')}),
    label("gSNo",'Coalesce(ThisItem.DocNo, "—") & "  rev " & Coalesce(ThisItem.Rev, "-")',12,4,300,26,size=11,bold=True,color=TEAL_D,indent=6),
    pill_label("gSType",'ThisItem.DocType.Value',320,6,80,22,TEAL_D,indent=6),
    pill_label("gSStat",'ThisItem.Status.Value',408,6,84,22,STATUSFILL.format(s='ThisItem.Status.Value'),indent=6),
    label("gSName",'ThisItem.Standard',12,30,480,44,size=14,bold=True,color=DARK,indent=6),
    label("gSSub",'Coalesce(ThisItem.Line, "") & If(IsBlank(ThisItem.Area), "", " · " & ThisItem.Area) & If(IsBlank(ThisItem.EquipType), "", " · " & ThisItem.EquipType) & "   ·   " & CountRows(Filter(colAllEl, StandardID = ThisItem.ID)) & " elements" & If(!IsBlank(ThisItem.ReviewDue) && ThisItem.ReviewDue <= Today(), "   ·   REVIEW DUE", "")',
          12,74,480,26,size=10,indent=6,extra={"Color":F(f'If(!IsBlank(ThisItem.ReviewDue) && ThisItem.ReviewDue <= Today(), {RED}, {G9})')}),
    btn("gSSel",'""','Set(varStdID, ThisItem.ID); Set(varStdNew, false); Set(varElID, Blank()); ClearCollect(colEl, Filter(colAllEl, StandardID = ThisItem.ID)); Select(btnSResetStd)',0,0,500,106,fill=CLEAR,color=CLEAR,indent=6,
        extra={"HoverFill":F("RGBA(0, 72, 81, 0.06)"),"PressedFill":F("RGBA(0, 72, 81, 0.12)"),"BorderColor":F(CLEAR)})]
gp={"Items":F(STDITEMS),"TemplateSize":"=112","TemplatePadding":"=0"}; gp.update(box(16,160,512,840))
out.append(ctrl("galStd","Gallery@2.15.0",gp,0,sk,variant="BrowseLayout_Vertical_TwoTextOneImageVariant_ver5.0"))
out.append(btn("btnSNew",'"+  NEW STANDARD"','Set(varStdID, Blank()); Set(varStdNew, true); Set(varElID, Blank()); Clear(colEl); Select(btnSResetStd)',22,1008,500,54,fill=WHITE,color=TEAL_D,size=14,
   extra={"BorderColor":F(TEAL_D),"BorderThickness":"=2",**RAD}))
T("std","sListBg","txtSSearch","ddSStatus","galStd","btnSNew")

# --- standard editor ---
X=544
out.append(label("sEdT",'If(varStdNew, "NEW STANDARD", If(IsBlank(varStdID), "← Pick a standard, or add a new one", "STANDARD  ·  " & ' + STD + '.DocNo))',X,100,900,34,size=15,bold=True,color=DARK,font="Georgia"))
EDV='(varStdNew || !IsBlank(varStdID))'
def sf(capn,name,default,x,y,w,h=44,hint='""',multi=False):
    out.append(cap("c"+name,capn,x,y,w)); out.append(txt(name,default,x,y+20,w,h,hint=hint,multi=multi))
    return ["c"+name,name]
D=lambda f: f'If(varStdNew, "", Coalesce({STD}.{f}, ""))'
E=[]
E+=sf("TITLE *","txtStTitle",D("Standard"),X,138,700,hint='"e.g. Labeler changeover — 10 oz"')
E+=sf("DOC NO","txtStNo",D("DocNo"),X+710,138,180,hint='"SW-205-012"')
E+=sf("REV","txtStRev",D("Rev"),X+900,138,80,hint='"1"')
out.append(cap("cStType","TYPE",X+990,138,170)); out.append(dd("ddStType",'["SWIS", "JEL", "OPL", "Centerline", "Changeover", "Checklist", "5S", "Other"]',X+990,158,170,44,default=f'If(varStdNew, "SWIS", {STD}.DocType.Value)',size=13)); E+=["cStType","ddStType"]
out.append(cap("cStStat","STATUS",X+1170,138,190)); out.append(dd("ddStStat",'["Draft", "Active", "Under review", "Retired"]',X+1170,158,190,44,default=f'If(varStdNew, "Draft", {STD}.Status.Value)',size=13)); E+=["cStStat","ddStStat"]
E+=sf("LINE","txtStLine",D("Line"),X,208,140,hint='"All / 205"')
E+=sf("AREA","txtStArea",D("Area"),X+150,208,200,hint='"Labeling"')
out.append(cap("cStEq","EQUIPMENT",X+360,208,200)); out.append(dd("ddStEq","colEq",X+360,228,200,44,default=f'If(varStdNew, "", {STD}.EquipType)',size=13)); E+=["cStEq","ddStEq"]
E+=sf("OWNER","txtStOwner",D("Owner"),X+570,208,220,hint='"name"')
E+=sf("REVIEW DUE (yyyy-mm-dd)","txtStRev2",f'If(varStdNew || IsBlank({STD}.ReviewDue), "", Text({STD}.ReviewDue, "yyyy-mm-dd"))',X+800,208,190,hint='"2027-04-30"')
E+=sf("LINK TO CONTROLLED DOC (SharePoint)","txtStLink",D("DocLink"),X+1000,208,280,hint='"paste URL"')
out.append(btn("btnStOpen",'"↗"','Launch(txtStLink.Text)',X+1290,228,70,44,fill=WHITE,color=TEAL_D,size=16,extra={"BorderColor":F(TEAL_D),"BorderThickness":"=1",**RAD,"DisplayMode":F('If(IsBlank(txtStLink.Text), DisplayMode.Disabled, DisplayMode.Edit)')})); E+=["btnStOpen"]
E+=sf("PURPOSE / SCOPE","txtStPurp",D("Purpose"),X,278,600,h=60,multi=True)
E+=sf("KEY SAFETY POINTS","txtStSafe",D("KeySafety"),X+610,278,560,h=60,multi=True)
STDREC=('{Standard: txtStTitle.Text, DocNo: txtStNo.Text, Rev: txtStRev.Text, DocType: {Value: ddStType.Selected.Value}, Status: {Value: ddStStat.Selected.Value},\n'
        ' Line: txtStLine.Text, Area: txtStArea.Text, EquipType: ddStEq.Selected.Value, Owner: txtStOwner.Text,\n'
        ' ReviewDue: If(IsBlank(txtStRev2.Text), Blank(), DateValue(txtStRev2.Text)), DocLink: txtStLink.Text, Purpose: txtStPurp.Text, KeySafety: txtStSafe.Text}')
SAVESTD=('IfError(\n'
 ' If(varStdNew,\n'
 '  Set(varStdID, Patch(SW_Standards, Defaults(SW_Standards), ' + STDREC + ', {AddedBy: User().FullName}).ID); Set(varStdNew, false),\n'
 '  Patch(SW_Standards, LookUp(SW_Standards, ID = varStdID), ' + STDREC + ')),\n'
 ' Notify("NOT SAVED — " & FirstError.Message, NotificationType.Error),\n'
 ' Notify("Standard saved", NotificationType.Success); ClearCollect(colStd, SW_Standards))')
out.append(btn("btnStSave",'If(IsBlank(txtStTitle.Text), "TITLE REQUIRED", "SAVE STANDARD")',SAVESTD,X+1180,298,180,60,fill=f'If(IsBlank(txtStTitle.Text), {G1}, {TEAL_D})',color=f'If(IsBlank(txtStTitle.Text), {G9}, {WHITE})',size=13,
   extra={"DisplayMode":F('If(IsBlank(txtStTitle.Text), DisplayMode.Disabled, DisplayMode.Edit)'),"DisabledFill":F(G1),"DisabledColor":F(G9),**RAD})); E+=["btnStSave"]
for n in E: EXTRA.setdefault(n,{})["Visible"]=F(f'varTab = "std" && {EDV}')
T("std","sEdT")

# --- elements ---
EY=370
out.append(rect("eBg",PANEL,X,EY,1364,700,extra={"Visible":F('varTab = "std" && !IsBlank(varStdID)')}))
out.append(label("eT",'"ELEMENTS  —  what GOOD looks like, step by step"',X+12,EY+6,800,30,size=13,bold=True,color=DARK,extra={"Visible":F('varTab = "std" && !IsBlank(varStdID)')}))
ESEL='(ThisItem.ID = varElID)'
ek=[rect("gEBg",WHITE,0,0,820,150,indent=6,extra={"BorderColor":F(f'If({ESEL}, {TEAL_D}, {G1})'),"BorderThickness":F(f'If({ESEL}, 3, 1)')}),
    label("gENo",'Text(ThisItem.ElementNo)',10,10,48,48,size=18,bold=True,color=WHITE,align="Center",fill=TEAL_D,indent=6),
    label("gEName",'ThisItem.Element',70,6,500,32,size=14,bold=True,color=DARK,indent=6),
    pill_label("gEType",'ThisItem.PointType.Value',480,10,80,22,f'If(ThisItem.PointType.Value = "Safety", {RED}, ThisItem.PointType.Value = "Quality", {TEAL_D}, {G9})',indent=6),
    label("gEGood",'"GOOD: " & Coalesce(ThisItem.GoodLooksLike, "")',70,40,500,64,size=11,color=DARK,indent=6,extra={"VerticalAlign":"=VerticalAlign.Top"}),
    label("gEWhy",'If(IsBlank(ThisItem.Why), "", "WHY: " & ThisItem.Why)',70,104,500,40,size=10,color=G9,indent=6,extra={"VerticalAlign":"=VerticalAlign.Top"}),
    image("gEImg",LATEST('StepNo = ThisItem.ElementNo && RefID = varStdID'),580,6,230,138,indent=6),
    btn("gESel",'""','Set(varElID, ThisItem.ID); Select(btnSResetEl)',0,0,570,150,fill=CLEAR,color=CLEAR,indent=6,
        extra={"HoverFill":F("RGBA(0, 72, 81, 0.06)"),"PressedFill":F("RGBA(0, 72, 81, 0.12)"),"BorderColor":F(CLEAR)})]
gp={"Items":F('Sort(colEl, ElementNo)'),"TemplateSize":"=158","TemplatePadding":"=0","Visible":F('varTab = "std" && !IsBlank(varStdID)')}; gp.update(box(X+8,EY+40,836,650))
out.append(ctrl("galEl","Gallery@2.15.0",gp,0,ek,variant="BrowseLayout_Vertical_TwoTextOneImageVariant_ver5.0"))
# element editor
EX=X+856; EW=496
EE=[]
out.append(label("eEdT",'If(IsBlank(varElID), "NEW ELEMENT", "EDIT ELEMENT " & ' + EL + '.ElementNo)',EX,EY+6,EW,30,size=13,bold=True,color=TEAL_D)); EE.append("eEdT")
out.append(cap("cElNo","NO.",EX,EY+40,70)); out.append(ti("txtElNo",f'If(IsBlank(varElID), Text(CountRows(colEl) + 1), Text({EL}.ElementNo))',EX,EY+60,70,44,'false',size=14,bold=True)); EE+=["cElNo","txtElNo"]
out.append(cap("cElName","ELEMENT (major step / check point) *",EX+80,EY+40,EW-80)); out.append(txt("txtElName",f'If(IsBlank(varElID), "", {EL}.Element)',EX+80,EY+60,EW-80,44)); EE+=["cElName","txtElName"]
out.append(cap("cElGood","WHAT GOOD LOOKS LIKE (key points) *",EX,EY+110,EW)); out.append(txt("txtElGood",f'If(IsBlank(varElID), "", Coalesce({EL}.GoodLooksLike, ""))',EX,EY+130,EW,96,multi=True)); EE+=["cElGood","txtElGood"]
out.append(cap("cElWhy","WHY (reason)",EX,EY+232,EW)); out.append(txt("txtElWhy",f'If(IsBlank(varElID), "", Coalesce({EL}.Why, ""))',EX,EY+252,EW,56,multi=True)); EE+=["cElWhy","txtElWhy"]
out.append(cap("cElType","TYPE",EX,EY+314,200)); out.append(dd("ddElType",'["Quality", "Safety", "Knack", "Ergo", "Info"]',EX,EY+334,200,44,default=f'If(IsBlank(varElID), "Quality", {EL}.PointType.Value)',size=13)); EE+=["cElType","ddElType"]
out.append(image("imgElCur",LATEST(f'StepNo = Value(txtElNo.Text) && RefID = varStdID'),EX,EY+386,EW,200,extra={"Image":F(f'If(!IsBlank(addElPh.Media), addElPh.Media, {LATEST("StepNo = Value(txtElNo.Text) && RefID = varStdID")})')})); EE.append("imgElCur")
out.append(ctrl("addElPh","AddMedia@2.2.1",{"X":F(str(EX+210)),"Y":F(str(EY+334)),"Width":F(str(EW-210)),"Height":"=44","Size":"=12",
   "Text":F('If(IsBlank(Self.Media), "📷  ADD / REPLACE STANDARD PHOTO", "✓  NEW PHOTO READY — save element")'),"Fill":F(MUTE),"Color":F(TEAL_D),"BorderColor":F(G5),"BorderThickness":"=1"})); EE.append("addElPh")
ELREC='{Element: txtElName.Text, StandardID: varStdID, ElementNo: Value(txtElNo.Text), GoodLooksLike: txtElGood.Text, Why: txtElWhy.Text, PointType: {Value: ddElType.Selected.Value}, Active: true}'
SAVEEL=('IfError(\n'
 ' If(IsBlank(varElID), Set(varElID, Patch(SW_Elements, Defaults(SW_Elements), ' + ELREC + ').ID), Patch(SW_Elements, LookUp(SW_Elements, ID = varElID), ' + ELREC + '));\n'
 ' If(!IsBlank(addElPh.Media), Patch(TS_Photos, LookUp(TS_Photos, ID = Value(' + FLOW + '.Run({contentBytes: addElPh.Media, name: "std.jpg"}, "SW" & varStdID & "-E" & txtElNo.Text & ".jpg", varStdID, Value(txtElNo.Text), 0, "Standard", txtElName.Text, User().Email).photoid)),\n'
 '   {Module: {Value: "Standard work"}, RefID: varStdID})),\n'
 ' Notify("ELEMENT NOT SAVED — " & FirstError.Message, NotificationType.Error),\n'
 ' Notify("Element saved", NotificationType.Success); ClearCollect(colAllEl, SW_Elements); ClearCollect(colEl, Filter(colAllEl, StandardID = varStdID));\n'
 ' ClearCollect(colStdPh, Filter(TS_Photos, Module.Value = "Standard work")); Reset(addElPh))')
ELOK='!IsBlank(txtElName.Text) && !IsBlank(txtElGood.Text) && !IsBlank(varStdID)'
out.append(btn("btnElSave",f'If({ELOK}, "SAVE ELEMENT", "NAME + GOOD REQUIRED")',SAVEEL,EX,EY+594,EW-170,56,fill=f'If({ELOK}, {TEAL_D}, {G1})',color=f'If({ELOK}, {WHITE}, {G9})',size=13,
   extra={"DisplayMode":F(f'If({ELOK}, DisplayMode.Edit, DisplayMode.Disabled)'),"DisabledFill":F(G1),"DisabledColor":F(G9),**RAD})); EE.append("btnElSave")
out.append(btn("btnElNew",'"+ NEW"','Set(varElID, Blank()); Select(btnSResetEl)',EX+EW-160,EY+594,160,56,fill=WHITE,color=TEAL_D,size=13,extra={"BorderColor":F(TEAL_D),"BorderThickness":"=2",**RAD})); EE.append("btnElNew")
for n in EE: EXTRA.setdefault(n,{})["Visible"]=F('varTab = "std" && !IsBlank(varStdID)')

# =================== TAB: CARDS ===================
out.append(rect("cListBg",PANEL,12,100,520,970))
CSEL='(ThisItem.ID = varCardID)'
ck=[rect("gCBg",WHITE,0,0,500,96,indent=6,extra={"BorderColor":F(f'If({CSEL}, {TEAL_D}, {G1})'),"BorderThickness":F(f'If({CSEL}, 3, 1)')}),
    rect("gCTab",'If(ThisItem.Active, RGBA(46, 160, 67, 1), RGBA(177, 179, 179, 1))',0,0,12,96,indent=6),
    label("gCName",'ThisItem.Card',22,4,400,46,size=13,bold=True,color=DARK,indent=6),
    pill_label("gCTier",'"Tier " & ThisItem.Tier',420,8,70,22,TEAL,indent=6),
    label("gCSub",'ThisItem.Frequency.Value & "  ·  " & Coalesce(ThisItem.Line, "") & "  ·  " & Coalesce(LookUp(colStd, ID = ThisItem.StandardID).DocNo, "no standard")',22,52,470,36,size=10,color=G9,indent=6),
    btn("gCSel",'""','Set(varCardID, ThisItem.ID); Set(varCardNew, false); Select(btnCLoad)',0,0,500,96,fill=CLEAR,color=CLEAR,indent=6,
        extra={"HoverFill":F("RGBA(0, 72, 81, 0.06)"),"PressedFill":F("RGBA(0, 72, 81, 0.12)"),"BorderColor":F(CLEAR)})]
gp={"Items":F('SortByColumns(colCards, "Tier", SortOrder.Ascending, "Title", SortOrder.Ascending)'),"TemplateSize":"=102","TemplatePadding":"=0"}; gp.update(box(16,108,512,890))
out.append(ctrl("galCardsM","Gallery@2.15.0",gp,0,ck,variant="BrowseLayout_Vertical_TwoTextOneImageVariant_ver5.0"))
out.append(btn("btnCNew",'"+  NEW CARD"','Set(varCardID, Blank()); Set(varCardNew, true); Select(btnCLoad)',22,1008,500,54,fill=WHITE,color=TEAL_D,size=14,extra={"BorderColor":F(TEAL_D),"BorderThickness":"=2",**RAD}))
T("card","cListBg","galCardsM","btnCNew")
CEV='(varCardNew || !IsBlank(varCardID))'
CE=[]
out.append(label("cEdT",'If(varCardNew, "NEW PROCESS CONFIRMATION CARD", If(IsBlank(varCardID), "← Pick a card, or build a new one from a standard", "CARD  ·  " & ' + CARDR + '.Card))',X,100,1200,34,size=15,bold=True,color=DARK,font="Georgia"))
T("card","cEdT")
CD=lambda f,dflt='""': f'If(varCardNew, {dflt}, Coalesce({CARDR}.{f}, {dflt}))'
out.append(cap("cCName","CARD TITLE *",X,138,560)); out.append(txt("txtCName",CD("Card"),X,158,560,44,hint='"e.g. MDI Accuracy & Completeness Audit"')); CE+=["cCName","txtCName"]
out.append(cap("cCStd","STANDARD IT CONFIRMS *",X+570,138,520))
out.append(dd("ddCStd",'ForAll(SortByColumns(Filter(colStd, Status.Value <> "Retired"), "DocNo"), {Value: Coalesce(DocNo, "") & "  —  " & Standard, ID: ID})',X+570,158,520,44,
   default=f'If(varCardNew, "", With({{s: LookUp(colStd, ID = {CARDR}.StandardID)}}, Coalesce(s.DocNo, "") & "  —  " & s.Standard))',size=12,
   onchange='ClearCollect(colPick, ForAll(Filter(colAllEl, StandardID = Self.Selected.ID), {EID: ID}))')); CE+=["cCStd","ddCStd"]
out.append(cap("cCTier","TIER",X+1100,138,80)); out.append(dd("ddCTier",'["1", "2", "3", "4"]',X+1100,158,80,44,default=f'If(varCardNew, "1", Text({CARDR}.Tier))',size=14)); CE+=["cCTier","ddCTier"]
out.append(cap("cCFreq","FREQUENCY",X+1190,138,170)); out.append(dd("ddCFreq",'["Every shift", "Daily", "Weekly", "Monthly"]',X+1190,158,170,44,default=f'If(varCardNew, "Every shift", {CARDR}.Frequency.Value)',size=13)); CE+=["cCFreq","ddCFreq"]
out.append(cap("cCLine","LINE",X,208,140)); out.append(txt("txtCLine",CD("Line",'"All"'),X,228,140,44,hint='"All / 205"')); CE+=["cCLine","txtCLine"]
out.append(cap("cCArea","AREA",X+150,208,220)); out.append(txt("txtCArea",CD("Area"),X+150,228,220,44)); CE+=["cCArea","txtCArea"]
out.append(cap("cCSh","SHIFTS",X+380,208,200)); CE.append("cCSh")
for i,s in enumerate(["1","2","3"]):
    on=f'!IsEmpty(Filter(colShiftSel, Value = "{s}"))'
    out.append(btn(f"btnCSh{s}",f'"{s}"',f'If({on}, RemoveIf(colShiftSel, Value = "{s}"), Collect(colShiftSel, {{Value: "{s}"}}))',X+380+i*66,228,60,44,
       fill=f'If({on}, {TEAL_D}, {WHITE})',color=f'If({on}, {WHITE}, {DARK})',size=14,extra={"BorderColor":F(TEAL_D),"BorderThickness":"=1",**RAD})); CE.append(f"btnCSh{s}")
out.append(btn("btnCAct",'If(varCardActive, "● ACTIVE", "○ INACTIVE")','Set(varCardActive, !varCardActive)',X+590,228,160,44,fill=f'If(varCardActive, {GREEN}, {G5})',color=WHITE,size=13,extra=RAD)); CE.append("btnCAct")
out.append(cap("cCIns","AUDITOR INSTRUCTIONS",X+760,208,600)); out.append(txt("txtCIns",CD("Instructions"),X+760,228,600,44)); CE+=["cCIns","txtCIns"]
# element picker
out.append(rect("cPickBg",PANEL,X,284,1364,620)); CE.append("cPickBg")
out.append(label("cPickT",'"CARD ITEMS  —  tick the standard\'s elements this card checks (" & CountRows(colPick) & " selected)"',X+12,290,1000,30,size=13,bold=True,color=DARK)); CE.append("cPickT")
PON='!IsEmpty(Filter(colPick, EID = ThisItem.ID))'
pk=[rect("gPBg",WHITE,0,0,664,140,indent=6,extra={"BorderColor":F(f'If({PON}, {TEAL_D}, {G1})'),"BorderThickness":F(f'If({PON}, 3, 1)')}),
    btn("gPChk",f'If({PON}, "✓", "")',f'If({PON}, RemoveIf(colPick, EID = ThisItem.ID), Collect(colPick, {{EID: ThisItem.ID}}))',10,44,52,52,
        fill=f'If({PON}, {TEAL_D}, {WHITE})',color=WHITE,size=22,indent=6,extra={"BorderColor":F(TEAL_D),"BorderThickness":"=2"}),
    label("gPName",'ThisItem.ElementNo & ".  " & ThisItem.Element',74,6,360,40,size=13,bold=True,color=DARK,indent=6),
    label("gPGood",'Coalesce(ThisItem.GoodLooksLike, "")',74,46,360,88,size=10,color=G9,indent=6,extra={"VerticalAlign":"=VerticalAlign.Top"}),
    image("gPImg",LATEST('StepNo = ThisItem.ElementNo && RefID = ThisItem.StandardID'),444,6,210,128,indent=6)]
gp={"Items":F('Sort(Filter(colAllEl, StandardID = ddCStd.Selected.ID), ElementNo)'),"WrapCount":"=2","TemplateSize":"=148","TemplatePadding":"=0"}; gp.update(box(X+8,324,1348,572))
out.append(ctrl("galPick","Gallery@2.15.0",gp,0,pk,variant="BrowseLayout_Vertical_TwoTextOneImageVariant_ver5.0")); CE.append("galPick")
out.append(label("cPickNone",'"This standard has no elements yet — add them on the STANDARDS tab (with photos), then come back."',X+20,340,1300,40,size=13,color=G9,
   extra={"Visible":F('varTab = "card" && ' + CEV + ' && CountRows(galPick.AllItems) = 0')}))
CARDREC=('{Card: txtCName.Text, StandardID: ddCStd.Selected.ID, Line: txtCLine.Text, Area: txtCArea.Text, Tier: Value(ddCTier.Selected.Value),\n'
         ' Frequency: {Value: ddCFreq.Selected.Value}, Shifts: colShiftSel, Instructions: txtCIns.Text, Active: varCardActive}')
SAVECARD=('IfError(\n'
 ' If(varCardNew,\n'
 '  Set(varCardID, Patch(PC_Cards, Defaults(PC_Cards), ' + CARDREC + ', {AddedBy: User().FullName}).ID); Set(varCardNew, false),\n'
 '  Patch(PC_Cards, LookUp(PC_Cards, ID = varCardID), ' + CARDREC + '));\n'
 ' RemoveIf(PC_CardItems, CardID = varCardID);\n'
 ' ForAll(Sort(Filter(colAllEl, StandardID = ddCStd.Selected.ID && ID in colPick.EID), ElementNo) As e,\n'
 '  Patch(PC_CardItems, Defaults(PC_CardItems), {Check: e.Element, CardID: varCardID, ItemNo: e.ElementNo, ElementID: e.ID, GoodLooksLike: e.GoodLooksLike, PhotoOnNo: true, Active: true})),\n'
 ' Notify("CARD NOT SAVED — " & FirstError.Message, NotificationType.Error),\n'
 ' Notify("Card saved with " & CountRows(colPick) & " items", NotificationType.Success); ClearCollect(colCards, PC_Cards))')
COK='!IsBlank(txtCName.Text) && !IsBlank(ddCStd.Selected.ID) && CountRows(colPick) > 0'
out.append(btn("btnCSave",f'If({COK}, "SAVE CARD", "TITLE · STANDARD · ITEMS REQUIRED")',SAVECARD,X,914,500,64,fill=f'If({COK}, {TEAL_D}, {G1})',color=f'If({COK}, {WHITE}, {G9})',size=15,
   extra={"DisplayMode":F(f'If({COK}, DisplayMode.Edit, DisplayMode.Disabled)'),"DisabledFill":F(G1),"DisabledColor":F(G9),**RAD})); CE.append("btnCSave")
QRURL=('With({u: Coalesce(LookUp(colCfg, Setting = "App_PCAudit").SettingValue, "")},\n'
       ' If(IsBlank(u), "Set App_PCAudit (web link) in MDI_Config to get this card\'s QR link", u & If("?" in u, "&", "?") & "card=" & varCardID))')
out.append(cap("cCQR","QR LINK FOR THIS CARD (print with qr_labels.py)",X+520,914,840))
out.append(label("lblCQR",QRURL,X+520,934,700,44,size=10,color=TEAL_D,fill=WHITE,extra={"PaddingLeft":"=8"}))
out.append(btn("btnCCopy",'"COPY"','Copy(lblCQR.Text); Notify("Link copied", NotificationType.Information)',X+1230,934,130,44,fill=WHITE,color=TEAL_D,size=12,extra={"BorderColor":F(TEAL_D),"BorderThickness":"=1",**RAD}))
CE+=["cCQR","lblCQR","btnCCopy"]
for n in CE: EXTRA.setdefault(n,{})["Visible"]=F(f'varTab = "card" && {CEV}')
for n in ["cCQR","lblCQR","btnCCopy"]: EXTRA[n]["Visible"]=F('varTab = "card" && !IsBlank(varCardID)')

# =================== TAB: RESULTS ===================
out.append(cap("cRPer","PERIOD",24,100,200))
out.append(dd("ddRPer",'Table({Value: "Last 7 days", N: 7}, {Value: "Last 30 days", N: 30}, {Value: "Last 90 days", N: 90})',24,120,200,44,default='"Last 30 days"',onchange="Select(btnSRefresh)",size=13))
out.append(cap("cRLine","LINE",234,100,160)); out.append(txt("txtRLine",'""',234,120,160,44,hint='"all"'))
AF='Filter(colAud, IsBlank(txtRLine.Text) || Line = txtRLine.Text)'
RF='Filter(colRes, IsBlank(txtRLine.Text) || Line = txtRLine.Text)'
def tile(name,capn,val,x,w,col=None):
    out.append(label(name,val,x,176,w,120,size=34,bold=True,color=DARK,fill=MUTE,align="Center",valign="Bottom",pb=14,extra=({"Color":F(col)} if col else None)))
    out.append(label(name+"C",f'"{capn}"',x,182,w,24,size=10,bold=True,color=G9,align="Center")); return [name,name+"C"]
TW=366
R=["cRPer","ddRPer","cRLine","txtRLine"]
R+=tile("kRAud","AUDITS DONE",f'Text(CountRows({AF}))',24,TW)
R+=tile("kRPass","PASS RATE",f'With({{n: CountRows({AF})}}, If(n = 0, "—", Text(CountRows(Filter({AF}, Result.Value = "Pass")) / n * 100, "0") & "%"))',24+(TW+12),TW,
        col=f'With({{n: CountRows({AF})}}, If(n = 0, {G9}, CountRows(Filter({AF}, Result.Value = "Pass")) / n >= 0.9, {GREEN}, CountRows(Filter({AF}, Result.Value = "Pass")) / n >= 0.75, {AMBER}, {RED}))')
R+=tile("kRScore","AVG SCORE",f'If(CountRows({AF}) = 0, "—", Text(Average({AF}, Score) * 100, "0") & "%")',24+2*(TW+12),TW)
R+=tile("kRFind","FINDINGS (NO)",f'Text(CountRows(Filter({RF}, Answer.Value = "No")))',24+3*(TW+12),TW)
R+=tile("kRAct","ACTIONS RAISED",f'Text(CountRows(Filter({RF}, ActionCreated)))',24+4*(TW+12),TW)
# adherence by card
out.append(rect("rAdhBg",WHITE,24,308,900,760)); out.append(label("rAdhT",'"ADHERENCE BY CARD  (done vs expected in period)"',36,314,860,28,size=12,bold=True,color=DARK)); R+=["rAdhBg","rAdhT"]
ADH=('ForAll(Filter(colCards, Active) As c, With({days: Coalesce(ddRPer.Selected.N, 30)},\n'
     ' With({exp: Switch(c.Frequency.Value, "Every shift", days * Max(1, CountRows(c.Shifts)), "Daily", days, "Weekly", RoundUp(days / 7, 0), RoundUp(days / 30, 0)),\n'
     '       done: CountRows(Filter(' + AF + ', CardID = c.ID)), pass: CountRows(Filter(' + AF + ', CardID = c.ID && Result.Value = "Pass"))},\n'
     '  {Card: c.Card, Tier: c.Tier, Exp: exp, Done: done, Pass: pass, Pct: If(exp = 0, 0, Min(1, done / exp))})))')
ak=[label("gAName",'ThisItem.Card',8,4,500,30,size=12,bold=True,color=DARK,indent=6),
    label("gASub",'"Tier " & ThisItem.Tier & "  ·  " & ThisItem.Done & " of " & ThisItem.Exp & " done  ·  " & ThisItem.Pass & " passed"',8,34,500,24,size=10,color=G9,indent=6),
    rect("gABarBg",G1,520,16,250,26,indent=6),
    rect("gABar",'If(ThisItem.Pct >= 0.9, RGBA(46, 160, 67, 1), ThisItem.Pct >= 0.75, RGBA(210, 153, 34, 1), RGBA(207, 34, 46, 1))',520,16,250,26,indent=6,extra={"Width":F('Max(2, 250 * ThisItem.Pct)')}),
    label("gAPct",'Text(ThisItem.Pct * 100, "0") & "%"',780,10,90,36,size=15,bold=True,color=DARK,align="Right",indent=6)]
gp={"Items":F(f'SortByColumns({ADH}, "Pct", SortOrder.Ascending)'),"TemplateSize":"=64","TemplatePadding":"=0"}; gp.update(box(30,346,888,716))
out.append(ctrl("galAdh","Gallery@2.15.0",gp,0,ak,variant="BrowseLayout_Vertical_TwoTextOneImageVariant_ver5.0")); R.append("galAdh")
# most missed
out.append(rect("rMisBg",WHITE,936,308,960,760)); out.append(label("rMisT",'"MOST MISSED ELEMENTS"',948,314,900,28,size=12,bold=True,color=DARK)); R+=["rMisBg","rMisT"]
MIS=(f'With({{t: SortByColumns(AddColumns(GroupBy(Filter({RF}, Answer.Value = "No"), ElementID, G), N, CountRows(G)), "N", SortOrder.Descending)}},\n'
     ' With({mx: Coalesce(Max(t, N), 0)}, AddColumns(t, Name, With({e: LookUp(colAllEl, ID = ElementID)}, Coalesce(LookUp(colStd, ID = e.StandardID).DocNo, "") & "  ·  " & Coalesce(e.Element, "(element " & ElementID & ")")),\n'
     '   Pct, If(mx > 0, N / mx, 0))))')
mk=[label("gMName",'ThisItem.Name',8,4,520,40,size=12,bold=True,color=DARK,indent=6),
    rect("gMBar",RED,540,14,1,24,indent=6,extra={"Width":F('Max(2, 330 * ThisItem.Pct)')}),
    label("gMN",'Text(ThisItem.N) & "×"',880,8,60,36,size=14,bold=True,color=DARK,align="Right",indent=6)]
gp={"Items":F(MIS),"TemplateSize":"=52","TemplatePadding":"=0"}; gp.update(box(942,346,948,716))
out.append(ctrl("galMis","Gallery@2.15.0",gp,0,mk,variant="BrowseLayout_Vertical_TwoTextOneImageVariant_ver5.0")); R.append("galMis")
out.append(label("rMisNone",'"No findings in this period."',950,350,900,30,size=12,color=G5,extra={"Visible":F('varTab = "res" && CountRows(galMis.AllItems) = 0')}))
T("res",*R)

# ---------- helpers (1x1 transparent buttons) ----------
HELP={"Color":F(CLEAR),"BorderColor":F(CLEAR),"HoverFill":F(CLEAR),"PressedFill":F(CLEAR),"TabIndex":"=-1"}
RESETSTD='Reset(txtStTitle); Reset(txtStNo); Reset(txtStRev); Reset(ddStType); Reset(ddStStat); Reset(txtStLine); Reset(txtStArea); Reset(ddStEq); Reset(txtStOwner); Reset(txtStRev2); Reset(txtStLink); Reset(txtStPurp); Reset(txtStSafe); Select(btnSResetEl)'
RESETEL='Reset(txtElNo); Reset(txtElName); Reset(txtElGood); Reset(txtElWhy); Reset(ddElType); Reset(addElPh)'
CLOAD=('Reset(txtCName); Reset(ddCStd); Reset(ddCTier); Reset(ddCFreq); Reset(txtCLine); Reset(txtCArea); Reset(txtCIns);\n'
       'Set(varCardActive, If(varCardNew, true, ' + CARDR + '.Active));\n'
       'ClearCollect(colShiftSel, If(varCardNew, Table({Value: "1"}, {Value: "2"}), ForAll(' + CARDR + '.Shifts, {Value: Value})));\n'
       'IfError(ClearCollect(colPick, ForAll(Filter(PC_CardItems, CardID = varCardID && Active = true), {EID: ElementID})), Clear(colPick))')
out.append(btn("btnSResetStd",'""',RESETSTD,0,1079,1,1,fill=CLEAR,color=CLEAR,extra=HELP))
out.append(btn("btnSResetEl",'""',RESETEL,2,1079,1,1,fill=CLEAR,color=CLEAR,extra=HELP))
out.append(btn("btnCLoad",'""',CLOAD,4,1079,1,1,fill=CLEAR,color=CLEAR,extra=HELP))
IS5S=f'{STD}.DocType.Value = "5S"'
EXTRA.setdefault("eT",{})["Text"]=F(f'If({IS5S}, "5S SECTIONS (photo = the standard)  ·  STANDARD ID " & varStdID & ": put it in SAF_Zones → StandardID", "ELEMENTS  —  what GOOD looks like, step by step")')
EXTRA.setdefault("cElName",{})["Text"]=F(f'If({IS5S}, "SECTION (board / bench / rack / floor area) *", "ELEMENT (major step / check point) *")')
EXTRA.setdefault("cElGood",{})["Text"]=F(f'If({IS5S}, "STANDARD CONDITION (what an auditor should see) *", "WHAT GOOD LOOKS LIKE (key points) *")')
tip("ddStType","5S = a 5S standard page: one section per area, each with a standard-condition photo. Link it to a zone in SAF_Zones (StandardID); Frontier audits compare against it.")
'''
for _ in range(2):
    out=[]
    exec(BODY)
write_themed(__import__("sys").argv[1] if len(__import__("sys").argv) > 1 else __import__("os").environ["MDI_OUTDIR"]+"/SW_Manager_v4.pa.yaml", "".join(out))
print("ok", len(out))
