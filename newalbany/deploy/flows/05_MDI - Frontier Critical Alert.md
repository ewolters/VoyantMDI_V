# Flow 05: MDI - Frontier Critical Alert

**What it does:** the moment a Frontier audit saves a **Critical** finding, everyone in `MDI_Config → Safety_Email` and the zone owner get a Teams message from the Flow bot. The message includes the zone, the item, the finding and the immediate action. A Critical finding means stop work until the area is safe, and escalate within the hour.

**Created by the flow installer** (`tools/install_flows.js.txt`), switched off. Turn it on with the others. The exact definition is in `json/05_MDI - Frontier Critical Alert.json`.

| Step | Detail |
|---|---|
| Trigger | SharePoint **When an item is created**, list **SAF_Results**. Trigger condition: `@equals(triggerBody()?['Severity']?['Value'], 'Critical')`, so other severities never start a run. |
| Get_safety_email | Get items, **MDI_Config**, filter `Title eq 'Safety_Email'` |
| All_recipients | Safety_Email (`;` or `,` separated) + the row's **ZoneOwnerEmail** |
| Valid / Clean_recipients | Keep entries containing `@`, then trim and lowercase them. `union()` removes duplicates. |
| Alert_each | Teams **Post message in a chat or channel**: Flow bot → Chat with Flow bot → recipient |
| Catch | Standard failure alert to `Alert_Email` |

**Test:** in Frontier Audit, rate an item **U**, choose severity **C**, fill in the finding, immediate action and photo, then submit. Within about a minute the people in Safety_Email and the zone owner get the Teams message.

**Notes**
- Recipients must be people in your Microsoft 365 tenant (the Flow bot can't message outside it).
- Leave `Safety_Email` blank and only the zone owner is alerted.
