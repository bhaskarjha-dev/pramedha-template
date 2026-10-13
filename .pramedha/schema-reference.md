# Schema Reference — PramedhaProfile Field Map

> This is the canonical field-by-field reference for every template file.
> Use it to understand what each field means, what values are valid, and how
> files relate to each other. This template works fully standalone — the
> `Maps to:` paths shown below document the PramedhaProfile schema mapping
> for optional integration with the Pramedha platform.

---

## Enums Reference

| Field | Valid Values |
|-------|-------------|
| `profession_type` | `engineering`, `creative`, `medical`, `business`, `academic`, `legal`, `freelance`, `executive`, `other` |
| `career_type` | `employed`, `freelance`, `portfolio`, `academic`, `military`, `government`, `student` |
| `skill_level` | `beginner`, `intermediate`, `advanced`, `expert` |
| `employment_type` | `full_time`, `part_time`, `contract`, `internship`, `freelance`, `self_employed`, `volunteer` |
| `location_type` | `onsite`, `remote`, `hybrid` |
| `language_fluency` | `native`, `fluent`, `professional`, `conversational`, `elementary` |
| `claim_status` | `claimed`, `evidenced`, `verified`, `contradicted`, `disputed` |
| `career_stage` | `student`, `early_career`, `mid_career`, `senior`, `executive`, `career_changer`, `returning`, `sabbatical`, `freelance` |
| `career_break_type` | `sabbatical`, `caregiving`, `parental_leave`, `education`, `health`, `relocation`, `career_transition` |
| `work_authorization` | `citizen`, `permanent_resident`, `work_visa`, `student_visa`, `need_sponsorship`, `other` |

---

## config.yaml & identity/identity.yaml → PramedhaProfile.professional.identity

| Config / Identity Field | Pramedha Field | Type | Source Priority |
|-------------------------|---------------|------|:---------------:|
| `user.name` / `name` | `identity.name` | string | identity.yaml > config.yaml |
| `user.email` / `contact.email` | `identity.email` | string | identity.yaml > config.yaml |
| `user.phone` / `contact.phone` | `identity.phone` | string | identity.yaml > config.yaml |
| `profiles.linkedin` | `identity.profiles[network=linkedin].url` | string | identity.yaml > config.yaml |
| `profiles.github` | `identity.profiles[network=github].url` | string | identity.yaml > config.yaml |
| `user.website` / `portfolio` | `identity.url` | string | identity.yaml > config.yaml |
| `location.*` | `identity.location` | Location | identity.yaml > config.yaml |
| `languages[].language` | `identity.languages[].language` | string | identity.yaml (exclusive) |
| `languages[].level` | `identity.languages[].fluency` | LanguageFluency | identity.yaml (exclusive) |
| `work_authorization` | `identity.work_authorization` | WorkAuth | identity.yaml (exclusive) |
| `pronouns` | `identity.pronouns` | string | identity.yaml (exclusive) |

---

## identity/experience.yaml → PramedhaProfile.professional.experience[]

| Template Field | Pramedha Field | Type |
|---------------|---------------|------|
| `company` | `employer` | string |
| `position` | `title` | string |
| `role_subtitle` | `functional_role` | string |
| `start_date` | `dates.start` | date (YYYY-MM) |
| `end_date` | `dates.end` | date or "present" |
| `location` | `location.city` | string |
| `employment_type` | `employment_type` | EmploymentType |
| `projects[].deliverables[].bullets[]` | `bullets[].text` | string |
| `projects[].deliverables[].skills[]` | *(feeds skills.yaml)* | string[] |
| `career_breaks[].type` | `career_breaks[].type` | CareerBreakType |
| `career_breaks[].start_date` | `career_breaks[].dates.start` | date (YYYY-MM) |
| `career_breaks[].end_date` | `career_breaks[].dates.end` | date (YYYY-MM) |
| `career_breaks[].description` | `career_breaks[].description` | string |
| `last_updated` | `meta.last_updated` | date (YYYY-MM-DD) |

> [!IMPORTANT]
> **Schema Mismatch — Intentional.**
> The template uses a RICHER structure (`projects → deliverables → bullets`)
> than PramedhaProfile's flat model (`ExperienceEntry → bullets`).
> On Pramedha import, each deliverable is flattened into a separate
> `ExperienceEntry` with the parent employer/position preserved.
> This richer format is better for humans; the flat format is better for database storage.
>
> **Note:** `PramedhaProfile.meta.import_sources` tracks which template
> deliverables were flattened from which project, enabling round-trip fidelity.

---

## Identity → Resume Cascade Mapping (RenderCV Flow)

The bridge between raw identity facts and RenderCV resume generation operates as follows:

| Identity Source | `resume/master.yaml` Section | RenderCV Entry Type & Fields |
|-----------------|-----------------------------|------------------------------|
| `identity/identity.yaml` & `config.yaml` | `header:` (`name`, `email`, `phone`, `website`, `location`, `social_networks`) | Top-level `cv` header: `name`, `email`, `phone`, `website`, `location`, `social_networks` |
| `identity/experience.yaml` | `experience:`<br>`[role_key]:`<br>&nbsp;&nbsp;`company`<br>&nbsp;&nbsp;`position`<br>&nbsp;&nbsp;`start_date`, `end_date`<br>&nbsp;&nbsp;`location`<br>&nbsp;&nbsp;`bullets: [key]: {phrasings}` | `ExperienceEntry`:<br>• `company`<br>• `position`<br>• `start_date`, `end_date`<br>• `location`<br>• `highlights: [...]` (selected from variant) |
| `identity/projects.yaml` | `projects:`<br>`[proj_key]:`<br>&nbsp;&nbsp;`name`<br>&nbsp;&nbsp;`date`<br>&nbsp;&nbsp;`location` (URL/repo)<br>&nbsp;&nbsp;`bullets: {phrasings}` | `NormalEntry`:<br>• `name`<br>• `date`<br>• `location`<br>• `highlights: [...]` |
| `identity/credentials.yaml` (`education[]`) | `education:`<br>`- institution`<br>&nbsp;&nbsp;`area`<br>&nbsp;&nbsp;`degree`<br>&nbsp;&nbsp;`start_date`, `end_date`<br>&nbsp;&nbsp;`highlights: [...]` | `EducationEntry`:<br>• `institution`<br>• `area`<br>• `degree`<br>• `start_date`, `end_date`<br>• `highlights: [...]` |
| `identity/credentials.yaml` (`publications[]`) | `publications:`<br>`- title`<br>&nbsp;&nbsp;`authors: [...]`<br>&nbsp;&nbsp;`date`<br>&nbsp;&nbsp;`journal` / `publisher`<br>&nbsp;&nbsp;`doi` / `url` | `PublicationEntry`:<br>• `title`<br>• `authors`<br>• `date`<br>• `journal`<br>• `doi`<br>• `url` |
| `identity/skills.yaml` | `technologies:` (or `skills:`)<br>`- label: "Category"`<br>&nbsp;&nbsp;`details: "item1, item2"` | `BulletEntry` or `NormalEntry` under Technologies section |

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
