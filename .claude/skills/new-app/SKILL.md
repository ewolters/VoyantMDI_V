---
name: new-app
description: Add a new SharePoint list and/or a new canvas app to the New Albany MDI so it installs, upgrades, permissions and moves sites like the existing apps. Use when Kenny wants a new app, a new list, a new tracker or a new screen that stores its own data.
argument-hint: "[what the app should track]"
---

Request: $ARGUMENTS

Follow `newalbany/NEW_APP_GUIDE.md` Part 2. Read Part 1 first if you haven't this session.

1. **New Albany only.** Holmdel has no lists; if this is for Holmdel, stop and say so (a Holmdel change means the board script or `tier2_data.json`, see holmdel/README.md).
2. **Decide with Kenny (Step 1).** One short question at a time: what each record is, which columns (offer a proposed table he can say yes to), who enters it and on what device, which permission plan. Propose the list name.
3. **Baseline:** `python3 newalbany/generator/make.py check` must be clean before you change anything.
4. **Package (Step 2):** add the list to `newalbany/deploy/mdi_package.json` (schema, indexes, perms, seed only if needed). Copy field XML from an existing list of the same type. Include `Active` (Boolean, default 1).
5. **Build (Step 3):** `make.py flow-setup` → copy the 00 flow into `newalbany/deploy/flows/json/`; `setup_package.py <next version>`; `starter_app.py <List> "<TITLE>" <prefix>`; copy the starter into a new generator with a `make.py` target; `make.py lint`. Push the branch, give Kenny the Download link (setup zip) and the Raw link (screen).
6. **Walk Kenny through Steps 4–8**, one numbered block at a time, waiting for him after each. Before Step 4.2, tell him re-running Set Up Site resets default views and list permissions on every MDI list (NEW_APP_GUIDE Part 1) and ask whether anyone has customized those on the Ohio site.
7. **Close out (Step 9)** once it's live: deploy file, setup zip, unmanaged MDI export, APP_BUILD_GUIDE card, CLAUDE.md + SYSTEM_REFERENCE tables, `newalbany/log.md`. `check` must be clean. Commit, PR, merge to `main`.
8. Say what's untested: the starter screen has only been linted, never run in Studio, until Kenny pastes it.

**Every reply in this skill ends with** the three parts in CLAUDE.md: *Question for you*, *Next step*, *You could ask me* (2–3 ready-to-copy prompts for this exact moment).
