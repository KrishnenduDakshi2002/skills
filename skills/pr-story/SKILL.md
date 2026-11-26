---
name: pr-story
description: Write a pull request's title and description as a plain-words story the owner understands at a glance, in the Layers story format - a Mermaid flowchart of what the product did before (red) and does now (green), or a few groups of very short lines, plus three one-line facts and a short spoken version - and validate it with the bundled checker before publishing. Use whenever creating a pull request, writing or editing a pull request's title or description, or pushing new commits to a branch that already has an open pull request, in any repository.
---

# PR Story

Write every pull request title and description so the owner understands the change without reading code. The owner reads them in Layers, their review app, which draws this format at the top of a review; GitHub shows it as ordinary markdown and renders the charts.

Read [format.md](references/format.md) before writing: it is the exact contract with Layers, including every cap. Read [examples.md](references/examples.md) for the shape of good stories and of a tangled chart to avoid.

A pull request is work already done. Say only what happened; never ask the reader to decide anything.

## Write the story

1. Work from the diff, not from memory of the session. Read the full change against its base branch, including its tests and any commits you did not write.
2. Find what a person experiences: who did what, what the product did before, and what it does now. Take the situation from the change's own tests or from the code path it changes. Never invent one.
3. Pick the layout:
   - Behaviour with branches: (a), one chart.
   - Use (b), a Before chart and a Now chart, when old and new share most of their steps or one chart would need edge labels like "before" or "now".
   - Renames, refactors, many small unrelated changes: (c), groups.
   - A change nobody can see, such as CI or an internal refactor: (c), with a first group saying nothing changes for users.
4. Draft the title, the layout, the three cells and the Listen text, within the caps in the format.
   - If the Listen text cannot tell the whole change in 105 words (about 40 seconds) without dropping something the reader needs, the pull request does too many things. Before opening it, split the work into smaller pull requests with more targeted changes, each with its own story; stack them when one depends on another.
   - On a pull request that is already open, do not rewrite its history on your own: publish the best story within the caps, and tell the owner in your reply that it should be split, with the split you propose.
5. Check every box, item and cell against the diff. Rewrite any that is not exactly what the code does, including edge cases the change handles; give each its own branch.
6. Use product words ("group", "scheduled message"), not internal ones ("cohort", "touch"). When an internal word cannot be avoided, add a few words of explanation.
7. Reread the whole body as someone who has never seen the code. Rewrite anything they could not follow.

Keep these out of everything visible: function, class, method, variable, enum, file and path names; formulas; test counts; commands run; "decide" questions. What a person sees or types is fine: a button label, a message text, an API route, a setting name. Mention tests only when something failed or was not tested, and then in plain words in the most fitting cell.

## Validate before publishing

Write the draft body to a temporary file outside the repository and run the bundled checker; `<skill-dir>` is the folder that holds this file:

```sh
node <skill-dir>/scripts/check-story.mjs <draft.md> --title "<title>"
```

- Fix every `ERROR` and rerun until it reports `OK`. Treat each `warn` as a decision to review.
- The checker flags likely code names. When it flags a real product or brand name, rerun with `--allow Name`; never use `--allow` for an identifier.
- Charts are parsed with the real Mermaid parser. The checker installs it into its own folder on first use (needs Node 22.13 or later, and network that once; checks run offline afterwards). Exit code 2 means it could not check: the output says why.
- Never publish a chart that does not parse or was not parsed. Fix it, or fall back to layout (c).
- The checker cannot tell whether a story is true. Steps 5 to 7 above stay your job.

## Publish

- Keep the repository's conventional title prefix and any ticket ids it requires.
- Put the story first. Any footer your own instructions require, a required template section, or ticket links go after the end marker.
- Pass the body from the validated file, for example `gh pr create --body-file <draft.md>` or `gh pr edit --body-file <draft.md>`, so quotes and fences reach the pull request unchanged.

## Keep it current

On every later push to a branch with an open pull request, reread the full diff of the pull request and rewrite the title and story to describe it as it now stands. Never append a changelog of pushes. Validate again before updating it.
