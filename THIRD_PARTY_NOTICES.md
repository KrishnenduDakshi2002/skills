# Third-Party Notices

Record every redistributed or adapted public skill here before publishing it.

| Local skill | Upstream source and path | Reviewed revision | License | Local modifications |
| --- | --- | --- | --- | --- |
| `grill-with-docs` | `mattpocock/skills`: `skills/engineering/grill-with-docs` plus its `grilling` and `domain-modeling` dependencies | `9c9f36ccd3995266cd675468af71639c8dde1ec5` | [MIT](licenses/mattpocock-skills/LICENSE) | Inlined the dependent workflows and references; replaced tool-specific skill dispatch with capability-based instructions; retained explicit invocation semantics for Claude Code and Codex. |
| `to-spec` | `mattpocock/skills`: `skills/engineering/to-spec` | `9c9f36ccd3995266cd675468af71639c8dde1ec5` | [MIT](licenses/mattpocock-skills/LICENSE) | Generalized tracker discovery and setup guidance, added a local fallback, and retained explicit invocation semantics for Claude Code and Codex. |
| `to-tickets` | `mattpocock/skills`: `skills/engineering/to-tickets` | `9c9f36ccd3995266cd675468af71639c8dde1ec5` | [MIT](licenses/mattpocock-skills/LICENSE) | Generalized tracker operations and setup guidance, added a local fallback, and retained explicit invocation semantics for Claude Code and Codex. |
| `implement` | `mattpocock/skills`: `skills/engineering/implement` plus its `tdd`, `code-review`, and `codebase-design` dependencies | `9c9f36ccd3995266cd675468af71639c8dde1ec5` | [MIT](licenses/mattpocock-skills/LICENSE) | Inlined the complete testing, mocking, seam-design, and two-axis review guidance; added validation and blocker handling; removed automatic commits and tool-specific slash-command assumptions. |
| `setup-engineering-workflow` | `mattpocock/skills`: `skills/engineering/setup-matt-pocock-skills` and its configuration templates | `9c9f36ccd3995266cd675468af71639c8dde1ec5` | [MIT](licenses/mattpocock-skills/LICENSE) | Renamed and generalized for Claude Code, Codex, GitHub, GitLab, local Markdown, and user-defined trackers; made shared configuration the cross-agent source of truth. |
| `thermo-nuclear-code-quality-review` | `cursor/plugins`: `cursor-team-kit/skills/thermo-nuclear-code-quality-review` | `3347cbab5b54136f6fba0994c3a01a56f7fb7fca` | [MIT](licenses/cursor-plugins/LICENSE) | Preserved the full review rubric; clarified that review is read-only until fixes are requested; added Codex UI and explicit-invocation metadata. |

For licenses that require carrying their text, add the exact upstream license file under `licenses/<source-name>/` and link it from the table. Every redistributed skill must also carry the required license text inside its own directory so selective Skills CLI installations preserve the notice.
