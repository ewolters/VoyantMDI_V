# Start here, Kenny

This kit lets you and Claude keep the MDI running and change it. You don't need to know Python or Power Fx: Claude does the code, you do the clicking in Power Apps and tell Claude what you see.

**How the work splits**
- **Claude Code (in your browser, at claude.ai/code, working in this repo)** reads the repo, changes the generators, rebuilds the app screens, checks them, and tells you exactly what to paste and where. Nothing is installed on your PC.
- **You** paste into Power Apps Studio in the **MDI Dev** environment, test, then ship the change to production with a managed export + upgrade.

---

## Part 1. One-time setup

### 1. Claude Code
- A **paid Claude plan** (Pro, Max, Team or Enterprise) and a GitHub account with access to `github.com/ewolters/VoyantMDI_V`.
- Go to **claude.ai/code**, pick this repo, and start a session. Claude reads `CLAUDE.md` automatically, which tells it everything about this system.
- First message: *"Read START_HERE.md, then run the generator check."* It should end with **"23 identical, 0 different"**. That proves the code in the repo matches what's installed.

### 2. How files get from Claude to you
Claude runs in the cloud, not on your PC, so files reach you through GitHub:
- Each session works on its own **branch** and pushes to GitHub. Ask Claude *"push this and give me the link to the file."*
- **A screen (`.pa.yaml`):** open the link → **Raw** → Ctrl+A, Ctrl+C → paste in Studio. (Or ask Claude to print a short one in the chat.)
- **A solution zip:** open the link → **Download raw file**.
- When a change is working in production, have Claude open a **pull request** and merge it into `main` on GitHub. `main` is the record of what's live; leave test branches unmerged.

### 3. Your development environment (MDI Dev)
Production stays untouched; every change is built and tested in a separate environment first.

