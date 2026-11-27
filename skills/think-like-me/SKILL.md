---
name: think-like-me
description: Apply the author's coding practices for maintainable architecture, DRY ownership, derived types, data-driven behavior, reviewable code, precise naming, purposeful comments, and readable layout. Use whenever writing, modifying, or refactoring code in any language, before writing the first line, or when the user says "think like me", "my style", "follow my practices", or complains about duplication, hard-coded behavior, maintainability, congested or hard-to-review code, vague names, or noisy comments.
---

# Think Like Me

Write code the way I would. These are my practices, in my own words; apply them by default whenever you produce or change code for me. They guide writing, not reviewing — for a review, use a code-review skill instead.

## Mindset

- **Think ambitious.** Even on a small task, see the big picture: how does this change affect the overall architecture, optimization, and performance? Never be lazy about architecture — dig deeper and work harder to get it robust and clean.
- **Simple is the hard version — write it anyway.** Writing complicated code is easy; writing simple code is hard. Simple code is what makes everything easier to debug, understand, and discover, so do the hard work of finding the simple shape.
- **Bug-free is the goal.** Whether a human or an AI writes the code, correctness is non-negotiable. Solidity comes from strict types, simple structure, and reusing proven systems — not from hope.
- **Architect for other developers.** My code should be robust, thoughtful, and generic enough that others can build on it as a backbone without needing to fully understand its internals.
- **Working is not the bar.** Code that works but leaves the codebase messier is not done. If behavior can stay the same while the structure becomes meaningfully cleaner, write the cleaner version.
- **Do the design work now.** Do not choose copy-paste, a parallel type, or a hard-coded case merely because it is quicker to write. Trace the owning concept and its consumers; finish the maintainable implementation within the task's scope instead of leaving an avoidable cleanup TODO.

## Explore before writing

- Go into deep exploration mode first. Find every existing code block that can help with the current task and use it as your reference.
- Study how the existing system behaves — its consistencies, its pros, its cons. Take the pros into the new code; do not carry the cons forward.
- Reuse the canonical helper or primitive that already exists over writing a near-duplicate.
- Before adding a type, constant, mapping, or branch, search for the same domain concept and its existing consumers, even when they use different names. Identify what is authoritative and what can be derived from it.
- Look for the "code judo" move: a reframing of the problem that makes whole branches, helpers, modes, or layers unnecessary. Aim for code that feels inevitable in hindsight.
- **Measure twice, cut once.** Before committing to a shape, ask once more whether it is the simplest one — the cost of a wrong shape is paid by everyone who touches the file afterwards.

## Design

- **Shared over scattered.** Give each shared rule one owner and make its consumers use it. Extract the smallest abstraction that removes real duplication; parameterize actual differences, not hypothetical future needs.
- **Right home.** Put logic in the layer that owns the concept. Do not leak feature-specific logic into shared paths or implementation details through APIs.
- **Discoverability.** If new code could look disconnected from the primary flow or be hard to find, link it into the existing, most common flows so the next person naturally discovers it.
- **Delete complexity, don't rearrange it.** Moving the same conditionals into a new helper has not simplified anything. Prefer reframing the state model or ownership boundary so the conditionals disappear, and prefer removing a moving piece over centralizing it.
- **When blocked, step back.** If a core architecture decision becomes a blocker, don't hack around it. Question the decision: is it scalable enough, robust enough, optimized enough? Follow the path that makes the goal more scalable and robust.
- Measure success by how few concepts a reader must hold in their head, not by how the diff looks.

## DRY: own knowledge once

- **One fact, one authoritative definition.** Keep business rules, supported variants, defaults, constraints, and field definitions in the layer that owns them. Derive dependent representations instead of maintaining synchronized copies. DRY applies to knowledge, not just repeated lines.
- **Follow the reason to change.** Share code when consumers express the same rule and should change together. Similar-looking code for independently evolving concepts should remain separate; do not couple unrelated domains just to remove matching syntax.
- **Complete the reuse.** When extracting a shared rule, migrate the affected consumers in scope and remove their superseded copies. A new helper beside the old implementations has not solved duplication. Identify any necessary follow-up outside scope explicitly.
- **Keep boundaries deliberate.** Independent public contracts, persistence models, and security allowlists may need explicit definitions and mappings. Share stable concepts where appropriate without making internal field additions silently change an external contract or expose data.

