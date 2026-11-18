"""Builds the 'MDI - Set Up Site' flow (clientdata JSON): creates/updates every MDI list on a SharePoint site with no console,
seeds config, sets permissions, and emails the SETUP CODE (MDI2:...) used to build the customer's app package.
Placeholders: __REF_SP__, __REF_O365__ (connection reference logical names)."""
import json, re, sys
PK = json.load(open(__import__("os").environ["MDI_DEPLOY"]+"/mdi_package.json"))
OUT = sys.argv[1] if len(sys.argv) > 1 else __import__("os").environ["MDI_TMP"]+"/setup_flow.json"

# ---------- compact package ----------
fmts, fidx = [], {}
def fk(v):
    if v not in fidx: fidx[v] = len(fmts); fmts.append(v)
    return fidx[v]
lists = []
for n, L in PK['schema'].items():
    fs = []
    for x in L['fields']:
        nm = re.search(r' Name="([^"]+)"', x).group(1)
        m = re.search(r' CustomFormatter="([^"]*)"', x)
        e = {"n": nm}
        if m: e["x"] = x.replace(m.group(0), ' CustomFormatter="§"'); e["k"] = fk(m.group(1))
        else: e["x"] = x
        fs.append(e)
    t = L['title']
    tb = {"Title": t['name'], "Required": bool(t.get('req')), "CustomFormatter": t.get('fmt', '') or ''}
    idx = [{"c": c.replace('*', ''), "b": ({"Indexed": True, "EnforceUniqueValues": True} if c.endswith('*') else {"Indexed": True})} for c in PK['indexes'].get(n, [])]
    lists.append({"n": n, "cb": {"Title": n, "BaseTemplate": L['base'], "Description": L.get('desc', '')}, "f": fs, "tb": tb,
                  "v": L['view'], "vb": {"ViewQuery": L.get('query', '') or '', "RowLimit": L.get('rows', 100)}, "i": idx})
pkg = {"lists": lists, "fmt": fmts, "names": [l['n'] for l in lists],
       "choice": [{"l": l, "f": f, "a": a} for l, fs in PK['choiceAdds'].items() for f, a in fs.items()],
       "seeds": [{"l": l, "rows": [{k: v for k, v in r.items() if v is not None} for r in rows]} for l, rows in PK['seed'].items()],
       "ensure": [{"l": l, "t": r['Title'].replace("'", "''"), "r": r} for l, rows in PK['ensureRows'].items() for r in rows],
       "perms": [{"l": l, "g": g} for g, ls in PK['perms'].items() for l in ls]}

# ---------- action helpers ----------
SPH = {"apiId": "/providers/Microsoft.PowerApps/apis/shared_sharepointonline", "connectionName": "shared_sharepointonline", "operationId": "HttpRequest"}
NM = {"Accept": "application/json;odata=nometadata", "Content-Type": "application/json;odata=nometadata"}
MERGE = {**NM, "X-HTTP-Method": "MERGE", "IF-MATCH": "*"}
VERB = {"Accept": "application/json;odata=verbose", "Content-Type": "application/json;odata=verbose"}
ALL = ["Succeeded", "Failed", "Skipped", "TimedOut"]
def sp(method, uri, body=None, headers=None, after=None):
    p = {"dataset": "@variables('Site')", "parameters/method": method, "parameters/uri": uri, "parameters/headers": headers or NM}
    if body is not None: p["parameters/body"] = body
    return {"runAfter": after or {}, "type": "OpenApiConnection", "inputs": {"host": SPH, "parameters": p, "authentication": "@parameters('$authentication')"}}
def tol(prev): return {prev: ALL}
def chain(acts):
    """ordered list of (name, action) → dict with tolerant runAfter chaining (first keeps its runAfter)"""
    d, prev = {}, None
    for n, a in acts:
        if prev is not None and not a.get("runAfter"): a["runAfter"] = tol(prev)
        d[n] = a; prev = n
    return d
def foreach(items, actions, after=None, conc=1):
    return {"type": "Foreach", "foreach": items, "actions": actions, "runAfter": after or {}, "runtimeConfiguration": {"concurrency": {"repetitions": conc}}}
def cond(expr, yes, no=None, after=None):
    return {"type": "If", "expression": expr, "actions": yes, "else": {"actions": no or {}}, "runAfter": after or {}}
def compose(v, after=None): return {"type": "Compose", "inputs": v, "runAfter": after or {}}
L = "items('Each_list')"
LU = "_api/web/lists/getbytitle('@{" + L + "?['n']}')"

