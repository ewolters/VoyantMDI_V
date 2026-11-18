"""Builds Power Automate clientdata JSON for the MDI flows (solution-aware, connection references)."""
import json, os, sys

SITE = os.environ.get("MDI_SITE", "https://verxted.sharepoint.com/sites/MDISandbox")
L = {  # list GUIDs (sandbox); the installer swaps these
    "People": "a4c78ec3-d9a8-4997-90cd-a4bb5a0e454d",
    "MDI_Config": "1ce134d3-335f-415c-8ae0-e8cf7c0d9e16",
    "HxH_Shift": "5f5caae7-2355-467a-b3a4-f48b6d18820b",
    "HxH_Hourly": "afa6c071-4098-4a7f-b8a9-0277ce745c2d",
    "Newspaper": "803c69e8-a326-4ece-bc21-9ac6f5b4ce24",
    "Lines": "d0b85ec7-8373-4b66-a93b-2ad99def3859",
    "Escalation_Contacts": "ff7632ce-d24b-426b-b826-989760b9347b",
    "Escalation_Log": "ff327b68-5f04-4080-99f2-58aaf88082d6",
    "TS_Photos": "606ed8b0-435f-4bb0-b9d8-c019af11f008",
    "SAF_Results": os.environ.get("MDI_L_SAF_RESULTS", "0f228237-bfa8-4f0d-bf1e-8d1fdc141367"),
}
TEAMS_REF = os.environ.get("MDI_TEAMS_REF", "craf4_sharedteams_a7259")
TEAMS_API = "/providers/Microsoft.PowerApps/apis/shared_teams"
SP_REF = os.environ.get("MDI_SP_REF", "craf4_sharedsharepointonline_17d15")
O365_REF = os.environ.get("MDI_O365_REF", "craf4_sharedoffice365_mdi")
SP_API = "/providers/Microsoft.PowerApps/apis/shared_sharepointonline"
O365_API = "/providers/Microsoft.PowerApps/apis/shared_office365"
AUTH = "@parameters('$authentication')"
ESC_FLOOR = 15  # escalation flow wakes at this many cumulative minutes, then applies Escalation_FirstLevelMin


def refs(*names):
    out = {}
    if "sp_invoker" in names:
        out["shared_sharepointonline"] = {"runtimeSource": "invoker",
            "connection": {"connectionReferenceLogicalName": SP_REF}, "api": {"name": "shared_sharepointonline"}}
    if "teams" in names:
        out["shared_teams"] = {"runtimeSource": "embedded",
            "connection": {"connectionReferenceLogicalName": TEAMS_REF}, "api": {"name": "shared_teams"}}
    if "sp" in names:
        out["shared_sharepointonline"] = {"runtimeSource": "embedded",
            "connection": {"connectionReferenceLogicalName": SP_REF}, "api": {"name": "shared_sharepointonline"}}
    if "o365" in names:
        out["shared_office365"] = {"runtimeSource": "embedded",
            "connection": {"connectionReferenceLogicalName": O365_REF}, "api": {"name": "shared_office365"}}
    return out


def sp(op, params, after=None, **extra):
    a = {"runAfter": after or {}, "type": "OpenApiConnection",
         "inputs": {"host": {"apiId": SP_API, "connectionName": "shared_sharepointonline", "operationId": op},
                    "parameters": {"dataset": SITE, **params}, "authentication": AUTH}}
    a.update(extra)
    return a


def http(method, uri, after=None, body=None):
    p = {"parameters/method": method, "parameters/uri": uri,
         "parameters/headers": {"Accept": "application/json;odata=nometadata",
                                "Content-Type": "application/json;odata=nometadata"}}
    if body is not None:
        p["parameters/body"] = body
    return sp("HttpRequest", p, after)


def mail(to, subject, body, after=None):
    return {"runAfter": after or {}, "type": "OpenApiConnection",
            "inputs": {"host": {"apiId": O365_API, "connectionName": "shared_office365", "operationId": "SendEmailV2"},
                       "parameters": {"emailMessage/To": to, "emailMessage/Subject": subject,
                                      "emailMessage/Body": body, "emailMessage/Importance": "Normal"},
                       "authentication": AUTH}}


