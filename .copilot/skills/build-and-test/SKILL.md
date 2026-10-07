---
name: build-and-test
description: "Execute evidence-based software verification: regression tests, applicable integration/E2E checks, lint/types, production build, and runtime behavior. Required checks cannot be skipped, weakened, or relabeled; autonomous completion requires a fresh independent verifier."
---

# Build and test

For autonomous runs, load `autonomous-delivery/references/protocol.md`. For an ordinary code change, use this procedure without launching the five-stage lifecycle or extra agents unless requested.

Apply the shared [engineering principles](../autonomous-delivery/references/engineering-principles.md): exercise narrow module contracts and their actual composition, preserve compatibility, and keep tests independent of incidental implementation details.

## 1. Fix applicability before implementation

Read repository instructions, manifests, lockfiles, test configuration, existing tests, and CI. Use actual project commands and supported versions, not guessed package-manager conventions.

Create one verification-matrix row for each category below. An autonomous run freezes the matrix inside the accepted implementation-plan contract. Non-autonomous work records the same decisions in its task context.

| Category | Required when | Only permitted exclusion |
|---|---|---|
| `behavior` | Executable code or behavior changes | `documentation_only`: no executable changes |
| `integration` | A changed boundary crosses a module, process, API, storage layer, or external dependency | `no_changed_boundary`: enumerate examined boundaries |
| `end_to_end` | A user flow through a UI, service, CLI, or package consumer changes | `no_user_flow`: identify why no consumer behavior changes |
| `lint` | A lint/static-analysis command is defined by repository instructions, manifests, or CI | `not_configured`: inspected configuration paths |
| `typecheck` | The repository defines a type-checking command or requires compilation for type checking | `not_configured`: inspected language/configuration evidence |
| `build` | The deliverable has a configured build/package/compile step | `no_build_step`: evidence that the artifact needs no build |
| `runtime` | Executable behavior changes | `documentation_only`: no executable changes |

For each required row record ID, category, criterion IDs, exact command, working directory, expected result, and timeout. Test rows additionally record minimum executed-test count and the IDs/names of new or changed regression tests that must run. A single repository command may satisfy several rows; reference the same genuine execution evidence rather than inventing separate runs.

Exclusions require concrete repository evidence and acceptance in the planning review before implementation. Missing dependencies, credentials, tools, service access, test infrastructure, time, or budget never justify an exclusion. A failed required row cannot be reclassified as excluded. Fix it or block.

The standalone case does not require fabricated build tooling for a documentation-only or interpreted project. It still requires explicit applicability rather than silently omitting a check.

## 2. Write tests that can fail

- Map each required behavior and feature to named tests/procedures and observable expected results.
- Cover the changed happy path, at least one relevant failure/boundary path, and preserved behavior at the affected interface.
- For a bug fix, run the new regression test against an isolated unfixed baseline and show failure for the expected reason, then show success with the fix. A setup error does not count as the expected failure. If baseline execution is impossible, record that blocker rather than claim red/green proof.
- Test the implementation and real boundary being changed. Do not mock away the defect, assert constants against themselves, or replace functional evidence with a screenshot.
- Use deterministic fixtures and explicit cleanup. Avoid arbitrary sleeps and live production data.
- Preserve existing coverage and assertions. Do not remove tests, add skips, lower thresholds, or update snapshots merely to get green.
- Exercise the lowest changed rule/boundary first, then the real consumer through integration/runtime checks for the working slice. Passing isolated modules without functioning composition does not establish completion. Run repository-defined dependency/architecture checks when they apply to the changed boundary.

In autonomous delivery, test strategy is planned before coding; test-writing waits for the five accepted planning gates. Assign independently owned test tasks to `autonomy-test-engineer`, with explicit worktree and file ownership. Tests not split into their own task remain the implementation owner's responsibility.

If required testing infrastructure is absent, include the minimum required infrastructure in the plan with approval for any new dependency. An ad hoc manual check cannot replace a planned required automated test.

## 3. Execute and retain evidence