## Types: derive relationships instead of rebuilding shapes

Apply the language's native type composition and inference mechanisms. In TypeScript:

- Reuse the owning domain type, schema, or generated contract. Infer a type from its runtime schema when supported; do not hand-maintain the same shape twice.
- Derive subsets and variants with indexed access, `Pick`, `Omit`, discriminated-union extraction, or mapped types as appropriate. Use `keyof` and `typeof` for relationships to existing keys and values; do not retype their unions manually.
- Use generics when a real relationship between inputs and outputs must be preserved. Keep variant-specific payloads correlated with their discriminants instead of widening everything to independent unions or optional fields.
- Use `satisfies` or an equivalent checked declaration to verify mappings while preserving useful inference. Do not cast away missing cases or incompatible fields to make an abstraction compile.
- Prefer an explicit field selection for stable or public subsets. Use `Omit` only when inheriting future fields is intentional. Derivation must preserve ownership and compatibility, not couple every type to the largest available model.
- Keep type transformations readable. Introduce a named derived type when it clarifies a domain concept or removes repeated construction; avoid elaborate conditional types for relationships ordinary composition can express.

For example, derive an internal order ID as `Order["id"]` and a summary as `Pick<Order, "id" | "status">` rather than repeating their property types. If a runtime status schema already owns the allowed statuses, infer the status union from it rather than declaring a second list.

## Behavior: derive what can be derived

- **Model variation as data when the algorithm stays the same.** Use a typed collection or configuration to drive repeated rendering, validation, or dispatch instead of copying the same flow for each case. Keep genuinely different behavior in explicit functions.
- **Keep related views connected.** If options, labels, validators, or handlers describe the same set of variants, derive them from its authoritative definition or check their completeness against it. Avoid parallel arrays, repeated key lists, and duplicated switch chains that must be edited in lockstep.
- **Compute dependent values.** Derive counts, flags, filtered lists, and other projections from authoritative state instead of storing another synchronized copy. Store snapshots or caches only when their semantics or measured cost justify it, with explicit update or invalidation rules.
- **Make extension predictable.** Walk through adding one realistic variant or changing one rule. A new variant should need its definition and genuinely new behavior; existing generic consumers should follow automatically, and required custom handling should be exposed by exhaustive checks.
- **Use transparent mechanisms.** Prefer direct iteration, typed lookups, and explicit dependencies. A fixed domain definition is a valid source of truth; the problem is repeating its consequences. Do not introduce reflection, runtime discovery, string-built property names, or a configuration framework when ordinary code expresses the relationship clearly.

For example, define a selector's labels and values once and derive its rendered options from that definition. If permitted values come from an existing contract, check the label mapping against that contract instead of creating another authoritative set.

## Red flags and green flags

Interrogate every addition — a code block, variable, type, module, file, or spec — with this lens:

**Red flags.** An addition that cannot justify itself:

- It provides no clear benefit, or nobody can say what the benefit is.
- Its impact on the existing code is negative — it degrades the structure, or its performance delta is negative with nothing gained in return.
- It serves only its narrow moment instead of the greater good of the codebase.
- It is an escape hatch: a workaround chosen instead of finding the better solution, bought at the cost of the current code architecture. When you catch yourself writing one, go back to the design and find the solution that doesn't destroy the structure.
- It is a thin wrapper: an identity abstraction, pass-through helper, or one-line indirection that adds a name without adding clarity. Inline it and keep the direct flow.

**Green flags.** Evidence that a shared owner would improve the current code:

- Multiple consumers implement the same domain rule and must change together.
- A localized constant, type, or transformation duplicates an existing source or can be derived from it.

