#!/usr/bin/env python3
"""Read-only consistency checks for autonomous delivery checkpoints."""

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import subprocess
import sys


PHASES = (
    "brainstorm", "requirements", "architecture", "design",
    "implementation_plan", "implementation", "verification",
)
EXCLUSIONS = {
    "behavior": "documentation_only",
    "integration": "no_changed_boundary",
    "end_to_end": "no_user_flow",
    "lint": "not_configured",
    "typecheck": "not_configured",
    "build": "no_build_step",
    "runtime": "documentation_only",
}
RUN_STATES = {"ready", "running", "blocked", "paused", "completed", "failed"}
GATE_STATES = {"pending", "running", "review_required", "accepted", "blocked", "stale"}
REVIEW_CYCLE_EXCEPTION_QUESTION = (
    "The validator hard-codes a maximum of two review cycles, so it rejects the extra cycle you just approved. "
    "May I make a narrowly scoped setup-maintenance change to support an explicit, recorded user-approved extra "
    "cycle for this implementation plan—keeping the default limit, all prior reviews, and every other completion "
    "check unchanged?"
)
REVIEW_CYCLE_EXCEPTION_ANSWER = "Authorize the scoped validator/protocol update and continue (Recommended)"


class Invalid(ValueError):
    pass


def need(condition, message):
    if not condition:
        raise Invalid(message)


def text(value, label):
    need(isinstance(value, str) and bool(value.strip()), f"{label}: nonempty text required")
    return value


def choice(value, allowed, label):
    text(value, label)
    need(value in allowed, f"{label}: unsupported value {value}")
    return value


def items(value, label):
    need(isinstance(value, list), f"{label}: array required")
    return value


def obj(value, label):
    need(isinstance(value, dict), f"{label}: object required")
    return value


def field(value, key):
    obj(value, key)
    need(key in value, f"missing field: {key}")
    return value[key]


def strings(value, label):
    result = items(value, label)
    for entry in result:
        text(entry, label)
    need(len(result) == len(set(result)), f"{label}: duplicate values")
    return result


def indexed(value, label):
    result = {}
    for entry in items(value, label):
        key = text(field(entry, "id"), f"{label}.id")
        need(key not in result, f"{label}: duplicate id {key}")
        result[key] = entry
    return result


def integer(value, minimum, label):
    need(type(value) is int and value >= minimum, f"{label}: integer >= {minimum} required")
    return value


def timestamp(value, label):
    parsed = datetime.fromisoformat(text(value, label).replace("Z", "+00:00"))
    need(parsed.tzinfo is not None, f"{label}: timezone required")
    return parsed


def digest(value, label):
    need(isinstance(value, str) and re.fullmatch(r"[0-9a-f]{64}", value) is not None,
         f"{label}: lowercase SHA-256 required")
    return value


def sha(data):
    return hashlib.sha256(data).hexdigest()


def canonical_sha(value):
    return sha(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode())


def unique_pairs(pairs):
    result = {}
    for key, value in pairs:
        need(key not in result, f"duplicate JSON key: {key}")
        result[key] = value
    return result


def invalid_constant(value):
    raise Invalid(f"invalid JSON constant: {value}")


def decode(data):
    return json.loads(data, object_pairs_hook=unique_pairs, parse_constant=invalid_constant)


def git(root, *arguments):
    return subprocess.run(
        ["git", "-c", "core.fsmonitor=false", "--no-pager", "-C", str(root), *arguments],
        check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=30,
    ).stdout


