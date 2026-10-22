---
name: mangomind-kb
description: Manage TagMango's MangoMind knowledge base — the products and features the AI support bot answers from — through the admin API instead of the dashboard forms. Use when asked to add, document, write up, update, correct, restructure, move, search, browse, export, or delete MangoMind knowledge-base products or features, to check whether the knowledge base covers a topic, or to manage synonym mappings for the support AI. Handles dashboard sign-in as a prerequisite, decides product-versus-feature placement, drafts the structured entry (title, description, steps, notes, rules, settings, plan, media, integrations), previews it, and writes to the API only after explicit approval.
argument-hint: "[add | modify | search | synonyms | auth] <what you want done>"
---

# MangoMind Knowledge Base

MangoMind is TagMango's internal support-AI console. Its knowledge base is a tree of **products** (areas of TagMango) containing **features** (capabilities). Every item in a feature — each step, note, rule, setting, media label — is chunked and embedded, then retrieved to answer creators on WhatsApp and Intercom. This skill replaces the dashboard's field-by-field forms with a conversation: gather context, decide placement, draft the structured entry, preview, get approval, call the API.

All API access goes through one dependency-free script:

```sh
python3 <skill-directory>/scripts/kb_api.py <command> …
```

Every command prints JSON (previews print markdown). Exit codes: `0` ok · `1` API or usage error · `2` not signed in · `3` missing permission · `4` payload failed local validation.

## Ground rules

1. **Sign-in is the prerequisite.** Start every session with `whoami`. On exit `2` follow [auth.md](references/auth.md) before anything else; on exit `3` stop and tell the user which permission is missing. Never ask the user to paste a token into the chat, and never print the credentials file.
2. **Nothing is written without an explicit approval of the exact content.** Always show the rendered preview (`render`) and, for edits, the diff (`diff`) first, then ask for a go-ahead that names the entry. Approval of an earlier draft does not carry over. Deletes need a second confirmation that names the entry; deleting a product deletes every feature under it.
3. **Placement is a decision, not a guess.** Product versus feature, and which product, follow [field-guide.md](references/field-guide.md); when two placements are plausible, ask. Never create a product silently.
4. **Record only what the user supplied or pointed you at.** Gaps become questions (batched, at most five at a time, only where the answer changes content). No filling in from general knowledge.
5. **Check before creating.** Search for an existing entry first; prefer modifying it over adding a near-duplicate.
6. **Write for retrieval.** Every list item stands alone and states one fact; follow the style rules in the field guide.
7. **Payload files are scratch.** Keep them in a temporary directory; never commit them. Report ids and dashboard links, not file paths.

## Workflows

Read the field guide before drafting or editing content, then the workflow file for the request:

| Request | Read | Core commands |
|---|---|---|
| Sign in, switch account, fix "not authenticated" | [auth.md](references/auth.md) | `configure`, `login`, `whoami`, `logout` |
| Add a feature or product from a description, doc, ticket, or screenshots | [field-guide.md](references/field-guide.md), then [add.md](references/add.md) | `products`, `search`, `validate`, `render`, `upsert` |
| Change, correct, rename, move, split, or delete an entry | [field-guide.md](references/field-guide.md), then [modify.md](references/modify.md) | `get`, `diff`, `render`, `upsert --id`, `delete` |
| Find, browse, export, or check coverage of a topic | [search.md](references/search.md) | `products`, `features`, `search`, `get`, `render`, `export` |
| Add or fix how creator vocabulary maps to knowledge-base terms | [synonyms.md](references/synonyms.md) | `synonyms list / create / update / delete` |

Mixed requests ("document this and make sure 'service' resolves to it") compose workflows in order: content first, then synonyms, each with its own preview and approval.

## How the script protects the data

- `upsert` validates the payload locally, refuses a `productId` that points at a feature, derives `nodeType`, and for updates fetches the live document, merges the payload field by field, and sends `updatedFields` only for sections that changed so the backend re-embeds exactly those. It reports `skipped` when nothing differs. `--dry-run` prints the exact request.
- `delete` and `synonyms delete` only preview until `--yes` is passed; the product preview includes the number of features that would be removed with it.
- `render` and `diff` are the preview surface: markdown in the dashboard's section order, and a per-field `+` / `-` / `~` change list ending with the sections to be re-embedded.

## Reporting

Close every task with: what was created, changed, or deleted (title, kind, id, parent product), the dashboard link (`<dashboardUrl>/products/<productId>/features?searchWithId=<id>` for a feature, `<dashboardUrl>/products?searchWithId=<id>` for a product), the sections re-embedded, any facts the user chose to leave out, and suggested follow-ups such as synonym mappings. Separate what was verified by an API response from what was inferred.