When you spot a green flag, reuse or extract the shared owner and connect the affected consumers. Keep single-use code local unless an established ownership boundary requires otherwise; possible future reuse alone does not justify a shared framework.

## While writing

- **The least code that fulfills the behavior.** Without losing any behavior, ask how little code this can be. Less code never means ugly or cryptic — it means the bare minimum that is readable, correct, and simple. Solving a problem with a flood of code is not my style.
- **Direct and boring over clever and magical.** Prefer code whose behavior is visible at the call site over generic mechanisms that hide simple data-shape assumptions. Brittle, ad-hoc, or "magic" behavior is a defect even when it works.
- **The strictest types I can have.** Strict types make code solid and less buggy. Avoid `any`, `unknown`, unnecessary optionality, and cast-heavy code; never paper over an unclear invariant with a silent fallback — make the boundary explicit.
- **Pure functions by default.** Same input, same output, no hidden side effects. Push I/O and mutation to the edges.
- **Immutability.** Return new values (spread, `map`, `filter`) instead of mutating arguments or shared state.
- **Composition over inheritance.** Small functions piped together; no deep class hierarchies.
- **Small units.** Functions under ~50 lines, modules focused on one job. Extract instead of appending — never push a file past ~1000 lines when the new code could be its own module.
- **Explicit dependencies.** Pass collaborators in as parameters; never reach for globals or module-level state inside core logic.
- **Early returns over nesting.** Handle the edge case and get out; keep the happy path at the lowest indentation.
- **No spaghetti growth.** Do not bolt one-off conditionals, booleans, nullable modes, or special cases into unrelated flows. Turn special-case logic into a simpler default flow with fewer exceptions. Treat "temporary" branching as permanent debt.
- **Repeated conditionals mean a missing model.** When the same condition chain shows up more than once, replace it with a typed model or explicit dispatcher instead of copying the branches; collapse duplicate branches into one clearer flow.
- **Separate orchestration from business logic.** Keep the "what to do" pure and testable, and the "when/in what order" thin at the edges.
- **Keep flows parallel and atomic.** Do not serialize independent async work for no reason, and do not structure related updates so state can be left half-applied.

## Layout: let the code breathe

Congested code is a defect, not a style choice. A human should be able to see the shape of a function from its whitespace before reading a single token. Formatters own indentation and line width; grouping and blank lines are on you — they preserve blank lines but never add them.

- **Blank lines are structure.** Inside a function, group statements into paragraphs by purpose — read inputs, guard, transform, persist, respond — and separate paragraphs with exactly one blank line.
- **Group what belongs together, separate what doesn't.** Lines that form one thought stay adjacent: a declaration and the single line that fills it, a guard and its throw, a loop and its accumulator. The moment the purpose changes, insert a blank line. Never run unrelated statements together; never split a tight pair apart.
- **Guards first, then air.** Put the early-return / throw guards at the top as one tight block, then one blank line, then the happy path.
- **Breathe before the result.** One blank line before the final `return` (or the statement that yields the result), unless the whole body is three lines or fewer.
- **One statement per line.** No `a(); b();` on one line, no side effects chained with `&&`, no nested ternaries. Break a long condition into a named predicate, or one clause per line.
- **Hoist complex expressions.** Pull dense expressions out of call arguments, template literals, and JSX attributes into named `const`s so the call site reads as a sentence.
- **Blank lines between every top-level unit.** Between import groups (external, internal alias, relative), between imports and the first declaration, between every top-level declaration, and between sibling JSX/HTML blocks that serve different purposes. Once a JSX element has more than ~3 props, put one prop per line.
- **Don't overshoot.** No double blank lines, no blank line between a comment and the line it describes, no blank line inside a two- or three-line group that is one thought, no blank line as the first or last line of a block.

Before:

