# Workflow — add a product or feature

Goal: turn the user's raw context (a description, a doc, screenshots, a ticket, code) into one well-placed, well-structured knowledge-base entry, and save it only after the user approves the exact content.

Read `field-guide.md` before drafting. Run every command as `python3 <skill-directory>/scripts/kb_api.py …`.

## 1. Session and permission

`whoami` must exit 0 with `can.writeFeatures: true`. Otherwise follow `auth.md` or stop and tell the user which permission is missing.

## 2. Intake

Collect what the user gives you and pull facts out of it:

- Name of the capability and the area of TagMango it belongs to.
- The procedure (navigation path, exact UI labels, order of actions).
- Constraints, limits, plan availability, defaults, sizes, gotchas.
- Configurable settings and what each controls.
- Tutorial or help links, third-party integrations.

Keep a list of **open questions** for anything the material does not state. Do not fill gaps from general knowledge.

## 3. Placement

1. `products --limit 200` — list existing products (summaries include feature counts).
2. Pick the product whose scope contains the capability. If two fit, or none fits, ask the user; offer to create a product only when the capability is clearly a new area with several future features.
3. `search "<2–4 key words from the title>"` and, if useful, `features --product <id> --search <word>` — look for an existing entry covering the same thing. If one exists, tell the user and switch to `modify.md` instead of creating a duplicate.
4. Note vocabulary: if the user's terms differ from what the knowledge base already uses, plan a synonym mapping (see `synonyms.md`) rather than renaming.

## 4. Draft the payload

Write the desired document as JSON to a temporary file (for example `${TMPDIR:-/tmp}/mangomind-kb/<slug>.json`; never commit payload files). Use the field-by-field table and placement table from `field-guide.md`. Include `productId` for a feature; omit it for a product.

Ask the open questions now, in one batch of at most five, only where the answer changes the content (navigation path, plan availability, limits, settings, links). If the host agent offers a structured question capability, use it; otherwise ask in plain text. Fill answers in; leave nothing as a placeholder.

## 5. Validate and preview

```sh
kb_api.py validate --file <payload.json>
kb_api.py render --file <payload.json>
```

Fix every error (exit 4). Treat warnings as review prompts: duplicates, over-long items, whitespace. Show the user the rendered markdown exactly as printed, plus the target product name and id, and iterate until they are satisfied.

## 6. Approval gate

Ask for an explicit go-ahead to create the entry, naming the title and the product it will live under. Do not proceed on silence or on approval of an earlier draft. If the user wants to see the exact request first, run `upsert --file <payload.json> --dry-run`.

Then:

```sh
kb_api.py upsert --file <payload.json>
```

The script sends `updatedFields` for every embeddable section so the backend chunks and embeds the whole entry.

## 7. Report

State: created title, kind (product or feature), the new id, the parent product, and the dashboard link (`<dashboardUrl>/products/<productId>/features?searchWithId=<id>` for a feature, `<dashboardUrl>/products?searchWithId=<id>` for a product). List any facts the user chose to leave out and any suggested synonym mappings. Offer to verify with `search`.

## Creating a product

Only after the user confirms a new area is warranted. The product payload has no `productId`; its description explains the area and which capabilities its features will cover; steps are normally empty. Create the product first, take its id from the response, then create its features with that `productId`.

## Batches

For several entries from one source document: draft all payloads, present a short table (title → product) for placement approval, then validate, preview, and approve each entry individually before saving it. Stop and report on the first API error.
