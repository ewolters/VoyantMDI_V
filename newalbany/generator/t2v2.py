# Tier 2 Board v2 generator (1920x1080). Layers: FLOOR -> LINE | DOMAIN -> CELL (line x domain). 7-day trend.
exec(open(__import__("os").environ["MDI_GEN"]+"/theme.py").read())
import os
HERE=os.path.dirname(os.path.abspath(__file__))
src=open(os.path.join(HERE,"t2.py")).read().split("# ---------------- header")[0]
exec(src)   # palette + ctrl/label/btn/rect/dd/ti helpers
exec(open(os.path.join(HERE,"harvey.py")).read())
OUT=os.environ.get("T2OUT", os.path.join(HERE,"..","T2_Board_v20.pa.yaml"))
LIGHT="RGBA(244, 245, 245, 1)"
HELP={"Color":F(CLEAR),"BorderColor":F(CLEAR),"HoverFill":"=RGBA(0, 178, 169, 0.08)","PressedFill":"=RGBA(0, 178, 169, 0.15)","TabIndex":"=-1",
      "RadiusTopLeft":"=0","RadiusTopRight":"=0","RadiusBottomLeft":"=0","RadiusBottomRight":"=0"}
def tap(name,onselect,x,y,w,h,indent=0,tip=None,vis=None):
    e=dict(HELP)
    if tip: e["Tooltip"]=F(tip)
    if vis: e["Visible"]=F(vis)
    return btn(name,'""',onselect,x,y,w,h,fill=CLEAR,color=CLEAR,indent=indent,extra=e)
def V(s,cond):  # add Visible to a control string
    return s.replace("Properties:\n",f"Properties:\n{' '*(len(s)-len(s.lstrip()))}      Visible: ={cond}\n",1)
def gal(name,items,x,y,w,h,tsize,kids,wrap=None,extra=None,vis=None):
    d={"Items":F(items),"TemplateSize":F(str(tsize)),"TemplatePadding":"=0","ShowScrollbar":"=true","BorderThickness":"=0"}
    if wrap: d["WrapCount"]=F(str(wrap))
    if vis: d["Visible"]=F(vis)
    if extra: d.update(extra)
    d.update(box(x,y,w,h))
    return ctrl(name,"Gallery@2.15.0",d,0,kids,variant="BrowseLayout_Vertical_TwoTextOneImageVariant_ver5.0")
I=6
HRMAX='Set(varHrMax, Max(Filter(colHrDay, Line = varLine), Max(Coalesce(HourlyTarget, 0), Coalesce(HourlyActual, 0))))'

HEX={"G":"#2EA043","A":"#D29922","R":"#CF222E"}
def svgchart(tbexpr,W,H,values=False):
    TOP=26 if values else 8; BOT=24 if values else 20; PH=H-TOP-BOT; SW=W/7
    col='Switch(S, "G", "%s", "A", "%s", "R", "%s", "#B1B3B3")'%(HEX["G"],HEX["A"],HEX["R"])
    f=lambda e: f'Text({e}, "0.0")'
    bh=f'Max(V / sc * {PH}, 2)'
    cx=f'(i * {SW:.3f} + {SW/2:.3f})'
    cyT=f'({TOP + PH} - T / sc * {PH})'
    fs=12 if values else 10
    svg=(f'"<svg xmlns=\'http://www.w3.org/2000/svg\' width=\'{W}\' height=\'{H}\' viewBox=\'0 0 {W} {H}\'>" & '
         # highlight day reviewed
         f'Concat(Filter(tb, D = varD), "<rect x=\'" & {f(f"i * {SW:.3f} + 2")} & "\' y=\'0\' width=\'{SW-4:.1f}\' height=\'{H}\' fill=\'#EEF6F6\'/>") & '
         # baseline
         f'"<line x1=\'0\' y1=\'{TOP+PH}\' x2=\'{W}\' y2=\'{TOP+PH}\' stroke=\'#D9D9D6\' stroke-width=\'1\'/>" & '
         # bars
         f'Concat(tb, "<rect x=\'" & {f(f"i * {SW:.3f} + {SW*0.22:.3f}")} & "\' y=\'" & {f(f"{TOP+PH} - {bh}")} & "\' width=\'{SW*0.56:.1f}\' height=\'" & {f(bh)} & "\' rx=\'2\' fill=\'" & {col} & "\'/>") & '
         # target line + points
         f'If(CountRows(Filter(tb, T >= 0)) > 1, "<polyline fill=\'none\' stroke=\'#07272D\' stroke-width=\'2.5\' stroke-linejoin=\'round\' points=\'" & Concat(Filter(tb, T >= 0), {f(cx)} & "," & {f(cyT)} & " ") & "\'/>", "") & '
         f'Concat(Filter(tb, T >= 0), "<circle cx=\'" & {f(cx)} & "\' cy=\'" & {f(cyT)} & "\' r=\'{5 if values else 3.5}\' fill=\'#07272D\' stroke=\'white\' stroke-width=\'1.5\'/>") & '
         # day labels
         f'Concat(tb, "<text x=\'" & {f(cx)} & "\' y=\'{H-6}\' font-family=\'Arial\' font-size=\'{fs}\' text-anchor=\'middle\' fill=\'" & If(D = varD, "#07272D", "#75787B") & "\' font-weight=\'" & If(D = varD, "bold", "normal") & "\'>" & Text(D, "{"ddd m/d" if values else "ddd"}") & "</text>") & ')
    if values:
        svg+=(f'Concat(tb, "<text x=\'" & {f(cx)} & "\' y=\'" & {f(f"{TOP+PH} - {bh} - 7")} & "\' font-family=\'Arial\' font-size=\'13\' font-weight=\'bold\' text-anchor=\'middle\' fill=\'" & {col} & "\'>" & Substitute(Substitute(Tx, "&", "and"), "<", "") & "</text>") & ')
    svg+='"</svg>"'
    return ('With({tb0: '+tbexpr+'},\n With({sc: Max(Coalesce(Max(tb0, V), 0), Coalesce(Max(tb0, T), 0), 0.0001) * 1.15},\n'
            '  With({tb: ForAll(Sequence(CountRows(tb0)), With({r: Index(tb0, Value)}, {i: Value - 1, V: Coalesce(r.V, 0), T: Coalesce(r.T, -1), S: r.S, Tx: r.Tx, D: r.Day}))},\n'
            '   "data:image/svg+xml;utf8," & EncodeUrl(' + svg + '))))')
def svgimg(name,expr,x,y,w,h,vis):
    d={"Image":F(expr),"ImagePosition":"=ImagePosition.Fit","Visible":F(vis)}; d.update(box(x,y,w,h))
    return ctrl(name,"Image@2.2.3",d,0)

def COL(st): return f'Switch({st}, "G", {GREEN}, "A", {AMBER}, "R", {RED}, {GREYT})'
def DOT(tr,i): return f'Switch(Mid({tr}, {i}, 1), "G", {GREEN}, "A", {AMBER}, "R", {RED}, {G1})'

DOMS=[("S","SAFETY"),("Q","QUALITY"),("D","DELIVERY"),("DT","DOWNTIME"),("C","COST · OEE"),("P","PEOPLE"),("M","MAINTENANCE"),("PC","PROCESS CONF."),("A","ACTIONS")]
DK=[k for k,_ in DOMS]
SWB=lambda f: 'Switch(varDom, '+", ".join(f'"{k}", {f}{k}' for k in DK)+')'
DNAME='Switch(varDom, '+", ".join(f'"{k}", "{n}"' for k,n in DOMS)+')'
TIPS={"S":"Safety events flagged on the hour-by-hour board (near misses / incidents), plus hazards found in safety audits (AR/U items, 5S flagged as hazards). Red = event or Critical/High hazard.",
      "Q":"Rework units (QA Rework app) as % of units produced. Scrap = FG scrap from the board.",
      "D":"Attainment = actual units / target units (HxH shift records).",
      "DT":"Unplanned downtime minutes from the board. Event = one line, shift and reason (minutes added across hours). Red = escalated or 60+ min per shift.",
      "C":"OEE, target-weighted across shifts, plus FG scrap units.",
      "P":"Actual crew vs PLAYBOOK standard crew (HxH). Red = short, amber = over standard.",
      "M":"Troubleshooting occurrences, fixes an operator could have done, issues not resolved, and UNLINKED: TS records with no board event + board machine stops with no TS record.",
      "PC":"Process-confirmation audits done vs due (cards x shifts run), and how many failed.",
      "A":"NEWSPAPER actions open at the end of the day, and how many were past due."}
# ---- metric definitions over base vars ----
DEF={
 "S":('If(sf = 0 && fch = 0, "✓", Text(sf) & If(fch > 0, " + " & Text(fch) & " C/H", ""))','If(sh = 0 && fa = 0, "no shifts", If(sf = 0, "no events", Text(sf) & If(sf = 1, " event", " events"))) & If(fa > 0, " · " & Text(fz) & If(fz = 1, " hazard", " hazards") & " in " & Text(fa) & If(fa = 1, " safety audit", " safety audits"), "")','If(sh = 0 && sf = 0 && fa = 0, "N", sf > 0 || fch > 0, "R", fz > 0, "A", "G")','Min(sf + fch, 3) / 3'),
 "Q":('If(a = 0, "—", Text(rw / a * 100, "0.0") & "%")','Text(rw, "#,##0") & " rework · " & Text(sc, "#,##0") & " scrap"','If(a = 0, "N", rw / a * 100 >= varRR, "R", rw / a * 100 >= varRA, "A", "G")','If(a = 0 || Coalesce(varRR, 0) = 0, 0, Min(rw / a * 100 / (2 * varRR), 1))'),
 "D":('If(pt = 0, "—", Text(a / pt * 100, "0") & "%")','If(pt = 0, "no board data", Text(a, "#,##0") & " / " & Text(pt, "#,##0"))','If(pt = 0, "N", a / pt * 100 >= varAG, "G", a / pt * 100 >= varAA, "A", "R")','If(pt = 0, 0, Min(a / pt, 1.2) / 1.2)'),
 "DT":('If(sh = 0, "—", Text(dt) & " min")','If(sh = 0, "", dte = 0, "no events", Text(dte) & If(dte = 1, " event", " events") & " · max " & Text(dtl) & "m" & If(escl > 0, " · L" & escl, ""))','If(sh = 0, "N", escl > 0 || dt / sh >= varDR, "R", dt / sh >= varDA, "A", "G")','If(sh = 0 || Coalesce(varDR, 0) = 0, 0, Min(dt / sh / (1.5 * varDR), 1))'),
 "C":('If(t = 0, "—", Text(o / t * 100, "0") & "%")','If(t = 0, "", Text(sc, "#,##0") & " units scrapped")','If(t = 0, "N", o / t >= If(t = 0 || effw = 0, varOG / 100, effw / t), "G", o / t >= If(t = 0 || effw = 0, varOG / 100, effw / t) - (varOG - varOA) / 100, "A", "R")','If(t = 0, 0, Min(o / t, 1.2) / 1.2)'),
 "P":('If(cs = 0, "—", Text(ca) & " / " & Text(cs))','If(cs = 0, "", ca > cs, "+" & Text(ca - cs) & " over std", ca < cs, Text(cs - ca) & " short", "on standard")','If(cs = 0, "N", ca < cs, "R", ca > cs, "A", "G")','If(cs = 0, 0, Min(ca / cs, 1.25) / 1.25)'),
 "M":('If(sh = 0 && tsn = 0, "—", Text(tsn) & " TS")','If(tsu > 0, Text(tsu) & " unlinked · ", "") & If(mnt > 0, Text(mnt) & If(mnt = 1, " stop", " stops") & " w/o TS · ", "") & Text(tsop) & " op-fix" & If(tsnr > 0, " · " & Text(tsnr) & " not fixed", "")','If(sh = 0 && tsn = 0, "N", tsnr > 0, "R", tsop > 0 || tsu > 0 || mnt > 0, "A", "G")','Min(tsn / 6, 1)'),
 "PC":('If(pcx = 0, "—", Text(pcd) & " / " & Text(pcx))','If(pcx = 0, "no cards due", pcd = 0, "none done", Text(pcf) & " failed")','If(pcx = 0, "N", pcd = 0, "R", pcd < pcx || (pcd - pcf) / pcd * 100 < varPCG, "A", "G")','If(pcx = 0, 0, Min(pcd / pcx, 1))'),
 "A":('Text(ao)','If(ov > 0, Text(ov) & " overdue", "open")','If(ov > 0, "R", ao > 0, "A", "G")','Min(ao / 6, 1)'),
}
EF='If(t = 0 || effw = 0, varOG / 100, effw / t)'
VAL={"S":'sf',"Q":'If(a = 0, 0, rw / a * 100)',"D":'a',"DT":'dt',"C":'If(t = 0, 0, o / t * 100)',"P":'ca',"M":'tsn',"PC":'pcd',"A":'ao'}
TG={"S":'-1',"Q":'If(a = 0, -1, varRA)',"D":'If(pt = 0, -1, pt)',"DT":'If(sh = 0, -1, varDA * sh)',"C":f'If(t = 0, -1, {EF} * 100)',"P":'If(cs = 0, -1, cs)',"M":'-1',"PC":'If(pcx = 0, -1, pcx)',"A":'-1'}
TGT={"S":'"target: zero"',"Q":'"limit " & Text(varRA) & "% rework"',"D":'If(pt = 0, "", "plan " & Text(pt, "#,##0") & " (PLAYBOOK rate × run hrs)")',"DT":'If(sh = 0, "", "allowance " & Text(varDA * sh) & " min (" & Text(varDA) & "/shift)")',
     "C":f'If(t = 0, "", "target " & Text({EF} * 100, "0") & "% (PLAYBOOK)")',"P":'If(cs = 0, "", "standard crew " & Text(cs) & " (PLAYBOOK)")',"M":'"target: zero unresolved"',"PC":'If(pcx = 0, "", Text(pcx) & " audits due")',"A":'"target: zero overdue"'}
