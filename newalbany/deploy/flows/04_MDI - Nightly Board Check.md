# Flow 04 — MDI - Nightly Board Check

> **Built for you:** the full definition is `json/04_MDI - Nightly Board Check.json`. In the sandbox it was created directly in solution MDI. The steps below are the readable version.

**What it does:** every morning it checks yesterday's hour-by-hour boards.
- Any shift with **2 or more hours not filled in** gets a NEWSPAPER action, so it comes up at Tier 1.
- OpEx gets a one-screen email digest: shifts checked, incomplete shifts, and active lines with no board at all.

Settings live in **MDI_Config**:

| Setting | Meaning | Default |
|---|---|---|
| `Alert_Email` | Who gets the digest and flow-failure alerts (a person or a distribution list) | (blank, so fill it in) |
| `NB_MinMissing` | Missing hours before an action is raised | 2 |

Build it **inside the MDI solution** (Solutions → MDI → + New → Automation → Cloud flow → **Scheduled**). Connectors: **SharePoint** and **Office 365 Outlook**, both standard.

---

## 1. Trigger: Recurrence
- Every **1 Day**, at **6:30 AM**
- Time zone: **(UTC-06:00) Central Time (US & Canada)**

## 2. Compose — `Today`
```
formatDateTime(convertFromUtc(utcNow(), 'Central Standard Time'), 'yyyy-MM-dd')
```

## 3. Compose — `Yesterday`
```
formatDateTime(addDays(convertFromUtc(utcNow(), 'Central Standard Time'), -1), 'yyyy-MM-dd')
```

## 4. Get settings
SharePoint **Get items**, List **MDI_Config**, Filter Query:
```
Title eq 'Alert_Email' or Title eq 'NB_MinMissing'
```

Then two Composes:
- **`AlertEmail`:**
  ```
  first(filter(body('Get_settings')?['value'], item()?['Title'] eq 'Alert_Email'))?['SettingValue']
  ```
  Built as a **Filter array** (`Alert_row`, Title is equal to Alert_Email) then `first(body('Alert_row'))?['SettingValue']`.
- **`MinMissing`:**
  ```
  int(coalesce(<same pattern for NB_MinMissing>, '2'))
  ```

## 5. Get shifts
SharePoint **Get items**, List **HxH_Shift**, Top Count **500**, Filter Query:
```
ShiftDate ge '@{outputs('Yesterday')}T00:00:00Z' and ShiftDate lt '@{outputs('Today')}T00:00:00Z'
```

## 6. Get hours
SharePoint **Get items**, List **HxH_Hourly**, Top Count **5000**, same Filter Query as step 5.

## 7. Initialize variable — `Incomplete` (Array, empty)

## 8. Apply to each — shift in `body('Get_shifts')?['value']`

**Compose `Expected`** (hours planned for the shift):
```
int(div(add(mul(float(coalesce(items('Apply_to_each')?['PlannedShiftHrs'], 0)), 60), 59), 60))
```

**Filter array `Filled`**
- From: `body('Get_hours')?['value']`
- Advanced mode:
  ```
  @and(equals(item()?['ShiftKey'], items('Apply_to_each')?['Title']), not(equals(item()?['CumulativeUnits'], null)))
  ```

**Compose `Missing`:**
```
sub(outputs('Expected'), length(body('Filled')))
```

**Condition:** `Missing` is greater than or equal to `MinMissing`.

**If yes:**
1. **Get items `Existing`.** List **Newspaper**, Filter Query:
   ```
   RefKey eq 'NB-@{items('Apply_to_each')?['Title']}'
   ```
2. **Condition:** `length(body('Existing')?['value'])` is equal to `0`.
   - **If yes: Create item**, List **Newspaper**:

     | Field | Value |
     |---|---|
     | Action | `Board not complete: @{items('Apply_to_each')?['Title']} (@{outputs('Missing')} of @{outputs('Expected')} hours missing)` |
     | Line | `@{items('Apply_to_each')?['Line']}` |
     | SQDCP | People |
     | Source | HxH |
     | Status | Open |
     | Progress | 0 |
     | Problem | `Hour-by-hour board left incomplete on @{outputs('Yesterday')}. Fill the missing hours and confirm the reason at Tier 1.` |
     | RaisedDate | `utcNow()` |
     | DueDate | `addDays(utcNow(), 2)` |
     | RefKey | `NB-@{items('Apply_to_each')?['Title']}` |

3. **Append to array variable `Incomplete`:**
   ```
   concat(items('Apply_to_each')?['Title'], ': ', outputs('Missing'), ' of ', outputs('Expected'), ' hours missing')
   ```

## 9. Lines with no board
1. SharePoint **Get items**, List **Lines**, Filter Query `Active eq 1`.
2. **Select** `LinesRan`:
   - From `body('Get_shifts')?['value']`
   - Map (text mode): `item()?['Line']`
3. **Filter array** `NoBoard`:
   - From `body('Get_lines')?['value']`
   - Advanced: `@not(contains(body('LinesRan'), item()?['Title']))`

## 10. Send an email (V2), Office 365 Outlook
- **To:** `@{outputs('AlertEmail')}`
- **Subject:** `MDI board check @{outputs('Yesterday')}: @{length(variables('Incomplete'))} incomplete shift(s)`
- **Body:**
  ```html
  <p><b>Shifts checked:</b> @{length(body('Get_shifts')?['value'])}</p>
  <p><b>Incomplete (actions raised in NEWSPAPER):</b><br>@{join(variables('Incomplete'), '<br>')}</p>
  <p><b>Active lines with no board yesterday</b> (down, or not filled in?):<br>@{join(body('Select_NoBoard'), ', ')}</p>
  ```
  For `Select_NoBoard`, add a Select from `NoBoard` mapping `item()?['Title']`.

## 11. Error handling
A **Catch** scope after *Send an email*, run after failed / timed out / skipped (same as flows 01–03).

## Test
1. Run it manually.
2. A line that saved only some hours yesterday should get one NEWSPAPER action, with RefKey `NB-<ShiftKey>`.
3. Run it again: no duplicate action is created.
