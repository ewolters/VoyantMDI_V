# Building the 9 MDI apps
*About 10 minutes per app, about 1.5 hours in total. Do this after the lists (step 1) and the flows (step 3) are in place.*

Each app is built the same way:
1. Create a blank app.
2. Set its size.
3. Connect its lists.
4. Paste in its design (the `.pa.yaml` file).
5. Set one start-up formula.
6. Publish and share.

Section 1 is the common procedure. Section 2 has one card per app with everything that differs. Section 3 covers the usual errors.

**Use only the files in this `apps/` folder.** Any other copies with different version numbers are out of date.

**Build order** (most important first, and Tier 2 last because it reads everything):
1. HxH Board
2. Quality (rework + NCR)
3. TS Maintenance
4. TS Binder
5. Newspaper
6. SW Manager
7. PC Audit
8. Tier 2 Board
9. Frontier Audit (safety + 5S), optional module

---

## 1. The procedure (repeat for each app)

### Step 1. Create the app
1. Go to **make.powerapps.com**. Check the environment (top right) is the same one the flows were installed into.
2. Click **+ Create**, then **Blank app**, then **Blank canvas app**.
3. **App name:** use the name on the app's card. **Format:** Tablet or Phone, as on the card.
4. Click **Create**. If a "Welcome to Power Apps Studio" box appears, close it (**Skip**).

### Step 2. Settings (before pasting anything)
Open **Settings** (gear icon or ⋯ in the top bar).
1. **General → Data row limit:** set to **2000**.
2. **Display**, for **Tablet** apps:
   - Size: **Custom**, Width **1920**, Height **1080**.
   - **Scale to fit:** On. **Lock aspect ratio:** On. **Lock orientation:** On (landscape).
3. **Display**, for **Phone** apps: leave the default size (640 × 1136) and set orientation to **Portrait**.
4. Close Settings.

> Pasting the design does **not** set these. If you skip this step, the screens come out cropped or squashed.

### Step 3. Connect the lists
1. In the left rail, click the **Data** icon (the cylinder), then **+ Add data**.
2. Search **SharePoint** and pick it. Choose the existing connection (the same account used for the flows), or add one.
3. Paste the **site address**, e.g. `https://voyant.sharepoint.com/sites/NewAlbanyMDI`, then **Connect**.
4. Tick **every list on the app's card**, then **Connect**.
   - **TS_Photos** is a document library. If it isn't in the list, look under **Libraries**.
   - The names must match exactly. Don't rename data sources.
5. If the card says **Flow: yes**: in the left rail click the **Power Automate** icon (lightning bolt), then **+ Add flow**, and pick **MDI - Upload Photo**.
   - It shows up in the app as `MDI-UploadPhoto`; that's correct.
   - It's only listed if the flow is **in the MDI solution and turned On**. The flow installer does both.

### Step 4. Paste the design
1. Open the app's `.pa.yaml` file in **Notepad**. Press Ctrl+A, then Ctrl+C.
2. In Studio, open the **Tree view** (layers icon in the left rail).
3. Right-click **Screen1**, then **Paste**. All the controls appear on the screen. A large app (Tier 2) takes a few seconds.

### Step 5. Start-up formula
1. Click **Screen1** in the Tree view.
2. In the property dropdown at the top left (it usually says *Fill*), pick **OnVisible**.
3. In the formula bar to its right, paste the **OnVisible** formula from the app's card exactly.

### Step 6. Check, save, publish, share
1. **Load the data in the editor:** hold **Alt** and click the app's **REFRESH** button once.
2. **Red ⚠ icons?** Click one to read the error. Almost always it's a list on the card that wasn't added; go back to Step 3. If an error names a list you did add, open Data, then ⋯ next to that list, then **Refresh**.
3. **Save:** top right, **Save**. The first save uses the name from Step 1.
4. **Publish:** click **Publish**, then **Publish this version**.
5. **Share:**
   - Go back to make.powerapps.com, then **Apps**, then ⋯ next to the app, then **Share**.
   - Add the people or group on the card, plus the **kiosk account** where marked. Leave "Co-owner" **unticked**.
   - Sharing the app doesn't grant data access by itself. List access comes from SharePoint: the Members group and the People-list switches.
