---
name: autonomous-delivery
description: "Coordinate explicitly requested autonomous coding through five planning gates, independent proposer/challenger reviews at every stage, isolated implementation, and mandatory build/test verification. Not for how-to questions, setup maintenance, or planning-only requests."
---

# Autonomous delivery

Read [the execution protocol](references/protocol.md) before starting. It defines gate acceptance, state/evidence formats, role boundaries, retry limits, and stop behavior. Related skills describe procedures; they do not waive that protocol. The sources and deliberate product-specific choices are in [the research notes](references/sources.md).

Apply [context management](references/context-management.md) throughout the run. The main session owns coordination and decisions; subagents own detailed discovery, artifact drafting, implementation, and check execution. Return bounded handoffs rather than raw transcripts.

Apply [engineering principles](references/engineering-principles.md) to architecture, design, implementation, and review. Require cohesive modules, explicit contracts, bottom-up working slices, and a necessity pass on every addition. Maintain authorized project-specific memory without duplicating the global policy.

## 1. Establish the contract and capabilities

Record the objective, repository/project, exclusions, deliverables, allowed actions, and measurable success criteria. Read the governing repository instructions in the coordinator; delegate detailed manifest, test, and implementation discovery to `autonomy-planner` before proposing changes. Do not repeat the worker's repository-wide exploration in the parent.

Use the user's actual execution host and available tools. Confirm that independent agents, durable artifacts, authorized isolated worktrees, and required build/test tools can be used. Test capability using read-only discovery; missing capability is a blocker, not permission to impersonate a worker.

The permitted write scope must be explicit. In a general chat with read-only repository access, create an authorized project session for code changes and test execution. Do not use the primary checkout or a scratch clone to evade that boundary.

Resolve material scope, behavior, compatibility, or permission decisions with the user before the affected gate. Make reversible implementation choices inside the agreed scope. Record the exact timezone-qualified deadline when requested. Do not invent a billing cap; a requested hard cap requires an actual enforcing control before unattended execution.

Apply the context-management change-batching procedure: keep user decisions in coordinator state, send consolidated worker-relevant deltas, and freeze completed discovery rather than repeatedly rewriting it. External prerequisites block only the work that depends on them. Evaluate and continue already-authorized independent work before pausing the whole run; user stops and invalidating changes still require immediate action.

## 2. Initialize durable state

Create a run directory inside the session's persistent artifact storage, outside the code repository. If none exists, obtain approval for a location. Initialize `checkpoint.json` from [the template](templates/checkpoint.json). A blank template is not a valid runnable checkpoint.

Record the actual run and coordinator IDs, repository identity, worktree path, timestamps, contract, and next action. The coordinator is the sole checkpoint writer. Workers return reports, not checkpoint edits. Save valid JSON; preserve the last valid version before replacing it atomically. Never recover malformed state by silently writing an empty checkpoint.

Use the session task database for active tracking when provided. Keep durable state sufficient for a new session to recover without chat memory: features, criterion IDs, dependencies, owners, artifacts, review findings, exact commands, failures, and next action. Do not store secrets.

Maintain `context-capsule.json` using [the capsule template](templates/context-capsule.json) and the context-management procedure. It is a compact index into canonical state, not a replacement for the checkpoint or evidence.

Register the run's single `autonomy-guardian` and perform its bounded startup check using [the guardian contract](references/context-management.md#guardian-registration-dispatch-and-corrections). Discover a callable native profile, retain its actual receipt/identity, and reconcile it on resume; a profile file alone is not a running monitor. Keep its coordinator-owned sidecar separate from the existing checkpoint schema.

Apply the authorized five-minute periodic monitoring default alongside event checks. Discover existing automation first; register one schedule owner/handle for the run and verify the actual schedule tool result and saved configuration readback before claiming automatic monitoring. A parent may own the wake-up and request fresh IDs/evidence, but the existing coordinator remains sole dispatcher. Preserve unrelated schedules, deduplicate pending/handled requests, and record a capability gap with event-only coverage when automation cannot be verified. Follow the guardian contract for no-progress investigation, costs/limits, resume, and cleanup; setup maintenance does not itself start schedules or product work.

## 3. Complete and challenge five planning gates

No implementation or test-writing worker starts before all five gates are accepted. Read-only discovery is allowed. A feasibility experiment requires an explicitly bounded planning task in an authorized isolated worktree; it does not count as delivered implementation.

