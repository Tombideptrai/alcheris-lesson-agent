# Installation Guide

This guide assumes:

- You have access to an Alcheris backend.
- You have an Alcheris account.
- You have an MCP-compatible agent environment such as Codex, Claude Desktop, Claude Code, or another MCP client.

## 1. Install The Skill

Copy the skill folder into your Codex skills directory.

Windows PowerShell:

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

Restart Codex if your environment does not hot-reload skills.

## 2. Install The Alcheris MCP Server

From an Alcheris app checkout that contains `mcp-server/`:

```bash
cd path/to/lesson-maker/mcp-server
pip install -e .
```

This installs the `alcheris-mcp` command.

Check that it is available:

```bash
alcheris-mcp --help
```

Some MCP stdio servers do not print a normal help screen. If the command exists but waits for input, that is usually fine.

## 3. Configure Environment Variables

Create local environment variables. Do not commit these values.

Windows PowerShell:

```powershell
$env:ALCHERIS_URL="http://localhost:8000"
$env:ALCHERIS_EMAIL="your-login-or-email"
$env:ALCHERIS_PASSWORD="your-password"
```

macOS/Linux:

```bash
export ALCHERIS_URL="http://localhost:8000"
export ALCHERIS_EMAIL="your-login-or-email"
export ALCHERIS_PASSWORD="your-password"
```

## 4. Connect The MCP Server

Use your MCP client's config format. The generic JSON shape is:

```json
{
  "mcpServers": {
    "alcheris": {
      "command": "alcheris-mcp",
      "env": {
        "ALCHERIS_URL": "http://localhost:8000",
        "ALCHERIS_EMAIL": "your-login-or-email",
        "ALCHERIS_PASSWORD": "your-password"
      }
    }
  }
}
```

A copy is provided at [mcp-config.example.json](mcp-config.example.json).

## 5. Test The Connection

Ask your agent:

```text
Use the Alcheris MCP to list my lessons.
```

Then ask:

```text
Use $alcheris-lesson-agent to audit one existing lesson and report empty blocks, weak block choices, and panel-mode issues.
```

## 6. Create A Lesson

Example:

```text
Use $alcheris-lesson-agent and the Alcheris MCP to create a self-study lesson from these notes. Preserve all important concepts, choose the right block types, use full-panel modes where appropriate, and validate the saved lesson before you finish.
```

## Troubleshooting

- If the MCP server cannot authenticate, check `ALCHERIS_URL`, `ALCHERIS_EMAIL`, and `ALCHERIS_PASSWORD`. Some Alcheris deployments accept a username as the `ALCHERIS_EMAIL` value.
- If the skill does not trigger, confirm `skills/alcheris-lesson-agent/SKILL.md` exists under your Codex skills directory.
- If lessons save but render badly, open `/learn/<lesson-id>` and run `scripts/validate_alcheris_lesson.py`.
- If a full-panel page looks wrong, make sure `rightPanelMode` matches the right-panel block type.
