# Virtual MDI — Deployment Package

> **This is the original hand-build install** (lists by console script, flows by console script, apps pasted one by one). It still works and is the fallback if packages won't import. The faster package route, and every recovery scenario, is in `../../HANDOFF.md`.
*Built in the SVEND sandbox (Verxted tenant), packaged for Voyant New Albany. All Microsoft 365: SharePoint lists + Power Apps + Power Automate. No premium connectors.*

## What's in the box
| Module | App (file) | Who uses it | Device |
|---|---|---|---|
| Hour x Hour | **HxH Board** (`apps/HxH_Board_v24.pa.yaml`) | Line leads / operators, every hour | Line tablet / TV |
| Downtime escalation | Flow **HxH - Downtime Escalation** | Automatic (Teams to contacts at 60/120/240 min) | — |
| QA rework | **QA Rework** (`apps/QA_Rework_v4.pa.yaml`) | QA | Tablet / PC |
| Troubleshooting | **TS Maintenance** (`apps/TS_Maintenance_v5.pa.yaml`) | Maintenance (QR at machine) | Phone |
| Troubleshooting binder | **TS Binder** (`apps/TS_Binder_v2.pa.yaml`) | Operators (read-only) | Line tablet / TV |
| Standard work + PC cards + 5S standards | **SW Manager** (`apps/SW_Manager_v4.pa.yaml`) | OpEx / supervisors / engineers | PC |
| Process confirmation | **PC Audit** (`apps/PC_Audit_v4.pa.yaml`) | Tier 1–3 auditors (QR on card/station) | Phone |
| Action register | **Newspaper** (`apps/Newspaper_v7.pa.yaml`) | Tier 1/2 meetings, owners | Tablet / PC / TV |
| Photos | Flow **MDI - Upload Photo** (shared by all apps) | — | — |
| Safety + 5S (optional) | **Frontier Audit** (`apps/Frontier_Audit_v2.pa.yaml`) + flow **MDI - Frontier Critical Alert**: DuPont STOP-style zone audits, 5S against the zone's standard photos. See `FRONTIER_LITE.md` | Frontier auditors (QR at zone) | Phone |
| Tier 2 roll-up | **Tier 2 Board** (`apps/T2_Board_v19.pa.yaml`): floor → line / domain → line × domain, 7-day trend, downtime events; Safety includes Frontier hazards | Tier 2 meeting | TV / PC |

Data: 28 SharePoint lists/libraries (24 core + 4 Frontier: SAF_Zones, SAF_Items, SAF_Audits, SAF_Results) (see `provision_mdi.js.txt` / `mdi_package.json`). Shared lists: Lines, Lookups, People, Assets, MDI_Config, PLAYBOOK, Newspaper, TS_Photos.

---
## Deployment order (≈ half a day)

### 0. Prerequisites
- A SharePoint site you own (e.g. `/sites/NewAlbanyMDI`) — members = everyone who enters data.
- Power Apps + Power Automate with standard M365 licenses (SharePoint + Teams connectors are standard).
- M365 accounts for: supervisors, QA, maintenance, OpEx, managers. **Line tablets/TVs** run under a shared kiosk account that is a site member.

### 1. Lists — `provision_mdi.js.txt` (5 min)
1. Open any page of the target site in Edge/Chrome → **F12 → Console**.
2. Open `provision_mdi.js.txt` in Notepad, select all, copy, paste into the console, Enter. It creates every list + column + pill formatting + view, then seeds **Lines, Lookups (reasons/equipment), MDI_Config, Escalation_Contacts (roles), PLAYBOOK**. Safe to re-run.
3. Check the console ends with `DONE`. Any `field failed` warnings → re-run once.

### 2. Fill the plant data (owner: Voyant)
| List | Fill in |
|---|---|
| **Lines** | ValueStream for each line; untick Active for lines not in use |
| **People** | Name, email, role, tier, shifts, lines — drives PC tiers and NEWSPAPER owners. Tick **CanLinkDowntime** only for the few people allowed to link troubleshooting records to board downtime after the fact |
| **Escalation_Contacts** | Name + email per role row, Active = Yes, shift-specific Y/N + shifts |
| **Lookups** | Review downtime / scrap / speed / headcount / rework reasons and equipment types. **Retire with Active = No — never delete** |
| **PLAYBOOK** | Confirm rates/crew/efficiency (seeded from Playbook_Summary_Current) |
| **Assets** | Optional: one row per machine (line, equipment type, model, asset tag) |

### 3. Flows: `tools/install_flows.js.txt` (10 min)
> First paste into an F12 Console is blocked by Edge: type `allow pasting`, Enter, then paste again.

