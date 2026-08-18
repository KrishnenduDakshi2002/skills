# ADR format

Store system-wide ADRs in `docs/adr/`. In a multi-context repository, follow the established context-specific ADR location. Scan existing ADRs and increment the highest four-digit prefix.

## Minimal template

```markdown
# {Short title of the decision}

{One to three sentences describing the context, decision, and reason.}
```

Add optional sections only when they preserve useful information:

- `Status` when a decision may be proposed, deprecated, or superseded.
- `Considered Options` when rejected alternatives are worth remembering.
- `Consequences` when non-obvious downstream effects matter.

Create an ADR only for an accepted choice that is hard to reverse, surprising without context, and based on a real trade-off. Do not record routine or obvious choices.

