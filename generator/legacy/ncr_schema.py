"""Adds the NCR list (nonconformance reports, ISO 9001:2015 8.7 + 10.2) to deploy/mdi_package.json. Idempotent."""
import json, html
P = __import__("os").environ["MDI_DEPLOY"]+"/mdi_package.json"
p = json.load(open(P))
def fx(fmt): return f' CustomFormatter="{html.escape(fmt, quote=True)}"' if fmt else ''
def text(n): return f'<Field Type="Text" Name="{n}" DisplayName="{n}" StaticName="{n}"/>'
def note(n): return f'<Field Type="Note" Name="{n}" DisplayName="{n}" NumLines="6" RichText="FALSE" StaticName="{n}"/>'
def num(n, dec=0): return f'<Field Type="Number" Name="{n}" DisplayName="{n}" Decimals="{dec}" StaticName="{n}"/>'
def date(n, only=True): return f'<Field Type="DateTime" Name="{n}" DisplayName="{n}" Format="{"DateOnly" if only else "DateTime"}" StaticName="{n}"/>'
def boolean(n, default=0): return f'<Field Type="Boolean" Name="{n}" DisplayName="{n}" StaticName="{n}"><Default>{default}</Default></Field>'
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
def choice(n, ch, default=None, fmt=None):
    c = ''.join(f'<CHOICE>{html.escape(x)}</CHOICE>' for x in ch)
    d = f'<Default>{html.escape(default)}</Default>' if default else ''
    return f'<Field Type="Choice" Name="{n}" DisplayName="{n}" Format="Dropdown" StaticName="{n}"{fx(fmt)}>{d}<CHOICES>{c}</CHOICES></Field>'

NCR_SOURCES = ["In-process", "Final inspection", "Customer complaint", "Supplier / incoming", "Audit"]
NCR_STATUS = {"Open": "#CF222E", "Contained": "#BF8700", "Dispositioned": "#8250DF", "CA in progress": "#0969DA", "Closed": "#2EA043", "Void": "#75787B"}
NCR_DISP = ["Use as is", "Rework", "Repair", "Regrade", "Scrap", "Return to supplier"]
NCR_UNITS = ["units", "cases", "pallets", "lbs", "kg", "gallons"]
S = p['schema']
S['NCR'] = {"base": 100,
  "desc": ("Nonconformance reports (ISO 9001:2015 8.7 control of nonconforming outputs, 10.2 corrective action). "
           "Title = NCR number (NCR-yyyy-####). Flow: Open → Contained → Dispositioned → CA in progress → Closed. "
           "Every stage stamps who and when (8.7.2 / 10.2.2 retained evidence). Photos in TS_Photos (Module NCR, RefID = ID)."),
  "title": {"name": "Title", "req": False, "fmt": ""},
  "fields": [
    # 1. identify (8.5.2 traceability)
    choice("Source", NCR_SOURCES, "In-process"), choice("Severity", ["Minor", "Major", "Critical"], "Minor",
           pill({"Minor": "#BF8700", "Major": "#CF222E", "Critical": "#82071E"})),
    text("Line"), text("ValueStream"), date("ShiftDate"), num("Shift"), text("Size"), text("Form"), text("ProductForm"),
    text("Job"), text("Lot"), text("Party"), text("DefectCategory"), note("Description"),
    num("QtyAffected", 1), choice("Unit", NCR_UNITS, "units"), text("Owner"), text("OwnerEmail"),
    text("RaisedBy"), date("RaisedAt", False),
    # 2. contain (8.7.1 b)
    note("Containment"), num("QtyOnHold", 1), text("HoldLocation"), text("ContainedBy"), date("ContainedAt", False),
    # 3. disposition (8.7.1 a-d, 8.7.2 c-d)
    choice("Disposition", NCR_DISP), num("DispQty", 1), note("DispNotes"), boolean("CustomerInformed"), text("Concession"),
    text("DispositionBy"), date("DispositionAt", False),
    boolean("Reverified"), note("ReverifyNotes"), text("ReverifiedBy"), date("ReverifiedAt", False),
    # 4. corrective action (10.2.1 b-c)
    boolean("CARequired", 1), note("RootCause"), note("SimilarCheck"), text("NewspaperRef"), text("RCARef"),
    text("CABy"), date("CAAt", False),
    # 5. effectiveness + close (10.2.1 d-f)
    choice("Effective", ["Pending", "Yes", "No"], "Pending", pill({"Pending": "#75787B", "Yes": "#2EA043", "No": "#CF222E"})),
    note("EffectNotes"), boolean("RiskQMSUpdated"), note("RiskQMSNotes"), text("VerifiedBy"), date("VerifiedAt", False),
    choice("Status", list(NCR_STATUS), "Open", pill(NCR_STATUS)), text("ClosedBy"), date("ClosedAt", False), date("DueDate")],
  "view": ["Title", "Status", "Severity", "Source", "Line", "ProductForm", "Job", "Lot", "DefectCategory", "QtyAffected", "Unit", "Disposition", "Owner", "RaisedAt", "DueDate"],
  "query": '<OrderBy><FieldRef Name="RaisedAt" Ascending="FALSE" /></OrderBy>', "rows": 100}
p['indexes']['NCR'] = ["RaisedAt", "Status", "Line"]
if 'NCR' not in p['perms']['data']: p['perms']['data'].append('NCR')
ca = p['choiceAdds']
for lst, fld, v in (("Newspaper", "Source", "NCR"), ("TS_Photos", "Module", "NCR")):
    ca.setdefault(lst, {}).setdefault(fld, [])
    if v not in ca[lst][fld]: ca[lst][fld].append(v)
DEFECTS = [("Fill / volume", "Under or over fill, wrong weight"), ("Seal / leak", "Cap, seal, crimp or container leaks"),
           ("Label / print", "Wrong, missing, crooked or smeared label, code date or print"),
           ("Contamination", "Foreign matter, wrong color or odor, micro"), ("Packaging damage", "Dented, crushed, torn or scuffed"),
           ("Wrong component", "Wrong bottle, cap, pump, label or carton loaded"), ("Spec / formula", "Off spec batch: viscosity, pH, appearance"),
           ("Count / pack-out", "Short count, mixed product, wrong case pack"), ("Other defect", "Describe in the NCR")]
er = p['ensureRows'].setdefault('Lookups', [])
have = {r['Title'] for r in er}
for i, (t, h) in enumerate(DEFECTS):
    if t not in have:
        er.append({"Title": t, "Category": "NCR defect", "Group": "NCR", "SortOrder": (i + 1) * 10, "Active": True, "Help": h})
rows = p['ensureRows'].setdefault('MDI_Config', [])
haveC = {r['Title'] for r in rows}
for t, v, k, n in [("NCR_DueDays", "30", "Threshold", "NCR: default days to close an NCR")]:
    if t not in haveC: rows.append({"Title": t, "SettingValue": v, "Kind": k, "Notes": n})
json.dump(p, open(P, 'w'), indent=1, ensure_ascii=False)
print("lists:", len(S), "lookups ensure:", len(er))
