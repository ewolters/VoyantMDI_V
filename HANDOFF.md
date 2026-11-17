# Handoff: rebuilding the MDI from scratch

From Eric Wolters to Kenny, November 2026. This is the "if it's gone, here's how to bring it back" document. For day-to-day changes see [START_HERE.md](START_HERE.md); for errors see [TROUBLESHOOTING.md](TROUBLESHOOTING.md); for how each piece works see [SYSTEM_REFERENCE.md](SYSTEM_REFERENCE.md).

---

## 1. What you're taking over

| Thing | Where it lives | Rebuild from |
|---|---|---|
| **Data** (about 33 lists) | SharePoint: `https://veepak1.sharepoint.com/sites/OhioContinuousImprovement` | Lists: the **MDI - Set Up Site** flow (§3C). **The data itself only exists in SharePoint: back it up (§5).** |
| **Apps + flows** (managed solution **MDI** 1.1.4.1) | Power Platform environment **Vee Pak, LLC (default)** | A managed export from **MDI Dev** (§3A) |
| **Your editable copy** (unmanaged **MDI**) | Environment **MDI Dev** (you create it; START_HERE Part 1.5) | `solution/MDI_OhioContinuousImprovement_UNMANAGED_v1.1.4.1.zip` (§3B) |
| **Setup flow** (solution **MDI Setup**) | Vee Pak default environment | `solution/MDISetup_UNMANAGED_v1.0.0.0.zip` |
| **Source code** for every screen and flow | This repo | It *is* the backup. Keep your copy pushed to GitHub. |
| **Holmdel Tier 2** (solution **MDI Tier 2 - Excel boards (no lists)** 1.0.0.19) | Vee Pak default environment, owned by Christina DeRamos; data = the Tier 1 Excel boards in `https://veepak1.sharepoint.com/holmdel` | `holmdel/package/…1.0.0.19_managed.zip` (§4) |

**Accounts that matter:** every flow runs on the connections of whoever set it up (Kenny at New Albany, Christina at Holmdel). If that person's account is disabled, the flows stop. Do §6 before anyone else leaves.

---

## 2. Which scenario are you in?

| What happened | Go to |
|---|---|
| Apps or flows are broken or missing in production, SharePoint data is fine | **§3A** |
| MDI Dev was deleted or messed up | **§3B** |
| The SharePoint site or lists are gone / you need a new site | **§3C** |
| A new plant wants the MDI | **§3D** |
| Holmdel needs reinstalling | **§4** |
| Packages won't import at all (tenant policy, licensing) | **§3E**: hand-build fallback |

---

## 3. New Albany

### 3A. Reinstall apps + flows into production (site is fine)
*About 30 minutes.*
1. In **MDI Dev**: Solutions → MDI → make sure every app is **Published** → ⋯ → **Settings**: version higher than production's → **Export solution → Managed** → download.
   *(No MDI Dev? Do §3B first.)*
2. In **Vee Pak, LLC (default)**: Solutions → **Import solution** → the managed zip → Next → connections: SharePoint, Office 365 Outlook, Teams, Dataverse, Excel Online (Business) → **Import**.
   - If MDI is still installed, it's an **Upgrade** (the default). If you deleted it, it's a fresh install. Same steps.
3. Solutions → MDI → **Cloud flows**: turn **On** HxH - Downtime Escalation, MDI - Upload Photo, MDI - Sync Permissions, MDI - Nightly Board Check, MDI - Import History. Leave Frontier Critical Alert off unless Frontier is used; leave Connect Site off.
4. **Share** each app (Apps → ⋯ → Share) with its users and the TV/kiosk accounts. For every app that calls a flow, give its users **run-only** access on that flow (**MDI - Upload Photo**: Quality, TS Maintenance, Newspaper, SW Manager, PC Audit, Frontier Audit; **MDI - Import History**: MDI Settings), with connections set to yours (TROUBLESHOOTING §2.1).
5. Open MDI Settings → PEOPLE → tick yourself **MDI ADMIN** → Save.
6. Re-pin the TV links: each app's link (Apps → ⋯ → Details → Web link) with `&hidenavbar=true` on the end for kiosk TVs.

