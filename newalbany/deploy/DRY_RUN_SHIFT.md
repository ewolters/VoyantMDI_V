# Dry-run shift: one line, end to end

**Goal:** prove that every app and flow works together on one real (or pretend) shift before go-live.

**People:**
- one supervisor or operator on the line tablet;
- one maintenance tech with a phone;
- QA for 10 minutes;
- the OpEx lead for Tier 2 the next morning.

**Time:** the shift itself, plus about 30 minutes the next morning.

Use a test line, or a real line with a **TEST** note in the remarks, so the rows are easy to clear afterwards (`tools/clear_test_data.js.txt`). Tick each box; anything that fails goes on the issue list at the bottom.

---

## During the shift

### 1. Start of shift: HxH board on the line tablet
- [ ] Open the board from the line's QR code or link. The line and shift are pre-filled.
- [ ] Pick the product/form. The **target per hour** fills in from PLAYBOOK.
  - **If not:** the PLAYBOOK row for that line, size and form is missing.
- [ ] Planned shift hours, lunch and breaks look right.

### 2. Every hour
- [ ] Enter cumulative units at the end of each hour. The run rate and the red/green color update.
- [ ] **Hour 2:** log a downtime of 25 minutes with a reason. It saves with no red banner.
- [ ] **Hour 3:** log 40 more minutes with **the same reason**. That makes 65 minutes cumulative.
  - **Check:** within about 2 minutes, the 60-minute escalation contact gets a **Teams** message from the Flow bot.
  - **Check:** an **Escalation_Log** row appears.
  - **Check:** editing hour 2 again does **not** send a second message.
- [ ] **Offline test (optional):** turn off the tablet's Wi-Fi, save an hour, and look for the red "waiting to save" banner. Turn Wi-Fi back on and tap **RETRY NOW**. The banner clears and the hour shows in HxH_Hourly.

### 3. Maintenance responds: TS Maintenance on a phone
- [ ] Log a troubleshooting occurrence for the same line and machine.
- [ ] At **"WHICH DOWNTIME IS THIS?"**, the board's downtime from step 2 shows as a suggestion. Pick it and enter the repair minutes.
- [ ] **Check:** the TS_Occurrences row has an **EventKey** matching the board (`Line-yyyymmdd-S#|Reason`) and its LinkStatus is set.
- [ ] Take a photo. It lands in **TS_Photos**, which proves the MDI - Upload Photo flow works.

### 4. Quality: QA Rework
- [ ] Log a rework entry.
- [ ] **Void** it: it disappears from the list but still exists with Voided = Yes. Nothing is deleted.

### 5. Standard work and process confirmation (if those modules are in use)
- [ ] **SW Manager:** open a standard and check the photos load.
- [ ] **PC Audit:** run one card, answer one item **No**, and tick its action toggle. When you submit, a Newspaper action appears for it.

### 6. End of shift
- [ ] Fill in every hour. **Leave one hour blank on purpose**; the morning check should catch it.
- [ ] Enter the end-of-shift totals (scrap, crew, reasons).

---

## Next morning

### 7. Nightly Board Check (automatic, 6:30 AM Central)
- [ ] The digest email arrives at Alert_Email.
- [ ] **Check:** with one blank hour, the shift is **not** flagged, because the default threshold is 2 missing hours (`NB_MinMissing`). To see a flag, leave two hours blank instead, or set NB_MinMissing to 1 for the test.
- [ ] Any line you didn't run shows under "Active lines with no board". That's expected for a one-line test.

### 8. Tier 2 board (OpEx, on the meeting TV)
- [ ] It opens on **yesterday**, floor level. The test line shows output vs target, OEE and downtime.
- [ ] Tap the line, then each SQDC letter. The numbers match what was entered.
- [ ] Downtime shows the escalated event. It shows **linked** if step 3 was done, or **unlinked** with a suggested match if it wasn't.
- [ ] As someone with **CanLinkDowntime**, link or waive an unlinked stop. Someone without the switch can't.
- [ ] Targets on the charts follow shift length and PLAYBOOK.

### 9. Newspaper (Tier 1 or 2 actions)
- [ ] The actions from steps 5 and 7 are there. Assign an owner and a due date, and move the Harvey ball to ¼.
- [ ] Close one: set Status = Done and check the ball is full.

### 10. Access (one minute)
- [ ] On the **People** list, turn **CanEditConfig** on for a test person. Within about a minute they're in **MDI Config Editors** (Site settings → People and groups). Turn it off and they're removed.

---

## Issue list

| # | Step | What happened | Screenshot? | Fixed? |
|---|---|---|---|---|
| 1 | | | | |
| 2 | | | | |
| 3 | | | | |

**When it's all green:** run `tools/clear_test_data.js.txt` in `demo` mode, or `reset` mode with a CUTOFF for go-live, to clear the test rows. Then go live one module a week (README, "Suggested rollout").
