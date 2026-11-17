/**
 * ReadProductionBoard  -  Office Script, deployed and called by the flow "MDI XB - Sync Excel Boards".
 *
 * Reads ONE Holmdel Tier 1 board ("<n>. Production Board <Month>", .xlsm or .xlsx: one tab per day,
 * two 8-hour shift blocks per tab) and returns one compact record per day x shift for Tier 2.
 * Read-only: it never writes to the board, so it is safe while a line lead has it open.
 *
 * Sheet geometry (1st shift / 2nd shift block; 2nd = 1st + 29 rows):
 *   row 2 / 31          A = W/O, B = Line Lead, C = Date, D = Line #, E = Description
 *   row 4 / 33          A = Stnd Hr Units, B = Stnd Crew, C = Stnd Speed, D = Act Crew, E = Act Speed, F = Target
 *   rows 6-13 / 35-42   hour 1-8: B units, C accumulated, E comment
 *                       O DT Min(1), P DT Code(1), Q DT Min(2), R DT Code(2)  <- optional per-hour downtime
 *   rows 17-27 / 46-56  A downtime reason, B minutes | C scrap item, D qty
 *   rows 18-20 / 47-49  E safety type (Near Miss / First Aid / Recordable), F qty
 * If the day tabs change layout, this script is the only thing to update.
 *
 * Record fields (short names keep the data file small):
 *   k key Line-yyyymmdd-S#, l line, d date yyyy-MM-dd, s shift, wo, lead, prod
 *   ht hourly target, tgt shift target (ht x 8), act units, h hourly units "130,119,,..."
 *   oee  the board's own "OEE Actual %" (H18 / H47) when it calculates; else A x P x Q from the speeds
 *   a/p/q  availability / performance / quality from the speeds (blank if speeds missing)
 *   dt downtime min (all rows, as the board totals them), dtr "Reason~min|..." (largest first), hdt 1 = per-hour slots used
 *   scrap qty, scr "Item~qty|..."
 *   sN/sF/sR near miss / first aid / recordable counts
 *   crS/crA standard / actual crew, sp/ssp actual / standard speed
 */

interface DtEvent { reason: string; minutes: number; }
interface Reason { c: string; t: string; }
interface Rec {
  k: string; l: string; d: string; s: number; wo: string; lead: string; prod: string;
  ht: number; tgt: number; act: number; h: string;
  a: number | null; p: number | null; q: number | null; oee: number | null;
  dt: number; dtr: string; hdt: number; scrap: number; scr: string;
  sN: number; sF: number; sR: number; crS: number | null; crA: number | null; sp: number | null; ssp: number | null;
}
interface Result { file: string; tabs: number; lines: string[]; months: string[]; rows: Rec[]; reasons: Reason[]; warnings: string[]; }
interface Settings {
  fromDate?: string; lineOverride?: string;
  shift1Start?: string; shift1End?: string; shift2Start?: string; shift2End?: string;
  lunchMin?: number; breakMin?: number; fileName?: string;
}

