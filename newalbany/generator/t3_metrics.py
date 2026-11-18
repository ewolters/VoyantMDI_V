# Tier 3 metric library. Each SQDCP letter holds several metrics. The KPI_Metrics list (catalog) switches metrics on/off,
# orders them and sets thresholds; the CALCULATION of each metric lives here (Power Apps can't run formulas stored in a list).
# Variables available inside a metric (sums over the window): pt plan, effw PLAYBOOK eff x target, t target, a actual, o OEE x target,
# sh shifts, sc scrap, ca/cs crew actual/std, dt downtime min, rw rework, sf board safety events, fz audit hazards, fch C/H hazards,
# fa audits done, dte downtime events, escl max escalation level, pcd/pcx/pcf PC done/due/failed, nd days in the window.
LETTERS = ["S", "Q", "D", "C", "P"]
LNAME = {"S": "SAFETY", "Q": "QUALITY", "D": "DELIVERY", "C": "COST", "P": "PEOPLE"}
LCAT = {"S": "Safety", "Q": "Quality", "D": "Delivery", "C": "Cost", "P": "People"}
# code, letter, name, short, unit, better(H/L), green, amber, has, value, text, status override (uses GEN for the generic rule) or None
MET = [
 ("SAF_EVENTS", "S", "Board safety events", "Events", "events", "L", 0, 0, 'sh > 0 || sf > 0', 'sf', 'If(sf = 0, "✓ none", Text(sf))', None),
 ("SAF_HAZ", "S", "Safety-audit hazards", "Hazards", "hazards", "L", 0, 99, 'fa > 0 || fz > 0', 'fz', 'Text(fz) & If(fch > 0, " · " & fch & " C/H", "")', 'If(fch > 0, "R", GEN)'),
 ("SAF_AUD", "S", "Safety audits completed", "Audits", "audits / week", "H", 5, 3, 'sh > 0 || fa > 0', 'fa / Max(nd, 1) * 7', 'Text(fa) & If(fa = 1, " audit", " audits")', None),
 ("QUAL_RW", "Q", "Rework", "Rework", "% of units", "L", 0.5, 2, 'a > 0', 'rw / a * 100', 'Text(rw / a * 100, "0.0") & "%"', None),
 ("QUAL_SCRAP", "Q", "Scrap", "Scrap", "% of units", "L", 0.5, 1, 'a + sc > 0', 'sc / (a + sc) * 100', 'Text(sc / (a + sc) * 100, "0.00") & "%"', None),
 ("QUAL_NCR", "Q", "NCRs", "NCRs", "NCRs", "L", 0, 1, 'false', '0', '"not yet collected"', None),
 ("DEL_ATT", "D", "Attainment to plan", "Attain", "% of plan", "H", 90, 80, 'pt > 0', 'a / pt * 100', 'Text(a / pt * 100, "0") & "%"', None),
 ("DEL_DT", "D", "Unplanned downtime", "Down", "min / shift", "L", 30, 60, 'sh > 0', 'dt / sh', 'Text(dt / sh, "0") & " min/sh"', 'If(escl > 0, "R", GEN)'),
 ("DEL_DTE", "D", "Downtime events", "Events", "events / shift", "L", 1, 2, 'sh > 0', 'dte / sh', 'Text(dte) & If(dte = 1, " event", " events")', None),
 ("COST_OEE", "C", "OEE", "OEE", "%", "H", 65, 50, 't > 0', 'o / t * 100', 'Text(o / t * 100, "0") & "%"', 'OEEST'),
 ("COST_SPEED", "C", "Speed loss", "Speed", "% below target rate", "L", 5, 10, 't > 0', 'Max(t - a, 0) / t * 100', 'Text(Max(t - a, 0) / t * 100, "0.0") & "%"', None),
 ("PEO_CREW", "P", "Crew vs standard", "Crew", "% of standard", "H", 100, 100, 'cs > 0', 'ca / cs * 100', 'Text(ca / cs * 100, "0") & "%"', 'If(ca < cs, "R", ca > cs, "A", "G")'),
 ("PEO_PC", "P", "Process confirmation", "PC", "% done", "H", 90, 75, 'pcx > 0', 'pcd / pcx * 100', 'Text(pcd) & " / " & Text(pcx)', None),
]
CODES = [m[0] for m in MET]
TIPM = {
 "SAF_EVENTS": "Safety events flagged on the hour-by-hour boards (near misses, incidents).",
 "SAF_HAZ": "Hazards found in safety audits (at-risk/unsafe items, 5S findings marked as hazards). Red = any Critical/High.",
 "SAF_AUD": "Safety audits completed, as a weekly rate against the target per week.",
 "QUAL_RW": "Rework units (QA Rework app) as % of units produced.",
 "QUAL_SCRAP": "Finished-goods scrap as % of units made (good + scrap).",
 "QUAL_NCR": "Nonconformance reports. Collected by the NCR app (coming).",
 "DEL_ATT": "Actual units / PLAYBOOK plan (rate x run hours).",
 "DEL_DT": "Unplanned downtime minutes per shift. Red = an escalation fired.",
 "DEL_DTE": "Downtime events per shift (one line, shift and reason).",
 "COST_OEE": "OEE weighted by target; target = PLAYBOOK efficiency when set.",
 "COST_SPEED": "Units short of the board target rate, as %.",
 "PEO_CREW": "Actual crew vs PLAYBOOK standard crew. Red = short, amber = over.",
 "PEO_PC": "Process-confirmation audits done vs due.",
}
def default_catalog_fx():
    """Power Fx table literal used when the KPI_Metrics list is empty (same schema as the loaded catalog)."""
    rows = []
    for i, (c, L, n, sh, u, b, g, am, *_r) in enumerate(MET):
        rows.append(f'{{Code: "{c}", Ltr: "{L}", Nm: "{n}", Sh: "{sh}", Un: "{u}", Hi: {"true" if b == "H" else "false"}, Gr: {g}, Am: {am}, Ord: {(i + 1) * 10}}}')
    return "Table(" + ", ".join(rows) + ")"
