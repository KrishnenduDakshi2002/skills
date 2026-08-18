# Issue tracker: Local Markdown

Store workflow artifacts under `.scratch/`:

```text
.scratch/<feature-slug>/spec.md
.scratch/<feature-slug>/issues/01-<slug>.md
.scratch/<feature-slug>/issues/02-<slug>.md
```

Use one file per issue, number issues in dependency order, and record blocking edges by number and title. Record workflow state as a `Status:` line near the top of each issue.

When a skill says to publish to the issue tracker, create the corresponding Markdown file and return its path. Do not combine multiple implementation tickets into one file.

