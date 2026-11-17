"""Rewrites the PKG line (line 9) of deploy/provision_mdi.js(.txt) from deploy/mdi_package.json."""
import json
D = "/mnt/user-data/outputs/deploy/"
p = json.load(open(D + "mdi_package.json"))
s = json.dumps(p, ensure_ascii=False, separators=(",", ":"))
for f, esc in (("provision_mdi.js.txt", True), ("provision_mdi.js", False)):
    js = open(D + f).read().split("\n")
    assert js[8].startswith("  const PKG = "), f
    js[8] = "  const PKG = " + (s.replace("https://", "https:\\/\\/") if esc else s) + ";"
    open(D + f, "w").write("\n".join(js))
print("ok", len(s))