```ts
export async function publishPost(postId: string, actor: User, deps: Deps) {
  const post = await deps.posts.findById(postId);
  if (!post) throw new NotFoundError(postId);
  if (post.authorId !== actor.id && !actor.roles.includes("editor")) throw new ForbiddenError();
  const slug = slugify(post.title); const publishedAt = deps.clock.now();
  const published = { ...post, slug, publishedAt, status: "published" as const };
  await deps.posts.save(published); await deps.events.emit({ type: "post.published", postId, publishedAt });
  return published;
}
```

After:

```ts
export async function publishPost(postId: string, actor: User, deps: Deps) {
  const post = await deps.posts.findById(postId);
  if (!post) throw new NotFoundError(postId);
  if (!canPublish(actor, post)) throw new ForbiddenError();

  const published: PublishedPost = {
    ...post,
    slug: slugify(post.title),
    publishedAt: deps.clock.now(),
    status: "published",
  };

  await deps.posts.save(published);
  await deps.events.emit({ type: "post.published", postId, publishedAt: published.publishedAt });

  return published;
}
```

Same behavior, same line budget in spirit — but the guards, the build, the persist, and the result are now four visible paragraphs, and the authorization rule has a name.

## Readability: write for the reviewer

The first reader of my code is a reviewer looking at a diff, not someone with jump-to-definition and an afternoon to spare. If the code only makes sense after reading every helper's body, it is not finished.

- **Read top-down.** Put the exported entry point first and its helpers below it, in the order it calls them, unless the language or the repo's convention requires otherwise. The reader should meet the story before the details.
- **One level of abstraction per function.** A function either orchestrates named steps or implements one detail, not both. If a high-level flow suddenly drops into string slicing or index math, extract that detail behind a name.
- **The call site is the documentation.** A reader should be able to predict what a call does and returns from its name and arguments alone. Replace positional booleans and bare literals with named options or constants: `render({ compact: true })`, not `render(true)`; `MAX_RETRIES`, not `3`.
- **Shallow and narrow.** Keep nesting to two levels inside a function; flatten deeper code with early returns or extraction. Past three parameters, take one named context or options object. Return a named object, not a tuple like `[attendees, session]`.
- **No clever compression.** Break long `reduce` chains, nested callbacks, dense regexes, and stacked operators into named intermediate values. Put each `await` into a named local before building a return value; never nest it inside an object literal or a function argument. A few extra lines with good names beat one line the reviewer has to execute in their head.
- **Real units, not inline closures.** Do not grow a function or component body with locally defined render helpers, mini-functions, or `(() => { … })()` blocks. Extract a real component, hook, or module-level function with its own name.
- **Every state is explicit.** Never let `undefined` carry meaning in a boolean or a value (`hasAttended: undefined` meaning "not final yet"). Model the extra state with a union or a separate field so a reviewer can see it.
- **Diff-friendly text.** Write long prompts, messages, and lists one item per line, so editing one step changes one line instead of rewriting a 1,000-character paragraph.
- **Keep the diff about the task.** Cleanup inside the task's scope is welcome. Unrelated renames, reformatting, and reordering are noise that hides the real change. When a refactor is needed, keep it separable from the behavior change so each can be reviewed on its own.
- **Make new code look native.** Match the surrounding file's patterns (how errors are raised, how modules export, how similar functions are named and ordered) so the reviewer only has to judge what is genuinely new.

## Naming

A name is the cheapest documentation I have and the first thing a reviewer reads. If a name needs a comment to explain it, the name is wrong.

