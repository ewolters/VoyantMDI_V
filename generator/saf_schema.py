"""Adds the Frontier (safety + 5S) lite lists to deploy/mdi_package.json. Idempotent."""
import json, html
P = '/mnt/user-data/outputs/deploy/mdi_package.json'
p = json.load(open(P))
GRAY = '{"$schema":"https://developer.microsoft.com/json-schemas/sp/v2/column-formatting.schema.json","elmType":"div","style":{"color":"#75787B","font-weight":"600"},"txtContent":"@currentField"}'
def pill(colors, default="#75787B"):
    expr = f"'{default}'"
    for k, c in reversed(list(colors.items())):
        expr = f"if(@currentField == '{k}', '{c}', {expr})"
    return json.dumps({"$schema": "https://developer.microsoft.com/json-schemas/sp/v2/column-formatting.schema.json", "elmType": "div",
        "style": {"display": "flex", "align-items": "center", "height": "100%"},
        "children": [{"elmType": "span", "style": {"padding": "0 10px", "border-radius": "11px", "color": "white", "font-weight": "600",
            "height": "22px", "line-height": "22px", "white-space": "nowrap", "box-sizing": "border-box",
            "display": "=if(@currentField == '', 'none', 'inline-block')", "background-color": "=" + expr}, "txtContent": "@currentField"}]},
        separators=(",", ":"))
def fx(fmt): return f' CustomFormatter="{html.escape(fmt, quote=True)}"' if fmt else ''
def text(n, req=False, fmt=None): return f'<Field Type="Text" Name="{n}" DisplayName="{n}" StaticName="{n}"{" Required=\"TRUE\"" if req else ""}{fx(fmt)}/>'
def note(n): return f'<Field Type="Note" Name="{n}" DisplayName="{n}" NumLines="6" RichText="FALSE" StaticName="{n}"/>'
def num(n, req=False, dec=0, fmt=GRAY): return f'<Field Type="Number" Name="{n}" DisplayName="{n}" Decimals="{dec}" StaticName="{n}"{" Required=\"TRUE\"" if req else ""}{fx(fmt)}/>'
def date(n, only=True): return f'<Field Type="DateTime" Name="{n}" DisplayName="{n}" Format="{"DateOnly" if only else "DateTime"}" StaticName="{n}"/>'
def boolean(n, default=1): return f'<Field Type="Boolean" Name="{n}" DisplayName="{n}" StaticName="{n}"><Default>{default}</Default></Field>'
def choice(n, ch, default=None, fmt=None):
    c = ''.join(f'<CHOICE>{html.escape(x)}</CHOICE>' for x in ch)
    d = f'<Default>{html.escape(default)}</Default>' if default else ''
    return f'<Field Type="Choice" Name="{n}" DisplayName="{n}" Format="Dropdown" StaticName="{n}"{fx(fmt)}>{d}<CHOICES>{c}</CHOICES></Field>'
SEV = {"Critical": "#CF222E", "High": "#E36209", "Medium": "#D29922", "Low": "#2EA043", "None": "#B1B3B3"}
RAT = {"S": "#2EA043", "OK": "#2EA043", "AR": "#D29922", "U": "#CF222E", "Deficient": "#CF222E", "N/A": "#B1B3B3"}
ZT = ["Transition", "Hidden infrastructure", "Overhead & below", "Temporal", "General"]
S = p['schema']
S['SAF_Zones'] = {"base": 100, "desc": "Frontier zone registry. One row per zone. ZoneID format FZ-<SITE>-<TYPE>-<NN>, e.g. FZ-NAL-TR-01. StandardID = the zone's 5S standard (SW Manager, type 5S).",
  "title": {"name": "ZoneID", "req": True, "fmt": ""},
  "fields": [text("ZoneName"), choice("ZoneType", ZT, "General"), text("Line"), text("Area"),
             choice("RiskLevel", ["High", "Medium", "Low"], "Medium", pill({"High": "#CF222E", "Medium": "#D29922", "Low": "#2EA043"})),
             choice("Frequency", ["Weekly", "Biweekly", "Monthly", "Quarterly"], "Monthly"),
             text("RequiredPPE"), note("PrimaryHazards"), num("StandardID"), text("Owner"), text("OwnerEmail"), text("Auditors"), note("Notes"), boolean("Active")],
  "view": ["ZoneID", "ZoneName", "ZoneType", "Line", "Area", "RiskLevel", "Frequency", "StandardID", "Owner", "Active"], "query": '<OrderBy><FieldRef Name="Title" /></OrderBy>', "rows": 100}
