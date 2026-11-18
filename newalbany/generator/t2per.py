# Tier 2 WEEKS & MONTHS screen (scrPeriods). Reuses the Tier 2 metric formulas (t2v2.py) per line per week/month.
import os, re
_OUTD = os.environ.pop("MDI_OUTDIR", None) or os.environ["MDI_TMP"]
_SCR=__import__("os").environ["MDI_TMP"]+"/_t2_tmp.yaml"
_OUT=os.environ.get("T2POUT", _OUTD+"/T2_Periods_v2.pa.yaml")
os.environ["T2OUT"]=_SCR
exec(open(__import__("os").environ["MDI_GEN"]+"/t2v2.py").read())
out=[]   # fresh control list for the new screen

REN=[("colShift","colPShift"),("colQA","colPQA"),("colTS","colPTS"),("colWv","colPWv"),("colPC","colPPC"),("colSafe","colPSafe"),
     ("colFR","colPFR"),("colFA","colPFA"),("colDTH","colPDTH"),("colEsc","colPEsc"),("colNews","colPNews"),("ddShift","ddPShift"),("ddVS","ddPVS")]
def ren(x):
    for a,b in REN: x=re.sub(r'\b'+a+r'\b', b, x)
    return x
def must(x, a, b):
    assert x.count(a)>=1, a; return x.replace(a,b)

# ---- one record per line per PERIOD (pp = row of colPer) ----
PREC=ren(DAYREC)
PREC=must(PREC,'With({dD: DateAdd(varD0, k.Value, TimeUnit.Days), L: ln.Title},','With({dD: pp.S, L: ln.Title},')
PREC=must(PREC,'With({dE: DateAdd(dD, 1, TimeUnit.Days), DKy: Text(dD, "yyyymmdd")},','With({dE: pp.E, K0: Value(Text(pp.S, "yyyymmdd")), K1: Value(Text(pp.E, "yyyymmdd"))},')
PREC=must(PREC,'StartsWith(ShiftKey, L & "-" & DKy)','StartsWith(ShiftKey, L & "-") && IfError(Value(Mid(ShiftKey, Len(L) + 2, 8)), 0) >= K0 && IfError(Value(Mid(ShiftKey, Len(L) + 2, 8)), 0) < K1')
PREC=must(PREC,'nDy * If(sh > 0, 1, 0)','nDy * CountRows(Distinct(shs, ShiftDate))')
PREC=must(PREC,'DueDate < dD','DueDate < DateAdd(dE, -1, TimeUnit.Days)')
PREC=must(PREC,'{Line: L, VS: ln.ValueStream, Ord: ln.DisplayOrder, Day: dD,','{Line: L, VS: ln.ValueStream, Ord: ln.DisplayOrder, N: pp.N, Day: dD,')
assert "DKy" not in PREC and "varD0" not in PREC
# ---- one record per DAY for the line/period the user tapped (k over days from varPS) ----
PDAY=ren(DAYREC)
PDAY=must(PDAY,'DateAdd(varD0, k.Value, TimeUnit.Days)','DateAdd(varPS, k.Value, TimeUnit.Days)')
assert "varD0" not in PDAY
# ---- PLANT total per period ----
PTOT=ren(TOTREC)
PTOT=must(PTOT,'With({dD: DateAdd(varD0, k.Value, TimeUnit.Days)},','With({dD: pp.S},')
PTOT=must(PTOT,'Filter(colDaily, Day = dD)','Filter(colPAgg, N = pp.N)')
PTOT=PTOT.replace('DateAdd(dD, 1, TimeUnit.Days)','pp.E')
PTOT=must(PTOT,'{Day: dD,','{N: pp.N, Day: dD,')
assert "varD0" not in PTOT and "colDaily" not in PTOT

