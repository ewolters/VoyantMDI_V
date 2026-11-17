import openpyxl, json, sys, datetime, warnings; warnings.filterwarnings('ignore')
src, out = sys.argv[1], sys.argv[2]
wb = openpyxl.load_workbook(src, data_only=True)
def conv(v):
    if v is None: return ""
    if isinstance(v, datetime.datetime): return (v - datetime.datetime(1899,12,30)).days + (v - datetime.datetime(1899,12,30)).seconds/86400
    if isinstance(v, datetime.date): return (v - datetime.date(1899,12,30)).days
    if isinstance(v, bool): return v
    if isinstance(v, (int, float)): return v
    return str(v)
data = {"name": sys.argv[3] if len(sys.argv) > 3 else src.split('/')[-1], "sheets": []}
for ws in wb.worksheets:
    data["sheets"].append({"name": ws.title, "v": [[conv(ws.cell(r, c).value) for c in range(1, 19)] for r in range(1, 58)]})
json.dump(data, open(out, "w"))