RAW='Plan: pt, EffW: effw, Tgt: t, Act: a, OEEw: o, Shifts: sh, Scrap: sc, CrewA: ca, CrewS: cs, DT: dt, RW: rw, Saf: sf, TSn: tsn, TSop: tsop, TSnr: tsnr, TSu: tsu, MNt: mnt, PCd: pcd, PCf: pcf, PCx: pcx, Esc: esc, AO: ao, OV: ov, DTe: dte, DTl: dtl, EscL: escl, Fz: fz, Fch: fch, FA: fa'
def derive():
    parts=[RAW]
    for k in DK:
        tx,sb,st,br=DEF[k]
        parts.append(f'txt{k}: {tx}, sub{k}: {sb}, st{k}: {st}, bar{k}: {br}, val{k}: {VAL[k]}, tg{k}: {TG[k]}, tgt{k}: {TGT[k]}')
    return ",\n        ".join(parts)
SHM='(ddShift.Selected.Value = "All" || Text(Shift) = ddShift.Selected.Value)'
WIN='ShiftDate >= varD0 && ShiftDate < varD1'
LOADTS='ClearCollect(colTSAll, Filter(TS_Occurrences, ShiftDate >= varD0 && ShiftDate < varD1)); ClearCollect(colTS, Filter(colTSAll, LinkStatus.Value <> "Waived")); ClearCollect(colWv, Filter(colTSAll, LinkStatus.Value = "Waived"))'

# =========================== HEADER ===========================
out.append(rect("hdrBar",DARK,0,0,1920,90))
out.append(label("lblBrand",'"voyant"',24,6,170,52,size=34,color=WHITE,font="Georgia"))
out.append(label("lblBrandSub",'"NEW ALBANY"',27,56,170,24,size=10,bold=True,color=TEAL))
out.append(label("lblTitle",'"TIER 2"',190,20,170,50,size=26,bold=True,color=AQUA,font="Georgia",extra={"Wrap":"=false"}))
out.append(cap("cVS","VALUE STREAM",380,6,300))
out.append(dd("ddVS",'Ungroup(Table({t: Table({Value: "All value streams"})}, {t: Distinct(colLines, ValueStream)}), t)',380,28,300,52,onchange="Select(btnCalc)",size=15,bold=True))
out.append(cap("cDate","DAY REVIEWED",690,6,190))
out.append(dd("ddDate",'ForAll(Sequence(30, 0), With({d: DateAdd(Today(), -Value, TimeUnit.Days)}, {Value: Text(d, "ddd m/d"), D: d}))',690,28,190,52,
   default='Text(DateAdd(Today(), -1, TimeUnit.Days), "ddd m/d")',onchange="Select(btnRefresh)",size=15,bold=True))
out.append(cap("cShift","SHIFT",890,6,110)); out.append(dd("ddShift",'["All", "1", "2", "3"]',890,28,110,52,onchange="Select(btnCalc)",size=16,bold=True))
out.append(btn("btnIdle",'If(varShowIdle, "ALL LINES", "RUNNING LINES")','Set(varShowIdle, !varShowIdle); Select(btnCalc)',1010,28,150,52,size=11,fill=TEAL_D,color=WHITE,
   extra={"Tooltip":'="Running lines = lines with any HxH data in the 7 days shown. Tap to switch."'}))
def LD(coll,src,nm): return f'IfError(ClearCollect({coll}, {src}), Notify("Tier 2: could not load {nm}", NotificationType.Error));\n'
CFG=lambda v,k,dflt: f'Set({v}, Value(Coalesce(LookUp(colCfg, Title = "{k}").SettingValue, "{dflt}")));\n'
LOAD=('Set(varD, ddDate.Selected.D); Set(varD0, DateAdd(varD, -6, TimeUnit.Days)); Set(varD1, DateAdd(varD, 1, TimeUnit.Days));\n'
 'If(IsBlank(varLayer), Set(varLayer, "floor"));\n'
 + LD("colCfg","MDI_Config","MDI_Config")
 + CFG("varAG","T2_AttainGreen",90)+CFG("varAA","T2_AttainAmber",80)+CFG("varOG","T2_OEEGreen",65)+CFG("varOA","T2_OEEAmber",50)
 + CFG("varRA","T2_ReworkAmber",0.5)+CFG("varRR","T2_ReworkRed",2)+CFG("varPCG","T2_PCGreen",90)+CFG("varDA","T2_DTAmber",30)+CFG("varDR","T2_DTRed",60)+CFG("varTSReq","T2_TSRequiredMin",15)
 + LD("colLines","Sort(Filter(Lines, Active), DisplayOrder)","Lines")
 + LD("colPB","PLAYBOOK","PLAYBOOK")
 + LD("colMR",'Filter(Lookups, Category.Value = "Downtime")',"Lookups (downtime reasons)")
 + 'RemoveIf(colMR, IsBlank(EquipType));\n'
 + 'Set(varCanLink, Coalesce(LookUp(People, Email = User().Email).CanLinkDowntime, false));\n'
 + LD("colShift",f"Filter(HxH_Shift, {WIN})","HxH_Shift")
 + LD("colHrDay","Filter(HxH_Hourly, ShiftDate >= varD && ShiftDate < varD1)","HxH_Hourly (day)")
 + LD("colDTH",f"Filter(HxH_Hourly, {WIN} && (DT_Minutes > 0 || DT2_Minutes > 0))","HxH_Hourly (downtime)")
 + LD("colSafe",f"Filter(HxH_Hourly, {WIN} && SafetyEvent = true)","HxH_Hourly (safety)")
 + LD("colFA","Filter(SAF_Audits, AuditDate >= varD0 && AuditDate < varD1)","SAF_Audits (safety audits)")
 + LD("colFR","Filter(SAF_Results, AuditDate >= varD0 && AuditDate < varD1)","SAF_Results (safety audits)")
 + 'RemoveIf(colFR, !(Rating.Value = "AR" || Rating.Value = "U" || (Rating.Value = "Deficient" && SafetyRelevant)));\n'
 + LD("colQA",f"Filter(QA_Rework, {WIN} && Voided = false)","QA_Rework")
 + 'IfError(ClearCollect(colTSAll, Filter(TS_Occurrences, ShiftDate >= varD0 && ShiftDate < varD1)), Notify("Tier 2: could not load TS_Occurrences", NotificationType.Error));\n'
 + 'ClearCollect(colTS, Filter(colTSAll, LinkStatus.Value <> "Waived")); ClearCollect(colWv, Filter(colTSAll, LinkStatus.Value = "Waived"));\n'
 + LD("colIss","TS_Issues","TS_Issues") + LD("colFix","TS_Fixes","TS_Fixes")
 + LD("colPC",f"Filter(PC_Audits, {WIN})","PC_Audits")
 + LD("colRes","Filter(PC_Results, Created >= varD0 && Created < varD1)","PC_Results")
 + LD("colEl","SW_Elements","SW_Elements")
 + LD("colCards","Filter(PC_Cards, Active = true)","PC_Cards")
 + LD("colEsc","Filter(Escalation_Log, NotifiedAt >= DateAdd(varD0, -1, TimeUnit.Days) && NotifiedAt < DateAdd(varD1, 1, TimeUnit.Days))","Escalation_Log")
 + LD("colNews",'Filter(Newspaper, Status.Value = "Open" || Status.Value = "In progress" || ClosedDate >= varD0)',"Newspaper")
 + 'Set(varLoadedAt, Now());\nSelect(btnCalc)')
out.append(btn("btnRefresh",'"REFRESH"',LOAD,1170,28,130,52,size=14))
out.append(label("lblLoaded",'If(IsBlank(varLoadedAt), "Tap REFRESH", "Updated " & Text(varLoadedAt, "h:mm AM/PM"))',1310,28,200,52,size=11,color=G5))
out.append(label("lblScope",'ddVS.Selected.Value & Char(10) & Text(varD, "ddd m/d") & "  ·  " & If(ddShift.Selected.Value = "All", "all shifts", "shift " & ddShift.Selected.Value)',
   1520,10,388,70,size=13,bold=True,color=AQUA,align="Right"))

