# Flow: HxH - Downtime Escalation

**What it does:** whenever an HxH row is saved with 60+ cumulative minutes on the same downtime issue this shift, it notifies every active contact whose level has been reached (and who covers that shift), once per contact per issue per level, and logs it.

**Build (new designer, ~10 min).** Connections needed: SharePoint, Microsoft Teams.

1. **Trigger:** SharePoint → *When an item is created or modified*. Site = your MDI site, List = **HxH_Hourly**.
   - Settings → **Trigger conditions** → add: `@greaterOrEquals(coalesce(triggerBody()?['EscCumMin'],0),60)`
   - Settings → **Concurrency control** on, degree = **1**.
2. **Get_contacts** — SharePoint *Get items*, List = **Escalation_Contacts**, Filter Query:
   `Active eq 1 and Level le @{triggerBody()?['EscCumMin']}`
3. **Get_log** — SharePoint *Get items*, List = **Escalation_Log**, Filter Query:
   `startswith(Title,'@{triggerBody()?['ShiftKey']}|@{triggerBody()?['EscReason']}|')`
4. **To_notify** — *Filter array*, From `@body('Get_contacts')?['value']`, **Edit in advanced mode**:
   ```
   @and(or(equals(item()?['ShiftSpecific'],false),contains(string(item()?['Shifts']),concat('"Value":"',string(triggerBody()?['Shift']),'"'))),not(contains(string(body('Get_log')?['value']),concat('|',string(item()?['Level']),'|',item()?['Email'],'"'))))
   ```
5. **Notify_each** — *Apply to each* over `@body('To_notify')`:
   - **Teams_alert** — Microsoft Teams *Post message in a chat or channel*: Post as **Flow bot**, Post in **Chat with Flow bot**, Recipient (gear → Use dynamic content) `@{items('Notify_each')?['Email']}`. Message (Toggle code view, paste HTML):
     ```html
     <p><b>DOWNTIME ESCALATION — @{items('Notify_each')?['Level']} min level</b></p>
     <p>Line <b>@{triggerBody()?['Line']}</b> · Shift @{triggerBody()?['Shift']} · @{triggerBody()?['ProductForm']}<br>
     Issue: <b>@{triggerBody()?['EscReason']}</b> — <b>@{triggerBody()?['EscCumMin']} min</b> this shift (as of hour @{triggerBody()?['HourNo']})<br>
     Your role: @{items('Notify_each')?['Role']}</p>
     <p>Go to the line. Communicate up and across.</p>
     ```
   - **Log_notification** — SharePoint *Create item*, List = **Escalation_Log**:
     Title `@{triggerBody()?['ShiftKey']}|@{triggerBody()?['EscReason']}|@{items('Notify_each')?['Level']}|@{items('Notify_each')?['Email']}`,
     ShiftKey, Line, Shift, Reason (= EscReason), CumMin (= EscCumMin), Level, ContactName (= Title), ContactEmail (= Email), Role, NotifiedAt `@{utcNow()}`.
6. Save, turn on. **Test:** add yourself to Escalation_Contacts (Active, Level 60), log 65 min on one reason in the HxH board → Teams message + one Escalation_Log row; raise to 125 min with a Level 120 contact → only the 120 contact is notified.

Tips: typing `@{expr}` (or a bare `@expr`) into a field stores a live expression in the new designer. Rich-text fields escape HTML unless you use *Toggle code view*.
Optional: add *Create item* in **Newspaper** (Source = Escalation) inside the loop to auto-raise an action.


---
## Error handling — flow failure alert (Catch)
So a broken flow can't fail silently. One **Scope** named **Catch** goes after the **last** top-level step:
1. On Catch: **Settings → Run after** → tick *has failed*, *has timed out* and *is skipped*, and untick *is successful*. Any earlier failure makes the last step skip, so this catches everything.
2. Inside Catch: SharePoint **Get items**, List **MDI_Config**, Filter `Title eq 'Alert_Email'`, Top 1. Then Office 365 Outlook **Send an email (V2)**:
   - **To:** `first(body('Catch_get_alert_email')?['value'])?['SettingValue']`
   - **Subject:** `MDI flow FAILED: @{workflow()?['tags']?['flowDisplayName']}`
   - **Body:** a link to `https://make.powerautomate.com/environments/@{workflow()?['tags']?['environmentName']}/flows/@{workflow()?['name']}/runs/@{workflow()?['run']?['name']}`

The exact JSON is in `json/catch_block.json`.
