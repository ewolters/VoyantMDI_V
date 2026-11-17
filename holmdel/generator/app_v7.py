"""Tier 2 app, v7 on top of v6: the two day-by-day charts become horizontal galleries.
A vertical gallery's WrapCount stops at 10, so a 30-day chart only drew its first 10 days (ending on the 9th).
Horizontal gallery: one day per template column, TemplateSize = chart width / days.
Usage: python3 app_v7.py Tier2_XB_v6.pa.yaml Tier2_XB_v7.pa.yaml
"""
import sys, re, yaml
src, dst = sys.argv[1], sys.argv[2]
y = open(src, encoding="utf-8").read()
TW = "Max(1, Coalesce(varTW, 30))"
for g, w in (("galTr", 1712), ("galO2", 830)):
    a = y.index(f"\n- {g}:\n") + 1; b = y.index("    Children:\n", a)
    blk = y[a:b]
    for old, new in [("    Variant: BrowseLayout_Vertical_TwoTextOneImageVariant_ver5.0\n", "    Variant: BrowseLayout_Horizontal_TwoTextOneImageVariant_ver5.0\n"),
                     (f"      WrapCount: |-\n        ={TW}\n", ""),
                     ("      TemplateSize: |-\n        =248\n", f"      TemplateSize: |-\n        ={w} / {TW}\n")]:
        assert blk.count(old) == 1, (g, old)
        blk = blk.replace(old, new)
    y = y[:a] + blk + y[b:]
open(dst, "w", encoding="utf-8").write(y)
doc = yaml.safe_load(open(dst, encoding="utf-8"))
print("ok")
