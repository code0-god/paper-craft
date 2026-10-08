# Host compatibility

Paper Craft uses the portable Agent Skills format: `SKILL.md` plus references, Python scripts, assets, schemas, venue data, and a license. Copy the complete directory. Do not create independent prompt forks per host or replace relative resources with repository-specific paths. `agents/openai.yaml` supplies optional Codex UI metadata; other hosts can ignore it.

## Native discovery and invocation

Append `/paper-craft/SKILL.md` to the roots below. Paths were checked against the linked official documentation on 2026-10-08. This verifies documented discovery support; it is not a claim that every host binary/version was executed in package tests.

| CLI target | Host | Project root | User root | Explicit request |
| --- | --- | --- | --- | --- |
| `codex` | Codex CLI / IDE | `.agents/skills` | `~/.agents/skills` | `$paper-craft` or `/skills` picker |
| `claude` | Claude Code | `.claude/skills` | `~/.claude/skills` | `/paper-craft` |
| `gemini` | Gemini CLI | `.gemini/skills` | `~/.gemini/skills` | Ask to use the `paper-craft` skill |
| `cursor` | Cursor | `.cursor/skills` | `~/.cursor/skills` | Type `/`, select `paper-craft` |
| `copilot` | GitHub Copilot CLI | `.github/skills` | `~/.copilot/skills` | `/paper-craft` |
| `opencode` | OpenCode | `.opencode/skills` | `~/.config/opencode/skills` | V2: `@paper-craft`; otherwise ask by name |
| `windsurf` | Windsurf compatibility paths | `.windsurf/skills` | `~/.codeium/windsurf/skills` | `@paper-craft` |
| `devin` | Devin Desktop | `.devin/skills` | `~/.config/devin/skills` | `@paper-craft` |
| `generic` | Other standard-capable hosts | `.agents/skills` | `~/.agents/skills` | Host picker or explicit file loading |

Automatic selection depends on the host and skill description. Some hosts also discover `.agents/skills` or Claude-compatible paths. Prefer the explicit native target when interoperability needs to be predictable. Gemini activation is model-driven and may request user consent; do not invent a slash command for its activation tool. OpenCode V1/V2 differ in explicit invocation. Windsurf paths remain supported by the current Devin Desktop documentation; the `devin` target uses preferred current paths.

When Gemini finds both `.agents/skills` and `.gemini/skills` at the same scope, the documented `.agents` alias takes precedence. Keep compatibility copies consistent when updating; a stale higher-priority copy can mask another installation.

Project installation means the current working directory, not automatic repository-root selection. Run from the intended project root. A custom `--destination` creates a complete portable folder but does not register it in host settings. Claude's additional-directory permission alone does not load its skills; use its documented `--add-dir` or `/add-dir` mechanism. Do not rewrite a user's settings file or bypass host permissions to make discovery succeed.

## Installation and updates

The npm CLI accepts a host target alongside user/project selection:

```bash
paper-craft install --agent claude --project
paper-craft update --agent claude --project
paper-craft install --agent all --project
paper-craft install --agent generic --destination /path/to/shared/paper-craft
```

Default remains `codex`. `all` installs the confirmed native target set, not every unknown application. Install into an existing target is refused; updates preserve each original directory in a backup. Install/update operations concern skill files only and do not install, sign into, or configure the host applications. Use the CLI help to inspect the supported target set and options in the installed package.

For manual installation, copy the canonical Skill to the matching root. Keep `LICENSE` and all internal resources. In any host, determine the actual skill folder before invoking Python scripts; do not assume the Codex path when running inside Claude or another application.

## Hosts without native skills

Make the complete Skill folder accessible and issue an explicit request:

```text
Read /path/to/paper-craft/SKILL.md and follow its applicable modules for this task.
Resolve referenced files relative to /path/to/paper-craft.
Review my manuscript without changing the original files.
```

For attachment-only interfaces, attach the entrypoint and the references needed for the task, plus permitted manuscript material. That is manual context loading, not automatic discovery. If the interface cannot read local files, run Python, browse official guidelines, render PDFs, or accept all required resources, limit the review to supplied evidence and mark unperformed checks SKIPPED/UNKNOWN. Never imply that installing a folder changes an unrelated chat application's capabilities. Language-model execution follows the selected host's data and permission policies.

## Official sources

- [Codex local discovery and invocation](https://learn.chatgpt.com/docs/build-skills#where-codex-loads-local-skills)
- [Claude Code skill locations and invocation](https://code.claude.com/docs/en/skills#choose-where-skills-load)
- [Gemini CLI discovery tiers](https://geminicli.com/docs/cli/skills/#discovery-tiers), [activation tool](https://geminicli.com/docs/tools/activate-skill/#usage)
- [Cursor skill directories](https://cursor.com/docs/skills#skill-directories)
- [Copilot CLI skills](https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/add-skills#using-agent-skills)
- [OpenCode V1 skill locations](https://opencode.ai/docs/skills/#place-files), [V2 discovery](https://opencode.ai/v2/docs/skills#discovery), [V2 loading](https://opencode.ai/v2/docs/skills#loading)
- [Devin Desktop / Windsurf skill scopes](https://docs.devin.ai/desktop/cascade/skills#skill-scopes)
- [Agent Skills format specification](https://agentskills.io/specification)
