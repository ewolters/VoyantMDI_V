# Voyant Virtual MDI: instructions for Claude

You are helping **Kenny** (Voyant, Vee Pak tenant) own and change a virtual MDI built on Microsoft 365. Kenny is a CI/operations person, not a developer, and is new to Claude Code. Eric Wolters built it and has left the project.

## Two plants, two different systems
Always establish **which plant** first. They share almost nothing:
- **New Albany (Ohio site):** the full MDI. SharePoint lists, 10 apps, 7 flows, environment variables, MDI Dev. Everything in this file below.
- **Holmdel:** Tier 2 only, **no lists**. A scheduled flow reads the Tier 1 Excel boards (via an Office Script on copies) into one JSON file that one app displays. Different solution, different connections (Christina's), different failure modes. Use `holmdel/TROUBLESHOOTING.md`, `holmdel/README.md` and `holmdel/HISTORY.md`; don't apply New Albany assumptions (no MDI_Config, no lists, no HxH app).

## How to work with Kenny
- **Plain words, one step at a time.** Give click-by-click directions for Power Apps / Power Automate ("Solutions → MDI → …"). Number the steps. Stop after anything he has to do in a browser and wait for him to report back.
- **Ask for the exact error text or a screenshot** (and which app, screen or flow) before proposing a fix. Don't guess from a summary. Check `TROUBLESHOOTING.md` first; most errors are already there.
- **Do the file work yourself.** Kenny shouldn't have to edit Python or YAML. You run the generators, check the output, and tell him which file to paste where.
- **Commands run on Windows.** Use `py` (or `python`) and backslash paths in anything you tell him to type. Prefer running commands yourself.
- **Say what's untested.** Nothing you generate has run until Kenny pastes it into Studio. Say so, and say what to check.

## What exists
| | |
|---|---|
| Production environment | **Vee Pak, LLC (default)**. Managed solution **MDI** (publisher `Cr21560`, prefix `craf4`), version 1.1.4.1 at hand-off, plus **MDI Setup**. |
| Dev environment | **MDI Dev**, where Kenny imports `solution/MDI_OhioContinuousImprovement_UNMANAGED_v1.1.4.1.zip`. All changes are made here. See START_HERE.md if it doesn't exist yet. |
| SharePoint site | `https://veepak1.sharepoint.com/sites/OhioContinuousImprovement` (about 33 lists: HxH_Hourly, HxH_Shift, Lines, PLAYBOOK, Lookups, MDI_Config, Newspaper, …). Schema: `deploy/mdi_package.json`. |
| Apps (10) | Tier 1 Hour x Hour, Tier 2 SQDC (+ WEEKS & MONTHS screen `scrPeriods`), Tier 3 War Room (Board, Bowler, Variances), Quality (REWORK + NCR), TS Maintenance, TS Binder, Newspaper, SW Manager, PC Audit, MDI Settings. |
| Flows (7 + setup) | HxH - Downtime Escalation, MDI - Upload Photo, MDI - Sync Permissions, MDI - Nightly Board Check, MDI - Frontier Critical Alert (off), MDI - Connect Site (needs Premium; not used at Ohio), MDI - Import History; MDI - Set Up Site (in MDI Setup). |
| Holmdel | Separate solution **MDI Tier 2 - Excel boards (no lists)** 1.0.0.19 in the same Vee Pak environment, imported and run by Christina DeRamos. See the Holmdel section above. Rebuild with `py holmdel/make.py`. |

## Repo map
- `deploy/apps/*.pa.yaml`: the current screen source for every app (one file per screen; `deploy/apps/APP_BUILD_GUIDE.md` says which file goes on which app/screen).
- `deploy/flows/json/`: flow definitions. `deploy/tools/`: browser-console scripts. `deploy/package/build_package.js`: rewires a managed export to another site (only needed for a new plant).
- `generator/`: Python that **writes** the `.pa.yaml` and flow JSON. **The generators are the source of truth**, not the YAML.
- `generator/make.py`: the only entry point you need.
- `solution/`: unmanaged solution zips for the dev environment.
- `TROUBLESHOOTING.md`: error → cause → fix. **Read it first for any reported problem.**
- `SYSTEM_REFERENCE.md`: how each flow and app works, the keys that link records, MDI_Config settings, where each board's math lives.
- `HANDOFF.md`: rebuilding from scratch (production, MDI Dev, a new site, Holmdel), backups, ownership.
- `log.md`: build history and decisions.

## Changing an app (the normal loop)
1. Find the generator: `py generator/make.py` lists targets (hxh, t2, t2periods, t3, t3screens, quality, mt, bd, np, pc, sw, fa, settings, flows, flow-import).
2. Before editing, run `py generator/make.py check`. It must say **all identical**; if not, someone hand-edited `deploy/apps` and you must reconcile first.
3. Edit the generator. Rebuild only that target: `py generator/make.py hxh`. Output lands in `build/` (git-ignored).
4. `py generator/make.py lint`. Fix anything reported. Also read the Power Fx traps in TROUBLESHOOTING.md §4; the lint doesn't catch them all.
5. Bump the version in the generator's output file name (e.g. HxH_Board_v22 → v23), rebuild, and copy the file into `deploy/apps/`, deleting the old version. Update `APP_BUILD_GUIDE.md` and this file's version notes if needed.
6. Tell Kenny exactly how to paste it **in MDI Dev**: which app, which screen, "select all controls on the screen and delete them, then select the screen and Ctrl+V", any OnVisible/App property to set, then **Publish**.
7. After he confirms it works: he ships it with the **ship-upgrade** skill steps (bump solution version, export managed, import as upgrade in production, check flows On).
8. Commit with a message that says what changed and the new file versions; add a dated line to `log.md`.

Small one-formula fixes can be given to Kenny to paste directly into a property in Studio, but **make the same change in the generator** in the same session so the next rebuild doesn't undo it.

## Rules
- **Never tell Kenny to edit or save anything in the production environment's managed solution** (apps or flows). It creates an unmanaged layer that blocks future upgrades. All edits happen in MDI Dev.
- **Never delete SharePoint list data or lists** without his explicit go-ahead, item by item. Prefer setting `Active = No` over deleting.
- **This repo is public.** Never commit passwords, setup codes (`MDI2:…`), personal data or Voyant documents. `deploy/customers/` is git-ignored for that reason.
- **Voyant's mail filter** blocks `.py` attachments and rewrites `https://` in `.txt` files. If something must be emailed, zip it without Python and write `https:\/\/` inside text scripts.
- **US English** in everything users see.

## Power Apps facts that bit us (details in TROUBLESHOOTING.md §4)
`Set()` is not allowed inside `ForAll()` · `IfError` with mixed types needs the 3-argument form · pasted classic ComboBoxes render blank rows · wrap-count galleries cap columns · SharePoint delegation returns at most the data row limit (2000), so load large lists in date chunks · a control that navigates to a screen errors until that screen exists · the export ships each app's **published** version · after a flow's inputs/outputs change, remove and re-add it in the app's Power Automate pane.
