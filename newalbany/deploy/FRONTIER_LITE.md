# Frontier Audit (lite): safety + 5S observation audits

An optional MDI module, modeled on DuPont STOP. An auditor goes deliberately to a **non-standard zone** (between departments, behind and under equipment, utility rooms, shift handoffs) and runs the D-S-O-I-R cycle on a phone:

| Phase | In the app |
|---|---|
| **D**ecide | Pick the zone (or scan its QR code) and write **why this zone, why now**. The zone's PPE and hazards are shown. |
| **S**top | 60 seconds at the threshold: write first impressions before entering. |
| **O**bserve: safety | Rate **19 items** in 6 categories: **S** safe, **AR** at risk, **U** unsafe, **N/A**. Every AR/U needs a **severity (C/H/M/L)**, what you saw, and a **photo**. Critical and High also need the immediate action taken. |
| **O**bserve: 5S | Each section of the zone's **5S standard** shows its **standard photo** and "good looks like". Rate it **Meets / Deficient / N/A**. A deficiency needs the **pillar** (Sort, Set, Shine, Standardize, Sustain), what's different, and a **photo of what you see now**. Tick "also a safety hazard" to give it a severity (the cross-feed rule). |
| **I**nteract | Required: the operator (name or role), their answers to the **4 standard questions**, and how open the conversation was (1–5). |
| **R**ecord | % safe and top severity. **Close the loop**: on the spot, within 24 hours, pending, or not done, plus the operator's key concern. **SUBMIT.** |

**What submitting does:**
- **Lists:** one row in **SAF_Audits**, plus one row per item and per section in **SAF_Results**.
- **Photos:** saved to **TS_Photos** (Module = Frontier audit).
- **Actions:** every AR/U finding and every 5S deficiency becomes a **NEWSPAPER action** unless the auditor unticks it (Critical and High always do).
  - Safety actions land under SQDCP = Safety; 5S under Quality, or Safety when it's also a hazard.
  - Source is "Frontier audit", and the owner is the zone owner.
  - The due date is set by severity from MDI_Config:

    | Severity | Default due |
    |---|---|
    | Critical | 1 day |
    | High | 1 day |
    | Medium | 30 days |
    | Low | 90 days |
    | 5S (not a hazard) | 30 days |
- **Critical findings:** flow **05 MDI - Frontier Critical Alert** sends a Teams message to the safety coordinator(s) in `Safety_Email` and the zone owner within about a minute.

Findings are never used against the operator. This is a systems tool.

---

## Set it up (about 30 minutes, after the main install)

1. **Lists.** The list setup script (`provision_mdi.js.txt`) creates SAF_Zones, SAF_Items (pre-loaded with the 19 checks), SAF_Audits and SAF_Results. It also adds the "5S" standard type, the "Frontier audit" sources and the MDI_Config settings. If MDI is already installed, run the script again: existing lists are reused and nothing is deleted.
2. **Zones: one row per zone in SAF_Zones.**
   - **ZoneID** format: `FZ-<SITE>-<TYPE>-<NN>`, e.g. `FZ-NAL-TR-01`.
   - **Type codes:** TR Transition, HI Hidden infrastructure, OH Overhead & below, TM Temporal, GF General.
   - **Also fill in:** ZoneName, ZoneType, Line/Area, RiskLevel, Frequency (High risk: weekly; Medium: monthly; Low: quarterly), RequiredPPE, PrimaryHazards, Owner and OwnerEmail.
   - The app shows a zone as **DUE** when its last audit is older than its frequency.
3. **5S standards: one per zone that has a defined 5S condition.**
   1. In **SW Manager** → **+ NEW STANDARD**, set **Type = 5S**.
   2. Add one **section** per area (tool board, bench, parts rack, floor/walkway, cleaning station), each with its **standard condition** text and a **photo of the area as it should look**.
   3. Mark a section's point type **Safety** if a deficiency there is automatically a hazard (walkways, LOTO boards).
   4. Put the standard's **ID** into the zone's **StandardID** in SAF_Zones. SW Manager shows the ID in the 5S sections header.

   A zone without a standard gets a general 5-pillar check instead.
4. **Settings in MDI_Config:**
   - `Safety_Email`: the safety coordinator(s); separate several with semicolons.
   - `SAF_DueDays_*`: due days if you want different timelines.
   - `App_Frontier`: the app's web link.
5. **App:** build **Frontier Audit** (`apps/Frontier_Audit_v2.pa.yaml`, phone) per `apps/APP_BUILD_GUIDE.md`, card 9.
6. **Flow:** the flow installer creates **05 MDI - Frontier Critical Alert**. Turn it on with the others. (Installed before this module existed? Re-run the list setup, then the flow installer; it only adds what's missing.)
7. **QR codes:** for each zone, use the `App_Frontier` link + `?zone=FZ-NAL-TR-01` → Edge → right-click → Create QR code. Post it at the zone boundary.
8. **Edit the checks:** wording lives in **SAF_Items**. To retire a check, set Active = No. Don't delete rows; past audits point at the item numbers.

## Run it
- **Cadence:** every zone at its frequency. Audits are **assigned and scheduled, not voluntary**. Target ≥ 80% completion.
- **Tier 1 (daily):** review yesterday's Frontier actions in NEWSPAPER (Source = Frontier audit), especially Critical and High, and confirm the loop was closed.
- **Tier 2 board (daily):** the **Safety (S)** tile now includes Frontier.
  - **Tile:** "N hazards in M Frontier audits". It turns red on any Critical/High hazard and amber on other hazards.
  - **Drill down:** tap S. The list shows each Frontier finding (severity, item, zone, 5S pillar) next to board safety events. Zones with no Line show at floor level only.
- **Weekly review:** the coordinator reviews SAF_Audits (completion by zone, top severity, % safe) and the 5S deficiencies by pillar (SAF_Results, Kind = 5S, grouped by Pillar). That is the Pareto.
- **Calibration (quarterly):** 3–5 auditors audit the same zone separately and compare severities. A gap of more than one level means retraining.

## What "lite" leaves out (the full SVEND Safety program has these)
- An FMEA register: S×O×D, RPN, hierarchy of controls, re-scoring after controls. Lite stops at severity plus a NEWSPAPER action.
- An audit schedule with named auditor assignments and completion KPIs (lite shows DUE per zone).
- The coordinator "FMEA Bridge" queue, duplicate detection, audit completion % against schedule, and a 5S Pareto chart. Tier 2 shows hazards found, not completion.
- Auditor certification tracking, calibration records, and audits of audits.
