"""Holmdel Tier 2 from Excel boards - no SharePoint lists.
Flow 1  MDI XB - Sync Excel Boards : every 30 min, changed boards -> Production/_Tier2/tier2_data.json
Flow 2  MDI XB - Tier 2 Data       : called by the app. GET -> data + settings, SAVE -> writes tier2_settings.json
"""
import json, sys
SCRIPT = open(sys.argv[1]).read(); OUTDIR = sys.argv[2]
OSTS = json.dumps({"version": "0.3.0", "body": SCRIPT, "description": "MDI XB: reads one Production Board for Tier 2. Deployed by the flow - edits here are overwritten.",
  "noCodeMetadata": "",
  "parameterInfo": json.dumps({"version": 1, "originalParameterOrder": [{"name": "settings", "index": 0}],
      "parameterSchema": {"type": "object", "required": ["settings"], "properties": {"settings": {"type": "string"}}},
      "returnSchema": {"type": "object", "properties": {"result": {"type": "string"}}},
      "signature": {"comment": "", "parameters": [{"name": "workbook", "comment": ""}, {"name": "settings", "comment": ""}]}}, separators=(",", ":")),
  "apiInfo": json.dumps({"variant": "synchronous", "variantVersion": 2}, separators=(",", ":"))}, separators=(",", ":"))
assert all(ord(c) < 128 for c in OSTS) and "@" not in OSTS
import hashlib
SCRIPT_FILE = "ReadProductionBoard_" + hashlib.sha1(SCRIPT.encode()).hexdigest()[:8] + ".osts"

EV = {
 "craf4_t2x_site": "SharePoint site of the boards (e.g. https://veepak1.sharepoint.com/holmdel)",
 "craf4_t2x_folder": "Board folder inside Documents (e.g. Production)",
 "craf4_t2x_shift1": "Shift 1 start-end (e.g. 07:00-15:15)",
 "craf4_t2x_shift2": "Shift 2 start-end (e.g. 15:15-23:30; blank = no 2nd shift)",
 "craf4_t2x_lunchmin": "Unpaid lunch minutes per shift (e.g. 30)",
 "craf4_t2x_breakmin": "Break minutes per shift (e.g. 20)",
}
def P(s): return f"{EV[s].split(' (')[0]} ({s})"
def par(s): return f"parameters('{P(s)}')"
def params(keys):
    p = {"$connections": {"defaultValue": {}, "type": "Object"}, "$authentication": {"defaultValue": {}, "type": "SecureObject"}}
    for k in keys: p[P(k)] = {"defaultValue": "", "type": "String", "metadata": {"schemaName": k}}
    return p
SP = "shared_sharepointonline"
def http(method, uri, body=None, after=None, accept="application/json"):
    a = {"runAfter": after if after is not None else {}, "type": "OpenApiConnection",
         "inputs": {"host": {"apiId": f"/providers/Microsoft.PowerApps/apis/{SP}", "connectionName": SP, "operationId": "HttpRequest"},
                    "parameters": {"dataset": "@outputs('Site')", "parameters/method": method, "parameters/uri": uri,
                                   "parameters/headers": {"Accept": accept, "Content-Type": "application/json"}},
                    "authentication": "@parameters('$authentication')"}}
    if body is not None: a["inputs"]["parameters"]["parameters/body"] = body
    return a
def sp_http(method, uri, after=None):  # classic SharePoint REST (nometadata)
    a = http(method, uri, after=after, accept="application/json;odata=nometadata")
    a["inputs"]["parameters"]["parameters/headers"]["Content-Type"] = "application/json;odata=nometadata"; return a
def ok(*n): return {x: ["Succeeded"] for x in n}
def any_(*n): return {x: ["Succeeded", "Failed", "Skipped", "TimedOut"] for x in n}
def compose(e, after): return {"runAfter": after, "type": "Compose", "inputs": e}
def query(frm, where, after): return {"runAfter": after, "type": "Query", "inputs": {"from": frm, "where": where}}
def iff(expr, yes, no=None, after=None): return {"runAfter": after or {}, "type": "If", "expression": expr, "actions": yes, "else": {"actions": no or {}}}
def setv(name, val, after): return {"runAfter": after, "type": "SetVariable", "inputs": {"name": name, "value": val}}
def init(name, typ, val, after): return {"runAfter": after, "type": "InitializeVariable", "inputs": {"variables": [{"name": name, "type": typ, "value": val}]}}
# file body may arrive parsed, as {$content}, or as text
def file_json(act, empty="{}"):
    return (f"if(equals(actions('{act}')?['status'], 'Succeeded'), "
            f"if(equals(string(body('{act}')?['$content']), ''), json(string(body('{act}'))), json(base64ToString(body('{act}')?['$content']))), json('{empty}'))")
