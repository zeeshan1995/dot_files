"""Static guidance contracts, not evidence of model behavior or throughput."""

import json
from pathlib import Path
import re
import unittest


HOME = Path(__file__).resolve().parents[3]
PROTOCOL = "skills/autonomous-delivery/references/protocol.md"
CONTEXT = "skills/autonomous-delivery/references/context-management.md"
REVIEW = "skills/adversarial-review/SKILL.md"
PROFILES = tuple(f"agents/autonomy-{role}.agent.md" for role in
                 ("guardian", "planner", "proposer", "challenger"))


def read(path):
    return (HOME / path).read_text(encoding="utf-8")


def section(text, heading):
    match = re.search(rf"^(#+) {re.escape(heading)}\n", text, re.M)
    if not match:
        raise AssertionError(f"Missing contract section: {heading}")
    end = re.search(rf"^#{{1,{len(match[1])}}} ", text[match.end():], re.M)
    return text[match.end():match.end() + end.start()] if end else text[match.end():]


def table(text, first_column):
    rows = [tuple(cell.strip() for cell in line.strip("|").split("|"))
            for line in text.splitlines() if line.startswith("|")]
    headers = [row for row in rows if row[0] == first_column]
    if len(headers) != 1:
        raise AssertionError(f"Expected one {first_column} table")
    start = rows.index(headers[0]) + 2
    result = {}
    for row in rows[start:]:
        if len(row) != len(headers[0]) or row[0] in result:
            raise AssertionError(f"Invalid or duplicate table row: {row}")
        result[row[0]] = row[1:]
    return result


def frontmatter(text):
    if not text.startswith("---\n") or "\n---\n" not in text[4:]:
        raise AssertionError("Missing delimited frontmatter")
    header, body = text[4:].split("\n---\n", 1)
    values = {}
    for line in header.splitlines():
        key, raw = line.split(":", 1)
        if key in values:
            raise AssertionError(f"Duplicate frontmatter key: {key}")
        raw = raw.strip()
        values[key] = json.loads(raw) if raw.startswith(('"', "[")) or raw in ("true", "false") else raw
    if not body.strip():
        raise AssertionError("Empty instruction body")
    return values


