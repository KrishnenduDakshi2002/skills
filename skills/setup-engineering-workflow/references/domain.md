# Domain documentation

Tell engineering skills where to read domain language and durable decisions.

## Single-context layout

Use for most repositories:

```text
CONTEXT.md
docs/adr/
```

## Multi-context layout

Use only when the repository has genuine independent domains:

```text
CONTEXT-MAP.md
docs/adr/
src/<context>/CONTEXT.md
src/<context>/docs/adr/
```

Before exploring, read the relevant glossary and ADRs. Proceed silently when they do not exist. The `grill-with-docs` workflow creates them lazily when language or a durable decision is actually resolved.

Use glossary terms consistently and surface conflicts with existing ADRs instead of silently overriding them.

