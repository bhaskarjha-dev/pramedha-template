# Audit Checklist — Systematic Freshness Check

> **Purpose:** Run this checklist monthly (or after any major career event)
> to ensure your career data is fresh, consistent, and accurate.
>
> Use with prompt #2 from ops/prompts.md for AI-assisted audit.

---

## 10-Area Audit

### 1. Contact Consistency
- [ ] identity.yaml contact matches config.yaml
- [ ] resume/master.yaml header matches identity.yaml
- [ ] LinkedIn/platform profiles match identity.yaml
- [ ] All links are live (not 404)

### 2. Experience Freshness
- [ ] Most recent work is captured in experience.yaml
- [ ] Recent projects have deliverables and bullets
- [ ] No work from the last 3 months is missing
- [ ] All dates are accurate (cross-check with offer letters)

### 3. Skills Accuracy
- [ ] Skills reflect what you've used in the last 6 months
- [ ] Levels match reality (not inflated from old resumes)
- [ ] New tools/frameworks from recent work are added
- [ ] Deprecated skills are removed or downgraded

### 4. Claims Integrity
- [ ] Every resume bullet has a claims register entry
- [ ] No ❌ UNVERIFIED claims in any active resume variant
- [ ] Metrics are tagged [measured] or [estimated]
- [ ] Evidence references are still valid

### 5. Resume Cascade Health
- [ ] `python resume/assemble.py --validate` passes
- [ ] All variants build without errors
- [ ] Generated YAMLs are up to date
- [ ] No orphaned bullets in master.yaml (not used by any variant)

### 6. Verification Coverage
- [ ] >80% of facts have ✅ VERIFIED tags
- [ ] <10% of facts are ❌ UNVERIFIED
- [ ] Evidence documents exist for all ✅ claims
- [ ] Contradictions log is current

### 7. Strategy Alignment
- [ ] Target roles still match career goals
- [ ] Resume variants exist for all Tier A roles
- [ ] Study plan reflects current skill gaps
- [ ] Financial targets are realistic for current market

### 8. Privacy Check
- [ ] No personal/ data leaking into identity/ or resume/
- [ ] No salary information in public-facing files
- [ ] Sensitive documents in data-corpus/ are noted in .gitignore
- [ ] If repo is public: no PII in committed files

### 9. Completeness
- [ ] Run: `python .pramedha/validate.py --status`
- [ ] Fill rate is >70% for active job search
- [ ] Professional summary variants are up to date
- [ ] All sections relevant to target roles are filled

### 10. Git Health
- [ ] No uncommitted changes sitting for >1 week
- [ ] Commit messages are descriptive
- [ ] generated/ and output/ are not committed
- [ ] No large binary files bloating the repo

---

## Scoring

| Score | Status |
|:-----:|--------|
| 10/10 | 🟢 Excellent — maintain monthly |
| 7-9/10 | 🟡 Good — fix failing areas this week |
| 4-6/10 | 🟠 Needs work — schedule a deep maintenance session |
| 0-3/10 | 🔴 Critical — fix before any applications |