S['SAF_Items'] = {"base": 100, "desc": "Frontier Card safety checklist (front of the card). Edit wording here; retire with Active = No, never delete.",
  "title": {"name": "Check", "req": True, "fmt": ""},
  "fields": [num("ItemNo", True), choice("Category", ["Body position", "PPE", "Surfaces", "Energy", "Emergency", "Environment"]), note("LookFor"), boolean("Active")],
  "view": ["ItemNo", "Category", "Check", "LookFor", "Active"], "query": '<OrderBy><FieldRef Name="ItemNo" /></OrderBy>', "rows": 100}
S['SAF_Audits'] = {"base": 100, "desc": "One row per Frontier audit (card header, operator interaction, close the loop, totals).",
  "title": {"name": "Ref", "req": False, "fmt": ""},
  "fields": [text("ZoneID"), text("ZoneName"), text("ZoneType"), text("Line"), text("Area"), date("AuditDate"), num("Shift"),
             choice("Classification", ["Routine", "Deep dive", "Post-incident", "New process", "Seasonal"], "Routine"),
             text("AuditedBy"), text("AuditorName"), note("WhyZone"), note("FirstLook"), date("StartedAt", False), date("CompletedAt", False),
             num("NS"), num("NAR"), num("NU"), num("NNA"), num("SafePct", dec=2), num("N5SOK"), num("N5SDef"), num("StandardID"),
             choice("TopSeverity", ["Critical", "High", "Medium", "Low", "None"], "None", pill(SEV)),
             text("OperatorRole"), note("Q1"), note("Q2"), note("Q3"), note("Q4"), num("Comfort"), note("KeyConcern"),
             choice("LoopMethod", ["On the spot", "Within 24 hours", "Pending", "Not done"]), date("FollowUpDate"), note("Notes")],
  "view": ["Ref", "AuditDate", "ZoneID", "ZoneName", "AuditorName", "SafePct", "NAR", "NU", "N5SDef", "TopSeverity", "LoopMethod", "Created"],
  "query": '<OrderBy><FieldRef Name="Created" Ascending="FALSE" /></OrderBy>', "rows": 100}
S['SAF_Results'] = {"base": 100, "desc": "Every rated line of every Frontier audit: safety items (S/AR/U/N/A) and 5S sections (OK/Deficient/N/A), with severity, finding, photo and action link.",
  "title": {"name": "Ref", "req": False, "fmt": ""},
  "fields": [num("AuditID"), text("ZoneID"), text("Line"), date("AuditDate"), choice("Kind", ["Safety", "5S"]), num("ItemNo"), text("Category"), text("Item"), num("ElementID"),
             choice("Rating", ["S", "AR", "U", "N/A", "OK", "Deficient"], None, pill(RAT)),
             choice("Pillar", ["Sort", "Set in order", "Shine", "Standardize", "Sustain"]),
             choice("Severity", ["Critical", "High", "Medium", "Low"], None, pill(SEV)),
             note("Finding"), note("ImmediateAction"), boolean("SafetyRelevant", 0), boolean("ActionCreated", 0), text("NewspaperRef"), text("ZoneOwnerEmail")],
  "view": ["AuditID", "ZoneID", "Kind", "ItemNo", "Item", "Rating", "Pillar", "Severity", "Finding", "ActionCreated", "Created"],
  "query": '<OrderBy><FieldRef Name="Created" Ascending="FALSE" /></OrderBy>', "rows": 100}
