# Holmdel Tier 2: troubleshooting

**Holmdel is not New Albany.** Nothing at Holmdel uses SharePoint lists, the MDI solution, MDI_Config, environment variables for lists, or the Hour x Hour app. Don't apply New Albany fixes here. Holmdel is:

| Piece | What it is |
|---|---|
| **Tier 1 Excel boards** | `https://veepak1.sharepoint.com/holmdel` → Documents → `Production/<group>/<Line N>/<n>. Production Board <Month>.xlsm`. One workbook per line per month, one tab per day, two shifts per tab. **They are the only record.** Operators type here; the board's own `SendWorkbook` macro saves and emails the handover. |
| **MDI XB - Sync Excel Boards** | Scheduled flow, every 30 min (Eastern), one run at a time. Lists the board folders, picks boards saved since the last run plus boards that failed last time, **copies** each into `Production/_Tier2/board copies <run>/`, runs the Office Script `ReadProductionBoard_<hash>.osts` on the copy, merges the results into `Production/_Tier2/tier2_data.json`. Runs on the importer's connections (today Christina's). |
| **MDI XB - Tier 2 Data** | Called by the app on REFRESH. Returns `tier2_data.json` + `tier2_settings.json`; saves target colors back to `tier2_settings.json`. Same connections. |
| **MDI Tier 2 - Holmdel** | The canvas app (the TV board and laptops). |
| Solution | **MDI Tier 2 - Excel boards (no lists)** (`MDITier2ExcelBoardsLite`), managed, 1.0.0.19, in **Vee Pak, LLC (default)**. Settings: site, board folder, shift 1/2 times, lunch, break. |

