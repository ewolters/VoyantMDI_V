# Virtual MDI: owner's troubleshooting guide

> **Holmdel is a different system** (Excel boards → flow → JSON file → app; no lists). For Holmdel problems use **[holmdel/TROUBLESHOOTING.md](../holmdel/TROUBLESHOOTING.md)** first. This guide is New Albany, plus the Power Platform permission basics both plants share (§2.1).

For Kenny (and his Claude) as the owner of the New Albany MDI and the Holmdel Tier 2 board. Written from what actually broke during the build and both installs. Read **Section 0** first; most problems trace back to it.

---

## 0. How the system is put together (read this first)

**New Albany (full MDI)**
- **Data:** about 33 SharePoint lists on `https://veepak1.sharepoint.com/sites/OhioContinuousImprovement` (HxH_Hourly, HxH_Shift, Lines, PLAYBOOK, Lookups, MDI_Config, Newspaper, …).
- **Apps and flows:** one **managed** solution named **MDI** (publisher `Cr21560`, prefix `craf4`) in the Vee Pak, LLC (default) environment. 10 canvas apps, 7 flows, 32 environment variables (1 site + 31 lists), 5 connection references (SharePoint, Office 365 Outlook, Teams, Dataverse, Excel Online (Business)).
- **Setup:** a second solution, **MDI Setup**, holds the flow **MDI - Set Up Site** that creates/repairs the lists and emails an `MDI2:` setup code.

**Holmdel (Tier 2 only, no lists)**
- **Data:** the Tier 1 Excel boards under `https://veepak1.sharepoint.com/holmdel` → Documents/Production/<group>/<Line N>/. No lists.
- **Apps and flows:** managed solution **MDI Tier 2 - Excel boards (no lists)**: the app **MDI Tier 2 - Holmdel**, flow **MDI XB - Sync Excel Boards** (every 30 min, reads changed boards with an Office Script into `Production/_Tier2/tier2_data.json`), and flow **MDI XB - Tier 2 Data** (the app calls it on Refresh).
- **Owner today:** Christina DeRamos (flows run on her connections).

**Rules that explain most failures**
1. **Managed = read-only.** You can't edit a managed app or flow in place. Opening a managed flow in the designer warns "Editing this managed flow will create customizations stored in a new unmanaged layer." **Never save there.** That layer blocks every future upgrade. Back out with ← and discard.
2. **Apps ship their published version.** A saved-but-unpublished app goes out (and comes back) as its old version.
3. **Sharing an app does not share its flows.** Every viewer of an app that calls a flow needs run-only access to that flow (see §2.1).
4. **Upgrades and generic imports can leave flows Off.** After every import, open the solution and check every flow says **On**.
5. **Everything points at a SharePoint site through environment variables.** If a variable points at the wrong site, the flow fails with "Unauthorized" or "Not found", not a clear message.

---

## 1. Changing anything: you need your own golden copy

> "I can't create a managed solution from the GitHub repo." Correct. The repo holds the **source** (`.pa.yaml` screens, flow JSON, generators), not a solution. A managed zip can only be **exported from an environment that holds the solution unmanaged.** Until now that environment was Eric's sandbox, in his tenant. Kenny needs his own.

**One-time setup (about 30 minutes):**
1. **Create a development environment** in the Vee Pak tenant: make.powerapps.com → ⚙ → Admin center → Environments → **New** → type **Developer** (free for the developer; includes Dataverse and Premium connectors for that one person). Name it `MDI Dev`. If Developer isn't allowed by the tenant, ask IT for a **Sandbox** environment.
2. **Import the unmanaged golden copy** into `MDI Dev`: Solutions → Import → the newest `MDI_OhioContinuousImprovement_UNMANAGED_v*.zip` in `newalbany/solution/` (1.1.4.2 as of Nov 18, 2026; already pointed at the Ohio site and lists). Untick *Enable plug-in steps and flows* under Advanced settings if offered, then check every flow is **Off** after import (MDI Dev points at the real Ohio lists). Create/pick the connections it asks for. Do **not** import it into the default (production) environment: the managed MDI is there and the two collide.
3. Optional: also import `MDISetup_UNMANAGED_v1.0.0.0.zip` there, so the setup flow can be edited too.
4. In `MDI Dev`, open each app once and **Publish** it.