def SW(rec, f): return 'Switch(Coalesce(varPDom, "D"), '+", ".join(f'"{k}", {rec}{f}{k}' for k in DK)+')'
PCOL=lambda st: f'Switch({st}, "G", {GREEN}, "A", {AMBER}, "R", {RED}, "L", {DARK}, "T", {TEAL_D}, {GREYT})'
WEEK0='DateAdd(Today(), 1 - Weekday(Today(), StartOfWeek.Monday), TimeUnit.Days)'
MON0='Date(Year(Today()), Month(Today()), 1)'
FROMITEMS=(f'If(varPMode = "M", ForAll(Sequence(6, 0), With({{s: DateAdd({MON0}, -Value, TimeUnit.Months)}}, {{Value: Text(s, "mmm yyyy"), S: s}})),'
           f' ForAll(Sequence(26, 0), With({{s: DateAdd({WEEK0}, -7 * Value, TimeUnit.Days)}}, {{Value: "Wk of " & Text(s, "m/d/yy"), S: s}})))')
FROMDEF=(f'If(varPMode = "M", Text(DateAdd({MON0}, -2, TimeUnit.Months), "mmm yyyy"), "Wk of " & Text(DateAdd({WEEK0}, -84, TimeUnit.Days), "m/d/yy"))')
TODEF=(f'If(varPMode = "M", Text({MON0}, "mmm yyyy"), "Wk of " & Text({WEEK0}, "m/d/yy"))')

def LDP(coll,src,nm): return f'IfError(ClearCollect({coll}, {src}), Notify("Trends: could not load {nm}", NotificationType.Error));\n'
def CHUNK(coll,lst,col,extra,nm):  # load a big list one week at a time (stays under the row limit)
    return (f'Clear({coll});\nIfError(ForAll(Sequence(RoundUp(DateDiff(varP0, varP1, TimeUnit.Days) / 7, 0), 0) As w,\n'
            f' Collect({coll}, Filter({lst}, {col} >= DateAdd(varP0, 7 * w.Value, TimeUnit.Days) && {col} < DateAdd(varP0, 7 * w.Value + 7, TimeUnit.Days){extra}))),\n'
            f' Notify("Trends: could not load {nm}", NotificationType.Error));\n')
PW='ShiftDate >= varP0 && ShiftDate < varP1'
LOADP=('Set(varPBusy, true); Set(varPSel, false);\n'
 'With({f: ddPFrom.Selected.S, t: ddPTo.Selected.S}, Set(varPF, If(f <= t, f, t)); Set(varPT, If(f <= t, t, f)));\n'
 'ClearCollect(colPer, If(varPMode = "M",\n'
 '  ForAll(Sequence(DateDiff(varPF, varPT, TimeUnit.Months) + 1, 0), With({s: DateAdd(varPF, Value, TimeUnit.Months)}, With({e: DateAdd(s, 1, TimeUnit.Months)},\n'
 '   {N: Value, S: s, E: If(e > Today(), DateAdd(Today(), 1, TimeUnit.Days), e), Lbl: Upper(Text(s, "mmm yy")), Lbl2: Text(s, "mmmm yyyy"), ToDate: e > Today()}))),\n'
 '  ForAll(Sequence(RoundDown(DateDiff(varPF, varPT, TimeUnit.Days) / 7, 0) + 1, 0), With({s: DateAdd(varPF, 7 * Value, TimeUnit.Days)}, With({e: DateAdd(s, 7, TimeUnit.Days)},\n'
 '   {N: Value, S: s, E: If(e > Today(), DateAdd(Today(), 1, TimeUnit.Days), e), Lbl: "WK " & Text(s, "m/d"), Lbl2: "Week of " & Text(s, "mmm d") & " – " & Text(DateAdd(s, 6, TimeUnit.Days), "mmm d"), ToDate: e > Today()})))));\n'
 'Set(varP0, First(colPer).S); Set(varP1, Last(colPer).E);\n'
 + LDP("colCfg","MDI_Config","MDI_Config")
 + CFG("varAG","T2_AttainGreen",90)+CFG("varAA","T2_AttainAmber",80)+CFG("varOG","T2_OEEGreen",65)+CFG("varOA","T2_OEEAmber",50)
 + CFG("varRA","T2_ReworkAmber",0.5)+CFG("varRR","T2_ReworkRed",2)+CFG("varPCG","T2_PCGreen",90)+CFG("varDA","T2_DTAmber",30)+CFG("varDR","T2_DTRed",60)+CFG("varTSReq","T2_TSRequiredMin",15)
 + LDP("colLines","Sort(Filter(Lines, Active), DisplayOrder)","Lines")
 + LDP("colPB","PLAYBOOK","PLAYBOOK")
 + LDP("colMR",'Filter(Lookups, Category.Value = "Downtime")',"Lookups (downtime reasons)")
 + 'RemoveIf(colMR, IsBlank(EquipType));\n'
 + LDP("colCards","Filter(PC_Cards, Active = true)","PC_Cards")
 + CHUNK("colPShift","HxH_Shift","ShiftDate","","HxH_Shift")
 + CHUNK("colPDTH","HxH_Hourly","ShiftDate"," && (DT_Minutes > 0 || DT2_Minutes > 0)","HxH_Hourly (downtime)")
 + LDP("colPSafe",f"Filter(HxH_Hourly, {PW} && SafetyEvent = true)","HxH_Hourly (safety)")
 + LDP("colPFA","Filter(SAF_Audits, AuditDate >= varP0 && AuditDate < varP1)","SAF_Audits")
 + LDP("colPFR","Filter(SAF_Results, AuditDate >= varP0 && AuditDate < varP1)","SAF_Results")
 + 'RemoveIf(colPFR, !(Rating.Value = "AR" || Rating.Value = "U" || (Rating.Value = "Deficient" && SafetyRelevant)));\n'
 + CHUNK("colPQA","QA_Rework","ShiftDate"," && Voided = false","QA_Rework")
 + CHUNK("colPTSAll","TS_Occurrences","ShiftDate","","TS_Occurrences")
 + 'ClearCollect(colPTS, Filter(colPTSAll, LinkStatus.Value <> "Waived")); ClearCollect(colPWv, Filter(colPTSAll, LinkStatus.Value = "Waived"));\n'
 + CHUNK("colPPC","PC_Audits","ShiftDate","","PC_Audits")
 + LDP("colPEsc","Filter(Escalation_Log, NotifiedAt >= DateAdd(varP0, -1, TimeUnit.Days) && NotifiedAt < DateAdd(varP1, 1, TimeUnit.Days))","Escalation_Log")
 + LDP("colPNews",'Filter(Newspaper, Status.Value = "Open" || Status.Value = "In progress" || ClosedDate >= varP0)',"Newspaper")
 + 'Set(varPLoadedAt, Now()); Set(varPBusy, false);\nSelect(btnPCalc)')

