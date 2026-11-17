"""Writes deploy/tools/install_flows.js.txt: a browser-console installer that creates the MDI solution,
connection references and the four flows in any Power Platform environment, pointed at the customer's site."""
import json, sys, importlib.util

spec = importlib.util.spec_from_file_location("flows", __import__("os").environ["MDI_GEN"]+"/flows.py")
F = importlib.util.module_from_spec(spec); spec.loader.exec_module(F)

LISTS = ["People", "MDI_Config", "HxH_Shift", "HxH_Hourly", "Newspaper", "Lines",
         "Escalation_Contacts", "Escalation_Log", "TS_Photos"]
OPTIONAL = ["SAF_Results"]          # Frontier (safety) module; flows that need it are skipped if the site doesn't have it
F.SITE = "__SITE__"
for k in LISTS + OPTIONAL:
    F.L[k] = f"__L_{k}__"
F.SP_REF, F.TEAMS_REF, F.O365_REF = "__REF_SP__", "__REF_TEAMS__", "__REF_O365__"

FLOWS = [
    ("MDI - Upload Photo", "Saves photos from the MDI apps into the TS_Photos library.", F.flow02()),
    ("HxH - Downtime Escalation", "Teams escalation when cumulative downtime for a reason crosses 60/120/240 min in a shift.", F.flow01()),
    ("MDI - Sync Permissions", "Keeps SharePoint group membership in step with the People list switches (Active, CanEditConfig, MDIAdmin).", F.flow03()),
    ("MDI - Nightly Board Check", "6:30 AM Central: raises a NEWSPAPER action for incomplete hour-by-hour boards and emails the digest to Alert_Email.", F.flow04()),
    ("MDI - Frontier Critical Alert", "Teams alert to the safety coordinator(s) and the zone owner the moment a Frontier audit records a Critical finding.", F.flow05()),
]
NEEDS = {"MDI - Frontier Critical Alert": ["SAF_Results"]}
for _, _, d in FLOWS:
    s = json.dumps(d)
    assert "verxted" not in s and "craf4" not in s, "sandbox value leaked"

TEMPLATES = json.dumps([{"name": n, "desc": ds, "needs": NEEDS.get(n, []), "clientdata": json.dumps(d, separators=(",", ":"))} for n, ds, d in FLOWS])