1. Find the environment address: **make.powerapps.com → gear → Session details → Instance url** (`https://orgXXXXXXXX.crm.dynamics.com`). Open it in Edge and sign in.
2. Press F12 → Console, paste the whole file, press Enter, and paste the **SETUP CODE** that step 1 printed (and copied to the clipboard) when asked.
3. It creates the **MDI** solution (publisher SVEND, prefix `svend`), connection references **MDI SharePoint / MDI Microsoft Teams / MDI Office 365 Outlook**, and the four flows (**Off**), already pointed at your site's lists. Re-running skips anything that exists.
4. In the solution: **Connection references** → pick a connection for each → Save. Then **Cloud flows** → Turn on all five (the fifth, Frontier Critical Alert, only if you use Frontier). Fill **MDI_Config → Alert_Email**.

Manual alternative: build the flows by hand inside a solution named MDI from `flows/*.md` (exact definitions in `flows/json/`). Power Apps Studio only lists flows that live in a solution.

### 4. Apps — `apps/` (10 min each)
**Full walkthrough with one card per app: `apps/APP_BUILD_GUIDE.md`.** Summary:

For **each** app:
1. make.powerapps.com → **+ Create → Blank canvas app** → name + format (table below).
2. **Settings → Display**: size (table below). Tablet = Custom 1920 × 1080, scale to fit on; Phone = default, portrait. **Settings → General → Data row limit = 2000.**
3. **Data → Add data → SharePoint → your site** → tick the lists in the table. Add the **MDI - Upload Photo** flow where marked — via the **Power Automate pane → + Add flow** (not Add data; search if it is not listed).
4. Open the `.pa.yaml` file, select all, copy → in the Tree view right-click **Screen1 → Paste**.
5. Select **Screen1** → property **OnVisible** → paste the formula below.
6. Alt+click the REFRESH button once (loads data in the editor). Fix any red ⚠ (usually a data source not added). **Save → Publish → Share** (with the right people / the kiosk account).

| App | Format / size | Data sources | Flow | Screen1.OnVisible |
|---|---|---|---|---|
| HxH Board | Tablet 1920×1080 | PLAYBOOK, HxH_Hourly, HxH_Shift, Lookups | – | `Select(btnRefresh)` |
| QA Rework | Tablet 1920×1080 | QA_Rework, Lookups, PLAYBOOK, HxH_Shift | – | `Select(btnQRefresh); Select(btnQCtx)` |
| TS Maintenance | **Phone** | Lookups, Lines, Assets, TS_Issues, TS_Fixes, TS_Procedures, TS_Steps, TS_Occurrences, TS_Photos, HxH_Hourly | ✔ | `Select(btnMRefresh)` |
| TS Binder | Tablet 1920×1080 | Lookups, Lines, TS_Issues, TS_Fixes, TS_Steps, TS_Occurrences, TS_Photos | – | `Select(btnBRefresh)` |
| SW Manager | Tablet 1920×1080 | SW_Standards, SW_Elements, PC_Cards, PC_CardItems, PC_Audits, PC_Results, TS_Photos, MDI_Config, Lookups | ✔ | `Select(btnSRefresh)` |
| PC Audit | **Phone** | PC_Cards, PC_CardItems, PC_Audits, PC_Results, SW_Elements, TS_Photos, Newspaper, Lines | ✔ | `Select(btnPRefresh)` |
| Newspaper | Tablet 1920×1080 | Newspaper, People, Lines, TS_Photos, PC_Audits | ✔ | `Select(btnNRefresh)` |
| Tier 2 Board | Tablet 1920×1080 | HxH_Shift, HxH_Hourly, QA_Rework, TS_Occurrences, TS_Issues, TS_Fixes, PC_Audits, PC_Results, PC_Cards, SW_Elements, Escalation_Log, Newspaper, Lines, MDI_Config, PLAYBOOK, Lookups, People, SAF_Audits, SAF_Results | – | `Select(btnRefresh)` |

### 5. Links + QR codes (15 min)
1. For each published app: ⋯ → **Details → Web link** → paste into **MDI_Config** (`App_HxH`, `App_QARework`, `App_TSMaintenance`, `App_TSBinder`, `App_SWManager`, `App_PCAudit`, `App_Newspaper`). SW Manager then shows each card's QR link.
2. QR labels: open the app link with its parameters in **Edge** (e.g. TS Maintenance web link + `?line=209&equip=Labeler`; PC Audit link + `?card=1`) → right-click the page → **Create QR code for this page** → Download. Paste the QR images into a Word/PowerPoint label sheet with the line/machine name in large text. SW Manager shows each PC card's full link. Eric can also send ready-made label PDFs.
3. Deep-link parameters: HxH/Binder/Newspaper `?line=209`; TS Maintenance `?line=&equip=&asset=`; PC Audit `?card=<ID>&line=`.

