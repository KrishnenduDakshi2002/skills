# Layers story format, v1

### Title
`<type>(<scope>): <headline>` — keep the repository's conventional prefix and any ticket ids it requires. The headline is the outcome in plain words, at most 12 words, no code names. Layers shows the kind from the type: `fix` = bug fix, `feat` = new, anything else = change.

### Body
Everything Layers reads sits between two markers. Anything after the end marker (a required footer, ticket links) is left as ordinary markdown.

```
<!-- layers:story v1 -->

ONE OF:
  (a) one Mermaid flowchart                            — behaviour with branches
  (b) **Before** + flowchart, then **Now** + flowchart — when one chart would tangle
  (c) groups: `#### Title` then `- item` lines          — no diagram fits

**Applies to:** …
**Existing data:** …
**Who notices:** …

<details>
<summary>Listen</summary>

The spoken version.

</details>

<!-- /layers:story -->
```

### Diagram rules
- `flowchart TD`, at most 11 nodes per chart.
- Every label in double quotes, at most 9 words, plain product words, no code names, no double quotes inside a label: `A["The creator approves Ruby's plan"]`, decisions `B{"Does it start?"}`.
- The path the product took before carries `:::old`; the path it takes now carries `:::new`; unchanged steps carry nothing. In layout (b) the Before chart may use `:::old` and the Now chart `:::new` on the steps that differ.
- Edge labels short: `-->|yes|`, `-->|no|`.
- Edge cases the change handles are their own branches.
- End every chart with exactly these two lines (GitHub uses them for colour; Layers replaces them with its own theme):
```
  classDef old fill:#fdecec,stroke:#d93036,stroke-dasharray:5 3,color:#1c1c1f
  classDef new fill:#e8f6ef,stroke:#218358,color:#1c1c1f
```
- Use layout (b) when the old and new paths share most of their steps, or the single chart would need edge labels like "before" / "now" to tell them apart.

### Groups (layout c)
At most 4 groups, each a `#### ` title and at most 4 `- ` items; each item at most 10 words. Quote the exact words a user now sees when that is the point.

### The three cells
Each one line, at most 18 words, all three always present:
- **Applies to:** new things only, or already-running ones too.
- **Existing data:** what happens to stored data ("Nothing stored changes" is fine).
- **Who notices:** who sees a difference, and what.

### Listen
The whole change as spoken English, at most 60 words, no symbols, no code names.

### Never, anywhere visible
Function, class, method, variable, enum, file or path names; formulas; test counts; commands run; "decide" questions. Allowed: what a person sees or types (a button label, a message text, an API route, a setting name). Nothing about tests unless something failed or was not tested — then say so in plain words in the most fitting cell.
