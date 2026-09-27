#!/usr/bin/env python3
"""Screenshot a Neon Doll VS Code theme in a throwaway VS Code.

    tools/vscode-shoot.py dark|light out.png

Everything lives in a temporary directory, which is also $HOME for VS Code:
the extension is packed with tools/build-vscode.py --vsix and installed into
a scratch --extensions-dir, so it is the only extension there; the theme is
set in a scratch --user-data-dir's settings.json. A separate user-data-dir is
a separate instance, so a VS Code already running on the desktop is never
asked to open the window. The sample project is a small git repository with
uncommitted changes, and a folder-open task shows a colored `git diff` and
`ls` in the integrated terminal, and then says it's ready.

It runs in a sealed shotbox session, which it starts itself, so nothing
reaches the desktop's display or session bus.
"""

import json
import os
import shutil
import signal
import subprocess
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

if len(sys.argv) != 3 or sys.argv[1] not in ("dark", "light"):
    sys.exit("usage: tools/vscode-shoot.py dark|light out.png")

# In a sealed shotbox session (https://github.com/mishan/shotbox, on PATH),
# started around this script if it isn't in one already.
if not os.environ.get("SHOTBOX_SCRATCH"):
    os.execvp("shotbox", ["shotbox", "run", "--screen", "1280x800", "--",
                          sys.executable, os.path.abspath(__file__), *sys.argv[1:]])


def shotbox(*args):
    subprocess.run(["shotbox", *map(str, args)], check=True)


variant, out = sys.argv[1], Path(sys.argv[2]).resolve()
tmp = Path(tempfile.mkdtemp(prefix="neon-doll-vscode-"))
home, ud, ext, proj = tmp / "home", tmp / "user-data", tmp / "extensions", tmp / "demo"
for d in (home, ud / "User", ext, proj / "src", proj / ".vscode"):
    d.mkdir(parents=True)

env = dict(os.environ, HOME=str(home), XDG_CONFIG_HOME=str(home / ".config"),
           XDG_DATA_HOME=str(home / ".local/share"), XDG_CACHE_HOME=str(home / ".cache"),
           GIT_CONFIG_NOSYSTEM="1")
code = ["code", "--user-data-dir", str(ud), "--extensions-dir", str(ext)]

vsix = tmp / "neon-doll.vsix"
subprocess.run([sys.executable, str(ROOT / "tools/build-vscode.py"), "--vsix", str(vsix)],
               check=True, stdout=subprocess.DEVNULL)