class OrchestrationGuidanceTests(unittest.TestCase):
    def assertTerms(self, text, *terms):
        for term in terms:
            with self.subTest(term=term):
                self.assertIn(term, text)

    def test_kickoff_outcome_consumer_and_prerequisite_evidence(self):
        text = section(read(CONTEXT), "Kickoff packet")
        self.assertTerms(text, "observable user outcome", "necessary enabling contract",
                         "exact consumer", "prerequisite evidence", "ownership conflicts",
                         "evidence-to-return", "existing task reports")

    def test_dispatch_uses_true_dependencies_not_feature_labels(self):
        text = section(read(CONTEXT), "Kickoff packet")
        self.assertTerms(text, "all eligible independent tasks", "capacity",
                         "whole feature/stage labels", "required stage-gate dependencies")

    def test_failure_route_contract(self):
        routes = table(section(read(PROTOCOL), "Failure routing"), "Failure")
        required = {
            "Compile/type or product logic": "implementation owner",
            "Test harness": "test owner",
            "Dependency/tool/environment": "existing owner",
            "Approved-contract contradiction": "coordinator",
            "Permission/policy": "block",
            "Empirical verification": "fresh independent verification",
            "No semantic progress": "bounded",
        }
        self.assertEqual(set(routes), set(required))
        for failure, obligation in required.items():
            self.assertIn(obligation, " ".join(routes[failure]), failure)
        self.assertTerms(" ".join(" ".join(row) for row in routes.values()),
                         "production defects", "planner", "authorized decision")

    def test_control_table_separates_evidence_from_authority(self):
        controls = table(section(read(PROTOCOL), "Control boundaries"), "Control")
        self.assertEqual(set(controls), {"Transition-record validator", "Executed checks",
                                        "Platform permissions", "Guardian reasoning",
                                        "Coordinator acceptance"})
        for control, limit in {
            "Transition-record validator": "not authentic execution",
            "Executed checks": "not untested behavior",
            "Platform permissions": "not instruction text",
            "Guardian reasoning": "not acceptance",
            "Coordinator acceptance": "not a permission grant",
        }.items():
            self.assertIn(limit, " ".join(controls[control]))

    def test_findings_anchor_to_approved_scope(self):
        text = section(read(REVIEW), "Required reports")
        self.assertTerms(text, "approved criterion", "invariant", "permission",
                         "concrete counterexample", "invented ideal",
                         "required verification")

    def test_good_enough_stage_evidence_not_hypothetical_ideal(self):
        text = section(read(REVIEW), "Good-enough acceptance and stop")
        self.assertTerms(text, "current stage", "approved criterion", "source anchor",
                         "supported failing scenario or contradiction",
                         "stage-appropriate missing evidence", "consequence",
                         "falsifying or resolution check", "reasoned counterexample",
                         "do not require code/runtime proof before implementation is allowed")

    def test_good_enough_material_violations_not_labels(self):
        text = section(read(REVIEW), "Good-enough acceptance and stop")
        self.assertTerms(text, "Confidence, labels, or severity alone", "Need more confidence",
                         "future feature", "naming, refactor, or style",
                         "Accessibility, security, performance, and architecture",
                         "even when labeled minor", "contradictions that affect consumers",
                         "refute unsupported blocking claims with evidence")

    def test_good_enough_accepts_dispositioned_advisories_after_four_reports(self):
        text = section(read(REVIEW), "Good-enough acceptance and stop")
        self.assertTerms(text, "both rounds completed (four reports)",
                         "required stage criteria and evidence current and satisfied",
                         "real blockers resolved/refuted", "explicitly resolved or declined",
                         "coordinator ACCEPTS and advances", "Open findings still prevent acceptance")

    def test_good_enough_optional_suggestions_do_not_create_work(self):
        text = section(read(REVIEW), "Good-enough acceptance and stop")
        self.assertTerms(text, "Default to declining nonessential suggestions",
                         "existing review record", "no new mandatory backlog or task",
                         "Do not silently fix nits", "no new cycle or polish task",
                         "not a 100-percent score or zero imaginable issues")

    def test_good_enough_round_two_and_changed_evidence_boundaries(self):
        text = section(read(REVIEW), "Good-enough acceptance and stop")
        self.assertTerms(text, "strongest findings", "not a mandatory new-defect hunt",
                         "may agree", "including round two", "not all defects must be found in round one",
                         "Accepted unchanged subjects", "genuinely changed evidence, source, or requirements",
                         "stale-acceptance rules", "user stops and budgets")

    def test_same_cause_fix_traces_consumers_before_new_review(self):
        text = section(read(REVIEW), "Semantic correction packet")
        self.assertTerms(text, "complete affected consumer trace", "one coherent patch",
                         "one canonical contract definition plus references",
                         "semantic preflight", "requirements and design",
                         "Distinct new errors still need current checks")

    def test_consumers_link_canonical_good_enough_contract(self):
        anchor = "adversarial-review/SKILL.md#good-enough-acceptance-and-stop"
        for path in (PROTOCOL, *PROFILES):
            with self.subTest(path=path):
                self.assertIn(anchor, read(path))
                self.assertNotIn("## Good-enough acceptance and stop", read(path))
        self.assertEqual(read(REVIEW).count("## Good-enough acceptance and stop"), 1)

    def test_planning_without_verified_slices_is_not_failure(self):
        text = section(read(CONTEXT), "Progress observations")
        self.assertTerms(text, "Planning with no implementation yet is not failure",
                         "optional progress fields", "current-stage evidence",
                         "good-enough-acceptance-and-stop")

    def test_semantic_correction_packet_preserves_full_review(self):
        text = section(read(REVIEW), "Semantic correction packet")
        self.assertTerms(text, "finding IDs", "root cause", "changed contract/paths",
                         "downstream impact", "accepted unaffected material",
                         "full current subject", "New genuine findings remain admissible",
                         "not forced acceptance", "existing versioned task/review artifacts")
        for role in ("planner", "proposer", "challenger"):
            self.assertIn("semantic-correction-packet", read(f"agents/autonomy-{role}.agent.md"))

    def test_progress_observation_is_optional_and_unknown_by_default(self):
        text = section(read(CONTEXT), "Progress observations")
        samples = re.findall(r"```json\n(.*?)\n```", text, re.S)
        self.assertEqual(len(samples), 1)
        observation = json.loads(samples[0])["progress_observation"]
        self.assertEqual(set(observation), {
            "previous_ref", "current_ref", "verified_slices", "planning_evidence",
            "work", "unresolved_finding_ids", "correction_effects",
            "last_substantive_evidence_at", "elapsed_since_evidence_seconds",
            "active_work_seconds", "usage", "cost"})
        self.assertEqual(set(observation["work"]), {"active", "ready", "blocked"})
        for key in ("last_substantive_evidence_at", "elapsed_since_evidence_seconds",
                    "active_work_seconds", "usage", "cost"):
            self.assertIsNone(observation[key], key)
        self.assertTerms(text, "optional", "existing guardian sidecar", "unknown",
                         "not a new registry", "not actual runtime receipts")

    def test_progress_meaning_not_metadata_or_elapsed_productivity(self):
        text = section(read(CONTEXT), "Progress observations")
        self.assertTerms(text, "meaningful planning progress", "user-visible verified slice",
                         "Acknowledgement", "timestamp-only", "not confirmed effects",
                         "unblocked task", "not delivered functionality",
                         "Elapsed time is not active work", "throughput",
                         "legitimate wait", "available capacity")

    def test_guardian_consumes_canonical_progress_and_routes(self):
        text = read(PROFILES[0])
        self.assertTerms(text, "context-management.md#progress-observations",
                         "protocol.md#failure-routing", "progress_observation",
                         "correction effect", "delivery")
        self.assertIn("progress observations", section(read(CONTEXT),
                                                     "Guardian registration, dispatch, and corrections"))

    def test_challenger_round_boundary_not_cycle_cap(self):
        text = read(PROFILES[-1])
        self.assertNotIn("enforces the cycle limit", text)
        self.assertTerms(text, "Stop after the assigned round", "evidence-backed continuation")

    def test_review_independence_two_rounds_and_history_preserved(self):
        self.assertTerms(read(REVIEW), "exactly two rounds", "distinct real agent contexts",
                         "both rounds completed", "full current subject")
        self.assertTerms(read(PROTOCOL), "all four content-hashed reports", "current prerequisite hashes",
                         "no fixed cycle-count cap", "historically approved third cycle",
                         "fourth and later cycles require progress")

    def test_gates_and_independent_frozen_verification_preserved(self):
        text = read(PROTOCOL)
        self.assertTerms(text, "`brainstorm`, `requirements`, `architecture`, `design`, `implementation_plan`",
                         "five accepted planning gates", "independent final verifier",
                         "Final source verification has exclusive access against edits",
                         "No gate may be accepted without its required evidence")

    def test_repair_limits_permissions_and_existing_state_preserved(self):
        text = read(PROTOCOL)
        self.assertTerms(text, "There is no fixed repair-count cap", "at most two retries",
                         "genuinely distinct, falsifiable repair hypothesis",
                         "Do not bypass denials", "contiguous", "budget", "user stop",
                         "Checkpoint schema version is 3", "existing task reports")

    def test_guardian_is_not_new_gate_scheduler_or_capacity(self):
        self.assertTerms(read(CONTEXT), "Never launch a second guardian",
                         "If four owners are executing, enqueue", "Acknowledgement alone is not resolution",
                         "two consecutive scheduled checks without substantive progress",
                         "not proof of worker failure", "not proposer/challenger rounds",
                         "do not start a ceremonial guardian final-review cycle")
        self.assertTerms(read(PROFILES[0]), "Do not spawn agents, schedule work, poll",
                         "edit any files (including reports)", "only the existing coordinator dispatches")

    def test_frontmatter_and_read_only_roles(self):
        for path in (REVIEW, *PROFILES):
            with self.subTest(path=path):
                data = frontmatter(read(path))
                self.assertTrue(data["description"])
                self.assertNotIn("model", data)
                if path in PROFILES:
                    self.assertIs(data["include-custom-instructions"], True)
                    expected = (["read", "search", "execute"] if "guardian" in path else
                                ["read", "search", "edit", "web"] if "planner" in path else
                                ["read", "search"])
                    self.assertEqual(data["tools"], expected)
        with self.assertRaisesRegex(AssertionError, "Duplicate"):
            frontmatter("---\nname: a\nname: b\n---\nbody")

    def test_local_references_and_heading_targets(self):
        for path in (PROTOCOL, CONTEXT, REVIEW, *PROFILES):
            for target in re.findall(r"\[[^\]]+\]\(([^)]+)\)", read(path)):
                if "://" in target:
                    continue
                with self.subTest(path=path, target=target):
                    file_part, _, anchor = target.partition("#")
                    dest = (HOME / path).parent / file_part if file_part else HOME / path
                    self.assertTrue(dest.is_file())
                    if anchor:
                        slugs = [re.sub(r"[^\w -]", "", h.lower()).replace(" ", "-")
                                 for h in re.findall(r"^#+ (.+)$", dest.read_text(), re.M)]
                        self.assertIn(anchor, slugs)


if __name__ == "__main__":
    unittest.main(verbosity=2)
