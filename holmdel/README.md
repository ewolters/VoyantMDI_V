# Holmdel Tier 2, built from the Tier 1 boards (no lists)

Problems: [TROUBLESHOOTING.md](TROUBLESHOOTING.md) · How it got here (and the two earlier designs): [HISTORY.md](HISTORY.md)

**The Tier 1 Excel boards are the only record.** Nothing is copied into SharePoint lists. A flow reads the boards and keeps one small data file next to them. The Tier 2 screen shows only what the Tier 1 board captures.

```
Documents / Production / Line 9-16 / Line 12 / 10. Production Board October.xlsm   (any month, any line; read-only is enough)
        |  every 30 min: boards changed since the last save, plus boards that failed last time
        v
MDI XB - Sync Excel Boards
        |  copies each board into Production/_Tier2/board copies <run>/  (Excel only runs scripts on files the account can edit)
        |  runs Production/_Tier2/ReadProductionBoard_<hash>.osts on the copy
        v
Production/_Tier2/tier2_data.json  (last 40 days, every line)      Production/_Tier2/tier2_settings.json (target colors)
        |                                                                  ^
        v                                                                  |
MDI XB - Tier 2 Data  <--GET / SAVE-->  MDI Tier 2 - Holmdel app (in the package) --+
```

Licenses: standard only (SharePoint, Excel Online (Business)). No Dataverse, no lists, nothing pasted in a console.

## What the Tier 2 board shows
**One row per line:**

| Column | Source on the Tier 1 board | Color |
|---|---|---|
| Safety | E18:F20 / E47:F49 (near miss / first aid / recordable) | red = recordable, amber = first aid, green = none or near miss only |
| Quality · scrap | C17:D27 / C46:D56 | % of units: amber / red at the target levels |
| Delivery | hour units B6:B13 / B35:B42 vs target F4 / F33 | efficiency %: green / amber at the target levels |
| Downtime | A17:B27 / A46:B56 (or per-hour O:R if added) | minutes per shift, every row, as the board totals them (M14); shows the top reason |
| OEE | the board's own **OEE Actual %** (H18 / H47) | blank when the board can't calculate it (no Act. Speed) |
| People | act / std crew (D4 / B4) | red = short, amber = over |
| Last 7 days | efficiency per day | same as Delivery |

**Elsewhere on the screen:**
- **Right column:** the plant's downtime by reason, and scrap by component.
- **Bottom row:** plant totals.
- **Tap a line:** its shifts, hour by hour against the hourly target, and downtime and scrap for that day.
- **SQDC tabs in the line view:** S · SAFETY, Q · QUALITY, D · DELIVERY and C · COST, next to OVERVIEW. Each tab has a 7/14/30/40-day trend window ending on the END date, five KPI tiles and a day-by-day trend chart colored by the target levels. Below the chart:
  - **S:** safety cross calendar and an event log.
  - **Q:** scrap Pareto and the worst shifts.
  - **D:** hour-of-shift attainment and shift 1 vs shift 2.
  - **C:** downtime Pareto and OEE by day.

  A metric drill-down opens the line view on the matching tab.
- **⚙ TARGETS:** OEE, efficiency, downtime and scrap color levels, saved next to the boards so every screen uses the same levels.

## Install / upgrade
Import `package/MDI_Tier2_ExcelBoards_NoLists_1.0.0.19_managed.zip` (upgrade over any earlier 1.0.0.x):

| Prompt | Holmdel value |
|---|---|
| Connections | SharePoint, Excel Online (Business): Christina's |
| SharePoint site of the boards | `https://veepak1.sharepoint.com/holmdel` |
| Board folder inside Documents | `Production` |
| Shift 1 / Shift 2 | `07:00-15:15` / `15:15-23:30` |
| Lunch / Break minutes | `30` / `15` |

If the six values are shown greyed, they are hints only: type each one in.

After the import, open the solution and check that **both flows show On**. An upgrade can leave a flow off.

**First sync:** open **MDI XB - Sync Excel Boards** and press **Run**. Allow roughly 15–30 seconds per board (copy, wait, read). After that it runs every 30 minutes and only reads boards that changed.

