# Alcheris Lesson Agent Skill

An installable AI skill for creating, editing, auditing, and repairing interactive
self-study lessons in Alcheris. It works with Codex, Claude Code, and any MCP-compatible
agent, and it is the single source of truth that Alcheris's own native in-app agent
derives from.

Alcheris is subject-neutral. The skill is designed for charts, coding, math, science,
product training, language lessons, exam prep, professional skills, and other
interactive learning experiences.

## What The Skill Does

The skill helps an AI agent turn source material into an Alcheris lesson that is:

- learner-facing, not a teacher lesson plan,
- structured as a self-study experience,
- built with the right Alcheris blocks and full-panel modes,
- **interactive by default** - it reaches for the alive blocks (animated graphs, staged
  illustrations, before/after sliders) instead of static text and images when the
  content has movement, parameters, or a process,
- **designed for the mobile path** - lessons collapse cleanly into mobile learning beats,
- checked for empty or weak blocks, and verified through the student/player route.

The core learning spine is:

```text
orient -> recognize/notice -> explore deeper -> explain/model -> guided practice -> independent application -> check/reflect
```

## Interactive Blocks And Mobile Beats

Two things separate a lively Alcheris lesson from a boring one:

1. **Interactive-first block choice.** When the source has movement, parameters, a
   before/after state, or a process, the skill authors an interactive block instead of a
   static equivalent - e.g. an `interaction` graph with slider reveal rather than a
   static chart image. See `references/alcheris-interactive-blocks.md`.
2. **Beat-aware structure.** Alcheris is self-study; many learners are on phones. Pages
   auto-collapse into learning beats, and beat quality depends on how blocks are ordered
   and signposted. See `references/alcheris-learning-beats.md`.

`skills/alcheris-lesson-agent/data/block-contracts.json` is the machine-readable source
of truth for interactive-block schemas, mobile behavior, and beats. The human references
and the Alcheris native in-app agent's system prompt both derive from it, so the public
skill and the app never drift.

## Repository Layout

```text
.
|-- README.md
|-- docs/
|   |-- env.example
|   |-- install.md
|   |-- mcp-config.example.json
|   `-- release-checklist.md
|-- examples/
|   |-- prompts.md
|   `-- trend-graph-lesson-done-right.md
`-- skills/
    `-- alcheris-lesson-agent/
        |-- SKILL.md
        |-- agents/openai.yaml
        |-- data/block-contracts.json
        |-- references/
        |   |-- alcheris-block-inventory.md
        |   |-- alcheris-interactive-blocks.md
        |   |-- alcheris-learning-beats.md
        |   `-- alcheris-lesson-contracts.md
        `-- scripts/validate_alcheris_lesson.py
```

## Quick Start

1. Install the skill:

```powershell
$SkillHome = "$env:USERPROFILE\.codex\skills"
New-Item -ItemType Directory -Force -Path $SkillHome
Copy-Item -Recurse -Force ".\skills\alcheris-lesson-agent" $SkillHome
```

macOS/Linux:

```bash
mkdir -p ~/.codex/skills
cp -R ./skills/alcheris-lesson-agent ~/.codex/skills/
```

2. Install and connect the Alcheris MCP server. See [docs/install.md](docs/install.md).

3. Ask your agent:

```text
Use $alcheris-lesson-agent to create an interactive Alcheris lesson from these notes.
```

More prompts: [examples/prompts.md](examples/prompts.md). A worked before/after is in
[examples/trend-graph-lesson-done-right.md](examples/trend-graph-lesson-done-right.md).

## Required Environment

The Alcheris MCP server expects:

```text
ALCHERIS_URL=http://localhost:8000
ALCHERIS_EMAIL=your-login-or-email
ALCHERIS_PASSWORD=your-password
```

Never commit real credentials.

## Validation

Validate the skill folder:

```bash
python /path/to/skill-creator/scripts/quick_validate.py ./skills/alcheris-lesson-agent
```

Validate a saved Alcheris lesson (checks block contracts, interactive-block schemas, and
mobile-beat structure):

```bash
ALCHERIS_EMAIL=your-login-or-email \
ALCHERIS_PASSWORD=your-password \
python ./skills/alcheris-lesson-agent/scripts/validate_alcheris_lesson.py <lesson-id>
```

Windows PowerShell:

```powershell
$env:ALCHERIS_EMAIL="your-login-or-email"
$env:ALCHERIS_PASSWORD="your-password"
python .\skills\alcheris-lesson-agent\scripts\validate_alcheris_lesson.py <lesson-id>
```

## Using This As The Source Of Truth

The Alcheris app vendors this skill (including `data/block-contracts.json`) into its own
repo with a sync script, and its native agent builds part of its system prompt from that
data. When you change the skill here, re-run the app's `tools/sync_skill.py` so the app
and this public skill stay in sync.

## Notes For Maintainers

- Keep `SKILL.md` concise. Put detailed contracts and design patterns in `references/`.
- Keep `data/block-contracts.json` authoritative; update it and the references together.
- Do not put credentials in examples.
- Keep MCP setup documentation at repo level, not inside the skill folder.
- Run the checklist in [docs/release-checklist.md](docs/release-checklist.md) before publishing.
