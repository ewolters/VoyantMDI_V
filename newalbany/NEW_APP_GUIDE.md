# New list + new app (New Albany)

How to add a SharePoint list and a new canvas app to the MDI so they install, upgrade, permission and move to a new site exactly like the existing ten apps. Part 1 explains how the install machinery works; Part 2 is the step-by-step; Part 3 is what goes wrong.

**For Claude:** use the `/new-app` skill, which follows Part 2. Do all the file work (Steps 1–3 and 9) yourself. Kenny does the browser steps (4–8), one at a time.

**Holmdel has no lists.** None of this applies there.

---

## Part 1. How the install works

```
newalbany/deploy/mdi_package.json        every list: columns, title, default view, indexes, seed rows, permissions
        │  newalbany/generator/flows/gen_setup_flow.py   (make.py target: flow-setup)
        ▼
flow "MDI - Set Up Site"                  the whole package is embedded in the flow
  in solution MDI Setup                   newalbany/generator/setup_package.py rebuilds the zip
        │  Run it, paste a site address (as a site OWNER)
        ▼
SharePoint site                           creates missing lists and columns, sets views, indexes, permissions,
        │                                 seeds empty lists, adds missing config rows,
        │                                 emails the setup code  MDI2:<base64 of {site, lists: [{n: name, id: GUID}]}>
        ▼
32 environment variables in solution MDI  1 "MDI SharePoint site" + 1 per list (display name = list name)
        │  set by: the import wizard, or Solutions → MDI → Environment variables, or
        │          flow "MDI - Connect Site" (paste the MDI2 code; Premium, MDI Dev only)
        ▼
apps and flows in solution MDI            every SharePoint data source points at an environment variable,
                                          never at a hard-coded site or list
```

What that means in practice:
- **A list only exists in the package if it's in `mdi_package.json`.** A list made by hand in SharePoint works today but won't be recreated on a rebuilt or new site, and has no permissions plan. For anything that lasts, put it in the package.
- **An app only moves between sites if its lists are environment variables.** That happens when the app is created **inside the MDI solution** and its lists are added with environment variables turned on (Step 5). An app created outside the solution is hard-wired to one site.
- **`MDI - Connect Site` matches environment variables to lists by display name.** The variable for list `Shift_Checks` must be named exactly `Shift_Checks`.
- **Permissions come in three plans** (`perms` in the package; applied by Set Up Site, list by list):

  | Plan | Owners | MDI Config Editors | Members | Visitors | Use for |
  |---|---|---|---|---|---|
  | `data` | Full | add/edit, no delete | add/edit, no delete | read | anything people enter on the floor |
  | `config` | Full | edit | read | read | settings, standards, reference lists |
  | `log` | Full | read | read | read | written only by flows (Escalation_Log) |

  People get into Members / MDI Config Editors / Owners through **MDI Settings → People** (the **MDI - Sync Permissions** flow does the SharePoint part). Nobody needs list permissions by hand.
- **Re-running Set Up Site on a live site** (needed to create a new list there):
  - **Safe for data:** creates only missing lists, columns and config rows; seeds a list only if it's empty; adds missing choices to choice columns.
  - **Resets on every MDI list:** the default view's columns (back to the package's) and the list permissions (back to the plan; anything granted by hand on an MDI list, or on single items, is removed). Ask before running if anyone has customized views or permissions on the Ohio site.
- **Production gets everything through a managed upgrade** of MDI, built in MDI Dev. Nothing is edited in production (`/ship-upgrade`).

Related files: `newalbany/deploy/flows/json/00_MDI-SetUpSite.json` and `06_MDI-ConnectSite.json` (generated; `check` compares them), `newalbany/solution/MDISetup_UNMANAGED_v*.zip`, `newalbany/deploy/package/build_package.js` (rewires a whole managed export to another site from an MDI2 code; for a new plant), HANDOFF.md §3C (new site).

---

## Part 2. Step by step

Example used throughout: a list **Shift_Checks** and an app **MDI Shift Checks**. About 1–2 hours the first time.

