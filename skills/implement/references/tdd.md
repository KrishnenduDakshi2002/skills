# Test-driven development

Use a red-green loop that produces behavior-focused tests worth keeping. Read [tests.md](tests.md), [mocking.md](mocking.md), and [codebase-design.md](codebase-design.md) before choosing or creating a seam.

## Choose seams first

A **seam** is the public interface through which behavior can be observed without reaching into implementation details.

- Use seams already agreed in the specification or tickets.
- Prefer the highest existing public seam that expresses the behavior.
- If no seam was agreed and the choice changes architecture or scope, confirm it with the user before writing tests.
- Do not add tests against a new internal seam merely because it is convenient.

## Red-green rules

Repeat one vertical slice at a time:

1. Write one behavior-focused test through a confirmed public seam.
2. Run it and confirm it fails for the expected behavioral reason, not a syntax, fixture, or environment error.
3. Add only enough implementation to make that test pass.
4. Run the focused test and relevant nearby checks.
5. Continue with the next behavior learned from the previous cycle.

Do not write all tests before all implementation. Do not anticipate future requirements or add speculative hooks. Keep structural refactoring outside the red-green cycle; perform it during the review stage with tests green.

## Test quality

- Verify behavior that callers or users care about through public interfaces.
- Use independently known expected values from the specification, examples, or fixtures.
- Write test names as behavioral specifications.
- Keep one logical behavior per test while allowing the assertions needed to establish it.
- Ensure tests survive internal refactors when behavior remains unchanged.

Reject tests that:

- Mock internal collaborators or test private methods.
- Assert internal call order or counts without a public contract requiring them.
- Bypass the interface to inspect a database or side channel.
- Recompute expected values with the same logic as the implementation.
- Pass before the intended behavior exists.

