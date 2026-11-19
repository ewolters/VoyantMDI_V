# MDI Settings: IMPORT HISTORY screen (scrImport) + regenerated THRESHOLDS screen with the IMPORT button.
import os, sys
SCR = __import__("os").environ["MDI_TMP"]+"/set/"
os.makedirs(SCR, exist_ok=True)
os.environ["SETOUT"] = SCR
sys.argv = ["settings.py", "3"]
exec(open(__import__("os").environ["MDI_GEN"]+"/settings.py").read())
FLOWN = "'MDI-ImportHistory'"
OUTDIR = __import__("os").environ["MDI_OUTDIR"]+"/"

def N(f): return f'IfError(Value(Text(v.{f}), "en-US"), Blank())'
def T(f): return f'Trim(Text(v.{f}))'
def Z(f): return f'With({{z: Trim(Text(v.{f}))}}, If(z = "0", "", z))'
def HM(f):  # minutes after midnight from ISO text or Excel serial
    return (f'With({{t: Text(v.{f})}}, If(IsNumeric(t), RoundDown(Mod(Value(t, "en-US"), 1) * 1440 + 0.5, 0),'
            f' With({{p: Coalesce(Find("T", t), 0)}}, IfError(Value(Mid(t, p + 1, 2)) * 60 + Value(Mid(t, p + 4, 2)), 0))))')
def DATE(f):
    return (f'IfError(With({{t: Text(v.{f})}}, If(t = "", Blank(), IsNumeric(t), DateAdd(Date(1899, 12, 30), RoundDown(Value(t, "en-US"), 0), TimeUnit.Days),'
            f' Date(Value(Left(t, 4)), Value(Mid(t, 6, 2)), Value(Mid(t, 9, 2))))), Blank())')
def DTM(f):
    return (f'IfError(With({{t: Text(v.{f})}}, If(t = "", Blank(), IsNumeric(t), DateAdd(Date(1899, 12, 30), RoundDown(Value(t, "en-US") * 1440 + 0.5, 0), TimeUnit.Minutes),'
            f' DateAdd(Date(Value(Left(t, 4)), Value(Mid(t, 6, 2)), Value(Mid(t, 9, 2))), {HM(f)}, TimeUnit.Minutes))), Blank())')
def TM(f):
    return f'IfError(If(Trim(Text(v.{f})) = "", "", With({{m: {HM(f)}}}, Text(Time(RoundDown(m / 60, 0), Mod(m, 60), 0), "h:mm AM/PM"))), "")'

SREC = ('{L: ' + T("Line") + ', D: ' + DATE("SnapshotDate") + ', Sh: ' + N("Shift") + ', PF: ' + T("ProductForm") + ', J1: ' + Z("Job1") + ', J2: ' + Z("Job2") +
        ', PSH: ' + N("PlannedShiftHrs") + ', ST: ' + TM("ActualStartTime") + ', ET: ' + TM("ActualEndTime") + ', LM: ' + N("LunchMin") + ', BM: ' + N("BreakMin") +
        ', TU: ' + N("TargetUnits") + ', AU: ' + N("ActualUnits") + ', AB: ' + N("AvgBPM") + ', TB: ' + N("TmaxBPM") + ', RD: ' + N("ReportedDowntimeMin") +
        ', CD: ' + N("CalculatedDowntimeMin") + ', MU: ' + N("MachineUptimeMin") + ', AV: ' + N("Availability") + ', PE: ' + N("Performance") +
        ', FS: ' + N("FGScrapQty") + ', QU: ' + N("Quality") + ', OE: ' + N("OEE") + ', SR: ' + Z("ScrapReasonCode") + ', SN: ' + Z("ScrapNotes") +
        ', SC: ' + N("StdCrewSize") + ', AC: ' + N("ActualCrewSize") + ', STR: ' + Z("StaffingReasonCode") + ', SLR: ' + Z("SpeedLossReasonCode") + '}')
PREC = ('{L: ' + T("Line") + ', D: ' + DATE("SnapshotDate") + ', Sh: ' + N("Shift") + ', HS: ' + DTM("HourStart") + ', PF: ' + T("ProductForm") + ', Job: ' + Z("Job") +
        ', HT: ' + N("HourlyTarget") + ', CT: ' + N("CumulativeTarget") + ', CU: ' + N("CumulativeUnits") + ', HA: ' + N("HourlyActual") + ', BPM: ' + N("BPM") + ', RR: ' + N("RunRatePct") + '}')
