"""Starter screen for a NEW app on ONE SharePoint list: browse, search, add, edit and retire records.

The columns come from that list's entry in newalbany/deploy/mdi_package.json, so add the list there first
(see NEW_APP_GUIDE.md). Text, Note, Number, DateTime (typed as a date), Boolean (Yes/No) and Choice columns get
an input; Calculated, MultiChoice, lookup and person columns are shown in the list only if they're text-like,
and are otherwise left out (add them by hand in the generator copy).

    python3 newalbany/generator/starter_app.py <ListName> [AppTitle] [Prefix]
        -> newalbany/build/<ListName>_v1.pa.yaml

This is a starting point, not a finished app: copy it to newalbany/generator/<app>.py, give it a make.py
target, and shape it from there (the generators are the source of truth). Untested until pasted into Studio.
Never deletes: if the list has an Active column, RETIRE sets Active = No.
"""
import json, os, re, sys

GEN = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(GEN)
os.environ.setdefault("MDI_GEN", GEN)
os.environ.setdefault("MDI_OUTDIR", os.path.join(ROOT, "build"))
exec(open(os.path.join(GEN, "theme.py"), encoding="utf-8").read())
_src = open(os.path.join(GEN, "build6.py"), encoding="utf-8").read()
exec(_src[:_src.index("DT_OLD=")])          # shared helpers: ctrl, label, btn, ti, dd, cap, box, F, colors
EXTRA.clear()

if len(sys.argv) < 2: print(__doc__); sys.exit(0)
LIST = sys.argv[1]
PKG = json.load(open(os.path.join(ROOT, "deploy", "mdi_package.json"), encoding="utf-8"))
if LIST not in PKG["schema"]: sys.exit(f"{LIST} is not in newalbany/deploy/mdi_package.json schema; add the list there first")
L = PKG["schema"][LIST]
TITLE_APP = sys.argv[2] if len(sys.argv) > 2 else LIST.replace("_", " ").upper()
P = (sys.argv[3] if len(sys.argv) > 3 else re.sub(r"[^A-Za-z]", "", LIST)[:3]).lower()   # control-name prefix

# ---- columns ----
cols = []
for x in L["fields"]:
    a = dict(re.findall(r' (\w+)="([^"]*)"', x.split(">")[0]))
    t, name = a.get("Type"), a.get("Name")
    if a.get("Hidden") == "TRUE" or a.get("ReadOnly") == "TRUE": continue
    c = {"name": name, "disp": a.get("DisplayName", name), "type": t, "req": a.get("Required") == "TRUE"}
    if t == "Choice": c["choices"] = re.findall(r"<CHOICE>([^<]*)</CHOICE>", x)
    if t in ("Text", "Note", "Number", "DateTime", "Boolean", "Choice"): cols.append(c)
HAS_ACTIVE = any(c["name"] == "Active" and c["type"] == "Boolean" for c in cols)
form = [c for c in cols if c["name"] != "Active"]
TITLE_DISP = L["title"]["name"]

def q(s): return '"' + s.replace('"', '""') + '"'
REC = "varRec"
def default_of(c):
    n = c["name"]
    if c["type"] in ("Text", "Note"): return f'Coalesce({REC}.{n}, "")'
    if c["type"] == "Number": return f'If(IsBlank({REC}.{n}), "", Text({REC}.{n}))'
    if c["type"] == "DateTime": return f'If(IsBlank({REC}.{n}), "", Text({REC}.{n}, "yyyy-mm-dd"))'
def value_of(c, ctl):
    n, t = c["name"], c["type"]
    if t in ("Text", "Note"): return f"{ctl}.Text"
    if t == "Number": return f"If(IsBlank({ctl}.Text), Blank(), Value({ctl}.Text))"
    if t == "DateTime": return f"If(IsBlank({ctl}.Text), Blank(), DateValue({ctl}.Text))"
    if t == "Boolean": return f'{ctl}.Selected.Value = "Yes"'
    if t == "Choice": return f"{{Value: {ctl}.Selected.Value}}"

out = []
LOAD = (f'IfError(ClearCollect(col{P}, ' + (f'Filter({LIST}, Active = true)' if HAS_ACTIVE else LIST) +
        f'), Notify("Could not load {LIST}: " & FirstError.Message, NotificationType.Error), true);\n'
        f'Set(var{P}Loaded, Now())')

# header
out.append(rect(f"{P}Hdr", DARK, 0, 0, 1920, 90))
out.append(label(f"{P}Brand", '"voyant"', 24, 6, 170, 52, size=34, color=WHITE, font="Georgia"))
out.append(label(f"{P}BrandSub", '"NEW ALBANY"', 27, 56, 170, 24, size=10, bold=True, color=TEAL))
out.append(label(f"{P}Title", q(TITLE_APP), 190, 20, 900, 50, size=24, bold=True, color=WHITE, font="Georgia"))
out.append(btn(f"{P}Refresh", '"REFRESH"', LOAD, 1600, 22, 140, 48, fill=TEAL, color=DARK, size=14))
out.append(btn(f"{P}New", '"+ NEW"', f"Set({REC}, Blank())", 1756, 22, 140, 48, fill=WHITE, color=DARK, size=14))

# left: search + list
out.append(ti(f"{P}Search", '""', 24, 110, 720, 52, "false", hint=q("search " + TITLE_DISP.lower()), size=16, number=False,
              extra={"Align": "=Align.Left"}))
sub = [c for c in form if c["name"] != "Title" and c["type"] in ("Text", "Choice", "DateTime", "Number")][:2]
def show(c):
    n, t = c["name"], c["type"]
    if t == "Choice": return f"ThisItem.{n}.Value"
    if t == "DateTime": return f'Text(ThisItem.{n}, "mmm d, yyyy")'
    if t == "Number": return f"Text(ThisItem.{n})"
    return f"ThisItem.{n}"
