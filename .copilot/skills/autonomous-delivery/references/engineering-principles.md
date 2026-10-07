# Engineering principles

These principles apply to implementation, additions, refactors, tests, and the reviews of that work. They do not independently activate autonomous execution. Follow the repository's established design and explicit user requirements; resolve a conflict before the affected change rather than rewriting the project to match a preferred pattern.

The objective is the simplest complete implementation whose responsibilities, contracts, and change locations are clear. Extensibility means localizing supported changes, not promising that every unknown future feature will require zero edits.

## 1. Modular structure and controlled dependencies

- Give each module a cohesive responsibility and an explicit public contract. Keep implementation details private. A module is a responsibility boundary, not necessarily a new directory, class, package, or service.
- Keep dependency direction explicit and acyclic. Place reusable business rules below orchestration and external interfaces; isolate I/O, framework, and vendor details at existing boundaries. Do not add a new layer just to reproduce this vocabulary.
- Keep state ownership and side effects explicit. Use typed inputs/results, validate at trust boundaries, preserve invariants, and propagate errors through repository-standard mechanisms. Do not hide failures behind success-shaped defaults.
- Reuse an existing implementation of the same domain concept. Extract shared code when it represents the same rule or a genuine boundary; similar-looking lines alone do not justify coupling unrelated features.
- Expose only the extension points required by accepted behavior or existing contracts. Use composition and narrow interfaces to isolate a real variation point, not an interface, factory, registry, or plugin mechanism for every class.
- Preserve compatibility for existing consumers and persisted data unless a behavior change/migration is explicitly accepted. Local extension is not permission for a broad public-API rewrite.

Before accepting architecture/design, describe the required feature's change impact: which modules own it, which contracts are involved, and which unrelated modules remain untouched. Trace an already accepted variation through those contracts when one exists. Do not invent a future feature to justify generalization.

## 2. Requirements first, bottom-up implementation

Design from the required user behavior and existing architecture first. Implement the accepted dependency graph bottom-up, inside small end-to-end slices:

1. Define the slice's observable outcome and required contracts.
2. Implement or adapt the lowest missing dependency, such as a domain type, invariant, or focused rule, with its tests.
3. Add the needed boundary adapter and compose the behavior in application logic.
4. Wire the actual consumer, such as the UI, handler, or CLI, and exercise the integrated slice.
5. Review the slice before building dependent behavior.

These are dependency levels, not mandatory new layers. Reuse existing levels and omit nonexistent layers from the design rather than creating empty wrappers. Record explicit task dependencies; parallelize only tasks whose inputs/contracts are ready.

Do not build a large foundation of unused utilities before proving the first working slice. Do not leave a pile of locally passing units without a functioning consumer. Bottom-up implementation never removes the existing planning, review, build, or runtime gates.

## 3. Every addition earns its place

Inspect every changed line before handoff. Each addition must serve an accepted behavior, invariant, compatibility requirement, required failure handling, tested boundary, essential observability, or a concrete simplification of the affected code.

- Every new function needs a known caller, framework entry point, or required public contract. Every branch needs a meaningful input/state case. Delete newly introduced dead code, unused exports, placeholder methods, and unreachable paths.
- Every new module, abstraction, configuration option, or dependency needs a concrete reason the existing local design cannot satisfy the requirement as clearly. Record the reason and the simpler alternative considered in the existing design/review artifact.
- Do not add speculative features, generic frameworks, configurable behavior with no consumer, pass-through wrappers without a boundary purpose, redundant storage, or duplicated sources of truth.
- Do not add a package when existing code or the standard library adequately handles the requirement. A required new dependency must have a scoped benefit, compatibility/maintenance assessment, and the project's required approval.
- Do not optimize unmeasured bottlenecks, prebuild caching/concurrency machinery, or retain scaffolding solely because it might be useful later.
- Do not optimize for the fewest lines at the expense of clarity, error handling, type safety, useful tests, or correctness. Readable code is not bloat; dense one-liners and clever indirection can cost more to maintain.
- Comments explain non-obvious reasons, contracts, or constraints. Do not annotate every line/function to prove it is justified. Record significant design decisions once, not repeated essays in code, plans, and handoffs.
- Keep refactoring scoped to the feature or defect. Do not bundle repository-wide renaming, formatting, reorganizing, or cleanup with an unrelated addition.

The author performs a necessity pass on the actual diff: remove unneeded additions, simplify artificial indirection, check existing helpers, and justify the remaining new boundaries. A concise rationale for nontrivial choices is required; a per-line justification document is not.

## 4. Carry the principles through existing gates

Use the existing artifacts and reviews; do not create a parallel planning bureaucracy.

| Gate | Required engineering evidence |
|---|---|
| Architecture | Module responsibilities, allowed dependency direction, actual feature change impact, and reasons for new boundaries |
| Design | Narrow public contracts, state/invariants, compatibility, failure behavior, and simpler alternatives to proposed abstractions |
| Implementation plan | Bottom-up task dependencies within working slices, file ownership, boundary/consumer checks, and the project-memory update owner/path |
| Implementation milestone | Scoped diff, known consumers of added functions, necessity-pass result, boundary checks, and reasons for any broader-than-planned changes |
| Verification | Actual checks of the composed behavior and preserved contracts, plus agreement between implemented boundaries and the final project documentation |

