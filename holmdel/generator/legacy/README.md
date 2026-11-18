# Holmdel app scripts (history only)

These produced the Tier 2 screen during the Oct 2026 build: `app.py` wrote v1, and each `app_vN.py` patched the previous version. They no longer run end to end: `app_v2.py` was written against a hand-edited intermediate that isn't kept. `app_patch.py` is from the first, list-based design (MDI_Config) and doesn't apply to the live app.

**The app source is `holmdel/deploy/Tier2_XB_v7.pa.yaml`.** `python3 holmdel/generator/make.py check` proves it matches the app in the shipped 1.0.0.19 package. To change the app, edit a copy saved as `Tier2_XB_v8.pa.yaml` (or change it in Studio in an unmanaged dev import and export it); see holmdel/README.md "Changing it". Read these scripts only to see how a piece was built.