### 3B. Rebuild MDI Dev
*About 20 minutes.* Follow START_HERE Part 1.5: create a Developer (or Sandbox) environment named **MDI Dev**, import `solution/MDI_OhioContinuousImprovement_UNMANAGED_v1.1.4.1.zip`, sign in to its five connections, open and **Publish** each app.

If you've shipped changes since 1.1.4.1, that zip is out of date. Rebuild from it, then re-apply your later screens from `deploy/apps/` (they're the current versions, and `py generator/make.py check` proves the repo matches them). Better: after every release, **export MDI Dev unmanaged** too and commit it to `solution/` so this zip is always current.

### 3C. New or rebuilt SharePoint site
*About 1 hour plus data entry.* The lists are created by a flow; the apps and flows are then repointed at the new lists.
1. **Create the site** (SharePoint → + Create site → Team site). Add members: everyone who enters data, plus the kiosk/TV accounts.
2. **Import MDI Setup** into the environment where you'll run it (production or MDI Dev): Solutions → Import → `solution/MDISetup_UNMANAGED_v1.0.0.0.zip`. Connections: SharePoint + Outlook. Turn the flow **MDI - Set Up Site** on.
3. **Run it:** open **MDI - Set Up Site** → **Run** → paste the new site's address (`https://veepak1.sharepoint.com/sites/<name>`). Run it as a **site owner**. It creates every list, column, view and permission, seeds Lines, Lookups, MDI_Config, Escalation_Contacts and PLAYBOOK, then **emails you an `MDI2:…` setup code** (also saved in the new site's MDI_Config list, row Setup_Code). It's safe to run again; it only adds what's missing.
   - Save the code privately (not in this public repo): it's the site address plus every list's ID.
4. **Repoint MDI Dev at the new site.** The apps and flows find the site and lists through **32 environment variables**. In MDI Dev, either:
   - **Fast:** turn on **MDI - Connect Site** in MDI Dev, Run it, paste the `MDI2:` code. It sets all 32 variables and restarts the flows. (It uses the Dataverse connector, which is Premium. A Developer environment should allow Premium connectors for its owner, which is why to run it in MDI Dev and not production. If it says it needs a license, use the by-hand route.)
   - **By hand:** Solutions → MDI → each environment variable → **Current value** → pick the new site, then the list with the same name. Ask Claude to decode the `MDI2:` code into a table of list names and IDs to make this quick.
5. In MDI Dev, open each app, check it loads data from the new site (Hour x Hour: pick a line; Tier 2: REFRESH), **Publish**.
6. Bump the version, export **Managed**, import into production (§3A steps 2–6).
7. **Fill in the plant data** (or import it): Lines (value streams), People (names, emails, roles; tick MDI ADMIN for yourself), Escalation_Contacts, PLAYBOOK (rates, crew), Lookups (reasons). Old Hour x Hour history: MDI Settings → THRESHOLDS & LINKS → **IMPORT HISTORY** reads the line data-entry workbooks (TROUBLESHOOTING §3).

**If the old site's data still exists** (e.g. site renamed or moved), don't rebuild: just repoint the variables (step 4) at it.

