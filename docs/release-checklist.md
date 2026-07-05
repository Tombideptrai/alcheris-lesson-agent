# Release Checklist

Run this before publishing the repository.

## Skill Package

- `skills/alcheris-lesson-agent/SKILL.md` has valid YAML frontmatter.
- `SKILL.md` is concise and points to references instead of duplicating them.
- `agents/openai.yaml` matches the skill purpose.
- No credentials appear in the repo.

## Validation

```bash
python /path/to/skill-creator/scripts/quick_validate.py ./skills/alcheris-lesson-agent
python -m py_compile ./skills/alcheris-lesson-agent/scripts/validate_alcheris_lesson.py
```

If an Alcheris backend is available:

```bash
ALCHERIS_EMAIL=your-login-or-email \
ALCHERIS_PASSWORD=your-password \
python ./skills/alcheris-lesson-agent/scripts/validate_alcheris_lesson.py <lesson-id>
```

## MCP

- `alcheris-mcp` is installable from the Alcheris MCP server package.
- Example MCP config uses placeholder credentials.
- Docs tell users to set `ALCHERIS_URL`, `ALCHERIS_EMAIL`, and `ALCHERIS_PASSWORD`.

## Functional Smoke Test

Ask an MCP-connected agent to:

1. List lessons.
2. Read one lesson.
3. Create a small draft lesson.
4. Validate the saved lesson.
5. Open the learner route and check for empty-panel messages.

## Content Quality Smoke Test

Confirm the agent:

- creates a self-study lesson, not a lesson plan,
- uses the lesson spine only when useful,
- chooses blocks by pedagogy,
- uses full-panel modes intentionally,
- does not leave placeholder or empty blocks,
- does not hide essential explanations only in accordions.
