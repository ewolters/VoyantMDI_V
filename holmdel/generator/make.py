"""Rebuild the Holmdel Tier 2 package (MDI Tier 2 - Excel boards (no lists)).

    python3 holmdel/generator/make.py check     rebuild 1.0.0.19 and compare with the shipped zip, and
                                                compare deploy/Tier2_XB_v7.pa.yaml with the shipped app
    python3 holmdel/generator/make.py 1.0.0.20  build a new MANAGED package (flows + script from this folder,
                                                app from APP_SOURCE below) -> holmdel/build/
    python3 holmdel/generator/make.py 1.0.0.20 unmanaged
                                                same, but UNMANAGED, for importing into a dev environment
                                                so the app can be edited in Studio
    python3 holmdel/generator/make.py 1.0.0.21 managed path/to/export.zip
                                                managed package using the app from a dev export

Inputs, all in the repo:
  holmdel/deploy/ReadProductionBoard.ts   board-reading Office Script (embedded in the sync flow)
  holmdel/deploy/Tier2_XB_v7.pa.yaml      the app screen source (matches the shipped app)
  holmdel/generator/flows.py              writes the two flow definitions + environment variables
  newalbany/solution/MDISetup_UNMANAGED_*.zip   solution skeleton only (publisher Cr21560 / craf4;
                                          no New Albany components are taken from it)
  APP_SOURCE                       a solution zip that contains the compiled canvas app
"""
import os, sys, glob, subprocess, zipfile, io

GEN = os.path.dirname(os.path.abspath(__file__))
HERE = os.path.dirname(GEN)                      # holmdel/
REPO = os.path.dirname(HERE)
OUT = os.path.join(HERE, "build")
TEMPLATE = sorted(glob.glob(os.path.join(REPO, "newalbany", "solution", "MDISetup_UNMANAGED_*.zip")))[-1]
SHIPPED = os.path.join(HERE, "solution", "MDI_Tier2_ExcelBoards_NoLists_1.0.0.19_managed.zip")
APP_YAML = os.path.join(HERE, "deploy", "Tier2_XB_v7.pa.yaml")
# The compiled app. To ship app changes: edit the app in a dev environment, export that solution
# (unmanaged), and point APP_SOURCE at the export (or pass it as the 3rd argument).
APP_SOURCE = SHIPPED
ENV = dict(os.environ, PYTHONUTF8="1")

def build(version, unmanaged=False, app=None):
    os.makedirs(os.path.join(OUT, "flows"), exist_ok=True)
    py = sys.executable
    subprocess.run([py, os.path.join(GEN, "flows.py"), os.path.join(HERE, "deploy", "ReadProductionBoard.ts"),
                    os.path.join(OUT, "flows")], check=True, env=ENV)
    lint = subprocess.run([py, os.path.join(GEN, "lint2.py")] + [os.path.join(OUT, "flows", f) for f in ("sync.json", "appdata.json")],
                          env=ENV, capture_output=True, text=True)
    print(lint.stdout.strip())
    if lint.returncode or "clean" not in lint.stdout: sys.exit("flow lint failed; fix before importing")
    kind = "unmanaged" if unmanaged else "managed"
    dst = os.path.join(OUT, f"MDI_Tier2_ExcelBoards_NoLists_{version}_{kind}.zip")
    subprocess.run([py, os.path.join(GEN, "build.py"), TEMPLATE, os.path.join(OUT, "flows"), dst, version,
                    app or APP_SOURCE], check=True, env=ENV)
    if unmanaged:
        zin = zipfile.ZipFile(dst); buf = io.BytesIO(); zout = zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED)
        for n in zin.namelist():
            b = zin.read(n)
            if n == "solution.xml": b = b.replace(b"<Managed>1</Managed>", b"<Managed>0</Managed>")
            zout.writestr(n, b)
        zout.close(); zin.close(); open(dst, "wb").write(buf.getvalue())
    print("wrote", dst)
    return dst

def app_yaml_diffs():
    """Compare every control property in APP_YAML with the app inside the shipped zip.
    Studio drops properties left at their default (X: =0, Align: =Align.Left, ...), so only
    properties present on both sides are compared."""
    import yaml, re
    z = zipfile.ZipFile(SHIPPED)
    msapp = zipfile.ZipFile(io.BytesIO(z.read([n for n in z.namelist() if n.endswith(".msapp")][0])))
    src = [n for n in msapp.namelist() if n.replace("\\", "/").endswith("Src/Screen1.pa.yaml")][0]
    def props(doc):
        out = {}
        def walk(items):
            for it in items or []:
                (name, c), = it.items()
                for k, v in (c.get("Properties") or {}).items():
                    out[f"{name}.{k}"] = re.sub(r"\s+", "", str(v).lstrip("="))
                walk(c.get("Children"))
        walk(doc["Screens"]["Screen1"].get("Children") if isinstance(doc, dict) else doc)
        return out
    shipped = props(yaml.safe_load(msapp.read(src).decode("utf-8-sig")))
    mine = props(yaml.safe_load(open(APP_YAML, encoding="utf-8")))
    return [k for k in mine if k in shipped and mine[k] != shipped[k]], len(mine)

if __name__ == "__main__":
    a = sys.argv[1:]
    if not a:
        print(__doc__); sys.exit(0)
    if a[0] == "check":
        dst = build("1.0.0.19")
        new, old = zipfile.ZipFile(dst), zipfile.ZipFile(SHIPPED)
        diffs = []
        for n in sorted(set(new.namelist()) | set(old.namelist())):
            x = new.read(n) if n in new.namelist() else None
            y = old.read(n) if n in old.namelist() else None
            if x != y:
                # the platform version stamp in the header line differs by template; ignore that line only
                if x and y and x.split(b"\n", 1)[-1] == y.split(b"\n", 1)[-1]: continue
                diffs.append(n)
        print("package: identical to the shipped 1.0.0.19 (apart from the platform version stamp)" if not diffs else f"package DIFFERENT: {diffs}")
        ad, n = app_yaml_diffs()
        print(f"app source: {os.path.basename(APP_YAML)} matches the shipped app ({n} properties)" if not ad else f"app source DIFFERENT: {ad[:20]}")
        sys.exit(1 if diffs or ad else 0)
    build(a[0], unmanaged=len(a) > 1 and a[1] == "unmanaged", app=a[2] if len(a) > 2 else None)
