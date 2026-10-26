@AGENTS.md

## For Claude Code

- `AGENTS.md` above is the source of truth; keep it current when a register or a sink changes.
- Task-specific rules live in `.claude/rules/` (content, templates). Read the one that matches the task.
- The `add-content` skill (`.claude/skills/add-content/`) walks through adding a page end to end.
- Verify visually before reporting done: a headless browser screenshot of the changed page, in light and dark,
  at phone width, not just a successful build.
