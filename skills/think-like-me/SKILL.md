---
name: think-like-me
description: Apply the author's personal coding practices and rules while writing, modifying, or refactoring code. Use whenever producing code in any language, before writing the first line, or when the user says "think like me", "my style", or "follow my practices".
---

# Think Like Me

Write code the way I would. These are my practices, in my own words; apply them by default whenever you produce or change code for me. They guide writing, not reviewing — for a review, use a code-review skill instead.

## Mindset

- **Think ambitious.** Even on a small task, see the big picture: how does this change affect the overall architecture, optimization, and performance? Never be lazy about architecture — dig deeper and work harder to get it robust and clean.
- **Simple is the hard version — write it anyway.** Writing complicated code is easy; writing simple code is hard. Simple code is what makes everything easier to debug, understand, and discover, so do the hard work of finding the simple shape.
- **Bug-free is the goal.** Whether a human or an AI writes the code, correctness is non-negotiable. Solidity comes from strict types, simple structure, and reusing proven systems — not from hope.
- **Architect for other developers.** My code should be robust, thoughtful, and generic enough that others can build on it as a backbone without needing to fully understand its internals.

## Explore before writing

- Go into deep exploration mode first. Find every existing code block that can help with the current task and use it as your reference.
- Study how the existing system behaves — its consistencies, its pros, its cons. Take the pros into the new code; do not carry the cons forward.
- Reuse the canonical helper or primitive that already exists over writing a near-duplicate.
- Look for the "code judo" move: a reframing of the problem that makes whole branches, helpers, modes, or layers unnecessary. Aim for code that feels inevitable in hindsight.

## Design

- **Shared over scattered.** If something can be made generic and shared across code blocks, make it shared — especially when that prevents drift between multiple localized versions of the same or similar logic.
- **Right home.** Put logic in the layer that owns the concept. Do not leak feature-specific logic into shared paths or implementation details through APIs.
- **Discoverability.** If new code could look disconnected from the primary flow or be hard to find, link it into the existing, most common flows so the next person naturally discovers it.
- **When blocked, step back.** If a core architecture decision becomes a blocker, don't hack around it. Question the decision: is it scalable enough, robust enough, optimized enough? Follow the path that makes the goal more scalable and robust.
- Measure success by how few concepts a reader must hold in their head, not by how the diff looks.

## Red flags and green flags

Interrogate every addition — a code block, variable, type, module, file, or spec — with this lens:

**Red flags.** An addition that cannot justify itself:

- It provides no clear benefit, or nobody can say what the benefit is.
- Its impact on the existing code is negative — it degrades the structure, or its performance delta is negative with nothing gained in return.
- It serves only its narrow moment instead of the greater good of the codebase.
- It is an escape hatch: a workaround chosen instead of finding the better solution, bought at the cost of the current code architecture. When you catch yourself writing one, go back to the design and find the solution that doesn't destroy the structure.

**Green flags.** Localized code with the potential to become something better for everyone:

- A small localized function that could become a shared utility with more generic options others can use.
- A localized constant, type, or pattern that others will plausibly need.

When you spot a green flag, promote it: extract the shared, more robust version instead of leaving the localized copy to drift — or if promoting it now is out of scope, say so explicitly so the potential isn't lost.

## While writing

- **The least code that fulfills the behavior.** Without losing any behavior, ask how little code this can be. Less code never means ugly or cryptic — it means the bare minimum that is readable, correct, and simple. Solving a problem with a flood of code is not my style.
- **The strictest types I can have.** Strict types make code solid and less buggy. Avoid `any`, `unknown`, unnecessary optionality, and cast-heavy code; never paper over an unclear invariant with a silent fallback — make the boundary explicit.
- **Pure functions by default.** Same input, same output, no hidden side effects. Push I/O and mutation to the edges.
- **Immutability.** Return new values (spread, `map`, `filter`) instead of mutating arguments or shared state.
- **Composition over inheritance.** Small functions piped together; no deep class hierarchies.
- **Small units.** Functions under ~50 lines, modules focused on one job. Extract instead of appending — never push a file past ~1000 lines when the new code could be its own module.
- **Explicit dependencies.** Pass collaborators in as parameters; never reach for globals or module-level state inside core logic.
- **Early returns over nesting.** Handle the edge case and get out; keep the happy path at the lowest indentation.
- **No spaghetti growth.** Do not bolt one-off conditionals, booleans, nullable modes, or special cases into unrelated flows. Treat "temporary" branching as permanent debt.
- **Repeated conditionals mean a missing model.** When the same condition chain shows up more than once, replace it with a typed model or explicit dispatcher instead of copying the branches.
- **Separate orchestration from business logic.** Keep the "what to do" pure and testable, and the "when/in what order" thin at the edges.
- **Keep flows parallel and atomic.** Do not serialize independent async work for no reason, and do not structure related updates so state can be left half-applied.

## Naming

- Name variables, files, functions, and modules for the bigger picture, not the immediate small task. A later addition that belongs in this module should feel like it belongs — never repelled by a name scoped to the original narrow use case.
- Files: `lowercase-with-dashes`
- Functions: verb phrases (`getUser`, `validateEmail`)
- Predicates: `isValid`, `hasPermission`, `canAccess`
- Constants: `UPPER_SNAKE_CASE`; variables descriptive and `const` by default

## Comments

- Comments are a special thing, not a routine one. The variables, function names, logic, and architecture should tell the whole story — comments must never be what guides the reader through the code.
- Write a comment only when the behavior cannot be fully expressed through code, syntax, and naming — or when a function carries a deeper meaning that is genuinely easier to follow in prose. In that case write it properly: the reasoning behind the behavior and how the code is meant to be used.

## Before finishing

- Ask: could I easily test this? If not, restructure until you could — untestable code is a design smell even when it works.
- Run the narrowest relevant check the repo provides (typecheck, lint, focused tests) and report results honestly.
- Re-read the diff as another developer would: every line should look like it always belonged there, and they should be able to build on it without reading its internals.
