"""Builds the unbranded MDI template: generic mdi_package.json + provision_mdi.js.txt with sample beverage-plant data.
Apps come from the generators run with MDI_THEME=neutral MDI_OUTDIR=<G>/apps."""
import json, re, os, sys, importlib.util
G = sys.argv[1]
SRC = __import__("os").environ["MDI_DEPLOY"]
spec = importlib.util.spec_from_file_location("theme", __import__("os").environ["MDI_GEN"]+"/theme.py")
T = importlib.util.module_from_spec(spec); os.environ["MDI_THEME"] = "neutral"; spec.loader.exec_module(T)

p = json.load(open(f"{SRC}/mdi_package.json"))
p["exportedFrom"] = "MDI template"; p["exportedAt"] = "2026-10-21"

# Lines
p["seed"]["Lines"] = [{"Title": t, "ValueStream": vs, "DisplayOrder": (i + 1) * 10, "Active": True}
                      for i, (t, vs) in enumerate([("CAN-1", "Cans"), ("CAN-2", "Cans"), ("PET-1", "Bottles"), ("PET-2", "Bottles"), ("GLASS-1", "Glass")])]

# PLAYBOOK: sample rates. Rate = units/min at standard. All fields from the schema kept; headcount/changeover are examples.
tmpl = {k: (0 if isinstance(v, (int, float)) and not isinstance(v, bool) else None) for k, v in p["seed"]["PLAYBOOK"][0].items()}
def pb(line, size, form, rate, hc, sched):
    r = dict(tmpl); r.update({"Title": f"{line}|{size}|{form}", "Line": line, "Size": size, "Form": form, "BoxMakerNote": None,
        "CO_CriticalCleaning": "8 hrs (sanitation)", "RateBPM": rate, "FinancialStdRate": round(rate * 0.85), "OEMStdRate": rate,
        "HC_LineLead": 1, "HC_FillerOp": 1, "HC_CasePackOp": 1, "HC_Packer": hc, "HC_Palletizer": 1, "HC_Inspector": 1,
        "AvailableHrsShift": 7.5, "CO_Flush": 0.5, "CO_CapChange": 0.5, "CO_PackSize": 1, "CO_Format": 2, "CO_Sanitation": 4,
        "CO_BatchChange": 0.25, "ScheduledUnitsShift": sched, "EfficiencyTarget": 0.85, "Active": True})
    return r
p["seed"]["PLAYBOOK"] = [
    pb("CAN-1", "12 oz can", "12-pack", 1200, 1, 459000), pb("CAN-1", "12 oz can", "24-pack", 1200, 1, 459000),
    pb("CAN-2", "16 oz can", "4-pack", 900, 2, 344000), pb("PET-1", "20 oz PET", "24-case", 600, 1, 229000),
    pb("PET-2", "2 L PET", "8-case", 220, 1, 84000), pb("GLASS-1", "12 oz glass", "24-case", 500, 2, 191000)]

# Lookups: drop the one product-specific reason
for r in p["seed"]["Lookups"]:
    if r["Title"] == "Tube Seal": r["Title"] = "Seam / Seal"

# MDI_Config notes
for r in p["seed"]["MDI_Config"]:
    if r["Title"] == "Site_URL": r["Notes"] = "This site's URL (the list setup fills it in)"

s = json.dumps(p, ensure_ascii=False, separators=(",", ":"))
s = s.replace("Source: New Albany Downtime Escalation Plan Rev 1.", "Fill in from the plant's escalation plan.")
s = s.replace("Source: Playbook_Summary_Current.xlsx Overview (Table1). ", "Rate = units/min at standard; headcount and changeover hours per item. ")
s = s.replace("Partition Placer (211 and 209)", "Partition Placer").replace("FZ-NAL-", "FZ-P14-")
s = T.apply_theme(s, "neutral")
json.loads(s)
open(f"{G}/mdi_package.json", "w").write(json.dumps(json.loads(s), indent=1, ensure_ascii=False))

js = open(f"{SRC}/provision_mdi.js.txt").read().split("\n")
assert js[8].startswith("  const PKG = ")
js[8] = "  const PKG = " + s.replace("https://", "https:\\/\\/") + ";"
out = T.apply_theme("\n".join(js), "neutral")
out = re.sub(r"Exported from: \S+", "Exported from: MDI template", out).replace("/sites/NewAlbanyMDI", "/sites/PlantMDI")
open(f"{G}/provision_mdi.js.txt", "w").write(out)
print("ok", len(out))
