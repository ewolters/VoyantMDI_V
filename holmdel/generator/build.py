"""Managed solution: MDI XB - Sync Excel Boards + MDI XB - Tier 2 Data. No lists, no app (the app is pasted from YAML in Studio)."""
import zipfile, json, re, uuid, sys
SETUP_ZIP, D, OUT, VERSION = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
APP_ZIP = sys.argv[5] if len(sys.argv) > 5 else None  # unmanaged export holding the compiled Tier 2 app
src = zipfile.ZipFile(SETUP_ZIP)
rd = lambda n: src.read(n).decode("utf-8-sig").replace("\r\n", "\n")
cust, sol = rd("customizations.xml"), rd("solution.xml")
EV = json.load(open(f"{D}/ev.json"))
# Holmdel's real values as defaults, so import never stops to ask (current values in the environment still win).
DEF = {"craf4_t2x_site": "https://veepak1.sharepoint.com/holmdel", "craf4_t2x_folder": "Production",
       "craf4_t2x_shift1": "07:00-15:15", "craf4_t2x_shift2": "15:15-23:30", "craf4_t2x_lunchmin": "30", "craf4_t2x_breakmin": "15"}
FLOWS = [("sync", "MDI XB - Sync Excel Boards", "Every 30 min: reads changed Tier 1 Production Boards (any month) under the board folder and writes Production/_Tier2/tier2_data.json for Tier 2.", "SyncExcelBoards", f"{D}/sync.json"),
         ("appdata", "MDI XB - Tier 2 Data", "Called by the Tier 2 app: GET returns the Tier 2 data and settings; SAVE stores the target colors.", "Tier2Data", f"{D}/appdata.json")]
def wf_xml(wid, wfile, name, desc):
    return f'''    <Workflow WorkflowId="{{{wid}}}" Name="{name}" Description="{desc}">
      <JsonFileName>/{wfile}</JsonFileName>
      <Type>1</Type>
      <Subprocess>0</Subprocess>
      <Category>5</Category>
      <Mode>0</Mode>
      <Scope>4</Scope>
      <OnDemand>0</OnDemand>
      <TriggerOnCreate>0</TriggerOnCreate>
      <TriggerOnDelete>0</TriggerOnDelete>
      <AsyncAutodelete>0</AsyncAutodelete>
      <SyncWorkflowLogOnFailure>0</SyncWorkflowLogOnFailure>
      <StateCode>1</StateCode>
      <StatusCode>2</StatusCode>
      <RunAs>1</RunAs>
      <IsTransacted>1</IsTransacted>
      <IntroducedVersion>1.0.0.0</IntroducedVersion>
      <IsCustomizable>1</IsCustomizable>
      <BusinessProcessType>0</BusinessProcessType>
      <IsCustomProcessingStepAllowedForOtherPublishers>1</IsCustomProcessingStepAllowedForOtherPublishers>
      <ModernFlowType>0</ModernFlowType>
      <PrimaryEntity>none</PrimaryEntity>
      <LocalizedNames>
        <LocalizedName languagecode="1033" description="{name}" />
      </LocalizedNames>
      <Descriptions>
        <Description languagecode="1033" description="{desc}" />
      </Descriptions>
    </Workflow>
'''
def cref(logical, disp, api, desc):
    return f'''    <connectionreference connectionreferencelogicalname="{logical}">
      <connectionreferencedisplayname>{disp}</connectionreferencedisplayname>
      <connectorid>/providers/Microsoft.PowerApps/apis/{api}</connectorid>
      <description>{desc}</description>
      <iscustomizable>1</iscustomizable>
      <promptingbehavior>0</promptingbehavior>
      <statecode>0</statecode>
      <statuscode>1</statuscode>
    </connectionreference>
'''
files, wfs, roots = {}, "", []
APPXML, ctypes = "", src.read("[Content_Types].xml")
if APP_ZIP:
    az = zipfile.ZipFile(APP_ZIP)
    ac = az.read("customizations.xml").decode("utf-8-sig").replace("\r\n", "\n")
    APPXML = "  " + ac[ac.find("<CanvasApps>"):ac.find("</CanvasApps>") + len("</CanvasApps>")] + "\n"
    for n in az.namelist():
        if n.startswith("CanvasApps/"): files[n] = az.read(n)
    roots += re.findall(r'<RootComponent type="300"[^>]*/>', az.read("solution.xml").decode("utf-8-sig"))
    ctypes = az.read("[Content_Types].xml")