- **One concept, one name, end to end.** The biggest naming failure is one idea wearing several names: participants, attendance, and attendees for one thing, or task and issue, or cohort and group and plan. Pick the domain noun once and carry it through the route, service, types, DTOs, UI keys, test ids, and comments. Never reuse one name for two concepts. When you rename, finish the rename everywhere: keys, test ids, helpers, and comments.
- **Name for the bigger picture.** Name variables, files, functions, and modules for where the code is going, not only the small task in front of you. A later addition that belongs in this module should feel at home there, not be pushed out by a name scoped to the original narrow use case.
- **Name the role, not the UI copy.** Components, files, and functions describe their responsibility (`ConversionPlanApprovalCard`, `CurrentPlanSummary`), not on-screen text or prose (`PlanForYourOk`, `ThisPlan`, `conversion-words.ts`). The copy will change; the role will not.
- **Name the role, not the type or the mechanics.** `activeSubscribers`, not `filteredList`; `invoiceTotal`, not `sum`; `retryDelayMs`, not `num`. Do not encode the type (`userArray`, `strName`) or the history (`newUser`, `user2`, `updatedData`, `finalResult`, `tempFix`).
- **No placeholder names.** `data`, `info`, `item`, `obj`, `result`, `res`, `temp`, `val`, `payload`, `handle`, `process`, and `doStuff` are placeholders, not names. Allow one only in a scope of a few lines where its meaning is obvious, such as the singular of the collection being mapped: `users.map((user) => …)`.
- **Scope sets length.** A three-line loop index can be `i`; an exported function must be fully specific. The wider the visibility, the more precise the name.
- **No private abbreviations.** Spell words out: `message`, not `msg`; `previous`, not `prev`, unless the codebase has already standardized the short form. Keep universally known abbreviations such as `id`, `url`, `html`, and `api`.
- **Functions say everything they do.** Use a verb plus an object that describes the outcome: `archiveExpiredSessions`, not `cleanup`. If an honest name needs "And", split the function. Make side effects visible in the verb: `get`, `compute`, `to`, `build` for pure work; `fetch`, `load`, `save`, `send`, `delete` for I/O. Never give a function a noun or preposition name (`currentState`, `titlesOf`, `withoutCohorts`), least of all one that queries or writes. An `assert` function only throws; if it also returns something, name it for what it returns.
- **Booleans read as yes/no questions.** `isActive`, `hasAccess`, `canEdit`, `shouldRetry`. Always use the positive form: `isEnabled`, never `isNotDisabled`. Name it for what it actually decides: `isConversionPlanApproval`, not `isPlan`.
- **The name matches what it holds.** A count is `memberCount`, not `members` or `pastMembers`; an id is `templateId`, not `launch`; a collection is plural (`orders`); a lookup is `xById` or `xByKey`. Put units in the name: `timeoutMs`, `priceInCents`, `directRevenueInr`, `createdAtIso`. If a value's type changes, rename it in the same change.
- **Name pairs symmetrically.** `open`/`close`, `start`/`stop`, `min`/`max`, `source`/`target`. Do not use `start`/`end` in one place and `begin`/`finish` in another.
- **Name shared code for what it owns.** Avoid vague buckets such as `utils`, `common`, `helpers`, or `manager`, and avoid pretending a feature-specific helper is universal.

Before:

```ts
const data = await get(id);
const res = data.items.filter((x) => x.s === "A" && x.exp > Date.now());
if (res.length && flag) process(res);
```

After:

```ts
const subscription = await fetchSubscription(subscriptionId);
const renewableSeats = subscription.seats.filter(isRenewable);

if (renewableSeats.length > 0 && autoRenewEnabled) {
  await renewSeats(renewableSeats);
}
```

Follow the repository's and language's naming conventions; where none exist, use these defaults:

- Files: `lowercase-with-dashes`
- Functions: verb phrases (`getUser`, `validateEmail`)
- Predicates: `isValid`, `hasPermission`, `canAccess`
- Constants: `UPPER_SNAKE_CASE`; variables descriptive and `const` by default

## Comments

Comments are a special thing, not a routine one. Names, types, and structure must tell the story. A comment that walks the reader through the code means the code failed to.