### 6. Go-live checklist
- [ ] Lists provisioned, plant data filled (step 2)
- [ ] All flows On and tested (Frontier alert: a test Critical finding reaches Safety_Email in Teams): escalation (test contact gets the Teams message), Sync Permissions (flip a People switch, check the group), Nightly Board Check (run once, digest arrives)
- [ ] All apps published + shared; kiosk account can open HxH Board, TS Binder, Newspaper
- [ ] One full shift dry run on one line (HxH every hour, one escalation, one QA entry, one TS occurrence, one PC card, actions in Newspaper)
- [ ] QR labels at machines/stations
- [ ] Remove test rows (any row with TEST/SAMPLE in the title)
- [ ] Tier 1 meeting uses HxH + Newspaper on the TV; Tier 2 uses the Tier 2 Board (yesterday by default) + its Newspaper panel

### Suggested rollout (one module a week)
1. HxH Board + escalation (one line → all lines) · 2. QA Rework · 3. Newspaper in Tier 1/2 · 4. Troubleshooting (maintenance first, binder next) · 5. Standard work + PC cards (Tier 1 MDI audit first) · 6. Tier 2 Board once a week or two of data has built up (the trend needs 7 days). · 7. Frontier safety + 5S audits (zones + 5S standards first; see `FRONTIER_LITE.md`).

---
## How it hangs together
- **Keys:** shift `Line-yyyymmdd-S#` (ShiftKey on every record), hour `…-H##`, product `Line|Size|Form` (PLAYBOOK).
- **Every module feeds NEWSPAPER** with a Source + RefKey (escalation, QA, troubleshooting, process confirmation, yellow tags next).
- **One photo library** (TS_Photos) tagged by Module + RefID (+ StepNo, Kind). Latest photo wins.
- **Reasons and equipment** come from Lookups — add a row, every app picks it up on refresh.
- **Ranking** (troubleshooting) = occurrences in the last 90 days. **Adherence** (PC) = audits done ÷ expected from card frequency × shifts.

## Downtime ↔ troubleshooting (one source of truth)
- **The HxH board owns downtime.** An event = line + shift + reason, `EventKey = ShiftKey|Reason` (same unit the escalation flow and Tier 2 use).
- **TS Maintenance** asks *"which downtime is this?"* right after the machine is picked: open board events for that line + machine in the last 24 h. The tech taps one (LinkStatus = Linked at fix) or "Not on the board yet" (Not on board). The tech logs **repair time**, not downtime.
- **Lookups.EquipType** maps each machine downtime reason to an equipment type. Add it for any new machine reason.
- **Tier 2 → ⇄ RECONCILE** (line or cell view; all shifts, 7 days):
  - **Left:** TS records with no board event.
  - **Right:** machine stops of **T2_TSRequiredMin (15) min or more** with no TS record. Candidates are ranked by match score: same machine +50, same shift +30, closeness in time up to +20. 80+ = STRONG, 50–79 = possible.
  - **LINK** a record to its stop.
  - **NO TS NEEDED** + reason waives a stop (operator cleared it, minor stop, covered by another record, not equipment). The waiver is stored as a TS_Occurrences row with LinkStatus = Waived, who and when. Waivers are excluded from all TS counts.
  - Both actions require People.CanLinkDowntime = Yes.
- **Clickable rows:** in Tier 2's downtime and maintenance detail tables, unresolved rows are tinted with a ⇄ LINK pill. Tapping one opens reconcile with that row **and its strongest match (score ≥ 50) already picked**. Downtime-event lists open the line's downtime detail.

## Newspaper progress (Harvey balls)
- `Newspaper.Progress` = 0 / 25 / 50 / 75 / 100. Tap the ball to step it. Status follows: 0 Open, 25–75 In progress, 100 Done (closed date stamped). Canceled is set in the edit panel.
- A red outline means past due and not done.

## Access (managed from the People list)
| People switch | Group | Can do |
|---|---|---|
| Active | site Members | Add and edit data (no delete); read config |
| CanEditConfig | MDI Config Editors | Edit config: PLAYBOOK, Lookups, People, contacts, lines, standards, PC cards |
| MDIAdmin | site Owners | Everything, incl. delete |
| CanLinkDowntime | (app rule) | Link or waive downtime in Tier 2 reconcile |

- The provisioner creates the **Contribute - no delete** level, the **MDI Config Editors** group and every list's permissions. **Flow 03** keeps group membership in step with the switches.
- **Keep one IT site owner who is not in People**, so nobody can switch off the last admin.
- QA entries are **voided**, not deleted: the row is kept, flagged and excluded from counts. Admins purge if needed.
- The person who runs the provisioner also gets a direct Full Control grant on each list (SharePoint does this when breaking inheritance). Harmless.

