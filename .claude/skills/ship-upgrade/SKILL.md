---
name: ship-upgrade
description: Move a change that works in the MDI Dev environment into production as a managed upgrade. Use when Kenny says a change is tested and ready, or asks how to release/ship/publish to the plant.
---

Walk Kenny through these steps one block at a time, waiting for him to confirm each block.

**A. In MDI Dev** (make.powerapps.com, environment picker top right = MDI Dev)
1. Solutions → **MDI** → Apps: every app he changed must be **Published**. An export ships each app's *published* version; a saved-but-unpublished change is left behind.
2. Solutions → MDI → ⋯ → **Settings** (or Overview → version): raise the version, e.g. 1.1.4.1 → **1.1.4.2**. It must be higher than what production has.
3. Solutions → MDI → **Export solution** → Next → **Managed** → Export. Download the zip when it's ready (keep it; name shows the version).

**B. In production** (environment = Vee Pak, LLC (default))
4. Solutions → **Import solution** → Browse → the managed zip → Next.
5. Leave **Upgrade** selected (the default). Confirm connections if asked → **Import**. It takes a few minutes.
6. When it finishes: Solutions → MDI → **Cloud flows**: every flow except *MDI - Frontier Critical Alert* and *MDI - Connect Site* should say **On**. Turn on any that are off.
7. Open the changed app from make.powerapps.com → Apps (or its link) and check the change on the real board. TVs may need a refresh to load the new version.

**C. Record it**
8. Commit and push the repo: message `Release MDI <version>: <what changed>`. Add a dated line to `log.md` with the version and what changed.

**If the import fails:** get the exact message. Common ones:
- "solution is already installed as managed / unmanaged": he picked the wrong zip or wrong environment. The UNMANAGED zip never goes to production.
- Version not higher: bump it in MDI Dev and export again.
- Missing dependency / connection reference: see TROUBLESHOOTING.md §2.4.
- After import a flow won't turn on: TROUBLESHOOTING.md §2.3–2.4.
