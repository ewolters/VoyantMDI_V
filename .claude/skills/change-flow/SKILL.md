---
name: change-flow
description: Change one of the New Albany MDI flows (HxH - Downtime Escalation, MDI - Upload Photo, Sync Permissions, Nightly Board Check, Frontier Critical Alert, Import History) and deliver it as a patched unmanaged solution zip for MDI Dev. Use when Kenny asks for a flow behavior change or a flow bug fix.
argument-hint: "[what to change]"
---

Change requested: $ARGUMENTS

Proven end to end on Nov 18, 2026 with MDI 1.1.4.2 (escalation flow reads `Escalation_FirstLevelMin`): patched zip imported into Kenny's MDI Dev (`MDI_Sandbox`), the flow opened in the designer with the new steps and no errors.

1. **Pin down the request.** Which flow, what should change, and what must stay the same at current settings. Check the live setting values it depends on (ask Kenny for a screenshot of MDI Settings) so you know whether shipping changes floor behavior.
2. **Baseline.** `python3 newalbany/generator/make.py flows` and `python3 newalbany/generator/make.py flow-import`. Every file in `newalbany/build/flows/` must match `newalbany/deploy/flows/json/`. If not, stop and reconcile.
3. **Edit the generator**: `newalbany/generator/flows.py` (flows 01–05) or `newalbany/generator/flows/gen_import_flow.py` (Import History). Reuse its helpers (`sp()`, `mail()`, `catch()`, `L[...]`). Flow traps:
   - To stop a run early, use **Terminate (Succeeded)** inside an If. An empty branch that skips later steps makes the `Catch` scope fire (it runs after *Failed, TimedOut, Skipped*) and emails a false failure alert.
   - Trigger conditions can't look anything up. To make a threshold configurable, wake at a low floor in the trigger, then read MDI_Config and Terminate below the setting.
   - Settings in MDI_Config are text: guard blanks (`if(empty(x), default, float(x))`).
   - A list the flow didn't use before needs its environment-variable parameter in that flow. `patch_solution.py` refuses in that case: add it in MDI Dev by hand first, then re-export unmanaged.
4. **Rebuild and diff.** Re-run step 2's commands; only the intended flow may differ. Read the diff. Copy the changed JSON into `newalbany/deploy/flows/json/`.
5. **Patch the solution.** `python3 newalbany/generator/patch_solution.py <current version> <next version> "<Flow display name>"`. Check its output: actions added/removed are what you meant, changed entries = `solution.xml` + that flow only. Copy `newalbany/build/MDI_OhioContinuousImprovement_UNMANAGED_v<next>.zip` into `newalbany/solution/`.
6. **Docs.** Update the flow spec (`newalbany/deploy/flows/NN_*.md`), `newalbany/SYSTEM_REFERENCE.md` (flows table, MDI_Config table if a setting is involved), `newalbany/solution/README.md` (new zip row, marked not yet tested), and add a dated line to `newalbany/log.md`.
7. **Push and hand over.** Commit on a branch, push, and give Kenny the download link: `https://github.com/ewolters/VoyantMDI_V/raw/<branch>/newalbany/solution/<zip name>`.
8. **Kenny tests in MDI Dev** (`MDI_Sandbox`), one block at a time:
   1. Solutions → Import solution → Browse → the zip → Next. Advanced settings: untick *Enable plug-in steps and flows*. Connections → Import.
   2. Solutions list: MDI shows the new version, Managed = No.
   3. Solutions → MDI → Cloud flows: every flow **Off**.
   4. Open the changed flow in edit mode: the new steps are there, no red error markers. Close **without saving**.

   MDI Dev points at the real Ohio lists, so don't turn flows on there. A live run test needs a scratch site.
9. When it checks out: `/ship-upgrade` (export managed from MDI Dev, upgrade production, check flows On). Then mark the zip tested in `newalbany/solution/README.md`, log it, and open a PR to `main`.

**Every reply in this skill ends with** the three parts in CLAUDE.md: *Question for you*, *Next step*, *You could ask me* (2–3 ready-to-copy prompts for this exact moment).
