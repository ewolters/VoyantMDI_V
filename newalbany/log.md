# New Albany Virtual MDI — Build Log

> Paths in entries before 2026-11-18 are from before the restructure: `generator/`, `deploy/` and `solution/` are now under `newalbany/`.

What we built, how we built it, and why. Newest entries at the bottom of each section. Every entry records the date, what changed, the method, and anything we learned the hard way.

**How to read this file:** Part A (Master summary) is the current state as of 2026-10-21 and is the place to start. Part B keeps the original Day-0 plan (now superseded) for history. Part C is the dated session log: every build, test, bug and decision in order.

---

# PART A — MASTER SUMMARY (current state, 2026-10-21)

## A1. What the system is
A virtual MDI (Managed Daily Improvement) system for Voyant New Albany, **100% Microsoft 365 on standard licenses**:
- **SharePoint Lists** are the data.
- **Power Apps canvas apps** are the screens. They are built as YAML and pasted into Studio.
- **Power Automate** handles escalation and photo upload.

There are no premium connectors, no Dataverse tables, and no custom code outside Microsoft. The early Excel / Office Scripts / Power BI plan (Part B) was dropped on Day 1 in favor of Power Apps (see Experiments 1–2 in Part C).

**Data flow:**

```
PLAYBOOK (Line|Size|Form → rate, crew, eff.)
   │
   ▼
HxH Board (hourly entry, crew gate, DT/scrap/speed reasons from Lookups)
   │  ├─► HxH_Hourly / HxH_Shift   (ShiftKey Line-yyyymmdd-S#)
   │  └─► Flow: HxH - Downtime Escalation ─► Teams to Escalation_Contacts at 60/120/240 min ─► Escalation_Log
   │
QA Rework app ───────► QA_Rework (joins HxH_Shift by ShiftKey)
TS Maintenance (phone, QR) ─► TS_Issues / TS_Fixes / TS_Procedures / TS_Steps / TS_Occurrences (+ photos)
TS Binder (operator, read-only) ◄── same TS lists, ranked by 90-day occurrences
SW Manager ─► SW_Standards / SW_Elements (+ photos) ─► PC_Cards / PC_CardItems
PC Audit (phone, QR ?card=) ─► PC_Audits / PC_Results ─► Newspaper actions on NO
Newspaper app ◄── actions from every module (Source + RefKey)
All photos ─► Flow: MDI - Upload Photo ─► TS_Photos library (Module + RefID + StepNo + Kind)
Tier 2 Board (PARKED) ◄── HxH_Shift, QA_Rework, TS_Occurrences, PC_Audits, Newspaper
```

## A2. Modules and status
| # | Module | App / flow | Current file | Status |
|---|---|---|---|---|
| 1 | Hour x Hour | HxH Board | HxH_Board_v13.pa.yaml | **Live in sandbox, tested.** PLAYBOOK-driven targets; Lookups dropdowns; muted palette; Actual Crew gates the sheet; 12-hour times. |
| 2 | Downtime escalation | Flow *HxH - Downtime Escalation* | deploy/flows/01_… .md | **Live, tested.** Contact-driven: 60 min and up, cumulative per issue. |
| 3 | QA rework | QA Rework (entry + quality dashboard) | QA_Rework_v3.pa.yaml (v3: VOID instead of delete) | **Live, tested** 2026-10-20 4:41 PM. |
| 4 | Troubleshooting (maintenance) | TS Maintenance (phone, QR) | TS_Maintenance_v3.pa.yaml · sandbox runs v1 | v1 tested end to end on a phone. **v3 links each fix to the board's downtime event and logs repair time. Eric to paste and test.** |
| 5 | Troubleshooting (operators) | TS Binder (read-only) | TS_Binder_v1.pa.yaml | Built. |
| 6 | Standard work | SW Manager | SW_Manager_v2.pa.yaml | Built. **Eric to paste v2, add the flow, and load the 6 sample photos.** |
| 7 | Process confirmation | PC Audit (phone, QR) | PC_Audit_v2.pa.yaml | Built. **Eric to paste v2 and test a card.** |
| 8 | Action register | Newspaper | Newspaper_v5.pa.yaml | **First paste 2026-10-21** (v4 renders). v5 = Harvey-ball progress + 2 error fixes. |
| 9 | Photos | Flow *MDI - Upload Photo* (in solution **MDI**) | deploy/flows/02_… .md | Live, On. |
| 10 | Tier 2 roll-up | Tier 2 Board | T2_Board_v6.pa.yaml | **Built 2026-10-21.** v2 pasted and rendering (cell layer confirmed). v3 adds the DOWNTIME domain and the events list. **Eric to re-paste v3.** |
| — | Yellow tags | — | — | Not started. Hooks are in place (see A8). |

## A3. Apps — build settings
| App | Size | Data sources | Flow | Screen1.OnVisible |
|---|---|---|---|---|
| HxH Board | 1920×1080 | PLAYBOOK, HxH_Hourly, HxH_Shift, Lookups | – | `Select(btnRefresh)` |
| QA Rework | 1920×1080 | QA_Rework, Lookups, PLAYBOOK, HxH_Shift | – | `Select(btnQRefresh); Select(btnQCtx)` |
| TS Maintenance | Phone 640×1136 | Lookups, Lines, Assets, TS_Issues, TS_Fixes, TS_Procedures, TS_Steps, TS_Occurrences, TS_Photos, HxH_Hourly | ✔ | `Select(btnMRefresh)` |
| TS Binder | 1920×1080 | Lookups, Lines, TS_Issues, TS_Fixes, TS_Steps, TS_Occurrences, TS_Photos | – | `Select(btnBRefresh)` |
| SW Manager | 1920×1080 | SW_Standards, SW_Elements, PC_Cards, PC_CardItems, PC_Audits, PC_Results, TS_Photos, MDI_Config, Lookups | ✔ | `Select(btnSRefresh)` |
| PC Audit | Phone 640×1136 | PC_Cards, PC_CardItems, PC_Audits, PC_Results, SW_Elements, TS_Photos, Newspaper, Lines | ✔ | `Select(btnPRefresh)` |
| Newspaper | 1920×1080 | Newspaper, People, Lines, TS_Photos, PC_Audits | ✔ | `Select(btnNRefresh)` |
| Tier 2 Board | 1920×1080 | HxH_Shift, HxH_Hourly, QA_Rework, TS_Occurrences, TS_Issues, TS_Fixes, PC_Audits, PC_Results, PC_Cards, SW_Elements, Escalation_Log, Newspaper, Lines, MDI_Config, PLAYBOOK, Lookups, People | – | `Select(btnRefresh)` |

Set Data row limit = 2000 in every app. In Studio, flows are added from the **Power Automate pane → + Add flow**, and that pane shows only flows that live in a solution.

**Deep-link parameters:**
- HxH, Binder, Newspaper: `?line=`
- TS Maintenance: `?line=&equip=&asset=`
- PC Audit: `?card=&line=`

## A4. SharePoint (sandbox)
**Site:** Verxted tenant → `/sites/MDISandbox`. A test site, `/sites/MDIDeployTest`, was used to prove the provisioner and can be deleted.

**Shared lists:**
- **Lines:** 15 rows, with ValueStream and Active.
- **Lookups:** Label / Category / Group / SortOrder / Active / Help. Categories are Downtime, Scrap, Speed loss, Extra headcount, Rework, Equipment.
- **People:** Name, Email, Role, Tier, Shifts, Lines, Area, Active.
- **MDI_Config:** Setting / SettingValue / Kind / Notes. Holds the app-link slots (App_HxH, App_QARework, App_TSMaintenance, App_TSBinder, App_Tier2, App_PCAudit, App_SWManager, App_Newspaper), the flow IDs, and the thresholds.
- **Assets:** equipment register, currently empty.
- **PLAYBOOK:** 37 rows plus calculated columns.
- **Newspaper:** the action register. Its Source choices cover every module.
- **TS_Photos:** document library shared by every module. Columns: Module, RefID, ProcID, StepNo, IssueID, Kind, Caption, TakenBy.

**Module lists:**
| Module | Lists |
|---|---|
| HxH | HxH_Hourly, HxH_Shift, Escalation_Contacts, Escalation_Log |
| QA | QA_Rework |
| Troubleshooting | TS_Issues, TS_Fixes, TS_Procedures, TS_Steps, TS_Occurrences |
| Standard work / PC | SW_Standards, SW_Elements, PC_Cards, PC_CardItems, PC_Audits, PC_Results |
| Unused | T2_Maint (left out of the deploy package). T2_QA and T2_Ops are in the recycle bin. |

All 24 provisioned lists/libraries and their full schema are in `deploy/mdi_package.json`.

## A5. Flows
Environment: `Default-00b4381d-bbd9-4097-aeda-50de00cc750a`.

| Flow | ID | Where | Used by |
|---|---|---|---|
| HxH - Downtime Escalation | ee768e81-a5e4-4ea2-8bcd-ecc57512f210 | My flows | Automatic (list trigger) |
| TS - Upload Photo | 10aa7d3a-1e08-4429-9c01-9b217b5ff337 | My flows | Sandbox TS Maintenance v1 only |
| MDI - Upload Photo | (copy of the TS flow) | **Solution "MDI"** (CDS Default Publisher) | SW Manager v2, PC Audit v2, Newspaper v2, TS Maintenance v2 (deploy) |

**Upload-photo interface:**
- **Inputs** (Power Apps V2 trigger): Photo (file), FileName, ProcID, StepNo, IssueID, Kind, Caption, TakenBy.
- **Returns:** `photoid`.
- **After the upload,** apps Patch Module and RefID onto the returned photo.

## A6. Conventions and keys
- **ShiftKey:** `Line-yyyymmdd-S#`. Hour key: `…-H##`. PlaybookKey: `Line|Size|Form`.
- **Shift times:** Shift 1 is 06:00–16:30; everything else is Shift 2. ShiftDate is the previous day when the hour is before 06:00.
- **Every module writes actions to Newspaper** with a Source and a RefKey.
- **Photos:** latest photo wins (`First(SortByColumns(Filter(...), "Created", Descending))`).
- **Ranking:**
  - Troubleshooting rank = number of occurrences in the last 90 days.
  - PC adherence = audits done ÷ audits expected (from frequency × shifts × days).
- **Naming:** see "Naming conventions" in Part C. Lists are `MODULE_Thing`; flows are "MODULE - Verb Noun"; files are `<App>_v#.pa.yaml`.
- **App pattern:**
  - One screen with panels switched by variables.
  - A REFRESH button loads every collection, and OnVisible = `Select(REFRESH)`.
  - Helper buttons are 1×1 and transparent.
  - Writes and loads are wrapped in `IfError` → Notify.
- **Brand:**
  - Fonts: Georgia for headings, Arial for body.
  - Colors: #07272D, #004851, #00B2A9, #B0E3E4; grays #75787B, #B1B3B3, #D9D9D6.
  - Color is used only as a signal (red / amber / green).

## A7. Gotchas (consolidated)
**SharePoint**
- Never name a column `Value`, `Text`, `Date` or `Author`. They collide with Power Fx or SharePoint: Author becomes Author0, and Lookups' Title displayed as "Value" broke formulas.
- Calculated columns created by script must use `[Display Name]` formulas. Internal names are rejected.

**Power Apps — pasting YAML**
- Pasted YAML brings only the controls. Set the app size, Screen1.OnVisible and the data row limit by hand.
- After renaming a column, use Data → ⋯ → Refresh on that data source.
- Control versions that paste cleanly:
  - Label@2.5.1, Classic/TextInput@2.3.2, Classic/DropDown@2.3.1, Classic/Button@2.2.0
  - Rectangle@2.3.0, Gallery@2.15.0, AddMedia@2.2.1, Image@2.2.3
- To see the exact schema for any control, use Tree view → View code.

**Power Fx formulas**
- `Sum()` of an empty table is Blank, and `Blank() = 0` is false. Use `Coalesce(…, 0)`.
- A time format without AM/PM switches to 24-hour.

**Flows**
- Power Apps can't write files to SharePoint directly. Use a V2 flow with a File input and `@base64ToBinary(triggerBody()?['file']?['contentBytes'])`. Writing it as `"@{…}"` writes base64 text instead of the file.
- The new Studio "Add flow" pane lists **only solution-aware flows**. Build flows inside solution MDI, or use Add existing → Outside Dataverse.
- A flow saved with Save As is created **Off**. Turn it on.

**Other**
- Containers ignore X/Y. The diamond icon means premium, not a permissions problem.

## A8. Open items
**Eric — now**
1. In SW Manager, PC Audit and Newspaper: add **MDI - Upload Photo** (Power Automate pane), paste the v2 YAML, and set OnVisible.
2. In SW Manager, load `sample_photos/SW1-E1…E6.jpg` onto the SAMPLE standard's elements, then run card 1 in PC Audit on a phone.
3. Delete the stale files on the laptop:
   - `deploy\apps\*_v1.pa.yaml` (SW_Manager, PC_Audit, Newspaper, TS_Maintenance)
   - `deploy\flows\02_TS - Upload Photo.md`
   - These have already been removed from the packaged zips.

**Next builds**
1. Publish the apps → paste their web links into MDI_Config → print QR labels (Edge → Create QR code, or Eric runs qr_labels.py) for TS Maintenance (line × machine) and PC cards.
2. HxH TROUBLESHOOT button → launches TS Binder with `line` and `equip`.
3. Yellow tags:
   - Planned list YT_Tags: asset, component, condition, photo, status Tagged → Parts ordered → Parts in → Repaired → Verified, PO / part #, ETA, owner.
   - Hooks already in place: TS_Occurrences.YellowTagRef, TS_Photos Kind "Yellow tag", Newspaper Source "Yellow tag".
4. Voyant tailoring: map their SharePoint standard-work library (DocLink / DocNo / approval), build real PC cards, fill the People list with tiers, and replace the sample photos with Voyant ones.
5. Tier 2: test v2 in Studio; tune the thresholds with Voyant.

**Housekeeping**
- Remove the duplicate HxH_Hourly_1 data source in the HxH app.
- Fold the generators into one common.py.
- Optionally rename the TS_Photos library to MDI_Photos. Apps bind by ID, so this is safe.

**Before go-live, clear the test data:**
- Escalation TEST contacts (Eric at 60 and 120 min).
- QA test entry (2,400, Dirty Bottles).
- TS test: "Labels Wrinkling" / "Teflon Worn" plus its 2 photos.
- SAMPLE standard and card (SW-MDI-001, card 1).
- People: Eric (TEST).
- **Tier 2 demo seed (2026-10-21):** every row tagged **T2TEST** — EnteredBy (HxH_Shift, HxH_Hourly, QA_Rework), LoggedBy (TS_Occurrences), AuditedBy (PC_Audits), Title prefix `T2TEST` (Escalation_Log, PC_Audits, PC_Results), RefKey prefix `T2TEST` (Newspaper), Author0 = T2TEST (TS_Issues 2–6 and TS_Fixes 2–9). Also set: Lines.ValueStream for 205/211/219 (Lotions & Creams) and 209/210 (Wash & Soap). Sandbox T2_AttainGreen/Amber = 90/80; the deploy seed uses 95/85.

**Open questions for Voyant**
- Escalation roster: names, and Teams channel or chat per tier.
- Kiosk account for the line TVs and tablets.
- Does rework count against OEE Quality?
- Line 205 workbook template.
- Their SW library structure.

## A9. File index (package `NEW_ALBANY_MDI_Full_Package_2026-10-21.zip`)
| Folder | Contents |
|---|---|
| `00_START_HERE.md` | One-page index and next steps |
| `KENNY_HANDOFF_for_Copilot.md` | For Kenny's Claude: every step a person must do by hand (H1–H21) and the triggers to call Eric |
| `log.md` | This file |
| `01_Apps_Current/` | The 8 current app YAMLs: HxH_Board_v11, QA_Rework_v3, TS_Maintenance_v3, TS_Binder_v1, SW_Manager_v2, PC_Audit_v2, Newspaper_v3, T2_Board_v15 |
| `02_Deploy/` | Deployment package: README, provision_mdi.js.txt, mdi_package.json, apps/, flows/. Also `MDI_Deploy_Package.zip`. **No .py or .js files**, because Voyant's mail filter blocks them. |
| `04_Source_Data/` | Voyant source workbooks: Line 209 entry, OEE rollup, Playbook summary, PLAYBOOK_v1, 205 TG Labeler troubleshooting guide (+ sim-augmented), Teflon OPL |
| `05_Reference/` | Downtime Escalation Plan Rev 1, Voyant Brand Guidelines |
| `06_Sample_Photos/` | SW1-E1…E6.jpg (template T-card photos for the SAMPLE standard) |
| `99_Archive/` | Superseded YAMLs: T2_Board_v1–v14, QA_Rework_v2, Newspaper_v2–v4, HxH_Board_v10–v12, TS_Maintenance_v2, HxH v1–v9, HxH_HourGallery snippet, QA v1, SW/PC/Newspaper v1 (old flow), TS_Maintenance_v1 (still the version running in the sandbox, on the TS flow) |

---

# PART B — ORIGINAL PLAN (Day 0, 2026-10-20) — SUPERSEDED, kept for history
> The stack below (Excel entry + Office Scripts + Power BI) was replaced on Day 1 by SharePoint Lists + Power Apps + Power Automate. See Part A. The defects found in review (B-section "Defects") are still valid and are what the HxH Board design fixes: targets come from PLAYBOOK × actual hours, planned vs. unplanned is split, reasons come from dropdowns only, and escalation is per issue.

## Stack decision

**2026-10-20 — Microsoft apps only. No custom HTML/JS for now.**

| Layer | Tool | Role |
|---|---|---|
| Entry (line side) | Excel Online (SharePoint) | HOUR x HOUR boards, one per line. The only place operators type. |
| Standards | Excel table / SharePoint List | PLAYBOOK — standard speeds per line × item. Single source of truth. |
| Data store | SharePoint Lists | Hourly, DowntimeEvents, Safety, Newspaper, T2 inputs. The official record once an hour is closed. |
| Logic | Office Scripts (TypeScript) | Reads/writes workbook contents. Called by flows. |
| Orchestration | Power Automate (standard license) | Close-out, escalation, Newspaper, PLAYBOOK push, validation. |
| Departmental input | Microsoft Forms / List forms | QA rework, Ops crewing, Maintenance → T2. |
| Visuals | Power BI (+ Excel where enough) | TIER2 dashboard. |
| Comms | Teams + Outlook | Escalation cards, digests. No SMS (Twilio = premium). |

**Stay on the standard license.** Premium items to avoid: HTTP action, "When an HTTP request is received" trigger, custom connectors, SQL Server, Dataverse, Twilio.

**Why Lists, not just workbooks:** the Excel connector has no row-added trigger (timer polling only), Power Query does not refresh on a schedule in Excel for the web, and multiple writers on one workbook cause file locks. Lists give event triggers, version history, and concurrency safety. Excel stays as the familiar entry surface.

---

## Target architecture

```
PLAYBOOK (line × item speeds)
     │  nightly push (flow + Office Script)
     ▼
HOUR x HOUR boards (Excel, per line) ── production + safety in/out
     │  hourly close-out (flow + Office Script)
     ▼
SharePoint Lists: Hourly · DowntimeEvents · Safety
     │                       │
     │                       ▼
     │               ESCALATION flow (every 15 min)
     │                 ├─► Teams card to tier, Acknowledge button, auto-escalate on no-ack
     │                 └─► NEWSPAPER List (one item per issue, idempotent key)
     ▼
TIER2 rollup ◄── T2 inputs: QA rework · Ops crewing · Maintenance (Forms → Lists)
     │
     ▼
TIER2 visuals (Power BI)
```

