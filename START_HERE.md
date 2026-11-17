# Start here, Kenny

This kit lets you and Claude keep the New Albany MDI running and change it, without Eric. You don't need to know Python or Power Fx: Claude does the code, you do the clicking in Power Apps and tell Claude what you see.

**How the work splits**
- **Claude (in the Claude desktop app, Code tab)** reads this folder, changes the generators, rebuilds the app screens, checks them, and tells you exactly what to paste and where.
- **You** paste into Power Apps Studio in the **MDI Dev** environment, test, then ship the change to production with a managed export + upgrade.

---

## Part 1. One-time setup (about an hour)

### 1. Claude
- You need a **paid Claude plan (Pro, Max, Team or Enterprise)**. Claude Code isn't available on the free plan.
- Install the **Claude desktop app** for Windows: use **Download for Windows** on the [desktop quickstart page](https://code.claude.com/docs/en/desktop-quickstart). Sign in.
- Click the **Code** tab at the top of the sidebar. That's Claude Code. (The normal chat tab can't see this folder.)

### 2. Two free tools Claude needs on your PC
- **Git for Windows**: https://git-scm.com/download/win (defaults are fine).
- **Python 3**: https://www.python.org/downloads/ . On the first installer screen, tick **"Add python.exe to PATH"**.

If your PC is locked down and IT has to install these, ask for exactly those two.

### 3. Your own copy of this repo
This folder lives on GitHub. You need your own copy so you can save changes:
- Make a free account at https://github.com if you don't have one.
- Either Eric **transfers** the repo to you (Settings → Transfer), or you open https://github.com/ewolters/VoyantMDI_V and click **Fork**. Either way, you end up with `github.com/<you>/VoyantMDI_V`.
- Consider making your copy **private** (repo Settings → Danger Zone → Change visibility). It contains your SharePoint site address.

### 4. Get it onto your PC
1. In the Code tab, choose **Local** and open a folder such as `Documents`.
2. Type: *"Clone https://github.com/&lt;you&gt;/VoyantMDI_V into this folder."* Approve what it asks.
3. Start a **new session** and open the new `VoyantMDI_V` folder as the project. Claude now reads `CLAUDE.md` automatically, which tells it everything about this system.
4. Type: *"Read START_HERE.md, then run the generator check."* It should end with **"23 identical, 0 different"**. That proves the code in the repo matches what's installed.

**Permission mode:** start in **Manual** (Claude asks before each change or command). Switch to **Accept edits** once you're comfortable.

### 5. Your development environment (MDI Dev)
Production stays untouched; every change is built and tested in a separate environment first.
1. **make.powerapps.com** → ⚙ (top right) → **Admin center** → **Environments** → **+ New**.
   - Name: `MDI Dev` · Type: **Developer** (free for you; if your tenant blocks it, ask IT for a **Sandbox** environment) · Add a Dataverse data store: **Yes**.
2. Back in make.powerapps.com, switch to **MDI Dev** (environment picker, top right).
3. **Solutions → Import solution → Browse →** `solution\MDI_OhioContinuousImprovement_UNMANAGED_v1.1.4.1.zip` from your `VoyantMDI_V` folder → **Next**. Sign in to the connections it asks for (SharePoint, Outlook, Teams, Dataverse, Excel Online) → **Import**.
4. Optional: import `solution\MDISetup_UNMANAGED_v1.0.0.0.zip` the same way.
5. When it finishes: **Solutions → MDI → Apps**, open each app once and **Publish**.

**Never import the UNMANAGED zip into your production (default) environment.** The managed MDI already lives there and the two collide.

**Heads-up:** MDI Dev points at the real Ohio SharePoint lists, so testing there writes real data. For risky changes, ask Claude to help you point MDI Dev at a scratch site first.

---

## Part 2. Everyday use

Open the Code tab, open the `VoyantMDI_V` folder, and just say what you want. Examples:

- *"On Hour x Hour, make the downtime reason box wider."* → Claude changes the generator, rebuilds, checks, and tells you which file to paste on which screen in MDI Dev.
- *"Holmdel: Christian gets 'does not have ReadAccess right(s) … entity Process'."* → Claude walks you through the fix in TROUBLESHOOTING.md.
- *"The change works in MDI Dev. Ship it to production."* → Claude walks you through the version bump, managed export and upgrade.
- *"Explain how the Tier 2 downtime number is calculated."* → Claude reads the code and answers in plain words.

**Three skills are built in.** Type `/` in the prompt box to see them:
- `/change-app`: change a screen or formula, start to finish.
- `/ship-upgrade`: move a tested change from MDI Dev to production.
- `/troubleshoot`: diagnose an error message or a board that looks wrong.

**Habits that keep this safe**
- Paste only into **MDI Dev**. Production only ever gets a managed **Upgrade** import.
- Give Claude the **exact error text** or a screenshot, plus which app/screen/flow.
- After every production import: open the solution and check every flow says **On**.
- At the end of a change, say *"commit and push this."* Your GitHub copy is the backup.

---

## Part 3. If you're stuck
- `TROUBLESHOOTING.md` has every error we've hit, with fixes. Claude reads it too.
- `log.md` is the build history, with why things are the way they are.
- Claude Code help: https://code.claude.com/docs/en/desktop