**App:** **MDI Tier 2 - Holmdel** comes in with the package, already connected to **MDI XB - Tier 2 Data**. Each viewer needs two things: the app shared with them, **and** run-only access on the Tier 2 Data flow (see Lessons). With the flow's connections set to Christina's, viewers need no SharePoint access. If Refresh says it can't reach the flow: Edit → Power Automate → remove the flow → **Add flow → MDI XB - Tier 2 Data** → Save → Publish.

## Rules the sync follows
- **Boards:** any file in `Production/<group>/<Line N>/` whose name contains "Production Board", .xlsm or .xlsx. Excel `~$` lock files are ignored. Macros in the boards are never run and never touched.
- **Line number:** from the line folder. Pure numbers are normalized (`Line 00` → 0, `Line18` → 18); anything else is kept as typed (`Line 7a` → 7a). A folder counts as a line folder when its name starts with "Line" followed by a digit. A line folder the data file hasn't seen before has all its boards read on the next run, not just the changed ones. A D2 that disagrees with the folder gets one note per board.
- **Month:** from the file name (`10.` or `October`). A tab named for another month (a "June 30" left in a July board) is read as the board's month, with a note; if the real tab for that day also exists, the real tab wins.
- **Year:** the one that puts the date closest to today, unless C2 holds a real date.
- **Re-reading:** a changed board replaces that line's data for the months it covers. Days cleared on the board disappear from Tier 2 too.
- **Failures:** a board that can't be read is listed in Board notes and retried on every run until it reads. The other boards are still saved.
- **Saving:** the data file is only rewritten when a board was read, so the folder doesn't collect a new file version every 30 minutes.
- **Copies:** each run copies into its own folder; the previous run's folder is deleted permanently at the start of the next run.
- **Window:** 40 days are kept.
- **Reasons:** downtime reasons, scrap components and safety types are whatever the board says. Nothing is typed in anywhere.
- **Script updates:** the script's file name carries a fingerprint of its content. A new version is uploaded under a new name; an existing file is never overwritten.