---

## Current state (as found 2026-10-20)

Files in this folder:

- **Line_209_Data_Entry_v1.xlsx** — two-shift Data_Entry sheet (12 hourly rows each, 2 DT slots per hour), Log_Production / Log_Downtime / Log_Shift tables, Dim_ tables (DowntimeReason, Standards, ScrapRef, ScrapReason, StaffingReason, SpeedLossReason), Trends sheet with 4 charts. Saves via EndShift.bas (VBA) or EndShift Office Scripts (not in folder; noted as never tested against a live file). 103 shifts logged 7/20–10/13.
- **Production_OEE_Rollup_v1.xlsx** — Power Query `Shift_Data` pulls `Log_Shift` from every .xlsx in SharePoint folder "Production Line Dashboard -only-" on site veepak1.sharepoint.com/sites/OhioContinuousImprovement. Bottoms-up OEE (sums of minutes/units, not averaged %). Rollup_LineMonth, Rollup_PlantMonth, Daily_View, MOR_Chart1/3/4 for month-end paste. 991 shift rows across 14 lines.
- **New Albany Downtime Escalation Plan-Rev_1.pdf** — cumulative downtime tiers: 15 min (Maint Tech, QC Lead) → 30 min (Supervisors) → 60 min (Managers) → 2 hrs (QA/EMRA Directors) → 4 hrs (GM). Escalate up AND across; escalate as soon as it's known the next threshold will be exceeded. Component availability → Warehouse Supr; component quality → Quality Supr.

### Defects found in review

1. **Inflated targets (209).** Hourly block is always 12 rows, so shift target = 12 × 8,100 = 97,200 even on 10-hr shifts (playbook per-shift = 78,975). Attainment reads ~20% low.
2. **Planned time logged as downtime.** Breaks entered as DT events; must be separated from unplanned for board and escalation.
3. **Validation bypass.** Free text ("planned breaks") gets past the dropdown and falls into "Other".
4. **Corrupt shift row.** 209 10/12 Shift 2: calculated DT −356 min, OEE −5,751%.
5. **Rollup "Complete" flag is null-check only.** Across 991 rows: 16 bad dates (1899/1900), 73 Performance >105% (44 on Line 210 — likely wrong T-Max), 17 OEE outside 0–1, 26 missing PlannedShiftHrs.
6. **Reported vs calculated DT on 209 ≈ 57%.** Logging discipline metric worth showing.
7. **Hourly DT ≠ issues.** Escalation is per issue; a 50-min fault split 20+30 across hours never trips the 60-min tier. Need an issue ID / continuing-down flag.

---

## Build sequence
*(Superseded. Actual status is in A2. Items 1, 2, 3, 5 and 7 were delivered in Power Apps form. Item 6 became the Newspaper app. Item 9 is the parked Tier 2 Board. Items 4 and 8 are no longer needed, because apps write to Lists directly and validate at entry.)*

- [ ] 1. PLAYBOOK — master table, line × item keyed
- [ ] 2. HOUR x HOUR board v2 — reads PLAYBOOK, correct targets, planned/unplanned split, issue ID, safety I/O
- [ ] 3. SharePoint Lists schema
- [ ] 4. Flow: hourly close-out (Office Script → Lists)
- [ ] 5. Flow: escalation (15-min recurrence, Teams adaptive card, ack + auto-escalate)
- [ ] 6. Flow: NEWSPAPER auto-populate + overdue reminders
- [ ] 7. T2 inputs — Forms for QA / Ops / Maintenance
- [ ] 8. Flow: data validation + reject loop
- [ ] 9. TIER2 visuals — Power BI

---

## Open questions
*(Day-0 list. Resolved since: the license is standard; the line-side surface is Power Apps in a browser; crewing comes from the HxH board, per Eric; escalation is cumulative per issue and unplanned only. Still open items are in A8.)*

- Line 205 workbook (confirm same template as 209)
- EndShift_OfficeScript.ts / EndShift.bas source files
- Power Automate license tier (standard assumed)
- Power BI license (Pro for viewers?)
- Line-side display hardware: browser Excel or desktop?
- Escalation roster: names / Teams channels per tier
- Does rework count against OEE Quality (first-pass yield) or report separately?
- Crewing: board's Actual Crew vs Ops input — which is authoritative?
- Escalation "cumulative" = per issue or per shift? (Reading: per issue, unplanned only)

---

# PART C — SESSION LOG (chronological)

## Session log

### 2026-10-20
- Reviewed the three files; findings above.
- Decided: MS-only stack, SharePoint Lists as store, Power Automate standard, Power BI for visuals.
- Started this log.
- Power Automate **Premium** plan assigned to Eric — in the **SVEND tenant** (environment "SVEND (default)"), not Voyant's. Use it as the learning sandbox. Production flows must eventually live in Voyant's tenant under a Voyant-owned account, on Voyant's licensing → keep designs on standard connectors so they port.