def catch(last, sp_auth=AUTH):
    """Failure alert: runs if the last top-level step failed, timed out or was skipped."""
    get = sp("GetItems", {"table": L["MDI_Config"], "$filter": "Title eq 'Alert_Email'", "$top": 1})
    get["inputs"]["authentication"] = sp_auth
    return {"Catch": {"type": "Scope", "runAfter": {last: ["Failed", "TimedOut", "Skipped"]}, "actions": {
        "Catch_get_alert_email": get,
        "Catch_send_alert": mail(
            "@{first(body('Catch_get_alert_email')?['value'])?['SettingValue']}",
            "MDI flow FAILED: @{workflow()?['tags']?['flowDisplayName']}",
            "<p>An MDI flow failed and needs a look.</p><p><b>Flow:</b> @{workflow()?['tags']?['flowDisplayName']}<br>"
            "<b>Run:</b> <a href=\"https://make.powerautomate.com/environments/@{workflow()?['tags']?['environmentName']}"
            "/flows/@{workflow()?['name']}/runs/@{workflow()?['run']?['name']}\">open the run history</a></p>",
            {"Catch_get_alert_email": ["Succeeded"]}),
    }}}


def wrap(triggers, actions, refnames):
    return {"properties": {"connectionReferences": refs(*refnames), "definition": {
        "$schema": "https://schema.management.azure.com/providers/Microsoft.Logic/schemas/2016-06-01/workflowdefinition.json#",
        "contentVersion": "1.0.0.0",
        "parameters": {"$connections": {"defaultValue": {}, "type": "Object"},
                       "$authentication": {"defaultValue": {}, "type": "SecureObject"}},
        "triggers": triggers, "actions": actions, "outputs": {}}}, "schemaVersion": "1.0.0.0"}