DREC = ('{L: ' + T("Line") + ', D: ' + DATE("SnapshotDate") + ', Sh: ' + N("Shift") + ', HS: ' + DTM("HourStart") + ', R0: ' + T("ReasonCode") + ', Cat: ' + T("Category") +
        ', M: ' + N("Minutes") + ', Nt: ' + Z("Notes") + '}')
PJ = lambda prop, rec: f'ForAll(Table(ParseJSON(varIR.{prop})) As j, With({{v: j.Value}}, {rec}))'

NORM = ('If(pl, d.R0, Coalesce(LookUp(colIDTL, Lower(Label) = s).Label,\n'
        '   If(StartsWith(s, "machine"), With({rest: Trim(Substitute(Mid(s, 8), "-", " "))},\n'
        '     Coalesce(LookUp(colIDTL, StartsWith(Lower(Label), "machine - ") && Left(Lower(Mid(Label, 11)), 6) = Left(rest, 6)).Label, "Machine - " & Proper(rest))),\n'
        '   d.R0)))')
SAME = 'L = k.L && D = k.D && Sh = k.Sh && HS = k.HS'
SCAN = ('Set(varIBusy, true); Set(varIFile, ThisItem.Name); Set(varIMsg, ""); Set(varIScanned, false);\n'
 'Set(varIR, Blank());\n'
 f'IfError(Set(varIR, {FLOWN}.Run("READ", ThisItem.Name)), Notify("Could not reach the import flow: " & FirstError.Message, NotificationType.Error));\n'
 'If(!IsBlank(varIR.err), Notify(varIR.err, NotificationType.Error); Set(varIMsg, varIR.err));\n'
 'Clear(colIS); Clear(colIP); Clear(colIDr);\n'
 'If(IsBlank(varIR.err) && !IsBlank(varIR.shift),\n'
 f' IfError(ClearCollect(colIS, {PJ("shift", SREC)});\n'
 f'  ClearCollect(colIP, {PJ("prod", PREC)});\n'
 f'  ClearCollect(colIDr, {PJ("dt", DREC)}),\n'
 '  Notify("The workbook tables could not be read: " & FirstError.Message, NotificationType.Error)));\n'
 'RemoveIf(colIS, IsBlank(D) || L = "" || IsBlank(Sh)); RemoveIf(colIP, IsBlank(D) || L = "" || IsBlank(Sh) || IsBlank(HS));\n'
 'RemoveIf(colIDr, IsBlank(D) || L = "" || IsBlank(Sh) || IsBlank(HS) || Coalesce(M, 0) <= 0);\n'
 'ClearCollect(colIDt, ForAll(colIDr As d, With({s: Lower(d.R0)}, With({pl: Lower(d.Cat) = "planned" || "plan" in s || "plen" in s || "break" in s},\n'
 '  {L: d.L, D: d.D, Sh: d.Sh, HS: d.HS, M: d.M, Nt: d.Nt, R0: d.R0, P: pl, R: ' + NORM + '}))));\n'
 # shifts
 'ClearCollect(colIShifts, ForAll(colIS As s, With({pb: LookUp(colIPB, Line = s.L && Size & " - " & Form = s.PF), k: s.L & "-" & Text(s.D, "yyyymmdd") & "-S" & Text(s.Sh)},\n'
 '  {Title: k, Line: s.L, ShiftDate: s.D, Shift: s.Sh, ProductForm: If(IsBlank(pb), Substitute(s.PF, " - ", " | ", 1), pb.Size & " | " & pb.Form), PlaybookKey: If(IsBlank(pb), "", pb.Title),\n'
 '   Job1: s.J1, Job2: s.J2, PlannedShiftHrs: s.PSH, ActualStartTime: s.ST, ActualEndTime: s.ET, LunchMin: s.LM, BreakMin: s.BM, TargetUnits: s.TU, ActualUnits: s.AU,\n'
 '   AvgBPM: s.AB, TmaxBPM: s.TB, ReportedDowntimeMin: s.RD, CalculatedDowntimeMin: s.CD, MachineUptimeMin: s.MU, Availability: s.AV, Performance: s.PE,\n'
 '   FGScrapQty: s.FS, Quality: s.QU, OEE: s.OE, ScrapReasonCode: s.SR, ScrapNotes: s.SN, StdCrewSize: s.SC, ActualCrewSize: s.AC,\n'
 '   StaffingReasonCode: s.STR, SpeedLossReasonCode: s.SLR, EnteredBy: "import · " & varIFile})));\n'
 # hour keys = production hours + downtime-only hours
 'ClearCollect(colIK, ForAll(colIP, {L: L, D: D, Sh: Sh, HS: HS}));\n'
 'Collect(colIK, ForAll(Filter(colIDt As d, IsBlank(LookUp(colIP, L = d.L && D = d.D && Sh = d.Sh && HS = d.HS))), {L: L, D: D, Sh: Sh, HS: HS}));\n'
 'ClearCollect(colIK2, ForAll(GroupBy(colIK, L, D, Sh, HS, G), {L: L, D: D, Sh: Sh, HS: HS}));\n'
 'ClearCollect(colIHrs, ForAll(colIK2 As k,\n'
 f' With({{p: LookUp(colIP, {SAME}), n: CountRows(Filter(colIK2, L = k.L && D = k.D && Sh = k.Sh && HS < k.HS)) + 1,\n'
 f'       dts: SortByColumns(Filter(colIDt, {SAME} && !P), "M", SortOrder.Descending), pls: Filter(colIDt, {SAME} && P)}},\n'
 '  With({pb: LookUp(colIPB, Line = k.L && Size & " - " & Form = p.PF), sk: k.L & "-" & Text(k.D, "yyyymmdd") & "-S" & Text(k.Sh)},\n'
 '   {Title: sk & "-H" & Text(n, "00"), ShiftKey: sk, Line: k.L, ShiftDate: k.D, Shift: k.Sh, HourNo: n, HourStart: k.HS, SlotMin: 60,\n'
 '    ProductForm: If(IsBlank(pb), Substitute(p.PF, " - ", " ", 1), pb.Size & " " & pb.Form), PlaybookKey: If(IsBlank(pb), "", pb.Title), Job: p.Job,\n'
 '    HourlyTarget: p.HT, CumTarget: p.CT, CumulativeUnits: p.CU, HourlyActual: p.HA, RunRatePct: p.RR, SpeedBPM: p.BPM,\n'
 '    DT_Minutes: First(dts).M, DT_Reason: Coalesce(First(dts).R, ""),\n'
 '    DT2_Minutes: If(CountRows(dts) > 1, Sum(dts, M) - First(dts).M, Blank()), DT2_Reason: If(CountRows(dts) > 1, Last(FirstN(dts, 2)).R, ""),\n'
 '    PlannedMin: If(CountRows(pls) > 0, Sum(pls, M), Blank()),\n'
 '    Notes: Concat(Filter(dts, Nt <> ""), Nt & "; ") & If(CountRows(pls) > 0, "Planned: " & Concat(pls, R0 & " " & Text(M) & "m", ", "), "") & If(CountRows(dts) > 2, " (" & Text(CountRows(dts) - 1) & " stops added into DT2)", ""),\n'
 '    SafetyEvent: false, EnteredBy: "import · " & varIFile}))));\n'
 # what is already in MDI
 'Set(varID0, Min(Min(colIShifts, ShiftDate), Min(colIHrs, ShiftDate))); Set(varID1, Max(Max(colIShifts, ShiftDate), Max(colIHrs, ShiftDate)));\n'
 'Clear(colIExS); Clear(colIExH);\n'
 'ForAll(Distinct(colIShifts, Line) As ln, Collect(colIExS, Filter(HxH_Shift, Line = ln.Value && ShiftDate >= varID0 && ShiftDate <= varID1)));\n'
 'ForAll(Distinct(colIHrs, Line) As ln, ForAll(Sequence(RoundDown(DateDiff(varID0, varID1, TimeUnit.Days) / 7, 0) + 1, 0) As w,\n'
 '  Collect(colIExH, Filter(HxH_Hourly, Line = ln.Value && ShiftDate >= DateAdd(varID0, 7 * w.Value, TimeUnit.Days) && ShiftDate < DateAdd(varID0, 7 * w.Value + 7, TimeUnit.Days)))));\n'
 'Set(varISOld, CountIf(colIShifts, Title in colIExS.Title)); Set(varIHOld, CountIf(colIHrs, Title in colIExH.Title));\n'
 'ClearCollect(colIUnk, Distinct(Filter(colIShifts, PlaybookKey = ""), ProductForm));\n'
 'ClearCollect(colIMap, ForAll(GroupBy(ForAll(Filter(colIDt, !P && R <> R0), {F: R0, T: R}), F, T, G), {F: F, T: T, N: CountRows(G)}));\n'
 'Set(varIScanned, true); Set(varIBusy, false)')