**Shipping a change from then on:**
1. Make the change in `MDI Dev` (Studio for apps; the flow designer for flows; it's unmanaged there, so saving is fine).
2. **Publish** every app you touched.
3. Solutions → MDI → ⋯ → **Settings** → raise the version (e.g. 1.1.4.2 → 1.1.4.3).
4. Solutions → MDI → **Export** → **Managed** → download.
5. In the production (default) environment: Solutions → Import → that zip → **Upgrade** (the default). Check every flow is **On** afterwards.

**Testing note:** `MDI Dev` points at the real Ohio lists, so anything you test there writes real data. For risky changes, run **MDI - Set Up Site** on a scratch SharePoint site and repoint the 32 environment variables in `MDI Dev` to it first.

**Changing an app from repo source instead of Studio:** create a blank screen in Studio, select it, and paste the `.pa.yaml` from `newalbany/deploy/apps/` (Ctrl+V on the screen). `newalbany/deploy/apps/APP_BUILD_GUIDE.md` says which file goes where.

---

## 2. Permission errors

### 2.1 `…does not have ReadAccess right(s) for record with id … of entity Process` (app shows zeros / "No lines")
**Seen at:** Holmdel (Christian; the TV account "HM").
**Meaning:** the app tried to run a flow and Dataverse refused. `Process` = the flow record. The signed-in user isn't allowed to run that flow. It has nothing to do with SharePoint; owning every SharePoint file doesn't help.
**Fix (flow owner, once per flow):**
1. Power Automate → **My flows** (or **Solutions → [solution] → the flow**) → open the flow's **details page**, not the editor.
2. **Run only users → Edit** → add the viewer, or better a **security/M365 group** of all board viewers (new people then just join the group).
3. **Connections used:** set SharePoint (and Excel Online if listed) to **Use this connection ([owner])**, not "Provided by run-only user". Then viewers need no SharePoint access of their own.
4. Save the panel. The viewer closes and reopens the app and presses Refresh.

**Traps:**
- **Right flow.** Only flows the app calls have a Run only users box. At Holmdel that's **MDI XB - Tier 2 Data**, not Sync Excel Boards (scheduled, runs as its owner). At New Albany: MDI - Upload Photo, MDI - Import History, MDI - Connect Site.
- **Can't find the box?** Power Automate → My flows → **Shared with me** → ⋯ next to the flow → **Manage run-only permissions**.
- **Co-owner is not the fix.** It clears the error but co-owners can edit and delete the flow. Viewers get run-only.
- **Alternative for many accounts:** Power Platform admin center → environment → Users → give the account (or a team) a security role with **Process read at Business Unit level**.

### 2.2 `403` / "Access denied" when a flow reads Excel boards
**Seen at:** Holmdel. The account had **view-only (no download)** rights on the Production library.
**Fix:** IT grants the flow owner at least **Read** (download allowed) on the board library. Office Scripts only run on files the account can edit; the Holmdel sync copies each board to `Production/_Tier2/board copies…` first for exactly that reason, so the owner needs **Contribute** on `_Tier2`.

### 2.3 Flow fails with `GetTable … Unauthorized` (or 401/404 on a list)
**Seen at:** Kenny's first New Albany import.
**Meaning:** the flow is pointing at the wrong site or list. A generic package was imported before the environment variables pointed at the customer site.
**Fix:** Solutions → MDI → Environment variables → check **MDI SharePoint site** is the Ohio site and the list variables are set. Build customer packages with `newalbany/deploy/package/build_package.js` (site + list IDs rewritten from the setup code), or, from now on, export from `MDI Dev` (§1). Then turn the flows Off and On.

### 2.4 "Turn on failed. A connector was imported, however the related connection references need connections created…"
**Fix:** Solutions → [solution] → **Connection references** (Objects list; use **All** + filter Type = Connection reference if it isn't listed) → open the reference (e.g. **MDI Excel Online (Business)**) → pick or create a connection → **Save**. Then turn the flow on.

### 2.5 "This flow requires a Premium license" / Dataverse connector blocked
**Seen at:** MDI - Connect Site (uses Dataverse) and Holmdel's first design.
**Meaning:** the Vee Pak production environment has no Power Automate Premium. Anything using Dataverse, SQL, or HTTP connectors won't run for normal users there.
**Fix:** don't use Connect Site in production; use rewired packages / the `MDI Dev` route (§1). A Developer environment has Premium for its owner, so Dataverse works there for building, not for plant users.

### 2.6 Power Query (Excel rollups): "Couldn't authenticate with the credentials provided"
**Seen at:** the Holmdel/Ohio Excel rollups.
**Test first:** blank query → `= SharePoint.Files("https://veepak1.sharepoint.com/holmdel", [ApiVersion = 15])`.
- Table of files → auth is fine, the problem is elsewhere.
- "Couldn't authenticate" → Data → Get Data → **Data Source Settings** → delete every `veepak1` entry under **both** "Data sources in current workbook" **and** "Global permissions" → close Excel completely → sign in with **Organizational account**.
- "Access to the resource is forbidden" → a permissions grant from IT, not Power Query.
- Empty table → wrong address.

---

## 3. "The board shows nothing / old data"

| Symptom | Check, in order |
|---|---|
| Holmdel Tier 2 blank for a line | (1) Is the board **saved**? Desktop Excel with AutoSave off holds entries locally; the browser, the sync and Tier 2 read only the saved file. Look for the user's initials in the file; have them Ctrl+S or press Send. (2) Right tab/day? (3) Was the board read? Open **MDI XB - Sync Excel Boards → run history**; a board that failed is retried every run and listed in its output. |
| Holmdel sync skipped runs ("Trigger concurrency throttling detected") | Expected: a run took longer than 30 min, so the next one waited. Leave Concurrency Control on. |
| Holmdel: "can't reach the flow" on Refresh | App in Studio → Power Automate pane → remove **MDI XB - Tier 2 Data** → Add flow → it again → Save → Publish. Also check §2.1. |
| New Albany app shows old screens after an upgrade | The exporting environment had saved-but-unpublished changes. Publish in `MDI Dev`, bump version, export, re-import. |
| New Albany Hour x Hour: "PICK THE PRODUCT RUNNING NOW" | By design (v22): a new shift must pick a product, then enter ACTUAL CREW, before hours unlock. |
| Tier 2 WEEKS & MONTHS slow | It loads a week at a time; 26 weeks is a lot. Try 13. Nothing older than 6 months is loaded. |
| Import History: "Could not read …" | The workbook must have tables **Tbl_Shift, Tbl_Production, Tbl_Downtime** and must not be open for editing. Check **MDI - Import History** is On and its Excel connection reference is set (§2.4). |
| Import History: "FINISHED: n row(s) did not save" | The message names the first failing row and the reason. Re-running is safe: saved rows are skipped. |
| Studio: "No lines" on a fresh install | Run **MDI - Set Up Site** (New Albany) or **MDI XB - Sync Excel Boards** (Holmdel) once. |

---

## 4. Power Fx / Studio traps (for edits in `MDI Dev`)

- **`Set()` can't be used inside `ForAll()`.** Collect into a collection instead and count it afterwards.
- **`IfError` types must agree.** Use the 3-argument form when the value and the fallback return different types: `IfError(Patch(...), Notify(...), true)`.
- **Classic ComboBoxes pasted from YAML render blank rows.** Use a text box filter (`FIND`) plus a dropdown.
- **Dropdown in a gallery with a blank Default shows another row's pick.** Give the Items a placeholder `" "` row, Default `Coalesce(Reason, " ")`, and `Trim` on save.
- **Wrap-count galleries cap columns.** For wide grids use fixed column slots (see Tier 2 WEEKS & MONTHS).
- **2,000-row limit.** Filters on SharePoint lists return at most the app's data row limit; load big lists in date chunks (`ForAll(Sequence(...), Collect(...))`).
- **Gallery rows pasted from YAML don't open when tapped.** Labels and rectangles inside a gallery only pass a tap to the gallery's OnSelect if their own OnSelect is `Select(Parent)`; Studio adds that when you insert them by hand, a YAML paste doesn't. Give them `OnSelect: =Select(Parent)` (MDI Settings v3 does this in `gal()`), or put a transparent tap button over the row (Tier 2 does). Symptom: "I can only add new, not edit" (MDI Settings v1/v2, fixed in v3).
- **Paste order matters.** A control that navigates to a screen errors until that screen exists; create the screen first.
- **Flows called from apps:** after changing a flow's inputs/outputs, remove and re-add it in the app's Power Automate pane, then Publish.
- **Voyant mail filters** block `.py` attachments and rewrite `https://` inside `.txt` scripts. Send zips without Python; in text scripts write `https:\/\/`.

---

## 5. Who/what owns what (fill in)

| Thing | Owner | Backup |
|---|---|---|
| MDI solution + flows (New Albany) | Kenny | |
| MDI Dev environment | Kenny | |
| Holmdel solution + flows | Christina DeRamos | |
| Board viewer group (Holmdel) | | |
| Board viewer group (New Albany) | | |
| TV / kiosk accounts | | |

**Before anyone leaves:** add a co-owner on every flow (Power Automate → flow → Owners → Edit), and move connections to a service account if IT has one. Flows that run on a departed person's connections stop when their account is disabled.

---

## 6. Prompt for Kenny's Claude

> You are maintaining a Microsoft 365 virtual MDI (Power Apps canvas apps + Power Automate + SharePoint lists) packaged as the managed solution "MDI" (publisher Cr21560, prefix craf4) in the Vee Pak tenant. Source is in github.com/ewolters/VoyantMDI_V: `newalbany/deploy/apps/*.pa.yaml` (screens to paste in Studio), `newalbany/deploy/flows/json` (flow definitions), `newalbany/generator/` (Python that writes the YAML/JSON; `newalbany/generator/lint/` checks it), `newalbany/log.md` (history), `newalbany/TROUBLESHOOTING.md` (this guide). Changes are made in the unmanaged copy in the "MDI Dev" environment, published, version-bumped, exported as managed, and imported as an upgrade into production. Never tell the user to save edits on a managed flow or app in production. Ask for the exact error text and which app/flow/screen before proposing a fix; check Section 2 of newalbany/TROUBLESHOOTING.md for permission errors first.
