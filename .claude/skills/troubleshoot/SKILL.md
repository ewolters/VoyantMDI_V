---
name: troubleshoot
description: Diagnose an error message, a flow failure, a permissions problem, or a board showing blank/old/wrong data, for New Albany or Holmdel. Use whenever Kenny reports something broken or strange.
argument-hint: "[error or symptom]"
---

Problem reported: $ARGUMENTS

1. **Get the facts first.** If not given, ask for: the exact error text (or a screenshot), which plant (New Albany / Holmdel), which app + screen or which flow, who sees it (everyone, one person, the TV account), and when it started / what changed.
2. **Holmdel is a different system.** For Holmdel, work from `holmdel/TROUBLESHOOTING.md` (start with its "which of these is it" table), `holmdel/README.md` and `holmdel/HISTORY.md`; the New Albany docs mostly don't apply. Diagnostics there: the Sync flow's run history and `Production/_Tier2/tier2_data.json` (`lastRun`, `failed`, `warnings`).
3. **New Albany: look it up.** Search `TROUBLESHOOTING.md`, then `SYSTEM_REFERENCE.md` for how the piece works, (and `holmdel/README.md` for Holmdel) for the error text and symptom. Most known problems are there: permission errors §2, blank/stale boards §3, Studio/Power Fx §4.
4. **If it's a flow**, have Kenny open the flow's **run history** (Power Automate → the flow → 28-day run history → the failed run) and tell you which action is red and its error. Don't guess past that.
5. **If it's data** (wrong number on a board), find how the number is computed in the generator (search `generator/` for the label text) and explain it in plain words, then check the source list/board with Kenny.
6. **Fix in the right place:** permissions and connections are clicks in Power Automate / the admin center (give numbered steps); app logic changes go through `/change-app` in MDI Dev, never directly in production.
7. **When solved**, if it wasn't already in TROUBLESHOOTING.md, add a short entry (symptom → cause → fix → trap), commit and push.
