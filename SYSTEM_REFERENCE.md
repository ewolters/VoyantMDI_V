# System reference (for troubleshooting)

How the New Albany MDI works underneath: what each flow does, what each app reads, the keys that tie records together, and where in the code to look. Written for Kenny's Claude; Kenny can read it too. Pair it with [TROUBLESHOOTING.md](TROUBLESHOOTING.md) (known errors) and [HANDOFF.md](HANDOFF.md) (rebuilds). Holmdel is separate: [holmdel/README.md](holmdel/README.md).

---

## 1. The shape of it
```
Line tablets / phones / TVs ──► 10 canvas apps (solution MDI) ──► SharePoint lists on /sites/OhioContinuousImprovement
                                   │  photos, history import                  ▲
                                   ▼                                          │
                         app-called flows (Upload Photo, Import History)       │
                                                                              │
   list-triggered / scheduled flows: Downtime Escalation, Sync Permissions, Nightly Board Check, Frontier Critical Alert
```
- **Everything is SharePoint lists.** No Dataverse tables, no SQL. The schema of every list (columns, types, choices, views, seed rows) is in `deploy/mdi_package.json`.
- **Apps and flows find the site through environment variables** (1 site + 31 lists). A wrong variable = "not found" / "Unauthorized" errors.
- **Apps run as the signed-in user.** That user needs SharePoint access to the lists the app reads (site Members), and run-only access to any flow the app calls.
- **Scheduled / list-triggered flows run as their owner's connections.**

## 2. Flows

| Flow | Trigger | Reads → writes | Sends | Notes |
|---|---|---|---|---|
| **HxH - Downtime Escalation** | HxH_Hourly item created/modified, only when `EscCumMin ≥ 60` (trigger condition); concurrency 1 | Escalation_Contacts (Active, Level ≤ minutes, shift match), Escalation_Log (already notified?) → Escalation_Log row per contact+level | Teams Flow bot message to each contact | Log Title = `<ShiftKey>\|<EscReason>\|<Level>\|<email>` stops repeats. Levels and contacts are edited in MDI Settings → ESCALATION. The 60-minute start is the trigger condition in the flow itself. |
| **MDI - Upload Photo** | Called by apps (PowerApps V2) with base64 text + tags | → TS_Photos library (file + Module/RefID/StepNo/Kind tags) | | Shared by Quality NCR, TS Maintenance, Newspaper, SW Manager, PC Audit, Frontier. Apps send the image as **text** (base64); a version taking a file input will break them. |
| **MDI - Sync Permissions** | People item created/modified | People → SharePoint groups via HTTP | | Active → site Members (contribute, no delete); CanEditConfig → "MDI Config Editors"; MDIAdmin → site Owners. Keep one IT site owner **not** in People so nobody can be locked out. |
| **MDI - Nightly Board Check** | Daily 6:30 AM Central | HxH_Hourly, HxH_Shift, Lines (yesterday) → Newspaper action for any shift with ≥ `NB_MinMissing` (2) hours missing | Digest email to `Alert_Email` | |
| **MDI - Frontier Critical Alert** | SAF_Results created with Severity = Critical | MDI_Config `Safety_Email` + zone owner | Teams | Off unless Frontier is used. |
| **MDI - Import History** | Called by MDI Settings → IMPORT HISTORY (V2: Mode LIST/READ, FileName) | LIST: files in Documents/MDI_Imports. READ: workbook tables Tbl_Shift, Tbl_Production, Tbl_Downtime (Excel Online) → returns JSON text | | The app parses and writes HxH_Shift / HxH_Hourly itself. Needs the Excel Online connection reference set. |
| **MDI - Connect Site** | Manual, paste `MDI2:` code | → sets the 32 environment variables, restarts flows | | Dataverse connector = **Premium**. Use only in MDI Dev. |
| **MDI - Set Up Site** (solution MDI Setup) | Manual, site address | → creates/repairs all lists, seeds them, saves `Setup_Code` in MDI_Config | Email with the `MDI2:` code | Safe to re-run; adds only what's missing. Run as a site owner. |

Every flow except Set Up Site, Connect Site and Import History has a **Catch** scope that emails `Alert_Email` when it fails. Flow definitions: `deploy/flows/json/`; readable versions: `deploy/flows/*.md`; generator: `generator/flows.py` (`py generator/make.py flows`), Import History: `generator/flows/gen_import_flow.py`.