IMPORT = ('Set(varIBusy, true); Clear(colIErr);\n'
 'ForAll(Filter(colIShifts, !(Title in colIExS.Title)) As r, IfError(Collect(HxH_Shift, r), Collect(colIErr, {T: r.Title, M: FirstError.Message}), true));\n'
 'If(varIUpd, ForAll(Filter(colIShifts, Title in colIExS.Title) As r, IfError(Patch(HxH_Shift, LookUp(colIExS, Title = r.Title), r), Collect(colIErr, {T: r.Title, M: FirstError.Message}), true)));\n'
 'ForAll(Filter(colIHrs, !(Title in colIExH.Title)) As r, IfError(Collect(HxH_Hourly, r), Collect(colIErr, {T: r.Title, M: FirstError.Message}), true));\n'
 'If(varIUpd, ForAll(Filter(colIHrs, Title in colIExH.Title) As r, IfError(Patch(HxH_Hourly, LookUp(colIExH, Title = r.Title), r), Collect(colIErr, {T: r.Title, M: FirstError.Message}), true)));\n'
 'Set(varIErrs, CountRows(colIErr)); Set(varIErr1, If(varIErrs > 0, First(colIErr).T & ": " & First(colIErr).M, ""));\n'
 'Set(varIMsg, If(varIErrs = 0, "DONE: " & varIFile & " imported. " & Text(CountRows(colIShifts) - If(varIUpd, 0, varISOld)) & " shifts and " & Text(CountRows(colIHrs) - If(varIUpd, 0, varIHOld)) & " hours written.",\n'
 '  "FINISHED: " & Text(varIErrs) & " row(s) did not save, the rest did. First problem: " & varIErr1));\n'
 'Notify(varIMsg, If(varIErrs = 0, NotificationType.Success, NotificationType.Warning));\n'
 'Set(varIBusy, false); Set(varIScanned, false)')