CALCP=('Set(varPBusy, true); Set(varPSel, false);\n'
 'ClearCollect(colPScope, Filter(colLines, ddPVS.Selected.Value = "All value streams" || ValueStream = ddPVS.Selected.Value));\n'
 'ClearCollect(colPAgg, Ungroup(ForAll(colPScope As ln,\n'
 '  With({nEv: CountRows(Filter(colCards, Frequency.Value = "Every shift" && (Line = "All" || ln.Title in Split(Line, ",")))),\n'
 '        nDy: CountRows(Filter(colCards, Frequency.Value = "Daily" && (Line = "All" || ln.Title in Split(Line, ","))))},\n'
 '   {rows: ForAll(colPer As pp,\n   ' + PREC + ')})), rows));\n'
 'ClearCollect(colPTot, ForAll(colPer As pp,\n  ' + PTOT + '));\n'
 'With({s: SortByColumns(Filter(colPScope As ln, varPIdle || CountRows(Filter(colPAgg, Line = ln.Title && Shifts > 0)) > 0), "ValueStream", SortOrder.Ascending, "DisplayOrder", SortOrder.Ascending)},\n'
 ' ClearCollect(colPRows, ForAll(Sequence(CountRows(s)), With({x: Index(s, Value)}, {Line: x.Title, VS: x.ValueStream, R: Value}))));\n'
 'Set(varPBusy, false);\nSelect(btnPGrid)')

NS=26; ND=31
def CREC(src,cond,i): return f'C{i}: With({{x: LookUp({src}, {cond}N = {i})}}, {{Tx: '+SW("x.","txt")+', Sb: '+SW("x.","sub")+', St: '+SW("x.","st")+'})'
GRID=('Set(varPNP, CountRows(colPer)); Set(varPCW, RoundDown(1896 / (varPNP + 1), 0));\n'
 'ClearCollect(colPGrid, {Line: "PLANT", VS: Text(CountRows(colPRows)) & " lines", R: 0, LSt: "T",\n  '
 + ",\n  ".join(CREC("colPTot","",i) for i in range(NS)) + '});\n'
 'ForAll(colPRows As rr, Collect(colPGrid, {Line: rr.Line, VS: rr.VS, R: rr.R, LSt: "L",\n  '
 + ",\n  ".join(CREC("colPAgg","Line = rr.Line && ",i) for i in range(NS)) + '}))')