def file_text(act):
    return (f"if(equals(actions('{act}')?['status'], 'Succeeded'), "
            f"if(equals(string(body('{act}')?['$content']), ''), string(body('{act}')), base64ToString(body('{act}')?['$content'])), '')")

def resolve(A, after):
    """Site, folder, the Production folder item, and the _Tier2 folder (created if missing)."""
    A["Site"] = compose("@{if(endsWith(trim(" + par("craf4_t2x_site") + "), '/'), take(trim(" + par("craf4_t2x_site") + "), sub(length(trim(" + par("craf4_t2x_site") + ")), 1)), trim(" + par("craf4_t2x_site") + "))}", after)
    # "Shared Documents/Production/", "/Production", "Production" -> "Production"
    A["Folder_raw"] = compose("@{replace(replace(replace(trim(" + par("craf4_t2x_folder") + "), '\\\\', '/'), 'Shared Documents/', ''), 'Documents/', '')}", after)
    A["Folder_lead"] = compose("@{if(startsWith(outputs('Folder_raw'), '/'), substring(outputs('Folder_raw'), 1, sub(length(outputs('Folder_raw')), 1)), outputs('Folder_raw'))}", ok("Folder_raw"))
    A["Folder"] = compose("@{if(endsWith(outputs('Folder_lead'), '/'), substring(outputs('Folder_lead'), 0, sub(length(outputs('Folder_lead')), 1)), outputs('Folder_lead'))}", ok("Folder_lead"))
    A["Get_board_folder"] = http("GET", "_api/v2.0/drive/root:/@{replace(outputs('Folder'), ' ', '%20')}?$select=id,name,webUrl,parentReference,sharepointIds", after=ok("Site", "Folder"))
    # Look for _Tier2 first; only create it when it is missing (no red "already exists" step on every run).
    A["List_board_folder"] = http("GET", "_api/v2.0/drive/items/@{body('Get_board_folder')?['id']}/children?$select=id,name&$top=999", after=ok("Get_board_folder"))
    A["Tier2_match"] = query("@body('List_board_folder')?['value']", "@equals(toLower(item()?['name']), '_tier2')", ok("List_board_folder"))
    A["Has_tier2"] = iff({"greater": ["@length(body('Tier2_match'))", 0]}, {},
        {"Make_tier2_folder": http("POST", "_api/v2.0/drive/items/@{body('Get_board_folder')?['id']}/children",
            body="{\"name\":\"_Tier2\",\"folder\":{},\"@microsoft.graph.conflictBehavior\":\"fail\"}")}, after=ok("Tier2_match"))
    A["Get_tier2_folder"] = http("GET", "_api/v2.0/drive/items/@{body('Get_board_folder')?['id']}:/_Tier2?$select=id", after=ok("Has_tier2"))
    return "Get_tier2_folder"

T2 = "body('Get_tier2_folder')?['id']"
_AFTER = "trim(substring(concat({x}, '    '), 4, length({x})))"   # text after the first 4 characters ("Line"); padded so short names never fail
LNUM = f"if(isInt({_AFTER}), string(int({_AFTER})), {_AFTER})"
def get_t2_file(name, after=None):
    p = "@{replace(replace(concat(outputs('LibUrl'), '/', outputs('Folder'), '/_Tier2/" + name + "'), '''', ''''''), ' ', '%20')}"
    return sp_http("GET", "_api/web/GetFileByServerRelativePath(decodedurl=@p)/$value?@p='" + p + "'", after=after)

