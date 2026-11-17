# Generates QA_Rework_v4.pa.yaml (1920x1080) — QA rework entry + quality dashboard
exec(open("/tmp/claude-0/gen/theme.py").read())
src=open('/tmp/claude-0/gen/build6.py').read()
exec(src[:src.index("DT_OLD=")])
EXTRA.clear()
MUTE="RGBA(243, 244, 244, 1)"; PANEL="RGBA(248, 249, 249, 1)"
BODY=r'''def tip(name,text): EXTRA.setdefault(name,{})["Tooltip"]='="'+text.replace('"','""')+'"'
RAD={"RadiusTopLeft":"=6","RadiusTopRight":"=6","RadiusBottomLeft":"=6","RadiusBottomRight":"=6"}

# ---------- header ----------
out.append(rect("hdrBar",DARK,0,0,1920,90))
out.append(label("lblBrand",'"voyant"',24,6,170,52,size=34,color=WHITE,font="Georgia"))
out.append(label("lblBrandSub",'"NEW ALBANY"',27,56,170,24,size=10,bold=True,color=TEAL))
out.append(label("lblTitle",'"QUALITY  ·  REWORK"',190,20,420,50,size=24,bold=True,color=WHITE,font="Georgia"))
out.append(label("lblUser",'"Logged in: " & User().FullName',1500,20,400,50,size=12,color=G5,align="Right"))

# ---------- LEFT: entry panel ----------
LX=12; LW=700
out.append(rect("entryBg",PANEL,LX,98,LW,974))
out.append(label("lblEntryT",'"LOG REWORK"',LX+16,104,400,32,size=16,bold=True,color=DARK,font="Georgia"))
CTX=('Set(varQS, LookUp(HxH_Shift, Title = ddQLine.Selected.Value & "-" & Text(ddQDate.Selected.D, "yyyymmdd") & "-S" & ddQShift.Selected.Value));\n'
     'Reset(ddQProd); Reset(txtQJob)')
out.append(cap("cQLine","LINE",LX+16,142,120)); out.append(dd("ddQLine","Distinct(PLAYBOOK, Line)",LX+16,164,130,52,default='"209"',onchange="Select(btnQCtx)",size=20,bold=True))
out.append(cap("cQDate","SHIFT DATE",LX+156,142,200)); out.append(dd("ddQDate",'ForAll(Sequence(14, 0, -1), With({d: DateAdd(Today(), Value, TimeUnit.Days)}, {Value: Text(d, "ddd m/d"), D: d}))',LX+156,164,200,52,onchange="Select(btnQCtx)",size=18))
out.append(cap("cQShift","SHIFT",LX+366,142,100)); out.append(dd("ddQShift",'["1", "2", "3"]',LX+366,164,100,52,onchange="Select(btnQCtx)",size=20,bold=True))
out.append(label("lblQCtx",'If(IsBlank(varQS), "No HxH board for this shift yet — pick product and job below.", "From HxH: " & varQS.ProductForm & "  ·  job " & Coalesce(varQS.Job1, "—"))',
   LX+476,150,LW-492,70,size=11,color=G9))
out.append(cap("cQProd","PRODUCT  (SIZE | FORM)  — FROM PLAYBOOK",LX+16,228,420))
out.append(dd("ddQProd",'ForAll(Filter(PLAYBOOK, Line = ddQLine.Selected.Value), {Value: Size & " | " & Form, Size: Size, Form: Form})',LX+16,250,440,52,
   default='Coalesce(varQS.ProductForm, "")',size=17))
out.append(cap("cQJob","JOB #",LX+466,228,200))
out.append(ti("txtQJob",'Coalesce(varQS.Job1, "")',LX+466,250,LW-482,52,'false',hint='"job #"',size=18,bold=True,number=False))

out.append(cap("cQReason","REWORK REASON  — TAP ONE",LX+16,316,400))
rk=[btn("gQReason",'ThisItem.Value','Set(varReason, ThisItem.Value)',4,4,320,60,
        fill=f'If((!IsBlank(varReason) && varReason = ThisItem.Value), {TEAL_D}, {WHITE})',color=f'If((!IsBlank(varReason) && varReason = ThisItem.Value), {WHITE}, {DARK})',size=15,indent=6,
        extra={"BorderColor":F(f'If((!IsBlank(varReason) && varReason = ThisItem.Value), {TEAL_D}, {G5})'),"BorderThickness":"=2","Tooltip":F('Coalesce(ThisItem.Help, "Lookups list → Category Rework")'),**RAD})]
gp={"Items":F("colRR"),"WrapCount":"=2","TemplateSize":"=68","TemplatePadding":"=0","ShowScrollbar":"=true"}
gp.update(box(LX+8,338,LW-16,210))
out.append(ctrl("galQReason","Gallery@2.15.0",gp,0,rk,variant="BrowseLayout_Vertical_TwoTextOneImageVariant_ver5.0"))

out.append(label("lblQNoReasons",'"No rework reasons loaded — press REFRESH, or add rows to Lookups (Category = Rework)."',LX+16,350,LW-32,40,size=12,color=G9,extra={"Visible":"=CountRows(colRR) = 0"}))
out.append(cap("cQQty","REWORK UNITS",LX+16,556,200))
out.append(ti("txtQQty",'""',LX+16,578,200,64,'false',hint='"0"',size=26,bold=True))
out.append(cap("cQNotes","NOTES  (OPTIONAL)",LX+228,556,300))
out.append(ti("txtQNotes",'""',LX+228,578,LW-244,64,'false',hint='"what happened, lot #, where found"',size=13,number=False,extra={"Align":"=Align.Left"}))
OK=('!IsBlank(ddQProd.Selected.Value) && !IsBlank(txtQJob.Text) && !IsBlank(varReason) && Coalesce(Value(txtQQty.Text), 0) > 0')
SAVE=('IfError(\n Patch(QA_Rework, Defaults(QA_Rework),\n'
 ' {Ref: ddQLine.Selected.Value & "-" & Text(ddQDate.Selected.D, "yyyymmdd") & "-S" & ddQShift.Selected.Value & "-" & Text(Now(), "hhmmss"),\n'
 '  Line: ddQLine.Selected.Value, ShiftDate: ddQDate.Selected.D, Shift: Value(ddQShift.Selected.Value),\n'
 '  ShiftKey: ddQLine.Selected.Value & "-" & Text(ddQDate.Selected.D, "yyyymmdd") & "-S" & ddQShift.Selected.Value,\n'
 '  Size: ddQProd.Selected.Size, Form: ddQProd.Selected.Form, ProductForm: ddQProd.Selected.Size & " " & ddQProd.Selected.Form,\n'
 '  PlaybookKey: ddQLine.Selected.Value & "|" & ddQProd.Selected.Size & "|" & ddQProd.Selected.Form,\n'
 '  Job: txtQJob.Text, Reason: varReason, ReworkQty: Value(txtQQty.Text), Notes: txtQNotes.Text, EnteredBy: User().Email}),\n'
 ' Notify("NOT SAVED — " & FirstError.Message & "  (check connection, try again)", NotificationType.Error),\n'
 ' Notify(Text(Value(txtQQty.Text)) & " units logged — " & varReason, NotificationType.Success);\n'
 ' Reset(txtQQty); Reset(txtQNotes); Set(varReason, Blank());\n'
 ' Select(btnQRefresh))')
out.append(btn("btnQSave",f'If({OK}, "SAVE REWORK", "PICK PRODUCT · JOB · REASON · UNITS")',SAVE,LX+16,656,LW-32,64,fill=f'If({OK}, {TEAL_D}, {G1})',color=f'If({OK}, {WHITE}, {G9})',size=16,
   extra={"DisplayMode":F(f'If({OK}, DisplayMode.Edit, DisplayMode.Disabled)'),"DisabledFill":F(G1),"DisabledColor":F(G9),**RAD}))

# required-field cues (yellow = still needed)
YEL="RGBA(255, 242, 179, 1)"; YELB="RGBA(210, 153, 34, 1)"
for n,empty in [("txtQJob","IsBlank(Self.Text)"),("txtQQty","Coalesce(Value(Self.Text), 0) <= 0")]:
    EXTRA.setdefault(n,{}).update({"Fill":F(f'If({empty}, {YEL}, {WHITE})'),"BorderColor":F(f'If({empty}, {YELB}, {G5})'),"BorderThickness":F(f'If({empty}, 3, 1)')})
EXTRA.setdefault("ddQProd",{}).update({"Fill":F(f'If(IsBlank(Self.Selected.Value), {YEL}, {WHITE})')})

# this shift's entries
out.append(label("lblQListT",'"THIS SHIFT  ·  " & ddQLine.Selected.Value & "  ·  " & ddQDate.Selected.Value & "  ·  S" & ddQShift.Selected.Value & "   —   " & Text(Coalesce(Sum(galQList.AllItems, ReworkQty), 0), "#,##0") & " units"',
   LX+16,732,LW-32,28,size=12,bold=True,color=G9))
lk=[label("gLReason",'ThisItem.Reason',8,4,220,40,size=13,bold=True,color=DARK,indent=6),
    label("gLProd",'ThisItem.ProductForm & "  ·  job " & ThisItem.Job',230,4,260,40,size=11,color=G9,indent=6),
    label("gLQty",'Text(ThisItem.ReworkQty, "#,##0")',490,4,80,40,size=16,bold=True,color=DARK,align="Right",indent=6),
    btn("gLDel",'"VOID"','IfError(Patch(QA_Rework, LookUp(QA_Rework, ID = ThisItem.ID), {Voided: true}),\n Notify("NOT VOIDED — " & FirstError.Message, NotificationType.Error),\n Notify("Entry voided. It no longer counts anywhere; an admin can remove it.", NotificationType.Information); Select(btnQRefresh))',584,8,56,32,fill=WHITE,color=G9,size=9,indent=6,
        extra={"DisplayMode":F('If(ThisItem.EnteredBy = User().Email, DisplayMode.Edit, DisplayMode.Disabled)'),"BorderColor":F(G1),"DisabledFill":F(CLEAR),"DisabledColor":F(CLEAR),
               "Tooltip":'="Void this entry if it was a mistake (only the person who entered it). Voided entries are kept for audit but excluded from every count."'})]
gp={"Items":F('SortByColumns(Filter(colQA, Line = ddQLine.Selected.Value && ShiftDate >= ddQDate.Selected.D && ShiftDate < DateAdd(ddQDate.Selected.D, 1, TimeUnit.Days) && Shift = Value(ddQShift.Selected.Value)), "Created", SortOrder.Descending)'),
    "TemplateSize":"=48","TemplatePadding":"=0","BorderColor":F(G1),"BorderThickness":"=1"}
gp.update(box(LX+8,762,LW-16,300))
out.append(ctrl("galQList","Gallery@2.15.0",gp,0,lk,variant="BrowseLayout_Vertical_TwoTextOneImageVariant_ver5.0"))
out.append(label("lblQEmpty",'"No rework logged for this shift."',LX+16,780,LW-32,40,size=12,color=G5,extra={"Visible":"=CountRows(galQList.AllItems) = 0"}))

# ---------- RIGHT: quality dashboard ----------
RX=724; RW=1184
out.append(label("lblDashT",'"QUALITY DASHBOARD"',RX,104,400,32,size=16,bold=True,color=DARK,font="Georgia"))
PER='Table({Value: "Today", N: 0}, {Value: "Last 7 days", N: 6}, {Value: "Last 30 days", N: 29})'
out.append(cap("cDPer","PERIOD",RX+420,98,200)); out.append(dd("ddDPer",PER,RX+420,118,200,44,default='"Last 7 days"',onchange="Select(btnQRefresh)",size=14))
out.append(cap("cDLine","LINE",RX+630,98,200)); out.append(dd("ddDLine",'Ungroup(Table({t: Table({Value: "All lines"})}, {t: Distinct(PLAYBOOK, Line)}), t)',RX+630,118,180,44,default='"All lines"',size=14))
out.append(cap("cDForm","FORM",RX+820,98,200)); out.append(dd("ddDForm",'Ungroup(Table({t: Table({Value: "All forms"})}, {t: Distinct(PLAYBOOK, Form)}), t)',RX+820,118,220,44,default='"All forms"',size=14))
LOAD=('IfError(ClearCollect(colLk, Filter(Lookups, Active = true)), Notify("Could not load Lookups — " & FirstError.Message, NotificationType.Error));\n'
 'ClearCollect(colRR, ForAll(Sort(Filter(colLk, Category.Value = "Rework"), SortOrder), {Value: Label, Help: Help}));\n'
 'Set(varFrom, DateAdd(Today(), -Coalesce(ddDPer.Selected.N, 6), TimeUnit.Days));\n'
 'Set(varQFrom, Min(varFrom, DateAdd(Today(), -13, TimeUnit.Days)));\n'
 'IfError(ClearCollect(colQA, Filter(QA_Rework, ShiftDate >= varQFrom && Voided = false)), Notify("Could not load QA_Rework — " & FirstError.Message, NotificationType.Error));\n'
 'IfError(ClearCollect(colQS, Filter(HxH_Shift, ShiftDate >= varFrom)), Notify("Could not load HxH_Shift — " & FirstError.Message, NotificationType.Warning));\n'
 'Set(varQLoaded, Now())')
out.append(btn("btnQRefresh",'"REFRESH"',LOAD,RX+RW-130,112,130,50,fill=TEAL_D,color=WHITE,size=13,extra=RAD))
tip("btnQRefresh","Reload rework entries, reasons and HxH units from SharePoint.")

# filtered set used by every visual
QF=('Filter(colQA, ShiftDate >= varFrom && (ddDLine.Selected.Value = "All lines" || Line = ddDLine.Selected.Value) && (ddDForm.Selected.Value = "All forms" || Form = ddDForm.Selected.Value))')
SF=('Filter(colQS, (ddDLine.Selected.Value = "All lines" || Line = ddDLine.Selected.Value) && (ddDForm.Selected.Value = "All forms" || EndsWith(ProductForm, ddDForm.Selected.Value)))')
def tile(name,capt,val,x,w,tipt):
    out.append(label(name,val,x,172,w,120,size=34,bold=True,color=DARK,fill=MUTE,align="Center",valign="Bottom",pb=14))
    out.append(label(name+"C",f'"{capt}"',x,178,w,24,size=10,bold=True,color=G9,align="Center"))
    tip(name,tipt)
TW=(RW-3*12)//4
tile("kQUnits","REWORK UNITS",f'Text(Coalesce(Sum({QF}, ReworkQty), 0), "#,##0")',RX,TW,"Total units reworked in the period (filters applied).")
tile("kQRate","REWORK % OF UNITS MADE",f'With({{r: Coalesce(Sum({QF}, ReworkQty), 0), m: Coalesce(Sum({SF}, Coalesce(ActualUnits, 0)), 0)}}, If(m <= 0, "—", Text(r / m * 100, "0.00") & "%"))',RX+TW+12,TW,
     "Rework units / units produced on the HxH boards for the same period, line and form.")
tile("kQEntries","ENTRIES",f'Text(CountRows({QF}))',RX+2*(TW+12),TW,"Number of rework entries logged.")
tile("kQTop","TOP REASON",f'Coalesce(First(SortByColumns(AddColumns(GroupBy({QF}, Reason, G), Qty, Sum(G, ReworkQty)), "Qty", SortOrder.Descending)).Reason, "—")',RX+3*(TW+12),TW,"Reason with the most rework units.")
EXTRA.setdefault("kQTop",{})["Size"]="=20"

def bars(name,title,keyexpr,keycol,x,y,w,h,tipt):
    out.append(rect(name+"Bg",WHITE,x,y,w,h))
    out.append(label(name+"T",f'"{title}"',x+12,y+6,w-24,28,size=12,bold=True,color=DARK))
    items=(f'With({{t: SortByColumns(AddColumns(GroupBy({QF}, {keyexpr}, G), Qty, Sum(G, ReworkQty)), "Qty", SortOrder.Descending)}},\n'
           f' With({{mx: Coalesce(Max(t, Qty), 0), tot: Coalesce(Sum(t, Qty), 0)}}, AddColumns(t, Pct, If(mx > 0, Qty / mx, 0), Share, If(tot > 0, Qty / tot, 0))))')
    bw=w-24-200-110
    k=[label(name+"K",f'ThisItem.{keycol}',4,4,196,36,size=12,bold=True,color=DARK,indent=6),
       ctrl(name+"Bar","Rectangle@2.3.0",{"Fill":F(TEAL_D),"X":"=204","Y":"=10","Height":"=24","Width":F(f'Max(2, {bw} * ThisItem.Pct)')},6),
       label(name+"V",'Text(ThisItem.Qty, "#,##0") & "  (" & Text(ThisItem.Share * 100, "0") & "%)"',204+bw+6,4,104,36,size=11,bold=True,color=G9,indent=6)]
    gp={"Items":F(items),"TemplateSize":"=44","TemplatePadding":"=0"}
    gp.update(box(x+6,y+38,w-12,h-44))
    out.append(ctrl("gal"+name,"Gallery@2.15.0",gp,0,k,variant="BrowseLayout_Vertical_TwoTextOneImageVariant_ver5.0"))
    out.append(label(name+"E",'"No rework in this period."',x+12,y+44,w-24,30,size=12,color=G5,extra={"Visible":F(f'CountRows({QF}) = 0')}))
    tip(name+"T",tipt)
HW=(RW-12)//2
bars("bReason","BY REASON",'Reason','Reason',RX,304,HW,360,"Pareto of rework units by reason.")
bars("bForm","BY FORM",'Form','Form',RX+HW+12,304,HW,360,"Rework units by product form (from the PLAYBOOK).")
bars("bLine","BY LINE",'Line','Line',RX,676,HW,392,"Rework units by line.")

# top jobs table
JX=RX+HW+12; JY=676
out.append(rect("jobsBg",WHITE,JX,JY,HW,392))
out.append(label("jobsT",'"TOP JOBS"',JX+12,JY+6,300,28,size=12,bold=True,color=DARK))
for t,x,w,a in [("JOB",12,120,None),("LINE",136,60,None),("FORM",200,190,None),("TOP REASON",394,0,None)]:
    pass
hdr=[("JOB",12,130,None),("LINE",146,60,None),("FORM",210,170,None),("TOP REASON",384,0,None),("UNITS",0,0,"Right")]
out.append(label("jH1",'"JOB"',JX+12,JY+36,130,22,size=9,bold=True,color=G9))
out.append(label("jH2",'"LINE"',JX+146,JY+36,60,22,size=9,bold=True,color=G9))
out.append(label("jH3",'"FORM"',JX+210,JY+36,160,22,size=9,bold=True,color=G9))
out.append(label("jH4",'"TOP REASON"',JX+374,JY+36,HW-374-100,22,size=9,bold=True,color=G9))
out.append(label("jH5",'"UNITS"',JX+HW-100,JY+36,88,22,size=9,bold=True,color=G9,align="Right"))
JI=(f'FirstN(SortByColumns(AddColumns(GroupBy({QF}, Job, Line, Form, G), Qty, Sum(G, ReworkQty),\n'
    '  TopR, First(SortByColumns(AddColumns(GroupBy(G, Reason, R), RQ, Sum(R, ReworkQty)), "RQ", SortOrder.Descending)).Reason), "Qty", SortOrder.Descending), 8)')
jk=[label("jJob",'ThisItem.Job',6,2,130,36,size=12,bold=True,color=DARK,indent=6),
    label("jLine",'ThisItem.Line',140,2,60,36,size=12,color=DARK,indent=6),
    label("jForm",'ThisItem.Form',204,2,160,36,size=11,color=G9,indent=6),
    label("jTop",'ThisItem.TopR',368,2,HW-12-368-100,36,size=11,color=G9,indent=6),
    label("jQty",'Text(ThisItem.Qty, "#,##0")',HW-12-100,2,88,36,size=14,bold=True,color=DARK,align="Right",indent=6)]
gp={"Items":F(JI),"TemplateSize":"=40","TemplatePadding":"=0"}
gp.update(box(JX+6,JY+58,HW-12,326))
out.append(ctrl("galJobs","Gallery@2.15.0",gp,0,jk,variant="BrowseLayout_Vertical_TwoTextOneImageVariant_ver5.0"))

out.append(label("lblQLoaded",'If(IsBlank(varQLoaded), "Not loaded — press REFRESH", "Loaded " & Text(varQLoaded, "h:mm AM/PM"))',RX+RW-330,1050,200,22,size=10,color=G9,align="Right"))

# tooltips for entry
for n,t in {"ddQLine":"Line the rework came from.","ddQDate":"Date the shift STARTED.","ddQShift":"Shift the product was made on.",
 "ddQProd":"Product from the PLAYBOOK. Defaults to what the HxH board shows for this shift.",
 "txtQJob":"REQUIRED. Job number. Defaults to Job 1 from the HxH board for this shift.",
 "txtQQty":"REQUIRED. Units reworked.","txtQNotes":"Optional detail.","btnQSave":"Saves one rework entry. Log each reason separately."}.items(): tip(n,t)

# helper: shift context loader (1x1, transparent)
HELP={"Color":F(CLEAR),"BorderColor":F(CLEAR),"HoverFill":F(CLEAR),"PressedFill":F(CLEAR),"TabIndex":"=-1"}
out.append(btn("btnQCtx",'""',CTX,0,1079,1,1,fill=CLEAR,color=CLEAR,extra=HELP))
'''
for _ in range(2):
    out=[]
    exec(BODY)
write_themed("/mnt/user-data/outputs/QA_Rework_v4.pa.yaml", "".join(out))
print("ok", len(out))
