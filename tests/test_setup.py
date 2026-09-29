import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]

# External service/package boundaries are simulated; the real installer performs
# all copying, backup, permission and dependency-ordering work in a private home.
TOOL = """#!/usr/bin/python3
import json, os, pathlib, subprocess, sys
name = pathlib.Path(sys.argv[0]).name
args = sys.argv[1:]
home = pathlib.Path(os.environ["HOME"])
with open(os.environ["SETUP_TEST_LOG"], "a") as file:
    file.write(json.dumps([name, *args]) + "\\n")
if os.environ.get("SETUP_TEST_FAIL") == name:
    print("Injected failure: " + name, file=sys.stderr)
    sys.exit(17)
if name == "sudo":
    sys.exit(subprocess.run(args).returncode)
elif name in ("apt-get", "loginctl", "vim"):
    pass
elif name == "git":
    assert args[0] == "clone", args
    destination = pathlib.Path(args[-1])
    (destination / ".git").mkdir(parents=True)
    entry = {"tpm": "tpm", "tmux-resurrect": "resurrect.tmux",
             "tmux-continuum": "continuum.tmux"}[destination.name]
    script = destination / entry
    script.write_text("#!/bin/sh\\nexit 0\\n")
    script.chmod(0o755)
elif name == "systemctl":
    if "start" in args:
        unit = args[-1]
        (home / (unit + ".active")).touch()
        if unit == "tmux.service":
            (home / "tmux-running").touch()
    elif "is-active" in args:
        sys.exit(0 if (home / (args[-1] + ".active")).exists() else 3)
elif name == "tmux":
    if args[0] == "has-session":
        sys.exit(0 if (home / "tmux-running").exists() else 1)
    assert args[0] == "source-file", args
else:
    raise RuntimeError("Unexpected external command: " + name)
"""


@unittest.skipIf(os.geteuid() == 0 or not Path("/run/systemd/system").is_dir(),
                 "The installer targets a non-root Linux systemd user")
class SetupTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="dotfiles-setup-test-")
        self.addCleanup(self.temporary.cleanup)
        self.directory = Path(self.temporary.name)
        self.home = self.directory / "new-user"
        self.home.mkdir()
        self.bin = self.directory / "bin"
        self.bin.mkdir()
        self.log = self.directory / "calls.jsonl"
        for name in ("sudo", "apt-get", "loginctl", "git", "vim", "tmux", "systemctl"):
            path = self.bin / name
            path.write_text(TOOL)
            path.chmod(0o755)
        self.environment = dict(os.environ, HOME=str(self.home),
                                PATH=f"{self.bin}:/usr/bin:/bin",
                                SETUP_TEST_LOG=str(self.log))
        for name in ("TMUX", "TMUX_PANE", "XDG_CONFIG_HOME", "COPILOT_HOME"):
            self.environment.pop(name, None)

    def setup(self, *args, failure=None):
        if failure:
            self.environment["SETUP_TEST_FAIL"] = failure
        result = subprocess.run(["bash", str(ROOT / "setup.sh"), *args],
                                cwd=self.directory, env=self.environment,
                                text=True, capture_output=True, timeout=30)
        if failure:
            self.assertNotEqual(result.returncode, 0, result.stdout)
        else:
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        return result

    def calls(self):
        return [json.loads(line) for line in self.log.read_text().splitlines()]

    def test_fresh_install_from_another_directory(self):
        self.setup()
        for relative in (
            ".tmux.conf", ".vimrc", ".bashrc", ".vim/plugin/tmux-session.vim",
            ".local/bin/tmux-app-state", ".copilot/hooks/tmux-app-restore.json",
            ".config/systemd/user/tmux.service", ".config/systemd/user/tmux-save.timer",
            ".config/systemd/user/tmux-save.service",
        ):
            self.assertEqual((self.home / relative).read_bytes(), (ROOT / relative).read_bytes())
        self.assertEqual((self.home / ".local/bin/tmux-app-state").stat().st_mode & 0o777, 0o755)
        self.assertEqual((self.home / ".local/state/tmux/vim").stat().st_mode & 0o777, 0o700)
        self.assertFalse((self.home / ".vim/.netrwhist").exists())
        calls = self.calls()
        self.assertEqual(len([call for call in calls if call[0] == "git"]), 3)
        self.assertIn(["systemctl", "--user", "start", "tmux.service"], calls)
        self.assertIn(["systemctl", "--user", "enable", "tmux.service", "tmux-save.timer"], calls)
        self.assertTrue(any(call[:2] == ["loginctl", "enable-linger"] for call in calls))
        self.assertLess(next(i for i, call in enumerate(calls) if call[0] == "vim"),
                        calls.index(["systemctl", "--user", "start", "tmux.service"]))
        package_calls = [call for call in calls if call[0] == "apt-get"]
        self.assertEqual(package_calls[0], ["apt-get", "update"])
        self.assertIn("python3", package_calls[1])
        self.assertFalse(any(word in ("purge", "upgrade", "openssh-server", "nodejs")
                             for call in package_calls for word in call))

    def test_rerun_backs_up_changes_and_does_not_restart_sessions(self):
        old = self.home / ".tmux.conf"
        old.write_text("original configuration\n")
        (self.home / "tmux-running").touch()
        extra_hook = self.home / ".copilot/hooks/existing.json"
        extra_hook.parent.mkdir(parents=True)
        extra_hook.write_text('{"version": 1, "hooks": {}}')
        self.setup("--skip-packages")
        backups = list((self.home / ".local/state/dot_files/backups").glob("*/**/.tmux.conf"))
        self.assertEqual(len(backups), 1)
        self.assertEqual(backups[0].read_text(), "original configuration\n")
        self.log.write_text("")
        (self.home / ".local/bin/tmux-app-state").chmod(0o644)
        self.setup("--skip-packages")
        self.assertEqual((self.home / ".local/bin/tmux-app-state").stat().st_mode & 0o777, 0o755)
        self.assertEqual(extra_hook.read_text(), '{"version": 1, "hooks": {}}')
        self.assertEqual(len(list((self.home / ".local/state/dot_files/backups").iterdir())), 1)
        calls = self.calls()
        self.assertFalse(any(call[0] in ("git", "apt-get") for call in calls))
        self.assertFalse(any(word in ("kill-server", "restart") for call in calls for word in call))
        self.assertNotIn(["systemctl", "--user", "start", "tmux.service"], calls)
        self.assertIn(["tmux", "source-file", str(self.home / ".tmux.conf")], calls)

    def test_failed_plugin_install_does_not_enable_services(self):
        for tool in ("git", "vim"):
            with self.subTest(tool=tool):
                self.log.write_text("")
                result = self.setup("--skip-packages", failure=tool)
                self.assertIn("Setup failed", result.stderr)
                self.assertNotIn("Setup complete", result.stdout)
                self.assertFalse(any("enable" in call or "start" in call
                                     for call in self.calls() if call[0] == "systemctl"))

    def test_custom_copilot_home(self):
        custom = self.home / "custom-copilot"
        self.environment["COPILOT_HOME"] = str(custom)
        self.setup("--skip-packages")
        self.assertTrue((custom / "hooks/tmux-app-restore.json").is_file())
        self.assertFalse((self.home / ".copilot/hooks/tmux-app-restore.json").exists())

    def test_conflicting_xdg_tmux_config_is_not_silently_ignored(self):
        config = self.home / ".config/tmux/tmux.conf"
        config.parent.mkdir(parents=True)
        config.write_text("set -g prefix C-x\n")
        result = self.setup("--skip-packages", failure="unused")
        self.assertIn("XDG", result.stderr)
        self.assertEqual(config.read_text(), "set -g prefix C-x\n")
        self.assertFalse((self.home / ".tmux.conf").exists())


if __name__ == "__main__":
    unittest.main()
