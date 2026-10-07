---
name: adversarial-review
description: "Run independent proposer/challenger review at every autonomous stage or on an explicit debate request. Use fixed rounds, concrete counterexamples, evidence-based finding resolution, and a coordinator verdict; never simulate independence or argue indefinitely."
---

# Adversarial review

Load `autonomous-delivery/references/protocol.md` from the sibling skill directory. Review concise written proposals and evidence, not private internal reasoning. The objective is a correct decision, not mandatory disagreement.

## Inputs and capability

The coordinator supplies a stage/milestone ID, immutable artifact and SHA-256, accepted prerequisite hashes, repository snapshot/context, acceptance criteria, constraints, and the review-cycle number.

Use `autonomy-proposer` and `autonomy-challenger` in distinct real agent contexts. Verify that the runtime exposes those profiles with read/search-only tools. If it cannot, block the required review and report the missing capability. Do not substitute a broad-write agent, coordinator self-review, or fictional role-play.

Each agent receives repository conventions and this review procedure explicitly. Agents do not inherit skills merely because a parent loaded one. Neither reviewer may execute commands, edit source/state, launch other agents, or expand scope.

Apply the delivery skill's context-management procedure. Pass frozen artifact references, not whole research transcripts. Each returned review report is at most 500 words or points to a complete runtime-managed result artifact; no finding may be silently truncated. Read-only reviewers do not gain write tools to persist reports.

## Cycle structure

Each cycle has exactly two rounds:

1. **Independent analysis:** give both agents the same packet, without the other agent's output. The proposer recommends a solution, states assumptions/tradeoffs, and gives a falsifying test. The challenger forms its own alternative, identifies concrete counterexamples and missing evidence, and gives a discriminating test.
2. **Rebuttal and final findings:** exchange the written reports once by artifact reference when accessible, otherwise as the complete bounded reports. Each role addresses the strongest evidence, corrects errors, and states remaining findings. The proposer must concede valid objections; the challenger must retract refuted objections.

Use same-task follow-ups for rebuttals only when supported. For one-shot agents, create a fresh context for that role with the packet and both reports, and record its distinct returned ID. Never imply the earlier process continued.

There is no fixed review-cycle cap or new per-cycle approval requirement within authorized scope. A corrected artifact or genuinely changed prerequisite evidence uses the next contiguous cycle under the same stage/milestone, never a reset. Preserve every prior packet, four reports, findings, dispositions, and verdict. Before continuation the coordinator must inspect whether the actual changes address prior findings; cosmetic changes and blind repeated debate are not progress. Cycles beyond the former default of two require a changed subject hash or prerequisite hash map versus the preceding cycle; unchanged evidence blocks continuation. Version the subject artifact to carry genuine new evidence rather than rename a gate or erase history. Follow the protocol's backward-compatible historical approval rules; existing first/second cycles and a valid historically approved third cycle remain valid without retroactive progress checks.

Review roles count toward the run's concurrency/usage limits. They may execute sequentially, but their initial assessments remain independent.

## Semantic correction packet

For a correction cycle, include in existing versioned task/review artifacts: prior finding IDs, evidence-backed root cause, changed contract/paths, downstream impact (affected consumers, prerequisites, checks, and acceptance), the distinguishing evidence/check, and accepted unaffected material to preserve. Link prior/current subjects and findings; a timestamp/hash change alone is not a correction.

Both roles inspect the full current subject for consistency while focusing correction analysis on the changed scope and its impact. New genuine findings remain admissible, including defects outside the edited lines that violate required behavior; scope discipline is not forced acceptance or old-findings-only review. Keep both independent reports and both rebuttals. The coordinator inspects semantic effect before continuation and invalidates dependent acceptance when contracts/prerequisites change under the protocol.

When real blockers remain, trace the root cause and complete affected consumer trace before assigning one coherent patch. Prefer one canonical contract definition plus references over conflicting duplicated paragraphs (for example exact interfaces repeated across requirements and design). Perform a semantic preflight against affected consumers, accepted prerequisites, and prior findings before requesting another cycle; partial wording fixes are not a complete same-cause correction. Distinct new errors still need current checks.

## Required reports

Each report names the stage, artifact hash, runtime agent ID, role, round, recommendation, evidence, and findings. A finding contains a stable ID, the challenged claim, impact, evidence or explicit hypothesis, proposed correction, and the observation that would resolve it.

