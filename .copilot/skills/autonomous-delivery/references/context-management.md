# Context management for autonomous runs

Subagents isolate their detailed work from the coordinator's context. They do not make the main context infinite: returned reports, parent tool output, instructions, and conversation history still consume it. Artifact storage preserves evidence; it does not remove text already loaded into a conversation.

## Division of work

| Role | Owns | Main-session return |
|---|---|---|
| Coordinator | User intent, permissions, task dependencies, dispatch, checkpoint, adjudication, user communication | Decisions and next action |
| `autonomy-planner` | Bounded repository discovery and one planning-stage artifact | Recommendation, open decisions, artifact references |
| `autonomy-implementer` | One code/integration task in its assigned worktree and targeted checks | Changed interfaces/paths, criterion IDs, check outcomes, source/artifact references |
| `autonomy-test-engineer` | Assigned test files, regression proof, test execution | Coverage, failures, test/evidence references |
| `autonomy-proposer` / `autonomy-challenger` | Independent stage analysis and rebuttal | Compact complete finding/disposition report or runtime-managed report reference |
| `autonomy-verifier` | Final check execution, source identity, full evidence ledger | Per-category verdict, blocker IDs, verifier/ledger references |
| `autonomy-guardian` | One bounded read-only check of intent, execution, evidence, and ownership drift | Deduplicated findings, smallest corrections, confirmation criteria, coverage limitations |

Delegate a whole bounded work item, not every command. The coordinator performs short status lookups, targeted evidence reads, metadata updates, and gate-validator calls directly. Routine setup maintenance and ordinary questions do not launch this worker topology.

Create fresh workers for new stages or independent work items. Reuse a worker only for same-task follow-ups, such as fixing its defect or answering a review objection. Do not run a permanent general-purpose worker that accumulates the entire project history.

## Guardian registration, dispatch, and corrections

The guardian is one logical observer assigned to one run, not an additional delivery or acceptance stage. The current coordinator registers it at startup or authorized resume and remains the only state writer. Setup maintenance itself does not start a product run or contact its owners.

**Discover and register.** Read the installed `autonomy-guardian.agent.md` under the configured Copilot home. Check the actual runtime tool catalog before dispatch. Use the native custom-agent route when it exposes this profile. In the app, a fresh `create_session` with `kickoff.agent: "autonomy-guardian"` and `kickoff.mode: "interactive"` can load a user-level profile even when the already-loaded `task` agent enum lacks it. Supply the bounded kickoff below, an authorized project/host with readable artifacts, and a native completion notification when supported. Do not set a model override, create a product worktree merely for monitoring when an authorized existing workspace is supported, or require restarting the active coordinator. Confirm the launch receipt and returned profile behavior; profile installation is not proof of runtime invocation.

Persist one coordinator-owned `guardian-state.json` beside run artifacts, outside product source. Keep only: `run_id`, profile name, actual guardian session/agent ID and invocation history, coordinator ID, current status (`idle`, `running`, `queued`, `unavailable`, or `unknown`), current/pending check IDs, last input fingerprint and report references, a findings ledger, and optional monitoring metadata and progress observations below. Reports use existing path/hash artifact references. A check fingerprint identifies the original goal/amendments, accepted input/source hashes, ownership/status snapshot, and material trigger; ignore timestamp-only churn and recurring request IDs. This is operational sidecar state, not a checkpoint schema extension or an acceptance artifact.

Before every dispatch or resume, reconcile that registration with authoritative live status using known IDs. Reuse the same native session for successive same-run bounded checks, passing only current inputs and ledger deltas. Never launch a second guardian for the run. If a confirmed terminal/lost session cannot be reused, preserve its identity/history and register a non-overlapping successor for the same logical guardian only after confirming the prior invocation has ended. Unknown identity/status blocks a replacement, not permission to race it. If a guardian is running, coalesce new triggers into its pending next check; do not send concurrent checks.