subprocess.run(code + ["--install-extension", str(vsix)], env=env, check=True,
               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

label = f"Neon Doll {variant.capitalize()}"
(ud / "User" / "settings.json").write_text(json.dumps({
    "workbench.colorTheme": label,
    "window.autoDetectColorScheme": False,
    "window.titleBarStyle": "custom",
    "window.newWindowDimensions": "maximized",
    "window.restoreWindows": "none",
    "window.commandCenter": True,
    "workbench.startupEditor": "none",
    "workbench.tips.enabled": False,
    "workbench.enableExperiments": False,
    "workbench.secondarySideBar.defaultVisibility": "hidden",
    "chat.disableAIFeatures": True,
    "telemetry.telemetryLevel": "off",
    "update.mode": "none",
    "extensions.autoCheckUpdates": False,
    "extensions.autoUpdate": False,
    "extensions.ignoreRecommendations": True,
    "security.workspace.trust.enabled": False,
    "task.allowAutomaticTasks": "on",
    "git.openRepositoryInParentFolders": "never",
    "git.autofetch": False,
    "editor.fontFamily": "'DejaVu Sans Mono', monospace",
    "editor.fontSize": 13,
    "editor.minimap.enabled": True,
    "terminal.integrated.fontFamily": "'DejaVu Sans Mono', monospace",
    "terminal.integrated.defaultProfile.linux": "bash",
    "terminal.integrated.enablePersistentSessions": False,
    # Cursors that don't blink: the picture waits for the window to hold still.
    "editor.cursorBlinking": "solid",
    "terminal.integrated.cursorBlinking": False,
}, indent=2))

# The sample project: committed, then changed, so the gutter and the explorer
# show added, modified and untracked.
APP_OLD = '''\
"""Count the colors in a palette file."""

import json
from pathlib import Path

LIMIT = 16


def load(path):
    return json.loads(Path(path).read_text())


class Palette:
    def __init__(self, colors):
        self.colors = colors[:LIMIT]

    def __len__(self):
        return len(self.colors)
'''
APP_NEW = '''\
"""Count the colors in a palette file."""

import json
from dataclasses import dataclass
from pathlib import Path

LIMIT = 16  # the terminal's sixteen, no more


def load(path: str) -> dict:
    """Read a Tilix scheme."""
    return json.loads(Path(path).read_text(encoding="utf-8"))


@dataclass
class Palette:
    colors: list[str]
    cursor: str = "#ff2d95"

    def __len__(self):
        return min(len(self.colors), LIMIT)

    def hex(self, i: int) -> str:
        if i < 0 or i >= len(self):
            raise IndexError(f"no color {i}, only {len(self)}")
        return self.colors[i].lower()


if __name__ == "__main__":
    p = Palette(load("tilix/neon-doll-dark.json")["palette"])
    for i in range(len(p)):
        print(f"{i:2d} {p.hex(i)}", end="\\n" if i % 4 == 3 else "  ")
    print(None is not True, 0x2d, 3.14)
'''
UTIL_TS = '''\
// Contrast between two colors, as WCAG 2 defines it.
export type Hex = `#${string}`;

const CHANNELS = [0.2126, 0.7152, 0.0722] as const;

function channel(v: number): number {
  v /= 255;
  return v <= 0.04045 ? v / 12.92 : ((v + 0.055) / 1.055) ** 2.4;
}

export function luminance(hex: Hex): number {
  const rgb = [1, 3, 5].map((i) => parseInt(hex.slice(i, i + 2), 16));
  return rgb.reduce((sum, v, i) => sum + CHANNELS[i] * channel(v), 0);
}

export class Pair {
  constructor(readonly fg: Hex, readonly bg: Hex) {}

  get ratio(): number {
    const [hi, lo] = [luminance(this.fg), luminance(this.bg)].sort((a, b) => b - a);
    return (hi + 0.05) / (lo + 0.05);
  }

  passes(): boolean {
    return this.ratio >= 4.5 && this.fg !== this.bg;
  }
}
'''
(proj / "src" / "palette.py").write_text(APP_OLD)
(proj / "README.md").write_text("# demo\n\nA palette and its contrast.\n")
(proj / "src" / "old.txt").write_text("gone soon\n")


def git(*args):
    subprocess.run(["git", "-c", "user.name=Demo", "-c", "user.email=demo@example.com",
                    "-c", "init.defaultBranch=main", *args], cwd=proj, env=env,
                   check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


git("init")
git("add", ".")
git("commit", "-m", "palette")
(proj / "src" / "palette.py").write_text(APP_NEW)
(proj / "src" / "contrast.ts").write_text(UTIL_TS)
(proj / "src" / "old.txt").unlink()

(proj / ".vscode" / "tasks.json").write_text(json.dumps({
    "version": "2.0.0",
    "tasks": [{
        "label": "status",
        "type": "shell",
        # A task that ends, printing a prompt as it goes, rather than a shell
        # left running: a running task's tab has a spinner that never stops.
        "command": "bash .vscode/demo.bashrc",
        "presentation": {"reveal": "always", "panel": "dedicated", "focus": False,
                         "showReuseMessage": False, "echo": False},
        "runOptions": {"runOn": "folderOpen"},
        "problemMatcher": [],
    }],
}, indent=2))
(proj / ".vscode" / "demo.bashrc").write_text(r"""
git -c color.ui=always diff --stat
git -c color.ui=always diff -U0 src/palette.py | sed -n 5,12p
for i in 0 1 2 3 4 5 6 7; do printf '\e[4%sm   \e[0m' $i; done; echo
for i in 0 1 2 3 4 5 6 7; do printf '\e[10%sm   \e[0m' $i; done; echo
printf '\e[35mdemo\e[0m \e[90mmain\e[0m $ '
touch "$SHOTBOX_SCRATCH/ready"
""")
(proj / ".git" / "info" / "exclude").write_text(".vscode/\n")

# The Electron binary itself, not the `code` wrapper, whose CLI would hand the
# window to a detached process; this way the whole session can be killed.
electron = Path(shutil.which("code")).resolve().parent.parent / "code"
app = subprocess.Popen(
    [str(electron), "--user-data-dir", str(ud), "--extensions-dir", str(ext), "--new-window", "--disable-gpu", "--ozone-platform=x11", "--no-sandbox",
            "--password-store=basic", "--disable-workspace-trust", "--skip-release-notes",
            "--skip-welcome", "--disable-telemetry", "--disable-crash-reporter",
            str(proj), "--goto", f"{proj}/src/palette.py:21:36"],
    env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
try:
    # The terminal's task is the last thing to start; then give the rest a
    # second without a change.
    shotbox("wait", "ready", "--timeout", "60")
    shotbox("wait", "stable", "1")
    shotbox("capture", out)
    print(out)
finally:
    os.killpg(app.pid, signal.SIGTERM)
    time.sleep(2)
    try:
        os.killpg(app.pid, signal.SIGKILL)
    except ProcessLookupError:
        pass
    shutil.rmtree(tmp, ignore_errors=True)
