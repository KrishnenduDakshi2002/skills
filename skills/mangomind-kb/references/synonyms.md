# Workflow — synonym mappings

Synonym mappings teach the support bot's query preprocessor that a creator's wording means a canonical knowledge-base term (for example a whitelabel brand calling a "Mango" a "Service"). They are a separate collection from products and features. Run every command as `python3 <skill-directory>/scripts/kb_api.py synonyms …`.

## Model

| Field | Meaning |
|---|---|
| `canonical` | The term the knowledge base uses. **Unique** across mappings; the API rejects a second mapping with the same canonical. |
| `synonyms` | Terms creators say. Dashboard convention: the canonical term is also listed here, and the script enforces it. |
| `mappingType` | `equivalent` (default) — all terms are interchangeable in both directions. `explicit` — the synonyms map to the canonical term one way only. Use `equivalent` unless the user asks otherwise. |
| `description` | Optional sentence that helps the language model understand the concept. |

Writes require `write:features`; reads require `view:features`.

## Commands

| Need | Command |
|---|---|
| Browse or search | `list [--search <word>] [--canonical <term>] [--type equivalent\|explicit] [--limit N]` |
| One mapping | `get <id>` |
| Create | `create --canonical <term> --synonym <term> --synonym <term> … [--description "…"] [--type …] [--dry-run]` |
| Update | `update <id> [--canonical <term>] [--synonym … --synonym …] [--description "…"] [--type …] [--dry-run]` — `--synonym` replaces the whole list |
| Delete | `delete <id>` previews; `delete <id> --yes` deletes |

## Workflow

1. **Check first.** `list --search <term>` for both the canonical and each proposed synonym. If a mapping already owns the canonical, extend it with `update` instead of creating a second one. If a proposed synonym already belongs to another mapping, ask the user which concept it should resolve to; one term should not point at two canonicals.
2. **Draft** the mapping with the canonical term spelled exactly as the knowledge-base entries use it (verify with `search` against features). Lower-case, singular forms are the norm; keep brand-specific casing only if the entries use it.
3. **Preview** with `--dry-run` and show the user the canonical, the full synonym list, the type, and the description.
4. **Approve, then save.** For `update`, show the current mapping (returned in the dry run) next to the new list, since the list is replaced wholesale.
5. **Delete** only after reading back the mapping's canonical and synonyms and getting a confirmation that names it.

## When to suggest synonyms

- After creating or renaming a feature whose title uses a term creators may phrase differently.
- When the user mentions whitelabel or brand-specific vocabulary.
- When a `search` for the user's wording misses an entry that a canonical term finds.

Suggest; do not create synonyms without the user's approval.