def catalog_seed_rows():
    return [{"Title": c, "Letter": L, "MetricName": n, "Short": sh, "Unit": u, "Better": "Higher" if b == "H" else "Lower",
             "Green": g, "Amber": am, "DisplayOrder": (i + 1) * 10, "Active": True, "Notes": TIPM[c]}
            for i, (c, L, n, sh, u, b, g, am, *_r) in enumerate(MET)]

def AGGM(tbl, extra, nd="1"):
    """aggregate daily rows -> one record: per-metric v_/t_/s_/g_/h_ fields + per-letter st/txt/sub (worst status, headline, summary)"""
    sums = ('pt: Sum(rs, Plan), effw: Sum(rs, EffW), t: Sum(rs, Tgt), a: Sum(rs, Act), o: Sum(rs, OEEw), sh: Sum(rs, Shifts), sc: Sum(rs, Scrap), '
            'ca: Sum(rs, CrewA), cs: Sum(rs, CrewS), dt: Sum(rs, DT), rw: Sum(rs, RW), sf: Sum(rs, Saf), fz: Sum(rs, Fz), fch: Sum(rs, Fch), fa: Sum(rs, FA), '
            'dte: Sum(rs, DTe), escl: Coalesce(Max(rs, EscL), 0), pcd: Sum(rs, PCd), pcx: Sum(rs, PCx), pcf: Sum(rs, PCf)')
    ths = ", ".join(f'th_{c}: LookUp(colMet, Code = "{c}")' for c in CODES)
    has = ", ".join(f'h_{m[0]}: !IsBlank(th_{m[0]}) && ({m[8]})' for m in MET)
    vals = ", ".join(f'v_{m[0]}: If(h_{m[0]}, {m[9]}, 0)' for m in MET)
    parts = []
    for (c, L, n, sh_, u, b, g, am, hs, vx, tx, ov) in MET:
        GEN = f'If(th_{c}.Hi, If(v_{c} >= th_{c}.Gr, "G", v_{c} >= th_{c}.Am, "A", "R"), If(v_{c} <= th_{c}.Gr, "G", v_{c} <= th_{c}.Am, "A", "R"))'
        if ov == 'OEEST':
            gr = f'If(effw > 0, effw / t * 100, th_{c}.Gr)'
            st = f'If(v_{c} >= {gr}, "G", v_{c} >= {gr} - (th_{c}.Gr - th_{c}.Am), "A", "R")'
            gl = f'If(h_{c}, {gr}, -1)'
        else:
            st = ov.replace("GEN", GEN) if ov else GEN
            gl = f'If(h_{c}, th_{c}.Gr, -1)'
        parts.append(f't_{c}: If(IsBlank(th_{c}), "", h_{c}, {tx}, {'"not yet collected"' if c == "QUAL_NCR" else '"—"'}), s_{c}: If(h_{c}, {st}, "N"), g_{c}: {gl}')
    lets = []
    for L in LETTERS:
        cs_ = [m[0] for m in MET if m[1] == L]
        z = " & ".join(f's_{c}' for c in cs_)
        tb = "Table(" + ", ".join(f'{{o: Coalesce(th_{c}.Ord, 0), x: th_{c}.Sh & " " & t_{c}, tv: t_{c}, a: !IsBlank(th_{c})}}' for c in cs_) + ")"
        lets.append(f'st{L}: With({{z: {z}}}, If("R" in z, "R", "A" in z, "A", "G" in z, "G", "N")), '
                    f'txt{L}: With({{q: SortByColumns(Filter({tb}, a), "o", SortOrder.Ascending)}}, If(CountRows(q) = 0, "—", First(q).tv)), '
                    f'sub{L}: Concat(SortByColumns(Filter({tb}, a), "o", SortOrder.Ascending), x, "  ·  ")')
    s = ('With({rs: ' + tbl + ', nd: ' + nd + '},\n With({' + sums + '},\n With({' + ths + '},\n With({' + has + '},\n With({' + vals + '},\n With({' + ", ".join(parts) + '},\n'
         '  {' + extra + ', ' + ", ".join(f'v_{c}: v_{c}, t_{c}: t_{c}, s_{c}: s_{c}, g_{c}: g_{c}' for c in CODES) + ',\n   ' + ",\n   ".join(lets) + '}))))))')
    return s

# number format for the bowler's target / actual / variance lines (value v_ is the numeric form of each metric)
FMT = {"SAF_EVENTS": "0", "SAF_HAZ": "0", "SAF_AUD": "0.0", "QUAL_RW": "0.0", "QUAL_SCRAP": "0.00", "QUAL_NCR": "0",
       "DEL_ATT": "0", "DEL_DT": "0", "DEL_DTE": "0.0", "COST_OEE": "0", "COST_SPEED": "0.0", "PEO_CREW": "0", "PEO_PC": "0"}
