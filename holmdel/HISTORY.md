# Holmdel: how it got here

Holmdel went through three designs. Only the last one is live. This page exists so nobody rebuilds a design that already failed, and so leftovers from the earlier ones are recognized for what they are.

## What Holmdel had (July 2026)
- **Production Boards:** one `.xlsm` per line per month, 31 day tabs, two shifts per tab, a `SendWorkbook` macro that emails the handover.
- **Compounding MDI (Macro WB):** an `INPUTS` sheet → `AddEntry` macro → a long table (`tblData`) → S/Q/D/C summary and Pareto sheets.
- A teardown (`Voyant_MDI_Teardown.md` in Eric's HOLMDEL folder) found: the `AddEntry` macro reading the wrong rows since someone inserted rows (Quality and Cost silently zero), 30-day helper columns dropping the 31st, `DATEVALUE` year/locale bugs, free-text reasons fragmenting Paretos, MTD totals summing empty cells, tabs named "June 30/31" in a July board, 2nd-shift efficiency using the shift-1 target, a hard-coded email list. Some of these are still in the board template (see TROUBLESHOOTING §4).

## Design 1: "Send to Central" macros (Aug 2026). Retired.
Each board got a **Send to Central** button (VBA modules `Module4_CentralPush_Board/MDI`, `Module5_Setup_*`) that wrote hour-by-hour rows into one shared workbook, `MDI Central Database.xlsx`, on SharePoint, with claim tokens, read-back verification, a local outbox and a sent archive to survive Excel's one-writer lock.
**Why it was dropped:** a spreadsheet as a shared database. Only one writer at a time, a reader holding the file open blocked every button, OneDrive-synced paths could silently overwrite, and it needed macros enabled, Trusted Locations, unblocked files and per-PC setup. It worked in testing (2,400 simulated runs, zero silent losses) but was fragile to install and operate.
**Leftovers you may find:** a Send to Central button on some boards; `%LOCALAPPDATA%\VoyantMDI` outbox folders on line PCs; a `VoyantMDI` registry value; an `MDI Central Database.xlsx` somewhere on the site. None of these feed Tier 2.

## Design 2: Power Query central rollup (Sep 2026). Superseded.
A read-only Excel workbook that pulled every line's current-month board through Power Query (`SharePoint.Files`), with parameters `pSiteUrl`, `pRootPath`, `pYear`, `pMonthOverride`. Nothing wrote to the boards.
**Problems hit:** Power Query sign-in ("Couldn't authenticate with the credentials provided"): cached credentials live in two places (workbook and Global permissions) and both had to be cleared, then the right account and level chosen; null-path and literal-URL bugs across query versions v6–v7.2. The fix procedure is in newalbany/TROUBLESHOOTING.md §2.6.
**Status:** replaced by Design 3. If someone still refreshes a rollup workbook, it's independent of Tier 2.

## Design 3: Tier 2 from the boards, no lists (Oct 2026). Live.
Scheduled flow → Office Script on a copy of each board → `tier2_data.json` → Tier 2 app. Standard licenses only. See holmdel/README.md.

How it ended up like this, and what each problem taught:

| When | Problem | Outcome |
|---|---|---|
| Build week, late Oct | First design copied New Albany: SharePoint lists + a setup flow using the **Dataverse** connector. Vee Pak's environment **blocks Dataverse** (Premium). | Dropped lists entirely. The boards stay the only record. |
| Build week, late Oct | Office Script "couldn't create a connection with Excel" / Forbidden on every board. Christina's access to the boards was **read-only**, and Excel only runs scripts on files the account can **edit**. | The flow **copies** each board into `_Tier2` and reads the copy. Boards stay read-only. |
| Build week, late Oct | Power Automate expression errors at import/run: `trim()` given 2 arguments; `addProperty` names containing dots. | Added `holmdel/generator/lint2.py` (argument counts, property names); every build runs it. |
| Build week, late Oct | OneDrive-style async copy didn't work on SharePoint. | Switched to SharePoint's synchronous copy plus a wait-for-copy loop. |
| Build week, late Oct | **403** on copy: her access was view-only **without download**. | IT granted Read (with download). |
| Build week, late Oct | Every board has the same file name, so one board's notes overwrote another's; a folder name under 4 letters crashed the scan; a failing note step lost the whole save; copies folder locked after a script run. | Notes keyed by board URL; per-run copy folders deleted on the next run; failures can't block the save. |
| Build week, late Oct | First run showed red on **Get_data** (no data file yet), hiding the real result; run view made **For each board** hard to find. | The flow checks for the file first; the failing step and error are written into the board's warnings. |
| Build week, late Oct | Board **C2 date cells** were often stale, producing duplicate days (two "Wed 10/27"). | Date = tab name + month from the file name; C2 ignored (warning if it disagrees). |
| Build week, late Oct | Tier 2's own OEE didn't match the board. | Tier 2 shows the board's **OEE Actual %**. Template inconsistency between shifts reported to the client. |
| Oct 29 | Viewer error "ReadAccess … entity Process". Sharing the app didn't share the Tier 2 Data flow. | Run-only users on Tier 2 Data, owner's connections. |
| Oct 29 | Board looked blank in the browser while filled in on a desktop: AutoSave off. | AutoSave on / save every hour. Freshness flag planned, not built. |
| Oct 29–30 | UI requests: date range (single day default), every metric clickable, Board Notes panel removed, SQDC tabs with trends. | 1.0.0.14 → 1.0.0.19. |
| Nov 16 | New TV account ("HM") got the Process error: app shared, flow not. Separately, the board "stopped updating" at 6:55 am. | Run-only + Basic User role for the new account. Both cleared by Nov 18. The permission error was the new account (not an outage); the cause of the 6:55 stop wasn't confirmed. A large Microsoft 365 outage had run Nov 12–13, and a hung or failed sync run is the main suspect (TROUBLESHOOTING §3). |

**Pattern worth remembering:** almost every Holmdel failure was an environment fact discovered live (licensing, permissions, Excel's edit rule, how people save), not a logic bug. Before changing anything at Holmdel, check those facts first, and test on a copy of the Production folder before importing at the plant.
