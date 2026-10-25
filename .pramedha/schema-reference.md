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
| `target_role_level` | `intern`, `entry`, `junior`, `mid`, `senior`, `lead`, `staff`, `principal`, `director`, `vp`, `c-level`, `executive` |

---

<a id="config-identity"></a>
## config.yaml & identity/identity.yaml → PramedhaProfile.professional.identity

| Config / Identity Field | Pramedha Field | Type | Source Priority |
|-------------------------|---------------|------|:---------------:|
| `user.name` / `name` | `identity.name` | string | identity.yaml > config.yaml |
| `user.email` / `contact.email` | `identity.email` | string | identity.yaml > config.yaml |
| `user.phone` / `contact.phone` | `identity.phone` | string | identity.yaml > config.yaml |
| `profiles.linkedin` | `identity.profiles[network=linkedin].url` | string | identity.yaml > config.yaml |
| `profiles.github` | `identity.profiles[network=github].url` | string | identity.yaml > config.yaml |
| `user.website` / `portfolio` | `identity.url` | string | identity.yaml > config.yaml |
| `target_role_level` | *(positioning reference)* | RoleLevel | config.yaml (exclusive) |
| `location.*` | `identity.location` | Location | identity.yaml > config.yaml |
| `languages[].language` | `identity.languages[].language` | string | identity.yaml (exclusive) |
| `languages[].level` | `identity.languages[].fluency` | LanguageFluency | identity.yaml (exclusive) |
| `work_authorization` | `identity.work_authorization` | WorkAuth | identity.yaml (exclusive) |
| `pronouns` | `identity.pronouns` | string | identity.yaml (exclusive) |

---

<a id="experience"></a>
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

| Identity Source | `tools/resume/master.yaml` Section | RenderCV Entry Type & Fields |
|-----------------|-----------------------------------|------------------------------|
| `identity/identity.yaml` & `config.yaml` | `header:` (`name`, `email`, `phone`, `website`, `location`, `social_networks`) | Top-level `cv` header: `name`, `email`, `phone`, `website`, `location`, `social_networks` |
| `identity/experience.yaml` | `experience:`<br>`[role_key]:`<br>&nbsp;&nbsp;`company`<br>&nbsp;&nbsp;`position`<br>&nbsp;&nbsp;`start_date`, `end_date`<br>&nbsp;&nbsp;`location`<br>&nbsp;&nbsp;`bullets: [key]: {phrasings}` | `ExperienceEntry`:<br>• `company`<br>• `position`<br>• `start_date`, `end_date`<br>• `location`<br>• `highlights: [...]` (selected from variant) |
| `identity/projects.yaml` | `projects:`<br>`[proj_key]:`<br>&nbsp;&nbsp;`name`<br>&nbsp;&nbsp;`date`<br>&nbsp;&nbsp;`location` (URL/repo)<br>&nbsp;&nbsp;`bullets: {phrasings}` | `NormalEntry`:<br>• `name`<br>• `date`<br>• `location`<br>• `highlights: [...]` |
| `identity/credentials.yaml` (`education[]`) | `education:`<br>`- institution`<br>&nbsp;&nbsp;`area`<br>&nbsp;&nbsp;`degree`<br>&nbsp;&nbsp;`start_date`, `end_date`<br>&nbsp;&nbsp;`highlights: [...]` | `EducationEntry`:<br>• `institution`<br>• `area`<br>• `degree`<br>• `start_date`, `end_date`<br>• `highlights: [...]` |
| `identity/credentials.yaml` (`publications[]`) | `publications:`<br>`- title`<br>&nbsp;&nbsp;`authors: [...]`<br>&nbsp;&nbsp;`date`<br>&nbsp;&nbsp;`journal` / `publisher`<br>&nbsp;&nbsp;`doi` / `url` | `PublicationEntry`:<br>• `title`<br>• `authors`<br>• `date`<br>• `journal`<br>• `doi`<br>• `url` |
| `identity/skills.yaml` | `technologies:` (or `skills:`)<br>`- label: "Category"`<br>&nbsp;&nbsp;`details: "item1, item2"` | `OneLineEntry` under Technologies section |

---

<a id="skills"></a>
## identity/skills.yaml → PramedhaProfile.professional.skills[]

| Template Field | Pramedha Field | Type |
|---------------|---------------|------|
| *(category key)* | `skills[].category` | string |
| `name` | `skills[].skills[].name` | string |
| `level` | `skills[].skills[].level` | SkillLevel |
| `years` | `skills[].skills[].years` | float |
| `evidence` | *(mapped to claims_registry)* | string |

---

<a id="credentials"></a>
## identity/credentials.yaml → Multiple Pramedha Arrays

| Template Section | Pramedha Field | Pramedha Model |
|-----------------|---------------|----------------|
| `education[]` | `professional.education[]` | `EducationEntry` |
| `certifications[]` | `professional.certifications[]` | `CertificationEntry` |
| `awards[]` | `professional.awards[]` | `AwardEntry` |
| `test_scores[]` | `professional.test_scores[]` | `TestScoreEntry` |
| `publications[]` | `professional.publications[]` | `PublicationEntry` |
| `patents[]` | `professional.patents[]` | `PatentEntry` |
| `grants[]` | `professional.grants[]` | `GrantEntry` |

---

<a id="projects"></a>
## identity/projects.yaml → PramedhaProfile.professional.projects[]