### 3D. A new plant
Same as §3C with its own site, plus its own production environment if the plant uses a different one. Shared viewer/TV accounts, Lines, PLAYBOOK and People are plant-specific. Keep one MDI Dev per plant (or repoint yours each time before exporting, and note which site the export points at in the zip's file name).

### 3E. Hand-build fallback (no package imports)
If solution imports are blocked, `deploy/README.md` is the original install: lists by browser-console script (`deploy/provision_mdi.js.txt`), flows by console script (`deploy/tools/install_flows.js.txt`), apps pasted from `deploy/apps/` using `deploy/apps/APP_BUILD_GUIDE.md` (one card per app: lists, flows, start-up formula, who to share with). Half a day. Note the app cards assume the lists are added directly; the packaged apps use environment variables instead. Either works.

---

## 4. Holmdel (Tier 2 only, reads the Excel boards)

Full notes: [holmdel/README.md](holmdel/README.md). Reinstall in about 30 minutes:
1. make.powerapps.com → environment **Vee Pak, LLC (default)** → Solutions → Import → `holmdel/package/MDI_Tier2_ExcelBoards_NoLists_1.0.0.19_managed.zip`.
2. Connections: **SharePoint** and **Excel Online (Business)**, signed in as the board owner (today Christina). That account needs **Read with download** on Documents/Production and edit rights on `Production/_Tier2` (TROUBLESHOOTING §2.2).
3. Settings it asks for: site `https://veepak1.sharepoint.com/holmdel` · board folder `Production` · shift 1 `07:00-15:15` · shift 2 `15:15-23:30` · lunch `30` · break `15`. If they show greyed out, type each one in.
4. Solutions → the solution → check **both flows On**.
5. Run **MDI XB - Sync Excel Boards** once (15–30 s per board), then it runs every 30 min.
6. Share the app **MDI Tier 2 - Holmdel** with viewers and the TV account, **and** add them as **run-only users** on **MDI XB - Tier 2 Data** with connections set to the owner's (TROUBLESHOOTING §2.1). Skipping this is the "ReadAccess … entity Process" error.

Nothing at Holmdel lives outside the Excel boards and two small files the sync writes (`Production/_Tier2/tier2_data.json`, `tier2_settings.json`). Losing those is harmless: the next sync rebuilds them (target colors reset to defaults).

---

## 5. Backups to set up now
- **SharePoint data.** Version history and the 93-day recycle bin cover accidents, not a deleted site. Monthly, export the big lists (HxH_Hourly, HxH_Shift, Newspaper, QA_Rework, NCR, PC_Audits/PC_Results, TS_*, KPI_Daily, PLAYBOOK, People, Lines, Lookups, MDI_Config) to Excel (list → Export → CSV) into a folder IT backs up. Ask IT whether the tenant has Microsoft 365 Backup or a retention policy on the site.
- **Solution.** After every release, export MDI from MDI Dev **both managed and unmanaged**, and commit them to `solution/`.
- **History older than 6 months.** Tier 2 only reads 6 months back. If Voyant runs the archive script it planned, keep its output with the backups.
- **This repo.** Push after every change. GitHub is the off-site copy of all the source.

## 6. Before anyone leaves (do now)
1. **Every flow gets a second owner.** Power Automate → each flow → **Owners → Edit** → add a second person (or a service account). For New Albany that's 7 flows + Set Up Site; for Holmdel, the two MDI XB flows.
2. **Connections on a service account**, if IT will give you one. Flows that run on a person's connections stop when that account is disabled.
3. **Power Platform environment admin:** make sure at least two people at Voyant can open the environments (MDI Dev and production) and import solutions.
4. **SharePoint site owners:** at least two.
5. **GitHub:** at least two people with access to the repo.
6. **Kiosk/TV accounts:** record in a password manager (not this repo) which account each TV uses.

## 7. Facts worth keeping

| | |
|---|---|
| Solution unique names | `MDI`, `MDISetup`; Holmdel: `MDI Tier 2 - Excel boards (no lists)` |
| Publisher | `Cr21560`, prefix `craf4` (same in every environment, so upgrades line up) |
| Environment variables | 32: `MDI SharePoint site` + one per list, named after the list |
| Connection references | `craf4_sharedsharepointonline_17d15`, `craf4_sharedoffice365_mdi`, `craf4_sharedteams_a7259`, `craf4_shareddataverse_mdi`, `craf4_sharedexcelonlinebusiness_mdi` |
| Licenses | Standard Microsoft 365 only in production. Premium is needed only for Connect Site (use it in MDI Dev). |
| Version at handoff | MDI 1.1.4.1 · MDI Setup 1.0.0.0 · Holmdel 1.0.0.19 |
