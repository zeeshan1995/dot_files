import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]


@unittest.skipUnless(shutil.which("tmux"), "tmux is required to check configuration dispatch")
class PlatformConfigTests(unittest.TestCase):
    def configuration(self, platform):
        with tempfile.TemporaryDirectory(prefix="dotfiles-platform-") as directory:
            root = Path(directory)
            tools = root / "bin"
            tools.mkdir()
            uname = tools / "uname"
            uname.write_text(f"#!/bin/sh\nprintf '%s\\n' '{platform}'\n")
            uname.chmod(0o755)
            environment = dict(os.environ, HOME=str(root),
                               PATH=f"{tools}:{os.environ['PATH']}")
            environment.pop("TMUX", None)
            socket = str(root / "tmux.sock")
            command = ["tmux", "-S", socket]
            try:
                subprocess.run([*command, "-f", "/dev/null", "new-session", "-d",
                                "sleep 60"], env=environment, check=True,
                               capture_output=True, timeout=10)
                subprocess.run([*command, "source-file", str(ROOT / ".tmux.conf")],
                               env=environment, check=True, capture_output=True, timeout=10)
                output = subprocess.check_output([*command, "show-options", "-g"],
                                                 env=environment, text=True, timeout=10)
                options = dict(line.split(" ", 1) for line in output.splitlines())
                return options
            finally:
                subprocess.run([*command, "kill-server"], env=environment,
                               capture_output=True, timeout=10)

    def test_linux_uses_systemd_and_exact_application_ids(self):
        options = self.configuration("Linux")
        self.assertEqual(options["@continuum-save-interval"], "0")
        self.assertEqual(options["@continuum-boot"], "on")
        self.assertEqual(options["@resurrect-strategy-vim"], "''")
        self.assertIn("tmux-app-state save", options["@resurrect-hook-post-save-layout"])
        self.assertIn("copilot --resume", options["@resurrect-processes"])
        self.assertEqual(options["prefix"], "C-a")

    def test_macos_keeps_continuum_without_linux_hooks(self):
        options = self.configuration("Darwin")
        self.assertEqual(options["@continuum-save-interval"], "5")
        self.assertEqual(options["@continuum-boot"], "off")
        self.assertEqual(options["@resurrect-strategy-vim"], "session")
        self.assertNotIn("@resurrect-hook-post-save-layout", options)
        self.assertEqual(options["@resurrect-processes"], '"copilot lazygit yazi"')
        self.assertEqual(options["prefix"], "C-a")


if __name__ == "__main__":
    unittest.main()
