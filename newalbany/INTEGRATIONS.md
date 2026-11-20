# Connecting other data (Epicor and others) to the MDI

Written Nov 20, 2026, after Kenny asked about comparing board entries with Epicor, as the old Excel Tier 1 setup did (manual entries vs an Epicor Power Query feed). **Nothing here is built yet.** Facts marked *(check)* weren't confirmed for Voyant.

## What the MDI already has to match on
Every Hour x Hour row saves line, shift date, shift, hour, cumulative units and **job number (exactly 6 digits since HxH v26)**; HxH_Shift has the shift totals. A "Board vs ERP" comparison joins on job (and/or line + date + shift) and can show as a variance tile on Tier 2 / Tier 3 with the usual thresholds.

## Routes

| Route | How | License | Freshness | Notes |
|---|---|---|---|---|
| **A. Existing Power Query workbook** | Workbook pulls from Epicor, saved on SharePoint; a standard flow (Excel Online (Business)) copies its table to a SharePoint list (e.g. `ERP_Production`) every 30–60 min; apps compare. | Standard | As of the last refresh | Desktop Excel must refresh it; a flow / Excel for the web generally can't run a Power Query against Epicor *(check)*. Fastest proof of value. |
| **B. Epicor exports a file** | Scheduled export (e.g. BAQ export) to a SharePoint folder or e-mail; standard flow loads it. | Standard | Epicor's schedule | Needs the Epicor admin. Same "flow reads a file" pattern as Holmdel. |
| **C. Flow calls Epicor** | Scheduled flow → Epicor REST API / BAQ, or SQL via the on-premises data gateway → SharePoint list. | **Premium** (HTTP, custom connector, SQL Server, gateway) | 15–60 min, automatic | Keep it to one background flow on a service account so the apps stay standard; confirm the licensing with Microsoft / the reseller *(check)*. |
| **D. Third-party connector** | e.g. CData Epicor Kinetic drivers/connectors. | Vendor subscription, usually + Premium | Near live | No Epicor-built Power Automate connector found. |
| **E. Power BI** | One report on the SharePoint lists + Epicor, scheduled refresh through a gateway; shown in Teams or as a tile. | Power BI Pro for viewers *(check)* | Scheduled | Best for analysis/trends, less for live boards. |

**Not possible on standard licenses:** a flow calling Epicor's web API directly. Office Scripts can't make external calls when a flow runs them (Microsoft: "No external calls from a script" in Power Automate), so the Holmdel script trick can't reach Epicor.

## Design rules for any route
- Store **daily or per-shift summaries** in the ERP list, not every transaction (apps read at most 2,000 rows per query).
- Matching: Epicor job numbers, line names and shift windows must map to the board's; document the mapping.
- Timing: boards post hourly, Epicor may post at shift end. Show "not posted yet" separately from a real gap.
- Security: read-only Epicor account owned by IT; credentials never in this repo (it's public).
- A new list follows `newalbany/NEW_APP_GUIDE.md` (package → Set Up Site → environment variable).

## Next step when this starts
Find out how the existing Power Query connects (Data → Queries & Connections → the query → its **Source** step), the Epicor version (Kinetic cloud or on-premises) and Voyant's Power Platform / Power BI licenses. Then pick a route and write the design (list columns, matching rules, the Tier 2 tile).

Sources: [CData: Epicor Kinetic to Power Automate](https://www.cdata.com/data/access/epicorkinetic-to-microsoft-power-automate/) · [Microsoft: Office Scripts external calls](https://learn.microsoft.com/en-us/office/dev/scripts/develop/external-calls) · [Microsoft: Office Scripts platform limits](https://learn.microsoft.com/office/dev/scripts/testing/platform-limits) · [Microsoft: on-premises data gateway in Power Automate](https://learn.microsoft.com/en-us/power-automate/gateway-manage)