# =========================== CALC ===========================
DAYREC=('With({dD: DateAdd(varD0, k.Value, TimeUnit.Days), L: ln.Title},\n'
 '   With({dE: DateAdd(dD, 1, TimeUnit.Days), DKy: Text(dD, "yyyymmdd")},\n'
 f'    With({{shs: Filter(colShift, Line = L && ShiftDate >= dD && ShiftDate < dE && {SHM}),\n'
 f'           qas: Filter(colQA, Line = L && ShiftDate >= dD && ShiftDate < dE && {SHM}),\n'
 f'           tss: Filter(colTS, Line = L && ShiftDate >= dD && ShiftDate < dE && {SHM}),\n'
 f'           pcs: Filter(colPC, Line = L && ShiftDate >= dD && ShiftDate < dE && {SHM}),\n'
 '           nws: Filter(colNews, Line = L && RaisedDate < dE && Status.Value <> "Canceled" && (IsBlank(ClosedDate) || ClosedDate >= dE))},\n'
 '     With({t: Sum(shs, Coalesce(TargetUnits, 0)), a: Sum(shs, Coalesce(ActualUnits, 0)), o: Sum(shs, Coalesce(OEE, 0) * Coalesce(TargetUnits, 0)),\n'
 '           sh: CountRows(shs), sc: Sum(shs, Coalesce(FGScrapQty, 0)), ca: Sum(shs, Coalesce(ActualCrewSize, 0)), cs: Sum(shs, Coalesce(StdCrewSize, 0)),\n'
 '           dt: Sum(shs, Coalesce(ReportedDowntimeMin, 0)), rw: Sum(qas, Coalesce(ReworkQty, 0)),\n'
 '           pt: Sum(shs, With({pb: LookUp(colPB, Title = PlaybookKey)}, If(IsBlank(pb), Coalesce(TargetUnits, 0), Coalesce(Value(Text(pb.UnitsPerHour)), 0) * Max(Coalesce(PlannedShiftHrs, pb.AvailableHrsShift, 0) - (Coalesce(LunchMin, 0) + Coalesce(BreakMin, 0)) / 60, 0)))),\n'
 '           effw: Sum(shs, Coalesce(LookUp(colPB, Title = PlaybookKey).EfficiencyTarget, 0) * Coalesce(TargetUnits, 0)),\n'
 f'           sf: CountRows(Filter(colSafe, Line = L && ShiftDate >= dD && ShiftDate < dE && {SHM})),\n'
 '           fz: CountRows(Filter(colFR, Line = L && AuditDate >= dD && AuditDate < dE)), fch: CountRows(Filter(colFR, Line = L && AuditDate >= dD && AuditDate < dE && (Severity.Value = "Critical" || Severity.Value = "High"))),\n'
 '           fa: CountRows(Filter(colFA, Line = L && AuditDate >= dD && AuditDate < dE)),\n'
 '           tsn: CountRows(tss), tsop: CountIf(tss, OperatorCouldFix), tsnr: CountIf(tss, Outcome.Value = "Not resolved - escalated"), tsu: CountIf(tss, IsBlank(EventKey)),\n'
 '           pcd: CountRows(pcs), pcf: CountIf(pcs, Result.Value = "Fail"),\n'
 '           esc: CountRows(Filter(colEsc, StartsWith(ShiftKey, L & "-" & DKy) && (ddShift.Selected.Value = "All" || EndsWith(ShiftKey, "-S" & ddShift.Selected.Value)))),\n'
 '           ao: CountRows(nws), ov: CountIf(nws, DueDate < dD),\n'
 '           escl: Coalesce(Max(Filter(colEsc, StartsWith(ShiftKey, L & "-" & DKy) && (ddShift.Selected.Value = "All" || EndsWith(ShiftKey, "-S" & ddShift.Selected.Value))), Level), 0)},\n'
 '      With({pcx: nEv * sh + nDy * If(sh > 0, 1, 0),\n'
 f'            evs: GroupBy(Filter(Ungroup(Table({{t: ForAll(Filter(colDTH, Line = L && ShiftDate >= dD && ShiftDate < dE && {SHM}), {{K: ShiftKey & "|" & DT_Reason, R: DT_Reason, M: Coalesce(DT_Minutes, 0)}})}}, {{t: ForAll(Filter(colDTH, Line = L && ShiftDate >= dD && ShiftDate < dE && {SHM}), {{K: ShiftKey & "|" & DT2_Reason, R: DT2_Reason, M: Coalesce(DT2_Minutes, 0)}})}}), t), M > 0 && !IsBlank(R)), K, R, G)}},\n'
 '      With({dte: CountRows(evs), dtl: Coalesce(Max(ForAll(evs, {v: Sum(G, M)}), v), 0), mnt: CountRows(Filter(evs, R in colMR.Label && Sum(G, M) >= varTSReq && CountRows(Filter(colTS, EventKey = K)) = 0 && CountRows(Filter(colWv, EventKey = K)) = 0))},\n'
 '       {Line: L, VS: ln.ValueStream, Ord: ln.DisplayOrder, Day: dD,\n        ' + derive() + '}))))))')
TOTREC=('With({dD: DateAdd(varD0, k.Value, TimeUnit.Days)},\n'
 ' With({rs: Filter(colDaily, Day = dD)},\n'
 '  With({pt: Sum(rs, Plan), effw: Sum(rs, EffW), t: Sum(rs, Tgt), a: Sum(rs, Act), o: Sum(rs, OEEw), sh: Sum(rs, Shifts), sc: Sum(rs, Scrap), ca: Sum(rs, CrewA), cs: Sum(rs, CrewS), dt: Sum(rs, DT),\n'
 '        rw: Sum(rs, RW), sf: Sum(rs, Saf), tsn: Sum(rs, TSn), tsop: Sum(rs, TSop), tsnr: Sum(rs, TSnr), tsu: Sum(rs, TSu), mnt: Sum(rs, MNt), pcd: Sum(rs, PCd), pcf: Sum(rs, PCf), pcx: Sum(rs, PCx),\n'
 '        esc: Sum(rs, Esc), ao: Sum(rs, AO), ov: Sum(rs, OV), dte: Sum(rs, DTe), dtl: Coalesce(Max(rs, DTl), 0), escl: Coalesce(Max(rs, EscL), 0),\n'
 '        fz: If(ddVS.Selected.Value = "All value streams", CountRows(Filter(colFR, AuditDate >= dD && AuditDate < DateAdd(dD, 1, TimeUnit.Days))), Sum(rs, Fz)),\n'
 '        fch: If(ddVS.Selected.Value = "All value streams", CountRows(Filter(colFR, AuditDate >= dD && AuditDate < DateAdd(dD, 1, TimeUnit.Days) && (Severity.Value = "Critical" || Severity.Value = "High"))), Sum(rs, Fch)),\n'
 '        fa: If(ddVS.Selected.Value = "All value streams", CountRows(Filter(colFA, AuditDate >= dD && AuditDate < DateAdd(dD, 1, TimeUnit.Days))), Sum(rs, FA))},\n'
 '   {Day: dD,\n        ' + derive() + '})))')

def wrap_sums(x):
    out=""; i=0
    while True:
        j=x.find("Sum(",i)
        if j<0: out+=x[i:]; break
        if j>0 and (x[j-1].isalnum() or x[j-1]=="_"): out+=x[i:j+4]; i=j+4; continue
        d=0; k=j+3
        while True:
            c=x[k]
            if c=="(": d+=1
            elif c==")":
                d-=1
                if d==0: break
            k+=1
        out+=x[i:j]+"Coalesce(Sum("+wrap_sums(x[j+4:k])+"), 0)"; i=k+1
    return out
DAYREC=wrap_sums(DAYREC); TOTREC=wrap_sums(TOTREC)
TRS=", ".join(f'tr{k}: Concat(Filter(colDaily As q, q.Line = r2.Line), st{k})' for k in DK)
TRT=", ".join(f'tr{k}: Concat(colTot, st{k})' for k in DK)
CALC=('ClearCollect(colScope, Filter(colLines, ddVS.Selected.Value = "All value streams" || ValueStream = ddVS.Selected.Value));\n'
 'ClearCollect(colDaily, Ungroup(ForAll(colScope As ln,\n'
 '  With({nEv: CountRows(Filter(colCards, Frequency.Value = "Every shift" && (Line = "All" || ln.Title in Split(Line, ",")))),\n'
 '        nDy: CountRows(Filter(colCards, Frequency.Value = "Daily" && (Line = "All" || ln.Title in Split(Line, ","))))},\n'
 '   {rows: ForAll(Sequence(7, 0) As k,\n   ' + DAYREC + ')})), rows));\n'
 'ClearCollect(colTot, ForAll(Sequence(7, 0) As k,\n  ' + TOTREC + '));\n'
 'ClearCollect(colFloor, SortByColumns(ForAll(Filter(colDaily As r, r.Day = varD && (varShowIdle || CountRows(Filter(colDaily As q, q.Line = r.Line && q.Shifts > 0)) > 0)) As r2,\n'
 '   Patch(r2, {' + TRS + '})), "VS", SortOrder.Ascending, "Ord", SortOrder.Ascending));\n'
 'Set(varTot, Patch(LookUp(colTot, Day = varD), {' + TRT + '}));\n'
 'Set(varDens, If(CountRows(colFloor) <= 6, 1, CountRows(colFloor) <= 12, 2, 3))')
out.append(tap("btnCalc",CALC,0,1079,1,1))

# =========================== SUB-BAR / BREADCRUMB ===========================
FLOOR='varLayer = "floor"'; LINE='varLayer = "line"'; DOM='varLayer = "domain"'; CELL='varLayer = "cell"'
out.append(rect("subBar",LIGHT,0,90,1920,44))
out.append(btn("bcFloor",'"FLOOR"','Set(varLayer, "floor")',12,96,110,32,size=11,fill=f'If({FLOOR}, {DARK}, {G1})',color=f'If({FLOOR}, {WHITE}, {DARK})'))
out.append(V(btn("bcLine",'"›  LINE " & varLine',HRMAX+'; Set(varLayer, "line")',128,96,150,32,size=11,fill=f'If({LINE}, {DARK}, {G1})',color=f'If({LINE}, {WHITE}, {DARK})'),
             'varLayer in ["line", "cell"]'))
out.append(V(btn("bcDomA",'"›  " & '+DNAME,'Set(varLayer, "domain")',128,96,190,32,size=11,fill=DARK,color=WHITE),DOM))
out.append(V(btn("bcDomC",'"›  " & '+DNAME,'Set(varLayer, "domain")',284,96,190,32,size=11,fill=DARK,color=WHITE,
             extra={"Tooltip":'="Compare all lines in this domain"'}),CELL))
out.append(btn("btnHome",'"⌂  HOME"','Set(varLayer, "floor"); Set(varLine, Blank()); Set(varDom, Blank()); Set(varAdd, false)',1796,96,112,32,size=11,
   fill=f'If(varLayer = "floor", {G1}, {TEAL})',color=DARK,extra={"Tooltip":'="Back to the full-floor view"',"DisplayMode":F('If(varLayer = "floor", DisplayMode.Disabled, DisplayMode.Edit)'),"DisabledFill":F(G1),"DisabledColor":F(G5)}))
out.append(V(btn("btnByForm",'"BY FORM  ▸"','Navigate(scrForm, ScreenTransition.None)',1556,96,112,32,size=11,fill=TEAL_D,color=WHITE,
   extra={"Tooltip":'="Performance grouped by form (Body Wash, Body Lotion, ...) using the product each shift picked"'}),'varLayer = "floor"'))
out.append(btn("btnTrends",'"TRENDS  ▸"','Navigate(scrPeriods, ScreenTransition.None)',1676,96,112,32,size=11,fill=TEAL_D,color=WHITE,
   extra={"Tooltip":'="Weeks and months: compare lines over a date range (up to 6 months back)"'}))
out.append(label("lblHint",'Switch(varLayer, "floor", "Tap a LINE for its detail  ·  tap a DOMAIN heading to compare lines  ·  tap a TILE for that line in that domain",'
   ' "line", "Line " & varLine & ": every domain over 7 days. Tap a card to open it.", "domain", ' + DNAME + ' & " across lines. Tap a line to open its detail.",'
   ' "cell", "Line " & varLine & "  ·  " & ' + DNAME + ' & "  ·  7 days ending " & Text(varD, "m/d"), "")',500,96,'If(varLayer = "floor", 1046, 1160)',32,size=11,color=G9,align="Right"))

# =========================== FLOOR ===========================
GX=12; LW=130; CW=146; CS=150
def cx(i): return LW+4+i*CS
out.append(V(rect("fHdr",TEAL_D,GX,138,1488,32),FLOOR))
out.append(V(label("fhLine",'"LINE"',GX,138,LW,32,size=11,bold=True,color=WHITE,align="Center"),FLOOR))
for i,(k,n) in enumerate(DOMS):
    out.append(V(label(f"fh{k}",f'"{n}  ▸"',GX+cx(i),138,CW,32,size=10,bold=True,color=WHITE,align="Center",extra={"Tooltip":F(f'"{TIPS[k]} Tap to compare lines."')}),FLOOR))
    out.append(tap(f"fhT{k}",f'Set(varDom, "{k}"); Set(varLayer, "domain")',GX+cx(i),138,CW,32,vis=FLOOR,tip=f'"{TIPS[k]} Tap to compare lines."'))
def tilekids(pfx,R,tr,y0,indent,tapfn,xo=0):
    ks=[]
    for i,k in enumerate(DK):
        x=cx(i)+xo
        ks.append(rect(f"{pfx}b{k}",COL(f"{R}.st{k}"),x,y0,CW,62,indent=indent,extra={"Tooltip":F(f'"{TIPS[k]}"')}))
        ks.append(label(f"{pfx}v{k}",f"{R}.txt{k}",x,y0,CW,40,size=19,bold=True,color=WHITE,align="Center",valign="Bottom",indent=indent))
        ks.append(label(f"{pfx}s{k}",f"{R}.sub{k}",x,y0+40,CW,22,size=8,bold=True,color=WHITE,align="Center",indent=indent))
        for d in range(1,8):
            ks.append(rect(f"{pfx}d{k}{d}",DOT(f"{tr}{k}",d),x+3+(d-1)*20,y0+67,18,12,indent=indent,
                extra={"BorderColor":F(f'If({d} = 7, {DARK}, {CLEAR})'),"BorderThickness":F(f'If({d} = 7, 2, 0)')}))
        if tapfn: ks.append(tapfn(k,x,y0))
    return ks
