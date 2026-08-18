# Agent Skills

A curated collection of portable agent skills for Claude Code, Codex, and other agents supported by the open Agent Skills ecosystem. The collection may include both original skills and carefully adapted skills from public repositories.

## Repository layout

```text
skills/
  <skill-name>/
    SKILL.md
    agents/openai.yaml   # optional Codex UI and invocation metadata
    scripts/             # optional deterministic helpers
    references/          # optional on-demand context
    assets/              # optional output resources
scripts/
  validate-skills.mjs
THIRD_PARTY_NOTICES.md
```

Keep each skill self-contained. Do not place installation instructions, changelogs, or repository-level documentation inside a skill directory.

## Portability baseline

- Use only `name` and `description` in `SKILL.md` frontmatter by default.
- For manually invoked workflows that target Claude Code, use `disable-model-invocation: true` and pair it with `policy.allow_implicit_invocation: false` in `agents/openai.yaml` for Codex. This is the collection's approved cross-agent frontmatter exception.
- Keep product-specific metadata under `agents/` so agents that do not understand it can ignore it without changing the shared skill.
- Avoid fixed assumptions about an agent's tool names, permission model, slash commands, hooks, or subagent support.
- Describe required capabilities in plain language and let the active agent select its available tools.
- Put unavoidable agent-specific guidance in a directly linked file such as `references/claude-code.md` or `references/codex.md`, and tell the agent when to read it.
- Keep one shared skill unless the workflows genuinely have different semantics. Do not create per-agent copies merely for different installation paths.

Agent-specific frontmatter may be ignored or interpreted differently by other agents. The local validator reports it as a portability warning.

## Create an original skill

Start from the Vercel Skills CLI template:

```bash
npm run skill:init -- my-skill
```

Then replace the generated placeholders with a concise, imperative workflow. Put all trigger conditions in the frontmatter `description`, because agents use it to decide whether to load the skill.

## Adapt a public skill

1. Review the complete upstream skill, bundled resources, and executable scripts.
2. Confirm that its license permits redistribution and modification.
3. Copy only the files needed for the skill to work.
4. Record the upstream repository, path, revision, license, and local changes in `THIRD_PARTY_NOTICES.md`.
5. Validate the adapted skill as if it were an original skill.

Do not assume that `skills update` will merge upstream changes into an adapted copy. Once copied here, this repository becomes the installation source for that copy.

## Validate and test discovery

Run the local structural checks:

```bash
npm run check
```

This also checks that explicit-only workflows are protected consistently in Claude Code and Codex and that every selectively installed skill carries a license.

Ask the Vercel Skills CLI to discover the collection:

```bash
npm run skills:list
```

Test one skill locally with multiple supported agents:

```bash
npx skills@latest add . --skill my-skill -a claude-code -a codex
```

This creates agent-specific installation targets in the current repository. They are ignored by Git. Use a throwaway consumer repository when testing additional agents so generated files do not clutter this authoring repository.

## Install after publishing

```bash
npx skills@latest add <owner>/<repository>
```

To install a specific skill:

```bash
npx skills@latest add <owner>/<repository> --skill my-skill
```

## Licensing

Choose a license for original work before publishing this repository. Third-party skills remain subject to their upstream licenses and notices. Each adapted skill carries its required upstream license so selective installations preserve attribution.