- **Fix the code before commenting on it.** When something seems to need a comment, first try a better name, an extracted function or named predicate, a named constant, or a stricter type. Comment only what is still unclear after that.
- **Comment the why, never the what.** Write a comment only for what code cannot express: the reason for a non-obvious choice, an invariant or constraint the caller must respect, a workaround (with its issue link), the format or units of external data, non-obvious arithmetic (a `- 1` boundary, a clamp, a `?? 0` default), or why the obvious approach was rejected. The best comments tie the code to an outside fact: "Zoom recycles meeting numbers, so a session UUID is trusted only when…".
- **Write plainly.** The most common failure is compressed, literary prose that has to be decoded ("a repeat answers the first launch"; "the whole of it as the agent wrote it"). Use plain subject–verb–object sentences, one idea per sentence, with ordinary words in their ordinary meaning (`parses` or `is valid`, not `reads`). Say what the code does before you get to the edge cases.
- **Use the code's vocabulary.** Refer to concepts exactly as the code names them: `cohort` if the code says cohort, not "group"; `CONVERSION_AGENT`, not a persona name. A comment that uses different words from the code adds a second vocabulary for the reader to learn.
- **Document contracts at boundaries.** An exported function in shared code may carry a short doc comment when its contract is not obvious from the signature: what it guarantees, what it throws, what side effects it has. Skip doc comments that only repeat the name and parameter types.
- **Never write these:**
  - Narration that restates the line below it (`// loop through users`, `// return the result`).
  - Section banners inside a function (`// --- validation ---`). Use a blank line, or extract a function.
  - Change history or notes to the reviewer (`// updated to use the new API`, `// fixed`, `// NEW`, `// as requested`). These belong in the commit message or the PR.
  - References to PR numbers, other services' internals, or other screens' layouts (`backend #6765's learning_buddy`, `so the column stays short beside For you`). These go stale the moment that other place changes.
  - The same comment pasted at several call sites. If a rule needs explaining everywhere, enforce it in one named function (`assertSessionInCall`) and explain it there once.
  - Commented-out code. Version control remembers it.
  - A bare `TODO` for work I could finish now. Finish it. A real out-of-scope follow-up gets a specific note and a reference.
- **Write it properly when you do.** Use full sentences in the present tense, describing the code as it is now. Put the comment directly above what it explains and keep it short. A doc comment on a constant or object must describe all of it, not just the first field. Update or delete the comment in the same change that alters the behavior.

Before:

```ts
// Check if user is admin
if (user.role === "admin" || user.role === "owner") {
  // Wait 2 seconds
  await sleep(2000); // NEW: added delay
}
```

After:

```ts
if (isWorkspaceManager(user)) {
  // The billing provider rejects plan changes made within ~2s of a seat update.
  await sleep(BILLING_SETTLE_DELAY_MS);
}
```

## Before finishing

- **Rehearse a change.** Pick a fact or variant touched by this task and trace every place that would need editing if it changed. Remove edits that merely synchronize duplicated knowledge; retain deliberate contract boundaries and genuinely distinct behavior.
- Check added types, literals, mappings, and derived state against their owners. Confirm the affected consumers actually use the shared source and that required cases cannot silently disappear behind a fallback or cast.
- Ask: could I easily test this? If not, restructure until you could — untestable code is a design smell even when it works.
- Skim the diff with unfocused eyes: can you see the paragraphs? If any function reads as one dense block, it is not finished — go back to the layout rules.
- **Read only the names.** Go through the diff's identifiers without reading the bodies: functions, variables, parameters, files. If you cannot predict what each one does or holds, rename it before presenting. Confirm that each concept has exactly one name across the diff, including UI keys, test ids, and comments.
- **Audit every comment you added.** Delete narration, change history, notes to the reviewer, and anything a rename or extraction could replace. Read the rest aloud: if a sentence needs decoding, rewrite it plainly. Keep only the why.
- **Hunt stale comments.** Re-read the existing comments near every line you changed or removed, and fix any that describe behavior that no longer exists.
- Ask what a demanding reviewer would say: "this works, but it makes the surrounding code more spaghetti", "this abstraction seems unnecessary", "this looks like a bespoke helper for something we already have". If any of those land, restructure before presenting.
- Run the narrowest relevant check the repo provides (typecheck, lint, focused tests) and report results honestly.
- Re-read the diff as another developer would: every line should look like it always belonged there, and they should be able to build on it without reading its internals.