# floor totals row (not a gallery)
out.append(V(rect("ftLineBg",DARK,GX,174,LW,82),FLOOR))
out.append(V(label("ftLine",'"FLOOR"',GX,178,LW,40,size=20,bold=True,color=WHITE,align="Center",font="Georgia"),FLOOR))
out.append(V(label("ftSub",'Text(CountRows(colFloor)) & " lines"',GX,218,LW,22,size=9,color=AQUA,align="Center"),FLOOR))
for c in tilekids("ft","varTot","varTot.tr",174,0,None,xo=GX):
    out.append(V(c,FLOOR))
# grid gallery
DS=lambda a,b,c: f'Switch(varDens, 1, {a}, 2, {b}, {c})'
def gtap(k,x,y0):
    return tap(f"gt{k}",f'Set(varLine, ThisItem.Line); Set(varDom, "{k}"); '+HRMAX+'; Set(varLayer, "cell")',x,0,CW,DS(82,40,31),indent=I,tip=f'"{TIPS[k]} Tap for line " & ThisItem.Line & " detail."')
LINETAP='Set(varLine, ThisItem.Line); '+HRMAX+'; Set(varLayer, "line")'
gk=[rect("gLineBg",DARK,0,DS(4,3,2),LW,DS(82,40,31),indent=I),
    label("gLine",'ThisItem.Line',0,DS(6,3,2),LW,DS(46,40,31),size=DS(24,17,14),bold=True,color=WHITE,align="Center",font="Georgia",indent=I,
          extra={"VerticalAlign":F('If(varDens = 1, VerticalAlign.Bottom, VerticalAlign.Middle)'),"Tooltip":F('ThisItem.Line & "  ·  " & ThisItem.VS')}),
    label("gVS",'ThisItem.VS',0,54,LW,26,size=8,color=AQUA,align="Center",indent=I,extra={"Visible":"=varDens = 1"}),
    tap("gLineTap",LINETAP,0,DS(4,3,2),LW,DS(82,40,31),indent=I,tip='"Open line " & ThisItem.Line')]
for i,k in enumerate(DK):
    x=cx(i)
    gk.append(rect(f"gb{k}",COL(f"ThisItem.st{k}"),x,DS(4,3,2),CW,DS(62,28,22),indent=I))
    gk.append(label(f"gv{k}",f"ThisItem.txt{k}",x,DS(4,3,2),CW,DS(40,28,22),size=DS(19,14,12),bold=True,color=WHITE,align="Center",indent=I,
          extra={"VerticalAlign":F('If(varDens = 1, VerticalAlign.Bottom, VerticalAlign.Middle)'),"Tooltip":F(f'"{TIPS[k]}" & Char(10) & ThisItem.sub{k}')}))
    gk.append(label(f"gs{k}",f"ThisItem.sub{k}",x,44,CW,22,size=8,bold=True,color=WHITE,align="Center",indent=I,extra={"Visible":"=varDens = 1"}))
    for d in range(1,8):
        gk.append(rect(f"gd{k}{d}",DOT(f"ThisItem.tr{k}",d),x+3+(d-1)*20,DS(71,33,26),18,DS(12,8,7),indent=I,
            extra={"BorderColor":F(f'If({d} = 7, {DARK}, {CLEAR})'),"BorderThickness":F(f'If({d} = 7, 2, 0)')}))
    gk.append(gtap(k,x,0))
out.append(gal("galFloor","colFloor",GX,260,1488,566,DS(90,46,37),gk,vis=FLOOR,extra={"TemplateFill":F(WHITE)}))

out.append(V(label("lblFloorEmpty",'If(CountRows(colFloor) = 0, If(IsBlank(varLoadedAt), "Loading…", "No lines with data in this selection. Try ALL LINES or another day."), "")',GX,400,1488,60,size=16,color=G9,align="Center"),FLOOR))

# ---- reasons builder ----
def reasons(k,SC,WS,WC):
    """SC=line scope cond, WS=window cond on ShiftDate, WC=window cond on Created. returns table {R,N,Sub}"""
    srt=lambda e: f'FirstN(SortByColumns({e}, "N", SortOrder.Descending), 10)'
    if k=="S":
        WA=WS.replace("ShiftDate","AuditDate")
        return srt(f'Ungroup(Table({{t: ForAll(Filter(colSafe, {SC} && {WS} && {SHM}), {{R: Line & " · " & Text(ShiftDate, "m/d") & " S" & Shift & " H" & HourNo & ": " & Coalesce(SafetyNotes, "safety event"), N: 1, Sub: ""}})}}, '
                   f'{{t: ForAll(Filter(colFR, ({SC}{" || IsBlank(Line)" if SC == "Line in colFloor.Line" else ""}) && {WA}), {{R: "AUDIT " & Coalesce(Severity.Value, "?") & " · " & ZoneID & ": " & Item, N: 1, Sub: Coalesce(Finding, "")}})}}), t)')
    if k=="Q": return srt(f'ForAll(GroupBy(Filter(colQA, {SC} && {WS} && {SHM}), Reason, G), {{R: Reason, N: Sum(G, ReworkQty), Sub: Text(CountRows(G)) & " entries"}})')
    if k=="D": return srt(f'ForAll(GroupBy(Filter(colShift, {SC} && {WS} && {SHM} && !IsBlank(SpeedLossReasonCode)), SpeedLossReasonCode, G), {{R: SpeedLossReasonCode, N: Sum(G, Max(Coalesce(TargetUnits, 0) - Coalesce(ActualUnits, 0), 0)), Sub: Text(CountRows(G)) & " shifts with this speed loss"}})')
    if k=="DT":
        base=f'Filter(colDTH, {SC} && {WS} && {SHM})'
        return srt(f'ForAll(GroupBy(Filter(Ungroup(Table({{t: ForAll({base}, {{R: DT_Reason, M: Coalesce(DT_Minutes, 0)}})}}, {{t: ForAll({base}, {{R: DT2_Reason, M: Coalesce(DT2_Minutes, 0)}})}}), t), !IsBlank(R) && M > 0), R, G), {{R: R, N: Sum(G, M), Sub: Text(CountRows(G)) & " events"}})')
    if k=="C": return srt(f'ForAll(GroupBy(Filter(colShift, {SC} && {WS} && {SHM} && !IsBlank(ScrapReasonCode)), ScrapReasonCode, G), {{R: ScrapReasonCode, N: Sum(G, FGScrapQty), Sub: "units scrapped"}})')
    if k=="P": return srt(f'ForAll(GroupBy(Filter(ForAll(Filter(colShift, {SC} && {WS} && {SHM}), {{R: If(ActualCrewSize < StdCrewSize, "Short staffed", ActualCrewSize > StdCrewSize, "Over std: " & Coalesce(StaffingReasonCode, "no reason"), "")}}), !IsBlank(R)), R, G), {{R: R, N: CountRows(G), Sub: "shifts"}})')
    if k=="M": return srt(f'ForAll(GroupBy(Filter(colTS, {SC} && {WS} && {SHM}), IssueID, G), {{R: Coalesce(LookUp(colIss, ID = IssueID).Title, "Concern " & IssueID), N: CountRows(G), Sub: Text(Sum(G, Coalesce(RepairMin, 0))) & " min repair · " & Text(CountIf(G, OperatorCouldFix)) & " op-fixable · " & Text(CountIf(G, IsBlank(EventKey))) & " unlinked"}})')
    if k=="PC": return srt(f'ForAll(GroupBy(Filter(colRes, Answer.Value = "No" && {SC} && {WC}), ElementID, G), {{R: Coalesce(LookUp(colEl, ID = ElementID).Title, "Item " & ElementID), N: CountRows(G), Sub: "times missed"}})')
    if k=="A": return srt(f'ForAll(GroupBy(ForAll(Filter(colNews, {SC} && (Status.Value = "Open" || Status.Value = "In progress")), {{R: Source.Value, OD: DueDate < Today()}}), R, G), {{R: R, N: CountRows(G), Sub: Text(CountIf(G, OD)) & " overdue"}})')
RUNIT={"S":"events","Q":"units","D":"short","DT":"min","C":"units","P":"shifts","M":"times","PC":"misses","A":"actions"}
SCF='Line in colFloor.Line'; WSD='ShiftDate >= varD && ShiftDate < varD1'; WCD='Created >= varD && Created < varD1'
def EVT(SC,WS,shm=True):
    base=f'Filter(colDTH, {SC} && {WS}' + (f' && {SHM})' if shm else ')')
    rec=lambda r,m: f'{{SK: ShiftKey, Ln: Line, SD: ShiftDate, Sh: Shift, H: HourNo, HS: HourStart, R: {r}, M: Coalesce({m}, 0)}}'
    return (f'ForAll(GroupBy(Filter(Ungroup(Table({{t: ForAll({base}, {rec("DT_Reason","DT_Minutes")})}}, {{t: ForAll({base}, {rec("DT2_Reason","DT2_Minutes")})}}), t), !IsBlank(R) && M > 0), SK, R, G), '
            '{SK: SK, R: R, Key: SK & "|" & R, Ln: First(G).Ln, SD: First(G).SD, Sh: First(G).Sh, H1: Min(G, H), H2: Max(G, H), T0: Min(G, HS), Mn: Sum(G, M), '
            'EL: Coalesce(Max(Filter(colEsc, ShiftKey = SK && Reason = R), Level), 0), '
            'TSn: CountRows(Filter(colTS, EventKey = SK & "|" & R)), Wv: CountRows(Filter(colWv, EventKey = SK & "|" & R)), Mach: R in colMR.Label, Need: R in colMR.Label && Sum(G, M) >= varTSReq})')
REC_EV=EVT("Line = varLine","true",shm=False)
EVR='LookUp('+REC_EV+', Key = varRecEv)'
NEEDEV='Filter('+REC_EV+', Need && TSn = 0 && Wv = 0)'
UNL='Filter(colTS, Line = varLine && IsBlank(EventKey))'
# score of an event row (implicit fields R, SK, T0) against TS record o
SC_O='If(LookUp(colMR, Label = R).EquipType = o.EquipType, 50, 0) + If(SK = o.ShiftKey, 30, 0) + Max(0, 20 - Abs(DateDiff(T0, o.OccurredAt, TimeUnit.Minutes)) / 15)'
# score of a TS row (implicit fields EquipType, ShiftKey, OccurredAt) against event e
SC_E='If(LookUp(colMR, Label = e.R).EquipType = EquipType, 50, 0) + If(e.SK = ShiftKey, 30, 0) + Max(0, 20 - Abs(DateDiff(e.T0, OccurredAt, TimeUnit.Minutes)) / 15)'
STRENGTH=lambda sc: f'If({sc} >= 80, "STRONG MATCH", {sc} >= 50, "possible match", "weak match")'
def evlist(name,items,x,y,w,h,vis,rowh=34,size=10):
    ks=[rect(name+"S",f'If(ThisItem.EL > 0, {RED}, ThisItem.Mn >= varDA, {AMBER}, {G5})',0,4,6,rowh-8,indent=I),
        label(name+"L",'ThisItem.Ln',10,0,52,rowh,size=size+2,bold=True,font="Georgia",indent=I),
        label(name+"H",'"S" & ThisItem.Sh & " H" & ThisItem.H1 & If(ThisItem.H2 > ThisItem.H1, "–" & ThisItem.H2, "")',62,0,74,rowh,size=size-1,color=G9,indent=I),
        label(name+"R",'Substitute(ThisItem.R, "Machine - ", "")',136,0,w-136-120,rowh,size=size,bold=True,indent=I,extra={"Tooltip":F('ThisItem.R & "  ·  " & Text(ThisItem.SD, "ddd m/d") & If(ThisItem.TSn > 0, "  ·  TS logged", "")')}),
        label(name+"M",'Text(ThisItem.Mn) & " min"',w-120,0,64,rowh,size=size,bold=True,align="Right",indent=I),
        label(name+"E",'If(ThisItem.EL > 0, "L" & ThisItem.EL, "")',w-48,6,36,rowh-12,size=size-1,bold=True,color=WHITE,align="Center",indent=I,
              extra={"Fill":F(f'If(ThisItem.EL > 0, {RED}, {CLEAR})'),"Tooltip":'="Escalation level reached"'})]
    ks.append(tap(name+"T",'Set(varLine, ThisItem.Ln); Set(varDom, "DT"); '+HRMAX+'; Set(varLayer, "cell")',0,0,w,rowh,indent=I,tip='"Open line " & ThisItem.Ln & " downtime detail"'))
    return gal(name,items,x,y,w,h,rowh,ks,vis=vis)