| Stage | Required artifact content | Challenge focus |
|---|---|---|
| `brainstorm` | Problem and user outcome, existing behavior, repository evidence, candidate approaches, unknowns, recommendation | Wrong problem, unsupported assumptions, simpler alternatives |
| `requirements` | Required features, non-goals, user flows, failure cases, nonfunctional constraints, stable acceptance criterion IDs, draft verification matrix | Missing or contradictory behavior, scope creep, untestable success |
| `architecture` | Cohesive components, ownership, interfaces, data/control flow, dependency direction, compatibility, feature change impact, alternatives and tradeoffs | Excess coupling, cycles, scattered changes, needless infrastructure, repository mismatch |
| `design` | Narrow contracts, state/invariants, validation/errors, relevant UX, migration/rollback, operational visibility, test strategy, reasons for new abstractions | Edge cases, invalid states, backward compatibility, unobservable failure, speculative generalization |
| `implementation_plan` | Self-contained plan with paths, bottom-up tasks in working slices, dependencies, owners/worktrees, exact checks, integration/recovery steps, and required project-memory updates | Missing dependencies, edit conflicts, unused foundations, missing test/build/runtime coverage, unresolved choices |

Keep artifacts concise but complete. Do not skip a stage because the task is small; reduce its prose, not its required outputs. Do not add unrequested features or architecture.

For each stage:

1. Give a fresh `autonomy-planner` the accepted prerequisite artifact references and the current stage's bounded drafting task. It reads the detailed inputs and writes the assigned versioned artifact. Inspect its decision handoff, resolve open questions, and freeze the artifact/hash without copying the full draft into chat.
2. Invoke `adversarial-review` with the stage ID, exact artifact, prerequisites, and acceptance criteria.
3. Record both independent reports, both rebuttals, findings/dispositions, and the coordinator verdict using the protocol's review format.
4. Resolve every blocking finding with evidence. Accept only the artifact actually reviewed. Missing evidence keeps the gate blocked.
5. Persist the accepted gate and next stage, then continue automatically within the approved scope.

The coordinator accepts engineering decisions, not permissions reserved for the user or platform. A plan-mode approval prompt must be resolved through the platform's approval mechanism.

The implementation-plan artifact must use [the plan template](templates/implementation-plan.json). Embed a self-contained `plan_text` and an exact copy of the finalized `contract`. This binds features, acceptance criteria, and check applicability to a reviewed artifact. After acceptance, changing that contract requires a new plan revision and review; reducing scope or checks additionally requires explicit user authorization.

## 4. Implement bounded milestones

Before dispatching code or test writers, run:

```text
python3 <skill-directory>/scripts/validate_checkpoint.py implement <run-directory>/checkpoint.json
```

Any nonzero result blocks dispatch. Fix the missing state/evidence; do not edit the validator, remove requirements, or change a failing gate to pass.

Dispatch at most four specialists concurrently, counting planning, implementation, test, review, verification, and the guardian while running. Respect any lower runtime/user limit. The coordinator is not counted. Parallel execution is the default for ready, independent tasks with disjoint ownership. At each dispatch boundary, evaluate all ready tasks and batch independent assignments rather than waiting for an unrelated worker to finish. Run independent review initial reports concurrently when capacity permits. Serialize only for a concrete dependency, shared mutable resource/file, lower runtime capacity, or frozen-source verification; record the reason in existing run state. Do not invent work, start dependent tasks, or overlap shared-file edits just to fill slots. Review roles may run sequentially in distinct contexts when only one slot is available.

At periodic requests, stage/accepted-plan transitions, milestone handoffs, changed dispatch boundaries, and concrete drift signals, dispatch or coalesce a bounded guardian check under the same contract. Overlap it with independent work when a slot is available; otherwise enqueue at the next free slot without interrupting four existing owners. Skip unchanged inputs and never overlap guardian invocations. Consume its report and route corrections before the next affected action, not as another acceptance/rebuttal gate. An unresolved critical risk blocks that action; routine advisory findings do not pause unrelated work.

Assign code tasks to `autonomy-implementer`, with one independently verifiable task per worker, a dedicated authorized worktree, exact file ownership, dependencies, criterion IDs, permitted actions, required commands, and stop condition. Shared interfaces, manifests, and lockfiles have one named owner. No nested delegation. The coordinator does not take over a worker's code changes merely because its context is getting full.

Each kickoff includes the relevant repository instructions, accepted plan, protocol version, and required specialist skill text or readable path. Do not assume custom subagents inherit skills; verify discovery and supply the procedure explicitly.

Include the engineering-principles reference in planning, implementation, and review kickoffs. New boundaries, abstractions, dependencies, and changes to project guidance must have a specific owner and justification in the accepted plan.