### Experiment 1 — HOUR x HOUR entry via Microsoft Forms (feasibility, SVEND tenant)
Goal: prove the chain Form → Flow → List works end to end before Voyant access.
- Form "HxH — Hourly Entry" (questions + branching: see chat 2026-10-20)
- List "HxH_Hourly" (all text/number columns for v1 — no Choice columns yet)
- Flow "HxH - Form to List": When a new response is submitted → Get response details → Create item
- Known Forms limits: static choice lists (can't read PLAYBOOK), no view of prior hours, can't validate against the previous hour (flow must do it), max 1 DT event per section unless we repeat the section.
- Status: **abandoned 2026-10-20** — Forms can't read PLAYBOOK and can't show the board. Clunky.

### Experiment 2 — HOUR x HOUR as a Power Apps canvas app (SVEND tenant)
Decision: Power Apps is the line-side entry AND the board. Dropdowns read the PLAYBOOK List live; target per hour computed from TargetSpeedBPM × 60 × EfficiencyTarget minus planned minutes; app writes each hour to HxH_Hourly with Patch(). Power Automate stays for background work (escalation, Newspaper, digests). Power Apps with standard connectors (SharePoint) is included in M365 licensing — no premium needed.
- Created **PLAYBOOK_v1.xlsx** (table PLAYBOOK; 209's three product forms from Dim_Standards; Title = Line|ProductForm key; Active flag). Import to a List: New → List → From Excel.
- Next: import PLAYBOOK List, create HxH_Hourly List, build the app with "Start with data".
- Eric built header (Voyant logo, title), DateMeta (TodayDate), ShiftMeta (ShiftSelect, Items ["1","2"]) by hand in auto-layout containers. Hand-building hour rows = too slow.
- **Method change: Gallery + YAML paste.** One template row, Items = ForAll(Sequence(12)) of hour start times from shift start (S1 06:00, S2 16:30). Controls delivered as `HxH_HourGallery.pa.yaml`, pasted into Tree view. Status tile = cumulative counter vs cumulative target (avoids cross-row references in a gallery). 8100 rate hard-coded until PLAYBOOK List exists.
- Status: in progress

---

### Sandbox SharePoint (Verxted tenant) — 2026-10-20
- Signed into built-in browser as eric.wolters@verxted.com (Power Automate environment "SVEND (default)" is this tenant).
- Created communication site **https://verxted.sharepoint.com/sites/MDISandbox** ("MDI Sandbox").
- Method: SharePoint REST from the browser session (`/_api/SPSiteManager/create`, `/_api/web/lists`, `fields/createfieldasxml`, `items`). Faster and exact vs clicking; same thing the UI does.
- **PLAYBOOK** list: Title (Line|ProductForm), Line, ProductForm, Size, Form, TargetSpeedBPM, EfficiencyTarget, StdCrew, AvailableHrsShift, Active (Yes/No, default Yes). 3 STUB rows from Line 209 Dim_Standards — replace when the real playbook file arrives.
- **HxH_Hourly** list: Title (key), Line, ShiftDate (date only), Shift, HourNo, HourStart (date+time), ProductForm, Job, CumTarget, CumulativeUnits, SpeedBPM, DT_Minutes, DT_Reason, StillDown (Yes/No), PlannedMin, SafetyEvent (Yes/No), SafetyNotes, Notes, EnteredBy.
- Not touched: existing "MDI Central Database" item in the tenant.

### Real PLAYBOOK → List — 2026-10-20
Source: **Playbook_Summary_Current.xlsx**, sheet Overview, Table1 (A1:AO38) — already flat, one row per Line × Size × Form. Per-line sheets (201…221P) are printable crew layouts (position letters, role counts, "KD 9/20/22"); not imported.
- PLAYBOOK List rebuilt: 37 rows, all loaded. **Key = Line|Size|Form** (the workbook's Line_Format = Line-Size is NOT unique: 202-3 oz, 207-8 oz, 210-8 oz each appear twice).
- **Line is Text**, not Number — line "221P" exists. HxH_Hourly.Line changed to Text too; added HxH_Hourly.PlaybookKey.
- Columns: Line, Size, Form, RateBPM, FinancialStdRate, OEMStdRate, 13 × HC_<role>, BoxMakerNote, AvailableHrsShift, 11 × CO_<changeover> (hrs; CO_CriticalCleaning is text), ScheduledUnitsShift, EfficiencyTarget, Active.
- **Calculated columns** (mirror the Excel formulas, so nobody stores a derived number): UnitsPerHour = RateBPM×60×Eff; UnitsPerShift = ROUNDUP(Eff×Rate×60×AvailHrs,0); TotalHC = sum of HC_ columns. Verified 209|10 oz|Body Wash → 8,100 / 78,975 / 9 — matches workbook.
- Note: REST returns calculated numbers as strings ("8100.00000000000"); Power Apps/flows may need Value().
- Playbook data issues to raise with Voyant: 201|7.8 oz has no Rate (#DIV/0! in source); Box Maker column mixes counts with text ("Inner Pack", "flex") → stored in BoxMakerNote, not counted in TotalHC; Financial Std Rate / OEM Std Rate empty for all rows; "Fruit Fushion" typo is in source (left as-is so keys match).
- **Mirror pass (Eric's request):** display names now = Excel headers exactly, default view in Excel column order, Title renamed "Key", made optional, hidden from view (Line / Size / Form are the visible identifiers). Every Excel formula column is a SharePoint calculated column:
  - UPLH = units_per_shift / (Total HC × 10)
  - Total HC = sum of the 13 role columns
  - Line_Format = CONCATENATE(Line,"-",Size)
  - Productivity vs Scheduled = units_per_shift / (Rate × 60 × Available Hrs)  (% format)
  - adjusted_line_speed = Rate × Productivity; units_per_hour = Rate × 60 × Productivity
  - Playbook Units per Shift = ROUNDUP(Eff × Rate × 60 × Avail Hrs, 0); Playbook Units per Hour = Eff × Rate × 60
  - Divide-by-zero wrapped in IF(ISERROR(),"") — 201|7.8 oz shows blank where Excel shows #DIV/0!.
  - Verified against workbook: 209 10 oz → UPLH 444.4, Productivity 38.0%, adj speed 68.4, adj units/hr 4,103, playbook 8,100/hr, 78,975/shift. 201 rows match.
  - Gotcha: `&` inside a formula in field SchemaXml breaks the XML — use CONCATENATE (or &amp;).
  - Internal names stay short (RateBPM, HC_Packer, CO_Flush…) — Power Apps shows display names, flows use internal names.
- Excel stays the maintained source until we know who owns it; a sync flow (Excel → List) is a later step.

### Voyant brand (Voyant_Brand_Guidelines LR.pdf v2.0)
- Fonts: Recife Display (headlines) + Graphik (body) → not available in Power Apps; **system defaults per guide = Georgia (headlines) + Arial (body)**.
- Primary: Dark green **#07272D**, Deep teal **#004851**, Teal **#00B2A9**, Light aqua **#B0E3E4**; grays **#75787B**, **#B1B3B3**, **#D9D9D6**.
- Secondary (hierarchy only): #221C35, #3F2A56, #9678D3, #C5B4E3, #0C2340, #01426A, #489FDF, #B9D9EB.
- Wordmark is lowercase "voyant"; clear space = height of the "v".
- Board rule: brand colors for chrome (header, labels, backgrounds); **status colors stay functional** (green / amber / red) — signals beat brand on a production board.

### HxH Board app — 2026-10-20
- Canvas app **HxH Board** created in make.powerapps.com (env SVEND (default), Verxted tenant), data sources PLAYBOOK + HxH_Hourly (+ HxH_Shift).
- Control schema confirmed from Studio "View code": `Label@2.5.1`, `Classic/TextInput@2.3.2`, `Classic/DropDown@2.3.1`, `Classic/Button@2.2.0`, `Rectangle@2.3.0`, `Gallery@2.15.0` (Variant BrowseLayout_Vertical_TwoTextOneImageVariant_ver5.0).
- Paste-from-YAML works when a human copies the text; the Claude browser pane can't write the OS clipboard, so Eric pastes.
- v1 (1366×768) pasted; rows were empty because nothing loaded `colHours` on screen open.
- **v2 = HxH_Board_v2.pa.yaml (1920×1080)** — all fields from the original Data_Entry form:
  - Header: Line / Product (Size | Form) / Date / Shift dropdowns from PLAYBOOK; Refresh = the load routine; standard rate, UPH, crew, eff.
  - Shift strip: Start / End (half-hour list), shift hrs (derived), Lunch, Break, Job 1, Std crew (PLAYBOOK Total HC), Actual crew (amber if over std), Reason for extra headcount, planned-minutes check (row plan min vs lunch+break).
  - 12 hour rows: Hour, Job, HR TGT, CUM TGT, Counter (cum), HR ACT, RUN %, +/- CUM tile, BPM (amber if < T-max), Plan min, DT1 min + reason, DT2 min + reason, Safety OK/EVENT, Notes. Rows past shift end show "off" and carry 0 target (fixes the 97,200 inflated-target defect). Last partial hour gets a prorated target (10.5-hr shift → 11 slots, last = 30 min).
  - Hourly target = PLAYBOOK UPH × (slot min − planned min) / 60. 6:00–4:30 with 45 planned min = 585 run min = PLAYBOOK 9.75 hrs.
  - Bottom strip: FG scrap qty, scrap reason, scrap notes, below-speed reason, est. 3% scrap allowance.
  - Right tiles: Attainment % (thru last entered hour; green ≥100, amber ≥90, red), Units actual/target + shift target, OEE with A/P/Q, Downtime reported vs calculated + % reported + top reason (across DT1+DT2), Safety.
  - OEE mirrors the workbook: Avg BPM = avg of BPM>0; Uptime = Actual ÷ Avg BPM; Availability = Uptime ÷ (shift min − lunch − break); Performance = Avg BPM ÷ T-max (PLAYBOOK Rate); Quality = 1 − scrap ÷ actual; Calc DT = available − uptime.
  - Saves: every row edit upserts HxH_Hourly (key Line-yyyymmdd-S#-H##) then upserts HxH_Shift (key Line-yyyymmdd-S#) with the full Log_Shift column set — so the existing rollup math still applies.
  - Helper buttons btnSaveRow / btnSaveShift are 1×1 px transparent (not Visible=false) so Select() always fires.
  - Dropdowns whose Default comes from saved data only save when the value actually differs (avoids writing records just by viewing a shift).
- SharePoint changes for v2: new list **HxH_Shift** (Log_Shift columns); HxH_Hourly + HourlyTarget, HourlyActual, RunRatePct, DT2_Minutes, DT2_Reason, SlotMin.

### HxH Board v3 — operator cues + hover tips (2026-10-20)
- v2 confirmed working in Studio (Eric screenshot).
- **v3 = HxH_Board_v3.pa.yaml** — same layout, adds:
  - Fill-in coloring (workbook convention: yellow = manual entry). Counter + BPM: yellow once the hour starts, **red once it ends with no entry**, white when done. DT reason turns yellow if minutes entered without a reason (and vice versa). Job 1, Actual crew, FG scrap: yellow until filled. Extra-HC reason / scrap reason / below-speed reason turn yellow only when their condition is true. Optional boxes (job change, plan min, notes, lunch, break) are thin gray.
  - **NEXT ▸ banner** (shift strip, right): next hour owed + count of overdue hours; green "✓ UP TO DATE" when clear.
  - Column headers: ✎ (gold text) marks operator-entry columns; PLAN header shows minutes marked vs lunch+break (red when they don't match) — replaces the overflowing check label.
  - Tooltips (Tooltip property) on every input, every column header and every KPI tile — hover help. Note: hover doesn't exist on a touchscreen; the colors + banner carry the message there.
  - Legend in the bottom strip.
  - Fixes: title no longer wraps; Eff now computed as UPH ÷ (Rate × 60) (showed 1%).
- Generator kept in `generator/` (build.py + ux.py + ux_tail.py) — Python that writes the pa.yaml, so layout changes are code edits, not clicking.

### HxH Board v4 — bug fixes from first live test (2026-10-20)
- Error "Patch: [HxH_Shift] Field 'Title' is required": deleting/pasting controls in Studio wiped global variables (varShiftKey etc.), so the save ran with a blank key. **Fix:** save keys are now built from the dropdowns at save time, never from a variable; row save calls Refresh first if nothing is loaded.
- **Power Fx `Text(x, "0%")` does NOT multiply by 100** — 0.63 rendered as "1%". Every percent is now `Text(x * 100, "0") & "%"`.
- **Power Fx Text() has no Excel-style section formats** — "+#,##0;-#,##0;0" printed literally. Sign is added by hand: `If(v >= 0, "+", "") & Text(v, "#,##0")`.
- **Blank vs "" trap:** Coalesce(x, "") returns Blank, and `Blank <> ""` evaluated true → every DT box showed yellow. Use IsBlank() for "is it empty" tests.
- After any re-paste in Studio: Alt+click REFRESH (or F5 preview) before entering data.

### Flow 1 — HxH - Downtime Escalation (v1) — 2026-10-20
- HxH Board v4 published.
- Flow built in the new Power Automate designer (browser pane), flow id ee768e81-a5e4-4ea2-8bcd-ecc57512f210, owner Eric, status On.
- **Trigger:** SharePoint "When an item is created or modified" → MDI Sandbox / HxH_Hourly.
- **Trigger condition** (Settings tab): `@greaterOrEquals(add(coalesce(triggerBody()?['DT_Minutes'],0),coalesce(triggerBody()?['DT2_Minutes'],0)),15)` — flow only runs for hours with ≥15 min unplanned DT, so no noise runs.
- **Action:** Teams "Post message in a chat or channel" → Flow bot → Chat with Flow bot → eric.wolters@verxted.com. Message = line, shift, hour, total DT, reasons, escalation tier per the New Albany plan (15: Maint Tech + QC Lead; 30: Ops/Maint/Quality/Processing Suprs; 60: Ops/Maint/Quality/Compounding Mgrs), entered by.
- Tested: wrote a TEST row (35 min, Machine - Filler) via REST → run Succeeded in 4 s, ~40 s after the write. Test row recycled.
- Known v1 gaps (by design, fix in v2): re-fires on every edit of a row that's ≥15; per-hour not per-issue (no cross-hour accumulation); 2 h / 4 h tiers not in message yet; posts only to Eric.
- **How-to:** in the new designer, typing `@{expression}` into a text field (via the </> code view of the message box) is saved as a live expression — confirmed in the action's Code view (not escaped). Faster than clicking the fx button for every token.
- **Gotcha:** connection sign-in opens a popup; the Claude browser pane blocks popups it didn't get from a human click → Eric clicks "Sign in" once per new connector.

### Flow 1 v2 — contact-driven escalation, 60 min+ (2026-10-20)
**Rule (Eric):** only escalate at 60 min+; who gets notified comes from a SharePoint contact list.
- **Escalation_Contacts** list: Name (Title), Email, Role, Level (cumulative min: 60/120/240), ShiftSpecific (Yes/No), Shifts (multi-choice 1/2/3), Active. Seeded from the New Albany plan — Ops/Maint/Quality/Compounding Mgrs @60, QA + EMRA Directors @120, GM @240 — **inactive with blank name/email until Voyant fills them in**. Two active TEST rows (Eric @60, @120).
- **Escalation_Log** list: Title = ShiftKey|Reason|Level|Email, plus ShiftKey, Line, Shift, Reason, CumMin, Level, ContactName, ContactEmail, Role, NotifiedAt. One row per person per issue per level → nobody is notified twice.
- **"Cumulative" = per issue (same DT reason, DT1+DT2) across the shift.** One hour can't exceed 60 min, so 60/120/240 only make sense summed across hours.
- **Board v5** (HxH_Board_v5.pa.yaml): row save now also writes ShiftKey, EscReason (whichever of the row's two reasons has the larger shift total), EscCumMin. The app does the math; the flow only routes. Limitation: if both reasons in one hour cross a level at once, the second escalates on the next save.
- **Flow (same flow, rebuilt):**
  1. Trigger: HxH_Hourly created/modified; condition `@greaterOrEquals(coalesce(triggerBody()?['EscCumMin'],0),60)`; concurrency = 1 (no double-sends from parallel runs).
  2. Get contacts: `Active eq 1 and Level le @{triggerBody()?['EscCumMin']}`
  3. Get log: `startswith(Title,'<ShiftKey>|<EscReason>|')`
  4. To notify (Filter array): shift matches (not shift-specific, or Shifts contains this shift) AND no log row ending `|<Level>|<Email>`
  5. Notify each → Teams alert (Flow bot chat to contact email: level, line, shift, product, reason, cumulative min, hour, role, "communicate up and across") → Log notification (create Escalation_Log row).
- **Tested** with REST-written rows: 75 min → only @60 contact notified + logged; same issue to 130 min → @120 notified, @60 NOT re-notified. Test rows recycled.
- Not yet: email copy (needs Outlook connection sign-in by Eric); real contacts.
- Gotchas: Teams Recipient field is a people picker — gear icon → "Use dynamic content" to accept an expression. In the rich-text message box, use the ref'd "Toggle code view" before typing HTML or it gets escaped as text.

### List views + visual formatting (2026-10-20)
- Lists created by REST only showed Title — `createfieldasxml` Options 8 did NOT add fields to the default view on new lists. Fixed by setting each default view's fields explicitly (removeallviewfields → addviewfield in order) and a sort (ViewQuery MERGE).
  - Escalation_Contacts: Name, Role, Email, Level, ShiftSpecific, Shifts, Active — sorted by Level, Role.
  - Escalation_Log: newest first. HxH_Hourly / HxH_Shift: all columns in reading order, newest key first.
- JSON column formatting (field CustomFormatter): Level pills (60 amber / 120 orange / 240 red); Active (green Active / gray Off); ShiftSpecific (teal pills); HxH_Hourly RunRatePct % green/amber/red, SafetyEvent OK/EVENT, DT minutes bold red ≥15, EscCumMin pill; HxH_Shift OEE/A/P/Q % colored.
- Gotcha: a pill div stretches to row height — wrap in a flex div (`align-items:center; height:100%`) with a fixed-height inner span.
- Display names on HxH lists left as internal names on purpose: Power Apps formulas reference display names, renaming would break the board.

- PLAYBOOK formatted to match: Line (dark green), Size (aqua), Form (gray), Rate (teal "BPM"), Playbook Units/hr (teal pill), Eff %, Total HC ("crew"), role headcounts as small pills (blank when 0), changeover hours gray when 0, Productivity % green/amber/red, Active pill, Box Maker note italic.
- Gotchas: column formatting has **no round()** → use floor(x + 0.5). **toLocaleString() on a calculated number renders it as a date (12/31/1969)** → use toString(floor(Number(@currentField) + 0.5)).

### Tier 2 — lists (2026-10-20)
Decisions (Eric): Tier 2 is a **separate Power Apps app**; grain = **value stream or line, by shift**; QA, Ops crewing, Maintenance and NEWSPAPER each get their own panel/app ("QA needs its own view").
- **Lines** — Line (Title), ValueStream (seeded "(assign)" → Voyant to fill), DisplayOrder, Active. 15 lines: 201, 202, 203, 205, 207–213, 219, 220, 221, 221P.
- **T2_QA** — Summary, Line, ShiftDate, Shift, ProductForm, Job, ReworkQty, HoldQty, ScrapQty, Category, Disposition, NCRNumber, Notes, EnteredBy.
- **T2_Ops** — Key, Line, ShiftDate, Shift, ScheduledCrew, PresentCrew, Absent, Temps, Borrowed, OTHours, Notes, EnteredBy.
- **T2_Maint** — Issue, Line, ShiftDate, Shift, Equipment, DowntimeMin, WorkOrder, Status (Open / In progress / Waiting parts / Closed), PMsDue, PMsDone, Notes, EnteredBy.
- **Newspaper** — Action, Line, ValueStream, SQDCP, Source, Problem, Owner, OwnerEmail, RaisedDate, DueDate, Status (Open / In progress / Done / Canceled), Countermeasure, RefKey, ClosedDate. DueDate formatted to show OVERDUE.
- All views show every column with pills, same as the other lists.

### Tier 2 Board app v1 (2026-10-20)
- App "Tier 2 Board", tablet, **Settings → Display → Custom 1920 × 1080**. Data: HxH_Hourly, HxH_Shift, Lines, Escalation_Log, T2_QA, T2_Ops, T2_Maint, Newspaper. Screen1.OnVisible = `Select(btnRefresh)` (set before paste — shows red until the paste brings btnRefresh in).
- YAML: `T2_Board_v1.pa.yaml` (generated by `generator/t2.py`, 67 controls). Paste: right-click Screen1 → Paste.
- Header: View (All lines / Value stream / Line) → selection → Date (last 14 days) → Shift (All/1/2/3) → REFRESH.
- REFRESH loads every source into collections, then `Select(btnCalc)` builds `colRows` (one row per line) + `colTopDT` (downtime pareto via Ungroup/GroupBy).
- Main grid = SQDCP tiles per line: SAFETY · QUALITY (rework/hold/scrap) · DELIVERY (attainment) · COST (OEE) · PEOPLE (present/scheduled) · MAINTENANCE (open WOs, DT) · ESCAL. · ACTIONS (open/overdue). Colored tiles + tooltips.
- Bottom: top-downtime pareto + 4 total tiles. Right: open NEWSPAPER actions; tapping status cycles Open → In progress → Done (sets ClosedDate). "+ ACTION" overlay writes to Newspaper with Source = Tier 2 (action + owner required).
- Shift filter: HxH lists store Shift as number (`Text(Shift) = ...`), T2 lists as choice (`Shift.Value = ...`). Day filter `ShiftDate >= d && ShiftDate < d+1`.
- Next: department apps — QA first, then Ops crewing, Maintenance, NEWSPAPER register.
- **Re-sequenced by Eric:** T2 Board is the LAST deliverable (it rolls up everything else). Order now: HxH fixes → dynamic dropdowns → QA input list + app → Ops / Maint / NEWSPAPER inputs → T2 Board. App is created and saved (sized, data connected, OnVisible set) but not pasted — park it.

### Lookups list — dynamic dropdowns (2026-10-20)
- Decision: **every standard dropdown comes from one SharePoint list, `Lookups`**, not hard-coded in app formulas. Adding a reason = add a row; no app edit or republish.
- Columns: Value (Title), Category (choice, fill-in allowed: Downtime / Scrap / Speed loss / Extra headcount / Rework), Group (e.g. Machine, Materials), SortOrder, Active, Help.
- Rule: **retire with Active = No, never delete.** Records store the reason as text, so history and paretos keep their labels.
- Seeded from the HxH form: Downtime 18 (Machine / Materials / Quality Issue / People / Other), Scrap 9, Speed loss 11, Extra headcount 11. **Rework: empty — waiting on Voyant's standard rework reasons.**
- View: grouped by Category, sorted by SortOrder; pills for Category (brand tints), Group (gray), Active (green/gray).
- App pattern: REFRESH loads `colLk = Filter(Lookups, Active = true)`, then one collection per dropdown with a blank first row: `ClearCollect(colLkDT, {Value: "", Help: ""}, ForAll(Sort(Filter(colLk, Category.Value = "Downtime"), SortOrder), {Value: Title, Help: Help}))`. Dropdown `Items = colLkDT`.
- Follow-up: T2_QA Category/Disposition and T2_Maint Equipment are choice columns → switch to text fed by Lookups when we build those apps.

### HxH Board v6 — muted palette + Lookups dropdowns (2026-10-20)
- `HxH_Board_v6.pa.yaml` (generator `generator/build6.py` + `ux6.py`). Needs the **Lookups** data source added to the HxH app before paste.
- All four reason dropdowns (DT1, DT2, extra headcount, scrap, speed loss) now read Lookups.
- **Color rule: color = signal.** Green/amber/red/yellow only where they mean something (attainment, run %, +/- cum, below-speed BPM, safety EVENT, due/overdue inputs, next-hour banner, plan-minutes mismatch). Everything else went neutral:
  - column header bar teal → light gray; entry columns (✎) in dark ink, calculated columns gray; plan header turns red only on mismatch.
  - current-hour row aqua → pale tint.
  - Safety OK pills green → quiet gray (only EVENT shows red). 12 green pills a shift was noise.
  - KPI tiles Units / OEE / Downtime → light gray with dark text; Attainment and Safety tiles keep their status colors.
  - Title and STD text in header calmer; REFRESH dark teal.

### HxH Board v7 — no more Microsoft blue (2026-10-20)
- The blue on dropdowns is just the classic control's default theme, not locked. Overridden on every Classic/DropDown: `ChevronBackground` white, `ChevronFill` gray, `ChevronHoverBackground` light gray / `ChevronHoverFill` dark, `ChevronDisabled*`, `SelectionFill` dark teal + `SelectionColor` white (picked item in the open list), `HoverFill`/`PressedFill` aqua, `FocusedBorderColor` dark teal, `HoverBorderColor` gray.
- Text inputs: `FocusedBorderColor` dark teal, `HoverBorderColor` gray (was blue).
- Column-header ✎ rendered as a stray slash (not in Arial) → replaced with ●.
- Generator: `build6.py` now writes v7; legend in `ux_tail6.py`.
- Tip: an app-wide alternative is Settings → Theme, but the per-control properties win and travel with the YAML.

### HxH v7 bug → v8 (2026-10-20)
- Symptom: "No PLAYBOOK standard", shift hrs 0.0, red ✕ on REFRESH. Error on btnRefresh.OnSelect: "Incompatible types for comparison: Error, Text".
- Cause: Lookups' Title column was renamed to display name **"Value"**. Power Apps uses display names, so `Title` didn't exist, and a column named `Value` collides with the `Value` used by dropdowns / ForAll. The first broken line killed the whole REFRESH chain, so the PLAYBOOK lookup never ran. Not a PLAYBOOK problem.
- Fix: renamed Lookups Title display name to **"Label"**; formulas use `{Value: Label, Help: Help}`. v8 = v7 + that change.
- **Lesson: never give a SharePoint column the display name `Value` (or other Power Fx keywords like `Text`, `Date`, `Count`). And after renaming a column, refresh the data source in Power Apps (Data → … → Refresh).**
- One failing statement in an OnSelect chain stops everything after it — if a board suddenly loses "unrelated" data, check REFRESH first.

### HxH v9 — Actual Crew gates the sheet (2026-10-20)
- Eric: make ACTUAL CREW mandatory, gate the rest if needed.
- Every hour-row input's DisplayMode = Edit only when `InShift && Coalesce(Value(txtCrew.Text), 0) > 0`.
- **Exception: SAFETY stays live** (separate `INSAFE` = InShift only) — a safety event must never be blocked by paperwork.
- Overlay label `lblCrewGate` (white 82%, over the grid left of the SAFETY column) reads "▲ ENTER ACTUAL CREW TO START THE SHIFT"; Visible only while crew is blank/0. Sits after the gallery in the YAML so it's on top and blocks clicks.
- NEXT banner says "NEXT ▸ ENTER ACTUAL CREW" (yellow) until crew is in, then goes back to the hourly counter prompt.
- Gate is UI-level (the app); SharePoint still accepts rows without crew. Good enough for the floor; T2 can flag shifts with blank crew.

### HxH v10 — hour labels all 12-hour (2026-10-20)
- Bug: hour column read "13:00–2:00 PM". **In Power Fx, `h` without an AM/PM token formats as 24-hour.** Start time used "h:mm", end used "h:mm AM/PM".
- Fix: start = `Substitute(Substitute(Text(StartT, "h:mm AM/PM"), " AM", ""), " PM", "")` → "1:00–2:00 PM". Font 14 → 13 so "10:00–11:00 AM" stays on one line.
- Lesson: always include AM/PM in a Power Fx time format, then strip it if you want it shorter.
- v10 = v9 + this. Generator `build6.py` writes v10.

### QA rework — list + app v1 (2026-10-20)
Eric: QA logs rework units by line, by reason, for a shift-date + shift. Reasons are standard. Map to PLAYBOOK form and job number so issues can be cut by form and job. Same app gives QA a simple quality dashboard.
- **Lookups → Rework** seeded (Group = Quality): Wrong Lot Code, Dirty Bottles, Wrong Component Used.
- **QA_Rework list** (new, replaces T2_QA — T2_QA was empty and went to the site recycle bin; restorable). One row per entry:
  Ref (Title, auto key `Line-yyyymmdd-S#-hhmmss`), Line, ShiftDate, Shift (number, same as HxH), Size, Form, ProductForm, PlaybookKey (`Line|Size|Form`, same key as HxH), Job (required), Reason (text from Lookups), ReworkQty, Notes, ShiftKey (`Line-yyyymmdd-S#`, joins to HxH_Shift), EnteredBy.
  View: newest shift date first; pills for Line (dark), Size (aqua), Form (gray), Shift, Reason (dark teal); Job in monospace; qty bold "units".
- **QA Rework app** (`QA_Rework_v1.pa.yaml`, generator `generator/qa.py`, 1920×1080, one screen). Data: QA_Rework, Lookups, PLAYBOOK, HxH_Shift.
  - LEFT = LOG REWORK. Line / shift date (14 days) / shift. On change, loads that shift's HxH_Shift record and **defaults product and Job 1 from the HxH board**. Product dropdown = PLAYBOOK for that line. Reason = big tap tiles from Lookups (Rework). Units + notes. SAVE stays gray and disabled until product, job, reason and units > 0 are all filled. Below: this shift's entries with a total; ✕ delete only on your own entries.
  - RIGHT = QUALITY DASHBOARD. Filters: period (Today / 7 / 30 days), line, form. Tiles: rework units, **rework % of units made** (÷ HxH_Shift ActualUnits, same filters), entries, top reason. Bars: by reason (pareto), by form, by line (count + share). Top jobs table: job, line, form, top reason, units.
  - Color: neutral tiles and dark-teal bars. No green/red yet because there's no rework target. Add one and the % tile can go red/amber/green.
- Generator gotcha: `EXTRA` overrides (tooltips, required-field colors) only apply if registered *before* the control is emitted. qa.py runs its body twice: pass 1 registers, pass 2 emits.
- T2 Board must read QA_Rework (not T2_QA) when we come back to it.

### QA Rework v2 — error handling (2026-10-20)
- v1 showed "Invalid operation: division by zero" on kQRate before any data loaded. **Cause: `Sum()` of an empty table returns Blank, and `Blank() = 0` is FALSE in Power Fx**, so `If(m = 0, …)` didn't catch it.
- Fix pattern: `Coalesce(Sum(...), 0)` and test `<= 0`. The same guard is on the bar % and share (`If(mx > 0, Qty / mx, 0)`), the shift total and the "Loaded" stamp ("Not loaded — press REFRESH").
- Writes wrapped: `IfError(Patch(...), Notify("NOT SAVED — " & FirstError.Message, Error), <success chain>)`. The form only clears after a confirmed save, so a failed save never eats the operator's entry. Delete works the same way.
- Loads wrapped: each ClearCollect in REFRESH has IfError → Notify naming the list that failed.
- Reason tiles: before reasons load, the empty template tile showed as "selected" (Blank = Blank). Now `!IsBlank(varReason) && …`. Added a hint label when no reasons are loaded.
- **Tested 2026-10-20 4:41 PM:** entry saved (209 / 10 oz Body Wash / job 12345 / Dirty Bottles / 2,400). Shift list, tiles, reason/form/line bars and top jobs all populated. Rework % shows "—" because that shift has no HxH_Shift record yet (expected).
- **Decision (Eric): Ops crewing comes from the HxH board** (Actual Crew + extra-headcount reason, now mandatory). No separate Ops app; the T2_Ops list is unused (empty, kept for now).
- **OnVisible reminder (QA):** pasted YAML only brings controls; screen properties don't come with it. Set Screen1 → OnVisible = `Select(btnQRefresh); Select(btnQCtx)` by hand.

## Lessons / how-to notes

- **Power Apps containers:** vertical container stacks, horizontal container rows. Put a horizontal container inside a vertical one for side-by-side. Inside containers, X/Y are ignored — use Flexible width / Fill portions / Align.
- **Diamond icon = premium**, not a permission problem. Dataverse tables are premium in Power Apps; we use SharePoint via Connectors.
- **Dropdown Items** can be a literal table: `["1","2"]`. `DropDownSample` is a placeholder.
- **Don't hand-build repeating rows.** Gallery = one template, N rows from Items.
- **Screen size:** set Custom size in Settings → Display *before* pasting a layout built for it (TV = 1920 × 1080).
- **Paste code:** controls can be copied/pasted as YAML. Right-click a control → Copy code to see the exact schema; paste YAML into Tree view to create controls.


### Troubleshooting system (living TS guide) — 2026-10-20
**Eric's intent:** a living troubleshooting guide ranked by real fixes. When maintenance fixes a machine and the countermeasure already exists, they just tap it — that's an occurrence that bumps its rank, and if the fix was operator-level it's flagged "operator could have fixed it". If the fix doesn't exist, maintenance documents it **while fixing** (step photos), linked to concern + cause. Operators get a read-only "binder" to look things up.
**Decisions:** new fixes go **live immediately** (no approval). **Operators do not log occurrences** here. Equipment comes from a list (Lookups → Equipment for now, Assets list for specific machines). **Maintenance uses phones; QR codes on machines gate entry** (operators don't have M365 accounts, so they can't open the maintenance app). Don't pre-load the 205 guide content — start empty.
**Source format followed:** 20260616_NAL_205 TG Labeler (concern → numbered cause/countermeasure in try-order with normal range → "if still not fixed, request maintenance [205.x.x]"; JEL/OPL photo procedures referenced from countermeasures; 4C TA form = Concern / Cause / Countermeasure / Check). The phone "new fix" screen is a digital 4C form. Removes the "send photos to OpEx → OpEx updates guide" bottleneck (troubleshooting cycle steps 5–6).

**Lists (MDISandbox):**
- **Assets** — Asset (Title), Line, EquipType, Model, AssetTag, Active, Notes. Equipment register, empty. QR codes and yellow tags hang off this.
- **TS_Issues** — Concern (Title), Code, EquipType*, Line (blank = all lines), Asset, Appearance, Escalation, Active, CreatedVia, AddedBy.
- **TS_Fixes** — Cause (Title), IssueID*, Code, Countermeasure*, Check, NormalRange, DoneBy (Operator/Maintenance/Engineering), SeqOrder, ProcID, Active, CreatedVia, AddedBy.
- **TS_Procedures** — Procedure (Title), DocType (JEL/OPL/Quick fix), Code, EquipType, Line, Asset, KeySafety, TimeEst, Active, CreatedVia, AddedBy. (One procedure can be shared by several fixes, as the JELs are in the 205 guide.)
- **TS_Steps** — Instruction (Title), ProcID*, StepNo*, KeyPoint.
- **TS_Occurrences** — Ref, OccurredAt, Line, Asset, EquipType, ShiftDate, Shift, ShiftKey (joins HxH), IssueID, FixID, Outcome (Existing fix / New fix added / Not resolved - escalated), FixLevel, OperatorCouldFix, DowntimeMin, LoggedBy, Notes, **WorkOrder, YellowTagRef, NewspaperRef (integration hooks)**.
- **TS_Photos** (document library) — ProcID, StepNo, IssueID, OccurrenceID, Kind (Step/Before/After/Appearance/**Yellow tag**), Caption, TakenBy.
- **Lookups → Equipment** added: Filler, Capper, Labeler, Coder, Conveyor, Tape machine, Print & apply, Unscrambler, Utilities, Other (same names as the HxH "Machine - X" downtime reasons).
- Gotcha: a text column named "Author" collides with SharePoint's built-in Author (Created By) → it became internal Author0; display renamed to **AddedBy**.

**Ranking:** in the apps, fix rank = number of occurrences with that FixID in the last 90 days (ties → SeqOrder). Concern rank = occurrences for that IssueID in 90 days. Computed live, not stored.

**Flow "TS - Upload Photo"** (id 10aa7d3a-1e08-4429-9c01-9b217b5ff337). Trigger: Power Apps (V2) with inputs Photo (file), FileName, ProcID, StepNo, IssueID (numbers), Kind, Caption, TakenBy (text) → keys file, text, number, number_1, number_2, text_1, text_2, text_3. Create file in /TS_Photos (name = utcNow stamp + FileName, body = `base64ToBinary(triggerBody()?['file']?['contentBytes'])`) → Update file properties (ProcID, StepNo, IssueID, Kind, Caption, TakenBy) → Respond photoid. Called from Power Apps as `'TS-UploadPhoto'.Run({contentBytes: addX.Media, name: "x.jpg"}, fileName, procId, stepNo, issueId, kind, caption, User().Email)`.
- Lesson: Power Apps can't write files into SharePoint itself — the standard route is a V2 flow with a File input. In the new designer, `"@{expr}"` in a binary field turns the file into a base64 string; use a bare `@base64ToBinary(...)`.

**Apps (YAML, generators in generator/):**
- `TS_Maintenance_v1.pa.yaml` (mt.py) — **phone 640×1136**. One screen with steps driven by `varStep`: where (line + machine tiles; QR params `line`, `equip`, `asset` skip ahead) → issue (concerns ranked, search, + new concern) → fix (ranked cause/countermeasure cards; "✓ THIS FIXED IT", "📷 STEPS", "NONE OF THESE — ADD NEW FIX", "NOT RESOLVED — ESCALATE") → new (digital 4C: concern + appearance photo if new, cause, countermeasure, check, normal range, who can do it) → steps (document while fixing: instruction, key point, photo; each SAVE STEP writes TS_Steps + uploads the photo) → log (downtime min required, WO, notes; amber banner when an operator-level fix was used) → done. New issue/procedure/fix rows are created at "START STEP PHOTOS" with Active = false and flipped live on SAVE, so abandoned drafts never show. Disabled "YELLOW TAG A PART (coming soon)" button marks the yellow-tag hook.
  - Control versions from Studio "View code": **AddMedia@2.2.1, Image@2.2.3**. Tip: Tree view → right-click a screen → View code shows the exact YAML schema.
- `TS_Binder_v1.pa.yaml` (bd.py) — **operator binder, 1920×1080, read-only**. Line + search; machine list with concern counts; concerns ranked by 90-day occurrences; selected concern shows appearance photo and fixes in try-order with "YOU CAN DO THIS" (operator) vs "CALL MAINTENANCE" pills; "📷 SHOW STEPS" opens a full-screen step-photo overlay; escalation text at the bottom. Param `line` / `equip` supported for links from HxH.

**Open ends / next:**
- **Yellow tags** (next build): use Assets for the component's machine, TS_Occurrences.YellowTagRef + TS_Photos Kind "Yellow tag" + NewspaperRef for parts/actions. Planned list: YellowTags (asset, component, condition, photo, status: Tagged → Parts ordered → Parts in → Repaired → Verified, PO/part #, ETA, owner).
- QR codes: once the maintenance app is published, generate one per line × machine (app link + `?line=205&equip=Labeler`).
- HxH: add a TROUBLESHOOT button → Launch the binder with `line` and `equip` from the DT reason (needs the binder's app ID).
- Tier 2: top concerns, "operator could have fixed it" count, downtime by concern.
- **Tested end to end 2026-10-20 ~5:24 PM (Eric, phone):** new concern "Labels Wrinkling" (209 Labeler) + appearance photo → fix "Teflon Worn" (Operator) → step 1 with photo → occurrence logged (New fix added, 16 min, ShiftKey 209-20261020-S2). Both photos landed in TS_Photos tagged correctly (I1-appearance; P1-S1). Fix and procedure flipped to Active on save. Flow name in Power Apps resolved as 'TS-UploadPhoto'.

## Where we left off — end of Day 1 (2026-10-20, 5:45 PM)
**Working and tested:** HxH Board v10 (Lookups dropdowns, muted palette, crew gate, 12-hr times) · Escalation flow (60 min+, contact-driven) · QA Rework app + dashboard · Troubleshooting system (lists, photo flow, TS Maintenance phone app, TS Binder).
**Built but parked:** Tier 2 Board (last deliverable — needs re-pointing T2_QA → QA_Rework, crewing from HxH_Shift, maintenance from TS_Occurrences).
**Next session (hotel):**
1. Web links for TS Maintenance + TS Binder → QR label sheet (line × machine) + HxH TROUBLESHOOT button.
2. Yellow tag system (hooks already in TS_Occurrences / TS_Photos / phone app).
3. NEWSPAPER register app (actions from escalations, QA, TS "not resolved", yellow tags).
4. Tier 2 Board rebuild on top of all of the above.
5. Rollout pack for Voyant: what to fill (Lines.ValueStream, Escalation_Contacts, Assets, Lookups), how to share apps, and how to move from the Verxted sandbox to Voyant SharePoint.

### Housekeeping + groundwork (2026-10-20 evening)
- **T2_Ops** (empty, unused — crewing comes from HxH) → site recycle bin. (T2_QA went earlier.) Both restorable.
- **Newspaper.Source** choices extended: + Troubleshooting, Yellow tag, Process confirmation, HxH (kept Escalation, Tier 2, Board, QA, Maintenance, Ops, Other). Every module tags its actions here.
- **TS_Photos** got **Module** (Troubleshooting / Process confirmation / Yellow tag / QA / Newspaper, default Troubleshooting) + **RefID** columns. Non-breaking groundwork for one shared photo library; existing 2 photos tagged Troubleshooting. The flow still sets the TS columns; when we generalize, the flow gains Module + RefID inputs and the TS app call gets two extra arguments.
- **People** list (new): Name, Email, Role (Operator lead … GM, OpEx), Tier, Shifts (1/2/3 multi), Lines ("All" or "205,209"), Area, Active, Notes. Seeded Eric (TEST). For PC audit layers, action owners, later escalation contacts.
- **MDI_Config** list (new): Setting / SettingValue / Kind / Notes. Seeded app-link slots (App_HxH, App_QARework, App_TSMaintenance, App_TSBinder, App_Tier2 — **paste web links here**), flow IDs (upload photo, escalation), thresholds (escalation 60 min, TS rank window 90 days), Site_URL. Apps will read links from here instead of hard-coding (`LookUp(MDI_Config, Setting = "App_TSBinder").SettingValue`).
- **generator/qr_labels.py** — QR label sheets for any app: `--url <web link> --lines 205,209 --equip Labeler,Capper` or `--csv stations.csv` (line,equip,asset,label) → PDF, 8 labels per Letter page with cut lines, Voyant colors. Appends `?line=&equip=&asset=` to the link. Tested.
- Test data still in place on purpose (demo): escalation TEST contacts (Eric @60/@120), QA test entry (2,400 Dirty Bottles), TS test (Labels Wrinkling / Teflon Worn + 2 photos). Clear before go-live.
- Still to do in housekeeping: remove duplicate HxH_Hourly_1 data source in the HxH app; archive old YAML versions (v1–v9) into an /archive folder (needs a manual move or a device shell); fold generators into one common.py.

### Naming conventions (from here on)
- Lists: `MODULE_Thing` (HxH_Hourly, TS_Fixes, QA_Rework); shared lists plain (Lines, Lookups, People, Assets, Newspaper, MDI_Config). New: PC_* for process confirmation, YT_* for yellow tags.
- Title column always renamed to a real display name; **never** "Value", "Text", "Date", "Author" (Power Fx / SharePoint collisions).
- Keys: shift `Line-yyyymmdd-S#`, hour `…-H##`, playbook `Line|Size|Form`.
- Choice/text: anything a user may add values to → text column fed by Lookups; fixed state machines (Status, Outcome) → choice.
- Apps: one screen per app where possible, step/panel visibility by variable; REFRESH button = load everything; Screen OnVisible = Select(REFRESH); helpers are 1×1 transparent buttons.
- Flows: "MODULE - Verb Noun" (HxH - Downtime Escalation, TS - Upload Photo).
- Files: `<App>_v#.pa.yaml` + generator in /generator; log every change here.

### Standard work + process confirmation (T-cards) — 2026-10-20 night (hotel)
**Eric's intent:** process confirmation cards = standard work audits, in the spirit of the "MDI Accuracy & Completeness Audit" T-card (front: HxH 1–3, back: SQDC 1–3; each item = name + "Good:" definition + reference photo + YES/NO + "if No, what was missed?"; card tab color green/red). Needs an **add-card feature** that documents the standard and mirrors its photos, and a **phone side (QR)** where cards are completed step by step with photos, each linked to a specific standard. Generic tonight, tailor to Voyant tomorrow. Keep Voyant branding. **Loop in standard work management** (Voyant already keeps SW on SharePoint) — build the whole system as an asset to introduce over time.

**Model:** Standard (SW_Standards) → Elements with what GOOD looks like + reference photo (SW_Elements + photos) → Card picks elements (PC_Cards + PC_CardItems) → Audit (PC_Audits) → item answers (PC_Results) → No = finding photo + NEWSPAPER action.
**Lists (MDISandbox):**
- **SW_Standards** — Standard (Title), DocNo, Rev, DocType (SWIS/JEL/OPL/Centerline/Changeover/Checklist/Other), Line, Area, EquipType, Status (Draft/Active/Under review/Retired), Owner, OwnerEmail, EffectiveDate, ReviewDue, **DocLink (URL of the controlled doc in their SharePoint SW library)**, Purpose, KeySafety, PPE, TimeEst, AddedBy. View: REVIEW DUE shows red; DocLink renders "Open doc ↗".
- **SW_Elements** — Element (Title), StandardID*, ElementNo*, GoodLooksLike, Why, PointType (Safety/Quality/Knack/Ergo/Info), TimeSec, Active.
- **PC_Cards** — Card (Title), StandardID, Line, Area, Tier, Frequency (Every shift/Daily/Weekly/Monthly), Shifts (multi), Instructions, Active, AddedBy.
- **PC_CardItems** — Check (Title), CardID*, ItemNo*, ElementID, GoodLooksLike, PhotoOnNo, Active.
- **PC_Audits** — Ref, CardID, StandardID, Line, Area, ShiftDate, Shift, ShiftKey (joins HxH), Tier, AuditedBy, AuditorName, Observed, StartedAt, CompletedAt, Result (Pass/Fail), Score, NYes, NNo, NNA, Notes.
- **PC_Results** — Ref, AuditID, CardID, ItemNo, ElementID, Answer (Yes/No/N/A), Missed, ActionCreated, NewspaperRef, Line, ShiftKey.
- **SAMPLE seeded** from the T-card: standard SW-MDI-001 "MDI board: Hour x Hour + SQDC completeness" (Draft) with 6 elements (HxH 1–3, SQDC 1–3, good/why text) and card "SAMPLE — MDI Accuracy & Completeness Audit" (Tier 1, every shift, shifts 1+2, 6 items). The 6 T-card photos are resized in **NEW ALBANY/sample_photos/SW1-E1…E6.jpg** — load them through SW Manager (element → add photo → save) as its first test. NOTE: they're from the template deck, not Voyant — replace with Voyant photos.

**Photos — one library decision:** the hotel connection wouldn't load the flow designer, so instead of a new flow, **TS_Photos is now the shared MDI photo library** (Module + RefID columns added earlier; Kind gained Standard + Finding; Module gained Standard work). Apps call the existing **'TS-UploadPhoto'** flow, then tag the returned photo: `Patch(TS_Photos, LookUp(TS_Photos, ID = Value('TS-UploadPhoto'.Run(...).photoid)), {Module: {Value: "Standard work"}, RefID: <id>})`. The flow's ProcID input carries the RefID; StepNo = element/item no. Empty MDI_Photos library recycled. (Later: rename flow/library to MDI_ when convenient — Power Apps binds by ID.)
- Latest photo wins: apps show `First(SortByColumns(Filter(photos, StepNo = n), "Created", Descending))` so re-shooting a standard photo replaces it everywhere (cards mirror the standard automatically).

**Apps:**
- `SW_Manager_v1.pa.yaml` (sw.py) — 1920×1080, three tabs:
  - **STANDARDS**: searchable library (status pills, element count, REVIEW DUE flag), standard editor (title, doc no, rev, type, status, line, area, equipment, owner, review due, link to controlled doc with ↗ open, purpose, key safety), elements list with GOOD/WHY + photo, element editor with photo add/replace.
  - **PC CARDS**: card list (green/gray tab = active), card editor (title, standard, tier, frequency, line, area, shifts, active, instructions), **item picker = tick the standard's elements** (with their photos), save writes PC_CardItems in element order; QR link for the card (from MDI_Config App_PCAudit + `card=<ID>`) with COPY.
  - **RESULTS**: period/line filters; audits done, pass rate (green ≥90 / amber ≥75 / red), avg score, findings, actions; **adherence by card** (done vs expected from frequency × shifts × days); most-missed elements.
  - Data: SW_Standards, SW_Elements, PC_Cards, PC_CardItems, PC_Audits, PC_Results, TS_Photos, MDI_Config, Lookups + flow TS - Upload Photo. OnVisible: `Select(btnSRefresh)`.
- `PC_Audit_v1.pa.yaml` (pc.py) — phone 640×1136. QR `?card=<ID>` jumps straight in (or pick from list: red tab DUE / green DONE ✓ for this shift). Item by item: progress bar, element name, type pill, **standard photo**, GOOD box, big YES / NO / N/A; on NO → "what was missed" (required), finding photo, create-action toggle (default on). Review screen (all answers, edit any, observed crew, notes) → SUBMIT writes PC_Audits + PC_Results + NEWSPAPER actions (Source = Process confirmation, SQDCP Safety if the element is a Safety point else Quality, due +7 days, RefKey = audit ref + item) + finding photos (Module Process confirmation, RefID = audit ID). Done screen = the T-card flips GREEN (pass) or RED (fail).
  - Data: PC_Cards, PC_CardItems, PC_Audits, PC_Results, SW_Elements, TS_Photos, Newspaper, Lines + flow. OnVisible: `Select(btnPRefresh)`.
- MDI_Config: added App_PCAudit and App_SWManager slots.

**Tomorrow (Voyant tailoring):** look at their SharePoint standard work library (columns, doc numbering, approval) → map DocLink/DocNo or sync with a flow; real cards (MDI audit + line-specific standards); People list → who audits at which tier; QR labels per card/station; Tier 2 adherence tile.

## 2026-10-21 — NEWSPAPER app + deploy package
### NEWSPAPER app v1 (`Newspaper_v1.pa.yaml`, generator np.py) — 1920×1080
- Filters: line, source, SQDCP, status (default Open + In progress), search, OVERDUE ONLY, MINE (OwnerEmail = me). `?line=` param.
- KPI tiles: open, overdue (red when > 0), due next 7 days, closed last 7 days, avg days to close (30 d).
- List sorted overdue first, then by due date. SQDCP letter, action + problem, line, source, owner (red "— unassigned"), due (red LATE / amber ≤ 2 days), **status pill tap-to-advance** Open → In progress → Done (sets ClosedDate) → Open.
- Edit panel: action, problem, countermeasure, owner (People list → sets OwnerEmail), due (yyyy-mm-dd), line (ValueStream filled from Lines), SQDCP, source, status buttons, add photo (Module Newspaper, RefID = action ID). Photos panel also shows the **process-confirmation finding photo** an action came from (parsed from RefKey `PC…-I<item>` → PC_Audits.Ref).
- New actions get RefKey `N<timestamp>`, RaisedDate now, default due +7 days.
- Data: Newspaper, People, Lines, TS_Photos, PC_Audits + flow. OnVisible `Select(btnNRefresh)`.

### Deploy package (`deploy/`, also `MDI_Deploy_Package.zip`)
- **provision_mdi.js** — browser-console provisioner generated from the live sandbox schema: 24 lists/libraries, every column (incl. calculated), pill formatting, default views, seed data (Lines 15, Lookups 62, MDI_Config 12 with links blanked, Escalation_Contacts 7 role rows, PLAYBOOK 37). Idempotent.
  - **Tested** by provisioning a fresh site `/sites/MDIDeployTest`: all 24 lists, seeds, views OK. Found + fixed: exported calculated-column formulas use internal names → SharePoint rejects them on create; package rewrites formulas to `[Display Name]`. PLAYBOOK calcs verified (e.g. UnitsPerHour 2250, TotalHC 6). The test site can be deleted.
  - Export trick: schema + seed gzipped + base64 in the browser (213 KB → 21 KB) to move it to the build container.
- **apps/** current versions of all 8 apps (T2 parked). **generator/** made path-relative; regenerating reproduces the YAML byte-for-byte.
- **flows/** step-by-step rebuild specs with every expression for HxH - Downtime Escalation and TS - Upload Photo.
- **tools/qr_labels.py**. **README.md** = deployment guide: prerequisites, 6 steps (lists → plant data → flows → apps table with sizes/data sources/OnVisible → links + QR → go-live checklist), rollout order, architecture keys, gotchas.
- T2_Maint list (unused) left out of the package.
- **Flow not listed in Studio (SW Manager / PC Audit):** "TS - Upload Photo" was On and in the right environment but didn't appear in the Power Automate → Add flow list for the new apps. Fix: **Save As → "MDI - Upload Photo"** (copy is created OFF → turned it on). SW Manager, PC Audit, Newspaper regenerated as **v2** calling `'MDI-UploadPhoto'`. TS Maintenance in the sandbox stays on the TS flow (works); the **deploy package now uses one flow, MDI - Upload Photo, for all apps** (TS_Maintenance_v2 in deploy/apps). Reminder: flows are added from the **Power Automate pane → + Add flow**, not Add data — search the list if it isn't shown.
- **Root cause found:** the new Studio "Add flow" pane says *"Add a flow from a solution in this environment"* — it lists **only solution-aware flows**. Our flows lived in My flows (outside Dataverse), so none showed (TS Maintenance got its flow before the pane changed). Fix: created solution **MDI** (CDS Default Publisher) → Add existing → Cloud flow → Outside Dataverse → **MDI - Upload Photo** → Add (it brought a SharePoint connection reference with it). Deploy README updated: build flows inside the MDI solution.

### Packaging + log consolidation (2026-10-21)
- Added **Part A — Master summary** at the top of this file: architecture, module status, app build settings, lists, flows, keys, consolidated gotchas, open items and the file index. The Day-0 plan is now marked superseded (Part B).
- Built **NEW_ALBANY_MDI_Full_Package_2026-10-21.zip**, covering everything in the NEW ALBANY folder, organized as described in A9. Stale duplicates (v1 apps calling the old flow, `02_TS - Upload Photo.md`) sit in 99_Archive or were dropped from deploy/. The package's copy of deploy/ is clean (v2 apps only).
- Generators in the container and in NEW ALBANY/generator were verified identical. np.py is now included (it was missing from the laptop's generator folder).
- Added **KENNY_HANDOFF_for_Copilot.md** at Eric's request. It is written for Kenny's Claude and covers 21 manual steps (access, provisioning, plant data, flows, app paste/publish, go-live), 10 call-Eric triggers, a message template, and what Claude may and may not do.
- **Voyant's email filter blocked the package because it contained Python files.** The shared package is now **script-free**:
  - no generator/ or tools/ folders;
  - the provisioner ships as `provision_mdi.js.txt` (content unchanged, pasted from Notepad);
  - QR labels are made with Edge → Create QR code, or Eric generates PDFs with qr_labels.py.
  - The generators stay on Eric's side only: NEW ALBANY/generator on the laptop, and the container.

## 2026-10-21 — Tier 2 Board v2
**Eric's direction:**
- Default to yesterday's full day.
- Layers: full floor, then drill down by line and by domain (SQDC), giving more and more detail.
- Show the trend.
- Populate test data in the sandbox for a demo.

**Demo data (MDISandbox), tagged T2TEST** (see A8 for how to clear it):
- **Coverage:** 5 lines (205, 209, 210, 211, 219) in 2 value streams, Oct 11–20, both shifts.
- **Rows:** 99 HxH_Shift, 990 HxH_Hourly, 22 QA_Rework, 56 TS_Occurrences, 6 Escalation_Log, 69 PC_Audits, 21 PC_Results, 25 Newspaper. Also 5 TS concerns with 8 fixes.
- 209 S1 on 10/20 was skipped so Eric's real test row is not duplicated. That row reads 0 units, so 209 shows red on 10/20.
- **Line personalities:**
  - 205: steady.
  - 209: filler downtime, escalations, improving.
  - 210: labeler, getting worse.
  - 211: dirty-bottle rework.
  - 219: short crew, PC audits skipped.
- MDI_Config gained 8 T2_* threshold rows.

**App:** `T2_Board_v2.pa.yaml` (generator `t2v2.py`, 409 controls). Size 1920×1080. Data sources are listed in A3. OnVisible: `Select(btnRefresh)`.
- **Header:**
  - Value stream filter.
  - Day reviewed (default yesterday; 30 days back).
  - Shift (All/1/2/3).
  - RUNNING LINES / ALL LINES toggle. Running = lines with any HxH data in the 7 days shown.
  - REFRESH.
- **Breadcrumb:** FLOOR › LINE x › DOMAIN.
- **Domains (8):**
  - Safety: HxH safety events.
  - Quality: rework % of units (QA_Rework), plus FG scrap.
  - Delivery: attainment.
  - Cost: target-weighted OEE.
  - People: actual vs standard crew.
  - Maintenance: downtime minutes, TS occurrences, operator-fixable fixes, escalations.
  - Process confirmation: audits done vs due (cards × shifts run), failures.
  - Actions: Newspaper items open at the end of the day, and how many were overdue.
- **Color:** thresholds come from MDI_Config. Gray = no data.
- **Layer 1 — FLOOR:**
  - A FLOOR totals row, then one row per line, sorted by value stream.
  - Each tile: value + sub-line + **7 trend blocks**. The oldest is on the left; the outlined block is the day reviewed.
  - Bottom: top downtime, rework reasons and TS concerns for the day.
  - Tap a line → LINE. Tap a domain heading → DOMAIN. Tap a tile → CELL.
- **Layer 2a — LINE:** 8 domain cards, each with a 7-day bar trend. Below them, an hour-by-hour strip for the day: target vs actual bars, downtime minutes and reason; a red cap marks a safety event.
- **Layer 2b — DOMAIN:** every line ranked side by side for that domain (tile, bar, sub-line, 7-day blocks), plus that domain's pareto across lines for the day. Rework, downtime, scrap, staffing, TS concerns, most-missed PC items, open actions by source.
- **Layer 3 — CELL (line × domain):**
  - Headline value.
  - 7-day trend bar chart.
  - The records behind it over 7 days, with a status stripe: shift records with A/P/Q, rework entries, TS occurrences with fix and outcome, audits, actions.
  - The line's 7-day pareto for that domain.
- **Right panel, on every layer:** Newspaper open actions filtered to the current scope. On a domain, it filters by SQDCP. Tap status to advance; + ACTION saves with Source = Tier 2.

**How it works:**
- REFRESH loads 7 days ending on the day reviewed. Hourly data is loaded for the reviewed day only, plus downtime hours and safety hours for all 7 days, to stay under the 2,000-row limit.
- btnCalc builds `colDaily` (line × day: all raw sums plus txt/sub/st/bar per domain), `colTot` (floor per day), `colFloor` (the reviewed day plus trend strings) and `varTot`.
- Drill-down layers are plain formulas over these collections, so taps only set varLayer, varLine and varDom. Nothing reloads.

**Not yet tested in Studio.**
- Watch for: Switch branch type mismatches (tables built per domain), `in Split(...)` for card line matching, and WrapCount galleries.

### Tier 2 v3: Downtime domain + events (2026-10-21)
**Feedback from Eric:**
- v2 pasted and renders. The cell layer for 211 × Quality matches the seed.
- Downtime and events were missing, and they are among the most important things on the board.
- There was a rendering bug in the upper-left corner.

**Changes:**
- **New DOWNTIME domain**, between Delivery and Cost (9 domains now).
  - **Value:** unplanned minutes. **Sub-line:** number of events, the longest event, and the escalation level reached.
  - **Red:** any escalation, or 60+ min per shift. **Amber:** 30+ min per shift. Both are MDI_Config settings (`T2_DTAmber` = 30, `T2_DTRed` = 60), added to the sandbox and the deploy seed.
- **Event definition:** one line, shift and downtime reason, with minutes added across the hours it touched (DT1 and DT2 slots). This matches the escalation flow's cumulative-per-issue rule. Each event carries:
  - the hours it spanned;
  - the escalation level (Escalation_Log, matched on ShiftKey + Reason);
  - whether a TS occurrence was logged (TS_Occurrences, matched on ShiftKey + equipment type in the reason).
- **Floor:** the bottom-left chart is now **DOWNTIME EVENTS (biggest first)**: line, shift and hours, reason, minutes, and an L1/L2 badge.
- **Line:** 9 domain cards in a 5 × 2 grid. The 10th slot holds that line's downtime events for the day.
- **Cell (line × Downtime):** every event over 7 days, plus a pareto by reason.
- **Domain (Downtime):** all lines side by side, plus the downtime-by-reason pareto.
- **Maintenance:** now troubleshooting-only (occurrences, operator-fixable, not fixed), so downtime isn't counted twice. Cost's sub-line is scrap only.
- **Delivery pareto:** now speed-loss reasons, weighted by units short.

**Fixes:**
- **Breadcrumb:** the domain button was rendering at x = 0 on top of FLOOR. `btn()` applies box() after `extra`, so an X override is lost. Now two fixed buttons (bcDomA for the domain view, bcDomC for the cell view). Lesson: use separate controls rather than X overrides on buttons and rects.
- **Pareto:** the value label overlapped the bar because the bar and the label each computed the maximum inside the template. Now `With({tb: items}, AddColumns(tb, P, N / Max(tb, N)))`, and both use ThisItem.P.
- **Header scope text:** split onto two lines so "shift 1" no longer wraps.

### Tier 2 demo seed: downtime events (2026-10-21)
Added 8 breakdowns that span several hours, weighted to 10/20 because that's the default view. All tagged T2TEST.

The affected HxH_Hourly rows were rewritten in place: reason, minutes, StillDown, EscReason/EscCumMin, HourlyActual and CumulativeUnits. Their HxH_Shift totals (DT, actual, A/P/Q/OEE) were recomputed to match.

**Events**

| Line | Date | Shift / hours | Reason | Minutes | Escalation | TS occurrences / notes |
|---|---|---|---|---|---|---|
| 209 | 10/20 | S2 H3–6 | Filler | 155 | L1 + L2 | Not resolved → fixed (O-ring) |
| 210 | 10/20 | S1 H2–4 | Labeler | 95 | L1 | Operator-fixable |
| 219 | 10/20 | S1 H1–2 | No People | 75 | L1 | — |
| 211 | 10/20 | S2 H7–8 | Components | 65 | L1 | — |
| 205 | 10/20 | S1 H6–7 | Capper | 45 | none (amber) | Operator-fixable |
| 209 | 10/19 | S1 H8–10 | No Bulk | 150 | L1 + L2 | — |
| 210 | 10/18 | S2 H5–6 | Labeler | 80 | L1 | — |
| 205 | 10/16 | S2 H2–3 | Coder | 65 | L1 | — |

**Also added:**
- A near miss on 210 10/20 S1 H3.
- 6 Newspaper actions tied to these events: escalation follow-ups, operator retraining, the near-miss fix, and staffing coverage.

**10/20 downtime per line after the seed:**

| Line | S1 | S2 |
|---|---|---|
| 205 | 64 | 0 |
| 209 | 0 (real test row) | 177 |
| 210 | 124 | 87 |
| 211 | 0 | 79 |
| 219 | 90 | 59 |

### Tier 2 v4: targets on the bar charts (2026-10-21)
**Eric's request:** add targets as lines on the bar charts, based on shift length and the input lists. PLAYBOOK becomes data source #15.

**Targets per domain.** The bar shows the value; a dark tick or line shows the target. Each target is computed per line per day, so the line steps where the product mix or shift length changes.

| Domain | Target |
|---|---|
| Delivery | **Plan = Σ shifts PLAYBOOK.UnitsPerHour × (PlannedShiftHrs − (LunchMin + BreakMin) / 60)**. PlannedShiftHrs falls back to PLAYBOOK.AvailableHrsShift; with no PLAYBOOK match, the board's TargetUnits is used. **Attainment is now actual ÷ plan** (fixes Day-0 defect #1, the 12-row inflated target). Example: Eric's real 209 S1 test row (12 h, 30 + 15 min) gets a plan of 11.25 × 8,100 = 91,125 instead of 97,200. |
| Downtime | Allowance = T2_DTAmber × shifts run. |
| Cost · OEE | PLAYBOOK.EfficiencyTarget, weighted by target units. **OEE status:** green at or above the PLAYBOOK target; amber within (T2_OEEGreen − T2_OEEAmber) points of it; red below that. Falls back to T2_OEEGreen when PLAYBOOK has no efficiency target. |
| People | Standard crew (HxH StdCrewSize, which comes from PLAYBOOK TotalHC). |
| Quality | T2_ReworkAmber %. |
| PC | Audits due. |
| Safety, Maintenance, Actions | No line, because the target is zero. Shown as text. |

**Where the targets appear:**
- **Line cards:** bars are scaled to the max of value and target over 7 days, with a dark target tick per day and a "▬ target" text line on each card.
- **Cell 7-day trend:** the same treatment, larger, plus a target line on the headline card.
- **Domain view:** bar plus a target marker per line.

**Data fields added to colDaily:** Plan, EffW, val*, tg* (−1 = no target), tgt* (target text).

v4 is 477 controls. Not yet tested in Studio.

### Tier 2 v5: division-by-zero fix (2026-10-21)
- **Symptom (Eric, v4):** division-by-zero errors all over the app.
- **Cause:** the known gotcha. `Sum()` of an empty table returns Blank, not 0, so `If(t = 0, …)` guards don't fire and the division runs.
  - It hits every line-day with no shift records: idle lines, and days before data exists.
  - The new PLAYBOOK plan/efficiency sums added more of them.
- **Fix:** the generator post-processes the line-day and floor-total calculations (`wrap_sums`). All 33 `Sum(...)` calls become `Coalesce(Sum(...), 0)`, so every guard sees a real 0.
  - Extra guards were added where a threshold is the denominator (varDR, varRR).
  - Every remaining division was audited. Each has a zero guard or a 0.0001 floor (the chart scales).
- **Rule going forward:** never divide by a Sum without Coalesce. The generator now enforces this.

### Tier 2 v6: mixed bar + line charts, HOME button (2026-10-21)
**Requests from Eric:**
- Replace the "dotted" per-bar target ticks with a real line and points.
- Add a Home button that returns to the top-level view.

**Charts**
- The 9 line-view cards and the big cell-view trend are now **SVG images**: an Image control with `"data:image/svg+xml;utf8," & EncodeUrl(svg)`, built by `svgchart()` in the generator.
- Each chart has:
  - status-colored bars;
  - a solid target **polyline** with a dot on each day (only drawn when 2+ days have a target);
  - day labels, and a shaded column for the day under review.
- The cell chart also prints each value above its bar.
- Scale = max(value, target) × 1.15 over the 7 days.
- Rendered a sample offline to check the look before shipping.
- This replaced 10 galleries (≈ 30 controls). v6 = 447 controls.

**SVG tips:**
- Use single quotes for SVG attributes inside Power Fx strings.
- Strip `&` and `<` from any data text placed in the SVG.
- EncodeUrl handles `#` colors.

**HOME button:** at the right end of the sub-bar. It sets varLayer = floor and clears varLine, varDom and the add-action overlay. It is disabled (gray) when already on the floor.

**Domain view:** keeps one target marker per line. The bars there compare lines, not days, so there is no series to join with a line.

## 2026-10-21: Board downtime ↔ troubleshooting link (one source of truth)
**Eric's question:** is TS downtime linked to HxH downtime? It wasn't.
- Both carried Line and ShiftKey, but nothing tied an occurrence to a board event.
- Minutes were entered twice.
- Tier 2 matched by guessing: ShiftKey plus the equipment name inside the reason.

**Decisions (Eric):**
- The board is THE source of truth for downtime.
- Fixes can be linked to a board event later, but only by restricted people.

**Design:**
- **Event** = line + shift + reason. `EventKey = ShiftKey|Reason`. It is computed, not stored on HxH_Hourly, so the HxH board and the escalation flow are unchanged.
- **Lookups.EquipType** (new) maps each machine downtime reason to an equipment type, so name-matching is gone. The 9 "Machine - X" reasons are mapped. Lookups.Group stays as the HxH dropdown grouping.
- **TS_Occurrences** gets 5 new columns:
  - EventKey;
  - RepairMin (wrench time; DowntimeMin is no longer written);
  - LinkStatus (Linked at fix / Not on board / Linked later);
  - LinkedBy and LinkedAt.
- **People.CanLinkDowntime** (new, default No). Eric = Yes in the sandbox.

**TS Maintenance v3** (`TS_Maintenance_v3.pa.yaml`, mt.py). New data source: HxH_Hourly.
- New step **"WHICH DOWNTIME IS THIS?"** comes after the machine is picked (QR jumps straight to it). It lists the board's events for that line and machine in the last 24 h, grouped from DT1 and DT2 slots.
  - Each card shows reason, minutes so far, shift and hours, and a STILL DOWN flag.
  - Tapping one sets EventKey with LinkStatus "Linked at fix".
  - "NOT ON THE BOARD YET" sets LinkStatus "Not on board", for a supervisor to link later.
- Back from the concern step returns to the event step.
- The log step shows the board's minutes read-only and asks for **REPAIR TIME** instead of downtime minutes.

**Tier 2 v7** (`T2_Board_v15.pa.yaml`). New data sources: Lookups, People (17 in total).
- Downtime events are matched to TS **exactly on EventKey**. An event's detail reads "n TS linked", "NO TS RECORD" (machine stop) or "not a machine stop".
- **The Maintenance domain counts as unlinked:**
  - TS records with no EventKey;
  - board machine stops with no TS record.

  Either makes the tile amber; the tile's sub-line shows the count.
- **Maintenance details:**
  - Cell detail shows "NOT LINKED" or the board reason, plus repair minutes.
  - The pareto sub-line shows repair minutes and the unlinked count.
- **⇄ RECONCILE (n)** button on the line and cell views opens an overlay for the line over 7 days:
  - **Left:** TS records with no board event.
  - **Right:** board machine stops with no TS record. Once a record is picked, they are re-ranked "same machine" first, then by minutes apart, with close matches highlighted green.
  - **LINK** writes EventKey, LinkStatus "Linked later", LinkedBy and LinkedAt. It is enabled only when `People.CanLinkDowntime` = Yes; others see "LINKING RESTRICTED".

**Sandbox:**
- The columns were added through the REST API.
- The 62 T2TEST occurrences were linked to their events: 54 "Linked at fix" and 8 left "Not on board" for the demo, all with RepairMin.
- Eric's original test occurrence (#1) was left untouched, so it shows as unlinked.

**Provisioner:** schema and seed updated with the 7 new columns and the EquipType mapping. Re-running it on an existing site adds the missing columns.

**After pasting:** in each app, refresh the TS_Occurrences, Lookups and People data sources (Data → ⋯ → Refresh). New columns don't appear until you do.

**Next step:** HxH TROUBLESHOOT button that opens TS Maintenance with line, equipment and the event pre-selected, so the link can also start from the board.

### Tier 2 v8: delegation warning fix (2026-10-21)
**v7 pasted and rendering** (screenshot 10:25): floor grid, downtime events list, Newspaper panel, HOME and RUNNING LINES are all working.

**Fixes:**
- **Delegation warning on btnRefresh:** `Filter(Lookups, … && EquipType <> "")`. SharePoint can't delegate `<> ""` on a text column.
  - Now: `Filter(Lookups, Category.Value = "Downtime")`, then `RemoveIf(colMR, IsBlank(EquipType))` in the app.
  - Every other data-source filter was audited; all use delegable operators (date ranges, choice equality, booleans).
- **Pareto value labels overlapping the bar:** the label was pushed past the gallery's template width, and Power Apps pulled it back over the bar. Max bar width is now (w − label column − 140) and the label is 118 px wide, so it always fits to the right of the bar.

**Rule:** for text "not empty" filters on SharePoint, load with a delegable filter and clean up locally, or use `!IsBlank()` on a small list.

## 2026-10-21: Scale to 15 lines (Tier 2 v9, Newspaper v3, 15-line seed)
**Eric's question:** what happens with more than 5 lines?
- **Screen:** the floor grid showed about 6 lines, then scrolled, which is invisible on an unattended TV. The domain view showed about 11.
- **Data:** every load fits the 2,000-row limit at 15 lines × 7 days, **except Newspaper**, which loaded every action ever recorded.

**Changes:**
- **Tier 2 floor density** (`varDens`, set in btnCalc from CountRows(colFloor)):

  | Mode | Lines shown | Row height | What's on each tile |
  |---|---|---|---|
  | 1 | ≤ 6 | 90 px | value + sub-line + 7 blocks |
  | 2 | 7–12 | 46 px | value + 7 blocks; sub-line on hover |
  | 3 | 13+ | 37 px | value + 7 blocks; sub-line on hover |

  All template positions are Switch(varDens, …) formulas. 15 lines fit in the 566 px grid. The line-name column shrinks, and the value stream moves to the tooltip.
- **Tier 2 domain view:** rows drop from 48 px to 36 px when there are more than 11 lines.
- **Newspaper loads filtered:** `Filter(Newspaper, Status.Value = "Open" || Status.Value = "In progress" || ClosedDate >= <window>)`, all delegable.
  - Tier 2 window: varD0 (the 7 days shown). Its action-trend maths only needs items open at some point in the window.
  - Newspaper app (**Newspaper_v3**): 60 days, which covers the "closed last 7 d" and "avg days to close (30 d)" figures.

**Sandbox seed: 10 more lines** (201, 202, 203, 207, 208, 212, 213, 220, 221, 221P), Oct 11–20, both shifts, each with its own downtime and crew profile.
- **Rows:** 200 HxH_Shift, 2,000 HxH_Hourly, 25 QA_Rework, 118 TS_Occurrences (about 85 % linked to their board event), 16 Escalation_Log, 154 PC_Audits, 18 Newspaper. All tagged T2TEST.
- **Value streams:**

  | Value stream | Lines |
  |---|---|
  | Lotions & Creams | 201, 203, 205, 207, 211, 219 |
  | Wash & Soap | 202, 209, 210 |
  | Creams & Butters | 208, 212, 213, 220, 221, 221P |

- **Sandbox totals:** 300 shifts, 2,991 hourly rows, 223 audits, 181 TS occurrences, 49 actions.

**INCIDENT (my mistake, caught 10:35):** the 9:49 downtime-event seed wrote EscReason/EscCumMin onto existing HxH_Hourly rows. The **live HxH - Downtime Escalation flow** fired on those edits.
- Between 9:49 and 10:00 it sent **9 real escalation notifications to Eric's TEST contact** and logged them (Escalation_Log IDs 18–26).
- The flow behaved correctly: L1 at 60, L2 at 120, on the right events. It served as an end-to-end test on realistic data.
- **Side effect:** those 9 rows duplicate the seeded T2TEST escalation rows for the same events, so escalation *counts* on those events read double. Levels are unaffected. Pending Eric's call: remove either set.
- The 15-line seed left Esc fields empty, so nothing fired.
- **Rule:** turn the escalation flow off before seeding or editing HxH_Hourly in bulk.

### Tier 2 v10: reconcile that can actually close the loop (2026-10-21)
**Eric (screenshot, line 212):** "reconcile doesn't seem to work". The left side was empty and the right side listed 9 stops, so LINK could never be enabled.
- **Root cause, data:** line 212 has no TS records at all. Its stops are Print & apply (no TS concerns for it) and short Labeler stops. So the panel was correct, but it had no way to resolve a stop that will never get a TS record.

**Design gaps fixed:**
1. **NO TS NEEDED (waiver).** A dropdown reason plus a button.
   - **Reasons:** operator cleared it, no maintenance; minor stop, no maintenance needed; covered by another TS record; not an equipment problem.
   - It writes a TS_Occurrences row with `LinkStatus = Waived`, EventKey, LinkedBy/LoggedBy, LinkedAt, and Notes = "No TS needed: <reason>".
   - Restricted by People.CanLinkDowntime, same as LINK.
   - LinkStatus gained the "Waived" choice in the sandbox and the provisioner.
   - Tier 2 loads TS_Occurrences once (colTSAll) and splits it locally: colTS (real records, used for every count) and colWv (waivers, used only as "this stop is covered").
2. **Only stops that need maintenance count.** Machine stops of `T2_TSRequiredMin` (new MDI_Config setting, 15 min = maintenance tier in the escalation plan) or more need a TS record. Shorter stops show as "short stop (< 15 min)". Applies to the Maintenance "unlinked" count, the downtime detail and reconcile.
3. **Reconcile ignores the shift filter** on both sides. Before, shift = 1 hid the shift-2 stop a shift-2 fix belonged to.

**Clickable rows (Eric's request):**
- **Downtime detail:** an unresolved stop is tinted amber and shows "⇄ reconcile"; tapping it opens reconcile with that stop picked.
- **Maintenance detail:** an unlinked record works the same way and opens reconcile with that record picked (its candidate stops ranked first).
- Users without CanLinkDowntime see "⇄ view".
- The DOWNTIME EVENTS lists (floor and line view) are clickable and open that line's downtime detail.

**Implementation notes:**
- Detail rows carry Id, EK and Act fields in every Switch branch, so the schemas stay identical.
- The selected stop is looked up by key (`EVR`) instead of being stored as a record variable. That avoids record-type mismatches between the different galleries that set it.
- IfError wraps only the SharePoint ClearCollect; local splits are chained after it.
- v10 = 483 controls.

### Tier 2 v11: row pill + strongest-match suggestions (2026-10-21)
**Eric (screenshot, 221P maintenance):** the "⇄ reconcile" text clashed with the repair-time column, and reconcile should suggest the strongest match.

**Changes:**
- **Detail table:** columns narrowed (190 / 70 / 390 / 250 / 112) to make room for a dedicated pill column at the end: amber **⇄ LINK** (can link) or gray **⇄ VIEW** (restricted).
- **Match score** for a TS record against a board stop:

  | Signal | Points |
  |---|---|
  | Same machine (Lookups.EquipType of the stop's reason = the record's EquipType) | +50 |
  | Same ShiftKey | +30 |
  | Closeness in time: 20 − minutes apart / 15 | up to +20 |

  Strength: **≥ 80 STRONG**, 50–79 possible, < 50 weak. Both reconcile lists sort by score once the other side is picked, and show the strength (green / amber / gray) with minutes apart and "same shift".
- **Auto-preselect:** tapping a ⇄ LINK row opens reconcile with that row picked and its top-scoring counterpart pre-selected if its score is ≥ 50. A strong match is one tap on LINK; the user can still pick another.
- **Implementation:**
  - REC_EV, EVR, NEEDEV, UNL and the two score expressions (SC_O, SC_E) are defined once, right after EVT, and reused.
  - Both Switch/If branches add the same columns (Sc, Dist), so the schemas match.
- v11 = 484 controls.

### Tier 2 v12: maintenance detail shows what "unlinked" counts (2026-10-21)
**Eric (screenshot, 208 maintenance):** the tile said "2 unlinked", but every row in the table was linked.
- **Cause:** the unlinked count = TS records with no board event **+ board machine stops (15+ min) with no TS record**. The maintenance table listed only TS records, so the missing-record stops were visible only under DOWNTIME.

**Changes:**
- **Maintenance detail** is now the union of TS records and board stops of T2_TSRequiredMin+ min with no TS record and no waiver.
  - Stop rows show "<machine>: board stop, hour x–y", "NO TS RECORD" (plus escalation level) and minutes down, with a red stripe.
  - Each stop row has a ⇄ LINK pill that opens reconcile with that stop and its strongest TS record pre-selected.
  - Built as `Ungroup(Table({t: TS rows}, {t: stop rows}), t)` with identical fields.
- **Tap logic:** Id = 0 means a stop row, so it takes the stop path.
- **Sub-line** split: "n unlinked · n stops w/o TS · n op-fix".
- **Column headers** for M: CONCERN / BOARD STOP · FIX · OUTCOME · LINK · TIME.

## 2026-10-21: US English throughout
**Eric:** "We're in the United States, there's no British spelling here."
- **Data:** Newspaper.Status choice **Cancelled → Canceled** in the sandbox (choice and pill formatting; no items used it) and in the provisioner and schema.
- **Apps:**
  - HxH_Board_v11: tooltip "Gray rows". Regenerated from build6 after confirming it reproduces v10 byte for byte; the diff is that one line.
  - Newspaper_v4: status filter and status buttons say "Canceled".
  - T2_Board_v13: "Canceled" in action filters; hour-strip legend "gray = target, color = actual".
- **Docs:** log, README, Kenny handoff and flow specs converted (color, gray, license, favor, canceled).
- **Scan:** current app YAMLs, generators, docs and every SharePoint list's column titles, descriptions, choices, Lookups values and MDI_Config notes. No other British spellings remain. Internal code identifiers (e.g. the GREYT constant) are not user-facing and were left alone.
- **Rule going forward:** US English in all on-screen text, data values and documents.

## 2026-10-21: Newspaper first build (v4 → v5) + Harvey-ball progress
**Eric pasted Newspaper v4** (first time this app exists in Studio). It rendered with 36 open and 12 overdue, but had two errors.
1. **`ddNOwn.Items`: "Name isn't recognized".** The People Title column is displayed as "Name", but **inside a collection** (colPeople) Power Apps uses the internal name. Now `{Value: Title, Email: Email}`.
   - **Lesson:** display names work against the data source; in a ClearCollect'ed copy, use internal names (Title).
2. **`gNStat.OnSelect`: "column DueSort does not exist".** `Patch(colNews, ThisItem, …)`: the gallery item carries the sort helper columns AddColumns(Late, DueSort) that colNews doesn't have. Now `Patch(colNews, LookUp(colNews, ID = ThisItem.ID), …)`.
   - **Lesson:** never Patch a collection with ThisItem from a gallery whose Items adds columns.

**Harvey balls (Eric's request)**
- **New column Newspaper.Progress** (Number 0–100, default 0). Added in the sandbox and the provisioner. The 49 actions were backfilled: Done = 100, Open = 0, In progress spread over 25/50/75.
- **Status follows progress:** 0 = Open, 25–75 = In progress, 100 = Done (stamps ClosedDate). Canceled stays a separate status.
- **`harvey.py`** builds static SVG data URIs:
  - teal quarters;
  - red outline when overdue and not done;
  - solid green at Done;
  - gray slash when Canceled.

  The offline render was checked. Rows created before the column existed fall back to a status-derived value (PROG()).
- **Newspaper v5:**
  - List: the PROGRESS column shows the ball plus %. Tap steps 0 → 25 → 50 → 75 → 100 → 0; canceled actions don't step.
  - Edit panel: five clickable balls (0–100 %) plus a Canceled toggle replace the four status buttons. Save writes Progress and Status.
- **Tier 2 v14:** the Newspaper panel uses the same ball and tap-to-step.

## 2026-10-21: Bulletproofing, steps 1–2 of 7
**Plan agreed with Eric:** finish New Albany to bulletproof first, then test, then make it generic. Build in the theme file and environment variables along the way so "generic" is extraction, not a rewrite.

**The 7 steps:**
1. Indexes and unique keys
2. Daylight saving
3. Permissions
4. Solution packaging with environment variables
5. Theme file
6. Dry-run shift and demo-data cleanup
7. Offline queue, nightly missed-hours check and flow alerts

### Step 1: indexes + unique keys (done)
- **Why:** SharePoint's 5,000-item list view threshold. Past 5,000 rows, filters on non-indexed columns fail or return partial data silently. HxH_Hourly grows about 130k rows a year at 15 lines.
- **Indexed in the sandbox (56 columns):** every column the apps and flows filter on, across HxH_Shift, HxH_Hourly, QA_Rework, TS_*, PC_*, SW_*, Escalation_Log (incl. Title, used by the flow's startswith), Newspaper, Lookups, People, Lines, plus PC_Results.Created.
- **Unique (enforced):** HxH_Shift.Title (ShiftKey) and HxH_Hourly.Title (hour key).
  - Existing data was checked first: 300 shifts and 2,991 hours, no duplicates.
  - Live test: a duplicate insert is rejected with SPDuplicateValuesFoundException.
  - The HxH board already saves as an upsert (`Coalesce(LookUp(…Title = k), Defaults(…))`), so normal saves are unaffected. Only a true two-tablet race fails, visibly, via the existing IfError.
- **Provisioner:** `PKG.indexes` lists them (Title* = unique). After the fields step it applies `Indexed` / `EnforceUniqueValues`. Tested on /sites/MDIDeployTest.
- **Escalation flow review:** it is already idempotent. It looks up Escalation_Log by `ShiftKey|Reason|Level|Email` before notifying, so edits to earlier hours don't re-notify. This morning's 9 alerts fired because the seeded T2TEST log rows used a different title format. **Removed "flow re-fires on edits" from the risk list.**

### Step 2: daylight saving (done; HxH_Board_v12)
- **Bug found:** shift length was `Mod(end − start, 1440)`, which assumes 24-hour nights, and slots were absolute minutes from start.
  - **Fall-back night (Oct 31 → Nov 1):** shift 2 (4:30 PM–3:00 AM) really runs 690 min. The board allowed 630, so the crew's last hour (2–3 AM CST) had no slot and no target.
  - **March:** a phantom hour.
- **Fix (build6):**
  - Start and end are built with `DateTime(Y, M, D, h, m)` as local wall-clock times. The end goes on the next day if it's at or before the start.
  - Duration = `DateDiff(start, end, Minutes)`.
  - Slot count = `Max(12, RoundUp(duration / 60))`.
  - The same duration expression is used for PlannedShiftHrs and available minutes in the shift save, so the Tier 2 PLAYBOOK plan is right on DST nights too.
  - v12 diff vs v11 is only those lines.
- **Verified with America/Chicago tz math:**

  | Night | Shift 2 duration |
  |---|---|
  | Normal | 630 min |
  | Fall back | 690 min |
  | Spring forward | 570 min |
  | 12-h night on fall back | 780 min (13 slots) |

- **Other apps:** shift-of-day logic (hour-of-day thresholds), escalation (cumulative minutes) and timestamps are unaffected.
- **Action:** **paste HxH_Board_v12 before Oct 31.**

### Step 3: permissions (done in the sandbox; provisioner + flow spec)
**Eric's decisions:**
- Config editing: OpEx, production managers, engineering/planning, **managed by switches on the People list ("like permissions")**.
- Deletes: admins only.

**Model:**

| Access level | Config lists (Lookups, PLAYBOOK, People, MDI_Config, Escalation_Contacts, Lines, Assets, SW_Standards, SW_Elements, PC_Cards, PC_CardItems) | Data lists (HxH_Shift, HxH_Hourly, QA_Rework, TS_Occurrences/Issues/Fixes/Procedures/Steps/Photos, PC_Audits, PC_Results, Newspaper) | Escalation_Log |
|---|---|---|---|
| Owners = admins | Full Control | Full Control | Full |
| MDI Config Editors (new group) | Contribute | Contribute - no delete | Read |
| Members (everyone, incl. kiosk) | Read | Contribute - no delete | Read |
| Visitors | Read | Read | Read |

- **Contribute - no delete** (new permission level) = Contribute minus DeleteListItems and DeleteVersions. Verified: view / add / edit yes; delete items and versions no.
- **People switches:** **MDIAdmin** and **CanEditConfig** (new Yes/No columns), alongside CanLinkDowntime. Eric = Yes on both.
- **Flow 03 "MDI - Sync Permissions"** (spec in deploy/flows): on a People create or modify, it adds or removes the person in Members (Active), MDI Config Editors (CanEditConfig or MDIAdmin) and Owners (MDIAdmin) via *Send an HTTP request to SharePoint* (standard connector).
  - **Lock-out guard:** keep one IT site owner outside People.
  - **Not yet built in the sandbox.** Membership is manual until it is; Eric is already Owner and Config Editor.
- **Apps that deleted:**
  - **QA Rework ✕ → VOID** (QA_Rework_v3). New `QA_Rework.Voided` column (default No, indexed, 48 rows backfilled). QA Rework and Tier 2 (T2_Board_v15) load with `Voided = false`.
  - **SW Manager's** `RemoveIf(PC_CardItems…)` is config work, so config editors keep delete on SW/PC config lists.
- **Column-level limit:** SharePoint can't restrict individual columns, so CanLinkDowntime stays an app rule, audited by LinkedBy/LinkedAt and version history.
- **Sandbox:** all 24 lists have unique permissions. Eric's effective rights were checked (full).
- **Provisioner:** `PKG.perms` plus a permissions step (permission level, group, break inheritance, grants). Tested on /sites/MDIDeployTest; all 24 lists OK. SharePoint also adds the runner as a direct Full Control grant.

### Step 5: theme file (done)
- **`generator/theme.py`** is the only place brand lives: brand word, site label, heading and body fonts, and five brand colors (dark, primary, accent, soft, tint) plus the SVG tint.
  - Themes defined: **voyant** (current), **svend** (placeholder values, *TODO: real SVEND palette and font*), **neutral** (unbranded).
  - Select with the `MDI_THEME` env var; override the site label with `MDI_SITE`.
- **How it works:** every generator writes through `write_themed()`, which maps the Voyant tokens to the active theme in every form they appear:
  - Power Fx `RGBA(r, g, b, α)` at any alpha;
  - SVG hex, including URL-encoded `%23…` inside the Harvey-ball images;
  - `"voyant"` and `"NEW ALBANY"`;
  - `Font.Georgia` / `Font.Arial`;
  - SVG font-family.

  Signal colors (green / amber / red), grays and whites are deliberately not remapped.
- **Verified:**
  - **voyant:** all 8 current apps regenerate **byte-identical** to the shipped files. The baseline was confirmed first, before the refactor.
  - **neutral:** all 8 apps parse, with **zero** leftover Voyant tokens; the site label and fonts are swapped. The two phone apps show no site label.
- Making the SVEND version later = fill in `THEMES["svend"]` and run the generators with `MDI_THEME=svend`.

### Handoff renamed for Copilot
Kenny **is** using Copilot for the install (Eric clarified "not" = "now"). `KENNY_HANDOFF_for_Copilot.md` → **`KENNY_HANDOFF_for_Copilot.md`**, addressed to "Kenny's assistant (Copilot or any other AI)". Same manual steps, triggers and guardrails. The checklist will be rewritten after solution packaging (step 4), when the install steps shrink.

### Step 6 (part): test-data cleanup script (done; not run)
- **`deploy/tools/clear_test_data.js.txt`:** browser-console script that moves rows to the **recycle bin** (restorable 93 days).
  - Defaults to **DRY_RUN** (report only), then asks `confirm()` before acting.
  - Reads lists by paging IDs, so it works past the 5,000-item threshold.
  - Needs admin rights.
- **Modes:**
  - **demo:** T2TEST-tagged rows (HxH, QA, TS, PC, escalations, Newspaper, T2TEST guide content), test waivers, TEST escalation contacts and every escalation sent to them (incl. the 9 flow-created ones). Keeps the SAMPLE standard and card and hand-made test rows.
  - **reset:** go-live clean slate. Every transaction created before CUTOFF, plus demo rows, plus the SAMPLE standard/card with children, plus PC/Newspaper photos. Keeps all config and the TS guide.
- **Dry run on the sandbox (demo mode):** 3,878 rows would go. Kept exactly the hand-made tests: 209 S1 10/20 shift + hour, QA 2,400, TS "Labels Wrinkling" occurrence / issue / fix, 2 photos, 7 role contacts. **Not executed.**
- **Still to do in step 6:** the full dry-run shift, with Eric.

### Step 7: resilience (done; HxH_Board_v13 + flow specs)
- **Offline queue (HxH_Board_v13):**
  - The row save previously had **no error handling**; a failed save showed only Power Apps' generic banner, and the hour was lost on reload.
  - Now the hour record is built once as `rec`. On a failed Patch it goes into `colPending` (`{K, HourNo, Rec, At}`, replacing any earlier entry for the same key) with a warning.
  - `btnFlush` re-Patches every queued record (an upsert by Title, so idempotent) and clears the queue on success. It runs before every row save and every REFRESH; there is also a red banner with **RETRY NOW**.
  - "Saved h:mm" only updates when nothing is queued. The shift-totals save is wrapped in IfError too; totals are recomputed on the next save.
  - **Limit:** the queue is in memory. Closing the app while hours are queued loses them, hence the banner text. SaveData isn't reliable in the web player, so it's not used.
- **Flow 04 "MDI - Nightly Board Check"** (spec): 6:30 AM Central.
  - For each of yesterday's shifts: expected hours = ceil(PlannedShiftHrs), filled = hourly rows with CumulativeUnits.
  - Missing ≥ `NB_MinMissing` (2) → one NEWSPAPER action (RefKey `NB-<ShiftKey>`, idempotent).
  - Emails a digest to `Alert_Email`, including active lines with no board.
- **Flow failure alerts:** a Try/Catch section added to flows 01–03 and built into 04. Catch emails `Alert_Email` with the run link.
- **Escalation concurrency:** the spec already had concurrency = 1; Eric to confirm the built flow matches.
- **MDI_Config:** `Alert_Email` (sandbox = Eric; seed = blank, fill in) and `NB_MinMissing` = 2.

## 2026-10-21 — Flows (step 5)
- Flow designer in the browser pane dropped clicks, so flows are now written straight into the environment's Dataverse (org8edeeb0b, Eric approved). Definitions are generated by `generator/flows.py` → `deploy/flows/json/`.
- New connection reference in solution MDI: **MDI Office 365 Outlook** (`craf4_sharedoffice365_mdi`), bound to Eric's Outlook connection "EmailConnect".
- **03 MDI - Sync Permissions** created in MDI (draft). Checks membership before add or remove, because SharePoint returns a 404 when you remove a non-member. Uses ensureuser before adding.
- **04 MDI - Nightly Board Check** created in MDI (draft): 6:30 AM Central, idempotent NB-<ShiftKey> actions, digest to Alert_Email.
- **01 HxH - Downtime Escalation** pulled into solution MDI by Eric (it notifies via **Teams** Flow bot, connection ref craf4_sharedteams_a7259). Catch scope added after Notify_each.
- **02 MDI - Upload Photo**: Catch added after the Respond step. The SharePoint lookup uses the invoker key like the other steps; email goes through the Outlook ref.
- Catch pattern (all flows): Scope after the last step, run after Failed/TimedOut/Skipped → Get Alert_Email → Send email (V2) with the run link. Spec files and README updated.
- Turning flows on via the API was blocked (fair: 03 changes live permissions), so Eric turns them on himself.
- Stray designer edits on flow 01 (UOM connector, half-built Catch) were never saved. Confirmed clean.
- Flow tests: Sync Permissions added Eric to Members within about a minute (his own row, additive only). Eric ran Nightly Board Check by hand: digest received, 1 action raised (NB-209-20261020-S1, 12 of 12 hours missing; correct).
- SW Manager, Newspaper, PC Audit and TS Binder added to solution MDI via AddSolutionComponent. **HxH Board, QA Rework, TS Maintenance and T2 Board are outside Dataverse.** Eric must add them: Solution MDI → Add existing → App → Canvas app → Outside Dataverse.
- New: `deploy/DRY_RUN_SHIFT.md` (one-line, end-to-end dry-run script). KENNY_HANDOFF_for_Copilot.md rewritten as an A–F install checklist (4 flows, Outlook connection, Alert_Email, cleanup script).
- Packaging note: the flows still hard-code the sandbox site URL and list GUIDs. A one-file solution import for Voyant needs a "MDI Site URL" environment variable and list names instead of GUIDs (flows), plus Studio re-pointing for the apps. Not done unattended, because it means editing live, tested flows. Do it with Eric present.
- **Flow installer (no installs, no Copilot):** `deploy/tools/install_flows.js.txt` is a browser-console script run on the environment's Dataverse page (`https://org….crm.dynamics.com`).
  - It asks for a SETUP CODE, then creates publisher SVEND (prefix svend), solution MDI, connection references (svend_mdi_sharepointonline / _teams / _office365) and all 4 flows, Off, pointed at the customer's site and list GUIDs. It is idempotent.
  - The provisioner now ends by building the SETUP CODE (`MDI1:` + base64 {site, list GUIDs}), copying it to the clipboard and printing it.
  - Generated by `generator/flows.py` (all 4 flows; definitions verified byte-identical, by canonical SHA-256, to the live tested sandbox flows) and `generator/make_installer.py`.
  - Tested in the sandbox against MDIDeployTest: created solution **MDITEST** with 4 flows named "… [install test]" (Off, unbound refs), correct site and GUIDs, no sandbox leaks. Those test flows and the MDITEST solution are safe to delete.
  - Edge blocks the first console paste: type `allow pasting`.

## 2026-10-21: Frontier Audit (lite): safety + 5S module
Eric asked for a lite version of his SVEND Safety HIRARC / Frontier program (DuPont STOP model). Requirements: photos on at-risk safety findings, photos on 5S, and 5S standard pages with sections stored in the system so audits pull in the actual standard (like TS / standard work).
- **Conflicts in Eric's documents, and the lite picks:**
  - **Rating scale:** S/AR/U vs S/AR/NA. Used S/AR/U/N/A.
  - **Items:** 19 items in three different versions. Used the card's 19 (4/2/3/4/3/3).
  - **Operator questions:** 3 vs 4. Used all 4.
  - **5S scoring:** tally vs 1–5. Used Meets/Deficient per section of the zone's standard, with pillar + photo.
  - **Timelines:** used the standard's (C/H 1 day, M 30, L 90; MDI_Config editable).
  - **Cross-feed:** a 5S deficiency flagged "also a safety hazard" gets a severity.
  - **Not fixed:** duplicate SAF-002 numbering and the frequency mismatch, which are left for Eric's doc set.
- **Lists:** SAF_Zones (config), SAF_Items (config, 19 seeded), SAF_Audits and SAF_Results (data). Indexes and perms in the package.
  - **Choice adds:** SW_Standards.DocType "5S", Newspaper.Source "Frontier audit", TS_Photos.Module "Frontier audit".
  - **MDI_Config:** App_Frontier, SAF_DueDays_{Critical,High,Medium,Low,5S}, Safety_Email.
- **Provisioner:** new `choiceAdds` step (merges choices into existing columns) and `ensureRows` step (adds missing config rows on existing sites; runs after seed). Fixed the duplicate Site_URL_Live row on re-run. The SETUP CODE now carries SAF_Results (optional).
  - Tested on MDIDeployTest: 4 lists, 19 items, choices, 7 config rows, perms, no warnings. Then run on MDISandbox.
- **Sandbox demo data:** 5S standard ID 2 "5S standard: Line 209 maintenance crib" (5-S-209-01, 5 sections, AddedBy SAMPLE, **no photos yet**; add them in SW Manager). Zones FZ-NAL-HI-01 (linked to std 2), FZ-NAL-TR-01, FZ-NAL-OH-01 (Notes "SAMPLE zone"). Safety_Email = eric.wolters@verxted.com.
- **Apps:**
  - **Frontier_Audit_v1** (phone; `generator/fa.py`): D-S-O-I-R flow, 19-item gallery with a finding panel (severity, finding, immediate action for C/H, photo required, Newspaper toggle forced on for C/H), and a 5S gallery against the standard photos with a deficiency panel.
  - It writes SAF_Audits, SAF_Results, Newspaper (due by severity) and photos (Kind Finding, Module Frontier audit, StepNo = item or 100+section).
  - **SW_Manager_v3:** "5S" type, section wording, and the standard ID shown for SAF_Zones. Diff vs v2 is only those lines.
  - Static checks pass (YAML, unique names, bracket balance, neutral theme has 0 Voyant tokens). **Not yet pasted into Studio.**
- **Flow 05 "MDI - Frontier Critical Alert":** trigger on SAF_Results created with condition Severity = Critical. Teams Flow bot message to Safety_Email + ZoneOwnerEmail (deduplicated), plus Catch. Created in sandbox solution MDI (Off). Added to flows.py and the installer (skipped if the site has no SAF_Results). Flows 01–04 definitions are unchanged (hashes match).
- **Cleanup script:** reset mode now also covers SAF_Audits/Results, Frontier photos and SAMPLE zones.
- **Docs:** `deploy/FRONTIER_LITE.md`, `flows/05_….md`, APP_BUILD_GUIDE card 9, README, Kenny checklist (C6, D, E6 → SW v3, E9 Frontier).
- **Full-version gap list (for a later SVEND Safety package):** FMEA register (S×O×D, RPN, hierarchy of controls, re-score), named schedule and assignments with completion KPI, coordinator bridge queue plus duplicate detection, Tier 2 Safety tile and 5S Pareto chart, certification and calibration records.

## 2026-10-21: Kenny's install: IfError type error
- **Symptom:** in Kenny's tenant (Vee Pak, LLC default environment, newer Studio build), HxH btnSaveShift.OnSelect showed "Invalid argument type (Boolean). Expecting a Record value instead" plus "IfError has some invalid arguments". Shift hours stuck at 10.5 because a formula with an error never runs, so the shift never saved and the board fell back to the 6:00–4:30 default.
- **Checked:** Kenny's HxH_Shift schema is identical to the sandbox (31 columns, same names and types).
- **Cause:** a 2-argument `IfError(Patch(...), Notify(...))`. Value type Record vs fallback type Boolean; the newer Power Fx rejects the mismatch.
- **Fix:**
  - On Kenny's laptop: hand edit to `..., NotificationType.Warning), true))));`.
  - In all apps: `generator/fx_compat.py` `fix_iferror()` (2-arg IfError with a Notify/Clear fallback becomes 3-arg `, true`), now run by `write_themed()`. 50 instances across 9 apps.
  - All generators regenerate the shipped files byte for byte.
- **New versions:** HxH_Board_v14, Newspaper_v6, PC_Audit_v3, QA_Rework_v4, T2_Board_v16, TS_Binder_v2, TS_Maintenance_v4. SW_Manager_v3 and Frontier_Audit_v1 keep their names (never pasted before). Docs updated.

## 2026-10-21 (later): Frontier into Tier 2, demo data
- **T2_Board_v17** (`generator/t2v2.py`; pre-change copy is t2v2.py.prefrontier): loads SAF_Audits + SAF_Results for the 7-day window, keeping only hazards (AR, U, or Deficient with SafetyRelevant).
  - **New per-line/day vars:** fz (hazards), fch (Critical+High), fa (audits). At floor level with "All value streams" they count all zones, including zones with no Line.
  - **S tile:** text "N + k C/H". Sub "… · x hazards in y Frontier". Red = board event or C/H; amber = other hazards.
  - **S lists:** Frontier rows added to the floor reasons list and the line detail list.
  - **Data sources:** 19 (adds SAF_Audits, SAF_Results). Sites provisioned before the Frontier lists must re-run the list setup first.
  - **Checks:** static checks pass. Diff vs v16 is limited to the S domain and loads.
- **Provisioner:** the existing-column check now matches internal name OR display name. SharePoint encodes names like Q1 → _x0051_1 (as with Job1). Without this, a re-run would have added duplicate Q1–Q4 columns. In REST, those fields are OData__x0051_1.
- **Sandbox demo data:**
  - 5 placeholder standard photos (canvas-drawn) for 5S standard 2 (TS_Photos, Module Standard work, RefID 2, StepNo 1–5, TakenBy SAMPLE).
  - Frontier demo audits for yesterday (AuditedBy T2TEST): FZ-NAL-HI-01 (line 209: 1 AR Medium, 1 U High, 1 5S deficient) and FZ-NAL-TR-01 (no line: 1 U Critical). 48 SAF_Results rows, Ref FA-T2TEST-….
- **Cleanup script:** demo mode removes FA-T2TEST results; reset mode also removes SAMPLE photos.
- **HxH_Board_v15** (ux6.py additions): target speed from PLAYBOOK Rate shown in three places:
  - the BPM column header ("● BPM / TGT 180");
  - each BPM entry's hint ("tgt 180") and tooltip;
  - the header standard label, now "TARGET SPEED 180 BPM" in aqua (was faint grey).

  Diff vs v14 is limited to those properties.

## 2026-10-21 17:00: photo flow File input fails on Kenny's tenant
- **Symptom:** TS Maintenance btnSSave: `'MDI-UploadPhoto'.Run({contentBytes: …})` → "Invalid argument type (Record). Expecting a Text value". The flow (installer-built) shows the inputs in the right order. Re-saving the flow and re-adding it didn't help (my guesses cost Eric time).
- **Fix: no File input any more.**
  - **Flow 02:** Photo is a Text input (key still `file`). Create_file body = `base64ToBinary(replace(last(split(string(file), ',')), '"', ''))`, which accepts the data-URI JSON or plain base64.
  - **Apps:** pass `JSON(<media>, JSONFormat.IncludeBinaryData)` (fx_compat.photo_b64, applied by write_themed).
  - **New versions:** TS_Maintenance_v5, Newspaper_v7, PC_Audit_v4, SW_Manager_v4, Frontier_Audit_v2 (only the Run lines changed).
- **Installer:** re-running now UPDATES existing flows whose definition differs (PATCH clientdata) and prints which ones to turn off/on and re-add in apps.
- **Sandbox flow 02 NOT changed yet:** the sandbox apps still send the old record form. Update it together with re-pasting the photo apps.
- **NOT yet verified end to end:** needs one photo save on Kenny's (or the sandbox) after the change.
- **17:16, Mimecast:** the emailed install_flows.js.txt arrived with every https:// URL rewritten to url.us.m.mimecastprotect.com, giving "SyntaxError: Invalid or unexpected token". Nothing ran.
  - **Fix:** all scripts write URLs as `https:\/\/` (identical value in JS; verified TEMPLATES and PKG are byte-equal after evaluation). make_installer does this automatically.
  - **Rule:** always send scripts inside a .zip.
- **HxH_Board_v16:** job number boxes (Job 1 + per-hour Job) limited to 6 characters (MaxLength).
- **HxH_Board_v17:** OEE tile: OEE % (44pt) and A/P/Q split into their own labels (new kAPQ, 20pt, no wrap). Before, a wide A/P/Q line wrapped to 3 lines and pushed the OEE number into the caption.

## 2026-10-22: Sandbox photo flow switched to text input
- Sandbox flow **MDI - Upload Photo** (31744db5…) PATCHed to the flows.py flow02 definition: Photo input is Text; Create_file body = `base64ToBinary(replace(last(split(string(file), ',')), '"', ''))`. Same as the version Kenny's installer ships.
- Previous definition kept in the browser session only (old record-form input: contentBytes/name).
- Next: Eric turns the flow Off/On, re-adds it in TS Maintenance, pastes TS_Maintenance_v5, and runs one live photo save.
- Same morning: **reverted** sandbox MDI - Upload Photo to its previous definition (verified byte-identical). Sandbox is as it was on 10/21. Focus moved to the enterprise managed-solution design.

## 2026-10-22: Tier 3 board v1 (plant leadership)
- Scope (Eric): plant leadership; SQDCP by value stream, trends vs target, escalations from T2 and leader standard work later. Performance visuals first; package as managed solution end of day.
- **New list KPI_Daily** (one row per line per day, the 29 raw measures Tier 2 computes; Title = Line|yyyymmdd; FLOOR = zone findings with no line). Added to mdi_package.json (perms: data) + provisioner rebuilt (tools: kpi_schema.py, rebuild_prov.py). Created in the sandbox by REST (34 columns, indexes KPIDate/Line/Title).
- MDI_Config ensureRows: App_Tier3, T3_WeekStart (Monday).
- **T3_Board_v1.pa.yaml** (generator t3.py; reuses T2 DAYREC so numbers match Tier 2): computes 7 days per line, saves closed new/changed days to KPI_Daily, loads 13 months of KPI_Daily in monthly chunks (2,000-row limit), merges. Views: PLANT (plant row + value streams), VALUE STREAM (its lines), KPI focus (13-week / 12-month chart + heatmap by VS or line). Period: day / week to date / month to date. 8-week dots per tile. OPEN TIER 2 button (App_Tier2).
- APP_BUILD_GUIDE card 10 added.
- T3 v2: fixed duplicate Visible on the KPI heatmap headers (Studio paste error PA1001). Added dupcheck.py (duplicate property lint) to the checks.
- T3 v3 (Eric's review): removed the history note; safety wording = 'safety audits' (no Frontier brand on T3); name cells autosize (no wrap); rows compressed (top 88, rows 72); whole row clickable; LINE drill-down (line's own tiles + trends, breadcrumb PLANT › VS › LINE); tile values no-wrap.
- T3 v4: every metric gets a page (tap a KPI heading or chart): **trend** vs target (13 wk / 12 mo) + heatmap by VS or line, **Pareto** for the selected period with cumulative % (S: what was found; Q: rework by reason; D: downtime minutes by reason; C: scrap by reason; P: staffing gaps), **Newspaper** actions for that SQDCP letter in scope (overdue in red) + ADD ACTION overlay (Source "Tier 3") + NEWSPAPER link (App_Newspaper). Grid KPI headings show open-action counts. Reason data now loads from the 1st of the month (varR0) so month-to-date Paretos work.
- Newspaper Source choice "Tier 3" added (package choiceAdds + sandbox list).
- Found: T2 add-action overlay patches `Title:` but Newspaper's title is displayed as **Action** (Power Apps uses display names). Fix in next T2 version.
- T3 restructure (Eric 09:28): one app, modules on screens. **ValueStreams** list (Title, Parent, Leader, LeaderEmail, DisplayOrder, Active, Notes): plant → value stream → vertical (Parent) → line; T3 falls back to Lines.ValueStream if empty. **Variances** list (Kind 24-hour/Monthly, SQDCP, ValueStream, Line, Magnitude + Unit [operational units, no dollars], Detail, Owner, RaisedDate, ShowUntil, MonthOf, Status, NewspaperRef, RCARef). MDI_Config T3_Var24Days = 7. Both created in the sandbox; ValueStreams seeded with the 3 value streams.
- T3_Board_v5 (PERFORMANCE): hierarchy drill (PLANT › VS › VERTICAL › LINE), tab strip PERFORMANCE | BOWLER | VARIANCES | ROOT CAUSE (placeholder), YTD aggregate (colY).
- T3_Bowler_v1 (scrBowler): 5 SQDCP × 12 months + YTD vs target for the scope; same metric by VS/vertical/line below (S/Q/D/C/P picker).
- T3_Variances_v1 (scrVariance): 24-hour board (shown T3_Var24Days days) + BIGGEST MISSES from the boards (units short of plan, top downtime) with RAISE; monthly MOR board by month; each card → NEWSPAPER (creates Tier 3 action, RefKey VAR-id), CLOSE/REOPEN, ROOT CAUSE placeholder.
- Root cause = its own system later. Next: fix Tier 2 (Action field bug, safety-audit wording), then root cause.
- T3 v6 / Bowler v2 / Variances v2: **Parent is a reserved word in Power Fx**; the ValueStreams column 'Parent' broke colVS and every formula downstream (Eric saw errors on every screen). Column is now **ParentVS** (package + sandbox; the empty old 'Parent' column in the sandbox list is unused). Collection field renamed Up.
- **T2 v18**: + ADD ACTION now saves the action name (Newspaper title is 'Action' in Power Apps; v17 patched 'Title' and failed). Safety wording 'safety audits' instead of Frontier (tile, tooltips, Pareto labels, timeline). Only those lines differ from v17.
- **T3 metric catalog** (Eric 10:12: several S/Q/D/C metrics per line, layered in over time; NCRs coming; accountability roll-up = separate app later). New list **KPI_Metrics** (Title = code, Letter, MetricName, Short, Unit, Better, Green, Amber, DisplayOrder, Active, Notes), seeded with 13 metrics: SAF_EVENTS, SAF_HAZ, SAF_AUD, QUAL_RW, QUAL_SCRAP, QUAL_NCR (stub), DEL_ATT, DEL_DT, DEL_DTE, COST_OEE, COST_SPEED, PEO_CREW, PEO_PC. Calculations live in generator/t3_metrics.py (Power Apps can't eval formulas from a list); the catalog switches/orders/thresholds them. Created + seeded in the sandbox; Variances gained a Metric column.
- **T3_Board_v7**: letter tile = worst of its metrics (headline metric big, others summarized); bottom charts = each letter's headline metric; letter page = one row per metric (value, target, 13-wk/12-mo chart), heatmap + Pareto for the selected metric, Newspaper for the letter. PC results load from the 1st of the month.
- **T3_Bowler_v3**: rows = every metric grouped by letter, 12 months + YTD; one metric by VS/vertical/line below (picker). **T3_Variances_v3**: optional Metric on each variance.
- Tier 2 v18 published (Action field fix + safety-audit wording).
- **T3_Bowler_v4**: true bowling chart: each metric = 3 lines per month and YTD: target, actual (cell colored by status), variance (signed; green = favorable for that metric's direction, red = unfavorable). Number formats per metric (t3_metrics.FMT).
- Cadence (Eric): Tier 1 hour x hour · Tier 2 shift by shift · Tier 3 day by day (war room) · Tier 4 lean steering (weekly) · Tier 5 MOR (monthly) · Hoshin year by year.
- **T3_Bowler_v5**: weekly bowler: 13 weeks + MTD column on the right (target / actual / variance); kids section also weekly + MTD. **T3_Board_v8** adds the MTD aggregate (colMTD) the bowler reads. Monthly views belong to Tier 5 (MOR).
- **T3_Bowler_v6 / T3_Board_v9** (Eric: bowler columns are DAYS): 7 day columns for the reviewed week (future days blank, reviewed day highlighted) + WTD + MTD, each target / actual / variance. Board computes colDy (per day) and colWTD. Supersedes the weekly v5.
- **T3_Variances_v4**: BIGGEST MISSES are keyed (SHORT|line|date, DT|line|reason|date) and drop off once raised (Variances.SourceKey, new column, package + sandbox). Metric dropdown lists only metrics with data in the current scope month to date (any letter; picking one sets SQDCP). Magnitude shows whole numbers without a trailing dot. 24-hour 'shown until' falls back to 7 days if the setting isn't loaded (the first test variance had saved with 0 days; fixed in the sandbox: ShowUntil 10/29, metric Attainment to plan, key SHORT|209|20261020).
- **T3_Variances_v5**: a monthly variance saved with no MonthOf (month variable not loaded yet) and so never showed; save now falls back to the reviewed month; + buttons and RAISE reload the board state first. Sandbox record 2 (monthly, line 209) fixed: MonthOf = Oct 2026.
- **T3_Variances_v6**: BIGGEST MISSES cover every letter for the reviewed day, top 3 per source, sorted S→Q→D→C→P then size: S board safety events, audit hazards (worst severity first); Q rework and scrap by line+reason; D below plan, downtime by line+reason; C speed loss by line+reason; P short crews, missed PC items. Each keyed (drops off once raised) with its metric preset. 24-hour list shortened; misses panel taller and scrolls.

## 2026-10-22 · Quality app + NCR (ISO 9001:2015 8.7 / 10.2)
- QA Rework renamed **Quality** (Eric). **Quality_v5** (Screen1 REWORK, same as QA_Rework_v4 plus REWORK / NCR LOG tabs) + **Quality_NCR_v1** (scrNCR).
- New list **NCR** (package + sandbox, 53 columns, indexed RaisedAt/Status/Line). Five stages, each stamped who/when: 1 IDENTIFY (found at, severity, line, date, shift, product, job, lot, customer/supplier, defect, qty, description, photo) · 2 CONTAIN (action, qty on hold, location) · 3 DISPOSITION (use as is / rework / repair / regrade / scrap / return to supplier; concession required for use as is; customer informed; authorized-by stamp; re-verification required after rework/repair/regrade) · 4 CORRECTIVE ACTION (needed? default yes for Major/Critical; root cause; could it happen elsewhere; actions into the Newspaper, Source NCR, RefKey = NCR #; RCA placeholder) · 5 VERIFY & CLOSE (effective? evidence; risks/QMS updated; close checklist; void, reopen).
- Defaults chosen (questions not answered): one log for internal, customer and supplier NCRs (Found at = In-process / Final inspection / Customer complaint / Supplier / incoming / Audit); number NCR-yyyy-#### from the list ID; disposition authority = the person who saves stage 3 (stamped). Close-by default from MDI_Config **NCR_DueDays** (30).
- Lookups: 9 rows, Category **NCR defect**. Choices added: Newspaper.Source "NCR", TS_Photos.Module "NCR". All also in the package (ensureRows / choiceAdds); provisioner rebuilt.
- Next: NCR counts into Tier 3 (un-stub QUAL_NCR, Pareto by defect, biggest misses).

## 2026-10-22 · QMS product (QTC 001 electronic board + internal audits + ISO binder)
- Eric: build an ISO audit and management system on the QTC 001 T-card framework. Decisions: virtual board is the status of record (draft amendment QTC 001-4/Amd 1 written), one nonconformity log (NCR gains NCType: Product / QMS finding / Customer complaint / Supplier), standalone brand-neutral product, board + audits first. Eric 11:50: evidence goes in too → ISO binder.
- New folder `_QMS_Product\`: provision_qms.js(.txt) (8 lists + QMS_Binder library; seeds 66 QTC 001-3 cards parsed from the catalogue docx, 89 internal audit questions in our own words by audit-map scope P1–P12 + P7A, installation settings), install_qms_flow.js.txt (solution QMS, flow QMS - Upload Evidence), 4 screens (QMS_Board_v1 Screen1, QMS_Audits_v1 scrAudit, QMS_Binder_v1 scrBinder, QMS_Setup_v1 scrSetup), QMS_BUILD_GUIDE.md, amendment draft docx.
- BOARD: 12 month racks + escalation (computed: due/WIP after month end; done returns to own month), lane strip colors, head band color + state word, card body (side 1) + completion block (side 2) with WIP / DONE / NOT USED (steward) / REOPEN, RAISE → NCR (QMS finding linked to the pull), FILE IT to the binder; event pack with suggestions from NCR (complaints → X05, use as is → X10); X12 done places T01–T05; MONTH OPEN, CLOSE MONTH (Form F-04 in QMS_MonthClose); KPI strip = QTC 001-5 Table 1 indicators.
- AUDITS: programme P1–P12, start/header, independence warning (auditor owns cards in scope), rating per question with evidence, RAISE NCR per minor/major, evidence to binder, ISSUE REPORT completes E05 for the month (record = audit ref, findings = NCRs).
- ISO BINDER: clause list (49 requirement clauses, QTC 001-1 Annex A) with files / open NC / % pulls done; per clause: card pulls, binder files, audit results, open NCs, add photo.
- SETUP: installation settings (F-01), calendar map, GENERATE / TOP UP DECK (only adds missing instance IDs), apply owner changes, coverage check, card register (F-03) editable, retire with F-02 reason (Core blocked).
- Sandbox: all QMS lists created and seeded (Cards 66, AuditQs 89, Config 10); NCR got NCType, Clause, AuditRef, PullRef + disposition "Not product (QMS finding)"; flow "QMS - Upload Evidence" created in solution MDI using the connected SharePoint reference (Off: Eric turns it on).
- Quality_NCR_v2: TYPE dropdown; for non-product types defect/qty optional; disposition "Not product (QMS finding)"; list rows show type, clause, audit ref.
- Open: management review screen (E06 pack, E07 decisions → Newspaper, E08), month-open/close flows, print files for physical cards, US-English pass on catalogue text (QTC docs use UK spelling).

## 2026-10-22 (afternoon/evening): Voyant packaged install — no hand-built apps
- Golden copy = sandbox (SVEND (default) env, site MDISandbox), solution **MDI**. All 9 apps checked against their cards and latest files: HxH v20, T2 v18, T3 Board v9 / Bowler v6 / Variances v6, Quality v5 + NCR v2, TS Maintenance v5, TS Binder v2, Newspaper v7, SW Manager v4, PC Audit v4. Packages are built from the **published** apps (a saved-but-unpublished app ships its old version).
- Photo flow standard: apps send the photo as base64 text; sandbox MDI - Upload Photo put back to the text input (it had been reverted to a file input). Every app's flow registration refreshed.
- HxH v20: PLAYBOOK standard loads on open without REFRESH; DT reason boxes no longer show another row's pick (blank-default fix). Lunch-as-downtime idea and search combo boxes dropped (pasted ComboBoxes render blank rows).
- Setup flow **MDI - Set Up Site** (solution MDI Setup): builds/updates the 33 lists on any site, seeds, perms, emails the MDI2 setup code (also saved in MDI_Config → Setup_Code). Fixed: hidden "_Level" field fooled the field check (Escalation_Contacts.Level). Safe to re-run; adds only what's missing.
- Apps and flows now read the site and lists through **32 environment variables** (1 site + 31 lists, shared across apps; Eric rewired the 94 app connections in Studio, I converted the 5 flows via API).
- **MDI - Connect Site** (in MDI): paste the MDI2 code → sets all variables, restarts the MDI flows. Works, but uses the Dataverse connector = **Power Automate Premium**. Kenny has no premium → for non-premium customers build the package per customer instead.
- Per-customer builder: `deploy\package\build_package.js` (run in the sandbox crm console with the customer's code) → MDI_<site>_managed_v<ver>.zip with the site/list IDs (and variable values) rewritten. Verified: no sandbox references left.
- Rehearsed on dev env **MDI Install Test** (site MDIInstallTest): setup flow, package import, Connect Site, upgrades 1.0.1 → 1.1.1. Hour x Hour wrote to the test site only.
- **Kenny (Vee Pak, LLC (default), site veepak1…/sites/OhioContinuousImprovement): installed** — MDI Setup zip + MDI_OhioContinuousImprovement_managed_v1.1.2.0.zip; 4 flows on (Frontier off); real HxH data showing on Tier 3. Lesson: importing the generic package before the variables point at the customer's site leaves the flows off ("GetTable Unauthorized").
- To ship a fix: change in sandbox → Publish → raise MDI version → export (or build per customer) → customer imports as **Upgrade**.
- Open: Tier 3 Variances shows blank RAISE rows under Biggest Misses; rename sandbox app "Tier 1 Hour x Hour_202610221040"; builder page for non-premium customers; one-page install guide (two zips, order, turn off old flows, `&hidenavbar=true` links); Kenny's old hand-built flows to turn off; optional Kenny playground dev env (unmanaged copy); GitHub staging-branch question still open.


## 2026-11-17: Handoff to Kenny
- Eric is off the Voyant engagement. Kenny (Voyant) owns New Albany; Christina DeRamos runs Holmdel day to day with Kenny as the contact.
- State at handoff: MDI 1.1.4.1 + MDI Setup 1.0.0.0 in Vee Pak (default); Holmdel `MDI Tier 2 - Excel boards (no lists)` 1.0.0.19.
- Repo became the developer kit: START_HERE (setup for Kenny), CLAUDE.md + skills (/change-app, /ship-upgrade, /troubleshoot), HANDOFF (rebuild from scratch, backups, ownership, open items), SYSTEM_REFERENCE, TROUBLESHOOTING.
- `generator/make.py check` rebuilds all 23 app screens identical to deploy/apps; `holmdel/make.py check` rebuilds Holmdel 1.0.0.19 identical apart from the platform version stamp.
- Kenny's editable copy: import `solution/MDI_OhioContinuousImprovement_UNMANAGED_v1.1.4.1.zip` into a new **MDI Dev** environment; ship changes as managed upgrades from there. Eric's sandbox is no longer the golden copy.
- Open items: HANDOFF.md §7.
- 2026-11-18: Setup docs corrected for how Kenny actually works: Claude Code on the web in this repo (no desktop app, no fork, nothing installed locally). START_HERE.md rewritten (files reach him via GitHub links on the session branch; merge to `main` once live). `py` → `python3` in CLAUDE.md, skills, HANDOFF, Holmdel README. Kenny's `test/solution-1.1.4.2` branch left as-is (test repack, not a release).
- 2026-11-18: Repo restructured into one folder per plant with the same layout. New Albany's `generator/`, `deploy/`, `solution/`, TROUBLESHOOTING, SYSTEM_REFERENCE and this log moved under `newalbany/`; new `newalbany/README.md`. Paths in all docs and skills are now from the repo root. `make.py check`: 23 identical.
- 2026-11-18: Fault-injection pass (RISK_REGISTER.md §7). `make.py check` now clears old output first, flags screens NOT DEPLOYED / NOT REBUILT, compares the generated flows with `deploy/flows/json` and lints every flow (`generator/lint/flowlint.py`, a copy of Holmdel's lint2 with base64/decodeBase64/base64ToBinary/float and optional substring length). `lint` fails on bracket errors (fxcheck exit code) and runs new `generator/lint/sources.py` (list-name typos, Set/UpdateContext/Navigate inside ForAll). Still not caught: mixed-type 2-arg IfError, references to missing controls/screens (Studio flags both on paste). New RISK_REGISTER.md; CLAUDE.md and skills now end every reply with a question, the next step and copyable prompts.
- 2026-11-18: New list / new app path. `NEW_APP_GUIDE.md` (how install works: mdi_package.json → Set Up Site → MDI2 code → 32 environment variables matched by display name → apps; step-by-step; failures) and `/new-app` skill. New make targets `flow-setup` and `flow-connect` (both reproduce the deployed flows), so `check` now covers all 9 flows. New `generator/setup_package.py` rebuilds the MDI Setup zip from the package (`check` reproduces the shipped 1.0.0.0 flow) and `generator/starter_app.py` writes a browse/add/edit/retire screen for any list in the package (linted, not yet run in Studio). Dry run in a copy: added an example list, setup zip held 34 lists, starter linted clean. Found: re-running Set Up Site resets default views and list permissions on every MDI list (documented).
- 2026-11-18: **MDI 1.1.4.2 (not yet tested): escalation start follows the setting.** HxH - Downtime Escalation ignored MDI_Config `Escalation_FirstLevelMin` (trigger fixed at 60). Now the trigger wakes at 15 min (the plan's first tier), reads the setting (blank = 60) and Terminates as Succeeded below it (Terminate, not an empty branch, so Catch doesn't fire). Unchanged behavior at the default 60. Generator `flows.py` (ESC_FLOOR), `deploy/flows/json/01`, spec, SYSTEM_REFERENCE updated. `solution/MDI_OhioContinuousImprovement_UNMANAGED_v1.1.4.2.zip` = 1.1.4.1 with only `solution.xml` and that flow's JSON changed (patched flow verified equal to the generator's apart from site/list references). Apps unchanged (`make.py check`: 23 identical). Next: import into MDI Dev (Kenny's MDI_Sandbox) with flows off, check the flow, then export managed and upgrade production.
- 2026-11-18: Instructions updated: Kenny's dev environment is named `MDI_Sandbox` (= "MDI Dev" in the docs; noted in START_HERE and CLAUDE.md, not renamed throughout). Import steps in START_HERE, HANDOFF §3B and TROUBLESHOOTING §1 now import with flows **off** and check they're Off (MDI Dev points at the real Ohio lists). New START_HERE Part 1 §4: managed vs unmanaged, and Power Apps vs Power Automate (same Solutions list per environment; My flows = outside solutions).
- 2026-11-18: **Flow-change route proven (repack, no designer edits).** Kenny imported `MDI_OhioContinuousImprovement_UNMANAGED_v1.1.4.2.zip` into MDI Dev (`MDI_Sandbox`); HxH - Downtime Escalation opened in the designer as Trigger → Get first level → Below first level (True: Stop below first level; False: 0 actions), no error markers, nothing to save. Production MDI Settings → ESCALATION → FIRST LEVEL = 60, so shipping 1.1.4.2 doesn't change when escalations fire. Seen on the same screen: no active escalation contacts listed and the flow-failure alert e-mail blank (configuration, not code; Kenny to check). Made the route repeatable:
  - `newalbany/generator/patch_solution.py <old> <new> "<Flow name>"`: replaces named flows' triggers/actions in the newest unmanaged zip with the generator's, re-pointed to the environment variables; bumps the version; copies everything else byte for byte; refuses on missing list variables or leftover sandbox references. Reproduces the imported 1.1.4.2 (same content; JSON key order differs). Run over all six generated flows it changes nothing but key order, so **the generators match every installed flow**.
  - Gotchas found building it: Python's `ZipFile.writestr` mutates the ZipInfo it's given (copy it, or the source zip reads back as "overlapped entries"); customizations.xml `<Workflow>` tags may carry a `Description` attribute after `Name`.
  - New skill `/change-flow`; CLAUDE.md "Changing a flow"; START_HERE skills list; solution README.
  - Still to do for 1.1.4.2: managed export from MDI_Sandbox and upgrade in production (`/ship-upgrade`), then PR to `main`.
- 2026-11-18: **MDI 1.1.4.2 live in production** (Vee Pak, LLC (default)). Kenny exported it as managed from MDI_Sandbox, imported it into production as an upgrade, and confirmed the flows On and working. First change shipped through the full route: generator → patched unmanaged zip → MDI Dev import → managed export → production upgrade. FIRST LEVEL was 60, so escalations still start at 60 min. `newalbany/solution/…_v1.1.4.2.zip` is now the editable source (1.1.4.1 kept, marked superseded). Docs updated to name 1.1.4.2 as current. Still open from the same check: no active escalation contacts listed and `Alert_Email` blank in MDI Settings (RISK_REGISTER §3, §5).
- 2026-11-19: **Hour x Hour v23 pasted in MDI_Sandbox and working** (Kenny's screenshot): LINE must be picked first (no default 209; rows, Safety and saves locked until then) and DATE opens a calendar built from standard controls (Holmdel Tier 2 pattern; any past date, future days disabled; date pinned on first load so a night shift past midnight keeps its date).
- 2026-11-19: **Hour x Hour v24: DT1 + DT2 can't exceed the hour.** Kenny asked to cap the sum at 60. Capped at the row's `SlotMin` (60 for a full hour, 30 for the last half-hour slot); an entry that would go over shows a warning, resets the box to its saved value and saves nothing. Only gDT1/gDT2 OnChange and tooltips changed vs v23. Not yet pasted.
- 2026-11-19: **Hour x Hour v25: hour notes in a popup.** Kenny: the NOTES box (68 px) was too small. The row now shows a button with "+ note" or the first words of the note (full note on hover); tapping opens a popup (multi-line box, up to 2,000 characters, SAVE NOTE / CANCEL; nothing saves until SAVE, a click outside doesn't close it). HxH_Hourly.Notes is a multi-line column, so long notes fit. The LINE placeholder is now "PICK" (v23's "— PICK LINE —" showed as "— PIC"). Not yet pasted. Kenny's screenshot still showed the 7-day DATE dropdown, so the file he pasted was an older v23 (possibly a cached raw link); check the DATE button reads "date ▾" after pasting v25.
- 2026-11-19: Paste instructions rewritten in plain words (Kenny: "regular people don't know what first to last means"). New START_HERE section "Replacing a screen"; CLAUDE.md and the change-app skill now point to it and ban developer shorthand.
- 2026-11-19: **Hour x Hour v26.** Job numbers (Job 1 and per-hour Job): numbers only, up to 6 digits (`IsMatch(Self.Text, "\d{1,6}")`; MaxLength 6 was already there since v16); a bad entry warns, resets and isn't saved. The hour cap now covers **DT1 + DT2 + PLAN** (was DT1 + DT2), checked on all three boxes, against the row's SlotMin (60, or 30 for a half-hour slot). Not yet pasted.
- 2026-11-19: **Hour x Hour v26 (same version, not yet pasted) also gets a mandatory safety description.** Tapping SAFETY opens a popup instead of toggling: REPORT EVENT stays disabled until at least 5 characters are typed, CANCEL leaves the hour OK. The text saves to HxH_Hourly.SafetyNotes (column existed but the board never wrote it; Tier 3 Biggest Misses already reads it). Tapping an EVENT hour shows its description (editable) and a NOT AN EVENT (UNDO) button for mistakes.