# ======================= FLOW 1: SYNC =======================
A = {}
A["Run_start"] = compose("@formatDateTime(utcNow(), 'yyyy-MM-ddTHH:mm:ssZ')", {})
last = resolve(A, ok("Run_start"))
A["OSTS"] = compose(OSTS, ok("Run_start"))
A["Script_match"] = query("@body('List_tier2')?['value']", f"@equals(toLower(item()?['name']), '{SCRIPT_FILE.lower()}')", ok("List_tier2"))
A["Script_current"] = iff({"greater": ["@length(body('Script_match'))", 0]}, {},
    {"Upload_script": http("PUT", f"_api/v2.0/drive/items/@{{{T2}}}:/{SCRIPT_FILE}:/content", body="@{outputs('OSTS')}")},
    after=ok("Script_match", "OSTS"))
A["Get_script_id"] = http("GET", f"_api/v2.0/drive/items/@{{{T2}}}:/{SCRIPT_FILE}?$select=id", after=ok("Script_current"))
# Read last run's data file only if it exists (a first run has none - no false "failed" step).
A["List_tier2"] = http("GET", f"_api/v2.0/drive/items/@{{{T2}}}/children?$select=id,name,size&$top=999", after=ok(last))
A["Data_file"] = query("@body('List_tier2')?['value']", "@equals(toLower(item()?['name']), 'tier2_data.json')", ok("List_tier2"))
A["Init_text"] = init("DataText", "string", "", ok("Run_start"))
# Boards are read from copies (Excel only runs scripts on files the account can edit; board access may be read-only).
# Each run copies into its own folder; the folders of earlier runs are deleted (permanently, not to the recycle bin)
# at the start of the next run, when Excel has long released them. A failed delete is ignored and retried next run.
A["Copies_name"] = compose("@concat('board copies ', workflow()['run']['name'])", ok("Run_start"))
A["Old_copies"] = query("@body('List_tier2')?['value']", "@startsWith(toLower(item()?['name']), 'board copies')", ok("List_tier2"))
A["Clean_old_copies"] = {"runAfter": ok("Old_copies", "LibUrl"), "type": "Foreach", "foreach": "@body('Old_copies')",
    "runtimeConfiguration": {"concurrency": {"repetitions": 1}}, "actions": {
      "Delete_old": sp_http("POST", "_api/web/GetFolderByServerRelativePath(decodedurl=@p)/DeleteObject()?@p='@{replace(replace(concat(outputs('LibUrl'), '/', outputs('Folder'), '/_Tier2/', items('Clean_old_copies')?['name']), '\'\'', '\'\'\'\''), ' ', '%20')}'"),
      "Delete_tolerated": compose("@actions('Delete_old')?['status']", any_("Delete_old"))}}
A["Make_copies"] = http("POST", f"_api/v2.0/drive/items/@{{{T2}}}/children",
    body="@concat('{\"name\":\"', outputs('Copies_name'), '\",\"folder\":{},\"@microsoft.graph.conflictBehavior\":\"fail\"}')", after={"Clean_old_copies": ["Succeeded", "Failed"], "Copies_name": ["Succeeded"]})
A["Get_copies_folder"] = http("GET", f"_api/v2.0/drive/items/@{{{T2}}}:/@{{replace(outputs('Copies_name'), ' ', '%20')}}?$select=id", after=ok("Make_copies"))
A["If_data"] = iff({"greater": ["@length(body('Data_file'))", 0]},
    {"Get_data": get_t2_file("tier2_data.json"),
     "Keep_text": setv("DataText", "@{" + file_text("Get_data") + "}", ok("Get_data"))}, after=ok("Data_file", "Init_text", "LibUrl"))