def capture_snapshot(worktree):
    root = Path(worktree).resolve(strict=True)
    top = Path(os.fsdecode(git(root, "rev-parse", "--show-toplevel")).strip()).resolve()
    need(top == root, "snapshot path must be the Git worktree root")
    heads = git(root, "rev-parse", "--revs-only", "HEAD").decode().splitlines()
    need(len(heads) <= 1, "ambiguous Git HEAD")
    paths = sorted(set(os.fsdecode(p) for p in
                       git(root, "ls-files", "--cached", "--others", "--exclude-standard", "-z").split(b"\0") if p))
    files = []
    for name in paths:
        relative = Path(name)
        need(not relative.is_absolute() and ".." not in relative.parts, "invalid source path")
        path = root / relative
        need(path.resolve().is_relative_to(root), f"source symlink escapes worktree: {name}")
        try:
            mode = path.lstat().st_mode
        except FileNotFoundError:
            files.append({"path": name, "kind": "deleted"})
            continue
        if stat.S_ISLNK(mode):
            files.append({"path": name, "kind": "symlink", "target": os.readlink(path)})
        else:
            need(stat.S_ISREG(mode), f"unsupported source directory/submodule/device: {name}")
            files.append({"path": name, "kind": "file", "mode": stat.S_IMODE(mode),
                          "sha256": sha(path.read_bytes())})
    return {"schema_version": 1, "root": str(root), "head": heads[0] if heads else None, "files": files}


