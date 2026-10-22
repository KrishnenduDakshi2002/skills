# Field guide — what goes where, and how to write it

Read this before drafting or editing any product or feature. Retrieval quality of the support bot depends directly on how content is split across these fields.

## The document model

One collection holds both **products** and **features**; they share one shape and differ only by parent:

- **Product** — a top-level area of TagMango (for example "Courses", "Mango / Service", "Marketing", "Payouts"). Has no `productId`. Its own document describes the area at a high level.
- **Feature** — one capability inside a product (for example "Course drip", "Coupon codes"). Has `productId` pointing at exactly one product. This is where how-to content lives.

The server derives `nodeType` from the presence of `productId`; never set it by hand.

## How retrieval consumes the content

When a document is saved, the backend deletes and regenerates the chunks for every field listed in `updatedFields` (the script computes this list):

- `title` and `description` each become one chunk.
- **Every item** in `steps`, `notes`, `rules`, and `additionalGuide` becomes its own chunk.
- Each `settings` item becomes one chunk of the form `label: description`.
- Each `media` item becomes one chunk of the form `label: url`.
- `integrations` and `plan` are stored and shown, but not embedded.
- A second, "contextual" chunk set is regenerated for the whole feature on every save.

Consequences:

1. **Each list item must stand alone.** A step that says "Then click Save" without context retrieves poorly; "In the Drip settings panel, click Save to apply the schedule" retrieves well.
2. **One fact per item.** Do not pack three tips into one note.
3. **Titles carry vocabulary.** The title is a retrieval chunk; use the name creators actually say, and put common alternates in synonyms (see `synonyms.md`), not in the title.
4. **Descriptions are self-contained summaries**, one to three sentences: what the feature does, who uses it, and the outcome.

## Field by field

| Field | Type | Embedded | Put here | Style |
|---|---|---|---|---|
| `title` | string, required | yes | The feature or product name as creators say it | Noun phrase, Title Case, under ~60 chars. No trailing punctuation. |
| `description` | string, required | yes | What it is, for whom, what outcome | 1–3 plain sentences. No steps here. |
| `steps` | string[] | yes, per item | The ordered procedure to do the main thing | Imperative, one action each, start with a navigation path when relevant ("Go to Dashboard > Courses > <course> > Settings"). Name UI labels exactly as shown. |
| `notes` | string[] | yes, per item | Tips, gotchas, sizes, defaults, use cases, behaviors that are not steps | One fact each, full sentence. |
| `rules` | string[] | yes, per item | Hard constraints, limits, eligibility, things that cannot be done | Declarative "must / cannot / only" sentences. |
| `settings` | {label, description}[] | yes, per item | Each configurable option the UI exposes | `label` = exact UI label; `description` = what it controls and its effect. |
| `plan` | string[] | no | Plans where the feature is available | Use existing plan names found in other entries; check with `search` before inventing one. |
| `integrations` | string[] | no | Third-party services involved (Pabbly, Zapier, Zoom, Razorpay…) | Proper names only. |
| `media` | {label, url}[] | label only | Tutorial videos, help articles, templates | `label` describes what the viewer learns; `url` absolute http(s). |
| `additionalGuide` | string[] | yes, per item | Longer supporting prose, troubleshooting sequences | Use sparingly: the dashboard form has no editor for it and its viewer shows only the heading, so content here is invisible to dashboard-only editors. Prefer `notes`. |

The bot answers in short WhatsApp-style messages and may quote a single item, so write every item so it reads correctly out of context and without internal jargon.

## Placement decision table

| The source material says… | It belongs in |
|---|---|
| "To do X: open A, click B, then C" | `steps` (one item per action) |
| "You can also…", "Recommended size is…", "By default…", "Use this when…" | `notes` |
| "Only on plan Y", "Maximum N", "Cannot be undone", "Requires…" | `rules` (plan names additionally in `plan`) |
| A toggle, dropdown, or input the creator configures | `settings` |
| "Watch this video", "See the help doc" | `media` |
| "Works with Zapier / Pabbly / Zoom" | `integrations` (and a `note` on how, if given) |
| A whole new capability in the same area | a **separate feature**, not more items |
| A new area of the product with several capabilities | a **new product**, after the user confirms |

## Content rules

- Only record facts the user provided or that come from material they pointed you at (docs, screenshots, code, tickets). Ask about anything else; never fill gaps from general knowledge of similar products.
- Keep TagMango terminology from the existing knowledge base: search for a related feature and reuse its wording for shared concepts (e.g. "Mango", "custom host", "storefront").
- Never duplicate the same fact across two features; link concepts through the shared product instead.
- No marketing language, no emojis, no first person.
- URLs must be absolute and reachable; do not shorten or rewrite them.
- Preserve item order in `steps` exactly as the procedure runs.

## Example feature payload

```json
{
  "productId": "66c4964c11e7fef26751f3a7",
  "title": "Course Drip Schedule",
  "description": "Release course chapters to learners on a schedule instead of all at once. Creators set a delay per chapter so content unlocks progressively after enrollment.",
  "steps": [
    "Go to Dashboard > Courses and open the course you want to schedule.",
    "Open the Settings tab and turn on Drip Content.",
    "For each chapter, set the number of days after enrollment when it unlocks.",
    "Click Save to apply the schedule to all current and future learners."
  ],
  "notes": [
    "Learners who enrolled before drip was enabled see chapters unlock relative to their original enrollment date.",
    "A chapter with a 0-day delay is available immediately after enrollment."
  ],
  "rules": [
    "Drip delays apply per chapter and cannot be set per learner.",
    "Changing a delay does not re-lock chapters a learner has already opened."
  ],
  "settings": [
    { "label": "Drip Content", "description": "Master toggle that enables scheduled chapter release for the course." },
    { "label": "Unlock after (days)", "description": "Days after enrollment when the chapter becomes available." }
  ],
  "plan": ["Freedom", "Enterprise"],
  "integrations": [],
  "media": [
    { "label": "Video: setting up drip content for a course", "url": "https://help.tagmango.com/courses/drip" }
  ],
  "additionalGuide": []
}
```

A product payload has the same shape without `productId`; its `steps` are usually empty and its `description` explains the area and what its features cover.
