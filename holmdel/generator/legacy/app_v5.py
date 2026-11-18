"""Tier 2 app, v5 on top of v4: the calendar's LATEST preset becomes TODAY (today's date, even if boards are still filling in).
Usage: python3 app_v5.py Tier2_XB_v4.pa.yaml Tier2_XB_v5.pa.yaml
"""
import sys, yaml
src, dst = sys.argv[1], sys.argv[2]
y = open(src, encoding="utf-8").read()
a = y.index("- calPL:\n"); b = y.index("\n- ", a + 3)
blk = y[a:b]
old_t, new_t = '="LATEST"', '="TODAY"'
old_o = "=Set(varTmpFrom, varD0); Set(varTmpTo, varD0);"
new_o = "=Set(varTmpFrom, Today()); Set(varTmpTo, Today());"
assert blk.count(old_t) == 1 and blk.count(old_o) == 1
blk = blk.replace(old_t, new_t).replace(old_o, new_o)
y = y[:a] + blk + y[b:]
open(dst, "w", encoding="utf-8").write(y)
yaml.safe_load(open(dst, encoding="utf-8"))
print("ok")