On failure, use the debugging procedure in `../autonomous-delivery/references/engineering-principles.md`: classify the failure, preserve the meaningful error and source, minimize the reproducer, and investigate a falsifiable cause before changing code or rerunning. Compile/typecheck edited code and harnesses before expensive UI/runtime checks. A harness/setup failure is not a product regression; an unchanged failing run is not a repair. Ordinary in-scope fixes and local checks are agent-owned, not repeated user approval requests. Deterministic repairs have no fixed count cap, but each requires a genuinely distinct evidence-backed hypothesis and coordinator inspection, contiguous same-operation accounting, honest results, and content-hashed logs. Without an evidence-backed next hypothesis, record a technical blocker; do not retry blindly or ask whether to fix a routine bug. Preserve transient retry limits and evidence-backed review continuation under the protocol, including contiguous four-report cycles, findings/verdict history, changed subject/prerequisite hashes beyond two cycles, and historical approval compatibility. Review has no fixed cycle cap or new routine per-cycle approval requirement; the coordinator must inspect actual progress. Gates, independent final verification, permissions, user stops, deadlines, and spending/budget limits remain unchanged; route defects to the assigned file owner.

Run only in an authorized project worktree. Restore locked dependencies only after a manifest change or a missing-dependency failure, using the repository's package manager. Do not add tools or change lockfiles without scope authorization.

During development, run the smallest targeted selection covering the change. At final verification, run every required matrix row and every repository-mandated final check on the integrated deliverable. Run serially when commands share state.

Inspect process completion, exit status, test counts, expected test names, and output. A started process, an unexpectedly empty test run, skipped required tests, timeout, nonzero exit, or incomplete log is not a pass. Preserve command failures even if a later retry succeeds.

For every required row record actual command/cwd, start/end time, source and accepted-plan hashes, runner ID, exit code, assertions/expected outcome, and a content-hashed log. For test rows record executed count, required tests executed, and skipped required tests. Zero skipped required tests is mandatory.

For autonomous runs, execute commands in the assigned implementation/test/verifier subagent, not in the coordinator. Store full output and structured result ledgers in assigned artifacts. Return a handoff within 500 words with check verdicts and artifact references; do not copy raw build/test logs into the parent. Preserve the command's exit status when writing logs.

Build, tests, and runtime are distinct gates. A shared command is valid only if its actual output proves each claimed gate. A successful build does not prove behavior; unit tests do not prove the built app starts.

## 4. Exercise the delivered artifact

For a service/UI, start the production artifact or the repository's accepted runtime harness, check readiness with a bounded timeout, exercise the changed user flow and relevant error path, and inspect the resulting state/errors. For a UI, use functional browser/E2E checks and compare relevant visuals. For a CLI/library, run a representative command or consumer against the delivered package.

Record outputs/assertions, not just an HTTP connection or screenshot. If the necessary runtime cannot be exercised, the runtime gate is blocked.

Stop task-only helpers by their exact process/session IDs. Delete only task-created temporary artifacts. Do not leave services running or contact production/paid resources without authorization.

## 5. Independent final gate

Every autonomous run uses `autonomy-verifier` in a fresh context that did not implement the code or tests. The coordinator must supply the accepted contract, matrix, exact source snapshot, allowed setup/service operations, and evidence destination. Missing verifier capability blocks autonomous completion.

Capture the integrated source before and after execution using the protocol's snapshot command and use `templates/verifier-report.json` from autonomous-delivery for the report. Freeze source against concurrent edits. The verifier must not repair source, tests, snapshots, manifests, or CI; report failures to the owner. Required setup that changes source returns control to the owner and restarts verification.

If a tracked or non-ignored source file changes, invalidate the final result and repeat the required matrix on a fresh snapshot. Record runtime/tool/dependency versions and relevant non-secret configuration; source hashing alone does not capture environment changes.

Pre-existing failures remain failed or blocked. Use an isolated baseline comparison to identify them; do not silently waive them or repair unrelated scope. Check remote CI at the exact revision before claiming it passed.

## 6. Completion verdict

Every required row must be passed, every required feature must map to fresh passing evidence, and the tested source must equal the delivered source. Excluded rows are classification decisions, never successful checks.

In an autonomous run, the coordinator records the verifier's results and obtains the final adversarial review. Pass the protocol's completion validator before setting `completed`. A blocked or unverified result remains explicitly incomplete.