Assign unique artifact output paths in each kickoff. Full reports and command logs stay there; the worker's returned message uses [the handoff template](templates/worker-handoff.json) and stays within 500 words. The same-task implementation owner handles its integration fixes; do not move verbose integration/debugging into the coordinator.

For each milestone:

1. Check authorization, deadlines/limits, current gates, and live ownership.
2. Implement the scoped behavior bottom-up within the accepted working slice and add regression tests; use `autonomy-test-engineer` for separately owned test tasks.
3. Execute targeted checks and inspect results. Preserve red/green evidence for bug fixes.
4. Complete the engineering necessity pass, then run `adversarial-review` on the frozen milestone diff and evidence. Challenge unnecessary additions and excessive change impact; resolve blocking findings before accepting the milestone.
5. Integrate in the owning session, update the scoped project memory for changed contracts/extension guidance, then execute the affected checks on the integrated result.
6. Persist task status, milestone artifact/review, failures, and next action before dispatching the next milestone.

Keep code persistent in authorized worktrees or authorized commits. A checkpoint is not a backup of source files. Do not commit/push/merge outside the contract.

## 5. Verify independently before completion

Freeze the integrated source. Use `build-and-test` and a fresh `autonomy-verifier` that did not implement the code or tests to execute the complete required matrix. Independent final verification is mandatory, not conditional on task size.

Capture the source manifest with the protocol's snapshot command before and after checks. If source changes, discard the verdict and repeat verification on the new snapshot.

Create the final verification artifact with the tested snapshot, all required gate results, feature-to-evidence mapping, and unresolved findings. Challenge it with proposer and challenger agents. Agreement cannot replace execution.

Completion requires all seven accepted stage gates, accepted implementation milestones, passed required checks, verified features, no open blockers, and no active workers or task-only helpers.

Also reconcile the guardian sidecar: no in-flight guardian check or unresolved critical affected-action finding may be hidden by the checkpoint validator. An idle registered guardian session is not active work and must not be woken solely to create a ceremonial final report. Run:

```text
python3 <skill-directory>/scripts/validate_checkpoint.py complete <run-directory>/checkpoint.json
```

Only after exit code zero may the coordinator mark the run `completed`. The validator checks records, references, hashes, and source identity; it does not authenticate agent reports or prove the software correct. The coordinator inspects the verifier's structured results and bounded exact evidence excerpts, not every line of raw logs. Missing or contradictory evidence gets a targeted follow-up, never an assumed pass.

## 6. Recover, yield, and stop

Apply the protocol's evidence-based deterministic repair and review-continuation policies, finite transient retry limits, and stop rules. Neither repair nor review has a fixed count cap or a new routine per-cycle permission requirement. The coordinator inspects a genuinely distinct investigated hypothesis before repair and actual corrections/new evidence against findings before review continuation. Beyond the former default of two review cycles, require changed subject/prerequisite hashes versus the preceding cycle, with only the protocol's historical approval compatibility exemption. Preserve all contiguous cycle records, four reports per cycle, findings and verdicts, same-operation repair accounting, failures, honest results, and content-hashed logs. No evidence-backed next step means a technical blocker, not blind retries or a routine permission question. Permissions, user stops, deadlines, and spending/budget limits remain unchanged. Checkpoint at every stage/milestone transition, dispatch, result, failure, and before yielding or context reduction. Keep full logs in artifacts and concise summaries in model context.

Refresh the context capsule after each checkpoint update and before compaction or a handoff. Compaction does not reset gate decisions, review/retry counts, ownership, deadlines, or limits. Use the runtime's real context-pressure signal; do not invent a remaining-token estimate.

Use `autonomous-resume` after interruption. Native completion notifications resume ordinary work; do not poll or run sleep loops. The authorized periodic guardian policy uses verified native automation under the guardian contract, not model polling. Broader scheduled delivery continuation requires separate authorization and an actual serialized supervisor with persistent storage, host availability, user-stop handling, and enforceable requested limits; monitoring authorization alone does not grant it.

No supervisor is installed by this skill. Copilot hook timeouts and stop-hook continuation caps mean a hook alone is not an unbypassable completion barrier. Do not label a local instruction-driven run as hard-enforced.

On user pause/stop or a limit, stop dispatching and preserve work; a wake-up cannot resume it. At product completion or cancellation, clear only the owned guardian schedule through its registered owner, verify cleanup by readback, and disable only this run's authorized continuation schedule. Separate setup completion is not live product completion and must not clear its monitoring. Do not archive or delete sessions with user work. Report the actual outcome and outstanding blockers, not a promise that an idle session will eventually finish.