# ---------- 01 HxH - Downtime Escalation ----------
def flow01():
    tb = "triggerBody()"
    ne = "items('Notify_each')"
    trig = {"When_an_item_is_created_or_modified": {
        "recurrence": {"frequency": "Minute", "interval": 1},
        "evaluatedRecurrence": {"frequency": "Minute", "interval": 1},
        "splitOn": "@triggerOutputs()?['body/value']", "type": "OpenApiConnection",
        "inputs": {"parameters": {"dataset": SITE, "table": L["HxH_Hourly"]},
                   "host": {"apiId": SP_API, "connectionName": "shared_sharepointonline", "operationId": "GetOnUpdatedItems"},
                   "authentication": AUTH},
        # Wake at the escalation plan's first tier (15 min); the real start is MDI_Config Escalation_FirstLevelMin,
        # checked below, so MDI Settings -> ESCALATION -> FIRST LEVEL works. Settings below 15 act as 15.
        "conditions": [{"expression": f"@greaterOrEquals(coalesce(triggerBody()?['EscCumMin'],0),{ESC_FLOOR})"}],
        "runtimeConfiguration": {"concurrency": {"runs": 1}}}}
    a = {}
    a["Get_first_level"] = sp("GetItems", {"table": L["MDI_Config"],
                              "$filter": "Title eq 'Escalation_FirstLevelMin'", "$top": 1})
    fl = "first(body('Get_first_level')?['value'])?['SettingValue']"
    # Terminate (Succeeded) rather than skipping: a skipped Notify_each would fire the Catch failure alert.
    a["Below_first_level"] = {"type": "If", "runAfter": {"Get_first_level": ["Succeeded"]},
        "expression": {"and": [{"less": [f"@float(coalesce({tb}?['EscCumMin'],0))",
                                         f"@if(empty({fl}), 60.0, float({fl}))"]}]},
        "actions": {"Stop_below_first_level": {"type": "Terminate", "runAfter": {},
                                               "inputs": {"runStatus": "Succeeded"}}},
        "else": {"actions": {}}}
    a["Get_contacts"] = sp("GetItems", {"table": L["Escalation_Contacts"],
                           "$filter": f"Active eq 1 and Level le @{{{tb}?['EscCumMin']}}"},
                           {"Below_first_level": ["Succeeded"]})
    a["Get_log"] = sp("GetItems", {"table": L["Escalation_Log"],
                      "$filter": f"startswith(Title,'@{{{tb}?['ShiftKey']}}|@{{{tb}?['EscReason']}}|')"},
                      {"Get_contacts": ["Succeeded"]})
    a["To_notify"] = {"runAfter": {"Get_log": ["Succeeded"]}, "type": "Query", "inputs": {
        "from": "@body('Get_contacts')?['value']",
        "where": "@and(or(equals(item()?['ShiftSpecific'],false),contains(string(item()?['Shifts']),concat('\"Value\":\"',string(triggerBody()?['Shift']),'\"'))),not(contains(string(body('Get_log')?['value']),concat('|',string(item()?['Level']),'|',item()?['Email'],'\"'))))"}}
    msg = (f"<p><b>DOWNTIME ESCALATION - @{{{ne}?['Level']}} MIN LEVEL</b></p>"
           f"<p>Line @{{{tb}?['Line']}} | Shift @{{{tb}?['Shift']}} | @{{{tb}?['ProductForm']}}</p>"
           f"<p><b>@{{{tb}?['EscReason']}}</b>: @{{{tb}?['EscCumMin']}} min cumulative this shift (through hour @{{{tb}?['HourNo']}})</p>"
           f"<p>You are notified as: @{{{ne}?['Role']}}. Per the New Albany escalation plan: communicate up to the next level and across to your peers.</p>"
           f"<p>Entered by @{{{tb}?['EnteredBy']}}</p>")
    a["Notify_each"] = {"foreach": "@body('To_notify')", "runAfter": {"To_notify": ["Succeeded"]}, "type": "Foreach", "actions": {
        "Teams_alert": {"type": "OpenApiConnection", "inputs": {
            "parameters": {"poster": "Flow bot", "location": "Chat with Flow bot",
                           "body/recipient": f"@{{{ne}?['Email']}}", "body/messageBody": msg},
            "host": {"apiId": TEAMS_API, "connectionName": "shared_teams", "operationId": "PostMessageToConversation"},
            "authentication": AUTH}},
        "Log_notification": sp("PostItem", {
            "table": L["Escalation_Log"],
            "item/Title": f"@{{{tb}?['ShiftKey']}}|@{{{tb}?['EscReason']}}|@{{{ne}?['Level']}}|@{{{ne}?['Email']}}",
            "item/ShiftKey": f"@{{{tb}?['ShiftKey']}}", "item/Line": f"@{{{tb}?['Line']}}",
            "item/Shift": f"@{tb}?['Shift']", "item/Reason": f"@{{{tb}?['EscReason']}}",
            "item/CumMin": f"@{tb}?['EscCumMin']", "item/Level": f"@{ne}?['Level']",
            "item/ContactName": f"@{{{ne}?['Title']}}", "item/ContactEmail": f"@{{{ne}?['Email']}}",
            "item/Role": f"@{{{ne}?['Role']}}", "item/NotifiedAt": "@utcNow()"}, {"Teams_alert": ["Succeeded"]})}}
    a.update(catch("Notify_each"))
    return wrap(trig, a, ["sp", "teams", "o365"])


