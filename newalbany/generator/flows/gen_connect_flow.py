# MDI - Connect Site: paste the MDI2 setup code; points every MDI environment variable at the customer's site + lists,
# then restarts the MDI flows that are on so they pick up the new values.
import json, sys
DV = {"apiId": "/providers/Microsoft.PowerApps/apis/shared_commondataserviceforapps", "connectionName": "shared_commondataserviceforapps"}
AUTH = "@parameters('$authentication')"
def dv(op, params, after=None):
    return {"runAfter": after or {}, "type": "OpenApiConnection", "inputs": {"host": dict(DV, operationId=op), "parameters": params, "authentication": AUTH}}
ALL = ["Succeeded", "Failed", "Skipped", "TimedOut"]
E_ = "items('Each_variable')"
each_var = {
    "Match_list": {"runAfter": {}, "type": "Query", "inputs": {"from": "@outputs('Code')?['lists']", "where": "@equals(item()?['n'], " + E_ + "?['displayname'])"}},
    "New_value": {"runAfter": {"Match_list": ["Succeeded"]}, "type": "Compose",
        "inputs": "@if(equals(" + E_ + "?['parameterkey'], 'dataset'), outputs('Code')?['site'], if(empty(body('Match_list')), '', first(body('Match_list'))?['id']))"},
    "If_value": {"runAfter": {"New_value": ["Succeeded"]}, "type": "If",
        "expression": {"and": [{"not": {"equals": ["@outputs('New_value')", ""]}}, {"greater": ["@length(" + E_ + "?['environmentvariabledefinition_environmentvariablevalue'])", 0]}]},
        "actions": {"Set_value": dv("UpdateRecord", {"entityName": "environmentvariablevalues",
            "recordId": "@first(" + E_ + "?['environmentvariabledefinition_environmentvariablevalue'])?['environmentvariablevalueid']",
            "item/value": "@{outputs('New_value')}"})},
        "else": {"actions": {"Not_set": {"runAfter": {}, "type": "AppendToArrayVariable", "inputs": {"name": "Skipped", "value": "@" + E_ + "?['displayname']"}}}}},
}
W = "items('Each_flow')"
each_flow = {
    "Turn_off": dv("UpdateRecord", {"entityName": "workflows", "recordId": "@" + W + "?['workflowid']", "item/statecode": 0, "item/statuscode": 1}),
    "Turn_on": dv("UpdateRecord", {"entityName": "workflows", "recordId": "@" + W + "?['workflowid']", "item/statecode": 1, "item/statuscode": 2}, {"Turn_off": ["Succeeded"]}),
}
actions = {
    "Skipped_var": {"runAfter": {}, "type": "InitializeVariable", "inputs": {"variables": [{"name": "Skipped", "type": "array", "value": []}]}},
    "Code": {"runAfter": {"Skipped_var": ["Succeeded"]}, "type": "Compose",
        "inputs": "@json(decodeBase64(substring(trim(triggerBody()?['text']), 5)))"},
    "Check_code": {"runAfter": {"Code": ALL}, "type": "If",
        "expression": {"and": [{"startsWith": ["@trim(triggerBody()?['text'])", "MDI2:"]}, {"equals": ["@actions('Code')?['status']", "Succeeded"]}]},
        "actions": {}, "else": {"actions": {"Bad_code": {"runAfter": {}, "type": "Terminate", "inputs": {"runStatus": "Failed", "runError": {"code": "BadCode", "message": "That is not an MDI setup code. Paste the whole code from the setup email (it starts with MDI2:)."}}}}}},
    "Get_variables": dv("ListRecords", {"entityName": "environmentvariabledefinitions",
        "$select": "schemaname,displayname,parameterkey",
        "$filter": "type eq 100000004 and startswith(schemaname,'craf4_shared_sharepointonline')",
        "$expand": "environmentvariabledefinition_environmentvariablevalue($select=environmentvariablevalueid,value)"}, {"Check_code": ["Succeeded"]}),
    "Each_variable": {"runAfter": {"Get_variables": ["Succeeded"]}, "type": "Foreach", "foreach": "@outputs('Get_variables')?['body/value']", "actions": each_var,
        "runtimeConfiguration": {"concurrency": {"repetitions": 1}}},
    "Get_flows": dv("ListRecords", {"entityName": "workflows", "$select": "workflowid,name",
        "$filter": "category eq 5 and statecode eq 1 and (startswith(name,'MDI - ') or startswith(name,'HxH - ')) and name ne 'MDI - Connect Site' and name ne 'MDI - Set Up Site'"}, {"Each_variable": ["Succeeded"]}),
    "Each_flow": {"runAfter": {"Get_flows": ["Succeeded"]}, "type": "Foreach", "foreach": "@outputs('Get_flows')?['body/value']", "actions": each_flow,
        "runtimeConfiguration": {"concurrency": {"repetitions": 1}}},
    "Did_it_fail": {"runAfter": {"Each_flow": ALL}, "type": "If",
        "expression": {"or": [{"not": {"equals": ["@actions('Get_variables')?['status']", "Succeeded"]}}, {"not": {"equals": ["@actions('Each_variable')?['status']", "Succeeded"]}}]},
        "actions": {"Not_connected_error": {"runAfter": {}, "type": "Terminate", "inputs": {"runStatus": "Failed", "runError": {"code": "NotConnected",
            "message": "Nothing was changed: could not read or update the MDI settings. Open this run, click the red step and send the error to your MDI contact."}}}}, "else": {"actions": {}}},
    "Not_connected": {"runAfter": {"Did_it_fail": ["Succeeded"]}, "type": "If", "expression": {"greater": ["@length(variables('Skipped'))", 0]},
        "actions": {"Some_lists_missing": {"runAfter": {}, "type": "Terminate", "inputs": {"runStatus": "Failed", "runError": {"code": "ListsMissing",
            "message": "@{concat('Connected, except these (not in the setup code; run MDI - Set Up Site again, then this flow): ', join(variables('Skipped'), ', '))}"}}}}, "else": {"actions": {}}},
}
flow = {"properties": {
    "connectionReferences": {"shared_commondataserviceforapps": {"runtimeSource": "embedded", "connection": {"connectionReferenceLogicalName": "__REF_DV__"}, "api": {"name": "shared_commondataserviceforapps"}}},
    "definition": {"$schema": "https://schema.management.azure.com/providers/Microsoft.Logic/schemas/2016-06-01/workflowdefinition.json#", "contentVersion": "1.0.0.0",
        "parameters": {"$connections": {"defaultValue": {}, "type": "Object"}, "$authentication": {"defaultValue": {}, "type": "SecureObject"}},
        "triggers": {"manual": {"type": "Request", "kind": "Button", "inputs": {"schema": {"type": "object", "properties": {
            "text": {"title": "Setup code", "type": "string", "x-ms-dynamically-added": True, "description": "Paste the whole code from the setup email (starts with MDI2:)", "x-ms-content-hint": "TEXT"}}, "required": ["text"]}}}},
        "actions": actions, "outputs": {}}},
    "schemaVersion": "1.0.0.0"}
json.dump(flow, open(sys.argv[1], "w"), separators=(",", ":"))