def pareto(name,items,x,y,w,h,rw=220,bw=None,unit='""',vis=None,rowh=32,size=11):
    bw=bw or (w-rw-140)
    items=f'With({{tb: {items}}}, AddColumns(tb, P, N / Max(Max(tb, N), 1)))'
    ks=[label(name+"R",'ThisItem.R',0,2,rw,rowh-4,size=size,bold=True,indent=I,extra={"Tooltip":F('ThisItem.R & If(IsBlank(ThisItem.Sub), "", "  ·  " & ThisItem.Sub)')}),
        rect(name+"B",TEAL_D,rw+6,7,f"Max(ThisItem.P * {bw}, 2)",rowh-14,indent=I),
        label(name+"N",f'Text(ThisItem.N, "#,##0") & " " & {unit}',rw+12,2,118,rowh-4,size=size-1,bold=True,color=DARK,indent=I,
              extra={"X":F(f"{rw} + 12 + ThisItem.P * {bw}")})]
    return gal(name,items,x,y,w,h,rowh,ks,vis=vis)
out.append(V(rect("fBot",LIGHT,GX,832,1488,240),FLOOR))
FEV=f'FirstN(SortByColumns({EVT(SCF,WSD)}, "Mn", SortOrder.Descending), 6)'
out.append(V(label("fBotCEV",'"DOWNTIME EVENTS (biggest first)  ·  " & Text(varD, "ddd m/d")',GX+12,836,480,26,size=11,bold=True,color=TEAL_D),FLOOR))
out.append(evlist("galFEV",FEV,GX+12,864,476,204,FLOOR))
out.append(V(label("fBotEEV",f'If(CountRows({FEV}) = 0, "No downtime logged.", "")',GX+12,900,476,30,size=11,color=G9),FLOOR))
for i,(k,cp,u) in enumerate([("Q","REWORK REASONS (units)",'"units"'),("M","TROUBLESHOOTING CONCERNS (times)",'"x"')]):
    i=i+1
    x=GX+12+i*492
    out.append(V(label(f"fBotC{k}",f'"{cp}  ·  " & Text(varD, "ddd m/d")',x,836,480,26,size=11,bold=True,color=TEAL_D),FLOOR))
    it=reasons(k,SCF,WSD,WCD)
    out.append(pareto(f"galF{k}",it,x,864,476,200,rw=170,unit=u,vis=FLOOR,rowh=32,size=10))
    out.append(V(label(f"fBotE{k}",f'If(CountRows({it}) = 0, "Nothing logged.", "")',x,900,476,30,size=11,color=G9),FLOOR))

# =========================== LINE LAYER ===========================
LR='LookUp(colDaily, Line = varLine && Day = varD)'
for i,(k,n) in enumerate(DOMS):
    col=i%5; row=i//5; x=GX+col*299; y=142+row*306; w=291; h=298
    out.append(V(rect(f"lc{k}Bg",WHITE,x,y,w,h,extra={"BorderColor":F(G1),"BorderThickness":"=2"}),LINE))
    out.append(V(rect(f"lc{k}St",COL(f"{LR}.st{k}"),x,y,w,8),LINE))
    out.append(V(label(f"lc{k}T",f'"{n}"',x+14,y+12,w-28,26,size=12,bold=True,color=TEAL_D),LINE))
    out.append(V(label(f"lc{k}V",f'{LR}.txt{k}',x+14,y+38,w-28,56,size=32,bold=True,font="Georgia",extra={"Color":F(COL(f"{LR}.st{k}"))}),LINE))
    out.append(V(label(f"lc{k}S",f'{LR}.sub{k}',x+14,y+90,w-28,20,size=10,color=G9),LINE))
    out.append(V(label(f"lc{k}G",f'"●— " & {LR}.tgt{k}',x+14,y+108,w-28,18,size=8,color=DARK),LINE))
    out.append(svgimg(f"imgLc{k}", svgchart(f'ForAll(Filter(colDaily, Line = varLine), {{V: val{k}, T: tg{k}, S: st{k}, Tx: txt{k}, Day: Day}})', w-28, 160, values=False), x+14, y+124, w-28, 160, LINE))
    out.append(tap(f"lc{k}Tap",f'Set(varDom, "{k}"); Set(varLayer, "cell")',x,y,w,h,vis=LINE,tip=f'"{TIPS[k]} Tap for detail."'))
# 10th slot: the line's downtime events for the day
EX=GX+4*299; EY=142+306
LEV=f'SortByColumns({EVT("Line = varLine",WSD)}, "Mn", SortOrder.Descending)'
out.append(V(rect("lcEvBg",WHITE,EX,EY,291,298,extra={"BorderColor":F(G1),"BorderThickness":"=2"}),LINE))
out.append(V(label("lcEvT",'"DOWNTIME EVENTS  ·  " & Text(varD, "m/d")',EX+14,EY+12,263,26,size=12,bold=True,color=TEAL_D),LINE))
out.append(evlist("galLEv",LEV,EX+6,EY+42,279,250,LINE,rowh=34,size=9))
out.append(V(label("lcEvE",f'If(CountRows({LEV}) = 0, "No downtime logged.", "")',EX+14,EY+60,263,30,size=11,color=G9),LINE))
# hour strip
out.append(V(label("lhC",'"HOUR BY HOUR  ·  LINE " & varLine & "  ·  " & Text(varD, "ddd m/d") & "   (gray = target, color = actual, red = downtime min)"',GX,752,1488,26,size=11,bold=True,color=TEAL_D),LINE))
HR='SortByColumns(Filter(colHrDay, Line = varLine && ' + SHM + '), "Shift", SortOrder.Ascending, "HourNo", SortOrder.Ascending)'
ACT_COL=f'If(Coalesce(ThisItem.HourlyTarget, 0) = 0, {GREYT}, ThisItem.HourlyActual / ThisItem.HourlyTarget * 100 >= varAG, {GREEN}, ThisItem.HourlyActual / ThisItem.HourlyTarget * 100 >= varAA, {AMBER}, {RED})'
hk=[label("hL",'"S" & ThisItem.Shift & "·" & ThisItem.HourNo',0,0,60,18,size=8,bold=True,color=G9,align="Center",indent=I),
    rect("hT",G1,8,f"200 - Coalesce(ThisItem.HourlyTarget, 0) / Max(varHrMax, 1) * 180",20,f"Coalesce(ThisItem.HourlyTarget, 0) / Max(varHrMax, 1) * 180",indent=I),
    rect("hA",ACT_COL,30,f"200 - Coalesce(ThisItem.HourlyActual, 0) / Max(varHrMax, 1) * 180",20,f"Coalesce(ThisItem.HourlyActual, 0) / Max(varHrMax, 1) * 180",indent=I),
    label("hN",'Text(Round(Coalesce(ThisItem.HourlyActual, 0) / 1000, 1)) & "k"',0,204,60,18,size=8,bold=True,align="Center",indent=I),
    label("hD",'If(Coalesce(ThisItem.DT_Minutes, 0) + Coalesce(ThisItem.DT2_Minutes, 0) > 0, Text(Coalesce(ThisItem.DT_Minutes, 0) + Coalesce(ThisItem.DT2_Minutes, 0)) & "m", "")',0,224,60,18,size=9,bold=True,color=RED,align="Center",indent=I),
    label("hR",'Left(Substitute(Substitute(Coalesce(ThisItem.DT_Reason, ""), "Machine - ", ""), "Materials - ", ""), 9)',0,244,60,30,size=7,color=G9,align="Center",indent=I,
          extra={"Tooltip":F('Coalesce(ThisItem.DT_Reason, "") & If(IsBlank(ThisItem.DT2_Reason), "", " + " & ThisItem.DT2_Reason) & If(ThisItem.SafetyEvent, "  ·  SAFETY: " & ThisItem.SafetyNotes, "")')}),
    rect("hSaf",RED,0,0,60,4,indent=I,extra={"Visible":F("ThisItem.SafetyEvent")})]
out.append(gal("galHr",HR,GX,782,1488,286,286,hk,wrap=24,vis=LINE,extra={"ShowScrollbar":"=false"}))
out.append(V(label("lhE",f'If(CountRows({HR}) = 0, "No hour-by-hour entries for line " & varLine & " on this day.", "")',GX,880,1488,40,size=14,color=G9,align="Center"),LINE))

# =========================== DOMAIN LAYER ===========================
def SW(field,R="ThisItem"): return 'Switch(varDom, '+", ".join(f'"{k}", {R}.{field}{k}' for k in DK)+')'
out.append(V(label("dT",DNAME+' & "  ·  BY LINE  ·  " & Text(varD, "ddd m/d")',GX,140,1000,34,size=16,bold=True,color=TEAL_D,font="Georgia"),DOM))
out.append(V(label("dTip",'Switch(varDom, '+", ".join(f'"{k}", "{TIPS[k]}"' for k in DK)+')',GX+700,140,788,34,size=10,color=G9,align="Right"),DOM))
RH='If(CountRows(colFloor) > 11, 36, 48)'
dk=[label("dL",'ThisItem.Line',0,2,90,RH,size=f'If(CountRows(colFloor) > 11, 14, 18)',bold=True,font="Georgia",indent=I),
    label("dV",'ThisItem.VS',90,2,150,RH,size=9,color=G9,indent=I),
    rect("dTile",COL(SW("st")),244,4,130,f'{RH} - 6',indent=I),
    label("dTx",SW("txt"),244,4,130,f'{RH} - 6',size=f'If(CountRows(colFloor) > 11, 13, 16)',bold=True,color=WHITE,align="Center",indent=I),
    rect("dBar",COL(SW("st")),384,f'{RH} / 2 - 8',"Max(ThisItem.V / ThisItem.Sc * 520, 3)",18,indent=I),
    rect("dTgt",DARK,"383 + Max(ThisItem.T, 0) / ThisItem.Sc * 520",4,3,f'{RH} - 6',indent=I,extra={"Visible":F("ThisItem.T >= 0"),"Tooltip":F(SW("tgt"))}),
    label("dSub",SW("sub"),914,2,320,RH,size=11,color=G9,indent=I)]
for d in range(1,8):
    dk.append(rect(f"dD{d}",DOT(SW("tr"),d),1244+(d-1)*30,f'{RH} / 2 - 8',26,16,indent=I,extra={"BorderColor":F(f'If({d} = 7, {DARK}, {CLEAR})'),"BorderThickness":F(f'If({d} = 7, 2, 0)')}))
