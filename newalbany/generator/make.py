"""Regenerate app screens and flows from the generators.

    python3 newalbany/generator/make.py              # list targets
    python3 newalbany/generator/make.py hxh t2       # build some
    python3 newalbany/generator/make.py all          # build everything
    python3 newalbany/generator/make.py check        # build everything, compare with newalbany/deploy (screens + flows), lint the flows
    python3 newalbany/generator/make.py lint         # Power Fx checks on everything in newalbany/build/ (brackets, duplicates,
                                                     #   list-name typos, Set/Navigate inside ForAll)

Output goes to build/ (never straight into deploy/). Copy a file into deploy/apps under a new
version number once it has been pasted, published and tested in the MDI Dev environment.
"""
import os, sys, subprocess, filecmp, shutil

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GEN = os.path.join(ROOT, "generator")
OUT = os.path.join(ROOT, "build")
TMP = os.path.join(OUT, "tmp")
ENV = dict(os.environ, MDI_GEN=GEN, MDI_DEPLOY=os.path.join(ROOT, "deploy"), MDI_OUTDIR=OUT, MDI_TMP=TMP,
           PYTHONIOENCODING="utf-8", PYTHONUTF8="1")   # UTF-8 files on Windows too

# target: (what it builds, command line after "python")
TARGETS = {
    "hxh":      ("Tier 1 Hour x Hour  -> HxH_Board_v26.pa.yaml", ["build6.py"]),
    "t2":       ("Tier 2 daily board  -> T2_Board_v19.pa.yaml", ["t2v2.py"]),
    "t2periods":("Tier 2 WEEKS & MONTHS screen -> T2_Periods_v2.pa.yaml", ["t2per.py"]),
    "t3":       ("Tier 3 War Room board -> T3_Board_v9.pa.yaml", ["t3.py", "{OUT}/T3_Board_v9.pa.yaml"]),
    "t3screens":("Tier 3 Bowler + Variances screens", ["t3screens.py", "{OUT}/T3_Bowler_v6.pa.yaml", "{OUT}/T3_Variances_v7.pa.yaml"]),
    "quality":  ("Quality app: REWORK + NCR screens", ["quality.py", "{OUT}/Quality_v5.pa.yaml", "{OUT}/Quality_NCR_v2.pa.yaml"]),
    "qa":       ("QA Rework (standalone, older)", ["qa.py"]),
    "mt":       ("TS Maintenance", ["mt.py"]),
    "bd":       ("TS Binder", ["bd.py"]),
    "np":       ("Newspaper", ["np.py"]),
    "pc":       ("PC Audit", ["pc.py"]),
    "sw":       ("SW Manager", ["sw.py", "{OUT}/SW_Manager_v4.pa.yaml"]),
    "fa":       ("Frontier Audit", ["fa.py", "{OUT}/Frontier_Audit_v2.pa.yaml"]),
    "settings": ("MDI Settings: all screens incl. IMPORT HISTORY", ["settings_imp.py"]),
    "flows":    ("Flow JSON (HxH escalation, photo, sync, nightly, frontier)", ["flows.py", "{OUT}/flows"]),
    "flow-import": ("Flow JSON: MDI - Import History", ["flows/gen_import_flow.py", "{OUT}/flows/07_MDI - Import History.json"]),
    "flow-setup": ("Flow JSON: MDI - Set Up Site (creates every list in deploy/mdi_package.json)", ["flows/gen_setup_flow.py", "{OUT}/flows/00_MDI-SetUpSite.json"]),
    "flow-connect": ("Flow JSON: MDI - Connect Site (MDI2 code -> environment variables)", ["flows/gen_connect_flow.py", "{OUT}/flows/06_MDI-ConnectSite.json"]),
}

def run(name):
    desc, cmd = TARGETS[name]
    cmd = [sys.executable] + [os.path.join(GEN, cmd[0])] + [c.replace("{OUT}", OUT) for c in cmd[1:]]
    print(f"== {name}: {desc}")
    r = subprocess.run(cmd, cwd=GEN, env=ENV)
    if r.returncode:
        print(f"!! {name} failed (exit {r.returncode})"); return False
    return True

