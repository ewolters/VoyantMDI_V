# Flow 03 — MDI - Sync Permissions

**What it does:** keeps SharePoint access in step with the switches on the **People** list, so access is managed by editing a row, not in SharePoint settings.

| People switch | SharePoint group | Access |
|---|---|---|
| **Active** | site **Members** group | Add and edit data, no delete (Contribute - no delete); read config |
| **CanEditConfig** | **MDI Config Editors** | Also edit config lists: PLAYBOOK, Lookups, People, contacts, lines, standards, PC cards |
| **MDIAdmin** | site **Owners** group | Full control, including delete |

Setting a switch to No (or Active to No) removes the person from that group.

> **Lock-out guard:** keep at least one IT site owner who is **not** managed by this flow. That is, a site collection admin, or an owner who isn't listed in People. The flow will happily remove anyone whose MDIAdmin is turned off.

Build it **inside the MDI solution** (Solutions → MDI → + New → Automation → Cloud flow → Automated). Connector: **SharePoint** (standard licence).

---

## 1. Trigger
**SharePoint → When an item is created or modified**
- Site Address: your MDI site
- List Name: **People**

## 2. How it works (as built)
Skipped if Email is blank. Otherwise:
- **Login** = `i:0#.f|membership|<email>`, plus a URL-encoded copy.
- **Groups** = three rows: Members (want = Active), MDI Config Editors (want = Active and (CanEditConfig or MDIAdmin)), Owners (want = Active and MDIAdmin).
- **For each group** (one at a time): *Send an HTTP request to SharePoint* GET `…/users?$filter=LoginName eq '<login>'` to see if they're already in it.
  - want and not in → POST `_api/web/ensureuser`, then POST `…/users` with `{"LoginName": …}`.
  - not want and in → POST `…/users/removeByLoginName(@v)?@v='<login>'`.
  - Otherwise nothing. Checking first matters: SharePoint returns an error if you remove someone who isn't in the group.

The full definition is `json/03_MDI - Sync Permissions.json`.

## 3. Save, turn on, and test
1. Edit a test People row: Active = Yes, CanEditConfig = Yes.
2. Check **Site settings → People and groups → MDI Config Editors**. The person should be listed within about a minute.
3. Turn CanEditConfig off and check they are removed.

**Notes**
- The person must have an M365 account. The kiosk account (line tablets) goes in People as Role = Other, Active = Yes, both switches No.
- The flow runs as its owner, who must be a site owner.
- `CanLinkDowntime` is an app-level switch (Tier 2 reconcile). This flow doesn't touch it.


---
## Error handling — flow failure alert (Catch)
So a broken flow can't fail silently. One **Scope** named **Catch** goes after the **last** top-level step:
1. On Catch: **Settings → Run after** → tick *has failed*, *has timed out* and *is skipped*, and untick *is successful*. Any earlier failure makes the last step skip, so this catches everything.
2. Inside Catch: SharePoint **Get items**, List **MDI_Config**, Filter `Title eq 'Alert_Email'`, Top 1. Then Office 365 Outlook **Send an email (V2)**:
   - **To:** `first(body('Catch_get_alert_email')?['value'])?['SettingValue']`
   - **Subject:** `MDI flow FAILED: @{workflow()?['tags']?['flowDisplayName']}`
   - **Body:** a link to `https://make.powerautomate.com/environments/@{workflow()?['tags']?['environmentName']}/flows/@{workflow()?['name']}/runs/@{workflow()?['run']?['name']}`

The exact JSON is in `json/catch_block.json`.