dk.append(tap("dTap",'Set(varLine, ThisItem.Line); '+HRMAX+'; Set(varLayer, "cell")',0,0,1488,RH,indent=I,tip='"Open line " & ThisItem.Line & " detail"'))
out.append(gal("galDom",'With({tb: AddColumns(colFloor, V, '+SWB("val")+', T, '+SWB("tg")+')}, AddColumns(tb, Sc, Max(Max(tb, V), Max(tb, T), 0.0001) * 1.1))',GX,178,1488,560,f'{RH} + 2',dk,vis=DOM,extra={"TemplateFill":F('If(Mod(ThisItem.Ord, 2) = 0, RGBA(250, 250, 250, 1), RGBA(255, 255, 255, 1))')}))
out.append(V(label("dHdT",'"bar = value   ▌ = target"',384,140,520,34,size=9,color=G9),DOM))
out.append(V(label("dHd7",'"last 7 days ▸"',1244,140,240,34,size=9,color=G9,align="Right"),DOM))
DREAS='Switch(varDom, '+", ".join(f'"{k}", {reasons(k,SCF,WSD,WCD)}' for k in DK)+')'
DUNIT='Switch(varDom, '+", ".join(f'"{k}", "{RUNIT[k]}"' for k in DK)+')'
out.append(V(rect("dBot",LIGHT,GX,744,1488,328),DOM))
out.append(V(label("dBotC",'Switch(varDom, "S", "SAFETY EVENTS", "Q", "REWORK BY REASON", "D", "SPEED LOSS (units short)", "DT", "DOWNTIME BY REASON", "C", "SCRAP BY REASON", "P", "STAFFING", "M", "TROUBLESHOOTING CONCERNS", "PC", "MOST-MISSED PC ITEMS", "A", "OPEN ACTIONS BY SOURCE") & "  ·  all lines shown  ·  " & If(varDom = "A", "now", Text(varD, "ddd m/d"))',GX+12,748,1400,28,size=12,bold=True,color=TEAL_D),DOM))
out.append(pareto("galDR",DREAS,GX+12,778,1460,290,rw=420,unit=DUNIT,vis=DOM,rowh=32,size=12))
out.append(V(label("dBotE",f'If(CountRows({DREAS}) = 0, "Nothing logged for this selection.", "")',GX+12,820,1400,30,size=12,color=G9),DOM))

# =========================== CELL LAYER ===========================
CR=LR
out.append(V(rect("cCardBg",WHITE,GX,140,600,328,extra={"BorderColor":F(G1),"BorderThickness":"=2"}),CELL))
out.append(V(rect("cCardSt",COL(SW("st",CR)),GX,140,600,10),CELL))
out.append(V(label("cCardT",'"LINE " & varLine & "  ·  " & '+DNAME,GX+20,158,560,34,size=16,bold=True,color=TEAL_D,font="Georgia"),CELL))
out.append(V(label("cCardV",SW("txt",CR),GX+20,196,560,96,size=56,bold=True,font="Georgia",extra={"Color":F(COL(SW("st",CR)))}),CELL))
out.append(V(label("cCardS",SW("sub",CR),GX+20,296,560,30,size=14,color=G9),CELL))
out.append(V(label("cCardG",'"●— " & '+SW("tgt",CR),GX+20,330,560,26,size=11,bold=True,color=DARK),CELL))
out.append(V(label("cCardD",'Text(varD, "dddd m/d") & If(ddShift.Selected.Value = "All", "  ·  all shifts", "  ·  shift " & ddShift.Selected.Value)',GX+20,356,560,26,size=11,color=G5),CELL))
out.append(V(label("cCardTip",'Switch(varDom, '+", ".join(f'"{k}", "{TIPS[k]}"' for k in DK)+')',GX+20,386,560,74,size=10,color=G9,valign="Top"),CELL))
SWL=lambda f: SW(f)
out.append(V(label("ctC",'"7-DAY TREND   ●— target"',624,140,400,24,size=10,bold=True,color=TEAL_D),CELL))
out.append(svgimg("imgCT", svgchart('ForAll(Filter(colDaily, Line = varLine), {V: '+SWB("val")+', T: '+SWB("tg")+', S: '+SWB("st")+', Tx: '+SWB("txt")+', Day: Day})', 876, 300, values=True), 624, 166, 876, 300, CELL))
# detail table
def DET(k):
    sd='Text(ShiftDate, "ddd m/d")'; ss='"S" & Shift'
    F_=lambda coll: f'Filter({coll}, Line = varLine && {SHM})'
    pct_=lambda e: f'If(IsBlank({e}), "—", Text({e} * 100, "0") & "%")'
    if k=="S": return ('Ungroup(Table({t: ' + f'ForAll({F_("colSafe")}, {{K: DateDiff(Date(2020, 1, 1), HourStart, TimeUnit.Minutes), T1: {sd}, T2: {ss} & " H" & HourNo, T3: Coalesce(SafetyNotes, "Safety event"), T4: Coalesce(DT_Reason, ""), T5: "", St: "R", Id: 0, EK: "", Act: false}})' + '}, '
                       '{t: ForAll(Filter(colFR, Line = varLine), {K: DateDiff(Date(2020, 1, 1), AuditDate, TimeUnit.Minutes), T1: Text(AuditDate, "ddd m/d"), T2: "SAFETY AUDIT", '
                       'T3: Coalesce(Severity.Value, "?") & ": " & Item & If(IsBlank(Finding), "", " | " & Finding), T4: ZoneID & If(Kind.Value = "5S", "  ·  5S " & Coalesce(Pillar.Value, ""), ""), T5: Rating.Value, '
                       'St: If(Severity.Value = "Critical" || Severity.Value = "High", "R", "A"), Id: 0, EK: "", Act: false})}), t)')
    if k=="Q": return f'ForAll({F_("colQA")}, {{K: DateDiff(Date(2020, 1, 1), ShiftDate, TimeUnit.Minutes) + Shift, T1: {sd}, T2: {ss}, T3: Reason, T4: ProductForm & "  ·  job " & Coalesce(Job, "—"), T5: Text(ReworkQty, "#,##0") & " units", St: "A"}})'
    if k=="D": return f'ForAll({F_("colShift")}, {{K: DateDiff(Date(2020, 1, 1), ShiftDate, TimeUnit.Minutes) + Shift, T1: {sd}, T2: {ss}, T3: ProductForm, T4: Text(ActualUnits, "#,##0") & " / " & Text(TargetUnits, "#,##0"), T5: If(Coalesce(TargetUnits, 0) = 0, "—", Text(ActualUnits / TargetUnits * 100, "0") & "%"), St: If(Coalesce(TargetUnits, 0) = 0, "N", ActualUnits / TargetUnits * 100 >= varAG, "G", ActualUnits / TargetUnits * 100 >= varAA, "A", "R")}})'
    if k=="DT": return ('ForAll(' + EVT("Line = varLine","true") + ', {K: DateDiff(Date(2020, 1, 1), SD, TimeUnit.Minutes) + Sh * 100 + H1, T1: Text(SD, "ddd m/d"), '
                        'T2: "S" & Sh & " H" & H1 & If(H2 > H1, "–" & H2, ""), T3: R, '
                        'T4: If(EL > 0, "Escalated L" & EL & "  ·  ", "") & If(TSn > 0, Text(TSn) & " TS linked", Wv > 0, "no TS needed (waived)", Need, "NO TS RECORD", Mach, "short stop (< " & varTSReq & " min)", "not a machine stop"), T5: Text(Mn) & " min", '
                        'St: If(EL > 0, "R", Mn >= varDA, "A", "G")})')
    if k=="C": return f'ForAll({F_("colShift")}, {{K: DateDiff(Date(2020, 1, 1), ShiftDate, TimeUnit.Minutes) + Shift, T1: {sd}, T2: {ss}, T3: "Avail " & {pct_("Availability")} & "  ·  Perf " & {pct_("Performance")} & "  ·  Qual " & {pct_("Quality")}, T4: Text(Coalesce(ReportedDowntimeMin, 0)) & " min down  ·  scrap " & Text(Coalesce(FGScrapQty, 0)) & If(IsBlank(ScrapReasonCode), "", " (" & ScrapReasonCode & ")"), T5: {pct_("OEE")}, St: If(IsBlank(OEE), "N", OEE * 100 >= varOG, "G", OEE * 100 >= varOA, "A", "R")}})'
    if k=="P": return f'ForAll({F_("colShift")}, {{K: DateDiff(Date(2020, 1, 1), ShiftDate, TimeUnit.Minutes) + Shift, T1: {sd}, T2: {ss}, T3: "Standard " & StdCrewSize & "  ·  actual " & ActualCrewSize, T4: Coalesce(StaffingReasonCode, "") & If(IsBlank(SpeedLossReasonCode), "", "  ·  speed loss: " & SpeedLossReasonCode), T5: If(ActualCrewSize > StdCrewSize, "+" & (ActualCrewSize - StdCrewSize), ActualCrewSize < StdCrewSize, Text(ActualCrewSize - StdCrewSize), "on std"), St: If(ActualCrewSize < StdCrewSize, "R", ActualCrewSize > StdCrewSize, "A", "G")}})'
    if k=="M": return ('Ungroup(Table({t: ' + f'ForAll({F_("colTS")}, {{K: DateDiff(Date(2020, 1, 1), OccurredAt, TimeUnit.Minutes), T1: {sd}, T2: {ss}, T3: EquipType & ": " & Coalesce(LookUp(colIss, ID = IssueID).Title, "concern " & IssueID), T4: Coalesce(LookUp(colFix, ID = FixID).Title, "no fix") & "  ·  " & Outcome.Value & If(IsBlank(EventKey), "  ·  NOT LINKED", "  ·  board " & Substitute(Last(Split(EventKey, "|")).Value, "Machine - ", "")), T5: Text(Coalesce(RepairMin, 0)) & " min repair" & If(OperatorCouldFix, "  OP", ""), St: If(Outcome.Value = "Not resolved - escalated", "R", IsBlank(EventKey) || OperatorCouldFix, "A", "G")}})'[:-2] + ', Id: ID, EK: Coalesce(EventKey, ""), Act: IsBlank(EventKey)})}, '
        '{t: ForAll(Filter(' + EVT("Line = varLine","true") + ', Need && TSn = 0 && Wv = 0), {K: DateDiff(Date(2020, 1, 1), T0, TimeUnit.Minutes), T1: Text(SD, "ddd m/d"), T2: "S" & Sh, '
        'T3: Substitute(R, "Machine - ", "") & ": board stop, hour " & H1 & If(H2 > H1, "–" & H2, ""), T4: "NO TS RECORD" & If(EL > 0, "  ·  escalated L" & EL, ""), T5: Text(Mn) & " min down", '
        'St: "R", Id: 0, EK: SK & "|" & R, Act: true})}), t)')
    if k=="PC": return f'ForAll({F_("colPC")}, {{K: DateDiff(Date(2020, 1, 1), Coalesce(CompletedAt, ShiftDate), TimeUnit.Minutes), T1: {sd}, T2: {ss}, T3: Coalesce(AuditorName, AuditedBy), T4: Text(NYes) & " yes  ·  " & Text(NNo) & " no" & If(Coalesce(NNA, 0) > 0, "  ·  " & NNA & " n/a", ""), T5: Result.Value & "  " & Text(Score * 100, "0") & "%", St: If(Result.Value = "Fail", "R", "G")}})'
    if k=="A": return ('ForAll(Filter(colNews, Line = varLine && (Status.Value = "Open" || Status.Value = "In progress" || ClosedDate >= varD0)), '
                       '{K: DateDiff(Date(2020, 1, 1), DueDate, TimeUnit.Minutes), T1: "due " & Text(DueDate, "m/d"), T2: Left(SQDCP.Value, 1) & " · " & Left(Source.Value, 6), T3: Title, T4: Coalesce(Owner, "— unassigned"), T5: Status.Value, '
                       'St: If(Status.Value = "Done" || Status.Value = "Canceled", "G", DueDate < Today(), "R", "A")})')
ACTX={"DT":', Id: 0, EK: SK & "|" & R, Act: Need && TSn = 0 && Wv = 0',}
def DETX(k):
    d=DET(k)
    if k in ("M", "S"): return d
    assert d.endswith('})'), k
    return d[:-2]+ACTX.get(k,', Id: 0, EK: "", Act: false')+'})'
CDET='SortByColumns(Switch(varDom, '+", ".join(f'"{k}", {DETX(k)}' for k in DK)+'), "K", SortOrder.Descending)'
HEADS={"S":("DAY","HOUR / AUDIT","WHAT HAPPENED / FOUND","DT REASON / ZONE","RATING"),"Q":("DAY","SHIFT","REASON","PRODUCT · JOB","QTY"),"D":("DAY","SHIFT","PRODUCT","ACTUAL / TARGET","ATTAIN."),
       "DT":("DAY","HOURS","REASON","ESCALATION · TROUBLESHOOTING","MINUTES"),"C":("DAY","SHIFT","A · P · Q","DOWNTIME · SCRAP","OEE"),"P":("DAY","SHIFT","CREW","REASON","VS STD"),"M":("DAY","SHIFT","CONCERN / BOARD STOP","FIX · OUTCOME · LINK","TIME"),
       "PC":("DAY","SHIFT","AUDITOR","ANSWERS","RESULT"),"A":("DUE","TYPE","ACTION","OWNER","STATUS")}
