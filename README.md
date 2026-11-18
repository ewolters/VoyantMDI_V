# Voyant Virtual MDI (Microsoft 365 build)

**New owner? Read [START_HERE.md](START_HERE.md).** Rebuilding from scratch: [HANDOFF.md](HANDOFF.md). How it works: [newalbany/SYSTEM_REFERENCE.md](newalbany/SYSTEM_REFERENCE.md). Errors: [newalbany/TROUBLESHOOTING.md](newalbany/TROUBLESHOOTING.md). What can break: [RISK_REGISTER.md](RISK_REGISTER.md). Claude reads [CLAUDE.md](CLAUDE.md) automatically.

Virtual MDI boards for Voyant on Microsoft 365, for two plants that share almost nothing: **New Albany** (the full MDI on SharePoint lists) and **Holmdel** (Tier 2 read straight from the Excel boards).

The repo has one folder per plant, laid out the same way:

```
README.md  START_HERE.md  CLAUDE.md  HANDOFF.md     both plants
RISK_REGISTER.md                                    what can break, how you'd know, how to fix (both plants)
.claude/skills/                                     /change-app  /change-flow  /ship-upgrade  /troubleshoot  /new-app
newalbany/                    holmdel/
  README.md                     README.md           overview, where to look
  TROUBLESHOOTING.md            TROUBLESHOOTING.md  error -> cause -> fix
  SYSTEM_REFERENCE.md           HISTORY.md          how it works in depth / how it got here
  NEW_APP_GUIDE.md                                  adding a list or an app (New Albany only)
  log.md                        log.md              dated build log
  generator/make.py             generator/make.py   build + `check` (repo == what's installed)
  deploy/apps/*.pa.yaml         deploy/*.pa.yaml    screen source
  solution/*.zip                solution/*.zip      install packages
  build/                        build/              output (git-ignored)
```

- **New Albany** (`newalbany/`): the full MDI on SharePoint lists, 10 apps, 7 flows, managed solution **MDI**. The generators in `newalbany/generator/` are the source of truth for the screens; `newalbany/deploy/apps/APP_BUILD_GUIDE.md` says which file goes on which app and screen; `newalbany/deploy/README.md` is the original hand-build install.
- **Holmdel** (`holmdel/`): Tier 2 only, no lists, read from the Tier 1 Excel boards. Solution **MDI Tier 2 - Excel boards (no lists)** 1.0.0.19. The screen source is `holmdel/deploy/Tier2_XB_v7.pa.yaml`; the board-reading script is `holmdel/deploy/ReadProductionBoard.ts`.

New Albany app versions: Hour x Hour v22 · Tier 2 v19 + Weeks & Months v2 · Tier 3 Board v9 / Bowler v6 / Variances v7 · Quality v5 + NCR v2 · TS Maintenance v5 · TS Binder v2 · Newspaper v7 · SW Manager v4 · PC Audit v4 · QA Rework v4 · Frontier Audit v2 · MDI Settings (Escalation, Dropdowns, Lines, Standards, scrCfg v2, People, scrImport v2). Solution version 1.1.4.2 (in production since Nov 18, 2026).

Customer setup codes (`newalbany/deploy/customers/`) are deliberately not in this repo.
