"""Adds an OEE TARGETS panel to the Tier 2 msapp: header button -> panel with green/amber inputs -> saves MDI_Config T2_OEEGreen / T2_OEEAmber."""
import json, copy, re, uuid

SAVE = '''With({g: Value(txtCfgG.Text), a: Value(txtCfgA.Text)},
 If(IsBlank(g) || IsBlank(a) || g < 0 || g > 100 || a < 0 || a > g,
  Notify("Enter two numbers from 0 to 100, with amber at or below green.", NotificationType.Warning),
  Set(varCfgErr, false);
  If(IsError(Patch(MDI_Config, If(IsBlank(LookUp(MDI_Config, Title = "T2_OEEGreen")), Defaults(MDI_Config), LookUp(MDI_Config, Title = "T2_OEEGreen")),
     {Title: "T2_OEEGreen", SettingValue: Text(g), Kind: {Value: "Threshold"}})), Set(varCfgErr, true));
  If(IsError(Patch(MDI_Config, If(IsBlank(LookUp(MDI_Config, Title = "T2_OEEAmber")), Defaults(MDI_Config), LookUp(MDI_Config, Title = "T2_OEEAmber")),
     {Title: "T2_OEEAmber", SettingValue: Text(a), Kind: {Value: "Threshold"}})), Set(varCfgErr, true));
  If(varCfgErr,
   Notify("Could not save the OEE targets. Check that you can edit the MDI_Config list.", NotificationType.Error),
   Set(varCfg, false);
   Notify("OEE targets saved: green " & Text(g) & "%, amber " & Text(a) & "%", NotificationType.Success);
   Select(btnRefresh))))'''

NEW = [  # name, clone-from, {prop: script}
 ("btnCfg", "btnRefresh", {"X": "1436", "Y": "28", "Width": "76", "Height": "52", "Text": '"⚙ OEE"',
    "Tooltip": '"OEE targets: set the green and amber levels for the Cost / OEE tiles."',
    "OnSelect": "Set(varCfg, true); Reset(txtCfgG); Reset(txtCfgA)", "DisplayMode": "DisplayMode.Edit", "Visible": "true"}),
 ("ovCfgDim", "ovDim", {"Visible": "varCfg"}),
 ("ovCfgPanel", "ovPanel", {"X": "660", "Y": "300", "Width": "600", "Height": "420", "Visible": "varCfg"}),
 ("ovCfgHdr", "ovHdr", {"X": "660", "Y": "300", "Width": "600", "Height": "60", "Visible": "varCfg"}),
 ("ovCfgTitle", "ovTitle", {"X": "684", "Y": "300", "Width": "552", "Height": "60", "Text": '"OEE TARGETS  ·  TIER 2"', "Visible": "varCfg"}),
 ("ocCfgG", "ocA", {"X": "684", "Y": "384", "Width": "260", "Height": "20", "Text": '"GREEN AT OR ABOVE (%)"', "Visible": "varCfg"}),
 ("txtCfgG", "txtAAction", {"X": "684", "Y": "406", "Width": "260", "Height": "48", "Default": "Text(varOG)", "HintText": '"e.g. 65"',
    "Format": "TextFormat.Number", "Visible": "varCfg"}),
 ("ocCfgA", "ocA", {"X": "960", "Y": "384", "Width": "276", "Height": "20", "Text": '"AMBER AT OR ABOVE (%)"', "Visible": "varCfg"}),
 ("txtCfgA", "txtAAction", {"X": "960", "Y": "406", "Width": "276", "Height": "48", "Default": "Text(varOA)", "HintText": '"e.g. 50"',
    "Format": "TextFormat.Number", "Visible": "varCfg"}),
 ("ocCfgNote", "ocReq", {"X": "684", "Y": "478", "Width": "552", "Height": "120",
    "Text": '"Cost / OEE tiles: green at or above the green level, amber at or above the amber level, red below. Saved to MDI_Config (T2_OEEGreen, T2_OEEAmber), so every screen showing Tier 2 picks it up on its next refresh."',
    "Visible": "varCfg"}),
 ("btnCfgCancel", "btnACancel", {"X": "904", "Y": "646", "Width": "160", "Height": "52", "OnSelect": "Set(varCfg, false)", "Visible": "varCfg"}),
 ("btnCfgSave", "btnASave", {"X": "1076", "Y": "646", "Width": "160", "Height": "52", "Text": '"SAVE TARGETS"', "OnSelect": SAVE, "DisplayMode": "DisplayMode.Edit", "Visible": "varCfg"}),
]

def patch(controls_json: str, screen_yaml: str, identity_json: str):
    c = json.loads(controls_json); top = c["TopParent"]; kids = top["Children"]
    allc = []
    def walk(n):
        allc.append(n)
        for ch in n.get("Children", []): walk(ch)
    walk(top)
    byname = {n["Name"]: n for n in allc}
    assert not any(n in byname for n, _, _ in NEW), "panel already present"
    uid = max(int(n["ControlUniqueId"]) for n in allc)
    pub = max(n["PublishOrderIndex"] for n in allc)
    z = len(kids)
    # make room in the header
    for r in byname["lblLoaded"]["Rules"]:
        if r["Property"] == "Width": r["InvariantScript"] = "120"
    ident = json.loads(identity_json)
    yaml_add = []
    for name, src, props in NEW:
        n = copy.deepcopy(byname[src]); uid += 1; pub += 1; z += 1
        n["Name"] = name; n["ControlUniqueId"] = str(uid); n["PublishOrderIndex"] = pub; n["Parent"] = "Screen1"
        props = dict(props, ZIndex=str(z))
        have = {r["Property"]: r for r in n["Rules"]}
        for p, v in props.items():
            if p in have: have[p]["InvariantScript"] = v
            else:
                n["Rules"].append({"Property": p, "Category": "Design", "InvariantScript": v, "RuleProviderType": "Unknown"})
                if p not in n["ControlPropertyState"]: n["ControlPropertyState"].append(p)
        kids.append(n)
        ident[name] = str(uuid.uuid5(uuid.NAMESPACE_URL, "svend/mdi/xb/app/" + name))
        # YAML: copy the source control's block, swap name + overridden props
        m = re.search(r"\n(\s*)- " + re.escape(src) + r":\n(.*?)(?=\n\s*- [A-Za-z0-9_]+:\n|\Z)", screen_yaml, re.S)
        ind = m.group(1); block = m.group(2)
        ctl = re.search(r"Control: (\S+)", block).group(1)
        pr = dict(re.findall(r"\n?\s{4,}([A-Za-z]+): (=.*)", block.split("Properties:", 1)[1])) if "Properties:" in block else {}
        for p, v in props.items():
            if p == "ZIndex": continue
            pr[p] = "=" + v
        lines = [f"{ind}- {name}:", f"{ind}    Control: {ctl}", f"{ind}    Properties:"]
        for p in sorted(pr):
            v = pr[p]
            if "\n" in v or ": " in v or " #" in v: lines.append(f"{ind}      {p}: |-\n" + "\n".join(f"{ind}        {l}" for l in v.split("\n")))
            else: lines.append(f"{ind}      {p}: {v}")
        yaml_add.append("\n".join(lines))
    screen_yaml = screen_yaml.replace("\n            Width: =200\n            X: =1310", "\n            Width: =120\n            X: =1310", 1)
    screen_yaml = screen_yaml.rstrip("\n") + "\n" + "\n".join(yaml_add) + "\n"
    return json.dumps(c, separators=(",", ":")), screen_yaml, json.dumps(ident, separators=(",", ":"))
