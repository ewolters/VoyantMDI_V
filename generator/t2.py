# Tier 2 Board generator (1920x1080). Same control schema as HxH board.
DARK="RGBA(7, 39, 45, 1)"; TEAL_D="RGBA(0, 72, 81, 1)"; TEAL="RGBA(0, 178, 169, 1)"; AQUA="RGBA(176, 227, 228, 1)"
G9="RGBA(117, 120, 123, 1)"; G5="RGBA(177, 179, 179, 1)"; G1="RGBA(217, 217, 214, 1)"; WHITE="RGBA(255, 255, 255, 1)"
GREEN="RGBA(46, 160, 67, 1)"; AMBER="RGBA(210, 153, 34, 1)"; RED="RGBA(207, 34, 46, 1)"; ORANGE="RGBA(227, 108, 9, 1)"; CLEAR="RGBA(0, 0, 0, 0)"
GREYT="RGBA(150, 152, 155, 1)"
out=[]
def ind(s,n): return "\n".join((" "*n+l) if l else l for l in s.split("\n"))
def ctrl(name, ctype, props, indent=0, children=None, variant=None):
    p=" "*indent; s=f"{p}- {name}:\n{p}    Control: {ctype}\n"
    if variant: s+=f"{p}    Variant: {variant}\n"
    s+=f"{p}    Properties:\n"
    for k,v in props.items():
        v=str(v)
        if "\n" in v or ": " in v or "#" in v: s+=f"{p}      {k}: |-\n"+ind(v, indent+8)+"\n"
        else: s+=f"{p}      {k}: {v}\n"
    if children: s+=f"{p}    Children:\n"+"".join(children)
    return s
def F(v): return "="+v
def box(x,y,w,h): return {"X":F(str(x)),"Y":F(str(y)),"Width":F(str(w)),"Height":F(str(h))}
def label(name,text,x,y,w,h,size=12,bold=False,color=DARK,font="Arial",align=None,fill=None,valign=None,indent=0,extra=None):
    d={"Text":F(text),"Font":F("Font."+font),"Size":F(str(size)),"Color":F(color)}
    if bold: d["FontWeight"]=F("FontWeight.Bold")
    if align: d["Align"]=F("Align."+align)
    if fill: d["Fill"]=F(fill)
    if valign: d["VerticalAlign"]=F("VerticalAlign."+valign)
    d.update(box(x,y,w,h))
    if extra: d.update(extra)
    return ctrl(name,"Label@2.5.1",d,indent)
def cap(name,text,x,y,w,color=G5,indent=0): return label(name,f'"{text}"',x,y,w,20,size=9,bold=True,color=color,indent=indent)
def dd(name,items,x,y,w,h,default=None,onchange=None,size=14,bold=False,indent=0,extra=None):
    d={"Items":F(items)}
    if default: d["Default"]=F(default)
    if onchange: d["OnChange"]=F(onchange)
    d.update({"Font":F("Font.Arial"),"Size":F(str(size))})
    if bold: d["FontWeight"]=F("FontWeight.Bold")
    if extra: d.update(extra)
    d.update(box(x,y,w,h)); return ctrl(name,"Classic/DropDown@2.3.1",d,indent)
def ti(name,default,x,y,w,h,hint='""',size=14,number=False,indent=0,extra=None):
    d={"Default":F(default),"HintText":F(hint),"Font":F("Font.Arial"),"Size":F(str(size)),"BorderColor":F(G5)}
    if number: d["Format"]=F("TextFormat.Number")
    if extra: d.update(extra)
    d.update(box(x,y,w,h)); return ctrl(name,"Classic/TextInput@2.3.2",d,indent)
def btn(name,text,onselect,x,y,w,h,fill=TEAL,color=DARK,size=12,indent=0,extra=None):
    d={"Text":F(text),"OnSelect":F(onselect),"Font":F("Font.Arial"),"Size":F(str(size)),"FontWeight":F("FontWeight.Bold"),
       "Fill":F(fill),"Color":F(color),"HoverFill":F("ColorFade(Self.Fill, -15%)"),"BorderColor":F("Self.Fill"),
       "RadiusTopLeft":"=6","RadiusTopRight":"=6","RadiusBottomLeft":"=6","RadiusBottomRight":"=6"}
    if extra: d.update(extra)
    d.update(box(x,y,w,h)); return ctrl(name,"Classic/Button@2.2.0",d,indent)