LOADI = (ME + ';\nSet(varIBusy, true);\n'
 'ClearCollect(colIPB, PLAYBOOK);\n'
 'ClearCollect(colIDTL, Filter(Lookups, Category.Value = "Downtime"));\n'
 f'IfError(Set(varIL, {FLOWN}.Run("LIST", "")), Notify("Could not reach the import flow (MDI - Import History). Is it turned on and added to this app? " & FirstError.Message, NotificationType.Error));\n'
 'If(!IsBlank(varIL.err), Notify(varIL.err, NotificationType.Error));\n'
 'Clear(colIFiles);\n'
 'If(!IsBlank(varIL.files), IfError(ClearCollect(colIFiles, ForAll(Table(ParseJSON(varIL.files)) As j, With({v: j.Value},\n'
 '  {Name: Text(v.Name), KB: RoundUp(Value(Text(v.Length), "en-US") / 1024, 0), At: Text(v.TimeLastModified)}))), Notify("File list unreadable: " & FirstError.Message, NotificationType.Error)));\n'
 'RemoveIf(colIFiles, !(EndsWith(Lower(Name), ".xlsx") || EndsWith(Lower(Name), ".xlsm")));\n'
 'Set(varIBusy, false)')

out = hdr("i", "scrImport", LOADI)
ADM = 'If(varAdm && !varIBusy, DisplayMode.Edit, DisplayMode.Disabled)'
out.append(label("iIntro", '"Back-fill Hour x Hour and Tier 2 from the line data-entry workbooks (Line_209_Data_Entry and the like). Only the Log_Shift, Log_Production and Log_Downtime tabs are read. The newest copy of each line\'s workbook holds its whole history, so one upload per line is enough. Dim_ tabs are ignored: standards live in STANDARDS, reasons in DROPDOWN LISTS."',
                 16, 148, 1888, 52, size=12, color=G9))
