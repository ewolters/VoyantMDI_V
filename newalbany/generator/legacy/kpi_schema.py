"""Adds KPI_Daily (Tier 3 history) + Tier 3 settings to deploy/mdi_package.json. Idempotent."""
import json, html
P = __import__("os").environ["MDI_DEPLOY"]+"/mdi_package.json"
p = json.load(open(P))
def text(n): return f'<Field Type="Text" Name="{n}" DisplayName="{n}" StaticName="{n}"/>'
def num(n, dec=0): return f'<Field Type="Number" Name="{n}" DisplayName="{n}" Decimals="{dec}" StaticName="{n}"/>'
def date(n, only=True): return f'<Field Type="DateTime" Name="{n}" DisplayName="{n}" Format="{"DateOnly" if only else "DateTime"}" StaticName="{n}"/>'
# same raw measures Tier 2 computes per line per day
RAW = ["Plan", "EffW", "Tgt", "Act", "OEEw", "Shifts", "Scrap", "CrewA", "CrewS", "DT", "RW", "Saf", "TSn", "TSop", "TSnr", "TSu", "MNt",
       "PCd", "PCf", "PCx", "Esc", "AO", "OV", "DTe", "DTl", "EscL", "Fz", "Fch", "FA"]
DEC = {"Plan": 1, "EffW": 2, "OEEw": 2}
p['schema']['KPI_Daily'] = {"base": 100,
  "desc": "Tier 3 history: one row per line per day with the same measures Tier 2 computes (written by the Tier 3 board for closed days). Title = Line|yyyymmdd. Line FLOOR = plant-wide Frontier findings.",
  "title": {"name": "Title", "req": True, "fmt": ""},
  "fields": [text("Line"), text("ValueStream"), date("KPIDate")] + [num(k, DEC.get(k, 0)) for k in RAW] + [date("UpdatedAt", False), text("UpdatedBy")],
  "view": ["Title", "Line", "ValueStream", "KPIDate", "Act", "Plan", "Shifts", "DT", "RW", "Saf", "Fz", "UpdatedAt"],
  "query": '<OrderBy><FieldRef Name="KPIDate" Ascending="FALSE" /></OrderBy>', "rows": 100}
p['indexes']['KPI_Daily'] = ["KPIDate", "Line", "Title"]
if 'KPI_Daily' not in p['perms']['data']: p['perms']['data'].append('KPI_Daily')
rows = p['ensureRows'].setdefault('MDI_Config', [])
have = {r['Title'] for r in rows}
for t, v, k, n in [("App_Tier3", "", "App link", "Tier 3 Board web link (play URL)"),
                   ("T3_WeekStart", "Monday", "Setting", "Tier 3: first day of the week for weekly trends (Monday or Sunday)")]:
    if t not in have: rows.append({"Title": t, "SettingValue": v, "Kind": k, "Notes": n})
json.dump(p, open(P, 'w'), indent=1, ensure_ascii=False)
print("KPI_Daily fields:", len(p['schema']['KPI_Daily']['fields']), "| lists:", len(p['schema']))