A["Existing"] = compose("@json(if(empty(variables('DataText')), '{}', variables('DataText')))", ok("If_data"))
# Data files older than this build (version < 3) were read with the old date rules: re-read the full 45 days once.
A["Since"] = compose("@formatDateTime(if(less(int(coalesce(outputs('Existing')?['version'], 0)), 3), addDays(utcNow(), -45), addMinutes(coalesce(outputs('Existing')?['lastRun'], addDays(utcNow(), -45)), -5)), 'yyyy-MM-ddTHH:mm:ssZ')", ok("Existing"))
A["Init_rows"] = init("Rows", "array", "@coalesce(outputs('Existing')?['rows'], json('[]'))", ok("Existing"))
A["Init_reasons"] = init("Reasons", "array", "@coalesce(outputs('Existing')?['reasons'], json('[]'))", ok("Init_rows"))
A["Init_warnings"] = init("Warnings", "array", "@coalesce(outputs('Existing')?['warnings'], json('[]'))", ok("Init_reasons"))
A["Init_read"] = init("Read", "array", "@json('[]')", ok("Init_warnings"))
A["Init_failed"] = init("Failed", "array", "@json('[]')", ok("Init_read"))
A["Init_read_urls"] = init("ReadUrls", "array", "@json('[]')", ok("Init_failed"))
A["SitePath"] = compose("@uriPath(outputs('Site'))", ok("Site"))
A["LibUrl"] = compose("@concat(if(equals(outputs('SitePath'), '/'), '', outputs('SitePath')), '/Shared Documents')", ok("SitePath"))
# Walk only Production/<group>/<line>/<board>: one call returns the groups, their line folders and the files in them.
A["RootPath"] = compose("@concat(outputs('LibUrl'), '/', outputs('Folder'))", ok("LibUrl", "Folder"))
A["Get_tree"] = sp_http("GET", "_api/web/GetFolderByServerRelativePath(decodedurl=@p)/Folders?@p='@{replace(replace(outputs('RootPath'), '''', ''''''), ' ', '%20')}'&$expand=Folders,Folders/Files", after=ok("RootPath", "Since"))
A["Init_lines"] = init("LinesV", "array", "@json('[]')", ok("Init_read_urls"))
A["Init_files"] = init("Files", "array", "@json('[]')", ok("Init_lines"))
LN = "items('Each_line')?['Name']"
REM = _AFTER.format(x=LN)
LID = LNUM.format(x=LN)
F = "items('Each_file')"
A["Each_group"] = {"runAfter": ok("Get_tree", "Init_files"), "type": "Foreach", "foreach": "@body('Get_tree')?['value']",
  "runtimeConfiguration": {"concurrency": {"repetitions": 1}}, "actions": {
   "Each_line": {"runAfter": {}, "type": "Foreach", "foreach": "@coalesce(items('Each_group')?['Folders'], json('[]'))",
    "runtimeConfiguration": {"concurrency": {"repetitions": 1}}, "actions": {
     "Is_line_folder": iff({"and": [{"equals": [f"@startsWith(toLower(concat({LN}, '    ')), 'line')", True]},
                                       {"equals": [f"@isInt(substring(concat({REM}, 'x'), 0, 1))", True]}]},   # "Line 7", "Line07", "Line 7a"; not "Line Archive"
       {"Add_line": {"runAfter": {}, "type": "AppendToArrayVariable", "inputs": {"name": "LinesV",
           "value": f"@addProperty(addProperty(json('{{}}'), 'line', {LID}), 'vs', items('Each_group')?['Name'])"}},
        "Each_file": {"runAfter": ok("Add_line"), "type": "Foreach", "foreach": "@coalesce(items('Each_line')?['Files'], json('[]'))",
          "runtimeConfiguration": {"concurrency": {"repetitions": 1}}, "actions": {
           "Is_changed_board": iff({"and": [
               {"equals": [f"@contains(toLower({F}?['Name']), 'production board')", True]},
               {"equals": [f"@startsWith({F}?['Name'], '~$')", False]},
               {"equals": [f"@or(endsWith(toLower({F}?['Name']), '.xlsm'), endsWith(toLower({F}?['Name']), '.xlsx'))", True]},
               {"equals": [f"@or(greaterOrEquals({F}?['TimeLastModified'], outputs('Since')), contains(coalesce(outputs('Existing')?['failed'], json('[]')), {F}?['ServerRelativeUrl']), "
                          f"not(contains(string(coalesce(outputs('Existing')?['lines'], json('[]'))), concat('\"line\":\"', {LID}, '\"'))))", True]}]},
             {"Add_file": {"runAfter": {}, "type": "AppendToArrayVariable", "inputs": {"name": "Files",
                "value": f"@addProperty(addProperty(addProperty(json('{{}}'), 'name', {F}?['Name']), 'url', {F}?['ServerRelativeUrl']), 'folder', {LN})"}}})}}})}}}}
