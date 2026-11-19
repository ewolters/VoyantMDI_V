# ---- UX layer: required-field coloring, hints, tooltips, small fixes ----
YEL="RGBA(255, 242, 179, 1)"; YELB="RGBA(210, 153, 34, 1)"; LRED="RGBA(249, 214, 213, 1)"; REDB="RGBA(207, 34, 46, 1)"
AMBL="RGBA(253, 236, 200, 1)"; OFF="RGBA(236, 236, 234, 1)"; W_="RGBA(255, 255, 255, 1)"; GB="RGBA(177, 179, 179, 1)"; GL="RGBA(217, 217, 214, 1)"
STARTED="Now() >= ThisItem.StartT"; ENDED="Now() >= DateAdd(ThisItem.StartT, ThisItem.SlotMin, TimeUnit.Minutes)"
def E(name, **kw):
    EXTRA.setdefault(name, {}).update({k: (v if str(v).startswith("=") else "="+str(v)) for k,v in kw.items()})
def tip(name, text): E(name, Tooltip='"'+text.replace('"','""')+'"')
# timed-required (hour row): yellow once the hour starts, red once it ends
def timed(name, empty, filled_fill=W_):
    E(name, Fill=f'If(!ThisItem.InShift, {OFF}, !({empty}), {filled_fill}, {ENDED}, {LRED}, {STARTED}, {YEL}, {W_})',
            BorderColor=f'If(!ThisItem.InShift, {GL}, !({empty}), {GB}, {ENDED}, {REDB}, {STARTED}, {YELB}, {GB})',
            BorderThickness=f'If(ThisItem.InShift && ({empty}) && {STARTED}, 3, 1)')
# conditional-required: yellow only when `need` is true and it is empty
def cond(name, need, empty):
    E(name, Fill=f'If(({need}) && ({empty}), {YEL}, {W_})', BorderColor=f'If(({need}) && ({empty}), {YELB}, {GB})',
            BorderThickness=f'If(({need}) && ({empty}), 3, 1)')
def optional(name): E(name, BorderColor=GL, BorderThickness="1")

# hour rows
timed("gCounter", "IsBlank(ThisItem.Cum)")
timed("gBPM", "IsBlank(ThisItem.BPM)", filled_fill=f'If(ThisItem.BPM < varTmax, {AMBL}, {W_})')
cond("gDT1", '!IsBlank(ThisItem.Reason)', "IsBlank(ThisItem.DT)")
cond("gR1", "Coalesce(ThisItem.DT, 0) > 0", 'IsBlank(ThisItem.Reason)')
cond("gDT2", '!IsBlank(ThisItem.Reason2)', "IsBlank(ThisItem.DT2)")
cond("gR2", "Coalesce(ThisItem.DT2, 0) > 0", 'IsBlank(ThisItem.Reason2)')
for n in ["gJob","gPlan","gNotes"]: optional(n)
E("gCounter", HintText=f'If(ThisItem.InShift && {STARTED}, "enter", "")')
E("gBPM", HintText=f'If(ThisItem.InShift && {STARTED}, "bpm", "")')
for n in ["gPlan","gDT1","gDT2"]: E(n, HintText='""')
E("gJob", HintText='""'); E("gNotes", HintText='""')

# shift-level
E("txtJob1", Fill=f'If(IsBlank(Self.Text), {YEL}, {W_})', BorderColor=f'If(IsBlank(Self.Text), {YELB}, {GB})', BorderThickness='If(IsBlank(Self.Text), 3, 1)')
E("txtCrew", Fill=f"If(Self.Text = \"\", {YEL}, Coalesce(Value(Self.Text), 0) > Value(varPB.'Total HC'), {AMBL}, {W_})",
             BorderColor=f'If(IsBlank(Self.Text), {YELB}, {GB})', BorderThickness='If(IsBlank(Self.Text), 3, 1)')
