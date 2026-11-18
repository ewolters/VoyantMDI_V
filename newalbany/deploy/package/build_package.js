// MDI package builder. Run in the browser console on the GOLDEN environment's Dataverse URL
// (https://<org>.crm.dynamics.com), signed in as a maker. It exports the MDI solution (managed),
// rewires every app and flow from the golden SharePoint site to the customer's site using the
// customer's SETUP CODE (MDI2:...), checks nothing still points at the golden site, and saves
// MDI_<site>_managed.zip to Downloads. Nothing in the golden environment is changed.
(async () => {
  // ---- golden site (where the apps were built) ----
  const GOLD_SITE = "https://verxted.sharepoint.com/sites/MDISandbox";
  const GOLD_LISTS = {"Assets":"a98b36e8-5c70-4ab2-a172-0df1b82d6174","Documents":"4ca79884-33ea-4d5f-abce-b7d99291a1d1","Escalation_Contacts":"ff7632ce-d24b-426b-b826-989760b9347b","Escalation_Log":"ff327b68-5f04-4080-99f2-58aaf88082d6","Events":"886f2fea-6a22-443a-8844-678890371b4e","Form Templates":"bafb6e8c-dae8-4539-85c7-465dadc0bceb","HxH_Hourly":"afa6c071-4098-4a7f-b8a9-0277ce745c2d","HxH_Shift":"5f5caae7-2355-467a-b3a4-f48b6d18820b","KPI_Daily":"1304bf64-bde8-4b41-9b38-d93ff70d58f4","KPI_Metrics":"605776c5-0e35-4cf1-a36d-5268248a3df4","Lines":"d0b85ec7-8373-4b66-a93b-2ad99def3859","Lookups":"5b214f86-ea6b-4b75-9735-f8f48caddcde","MDI_Config":"1ce134d3-335f-415c-8ae0-e8cf7c0d9e16","NCR":"0d03ad65-e4d6-408a-b227-7a07039e4d12","Newspaper":"803c69e8-a326-4ece-bc21-9ac6f5b4ce24","PC_Audits":"18aa5766-7fee-4307-bdd9-50d7d3c2f607","PC_CardItems":"ef5aebb8-8886-4238-add6-402bd38f6c0f","PC_Cards":"f64686fd-e868-46f0-a2e0-b5125e6fcb76","PC_Results":"89019241-562d-4f96-b1aa-edb411560f6c","People":"a4c78ec3-d9a8-4997-90cd-a4bb5a0e454d","PLAYBOOK":"ec120d81-adae-436b-aad3-7ff5ce42e13d","QA_Rework":"51f1d39f-491f-472e-b95e-24aaab7b5ee9","QMS_AuditQs":"d4e88312-1e53-41fe-8012-3cf2da79062a","QMS_AuditResults":"a9cd5872-ab43-4e84-becf-e74214ff92b2","QMS_Audits":"d5499dd1-1f76-422f-8c3a-149a4370793a","QMS_Binder":"c8c2c50e-cc27-44df-8026-47a9b5925845","QMS_Cards":"2132999e-19f9-48bb-bdf1-bf0f3eb29a16","QMS_Config":"88a21ad4-7e27-400b-88c0-0fab801dc1d5","QMS_MonthClose":"704e2ee2-6413-44ed-bf7f-fbcee4b09a80","QMS_Pulls":"1ccea953-5619-4555-b156-52b7203c696c","SAF_Audits":"015591cb-a5d8-40ce-b734-a39749736d11","SAF_Items":"9c1d127a-7274-4174-a5b0-edb9707323c3","SAF_Results":"0f228237-bfa8-4f0d-bf1e-8d1fdc141367","SAF_Zones":"bef27523-94b4-4999-a201-9524443b5b3b","Site Pages":"377e330f-15ce-4b2a-a024-c9aafd21366d","Style Library":"c70a82b6-43f9-4440-82cc-e47b7d1366cd","SW_Elements":"bd2d87d0-738d-40fe-9d23-d7d2128c0986","SW_Standards":"994300db-7167-4b6c-9f02-b8181ba97c0b","T2_Maint":"543ceb92-bb86-4761-9559-aa15fa12a16f","TS_Fixes":"7347f77d-dbc6-447a-8802-427effa43dbf","TS_Issues":"cef62f56-c083-4c10-90a3-59512efa6be5","TS_Occurrences":"d87e8a20-e622-4a0d-9b61-081fd9d5982b","TS_Photos":"606ed8b0-435f-4bb0-b9d8-c019af11f008","TS_Procedures":"0896146a-c27b-4de7-a797-d9051df16601","TS_Steps":"14d0a277-19e1-411c-b2bf-346317ba5411","ValueStreams":"edafea77-dcc6-43fc-89ac-4cfcb732512d","Variances":"87a7cabc-b601-424c-bdde-2875851b0222"};
  const SOLUTION = "MDI", MANAGED = true;

  const code = (window.MDI_CODE || prompt("Paste the customer's SETUP CODE (MDI2:...)") || "").trim();
  if (!code.startsWith("MDI2:")) throw new Error("Not a setup code (must start with MDI2:)");
  const cust = JSON.parse(new TextDecoder().decode(Uint8Array.from(atob(code.slice(5)), c => c.charCodeAt(0))));
  const newSite = cust.site.replace(/\/+$/, "");
  const newIds = Object.fromEntries(cust.lists.map(l => [l.n, l.id.toLowerCase()]));
  console.log("Customer site:", newSite, "lists:", cust.lists.length);

  // ---- zip helpers ----
  const dec = new TextDecoder(), enc = new TextEncoder();
  const CRC = (() => { const t = new Uint32Array(256); for (let n = 0; n < 256; n++) { let c = n; for (let k = 0; k < 8; k++) c = c & 1 ? 0xEDB88320 ^ (c >>> 1) : c >>> 1; t[n] = c >>> 0; } return t; })();
  const crc32 = b => { let c = 0xFFFFFFFF; for (let i = 0; i < b.length; i++) c = CRC[(c ^ b[i]) & 0xFF] ^ (c >>> 8); return (c ^ 0xFFFFFFFF) >>> 0; };
  const pipe = async (b, s) => new Uint8Array(await new Response(new Blob([b]).stream().pipeThrough(s)).arrayBuffer());
  function list(b) {
    const dv = new DataView(b.buffer, b.byteOffset, b.byteLength); let e = b.length - 22;
    while (dv.getUint32(e, true) !== 0x06054b50) e--;
    let off = dv.getUint32(e + 16, true); const n = dv.getUint16(e + 10, true), out = [];
    for (let i = 0; i < n; i++) {
      const nl = dv.getUint16(off + 28, true), el = dv.getUint16(off + 30, true), cl = dv.getUint16(off + 32, true);
      const nameBytes = b.slice(off + 46, off + 46 + nl), lho = dv.getUint32(off + 42, true);
      const lnl = dv.getUint16(lho + 26, true), lel = dv.getUint16(lho + 28, true), csize = dv.getUint32(off + 20, true);
      out.push({ nameBytes, name: dec.decode(nameBytes), method: dv.getUint16(off + 10, true), crc: dv.getUint32(off + 16, true),
        csize, usize: dv.getUint32(off + 24, true), time: dv.getUint16(off + 12, true), date: dv.getUint16(off + 14, true),
        raw: b.slice(lho + 30 + lnl + lel, lho + 30 + lnl + lel + csize) });
      off += 46 + nl + el + cl;
    }
    return out;
  }
  const read = async f => f.method === 0 ? f.raw : await pipe(f.raw, new DecompressionStream("deflate-raw"));
  async function setData(f, data) { f.raw = await pipe(data, new CompressionStream("deflate-raw")); f.method = 8; f.crc = crc32(data); f.csize = f.raw.length; f.usize = data.length; }
  function write(files) {
    const parts = [], cen = []; let off = 0;
    for (const f of files) {
      const h = new DataView(new ArrayBuffer(30));
      h.setUint32(0, 0x04034b50, true); h.setUint16(4, 20, true); h.setUint16(6, 0x0800, true); h.setUint16(8, f.method, true);
      h.setUint16(10, f.time, true); h.setUint16(12, f.date, true); h.setUint32(14, f.crc, true); h.setUint32(18, f.csize, true);
      h.setUint32(22, f.usize, true); h.setUint16(26, f.nameBytes.length, true); h.setUint16(28, 0, true);
      parts.push(new Uint8Array(h.buffer), f.nameBytes, f.raw);
      const c = new DataView(new ArrayBuffer(46));
      c.setUint32(0, 0x02014b50, true); c.setUint16(4, 20, true); c.setUint16(6, 20, true); c.setUint16(8, 0x0800, true); c.setUint16(10, f.method, true);
      c.setUint16(12, f.time, true); c.setUint16(14, f.date, true); c.setUint32(16, f.crc, true); c.setUint32(20, f.csize, true);
      c.setUint32(24, f.usize, true); c.setUint16(28, f.nameBytes.length, true); c.setUint32(42, off, true);
      cen.push(new Uint8Array(c.buffer), f.nameBytes);
      off += 30 + f.nameBytes.length + f.raw.length;
    }
    const cl = cen.reduce((s, x) => s + x.length, 0), e = new DataView(new ArrayBuffer(22));
    e.setUint32(0, 0x06054b50, true); e.setUint16(8, files.length, true); e.setUint16(10, files.length, true); e.setUint32(12, cl, true); e.setUint32(16, off, true);
    return new Blob([...parts, ...cen, new Uint8Array(e.buffer)], { type: "application/zip" });
  }

  // ---- rewrite rules ----
  const gu = new URL(GOLD_SITE), nu = new URL(newSite);
  const esc = s => s.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
  const gPath = gu.pathname.split("/").filter(Boolean), nPath = nu.pathname.split("/").filter(Boolean);
  const siteRe = new RegExp(esc(gu.host) + "((?:\\\\)?/)" + gPath.map(esc).join("(?:\\\\)?/"), "gi");
  const siteNew = (m, sep) => nu.host + sep + nPath.join(sep);
  const unmapped = new Set();
  const guidRules = Object.entries(GOLD_LISTS).map(([name, id]) => ({ name, re: new RegExp(esc(id), "gi"), to: newIds[name] }));
  function rewrite(t) {
    let s = t.replace(siteRe, siteNew), hits = s !== t;
    for (const g of guidRules) { if (g.re.test(s)) { g.re.lastIndex = 0; if (!g.to) { unmapped.add(g.name); continue; } s = s.replace(g.re, g.to); hits = true; } g.re.lastIndex = 0; }
    return { s, hits };
  }
  const isText = n => /\.(json|xml|yaml|sarif)$/i.test(n) || /^\[Content_Types\]/.test(n);

  // ---- export ----
  console.log("Exporting", SOLUTION, MANAGED ? "(managed)" : "(unmanaged)", "...");
  const r = await fetch("/api/data/v9.2/ExportSolution", { method: "POST", headers: { "Content-Type": "application/json", "OData-Version": "4.0" }, body: JSON.stringify({ SolutionName: SOLUTION, Managed: MANAGED }) });
  if (!r.ok) throw new Error("Export failed: " + r.status + " " + (await r.text()).slice(0, 300));
  const sol = Uint8Array.from(atob((await r.json()).ExportSolutionFile), c => c.charCodeAt(0));

  const outer = list(sol); let changed = 0;
  for (const f of outer) {
    if (f.name.endsWith(".msapp")) {
      const inner = list(await read(f)); let any = false;
      for (const g of inner) { if (!isText(g.name)) continue; const { s, hits } = rewrite(dec.decode(await read(g))); if (hits) { await setData(g, enc.encode(s)); any = true; changed++; } }
      if (any) await setData(f, new Uint8Array(await write(inner).arrayBuffer()));
    } else if (isText(f.name)) {
      const { s, hits } = rewrite(dec.decode(await read(f))); if (hits) { await setData(f, enc.encode(s)); changed++; }
    }
  }
  if (unmapped.size) throw new Error("The setup code has no list for: " + [...unmapped].join(", ") + ". Run the setup flow on the customer site again.");

  // ---- verify ----
  const blob = write(outer), check = list(new Uint8Array(await blob.arrayBuffer()));
  const leftovers = []; let ver = "";
  const scan = (name, t) => { if (new RegExp(esc(gu.host) + "(\\\\)?/" + gPath.map(esc).join("(\\\\)?/"), "i").test(t)) leftovers.push(name + ": golden site"); for (const g of guidRules) if (new RegExp(esc(GOLD_LISTS[g.name]), "i").test(t)) leftovers.push(name + ": " + g.name); };
  for (const f of check) {
    if (f.name.endsWith(".msapp")) { for (const g of list(await read(f))) if (isText(g.name)) scan(f.name + "/" + g.name, dec.decode(await read(g))); }
    else if (isText(f.name)) { const t = dec.decode(await read(f)); scan(f.name, t); if (f.name === "solution.xml") ver = (t.match(/<Version>([^<]+)/) || [])[1] || ""; }
    if (crc32(await read(f)) !== f.crc) leftovers.push(f.name + ": bad CRC");
  }
  if (leftovers.length) throw new Error("Still pointing at the golden site:\n" + leftovers.join("\n"));

  const siteName = nPath[nPath.length - 1] || nu.host.split(".")[0];
  window.MDI_PACKAGE = { blob, name: `MDI_${siteName}_managed_v${ver}.zip`, changed, site: newSite };
  console.log(`OK: ${changed} files rewired to ${newSite}. Package ready: ${window.MDI_PACKAGE.name} (${Math.round(blob.size / 1024)} KB).`);
  if (!window.MDI_NO_DOWNLOAD) { const a = document.createElement("a"); a.href = URL.createObjectURL(blob); a.download = window.MDI_PACKAGE.name; a.click(); }
})().catch(e => console.error("MDI package FAILED:", e.message));