Classify a finding as blocking only when it traces to an approved criterion, governing invariant, permission boundary, required verification result, or a concrete counterexample to required behavior. Cite the exact source/criterion and missing or contradictory evidence; an unresolved empirical requirement remains blocking. An invented ideal or unsupported preference is not a requirement. Pure style preferences are advisory and must not be promoted into invented defects.

All findings need a recorded disposition. A blocking finding is closed only as:

- `resolved`: the current artifact/code addresses it and evidence demonstrates the resolution;
- `refuted`: contrary evidence disproves it.

Do not close a blocking finding as deferred, risk accepted, probably fine, or safer by intuition. If a required empirical claim cannot be checked, keep it blocked. Advisory preferences may be declined with a reason; label them advisory from the evidence, not to evade a blocker.

## Good-enough acceptance and stop

Grade the current stage against its approved criterion and required invariant, not a hypothetical ideal. A blocking report must state the exact source anchor, a concrete supported failing scenario or contradiction OR genuinely required stage-appropriate missing evidence, the material consequence, and a falsifying or resolution check. A reasoned counterexample can establish a planning defect; do not require code/runtime proof before implementation is allowed. Future runtime tests planned but not yet executed are not missing current-stage evidence unless an approved current criterion genuinely requires empirical proof.

Confidence, labels, or severity alone do not establish a blocker. "Need more confidence", a possible future feature, or preferred naming, refactor, or style is advisory without a traceable material violation. Accessibility, security, performance, and architecture can block when concrete required behavior or an invariant is breached, even when labeled minor; none is categorically exempt. Duplicated contradictions that affect consumers block, but optional cleanup does not. The coordinator adjudicates exact required scope: reject or refute unsupported blocking claims with evidence, never invent a requirement or hide a real risk. Keep the original claim and evidence-backed disposition; a blocking finding must be refuted, not silently relabeled and declined.

With both rounds completed (four reports), required stage criteria and evidence current and satisfied, real blockers resolved/refuted with evidence, and advisory findings explicitly resolved or declined with a reason, the coordinator ACCEPTS and advances to the next authorized action. Open findings still prevent acceptance, including advisories. This is sufficient acceptance, not a 100-percent score or zero imaginable issues; all other protocol gate prerequisites still apply.

Default to declining nonessential suggestions for the current scope unless an existing authorized required criterion needs them. Preserve low-priority suggestions and their rationale in the existing review record, with no new mandatory backlog or task. Do not silently fix nits and induce re-review: no new cycle or polish task for only optional refactoring, nits, or the mere existence of an advisory.

In round two, synthesize each other's strongest findings, correct mistakes, and state remaining required gaps; this is not a mandatory new-defect hunt, and sufficient evidence means the roles may agree. New concrete required defects remain eligible in any round, including round two; not all defects must be found in round one. Accepted unchanged subjects are not reopened for newly imagined enhancements. A newly supported required defect or genuinely changed evidence, source, or requirements warrants scoped review under the protocol's stale-acceptance rules, preserving accepted unaffected material.

These rules preserve two independent roles, exactly two rounds per cycle, all five planning gates, final independent verification and required tests, evidence-backed deterministic repair without a fixed count cap, transient retry limits, permissions, deadlines, user stops and budgets. They do not impose a universal cycle cap or suppress real defects.

## Adjudication and outputs

The coordinator decides using correctness, required behavior, actual verification results, compatibility, and maintainability. Compare performance/cost only when part of the requirements and supported by measurements. Do not vote by agent count or confidence.

Read the delivery skill's [engineering principles](../autonomous-delivery/references/engineering-principles.md). At architecture/design review, challenge dependency direction, feature change impact, and unjustified abstractions. At plan/code review, require bottom-up working slices, known consumers, a necessity pass, and accurate scoped project memory. Name concrete costs or contract violations; do not equate fewer lines or more design patterns with better engineering.

Persist the packet, four reports, findings, and verdict using `templates/review.json` in the autonomous-delivery skill. Record actual agent IDs; the two round-one agents must differ from each other and the coordinator. Bind all reports to the reviewed artifact hash and prerequisite hashes.

Apply [Good-enough acceptance and stop](#good-enough-acceptance-and-stop) for the explicit coordinator verdict and next action. A material revision makes prior acceptance stale and requires a review cycle for the new artifact.

For planning, acceptance advances only to the next planning stage; it does not authorize coding early. For implementation, assign accepted fixes to the existing owner and re-run affected checks. For verification, inspect the independent verifier's actual results; agreement between reviewers never substitutes for execution.

Return the decision, consequential findings/dispositions, and required next action. Keep full transcripts in artifacts, not the main conversation.