COLX=[(16,100),(118,70),(192,390),(588,250),(842,112)]
out.append(V(rect("cDetHdr",TEAL_D,GX,476,1050,30),CELL))
for j,(x,w) in enumerate(COLX):
    out.append(V(label(f"cH{j}",'Switch(varDom, '+", ".join(f'"{k}", "{HEADS[k][j]}"' for k in DK)+')',GX+x,476,w,30,size=10,bold=True,color=WHITE),CELL))
ek=[rect("eSt",COL("ThisItem.St"),0,4,8,32,indent=I)]
for j,(x,w) in enumerate(COLX):
    ek.append(label(f"eT{j+1}",f"ThisItem.T{j+1}",x,0,w,40,size=11 if j!=2 else 12,bold=(j in (2,4)),indent=I,extra={"Tooltip":F(f"ThisItem.T{j+1}")}))
ek.append(rect("eLine",G1,0,39,1050,1,indent=I))
ek.insert(0,rect("eAct","RGBA(210, 153, 34, 0.10)",0,0,1050,40,indent=I,extra={"Visible":"=ThisItem.Act"}))
ek.append(label("eRec",'"⇄ LINK"',962,8,80,24,size=9,bold=True,color=WHITE,fill=AMBER,align="Center",indent=I,extra={"Visible":"=ThisItem.Act && varCanLink"}))
ek.append(label("eRecV",'"⇄ VIEW"',962,8,80,24,size=9,bold=True,color=WHITE,fill=G5,align="Center",indent=I,extra={"Visible":"=ThisItem.Act && !varCanLink"}))
TAPDET=('If(varDom = "DT" || ThisItem.Id = 0,\n'
 ' Set(varRecEv, ThisItem.EK);\n'
 ' Set(varRecTS, With({e: LookUp(' + REC_EV + ', Key = ThisItem.EK)}, With({b: First(SortByColumns(AddColumns(' + UNL + ', Sc, ' + SC_E + '), "Sc", SortOrder.Descending))}, If(b.Sc >= 50, b.ID, Blank())))),\n'
 ' Set(varRecTS, ThisItem.Id);\n'
 ' Set(varRecEv, With({o: LookUp(colTS, ID = ThisItem.Id)}, With({b: First(SortByColumns(AddColumns(' + NEEDEV + ', Sc, ' + SC_O + '), "Sc", SortOrder.Descending))}, If(b.Sc >= 50, b.Key, "")))));\n'
 'Set(varRec, true)')
ek.append(tap("eTap",TAPDET,0,0,1050,40,indent=I,tip='"Open reconcile with this row and its strongest match picked"',vis="ThisItem.Act"))
out.append(gal("galDet",CDET,GX,508,1050,562,40,ek,vis=CELL))
out.append(V(label("cDetE",f'If(CountRows({CDET}) = 0, "No records for line " & varLine & " in the last 7 days.", "")',GX,560,1050,40,size=13,color=G9,align="Center"),CELL))
CREAS='Switch(varDom, '+", ".join(f'"{k}", {reasons(k,"Line = varLine","true","true")}' for k in DK)+')'
out.append(V(rect("cRBg",LIGHT,GX+1062,476,426,594),CELL))
out.append(V(label("cRC",'"PARETO  ·  LINE " & varLine & "  ·  7 DAYS"',GX+1074,480,400,28,size=11,bold=True,color=TEAL_D),CELL))
out.append(pareto("galCR",CREAS,GX+1074,510,404,556,rw=170,unit=DUNIT,vis=CELL,rowh=34,size=10))
out.append(V(label("cRE",f'If(CountRows({CREAS}) = 0, "Nothing logged.", "")',GX+1074,540,404,30,size=11,color=G9),CELL))

# =========================== RIGHT: NEWSPAPER ===========================
RX=1512; RW=396
out.append(rect("npHdr",DARK,RX,138,RW,36))
out.append(label("npTitle",'"NEWSPAPER  ·  OPEN ACTIONS"',RX+10,138,260,36,size=12,bold=True,color=AQUA))
out.append(btn("btnAdd",'"+ ACTION"','Set(varAdd, true)',RX+RW-110,142,100,28,size=11))
NSC=('If(varLayer in ["line", "cell"], Line = varLine, Line in colFloor.Line) && '
     'If(varLayer in ["domain", "cell"] && varDom in ["S", "Q", "D", "C", "P"], SQDCP.Value = Switch(varDom, "S", "Safety", "Q", "Quality", "D", "Delivery", "C", "Cost", "People"), true)')
NEWS_ITEMS=f'SortByColumns(Filter(colNews, (Status.Value = "Open" || Status.Value = "In progress") && {NSC}), "DueDate", SortOrder.Ascending)'
out.append(label("npScope",'Switch(varLayer, "floor", "All lines shown", "line", "Line " & varLine, "domain", ' + DNAME + ' & " · all lines", "Line " & varLine & " · " & ' + DNAME + ') & "  ·  " & CountRows(' + NEWS_ITEMS + ') & " open"',
                 RX,176,RW,24,size=10,color=G9,align="Center"))
CYCLE=('With({nx: Switch(ThisItem.Status.Value, "Open", "In progress", "In progress", "Done", "Open")},\n'
       '  If(IsError(Patch(Newspaper, LookUp(Newspaper, ID = ThisItem.ID), {Status: {Value: nx}, ClosedDate: If(nx = "Done", Now(), Blank())})), Notify("Could not update the action", NotificationType.Error)));\n'
       'ClearCollect(colNews, Filter(Newspaper, Status.Value = "Open" || Status.Value = "In progress" || ClosedDate >= varD0))')
nk=[rect("nBg","RGBA(247, 248, 248, 1)",4,4,RW-28,108,indent=I),
    rect("nStripe",'Switch(ThisItem.SQDCP.Value, "Safety", '+RED+', "Quality", RGBA(123, 63, 160, 1), "Delivery", '+TEAL_D+', "Cost", '+AMBER+', "People", '+TEAL+', '+G9+')',4,4,8,108,indent=I),
    label("nTitle",'ThisItem.Title',20,6,RW-60,44,size=12,bold=True,indent=I,extra={"Tooltip":F("ThisItem.Problem")}),
    label("nMeta",'"Line " & ThisItem.Line & "  ·  " & ThisItem.SQDCP.Value & "  ·  " & ThisItem.Source.Value',20,50,RW-60,22,size=9,color=G9,indent=I),
    label("nOwn",'Coalesce(ThisItem.Owner, "— unassigned")',20,72,RW-170,18,size=10,indent=I,extra={"Color":F(f'If(IsBlank(ThisItem.Owner), {RED}, {DARK})')}),
    label("nDue",'"Due " & Text(ThisItem.DueDate, "m/d") & If(ThisItem.DueDate < Today(), "  LATE", "")',20,90,RW-170,20,size=10,bold=True,indent=I,
          extra={"Color":F(f'If(ThisItem.DueDate < Today(), {RED}, {DARK})')}),
    ctrl("nHb","Image@2.2.3",{"Image":F(HB_EXPR(PROG("ThisItem"), 'ThisItem.DueDate < Today() && (ThisItem.Status.Value = "Open" || ThisItem.Status.Value = "In progress")', "ThisItem.Status.Value")),"ImagePosition":"=ImagePosition.Fit","X":F(str(RW-112)),"Y":"=66","Width":"=40","Height":"=40"},I),
    label("nPct",'Text('+PROG("ThisItem")+') & "%"',RW-68,66,48,40,size=10,bold=True,color=DARK,indent=I),
    btn("nStatus",'""',CYCLE_PATCH("ThisItem",'ClearCollect(colNews, Filter(Newspaper, Status.Value = "Open" || Status.Value = "In progress" || ClosedDate >= varD0))'),RW-116,62,100,48,fill=CLEAR,color=CLEAR,indent=I,
        extra={"HoverFill":F("RGBA(0, 72, 81, 0.08)"),"BorderColor":F(CLEAR),"Tooltip":'="Tap to step progress: 0 → 25 → 50 → 75 → 100% (Done)"'})]
out.append(gal("galNews",NEWS_ITEMS,RX,202,RW,868,116,nk))
out.append(label("lblNoNews",f'If(CountRows({NEWS_ITEMS}) = 0, "No open actions for this selection.", "")',RX,260,RW,40,size=12,color=G9,align="Center"))

# =========================== RECONCILE OVERLAY ===========================
REC_EV=EVT("Line = varLine","true",shm=False)
EVR='LookUp('+REC_EV+', Key = varRecEv)'
out.append(V(btn("btnRec",'"⇄  RECONCILE  (" & Text(CountRows(Filter(colTS, Line = varLine && IsBlank(EventKey))) + CountRows(Filter('+REC_EV+', Need && TSn = 0 && Wv = 0))) & ")"','Set(varRecTS, Blank()); Set(varRecEv, ""); Set(varRec, true)',1552,96,236,32,size=11,fill=AMBER,color=DARK,
   extra={"Tooltip":'="Link troubleshooting records to board downtime for this line, or waive stops that need no TS record (last 7 days, all shifts)"'}),'varLayer in ["line", "cell"]'))

VR={"Visible":"=varRec"}
def vr(d=None): d=dict(d or {}); d.update(VR); return d
out.append(rect("rcDim","RGBA(7, 39, 45, 0.55)",0,0,1920,1080,extra=VR))
out.append(rect("rcPanel",WHITE,160,110,1600,900,extra=VR))
out.append(rect("rcHdr",DARK,160,110,1600,60,extra=VR))
out.append(label("rcTitle",'"RECONCILE DOWNTIME  ·  LINE " & varLine & "  ·  7 days ending " & Text(varD, "m/d")',184,110,1100,60,size=18,bold=True,color=AQUA,font="Georgia",extra=VR))
out.append(btn("rcClose",'"✕  CLOSE"','Set(varRec, false)',1630,122,116,36,size=11,fill=G1,color=DARK,extra=vr()))
out.append(label("rcRule",'"Board = source of truth. Machine stops of " & varTSReq & "+ min need a TS record. LINK a record to its stop, or mark a stop NO TS NEEDED with a reason. All shifts. " & If(varCanLink, "", "VIEW ONLY: restricted (People → CanLinkDowntime).")',
   184,176,1550,30,size=11,color=G9,extra=vr({"Color":F(f'If(varCanLink, {G9}, {RED})')})))
# left: TS records with no board event
RU=('With({e: ' + EVR + '}, If(IsBlank(varRecEv), SortByColumns(AddColumns(' + UNL + ', Sc, 0), "OccurredAt", SortOrder.Descending),\n'
    ' SortByColumns(AddColumns(' + UNL + ', Sc, ' + SC_E + '), "Sc", SortOrder.Descending)))')
out.append(label("rcLC",'"TROUBLESHOOTING WITH NO BOARD EVENT  (" & CountRows(' + RU + ') & ")"',184,212,740,28,size=12,bold=True,color=TEAL_D,extra=VR))
uk=[rect("ruBg",f'If(ThisItem.ID = varRecTS, {AQUA}, RGBA(247, 248, 248, 1))',0,3,736,74,indent=I),
    label("ruW",'Text(ThisItem.OccurredAt, "ddd m/d h:mm AM/PM") & "  ·  S" & ThisItem.Shift',12,4,360,26,size=11,bold=True,indent=I),
    label("ruE",'ThisItem.EquipType',380,4,200,26,size=12,bold=True,color=TEAL_D,indent=I),
    label("ruS",'If(IsBlank(varRecEv), "", ' + STRENGTH("ThisItem.Sc") + ')',440,4,130,26,size=9,bold=True,align="Right",indent=I,
          extra={"Color":F(f'If(ThisItem.Sc >= 80, {GREEN}, ThisItem.Sc >= 50, {AMBER}, {G5})')}),
    label("ruR",'Text(Coalesce(ThisItem.RepairMin, 0)) & " min repair"',580,4,150,26,size=10,color=G9,align="Right",indent=I),
    label("ruC",'Coalesce(LookUp(colIss, ID = ThisItem.IssueID).Title, "concern") & "  ·  " & ThisItem.Outcome.Value & "  ·  " & Coalesce(ThisItem.LoggedBy, "")',12,32,716,40,size=10,color=G9,indent=I),
    tap("ruTap",'Set(varRecTS, ThisItem.ID)',0,0,736,80,indent=I)]
