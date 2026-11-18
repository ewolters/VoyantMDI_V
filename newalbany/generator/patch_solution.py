"""Patch generated flows into an unmanaged MDI solution zip and bump its version (the flow-change route).

    python3 newalbany/generator/make.py flows          # regenerate flow JSON into newalbany/build/flows first
    python3 newalbany/generator/patch_solution.py 1.1.4.2 1.1.4.3 "HxH - Downtime Escalation" [more flow names]

Reads  newalbany/solution/MDI_OhioContinuousImprovement_UNMANAGED_v<old>.zip
Writes newalbany/build/MDI_OhioContinuousImprovement_UNMANAGED_v<new>.zip

For each named flow it replaces the solution flow's triggers and actions with the generator's (newalbany/build/flows/),
re-pointed from the generator's sandbox site and list GUIDs to the solution's environment-variable parameters.
Everything else in the zip is copied byte for byte; solution.xml gets only the new <Version>.
Refuses if a flow needs a list the solution flow has no environment variable for, or if any sandbox reference is left.
First used for MDI 1.1.4.2 (2026-11-18); its output has the same content as the imported 1.1.4.2 zip (JSON key order can differ).
"""
import json, os, re, sys, zipfile, glob, copy

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)                      # newalbany/
sys.path.insert(0, HERE)
import flows as G                                  # generator: G.SITE, G.L (sandbox GUIDs)

STEM = "MDI_OhioContinuousImprovement_UNMANAGED_v"


def solution_flow_files(z):
    """Flow display name -> JSON entry name, from customizations.xml."""
    t = z.read("customizations.xml").decode("utf-8")
    out = {}
    for m in re.finditer(r'<Workflow [^>]*?\bName="([^"]+)"[^>]*>\s*<JsonFileName>/?([^<]+)</JsonFileName>', t):
        out[m.group(1)] = m.group(2)
    return out


def generated_flow(name):
    hits = [p for p in glob.glob(os.path.join(ROOT, "build", "flows", "*.json"))
            if re.sub(r"^\d+_", "", os.path.basename(p)[:-5]) == name]
    if len(hits) != 1:
        sys.exit(f"No generated flow named '{name}' in newalbany/build/flows (run make.py flows / flow-import first)")
    return json.load(open(hits[0], encoding="utf-8"))


def repoint(obj, site_param, list_params):
    guid_to_list = {v.lower(): k for k, v in G.L.items()}
    def walk(o):
        if isinstance(o, dict):
            r = {}
            for k, v in o.items():
                if k == "dataset" and v == G.SITE:
                    v = f"@parameters('{site_param}')"
                elif k == "table" and isinstance(v, str) and v.lower() in guid_to_list:
                    lst = guid_to_list[v.lower()]
                    if lst not in list_params:
                        sys.exit(f"Flow uses list {lst}, but the solution flow has no environment variable for it. "
                                 "Add it in MDI Dev first (or ask for help); not patched.")
                    v = f"@parameters('{list_params[lst]}')"
                else:
                    v = walk(v)
                r[k] = v
            return r
        if isinstance(o, list):
            return [walk(x) for x in o]
        return o
    return walk(obj)


def main():
    if len(sys.argv) < 4:
        sys.exit(__doc__)
    old, new, names = sys.argv[1], sys.argv[2], sys.argv[3:]
    src = os.path.join(ROOT, "solution", f"{STEM}{old}.zip")
    dst = os.path.join(ROOT, "build", f"{STEM}{new}.zip")
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    zi = zipfile.ZipFile(src)
    files = solution_flow_files(zi)
    patched = {}
    for name in names:
        if name not in files:
            sys.exit(f"Solution has no flow named '{name}'. Flows: {', '.join(sorted(files))}")
        entry = files[name]
        sol = json.loads(zi.read(entry).decode("utf-8"))
        gen = generated_flow(name)
        sd, gd = sol["properties"]["definition"], gen["properties"]["definition"]
        params = sd["parameters"]
        site_param = next(k for k in params if k.startswith("MDI SharePoint site"))
        list_params = {k.split(" (")[0]: k for k in params if " (craf4_" in k and not k.startswith("MDI SharePoint site")}
        before = set(sd["actions"])
        sd["triggers"] = repoint(gd["triggers"], site_param, list_params)
        sd["actions"] = repoint(gd["actions"], site_param, list_params)
        text = json.dumps(sol, ensure_ascii=False, indent=2)
        leftovers = [s for s in [G.SITE, *G.L.values()] if s.lower() in text.lower()]
        if leftovers:
            sys.exit(f"{name}: sandbox references left after re-pointing: {leftovers}. Not patched.")
        patched[entry] = text.encode("utf-8")
        after = set(sd["actions"])
        print(f"{name}: actions added {sorted(after - before) or '-'}, removed {sorted(before - after) or '-'}")
    with zipfile.ZipFile(dst, "w") as zo:
        for info in zi.infolist():
            data = zi.read(info)
            if info.filename == "solution.xml":
                t = data.decode("utf-8"); tag = f"<Version>{old}</Version>"
                if t.count(tag) != 1:
                    sys.exit(f"solution.xml doesn't have version {old}")
                data = t.replace(tag, f"<Version>{new}</Version>").encode("utf-8")
            elif info.filename in patched:
                data = patched[info.filename]
            zo.writestr(copy.copy(info), data, compress_type=info.compress_type)  # writestr mutates its ZipInfo
    zi = zipfile.ZipFile(src); zt = zipfile.ZipFile(dst)
    assert zt.testzip() is None and [i.filename for i in zt.infolist()] == [i.filename for i in zi.infolist()]
    changed = [n for n in zi.namelist() if zi.read(n) != zt.read(n)]
    print(f"wrote {dst}\nchanged entries: {changed}")


if __name__ == "__main__":
    main()