cond("ddStaff", "Coalesce(Value(txtCrew.Text), 0) > Value(varPB.'Total HC')", 'IsBlank(Self.Selected.Value)')
E("txtScrap", Fill=f'If(IsBlank(Self.Text), {YEL}, {W_})', BorderColor=f'If(IsBlank(Self.Text), {YELB}, {GB})', BorderThickness='If(IsBlank(Self.Text), 3, 1)', HintText='"0 if none"')
cond("ddScrapReason", "Coalesce(Value(txtScrap.Text), 0) > 0", 'IsBlank(Self.Selected.Value)')
cond("ddSpeedLoss", "With({b: If(CountRows(Filter(colHours, Coalesce(BPM, 0) > 0)) = 0, Blank(), Average(Filter(colHours, Coalesce(BPM, 0) > 0), BPM))}, !IsBlank(b) && b < varTmax)", 'IsBlank(Self.Selected.Value)')
for n in ["txtLunch","txtBreak","txtScrapNotes"]: optional(n)

# fixes
E("lblTitle", Size="22", Width="260", Wrap="false")
E("lblStd", Text="If(IsBlank(varPB), \"No PLAYBOOK standard\", \"STD  \" & Text(varPB.Rate) & \" BPM  ·  \" & Text(varUPH, \"#,##0\") & \" /hr\" & Char(10) & \"Crew \" & Text(Value(varPB.'Total HC')) & \"  ·  Eff \" & If(varPB.Rate > 0, Text(varUPH / (varPB.Rate * 60) * 100, \"0\") & \"%\", \"—\"))")
E("cPlanChk", Visible="false"); E("lblPlanChk", Visible="false")
E("lblSumTitle", Width="170")

# column headers: ● marks operator-entry columns
HDR={0:("HOUR","Hour of the shift. Highlighted row = the hour running now. Gray rows are outside the shift."),
 1:("JOB","Only fill if the job changed this hour (changeover). Blank = Job 1."),
 2:("HR TGT","Hourly target = PLAYBOOK units/hr x (minutes in this slot - planned minutes) / 60."),
 3:("CUM TGT","Running total of hourly targets through this hour."),
 4:("● COUNTER","Cumulative counter reading at the END of the hour - not the hourly count. The board calculates the hour."),
 5:("HR ACT","Units made this hour = this counter - last hour's counter."),
 6:("RUN %","How this hour ran: HR ACT / HR TGT. Green 100%+, amber 90-99%, red under 90%. ★ purple = an exceptional hour for this line (well above its normal hour over the last 30 days)."),
 7:("+/- CUM","Counter minus cumulative target. Green = ahead of plan, red = behind."),
 8:("● BPM","Line speed this hour in bottles per minute. Amber = below standard speed."),
 10:("● DT1","Unplanned downtime minutes, first event. Pick a reason next to it."),
 11:("● DT1 REASON","Reason for downtime event 1. Required when DT1 > 0."),
 12:("● DT2","Unplanned downtime minutes, second event this hour (if any)."),
 13:("● DT2 REASON","Reason for downtime event 2. Required when DT2 > 0."),
 14:("● SAFETY","Tap for a safety incident or near miss this hour (turns red). Tap again to undo. Add a note."),
 15:("NOTES","Optional. Anything leadership should know about this hour.")}
for i,(t,tt) in HDR.items():
    E(f"h{i:02d}", Text='"'+t+'"', Tooltip='"'+tt+'"', Color=("RGBA(7, 39, 45, 1)" if t.startswith("●") else "RGBA(117, 120, 123, 1)"))
PLANOK='Sum(colHours, Planned) = Coalesce(Value(txtLunch.Text), 0) + Coalesce(Value(txtBreak.Text), 0)'
E("h09", Text='"● PLAN" & Char(10) & Text(Sum(colHours, Planned)) & "/" & Text(Coalesce(Value(txtLunch.Text), 0) + Coalesce(Value(txtBreak.Text), 0))',
   Color=f'If({PLANOK}, RGBA(7, 39, 45, 1), RGBA(207, 34, 46, 1))', Size="9",
   Tooltip='"Planned minutes in this hour (lunch, break, planned meeting). Lowers the hour target. Header shows minutes marked / lunch + break - they should match."')