## Known limits
- **Freshness:** Tier 2 sees what has been **saved** to SharePoint. A board open in desktop Excel with unsaved changes isn't visible until it's saved (the board's Send macro saves it).
- **Office Scripts quota:** 1,600 script runs per user per day. One run per changed board, so about 24 active boards × 48 runs a day stays under it.
- **Shift 2 OEE on the board itself:** H47 is `=B43/(E33*450)` (fixed 450 minutes) while H18 is `=B14/(E4*56.25*hours run)`. Tier 2 shows what the board shows, so the two shifts are calculated differently until the template is fixed.

## Lessons learned

### Sharing the app doesn't share the flow (2026-10-29)
**Symptom:** a viewer (Christian Algarin) presses Refresh and gets `MDIXB-Tier2Data.Run failed: … user … does not have ReadAccess right(s) for record with id b2321e1e-… of entity Process`. He owns everything in SharePoint, and the error still appears.

**Cause:** the error is about Power Platform, not SharePoint. `Process` is the flow record, and `b2321e1e-d0f5-5596-9d3a-65dcc95a8161` is **MDI XB - Tier 2 Data**. The app runs that flow as the person using the app. Sharing the app gives no permission on the flow, so every viewer other than the flow's owner hits this, including the TV account.

**Fix (flow owner, once):**
1. Power Automate → **My flows** → open **MDI XB - Tier 2 Data** (or **⋯ → Manage run-only permissions**). Use the details page, **not** the editor.
2. **Run only users → Edit**: add each viewer, or better a group that covers all viewers.
3. **Connections used**: set SharePoint (and Excel Online, if listed) to **Use this connection (Christina's)**, not "Provided by run-only user".
4. Save the panel. The viewer closes and reopens the app, then presses Refresh.

**Traps hit while fixing it:**
- **Wrong flow.** Only the Tier 2 Data flow needs sharing. The Sync flow is scheduled and runs as its owner. The Sync flow's details page has no Run only users box, because only app-triggered flows have one.
- **Co-owner vs run-only.** Making someone a co-owner also clears the error, but co-owners can edit and delete the flow. Board viewers should be run-only.
- **Don't save in the editor.** Opening a managed flow in the designer shows "Editing this managed flow will create customizations stored in a new unmanaged layer." Saving there adds an unmanaged layer that blocks future package upgrades. Back out with ← and discard the changes.

**For the next site:** add a "share the Tier 2 Data flow run-only with the viewer group" step to the install, right after sharing the app. Ask the site for a security or M365 group of board viewers up front, so new viewers just get added to that group.

### Open in desktop Excel ≠ saved (2026-10-29)
**Symptom:** Christian had a board open with data filled in, but Christina, looking at the same file in the browser, saw it blank. The blank board also showed #DIV/0! where the efficiency formula divides by an empty target. Once Christian closed the file, she saw everything.

**Cause:** desktop Excel was holding his entries locally with AutoSave off. That's common for macro-enabled .xlsm boards. Until a save, SharePoint holds the last saved version, and that's what the browser, the sync and Tier 2 all read. Closing the file triggered the save.

**Checks, in this order:**
1. Same tab? Today's entries are on today's tab, and the browser may be sitting on yesterday's.
2. Is the board open on someone's desktop? Look for their initials bubble in the file. Check their AutoSave toggle (top-left in Excel), and have them press Ctrl+S or the board's Send button. Then refresh the browser.

**Prevention:**
- Turn **AutoSave on** in desktop Excel on every line PC. If it won't turn on for the .xlsm, the standard is Send or Ctrl+S at the end of every hour.
- Tier 2 board-freshness flag (planned): a line whose board hasn't saved in about 2 hours during a shift shows grey with its last-saved time, so a stale board isn't read as zero production.

## Files
| File | |
|---|---|
| `package/MDI_Tier2_ExcelBoards_NoLists_1.0.0.19_managed.zip` | the two flows, the app, the six settings |
| `ReadProductionBoard.ts` | board-reading script (the flow deploys its own copy) |
| `Tier2_XB_v7.pa.yaml` | the Tier 2 screen source (v7, compiled into the 1.0.0.19 app) |
| `make.py` | rebuilds the package; run `py holmdel\make.py` for usage |
| `generator/` | `flows.py` (flows + settings) and `build.py` (package), called by `make.py`; `lint2.py` checks flow expressions |
| `generator/test/` | `export.py` + `run.js` run the script against any board offline: `python3 export.py board.xlsx board.json; node run.js ../../ReadProductionBoard.ts board.json '{"lineOverride":"Line 12"}'` |

## For the new owner (Nov 2026)
- **Supporting it** (permissions, sync, stale boards) needs nothing but this README, `../TROUBLESHOOTING.md` and the Power Platform admin screens.
- **Reinstalling or upgrading** uses `package/MDI_Tier2_ExcelBoards_NoLists_1.0.0.19_managed.zip` as described above.
- **Changing it.** Everything needed is in this folder; `holmdel/make.py` rebuilds the package (`py holmdel\make.py check` proves it reproduces the shipped 1.0.0.19, apart from a platform version stamp).
  - **Flow or board-reading changes** (what's read from the boards, the sync schedule, the data file): edit `ReadProductionBoard.ts` or `generator/flows.py` → `py holmdel\make.py 1.0.0.20` (it lints the flows) → import `build\holmdel\…_1.0.0.20_managed.zip` into Vee Pak (default) as an **Upgrade** → check both flows On. The app inside is the same compiled app as 1.0.0.19.
  - **App (screen) changes:** `py holmdel\make.py 1.0.0.20 unmanaged` → import that zip into **MDI Dev** (a separate solution, no clash with MDI) → **turn Sync Excel Boards Off in MDI Dev** (otherwise it reads the real boards from a second place) → edit the app in Studio (the screen source is `Tier2_XB_v7.pa.yaml`) → Publish → export that solution **unmanaged** → `py holmdel\make.py 1.0.0.21 managed <path to the export zip>` → import the managed zip into production as an Upgrade.
  - **Untested:** the unmanaged import into a dev environment and the app-from-export rebuild haven't been run yet. The managed rebuild has (byte-identical apart from the version stamp).
- `generator/app*.py` are the scripts that produced `Tier2_XB_v1…v7.pa.yaml`, each patching the previous version (`app.py` → v1, `app_v2.py v1 v2`, …); for new app changes, edit in Studio or patch v7 the same way.
