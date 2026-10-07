"""Positive and negative contract tests; all agents/evidence are synthetic fixtures."""

import copy
from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

import validate_checkpoint as gate


SKILL = Path(__file__).resolve().parents[1]
EXCEPTION_RUN_ID = "fixture-exception-run"
EXCEPTION_SESSION_ID = "fixture-exception-session"
EXCEPTION_QUESTION = (
    "The validator hard-codes a maximum of two review cycles, so it rejects the extra cycle you just approved. "
    "May I make a narrowly scoped setup-maintenance change to support an explicit, recorded user-approved extra "
    "cycle for this implementation plan—keeping the default limit, all prior reviews, and every other completion "
    "check unchanged?"
)
EXCEPTION_ANSWER = "Authorize the scoped validator/protocol update and continue (Recommended)"


class GateTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="copilot-gate-test-", dir=Path.cwd())
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.run = self.base / "run"
        self.repo = self.base / "source"
        self.run.mkdir()
        self.repo.mkdir()
        subprocess.run(["git", "init", "--quiet", str(self.repo)], check=True, capture_output=True)
        (self.repo / "app.py").write_text("print('fixture')\n")
        gate.git(self.repo, "add", "app.py")
        self.data = json.loads((SKILL / "templates/checkpoint.json").read_text())
        self.data.update(
            run_id="fixture-run", status="running", phase="verification",
            created_at="2026-10-01T00:00:00Z", updated_at="2026-10-01T01:00:00Z",
            coordinator_session_id="fixture-coordinator",
            coordinator_history=["fixture-coordinator", EXCEPTION_SESSION_ID],
            next_action="Finalize fixture",
        )
        self.data["repository"].update(identity="fixture-repo", worktree_path=str(self.repo))
        self.data["execution"]["host"] = "fixture-host"
        contract = self.data["contract"]
        contract.update(
            objective="Verify a synthetic delivery", change_kind="executable", deliverables=["fixture artifact"],
            permitted_actions=["edit assigned fixture files"],
            features=[{"id": "feature-one", "description": "Fixture behavior", "criterion_ids": ["criterion-one"]}],
            acceptance_criteria=[{"id": "criterion-one", "description": "Fixture produces expected output"}],
        )
        for category in gate.EXCLUSIONS:
            is_test = category in {"behavior", "integration", "end_to_end"}
            contract["verification_matrix"].append({
                "id": category, "category": category, "applicability": "required",
                "criterion_ids": ["criterion-one"], "command": f"fixture-check {category}",
                "cwd": str(self.repo), "expected": "fixture passes", "timeout_seconds": 30,
                "test_kind": "tests" if is_test else "procedure",
                "minimum_tests": 1 if is_test else 0,
                "required_tests": ["regression-one"] if is_test else [],
            })
        self.data["source_snapshot"] = self.reference("source.json", gate.capture_snapshot(self.repo))
        for name in gate.PHASES[:5]:
            content = {"schema_version": 1, "plan_text": "Self-contained fixture plan.", "contract": contract}
            self.accept(name, content if name == "implementation_plan" else f"Fixture {name}")
        milestone = {"id": "milestone-one", "depends_on": ["implementation_plan"],
                     "status": "pending", "artifact": None, "reviews": []}
        self.data["milestones"] = [milestone]
        self.accept("milestone-one", "Fixture implementation milestone")
        self.accept("implementation", {
            "source_snapshot_sha256": self.data["source_snapshot"]["sha256"],
            "milestone_sha256": {"milestone-one": milestone["artifact"]["sha256"]},
            "summary": "Synthetic integrated implementation",
        })
        self.data["workers"].extend([
            {"id": "fixture-writer", "role": "implementation", "status": "completed"},
            {"id": "fixture-verifier", "role": "verification", "status": "completed"},
        ])
        self.data["tasks"] = [{
            "id": "task-one", "status": "done", "depends_on": [], "owner_id": "fixture-writer",
            "milestone_id": "milestone-one", "criterion_ids": ["criterion-one"],
        }]
        self.data["execution"]["verifier"] = {
            "id": "fixture-verifier", "report": self.reference("verifier.json", {
                "runner_id": "fixture-verifier",
                "plan_sha256": self.phase("implementation_plan")["artifact"]["sha256"],
                "before_snapshot_sha256": self.data["source_snapshot"]["sha256"],
                "after_snapshot_sha256": self.data["source_snapshot"]["sha256"],
                "environment": ["Synthetic test fixture; no real agent execution"],
                "summary": "Synthetic verifier report",
            })
        }
        for check in contract["verification_matrix"]:
            self.data["verification_evidence"].append({
                "id": f"evidence-{check['id']}", "check_id": check["id"],
                "snapshot_sha256": self.data["source_snapshot"]["sha256"],
                "plan_sha256": self.phase("implementation_plan")["artifact"]["sha256"],
                "runner_id": "fixture-verifier", "command": check["command"], "cwd": check["cwd"],
                "started_at": "2026-10-01T00:30:00Z", "finished_at": "2026-10-01T00:31:00Z",
                "result": "passed", "exit_code": 0, "tests_executed": check["minimum_tests"],
                "required_tests_executed": check["required_tests"], "skipped_required_tests": [],
                "observed": "Synthetic expected result",
                "log": self.reference(f"logs/{check['id']}.txt", f"Synthetic {check['id']} log"),
            })
        self.data["feature_results"] = [{
            "id": "feature-one", "status": "verified",
            "evidence_ids": [e["id"] for e in self.data["verification_evidence"]],
        }]
        self.refresh_verification_review()

    def reference(self, name, value):
        path = self.run / name
        path.parent.mkdir(parents=True, exist_ok=True)
        data = (json.dumps(value, sort_keys=True, indent=2) if isinstance(value, (dict, list)) else value).encode()
        path.write_bytes(data)
        return {"path": name, "sha256": gate.sha(data)}

    def phase(self, name):
        return next(g for g in self.data["phase_gates"] + self.data["milestones"] if g["id"] == name)

    def accept(self, name, content):
        entry = self.phase(name)
        entry["artifact"] = self.reference(f"artifacts/{name}.json", content)
        review = {
            "schema_version": 1, "stage_id": name, "cycle": 1,
            "subject_sha256": entry["artifact"]["sha256"],
            "prerequisite_sha256": {dep: self.phase(dep)["artifact"]["sha256"] for dep in entry["depends_on"]},
            "findings": [], "decision": {"verdict": "accepted", "coordinator_session_id": "fixture-coordinator",
                                        "reason": "Synthetic evidence supports the fixture"},
        }
        for role in ("proposer", "challenger"):
            actor = f"fixture-{name}-{role}"
            if not any(w["id"] == actor for w in self.data["workers"]):
                self.data["workers"].append({"id": actor, "role": "review", "status": "completed"})
            review[role] = {}
            for round_name in ("initial", "rebuttal"):
                review[role][f"{round_name}_agent_id"] = actor
                review[role][f"{round_name}_report"] = self.reference(
                    f"reviews/{name}-{role}-{round_name}.txt", f"{actor} {round_name} {entry['artifact']['sha256']}")
        entry["reviews"] = [self.reference(f"reviews/{name}.json", review)]
        entry["status"] = "accepted"

    def refresh_verification_review(self):
        self.accept("verification", {
            "plan_sha256": self.phase("implementation_plan")["artifact"]["sha256"],
            "source_snapshot_sha256": self.data["source_snapshot"]["sha256"],
            "evidence_sha256": gate.canonical_sha(self.data["verification_evidence"]),
            "verifier_report_sha256": self.data["execution"]["verifier"]["report"]["sha256"],
            "summary": "Synthetic final verification summary",
        })

    def save(self):
        path = self.run / "checkpoint.json"
        path.write_text(json.dumps(self.data))
        return path

    def validate(self, action="complete"):
        gate.Validator(self.save()).validate(action)

    def blocked(self, message):
        return self.assertRaisesRegex(gate.Invalid, message)

    def test_complete_and_audit_pass(self):
        self.validate()
        self.data["status"] = "completed"
        self.validate("audit")

    def test_planning_worker_is_registered_and_must_finish(self):
        worker = {"id": "fixture-planner", "role": "planning", "status": "completed"}
        self.data["workers"].append(worker)
        self.validate()
        worker["status"] = "running"
        with self.blocked("worker still active"):
            self.validate()

    def test_implementation_gate_passes(self):
        self.data["phase"] = "implementation"
        self.validate("implement")

    def test_blank_template_cannot_run(self):
        self.data = json.loads((SKILL / "templates/checkpoint.json").read_text())
        with self.blocked("run id"):
            self.validate("implement")

    def test_each_unaccepted_planning_gate_blocks_implementation(self):
        baseline = copy.deepcopy(self.data)
        for phase in gate.PHASES[:5]:
            with self.subTest(phase=phase):
                self.data = copy.deepcopy(baseline)
                self.data["phase"] = "implementation"
                self.phase(phase)["status"] = "pending"
                with self.blocked("unaccepted dependency|five accepted"):
                    self.validate("implement")

    def test_paused_and_failed_runs_do_not_complete(self):
        for status in ("paused", "blocked", "failed"):
            with self.subTest(status=status):
                self.data["status"] = status
                with self.blocked("cannot complete"):
                    self.validate()

    def test_deadline_blocks_dispatch(self):
        self.data["phase"] = "implementation"
        self.data["contract"]["deadline_at"] = (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
        self.accept("implementation_plan", {
            "schema_version": 1, "plan_text": "Updated fixture deadline", "contract": self.data["contract"]
        })
        for name in ("implementation", "verification"):
            self.phase(name)["status"] = "pending"
        self.data["milestones"] = []
        with self.blocked("deadline reached"):
            self.validate("implement")

    def test_accepted_without_reviews_fails(self):
        self.phase("brainstorm")["reviews"] = []
        with self.blocked("lacks artifact/reviews"):
            self.validate()

    def test_modified_artifact_fails(self):
        artifact = self.phase("design")["artifact"]
        (self.run / artifact["path"]).write_text("Unreviewed design")
        with self.blocked("hash mismatch"):
            self.validate()

    def mutate_review(self, callback):
        entry = self.phase("verification")
        ref = entry["reviews"][-1]
        review = json.loads((self.run / ref["path"]).read_text())
        callback(review)
        entry["reviews"][-1] = self.reference(ref["path"], review)

    def add_review_cycles(self, gate_id, count):
        entry = self.phase(gate_id)
        original_ref = entry["reviews"][0]
        original = json.loads((self.run / original_ref["path"]).read_text())
        refs = []
        for cycle in range(1, count + 1):
            review = copy.deepcopy(original)
            review["cycle"] = cycle
            for role in ("proposer", "challenger"):
                for round_name in ("initial", "rebuttal"):
                    report_key = f"{round_name}_report"
                    report = review[role][report_key]
                    report_name = f"reviews/{gate_id}-{cycle}-{role}-{round_name}.txt"
                    review[role][report_key] = self.reference(
                        report_name, f"Cycle {cycle} {role} {round_name} {entry['artifact']['sha256']}"
                    )
            refs.append(self.reference(f"reviews/{gate_id}-cycle-{cycle}.json", review))
        entry["reviews"] = refs

    def record_review_cycle_exception(self, *, run_id=EXCEPTION_RUN_ID, gate_id="implementation_plan",
                                      additional_cycles=1, approved=True, question=EXCEPTION_QUESTION,
                                      answer=EXCEPTION_ANSWER, source_session_id=EXCEPTION_SESSION_ID,
                                      recorded_at="2026-01-01T00:00:00+00:00", reason="User-authorized scoped maintenance",
                                      preserved_reviews=None):
        entry = self.phase(gate_id)
        approval = {
            "schema_version": 1,
            "kind": "review-cycle-exception-approval",
            "run_id": run_id,
            "gate_id": gate_id,
            "additional_cycles": additional_cycles,
            "approved": approved,
            "approval_question": question,
            "approval_answer": answer,
            "source_session_id": source_session_id,
            "recorded_at": recorded_at,
            "reason": reason,
            "preserved_reviews": preserved_reviews if preserved_reviews is not None else entry["reviews"][:2],
        }
        entry["review_cycle_exception"] = self.reference(
            f"approvals/{gate_id}-review-cycle-exception.json", approval
        )

    def add_correction_cycles(self, gate_id, count, *, prerequisites_only=False):
        self.add_review_cycles(gate_id, count)
        entry = self.phase(gate_id)
        for cycle, ref in enumerate(entry["reviews"][:-1], 1):
            review = json.loads((self.run / ref["path"]).read_text())
            if prerequisites_only:
                key = entry["depends_on"][0]
                review["prerequisite_sha256"][key] = self.reference(
                    f"artifacts/{gate_id}-prerequisite-v{cycle}.txt",
                    f"Prerequisite evidence version {cycle}",
                )["sha256"]
            else:
                review["subject_sha256"] = self.reference(
                    f"artifacts/{gate_id}-v{cycle}.txt", f"Subject correction version {cycle}",
                )["sha256"]
            review["decision"]["verdict"] = "revise"
            review["findings"] = [{
                "id": "correction-one", "blocking": True, "status": "open",
                "rationale": "Synthetic correction required", "evidence": [],
            }]
            entry["reviews"][cycle - 1] = self.reference(ref["path"], review)
        ref = entry["reviews"][-1]
        review = json.loads((self.run / ref["path"]).read_text())
        review["findings"] = [{
            "id": "correction-one", "blocking": True, "status": "resolved",
            "rationale": "Synthetic correction verified", "evidence": [entry["artifact"]],
        }]
        entry["reviews"][-1] = self.reference(ref["path"], review)

    def test_same_agent_cannot_be_both_reviewers(self):
        self.mutate_review(lambda r: r["challenger"].update(
            initial_agent_id=r["proposer"]["initial_agent_id"]))
        with self.blocked("distinct agent contexts"):
            self.validate()

    def test_unresolved_blocker_prevents_acceptance(self):
        self.mutate_review(lambda r: r["findings"].append({
            "id": "issue-one", "blocking": True, "status": "declined",
            "rationale": "Accepting risk is not a resolution", "evidence": [],
        }))
        with self.blocked("resolved/refuted"):
            self.validate()

    def test_accepted_review_with_three_declined_advisories_passes(self):
        self.mutate_review(lambda r: r["findings"].extend({
            "id": f"optional-{index}", "blocking": False, "status": "declined",
            "rationale": f"{suggestion} is not needed by the approved current scope",
            "evidence": [],
        } for index, suggestion in enumerate(("Rename helper", "Extract wrapper", "Polish prose"), 1)))
        self.validate()

    def test_declined_blocker_with_evidence_still_fails(self):
        self.mutate_review(lambda r: r["findings"].append({
            "id": "required-one", "blocking": True, "status": "declined",
            "rationale": "Required invariant violation cannot be risk accepted",
            "evidence": [self.phase("verification")["artifact"]],
        }))
        with self.blocked("resolved/refuted"):
            self.validate()

    def test_accepted_review_rejects_any_open_finding(self):
        for blocking in (False, True):
            with self.subTest(blocking=blocking):
                self.mutate_review(lambda r: r.update(findings=[{
                    "id": "open-one", "blocking": blocking, "status": "open",
                    "rationale": "Not dispositioned", "evidence": [],
                }]))
                with self.blocked("accepted review has an open finding"):
                    self.validate()

    def test_declined_advisory_requires_rationale(self):
        self.mutate_review(lambda r: r["findings"].append({
            "id": "optional-one", "blocking": False, "status": "declined",
            "rationale": " ", "evidence": [],
        }))
        with self.blocked("finding rationale"):
            self.validate()

    def test_declined_advisory_cannot_hide_failed_required_check(self):
        self.data["verification_evidence"][0].update(result="failed", exit_code=1)
        self.refresh_verification_review()
        self.mutate_review(lambda r: r["findings"].append({
            "id": "optional-one", "blocking": False, "status": "declined",
            "rationale": "Optional naming only; required check still failed", "evidence": [],
        }))
        with self.blocked("latest check did not pass"):
            self.validate()

    def test_repeated_review_reference_does_not_reset_cycles(self):
        entry = self.phase("verification")
        entry["reviews"] *= 3
        with self.blocked("review cycle mismatch"):
            self.validate()

    def test_default_two_review_cycles_remain_allowed(self):
        self.add_review_cycles("implementation_plan", 2)
        self.validate()

    def test_unchanged_third_cycle_is_no_progress(self):
        for count in (3, 4):
            with self.subTest(count=count):
                self.add_review_cycles("implementation_plan", count)
                with self.blocked("review makes no progress"):
                    self.validate()
                failure = subprocess.run(
                    [sys.executable, str(SKILL / "scripts/validate_checkpoint.py"),
                     "complete", str(self.save())], capture_output=True, text=True, timeout=30,
                )
                self.assertEqual(failure.returncode, 1)
                self.assertIn("review makes no progress", failure.stderr)
                self.assertNotIn("VALID", failure.stdout)

    def test_third_and_fourth_subject_correction_reviews_pass(self):
        baseline = copy.deepcopy(self.data)
        for count in (3, 4):
            with self.subTest(count=count):
                self.data = copy.deepcopy(baseline)
                self.add_correction_cycles("verification", count)
                self.validate()
                success = subprocess.run(
                    [sys.executable, str(SKILL / "scripts/validate_checkpoint.py"),
                     "complete", str(self.save())], capture_output=True, text=True, timeout=30,
                )
                self.assertEqual(success.returncode, 0, success.stderr)
                self.assertIn("VALID complete", success.stdout)

    def test_third_and_fourth_prerequisite_correction_reviews_pass(self):
        baseline = copy.deepcopy(self.data)
        for count in (3, 4):
            with self.subTest(count=count):
                self.data = copy.deepcopy(baseline)
                self.add_correction_cycles("verification", count, prerequisites_only=True)
                self.validate()

    def test_changed_subject_path_without_changed_hash_is_no_progress(self):
        self.add_review_cycles("verification", 3)
        entry = self.phase("verification")
        entry["artifact"] = self.reference(
            "artifacts/verification-renamed.json",
            (self.run / entry["artifact"]["path"]).read_text(),
        )
        with self.blocked("review makes no progress"):
            self.validate()

    def test_correction_reviews_preserve_integrity_checks(self):
        baseline = copy.deepcopy(self.data)
        cases = (
            ("missing report", lambda r: r["proposer"].pop("initial_report"), "missing field"),
            ("opposing actor", lambda r: r["challenger"].update(
                rebuttal_agent_id=r["proposer"]["initial_agent_id"]), "distinct agent contexts"),
            ("self review", lambda r: r["proposer"].update(
                initial_agent_id="fixture-coordinator"), "cannot independently review"),
            ("unregistered actor", lambda r: r["proposer"].update(
                initial_agent_id="missing-reviewer"), "review actor missing or not completed"),
            ("duplicate reports", lambda r: r["challenger"].update(
                initial_report=r["proposer"]["initial_report"]), "four distinct"),
            ("cycle gap", lambda r: r.update(cycle=5), "review cycle mismatch"),
            ("wrong stage", lambda r: r.update(stage_id="design"), "another gate"),
        )
        for index in (0, 3):
            for label, mutate, message in cases:
                with self.subTest(cycle=index + 1, case=label):
                    self.data = copy.deepcopy(baseline)
                    self.add_correction_cycles("verification", 4)
                    entry = self.phase("verification")
                    ref = entry["reviews"][index]
                    review = json.loads((self.run / ref["path"]).read_text())
                    mutate(review)
                    entry["reviews"][index] = self.reference(ref["path"], review)
                    with self.blocked(message):
                        self.validate()

    def test_correction_reviews_still_require_current_acceptance(self):
        baseline = copy.deepcopy(self.data)
        cases = (
            (lambda r: r.update(subject_sha256="0" * 64), "reviewed artifact is stale"),
            (lambda r: r.update(prerequisite_sha256={}), "prerequisite hashes are stale"),
            (lambda r: r["decision"].update(verdict="revise"), "needs an accepted review"),
            (lambda r: r["findings"][0].update(status="open"), "open finding"),
            (lambda r: r["findings"][0].update(evidence=[]), "resolved/refuted with evidence"),
        )
        for mutate, message in cases:
            with self.subTest(message=message):
                self.data = copy.deepcopy(baseline)
                self.add_correction_cycles("verification", 4)
                self.mutate_review(mutate)
                with self.blocked(message):
                    self.validate()

    def test_user_approved_third_cycle_is_scoped(self):
        self.data["run_id"] = EXCEPTION_RUN_ID
        self.add_review_cycles("implementation_plan", 3)
        self.record_review_cycle_exception()
        self.validate()

    def creator_approved_third_cycle(self):
        self.data["run_id"] = EXCEPTION_RUN_ID
        self.data["creator_session_id"] = EXCEPTION_SESSION_ID
        self.data["coordinator_history"] = ["previous-fixture-coordinator", "fixture-coordinator"]
        self.add_review_cycles("implementation_plan", 3)
        self.record_review_cycle_exception()

    def test_historical_approval_from_distinct_creator_passes(self):
        self.creator_approved_third_cycle()
        self.assertNotIn(self.data["creator_session_id"], self.data["coordinator_history"])
        self.validate("audit")
        self.validate()

    def test_creator_approval_rejects_unrelated_or_missing_issuer(self):
        self.creator_approved_third_cycle()
        for source in ("another-session", "", " ", None):
            with self.subTest(source=source):
                self.record_review_cycle_exception(source_session_id=source)
                with self.blocked("source session mismatch|nonempty text required"):
                    self.validate()
        self.record_review_cycle_exception()
        entry = self.phase("implementation_plan")
        ref = entry["review_cycle_exception"]
        approval = json.loads((self.run / ref["path"]).read_text())
        approval.pop("source_session_id")
        entry["review_cycle_exception"] = self.reference(ref["path"], approval)
        with self.blocked("malformed fields"):
            self.validate()

    def test_creator_approval_preserves_history_and_hash_checks(self):
        self.creator_approved_third_cycle()
        entry = self.phase("implementation_plan")
        baseline = copy.deepcopy(entry["reviews"])
        entry["reviews"][0] = self.reference(
            "reviews/rewritten-first-review.json",
            (self.run / baseline[0]["path"]).read_text(),
        )
        with self.blocked("does not preserve the original first two reviews"):
            self.validate()
        entry["reviews"] = baseline
        (self.run / baseline[0]["path"]).write_text("{}")
        with self.blocked("hash mismatch"):
            self.validate()
        approval = entry["review_cycle_exception"]
        (self.run / approval["path"]).write_text("{}")
        with self.blocked("hash mismatch"):
            self.validate()

    def test_approval_creator_does_not_become_coordinator(self):
        self.creator_approved_third_cycle()
        self.mutate_review(lambda r: r["decision"].update(coordinator_session_id=EXCEPTION_SESSION_ID))
        with self.blocked("unknown review coordinator"):
            self.validate()

    def test_exception_rejects_invalid_decision_evidence(self):
        self.data["run_id"] = EXCEPTION_RUN_ID
        self.add_review_cycles("implementation_plan", 3)
        cases = (
            ("wrong run", {"run_id": "another-run"}),
            ("wrong gate", {"gate_id": "design"}),
            ("not affirmative", {"approved": False}),
            ("wrong question", {"question": "An unrelated question"}),
            ("wrong answer", {"answer": "No"}),
            ("overbroad cycle grant", {"additional_cycles": 2}),
            ("wrong source session", {"source_session_id": "another-session"}),
            ("missing reason", {"reason": " "}),
            ("missing timezone", {"recorded_at": "2026-01-01T00:00:00"}),
            ("changed history", {"preserved_reviews": []}),
        )
        for label, changes in cases:
            with self.subTest(case=label):
                self.phase("implementation_plan").pop("review_cycle_exception", None)
                self.record_review_cycle_exception(**changes)
                with self.blocked("review-cycle exception"):
                    self.validate()

    def test_exception_artifact_hash_must_match(self):
        self.data["run_id"] = EXCEPTION_RUN_ID
        self.add_review_cycles("implementation_plan", 3)
        self.record_review_cycle_exception()
        ref = self.phase("implementation_plan")["review_cycle_exception"]
        (self.run / ref["path"]).write_text("{}")
        with self.blocked("hash mismatch"):
            self.validate()

    def test_exception_must_be_a_well_formed_hashed_artifact(self):
        self.data["run_id"] = EXCEPTION_RUN_ID
        self.add_review_cycles("implementation_plan", 3)
        self.record_review_cycle_exception()
        entry = self.phase("implementation_plan")
        entry["review_cycle_exception"] = {"path": "missing.json", "sha256": "0" * 64}
        with self.assertRaises((FileNotFoundError, gate.Invalid)):
            self.validate()

    def test_malformed_exception_json_is_rejected(self):
        self.data["run_id"] = EXCEPTION_RUN_ID
        self.add_review_cycles("implementation_plan", 3)
        self.record_review_cycle_exception()
        entry = self.phase("implementation_plan")
        ref = entry["review_cycle_exception"]
        entry["review_cycle_exception"] = self.reference(ref["path"], "{malformed")
        with self.assertRaises((gate.Invalid, json.JSONDecodeError)):
            self.validate()

    def test_exception_artifact_requires_exact_schema_fields(self):
        self.data["run_id"] = EXCEPTION_RUN_ID
        self.add_review_cycles("implementation_plan", 3)
        for label, mutate in (
            ("missing field", lambda document: document.pop("reason")),
            ("extra field", lambda document: document.update(unapproved_override=True)),
        ):
            with self.subTest(case=label):
                self.record_review_cycle_exception()
                entry = self.phase("implementation_plan")
                ref = entry["review_cycle_exception"]
                approval = json.loads((self.run / ref["path"]).read_text())
                mutate(approval)
                entry["review_cycle_exception"] = self.reference(ref["path"], approval)
                with self.blocked("malformed fields"):
                    self.validate()

    def test_historical_exception_does_not_allow_unchanged_fourth_cycle(self):
        self.data["run_id"] = EXCEPTION_RUN_ID
        self.add_review_cycles("implementation_plan", 4)
        self.record_review_cycle_exception()
        with self.blocked("review makes no progress"):
            self.validate()

    def test_historical_exception_allows_corrected_fourth_cycle(self):
        self.data["run_id"] = EXCEPTION_RUN_ID
        self.add_correction_cycles("verification", 4)
        self.record_review_cycle_exception(gate_id="verification")
        self.validate()

    def test_historical_exception_scope_is_record_bound_not_hardcoded(self):
        self.add_review_cycles("verification", 3)
        self.record_review_cycle_exception(run_id=self.data["run_id"], gate_id="verification")
        self.validate()

    def test_historical_exception_rejects_rehashed_history_tampering(self):
        self.data["run_id"] = EXCEPTION_RUN_ID
        self.add_review_cycles("implementation_plan", 3)
        self.record_review_cycle_exception()
        entry = self.phase("implementation_plan")
        ref = entry["reviews"][0]
        review = json.loads((self.run / ref["path"]).read_text())
        review["decision"]["reason"] = "Rewritten historical verdict"
        entry["reviews"][0] = self.reference(ref["path"], review)
        with self.blocked("does not preserve"):
            self.validate()

    def test_exception_is_not_valid_with_two_cycles(self):
        self.data["run_id"] = EXCEPTION_RUN_ID
        self.add_review_cycles("implementation_plan", 2)
        self.record_review_cycle_exception()
        with self.blocked("at least three review cycles"):
            self.validate()

    def test_exception_does_not_allow_noncontiguous_cycles(self):
        self.data["run_id"] = EXCEPTION_RUN_ID
        self.add_review_cycles("implementation_plan", 3)
        entry = self.phase("implementation_plan")
        third_ref = entry["reviews"][2]
        third = json.loads((self.run / third_ref["path"]).read_text())
        third["cycle"] = 4
        entry["reviews"][2] = self.reference(third_ref["path"], third)
        self.record_review_cycle_exception()
        with self.blocked("review cycle mismatch"):
            self.validate()

    def test_exception_cannot_be_reused_for_another_gate(self):
        self.data["run_id"] = EXCEPTION_RUN_ID
        self.add_review_cycles("design", 3)
        self.record_review_cycle_exception(gate_id="implementation_plan")
        self.phase("design")["review_cycle_exception"] = self.phase(
            "implementation_plan").pop("review_cycle_exception")
        with self.blocked("scope mismatch"):
            self.validate()

    def test_plan_cannot_change_contract(self):
        self.data["contract"]["objective"] = "Quietly reduced scope"
        with self.blocked("contract changed"):
            self.validate()

    def test_missing_check_is_not_success(self):
        self.data["verification_evidence"] = [
            e for e in self.data["verification_evidence"] if e["check_id"] != "build"]
        with self.blocked("missing current verification: build"):
            self.validate()

    def test_invalid_verification_cases(self):
        cases = [
            ({"exit_code": 1}, "did not pass"),
            ({"result": "failed"}, "did not pass"),
            ({"tests_executed": 0}, "executed tests"),
            ({"required_tests_executed": []}, "was not executed"),
            ({"skipped_required_tests": ["regression-one"]}, "was skipped"),
            ({"runner_id": "fixture-writer"}, "independent verifier"),
            ({"command": "weaker-check"}, "differs from accepted plan"),
        ]
        baseline = copy.deepcopy(self.data["verification_evidence"][0])
        for mutation, message in cases:
            with self.subTest(mutation=mutation):
                self.data["verification_evidence"][0] = {**baseline, **mutation}
                with self.blocked(message):
                    self.validate()

    def test_newer_failure_cannot_be_hidden_by_older_pass(self):
        newer = copy.deepcopy(self.data["verification_evidence"][0])
        newer.update(id="later-failure", finished_at="2026-10-01T00:32:00Z", result="failed", exit_code=1)
        self.data["verification_evidence"].append(newer)
        with self.blocked("latest check did not pass"):
            self.validate()

    def test_source_mutation_blocks_completion(self):
        (self.repo / "app.py").write_text("print('changed after verification')\n")
        with self.blocked("delivered source differs"):
            self.validate()

    def test_untracked_source_is_not_omitted(self):
        (self.repo / "new.py").write_text("print('not verified')\n")
        with self.blocked("delivered source differs"):
            self.validate()

    def test_verifier_cannot_have_authored_code(self):
        self.data["execution"]["verifier"]["id"] = "fixture-writer"
        with self.blocked("authored/coordinated"):
            self.validate()

    def test_feature_requires_current_evidence(self):
        self.data["feature_results"][0]["evidence_ids"] = []
        with self.blocked("stale/nonpassing"):
            self.validate()

    def test_active_worker_blocks_completion(self):
        self.data["workers"][0]["status"] = "running"
        with self.blocked("worker still active"):
            self.validate()

    def test_running_helper_and_schedule_block_completion(self):
        self.data["execution"]["helpers"] = [{"id": "fixture-helper"}]
        with self.blocked("helpers must be stopped"):
            self.validate()
        self.data["execution"]["helpers"] = []
        self.data["execution"]["automation_enabled"] = True
        with self.blocked("disable this run"):
            self.validate()

    def test_stale_final_review_blocks(self):
        self.data["verification_evidence"][0]["observed"] = "Unreviewed new assertion"
        with self.blocked("review evidence is stale"):
            self.validate()

    def test_completed_label_does_not_bypass_audit(self):
        self.data["status"] = "completed"
        self.data["feature_results"][0]["status"] = "unverified"
        with self.blocked("unverified feature"):
            self.validate("audit")

    def test_artifact_path_escape_blocks(self):
        self.phase("brainstorm")["artifact"]["path"] = "../outside.txt"
        with self.blocked("run-relative"):
            self.validate()

    def test_artifact_symlink_escape_blocks(self):
        outside = self.base / "outside.txt"
        outside.write_text("outside")
        (self.run / "outside-link").symlink_to(outside)
        self.phase("brainstorm")["artifact"] = {"path": "outside-link", "sha256": gate.sha(b"outside")}
        with self.blocked("escapes run directory"):
            self.validate()

    def test_source_symlink_escape_blocks(self):
        (self.repo / "outside-link").symlink_to(self.run)
        with self.blocked("source symlink escapes"):
            gate.capture_snapshot(self.repo)

    def test_duplicate_json_and_nonfinite_values_fail(self):
        for document in ('{"run_id": "one", "run_id": "two"}', '{"value": NaN}'):
            with self.subTest(document=document), self.assertRaises(gate.Invalid):
                gate.decode(document)

    def test_unknown_schema_blocks(self):
        self.data["schema_version"] = 99
        with self.blocked("schema 3 required"):
            self.validate()

    def test_required_source_identity_before_and_after(self):
        verifier = self.data["execution"]["verifier"]
        report = json.loads((self.run / verifier["report"]["path"]).read_text())
        report["after_snapshot_sha256"] = "0" * 64
        verifier["report"] = self.reference("verifier.json", report)
        with self.blocked("source changed during verification"):
            self.validate()

    def test_retry_limit_and_preserved_attempts(self):
        log = self.reference("retry.txt", "Synthetic failure")
        self.data["failure_attempts"] = [{
            "operation_id": "op-one", "kind": "transient", "attempt": n,
            "result": "failed", "hypothesis": "Transient fixture failure", "log": log,
        } for n in range(1, 5)]
        with self.blocked("retry/repair limit exceeded"):
            self.validate()
        self.data["failure_attempts"] = [self.data["failure_attempts"][1]]
        with self.blocked("contiguous and preserved"):
            self.validate()

    def repair_attempts(self, count):
        hypotheses = (
            "Observed stale output: invalidate the build cache",
            "Observed wrong entry point: repair the package export",
            "Observed missing asset: include it in the package",
            "Observed incorrect asset URL: resolve it relative to the installed package",
        )
        return [{
            "operation_id": "op-one", "kind": "repair", "attempt": n,
            "result": "failed" if n < count else "succeeded",
            "hypothesis": hypotheses[n - 1],
            "log": self.reference(f"repairs/{n}.txt", f"Synthetic observation and check result for repair {n}"),
        } for n in range(1, count + 1)]

    def test_third_evidence_backed_repair_passes(self):
        self.data["failure_attempts"] = self.repair_attempts(3)
        self.validate()
        self.assertEqual([a["result"] for a in self.data["failure_attempts"]], ["failed", "failed", "succeeded"])
        self.data["failure_attempts"][2]["result"] = "failed"
        self.validate("audit")

    def test_fourth_evidence_backed_repair_passes(self):
        self.data["failure_attempts"] = self.repair_attempts(4)
        self.validate()

    def test_duplicate_repair_hypothesis_fails(self):
        for duplicate in (
            "Observed stale output: invalidate the build cache",
            "  OBSERVED  stale output:\n invalidate the build CACHE  ",
        ):
            for count in (2, 3):
                with self.subTest(hypothesis=duplicate, count=count):
                    self.data["failure_attempts"] = self.repair_attempts(count)
                    self.data["failure_attempts"][-1]["hypothesis"] = duplicate
                    with self.blocked("distinct repair hypothesis"):
                        self.validate()

    def test_repair_requires_log_and_hypothesis(self):
        for field_name in ("log", "hypothesis"):
            with self.subTest(field=field_name):
                self.data["failure_attempts"] = self.repair_attempts(1)
                del self.data["failure_attempts"][0][field_name]
                with self.blocked(f"missing field: {field_name}"):
                    self.validate()
        self.data["failure_attempts"] = self.repair_attempts(1)
        self.data["failure_attempts"][0]["hypothesis"] = " \n "
        with self.blocked("attempt hypothesis"):
            self.validate()

    def test_repair_log_must_exist_be_nonempty_and_match_hash(self):
        for content, message in (("", "empty artifact"), ("Changed result", "hash mismatch")):
            with self.subTest(content=content):
                self.data["failure_attempts"] = self.repair_attempts(1)
                ref = self.data["failure_attempts"][0]["log"]
                (self.run / ref["path"]).write_text(content)
                with self.blocked(message):
                    self.validate()
        self.data["failure_attempts"] = self.repair_attempts(1)
        (self.run / self.data["failure_attempts"][0]["log"]["path"]).unlink()
        with self.assertRaises(FileNotFoundError):
            self.validate()

    def test_repair_counts_cannot_gap_or_restart(self):
        for numbers in ((1, 3), (1, 1), (2,)):
            with self.subTest(numbers=numbers):
                repairs = self.repair_attempts(3)
                self.data["failure_attempts"] = [copy.deepcopy(repairs[n - 1]) for n in numbers]
                with self.blocked("contiguous and preserved"):
                    self.validate()

    def test_repair_accounting_is_per_operation_and_kind(self):
        repairs = self.repair_attempts(4)
        transient = {
            "operation_id": "op-one", "kind": "transient", "attempt": 1, "result": "failed",
            "hypothesis": repairs[0]["hypothesis"], "log": repairs[0]["log"],
        }
        other = {**repairs[0], "operation_id": "op-two"}
        self.data["failure_attempts"] = [repairs[0], transient, other, *repairs[1:]]
        self.validate()

    def test_repairs_do_not_extend_transient_limit(self):
        repairs = self.repair_attempts(4)
        transients = [{
            "operation_id": "op-one", "kind": "transient", "attempt": n,
            "result": "failed", "hypothesis": "Observed transient connection failure", "log": repairs[0]["log"],
        } for n in range(1, 5)]
        self.data["failure_attempts"] = repairs + transients[:3]
        self.validate()
        self.data["failure_attempts"].append(transients[3])
        with self.blocked("retry/repair limit exceeded"):
            self.validate()

    def test_repair_result_must_be_honestly_classified(self):
        self.data["failure_attempts"] = self.repair_attempts(1)
        self.data["failure_attempts"][0]["result"] = "passed"
        with self.blocked("attempt result"):
            self.validate()

    def test_cli_accepts_distinct_repairs_and_blocks_duplicates(self):
        script = SKILL / "scripts/validate_checkpoint.py"
        self.data["failure_attempts"] = self.repair_attempts(4)
        success = subprocess.run([sys.executable, str(script), "complete", str(self.save())],
                                 capture_output=True, text=True)
        self.assertEqual(success.returncode, 0, success.stderr)
        self.assertIn("VALID complete", success.stdout)
        self.data["failure_attempts"][3]["hypothesis"] = self.data["failure_attempts"][0]["hypothesis"]
        failure = subprocess.run([sys.executable, str(script), "complete", str(self.save())],
                                 capture_output=True, text=True)
        self.assertEqual(failure.returncode, 1)
        self.assertIn("distinct repair hypothesis", failure.stderr)
        self.assertNotIn("VALID", failure.stdout)

    def test_malformed_states_fail_cleanly(self):
        for value in (None, [], {}, True, 42):
            with self.subTest(value=value):
                self.data["status"] = value
                with self.blocked("run state"):
                    self.validate()

    def test_timezone_is_required(self):
        self.data["updated_at"] = "2026-10-01T01:00:00"
        with self.blocked("timezone required"):
            self.validate()

    def test_task_dependencies_cannot_cycle(self):
        self.data["tasks"].append({
            "id": "task-two", "status": "done", "depends_on": ["task-one"],
            "owner_id": "fixture-writer", "milestone_id": "milestone-one",
            "criterion_ids": ["criterion-one"],
        })
        self.data["tasks"][0]["depends_on"] = ["task-two"]
        with self.blocked("cyclic task"):
            self.validate()

    def test_missing_matrix_categories_fail(self):
        self.data["contract"]["verification_matrix"].pop()
        self.accept("implementation_plan", {
            "schema_version": 1, "plan_text": "Incomplete fixture matrix", "contract": self.data["contract"]
        })
        self.phase("implementation")["status"] = "pending"
        self.phase("verification")["status"] = "pending"
        self.data["milestones"] = []
        with self.blocked("all seven check categories"):
            self.validate("audit")

    def test_unsupported_exclusion_and_outside_cwd_fail(self):
        baseline = copy.deepcopy(self.data["contract"])
        for mutation, message in (("excluded", "executable changes require"), ("cwd", "outside the authorized")):
            with self.subTest(mutation=mutation):
                self.data["contract"] = copy.deepcopy(baseline)
                check = self.data["contract"]["verification_matrix"][0]
                if mutation == "excluded":
                    check.update(applicability="excluded", criterion_ids=[], exclusion_reason="documentation_only",
                                 exclusion_evidence=[self.reference("exclude.txt", "Cannot exclude changed behavior")])
                else:
                    check["cwd"] = str(self.base)
                self.accept("implementation_plan", {
                    "schema_version": 1, "plan_text": "Invalid fixture matrix", "contract": self.data["contract"]
                })
                self.phase("implementation")["status"] = "pending"
                self.phase("verification")["status"] = "pending"
                self.data["milestones"] = []
                with self.blocked(message):
                    self.validate("audit")

    def test_deleted_tracked_file_is_part_of_snapshot(self):
        (self.repo / "app.py").unlink()
        snapshot = gate.capture_snapshot(self.repo)
        self.assertIn({"path": "app.py", "kind": "deleted"}, snapshot["files"])
        with self.blocked("delivered source differs"):
            self.validate()

    def test_executable_bit_changes_snapshot(self):
        before = gate.capture_snapshot(self.repo)
        (self.repo / "app.py").chmod(0o755)
        self.assertNotEqual(before, gate.capture_snapshot(self.repo))

    def test_review_context_cannot_be_reused_across_stages(self):
        self.mutate_review(lambda r: r["challenger"].update(initial_agent_id="fixture-brainstorm-challenger"))
        with self.blocked("reused across stages"):
            self.validate()

    def test_review_and_verifier_must_be_in_registry(self):
        original = copy.deepcopy(self.data["workers"])
        for actor in ("fixture-verifier", "fixture-verification-challenger"):
            with self.subTest(actor=actor):
                self.data["workers"] = [w for w in original if w["id"] != actor]
                with self.blocked("worker registry"):
                    self.validate()

    def test_resume_preserves_historical_review_coordinators(self):
        self.data["coordinator_session_id"] = "fixture-new-coordinator"
        self.data["coordinator_history"].append("fixture-new-coordinator")
        self.validate()

    def test_unknown_programmatic_action_cannot_bypass_gate(self):
        with self.blocked("validation action"):
            gate.Validator(self.save()).validate("skip")

    def test_boolean_review_schema_is_not_integer(self):
        self.mutate_review(lambda r: r.update(schema_version=True))
        with self.blocked("unsupported review schema"):
            self.validate()

    def test_cli_exit_codes(self):
        script = SKILL / "scripts/validate_checkpoint.py"
        success = subprocess.run([sys.executable, str(script), "complete", str(self.save())],
                                 capture_output=True, text=True)
        self.assertEqual(success.returncode, 0, success.stderr)
        self.assertIn("VALID complete", success.stdout)
        self.data["workers"][0]["status"] = "running"
        failure = subprocess.run([sys.executable, str(script), "complete", str(self.save())],
                                 capture_output=True, text=True)
        self.assertEqual(failure.returncode, 1)
        self.assertIn("BLOCKED", failure.stderr)
        self.assertNotIn("VALID", failure.stdout)


if __name__ == "__main__":
    unittest.main()