OPENB=(''
 'With({pp: LookUp(colPer, N = varPN)}, Set(varPS, pp.S); Set(varPE, pp.E); Set(varPLbl, pp.Lbl2));\n'
 'Set(varPRec, LookUp(colPAgg, Line = varPLine && N = varPN));\n'
 'With({ln: LookUp(colLines, Title = varPLine)},\n'
 ' With({nEv: CountRows(Filter(colCards, Frequency.Value = "Every shift" && (Line = "All" || ln.Title in Split(Line, ",")))),\n'
 '       nDy: CountRows(Filter(colCards, Frequency.Value = "Daily" && (Line = "All" || ln.Title in Split(Line, ","))))},\n'
 '  ClearCollect(colPDays, ForAll(Sequence(DateDiff(varPS, varPE, TimeUnit.Days), 0) As k,\n   ' + PDAY + '))));\n'
 'Set(varPDW, RoundDown(1896 / Max(CountRows(colPDays), 1), 0));\n'
 'Set(varPSel, true)')

# =========================== HEADER ===========================
out.append(rect("pHdrBar",DARK,0,0,1920,90))
out.append(label("pBrand",'"voyant"',24,6,170,52,size=34,color=WHITE,font="Georgia"))
out.append(label("pBrandSub",'"NEW ALBANY"',27,56,170,24,size=10,bold=True,color=TEAL))
out.append(label("pTitle",'"TIER 2"',190,6,170,40,size=26,bold=True,color=AQUA,font="Georgia",extra={"Wrap":"=false"}))
out.append(label("pTitleSub",'"WEEKS & MONTHS"',192,50,180,24,size=10,bold=True,color=WHITE))
out.append(cap("pcView","VIEW",380,6,220))
for i,(m,t) in enumerate([("W","WEEKS"),("M","MONTHS")]):
    out.append(btn(f"pbView{m}",f'"{t}"',f'Set(varPMode, "{m}")',380+i*112,28,108,52,size=13,
        fill=f'If(Coalesce(varPMode, "W") = "{m}", {TEAL}, {TEAL_D})',color=f'If(Coalesce(varPMode, "W") = "{m}", {DARK}, {WHITE})'))
out.append(cap("pcFrom","FROM",616,6,190)); out.append(dd("ddPFrom",FROMITEMS,616,28,190,52,default=FROMDEF,size=14,bold=True))
out.append(cap("pcTo","TO",816,6,190));     out.append(dd("ddPTo",FROMITEMS,816,28,190,52,default=TODEF,size=14,bold=True))
out.append(cap("pcVS","VALUE STREAM",1016,6,240))
out.append(dd("ddPVS",'Ungroup(Table({t: Table({Value: "All value streams"})}, {t: Distinct(colLines, ValueStream)}), t)',1016,28,240,52,onchange="If(!IsEmpty(colPer), Select(btnPCalc))",size=14,bold=True))
out.append(cap("pcShift","SHIFT",1266,6,100)); out.append(dd("ddPShift",'["All", "1", "2", "3"]',1266,28,100,52,onchange="If(!IsEmpty(colPer), Select(btnPCalc))",size=16,bold=True))
out.append(btn("btnPLoad",'If(varPBusy, "LOADING…", "LOAD")',LOADP,1376,28,130,52,size=14,
   extra={"Tooltip":'="Load the weeks or months picked in FROM and TO. Up to 6 months back; older data is archived."'}))
out.append(btn("btnPIdle",'If(varPIdle, "ALL LINES", "RUNNING LINES")','Set(varPIdle, !varPIdle); If(!IsEmpty(colPer), Select(btnPCalc))',1516,28,150,52,size=11,fill=TEAL_D,color=WHITE,
   extra={"Tooltip":'="Running lines = lines with board data in the range. Tap to switch."'}))