A["Settings"] = compose("@" + "addProperty(addProperty(addProperty(addProperty(addProperty(addProperty(json('{}'), "
    f"'shift1Start', trim(first(split({par('craf4_t2x_shift1')}, '-')))), 'shift1End', trim(last(split({par('craf4_t2x_shift1')}, '-')))), "
    f"'shift2Start', if(empty(trim({par('craf4_t2x_shift2')})), '', trim(first(split({par('craf4_t2x_shift2')}, '-'))))), "
    f"'shift2End', if(empty(trim({par('craf4_t2x_shift2')})), '', trim(last(split({par('craf4_t2x_shift2')}, '-'))))), "
    f"'lunchMin', if(isInt(trim({par('craf4_t2x_lunchmin')})), int(trim({par('craf4_t2x_lunchmin')})), 0)), "
    f"'breakMin', if(isInt(trim({par('craf4_t2x_breakmin')})), int(trim({par('craf4_t2x_breakmin')})), 0))", ok("Run_start"))
A["GraphSite"] = compose("@concat('sites/', uriHost(outputs('Site')), ',', body('Get_board_folder')?['sharepointIds']?['siteId'], ',', body('Get_board_folder')?['sharepointIds']?['webId'])", ok(last))
A["DriveId"] = compose("@body('Get_board_folder')?['parentReference']?['driveId']", ok(last))

B = {}; it = "items('For_each_board')"
B["Line_folder"] = compose(f"@{it}?['folder']", {})
B["Get_board_item"] = http("GET",
    f"_api/v2.0/drive/root:/@{{replace(replace(replace(substring({it}?['url'], add(length(outputs('LibUrl')), 1), sub(length({it}?['url']), add(length(outputs('LibUrl')), 1))), '%', '%25'), ' ', '%20'), '#', '%23')}}?$select=id",
    after=ok("Line_folder"))
CF = "body('Get_copies_folder')?['id']"
CN = f"concat({it}?['folder'], ' - ', {it}?['name'])"
B["Copy_name"] = compose(f"@{CN}", ok("Get_board_item"))
# Classic SharePoint copy: synchronous (200 when the copy exists), needs only read access to the board.
# (The OneDrive-style /copy call is answered asynchronously and was rejected by the connector.)
B["Copy_dest"] = compose("@concat(outputs('LibUrl'), '/', outputs('Folder'), '/_Tier2/', outputs('Copies_name'), '/', outputs('Copy_name'))", ok("Copy_name"))
B["Copy_board"] = sp_http("POST", "_api/web/GetFileByServerRelativePath(decodedurl=@s)/copyTo(strNewUrl=@d,bOverWrite=true)?@s='@{encodeUriComponent(replace(items('For_each_board')?['url'], '''', ''''''))}'&@d='@{encodeUriComponent(replace(outputs('Copy_dest'), '''', ''''''))}'", after=ok("Copy_dest"))
# SharePoint answers the copy with 202 Accepted and finishes it in the background; the connector may report that as a failure
# even though the copy is made. So the wait loop decides: it runs either way and only a copy that never appears stops the board.
B["Wait_for_copy"] = {"runAfter": ok("Copy_board"), "type": "Until",
    "expression": "@and(equals(actions('Get_copy')?['status'], 'Succeeded'), greater(coalesce(body('Get_copy')?['size'], 0), 0))",
    "limit": {"count": 24, "timeout": "PT3M"},
    "actions": {
      "Get_copy": http("GET", "_api/v2.0/drive/items/@{" + CF + "}:/@{replace(replace(replace(outputs('Copy_name'), '%', '%25'), ' ', '%20'), '#', '%23')}?$select=id,size"),
      "Pause": {"runAfter": {"Get_copy": ["Failed", "Succeeded"]}, "type": "Wait", "inputs": {"interval": {"count": 5, "unit": "Second"}}}}}