def rect(name,fill,x,y,w,h,indent=0,extra=None):
    d={"Fill":F(fill)}; 
    if extra: d.update(extra)
    d.update(box(x,y,w,h)); return ctrl(name,"Rectangle@2.3.0",d,indent)
def pct(x): return f'Text(({x}) * 100, "0") & "%"'
SHM='(ddShift.Selected.Value = "All" || Text(Shift) = ddShift.Selected.Value)'        # number Shift (HxH lists)
SHC='(ddShift.Selected.Value = "All" || Shift.Value = ddShift.Selected.Value)'        # choice Shift (T2 lists)
DAY='ShiftDate >= ddDate.Selected.D && ShiftDate < DateAdd(ddDate.Selected.D, 1, TimeUnit.Days)'
DSTR='Text(ddDate.Selected.D, "yyyymmdd")'

# ---------------- header ----------------
out.append(rect("hdrBar",DARK,0,0,1920,90))
out.append(label("lblBrand",'"voyant"',24,6,170,52,size=34,color=WHITE,font="Georgia"))
out.append(label("lblBrandSub",'"NEW ALBANY"',27,56,170,24,size=10,bold=True,color=TEAL))
out.append(label("lblTitle",'"TIER 2"',190,20,170,50,size=26,bold=True,color=AQUA,font="Georgia",extra={"Wrap":"=false"}))
out.append(cap("cView","VIEW",380,6,160)); out.append(dd("ddView",'["All lines", "Value stream", "Line"]',380,28,170,52,onchange="Select(btnCalc)",size=16,bold=True))
out.append(cap("cSel",'VALUE STREAM / LINE',560,6,280))
out.append(dd("ddSel",'If(ddView.Selected.Value = "Value stream", Distinct(colLines, ValueStream), ForAll(colLines, {Value: Title}))',560,28,280,52,onchange="Select(btnCalc)",size=16,
   extra={"DisplayMode":F('If(ddView.Selected.Value = "All lines", DisplayMode.Disabled, DisplayMode.Edit)')}))
out.append(cap("cDate","DATE",850,6,190))
out.append(dd("ddDate",'ForAll(Sequence(14, 0, -1), With({d: DateAdd(Today(), Value, TimeUnit.Days)}, {Value: Text(d, "ddd m/d"), D: d}))',850,28,190,52,onchange="Select(btnRefresh)",size=16))
out.append(cap("cShift","SHIFT",1050,6,110)); out.append(dd("ddShift",'["All", "1", "2", "3"]',1050,28,110,52,onchange="Select(btnCalc)",size=18,bold=True))
LOAD=('ClearCollect(colLines, Sort(Filter(Lines, Active), DisplayOrder));\n'
 f'ClearCollect(colShift, Filter(HxH_Shift, {DAY}));\n'
 f'ClearCollect(colHr, Filter(HxH_Hourly, {DAY}));\n'
 f'ClearCollect(colQA, Filter(T2_QA, {DAY}));\n'
 f'ClearCollect(colOps, Filter(T2_Ops, {DAY}));\n'
 f'ClearCollect(colMaint, Filter(T2_Maint, {DAY}));\n'
 'ClearCollect(colEsc, Filter(Escalation_Log, NotifiedAt >= DateAdd(ddDate.Selected.D, -1, TimeUnit.Days)));\n'
 'ClearCollect(colNews, Newspaper);\n'
 'Set(varLoadedAt, Now());\n'
 'Select(btnCalc)')
out.append(btn("btnRefresh",'"REFRESH"',LOAD,1172,28,130,52,size=14))
out.append(label("lblLoaded",'If(IsBlank(varLoadedAt), "", "Updated " & Text(varLoadedAt, "h:mm AM/PM"))',1310,28,200,52,size=11,color=G5))
out.append(label("lblScope",'Switch(ddView.Selected.Value, "All lines", "All lines", "Value stream", "Value stream: " & ddSel.Selected.Value, "Line " & ddSel.Selected.Value) & "  ·  " & ddDate.Selected.Value & "  ·  " & If(ddShift.Selected.Value = "All", "All shifts", "Shift " & ddShift.Selected.Value)',
   1520,10,388,70,size=14,bold=True,color=AQUA,align="Right"))