each_list = chain([
    ("Find_list", sp("GET", "_api/web/lists?$select=Id&$filter=Title eq '@{" + L + "?['n']}'")),
    ("If_new_list", cond({"equals": ["@length(body('Find_list')?['value'])", 0]},
                         {"Create_list": sp("POST", "_api/web/lists", "@{string(" + L + "?['cb'])}")})),
    ("Get_fields", sp("GET", LU + "/fields?$select=InternalName,Title&$filter=Hidden eq false&$top=1000")),
    ("Sel_internal", {"type": "Select", "inputs": {"from": "@body('Get_fields')?['value']", "select": "@item()?['InternalName']"}}),
    ("Sel_title", {"type": "Select", "inputs": {"from": "@body('Get_fields')?['value']", "select": "@item()?['Title']"}}),
    ("Have", compose("@union(body('Sel_internal'), body('Sel_title'))")),
    ("Each_field", foreach("@" + L + "?['f']", {
        "If_missing": cond({"not": {"contains": ["@outputs('Have')", "@items('Each_field')?['n']"]}},
            {"Add_field": sp("POST", LU + "/fields/createfieldasxml",
                "@{string(addProperty(json('{}'), 'parameters', addProperty(addProperty(json('{}'), 'SchemaXml', replace(items('Each_field')?['x'], '§', outputs('PKG')?['fmt'][coalesce(items('Each_field')?['k'], 0)])), 'Options', 8)))}")})})),
    ("Set_title", sp("POST", LU + "/fields/getbyinternalnameortitle('Title')", "@{string(" + L + "?['tb'])}", MERGE)),
    ("Each_index", foreach("@" + L + "?['i']", {
        "Index": sp("POST", LU + "/fields/getbyinternalnameortitle('@{items('Each_index')?['c']}')", "@{string(items('Each_index')?['b'])}", MERGE)})),
    ("Get_view", sp("GET", LU + "/defaultview?$select=Id")),
    ("Clear_view", sp("POST", LU + "/views('@{body('Get_view')?['Id']}')/viewfields/removeallviewfields")),
    ("Each_viewfield", foreach("@" + L + "?['v']", {
        "Add_viewfield": sp("POST", LU + "/views('@{body('Get_view')?['Id']}')/viewfields/addviewfield('@{items('Each_viewfield')}')")})),
    ("Set_view", sp("POST", LU + "/views('@{body('Get_view')?['Id']}')", "@{string(" + L + "?['vb'])}", MERGE)),
])
C = "items('Each_choice')"
each_choice = chain([
    ("Get_choice", sp("GET", "_api/web/lists/getbytitle('@{" + C + "?['l']}')/fields/getbyinternalnameortitle('@{" + C + "?['f']}')?$select=Id,Choices")),
    ("Merge_choice", sp("POST", "_api/web/lists/getbytitle('@{" + C + "?['l']}')/fields('@{body('Get_choice')?['Id']}')",
        "@{string(addProperty(json('{\"__metadata\":{\"type\":\"SP.FieldChoice\"}}'), 'Choices', addProperty(json('{\"__metadata\":{\"type\":\"Collection(Edm.String)\"}}'), 'results', union(body('Get_choice')?['Choices'], " + C + "?['a']))))}",
        {**VERB, "X-HTTP-Method": "MERGE", "IF-MATCH": "*"})),
])
S = "items('Each_seed')"
each_seed = chain([
    ("Get_count", sp("GET", "_api/web/lists/getbytitle('@{" + S + "?['l']}')?$select=ItemCount")),
    ("If_empty", cond({"equals": ["@body('Get_count')?['ItemCount']", 0]},
        {"Each_row": foreach("@" + S + "?['rows']", {"Add_row": sp("POST", "_api/web/lists/getbytitle('@{" + S + "?['l']}')/items", "@{string(item())}")}, conc=5)})),
])
E = "items('Each_ensure')"
each_ensure = chain([
    ("Find_row", sp("GET", "_api/web/lists/getbytitle('@{" + E + "?['l']}')/items?$select=ID&$filter=Title eq '@{" + E + "?['t']}'")),
    ("If_no_row", cond({"equals": ["@length(body('Find_row')?['value'])", 0]},
        {"Add_config_row": sp("POST", "_api/web/lists/getbytitle('@{" + E + "?['l']}')/items", "@{string(" + E + "?['r'])}")})),
])
perm = chain([
    ("Get_role", sp("GET", "_api/web/roledefinitions?$select=Id&$filter=Name eq 'Contribute - no delete'")),
    ("If_no_role", cond({"equals": ["@length(body('Get_role')?['value'])", 0]}, chain([
        ("Get_contribute", sp("GET", "_api/web/roledefinitions/getbyname('Contribute')?$select=BasePermissions")),
        ("Create_role", sp("POST", "_api/web/roledefinitions",
            "{\"__metadata\":{\"type\":\"SP.RoleDefinition\"},\"Name\":\"Contribute - no delete\",\"Description\":\"Add and edit list items; cannot delete items or versions.\",\"Order\":200,"
            "\"BasePermissions\":{\"__metadata\":{\"type\":\"SP.BasePermissions\"},\"High\":\"@{body('Get_contribute')?['BasePermissions']?['High']}\",\"Low\":\"@{sub(int(body('Get_contribute')?['BasePermissions']?['Low']), 136)}\"}}",
            VERB)),
    ]))),
    ("Get_role2", sp("GET", "_api/web/roledefinitions?$select=Id&$filter=Name eq 'Contribute - no delete'")),
    ("Get_group", sp("GET", "_api/web/sitegroups?$select=Id&$filter=Title eq 'MDI Config Editors'")),
    ("If_no_group", cond({"equals": ["@length(body('Get_group')?['value'])", 0]},
        {"Create_group": sp("POST", "_api/web/sitegroups", "{\"Title\":\"MDI Config Editors\",\"Description\":\"Can edit MDI config lists.\"}")})),
    ("Get_group2", sp("GET", "_api/web/sitegroups?$select=Id&$filter=Title eq 'MDI Config Editors'")),
    ("Get_owners", sp("GET", "_api/web/AssociatedOwnerGroup?$select=Id")),
    ("Get_members", sp("GET", "_api/web/AssociatedMemberGroup?$select=Id")),
    ("Get_visitors", sp("GET", "_api/web/AssociatedVisitorGroup?$select=Id")),
    ("Get_full", sp("GET", "_api/web/roledefinitions/getbyname('Full Control')?$select=Id")),
    ("Get_contrib_id", sp("GET", "_api/web/roledefinitions/getbyname('Contribute')?$select=Id")),
    ("Get_read", sp("GET", "_api/web/roledefinitions/getbyname('Read')?$select=Id")),
])
O, M_, V_, G_ = "@body('Get_owners')?['Id']", "@body('Get_members')?['Id']", "@body('Get_visitors')?['Id']", "@first(body('Get_group2')?['value'])?['Id']"
FULL, CON, RD, NOD = "@body('Get_full')?['Id']", "@body('Get_contrib_id')?['Id']", "@body('Get_read')?['Id']", "@first(body('Get_role2')?['value'])?['Id']"
perm["Plan"] = compose({"config": [[O, FULL], [G_, CON], [M_, RD], [V_, RD]], "data": [[O, FULL], [G_, NOD], [M_, NOD], [V_, RD]], "log": [[O, FULL], [G_, RD], [M_, RD], [V_, RD]]},
                       tol("Get_read"))