out.append(btn("btnPBack",'"◂  DAILY"','Back()',1676,28,120,52,size=13,fill=AQUA,color=DARK,extra={"Tooltip":'="Back to the daily Tier 2 board"'}))
out.append(label("pLoaded",'If(varPBusy, "Working…", IsBlank(varPLoadedAt), "Pick a range, then LOAD", "Updated" & Char(10) & Text(varPLoadedAt, "h:mm AM/PM"))',1806,28,110,52,size=10,color=G5))
out.append(tap("btnPCalc",CALCP,0,1079,1,1))
out.append(tap("btnPGrid",GRID,2,1079,1,1))
out.append(tap("btnPOpen",OPENB,4,1079,1,1))

# =========================== DOMAIN TABS ===========================
out.append(rect("pSubBar",LIGHT,0,90,1920,48))
for i,(k,n) in enumerate(DOMS):
    out.append(btn(f"pTab{k}",f'"{n}"',f'Set(varPDom, "{k}"); Select(btnPGrid)',12+i*152,96,146,36,size=10,
        fill=f'If(Coalesce(varPDom, "D") = "{k}", {DARK}, {G1})',color=f'If(Coalesce(varPDom, "D") = "{k}", {WHITE}, {DARK})',extra={"Tooltip":F(f'"{TIPS[k]}"')}))
out.append(label("pHint",'If(IsEmpty(colPGrid), "", "Tap a cell to see that line day by day.")',1390,96,518,36,size=11,color=G9,align="Right"))

# =========================== GRID (fixed column slots, no wrap) ===========================
HV='!IsEmpty(colPGrid)'
out.append(V(rect("phLBg",TEAL_D,12,142,'varPCW - 2',46),HV))
out.append(V(label("phL",'"LINE"',12,142,'varPCW - 2',46,size=11,bold=True,color=WHITE,align="Center"),HV))
for i in range(NS):
    x=f'12 + {i+1} * varPCW'; v=f'varPNP > {i}'
    out.append(V(rect(f"ph{i}Bg",TEAL_D,x,142,'varPCW - 2',46),v))
    out.append(V(label(f"ph{i}",f'LookUp(colPer, N = {i}).Lbl',x,144,'varPCW - 2',24,size='If(varPNP > 13, 9, 11)',bold=True,color=WHITE,align="Center",extra={"Wrap":"=false"}),v))
    out.append(V(label(f"ph{i}s",f'If(LookUp(colPer, N = {i}).ToDate, "to date", "")',x,168,'varPCW - 2',18,size=8,color=AQUA,align="Center"),v))
SMALL='varPNP > 13'
cell=[rect("pcLBg",'If(ThisItem.LSt = "T", '+TEAL_D+', '+DARK+')',"0","2","varPCW - 2","58",indent=I),
      label("pcL",'ThisItem.Line',"2","4","varPCW - 6","32",size=f'If({SMALL}, 12, 15)',bold=True,color=WHITE,align="Center",indent=I,extra={"Wrap":"=false"}),
      label("pcLs",'ThisItem.VS',"2","34","varPCW - 6","24",size=8,color=AQUA,align="Center",indent=I,extra={"Visible":F(f'!({SMALL})')})]
for i in range(NS):
    x=f'{i+1} * varPCW'; v=f'varPNP > {i}'; c=f'ThisItem.C{i}'
    cell.append(rect(f"pc{i}Bg",PCOL(f'{c}.St'),x,"2","varPCW - 2","58",indent=I,extra={"Visible":F(v),"Tooltip":F(f'{c}.Sb')}))
    cell.append(label(f"pc{i}Tx",f'Coalesce({c}.Tx, "—")',x,"4","varPCW - 2","32",size=f'If({SMALL}, 11, 17)',bold=True,color=WHITE,align="Center",indent=I,extra={"Visible":F(v),"Wrap":"=false"}))
    cell.append(label(f"pc{i}Sb",f'{c}.Sb',x,"34","varPCW - 2","24",size=8,color=WHITE,align="Center",indent=I,extra={"Visible":F(f'{v} && !({SMALL})')}))
    cell.append(tap(f"pc{i}Tap",f'Set(varPLine, ThisItem.Line); Set(varPN, {i}); Select(btnPOpen)',x,"2","varPCW - 2","58",indent=I,tip='"Open " & ThisItem.Line & " day by day"',vis=f'{v} && ThisItem.LSt = "L"'))