# ---------------- calc (rows per line) ----------------
CALC=('ClearCollect(colRows,\n'
 '  ForAll(\n'
 '    Switch(ddView.Selected.Value, "All lines", colLines, "Value stream", Filter(colLines, ValueStream = ddSel.Selected.Value), Filter(colLines, Title = ddSel.Selected.Value)),\n'
 '    With({L: Title, VS: ValueStream},\n'
 f'     With({{sh: Filter(colShift, Line = L && {SHM}), hr: Filter(colHr, Line = L && {SHM}),\n'
 f'            qa: Filter(colQA, Line = L && {SHC}), op: Filter(colOps, Line = L && {SHC}), mt: Filter(colMaint, Line = L && {SHC}),\n'
 '            nw: Filter(colNews, Line = L && (Status.Value = "Open" || Status.Value = "In progress"))},\n'
 '      {Line: L, VS: VS,\n'
 '       Tgt: Sum(sh, Coalesce(TargetUnits, 0)), Act: Sum(sh, Coalesce(ActualUnits, 0)),\n'
 '       OEEw: Sum(sh, Coalesce(OEE, 0) * Coalesce(TargetUnits, 0)),\n'
 '       Safety: CountIf(hr, SafetyEvent),\n'
 '       DT: Sum(hr, Coalesce(DT_Minutes, 0) + Coalesce(DT2_Minutes, 0)),\n'
 '       Rework: Sum(qa, Coalesce(ReworkQty, 0)), Hold: Sum(qa, Coalesce(HoldQty, 0)),\n'
 '       Scrap: Sum(qa, Coalesce(ScrapQty, 0)) + Sum(sh, Coalesce(FGScrapQty, 0)),\n'
 '       Sched: Sum(op, Coalesce(ScheduledCrew, 0)), Present: Sum(op, Coalesce(PresentCrew, 0)), Absent: Sum(op, Coalesce(Absent, 0)),\n'
 '       CrewAct: Sum(sh, Coalesce(ActualCrewSize, 0)), CrewStd: Sum(sh, Coalesce(StdCrewSize, 0)),\n'
 '       MOpen: CountIf(mt, Status.Value <> "Closed"), MDT: Sum(mt, Coalesce(DowntimeMin, 0)),\n'
 f'       Esc: CountRows(Filter(colEsc, StartsWith(ShiftKey, L & "-" & {DSTR}) && (ddShift.Selected.Value = "All" || EndsWith(ShiftKey, "-S" & ddShift.Selected.Value)))),\n'
 '       AOpen: CountRows(nw), AOver: CountIf(nw, DueDate < Today()),\n'
 '       Shifts: CountRows(sh)}))));\n'
 f'With({{hs: Filter(colHr, Line in colRows.Line && {SHM})}},\n'
 '  ClearCollect(colTopDT, FirstN(SortByColumns(AddColumns(GroupBy(Filter(Ungroup(Table({t: ForAll(hs, {R: DT_Reason, M: Coalesce(DT_Minutes, 0)})}, {t: ForAll(hs, {R: DT2_Reason, M: Coalesce(DT2_Minutes, 0)})}), t), !IsBlank(R) && M > 0), R, G), Mins, Sum(G, M)), "Mins", SortOrder.Descending), 6)))')
HELP={"Color":F(CLEAR),"BorderColor":F(CLEAR),"HoverFill":F(CLEAR),"PressedFill":F(CLEAR),"TabIndex":"=-1","RadiusTopLeft":"=0","RadiusTopRight":"=0","RadiusBottomLeft":"=0","RadiusBottomRight":"=0"}
out.append(btn("btnCalc",'""',CALC,0,1079,1,1,fill=CLEAR,color=CLEAR,extra=HELP))

# ---------------- SQDCP grid ----------------
COLS=[("LINE",0,120),("SAFETY",124,160),("QUALITY",288,210),("DELIVERY",502,210),("COST · OEE",716,210),("PEOPLE",930,200),("MAINTENANCE",1134,170),("ESCAL.",1308,80),("ACTIONS",1392,96)]
out.append(rect("colHdr",TEAL_D,12,96,1488,36))
for i,(t,x,w) in enumerate(COLS):
    out.append(label(f"h{i}",f'"{t}"',12+x,96,w,36,size=11,bold=True,color=WHITE,align="Center"))