`tier2_data.json` is plain text you can open in the browser. It holds `lastRun` (when the sync last saved), `boardsRead`, `failed` (boards that couldn't be read and will be retried), `warnings` (per-board notes: wrong-month tabs, D2 vs folder mismatches, read errors), `lines`, `reasons` and the last 40 days of `rows`. **The app does not show the warnings** (that panel was removed on request), so this file and the flow's run history are where problems show up.

---

## First, which of these is it?

| Symptom | Go to |
|---|---|
| App says **"…does not have ReadAccess right(s) for record … of entity Process"** | §1 |
| **"No lines to show"** and zeros everywhere | §1 if that error appears; otherwise §3 |
| One line blank or behind, others fine | §2 |
| Every line stopped updating at some time | §3 |
| A number on Tier 2 doesn't match the board | §4 |
| Flow fails (red in run history) | §5 |
| Anything after an upgrade/reinstall | §6 |

---

## 1. Permission errors in the app

### "…does not have ReadAccess right(s) for record with id b2321e1e-… of entity Process"
**Seen:** Oct 29 (Christian Algarin), Nov 16 (new TV account "HM").
**Cause:** the app runs **MDI XB - Tier 2 Data** as the signed-in user. Sharing the app doesn't share the flow. `Process` = the flow record; `b2321e1e-d0f5-5596-9d3a-65dcc95a8161` = Tier 2 Data. Owning the SharePoint files doesn't help: it isn't SharePoint.
**Fix (flow owner):**
1. Power Automate → **Solutions** → **MDI Tier 2 - Excel boards (no lists)** → **Cloud flows** → **MDI XB - Tier 2 Data** → its **details page** (not the editor). **Seen Nov 18:** Tier 2 Data didn't appear in Christina's My flows at all (only Sync Excel Boards did), and from My flows the Run only users card loaded and then vanished. Through Solutions the card stayed. Direct link: `https://make.powerautomate.com/environments/Default-674a846e-c4b8-4ad5-93be-705ef8d7c576/flows/b2321e1e-d0f5-5596-9d3a-65dcc95a8161/details`. **Check the page title says Tier 2 Data**; adding people to Sync Excel Boards does nothing for viewers.
2. **Run only users → Edit** → add the user, the TV account, or better a group of all viewers.
3. **Connections used:** SharePoint and Excel Online = **Use this connection** (the owner's). Then viewers need no access to the boards at all.
4. Save the panel. On the device: close the browser/app completely, reopen, REFRESH.
**If it still fails for a brand-new account** (typical for TV/kiosk accounts created the same day): the account probably has **no security role** in the Vee Pak environment. An admin: Power Platform admin center → Vee Pak, LLC (default) → Users → the account → **Basic User** (or a team with it).
**Traps:**
- Only **Tier 2 Data** needs run-only users. **Sync Excel Boards** is scheduled and runs on the owner's connections; it has no Run only users box. Sharing it does nothing for viewers.
- **Co-owner** also clears the error but lets the person edit and delete the flow. Viewers = run-only.
- People who "already work" got access earlier (as of Nov 18 the run-only list was only Rene and Christian, while the app was shared with 10). Every account the app is shared with needs the same step; compare the app's **Share** list with this card.
- Sharing the app and adding run-only are two separate steps. Do both for every new viewer, or add one M365 group to both once.

### App opens but REFRESH says it can't reach the flow
App → Edit → Power Automate pane → remove **MDI XB - Tier 2 Data** → Add flow → it again → Save → Publish. Only possible in an unmanaged copy (see README "Changing it"); in production, reimport the package instead.

---

## 2. One line is blank, behind, or wrong
Check in this order:
1. **Is the board saved?** Desktop Excel with AutoSave off holds entries on that PC; SharePoint (and the browser, the sync, Tier 2) only has the last save. Look for the person's initials on the file; have them **Ctrl+S** or press the board's Send button. **Seen Oct 29:** Christian's board looked blank to Christina until he closed it. Prevention: AutoSave on for every line PC, or save at the end of every hour.
2. **Is it the SharePoint file?** If the floor PC opened a *downloaded* or *local* copy, nothing reaches SharePoint. The board must be opened from the SharePoint folder (or a OneDrive-synced copy of it).
3. **Right folder and name?** The sync only reads files named `…Production Board…` (.xlsm or .xlsx) inside a folder whose name starts with `Line` + a digit, under a group folder in `Production`. A board dropped directly in a group folder, or renamed, is invisible.
4. **Right tab?** The month comes from the **file name** (`10.` or `October`), the day from the **tab name**. The C2 date cell is ignored (it was often stale and caused duplicate days). A tab named for the wrong month (a "June 30" in a July board) is read as the file's month, with a warning.
5. **Line number:** comes from the **line folder**, not cell D2 (`Line 00` → 0, `Line18` → 18, `Line 7a` stays `7a`). If D2 disagrees, there's a warning; the folder wins.
6. **Did it fail to read?** Open `Production/_Tier2/tier2_data.json`: is the board in `failed`? Its `warnings` entry says which step failed. Failed boards are retried every run.
7. **Older than 40 days?** Tier 2 keeps 40 days.

## 3. Everything stopped updating
1. **Run history:** Power Automate → **MDI XB - Sync Excel Boards** → 28-day run history.
   - **No runs since a time** → the flow is **Off** (an import, or Power Automate turned it off after repeated failures). Turn it on, press **Run**.
   - **Runs failing** → §5.
   - **Runs succeeding but nothing new** → nobody saved a board to SharePoint (§2, items 1–2). **Seen Nov 16:** board "stopped" at 6:55 am; check this first.
2. **Connections:** the flows run on the importer's connections. If that person's password changed, their account was disabled, or the connection expired, every run fails. Solutions → the Holmdel solution → **Connection references** → re-select a working connection. **Before anyone leaves, move the connections to another owner or a service account.**
3. **"Trigger concurrency throttling detected"** (yellow) is expected: a run took longer than 30 minutes, so the next one waited. Leave it. **But** only one sync runs at a time, so a single run that hangs (for hours, "Running" at the top of the history) holds back every run after it and Tier 2 freezes at that time. Open it; if it's stuck on one step, **Cancel** it, and the next run proceeds. During a Microsoft 365 service incident, check the Microsoft 365 Service health page before chasing anything else.
4. `tier2_data.json` → `lastRun` shows when the sync last **saved**. It only saves when a board actually changed, so a quiet weekend leaves it alone.

## 4. A number doesn't match the board
Tier 2 shows what the board calculates; it doesn't fix the template.
- **OEE** is the board's own **OEE Actual %** (H18 shift 1, H47 shift 2). The template calculates the two shifts differently (H18 uses hours run × 56.25 at actual speed; H47 uses a fixed 450 minutes). Blank when the board has no Act. Speed.
- **Downtime** = all reason rows (A17:B27 / A46:B56), as the board totals them. **Scrap** = C17:D27 / C46:D56. **Safety** = E18:F20 / E47:F49. **Crew** = D4 (act) vs B4 (std). **Delivery** = hourly units B6:B13 / B35:B42 vs target F4 / F33.
- **Reasons and components** are whatever the board's rows say; nothing is typed in elsewhere. Free-text variations on the board show as separate reasons.
- **Colors** come from ⚙ TARGETS in the app (saved to `tier2_settings.json`, shared by every screen).
- Other known template defects (from the July teardown): 2nd-shift hourly efficiency on the board used the shift-1 target (F$4), "Units Missed" sign reversed, MTD totals summing empty cells. Tier 2 reads the raw cells, so it isn't affected by the MTD issues, but leads comparing against those board cells will see differences.
- Offline check: `holmdel/generator/test` runs the script on any board file and prints what Tier 2 would read (see README).

## 5. Sync flow errors (what each failing step means)
Open the failed run → scroll to **For each board** → **Next failed >** → expand **Try board** → the red step. (The run view draws the loop below where the parallel branches join; zoom the browser out with Ctrl −.) Or read the board's `warnings` in `tier2_data.json`.

| Red step / message | Meaning | Fix |
|---|---|---|
| **Run script**: "couldn't create a connection with Excel" / Forbidden | Excel only runs scripts on files the account can **edit**. That's why the flow copies boards first. If it happens on the copy: Office Scripts disabled for Power Automate in the tenant (M365 admin → Org settings → Office Scripts), or a sensitivity label/encryption on the files. | Admin setting / ask IT to leave the Production folder unlabeled |
| **Copy board** / **Get board item**: 403 | The connection's account can't **download** the boards. **Seen during the build:** Christina had view-only (no download). | IT grants **Read** (with download) on Documents/Production, and Contribute on `Production/_Tier2` |
| **Folder_failed** in the app / **Get tree** red | The board-folder setting is wrong. `Production`, `/Production/` and `Shared Documents/Production` all work; anything else doesn't. | Fix the solution setting (Solutions → the solution → environment variables), then Run |
| **Get_data** "not found" on the very first run | Early versions only: no data file existed yet. Current versions check first. | None |
| **Delete old** copies red | A previous copy folder was still locked by Excel. Tolerated; retried next run. | None |
| **Save data** red | Reading worked, writing `tier2_data.json` failed (permissions on `_Tier2`, or the file is checked out). | Contribute on `_Tier2`; make sure nobody has the file checked out |
| Office Scripts quota | 1,600 script runs per user per day. About 24 active boards × 48 runs fits. | Fewer runs or fewer boards per run |

## 6. After an upgrade or reinstall
- Open the solution: **both flows On** (upgrades can leave a flow off).
- Run **Sync Excel Boards** once (15–30 s per board), then REFRESH the app.
- Check viewers still have run-only on **Tier 2 Data** (§1).
- **Never save edits to the managed flows or app in production.** Opening a managed flow shows "Editing this managed flow will create customizations stored in a new unmanaged layer"; saving there blocks future upgrades. Back out with ← and discard.
- The six settings at import: site `https://veepak1.sharepoint.com/holmdel`, folder `Production`, shifts `07:00-15:15` / `15:15-23:30`, lunch `30`, break `15`. If they appear greyed, they're hints: type them in.

## 7. Things that are fine
- `board copies <run>` folders in `_Tier2`: one per run, the previous one deleted at the start of the next run.
- New `ReadProductionBoard_<hash>.osts` files: a new script version gets a new name; old ones are never overwritten.
- The boards' macros never run from the flow; copies keep them intact.