## 3. Apps

One card per app (lists, flows, start-up formula, who to share with, how to check it): **`deploy/apps/APP_BUILD_GUIDE.md` §2**.

| App | Screens → file | Generator (`make.py` target) |
|---|---|---|
| Tier 1 Hour x Hour | Screen1 → `HxH_Board_v22` | `build6.py` (+ `ux6.py`, `ux_tail6.py`) · `hxh` |
| Tier 2 SQDC | Screen1 → `T2_Board_v19`; scrPeriods → `T2_Periods_v2` | `t2v2.py` · `t2`; `t2per.py` · `t2periods` |
| Tier 3 War Room | Screen1 → `T3_Board_v9`; scrBowler → `T3_Bowler_v6`; scrVariance → `T3_Variances_v7` | `t3.py` (+ `t3_metrics.py`) · `t3`; `t3screens.py` · `t3screens` |
| Quality | Screen1 → `Quality_v5`; scrNCR → `Quality_NCR_v2` | `quality.py` (builds on `qa.py`) · `quality` |
| TS Maintenance / TS Binder | `TS_Maintenance_v5` / `TS_Binder_v2` | `mt.py` · `mt` / `bd.py` · `bd` |
| Newspaper | `Newspaper_v7` | `np.py` · `np` |
| SW Manager / PC Audit | `SW_Manager_v4` / `PC_Audit_v4` | `sw.py` · `sw` / `pc.py` · `pc` |
| Frontier Audit (optional) | `Frontier_Audit_v2` | `fa.py` · `fa` |
| MDI Settings | Screen1 Escalation · scrDrop · scrLines · scrStd · scrCfg (`Settings_scrCfg_v2`) · scrPeople · scrImport (`Settings_scrImport_v2`) | `settings.py` + `settings_imp.py` · `settings` |

Shared building blocks: `generator/theme.py` (colors, `write_themed`, Voyant theme), `fx_compat.py` (post-processing, e.g. IfError arity), `settings_helpers.py`. Most apps start from `build6.py`'s helper functions (`label`, `btn`, `rect`, `dd`, `gal`, `tap`).

