# Codebase design vocabulary

Use these terms when selecting testing seams or reshaping code:

- **Module:** anything with an interface and implementation.
- **Interface:** everything callers must know, including invariants, errors, ordering, configuration, and performance characteristics.
- **Implementation:** behavior hidden inside a module.
- **Depth:** caller leverage provided by an interface. A deep module hides substantial behavior behind a small interface.
- **Seam:** the location where behavior can vary through a module's interface.
- **Adapter:** a concrete implementation that fills an interface at a seam.
- **Leverage:** capability callers receive per unit of interface they learn.
- **Locality:** concentration of change, knowledge, bugs, and verification in one module.

## Principles

- Treat the interface as the test surface.
- Reduce methods and parameters while hiding more complexity behind the interface.
- Accept dependencies instead of constructing them inside behavior that needs testing.
- Return results when possible rather than exposing mutation as the only observable effect.
- Do not introduce a seam for hypothetical variation; one adapter is usually hypothetical, two establish real variation.
- Apply the deletion test: if deleting the module merely spreads its complexity across callers, it was earning its keep; if complexity disappears, it was likely a pass-through.