6. **Web link:**
   - Go to ⋯ next to the app, then **Details**, and copy the **Web link**.
   - On the SharePoint site, open the **MDI_Config** list and paste the link into **SettingValue** on the row named on the card.
   - QR codes and app-to-app buttons use these links.

---

## 2. App cards

### 1. HxH Board: hour-by-hour production board (line tablet / TV)
| | |
|---|---|
| **File** | `HxH_Board_v26.pa.yaml` |
| **Name / format** | `MDI HxH Board`, **Tablet** 1920 × 1080 |
| **Lists** | PLAYBOOK, HxH_Hourly, HxH_Shift, Lookups |
| **Flow** | no |
| **Screen1.OnVisible** | `Select(btnRefresh)` |
| **Share with** | supervisors, operators/leads, **kiosk account** |
| **MDI_Config row** | `App_HxH` |
| **Check** | Pick a line and shift. The hourly targets fill in from PLAYBOOK. Save an hour and a row appears in HxH_Hourly. |

### 2. Quality: rework log + NCR log (was QA Rework)
| | |
|---|---|
| **Files** | 2 screens: `Quality_v5.pa.yaml` → **Screen1** (REWORK), `Quality_NCR_v2.pa.yaml` → **scrNCR** (NCR LOG) |
| **Name / format** | `MDI Quality`, **Tablet** 1920 × 1080 |
| **Lists** (9) | QA_Rework, Lookups, PLAYBOOK, HxH_Shift, **NCR, Lines, Newspaper, MDI_Config, TS_Photos** |
| **Flow** | yes (photos on NCRs) |
| **Second screen** | Add it **before** pasting Screen1 (Screen1's tab button points to it): **+ New screen → Blank**, rename it `scrNCR`, paste `Quality_NCR_v2`. Then paste `Quality_v5` on Screen1. |
| **OnVisible** | Screen1: `Select(btnQRefresh); Select(btnQCtx)` · scrNCR: `Select(nLoad)` |
| **Share with** | QA techs, supervisors, quality manager, kiosk account if used at a QA station |
| **MDI_Config row** | `App_QARework` (existing row; keep the name) |
| **Check** | NCR LOG → + NEW NCR → fill the yellow fields → RAISE NCR. It gets a number (NCR-2026-0001) and moves to CONTAIN. Walk it through each stage; CLOSE stays grey until every check on stage 5 is green. |
| **Upgrading the old QA Rework app?** | Open it, add the 5 new lists + the flow, add scrNCR, then on Screen1 select all controls, delete, and paste `Quality_v5`. Rename the app to `MDI Quality` (Settings → General). |

### 3. TS Maintenance: troubleshooting and repair log (phone, from machine QR codes)
| | |
|---|---|
| **File** | `TS_Maintenance_v5.pa.yaml` |
| **Name / format** | `MDI TS Maintenance`, **Phone** (portrait) |
| **Lists** | Lookups, Lines, Assets, TS_Issues, TS_Fixes, TS_Procedures, TS_Steps, TS_Occurrences, TS_Photos, HxH_Hourly |
| **Flow** | **yes**: MDI - Upload Photo |
| **Screen1.OnVisible** | `Select(btnMRefresh)` |
| **Share with** | maintenance techs, supervisors |
| **MDI_Config row** | `App_TSMaintenance` (machine QR codes add `?line=209&equip=Labeler`) |
| **Check** | Log an occurrence. **"WHICH DOWNTIME IS THIS?"** lists the board's downtime for that line. Take a photo and it lands in TS_Photos. |

### 4. TS Binder: troubleshooting guide (line tablet)
| | |
|---|---|
| **File** | `TS_Binder_v2.pa.yaml` |
| **Name / format** | `MDI TS Binder`, **Tablet** 1920 × 1080 |
| **Lists** | Lookups, Lines, TS_Issues, TS_Fixes, TS_Steps, TS_Occurrences, TS_Photos |
| **Flow** | no |
| **Screen1.OnVisible** | `Select(btnBRefresh)` |
| **Share with** | operators, maintenance, supervisors, **kiosk account** |
| **MDI_Config row** | `App_TSBinder` |
| **Check** | Pick a line and a machine. Its issues and fixes list, with step photos. |

### 5. Newspaper: action register (Tier 1 and Tier 2 meetings)
| | |
|---|---|
| **File** | `Newspaper_v7.pa.yaml` |
| **Name / format** | `MDI Newspaper`, **Tablet** 1920 × 1080 |
| **Lists** | Newspaper, People, Lines, TS_Photos, PC_Audits |
| **Flow** | **yes**: MDI - Upload Photo |
| **Screen1.OnVisible** | `Select(btnNRefresh)` |
| **Share with** | everyone who attends Tier 1/2, plus the kiosk account on the meeting TV |
| **MDI_Config row** | `App_Newspaper` |
| **Check** | Open actions show with Harvey balls. Change Progress and the ball updates. |

### 6. SW Manager: standard work library and process-confirmation card builder (office)
| | |
|---|---|
| **File** | `SW_Manager_v4.pa.yaml` |
| **Name / format** | `MDI SW Manager`, **Tablet** 1920 × 1080 |
| **Lists** | SW_Standards, SW_Elements, PC_Cards, PC_CardItems, PC_Audits, PC_Results, TS_Photos, MDI_Config, Lookups |
| **Flow** | **yes**: MDI - Upload Photo |
| **Screen1.OnVisible** | `Select(btnSRefresh)` |
| **Share with** | OpEx, engineering, production managers (people with CanEditConfig) |
| **MDI_Config row** | `App_SWManager` |
| **Check** | The SAMPLE standard opens with photos. Each card shows its QR link once `App_PCAudit` is filled in. |

### 7. PC Audit: process confirmation (phone, from card QR codes)
| | |
|---|---|
| **File** | `PC_Audit_v4.pa.yaml` |
| **Name / format** | `MDI PC Audit`, **Phone** (portrait) |
| **Lists** | PC_Cards, PC_CardItems, PC_Audits, PC_Results, SW_Elements, TS_Photos, Newspaper, Lines |
| **Flow** | **yes**: MDI - Upload Photo |
| **Screen1.OnVisible** | `Select(btnPRefresh)` |
| **Share with** | supervisors, managers, OpEx |
| **MDI_Config row** | `App_PCAudit` (card QR codes add `?card=<ID>`) |
| **Check** | Run the SAMPLE card. Answering **No** with the action toggle on creates a Newspaper action. |

### 8. Tier 2 Board: daily Tier 2 meeting (meeting-room TV)
| | |
|---|---|
| **Files** | `T2_Board_v19.pa.yaml` → **Screen1** · `T2_Periods_v2.pa.yaml` → new blank screen **scrPeriods** (create it first; set its OnVisible to `If(IsEmpty(colPer), Select(btnPLoad))`) |
| **Name / format** | `MDI Tier 2 Board`, **Tablet** 1920 × 1080 |
| **Lists** (19) | HxH_Shift, HxH_Hourly, QA_Rework, TS_Occurrences, TS_Issues, TS_Fixes, PC_Audits, PC_Results, PC_Cards, SW_Elements, Escalation_Log, Newspaper, Lines, MDI_Config, PLAYBOOK, Lookups, People, SAF_Audits, SAF_Results |
| **Flow** | no |
| **Screen1.OnVisible** | `Select(btnRefresh)` |
| **Share with** | managers, OpEx, Tier 2 attendees, kiosk account on the meeting TV |
| **MDI_Config row** | `App_Tier2` |
| **Check** | Opens on **yesterday**, floor level. Tap a line, then an SQDC letter, to drill down. **Home** returns to the top. |

> Tier 2 is the largest app (300 KB). The paste takes 5–10 seconds, and the first Alt+REFRESH takes a few more.


### 9. Frontier Audit: safety + 5S observation audit (phone, from zone QR codes). Optional module.
| | |
|---|---|
| **File** | `Frontier_Audit_v2.pa.yaml` |
| **Name / format** | `MDI Frontier Audit`, **Phone** (portrait) |
| **Lists** | SAF_Zones, SAF_Items, SAF_Audits, SAF_Results, SW_Standards, SW_Elements, TS_Photos, Newspaper, MDI_Config |
| **Flow** | **yes**: MDI - Upload Photo |
| **Screen1.OnVisible** | `Select(btnFRefresh)` |
| **Share with** | trained Frontier auditors, the safety coordinator, supervisors |
| **MDI_Config row** | `App_Frontier` (zone QR codes add `?zone=FZ-NAL-TR-01`) |
| **Check** | Pick a zone and say why. Rate all 19 safety items: an **AR/U** item asks for severity, what you saw and a photo. Rate the 5S sections against the zone's standard photos. Fill in the 4 operator questions and close the loop, then **SUBMIT**. Check that one SAF_Audits row and 19+ SAF_Results rows appear, and that each AR/U finding has a Newspaper action with a due date set by severity. |

> Before this app is useful you need zones (SAF_Zones) and, ideally, a 5S standard per zone (SW Manager, type **5S**). See `../FRONTIER_LITE.md`.


### 10. Tier 3 Board: plant leadership meeting (meeting-room TV). One app, three screens.
| | |
|---|---|
| **Files** | `T3_Board_v9.pa.yaml` → **Screen1** (PERFORMANCE) · `T3_Bowler_v6.pa.yaml` → screen **scrBowler** · `T3_Variances_v7.pa.yaml` → screen **scrVariance** |
| **Name / format** | `MDI Tier 3 Board`, **Tablet** 1920 × 1080 |
| **Lists** (23) | the 19 Tier 2 lists (HxH_Shift, HxH_Hourly, QA_Rework, TS_Occurrences, TS_Issues, TS_Fixes, PC_Audits, PC_Results, PC_Cards, SW_Elements, Escalation_Log, Newspaper, Lines, MDI_Config, PLAYBOOK, Lookups, People, SAF_Audits, SAF_Results) **+ KPI_Daily, ValueStreams, Variances, KPI_Metrics** |
| **Flow** | no |
| **Screens** | Add two screens (**New screen → Blank**) and rename them exactly **scrBowler** and **scrVariance**. Paste each file onto its screen. |
| **OnVisible** | Screen1: `If(IsBlank(varLoadedAt), Select(btnRefresh))` · scrBowler: none · scrVariance: `Select(vLoad)` |
| **Share with** | plant manager and staff, OpEx, kiosk account on the meeting TV. Users need **edit** on KPI_Daily and Variances (site Members have it). |
| **MDI_Config rows** | `App_Tier3`; `T3_Var24Days` (default 7); `App_Newspaper` and `App_Tier2` for the jump buttons |
| **Check** | PERFORMANCE opens on yesterday, whole plant: one row per value stream (from **ValueStreams**; verticals = rows with a ParentVS). Tap a value stream → its verticals and lines; tap a line → its own trends. Tap a KPI heading → trend, Pareto and that letter's Newspaper actions. BOWLER: each day of the reviewed week + WTD + MTD (target / actual / variance) for the current scope, and the same metric by value stream. VARIANCES: raise a 24-hour variance from BIGGEST MISSES, push it to the Newspaper, close it; flip to a month for MOR variances. |

> **Metrics are configurable** in the **KPI_Metrics** list is the metric catalog: each SQDCP letter holds several metrics (Safety: board events, audit hazards, audits completed; Quality: rework, scrap, NCRs (stub); Delivery: attainment, downtime/shift, downtime events; Cost: OEE, speed loss; People: crew vs standard, process confirmation). Turn metrics on/off, order them and set Green/Amber thresholds there; the calculations are built into the app. A letter tile = its worst metric.
> **Value streams are configurable** in the **ValueStreams** list: Title = name (must match Lines → ValueStream), ParentVS = the big value stream for a vertical (blank for top level), DisplayOrder, Active. If the list is empty, Tier 3 falls back to the value streams typed on Lines.
> Tier 3 computes the last 7 days with Tier 2's formulas and saves closed days to **KPI_Daily**, so trends build up from the first day it is opened. Root cause is a placeholder tab for now.

---|---|
| **File** | `T3_Board_v9.pa.yaml` → **Screen1** · `T3_Bowler_v6.pa.yaml` → **scrBowler** · `T3_Variances_v7.pa.yaml` → **scrVariance** |
| **Name / format** | `MDI Tier 3 Board`, **Tablet** 1920 × 1080 |
| **Lists** (20) | the 19 Tier 2 lists (HxH_Shift, HxH_Hourly, QA_Rework, TS_Occurrences, TS_Issues, TS_Fixes, PC_Audits, PC_Results, PC_Cards, SW_Elements, Escalation_Log, Newspaper, Lines, MDI_Config, PLAYBOOK, Lookups, People, SAF_Audits, SAF_Results) **+ KPI_Daily** |
| **Flow** | no |
| **Screen1.OnVisible** | `Select(btnRefresh)` |
| **Share with** | plant manager and staff, OpEx, kiosk account on the meeting TV. Users need **edit** on KPI_Daily (site Members have it). |
| **MDI_Config row** | `App_Tier3` |
| **Check** | Opens on **yesterday**, whole plant: a PLANT row and one row per value stream, SQDCP tiles. Switch **DAY / WEEK TO DATE / MONTH TO DATE**. Tap a value stream for its lines, a line for its own trends; tap a KPI heading for its page: trend vs target, Pareto for the period, and that metric's open Newspaper actions (+ ADD ACTION, Source = Tier 3). Top right shows "N day-rows saved to history"; KPI_Daily gains rows. |

> Tier 3 computes the last 7 days itself with Tier 2's formulas and saves closed days to **KPI_Daily**, so trends build up from the first day it is opened. Weekly and monthly trends read KPI_Daily, so they stay fast as history grows.

### 11. MDI Settings: escalation rules, dropdown lists, lines, standards, thresholds, people (office)
| | |
|---|---|
| **Files** | 6 screens: `Settings_Escalation_v1` → **Screen1** · `Settings_Dropdowns_v1` → **scrDrop** · `Settings_Lines_v1` → **scrLines** · `Settings_Standards_v1` → **scrStd** · `Settings_scrCfg_v2` → **scrCfg** · `Settings_People_v1` → **scrPeople** · `Settings_scrImport_v2` → **scrImport** |
| **Name / format** | `MDI Settings`, **Tablet** 1920 × 1080. Create it from **Solutions → MDI → New → App → Canvas app** so it lands in the MDI solution. |
| **Lists** (8) | Escalation_Contacts, MDI_Config, Lookups, Lines, ValueStreams, PLAYBOOK, KPI_Metrics, People. Turn on Settings → General → *Automatically create environment variables when adding data sources* first; pick the existing variables when offered. |
| **Flow** | **MDI - Import History** (Power Automate pane → Add flow; used by scrImport) |
| **Screens** | Add 6 blank screens named exactly scrDrop, scrLines, scrStd, scrCfg, scrPeople, scrImport. Paste each file onto its screen; paste Screen1 last. |
| **OnVisible** | Screen1 `Select(eLoad)` · scrDrop `Select(dLoad)` · scrLines `Select(lLoad)` · scrStd `Select(sLoad)` · scrCfg `Select(cLoad)` · scrPeople `Select(pLoad)` · scrImport `Select(iLoad)` |
| **Share with** | MDI admins and config editors (everyone else sees it view-only) |
| **Who can edit** | People list: **CanEditConfig** or **MDIAdmin**. Only an MDI admin can grant those. If nobody is MDI admin yet, the app opens in SETUP MODE so the first admin can tick themselves. |
| **Check** | PEOPLE: tick MDI ADMIN on yourself, SAVE. ESCALATION: add a contact at 60 min. DROPDOWN LISTS → Downtime: add a reason, move it up with ▲, and see it in Hour x Hour after REFRESH. |

---

## 3. When something goes wrong

| What you see | Cause | Fix |
|---|---|---|
| Dozens of red ⚠ right after pasting | One or more lists from the card aren't added | Data → + Add data → add the missing ones (names exactly as on the card) |
| ⚠ on `'MDI-UploadPhoto'` | Flow not added to this app | Power Automate pane → + Add flow → MDI - Upload Photo |
| MDI - Upload Photo isn't in the Add flow list | Flow is Off, or not in the MDI solution | Solutions → MDI → Cloud flows → Turn on. Then reopen the pane. |
| Screens cropped, overlapping or tiny | Size set after pasting, or not set | Settings → Display → set the size, then check again. If still wrong, start the app over. |
| The app opens empty | OnVisible not set, or the data was never loaded in the editor | Step 5, then Alt+click REFRESH |
| A delegation warning (yellow triangle) | Expected on a few formulas; they're handled with the 2000 row limit | Ignore, unless the app's **Check** fails |
| A red banner when saving, naming a list | Missing permission on that list, or a changed column | Check the person is Active in People. Otherwise **Call Eric** |
| "Premium" or diamond prompts | Something other than SharePoint was added | Remove it; these apps use SharePoint and the one flow only |

**Don't edit the design by hand.** The design files are generated on Eric's side, and the next version replaces any hand edits. Send layout or wording changes to Eric instead. Numbers like color thresholds live in **MDI_Config** and are safe to change.