# ---------- 02 MDI - Upload Photo ----------
def flow02():
    RAW = {"value": "@json(decodeBase64(triggerOutputs().headers['X-MS-APIM-Tokens']))['$ConnectionKey']", "type": "Raw"}
    def fld(title, kind):
        hint = {"FILE": None, "TEXT": "Please enter your input", "NUMBER": "Please enter a number"}[kind]
        return {"description": hint, "title": title, "type": "string" if kind == "TEXT" else "number",
                "x-ms-content-hint": kind, "x-ms-dynamically-added": True}
    props = {"file": {"description": "Photo as base64 text (the apps send it this way)", "title": "Photo", "type": "string",
                      "x-ms-content-hint": "TEXT", "x-ms-dynamically-added": True},
             "text": fld("FileName", "TEXT"), "number": fld("ProcID", "NUMBER"), "number_1": fld("StepNo", "NUMBER"),
             "number_2": fld("IssueID", "NUMBER"), "text_1": fld("Kind", "TEXT"), "text_2": fld("Caption", "TEXT"),
             "text_3": fld("TakenBy", "TEXT")}
    trig = {"manual": {"type": "Request", "kind": "PowerAppV2", "inputs": {"schema": {
        "type": "object", "properties": props, "required": list(props.keys())}}}}
    tb = "triggerBody()"
    cf = sp("CreateFile", {"folderPath": "/TS_Photos", "name": f"@{{concat(utcNow('yyyyMMdd-HHmmss'),'_',{tb}?['text'])}}",
                           "body": f"@base64ToBinary(replace(last(split(string({tb}?['file']), ',')), '\"', ''))"},
            runtimeConfiguration={"contentTransfer": {"transferMode": "Chunked"}})
    cf["inputs"]["authentication"] = RAW
    up = sp("PatchFileItem", {"table": L["TS_Photos"], "id": "@{outputs('Create_file')?['body/ItemId']}",
            "item/Title": f"@{{{tb}?['text_2']}}", "item/Kind/Value": f"@{{{tb}?['text_1']}}",
            "item/ProcID": f"@{tb}?['number']", "item/StepNo": f"@{tb}?['number_1']", "item/IssueID": f"@{tb}?['number_2']",
            "item/Caption": f"@{{{tb}?['text_2']}}", "item/TakenBy": f"@{{{tb}?['text_3']}}"}, {"Create_file": ["Succeeded"]})
    up["inputs"]["authentication"] = RAW
    a = {"Create_file": cf, "Update_file_properties": up,
         "Respond_to_a_Power_App_or_flow": {"runAfter": {"Update_file_properties": ["Succeeded"]}, "type": "Response", "kind": "PowerApp",
            "inputs": {"schema": {"type": "object", "properties": {"photoid": {"title": "photoid", "type": "string",
                       "x-ms-content-hint": "TEXT", "x-ms-dynamically-added": True}}, "additionalProperties": {}},
                       "statusCode": 200, "body": {"photoid": "@{outputs('Create_file')?['body/ItemId']}"}}}}
    a.update(catch("Respond_to_a_Power_App_or_flow", RAW))
    return wrap(trig, a, ["sp_invoker", "o365"])


# ---------- 05 MDI - Frontier Critical Alert ----------
def flow05():
    tb = "triggerBody()"
    trig = {"When_a_Critical_finding_is_saved": {
        "type": "OpenApiConnection", "recurrence": {"interval": 1, "frequency": "Minute"},
        "splitOn": "@triggerOutputs()?['body/value']",
        "conditions": [{"expression": "@equals(triggerBody()?['Severity']?['Value'], 'Critical')"}],
        "inputs": {"host": {"apiId": SP_API, "connectionName": "shared_sharepointonline", "operationId": "GetOnNewItems"},
                   "parameters": {"dataset": SITE, "table": L["SAF_Results"]}, "authentication": AUTH}}}
    a = {}
    a["Get_safety_email"] = sp("GetItems", {"table": L["MDI_Config"], "$filter": "Title eq 'Safety_Email'", "$top": 1})
    a["All_recipients"] = {"type": "Compose", "runAfter": {"Get_safety_email": ["Succeeded"]},
        "inputs": f"@split(replace(concat(coalesce(first(body('Get_safety_email')?['value'])?['SettingValue'], ''), ';', coalesce({tb}?['ZoneOwnerEmail'], '')), ',', ';'), ';')"}
    a["Valid_recipients"] = {"type": "Query", "runAfter": {"All_recipients": ["Succeeded"]},
        "inputs": {"from": "@outputs('All_recipients')", "where": "@contains(trim(item()), '@')"}}
    a["Clean_recipients"] = {"type": "Select", "runAfter": {"Valid_recipients": ["Succeeded"]},
        "inputs": {"from": "@body('Valid_recipients')", "select": "@toLower(trim(item()))"}}
    msg = (f"<p><b>&#9888; CRITICAL SAFETY FINDING (Frontier audit)</b></p>"
           f"<p><b>Zone:</b> @{{{tb}?['ZoneID']}}@{{if(empty(coalesce({tb}?['Line'], '')), '', concat(' (line ', {tb}?['Line'], ')'))}}<br>"
           f"<b>What:</b> @{{{tb}?['Item']}} (@{{{tb}?['Kind']?['Value']}})<br>"
           f"<b>Finding:</b> @{{{tb}?['Finding']}}<br>"
           f"<b>Immediate action:</b> @{{coalesce({tb}?['ImmediateAction'], 'none recorded')}}</p>"
           f"<p>Critical = stop work until the area is safe, and escalate to site leadership within the hour. "
           f"The action is in NEWSPAPER (ref @{{{tb}?['NewspaperRef']}}).</p>")
    a["Alert_each"] = {"type": "Foreach", "foreach": "@union(body('Clean_recipients'), body('Clean_recipients'))",
        "runAfter": {"Clean_recipients": ["Succeeded"]}, "actions": {
        "Teams_alert": {"type": "OpenApiConnection", "inputs": {
            "parameters": {"poster": "Flow bot", "location": "Chat with Flow bot",
                           "body/recipient": "@{items('Alert_each')}", "body/messageBody": msg},
            "host": {"apiId": TEAMS_API, "connectionName": "shared_teams", "operationId": "PostMessageToConversation"},
            "authentication": AUTH}}}}
    a.update(catch("Alert_each"))
    return wrap(trig, a, ["sp", "teams", "o365"])