JS = r"""/* MDI FLOW INSTALLER: creates the MDI solution, its connection references and all the MDI flows
   in YOUR Power Platform environment, already pointed at YOUR SharePoint site.

   HOW TO RUN (about 2 minutes)
   1. Run the list setup first (provision_mdi.js.txt). At the end it copies a SETUP CODE to your clipboard
      and also prints it in the console (it starts with MDI1:).
   2. Find your environment's address: make.powerapps.com → gear icon (top right) → Session details →
      "Instance url" (looks like https://orgXXXXXXXX.crm.dynamics.com). Open that address in Edge and sign in.
   3. On that page press F12 → Console. Paste this whole file → Enter. Paste the SETUP CODE when asked → OK.
   4. When it prints DONE, follow the three NEXT STEPS it prints (connect, then turn the flows on).

   Safe to run again: anything that already exists is kept; flows that differ from this version are UPDATED in place. Nothing is deleted.
*/
(async () => {
  const SOLUTION = 'MDI';            // solution unique name
  const NAME_SUFFIX = '';            // leave empty (only used for testing)
  const TEMPLATES = __TEMPLATES__;
  const LISTS = __LISTS__, OPTIONAL = __OPTIONAL__;

  const log = (...a) => console.log('%c[MDI flows]', 'color:#00B2A9;font-weight:bold', ...a);
  const fail = m => { console.error('[MDI flows] STOPPED: ' + m); alert('MDI flow installer stopped:\n\n' + m); };
  if (!/\.dynamics\.com$/i.test(location.hostname)) return fail('Run this on your environment page (https://org….crm.dynamics.com), not on ' + location.hostname + '. See step 2 at the top of the file.');
  const API = location.origin + '/api/data/v9.2/';
  const H = { Accept: 'application/json', 'Content-Type': 'application/json', 'OData-MaxVersion': '4.0', 'OData-Version': '4.0' };
  const get = async u => { const r = await fetch(API + u, { headers: H }); if (!r.ok) throw new Error(u.split('?')[0] + ' ' + r.status + ' ' + (await r.text()).slice(0, 300)); return r.json(); };
  const post = async (u, body, sol) => { const r = await fetch(API + u, { method: 'POST', headers: { ...H, ...(sol ? { 'MSCRM.SolutionUniqueName': sol } : {}), Prefer: 'return=representation' }, body: JSON.stringify(body) });
    if (!r.ok) throw new Error(u + ' ' + r.status + ' ' + (await r.text()).slice(0, 400)); return r.status === 204 ? {} : r.json(); };
  const q = s => s.replace(/'/g, "''");

  try { await get('WhoAmI'); } catch (e) { return fail('Not signed in to this environment. Reload the page, sign in, then paste again.\n' + e.message); }

  // 1. setup code from the list setup
  const raw = (window.prompt('Paste the SETUP CODE from the list setup (starts with MDI1:)') || '').trim();
  let S; try { if (!raw.startsWith('MDI1:')) throw 0; S = JSON.parse(atob(raw.slice(5))); } catch (e) { return fail('That is not a valid SETUP CODE. Re-run the list setup and copy the line that starts with MDI1:'); }
  const miss = LISTS.filter(k => !/^[0-9a-f-]{36}$/i.test((S.lists || {})[k] || ''));
  if (!/^https:\/\/[^/]+\.sharepoint\.com\/(sites|teams)\/[^/]+$/i.test(S.site || '') || miss.length) return fail('SETUP CODE incomplete. Missing: ' + (miss.join(', ') || 'site URL') + '. Re-run the list setup.');
  log('Site:', S.site);

  // 2. publisher + solution
  let sol = (await get(`solutions?$select=solutionid,uniquename&$expand=publisherid($select=customizationprefix,uniquename)&$filter=uniquename eq '${SOLUTION}'`)).value[0];
  if (!sol) {
    let pub = (await get("publishers?$select=publisherid,customizationprefix&$filter=uniquename eq 'SVEND'")).value[0];
    if (!pub) { pub = await post('publishers', { uniquename: 'SVEND', friendlyname: 'SVEND', customizationprefix: 'svend', customizationoptionvalueprefix: 41730, description: 'SVEND MDI' }); log('created publisher SVEND'); }
    await post('solutions', { uniquename: SOLUTION, friendlyname: SOLUTION, version: '1.0.0.0', 'publisherid@odata.bind': `/publishers(${pub.publisherid})`, description: 'Virtual MDI: flows, connection references and apps' });
    sol = (await get(`solutions?$select=solutionid,uniquename&$expand=publisherid($select=customizationprefix,uniquename)&$filter=uniquename eq '${SOLUTION}'`)).value[0];
    log('created solution', SOLUTION);
  } else log('solution', SOLUTION, 'already exists');
  const P = sol.publisherid.customizationprefix;

  // 3. connection references (one per connector; you pick the connection afterwards)
  const REFS = [['__REF_SP__', 'shared_sharepointonline', 'SharePoint'], ['__REF_TEAMS__', 'shared_teams', 'Microsoft Teams'], ['__REF_O365__', 'shared_office365', 'Office 365 Outlook']];
  const refName = {};
  for (const [ph, api, label] of REFS) {
    const ln = `${P}_mdi_${api.replace('shared_', '')}`; refName[ph] = ln;
    const ex = (await get(`connectionreferences?$select=connectionreferenceid&$filter=connectionreferencelogicalname eq '${ln}'`)).value[0];
    if (ex) { log('connection slot exists:', 'MDI ' + label); continue; }
    await post('connectionreferences', { connectionreferencelogicalname: ln, connectionreferencedisplayname: 'MDI ' + label,
      connectorid: '/providers/Microsoft.PowerApps/apis/' + api, description: 'Used by the MDI flows' }, SOLUTION);
    log('created connection slot:', 'MDI ' + label);
  }

  // 4. flows
  const fill = t => {
    let s = t.split('__SITE__').join(S.site);
    for (const k of LISTS.concat(OPTIONAL)) if (S.lists[k]) s = s.split(`__L_${k}__`).join(S.lists[k]);
    for (const ph in refName) s = s.split(ph).join(refName[ph]);
    if (/__[A-Za-z_]+__/.test(s)) throw new Error("unfilled placeholder " + s.match(/__[A-Za-z_]+__/)[0]);
    JSON.parse(s); return s;
  };
  const made = [], skipped = [], updated = [];
  for (const t of TEMPLATES) {
    const name = t.name + NAME_SUFFIX;
    const lack = (t.needs || []).filter(k => !S.lists[k]);
    if (lack.length) { skipped.push(name); log('skipped (site has no ' + lack.join(', ') + ' list; re-run the list setup, then this):', name); continue; }
    const ex = (await get(`workflows?$select=workflowid,clientdata&$filter=category eq 5 and name eq '${q(name)}'`)).value[0];
    if (ex) {
      const want = fill(t.clientdata);
      let same = false; try { same = JSON.stringify(JSON.parse(ex.clientdata).properties.definition) === JSON.stringify(JSON.parse(want).properties.definition); } catch (e) {}
      if (same) { skipped.push(name); log('flow up to date:', name); continue; }
      const r = await fetch(API + `workflows(${ex.workflowid})`, { method: 'PATCH', headers: { ...H, 'If-Match': '*' }, body: JSON.stringify({ clientdata: want }) });
      if (!r.ok) throw new Error('update ' + name + ' ' + r.status + ' ' + (await r.text()).slice(0, 300));
      updated.push(name); log('flow UPDATED to the latest version:', name); continue;
    }
    await post('workflows', { category: 5, type: 1, primaryentity: 'none', name, description: t.desc, clientdata: fill(t.clientdata) }, SOLUTION);
    made.push(name); log('created flow (Off):', name);
  }

  const envId = (await get('RetrieveCurrentOrganization(AccessType=@p)?@p=Microsoft.Dynamics.CRM.EndpointAccessType\'Default\'').catch(() => ({}))).Detail?.EnvironmentId;
  const link = envId ? `https://make.powerautomate.com/environments/${envId}/solutions/${sol.solutionid}` : 'make.powerautomate.com → Solutions → ' + SOLUTION;
  log(`DONE. Created ${made.length} flow(s), updated ${updated.length}, ${skipped.length} already up to date.`);
  if (updated.length) console.log('%cUPDATED: ' + updated.join(', ') + '. In Cloud flows, turn each of these Off and On once. Then in every app that uses an updated flow: Power Automate pane → ⋯ next to the flow → Remove → + Add flow (so the app picks up the new inputs).', 'font-weight:bold;color:#CF222E');
  console.log('%cNEXT STEPS', 'font-weight:bold;font-size:14px',
    `\n1. Open the solution: ${link}` +
    `\n2. Left menu → Connection references. Open each of "MDI SharePoint", "MDI Microsoft Teams", "MDI Office 365 Outlook":` +
    `\n   pick your connection in the Connection box (or "+ New connection" and sign in) → Save.` +
    `\n3. Left menu → Cloud flows. Select each MDI flow → Turn on.` +
    `\n   Then fill MDI_Config → Alert_Email on the SharePoint site if you haven't.`);
})().catch(e => { console.error('[MDI flows] STOPPED:', e.message); alert('MDI flow installer stopped:\n\n' + e.message + '\n\nNothing was deleted. Fix the cause and paste again; finished steps are skipped.'); });
"""
JS = JS.replace("__TEMPLATES__", TEMPLATES).replace("__LISTS__", json.dumps(LISTS)).replace("__OPTIONAL__", json.dumps(OPTIONAL))
out = sys.argv[1]
JS = JS.replace("https://", "https:\\/\\/")   # mail filters (Mimecast) rewrite literal URLs and break the script
open(out, "w").write(JS)
print("wrote", out, len(JS))
