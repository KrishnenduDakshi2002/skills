# Agent instructions

## Scope

Treat `skills/` as the canonical distribution source. Treat `.agents/skills/`, `.claude/skills/`, `.codex/skills/`, and `.cursor/skills/` as generated installation targets.

## Authoring rules

- Place every skill at `skills/<skill-name>/SKILL.md`.
- Match the folder name to the frontmatter `name` exactly.
- Use lowercase letters, digits, and hyphens for names; keep names under 64 characters.
- Use only `name` and `description` in YAML frontmatter by default. Add agent-specific fields only when their reduced portability is intentional and documented.
- For explicit-only task workflows, pair Claude Code's `disable-model-invocation: true` frontmatter with Codex's `policy.allow_implicit_invocation: false` in `agents/openai.yaml`. Treat this pair as an approved, reviewed portability exception.
- Put optional product-specific metadata under `agents/` rather than changing the shared workflow; other agents must still be able to use the skill without it.
- State what the skill does and every important trigger in `description`.
- Write the body as concise imperative instructions for another agent.
- Refer to capabilities rather than hard-coded agent tool names when possible.
- Keep one cross-agent workflow. Put necessary Claude Code, Codex, or other agent differences in directly linked reference files instead of duplicating the skill.
- Keep `SKILL.md` under 500 lines when practical. Move detailed material to directly linked files in `references/`.
- Add `scripts/` only for repeated or deterministic operations, and execute representative cases before considering them validated.
- Add `assets/` only for files consumed in generated output.
- Do not add a README, changelog, or installation guide inside an individual skill.

## Third-party skills

- Read the full upstream skill and bundled executable code before copying it.
- Verify the upstream license permits the intended use.
- Preserve required copyright and license notices.
- Pin the reviewed upstream revision in `THIRD_PARTY_NOTICES.md` and summarize local modifications.
- Do not present adapted third-party work as wholly original.

## Quality gates

Run `npm run check` after editing skills. It enforces paired Claude Code/Codex invocation controls and a carried license for selective installations. Treat portability warnings as decisions to review, not harmless noise. When network access is available, also run `npm run skills:list` to confirm Vercel Skills CLI discovery.
