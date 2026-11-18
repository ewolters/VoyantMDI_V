"""Rebuild the MDI Setup solution zip (the installer flow 'MDI - Set Up Site') from deploy/mdi_package.json.

Use after adding or changing a list in newalbany/deploy/mdi_package.json. The Set Up Site flow carries the whole
list schema inside it, so a new list only reaches SharePoint once this package is rebuilt, imported and run.

    python3 newalbany/generator/setup_package.py 1.0.0.1      -> newalbany/build/MDISetup_UNMANAGED_v1.0.0.1.zip
    python3 newalbany/generator/setup_package.py check        rebuild 1.0.0.0 and compare with the shipped zip

Inputs: the newest newalbany/solution/MDISetup_UNMANAGED_*.zip (template: publisher Cr21560/craf4, connection
references) and the flow written by generator/flows/gen_setup_flow.py. Only the flow JSON and the version change.
"""
import glob, io, json, os, re, subprocess, sys, zipfile

GEN = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(GEN)
OUT = os.path.join(ROOT, "build")
REFS = {"__REF_SP__": "craf4_sharedsharepointonline_17d15", "__REF_O365__": "craf4_sharedoffice365_mdi"}

def vt(v): return tuple(int(x) for x in v.split("."))
zips = sorted(glob.glob(os.path.join(ROOT, "solution", "MDISetup_UNMANAGED_v*.zip")),
              key=lambda z: vt(re.search(r"_v([\d.]+)\.zip$", z).group(1)))
if not zips: sys.exit("missing newalbany/solution/MDISetup_UNMANAGED_v*.zip; restore it from git")
TEMPLATE = zips[-1]
SHIPPED_V = re.search(r"_v([\d.]+)\.zip$", TEMPLATE).group(1)

def flow_json():
    os.makedirs(os.path.join(OUT, "tmp"), exist_ok=True)
    f = os.path.join(OUT, "tmp", "setup_flow.json")
    env = dict(os.environ, MDI_DEPLOY=os.path.join(ROOT, "deploy"), MDI_TMP=os.path.join(OUT, "tmp"), PYTHONUTF8="1")
    subprocess.run([sys.executable, os.path.join(GEN, "flows", "gen_setup_flow.py"), f], check=True, env=env, capture_output=True)
    s = open(f, encoding="utf-8").read()
    for k, v in REFS.items(): s = s.replace(k, v)
    return json.loads(s)

def build(version):
    zin = zipfile.ZipFile(TEMPLATE)
    wf = [n for n in zin.namelist() if n.startswith("Workflows/") and n.endswith(".json")]
    assert len(wf) == 1, wf
    old = json.loads(zin.read(wf[0]))
    new = flow_json()
    for k in ("templateName",):                       # properties Power Automate adds on export; keep them
        if k in old["properties"]: new["properties"][k] = old["properties"][k]
    buf = io.BytesIO(); zout = zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED)
    for n in zin.namelist():
        b = zin.read(n)
        if n == wf[0]: b = json.dumps(new, separators=(",", ":")).encode("utf-8")
        if n == "solution.xml": b = re.sub(rb"<Version>[^<]+</Version>", f"<Version>{version}</Version>".encode(), b, count=1)
        zout.writestr(n, b)
    zout.close()
    os.makedirs(OUT, exist_ok=True)
    dst = os.path.join(OUT, f"MDISetup_UNMANAGED_v{version}.zip")
    open(dst, "wb").write(buf.getvalue())
    return dst, old, new

if __name__ == "__main__":
    a = sys.argv[1:]
    if not a: print(__doc__); sys.exit(0)
    if a[0] == "check":
        _, old, new = build(SHIPPED_V)
        same = old == new
        print(f"setup package: flow in {os.path.basename(TEMPLATE)} " + ("matches deploy/mdi_package.json + the generator" if same else
              "DIFFERS from what the generator builds now (mdi_package.json changed since that zip was made: rebuild with a new version)"))
        sys.exit(0 if same else 1)
    v = a[0]
    if not re.fullmatch(r"\d+\.\d+\.\d+\.\d+", v): sys.exit(f"version must look like 1.0.0.1, not {v!r}")
    if vt(v) <= vt(SHIPPED_V): sys.exit(f"version {v} must be higher than the shipped {SHIPPED_V}")
    dst, _, new = build(v)
    names = new["properties"]["definition"]["actions"]["PKG"]["inputs"]["names"] if isinstance(new["properties"]["definition"]["actions"].get("PKG", {}).get("inputs"), dict) else []
    print("wrote", dst, f"({len(names)} lists)" if names else "")
