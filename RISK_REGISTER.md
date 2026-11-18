# Risk register: what can break, how you'd know, how to fix it

Both plants. Written Nov 18, 2026 at hand-off, after deliberately breaking the repo's tooling to see what it catches (§7).

**How to read it.** Each row is one way the system can fail. *Likely* and *Impact* are High / Med / Low. *You'd notice* is the first symptom someone actually sees. *Fix* is the repair; *Prevent* is what stops it happening again. Section numbers point into the troubleshooting guides: **NA** = `newalbany/TROUBLESHOOTING.md`, **HT** = `holmdel/TROUBLESHOOTING.md`.

**For Claude:** when Kenny reports a problem, find the matching row here first, then follow the linked troubleshooting section. If nothing matches, add a row once it's solved.

---

## 1. Act on these now (highest risk at hand-off)

| # | Risk | Why it's top | Do this |
|---|---|---|---|
| 1 | **Holmdel runs on one person's connections (Christina).** Password change, MFA reset, leave, or account disabled → every sync run and every REFRESH fails. | Single point of failure for the whole plant's Tier 2. | Add a co-owner on both Holmdel flows, then move both connection references to a service account (HT §3.2). |
| 2 | **New Albany flow ownership / connections not duplicated** (HANDOFF §6 not done). Same failure for escalations, photos, permissions, the nightly check, history import. | Same as above, five flows. | Co-owner on each MDI flow; service-account connections. |
| 3 | **Viewers get "ReadAccess … entity Process"** whenever someone shares an app but not the flow behind it. Hit Oct 29, Nov 16 and Nov 18 (IT spent 90 min on it). | Will recur with every new hire and every new TV. | One M365 group of viewers: share the app to it **and** add it as run-only on every flow the app calls (HT §1, NA §2.1). |
| 4 | **Someone saves an edit to a managed app or flow in production.** Creates an unmanaged layer; later upgrades silently don't take effect for that component. | Easy to do by accident ("Edit" is right there). | Only edit in MDI Dev. If it happened: §4 row "unmanaged layer". |
| 5 | **The GitHub repo lives on Eric's personal account.** If it's deleted, renamed or access is removed, Kenny loses the source, the generators and these guides. | No other copy of the generators exists. | Transfer the repo to Kenny or a Voyant GitHub org, or Kenny keeps his own fork as a backup. |

---

## 2. People, access and accounts (both plants)