# The wait loop ends quietly at its limit; this step fails (and names itself in Board notes) if the copy never appeared.
B["Copy_ready"] = compose("@if(equals(actions('Get_copy')?['status'], 'Succeeded'), body('Get_copy')?['id'], int('the copy did not finish within 3 minutes'))", ok("Wait_for_copy"))
B["Run_script"] = {"runAfter": ok("Copy_ready"), "type": "OpenApiConnection",
  "inputs": {"host": {"apiId": "/providers/Microsoft.PowerApps/apis/shared_excelonlinebusiness", "connectionName": "shared_excelonlinebusiness", "operationId": "RunScriptProdV2"},
    "parameters": {"source": "@outputs('GraphSite')", "drive": "@outputs('DriveId')", "file": "@outputs('Copy_ready')",
      "scriptSource": "@outputs('GraphSite')", "scriptDrive": "@outputs('DriveId')", "scriptId": "@body('Get_script_id')?['id']",
      "ScriptParameters": {"settings": "@{string(setProperty(setProperty(outputs('Settings'), 'lineOverride', outputs('Line_folder')), 'fileName', items('For_each_board')?['name']))}"}},
    "authentication": "@parameters('$authentication')"}, "runtimeConfiguration": {"staticResult": None} }
del B["Run_script"]["runtimeConfiguration"]
B["Result"] = compose("@json(body('Run_script')?['result'])", ok("Run_script"))
B["Board_line"] = compose("@coalesce(first(outputs('Result')?['lines']), '')", ok("Result"))
# drop this line's rows for the months this board covers, then add the board's rows
B["Keep_rows"] = query("@variables('Rows')",
    "@not(and(equals(string(item()?['l']), outputs('Board_line')), contains(outputs('Result')?['months'], substring(string(item()?['d']), 0, 7))))", ok("Board_line"))
B["Merged_rows"] = compose("@union(body('Keep_rows'), coalesce(outputs('Result')?['rows'], json('[]')))", ok("Keep_rows"))
B["Set_rows"] = setv("Rows", "@outputs('Merged_rows')", ok("Merged_rows"))
B["Merged_reasons"] = compose("@union(variables('Reasons'), coalesce(outputs('Result')?['reasons'], json('[]')))", ok("Set_rows"))
B["Set_reasons"] = setv("Reasons", "@outputs('Merged_reasons')", ok("Merged_reasons"))
B["Other_warnings"] = query("@variables('Warnings')", f"@and(not(empty(item()?['url'])), not(equals(item()?['url'], {it}?['url'])))", ok("Set_reasons"))
B["Merged_warnings"] = compose(f"@if(empty(outputs('Result')?['warnings']), body('Other_warnings'), union(body('Other_warnings'), createArray(addProperty(addProperty(addProperty(addProperty(json('{{}}'), 'file', {it}?['name']), 'url', {it}?['url']), 'line', outputs('Board_line')), 'items', outputs('Result')?['warnings']))))", ok("Other_warnings"))
B["Set_warnings"] = setv("Warnings", "@outputs('Merged_warnings')", ok("Merged_warnings"))
B["Note_read"] = {"runAfter": ok("Set_warnings"), "type": "AppendToArrayVariable", "inputs": {"name": "Read", "value": f"@{it}?['name']"}}
B["Note_read_url"] = {"runAfter": ok("Note_read"), "type": "AppendToArrayVariable", "inputs": {"name": "ReadUrls", "value": f"@{it}?['url']"}}
FS = "last(body('Failed_steps'))"   # the step that actually stopped the board (an earlier tolerated failure may precede it)
C = {}
C["Failed_steps"] = query("@result('Try_board')", "@equals(item()?['status'], 'Failed')", {})
C["Why"] = compose(f"@take(concat(coalesce({FS}?['name'], 'step'), ': ', string(coalesce({FS}?['outputs']?['body'], {FS}?['error'], 'unknown error'))), 220)", ok("Failed_steps"))
C["Other_warnings_f"] = query("@variables('Warnings')", f"@and(not(empty(item()?['url'])), not(equals(item()?['url'], {it}?['url'])))", ok("Why"))
C["Set_warnings_f"] = setv("Warnings", f"@union(body('Other_warnings_f'), createArray(addProperty(addProperty(addProperty(addProperty(json('{{}}'), 'file', {it}?['name']), 'url', {it}?['url']), 'line', " + LNUM.format(x=it + "?['folder']") + "), 'items', createArray(concat('Could not read this board - will retry next run. ', outputs('Why'))))))", ok("Other_warnings_f"))
C["Note_failed"] = {"runAfter": ok("Set_warnings_f"), "type": "AppendToArrayVariable", "inputs": {"name": "Failed", "value": f"@{it}?['url']"}}
A["For_each_board"] = {"runAfter": ok("Each_group", "Get_script_id", "Settings", "GraphSite", "DriveId", "Get_copies_folder"), "type": "Foreach", "foreach": "@variables('Files')",
    "actions": {"Try_board": {"runAfter": {}, "type": "Scope", "actions": B},
                "Board_failed": {"runAfter": {"Try_board": ["Failed", "TimedOut"]}, "type": "If",
                  # a tolerated failure (the copy's 202) can mark Try_board failed even though the board was read: then do nothing
                  "expression": {"equals": [f"@contains(variables('ReadUrls'), {it}?['url'])", False]}, "actions": C, "else": {"actions": {}}}},
    "runtimeConfiguration": {"concurrency": {"repetitions": 1}}}
