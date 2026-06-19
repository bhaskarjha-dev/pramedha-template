# Operations Guide — Session Rules & Maintenance

> **Purpose:** Rules for AI sessions, data integrity, and maintenance rituals.
> Read `VISION.md` first for the mission. This file is how you execute it safely.

---

## AI Session Rules

When an AI assistant works on this repo, these rules apply:

### DO:
1. **Read `.pramedha/agent-instructions.md` first** — it's the master protocol
2. **Check `authority-map.md` before editing** — know what's truth for what
3. **Tag every claim with verification status** (✅/⚠️/❌)
4. **Cross-reference across sources** — don't trust a single document
5. **Ask when uncertain** — never fabricate data
6. **Commit with clear messages** — describe what changed and why

### DON'T:
1. **Never fabricate claims or metrics** — leave empty if unknown
2. **Never share personal/ data** in any public-facing content
3. **Never edit generated/ files** — they're auto-assembled
4. **Never remove verification tags** — they're the integrity layer
5. **Never use old resume bullets as source of truth** — use identity/*.yaml

---

## What to Update When

> When a career event happens, update files in this exact order.
> **Rule:** Update structured truth BEFORE outward-facing assets.

| Event | Step 1 (Log) | Step 2 (Truth) | Step 3 (Verify) | Step 4 (Assets) |
|-------|-------------|---------------|----------------|----------------|
| **New job / promotion** | journal/work-log/ | identity/experience.yaml | claims-and-evidence.md | resume/master.yaml → rebuild |
| **New certification** | journal/learning-log.md | identity/credentials.yaml | claims-and-evidence.md | resume/master.yaml |
| **Learned new skill** | journal/learning-log.md | identity/skills.yaml | — | strategy/study-plan.md |
| **Won award / recognition** | journal/wins.md | identity/credentials.yaml | claims-and-evidence.md | — |
| **Got feedback** | journal/feedback.md | — | — | — |
| **Applied to job** | — | — | — | strategy/job-search/tracker.md |
| **Shipped project** | journal/work-log/ | identity/projects.yaml | claims-and-evidence.md | resume/master.yaml |
| **Received offer** | — | — | — | strategy/offer-comparison.md |
| **Claim becomes stronger** | — | — | claims-and-evidence.md (upgrade tier) | — |
| **Claim becomes weaker** | — | — | claims-and-evidence.md (downgrade tier) | Remove from resume |
| **Contact info changed** | — | config.yaml | — | — |

---

## Anti-Inflation Rules

> These prevent resume drift — the slow, unconscious inflation of claims over time.

1. **No rounding up experience years** — "nearly 3 years" ✅, "4+ years" ❌
2. **No future credential in current tense** — don't list a cert until you pass it
3. **No count without evidence** — "Led team of 5" needs proof (org chart, email, etc.)
4. **Latest dated evidence wins** — when counts conflict across time, use the number backed by the most recent dated source
5. **Estimated ≠ Measured** — tag every metric: `[measured]` or `[estimated]`. Estimated claims get 🟡, not 🟢
6. **No private data in public assets** — `personal/` content NEVER appears in resumes, LinkedIn, or cover letters

---

## Maintenance Rituals

### Weekly (5 min)
- [ ] Log this week's work in `journal/work-log/`
- [ ] Capture any wins in `journal/wins.md`
- [ ] Update `strategy/job-search/tracker.md` if actively applying
- [ ] Log any feedback received in `journal/feedback.md`

### Monthly (15 min)
- [ ] Review and update `identity/skills.yaml` — new skills learned?
- [ ] Check `identity/claims-and-evidence.md` — any new evidence?
- [ ] Update `strategy/study-plan.md` progress
- [ ] Warm 2-3 networking contacts (see `strategy/networking.md`)
- [ ] Update `journal/learning-log.md` with monthly summary

### Quarterly (30 min)
- [ ] Audit `identity/experience.yaml` — anything missing?
- [ ] Review `strategy/target-roles.md` — priorities changed?
- [ ] Run resume cascade: `python resume/assemble.py --validate`
- [ ] Check for new certifications to add to `identity/credentials.yaml`
- [ ] Refresh `identity/references.yaml` — are 3+ references warm?
- [ ] Review `strategy/risk-register.md` — update contingency plans
- [ ] Run full audit: `ops/audit-checklist.md`

---

## Anti-Drift Rules

1. **Single source of truth:** Each fact lives in ONE file. See `authority-map.md`.
2. **Identity wins:** If resume/LinkedIn conflicts with `identity/*.yaml`, fix the resume.
3. **Evidence required:** No new bullet in experience.yaml without evidence in work-log.
4. **Verification required:** Every outward-facing claim passes through `claims-and-evidence.md`.

---

## What Good Maintenance Looks Like

In a healthy system:
- Facts appear once, then get reused everywhere
- New work strengthens old claims instead of creating contradictions
- Each month makes interviews easier, not harder
- The claims register gets tighter, not looser
