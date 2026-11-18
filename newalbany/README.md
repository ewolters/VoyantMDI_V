# New Albany (Ohio) MDI

The full virtual MDI on Microsoft 365 for the Ohio Continuous Improvement site: about 33 SharePoint lists, 10 canvas apps, 7 flows, packaged as the managed solution **MDI** (publisher `Cr21560`, prefix `craf4`) in **Vee Pak, LLC (default)**, plus **MDI Setup**. Version 1.1.4.2 in production since Nov 18, 2026 (1.1.4.1 at hand-off).

| | |
|---|---|
| How it works (flows, apps, keys, MDI_Config, where each board's math lives) | [SYSTEM_REFERENCE.md](SYSTEM_REFERENCE.md) |
| Errors and fixes | [TROUBLESHOOTING.md](TROUBLESHOOTING.md) |
| Build history and decisions | [log.md](log.md) |
| Which screen file goes on which app | [deploy/apps/APP_BUILD_GUIDE.md](deploy/apps/APP_BUILD_GUIDE.md) |
| Adding a list or a new app; how the install works | [NEW_APP_GUIDE.md](NEW_APP_GUIDE.md) |
| Original hand-build install (lists, flows, apps one by one) | [deploy/README.md](deploy/README.md) |
| Rebuilding production, MDI Dev or a new site | [../HANDOFF.md](../HANDOFF.md) |

**Changing it:** `python3 newalbany/generator/make.py` lists the targets; `check` must report all identical before and after; edit the generator, never the YAML in `deploy/apps/` by hand. The full loop is in [../CLAUDE.md](../CLAUDE.md) and the `/change-app` skill. Changes are pasted into **MDI Dev** and shipped as a managed upgrade (`/ship-upgrade`).

**Install packages:** `solution/MDI_OhioContinuousImprovement_UNMANAGED_v1.1.4.2.zip` and `solution/MDISetup_UNMANAGED_v1.0.0.0.zip`, for MDI Dev only; never import an unmanaged zip into production.
