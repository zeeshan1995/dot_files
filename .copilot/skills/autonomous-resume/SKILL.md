---
name: autonomous-resume
description: "Recover an existing autonomous run from a durable checkpoint, accepted stage artifacts, live ownership, and verified code state. Never duplicate active workers, skip missing gates, reset retry budgets, or treat an interrupted run as complete."
---

# Resume autonomous work

Load the sibling `autonomous-delivery` skill and its `references/protocol.md`. If these cannot be read, report a blocker. A resume request permits recovery of the recorded task, not new scope or new permissions.

## 1. Identify the run

Use the supplied checkpoint path and run ID. If absent, inspect only the relevant session's history/artifacts. Ask the user if the run remains ambiguous; do not scan their home directory.

Read the compact `context-capsule.json` when present, verify its checkpoint hash, and use it to select the relevant canonical records. A stale or missing capsule is rebuilt from the actual checkpoint after ownership is established; it never replaces missing gate evidence. Do not reload the entire prior conversation or every worker transcript.

Validate JSON, schema version, repository identity, coordinator, and contract. Never reconstruct missing state from guesses or execute command strings simply because they appear in a checkpoint.

The current schema is version 3. For an older version, preserve the original checkpoint, establish exclusive ownership, and migrate explicitly against the current template. Copy facts and artifacts, retain failures/counts, and mark gates without verifiable review records incomplete. Do not synthesize acceptance. Unknown future versions block recovery.

## 2. Establish exclusive ownership

Read authoritative session/agent activity using recorded IDs before writing state. A quiet branch, old timestamp, or idle turn is not proof that the run is abandoned.

- Another active coordinator: observe and yield; do not take over.
- Active workers: preserve assignments and await native results; do not duplicate them.
- Pending input/plan: read the exact request and resolve only with existing user/platform authorization.
- Unknown ownership or overlapping scheduler invocations: block until exclusive ownership is established by the runtime or user.
- Confirmed interrupted owner: preserve its source/artifacts, record the new coordinator ID, and proceed.

Do not remove a lock based only on age. Never discard user changes to make recovery easier.

Reconcile the single guardian's `guardian-state.json` under the [guardian contract](../autonomous-delivery/references/context-management.md#guardian-registration-dispatch-and-corrections), including its actual known session ID, live invocation status, pending checks, and unconfirmed corrections. An active guardian keeps its assignment; unknown status forbids a duplicate. Missing sidecar state in a historical run is initialized by the exclusive coordinator without changing checkpoint schema or invalidating accepted gates. Discover the native custom profile before dispatch; a static task enum missing `autonomy-guardian` is not permission to substitute another role or restart the product coordinator.

Discover the existing schedule through its registered owner and actual automation tools before creating or changing anything. Verify the schedule handle, run/guardian binding, cadence, authorization, and saved configuration readback; never duplicate or reset an existing schedule or its pending and handled request IDs, input fingerprint, finding/correction history, or unprogressed-check count. A parent-owned timer remains a request source, not another dispatcher. Preserve an unrelated schedule; uncertain ownership blocks replacement. Historical missing monitoring metadata is unknown/unverified, not evidence that no schedule exists. If supported authorized automation is absent, record the monitoring capability gap and retain event checks; do not invent receipts, OS cron, or a daemon. Reconcile stops and limits before any periodic or resume dispatch.

## 3. Reconcile evidence, not assertions

Run the protocol's checkpoint audit. Compare actual worktree/branch/source state, artifact hashes, review records, task dependencies, known process IDs, and automation state with the checkpoint.

Resume the earliest incomplete or stale stage. Keep accepted planning when its artifact, prerequisite hashes, and contract are unchanged. Missing reviews require a real review, not self-certification.

An implementation change that follows the accepted plan invalidates code-dependent verification, not the entire brainstorming process. A changed requirement, interface, architectural decision, or verification contract invalidates that stage and dependent stages. Preserve unrelated valid work.

Before resuming code/test edits, pass the `implement` validator action. Before new feature work, run the accepted plan's baseline smoke/regression command to establish that the recovered environment works. A failure blocks dependent work and is investigated; it is not hidden by starting a new feature.

Delegate recovered source investigation and command execution to their bounded owners, using artifact references and short handoffs. Native compaction of the same coordinator does not authorize duplicate workers; replacement of a coordinator requires the explicit ownership handoff described in context management.

Carry review-cycle, failure, and retry counts forward. Do not reset them by renaming a task, spawning another agent, or starting another session. Review has no fixed cycle cap: preserve every four-report cycle, findings/verdict history, and existing historical approval artifact. Continue only on corrections/new evidence inspected against findings under the protocol's changed-subject/prerequisite-hash rule beyond two cycles and its historical-third-cycle compatibility rule. No fresh routine per-cycle approval is required; no-progress blockers and external permission/stop controls still apply.

## 4. Respect stop states

`completed` and `failed` do not relaunch. `paused` stays paused until the user resumes it. `blocked` resumes only after the recorded blocker is resolved with evidence. A wake-up never grants extra permission or extends a deadline/budget.

If a requested hard limit cannot be enforced, unattended continuation is blocked. If ownership, capability, or persistence cannot be verified, report that precise gap rather than silently degrading the run.

## 5. Continue one bounded action

Persist the reconciled checkpoint and next action before dispatch. Follow `autonomous-delivery`, including independent stage review and final verification. Only the current coordinator writes state; reviewers return reports.

Dispatch/coalesce the bounded resume guardian check and authorized periodic requests against the recovered original goal, authorized changes, fresh exact owner IDs, current artifacts and ownership. Count it within the four-specialist ceiling; queue at the next free slot if all slots are occupied. Skip unchanged inputs and never overlap guardian invocations. Consume its report and confirm existing corrections on evidence before the next affected action; routine advisories do not pause independent work. After two consecutive scheduled checks without substantive progress, follow the bounded investigation/monitoring-gap contract, not blind nudges or duplicate workers. This is not a new planning/review gate or a perpetual monitor, and does not waive any stop state above.

Before yielding, save completed work, unresolved blockers, evidence references, and the next action. On user pause/stop, do not dispatch new work. At product completion/cancellation, stop this run's task-only helpers and clear only its owned monitoring schedule through the registered owner, verifying cleanup by readback; preserve unrelated schedules. A separate setup-maintenance completion is not completion of the live product run. Preserve code and artifacts. Report the actual state without claiming that a stopped process is still working.
