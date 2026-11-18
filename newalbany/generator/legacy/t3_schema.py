"""Adds ValueStreams (configurable hierarchy) and Variances (Tier 3 variance boards) to deploy/mdi_package.json. Idempotent."""
import json, html
P = __import__("os").environ["MDI_DEPLOY"]+"/mdi_package.json"
p = json.load(open(P))
def fx(fmt): return f' CustomFormatter="{html.escape(fmt, quote=True)}"' if fmt else ''
def text(n): return f'<Field Type="Text" Name="{n}" DisplayName="{n}" StaticName="{n}"/>'
def note(n): return f'<Field Type="Note" Name="{n}" DisplayName="{n}" NumLines="6" RichText="FALSE" StaticName="{n}"/>'
def num(n, dec=0): return f'<Field Type="Number" Name="{n}" DisplayName="{n}" Decimals="{dec}" StaticName="{n}"/>'
def date(n, only=True): return f'<Field Type="DateTime" Name="{n}" DisplayName="{n}" Format="{"DateOnly" if only else "DateTime"}" StaticName="{n}"/>'
def boolean(n, default=1): return f'<Field Type="Boolean" Name="{n}" DisplayName="{n}" StaticName="{n}"><Default>{default}</Default></Field>'
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
SQ = {"Safety": "#CF222E", "Quality": "#8250DF", "Delivery": "#0969DA", "Cost": "#1A7F37", "People": "#BF8700"}
UNITS = ["units", "cases", "minutes", "hours", "%", "points", "events", "shifts", "people"]
S = p['schema']
S['ValueStreams'] = {"base": 100,
  "desc": "Value streams and verticals for Tier 3. Name = the value stream (must match Lines → ValueStream). ParentVS = the big value stream a vertical belongs to (blank for a top-level value stream). Retire with Active = No.",
  "title": {"name": "Title", "req": True, "fmt": ""},
  "fields": [text("ParentVS"), text("Leader"), text("LeaderEmail"), num("DisplayOrder"), boolean("Active"), note("Notes")],
  "view": ["Title", "ParentVS", "Leader", "DisplayOrder", "Active"], "query": '<OrderBy><FieldRef Name="DisplayOrder" /></OrderBy>', "rows": 100}
S['Variances'] = {"base": 100,
  "desc": "Tier 3 variance boards. 24-hour = the biggest misses of the day (shown for T3_Var24Days days). Monthly = big hits to discuss at the MOR (MonthOf). Magnitude is in operational units, never dollars.",
  "title": {"name": "Title", "req": True, "fmt": ""},
  "fields": [choice("Kind", ["24-hour", "Monthly"], "24-hour", pill({"24-hour": "#CF222E", "Monthly": "#0969DA"})),
             choice("SQDCP", list(SQ), None, pill(SQ)), text("ValueStream"), text("Line"),
             num("Magnitude", 1), choice("Unit", UNITS, "units"), note("Detail"), text("Owner"), text("OwnerEmail"),
             date("RaisedDate", False), date("ShowUntil"), date("MonthOf"),
             choice("Status", ["Open", "Closed"], "Open", pill({"Open": "#CF222E", "Closed": "#2EA043"})), date("ClosedDate", False),
             text("NewspaperRef"), text("RCARef"), text("RaisedBy"), text("Metric"), text("SourceKey")],
  "view": ["Title", "Kind", "SQDCP", "ValueStream", "Line", "Magnitude", "Unit", "Owner", "RaisedDate", "ShowUntil", "MonthOf", "Status"],
  "query": '<OrderBy><FieldRef Name="RaisedDate" Ascending="FALSE" /></OrderBy>', "rows": 100}
p['indexes']['Variances'] = ["RaisedDate", "Status", "ValueStream"]
exec(open(__import__("os").environ["MDI_GEN"]+"/t3_metrics.py").read())
S['KPI_Metrics'] = {"base": 100,
  "desc": "Tier 3 metric catalog. Each SQDCP letter holds several metrics. Title = metric code (fixed; the calculation is built into the apps). Turn metrics on/off (Active), order them, and set Green/Amber thresholds here. Better = Higher or Lower.",
  "title": {"name": "Title", "req": True, "fmt": ""},
  "fields": [choice("Letter", ["S", "Q", "D", "C", "P"], None, pill({"S": "#CF222E", "Q": "#8250DF", "D": "#0969DA", "C": "#1A7F37", "P": "#BF8700"})),
             text("MetricName"), text("Short"), text("Unit"), choice("Better", ["Higher", "Lower"], "Higher"), num("Green", 2), num("Amber", 2),
             num("DisplayOrder"), boolean("Active"), note("Notes")],
  "view": ["Title", "Letter", "MetricName", "Short", "Unit", "Better", "Green", "Amber", "DisplayOrder", "Active"],
  "query": '<OrderBy><FieldRef Name="DisplayOrder" /></OrderBy>', "rows": 100}
if 'KPI_Metrics' not in p['perms']['config']: p['perms']['config'].append('KPI_Metrics')
p['seed']['KPI_Metrics'] = catalog_seed_rows()
for lst, grp in (("ValueStreams", "config"), ("Variances", "data")):
    if lst not in p['perms'][grp]: p['perms'][grp].append(lst)
rows = p['ensureRows'].setdefault('MDI_Config', [])
have = {r['Title'] for r in rows}
for t, v, k, n in [("T3_Var24Days", "7", "Threshold", "Tier 3: days a 24-hour variance stays on the board")]:
    if t not in have: rows.append({"Title": t, "SettingValue": v, "Kind": k, "Notes": n})
json.dump(p, open(P, 'w'), indent=1, ensure_ascii=False)
print("lists:", len(S))