If `task` has a static catalog without `autonomy-guardian`, do not impersonate it with a generic agent, proposer, challenger, or verifier. Use the fresh native-profile route only if actually exposed and authorized. Otherwise record `unavailable` with the precise capability gap; there is no independent guardian report to claim. The coordinator keeps its existing safety duties and queues the missing check. If the native profile runs but cannot message, its returned response is the coordinator-consumed report fallback described below. Missing capability blocks any dependent safety decision, not already-authorized unrelated work. No restart or polling loop is required; profile availability and scheduling availability are separate capabilities.

**Periodic wake-ups plus event checks.** For autonomous runs, the default cadence is five minutes when supported authorized host/session automation is available. This standing preference does not start a product lifecycle or schedule for standalone setup/how-to work. Discover existing automation first; register exactly one schedule owner and schedule handle, bound to this run and its single guardian. The owner may be the parent session rather than the delivery coordinator. Preserve existing unrelated automation: never silently overwrite an unrelated schedule to obtain the one available slot. A conflict or unknown ownership is a monitoring capability gap until resolved within authorization.

Before claiming automatic monitoring, call the actual schedule tool when registration/change is needed and verify its result against a saved configuration readback (owner, handle, cadence, enabled state, wake prompt, and run/guardian binding). For an existing schedule, inspect the actual saved configuration and retain its genuine registration receipt if available; missing historical receipts are not invented. Record tool receipts/readback references and verification time in the sidecar. A file or intended cadence alone is not an enabled timer. If automation is unsupported, unavailable, or unverified, record the precise monitoring capability gap and retain event-driven checks truthfully. Do not invent OS cron, a background daemon, or constant model polling. A native scheduler wakes its owner; the guardian runs only when invoked. There is no guarantee of uninterrupted execution or host availability. Account for recurring tokens and cost; no schedule overrides a spending limit, budget, deadline, permission, or user stop.

The timer owner requests fresh exact background-agent IDs, authoritative status, current artifact/source identities, and changes since the last check from the existing coordinator; use available status tools and targeted artifact reads, not self-report alone. Distinguish timestamped snapshots from direct observation and record unavailable tools/hosts as coverage limits. The coordinator is the sole dispatch owner; a parent wake-up must not spawn, replace, or directly dispatch guardians/workers. Maintain pending and handled request IDs across both owners' handoffs so repeated deliveries/wakes cannot double-dispatch. Mark requests handled only after recording a dispatched check, coalescing into a tracked pending check, or an evidenced skip/stop/gap disposition. Check run state and capacity first; no overlapping guardian invocations. Coalesce requests while running or full, then dispatch at the next free slot; scheduled wakes do not reserve a specialist slot.

After refreshing status and evidence, skip unchanged inputs rather than spending another guardian invocation on identical evidence. Still record the scheduled observation/disposition. After two consecutive scheduled checks without substantive progress (including unchanged-input skips), perform one bounded investigation of exact owner status, pending requests, artifact changes, and any known tool wait; surface the specific stall or monitoring gap with evidence and an actionable next event. This is not proof of worker failure or permission to restart accepted planning: not blind nudges or duplicate workers. Retain the count and investigation evidence on resume; suppress repeated escalation for the same unchanged condition until new evidence or an authorized recovery action exists.

Also check at startup/resume, stage or accepted-plan transitions, milestone handoffs, and dispatch boundaries where intent, evidence, source, or ownership materially changed. Check concrete drift signals: preview/synthetic proof substituted for a requested real integration; unsupported completion claims; unapproved scope expansion; duplicate work; ready independent work serialized without reason; stale evidence; skipped gates; unsafe next actions; or repeated rework without semantic progress. A status complaint is a reason to inspect known evidence, not proof of drift or permission to restart planning.

Optional additive sidecar fragment (illustrative defaults only, not runtime receipts; missing historical metadata means unknown/unverified and requires schedule discovery, not recreation):