A["Cutoff"] = compose("@formatDateTime(addDays(convertFromUtc(utcNow(), 'Eastern Standard Time'), -40), 'yyyy-MM-dd')", {"For_each_board": ["Succeeded", "Failed", "TimedOut"]})
A["Unread"] = query("@variables('Files')", "@and(not(contains(variables('ReadUrls'), item()?['url'])), not(contains(variables('Failed'), item()?['url'])))", ok("Cutoff"))
A["Unread_urls"] = {"runAfter": ok("Unread"), "type": "Select", "inputs": {"from": "@body('Unread')", "select": "@item()?['url']"}}
A["Tomorrow"] = compose("@formatDateTime(addDays(convertFromUtc(utcNow(), 'Eastern Standard Time'), 1), 'yyyy-MM-dd')", ok("Unread_urls"))
A["Recent_rows"] = query("@variables('Rows')", "@and(greaterOrEquals(string(item()?['d']), outputs('Cutoff')), lessOrEquals(string(item()?['d']), outputs('Tomorrow')))", ok("Tomorrow"))
A["Data"] = compose("@" + "addProperty(addProperty(addProperty(addProperty(addProperty(addProperty(addProperty(addProperty(addProperty(json('{}'), "
    "'version', 3), 'lastRun', outputs('Run_start')), 'boardsRead', variables('Read')), "
    "'shifts', outputs('Settings')), "
    "'lines', variables('LinesV')), 'reasons', variables('Reasons')), 'warnings', variables('Warnings')), 'rows', body('Recent_rows')), 'failed', union(variables('Failed'), body('Unread_urls')))",
    ok("Recent_rows"))
# Nothing changed -> no save: lastRun stays put, so the next run still looks back far enough. (Saves no new file version every 30 min.)
A["Anything_new"] = iff({"greater": ["@length(variables('Files'))", 0]},
    {"Save_data": http("PUT", f"_api/v2.0/drive/items/@{{{T2}}}:/tier2_data.json:/content", body="@{string(outputs('Data'))}")}, {}, after=ok("Data"))
sync = {"properties": {"connectionReferences": {
    "shared_sharepointonline": {"runtimeSource": "embedded", "connection": {"connectionReferenceLogicalName": "craf4_t2x_sharepoint"}, "api": {"name": "shared_sharepointonline"}},
    "shared_excelonlinebusiness": {"runtimeSource": "embedded", "connection": {"connectionReferenceLogicalName": "craf4_t2x_excelonline"}, "api": {"name": "shared_excelonlinebusiness"}}},
  "definition": {"$schema": "https://schema.management.azure.com/providers/Microsoft.Logic/schemas/2016-06-01/workflowdefinition.json#", "contentVersion": "1.0.0.0",
    "parameters": params(EV), "triggers": {"Every_30_minutes": {"type": "Recurrence", "recurrence": {"frequency": "Minute", "interval": 30, "timeZone": "Eastern Standard Time"},
      "runtimeConfiguration": {"concurrency": {"runs": 1}}}}, "actions": A, "outputs": {}}}, "schemaVersion": "1.0.0.0"}

# ======================= FLOW 2: APP DATA =======================
D = {}
D["Run_start"] = compose("@utcNow()", {})
last = resolve(D, ok("Run_start"))
def respond(name, data, settings, okv, err, after):
    props = {k: {"title": k, "type": "string", "x-ms-content-hint": "TEXT", "x-ms-dynamically-added": True} for k in ("data", "settings", "ok", "err")}
    return {"runAfter": after, "type": "Response", "kind": "PowerApp", "inputs": {"statusCode": 200,
        "body": {"data": data, "settings": settings, "ok": okv, "err": err}, "schema": {"type": "object", "properties": props, "additionalProperties": {}}}}
