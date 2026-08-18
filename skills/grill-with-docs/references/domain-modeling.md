# Domain modeling

Use this discipline while grilling. Challenge terminology, probe boundaries with scenarios, compare claims with code, and capture resolved language and decisions as they crystallize.

## Locate domain documentation

Most repositories use a single context:

```text
CONTEXT.md
docs/adr/
src/
```

If `CONTEXT-MAP.md` exists, use it to locate the relevant per-context `CONTEXT.md` files and context-specific ADR directories. Treat root `docs/adr/` as system-wide decisions.

Create files lazily. Create a glossary only after the first term is resolved and an ADR directory only after the first qualifying decision is accepted.

## Challenge the model

- When the user's terminology conflicts with the glossary, quote the conflict and ask which meaning is authoritative.
- When a term is fuzzy or overloaded, propose a precise canonical term and distinguish neighboring concepts.
- Invent concrete scenarios that probe edge cases and force boundaries to become explicit.
- Check stated behavior against the code. Surface contradictions instead of silently choosing one account.

## Maintain the glossary

Update the applicable `CONTEXT.md` immediately when a term is resolved. Read [context-format.md](context-format.md) before writing.

Keep `CONTEXT.md` free of implementation detail. It is a glossary, not a specification, decision log, or scratchpad.

## Record decisions sparingly

Offer an ADR only when all three conditions hold:

1. The decision is meaningfully expensive to reverse.
2. A future reader would find it surprising without context.
3. Genuine alternatives existed and the choice reflects a trade-off.

Read [adr-format.md](adr-format.md) immediately before writing an accepted ADR.

