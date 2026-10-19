#!/usr/bin/env python3
"""Check the GTK 4 and GTK 3 themes as a screen reader and a low-vision
reader meet them, on tools/preview.py and tools/preview3.py in sealed
sessions: every control named, text and control edges above WCAG's floors
as drawn on the screen, and the focus seen at every stop. Dark and light,
and GTK 4 in high contrast too.

    tools/a11y-check.py

Needs shotbox 0.9.0 or later on PATH. tools/scheme-colors.py checks the same
floors on the palette; this checks them on the pixels.
"""

import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent

# What the checks report that isn't a problem, by (role, name), and why.
EXEMPT = {
    ("label", "disabled"): "disabled text, which WCAG leaves out",
    ("button", "Flat"): "a flat button has no edge, by design",
    ("button", "Back"): "header bar buttons are flat",
    ("button", "Search"): "header bar buttons are flat",
    ("button", "Main menu"): "header bar buttons are flat",
    ("toggle button", "Main menu"): "header bar buttons are flat",
    ("toggle button", "Menu"): "header bar buttons are flat",
    ("button", "example.org"): "a link button is a link, with no edge by design",
    ("button", "Minimize"): "window controls are flat",
    ("button", "Maximize"): "window controls are flat",
    ("button", "Close"): "window controls are flat",
    ("button", "Dismiss"): "a toast's close button is flat",
    ("button", "Close Tab"): "a tab's close button is flat, and drawn only on hover, "
                             "where it clears 3:1",
    ("text", "Display name"): "a row's edge is its boxed list's",
    ("combo box", "Theme"): "a row's edge is its boxed list's",
}
# libadwaita's tab bar scrolls its tabs in a scroll pane it doesn't name.
LINT_IGNORE = "focusable scroll pane with no name"

INSIDE = """
"$PREVIEW" $PREVIEW_ARGS >/dev/null 2>&1 &
shotbox wait window "$WINDOW" >/dev/null && shotbox wait stable >/dev/null
shotbox a11y lint --window "$WINDOW" --ignore "$LINT_IGNORE" > "$OUT/lint.txt"
echo $? > "$OUT/lint.status"
shotbox a11y contrast --edges 3 --window "$WINDOW" --json > "$OUT/contrast.json"
shotbox a11y tabwalk --visible --key ctrl+Tab --window "$WINDOW" --json > "$OUT/walk.json"
true
"""


def check(label, program, window, preview_args, session_args):
    with tempfile.TemporaryDirectory() as out:
        run = subprocess.run(
            ["shotbox", "run", "--a11y", "--screen", "1240x1040", *session_args,
             "--env", f"PREVIEW={HERE / program}", "--env", f"PREVIEW_ARGS={preview_args}",
             "--env", f"WINDOW={window}",
             "--env", f"OUT={out}", "--env", f"LINT_IGNORE={LINT_IGNORE}",
             "--", "sh", "-c", INSIDE],
            capture_output=True, text=True)
        if run.returncode:
            sys.exit(f"{label}: the session failed\n{run.stdout}{run.stderr}")
        out = Path(out)
        problems = []
        if (out / "lint.status").read_text().strip() != "0":
            problems += [f"lint: {line}" for line in (out / "lint.txt").read_text().splitlines()]
        contrast = json.loads((out / "contrast.json").read_text())
        for n in contrast["problems"]:
            if (n["role"], n["name"]) not in EXEMPT:
                problems.append(f'{n["role"]} "{n["name"]}": {n["problem"]}')
        walk = json.loads((out / "walk.json").read_text())
        if walk.get("end") != "cycle":
            problems.append(f"tabwalk: {walk.get('end')}")
        for n in walk["focus"]:
            if n.get("changed") is not None and n["changed"] < n["needed"] \
                    and (n["role"], n["name"]) not in EXEMPT:
                problems.append(f'{n["role"]} "{n["name"]}": focus not shown, '
                                f'{n["changed"]} pixels changed, {n["needed"]} needed')
    # What shotbox couldn't measure (GTK 4's edges, and text it can't find
    # where GTK says it is) passes by default, so say how much there was.
    unmeasured = f", {len(contrast['notes'])} not measured" if contrast["notes"] else ""
    print(f"{label}: " + ("ok" if not problems else f"{len(problems)} problems") + unmeasured)
    for p in problems:
        print(f"  {p}")
    return not problems


if __name__ == "__main__":
    with tempfile.TemporaryDirectory() as home:
        # GTK 3 reads a theme by name, from a home it looks in.
        shutil.copytree(HERE.parent / "themes", Path(home) / ".local/share/themes")
        gtk3 = ["--seed", home, "--env", "GTK_THEME=Neon-Doll{}"]
        runs = [("GTK 4, dark", "preview.py", "preview.py", "", []),
                ("GTK 4, light", "preview.py", "preview.py", "--light", []),
                ("GTK 4, high contrast", "preview.py", "preview.py", "", ["--high-contrast"]),
                ("GTK 3, dark", "preview3.py", "photos", "", [a.format("-dark") for a in gtk3]),
                ("GTK 3, light", "preview3.py", "photos", "", [a.format("") for a in gtk3])]
        results = [check(*run) for run in runs]
    sys.exit(0 if all(results) else 1)
