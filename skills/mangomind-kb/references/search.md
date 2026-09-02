# Workflow — search, browse, export, and answer coverage questions

Read-only. Requires `view:features` (or `admin`). Run every command as `python3 <skill-directory>/scripts/kb_api.py …`.

## Commands

| Need | Command | Notes |
|---|---|---|
| All products | `products [--search <title-part>] [--limit N]` | Summaries with per-field item counts; `--full` for whole documents. |
| Features of one product | `features --product <id> [--search <title-part>]` | Also returns the product summary. Title filter only. |
| One entry | `get <id>` | Full document. |
| Full-text search | `search "<words>" [--limit N]` | Atlas Search over title, description, steps, notes and other text; returns `searchScore` and `matchedFields` (`path`, `matchedText`, `matchedWords`). |
| Human-readable view | `render --id <id>` | Markdown in the dashboard's section order. |
| Word export | `export --out <file.docx> [--product <id>]` | Same document the dashboard's "Export Knowledge Base" button produces. |

`products` and `features` filter by title only; use `search` for anything inside the content. Server-side paging of `products` and `features` is unreliable (the API skips by page number, not by page size), so request one page with a large `--limit` instead of walking pages.

## Interpreting search results

- `nodeType` tells you whether a hit is a product or a feature; `product` is the parent id for features.
- `matchedFields[].path` names the field that matched (`title`, `steps`, `notes`, `settings.description`…); `matchedWords` are the exact tokens that hit. Quote `matchedText` when telling the user why an entry matched.
- The search is lexical. Try two or three phrasings and known synonyms (`synonyms list --search <word>` shows the canonical vocabulary) before concluding something is missing.

## Answering "does the knowledge base cover X?"

1. `search` with the user's phrasing, then with the canonical TagMango term if a synonym mapping exists.
2. Open the strongest hits with `get` and check whether the specific fact is present in `steps`, `notes`, `rules`, or `settings`.
3. Report: covered (where, quoting the item), partially covered (what is missing), or not covered. Offer to add or modify via `add.md` / `modify.md`; do not change anything in this workflow.

## Browsing for review

To review an area end to end: `features --product <id> --limit 200`, then `render --id` on each entry the user cares about, or `export --product <id>` for offline reading. Point out inconsistencies you notice (duplicated facts across features, steps written as notes, missing plan information) as suggestions, not as edits.

## Dashboard links

- Feature: `<dashboardUrl>/products/<productId>/features?searchWithId=<featureId>`
- Product: `<dashboardUrl>/products?searchWithId=<productId>`

`configure` prints the configured `dashboardUrl`.