D["SitePath"] = compose("@uriPath(outputs('Site'))", ok("Site"))
D["LibUrl"] = compose("@concat(if(equals(outputs('SitePath'), '/'), '', outputs('SitePath')), '/Shared Documents')", ok("SitePath"))
D["Init_dtxt"] = init("DataTxt", "string", "", ok("Run_start"))
D["Init_stxt"] = init("SetTxt", "string", "", ok("Init_dtxt"))
D["Mode"] = iff({"equals": ["@toUpper(trim(triggerBody()?['text']))", "SAVE"]},
  {"Save_settings": http("PUT", f"_api/v2.0/drive/items/@{{{T2}}}:/tier2_settings.json:/content", body="@{triggerBody()?['text_1']}"),
   "Saved": respond("Saved", "", "@{triggerBody()?['text_1']}", "1", "", ok("Save_settings")),
   "Save_failed": respond("Save_failed", "", "", "0", "Could not save the settings file in _Tier2: @{outputs('Save_settings')?['statusCode']}", {"Save_settings": ["Failed", "TimedOut"]})},
  {"List_t2": http("GET", f"_api/v2.0/drive/items/@{{{T2}}}/children?$select=name&$top=999"),
   "Names": compose("@toLower(string(body('List_t2')?['value']))", ok("List_t2")),
   "Has_data": iff({"equals": ["@contains(outputs('Names'), '\"tier2_data.json\"')", True]},
       {"Get_data": get_t2_file("tier2_data.json"), "Keep_data": setv("DataTxt", "@{" + file_text("Get_data") + "}", ok("Get_data"))}, {}, after=ok("Names")),
   "Has_settings": iff({"equals": ["@contains(outputs('Names'), '\"tier2_settings.json\"')", True]},
       {"Get_settings": get_t2_file("tier2_settings.json"), "Keep_settings": setv("SetTxt", "@{" + file_text("Get_settings") + "}", ok("Get_settings"))}, {}, after=ok("Names")),
   "Send": respond("Send", "@{variables('DataTxt')}", "@{variables('SetTxt')}",
                   "@{if(empty(variables('DataTxt')), '0', '1')}",
                   "@{if(empty(variables('DataTxt')), 'No Tier 2 data yet. Run MDI XB - Sync Excel Boards once.', '')}",
                   any_("Has_data", "Has_settings"))},
  after=ok(last, "LibUrl", "Init_dtxt", "Init_stxt"))
D["Folder_failed"] = respond("Folder_failed", "", "", "0", "Could not open the board folder @{outputs('Folder')} on @{outputs('Site')}. Check the solution's site and folder settings.", {"Get_tier2_folder": ["Failed", "TimedOut", "Skipped"]})
appflow = {"properties": {"connectionReferences": {
    "shared_sharepointonline": {"runtimeSource": "embedded", "connection": {"connectionReferenceLogicalName": "craf4_t2x_sharepoint"}, "api": {"name": "shared_sharepointonline"}}},
  "definition": {"$schema": "https://schema.management.azure.com/providers/Microsoft.Logic/schemas/2016-06-01/workflowdefinition.json#", "contentVersion": "1.0.0.0",
    "parameters": params(["craf4_t2x_site", "craf4_t2x_folder"]),
    "triggers": {"manual": {"type": "Request", "kind": "PowerAppV2", "inputs": {"schema": {"type": "object", "properties": {
        "text": {"title": "Mode", "description": "GET or SAVE", "type": "string", "x-ms-content-hint": "TEXT", "x-ms-dynamically-added": True},
        "text_1": {"title": "Payload", "description": "Settings JSON (SAVE only)", "type": "string", "x-ms-content-hint": "TEXT", "x-ms-dynamically-added": True}},
        "required": ["text", "text_1"]}}}},
    "actions": D, "outputs": {}}}, "schemaVersion": "1.0.0.0"}
json.dump(sync, open(f"{OUTDIR}/sync.json", "w"), indent=1)
json.dump(appflow, open(f"{OUTDIR}/appdata.json", "w"), indent=1)
json.dump(EV, open(f"{OUTDIR}/ev.json", "w"), indent=1)
print("ok")
