# Schema Reference — PramedhaProfile Field Map

> Every field in this template maps to a field in `PramedhaProfile`.
> This reference ensures clean import into Pramedha.

---

## Enums Reference

| Field | Valid Values |
|-------|-------------|
| `profession_type` | `engineering`, `creative`, `medical`, `business`, `academic`, `legal`, `freelance`, `executive`, `other` |
| `skill_level` | `beginner`, `intermediate`, `advanced`, `expert` |
| `employment_type` | `full_time`, `part_time`, `contract`, `internship`, `freelance`, `self_employed`, `volunteer` |
| `location_type` | `onsite`, `remote`, `hybrid` |
| `language_fluency` | `native`, `fluent`, `professional`, `elementary` |
| `claim_status` | `claimed`, `evidenced`, `verified`, `contradicted`, `disputed` |
| `career_stage` | `student`, `early_career`, `mid_career`, `senior`, `executive`, `career_changer`, `returning`, `freelance` |
| `work_authorization` | `citizen`, `permanent_resident`, `work_visa`, `student_visa`, `need_sponsorship`, `other` |

---

## identity/identity.yaml → PramedhaProfile.professional.identity

| Template Field | Pramedha Field | Type | Required |
|---------------|---------------|------|:--------:|
| `name` | `identity.name` | string | ✅ |
| `contact.email` | `identity.email` | string | ✅ |
| `contact.phone` | `identity.phone` | string | |
| `online_presence.linkedin` | `identity.profiles[network=linkedin].url` | string | |
| `online_presence.github` | `identity.profiles[network=github].url` | string | |
| `online_presence.website` | `identity.url` | string | |
| `location.current_city` | `identity.location.city` | string | |
| `languages[].language` | `identity.languages[].language` | string | |
| `languages[].level` | `identity.languages[].fluency` | LanguageFluency | |

---

## identity/experience.yaml → PramedhaProfile.professional.experience[]

| Template Field | Pramedha Field | Type |
|---------------|---------------|------|
| `company` | `employer` | string |
| `title` | `title` | string |
| `start_date` | `dates.start` | date (YYYY-MM) |
| `end_date` | `dates.end` | date or null |
| `location` | `location.city` | string |
| `employment_type` | `employment_type` | EmploymentType |
| `projects[].deliverables[].bullets[]` | `bullets[].text` | string |
| `projects[].deliverables[].skills[]` | *(feeds skills.yaml)* | string[] |

> [!IMPORTANT]
> **Schema Mismatch — Intentional.**
> The template uses a RICHER structure (`projects → deliverables → bullets`)
> than PramedhaProfile's flat model (`ExperienceEntry → bullets`).
> On Pramedha import, each deliverable is flattened into a separate
> `ExperienceEntry` with the parent employer/title preserved.
> This richer format is better for humans; the flat format is better for database storage.
>
> **Note:** `PramedhaProfile.meta.import_sources` tracks which template
> deliverables were flattened from which project, enabling round-trip fidelity.

---

## identity/skills.yaml → PramedhaProfile.professional.skills[]

| Template Field | Pramedha Field | Type |
|---------------|---------------|------|
| *(category key)* | `skills[].category` | string |
| `name` | `skills[].skills[].name` | string |
| `level` | `skills[].skills[].level` | SkillLevel |
| `years` | `skills[].skills[].years` | float |
| `evidence` | *(mapped to claims_registry)* | string |

---

## identity/credentials.yaml → Multiple Pramedha Arrays

| Template Section | Pramedha Field |
|-----------------|---------------|
| `education[]` | `professional.education[]` |
| `certifications[]` | `professional.certifications[]` |
| `awards[]` | `professional.awards[]` |
| `test_scores[]` | `professional.test_scores[]` |
| `publications[]` | `professional.publications[]` |
| `patents[]` | `professional.patents[]` |
| `grants[]` | `professional.grants[]` |

---

## personal/ → PramedhaProfile.personal

| Template File | Pramedha Field |
|--------------|---------------|
| `preferences.yaml → career_anchor` | `personal.work_preferences.career_anchor` |
| `preferences.yaml → work_values` | `personal.work_preferences.work_values` |
| `preferences.yaml → deal_breakers` | `personal.work_preferences.deal_breakers` |
| `preferences.yaml → strengths` | `personal.work_preferences.self_identified_strengths` |
| `life-goals.md → short_term` | `personal.career_goals.short_term` |
| `life-goals.md → medium_term` | `personal.career_goals.medium_term` |
| `life-goals.md → long_term` | `personal.career_goals.long_term` |
| `about-me.md → career_stage` | `personal.life_context.career_stage` |

---

## claims-and-evidence.md → PramedhaProfile.meta

| Template Concept | Pramedha Field |
|-----------------|---------------|
| Claims Register rows | `meta.claims_registry[]` |
| Contradictions Log rows | `meta.contradictions[]` |
| ✅ VERIFIED tag | `claim_status: "verified"` |
| ⚠️ ESTIMATED tag | `claim_status: "claimed"` |
| ❌ UNVERIFIED tag | `claim_status: "disputed"` |
