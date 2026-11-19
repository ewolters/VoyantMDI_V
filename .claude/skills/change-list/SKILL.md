---
name: change-list
description: Change an existing New Albany SharePoint list - add a column, add a choice, add an index - safely while production uses the same site. Use when Kenny asks to add a field/column, change a list or "do a schema change". For a brand-new list use /new-app.
argument-hint: "[list and what to add]"
---

Change requested: $ARGUMENTS

Follow `newalbany/NEW_APP_GUIDE.md` **Part 4** exactly. Key points:
1. MDI Dev and production share the Ohio site: a list change is live for production immediately. Only additive changes (column, choice, index) go straight to the site. Rename / delete / type change / making a column required in SharePoint / renaming a list: stop and plan the add-new-then-switch route with Kenny (Part 4 "Don't").
2. Agree the column name (no spaces, not a Power Fx word like Value/Text/Date/Author/Title/Parent), type, and whether the app requires it (in the app, never in SharePoint).
3. Update `newalbany/deploy/mdi_package.json` (field XML copied from an existing column of the same type; `indexes`, `choiceAdds` as needed), rebuild the Set Up Site flow (`make.py flow-setup`, copy to `deploy/flows/json`) and the next `MDISetup_UNMANAGED_v*.zip` (`setup_package.py`, next version, into `newalbany/solution/`), run `check`, push.
4. Walk Kenny through adding it **by hand** in List settings (plain words, one step at a time, exact column name), or through re-running Set Up Site only if he accepts that it resets views and permissions on every MDI list.
5. Have him send a screenshot of List settings, then refresh the data source in each app in MDI Dev (Data → list → ⋯ → Refresh) before any app change.
6. App change with `/change-app` (new version number), flow change with `/change-flow`, release with `/ship-upgrade`. Log it.

**Every reply in this skill ends with** the three parts in CLAUDE.md: *Question for you*, *Next step*, *You could ask me* (2–3 ready-to-copy prompts for this exact moment).
