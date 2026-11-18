# Flow: MDI - Upload Photo  (shared photo pipeline for ALL MDI apps)

**What it does:** Power Apps sends a photo + tags; the flow saves it in the **TS_Photos** library (the shared MDI photo library), sets its tags and returns the new item ID. Apps then stamp **Module** + **RefID** on it.
**Name it exactly `MDI - Upload Photo`** — Power Apps calls it as `'MDI-UploadPhoto'`. If Power Apps shows a different name when you add it, find/replace that name in the app formulas.

1. **Trigger:** Power Apps → *When Power Apps calls a flow (V2)*. Add inputs **in this order** (order = argument order in Power Apps):
   | # | Type | Name |
   |---|---|---|
   | 1 | **Text** | Photo *(base64 text; the apps send `JSON(photo, JSONFormat.IncludeBinaryData)`)* |
   | 2 | Text | FileName |
   | 3 | Number | ProcID *(apps pass the RefID here)* |
   | 4 | Number | StepNo |
   | 5 | Number | IssueID |
   | 6 | Text | Kind |
   | 7 | Text | Caption |
   | 8 | Text | TakenBy |
   (Internal keys become file, text, number, number_1, number_2, text_1, text_2, text_3.)
2. **Create_file** — SharePoint *Create file*: Site = MDI site, Folder Path `/TS_Photos`,
   File Name `@{concat(utcNow('yyyyMMdd-HHmmss'),'_',triggerBody()?['text'])}`,
   File Content (type it bare, no braces): `@base64ToBinary(replace(last(split(string(triggerBody()?['file']), ',')), '"', ''))`
3. **Update file properties** — Library **TS_Photos**, Id `@{outputs('Create_file')?['body/ItemId']}`; Show all advanced:
   Title `@{triggerBody()?['text_2']}`, Kind Value (Enter custom value) `@{triggerBody()?['text_1']}`, ProcID `@triggerBody()?['number']`, StepNo `@triggerBody()?['number_1']`, IssueID `@triggerBody()?['number_2']`, Caption `@{triggerBody()?['text_2']}`, TakenBy `@{triggerBody()?['text_3']}`.
4. **Respond to a Power App or flow** — Text output **photoid** = `@{outputs('Create_file')?['body/ItemId']}`.
5. Save. In each app: Data → Add data → Power Automate pane → **+ Add flow** → **MDI - Upload Photo** (flows are NOT under Add data; if it isn't listed, search for it).

Gotcha: `"@{...}"` around the file content would turn the image into a base64 *text* file — it must be the bare `@base64ToBinary(...)`.


---
## Error handling — flow failure alert (Catch)
So a broken flow can't fail silently. One **Scope** named **Catch** goes after the **last** top-level step:
1. On Catch: **Settings → Run after** → tick *has failed*, *has timed out* and *is skipped*, and untick *is successful*. Any earlier failure makes the last step skip, so this catches everything.
2. Inside Catch: SharePoint **Get items**, List **MDI_Config**, Filter `Title eq 'Alert_Email'`, Top 1. Then Office 365 Outlook **Send an email (V2)**:
   - **To:** `first(body('Catch_get_alert_email')?['value'])?['SettingValue']`
   - **Subject:** `MDI flow FAILED: @{workflow()?['tags']?['flowDisplayName']}`
   - **Body:** a link to `https://make.powerautomate.com/environments/@{workflow()?['tags']?['environmentName']}/flows/@{workflow()?['name']}/runs/@{workflow()?['run']?['name']}`

The exact JSON is in `json/catch_block.json`.
