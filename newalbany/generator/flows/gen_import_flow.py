"""MDI - Import History: lists workbooks in <site>/Shared Documents/MDI_Imports and returns the Log_ tables
(Tbl_Production, Tbl_Downtime, Tbl_Shift) of one workbook as JSON text for the MDI Settings app to import."""
import json, sys, os
SITEVAR = "craf4_shared_sharepointonline_116804f493f543e68b7c121bf1791461"
SITEP = f"MDI SharePoint site ({SITEVAR})"
SITE = f"@parameters('{SITEP}')"
SP_REF, XL_REF = "craf4_sharedsharepointonline_17d15", "craf4_sharedexcelonlinebusiness_mdi"
AUTH = "@parameters('$authentication')"
SP_API = "/providers/Microsoft.PowerApps/apis/shared_sharepointonline"
XL_API = "/providers/Microsoft.PowerApps/apis/shared_excelonlinebusiness"
FOLDER = f"@{{concat(uriPath({SITE[1:]}), '/Shared Documents/MDI_Imports')}}"
FOLDER_URI = f"@{{replace(concat(uriPath({SITE[1:]}), '/Shared Documents/MDI_Imports'), ' ', '%20')}}"
JH = {"Accept": "application/json;odata=nometadata", "Content-Type": "application/json;odata=nometadata"}

def http(method, uri, after, body=None, headers=JH):
    p = {"dataset": SITE, "parameters/method": method, "parameters/uri": uri, "parameters/headers": headers}
    if body is not None: p["parameters/body"] = body
    return {"runAfter": after, "type": "OpenApiConnection",
            "inputs": {"host": {"apiId": SP_API, "connectionName": "shared_sharepointonline", "operationId": "HttpRequest"},
                       "parameters": p, "authentication": AUTH}}
def rows(table, after):
    return {"runAfter": after, "type": "OpenApiConnection",
            "inputs": {"host": {"apiId": XL_API, "connectionName": "shared_excelonlinebusiness", "operationId": "GetItems"},
                       "parameters": {"source": SITE, "drive": "@first(body('Find_documents_library'))?['id']",
                                      "file": "@body('Get_workbook')?['id']", "table": table, "dateTimeFormat": "ISO 8601"},
                       "authentication": AUTH},
            "runtimeConfiguration": {"paginationPolicy": {"minimumItemCount": 5000}}}
OUT = ["files", "folder", "prod", "dt", "shift", "err"]
def respond(name, after, vals):
    body = {k: vals.get(k, "") for k in OUT}
    return {name: {"runAfter": after, "type": "Response", "kind": "PowerApp",
            "inputs": {"statusCode": 200, "body": body,
                       "schema": {"type": "object", "properties": {k: {"title": k, "type": "string", "x-ms-content-hint": "TEXT", "x-ms-dynamically-added": True} for k in OUT}, "additionalProperties": {}}}}}

trig = {"manual": {"type": "Request", "kind": "PowerAppV2", "inputs": {"schema": {"type": "object", "properties": {
    "text": {"title": "Mode", "description": "LIST or READ", "type": "string", "x-ms-content-hint": "TEXT", "x-ms-dynamically-added": True},
    "text_1": {"title": "FileName", "description": "Workbook name in MDI_Imports (READ only)", "type": "string", "x-ms-content-hint": "TEXT", "x-ms-dynamically-added": True}},
    "required": ["text", "text_1"]}}}}

FURL = f"@{{concat({SITE[1:]}, '/Shared%20Documents/Forms/AllItems.aspx?id=', encodeUriComponent(concat(uriPath({SITE[1:]}), '/Shared Documents/MDI_Imports')))}}"
listing = {}
listing["List_files"] = http("GET", f"_api/web/GetFolderByServerRelativeUrl('{FOLDER_URI}')/Files?$select=Name,TimeLastModified,Length&$orderby=TimeLastModified%20desc", {})
listing.update(respond("Respond_list", {"List_files": ["Succeeded"]}, {"files": "@{string(body('List_files')?['value'])}", "folder": FURL}))
listing.update(respond("Respond_list_failed", {"List_files": ["Failed", "TimedOut"]}, {"folder": FURL, "err": "Could not list the MDI_Imports folder: @{outputs('List_files')?['statusCode']}"}))