Proposer and challenger must examine both under-design and over-design. Challenge changes that scatter one rule across unrelated modules, expose internals, introduce cycles, require unrelated edits for the accepted feature, or add abstractions without a current responsibility.

A finding must identify the affected contract, dependency, code, or maintenance cost. Concrete violations of these required principles block acceptance until resolved/refuted; preferences about naming style, patterns, or line count alone are not evidence of a defect. The checkpoint validator checks records, not the semantic quality of modularity; reviewers must inspect the relevant design and diff.

Test public behavior and boundary contracts so internal refactors do not require rewriting tests that only mirror implementation details. Use the existing architecture/import checks when the repository defines them. Do not install a new framework just to label the design modular.

## 5. Project memory that helps the next feature

"Project memory" means the repository's existing durable guidance: for example, the applicable `AGENTS.md`, `.github/copilot-instructions.md`, architecture document, or established decision records. It is not the conversation transcript or a new instruction file for every task.

- During discovery, identify the authoritative locations and conflicting/stale statements. Read them before designing extensions; preserve unrelated content and resolve instruction conflicts with the user.
- During planning, identify necessary updates and give one implementation/documentation owner the exact path and write scope. The planner writes only its assigned session artifacts; it does not edit repository guidance during the planning gates.
- When a delivered change alters boundaries, public contracts, state ownership, supported extension points, dependencies, or verification commands, update the relevant existing document to describe the final implemented state. Record how to add the next supported variation, required tests, and the reason for non-obvious decisions.
- Keep the record compact and actionable. Link to canonical code or documentation rather than copying it. Do not copy the entire global policy, task logs, speculative roadmaps, or a running list of every function into repository memory.
- Write only in an authorized project session/worktree. Creating a new memory location or changing repository-governing instructions requires explicit authorization in the task scope; this global preference does not silently approve repository policy changes. If that authorization is missing, keep the proposed update in session artifacts and report it as pending, not applied.
- Before completion, reconcile required documentation updates with the delivered code and remove newly stale statements in the touched scope. If the change introduces no durable design/usage change, preserve existing memory instead of adding a no-op entry.

This user-level reference supplies the common engineering constraints across projects. Project memory should retain project-specific decisions and extension guidance, not another divergent copy of these rules.

## 6. Debug causes, not symptoms

Routine in-scope defects are the implementation owner's responsibility, including defects in code or harnesses the owner just wrote. Ordinary repairs and local checks do not need a fresh "should I fix it?" question. Respect file ownership, review gates, transient retry limits, user stops, deadlines/budgets, and external permission boundaries. Deterministic repairs have no fixed count cap: each requires investigation and a genuinely distinct, evidence-backed hypothesis under the [protocol](protocol.md). This does not authorize blind retries or policy changes.

1. Preserve the first meaningful failure: exact command, source revision, exit status, error/stack, expected result, and observed result. Reproduce with the smallest existing check that exercises the failing boundary. Classify the failure as compile/type, product logic, test harness, environment/service, or permission/policy before choosing a repair. A compile error or broken selector is not evidence of a product regression.
2. Form a falsifiable root-cause hypothesis. Trace the relevant inputs, call path, state ownership, and outputs; inspect the actual dependency/API contract. Use repository tooling, targeted diagnostics, or a minimal reproducer to distinguish competing causes. Record the hypothesis and observation in the existing task report/operation ledger, not a new planning document.
3. Fix the smallest coherent cause within assigned ownership. Reuse supported tools and existing helpers. Do not substitute broad catches, unsafe casts, larger timeouts, retries, or mocked boundaries for understanding the failure. Use a runtime guard when an external value genuinely has an unknown type. A test-owner discovery of a production defect goes to the production owner with a reproducer, not to the user as a request to debug.
4. Check cheap prerequisites first: compile/typecheck after code or harness edits, then the affected regression and boundary checks, then the required consumer/runtime checks. Prefer observable readiness/events/assertions over sleeps. For persistence, restart the actual product using the same isolated storage/profile and verify the result from the new process; resetting a test double or reusing an in-memory object does not prove persistence.
5. If a check still fails, compare the new error to the preserved failure. Investigate new evidence before another repair. An identical command on unchanged code without an identified transient cause is not a debugging step. Record a distinct falsifiable hypothesis, supporting observation, proposed change, and distinguishing check for each repair; cosmetic rewording is not progress. Maintain contemporaneous contiguous attempt accounting under the same operation, with honest results and content-hashed logs; do not rename tasks to reset it. The coordinator inspects this evidence before continuation. On success run the affected checks and required final matrix; preserve all failed attempts and remove task-only diagnostics/helpers.

If no evidence-backed distinct repair hypothesis remains, record a new technical blocker with the evidence already obtained; do not ask the user whether to fix a routine defect. Review has no fixed cycle cap: preserve contiguous history and require evidence-backed corrections/new evidence, inspected against prior findings by the coordinator. Beyond two cycles, unchanged subject/prerequisite hashes block continuation except for the protocol's historically approved third cycle. An exhausted transient retry limit, review no-progress blocker, deadline, hard spend limit, budget, user stop, or missing external permission still stops the affected work under the protocol. Do not claim completion, fabricate a pass, or ask the user to repair agent-written code. A genuine required authorization is separate from permission for an ordinary bug fix or review continuation. The validator checks recorded consistency, not authentic execution or meaningful semantic differences; the coordinator must inspect actual evidence. Instructions do not prove that a defect is fixed; execution evidence does.