def check():
    """Every deployed screen and flow must be rebuilt byte-for-byte by the generators."""
    apps = os.path.join(ROOT, "deploy", "apps")
    flows = os.path.join(ROOT, "deploy", "flows", "json")
    alias = {"Settings_Thresholds_v2.pa.yaml": "Settings_scrCfg_v2.pa.yaml",
             "Settings_scrImport_v2.pa.yaml": "Settings_scrImport_v2.pa.yaml",
             **{f"Settings_{n}_v2.pa.yaml": f"Settings_{n}_v1.pa.yaml" for n in ("Dropdowns", "Escalation", "Lines", "People", "Standards")}}
    same = diff = 0; covered = set()
    for f in sorted(os.listdir(OUT)):
        if not f.endswith(".pa.yaml"): continue
        ref = os.path.join(apps, alias.get(f, f))
        if not os.path.exists(ref):
            if not f.startswith("_"):   # _*.pa.yaml are generator scratch files
                diff += 1; print("  NOT DEPLOYED  " + f + "   (built, but no such file in newalbany/deploy/apps: deleted, or a new version not copied in yet)")
            continue
        covered.add(alias.get(f, f))
        ok = filecmp.cmp(os.path.join(OUT, f), ref, shallow=False)
        same += ok; diff += not ok
        print(("  same  " if ok else "  DIFF  ") + f + ("" if alias.get(f, f) == f else f"  (vs {alias[f]})"))
    # deployed screens that no generator produced: a generator that failed, was renamed, or an old version left behind
    orphans = [f for f in sorted(os.listdir(apps)) if f.endswith(".pa.yaml") and f not in covered]
    for f in orphans: print("  NOT REBUILT  " + f + "   (no generator wrote it: failed generator, renamed output, or an old version to delete)")
    # flows the generators write, compared with deploy/flows/json, then linted
    fl_same = fl_diff = 0; fdir = os.path.join(OUT, "flows")
    for f in sorted(os.listdir(fdir)) if os.path.isdir(fdir) else []:
        ref = os.path.join(flows, f)
        if not f.endswith(".json") or not os.path.exists(ref): continue
        ok = filecmp.cmp(os.path.join(fdir, f), ref, shallow=False)
        fl_same += ok; fl_diff += not ok
        print(("  same  " if ok else "  DIFF  ") + "flow " + f)
    fl_bad = 0
    for f in sorted(os.listdir(flows)):
        if f.endswith(".json") and f != "catch_block.json":
            r = subprocess.run([sys.executable, os.path.join(GEN, "lint", "flowlint.py"), os.path.join(flows, f)], env=ENV, capture_output=True, text=True)
            if r.returncode: fl_bad += 1; print("  FLOW LINT  " + r.stdout.strip())
    sp = subprocess.run([sys.executable, os.path.join(GEN, "setup_package.py"), "check"], env=ENV, capture_output=True, text=True)
    print("  " + sp.stdout.strip())
    print(f"{same} identical, {diff} different" + (f", {len(orphans)} not rebuilt" if orphans else "")
          + f"; flows {fl_same} identical, {fl_diff} different" + (f", {fl_bad} fail lint" if fl_bad else ", lint clean"))
    return diff == 0 and not orphans and fl_diff == 0 and fl_bad == 0 and sp.returncode == 0

if __name__ == "__main__":
    os.makedirs(TMP, exist_ok=True); os.makedirs(os.path.join(OUT, "flows"), exist_ok=True)
    args = sys.argv[1:]
    if not args:
        print(__doc__); [print(f"  {k:10} {v[0]}") for k, v in TARGETS.items()]; sys.exit(0)
    if args[0] == "lint":
        bad = 0
        for f in sorted(os.listdir(OUT)):
            if f.endswith(".pa.yaml"):
                for tool in ("fxcheck.py", "dupcheck.py", "sources.py"):
                    r = subprocess.run([sys.executable, os.path.join(GEN, "lint", tool), os.path.join(OUT, f)], env=ENV, capture_output=True, text=True)
                    last = (r.stdout.strip().splitlines() or [""])[-1]
                    print(f"  {f:40} {tool:12} {last}")
                    bad += r.returncode != 0
        sys.exit(1 if bad else 0)
    names = list(TARGETS) if args[0] in ("all", "check") else args
    if args[0] == "check":   # start clean, so a generator that fails can't hide behind last run's output
        for f in os.listdir(OUT):
            if f.endswith(".pa.yaml"): os.remove(os.path.join(OUT, f))
        shutil.rmtree(os.path.join(OUT, "flows"), ignore_errors=True); os.makedirs(os.path.join(OUT, "flows"))
    bad = [n for n in names if n not in TARGETS]
    if bad: sys.exit(f"unknown target(s): {bad}")
    ok = all([run(n) for n in names])
    if args[0] == "check": ok = check() and ok
    sys.exit(0 if ok else 1)