class Validator:
    def __init__(self, checkpoint):
        self.path = Path(checkpoint).resolve(strict=True)
        self.root = self.path.parent
        self.data = obj(decode(self.path.read_bytes()), "checkpoint")
        self.review_owners = {}

    def artifact(self, reference):
        obj(reference, "artifact")
        need(set(reference) == {"path", "sha256"}, "artifact requires exactly path and sha256")
        relative = Path(text(reference["path"], "artifact.path"))
        need(not relative.is_absolute() and ".." not in relative.parts, "artifact path must be run-relative")
        path = (self.root / relative).resolve(strict=True)
        need(path.is_relative_to(self.root), "artifact escapes run directory")
        data = path.read_bytes()
        need(bool(data.strip()), f"empty artifact: {relative}")
        need(sha(data) == digest(reference["sha256"], "artifact.sha256"),
             f"artifact hash mismatch: {relative}")
        return data

    def artifact_json(self, reference):
        return obj(decode(self.artifact(reference)), "artifact JSON")

    def review(self, gate, reference, cycle, current):
        review = self.artifact_json(reference)
        need(type(field(review, "schema_version")) is int and review["schema_version"] == 1,
             "unsupported review schema")
        need(field(review, "stage_id") == gate["id"], "review belongs to another gate")
        need(type(field(review, "cycle")) is int and review["cycle"] == cycle, "review cycle mismatch")
        digest(field(review, "subject_sha256"), "review subject")
        ids = {}
        report_hashes = []
        for role in ("proposer", "challenger"):
            actor = obj(field(review, role), role)
            ids[role] = set()
            for round_name in ("initial", "rebuttal"):
                actor_id = text(field(actor, f"{round_name}_agent_id"), "review actor id")
                need(actor_id not in self.coordinators, "coordinator cannot independently review itself")
                previous_gate = self.review_owners.setdefault(actor_id, gate["id"])
                need(previous_gate == gate["id"], "review context reused across stages")
                ids[role].add(actor_id)
                report = field(actor, f"{round_name}_report")
                self.artifact(report)
                report_hashes.append(report["sha256"])
        need(not ids["proposer"] & ids["challenger"], "review roles must have distinct agent contexts")
        need(len(set(report_hashes)) == 4, "four distinct role/round reports required")
        decision = obj(field(review, "decision"), "review decision")
        verdict = choice(field(decision, "verdict"), {"accepted", "revise", "blocked"}, "review verdict")
        need(field(decision, "coordinator_session_id") in self.coordinators, "unknown review coordinator")
        text(field(decision, "reason"), "review decision reason")
        for finding in indexed(field(review, "findings"), "findings").values():
            blocking = field(finding, "blocking")
            need(type(blocking) is bool, "finding.blocking must be boolean")
            status = choice(field(finding, "status"), {"open", "resolved", "refuted", "declined"}, "finding disposition")
            text(field(finding, "rationale"), "finding rationale")
            evidence = items(field(finding, "evidence"), "finding evidence")
            for item in evidence:
                self.artifact(item)
            if verdict == "accepted":
                need(status != "open", "accepted review has an open finding")
                if blocking:
                    need(status in {"resolved", "refuted"} and bool(evidence),
                         "blocking finding must be resolved/refuted with evidence")
        if current:
            need(verdict == "accepted", "accepted gate needs an accepted review")
            need(review["subject_sha256"] == gate["artifact"]["sha256"], "reviewed artifact is stale")
            expected = {key: self.gates[key]["artifact"]["sha256"] for key in gate["depends_on"]}
            need(field(review, "prerequisite_sha256") == expected, "review prerequisite hashes are stale")
        else:
            obj(field(review, "prerequisite_sha256"), "review prerequisite hashes")
        return review

    def review_cycle_exception(self, gate, reviews, reference):
        need(len(reviews) >= 3, "review-cycle exception requires at least three review cycles")
        approval = self.artifact_json(reference)
        required = {
            "schema_version", "kind", "run_id", "gate_id", "additional_cycles", "approved",
            "approval_question", "approval_answer", "source_session_id", "recorded_at", "reason",
            "preserved_reviews",
        }
        need(set(approval) == required, "review-cycle exception has malformed fields")
        need(type(approval["schema_version"]) is int and approval["schema_version"] == 1,
             "review-cycle exception schema unsupported")
        need(approval["kind"] == "review-cycle-exception-approval",
             "review-cycle exception kind mismatch")
        need(approval["run_id"] == field(self.data, "run_id")
             and approval["gate_id"] == gate["id"],
             "review-cycle exception scope mismatch")
        need(type(approval["additional_cycles"]) is int and approval["additional_cycles"] == 1,
             "review-cycle exception must authorize exactly one additional cycle")
        need(approval["approved"] is True, "review-cycle exception is not affirmatively approved")
        need(approval["approval_question"] == REVIEW_CYCLE_EXCEPTION_QUESTION
             and approval["approval_answer"] == REVIEW_CYCLE_EXCEPTION_ANSWER,
             "review-cycle exception approval text mismatch")
        source_session = text(approval["source_session_id"], "review-cycle exception source session")
        need(source_session in self.coordinators
             or source_session == self.data.get("creator_session_id"),
             "review-cycle exception source session mismatch")
        timestamp(approval["recorded_at"], "review-cycle exception timestamp")
        text(approval["reason"], "review-cycle exception reason")
        need(approval["preserved_reviews"] == reviews[:2],
             "review-cycle exception does not preserve the original first two reviews")

    def gate(self, gate):
        state = choice(field(gate, "status"), GATE_STATES, "gate state")
        dependencies = strings(field(gate, "depends_on"), "gate dependencies")
        need(all(key in self.gates and key != gate["id"] for key in dependencies), "invalid gate dependency")
        artifact = field(gate, "artifact")
        if artifact is not None:
            self.artifact(artifact)
        reviews = items(field(gate, "reviews"), "gate reviews")
        if "review_cycle_exception" in gate:
            self.review_cycle_exception(gate, reviews, gate["review_cycle_exception"])
        if state == "accepted":
            need(artifact is not None and bool(reviews), "accepted gate lacks artifact/reviews")
            need(all(self.gates[key]["status"] == "accepted" for key in dependencies),
                 "accepted gate has an unaccepted dependency")
        previous = None
        for cycle, reference in enumerate(reviews, 1):
            review = self.review(gate, reference, cycle, state == "accepted" and cycle == len(reviews))
            historical_third = cycle == 3 and "review_cycle_exception" in gate
            if cycle > 2 and not historical_third:
                need(review["subject_sha256"] != previous["subject_sha256"]
                     or review["prerequisite_sha256"] != previous["prerequisite_sha256"],
                     "review makes no progress: subject and prerequisite hashes unchanged")
            previous = review

    def contract(self):
        contract = obj(field(self.data, "contract"), "contract")
        text(field(contract, "objective"), "contract objective")
        need(bool(strings(field(contract, "deliverables"), "deliverables")), "deliverables required")
        strings(field(contract, "permitted_actions"), "permitted actions")
        strings(field(contract, "exclusions"), "scope exclusions")
        change_kind = choice(field(contract, "change_kind"), {"executable", "documentation"}, "change kind")
        if field(contract, "deadline_at") is not None:
            timestamp(contract["deadline_at"], "deadline")
        if field(contract, "requested_worker_limit") is not None:
            integer(contract["requested_worker_limit"], 1, "worker limit")
        self.criteria = indexed(field(contract, "acceptance_criteria"), "acceptance criteria")
        self.features = indexed(field(contract, "features"), "features")
        need(bool(self.criteria) and bool(self.features), "features and acceptance criteria required before coding")
        for criterion in self.criteria.values():
            text(field(criterion, "description"), "criterion description")
        feature_coverage = set()
        for feature in self.features.values():
            text(field(feature, "description"), "feature description")
            coverage = set(strings(field(feature, "criterion_ids"), "feature criteria"))
            need(bool(coverage) and coverage <= self.criteria.keys(), "invalid feature criteria")
            feature_coverage.update(coverage)
        need(feature_coverage == self.criteria.keys(), "criteria not mapped to features")
        self.checks = indexed(field(contract, "verification_matrix"), "verification matrix")
        categories = {}
        coverage = set()
        for check in self.checks.values():
            category = choice(field(check, "category"), EXCLUSIONS, "check category")
            classification = choice(field(check, "applicability"), {"required", "excluded"}, "applicability")
            categories.setdefault(category, set()).add(classification)
            criterion_ids = set(strings(field(check, "criterion_ids"), "check criteria"))
            need(criterion_ids <= self.criteria.keys(), "unknown check criterion")
            if classification == "excluded":
                need(change_kind != "executable" or category not in {"behavior", "runtime"},
                     "executable changes require behavior and runtime checks")
                need(not criterion_ids, "excluded check cannot prove an acceptance criterion")
                need(field(check, "exclusion_reason") == EXCLUSIONS[category], "invalid exclusion reason")
                evidence = items(field(check, "exclusion_evidence"), "exclusion evidence")
                need(bool(evidence), "exclusion requires repository evidence")
                for reference in evidence:
                    self.artifact(reference)
            else:
                for key in ("command", "cwd", "expected"):
                    text(field(check, key), f"check.{key}")
                need(Path(check["cwd"]).is_absolute(), "check cwd must be absolute")
                need(Path(check["cwd"]).resolve().is_relative_to(self.worktree),
                     "check cwd is outside the authorized worktree")
                integer(field(check, "timeout_seconds"), 1, "check timeout")
                kind = choice(field(check, "test_kind"), {"tests", "procedure"}, "test kind")
                count = integer(field(check, "minimum_tests"), 0, "minimum tests")
                names = strings(field(check, "required_tests"), "required tests")
                need((kind == "tests" and count >= 1 and bool(names))
                     or (kind == "procedure" and count == 0 and not names), "invalid test expectations")
                coverage.update(criterion_ids)
        need(set(categories) == set(EXCLUSIONS), "matrix must classify all seven check categories")
        need(all(len(value) == 1 for value in categories.values()), "category is both required and excluded")
        need(coverage == self.criteria.keys(), "acceptance criterion lacks a required check")
        return contract

    def audit(self):
        data = self.data
        need(type(field(data, "schema_version")) is int and data["schema_version"] == 3,
             "checkpoint schema 3 required; migrate older state explicitly")
        text(field(data, "run_id"), "run id")
        choice(field(data, "status"), RUN_STATES, "run state")
        choice(field(data, "phase"), PHASES, "run phase")
        need(timestamp(field(data, "updated_at"), "updated_at") >= timestamp(field(data, "created_at"), "created_at"),
             "checkpoint timestamps are reversed")
        self.coordinators = strings(field(data, "coordinator_history"), "coordinator history")
        need(text(field(data, "coordinator_session_id"), "coordinator id") in self.coordinators,
             "current coordinator missing from history")
        repository = obj(field(data, "repository"), "repository")
        text(field(repository, "identity"), "repository identity")
        need(Path(text(field(repository, "worktree_path"), "worktree path")).is_absolute(),
             "worktree path must be absolute")
        self.worktree = Path(repository["worktree_path"]).resolve()
        need(not self.root.is_relative_to(self.worktree), "run artifacts must be outside worktree")
        phases = items(field(data, "phase_gates"), "phase gates")
        need([field(g, "id") for g in phases] == list(PHASES), "seven ordered phase gates required")
        self.gates = indexed(phases, "phase gates")
        self.milestones = indexed(field(data, "milestones"), "milestones")
        need(not self.gates.keys() & self.milestones.keys(), "milestone id collides with phase")
        self.gates.update(self.milestones)
        for i, gate in enumerate(phases):
            need(field(gate, "depends_on") == ([] if i == 0 else [PHASES[i - 1]]), "phase dependency order changed")
        for gate in self.milestones.values():
            need(field(gate, "depends_on") == ["implementation_plan"], "milestone must depend on accepted plan")
        for gate in self.gates.values():
            self.gate(gate)
        if self.gates["implementation_plan"]["status"] == "accepted":
            plan = self.artifact_json(self.gates["implementation_plan"]["artifact"])
            need(type(field(plan, "schema_version")) is int and plan["schema_version"] == 1,
                 "unsupported implementation-plan schema")
            text(field(plan, "plan_text"), "plan text")
            need(field(plan, "contract") == field(data, "contract"), "contract changed after plan review")
            self.contract()
        items(field(data, "tasks"), "tasks")
        items(field(data, "workers"), "workers")
        for blocker in indexed(field(data, "blockers"), "blockers").values():
            choice(field(blocker, "status"), {"open", "resolved"}, "blocker status")
            choice(field(blocker, "scope"), {"run", "gate", "task"}, "blocker scope")
            text(field(blocker, "reason"), "blocker reason")
        execution = obj(field(data, "execution"), "execution")
        text(field(execution, "host"), "execution host")
        need(type(field(execution, "automation_enabled")) is bool, "automation_enabled must be boolean")
        if data["status"] != "completed":
            text(field(data, "next_action"), "next action")
        attempts = {}
        repair_hypotheses = {}
        for attempt in items(field(data, "failure_attempts"), "failure attempts"):
            operation = text(field(attempt, "operation_id"), "failure operation")
            kind = choice(field(attempt, "kind"), {"transient", "repair"}, "failure kind")
            key = (operation, kind)
            expected = attempts.get(key, 0) + 1
            number = integer(field(attempt, "attempt"), 1, "failure attempt")
            need(number == expected, "attempt counts must be contiguous and preserved")
            if kind == "transient":
                need(number <= 3, "operation retry/repair limit exceeded")
            attempts[key] = number
            choice(field(attempt, "result"), {"succeeded", "failed"}, "attempt result")
            hypothesis = text(field(attempt, "hypothesis"), "attempt hypothesis")
            if kind == "repair":
                normalized = " ".join(hypothesis.split()).casefold()
                previous = repair_hypotheses.setdefault(operation, set())
                need(normalized not in previous, "distinct repair hypothesis required within the same operation")
                previous.add(normalized)
            self.artifact(field(attempt, "log"))

    def implement(self):
        need(self.data["status"] == "running", "implementation requires a running run")
        need(self.data["phase"] == "implementation", "implementation phase required")
        need(all(self.gates[key]["status"] == "accepted" for key in PHASES[:5]),
             "five accepted planning gates required")
        contract = self.data["contract"]
        deadline = field(contract, "deadline_at")
        if deadline is not None:
            need(datetime.now(timezone.utc) < timestamp(deadline, "deadline"), "execution deadline reached")
        for blocker in self.data["blockers"]:
            if field(blocker, "status") == "open":
                need(field(blocker, "scope") == "task", "open stage/run blocker")
        limit = field(contract, "requested_usage_limit")
        if limit is not None:
            text(field(contract, "usage_limit_enforced_by"), "requested usage limit enforcing control")

    def complete(self):
        data = self.data
        need(data["status"] in {"running", "completed"}, "blocked/paused/failed run cannot complete")
        need(data["phase"] == "verification", "verification phase required for completion")
        need(all(self.gates[key]["status"] == "accepted" for key in PHASES), "all seven gates must be accepted")
        need(bool(self.milestones) and all(g["status"] == "accepted" for g in self.milestones.values()),
             "accepted implementation milestones required")
        need(all(field(b, "status") == "resolved" for b in data["blockers"]), "unresolved blockers")
        execution = data["execution"]
        need(field(execution, "automation_enabled") is False, "disable this run's schedule before completion")
        need(not items(field(execution, "helpers"), "helpers"), "task-only helpers must be stopped and removed from active list")
        workers = indexed(data["workers"], "workers")
        for worker in workers.values():
            status = text(field(worker, "status"), "worker status")
            need(status in {"completed", "failed", "cancelled"}, "worker still active")
            choice(field(worker, "role"), {"planning", "implementation", "test", "review", "verification"}, "worker role")
        for actor_id in self.review_owners:
            need(actor_id in workers and workers[actor_id]["role"] == "review"
                 and workers[actor_id]["status"] == "completed", "review actor missing or not completed in worker registry")
        tasks = indexed(data["tasks"], "tasks")
        need(bool(tasks), "completed run requires completed tasks")
        authors = set(self.coordinators)
        authors.update(w["id"] for w in workers.values() if w["role"] in {"implementation", "test"})
        for task in tasks.values():
            need(field(task, "status") == "done", "unfinished task")
            owner = text(field(task, "owner_id"), "task owner")
            need(owner in workers or owner in self.coordinators, "unknown task owner")
            authors.add(owner)
            milestone_id = text(field(task, "milestone_id"), "task milestone")
            need(milestone_id in self.milestones, "task missing reviewed milestone")
            criterion_ids = strings(field(task, "criterion_ids"), "task criteria")
            need(bool(criterion_ids) and set(criterion_ids) <= self.criteria.keys(), "invalid task criteria")
            dependencies = strings(field(task, "depends_on"), "task dependencies")
            need(all(dep in tasks and dep != task["id"] for dep in dependencies), "invalid task dependency")
        visited, active = set(), set()

        def visit(key):
            need(key not in active, "cyclic task dependencies")
            if key in visited:
                return
            active.add(key)
            for dependency in tasks[key]["depends_on"]:
                visit(dependency)
            active.remove(key)
            visited.add(key)

        for key in tasks:
            visit(key)
        verifier = obj(field(execution, "verifier"), "independent verifier")
        verifier_id = text(field(verifier, "id"), "verifier id")
        need(verifier_id not in authors, "final verifier authored/coordinated the work")
        need(verifier_id in workers and workers[verifier_id]["role"] == "verification"
             and workers[verifier_id]["status"] == "completed", "verifier missing or not completed in worker registry")
        verifier_report = self.artifact_json(field(verifier, "report"))
        need(field(verifier_report, "runner_id") == verifier_id, "verifier report runner differs")
        need(bool(strings(field(verifier_report, "environment"), "verification environment")),
             "verifier must record environment/tool/dependency versions")
        text(field(verifier_report, "summary"), "verifier report summary")
        source_ref = field(data, "source_snapshot")
        recorded_source = self.artifact_json(source_ref)
        need(type(field(recorded_source, "schema_version")) is int and recorded_source["schema_version"] == 1,
             "unsupported source snapshot schema")
        actual_source = capture_snapshot(data["repository"]["worktree_path"])
        need(not self.root.is_relative_to(Path(actual_source["root"])), "run artifacts must be outside worktree")
        need(recorded_source == actual_source, "delivered source differs from tested source")
        plan_sha = self.gates["implementation_plan"]["artifact"]["sha256"]
        need(field(verifier_report, "plan_sha256") == plan_sha, "verifier report plan is stale")
        need(field(verifier_report, "before_snapshot_sha256") == source_ref["sha256"]
             and field(verifier_report, "after_snapshot_sha256") == source_ref["sha256"],
             "source changed during verification")
        implementation = self.artifact_json(self.gates["implementation"]["artifact"])
        text(field(implementation, "summary"), "implementation summary")
        need(field(implementation, "source_snapshot_sha256") == source_ref["sha256"], "implementation review source is stale")
        need(field(implementation, "milestone_sha256") == {k: v["artifact"]["sha256"] for k, v in self.milestones.items()},
             "implementation milestone references are stale")
        evidence = indexed(field(data, "verification_evidence"), "verification evidence")
        latest = {}
        for record in evidence.values():
            digest(field(record, "snapshot_sha256"), "evidence snapshot")
            digest(field(record, "plan_sha256"), "evidence plan")
            finished = timestamp(field(record, "finished_at"), "check finish")
            need(finished >= timestamp(field(record, "started_at"), "check start"), "check timestamps reversed")
            choice(field(record, "result"), {"passed", "failed", "blocked"}, "check result")
            self.artifact(field(record, "log"))
            if record["snapshot_sha256"] == source_ref["sha256"] and record["plan_sha256"] == plan_sha:
                check_id = text(field(record, "check_id"), "evidence check id")
                need(check_id in self.checks, "evidence references unknown current check")
                if check_id not in latest or finished >= latest[check_id][0]:
                    latest[check_id] = (finished, record)
        passing = {}
        for key, check in self.checks.items():
            if check["applicability"] == "excluded":
                continue
            need(key in latest, f"missing current verification: {key}")
            record = latest[key][1]
            need(field(record, "runner_id") == verifier_id, f"check not run by independent verifier: {key}")
            need(record["result"] == "passed" and type(field(record, "exit_code")) is int and record["exit_code"] == 0,
                 f"latest check did not pass: {key}")
            need(field(record, "command") == check["command"] and field(record, "cwd") == check["cwd"],
                 f"check command/cwd differs from accepted plan: {key}")
            text(field(record, "observed"), "observed check outcome")
            integer(field(record, "tests_executed"), check["minimum_tests"], "executed tests")
            executed = strings(field(record, "required_tests_executed"), "executed required tests")
            need(set(check["required_tests"]) <= set(executed), f"required test was not executed: {key}")
            need(field(record, "skipped_required_tests") == [], f"required test was skipped: {key}")
            passing[record["id"]] = set(check["criterion_ids"])
        results = indexed(field(data, "feature_results"), "feature results")
        need(results.keys() == self.features.keys(), "feature results do not match required features")
        for key, feature in self.features.items():
            result = results[key]
            need(field(result, "status") == "verified", f"unverified feature: {key}")
            refs = strings(field(result, "evidence_ids"), "feature evidence")
            need(bool(refs) and all(ref in passing for ref in refs), "feature refers to stale/nonpassing evidence")
            coverage = set().union(*(passing[ref] for ref in refs))
            need(set(feature["criterion_ids"]) <= coverage, f"feature criteria not verified: {key}")
        final = self.artifact_json(self.gates["verification"]["artifact"])
        need(field(final, "plan_sha256") == plan_sha, "verification review plan is stale")
        need(field(final, "source_snapshot_sha256") == source_ref["sha256"], "verification review source is stale")
        need(field(final, "evidence_sha256") == canonical_sha(data["verification_evidence"]), "verification review evidence is stale")
        need(field(final, "verifier_report_sha256") == verifier["report"]["sha256"], "verification review report is stale")
        text(field(final, "summary"), "verification summary")

    def validate(self, action):
        choice(action, {"audit", "implement", "complete"}, "validation action")
        self.audit()
        if action == "implement":
            self.implement()
        if action == "complete" or self.data["status"] == "completed":
            self.complete()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("audit", "implement", "complete", "snapshot"))
    parser.add_argument("path", type=Path, help="checkpoint path, or worktree root for snapshot")
    args = parser.parse_args()
    try:
        if args.action == "snapshot":
            print(json.dumps(capture_snapshot(args.path), indent=2, sort_keys=True))
        else:
            validator = Validator(args.path)
            validator.validate(args.action)
            print(f"VALID {args.action}: {validator.data['run_id']}")
        return 0
    except (Invalid, OSError, UnicodeError, ValueError, RecursionError,
            subprocess.CalledProcessError, subprocess.TimeoutExpired) as error:
        print(f"BLOCKED: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