# left: folder + files
out.append(rect("iLBg", LIGHT, 16, 206, 640, 864))
out.append(label("iS1", '"1  PUT WORKBOOKS IN THE IMPORT FOLDER"', 32, 214, 600, 30, size=13, bold=True, color=TEAL_D))
out.append(label("iS1t", '"Open the folder, drag the .xlsx files in, then tap ↻ LIST."', 32, 244, 600, 26, size=11, color=G9))
out.append(btn("iOpen", '"OPEN IMPORT FOLDER"', 'Launch(varIL.folder)', 32, 276, 290, 48, size=13, fill=TEAL_D, color=WHITE,
               extra={"DisplayMode": F('If(IsBlank(varIL.folder), DisplayMode.Disabled, DisplayMode.Edit)')}))
out.append(btn("iList", '"↻  LIST"', 'Select(iLoad)', 334, 276, 140, 48, size=13, fill=WHITE, color=TEAL_D, extra={"BorderColor": F(TEAL_D), "BorderThickness": "=1"}))
out.append(label("iS2", '"2  SCAN A WORKBOOK"', 32, 340, 600, 30, size=13, bold=True, color=TEAL_D))
fk = [gl("giN", 'ThisItem.Name', 12, 380, bold=True, size=12, h=30, y=4),
      gl("giA", 'Text(ThisItem.KB) & " KB  ·  added " & Text(DateTimeValue(ThisItem.At), "m/d/yyyy h:mm AM/PM")', 12, 380, size=9, color=G9, h=22, y=32),
      btn("giScan", 'If(varIBusy && varIFile = ThisItem.Name, "…", "SCAN")', SCAN, 470, 9, 120, 40, size=12, fill=TEAL, color=DARK, indent=I,
          extra={"DisplayMode": F(ADM)})]
out.append(gal("galIF", 'colIFiles', 16, 374, 640, 696, 58, fk, 'false', 'ThisItem.Name = varIFile'))
out.append(label("iNoFiles", 'If(varIBusy, "Working…", "No workbooks in the import folder yet.")', 32, 400, 600, 40, size=12, color=G9, extra={"Visible": F('IsEmpty(colIFiles)')}))
# right: preview + import
RX = 676; RW = 1228
VS = 'varIScanned'
def vs(s): return s.replace("    Properties:\n", "    Properties:\n      Visible: =" + VS + "\n", 1)
out.append(ctrl("iRBg", "Rectangle@2.3.0", {"Fill": F(WHITE), "BorderColor": F(G1), "BorderThickness": "=1", **box(RX, 206, RW, 864)}))
out.append(label("iS3", 'If(varIScanned, "3  CHECK, THEN IMPORT:  " & varIFile, "3  CHECK, THEN IMPORT")', RX + 16, 214, RW - 32, 30, size=13, bold=True, color=TEAL_D))
out.append(label("iMsg", 'varIMsg', RX + 16, 248, RW - 32, 40, size=12, bold=True, extra={"Color": F(f'If(StartsWith(varIMsg, "DONE"), {GREEN}, {RED})'), "Visible": F('!IsBlank(varIMsg)')}))
TILES = [("LINE", 'Concat(Distinct(colIShifts, Line), Value, ", ")', '"line(s) in the file"'),
         ("DATES", 'Text(varID0, "m/d/yy") & " – " & Text(varID1, "m/d/yy")', 'Text(DateDiff(varID0, varID1, TimeUnit.Days) + 1) & " days"'),
         ("SHIFTS", 'Text(CountRows(colIShifts))', 'Text(CountRows(colIShifts) - varISOld) & " new  ·  " & Text(varISOld) & " already in MDI"'),
         ("HOURS", 'Text(CountRows(colIHrs))', 'Text(CountRows(colIHrs) - varIHOld) & " new  ·  " & Text(varIHOld) & " already in MDI"'),
         ("DOWNTIME", 'Text(CountIf(colIDt, !P))', 'Text(Sum(Filter(colIDt, !P), M)) & " min unplanned  ·  " & Text(Sum(Filter(colIDt, P), M)) & " min planned"')]
