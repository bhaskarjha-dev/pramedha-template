# External Tools

This directory is a **gitignored mount point** for third-party career tools.
Clone or install any tool here — it won't be tracked in your career repo.

## How to Use

```bash
# Example: Clone career-ops (AI job search agent)
cd tools/external/
git clone https://github.com/career-ops-hq/career-ops

# Example: Install JobSpy (job scraper)
pip install python-jobspy
# Use it from here, pointing at your identity/ data
```

## How External Tools Access Your Data

External tools can read your career data from the root of this repository:

| What They Need | Where It Lives |
|---------------|----------------|
| Your profile | `../../config.yaml` + `../../identity/identity.yaml` |
| Work history | `../../identity/experience.yaml` |
| Skills | `../../identity/skills.yaml` |
| What you want | `../../strategy/target-roles.md` |
| Your resume | `../../tools/resume/` (built-in engine) |

Most AI-powered tools (career-ops, ai-job-search) can be pointed at these
YAML files directly. The AI agent you're using (Claude, Copilot, Antigravity)
acts as the adapter — it reads your YAML and feeds it to the tool.

## Popular Tools

| Tool | What It Does | Install |
|------|-------------|---------|
| [career-ops](https://github.com/career-ops-hq/career-ops) | AI job search agent — scores listings, tailors CVs | `npx @santifer/career-ops init` |
| [JobSpy](https://github.com/speedyapply/JobSpy) | Multi-board job scraper (LinkedIn, Indeed, 6 more) | `pip install python-jobspy` |
| [job-ops](https://github.com/DaKheera47/job-ops) | Full-stack job search dashboard | `docker compose up -d` |
| [ai-job-search](https://github.com/MadsLorentzen/ai-job-search) | Claude Code job application framework | `git clone` |

## Pramedha Platform

If you want intelligent integration (automated matching, artifact generation,
MCP server for agent access), see [Pramedha](https://github.com/bhaskarjha-dev/pramedha)
— the full Career OS that this template's data format is compatible with.
