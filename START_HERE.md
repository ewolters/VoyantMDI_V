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
1. **make.powerapps.com** → ⚙ (top right) → **Admin center** → **Environments** → **+ New**.
   - Name: `MDI Dev` · Type: **Developer** (free; if your tenant blocks it, ask IT for a **Sandbox**) · Add a Dataverse data store: **Yes**.
2. Back in make.powerapps.com, switch to **MDI Dev** (environment picker, top right).
3. Download `newalbany/solution/MDI_OhioContinuousImprovement_UNMANAGED_v1.1.4.1.zip` from GitHub (`main`). **Solutions → Import solution → Browse →** that zip → **Next**. Sign in to the connections it asks for (SharePoint, Outlook, Teams, Dataverse, Excel Online) → **Import**.
4. Optional: import `newalbany/solution/MDISetup_UNMANAGED_v1.0.0.0.zip` the same way.
5. When it finishes: **Solutions → MDI → Apps**, open each app once and **Publish**.

**Never import the UNMANAGED zip into your production (default) environment.** The managed MDI already lives there and the two collide.

**Heads-up:** MDI Dev points at the real Ohio SharePoint lists, so testing there writes real data. For risky changes, ask Claude to help you point MDI Dev at a scratch site first.

---

## Part 2. Everyday use

Start a session on this repo and say what you want. Say **which plant** (New Albany or Holmdel) first; they're different systems. Examples:

- *"New Albany, Hour x Hour: make the downtime reason box wider."* → Claude changes the generator, rebuilds, checks, pushes, and tells you which file to paste on which screen in MDI Dev.
- *"Holmdel: the TV says 'does not have ReadAccess right(s) … entity Process'."* → Claude walks you through the fix in `holmdel/TROUBLESHOOTING.md`.
- *"The change works in MDI Dev. Ship it to production."* → Claude walks you through the version bump, managed export and upgrade.
- *"New Albany: I want a new app to log start-of-shift line checks, with its own list."* → `/new-app`: Claude proposes the list, builds the installer and a starter screen, then walks you through creating the list, the app and the upgrade (`newalbany/NEW_APP_GUIDE.md`).
- *"Explain how the Tier 2 downtime number is calculated."* → Claude reads the code and answers in plain words.

**Three skills are built in.** Type `/` in the prompt box to see them:
- `/change-app`: change a screen or formula, start to finish.
- `/ship-upgrade`: move a tested change from MDI Dev to production.
- `/troubleshoot`: diagnose an error message or a board that looks wrong.
- `/new-app`: a new list and a new app, start to finish (New Albany).

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