| Template Field | Pramedha Field | Type |
|---------------|---------------|------|
| `public[].name` / `internal[].name` | `projects[].name` | string |
| `tagline` | `projects[].description` | string |
| `tech[]` | `projects[].technologies` / `tech_stack` | string[] |
| `live_url` / `repo` | `projects[].url` / `repo_url` | string |
| `start_date`, `end_date` | `projects[].dates` | DateRange |
| `role` | `projects[].role` | string |
| `highlights[]` | `projects[].highlights` | string[] |
| `impact_metrics` | `projects[].metrics` | string |
| `featured[]` | `professional.featured[]` | `FeaturedItem` |

---

<a id="speaking-and-community"></a>
## identity/speaking-and-community.yaml → Thought Leadership & Community

| Template Section | Pramedha Field / Equivalent | Description |
|-----------------|-----------------------------|-------------|
| `speaking[]` | `professional.featured[]` or extension | Talks, presentations, panel sessions |
| `hackathons[]` | `professional.projects[]` or `awards[]` | Competitions and hackathon builds |
| `community[]` | `professional.organizations[]` | Meetups, organizations, community leadership |
| `content_metrics` | `meta.metrics` | Social audience and readership reach |

---

<a id="volunteering"></a>
## identity/volunteering.yaml → PramedhaProfile.professional.volunteer[]

| Template Section | Pramedha Field | Pramedha Model |
|-----------------|---------------|----------------|
| `volunteering[]` | `professional.volunteer[]` | `VolunteerEntry` |
| `open_source[]` | `professional.projects[]` (with open-source tag) | `ProjectEntry` |
| `mentoring[]` | `professional.volunteer[]` / `experience[]` | `VolunteerEntry` |

---

<a id="references"></a>
## identity/references.yaml → PramedhaProfile.professional.references[]

| Template Field | Pramedha Field | Type |
|---------------|---------------|------|
| `name` | `professional.references[].name` | string |
| `relationship` | `professional.references[].relationship` | string |
| `title` + `company` | `professional.references[].reference` | string |
| `email` / `phone` | `professional.references[].contact` | string |

---

<a id="personal"></a>
## personal/ → PramedhaProfile.personal

| Template File | Pramedha Field |
|--------------|---------------|
| `preferences.yaml → career_anchor` | `personal.work_preferences.career_anchor` |
| `preferences.yaml → work_values` | `personal.work_preferences.work_values` |
| `preferences.yaml → deal_breakers` | `personal.work_preferences.deal_breakers` |
| `preferences.yaml → strengths` | `personal.work_preferences.self_identified_strengths` |
| `preferences.yaml → remote_preference` | `personal.work_preferences.remote_preference` |
| `preferences.yaml → career_stage` | `personal.life_context.career_stage` |
| `preferences.yaml → risk_tolerance` | `personal.life_context.risk_tolerance` |
| `life-goals.md → short_term` | `personal.career_goals.short_term` |
| `life-goals.md → medium_term` | `personal.career_goals.medium_term` |
| `life-goals.md → long_term` | `personal.career_goals.long_term` |
| `about-me.md → career_stage` | `personal.life_context.career_stage` |

---

<a id="claims-and-meta"></a>
## claims-and-evidence.md → PramedhaProfile.meta

| Template Concept | Pramedha Field |
|-----------------|---------------|
| Claims Register rows | `meta.claims_registry[]` |
| Contradictions Log rows | `meta.contradictions[]` |
| ✅ VERIFIED tag | `claim_status: "verified"` |
| ⚠️ ESTIMATED tag | `claim_status: "claimed"` |
| ❌ UNVERIFIED tag | `claim_status: "disputed"` |

---

<a id="pramedha-compatibility"></a>
## Pramedha Compatibility & Contract Reference

### The "Pramedha Portable Format" Principle

`pramedha-template` is designed to be the canonical **file-based, portable representation** of a career profile.
- **Standalone:** Zero external dependencies, pure Git + YAML + Markdown. Any LLM (Claude, ChatGPT, Copilot, Antigravity) can read and modify it directly.
- **Platform-Compatible:** When imported into the Pramedha Career OS platform, this flat-file structure maps cleanly into the unified `PramedhaProfile` Pydantic models.

### Field Coverage Summary

| Area | Template Support | Platform Support | Notes |
|------|:----------------:|:----------------:|-------|
| Professional Facts | ✅ Full | ✅ Full | Exact 1:1 mapping |
| Work Experience | ✅ Hierarchical | ✅ Flat | Template's employer→project→deliverable flattens to `ExperienceEntry` |
| Skills Matrix | ✅ Categorized | ✅ Taxonomized | Platform maps names to Lightcast/ESCO canonical IDs |
| Credentials & Education | ✅ Full | ✅ Full | Split into education, certs, awards |
| Private Preferences | ✅ Private YAML | ✅ Personal Layer | Strictly guarded, never serialized to outward assets |
| Claims & Verification | ✅ Markdown Ledger | ✅ Meta Layer | Trust scores and verification tags align |
| External Tools Integration | ✅ `tools/` | ✅ MCP & SDK | Decoupled tool satellites mounted under `tools/` (e.g. `tools/resume/`) |
| Vector Embeddings | ❌ (File-based) | ✅ Qdrant/pgvector | Computed during platform intake |
| Knowledge Graph | ❌ (File-based) | ✅ NetworkX/Neo4j | Inferred during platform graph queries |