P = "items('Each_perm')"
perm["Each_perm"] = foreach("@outputs('PKG')?['perms']", chain([
    ("Break", sp("POST", "_api/web/lists/getbytitle('@{" + P + "?['l']}')/breakroleinheritance(copyRoleAssignments=false,clearSubscopes=true)")),
    ("Each_grant", foreach("@outputs('Plan')?[" + P + "?['g']]", {
        "Grant": sp("POST", "_api/web/lists/getbytitle('@{" + P + "?['l']}')/roleassignments/addroleassignment(principalid=@{items('Each_grant')[0]},roledefid=@{items('Each_grant')[1]})")})),
]), tol("Plan"))

code = chain([
    ("Find_site_row", sp("GET", "_api/web/lists/getbytitle('MDI_Config')/items?$select=ID&$filter=Title eq 'Site_URL_Live'")),
    ("If_no_site_row", cond({"equals": ["@length(body('Find_site_row')?['value'])", 0]},
        {"Add_site_row": sp("POST", "_api/web/lists/getbytitle('MDI_Config')/items", "{\"Title\":\"Site_URL_Live\",\"Kind\":\"Site\",\"SettingValue\":\"@{variables('Site')}\",\"Notes\":\"Set by MDI - Set Up Site\"}")})),
    ("Get_lists", sp("GET", "_api/web/lists?$select=Id,Title&$filter=Hidden eq false&$top=500")),
    ("Our_lists", {"type": "Query", "inputs": {"from": "@body('Get_lists')?['value']", "where": "@contains(outputs('PKG')?['names'], item()?['Title'])"}}),
    ("Ids", {"type": "Select", "inputs": {"from": "@body('Our_lists')", "select": {"n": "@item()?['Title']", "id": "@item()?['Id']"}}}),
    ("Code", compose("MDI2:@{base64(concat('{\"site\":\"', variables('Site'), '\",\"lists\":', string(body('Ids')), '}'))}")),
    ("Find_code_row", sp("GET", "_api/web/lists/getbytitle('MDI_Config')/items?$select=ID&$filter=Title eq 'Setup_Code'")),
    ("If_no_code_row", cond({"equals": ["@length(body('Find_code_row')?['value'])", 0]},
        {"Add_code_row": sp("POST", "_api/web/lists/getbytitle('MDI_Config')/items", "{\"Title\":\"Setup_Code\",\"Kind\":\"Other\",\"SettingValue\":\"see Notes\",\"Notes\":\"@{outputs('Code')}\"}")},
        {"Update_code_row": sp("POST", "_api/web/lists/getbytitle('MDI_Config')/items(@{first(body('Find_code_row')?['value'])?['ID']})", "{\"Notes\":\"@{outputs('Code')}\"}", MERGE)})),
    ("Email_code", {"runAfter": {}, "type": "OpenApiConnection", "inputs": {
        "host": {"apiId": "/providers/Microsoft.PowerApps/apis/shared_office365", "connectionName": "shared_office365", "operationId": "SendEmailV2"},
        "parameters": {"emailMessage/To": "@{triggerOutputs()?['headers']?['x-ms-user-email']}",
                       "emailMessage/Subject": "MDI site setup finished: @{variables('Site')}",
                       "emailMessage/Body": "<p>The MDI lists are set up on <b>@{variables('Site')}</b> (@{length(body('Ids'))} of @{length(outputs('PKG')?['names'])} lists found).</p>"
                                            "<p><b>Next:</b> forward this email to your MDI provider. They send back the app package built for this site.</p>"
                                            "<p>SETUP CODE (also saved in the MDI_Config list, row Setup_Code):</p><p style=\"font-family:Consolas,monospace;font-size:10px;word-break:break-all\">@{outputs('Code')}</p>",
                       "emailMessage/Importance": "Normal"},
        "authentication": "@parameters('$authentication')"}}),
])

