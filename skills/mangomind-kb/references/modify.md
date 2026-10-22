# Workflow — modify, move, or delete

Goal: apply the user's requested change to an existing entry with a clear before/after, and save only after approval. Run every command as `python3 <skill-directory>/scripts/kb_api.py …`.

## 1. Session and permission

`whoami` must exit 0 with `can.writeFeatures: true`; otherwise see `auth.md`.

## 2. Locate the entry

- Given an id: `get <id>`.
- Given a name or topic: `search "<words>"`, then `products` / `features --product <id> --search <word>` to narrow. Results include `nodeType`, `product`, and `matchedFields` (which field matched and the matched words).
- Several plausible matches: show titles with their products and ask the user to pick. Never edit a guess.

Save the `get` output as the baseline (for example `${TMPDIR:-/tmp}/mangomind-kb/<id>.before.json`).

## 3. Build the desired document

Copy the baseline, apply the change following `field-guide.md`, and save it as the payload. Sending the full desired document keeps the preview complete; the script merges by field, so a payload containing only the changed fields is also accepted and leaves the other fields untouched.

Typical edits:

- **Correct or add a fact** → edit or append the item in the right field (steps for procedure, notes for behavior, rules for constraints, settings for options).
- **Rename** → change `title`; consider a synonym mapping so the old term still resolves (see `synonyms.md`).
- **Move a feature to another product** → set `productId` to the new product id. Confirm the target is a product (`get <id>` shows no `product` field).
- **Split** → trim the source entry and create the new entry via `add.md`; approve both.

Do not convert a product into a feature or vice versa unless the user explicitly asks and, for a product, it has zero features (`features --product <id>` total is 0). Re-parenting a product that still has children leaves those children pointing at a feature.

## 4. Preview the change

```sh
kb_api.py validate --file <payload.json> --id <id>
kb_api.py diff --id <id> --file <payload.json>
kb_api.py render --file <payload.json>      # full desired document, when the payload is complete
```

Show the diff verbatim: removed items are prefixed `-`, added `+`, order changes `~`, and the closing line lists the sections that will be re-chunked and re-embedded (`updatedFields`). Iterate until the user is satisfied.

## 5. Approval gate and save

Ask for an explicit go-ahead naming the entry title and summarising the change. Then:

```sh
kb_api.py upsert --id <id> --file <payload.json>
```

The script recomputes the diff against the live document at save time and sends only the changed sections in `updatedFields`. If nothing differs it reports `skipped` and makes no request. Use `--dry-run` to show the exact request first when asked.

## 6. Delete

```sh
kb_api.py delete <id>          # preview only: kind, title, and for a product the number of features under it
```

Deleting a **product cascades**: every feature under it and all their chunks are removed. Deletion is irreversible; there is no trash. Read the preview back to the user with the exact title, the kind, and the child count, and require a confirmation that names the entry. Only then:

```sh
kb_api.py delete <id> --yes
```

## 7. Report

State the entry, the fields changed (from the diff), the re-embedded sections, and the dashboard link (`<dashboardUrl>/products/<productId>/features?searchWithId=<id>` for a feature, `<dashboardUrl>/products?searchWithId=<id>` for a product). For deletions, state what was removed including cascaded features.
