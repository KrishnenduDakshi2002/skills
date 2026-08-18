# CONTEXT.md format

Use a root `CONTEXT.md` for a single-context repository. If a root `CONTEXT-MAP.md` exists, use it to locate the relevant per-context glossary.

## Template

```markdown
# {Context Name}

{One or two sentences describing the context and why it exists.}

## Language

**Order**:
{A one- or two-sentence definition.}
_Avoid_: Purchase, transaction

**Invoice**:
A request for payment sent to a customer after delivery.
_Avoid_: Bill, payment request
```

## Rules

- Pick one canonical term and list rejected synonyms under `_Avoid_`.
- Define what a concept is in one or two sentences, not everything it does.
- Include only domain-specific concepts, not general programming terminology.
- Group terms under subheadings only when natural clusters emerge.

For multiple contexts, keep a root map:

```markdown
# Context Map

## Contexts

- [Ordering](./src/ordering/CONTEXT.md) — receives and tracks customer orders
- [Billing](./src/billing/CONTEXT.md) — generates invoices and processes payments

## Relationships

- **Ordering → Billing**: Ordering emits `OrderPlaced`; Billing consumes it.
```

When the current topic could belong to multiple contexts and the repository does not resolve the ambiguity, ask which context owns it.