line2 = ' & "   ·   " & '.join(f'Coalesce({show(c)}, "")' for c in sub) or '""'
kids = [label(f"{P}GT", "ThisItem.Title", 16, 6, 680, 40, size=16, bold=True, color=DARK, indent=6),
        label(f"{P}GS", line2, 16, 46, 680, 30, size=12, color=G9, indent=6),
        btn(f"{P}GSel", '""', f"Set({REC}, ThisItem)", 0, 0, 712, 84, fill="RGBA(0, 0, 0, 0)", color="RGBA(0, 0, 0, 0)", indent=6,
            extra={"HoverFill": F("RGBA(0, 72, 81, 0.06)"), "BorderColor": F("RGBA(0, 0, 0, 0)")})]
gp = {"Items": F(f'SortByColumns(Search(col{P}, {P}Search.Text, Title), "Title")'), "TemplateSize": "=88", "TemplatePadding": "=2"}
gp.update(box(24, 176, 720, 880))
out.append(ctrl(f"{P}Gal", "Gallery@2.15.0", gp, 0, kids, variant="BrowseLayout_Vertical_TwoTextOneImageVariant_ver5.0"))
out.append(label(f"{P}Count", f'CountRows({P}Gal.AllItems) & " shown" & If(IsBlank(var{P}Loaded), "  ·  press REFRESH", "")',
                 24, 1056, 720, 22, size=10, color=G9))

# right: form
X = 780; W = 1116
out.append(rect(f"{P}Panel", "RGBA(248, 249, 249, 1)", X, 110, W, 950))
out.append(label(f"{P}Mode", f'If(IsBlank({REC}), "NEW {TITLE_DISP.upper()}", "EDIT: " & {REC}.Title)', X + 24, 120, W - 48, 44,
                 size=20, bold=True, color=DARK, font="Georgia"))
y = 180; ctls = []; left_out = []
for i, c in enumerate([{"name": "Title", "disp": TITLE_DISP, "type": "Text", "req": True}] + [c for c in form if c["name"] != "Title"]):
    ctl = f"{P}F{i}"
    h = 96 if c["type"] == "Note" else 52
    if y + 22 + h > 975: left_out.append(c["name"]); continue      # keep clear of the SAVE row
    out.append(cap(f"{P}C{i}", c["disp"].upper() + (" *" if c["req"] else ""), X + 24, y, 500))
    if c["type"] == "Boolean":
        out.append(dd(ctl, '["Yes", "No"]', X + 24, y + 22, 300, 52, default=f'If({REC}.{c["name"]}, "Yes", "No")'))
    elif c["type"] == "Choice":
        items = "[" + ", ".join(q(v) for v in c.get("choices", [])) + "]"
        out.append(dd(ctl, items, X + 24, y + 22, 520, 52, default=f'{REC}.{c["name"]}.Value'))
    else:
        extra = {"Align": "=Align.Left"}
        if c["type"] == "Note": extra["Mode"] = "=TextMode.MultiLine"
        hint = '"yyyy-mm-dd"' if c["type"] == "DateTime" else '""'
        out.append(ti(ctl, default_of(c), X + 24, y + 22, W - 48, h, "false", hint=hint, size=15, number=c["type"] == "Number", extra=extra))
    ctls.append((c, ctl)); y += 22 + h + 12

REQ = " && ".join(f"!IsBlank({ctl}.Text)" for c, ctl in ctls if c["req"] and c["type"] not in ("Boolean", "Choice")) or "true"
FIELDS = ", ".join(f'{c["name"]}: {value_of(c, ctl)}' for c, ctl in ctls)
SAVE = (f'If(!({REQ}), Notify("Fill in the fields marked *.", NotificationType.Warning),\n'
        f' IfError(Set({REC}, Patch({LIST}, If(IsBlank({REC}), Defaults({LIST}), LookUp({LIST}, ID = {REC}.ID)), {{{FIELDS}}})),\n'
        f'  Notify("Could not save: " & FirstError.Message, NotificationType.Error),\n'
        f'  Notify("Saved", NotificationType.Success); {LOAD}))')
out.append(btn(f"{P}Save", '"SAVE"', SAVE, X + W - 24 - 220, 990, 220, 56, fill=TEAL, color=DARK, size=16))
if HAS_ACTIVE:
    RET = (f'IfError(Patch({LIST}, LookUp({LIST}, ID = {REC}.ID), {{Active: false}}),\n'
           f'  Notify("Could not retire: " & FirstError.Message, NotificationType.Error),\n'
           f'  Set({REC}, Blank()); Notify("Retired (Active = No). Nothing was deleted.", NotificationType.Success); {LOAD})')
    out.append(btn(f"{P}Retire", '"RETIRE"', RET, X + 24, 990, 220, 56, fill=WHITE, color=DARK, size=16,
                   extra={"Visible": f"=!IsBlank({REC})"}))

EXTRA.setdefault(f"{P}Hdr", {})
os.makedirs(os.environ["MDI_OUTDIR"], exist_ok=True)
dst = os.path.join(os.environ["MDI_OUTDIR"], f"{LIST}_v1.pa.yaml")
write_themed(dst, "".join(out))
print("wrote", dst, f"({len(ctls)} inputs)")
skipped = [c for c in cols if c["name"] != "Active" and c["name"] not in [x["name"] for x, _ in ctls] and c["name"] != "Title"]
if left_out: print("Not on the form (no room; add a second screen or a scroll):", ", ".join(left_out))
print(f"Screen1.OnVisible: Select({P}Refresh)")
