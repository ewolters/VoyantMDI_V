# Holmdel build log

Dated changes to the Holmdel Tier 2 solution and this folder. The story of the three designs and the build-week problems is in [HISTORY.md](HISTORY.md).

- 2026-10 (build week, late Oct): Design 3 built: scheduled sync flow, Office Script on board copies, `tier2_data.json`, Tier 2 app.
- 2026-10-29/30: date range, clickable metrics, Board Notes removed, SQDC tabs with trends. 1.0.0.14 → 1.0.0.19 (current, imported by Christina DeRamos).
- 2026-11-16: new TV account ("HM") hit the Process/ReadAccess error; fixed with run-only on Tier 2 Data plus Basic User. Board froze at 6:55 am; cause not confirmed (TROUBLESHOOTING §3). Both cleared by Nov 18.
- 2026-11-18: Repo restructured to match New Albany: `deploy/` (Tier2_XB_v7.pa.yaml, ReadProductionBoard.ts), `solution/` (the 1.0.0.19 package), `generator/make.py`. The v1→v7 patch scripts moved to `generator/legacy/` (they no longer run end to end). `make.py check` now also proves `Tier2_XB_v7.pa.yaml` matches the app in the shipped package. Handed to Kenny.