for i, (t, big, sub) in enumerate(TILES):
    x = RX + 16 + i * 240
    out.append(vs(rect(f"iT{i}", TEAL_D, x, 296, 232, 104)))
    out.append(vs(label(f"iT{i}h", f'"{t}"', x, 300, 232, 22, size=9, bold=True, color=AQUA, align="Center")))
    out.append(vs(label(f"iT{i}v", big, x, 322, 232, 44, size=20, bold=True, color=WHITE, align="Center")))
    out.append(vs(label(f"iT{i}s", sub, x + 6, 366, 220, 32, size=9, color=WHITE, align="Center")))
out.append(vs(label("iUnkH", 'If(IsEmpty(colIUnk), "✓  Every product matches a PLAYBOOK row (targets and Tier 2 plan will line up).", "▲  " & Text(CountRows(colIUnk)) & " product(s) not in PLAYBOOK for this line. They import, but Tier 2 plan falls back to the workbook target. Add them in STANDARDS if needed:")',
                    RX + 16, 412, RW - 32, 44, size=11, bold=True, extra={"Color": F(f'If(IsEmpty(colIUnk), {GREEN}, {AMBER})')})))
out.append(vs(label("iUnk", 'Concat(colIUnk, Value, "   ·   ")', RX + 16, 456, RW - 32, 40, size=11, color=DARK)))
out.append(vs(label("iMapH", 'If(IsEmpty(colIMap), "✓  Every downtime reason matches a DROPDOWN LISTS reason.", "Downtime reasons cleaned up to match DROPDOWN LISTS (typed variants in the workbook):")',
                    RX + 16, 504, RW - 32, 30, size=11, bold=True, color=TEAL_D)))
mk = [gl("gmF", 'ThisItem.F', 12, 380, size=11, h=34), gl("gmArrow", '"→"', 396, 30, size=12, color=G9, h=34),
      gl("gmT", 'ThisItem.T', 430, 380, size=11, bold=True, h=34), gl("gmN2", 'Text(ThisItem.N) & " stops"', 820, 140, size=10, color=G9, h=34)]
p = gal("galIMap", 'SortByColumns(colIMap, "N", SortOrder.Descending)', RX + 16, 536, 980, 250, 34, mk, 'false', 'false')
out.append(vs(p))
out.append(vs(label("iPlan", '"Planned stops (breaks, changeovers, batch changes) go into PLANNED MIN for the hour, not downtime. Up to two unplanned stops per hour fill DT and DT2; more are added into DT2."',
                    RX + 16, 792, RW - 32, 44, size=10, color=G9)))
out.append(vs(tog("iUpd", "varIUpd", '"ALSO OVERWRITE ROWS ALREADY IN MDI"', RX + 16, 846, 420, 44, disp=ADM)))
out.append(vs(label("iUpdT", 'If(varIUpd, "Rows already in MDI are replaced with the workbook values.", "Rows already in MDI are left alone (safe to re-run the same workbook).")', RX + 448, 846, 760, 44, size=11, color=G9)))
out.append(vs(btn("iGo", 'If(varIBusy, "IMPORTING…  KEEP THIS OPEN", "IMPORT " & Text(CountRows(colIShifts) - If(varIUpd, 0, varISOld)) & " SHIFTS + " & Text(CountRows(colIHrs) - If(varIUpd, 0, varIHOld)) & " HOURS")',
                  IMPORT, RX + 16, 904, 620, 60, size=16, fill=GREEN, color=WHITE, extra={"DisplayMode": F(ADM)})))
out.append(vs(label("iGoT", 'If(varAdm, "Large files take a few minutes. Boards pick it up on their next REFRESH.", "Only an MDI admin can import.")', RX + 652, 904, 560, 60, size=11, color=G9)))
out.append(label("iIdle", '"Scan a workbook on the left. Nothing is written until you tap IMPORT."', RX + 16, 320, RW - 32, 40, size=14, color=G9, extra={"Visible": F('!varIScanned')}))

write_themed(OUTDIR + "Settings_scrImport_v3.pa.yaml", "".join(out))
import shutil
shutil.copy(__import__("os").environ.get("MDI_OUTDIR", SCR.rstrip("/")) + "/Settings_Thresholds_v3.pa.yaml", OUTDIR + "Settings_scrCfg_v3.pa.yaml")
print("ok")