## Flow failure alerts
Every flow ends with a **Catch** scope that runs only if the last step failed, timed out or was skipped (any earlier failure makes it skip). Catch emails `MDI_Config → Alert_Email` with a direct link to the failed run. Email goes through the solution's **MDI Office 365 Outlook** connection reference. The exact steps are at the end of each flow file. The full definitions are in `flows/json/`.

## Built-in protections
- **Indexes:** the provisioner indexes every column the apps and flows filter on (56 columns), so lists keep working past SharePoint's 5,000-item threshold. HxH_Hourly passes 5,000 rows in about two weeks at 15 lines.
- **Unique keys:** HxH_Shift and HxH_Hourly titles (ShiftKey / hour key) are enforced unique, so two tablets can never create the same shift or hour twice. The second save fails with a visible error.
- **Daylight saving:** shift length and hour slots use real local clock times. The fall-back night gets its extra hour (an extra slot when needed); spring-forward loses one.
- **Escalation flow:** notifies once per shift + reason + level + contact, with trigger concurrency 1. Editing earlier hours does not re-notify.
- **Offline-safe board:** if an hour can't be saved (Wi-Fi drop), the HxH board keeps it on the tablet. A red banner shows the waiting hours, and the board retries before every save and refresh (plus a RETRY NOW button). Keep the app open while the banner shows.
- **Nightly board check (flow 04):** at 6:30 AM, any shift from yesterday with 2+ unfilled hours becomes a NEWSPAPER action, and OpEx gets a digest (incl. active lines with no board).
- **Test data:** `tools/clear_test_data.js.txt` moves test/demo rows to the recycle bin. `demo` = sandbox demo rows; `reset` = all transactions before a cutoff (go-live clean slate), keeping config. It always reports first (DRY_RUN).

## Scale (15 lines and beyond)
- **Tier 2 floor density** adjusts to the number of lines shown:
  - **≤ 6 lines:** full tiles (value, sub-line, 7-day blocks).
  - **7–12 lines:** compact (value and blocks; sub-line on hover).
  - **13+ lines:** dense (≈ 37 px rows). 15 lines fit on one 1080p screen; beyond 15 the grid scrolls.

  For a 1:1 Tier 2 per value stream, set the VALUE STREAM filter.
- **Row limit 2,000 per load.** Every load is filtered to a window that stays well under it at 15 lines × 3 shifts. Newspaper loads only open/in-progress actions plus those recently closed (Tier 2: 7 days; Newspaper app: 60 days). Older closed actions stay in SharePoint.
- **Seeding test data:** never write `EscReason`/`EscCumMin` on HxH_Hourly while the escalation flow is ON. The flow will send real Teams escalations. Turn the flow off first.

## Gotchas (learned the hard way)
- **Newer Power Apps builds type-check `IfError` strictly.** `IfError(Patch(...), Notify(...))` fails with "Invalid argument type (Boolean). Expecting a Record" because the save returns a record and Notify returns true/false. Every app now uses `IfError(value, Notify(...), true)`. If you hand-write a formula, follow the same form.
- Never name a SharePoint column `Value`, `Text`, `Date` or `Author` — Power Fx/SharePoint collisions.
- Pasting YAML only brings controls — screen OnVisible and app size must be set by hand.
- `Sum()` of an empty table is Blank and `Blank() = 0` is false → apps use `Coalesce(…, 0)`.
- Power Fx time formats need AM/PM or they switch to 24-hour.
- After renaming a column, refresh the data source in the app (Data → ⋯ → Refresh).
- Calculated columns created by script need formulas written with **display names** in brackets.
- Power Apps → Add flow lists **only solution-aware flows** — keep flows in the MDI solution.
- Tier 2 colors come from **MDI_Config** (`T2_AttainGreen/Amber`, `T2_OEEGreen/Amber`, `T2_ReworkAmber/Red`, `T2_PCGreen`, `T2_DTAmber/Red`): change the number, tap REFRESH. No app edit needed.

## Files
- `provision_mdi.js.txt` — run in the browser console on the target site (lists, columns, formatting, views, seed).
- `mdi_package.json` — the same schema + seed as data (for review / other tooling).
- `apps/*.pa.yaml` — the apps. They are generated on Eric's side; send design changes to Eric rather than hand-editing the YAML.
- `flows/*.md` — flow build specs (`flows/json/` = exact definitions); `tools/install_flows.js.txt` builds them all.
- `FRONTIER_LITE.md` — the Frontier safety + 5S audit module: what it does, setup, cadence.
- `DRY_RUN_SHIFT.md` — one-shift end-to-end test script.