**Kenny's is named `MDI_Sandbox`** (created Nov 2026). Everywhere these docs say **MDI Dev**, that's `MDI_Sandbox`. If it already exists, skip step 1. (Not the same thing as Eric's old `MDISandbox` SharePoint site in the Verxted tenant, which is no longer used.)

1. **make.powerapps.com** → ⚙ (top right) → **Admin center** → **Environments** → **+ New**.
   - Name: `MDI Dev` · Type: **Developer** (free; if your tenant blocks it, ask IT for a **Sandbox**) · Add a Dataverse data store: **Yes**.
2. Back in make.powerapps.com, switch to **MDI Dev** (environment picker, top right).
3. Download the newest `newalbany/solution/MDI_OhioContinuousImprovement_UNMANAGED_v*.zip` from GitHub (`main`). **Solutions → Import solution → Browse →** that zip → **Next**.
   - **Flows off:** if the next screen has **Advanced settings**, untick *Enable plug-in steps and flows included in the solution*. MDI Dev points at the real Ohio lists, so flows running here would send real escalations and change real site permissions alongside production.
   - Sign in to the connections it asks for (SharePoint, Outlook, Teams, Dataverse, Excel Online) → **Import**.
4. When it finishes: **Solutions → MDI → Cloud flows**: every flow must say **Off**. Turn off any that are on.
5. Optional: import `newalbany/solution/MDISetup_UNMANAGED_v1.0.0.0.zip` the same way.
6. **Solutions → MDI → Apps**, open each app once and **Publish**.

**Never import the UNMANAGED zip into your production (default) environment.** The managed MDI already lives there and the two collide.

**Heads-up:** MDI Dev points at the real Ohio SharePoint lists, so testing there writes real data. Keep its flows **off**. For risky changes, or to test a flow for real, ask Claude to help you point MDI Dev at a scratch site first.

### 4. Managed vs unmanaged (and Power Apps vs Power Automate)
- A **solution** (MDI) is one package stored in an **environment**. It holds the apps, the flows, the 32 environment variables and the connection references together.
- **make.powerapps.com** and **make.powerautomate.com** show the **same** Solutions list for the environment you've picked. Import MDI in one and it shows in the other. Apps open in Power Apps Studio; flows open in the flow designer. Do solution work (import, export, version, environment variables) in **make.powerapps.com**; these instructions are written for it.
- **Managed** = the locked, installed copy. Production (**Vee Pak, LLC (default)**) has managed MDI. **Never edit it**: an edit there creates an "unmanaged layer" that blocks future upgrades.
- **Unmanaged** = the editable copy. MDI Dev has unmanaged MDI. Edit freely.
- A change moves: edit in MDI Dev (unmanaged) → **Export as Managed** → import into production as an **Upgrade**. The export is where unmanaged becomes managed.
- **My flows** in Power Automate lists flows *outside* any solution, e.g. old hand-built ones. The real MDI flows are inside the MDI solution (Solutions → MDI → Cloud flows).

### Replacing a screen (the paste steps, in plain words)
Use these every time Claude gives you a new screen file. Example: the Hour x Hour board.
1. **Copy the new file.** Open the link Claude gives you. Press **Ctrl+A** (selects all the text), then **Ctrl+C** (copies it).
2. **Open the app for editing:** make.powerapps.com → top right, check the environment says **MDI_Sandbox** → **Solutions** → **MDI** → **Apps** → click the app → **Edit**.
3. **Find the screen.** On the left is a panel called **Tree view**, a list of the app's screens (Screen1, scrPeriods, …). Click the **name of the screen** Claude told you (for example **Screen1**).
4. **Empty the screen.** Click once on the picture of the board in the middle of the window. Press **Ctrl+A**: every box on the board gets a thin outline. Press **Delete**: the board goes blank.
   - Check: in Tree view, the screen name has nothing listed under it any more, and **the other screens still have their items.** If another screen went empty, press **Ctrl+Z** (undo) and start this step again.
   - If Ctrl+A didn't outline anything: in Tree view click the arrow next to the screen name so its items show, click the **top** item, scroll to the **bottom** of that list, hold **Shift** and click the **bottom** item, then press **Delete**.
5. **Paste.** Click the **screen name** in Tree view again, then press **Ctrl+V**. Big screens take 10–20 seconds.
6. **Errors?** A red circle with an ✕ means a problem. Send Claude a screenshot or the message text. Don't Publish with red errors.
7. **Publish** (purple button, top right), then **Play** (▶) to test.

---

## Part 2. Everyday use

Start a session on this repo and say what you want. Say **which plant** (New Albany or Holmdel) first; they're different systems. Examples:

- *"New Albany, Hour x Hour: make the downtime reason box wider."* → Claude changes the generator, rebuilds, checks, pushes, and tells you which file to paste on which screen in MDI Dev.
- *"Holmdel: the TV says 'does not have ReadAccess right(s) … entity Process'."* → Claude walks you through the fix in `holmdel/TROUBLESHOOTING.md`.
- *"The change works in MDI Dev. Ship it to production."* → Claude walks you through the version bump, managed export and upgrade.
- *"New Albany: I want a new app to log start-of-shift line checks, with its own list."* → `/new-app`: Claude proposes the list, builds the installer and a starter screen, then walks you through creating the list, the app and the upgrade (`newalbany/NEW_APP_GUIDE.md`).
- *"Explain how the Tier 2 downtime number is calculated."* → Claude reads the code and answers in plain words.

**Six skills are built in.** Type `/` in the prompt box to see them:
- `/change-app`: change a screen or formula, start to finish.
- `/change-flow`: change a flow; Claude sends you a patched solution zip to import into MDI Dev (no flow designer editing).
- `/ship-upgrade`: move a tested change from MDI Dev to production.
- `/troubleshoot`: diagnose an error message or a board that looks wrong.
- `/new-app`: a new list and a new app, start to finish (New Albany).
- `/change-list`: add a column, a choice or an index to an existing list, safely (New Albany).

**Habits that keep this safe**
- Paste only into **MDI Dev**. Production only ever gets a managed **Upgrade** import.
- Give Claude the **exact error text** or a screenshot, plus which app/screen/flow.
- After every production import: open the solution and check every flow says **On**.
- One change per session/branch. Merge to `main` once it's live, so the next session starts from what production actually runs.
- **The repo is public.** Don't paste setup codes (`MDI2:…`), passwords or Voyant documents into files Claude commits.

---

## Part 3. If you're stuck
- **Every Claude reply ends with a question, the next step, and two or three prompts you can copy.** If you don't know what to say, pick one of those, or just answer the question.
- `RISK_REGISTER.md` lists what can break at each plant, how you'd notice and how to fix it. §1 there is the short list to deal with first.
- `newalbany/TROUBLESHOOTING.md` (New Albany) and `holmdel/TROUBLESHOOTING.md` have every error we've hit, with fixes. Claude reads them too.
- `newalbany/log.md` is the build history, with why things are the way they are.
- Claude Code on the web help: https://code.claude.com/docs/en/claude-code-on-the-web