# ---------- 03 MDI - Sync Permissions ----------
def flow03():
    trig = {"When_a_People_row_changes": {
        "type": "OpenApiConnection", "recurrence": {"interval": 1, "frequency": "Minute"},
        "splitOn": "@triggerOutputs()?['body/value']",
        "inputs": {"host": {"apiId": SP_API, "connectionName": "shared_sharepointonline", "operationId": "GetOnUpdatedItems"},
                   "parameters": {"dataset": SITE, "table": L["People"]}, "authentication": AUTH}}}
    tb = "triggerBody()"
    active = f"equals({tb}?['Active'], true)"
    groups = ("@createArray("
              f"addProperty(json('{{\"name\":\"Members\",\"path\":\"AssociatedMemberGroup\"}}'), 'want', {active}),"
              f"addProperty(json('{{\"name\":\"Config editors\",\"path\":\"sitegroups/getbyname(''MDI%20Config%20Editors'')\"}}'), 'want', "
              f"and({active}, or(equals({tb}?['CanEditConfig'], true), equals({tb}?['MDIAdmin'], true)))),"
              f"addProperty(json('{{\"name\":\"Owners\",\"path\":\"AssociatedOwnerGroup\"}}'), 'want', "
              f"and({active}, equals({tb}?['MDIAdmin'], true)))"
              ")")
    it = "items('Each_group')"
    each = {"type": "Foreach", "foreach": "@outputs('Groups')",
            "runtimeConfiguration": {"concurrency": {"repetitions": 1}},
            "runAfter": {"Groups": ["Succeeded"]},
            "actions": {
                "Check_membership": http("GET",
                    f"_api/web/@{{{it}?['path']}}/users?$select=Id&$filter=LoginName eq '@{{outputs('LoginEnc')}}'"),
                "Is_member": {"type": "Compose", "runAfter": {"Check_membership": ["Succeeded"]},
                              "inputs": "@greater(length(coalesce(body('Check_membership')?['value'], createArray())), 0)"},
                "Add_if_needed": {"type": "If", "runAfter": {"Is_member": ["Succeeded"]},
                    "expression": {"and": [{"equals": [f"@{it}?['want']", True]}, {"equals": ["@outputs('Is_member')", False]}]},
                    "actions": {
                        "Ensure_user": http("POST", "_api/web/ensureuser",
                                            body="{\"logonName\":\"@{outputs('Login')}\"}"),
                        "Add_to_group": http("POST", f"_api/web/@{{{it}?['path']}}/users",
                                             {"Ensure_user": ["Succeeded"]},
                                             body="{\"LoginName\":\"@{outputs('Login')}\"}")},
                    "else": {"actions": {}}},
                "Remove_if_needed": {"type": "If", "runAfter": {"Add_if_needed": ["Succeeded"]},
                    "expression": {"and": [{"equals": [f"@{it}?['want']", False]}, {"equals": ["@outputs('Is_member')", True]}]},
                    "actions": {
                        "Remove_from_group": http("POST",
                            f"_api/web/@{{{it}?['path']}}/users/removeByLoginName(@v)?@v='@{{outputs('LoginEnc')}}'")},
                    "else": {"actions": {}}},
            }}
    acts = {
        "Has_email": {"type": "If", "runAfter": {},
            "expression": {"and": [{"not": {"equals": [f"@trim(coalesce({tb}?['Email'], ''))", ""]}}]},
            "actions": {
                "Login": {"type": "Compose", "runAfter": {},
                          "inputs": f"@concat('i:0#.f|membership|', toLower(trim({tb}?['Email'])))"},
                "LoginEnc": {"type": "Compose", "runAfter": {"Login": ["Succeeded"]},
                             "inputs": "@encodeUriComponent(outputs('Login'))"},
                "Groups": {"type": "Compose", "runAfter": {"LoginEnc": ["Succeeded"]}, "inputs": groups},
                "Each_group": each},
            "else": {"actions": {}}},
    }
    acts.update(catch("Has_email"))
    return wrap(trig, acts, ["sp", "o365"])


