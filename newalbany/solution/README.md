# Solution packages (unmanaged)

These are the editable source of the installed solutions. Import them only into a **development** environment (e.g. `MDI Dev`), never into the production environment that already has the managed MDI. See `../TROUBLESHOOTING.md` §1.

| File | What it is |
|---|---|
| `MDI_OhioContinuousImprovement_UNMANAGED_v1.1.4.1.zip` | The full MDI (10 apps, 7 flows, 32 environment variables, 5 connection references), already pointed at the Vee Pak Ohio site and its lists. Same content as the managed 1.1.4.1 Kenny installed. Publisher `Cr21560`, prefix `craf4`. |
| `MDISetup_UNMANAGED_v1.0.0.0.zip` | The **MDI - Set Up Site** flow: creates or repairs the lists on a SharePoint site and emails the MDI2 setup code. |

To ship a change: edit and publish in the dev environment → raise the MDI version → Export as **Managed** → import into production as an **Upgrade**.