| What breaks | You'd notice | Likely | Impact | Fix | Prevent |
|---|---|---|---|---|---|
| App shared, flow not | "…ReadAccess right(s) for record … of entity Process" on REFRESH/SAVE | **High** | Med (that user only) | Flow details page → **Run only users** → add user; connections "Use this connection". Holmdel: reach Tier 2 Data via **Solutions** (it may not be in My flows, and the card there can vanish). HT §1, NA §2.1 | Groups, not names (row 3 above) |
| Brand-new account (TV/kiosk) has no environment role | Same error even after run-only is set | Med | Med | IT: Power Platform admin center → Vee Pak, LLC (default) → Users → **Basic User** | Ask IT for Basic User whenever a device account is created |
| Kiosk/TV account password expires or is reset | TV shows a sign-in screen; board blank | Med | Med (the floor stops seeing Tier 2) | Sign the TV back in (Holmdel's label is on the back of the TV) | IT: no-expiry policy for device accounts, or a shared device license |
| Someone removed from SharePoint site / People list | Can open the app but saves fail, or lists show empty | Med | Low–Med | NA: add them in MDI Settings → People (the Sync Permissions flow adds them to the site). Holmdel: Read on Documents/Production | Manage people through MDI Settings → People, not directly in SharePoint |
| Everyone locked out of the NA site (all owners removed by the People sync) | "Access denied" on the site for everyone | Low | **High** | Tenant/SharePoint admin restores an owner | Keep one IT site owner who is **not** in the People list (SYSTEM_REFERENCE §2) |
| User from outside the Voyant tenant set as escalation contact | Escalation never arrives (Teams bot can't reach them) | Low | Med | Use internal accounts only | Note on the Escalation settings screen |
| Viewer has the app but no Power Apps license | "You need a license" on open | Low | Med | IT assigns a license that includes Power Apps (standard M365 is enough; nothing here is Premium) | — |

## 3. Connections, ownership and licensing

| What breaks | You'd notice | Likely | Impact | Fix | Prevent |
|---|---|---|---|---|---|
| Connection owner's password/MFA changes or account is disabled | All runs of that flow red ("Unauthorized"/"connection invalid"); NA flows email `Alert_Email` from their Catch | **High** over a year | **High** | Solutions → the solution → **Connection references** → pick a working connection (sign in fresh). NA §2.3/2.4, HT §3.2 | Service account as connection owner; second flow owner |
| A flow is turned **Off** (after an import, or by Power Automate after repeated failures) | Data stops arriving at one time; no red runs, just no runs | Med | High | Open the flow → Turn on → Run once. HT §3.1 | After every import, check every flow says **On** (ship-upgrade step) |
| A **Premium** connector gets added (Dataverse, HTTP, SQL, a custom connector) | "This flow/app requires a Premium license"; or import blocked | Med (it's tempting) | **High**: every user would need Premium | Remove it; rebuild that step with standard connectors. NA §2.5 | Rule: standard connectors only. Holmdel's first design died on this. |
| `Alert_Email` blank or a departed person | Flows fail and nobody hears | Med | Med | MDI Settings → config → `Alert_Email` = a monitored mailbox or group | Use a group mailbox, not a person |
| Microsoft 365 / Power Platform outage (e.g. Nov 12–13, 2026) | Several things fail at once, no change made | Low–Med | Med, temporary | Check **Microsoft 365 Service health** first. Wait. Afterward cancel any hung run (HT §3.3) and press Run | — |
| Microsoft retires a feature used here (classic controls, a connector action, Office Scripts in flows) | Message center notice; later errors on old actions | Low per year | Med–High | Rebuild the affected screen/step in MDI Dev | IT forwards Power Platform Message center notices to Kenny |

## 4. Releases and environments (mainly New Albany)

| What breaks | You'd notice | Likely | Impact | Fix | Prevent |
|---|---|---|---|---|---|
| **Unmanaged layer in production** (an edit saved on a managed app/flow there) | An upgrade imports "successfully" but that app or flow doesn't change | Med | High | In production: Solutions → **MDI** → the app or flow → **⋯ → Advanced → See solution layers**. If the top layer is **Unmanaged** (Active), choose **Remove active customizations** (this throws away the production edit). Then re-import the upgrade | Never click Save on anything in production that says "managed". Edits happen only in MDI Dev |
| Upgrade shows **old screens** | After import, the change isn't there | Med | Low | MDI Dev: open the app → **Publish** → bump the version → export → import again. NA §3 | The export ships the *published* app: always Publish before exporting |
| Import refused: version not higher | "The solution is already installed with the same or higher version" | Med | Low | Bump the solution version in MDI Dev, export again | ship-upgrade skill step 1 |
| Upgrade imported as **Update** or into the wrong environment | Duplicate or missing components; or an unmanaged MDI appears in production | Low | High | If an unmanaged MDI landed in production, stop and rebuild from HANDOFF §3A; don't delete production lists | Import screen: check environment name (top right) and choose **Upgrade** |
| **MDI Dev writes to the real Ohio lists** | Test entries appear on the floor boards | Med | Med | Delete the test rows (or set `Active = No`); `newalbany/deploy/tools/clear_test_data.js.txt` exists for bulk test data | Test on a scratch site for risky changes (START_HERE) |
| MDI Dev environment gone (deleted by cleanup, IT, or expired) | Can't find MDI Dev in the environment picker | Low–Med | Med (no place to make changes) | HANDOFF §3B: create it again, import the unmanaged zip in `newalbany/solution/`, then re-apply any newer screens from `newalbany/deploy/apps/` | After each shipped change, export the **unmanaged** solution from MDI Dev and commit it to `newalbany/solution/` so the golden copy is current |
| `newalbany/solution/` zip older than production | Rebuilding MDI Dev loses changes shipped since | **High** (it's 1.1.4.1 today) | Med | Re-apply newer screens from `newalbany/deploy/apps/` (they're the record) | Same as above |
| A flow's inputs/outputs change but the app still has the old link | App error calling the flow ("invalid number of arguments") | Med when flows change | Med | In MDI Dev: app → Power Automate pane → remove the flow → add it again → Publish | Part of any flow change |
| Holmdel app change: unmanaged dev import route | Never run end to end (documented, untested) | — | Med | Follow holmdel/README "Changing it"; turn **Sync Excel Boards Off in MDI Dev** first | Do a dry run on a non-urgent change |

## 5. New Albany data (SharePoint lists)

| What breaks | You'd notice | Likely | Impact | Fix | Prevent |
|---|---|---|---|---|---|
| **Set Up Site re-run on the live site** (to add a new list) | Default views and list permissions on every MDI list go back to the package's | Med (whenever a list is added) | Med | Re-apply hand-made views/permissions, or add them to `mdi_package.json` | Ask before running; keep customizations in the package (NEW_APP_GUIDE Part 1) |
| New app's environment variable named differently from its list (`Shift Checks`) | Connect Site skips it; a rebuilt or new site leaves the app pointing at the old list | Med | Med | Rename the variable's display name to exactly the list name | NEW_APP_GUIDE Step 7 |
| New app created outside the MDI solution, or its lists added without environment variables | App works in MDI Dev but isn't in the export, or is hard-wired to one site | Med | Med | Create it from Solutions → MDI; re-add the data sources with the setting on | NEW_APP_GUIDE Step 5 |
| A list made by hand in SharePoint, not in the package | Works now; missing after a site rebuild or at a new plant | Med | Med | Add it to `mdi_package.json`, rebuild MDI Setup | NEW_APP_GUIDE Step 2 |
| A list column renamed or deleted in SharePoint | App errors "column not found", or a field goes blank | Low–Med | High | Recreate the column with the original **internal name** (schema: `newalbany/deploy/mdi_package.json`), or re-run **MDI - Set Up Site** (adds what's missing) | Only site owners can change columns; keep owners few |
| A list deleted | App shows nothing on that screen; flow GetTable 404 | Low | High | Restore from the SharePoint **site recycle bin** (93 days), else Set Up Site recreates it empty | Never delete lists (CLAUDE.md rule) |
| A line deleted or renamed in Lines/Lookups | History for that line vanishes from Tier 2/3, keys stop matching (`ShiftKey = <Line>-<yyyymmdd>-S<n>`) | Med | Med | Restore the old name; for retired lines set `Active = No` | Retire with Active = No, never rename a line that has history |
| **2,000-row limit** on a new formula | Totals quietly stop growing; old data "disappears" | Med when formulas change | Med | Load in date chunks like the existing screens (SYSTEM_REFERENCE §7) | Review any new Filter on HxH_Hourly / HxH_Shift / KPI_Daily |
| **5,000-item view threshold** on an unindexed column | "The attempted operation is prohibited because it exceeds the list view threshold" as lists grow | Med (HxH_Hourly grows fastest) | Med | Index the column in List settings → Indexed columns (the package's `indexes` lists the existing ones) | Filter large lists only on indexed columns (dates, keys) |
| Escalation_Contacts out of date | Escalations go to people who left, or nobody | **High** over time | Med | MDI Settings → Escalation | Review at each staffing change |
| MDI_Config wrong value | Board colors/thresholds wrong; settings "don't work" | Med | Low–Med | MDI Settings → config. Note three settings aren't read by anything (`Escalation_FirstLevelMin`, `TS_RankWindowDays`, `T2_TrendDays`, SYSTEM_REFERENCE §5) | — |
| History import from a workbook that's open, renamed tables, or odd cells ("3-4") | "Could not read…" or "n rows did not save" | Med | Low | Close the workbook; tables must be Tbl_Shift / Tbl_Production / Tbl_Downtime; re-run (saved rows are skipped). NA §3 | — |
| SharePoint storage fills (photos) | Upload Photo fails | Low | Low–Med | Clear old photos in TS_Photos or ask IT for more storage | — |
| Nightly Board Check timing | Runs 6:30 AM **Central** (New Albany is Eastern) | — | Low | Change the recurrence time zone in the flow (generator: `newalbany/generator/flows.py`) if the digest arrives at the wrong hour | — |

## 6. Holmdel (Excel boards, no lists)

| What breaks | You'd notice | Likely | Impact | Fix | Prevent |
|---|---|---|---|---|---|
| Board not **saved** (AutoSave off, desktop Excel) | One line blank or hours behind | **High** | Med | Ctrl+S / Send on that PC. HT §2.1 | AutoSave on for every line PC; save every hour |
| Board opened from a downloaded/local copy | That line never updates | Med | Med | Open from the SharePoint folder. HT §2.2 | Pin the SharePoint folder on line PCs |
| Board renamed, moved, or new month's file named differently | Line vanishes from Tier 2 | Med (every month a new file) | Med | Name must contain `Production Board`, inside `Production/<group>/Line N/`. HT §2.3 | Copy last month's file and rename only the month |
| **Board template changed** (rows/cells inserted or moved) | Numbers wrong or zero for that metric, **no error** | Med | **High** (silently wrong) | Update the cell map in `holmdel/deploy/ReadProductionBoard.ts`, test with `holmdel/generator/test` on a copy of the new board, rebuild (`holmdel/generator/make.py 1.0.0.20`), upgrade | Tell leads: no inserted rows/columns in the template; changes go through Kenny |
| A **hung sync run** (one run at a time) | Everything freezes at one time; history shows a run "Running" for hours | Low–Med | High | Open that run → **Cancel**; next run proceeds. HT §3.3 | — |
| Office Scripts disabled in the tenant, or sensitivity label on the files | "Run script" red: Forbidden / couldn't connect with Excel | Low | High | M365 admin → Org settings → Office Scripts → allow in Power Automate; no label on Production. HT §5 | — |
| Office Scripts daily quota (1,600 runs/user/day) | Runs fail late in the day | Low (about 24 boards × 48 runs fits) | Med | Fewer runs or fewer boards per run. HT §5 | Grows with lines: revisit if boards double |
| Christina's access to boards reduced (view without download) | Copy board 403 | Low | High | IT: Read with download on Documents/Production, Contribute on `_Tier2`. HT §5 | — |
| `tier2_data.json` checked out / `_Tier2` permissions | Save data red | Low | High | Check in / Contribute on `_Tier2`. HT §5 | Nobody edits `_Tier2` by hand |
| Old **Send to Central** macros or rollup workbooks still used | Someone reports numbers from the wrong place | Low | Low | They don't feed Tier 2 (holmdel/HISTORY.md) | — |
| Tier 2 vs board OEE mismatch | Leads dispute numbers | Med | Low | Tier 2 shows the board's own OEE cell; the template calculates shifts differently. HT §4 | Fix the template, not Tier 2 |

## 7. The repo and Claude (tested Nov 18)

Each failure below was created on purpose in a copy of the repo, and the checks were run. **Before** = what the tooling did at hand-off; **Now** = after the fixes made the same day.

| Broken on purpose | Before | Now |
|---|---|---|
| Hand-edited a deployed New Albany screen | caught by `check` | caught |
| Deleted a deployed screen | **missed** (check said all identical) | caught: NOT DEPLOYED |
| Left an old version (v21 next to v22) | **missed** | caught: NOT REBUILT |
| A generator crashes | failed, but still printed "23 identical" from last run's output | caught: NOT REBUILT, build folder cleared first |
| Hand-edited a deployed flow | **missed** (flows weren't compared) | caught: DIFF flow |
| Bad expression in a New Albany flow | **missed** (no flow lint) | caught: flow lint runs in `check` |
| Unbalanced bracket in a formula | printed, but lint still "passed" | lint fails |
| Duplicate property | caught | caught |
| `Set()` inside `ForAll()` | **missed** | caught (lint) |
| List-name typo (`HxH_Shiftt`) | **missed** | caught (lint) |
| Two-argument `IfError` with mixed types | missed | **still missed** (needs types; Studio shows it on paste) |
| Reference to a control or screen that doesn't exist | missed | **still missed** (Studio shows it on paste) |
| Holmdel screen file edited by one character | caught (new check) | caught |
| Holmdel board script syntax error | **missed** (built a broken package) | caught: `tsc` check, build refuses (skipped with a warning if `tsc` isn't installed) |
| Holmdel flow expression wrong argument count | caught (lint2) | caught |
| Holmdel version `banana`, or not higher than shipped | **missed** (built it) | refused |
| Holmdel skeleton zip missing | crashed with IndexError | clear message |

**Still on the human side:**

| What breaks | You'd notice | Fix | Prevent |
|---|---|---|---|
| Something pasted into **production** Studio instead of MDI Dev | "Editing this managed…" banner; unmanaged layer (§4) | §4 unmanaged-layer fix | Check the environment name before every paste |
| `main` doesn't match production | A rebuild "undoes" a live change | Merge each live change to `main`; never merge test branches | START_HERE habits |
| A Holmdel package built but the new zip not committed | Next build's version check compares against the old one | Commit the shipped zip to `holmdel/solution/` | Part of shipping Holmdel |
| Secrets or names committed (public repo) | They're on GitHub | Remove, push; the history still holds them (rewriting needs a force-push) | Setup codes stay in `newalbany/deploy/customers/` (git-ignored); first names only in docs |
| Claude's change looks right but fails in Studio | Red errors after paste | Send Claude the exact error text or a screenshot | Nothing is tested until it's pasted, published and used once |
| The cloud session lacks `tsc` | Holmdel check says "syntax check skipped" | `npm i -g typescript` in the session | — |

---

## 8. First 10 minutes when something breaks

1. **What exactly?** Exact error text or a photo, which plant, which app/screen or flow, which user/device, since when.
2. **One user or everyone?** One user → access (§2). Everyone → connections, flow off, outage (§3).
3. **Microsoft 365 Service health** if several things broke at once with no change made.
4. **Run history** of the flow involved: no runs (Off), red runs (open the red step), or "Running" for hours (cancel it).
5. **Anything changed recently?** An import, a new person, a password change, a new board file, a template edit.
6. Find the row in this file, follow its link. If it's new, solve it, then add a row here and a line to the plant's `log.md`.
