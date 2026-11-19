---
name: change-app
description: Change a screen, formula or behavior in one of the MDI apps (Hour x Hour, Tier 2, Tier 3, Quality, TS, Newspaper, SW, PC Audit, Settings, Frontier). Use when Kenny asks for any visual or logic change to an app.
argument-hint: "[what to change]"
---

Change requested: $ARGUMENTS

1. **Pin down the request.** Which app, which screen, what should it look like or do afterwards? If anything is ambiguous, ask Kenny one short question (a screenshot helps) before editing.
2. **Baseline.** Run `python3 newalbany/generator/make.py check`. It must report all identical. If not, stop and explain what differs before changing anything.
3. **Find the code.** `newalbany/generator/make.py` maps targets to generator files. Search the generator for the control name or the text shown on screen. Read enough of it to understand how the screen is built (helpers like `label()`, `btn()`, `gal()` come from `theme.py` / the app's own helpers).
4. **Edit the generator**, not the YAML. Keep the existing style. Watch the Power Fx traps in `newalbany/TROUBLESHOOTING.md` §4 (no `Set` inside `ForAll`, 3-argument `IfError` for mixed types, no pasted ComboBoxes, 2000-row delegation limit).
5. **Rebuild just that target** (`python3 newalbany/generator/make.py <target>`), then `python3 newalbany/generator/make.py lint`. Fix anything reported. Diff the new file in `newalbany/build/` against the current one in `newalbany/deploy/apps/` and confirm only the intended controls/properties changed.
6. **Version it.** Bump the version number in the generator's output file name, rebuild, copy the new file into `newalbany/deploy/apps/`, and delete the previous version there. Update `newalbany/deploy/apps/APP_BUILD_GUIDE.md` if it names the file.
7. **Tell Kenny how to apply it in MDI Dev**, numbered:
   - make.powerapps.com → environment **MDI Dev** → Solutions → MDI → the app → Edit.
   - Which screen, then the paste steps exactly as written in START_HERE "Replacing a screen" (plain words: click the screen name in Tree view, click the board, Ctrl+A, Delete, click the screen name, Ctrl+V). Never say "select first to last" or other developer shorthand (open it in Notepad, Ctrl+A, Ctrl+C).
   - Any screen OnVisible / App.OnStart property to set, and any new screen to create first (exact name).
   - Fix any red ✕ errors (send Claude the text), then **Publish**.
   - What to test, and what "working" looks like.
   For a one-formula change, giving him the formula for one property is fine. The generator still gets the same change.
8. Say clearly that it's untested until he pastes it, and wait for his result.
9. When he confirms: commit (`git add -A`, message naming the app and new file version), add a dated line to `newalbany/log.md`, push. Then offer `/ship-upgrade`.

**Every reply in this skill ends with** the three parts in CLAUDE.md: *Question for you*, *Next step*, *You could ask me* (2–3 ready-to-copy prompts for this exact moment).