out.append(gal("galRU",RU,184,244,740,690,80,uk,vis="varRec"))
out.append(label("rcLE",f'If(CountRows({RU}) = 0, "All troubleshooting records on this line are linked.", "")',184,300,740,30,size=12,color=G9,extra=VR))
# right: board machine events without TS, ranked for the selected record
SEL='LookUp(colTS, ID = varRecTS)'
RE=('With({ev: ' + NEEDEV + ', o: ' + SEL + '},\n'
    ' If(IsBlank(varRecTS), SortByColumns(AddColumns(ev, Sc, 0, Dist, 0), "T0", SortOrder.Descending),\n'
    '  SortByColumns(AddColumns(ev, Sc, ' + SC_O + ', Dist, Abs(DateDiff(T0, o.OccurredAt, TimeUnit.Minutes))), "Sc", SortOrder.Descending)))')
out.append(label("rcRC",'"MACHINE STOPS " & varTSReq & "+ MIN WITH NO TS RECORD  (" & CountRows(Filter(' + REC_EV + ', Need && TSn = 0 && Wv = 0)) & ")" & If(IsBlank(varRecTS), "", "  ·  strongest match first")',
   996,212,740,28,size=12,bold=True,color=TEAL_D,extra=VR))
xk=[rect("reBg",f'If(ThisItem.Key = varRecEv, {AQUA}, RGBA(247, 248, 248, 1))',0,3,736,74,indent=I),
    rect("reSt",f'If(ThisItem.EL > 0, {RED}, {AMBER})',0,3,6,74,indent=I),
    label("reW",'Text(ThisItem.SD, "ddd m/d") & "  ·  S" & ThisItem.Sh & " hour " & ThisItem.H1 & If(ThisItem.H2 > ThisItem.H1, "–" & ThisItem.H2, "")',14,4,360,26,size=11,bold=True,indent=I),
    label("reR",'Substitute(ThisItem.R, "Machine - ", "")',380,4,220,26,size=12,bold=True,color=TEAL_D,indent=I),
    label("reM",'Text(ThisItem.Mn) & " min" & If(ThisItem.EL > 0, "  ·  L" & ThisItem.EL, "")',600,4,130,26,size=11,bold=True,align="Right",indent=I),
    label("reF",'If(IsBlank(varRecTS), "", ' + STRENGTH("ThisItem.Sc") + ' & "  ·  " & If(ThisItem.Dist < 60, Text(ThisItem.Dist) & " min apart", Text(Round(ThisItem.Dist / 60, 1)) & " h apart") & If(ThisItem.SK = ' + SEL + '.ShiftKey, "  ·  same shift", ""))',14,34,716,36,size=10,bold=True,indent=I,
          extra={"Color":F(f'If(ThisItem.Sc >= 80, {GREEN}, ThisItem.Sc >= 50, {AMBER}, {G9})')}),
    tap("reTap",'Set(varRecEv, ThisItem.Key)',0,0,736,80,indent=I)]
out.append(gal("galRE",RE,996,244,740,690,80,xk,vis="varRec"))
out.append(label("rcRE",f'If(CountRows(Filter({REC_EV}, Need && TSn = 0 && Wv = 0)) = 0, "Every machine stop of " & varTSReq & "+ min has a TS record or a waiver.", "")',996,300,740,30,size=12,color=G9,extra=VR))
LINK=('If(IsError(Patch(TS_Occurrences, LookUp(TS_Occurrences, ID = varRecTS), {EventKey: varRecEv, LinkStatus: {Value: "Linked later"}, LinkedBy: User().Email, LinkedAt: Now()})),\n'
      ' Notify("Link not saved. Check your connection and try again.", NotificationType.Error),\n'
      ' Notify("Linked.", NotificationType.Success);\n'
      ' ' + LOADTS + ';\n'
      ' Set(varRecTS, Blank()); Set(varRecEv, "");\n'
      ' Select(btnCalc))')
LOKR='varCanLink && !IsBlank(varRecTS) && !IsBlank(varRecEv)'
out.append(btn("rcLink",f'If(!varCanLink, "LINKING RESTRICTED", IsBlank(varRecTS) || IsBlank(varRecEv), "PICK ONE ON EACH SIDE", "⇄  LINK")',LINK,1486,946,260,52,size=14,color=WHITE,fill=GREEN,
   extra=vr({"DisplayMode":F(f'If({LOKR}, DisplayMode.Edit, DisplayMode.Disabled)'),"DisabledFill":F(G1),"DisabledColor":F(G9)})))
out.append(label("rcSel",'If(IsBlank(varRecEv), If(IsBlank(varRecTS), "", "Record picked. Strongest stop is first on the right."), IsBlank(varRecTS), "Stop picked: " & Substitute(' + EVR + '.R, "Machine - ", "") & " " & ' + EVR + '.SK, LookUp(colTS, ID = varRecTS).EquipType & " fix  →  board event " & Substitute(Last(Split(varRecEv, "|")).Value, "Machine - ", "") & " (" & First(Split(varRecEv, "|")).Value & ")")',
   184,946,560,52,size=11,bold=True,color=DARK,extra=VR))
WAIVE=('With({e: ' + EVR + '}, If(IsError(Patch(TS_Occurrences, Defaults(TS_Occurrences), {Title: "WAIVE " & e.SK & " " & Text(Now(), "hhmmss"),\n'
       '  OccurredAt: e.T0, Line: varLine, EquipType: LookUp(colMR, Label = e.R).EquipType, ShiftDate: e.SD, Shift: e.Sh, ShiftKey: e.SK,\n'
       '  EventKey: varRecEv, LinkStatus: {Value: "Waived"}, LinkedBy: User().Email, LinkedAt: Now(), LoggedBy: User().Email, Notes: "No TS needed: " & ddWaive.Selected.Value})),\n'
       ' Notify("Waiver not saved. Check your connection and try again.", NotificationType.Error),\n'
       ' Notify("Marked: no TS needed.", NotificationType.Success);\n'
       ' ' + LOADTS + ';\n'
       ' Set(varRecTS, Blank()); Set(varRecEv, "");\n'
       ' Select(btnCalc)))')
LOKW='varCanLink && !IsBlank(varRecEv)'
out.append(dd("ddWaive",'["Operator cleared it, no maintenance", "Minor stop, no maintenance needed", "Covered by another TS record", "Not an equipment problem"]',760,950,380,44,size=12,extra=vr()))
out.append(btn("rcWaive",'If(!varCanLink, "WAIVE RESTRICTED", IsBlank(varRecEv), "PICK A STOP TO WAIVE", "NO TS NEEDED")',WAIVE,1150,946,320,52,size=13,color=DARK,fill=AMBER,
   extra=vr({"DisplayMode":F(f'If({LOKW}, DisplayMode.Edit, DisplayMode.Disabled)'),"DisabledFill":F(G1),"DisabledColor":F(G9),"Tooltip":'="Records that this board stop needed no troubleshooting record, with the reason, who and when."'})))

# =========================== ADD-ACTION OVERLAY ===========================
VA={"Visible":"=varAdd"}
def vx(d): d=dict(d or {}); d.update(VA); return d
out.append(rect("ovDim","RGBA(7, 39, 45, 0.55)",0,0,1920,1080,extra=VA))
out.append(rect("ovPanel",WHITE,560,170,800,700,extra=VA))
out.append(rect("ovHdr",DARK,560,170,800,60,extra=VA))
out.append(label("ovTitle",'"NEW NEWSPAPER ACTION  ·  TIER 2"',584,170,700,60,size=18,bold=True,color=AQUA,font="Georgia",extra=VA))
cv=lambda n,t,x,y,w: V(cap(n,t,x,y,w,color=G9),"varAdd")
out.append(cv("ocA","ACTION (WHAT WILL BE DONE)",584,246,700))
out.append(ti("txtAAction",'""',584,268,752,48,hint='"e.g. Replace worn filler nozzle gaskets"',size=15,extra=vx(None)))
out.append(cv("ocL","LINE",584,330,150))
out.append(dd("ddALine",'ForAll(colLines, {Value: Title})',584,352,150,48,size=15,extra=vx({"Default":F('If(IsBlank(varLine), First(colFloor).Line, varLine)')})))
out.append(cv("ocS","SQDCP",746,330,200))
out.append(dd("ddASQ",'["Safety", "Quality", "Delivery", "Cost", "People"]',746,352,200,48,size=15,
   extra=vx({"Default":F('Switch(varDom, "S", "Safety", "Q", "Quality", "C", "Cost", "P", "People", "PC", "People", "Delivery")')})))
out.append(cv("ocD","DUE",958,330,200))
out.append(dd("ddADue",'ForAll(Sequence(30, 1), With({d: DateAdd(Today(), Value, TimeUnit.Days)}, {Value: Text(d, "ddd m/d"), D: d}))',958,352,200,48,size=15,extra=vx({"Default":F('Text(DateAdd(Today(), 7, TimeUnit.Days), "ddd m/d")')})))
out.append(cv("ocO","OWNER",1170,330,170))
out.append(ti("txtAOwner",'""',1170,352,166,48,hint='"name"',size=15,extra=vx(None)))
out.append(cv("ocP","PROBLEM (WHAT HAPPENED)",584,414,700))
out.append(ti("txtAProblem",'""',584,436,752,140,hint='"What happened, where, how much"',size=14,extra=vx({"Mode":"=TextMode.MultiLine"})))
out.append(cv("ocC","COUNTERMEASURE (OPTIONAL)",584,590,700))
out.append(ti("txtACM",'""',584,612,752,110,hint='"Containment / root-cause fix"',size=14,extra=vx({"Mode":"=TextMode.MultiLine"})))
SAVEA=('If(IsError(Patch(Newspaper, Defaults(Newspaper),\n'
 '  {Action: txtAAction.Text, Line: ddALine.Selected.Value,\n'
 '   ValueStream: LookUp(colLines, Title = ddALine.Selected.Value).ValueStream,\n'
 '   SQDCP: {Value: ddASQ.Selected.Value}, Source: {Value: "Tier 2"}, Status: {Value: "Open"},\n'
 '   Problem: txtAProblem.Text, Countermeasure: txtACM.Text, Owner: txtAOwner.Text,\n'
 '   RaisedDate: Now(), DueDate: ddADue.Selected.D, RefKey: "T2-" & Text(Now(), "yyyymmddhhmmss")})),\n'
 ' Notify("Action not saved. Check your connection and try again.", NotificationType.Error),\n'
 ' Reset(txtAAction); Reset(txtAProblem); Reset(txtACM); Reset(txtAOwner);\n'
 ' Set(varAdd, false);\n'
 ' ClearCollect(colNews, Filter(Newspaper, Status.Value = "Open" || Status.Value = "In progress" || ClosedDate >= varD0)))')
out.append(btn("btnASave",'"SAVE ACTION"',SAVEA,1176,790,160,52,size=14,color=WHITE,fill=GREEN,
   extra=vx({"DisplayMode":F('If(IsBlank(txtAAction.Text) || IsBlank(txtAOwner.Text), DisplayMode.Disabled, DisplayMode.Edit)')})))
out.append(btn("btnACancel",'"CANCEL"','Set(varAdd, false)',1004,790,160,52,size=14,color=DARK,fill=G1,extra=vx(None)))
out.append(label("ocReq",'"Action and owner are required."',584,800,400,30,size=11,color=G9,extra=VA))

yaml="".join(out)
write_themed(OUT, yaml)
print("ok",len(yaml),"controls",yaml.count("    Control:"))