for key, name, desc, slug, path in FLOWS:
    wid = str(uuid.uuid5(uuid.NAMESPACE_URL, "svend/mdi/t2x/" + key))
    wfile = f"Workflows/MDIXB-{slug}-{wid.upper()}.json"
    files[wfile] = open(path).read().encode("utf-8")
    wfs += wf_xml(wid, wfile, name, desc)
    roots.append(f'<RootComponent type="29" id="{{{wid}}}" behavior="0" />')
crefs = (cref("craf4_t2x_sharepoint", "Tier 2 XB SharePoint", "shared_sharepointonline", "Reads the Tier 1 boards; writes Production/_Tier2")
         + cref("craf4_t2x_excelonline", "Tier 2 XB Excel Online (Business)", "shared_excelonlinebusiness", "Runs the board-reading Office Script"))
head = cust[:cust.find("<Entities>")]
c2 = (head + "<Entities></Entities>\n  <Roles></Roles>\n  <Workflows>\n" + wfs + "  </Workflows>\n  <FieldSecurityProfiles></FieldSecurityProfiles>\n  <Templates />\n  <EntityMaps />\n"
      "  <EntityRelationships />\n  <OrganizationSettings />\n  <optionsets />\n  <CustomControls />\n  <EntityDataProviders />\n" + APPXML + "  <connectionreferences>\n" + crefs
      + "  </connectionreferences>\n" + cust[cust.find("  <Languages>"):])
for k, disp in EV.items():
    files[f"environmentvariabledefinitions/{k}/environmentvariabledefinition.xml"] = f'''<environmentvariabledefinition schemaname="{k}">
  <displayname default="{disp}">
    <label description="{disp}" languagecode="1033" />
  </displayname>
  <defaultvalue>{DEF[k]}</defaultvalue>
  <introducedversion>1.0.0.0</introducedversion>
  <iscustomizable>1</iscustomizable>
  <isrequired>{0 if k == 'craf4_t2x_shift2' else 1}</isrequired>
  <secretstore>0</secretstore>
  <type>100000000</type>
</environmentvariabledefinition>'''.encode("utf-8")
    roots.append(f'<RootComponent type="380" schemaName="{k}" behavior="0" />')
s = re.sub(r"<UniqueName>MDISetup</UniqueName>", "<UniqueName>MDITier2ExcelBoardsLite</UniqueName>", sol, count=1)
s = re.sub(r'(<LocalizedNames>\s*<LocalizedName description=")[^"]*(" languagecode="1033" />)', r"\1MDI Tier 2 - Excel boards (no lists)\2", s, count=1)
s = re.sub(r"<Version>[^<]*</Version>", f"<Version>{VERSION}</Version>", s, count=1)
s = re.sub(r"<RootComponents>.*?</RootComponents>", "<RootComponents>\n      " + "\n      ".join(roots) + "\n    </RootComponents>", s, flags=re.S)
s = re.sub(r"<MissingDependencies>.*?</MissingDependencies>", "<MissingDependencies />", s, flags=re.S)
with zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED) as z:
    z.writestr("[Content_Types].xml", ctypes)
    z.writestr("solution.xml", s.replace("\n", "\r\n").encode("utf-8"))
    z.writestr("customizations.xml", c2.replace("\n", "\r\n").encode("utf-8"))
    for n, b in files.items(): z.writestr(n, b)
print("built", OUT, len(files), "files")