out.append(gal("galPGrid",'SortByColumns(colPGrid, "R", SortOrder.Ascending)',12,190,1896,'If(varPSel, 430, 884)',62,cell,extra={"ShowScrollbar":"=true"}))
out.append(label("pEmpty",'If(varPBusy, "Loading… larger ranges take longer.", IsEmpty(colPer), "Pick WEEKS or MONTHS, a FROM and TO, then tap LOAD.", "No lines with data in this range. Try ALL LINES.")',
   12,300,1896,80,size=18,color=G9,align="Center",extra={"Visible":F('IsEmpty(colPRows) || varPBusy')}))

# =========================== DETAIL (line x period, day by day) ===========================
VP='varPSel'
def vp(s): return V(s,VP)
out.append(vp(rect("pdBg",WHITE,0,624,1920,456,extra={"BorderColor":F(TEAL),"BorderThickness":"=3"})))
out.append(vp(label("pdTitle",'"LINE " & varPLine & "  ·  " & varPLbl',16,630,1200,40,size=20,bold=True,color=DARK,font="Georgia")))
out.append(vp(btn("pdClose",'"✕  CLOSE"','Set(varPSel, false)',1786,634,120,36,size=11,fill=G1,color=DARK)))
for i,(k,n) in enumerate(DOMS):
    x=12+i*212
    out.append(vp(rect(f"pdb{k}",COL(f"varPRec.st{k}"),x,676,206,96,extra={"BorderColor":F(DARK),"BorderThickness":F(f'If(Coalesce(varPDom, "D") = "{k}", 4, 0)')})))
    out.append(vp(label(f"pdn{k}",f'"{n}"',x,678,206,20,size=9,bold=True,color=WHITE,align="Center")))
    out.append(vp(label(f"pdv{k}",f"varPRec.txt{k}",x,698,206,40,size=20,bold=True,color=WHITE,align="Center")))
    out.append(vp(label(f"pds{k}",f"varPRec.sub{k}",x,738,206,32,size=8,color=WHITE,align="Center")))
    out.append(vp(tap(f"pdt{k}",f'Set(varPDom, "{k}"); Select(btnPGrid)',x,676,206,96,tip=f'"Show {n.title()} day by day"')))
PDN='Switch(Coalesce(varPDom, "D"), '+", ".join(f'"{k}", "{n}"' for k,n in DOMS)+')'
out.append(vp(label("pdDayHdr",PDN+' & " day by day  ·  " & '+SW("varPRec.","tgt"),16,778,1600,30,size=12,bold=True,color=G9)))
DSM='CountRows(colPDays) > 10'
for j in range(ND):
    d=f'Last(FirstN(colPDays, {j+1}))'; x=f'12 + {j} * varPDW'; v=f'{VP} && CountRows(colPDays) > {j}'
    out.append(V(rect(f"py{j}Bg",COL(SW(d+".","st")),x,812,'varPDW - 2',120,extra={"Tooltip":F(SW(d+".","sub"))}),v))
    out.append(V(label(f"py{j}D",f'Text({d}.Day, "ddd")',x,816,'varPDW - 2',20,size=9,bold=True,color=WHITE,align="Center"),v))
    out.append(V(label(f"py{j}D2",f'Text({d}.Day, "m/d")',x,834,'varPDW - 2',20,size=9,color=WHITE,align="Center"),v))
    out.append(V(label(f"py{j}V",SW(d+".","txt"),x,858,'varPDW - 2',40,size=f'If({DSM}, 11, 18)',bold=True,color=WHITE,align="Center"),v))
    out.append(V(label(f"py{j}S",SW(d+".","sub"),f'{x} + 2',898,'varPDW - 6',32,size=7,color=WHITE,align="Center"),f'{v} && !({DSM})'))
out.append(vp(label("pdFoot",'"Gray = no data that day.  Hover a day for detail.  Open the DAILY board on any day for the full drill-down."',16,940,1600,28,size=10,color=G9)))

yaml="".join(out)
write_themed(_OUT, yaml)
print("ok",len(yaml),"controls",yaml.count("    Control:"))