TILE_H=88; I=6
def tile(name,x,w,big,small,fill,tip,indent=I,bigsize=26):
    return [label(name,big,x,5,w,TILE_H-30,size=bigsize,bold=True,color=WHITE,align="Center",valign="Bottom",fill=fill,indent=indent,extra={"Tooltip":F(tip)}),
            label(name+"s",small,x,5+TILE_H-30,w,26,size=10,bold=True,color=WHITE,align="Center",fill=fill,indent=indent,extra={"Tooltip":F(tip)})]
kids=[]
kids.append(label("gLine",'ThisItem.Line',0,5,120,TILE_H,size=24,bold=True,color=WHITE,align="Center",fill=DARK,indent=I,font="Georgia"))
kids.append(label("gVS",'ThisItem.VS',0,5+TILE_H-24,120,22,size=8,color=AQUA,align="Center",indent=I))
NODATA='ThisItem.Shifts = 0'
kids+=tile("tS",124,160,'If(ThisItem.Safety = 0, "✓", Text(ThisItem.Safety))','If(ThisItem.Safety = 0, "no events", If(ThisItem.Safety = 1, "event", "events"))',
           f'If(ThisItem.Safety = 0, {GREEN}, {RED})','"Safety incidents / near misses flagged on the hour-by-hour board."')
kids+=tile("tQ",288,210,'Text(ThisItem.Rework + ThisItem.Hold + ThisItem.Scrap, "#,##0")','"RW " & Text(ThisItem.Rework) & " · HOLD " & Text(ThisItem.Hold) & " · SCRAP " & Text(ThisItem.Scrap)',
           f'If(ThisItem.Hold > 0, {RED}, ThisItem.Rework + ThisItem.Scrap > 0, {AMBER}, {GREEN})','"Units: rework + hold (QA input) + scrap (QA input + FG scrap from the board). Red = anything on hold."')
kids+=tile("tD",502,210,f'If(ThisItem.Tgt = 0, "—", {pct("ThisItem.Act / ThisItem.Tgt")})','If(ThisItem.Tgt = 0, "no board data", Text(ThisItem.Act, "#,##0") & " / " & Text(ThisItem.Tgt, "#,##0"))',
           f'If(ThisItem.Tgt = 0, {GREYT}, ThisItem.Act / ThisItem.Tgt >= 1, {GREEN}, ThisItem.Act / ThisItem.Tgt >= 0.9, {AMBER}, {RED})','"Attainment = actual units / target units (from the hour-by-hour board shift records)."')
kids+=tile("tC",716,210,f'If(ThisItem.Tgt = 0, "—", {pct("ThisItem.OEEw / ThisItem.Tgt")})','"DT " & Text(ThisItem.DT) & " min reported"',
           f'If(ThisItem.Tgt = 0, {GREYT}, ThisItem.OEEw / ThisItem.Tgt >= 0.65, {GREEN}, ThisItem.OEEw / ThisItem.Tgt >= 0.5, {AMBER}, {RED})','"OEE (target-weighted across shifts) from the board. DT = DT1 + DT2 minutes logged on the board."')
kids+=tile("tP",930,200,'If(ThisItem.Sched > 0, Text(ThisItem.Present) & "/" & Text(ThisItem.Sched), ThisItem.CrewStd > 0, Text(ThisItem.CrewAct) & "/" & Text(ThisItem.CrewStd), "—")',
           'If(ThisItem.Sched > 0, "present / sched · absent " & Text(ThisItem.Absent), ThisItem.CrewStd > 0, "actual / std crew (board)", "no crewing data")',
           f'If(ThisItem.Sched > 0, If(ThisItem.Present >= ThisItem.Sched, {GREEN}, {AMBER}), ThisItem.CrewStd > 0, If(ThisItem.CrewAct > ThisItem.CrewStd, {AMBER}, {GREEN}), {GREYT})',
           '"Ops crewing input (present / scheduled). If Ops has not entered, falls back to actual vs standard crew from the board."')
