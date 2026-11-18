---
name: troubleshoot
description: Diagnose an error message, a flow failure, a permissions problem, or a board showing blank/old/wrong data, for New Albany or Holmdel. Use whenever Kenny reports something broken or strange.
argument-hint: "[error or symptom]"
---

Problem reported: $ARGUMENTS

1. **Get the facts first.** If not given, ask for: the exact error text (or a screenshot), which plant (New Albany / Holmdel), which app + screen or which flow, who sees it (everyone, one person, the TV account), and when it started / what changed.
2. **Check `RISK_REGISTER.md`** for a matching row (§8 there is the first-10-minutes triage), then follow its link.
3. **Holmdel is a different system.** For Holmdel, work from `holmdel/TROUBLESHOOTING.md` (start with its "which of these is it" table), `holmdel/README.md` and `holmdel/HISTORY.md`; the New Albany docs mostly don't apply. Diagnostics there: the Sync flow's run history and `Production/_Tier2/tier2_data.json` (`lastRun`, `failed`, `warnings`).
4. **New Albany: look it up.** Search `newalbany/TROUBLESHOOTING.md`, then `newalbany/SYSTEM_REFERENCE.md` for how the piece works, (and `holmdel/README.md` for Holmdel) for the error text and symptom. Most known problems are there: permission errors §2, blank/stale boards §3, Studio/Power Fx §4.
5. **If it's a flow**, have Kenny open the flow's **run history** (Power Automate → the flow → 28-day run history → the failed run) and tell you which action is red and its error. Don't guess past that.
6. **If it's data** (wrong number on a board), find how the number is computed in the generator (search `newalbany/generator/` for the label text) and explain it in plain words, then check the source list/board with Kenny.
7. **Fix in the right place:** permissions and connections are clicks in Power Automate / the admin center (give numbered steps); app logic changes go through `/change-app` in MDI Dev, never directly in production.
8. **When solved**, if it wasn't already there, add a short entry to that plant's TROUBLESHOOTING.md (symptom → cause → fix → trap), a row to `RISK_REGISTER.md` if it's a new kind of failure, and a dated line to the plant's `log.md`. Commit and push.

**Every reply in this skill ends with** the three parts in CLAUDE.md: *Question for you*, *Next step*, *You could ask me* (2–3 ready-to-copy prompts for this exact moment).