```json
{
  "monitoring": {
    "cadence_minutes": 5,
    "owner_id": null,
    "handle": null,
    "status": "unverified",
    "registration_receipt": null,
    "readback_ref": null,
    "verified_at": null,
    "pending_request_ids": [],
    "handled_request_ids": [],
    "unprogressed_checks": 0,
    "investigation_ref": null,
    "capability_gap": null,
    "cleanup_ref": null
  }
}
```

Use the containing sidecar's actual run/guardian identities, not another registry or checkpoint schema. Preserve request dispositions, evidence/report references, investigation history, and prior schedule identity when metadata changes; null defaults never overwrite real receipts or counters.

Coalesce simultaneous events and unchanged inputs into one check. Do not dispatch for each tool call, repeatedly review accepted unchanged stages, or demand a clean guardian report for every transition. Count its executing invocation within the total four-specialist ceiling (or lower actual limit), across both registries; an idle registration does not reserve a slot. Overlap read-only checks with independent work when capacity permits. If four owners are executing, enqueue the check at the next free slot; never interrupt them to make room. A known critical risk still blocks its next affected action while queued.

**Bounded kickoff.** Supply run/check/coordinator IDs, the original user goal and authorized amendments (with evidence references), current approved contract/plan and criterion IDs, relevant artifact/source identities, exact allowed read paths, known owners and timestamped live-status snapshot, ready tasks/dependencies and any serialization reason, previous finding IDs/dispositions/deliveries, available [progress observations](#progress-observations), trigger, and a concrete check budget (for example one pass over named artifacts and at most three targeted status/diff reads). Include protocol/context-management paths, tool/capability limits, and stop-after-report. Never supply the full transcript or authorize writes. Ownership changes in an overlapping check require coordinator revalidation before routing.

**Handoff and correction loop.** The guardian returns JSON within 500 words:

```json
{
  "run_id": "...", "check_id": "...", "guardian_id": null,
  "status": "observed", "input_refs": [], "coverage_limits": [],
  "findings": [{
    "id": "G-001", "severity": "critical", "affected_action": "...",
    "evidence": [], "recipient_id": "...", "correction": "...",
    "confirm_by": "...", "delivery": "report_only"
  }],
  "confirmations": [], "next_trigger": null
}
```

`status` is `observed`, `limited`, or `unavailable`, never stage acceptance or run completion. `guardian_id` is the actual receipt ID, filled by the coordinator if unknown. Evidence includes exact path/hash and location or timestamped runtime observation; hypotheses are labeled. `delivery` is `report_only` or `sent` with the actual recipient/message receipt when available. A direct message is allowed only through an exposed tool to a supplied known coordinator/owner, for a high-confidence in-scope correction preserving existing assignment and authority. No messaging capability means response-only delivery; the coordinator persists/hashes the report, consumes it, and routes the correction. The guardian never writes even its own report.

The coordinator deduplicates by finding ID and underlying issue/affected scope (not wording), retains evidence/version and delivery history, and records recipient, disposition (`open`, `routed`, `awaiting_confirmation`, `resolved`, `refuted`, or `declined`), corrective action, and confirmation evidence. Check ownership before sending; do not send again when the same correction already reached the owner. Acknowledgement alone is not resolution. Confirm the criterion on changed evidence at a later natural boundary; reopen only when new evidence warrants it. Do not erase unresolved findings on compaction/resume.

An unresolved critical finding blocks the next affected dispatch, acceptance, unsafe action, or completion until resolved/refuted with evidence; mirror that scoped blocker into the existing checkpoint format. The guardian cannot cancel or control a worker already executing: promptly route urgent evidence to the coordinator, which handles existing stop/permission procedures. Routine advisories may be declined with a reason and never globally stall independent work. A hypothesis or incomplete coverage must not be represented as verified drift; identify the exact dependent decision needing evidence. No gate, permission, or acceptance override is permitted.

Reports are bounded corrections, not proposer/challenger rounds, another four-report gate, or a substitute for final verification. Before completion/yield, reconcile pending critical corrections and actual in-flight checks; do not start a ceremonial guardian final-review cycle. Preserve its registration/report index for resume. The guardian monitors only while invoked and stops after each budget/report; an idle session is not watching agents. Verified periodic wake-ups are automatic requests, not continuous observation or an external supervisor.

On user pause or stop, no new dispatch is permitted; record pending requests as held/stopped, and the registered owner should suspend/clear only its owned schedule to avoid further wakes. A wake-up never resumes stopped work. On completion or cancellation, clear only the owned schedule through the actual registered owner/tool and verify cleanup by readback; preserve unrelated automation and retain the cleanup receipt/history. If cleanup is unavailable, record and surface the outstanding monitoring gap rather than claiming it stopped. Separate scoped setup completion is not live product completion: it must not cancel the live run's schedule or relaunch its coordinator.

## Progress observations

The coordinator may retain this compact optional observation in the existing guardian sidecar and supply it to the next check. The guardian may return `progress_observation` alongside its bounded handoff; the coordinator persists it. Reuse existing task reports and path/hash evidence references, not a new registry or acceptance schema. Illustrative empty fields below are not actual runtime receipts; null means unknown, and empty lists mean no supplied observations, not proof of no work:

```json
{
  "progress_observation": {
    "previous_ref": null, "current_ref": null,
    "verified_slices": [], "planning_evidence": [],
    "work": {"active": [], "ready": [], "blocked": []},
    "unresolved_finding_ids": [], "correction_effects": [],
    "last_substantive_evidence_at": null,
    "elapsed_since_evidence_seconds": null,
    "active_work_seconds": null, "usage": null, "cost": null
  }
}
```

Compare prior/current evidence, not report counts. Each slice names its criterion, exact consumer, and passing boundary evidence; meaningful planning progress (resolved contradiction, accepted contract, new feasibility evidence) belongs separately from a user-visible verified slice. Work entries name task/owner, true prerequisite evidence or blocker, and any serialization reason. A correction effect names the finding, confirmation evidence, and observed effect: an unblocked task, removed unnecessary scope, enabled safe parallel task, or corrected unsupported claim. An unblocked task is not delivered functionality. Acknowledgement, metadata cleanup, and timestamp-only rewrites are not confirmed effects or substantive progress.

Planning with no implementation yet is not failure: optional progress fields do not create new current-stage evidence requirements. Apply [Good-enough acceptance and stop](../../adversarial-review/SKILL.md#good-enough-acceptance-and-stop), not an implementation-first productivity threshold.

Record time since last substantive evidence only from genuine comparable timestamps, with their source. Elapsed time is not active work or proof of a stall; keep unavailable timing, usage, and cost unknown, never infer them from turn counts or cadence. A confirmed correction effect is not a measured throughput improvement. Apply the existing two-unprogressed-check investigation, not a new productivity threshold: inspect a legitimate wait for a named active prerequisite and substantive interim evidence before alleging failure. Recommend parallel work only with true prerequisite readiness and available capacity; four occupied slots are not a serialization violation. These observations do not add a guardian approval gate or override stops, limits, or required evidence.

## Kickoff packet

Pass only:

- Run/stage/task IDs, role, observable user outcome or necessary enabling contract, criterion IDs, exact consumer, and the precise stop condition.
- Applicable instructions and skill/protocol paths, which the worker must actually read.
- Accepted input artifact paths/hashes and the relevant source revision/worktree.
- File ownership and ownership conflicts, permissions, true prerequisites with prerequisite evidence, exact check commands, and actual limits.
- Unique artifact output paths, evidence-to-return for the outcome/consumer, and the handoff schema.

Use existing task reports/state for these fields. At dispatch, evaluate all eligible independent tasks within capacity under the protocol; serialize by actual prerequisite or shared resource, not whole feature/stage labels. Preserve required stage-gate dependencies, accepted inputs, and file isolation; an enabling contract is useful progress but not a claim of delivered user functionality.

Do not paste the entire parent transcript, all prior plans, or other workers' raw logs. A worker must have access to the referenced files on its actual host. If paths are not accessible, provide an authorized artifact transfer; never invent shared filesystem access or send private artifacts to an unrelated service.

## Bounded discovery and change batching

The coordinator owns incoming decisions; a discovery worker is not a continuously refreshed copy of the conversation.

- Define the exact question, evidence sources, output paths, and observable stop condition before dispatch. Verify the required tools are actually exposed to the assigned role; a declared tool profile is not evidence that a callable tool exists.
- Record each user decision promptly in canonical state, but forward it only when it changes the worker's current assignment. Accumulate non-urgent, relevant deltas into one consolidated update at a task boundary. Do not reopen discovery for details that belong to a later planning stage.
- Deliver user stops, permission revocations, safety issues, and changes that invalidate current work immediately. Do not batch these behind other work. Never accept an artifact against superseded inputs; apply the protocol's stale-gate and re-review rules.
- Once the assigned assessment is complete, request its final handoff and end the worker's turn. Freeze the delivered evidence instead of requesting a full rewrite for each new clarification. A follow-up must identify a specific missing conclusion or material contradiction and the minimum evidence needed to resolve it; preserve prior versions and retry/review counts.
- Distinguish researchable unknowns from external dependencies. Missing administrator approval, consent, credentials, authorized validation, or a required capability gets a bounded blocked handoff for the affected assignment, with the completed findings and the exact action needed. More documentation cannot substitute for those prerequisites; the worker's blocker does not automatically pause unrelated work.
- When a user asks about a delay, report the actual assignment, completed outputs, and known executing or queued work. Say when the runtime does not expose the current tool wait. Do not launch duplicate research, poll repeatedly, or hide a finished assessment behind pending document edits.

Before pausing the whole run, record the blocker's actual scope, affected tasks/gates and dependencies, and whether any already-authorized independent work is ready. Continue that ready work without bypassing gates. A blocked live check does not by itself block independent brainstorming; it still blocks any acceptance requiring that check's evidence. If no eligible work remains, record that reason and request the precise missing input.

Do not infer a user stop from a delay complaint, a status question, or an idle worker. Whole-run stopping requires an actual global stop/limit, an unresolved run-wide safety or capability blocker, or no eligible independent work. This procedure does not reduce planning gates, independent reviews, verification requirements, or permission boundaries. It is coordination guidance, not a runtime-enforced timeout or spending control.

## Artifact-first output

Each worker returns at most 500 words using `templates/worker-handoff.json`. The status is `ready_for_review`, `blocked`, or `failed`; a worker cannot declare the run completed. Runtime IDs come from actual launch/result receipts. If the worker cannot see its ID, the coordinator fills it from the receipt rather than accepting a guess.

The same limit applies to a separately saved handoff artifact. Keep detailed assessments and source excerpts in their own artifacts and reference them; do not turn the handoff into a second full report.

Persist detailed plans, diff explanations, check commands/output, and structured evidence in the assigned artifact files before returning. Include paths and tool-computed content hashes, not their complete contents. A worker without a hashing tool returns `pending_artifact_paths`; the coordinator computes the hashes directly from the assigned files before adding canonical artifact references. Never invent a hash or weaken the gate's hash requirement. Preserve exit codes when redirecting output; a successful log-writing command must not mask a failed build/test.

Planner/implementation/test workers may write their assigned artifacts, never `checkpoint.json` or another worker's artifacts. The verifier may generate logs and its report/ledger in assigned output paths, but cannot edit source or the checkpoint.

Proposer/challenger toolsets remain read-only. Use a runtime-managed result artifact when the runtime actually supplies one. Otherwise return the complete bounded report and let the coordinator save that small report. The guardian likewise returns its dedicated bounded JSON above for coordinator persistence, rather than writing an artifact or using the delivery-worker handoff schema. Do not grant reviewers write access merely to save tokens. If a complete review cannot fit the handoff and no artifact facility is available, return `blocked` with the delivery limitation; do not truncate away a finding or claim the review is complete.

Every handoff includes the blocking-finding IDs. When their index cannot fit, persist the complete index, return its reference and total count, and keep the task blocked until every finding has a recorded disposition. Brevity is not authorization to omit failures, alter evidence, or weaken a gate.

## Coordinator reading policy

- Keep the objective, immutable constraints, current stage, ready task IDs, active worker IDs, unresolved decisions, and next action in the working context.
- Read handoffs and the current decision artifact, not every supporting file. Use structured queries to select checkpoint fields rather than dumping growing ledgers.
- Run the gate validator against full on-disk state; consume its short result. Hash large artifacts with a tool rather than reading them into model context.
- Validate and import structured worker evidence with a local data operation; do not route an entire ledger through model text just to copy it into the checkpoint. Preserve all existing checkpoint fields and keep the coordinator as the only writer.
- When evidence is insufficient, request a specific conclusion with exact evidence excerpts from the existing task owner or assigned reviewer. Do not repeat its broad search.
- Do not fetch entire transcripts, rerun verbose commands in the parent, or reread already accepted artifacts just to remember them. Reference their stable IDs/hashes.
- No polling loops. Synchronous delegation also isolates context; use background work only while there is independent coordinator work. After notification, read the bounded result once and use incremental reads only for new same-task output.
- Full reports remain authoritative evidence for reviewers and verification. A short handoff alone is not sufficient to accept a gate.

## Checkpoint and context capsule

After every checkpoint update, write `context-capsule.json` using the template. It must remain within 1,000 words by linking to long lists and artifacts. It includes the checkpoint path/hash, run and coordinator IDs, objective, current phase, non-negotiable constraints, pending decisions/blockers, active worker IDs, relevant artifact references, and next action.

The capsule is a projection of `checkpoint.json`, not independent authority. Do not embed the capsule's hash back into the checkpoint: the capsule already hashes the checkpoint, so that would create a circular dependency. Its path may be recorded as an ordinary artifact-path string.

The coordinator alone updates the capsule. If its checkpoint hash is stale, rebuild it from canonical state before relying on it. On recovery, verify state through `autonomous-resume`; do not copy capsule status into the checkpoint or reconstruct missing evidence from a summary.

## Context refresh

Checkpoint and refresh the capsule at every stage/milestone boundary and before yielding. This is required even when token telemetry is unavailable.

If the runtime reports at least 70% context usage, or issues a context-pressure/compaction warning, do not dispatch another work item until the checkpoint and capsule are saved. Use supported native compaction, or let the runtime's documented automatic compaction finish. Never print a slash command in chat and claim it executed.

If the runtime exposes neither a usable compaction mechanism nor automatic compaction under context pressure, pause dispatch and provide a capsule-based resume handoff. Do not claim an unsupported automatic coordinator replacement.

When no token telemetry exists, do not estimate a percentage from message count. Continue bounded handoffs and boundary checkpoints so native compaction or a resumed session can recover. These practices reduce growth; they do not guarantee a fixed upper bound on total context.

After refresh, reload the personal routing rules, the delivery protocol, and the capsule. Reconcile the current checkpoint, relevant artifact hashes, and live ownership before continuing. Do not replay completed stages, reset transient retry accounting, erase contiguous review history, or duplicate active workers. Review continuation follows the protocol's evidence-backed progress rule, not a fixed cycle budget; retain historical approval records and inspect actual changes against findings.

Also reconcile `guardian-state.json` beside the checkpoint: retain the same guardian registration, pending triggers, finding IDs, delivery history, and unconfirmed corrections. Discover/reconcile its existing schedule owner/handle and saved configuration before any change; preserve pending/handled request IDs, no-progress counts, and receipts across resume rather than duplicate or reset monitoring. Do not lose this sidecar merely because it is intentionally outside the version-3 checkpoint/capsule schema.

A fresh coordinator session is a separate recovery operation, not an ordinary subagent. Establish an explicit ownership handoff and confirm the old coordinator is no longer dispatching before the new one writes state. Never fork a competing coordinator just to gain another context window.