# tooltips on inputs
T={"ddLine":"Production line. Standards load from the PLAYBOOK list.",
 "ddProduct":"Item running now (Size | Form). Long list? Type part of the size or form in FIND to narrow it. Sets standard speed, units/hr and crew from the PLAYBOOK.",
 "txtProdFind":"Type part of the size or form (for example 10 oz or wash) to narrow the product list. Clear it to see all.",
 "btnDate":"Date the shift STARTED (night shift keeps its start date after midnight). Tap for a calendar.",
 "ddShift":"1 = first shift, 2 = second shift.",
 "btnRefresh":"Reload this line / date / shift from SharePoint. Display screens: press to pick up the latest entries.",
 "ddStart":"Actual shift start. Changing it rebuilds the hour rows and targets.",
 "ddEnd":"Actual shift end. Hours after the end show 'off' with no target.",
 "txtLunch":"Lunch minutes this shift. Also put them in the PLAN column of the hour lunch was taken.",
 "txtBreak":"Break minutes this shift. Also put them in the PLAN column of the hour(s) breaks were taken.",
 "txtJob1":"REQUIRED. Primary job number for the shift.",
 "lblStdCrew":"Standard crew for this item from the PLAYBOOK (Total HC).",
 "txtCrew":"REQUIRED. People actually on the line. If more than standard, pick a reason.",
 "ddStaff":"Required when actual crew is above standard.",
 "gJob":"Only if the job changed this hour (changeover). Blank = Job 1.",
 "gCounter":"REQUIRED each hour. Cumulative counter reading at the END of the hour. Yellow = due now, red = overdue.",
 "gBPM":"REQUIRED each hour. Line speed in bottles per minute. Amber after entry = below standard speed.",
 "gPlan":"Planned minutes this hour (lunch, break, planned meeting). Lowers this hour's target.",
 "gDT1":"Unplanned downtime minutes, event 1.",
 "gR1":"Reason for downtime event 1. Required when there are DT1 minutes. List comes from the Lookups list (Downtime).",
 "gDT2":"Unplanned downtime minutes, event 2 (if a second issue hit this hour).",
 "gR2":"Reason for downtime event 2. Required when there are DT2 minutes. List comes from the Lookups list (Downtime).",
 "gSafety":"Tap if a safety incident or near miss happened this hour. Tap again to undo. Add a note.",
 "gNotes":"Optional note for this hour.",
 "txtScrap":"REQUIRED at end of shift. Finished-goods scrap units. Enter 0 if none.",
 "ddScrapReason":"Required when scrap is more than 0.",
 "txtScrapNotes":"Optional detail on scrap.",
 "ddSpeedLoss":"Required when average speed for the shift is below standard.",
 "kAttain":"Counter at the last entered hour / cumulative target through that hour. Green 100%+, amber 90-99%, red under 90%.",
 "kUnits":"Units made vs target through the last entered hour. Bottom line = full-shift target.",
 "kOEE":"OEE = Availability x Performance x Quality. A = uptime / (shift - lunch - break); P = avg BPM / standard BPM; Q = 1 - scrap / units.",
 "kDT":"Reported = DT1 + DT2 minutes entered. Calc = available time - machine uptime (units / avg BPM). % reported shows how much downtime got logged.",
 "kSafety":"Hours flagged EVENT this shift."}
for n,t in T.items(): tip(n,t)

# ---- target speed (PLAYBOOK Rate) shown where the BPM is entered ----
E("h08", Text='"● BPM" & Char(10) & If(varTmax > 0, "TGT " & Text(varTmax), "no std")', Size="9",
  Tooltip='"Line speed this hour in bottles per minute. TGT = target speed for this item from the PLAYBOOK (Rate). Amber after entry = below target."')
E("gBPM", HintText=f'If(ThisItem.InShift && {STARTED}, If(varTmax > 0, "tgt " & Text(varTmax), "bpm"), "")',
  Tooltip='"REQUIRED each hour. Line speed in bottles per minute. Target for this item: " & If(varTmax > 0, Text(varTmax) & " BPM (PLAYBOOK)", "not in PLAYBOOK") & ". Amber after entry = below target."')
E("lblStd", Text="If(IsBlank(varPB), \"No PLAYBOOK standard\", \"TARGET SPEED  \" & Text(varPB.Rate) & \" BPM\" & Char(10) & Text(varUPH, \"#,##0\") & \" /hr  ·  Crew \" & Text(Value(varPB.'Total HC')) & \"  ·  Eff \" & If(varPB.Rate > 0, Text(varUPH / (varPB.Rate * 60) * 100, \"0\") & \"%\", \"—\"))",
  Color="RGBA(176, 227, 228, 1)", Size="14")

# ---- job numbers are 6 characters ----
E("txtJob1", MaxLength="6")
E("gJob", MaxLength="6")