### 1. Decide (Kenny + Claude, 5 minutes)
- **List name:** letters, digits and underscores, no spaces (`Shift_Checks`). It becomes the name in formulas, the environment variable and the Set Up Site entry. Don't rename it later.
- **Columns:** name, type and required. Types that work end to end: Text, Note (multi-line), Number, DateTime (date only), Choice, Boolean. Add **Active** (Boolean, default Yes) so records are retired, never deleted. Person, lookup and multi-choice columns work in SharePoint but need hand work in the app.
- **Which plan:** `data`, `config` or `log` (table above).
- **Indexes:** any column the app filters on (usually Line and a date). Needed once the list passes 5,000 items.
- **Who uses the app, on what device:** Tablet 1920×1080 (TV, line tablet, PC) or Phone.

### 2. Add the list to the package (Claude)
Edit `newalbany/deploy/mdi_package.json`:
- `schema.<List>`: `base` 100 (a list; 101 = document library), `desc`, `title` (`{"name": "<what the Title column is called>", "req": true, "fmt": ""}`), `fields` (SharePoint field XML, one string per column; copy the type you need from an existing list: `Lines` has Text/Number/Boolean, `Lookups` Choice, `People` Note/MultiChoice, `HxH_Hourly` DateTime), `view` (column internal names for the default view, `LinkTitle` first), `query` (CAML order, optional), `rows` (view page size).
- `indexes.<List>`: column names (`*` on the end = unique).
- `perms.<plan>`: add the list name.
- `seed.<List>`: starter rows, only if the list needs them (seeded only when empty).

Then run `python3 newalbany/generator/make.py check`. It now reports the Set Up Site flow (`flow 00_MDI-SetUpSite.json`) and the setup package as **different**: that's expected, and stays until Step 9.

### 3. Build the installer and the starter screen (Claude)
- `python3 newalbany/generator/make.py flow-setup` → copy `newalbany/build/flows/00_MDI-SetUpSite.json` over `newalbany/deploy/flows/json/00_MDI-SetUpSite.json`.
- `python3 newalbany/generator/setup_package.py 1.0.0.1` (next version after the newest `newalbany/solution/MDISetup_UNMANAGED_v*.zip`) → `newalbany/build/MDISetup_UNMANAGED_v1.0.0.1.zip`.
- `python3 newalbany/generator/starter_app.py Shift_Checks "SHIFT CHECKS" shc` → `newalbany/build/Shift_Checks_v1.pa.yaml`: header, search, list of records, a form for every column that fits, SAVE, and RETIRE (sets Active = No). The third argument is a 2–4 letter prefix for control names; pick one no other app uses.
- Copy the starter to a real generator (`newalbany/generator/shc.py`), give it a `make.py` target, shape the screen there, then `make.py lint`. The starter is a starting point; the generator copy is the source of truth from now on.
- Push the branch; give Kenny the links: the MDI Setup zip (Download) and the screen file (Raw).

### 4. Create the list on the site (Kenny, MDI Dev)
1. make.powerapps.com → environment **MDI Dev** → **Solutions → Import solution** → `MDISetup_UNMANAGED_v1.0.0.1.zip` → Next → connections SharePoint + Outlook → **Import** (it upgrades MDI Setup in MDI Dev).
2. Solutions → **MDI Setup** → Cloud flows → **MDI - Set Up Site** → **Turn on** if off → **Run** → site `https://veepak1.sharepoint.com/sites/OhioContinuousImprovement` → Run. You must be a **site owner**. (Read the "re-running" note in Part 1 first.)
3. When it succeeds: open the site → Site contents → **Shift_Checks** should be there with its columns. A new `MDI2:` code arrives by email. Save it privately (`newalbany/deploy/customers/` on your own copy, never committed).

### 5. Create the app inside the solution (Kenny, MDI Dev)
1. Solutions → **MDI** → **+ New → App → Canvas app** → name `MDI Shift Checks`, format **Tablet** → Create. (Creating it from inside the solution is what makes it part of MDI.)
2. **Settings** (before pasting anything):
   - General → **Data row limit: 2000**.
   - General → **Automatically create environment variables when adding data sources: On**. It only works for an app created or edited from the solution; check it's on, don't assume it is.
   - Display → Custom **1920 × 1080**, Scale to fit **On**, Lock aspect ratio **On**, landscape (Tablet apps).