reading = {}
reading["Get_drives"] = http("GET", "_api/v2.0/drives?$select=id,name,webUrl", {}, headers={"Accept": "application/json"})
reading["Find_documents_library"] = {"runAfter": {"Get_drives": ["Succeeded"]}, "type": "Query",
    "inputs": {"from": "@body('Get_drives')?['value']", "where": "@endsWith(toLower(item()?['webUrl']), '/shared%20documents')"}}
reading["Get_workbook"] = http("GET", "_api/v2.0/drives/@{first(body('Find_documents_library'))?['id']}/root:/MDI_Imports/@{encodeUriComponent(triggerBody()?['text_1'])}?$select=id,name",
                               {"Find_documents_library": ["Succeeded"]}, headers={"Accept": "application/json"})
for nm, tb in [("Rows_shift", "Tbl_Shift"), ("Rows_production", "Tbl_Production"), ("Rows_downtime", "Tbl_Downtime")]:
    reading[nm] = rows(tb, {"Get_workbook": ["Succeeded"]})
ALL3 = {"Rows_shift": ["Succeeded"], "Rows_production": ["Succeeded"], "Rows_downtime": ["Succeeded"]}
reading.update(respond("Respond_rows", ALL3, {"prod": "@{string(body('Rows_production')?['value'])}", "dt": "@{string(body('Rows_downtime')?['value'])}", "shift": "@{string(body('Rows_shift')?['value'])}"}))
reading.update(respond("Respond_read_failed", {"Respond_rows": ["Skipped"]},
    {"err": "Could not read @{triggerBody()?['text_1']}. It needs the tables Tbl_Shift, Tbl_Production and Tbl_Downtime (the Log_ tabs of the line data-entry workbook), and must not be open for editing by someone else."}))

actions = {
    "Make_sure_import_folder_exists": http("POST", "_api/web/folders", {}, body=f'{{"ServerRelativeUrl": "{FOLDER}"}}'),
    "List_or_read": {"runAfter": {"Make_sure_import_folder_exists": ["Succeeded", "Failed"]}, "type": "If",
        "expression": {"equals": ["@toUpper(triggerBody()?['text'])", "LIST"]},
        "actions": listing, "else": {"actions": reading}},
}
flow = {"properties": {
    "connectionReferences": {
        "shared_sharepointonline": {"runtimeSource": "embedded", "connection": {"connectionReferenceLogicalName": SP_REF}, "api": {"name": "shared_sharepointonline"}},
        "shared_excelonlinebusiness": {"runtimeSource": "embedded", "connection": {"connectionReferenceLogicalName": XL_REF}, "api": {"name": "shared_excelonlinebusiness"}}},
    "definition": {
        "$schema": "https://schema.management.azure.com/providers/Microsoft.Logic/schemas/2016-06-01/workflowdefinition.json#",
        "contentVersion": "1.0.0.0",
        "parameters": {"$connections": {"defaultValue": {}, "type": "Object"}, "$authentication": {"defaultValue": {}, "type": "SecureObject"},
                       SITEP: {"defaultValue": "https://verxted.sharepoint.com/sites/MDISandbox", "type": "String", "metadata": {"schemaName": SITEVAR}}},
        "triggers": trig, "actions": actions, "outputs": {}}},
    "schemaVersion": "1.0.0.0"}
s = json.dumps(flow, separators=(",", ":"))
os.makedirs(os.path.dirname(sys.argv[1]) or ".", exist_ok=True); open(sys.argv[1], "w").write(json.dumps(flow, indent=1))
print("ok", len(s))
