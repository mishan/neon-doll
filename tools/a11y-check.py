#!/usr/bin/env python3
"""Check the GTK 4 theme as a screen reader and a low-vision reader meet it,
on tools/preview.py in a sealed session: every control named, text and
control edges above WCAG's floors as drawn on the screen, and the focus
seen at every stop. Dark, light and high contrast.

    tools/a11y-check.py

Needs shotbox 0.4.2 or later on PATH. tools/scheme-colors.py checks the same
floors on the palette; this checks them on the pixels.
"""

import json
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
    ("button", "Minimize"): "window controls are flat",
    ("button", "Maximize"): "window controls are flat",
    ("button", "Close"): "window controls are flat",
    ("button", "Dismiss"): "a toast's close button is flat",
    ("button", "Close Tab"): "a tab's close button is flat, and drawn only on hover",
    ("text", "Display name"): "a row's edge is its boxed list's",
    ("combo box", "Theme"): "a row's edge is its boxed list's",
    ("text", "notes"): "a text view's edge is its frame's",
}
# libadwaita's tab bar scrolls its tabs in a scroll pane it doesn't name.
LINT_IGNORE = "focusable scroll pane with no name"

INSIDE = """
"$PREVIEW" $PREVIEW_ARGS >/dev/null 2>&1 &
shotbox wait window preview.py >/dev/null && shotbox wait stable >/dev/null
shotbox a11y lint --window preview.py --ignore "$LINT_IGNORE" > "$OUT/lint.txt"
echo $? > "$OUT/lint.status"
shotbox a11y contrast --edges 3 --window preview.py --json > "$OUT/contrast.json"
shotbox a11y tabwalk --visible --key ctrl+Tab --window preview.py --json > "$OUT/walk.json"
true
"""


def check(label, preview_args, session_args):
    with tempfile.TemporaryDirectory() as out:
        subprocess.run(
            ["shotbox", "run", "--a11y", "--screen", "1240x1040", *session_args,
             "--env", f"PREVIEW={HERE / 'preview.py'}", "--env", f"PREVIEW_ARGS={preview_args}",
             "--env", f"OUT={out}", "--env", f"LINT_IGNORE={LINT_IGNORE}",
             "--", "sh", "-c", INSIDE],
            check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        out = Path(out)
        problems = []
        if (out / "lint.status").read_text().strip() != "0":
            problems += [f"lint: {line}" for line in (out / "lint.txt").read_text().splitlines()]
        for n in json.loads((out / "contrast.json").read_text()):
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
    print(f"{label}: " + ("ok" if not problems else f"{len(problems)} problems"))
    for p in problems:
        print(f"  {p}")
    return not problems


if __name__ == "__main__":
    runs = [("dark", "", []), ("light", "--light", []),
            ("high contrast", "", ["--high-contrast"])]
    results = [check(*run) for run in runs]
    sys.exit(0 if all(results) else 1)
