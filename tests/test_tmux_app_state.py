import importlib.machinery
import importlib.util
import json
import os
from pathlib import Path
import shlex
import sys
import tempfile
import unittest
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
loader = importlib.machinery.SourceFileLoader(
    "tmux_app_state", str(ROOT / ".local/bin/tmux-app-state")
)
spec = importlib.util.spec_from_loader(loader.name, loader)
app = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = app
loader.exec_module(app)


def pane(index, command="bash"):
    return "\t".join(("pane", "work", "1", "1", ":*", str(index),
                      "fixture", ":/workspace", "1", command, ":" + command))


class SnapshotTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="tmux-app-test-")
        self.addCleanup(self.temporary.cleanup)
        self.path = Path(self.temporary.name) / "snapshot.txt"
        self.vim_one = Path(self.temporary.name) / "editor one.vim"
        self.vim_two = Path(self.temporary.name) / "editor two.vim"
        self.vim_one.touch()
        self.vim_two.touch()
        self.owner = app.Process(123, 100, 123, 456, 123, 789)
        self.state = {"kind": "copilot", "pid": 123, "started": 789,
                      "session_id": "c3b2401f-abab-4fb6-86d3-bf0eb1bba0d5",
                      "cwd": "/workspace/a project"}

    def rewrite(self, states, alive=True, active=True):
        registrations = "\n".join(
            f"work\t1\t{index}\t100\t{json.dumps(state)}"
            for index, state in states.items()
        )
        with patch.object(app, "tmux", return_value=registrations), \
                patch.object(app, "process", return_value=self.owner if alive else None), \
                patch.object(app, "active_in_pane", return_value=active):
            app.save_layout(self.path)
        return [line.split("\t") for line in self.path.read_text().splitlines()]

    def test_exact_copilot_and_independent_vim_files(self):
        self.path.write_text("\n".join((pane(1, "copilot"), pane(2, "vim"),
                                      pane(3, "vim"), pane(4), "state\twork\t")) + "\n")
        first = dict(self.state, kind="vim", file=str(self.vim_one), readonly=False)
        second = dict(first, file=str(self.vim_two), readonly=True)
        rows = self.rewrite({1: self.state, 2: first, 3: second})
        self.assertEqual(shlex.split(rows[0][10][1:]),
                         ["copilot", "--resume", self.state["session_id"]])
        self.assertEqual(rows[0][7], ":/workspace/a project")
        self.assertEqual(shlex.split(rows[1][10][1:]), ["vim", "-S", str(self.vim_one)])
        self.assertEqual(shlex.split(rows[2][10][1:]), ["vim", "-R", "-S", str(self.vim_two)])
        self.assertEqual("\t".join(rows[3]), pane(4))
        self.assertEqual("\t".join(rows[4]), "state\twork\t")
        self.assertEqual(self.path.stat().st_mode & 0o777, 0o600)

    def test_dead_background_and_reused_pid_records_are_ignored(self):
        for alive, active, started in ((False, True, 789), (True, False, 789),
                                       (True, True, 790)):
            with self.subTest(alive=alive, active=active, started=started):
                self.path.write_text(pane(1) + "\n")
                rows = self.rewrite({1: dict(self.state, started=started)}, alive, active)
                self.assertEqual("\t".join(rows[0]), pane(1))

    def test_latest_registered_conversation_wins(self):
        self.path.write_text(pane(1, "copilot") + "\n")
        new_id = "70a11bfd-2956-48a8-9d7f-83dbed510da0"
        rows = self.rewrite({1: dict(self.state, session_id=new_id)})
        self.assertEqual(shlex.split(rows[0][10][1:])[-1], new_id)

    def test_session_end_clears_only_the_matching_conversation(self):
        for session_id, should_clear in (
            (self.state["session_id"], True),
            ("70a11bfd-2956-48a8-9d7f-83dbed510da0", False),
        ):
            with self.subTest(session_id=session_id):
                with patch.dict(os.environ, {"TMUX_PANE": "%9"}), \
                        patch.object(app, "active_in_pane", return_value=True), \
                        patch.object(app, "tmux", side_effect=["100", json.dumps(self.state), ""]) as tmux:
                    app.register(self.owner, dict(self.state, session_id=session_id), ending=True)
                    self.assertEqual(tmux.call_count, 3 if should_clear else 2)
                    if should_clear:
                        tmux.assert_called_with("set-option", "-pu", "-t", "%9", app.OPTION)

    def test_bad_record_does_not_replace_snapshot(self):
        original = "pane\tunsupported-format\n"
        self.path.write_text(original)
        with self.assertRaisesRegex(ValueError, "Unsupported"):
            self.rewrite({})
        self.assertEqual(self.path.read_text(), original)

    def test_repeated_same_second_save_preserves_last_snapshot(self):
        self.path.write_text(pane(1) + "\n")
        last = self.path.parent / "last"
        last.symlink_to(self.path.name)
        self.rewrite({})
        self.assertNotEqual(last.resolve(), self.path.resolve())
        self.assertEqual(last.read_text(), self.path.read_text())
        self.path.unlink()
        self.assertEqual(last.read_text(), pane(1) + "\n")

    def test_missing_vim_session_is_an_explicit_failure(self):
        self.path.write_text(pane(1, "vim") + "\n")
        with self.assertRaisesRegex(ValueError, "missing"):
            self.rewrite({1: dict(self.state, kind="vim", readonly=False,
                                 file=str(self.vim_one) + ".missing")})
        self.assertEqual(self.path.read_text(), pane(1, "vim") + "\n")

    def test_hook_is_inert_outside_tmux(self):
        with patch.dict(os.environ, {}, clear=True), patch.object(app, "tmux") as tmux:
            app.copilot_hook()
        tmux.assert_not_called()


if __name__ == "__main__":
    unittest.main()