**Loading pattern:** each screen has a hidden **Load/Refresh** button whose OnSelect loads everything into collections (`col…`), and the screen's OnVisible does `Select(<that button>)`. If a screen shows nothing, its OnVisible wasn't set or its load errored (see the app's notification bar).

## 4. Keys that tie records together

| Key | Format | Where |
|---|---|---|
| **ShiftKey** | `<Line>-<yyyymmdd>-S<shift>`, e.g. `209-20261020-S1` | HxH_Shift **Title**; HxH_Hourly **ShiftKey**; Escalation_Log Title prefix |
| **Hourly row** | `<ShiftKey>-H<nn>` (hour number in the shift, 01…) | HxH_Hourly **Title** |
| **PlaybookKey** | `<Line>\|<Size>\|<Form>` | PLAYBOOK **Title**; copied onto HxH_Shift / HxH_Hourly. Tier 2 plan and targets look up PLAYBOOK by it. |
| **ProductForm** | HxH_Shift: `Size \| Form`; HxH_Hourly: `Size Form` | written by Hour x Hour; blank on a new shift until a product is picked (v22) |
| **Lookups** | Category (choice) + Label (the Title column) + Active + SortOrder | all dropdown reasons. Retire with **Active = No**; never delete (history references the text). |
| **MDI_Config** | Title = setting name, value column | app links, thresholds, emails, Setup_Code |

Saving the same key twice updates rather than duplicates. Hour x Hour and IMPORT HISTORY both look up by Title first.

## 5. MDI_Config settings

| Setting | Used by | Meaning |
|---|---|---|
| `App_HxH`, `App_Tier2`, `App_Tier3`, `App_Newspaper`, `App_PCAudit`, `App_SWManager`, `App_TSMaintenance`, `App_TSBinder`, `App_QARework` | apps, QR codes | each app's web link |
| `Site_URL` | apps | the SharePoint site |
| `Alert_Email` | all flows' Catch, Nightly Board Check | where failures and the digest go |
| `Safety_Email` | Frontier Critical Alert | extra recipients for Critical findings |
| `Escalation_FirstLevelMin` | MDI Settings (display/edit only) | intended first escalation level (60). The flow's trigger condition is fixed at 60; changing this setting alone doesn't change when the flow fires. |
| `NB_MinMissing` | Nightly Board Check | missing hours before an action is raised (2) |
| `TS_RankWindowDays` | (seeded, not read by the current apps) | |
| `T2_AttainGreen` / `T2_AttainAmber` | Tier 2/3 | attainment % thresholds (90 / 80) |
| `T2_OEEGreen` / `T2_OEEAmber` | Tier 2/3 | OEE % (65 / 50) |
| `T2_ReworkAmber` / `T2_ReworkRed` | Tier 2/3 | rework % of units (0.5 / 2) |
| `T2_PCGreen` | Tier 2/3 | process-confirmation completion % (90) |
| `T2_DTAmber` / `T2_DTRed` | Tier 2/3 | downtime minutes per shift (30 / 60) |
| `T2_TSRequiredMin` | Tier 2 | downtime minutes that require a troubleshooting record (15) |
| `T2_TrendDays` | (seeded, not read by the current apps; the trend is 7 days) | |
| `Setup_Code` | Set Up Site / Connect Site | the `MDI2:` code for this site. Private. |

Edit these in MDI Settings → THRESHOLDS & LINKS (no code change needed). Tier 3 metric on/off, order and thresholds live in the **KPI_Metrics** list; value-stream grouping in **ValueStreams**.

## 6. How the boards calculate (where to look)
- **Tier 2 daily board** (`generator/t2v2.py`): `DAYREC` builds one record per line per day from HxH_Shift (plan, actual, OEE), HxH_Hourly (downtime events, safety), QA_Rework, TS_Occurrences, PC_Audits, SAF_*, Escalation_Log and Newspaper; `derive()` turns those into text, sub-text and a G/A/R/N status per domain (S Safety, Q Quality, D Delivery, DT Downtime, C Cost/OEE, P People, M Maintenance, PC Process confirmation, A Actions). `TOTREC` is the plant row. Thresholds come from §5.
- **Tier 2 WEEKS & MONTHS** (`generator/t2per.py`): reuses the same formulas per week/month (`PREC`), loads lists one week at a time, never more than 6 months back (26 weeks / current + 5 months).
- **Tier 3** (`generator/t3.py`, `t3_metrics.py`): the same domain formulas, plus it saves each closed day to **KPI_Daily**; week/month views read KPI_Daily.
- **Hour x Hour** (`generator/build6.py`): RUN % tile = hourly actual ÷ hourly target; purple ★ marks an hour above max(105%, mean + 2 SD of the line's last 30 days) once 20+ hours exist, else 115%. The cover over the hours stays until a product is picked and ACTUAL CREW is entered.
- **OEE rule (boards):** empty hours through the rest of a shift, or "DNR" (did not run) in the comments, mean the crew went elsewhere and those hours aren't counted against the line.

To explain any number on a screen: search the generator for the label text, find the formula, then trace its collection back to the load button.

## 7. Limits and behaviors that look like bugs
- **2,000-row data limit** per query (app setting). Big lists are loaded in date chunks; anything that filters a large list in one go may silently cut off at 2,000.
- **History window:** Tier 2 reads at most 6 months back; Tier 3 week/month views depend on KPI_Daily having been written (it fills as Tier 3 is opened).
- **Published vs saved:** users and exports get the last **published** app.
- **Flows can switch off** after an import or after repeated failures; check run history first.
- **Teams Flow bot** can only message people in the Voyant tenant.
- **Kiosk/TV accounts** are ordinary users: they need site membership, the app shared, and run-only on any flow the app calls.

## 8. Holmdel in one paragraph
A separate managed solution reads the Tier 1 Excel boards directly; no lists. **MDI XB - Sync Excel Boards** (every 30 min, owner's connections) copies changed boards to `Production/_Tier2/board copies…`, runs the Office Script `ReadProductionBoard.ts` on each copy, and merges results into `Production/_Tier2/tier2_data.json` (40 days). **MDI XB - Tier 2 Data** serves that file to the app (and saves target colors to `tier2_settings.json`). Viewers need the app shared **and** run-only on Tier 2 Data. Freshness depends on boards being **saved** (desktop Excel with AutoSave off holds data locally). Details, rules and known limits: `holmdel/README.md`.