# ---------- 04 MDI - Nightly Board Check ----------
def flow04():
    trig = {"Every_morning": {"type": "Recurrence", "recurrence": {
        "frequency": "Day", "interval": 1, "timeZone": "Central Standard Time",
        "schedule": {"hours": ["6"], "minutes": [30]}}}}
    ct = "convertFromUtc(utcNow(), 'Central Standard Time')"
    sh = "items('Each_shift')"
    a = {}
    a["Today"] = {"type": "Compose", "runAfter": {}, "inputs": f"@formatDateTime({ct}, 'yyyy-MM-dd')"}
    a["Yesterday"] = {"type": "Compose", "runAfter": {"Today": ["Succeeded"]},
                      "inputs": f"@formatDateTime(addDays({ct}, -1), 'yyyy-MM-dd')"}
    a["Get_settings"] = sp("GetItems", {"table": L["MDI_Config"],
                           "$filter": "Title eq 'Alert_Email' or Title eq 'NB_MinMissing'"}, {"Yesterday": ["Succeeded"]})
    a["Alert_row"] = {"type": "Query", "runAfter": {"Get_settings": ["Succeeded"]},
                      "inputs": {"from": "@body('Get_settings')?['value']", "where": "@equals(item()?['Title'], 'Alert_Email')"}}
    a["Min_row"] = {"type": "Query", "runAfter": {"Alert_row": ["Succeeded"]},
                    "inputs": {"from": "@body('Get_settings')?['value']", "where": "@equals(item()?['Title'], 'NB_MinMissing')"}}
    a["AlertEmail"] = {"type": "Compose", "runAfter": {"Min_row": ["Succeeded"]},
                       "inputs": "@first(body('Alert_row'))?['SettingValue']"}
    a["MinMissing"] = {"type": "Compose", "runAfter": {"AlertEmail": ["Succeeded"]},
                       "inputs": "@int(coalesce(first(body('Min_row'))?['SettingValue'], '2'))"}
    win = "ShiftDate ge '@{outputs('Yesterday')}T00:00:00Z' and ShiftDate lt '@{outputs('Today')}T00:00:00Z'"
    a["Get_shifts"] = sp("GetItems", {"table": L["HxH_Shift"], "$filter": win, "$top": 500}, {"MinMissing": ["Succeeded"]})
    a["Get_hours"] = sp("GetItems", {"table": L["HxH_Hourly"], "$filter": win, "$top": 5000}, {"Get_shifts": ["Succeeded"]},
                        runtimeConfiguration={"paginationPolicy": {"minimumItemCount": 20000}})
    a["Incomplete"] = {"type": "InitializeVariable", "runAfter": {"Get_hours": ["Succeeded"]},
                       "inputs": {"variables": [{"name": "Incomplete", "type": "array", "value": []}]}}
    a["Each_shift"] = {"type": "Foreach", "foreach": "@body('Get_shifts')?['value']",
        "runtimeConfiguration": {"concurrency": {"repetitions": 1}}, "runAfter": {"Incomplete": ["Succeeded"]},
        "actions": {
            "Expected": {"type": "Compose", "runAfter": {},
                         "inputs": f"@div(add(int(mul(float(coalesce({sh}?['PlannedShiftHrs'], 0)), 60)), 59), 60)"},
            "Filled": {"type": "Query", "runAfter": {"Expected": ["Succeeded"]}, "inputs": {
                "from": "@body('Get_hours')?['value']",
                "where": f"@and(equals(item()?['ShiftKey'], {sh}?['Title']), not(equals(item()?['CumulativeUnits'], null)))"}},
            "Missing": {"type": "Compose", "runAfter": {"Filled": ["Succeeded"]},
                        "inputs": "@sub(outputs('Expected'), length(body('Filled')))"},
            "Enough_missing": {"type": "If", "runAfter": {"Missing": ["Succeeded"]},
                "expression": {"and": [{"greaterOrEquals": ["@outputs('Missing')", "@outputs('MinMissing')"]}]},
                "actions": {
                    "Existing_action": sp("GetItems", {"table": L["Newspaper"],
                                          "$filter": f"RefKey eq 'NB-@{{{sh}?['Title']}}'", "$top": 1}),
                    "Not_raised_yet": {"type": "If", "runAfter": {"Existing_action": ["Succeeded"]},
                        "expression": {"and": [{"equals": ["@length(body('Existing_action')?['value'])", 0]}]},
                        "actions": {"Raise_action": sp("PostItem", {
                            "table": L["Newspaper"],
                            "item/Title": f"Board not complete: @{{{sh}?['Title']}} (@{{outputs('Missing')}} of @{{outputs('Expected')}} hours missing)",
                            "item/Line": f"@{{{sh}?['Line']}}",
                            "item/SQDCP/Value": "People", "item/Source/Value": "HxH", "item/Status/Value": "Open",
                            "item/Progress": 0,
                            "item/Problem": "Hour-by-hour board left incomplete on @{outputs('Yesterday')}. Fill the missing hours and confirm the reason at Tier 1.",
                            "item/RaisedDate": "@utcNow()", "item/DueDate": "@addDays(utcNow(), 2)",
                            "item/RefKey": f"NB-@{{{sh}?['Title']}}"})},
                        "else": {"actions": {}}},
                    "Note_incomplete": {"type": "AppendToArrayVariable", "runAfter": {"Not_raised_yet": ["Succeeded"]},
                        "inputs": {"name": "Incomplete", "value": f"@{{{sh}?['Title']}}: @{{outputs('Missing')}} of @{{outputs('Expected')}} hours missing"}}},
                "else": {"actions": {}}}}}
    a["Get_lines"] = sp("GetItems", {"table": L["Lines"], "$filter": "Active eq 1"}, {"Each_shift": ["Succeeded"]})
    a["LinesRan"] = {"type": "Select", "runAfter": {"Get_lines": ["Succeeded"]},
                     "inputs": {"from": "@body('Get_shifts')?['value']", "select": "@item()?['Line']"}}
    a["NoBoard"] = {"type": "Query", "runAfter": {"LinesRan": ["Succeeded"]},
                    "inputs": {"from": "@body('Get_lines')?['value']", "where": "@not(contains(body('LinesRan'), item()?['Title']))"}}
    a["NoBoardNames"] = {"type": "Select", "runAfter": {"NoBoard": ["Succeeded"]},
                         "inputs": {"from": "@body('NoBoard')", "select": "@item()?['Title']"}}
    a["Send_digest"] = mail("@{outputs('AlertEmail')}",
        "MDI board check @{outputs('Yesterday')}: @{length(variables('Incomplete'))} incomplete shift(s)",
        "<p><b>Shifts checked:</b> @{length(body('Get_shifts')?['value'])}</p>"
        "<p><b>Incomplete (actions raised in NEWSPAPER):</b><br>@{if(empty(variables('Incomplete')), 'None', join(variables('Incomplete'), '<br>'))}</p>"
        "<p><b>Active lines with no board yesterday</b> (down, or not filled in?):<br>@{if(empty(body('NoBoardNames')), 'None', join(body('NoBoardNames'), ', '))}</p>",
        {"NoBoardNames": ["Succeeded"]})
    a.update(catch("Send_digest"))
    return wrap(trig, a, ["sp", "o365"])


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "."
    os.makedirs(out, exist_ok=True)
    for name, fn in [("01_HxH - Downtime Escalation", flow01), ("02_MDI - Upload Photo", flow02), ("03_MDI - Sync Permissions", flow03),
                     ("04_MDI - Nightly Board Check", flow04), ("05_MDI - Frontier Critical Alert", flow05)]:
        with open(os.path.join(out, name + ".json"), "w") as f:
            json.dump(fn(), f, indent=1)
    with open(os.path.join(out, "catch_block.json"), "w") as f:
        json.dump(catch("<LAST_STEP>"), f, indent=1)
    print("ok")