kids+=tile("tM",1134,170,'If(ThisItem.MOpen = 0, "✓", Text(ThisItem.MOpen) & " open")','Text(ThisItem.MDT) & " min maint DT"',
           f'If(ThisItem.MDT >= 60, {RED}, ThisItem.MOpen > 0, {AMBER}, {GREEN})','"Maintenance input: open issues (not Closed) and downtime minutes they logged."',bigsize=22)
kids+=tile("tE",1308,80,'Text(ThisItem.Esc)','If(ThisItem.Esc = 1, "alert", "alerts")',f'If(ThisItem.Esc = 0, {GREEN}, {RED})','"Downtime escalation notifications sent (60/120/240 min levels) for this line and day."')
kids+=tile("tA",1392,96,'Text(ThisItem.AOpen)','If(ThisItem.AOver > 0, Text(ThisItem.AOver) & " overdue", "open")',f'If(ThisItem.AOver > 0, {RED}, ThisItem.AOpen > 0, {AMBER}, {GREEN})','"Open NEWSPAPER actions for this line. Red = past due."')
gprops={"Items":F("colRows"),"TemplateSize":F(str(TILE_H+10)),"TemplatePadding":"=0","ShowScrollbar":"=true","TemplateFill":F(WHITE),"BorderThickness":"=0"}
gprops.update(box(12,134,1488,690))
out.append(ctrl("galRows","Gallery@2.15.0",gprops,0,kids,variant="BrowseLayout_Vertical_TwoTextOneImageVariant_ver5.0"))
out.append(label("lblEmpty",'If(CountRows(colRows) = 0, If(ddView.Selected.Value = "Value stream" && ddSel.Selected.Value = "(assign)", "Assign value streams in the Lines list to use this view.", "No lines in this selection."), "")',12,300,1488,60,size=18,color=G9,align="Center"))

# ---------------- bottom: pareto + totals ----------------
out.append(rect("botBar","RGBA(244, 245, 245, 1)",12,830,1488,240))
out.append(label("lblPareto",'"TOP DOWNTIME REASONS (minutes, selection)"',24,834,700,26,size=11,bold=True,color=TEAL_D))
pk=[label("pR",'ThisItem.R',0,2,300,30,size=12,bold=True,indent=I),
    rect("pBar",TEAL_D,305,6,f"ThisItem.Mins / Max(First(colTopDT).Mins, 1) * 480",22,indent=I),
    label("pM",'Text(ThisItem.Mins) & " min"',305,2,600,30,size=12,bold=True,color=DARK,indent=I,extra={"X":F("305 + ThisItem.Mins / Max(First(colTopDT).Mins, 1) * 480 + 8")})]
pg={"Items":F("colTopDT"),"TemplateSize":"=33","TemplatePadding":"=0","ShowScrollbar":"=false"}; pg.update(box(24,862,900,200))
out.append(ctrl("galPareto","Gallery@2.15.0",pg,0,pk,variant="BrowseLayout_Vertical_TwoTextOneImageVariant_ver5.0"))
out.append(label("lblNoDT",'If(CountRows(colTopDT) = 0, "No downtime reasons logged for this selection.", "")',24,900,900,30,size=12,color=G9))
TOT=[("kAtt","DELIVERY",f'If(Sum(colRows, Tgt) = 0, "—", {pct("Sum(colRows, Act) / Sum(colRows, Tgt)")})',f'If(Sum(colRows, Tgt) = 0, {GREYT}, Sum(colRows, Act) / Sum(colRows, Tgt) >= 1, {GREEN}, Sum(colRows, Act) / Sum(colRows, Tgt) >= 0.9, {AMBER}, {RED})'),
     ("kOEE","OEE",f'If(Sum(colRows, Tgt) = 0, "—", {pct("Sum(colRows, OEEw) / Sum(colRows, Tgt)")})',f'If(Sum(colRows, Tgt) = 0, {GREYT}, Sum(colRows, OEEw) / Sum(colRows, Tgt) >= 0.65, {GREEN}, Sum(colRows, OEEw) / Sum(colRows, Tgt) >= 0.5, {AMBER}, {RED})'),
     ("kSaf","SAFETY",'If(Sum(colRows, Safety) = 0, "✓", Text(Sum(colRows, Safety)))',f'If(Sum(colRows, Safety) = 0, {GREEN}, {RED})'),
     ("kAct","OVERDUE",'Text(Sum(colRows, AOver))',f'If(Sum(colRows, AOver) > 0, {RED}, {GREEN})')]