ITEMS = [
 ("Body position", "Lifting posture", "Load held close, knees bent, no twisting while lifting; lift aids used where provided."),
 ("Body position", "Reaching", "No reaching above shoulder or below knee to do the task; no overreaching or lateral bending."),
 ("Body position", "Repetitive motion / awkward posture", "Repeated motions, sustained bending, twisting or kneeling; pacing, rotation and breaks."),
 ("Body position", "Workstation height", "Tables, benches and controls at the right height for the task and the person."),
 ("PPE", "Correct PPE, good condition", "Required PPE for the zone and task is worn, fits, and is not worn out or damaged."),
 ("PPE", "PPE available at point of use", "Required PPE is stocked in the zone; nobody has to leave to get it."),
 ("Surfaces", "Trip / slip hazards", "Cords, hoses, strapping, spills, debris or uneven floor in walkways and work areas."),
 ("Surfaces", "Guardrails / handrails", "Present and secure wherever there is an edge, stair or platform."),
 ("Surfaces", "Floor markings", "Aisle, storage and hazard markings visible, accurate and respected."),
 ("Energy", "LOTO applied where required", "Stored energy isolated and locked during maintenance or clearing; lockout points visible."),
 ("Energy", "Electrical clearance (36 in.)", "36 in. clear in front of panels; covers closed; no taped repairs or exposed conductors."),
 ("Energy", "Chemical containers labeled, contained", "GHS labels, lids on, secondary containment, SDS available."),
 ("Energy", "Compressed gas chained / capped", "Cylinders secured upright, caps on when not in use, stored by type."),
 ("Emergency", "Extinguisher / eyewash accessible", "Not blocked, inspection tags current, eyewash flowing and signed."),
 ("Emergency", "Exit paths clear and marked", "Exit routes free of clutter, signs lit or reflective, doors unlocked."),
 ("Emergency", "Spill / first aid kit stocked", "Kits present, complete and in date."),
 ("Environment", "Lighting adequate for task", "Enough light to work and to see hazards; no burned-out fixtures in the zone."),
 ("Environment", "Ventilation / air quality", "No buildup of dust, fumes or vapors; extraction working."),
 ("Environment", "Noise: can talk at arm's length?", "If you have to shout at arm's length, hearing protection is required and should be worn."),
]
p['seed']['SAF_Items'] = [{"Title": t, "ItemNo": i + 1, "Category": c, "LookFor": lf, "Active": True} for i, (c, t, lf) in enumerate(ITEMS)]
p['indexes']['SAF_Zones'] = ['Title*', 'Active', 'Line']
p['indexes']['SAF_Items'] = ['ItemNo', 'Active']
p['indexes']['SAF_Audits'] = ['Title', 'ZoneID', 'AuditDate']
p['indexes']['SAF_Results'] = ['AuditID', 'ZoneID', 'AuditDate', 'Severity']
for k, l in [('config', 'SAF_Zones'), ('config', 'SAF_Items'), ('data', 'SAF_Audits'), ('data', 'SAF_Results')]:
    if l not in p['perms'][k]: p['perms'][k].append(l)
# choices added to existing lists (provisioner merges them in on existing sites too)
p['choiceAdds'] = {"SW_Standards": {"DocType": ["5S"]}, "Newspaper": {"Source": ["Frontier audit"]}, "TS_Photos": {"Module": ["Frontier audit"]}}
for lst, fs in p['choiceAdds'].items():
    for fname, adds in fs.items():
        for i, x in enumerate(S[lst]['fields']):
            if f' Name="{fname}"' in x:
                for a in adds:
                    if f'<CHOICE>{html.escape(a)}</CHOICE>' not in x: x = x.replace('</CHOICES>', f'<CHOICE>{html.escape(a)}</CHOICE></CHOICES>')
                S[lst]['fields'][i] = x
# config rows added on existing sites too (only if the Title is missing)
p['ensureRows'] = {"MDI_Config": [
  {"Title": "App_Frontier", "SettingValue": "", "Kind": "App link", "Notes": "Frontier Audit (phone) web link. Zone QR codes = this + ?zone=<ZoneID>"},
  {"Title": "SAF_DueDays_Critical", "SettingValue": "1", "Kind": "Threshold", "Notes": "Frontier: days to close a Critical finding (also: stop work + Teams alert)"},
  {"Title": "SAF_DueDays_High", "SettingValue": "1", "Kind": "Threshold", "Notes": "Frontier: days to start corrective action on a High finding"},
  {"Title": "SAF_DueDays_Medium", "SettingValue": "30", "Kind": "Threshold", "Notes": "Frontier: days to close a Medium finding"},
  {"Title": "SAF_DueDays_Low", "SettingValue": "90", "Kind": "Threshold", "Notes": "Frontier: days to close a Low finding (next maintenance window)"},
  {"Title": "SAF_DueDays_5S", "SettingValue": "30", "Kind": "Threshold", "Notes": "Frontier: days to close a 5S deficiency that is not safety-relevant"},
  {"Title": "Safety_Email", "SettingValue": "", "Kind": "Other", "Notes": "Frontier: safety coordinator email(s), ; separated. Get a Teams alert on every Critical finding (with the zone owner)."}]}
json.dump(p, open(P, 'w'), separators=(',', ':'))
print('ok', len(S), 'lists')
