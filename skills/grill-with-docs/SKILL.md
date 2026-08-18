---
name: grill-with-docs
description: Relentlessly interview the user to sharpen a plan or design while maintaining the project's domain glossary and recording durable architectural decisions. Use only when the user explicitly asks to be grilled, stress-test a design, or run grill-with-docs and wants the resulting terminology and decisions captured in repository documentation.
disable-model-invocation: true
---

# Grill With Docs

Sharpen a plan through a decision-tree interview while capturing resolved domain language and durable architectural decisions. Do not implement the plan.

Read [domain-modeling.md](references/domain-modeling.md) before starting. Read the linked format reference immediately before creating or editing a glossary or ADR.

## Process

### 1. Establish facts and existing language

Read relevant repository instructions, `CONTEXT.md` or `CONTEXT-MAP.md`, applicable ADRs, and the code involved in the design. Discover facts with available tools instead of asking the user. Use parallel exploration when supported and useful; otherwise investigate directly.

Treat factual investigation as a prerequisite in the decision tree. Continue asking independent questions while a fact is being investigated.

### 2. Map the design tree

Represent the design as decisions and dependencies between decisions. The **frontier** is every unresolved decision whose prerequisites are settled.

Do not ask a question whose answer depends on another unresolved question. Recompute the frontier after every response because each answer may add, remove, or reshape branches.

### 3. Ask one frontier at a time

Ask every currently independent frontier question in one round. Use a structured question interface when the active agent provides one; otherwise ask in plain text. Number every question and provide a recommended answer:

```text
Q1 — <question title>: <question and relevant choices>

Recommended: <answer and concise rationale>
```

Wait for the user's answers before asking the next frontier. Decisions belong to the user; facts and repository investigation belong to the agent.

### 4. Model the domain continuously

During each round:

- Call out conflicts with existing glossary terms.
- Replace vague or overloaded language with proposed canonical terms.
- Invent concrete edge-case scenarios that test boundaries between concepts.
- Cross-check claims against the code and surface contradictions.
- Update the applicable `CONTEXT.md` as soon as a term is resolved.
- Offer an ADR only when the decision is hard to reverse, surprising without context, and the result of a real trade-off. Write it after the user accepts.

Never use the glossary as a scratchpad or implementation spec. Keep implementation choices in ADRs or the eventual specification.

### 5. Close the session

Finish only when the frontier is empty. Summarize the settled decisions, glossary changes, ADRs created, and any explicitly deferred questions. Ask the user to confirm that shared understanding has been reached. Do not start implementation.