for i,(n,c,v,f) in enumerate(TOT):
    x=940+i*138
    out.append(label(n,v,x,846,130,150,size=34,bold=True,color=WHITE,align="Center",valign="Bottom",fill=f,font="Georgia",extra={"PaddingBottom":"=14"}))
    out.append(label(n+"c",f'"{c}"',x,852,130,24,size=10,bold=True,color=WHITE,align="Center"))
out.append(label("lblTotCap",'"SELECTION TOTALS"',940,1004,546,24,size=10,bold=True,color=G9,align="Center"))

# ---------------- right: NEWSPAPER ----------------
RX=1512; RW=396
out.append(rect("npHdr",DARK,RX,96,RW,36))
out.append(label("npTitle",'"NEWSPAPER  ·  OPEN ACTIONS"',RX+10,96,260,36,size=12,bold=True,color=AQUA))
out.append(btn("btnAdd",'"+ ACTION"','Set(varAdd, true)',RX+RW-110,100,100,28,size=11))
NEWS_ITEMS='SortByColumns(Filter(colNews, Line in colRows.Line && (Status.Value = "Open" || Status.Value = "In progress")), "DueDate", SortOrder.Ascending)'
CYCLE=('With({nx: Switch(ThisItem.Status.Value, "Open", "In progress", "In progress", "Done", "Open")},\n'
       '  Patch(Newspaper, LookUp(Newspaper, ID = ThisItem.ID), {Status: {Value: nx}, ClosedDate: If(nx = "Done", Today(), Blank())}));\n'
       'ClearCollect(colNews, Newspaper);\nSelect(btnCalc)')
nk=[rect("nBg","RGBA(247, 248, 248, 1)",4,4,RW-28,108,indent=I),
    rect("nStripe",'Switch(ThisItem.SQDCP.Value, "Safety", '+RED+', "Quality", RGBA(123, 63, 160, 1), "Delivery", '+TEAL_D+', "Cost", '+AMBER+', "People", '+TEAL+', '+G9+')',4,4,8,108,indent=I),
    label("nTitle",'ThisItem.Title',20,6,RW-140,44,size=13,bold=True,indent=I),
    label("nMeta",'"Line " & ThisItem.Line & "  ·  " & ThisItem.SQDCP.Value & "  ·  " & Coalesce(ThisItem.Owner, "no owner")',20,50,RW-60,24,size=10,color=G9,indent=I),
    label("nDue",'"Due " & Text(ThisItem.DueDate, "m/d") & If(ThisItem.DueDate < Today(), "  OVERDUE", "")',20,76,RW-160,28,size=12,bold=True,indent=I,
          extra={"Color":F(f'If(ThisItem.DueDate < Today(), {RED}, {DARK})')}),
    btn("nStatus",'ThisItem.Status.Value',CYCLE,RW-138,72,110,32,size=10,color=WHITE,indent=I,
        fill=f'If(ThisItem.Status.Value = "Open", {RED}, {AMBER})',extra={"Tooltip":'="Tap to advance: Open → In progress → Done"'})]
ng={"Items":F(NEWS_ITEMS),"TemplateSize":"=116","TemplatePadding":"=0","ShowScrollbar":"=true"}; ng.update(box(RX,134,RW,936))
out.append(ctrl("galNews","Gallery@2.15.0",ng,0,nk,variant="BrowseLayout_Vertical_TwoTextOneImageVariant_ver5.0"))
out.append(label("lblNoNews",f'If(CountRows({NEWS_ITEMS}) = 0, "No open actions for this selection.", "")',RX,200,RW,40,size=12,color=G9,align="Center"))