3. **Data → + Add data → SharePoint →** your connection. If it shows an **Advanced** tab listing environment variables, use it: pick the existing site variable **MDI SharePoint site**. Otherwise pick the site `…/OhioContinuousImprovement`, tick **Shift_Checks**, Connect; if it says a variable already exists for the site, **use the existing one** (a second site variable means two things to repoint later).
4. Add the other lists the screen uses (for example **Lines** for a line dropdown), the same way. Each existing list already has a variable; when it offers the existing one, keep it.

### 6. Paste the screen (Kenny)
1. Open the Raw link, Ctrl+A, Ctrl+C.
2. Tree view → right-click **Screen1** → **Paste**.
3. Screen1 → property **OnVisible** → paste `Select(shcRefresh)` (Claude gives the exact text).
4. Alt+click **REFRESH**. Red ⚠ → click it, send Claude the text (most often a list that wasn't added in 5.3).
5. Try it: + NEW → fill in → SAVE → it appears in the list; edit it; RETIRE it.
6. **Save → Publish → Publish this version.**

### 7. Check the environment variables (Kenny, 2 minutes)
Solutions → MDI → **Environment variables**: there must be one named exactly **Shift_Checks** (rename the display name if Studio called it something else; Connect Site and rebuilds depend on the name). It should show the site and the list as its current value.

### 8. Ship and share (Kenny, with `/ship-upgrade`)
1. Bump the MDI solution version, export **Managed**, import into **Vee Pak, LLC (default)** as an **Upgrade**.
2. The import asks for a value for the **new** environment variable: pick the Ohio site, then **Shift_Checks**.
3. **Share** the app with its users (a group is better than names) and the TV/kiosk account if it runs on a TV. If the app calls a flow, add them as **run-only** users on that flow too (that's what broke Holmdel on Nov 18).
4. Users must be **Members** of the site: MDI Settings → People. The list's plan does the rest.
5. Optional: add an `App_ShiftChecks` row to MDI_Config with the app's web link, for QR codes or buttons from other apps.

### 9. Close it out in the repo (Claude)
- Copy the final screen into `newalbany/deploy/apps/Shift_Checks_v1.pa.yaml` (from the generator target, not the starter).
- Copy the MDI Setup zip into `newalbany/solution/` (keep the old one until production has the new one, then remove it).
- Ask Kenny for an **unmanaged** export of MDI from MDI Dev and commit it to `newalbany/solution/` (the golden copy now includes the new app).
- Add an app card to `newalbany/deploy/apps/APP_BUILD_GUIDE.md`, the app to the tables in CLAUDE.md and `newalbany/SYSTEM_REFERENCE.md`, and a dated line to `newalbany/log.md`.
- `python3 newalbany/generator/make.py check` must be clean again (screens, flows and setup package all identical). Commit, push, merge to `main` once it's live.

---

## Part 3. What goes wrong

| Symptom | Cause | Fix |
|---|---|---|
| Set Up Site fails at **Create_list** / 403 | Run by someone who isn't a site owner | Run it as a site owner |
| Set Up Site **Add_field** red for one column | Bad field XML in the package | Send Claude the error; fix the XML in `mdi_package.json`, rebuild (Step 3), re-run (it skips what exists) |
| Views or permissions on other lists changed after Set Up Site | Expected: re-running resets default views and list permissions on every MDI list | Re-apply anything that was hand-made, or put it in the package |
| App shows the list but **"not found" in production** after the upgrade | The new environment variable wasn't given a value at import | Production: Solutions → Default Solution → Environment variables → **Shift_Checks** → current value = site + list (setting a value is allowed; editing apps is not) |
| Environment variable named `Shift Checks` or `Shift_Checks (…)` | Studio's default name | Rename the display name to exactly the list name |
| No environment variable was created at all | App made outside the solution, or the setting was off | Delete the data source, turn the setting on, add the list again; if the app isn't in Solutions → MDI → Apps, create it there and paste the screen again |
| "Delegation" warning, or records stop at 2,000 | Filter on a big list | Filter on an indexed column with a date window (see Hour x Hour and Tier 2) |
| "The attempted operation is prohibited…list view threshold" | More than 5,000 items and an unindexed filter column | Add the column to `indexes` in the package (re-run Set Up Site) or index it in List settings |
| Users can see but not save | Not site Members | MDI Settings → People → Active |
| `check` keeps saying the setup package differs | The new MDI Setup zip isn't in `newalbany/solution/` yet | Step 9 |

See also: `RISK_REGISTER.md` §4–5, `newalbany/TROUBLESHOOTING.md` §2–4.

---

## Part 4. Changing an existing list (add a column, add a choice, index it)

**Read this first.** MDI Dev (`MDI_Sandbox`) and production read the **same SharePoint site** (Ohio). A change to a list is live for production the moment it's made. So:
- Only **add** things (a column, a choice, an index). Adding is safe: apps and flows ignore columns they don't use.
- **List first, app second.** The column has to exist before any screen or flow uses it.
- Never rename, delete or change the type of a column that's in use (see "Don't" below).

Example: add a **SafetyCategory** choice column to **HxH_Hourly**.

### A. Add a column (most common)
1. **Decide (Kenny + Claude).** Which list, the column name, the type, and whether the app must require it.
   - Name: letters and digits, no spaces (`SafetyCategory`). Not `Value`, `Text`, `Date`, `Author`, `Title`, `Parent` or other Power Fx words.
   - Type: Text, Note (multi-line), Number, Date only, Choice, Yes/No.
   - **Required:** make it required **in the app**, never "Require that this column contains information" in SharePoint. A required SharePoint column makes every save from the current production apps fail until they're upgraded.
2. **Claude updates the package**, so a rebuilt or new site gets the column too: adds the field to `schema.<List>.fields` in `newalbany/deploy/mdi_package.json` (plus `indexes` if the app will filter on it), rebuilds the Set Up Site flow and the next `MDISetup_UNMANAGED_v*.zip` (Part 2, step 3), runs `check`, pushes.
3. **Kenny adds the column on the site.** Pick one:
   - **By hand (recommended for 1–3 columns; touches nothing else):** open the site → **Site contents** → the list (e.g. **HxH_Hourly**) → ⚙ (top right) → **List settings** → under Columns, **Create column** → **Column name**: type it **exactly** as Claude gave it (this sets its permanent internal name) → pick the type (for Choice, type the choices one per line) → leave "Require…" on **No** → **OK**.
   - **By running the updated MDI - Set Up Site** (adds every missing column at once): import the new MDI Setup zip in MDI Dev and run it as a site owner. It also **resets the default views and permissions on every MDI list**; ask first if anyone has customized those.
4. **Check:** List settings → the column is listed with the right name and type. Send Claude a screenshot.
5. **Make it visible to the app (MDI Dev):** open the app in Edit → left bar **Data** → the list → **⋯** → **Refresh**. Until this is done, formulas can't see the new column (red "name isn't valid" errors).
6. **Use it in the app:** `/change-app` (new version, paste, Publish, test). If a flow must write it: `/change-flow`.
7. **Ship:** `/ship-upgrade`. Production apps keep working before and after, because the column is only added.
8. **Claude closes it out:** log entry, `check` all identical, merge to `main` once live.

### B. Add a choice to a Choice column
- **Dropdowns in the apps mostly come from the Lookups list**, not from Choice columns. For those (downtime, scrap, rework, speed-loss reasons…), there's no list change at all: **MDI Settings → DROPDOWN LISTS → add the row.**
- For a real Choice column (e.g. Newspaper **Source**): List settings → click the column → add the new choice on its own line → **OK**. Claude adds it to `choiceAdds` in the package so new sites get it.

### C. Index a column (lists past 5,000 rows, or "list view threshold" errors)
List settings → **Indexed columns** → **Create a new index** → pick the column → **Create**. Claude adds it to `indexes` in the package.

### Don't (on a list that's in use)
| Don't | Why | Do instead (Claude plans it with you) |
|---|---|---|
| Rename a column | Apps use the display name: every formula using it breaks in production at once | Add a new column, switch the app to it in a new version, stop using the old one |
| Delete a column | Data is gone (recycle bin doesn't keep columns); apps break | Hide it from the view; leave it in the list |
| Change a column's type | Data can be lost or converted wrongly | New column of the right type, copy the data over, switch the app |
| Make an existing column required in SharePoint | Saves from apps that don't fill it fail | Require it in the app |
| Rename a list | Environment variables and Connect Site match lists by name | Don't; ask Claude |

**Bigger changes** (several columns, a type change, data copy): do them on a **scratch site** first (HANDOFF.md §3C), test the apps there, then repeat on Ohio.

