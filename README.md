# Voyant Virtual MDI (Microsoft 365 build)

**New owner? Read [START_HERE.md](START_HERE.md).** Rebuilding from scratch: [HANDOFF.md](HANDOFF.md). How it works: [SYSTEM_REFERENCE.md](SYSTEM_REFERENCE.md). Errors: [TROUBLESHOOTING.md](TROUBLESHOOTING.md). Claude reads [CLAUDE.md](CLAUDE.md) automatically.

Virtual MDI boards for Voyant New Albany, built entirely on Microsoft 365: SharePoint lists, Power Apps canvas apps (pasted from `.pa.yaml`), and Power Automate flows, packaged as the **MDI** managed solution.

| Folder | What's in it |
|---|---|
| `deploy/` | Everything needed to install: app screens (`apps/`, newest version of each), flow definitions (`flows/`), the site/list schema and provisioner (`mdi_package.json`, `provision_mdi.js`), the per-customer package builder (`package/`), console tools (`tools/`), and the install guide (`README.md`). |
| `deploy/apps/APP_BUILD_GUIDE.md` | Which file goes on which app and screen. |
| `generator/` | The Python generators that write the `.pa.yaml` screens and flow JSON. Run everything through `generator/make.py` (`check` proves the repo matches the installed apps; `lint` runs the checks). Old one-off scripts are in `generator/legacy/`. |
| `holmdel/` | Holmdel's Tier 2 (Excel boards, no lists): install notes, the 1.0.0.19 package, board-reading script, app source and generator. |
| `.claude/skills/` | `/change-app`, `/ship-upgrade`, `/troubleshoot` for Claude Code. |
| `solution/` | Unmanaged solution zips (MDI, MDI Setup) for the owner's dev environment, the starting point for building managed upgrades. |
| `log.md` | Engineering log for the build. |
| `TROUBLESHOOTING.md` | Owner's guide: how changes ship, permission errors (incl. Holmdel), blank-board checks, Power Fx traps, and a starter prompt for the owner's Claude. |

Current app versions: Hour x Hour v22 · Tier 2 v19 + Weeks & Months v2 · Tier 3 Board v9 / Bowler v6 / Variances v7 · Quality v5 + NCR v2 · TS Maintenance v5 · TS Binder v2 · Newspaper v7 · SW Manager v4 · PC Audit v4 · QA Rework v4 · Frontier Audit v2 · MDI Settings (Escalation, Dropdowns, Lines, Standards, scrCfg v2, People, scrImport v2). Solution version 1.1.4.1.

Customer setup codes (`deploy/customers/`) are deliberately not in this repo.
