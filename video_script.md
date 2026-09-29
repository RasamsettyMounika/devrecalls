# 3-Minute Video Demo Script: DevRecall & Hindsight Agent Memory

**Target Length:** ~3 minutes  
**Format:** Screen recording (OBS / Loom) with terminal open and voiceover.

---

## 5 High-Performing YouTube Titles
1. **Why Coding Agents Keep Breaking Your Terminal (And How We Fixed It)**
2. **I Stopped AI Agents From Forgetting My Dev Stack Using Hindsight**
3. **Giving an AI Terminal Agent Long-Term Memory in 3 Minutes**
4. **Before vs After: What Happens When an AI Agent Actually Remembers?**
5. **We Built an AI Co-Pilot That Never Makes the Same Mistake Twice**

---

## Video Script & Visual Cues

### [0:00 - 0:30] PART 1: Quick Intro (Who I am & What this is)
* **[Screen Cue]:** Show VS Code with the project folder `devrecall` open. Terminal is clear. Face cam in corner (optional).
* **[Narration]:**
  > *"Hey everyone! If you've used any AI coding assistant or terminal co-pilot, you know the frustration: every time you start a session, it completely forgets your setup. It suggests Linux commands on Windows, recommends `npm` when your project strictly uses `pnpm`, and tries to spin up Docker on ports that are already blocked.*  
  > *Today, I built **DevRecall**—a lightweight CLI pair programmer powered by **Hindsight Agent Memory** from Vectorize. Instead of re-explaining your workstation quirks ten times a day, DevRecall retains your environment rules and recalls them automatically before running commands."*

---

### [0:30 - 1:00] PART 2: The Problem (Agent Without Memory)
* **[Screen Cue]:** In the terminal, run:
  ```powershell
  python main.py demo
  ```
  Camera focuses on **PHASE 1: THE PROBLEM**.
* **[Narration]:**
  > *"Let's look at the classic failure. Watch what happens when we ask a standard stateless agent: 'How do I set test environment variables and run our integration tests?'*  
  > *Because it has no memory of our workstation, it makes a generic guess: `export NODE_ENV=test && npm test`. But we're on Windows PowerShell, and this repo is a `pnpm` monorepo.*  
  > *When we execute that, PowerShell immediately throws: `export is not recognized as a cmdlet`, and `npm` throws missing script. Command fails, and the developer has to stop and rewrite it manually."*

---

### [1:00 - 2:30] PART 3: Live Demo (Hindsight Retain & Recall in Action)
* **[Screen Cue]:** The terminal advances to **PHASE 2 & PHASE 3**. Point cursor at `Hindsight Retain` outputs, then the `Hindsight Recalled Memory Units` table.
* **[Narration]:**
  > *"Now, here is how Hindsight solves this. In Phase 2, we store three simple environment facts into our Hindsight memory bank: our OS shell is PowerShell 7, our package manager is strictly `pnpm`, and our PostgreSQL host port is mapped to 5433.*  
  > *Notice the API: it's just a clean `client.retain()` call with contextual tags.*  
  > *Now in Phase 3, we ask the exact same question again: 'How do I set test environment variables and run our integration tests?'*  
  > *Look at the table right here on screen. DevRecall immediately calls `client.recall()`. Hindsight matches our query against the stored bank and retrieves the exact three rules in milliseconds.*  
  > *The agent synthesizes the response using that recalled context. And look at the final output:*  
  > `$env:NODE_ENV='test'; $env:DB_PORT='5433'; pnpm test`  
  > *PowerShell syntax is correct, the port conflict is avoided, and `pnpm` is invoked. Zero manual explanations, running cleanly on the first try."*

---

### [2:30 - 3:00] PART 4: Wrap-Up & Key Takeaways
* **[Screen Cue]:** Switch tab to the GitHub repo or `devrecall/memory.py` code.
* **[Narration]:**
  > *"The big takeaway here: developer productivity doesn't need giant 1-million-token context windows that slow down inference. What developer agents really need is surgical, durable memory that persists across terminal sessions.*  
  > *Integrating Hindsight took less than 20 lines of Python, and it completely eliminated environment drift in our CLI.*  
  > *Check out the repo link in the description, try Hindsight for your own agent workflows, and let me know in the comments what you think! Thanks for watching."*

---

## Recording Checklist for You
1. Set terminal font size to **18pt+** so it's super easy to read on mobile.
2. Run `python main.py demo` once to make sure you're comfortable with the timing.
3. Open OBS / Loom / QuickTime, hit Record, and talk through the script above!