actions = {
    "Site": {"type": "InitializeVariable", "inputs": {"variables": [{"name": "Site", "type": "string",
             "value": "@{if(endsWith(trim(triggerBody()?['text']), '/'), take(trim(triggerBody()?['text']), sub(length(trim(triggerBody()?['text'])), 1)), trim(triggerBody()?['text']))}"}]}, "runAfter": {}},
    "PKG": compose(pkg, {"Site": ["Succeeded"]}),
    "Each_list": foreach("@outputs('PKG')?['lists']", each_list, {"PKG": ["Succeeded"]}),
    "Each_choice": foreach("@outputs('PKG')?['choice']", each_choice, tol("Each_list")),
    "Each_seed": foreach("@outputs('PKG')?['seeds']", each_seed, tol("Each_choice")),
    "Each_ensure": foreach("@outputs('PKG')?['ensure']", each_ensure, tol("Each_seed")),
    "Permissions": {"type": "Scope", "actions": perm, "runAfter": tol("Each_ensure")},
    "Setup_code": {"type": "Scope", "actions": code, "runAfter": tol("Permissions")},
}
defn = {"$schema": "https://schema.management.azure.com/providers/Microsoft.Logic/schemas/2016-06-01/workflowdefinition.json#", "contentVersion": "1.0.0.0",
        "parameters": {"$connections": {"defaultValue": {}, "type": "Object"}, "$authentication": {"defaultValue": {}, "type": "SecureObject"}},
        "triggers": {"manual": {"type": "Request", "kind": "Button", "inputs": {"schema": {"type": "object", "properties": {
            "text": {"title": "SharePoint site address", "type": "string", "x-ms-dynamically-added": True, "description": "e.g. https://contoso.sharepoint.com/sites/PlantMDI", "x-ms-content-hint": "TEXT"}},
            "required": ["text"]}}}},
        "actions": actions, "outputs": {}}
flow = {"properties": {"connectionReferences": {
    "shared_sharepointonline": {"runtimeSource": "invoker", "connection": {"connectionReferenceLogicalName": "__REF_SP__"}, "api": {"name": "shared_sharepointonline"}},
    "shared_office365": {"runtimeSource": "invoker", "connection": {"connectionReferenceLogicalName": "__REF_O365__"}, "api": {"name": "shared_office365"}}},
    "definition": defn}, "schemaVersion": "1.0.0.0"}
json.dump(flow, open(OUT, 'w'), separators=(',', ':'), ensure_ascii=False)
s = json.dumps(flow, separators=(',', ':'), ensure_ascii=False)
print("bytes", len(s.encode()), "pkg", len(json.dumps(pkg, separators=(',', ':'), ensure_ascii=False)))