# ---------------- add-action overlay ----------------
V={"Visible":"=varAdd"}
out.append(rect("ovDim","RGBA(7, 39, 45, 0.55)",0,0,1920,1080,extra=V))
out.append(rect("ovPanel",WHITE,560,170,800,700,extra=V))
out.append(rect("ovHdr",DARK,560,170,800,60,extra=V))
out.append(label("ovTitle",'"NEW NEWSPAPER ACTION"',584,170,600,60,size=18,bold=True,color=AQUA,font="Georgia",extra=V))
def vx(d): d=dict(d or {}); d.update(V); return d
out.append(cap("ocA","ACTION (WHAT WILL BE DONE)",584,246,700,color=G9).replace("Properties:\n","Properties:\n      Visible: =varAdd\n",1))
out.append(ti("txtAAction",'""',584,268,752,48,hint='"e.g. Replace worn filler nozzle gaskets"',size=15,extra=vx(None)))
out.append(cap("ocL","LINE",584,330,150,color=G9).replace("Properties:\n","Properties:\n      Visible: =varAdd\n",1))
out.append(dd("ddALine",'ForAll(colLines, {Value: Title})',584,352,150,48,size=15,extra=vx({"Default":F('If(ddView.Selected.Value = "Line", ddSel.Selected.Value, First(colRows).Line)')})))
out.append(cap("ocS","SQDCP",746,330,200,color=G9).replace("Properties:\n","Properties:\n      Visible: =varAdd\n",1))
out.append(dd("ddASQ",'["Safety", "Quality", "Delivery", "Cost", "People"]',746,352,200,48,size=15,extra=vx(None)))
out.append(cap("ocD","DUE",958,330,200,color=G9).replace("Properties:\n","Properties:\n      Visible: =varAdd\n",1))
out.append(dd("ddADue",'ForAll(Sequence(30, 1), With({d: DateAdd(Today(), Value, TimeUnit.Days)}, {Value: Text(d, "ddd m/d"), D: d}))',958,352,200,48,size=15,extra=vx({"Default":F('Text(DateAdd(Today(), 7, TimeUnit.Days), "ddd m/d")')})))
out.append(cap("ocO","OWNER",1170,330,170,color=G9).replace("Properties:\n","Properties:\n      Visible: =varAdd\n",1))
out.append(ti("txtAOwner",'""',1170,352,166,48,hint='"name"',size=15,extra=vx(None)))
out.append(cap("ocP","PROBLEM (WHAT HAPPENED)",584,414,700,color=G9).replace("Properties:\n","Properties:\n      Visible: =varAdd\n",1))
out.append(ti("txtAProblem",'""',584,436,752,140,hint='"What happened, where, how much"',size=14,extra=vx({"Mode":"=TextMode.MultiLine"})))
out.append(cap("ocC","COUNTERMEASURE (OPTIONAL)",584,590,700,color=G9).replace("Properties:\n","Properties:\n      Visible: =varAdd\n",1))
out.append(ti("txtACM",'""',584,612,752,110,hint='"Containment / root-cause fix"',size=14,extra=vx({"Mode":"=TextMode.MultiLine"})))
SAVEA=('Patch(Newspaper, Defaults(Newspaper),\n'
 '  {Title: txtAAction.Text, Line: ddALine.Selected.Value,\n'
 '   ValueStream: LookUp(colLines, Title = ddALine.Selected.Value).ValueStream,\n'
 '   SQDCP: {Value: ddASQ.Selected.Value}, Source: {Value: "Tier 2"}, Status: {Value: "Open"},\n'
 '   Problem: txtAProblem.Text, Countermeasure: txtACM.Text, Owner: txtAOwner.Text,\n'
 '   RaisedDate: Today(), DueDate: ddADue.Selected.D});\n'
 'Reset(txtAAction); Reset(txtAProblem); Reset(txtACM); Reset(txtAOwner);\n'
 'Set(varAdd, false);\n'
 'ClearCollect(colNews, Newspaper);\nSelect(btnCalc)')
out.append(btn("btnASave",'"SAVE ACTION"',SAVEA,1176,790,160,52,size=14,color=WHITE,fill=GREEN,
   extra=vx({"DisplayMode":F('If(IsBlank(txtAAction.Text) || IsBlank(txtAOwner.Text), DisplayMode.Disabled, DisplayMode.Edit)')})))
out.append(btn("btnACancel",'"CANCEL"','Set(varAdd, false)',1004,790,160,52,size=14,color=DARK,fill=G1,extra=vx(None)))
out.append(label("ocReq",'"Action and owner are required."',584,800,400,30,size=11,color=G9,extra=V))

open("/mnt/user-data/outputs/T2_Board_v1.pa.yaml","w").write("".join(out))
print("ok",sum(len(x) for x in out))