function main(workbook: ExcelScript.Workbook, settings: string): string {
  let cfg: Settings = {};
  try { cfg = JSON.parse(settings === undefined || settings === "" ? "{}" : settings) as Settings; } catch (e) { cfg = {}; }
  const fromDate = cfg.fromDate ?? "";
  const lineOverride = cfg.lineOverride ?? "";
  const shift1Start = cfg.shift1Start ?? "07:00", shift1End = cfg.shift1End ?? "15:15";
  const shift2Start = cfg.shift2Start ?? "15:15", shift2End = cfg.shift2End ?? "23:30";
  const lunchMin = Number(cfg.lunchMin ?? 0), breakMin = Number(cfg.breakMin ?? 0);

  const res: Result = { file: cfg.fileName ?? workbook.getName(), tabs: 0, lines: [], months: [], rows: [], reasons: [], warnings: [] };
  const seen: string[] = [];
  const totTabs: string[] = [], d2Tabs: string[] = [], c2Tabs: string[] = [], futureTabs: string[] = [];
  const misnamed: boolean[] = [];   // parallel to res.rows: row came from a tab named for another month   // repeated notes are summarized once per board
  const addReason = (c: string, t: string) => {
    const k = (c + "|" + t).toLowerCase();
    if (t !== "" && t.toLowerCase() !== "total" && seen.indexOf(k) < 0) { seen.push(k); res.reasons.push({ c, t }); }
  };
  const months = ["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"];
  const now = new Date();
  // Line: the line folder ("Line 00", "Line 1") wins over D2. Numbers normalized: "00" -> "0", "03" -> "3".
  const norm = (x: string) => { const t = x.replace(/^lines?\s*/i, "").trim(); return /^\d+$/.test(t) ? String(parseInt(t, 10)) : t; };
  const fromFolder = norm(lineOverride);
  // The board's month comes from its file name ("10. Production Board October.xlsm"). A tab copied from the
  // previous month ("June 30" in a July board) is read as the board's month, with a note.
  const fileName = cfg.fileName !== undefined && cfg.fileName !== "" ? cfg.fileName : workbook.getName();   // the flow reads a renamed copy
  const lead = /^\s*(\d{1,2})\s*\./.exec(fileName);
  let fileMonth = lead !== null && parseInt(lead[1], 10) >= 1 && parseInt(lead[1], 10) <= 12 ? parseInt(lead[1], 10) - 1 : -1;
  if (fileMonth < 0) {
    const m = /production board\s+([a-z]+)/i.exec(fileName);
    if (m !== null) fileMonth = months.indexOf(m[1].substring(0, 3).toLowerCase());
  }

  for (const ws of workbook.getWorksheets()) {
    const name = ws.getName().trim();
    const parts = name.split(/\s+/);
    if (parts.length !== 2) continue;                       // skips MTD TOTALS, SELF-CHECK, etc.
    const tabMonth = months.indexOf(parts[0].substring(0, 3).toLowerCase());
    const day = parseInt(parts[1]);
    if (tabMonth < 0 || isNaN(day)) continue;
    const mIdx = fileMonth >= 0 ? fileMonth : tabMonth;

    const v = ws.getRange("A1:R57").getValues();
    const cell = (r: number, c: number) => v[r - 1][c - 1];
    const num = (x: string | number | boolean): number | null =>
      typeof x === "number" ? x : (typeof x === "string" && x.trim() !== "" && !isNaN(Number(x)) ? Number(x) : null);
    const txt = (x: string | number | boolean): string => (x === null || x === undefined) ? "" : String(x).trim();
    const pos = (x: number | null) => (x !== null && x > 0 ? x : null);   // 0 = not filled in

    // Reasons for Lookups / the Pareto legend: every label on the board, filled in or not.
    for (const off of [0, 29]) {
      for (let r = 17; r <= 27; r++) { addReason("Downtime", txt(cell(r + off, 1))); addReason("Scrap", txt(cell(r + off, 3))); }
      for (let r = 6 + off; r <= 13 + off; r++) { addReason("Downtime", txt(cell(r, 16))); addReason("Downtime", txt(cell(r, 18))); }
    }

    // Date: the tab ("October 27") in the board's month, with the year that puts it closest to today.
    // C2 is NOT trusted: boards are copied forward from old templates and C2 often still holds an old date
    // (a 2021 "10/27" showed up as a second Wed 10/27). A C2 that disagrees with the tab gets one note per board.
    let y = now.getFullYear(), best = Number.MAX_VALUE;
    for (const cand of [now.getFullYear() - 1, now.getFullYear(), now.getFullYear() + 1]) {
      const gap = Math.abs(new Date(cand, mIdx, day).getTime() - now.getTime());
      if (gap < best) { best = gap; y = cand; }
    }
    const d = new Date(y, mIdx, day);
    if (d.getMonth() !== mIdx || day < 1) { res.warnings.push(`${name}: not a real date (tab skipped)`); continue; }
    const iso = ymd(d);
    const c2 = num(cell(2, 3));
    if (c2 !== null && c2 > 20000 && c2 < 80000) {
      const u = new Date(Date.UTC(1899, 11, 30) + Math.round(c2) * 86400000);
      const c2iso = `${u.getUTCFullYear()}-${pad(u.getUTCMonth() + 1)}-${pad(u.getUTCDate())}`;
      if (c2iso !== iso) c2Tabs.push(`${name} (C2 ${u.getUTCMonth() + 1}/${u.getUTCDate()}/${u.getUTCFullYear()})`);
    }
    const tomorrow = new Date(now.getFullYear(), now.getMonth(), now.getDate() + 1);
    const future = d.getTime() > tomorrow.getTime();
    if (fileMonth >= 0 && tabMonth !== fileMonth) res.warnings.push(`${name}: tab is named for another month; read as ${iso}`);
    if (fromDate !== "" && iso < fromDate) continue;
    res.tabs++;

    let hasHours = false;
    for (let r = 6; r <= 42; r++) if ((r <= 13 || r >= 35) && num(cell(r, 2)) !== null) hasHours = true;
    if (future) { if (hasHours) futureTabs.push(name); continue; }   // a dated-ahead tab with hours is mislabeled: skip it
    const line = /^\d+[A-Za-z]?$/.test(fromFolder) ? fromFolder : norm(txt(cell(2, 4)));
    if (line === "") { if (hasHours) res.warnings.push(`${name}: has hours but no line number (folder or D2)`); continue; }
    const d2 = norm(txt(cell(2, 4)));
    if (d2 !== "" && d2 !== line) d2Tabs.push(`${name} (${d2})`);

    for (const sh of [1, 2]) {
      const off = sh === 1 ? 0 : 29;
      const pick = (r: number, c: number) => txt(cell(r + off, c)) !== "" ? cell(r + off, c) : cell(r, c);  // day header is filled on shift 1 only
      const wo = txt(pick(2, 1)), lead = txt(pick(2, 2)), prod = txt(pick(2, 5));
      const stdCrew = pos(num(pick(4, 2))), stdSpeed = pos(num(pick(4, 3))), actCrew = pos(num(pick(4, 4))), actSpeed = pos(num(pick(4, 5)));
      const units: (number | null)[] = [];
      for (let i = 1; i <= 8; i++) units.push(num(cell(5 + off + i, 2)));

      // Hourly target. F4 is per hour by template (=A4/B4*D4), but boards have a SHIFT total typed over it.
      const stdHr = num(pick(4, 1));
      let ht = num(cell(4 + off, 6)) ?? num(cell(4, 6)) ?? 0;
      const bestHr = Math.max(0, ...units.map(u => u ?? 0));
      if (ht <= 0 && stdHr !== null && stdHr > 0) ht = stdCrew && actCrew ? stdHr / stdCrew * actCrew : stdHr;
      if (ht > 0 && bestHr > 0 && ht > 3 * bestHr) {
        totTabs.push(`${name} S${sh}`);
        ht = ht / 8;
      }

      // Downtime: per-hour slots O:R when used (New Albany pattern), else the shift block A17:B27.
      let hourly: DtEvent[] = [];
      for (let i = 1; i <= 8; i++) {
        const r = 5 + off + i;
        for (const [mc, cc] of [[15, 16], [17, 18]]) {
          const m = num(cell(r, mc)), c = txt(cell(r, cc));
          if (m !== null && m > 0) hourly.push({ reason: c === "" ? "Unspecified" : c, minutes: m });
        }
      }
      let block: DtEvent[] = [];
      const scrap: { item: string; qty: number }[] = [];
      for (let r = 17; r <= 27; r++) {
        const reason = txt(cell(r + off, 1)), m = num(cell(r + off, 2));
        if (reason !== "" && m !== null && m > 0) block.push({ reason, minutes: m });
        const item = txt(cell(r + off, 3)), qn = num(cell(r + off, 4));
        if (item !== "" && qn !== null && qn > 0) scrap.push({ item, qty: qn });
      }
      const hdt = hourly.length > 0;
      if (hdt) {
        const hT = hourly.reduce((s, e) => s + e.minutes, 0), bT = block.reduce((s, e) => s + e.minutes, 0);
        if (bT > 0 && Math.abs(bT - hT) > 0.5) res.warnings.push(`${name} S${sh}: hourly downtime ${hT} min vs shift block ${bT} min (hourly used)`);
      }
      const events = hdt ? hourly : block;
      // one entry per reason
      const byReason: DtEvent[] = [];
      for (const e of events) {
        const hit = byReason.filter(x => x.reason.toLowerCase() === e.reason.toLowerCase())[0];
        if (hit) hit.minutes += e.minutes; else byReason.push({ reason: e.reason, minutes: e.minutes });
      }
      byReason.sort((a, b) => b.minutes - a.minutes);
      scrap.sort((a, b) => b.qty - a.qty);

      let sN = 0, sF = 0, sR = 0;
      for (let r = 18; r <= 20; r++) {
        const t = txt(cell(r + off, 5)).toLowerCase(), qn = num(cell(r + off, 6));
        if (qn === null || qn <= 0) continue;
        if (t.indexOf("record") >= 0) sR += qn; else if (t.indexOf("first") >= 0) sF += qn; else sN += qn;  // blank / DNR / near miss
      }

      const filled = units.filter(u => u !== null).length;
      if (filled === 0 && byReason.length === 0 && scrap.length === 0 && sN + sF + sR === 0) continue;  // shift not run / not filled

      const act = units.reduce((s: number, u) => s + (u ?? 0), 0);
      const dtTotal = byReason.reduce((s, e) => s + e.minutes, 0);
      const scrapQty = scrap.reduce((s, x) => s + x.qty, 0);

      // OEE, same math as the New Albany app: A = uptime / available, P = act / std speed, Q = good / total.
      const sStart = sh === 1 ? shift1Start : shift2Start, sEnd = sh === 1 ? shift1End : shift2End;
      const shiftMin = sStart === "" || sEnd === "" ? 480 : (mins(sEnd) > mins(sStart) ? mins(sEnd) - mins(sStart) : mins(sEnd) + 1440 - mins(sStart));
      const avail = Math.max(1, shiftMin - lunchMin - breakMin);
      const up = actSpeed !== null ? act / actSpeed : null;
      const A = up !== null ? Math.min(1, up / avail) : null;
      const P = actSpeed !== null && stdSpeed !== null ? actSpeed / stdSpeed : null;
      const Q = act > 0 ? Math.max(0, 1 - scrapQty / act) : null;
      // The board's own OEE Actual % (H18 shift 1, H47 shift 2) - what the line sees. Errors (#DIV/0!) read as blank.
      const boardOee = num(cell(18 + off, 8));
      const oee = boardOee !== null && boardOee >= 0 && boardOee < 5 && act > 0 ? boardOee : (A !== null && P !== null && Q !== null ? A * P * Q : null);

      res.rows.push({
        k: `${line}-${iso.replace(/-/g, "")}-S${sh}`, l: line, d: iso, s: sh, wo, lead, prod,
        ht: r2(ht), tgt: Math.round(ht * 8), act, h: units.map(u => (u === null ? "" : String(u))).join(","),
        a: r4(A), p: r4(P), q: r4(Q), oee: r4(oee),
        dt: dtTotal, dtr: byReason.map(e => `${clean(e.reason)}~${e.minutes}`).join("|"), hdt: hdt ? 1 : 0,
        scrap: scrapQty, scr: scrap.map(x => `${clean(x.item)}~${x.qty}`).join("|"),
        sN, sF, sR, crS: stdCrew, crA: actCrew, sp: actSpeed, ssp: stdSpeed
      });
      misnamed.push(fileMonth >= 0 && tabMonth !== fileMonth);
      if (res.lines.indexOf(line) < 0) res.lines.push(line);
      const ym = iso.substring(0, 7);
      if (res.months.indexOf(ym) < 0) res.months.push(ym);
    }
  }
  const keep: Rec[] = [];
  res.rows.forEach((r, i) => {
    const twin = res.rows.some((o, j) => j !== i && o.k === r.k);
    if (twin && misnamed[i]) { res.warnings.push(`${r.k}: a tab named for another month duplicates a real tab for ${r.d}; the real tab was used`); return; }
    if (twin && keep.some(o => o.k === r.k)) return;
    keep.push(r);
  });
  res.rows = keep;
  if (c2Tabs.length > 0) res.warnings.push(`Date (C2) disagrees with the tab name on ${c2Tabs.length} tab(s), tab name used: ${c2Tabs.slice(0, 4).join(", ")}${c2Tabs.length > 4 ? ", ..." : ""}`);
  if (futureTabs.length > 0) res.warnings.push(`Tabs dated after today have hours entered (skipped - check the tab names): ${futureTabs.slice(0, 4).join(", ")}${futureTabs.length > 4 ? ", ..." : ""}`);
  if (totTabs.length > 0) res.warnings.push(`Target (F4/F33) holds a shift total, read as total / 8 per hour, on ${totTabs.length} shift(s): ${totTabs.slice(0, 4).join(", ")}${totTabs.length > 4 ? ", ..." : ""}`);
  if (d2Tabs.length > 0) res.warnings.push(`Line # (D2) differs from the line folder (${fromFolder}) on ${d2Tabs.length} tab(s): ${d2Tabs.slice(0, 4).join(", ")}${d2Tabs.length > 4 ? ", ..." : ""}. Folder used.`);
  return JSON.stringify(res);

  function clean(x: string): string { return x.replace(/[|~]/g, "/"); }
  function r2(x: number): number { return Math.round(x * 100) / 100; }
  function r4(x: number | null): number | null { return x === null ? null : Math.round(x * 10000) / 10000; }
  function pad(n: number): string { return n < 10 ? "0" + n : String(n); }
  function ymd(x: Date): string { return `${x.getFullYear()}-${pad(x.getMonth() + 1)}-${pad(x.getDate())}`; }
  function mins(hhmm: string): number { const [h, m] = hhmm.split(":").map(x => parseInt(x)); return h * 60 + (isNaN(m) ? 0 : m); }
}
