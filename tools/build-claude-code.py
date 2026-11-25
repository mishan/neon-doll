#!/usr/bin/env python3
"""Build the Claude Code themes into claude-code/neon-doll-{dark,light}.json.

    tools/build-claude-code.py            write both themes
    tools/build-claude-code.py --check    fail if the output is stale

Claude Code's own colors, over whatever the terminal's background is: the
Neon Doll terminal schemes' for the look on the screenshots. Fuchsia is
where you are (the spinner, Claude's label, the picker's highlighted row);
purple is what you can act on (dialogs, plan mode, links into memory);
diffs, success, errors and warnings are the editor schemes' tints and
colors. Tokens not named here keep the base preset's, the subagents' and
ultrathink's colors included, since those only need to differ from each
other.

The terminal's 16 colors can't carry this: fuchsia isn't one of them. So
the colors are hex, and there's a theme per variant, as Claude Code has no
custom theme that follows light and dark.
"""

import json
import sys
from pathlib import Path

import tokens

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "claude-code"
NAMES = {"dark": "Neon Doll Dark", "light": "Neon Doll Light"}


def overrides(variant):
    f = tokens.flat(variant)
    # Diff rows at 1.6x the editor schemes' tints, as on magit's highlighted
    # hunk: the dimmed rows after a rejected edit keep the plain tint.
    diff = lambda token, k=1.6: tokens.over(f["bg"], *(lambda c, a: (c, a * k))(*tokens.tint(variant, token)))
    # The shimmer is the lighter half of the spinner's sweep: toward ink.
    shimmer = lambda c: tokens.over(c, f["ink"], 0.45)
    return {
        "claude": f["pink"],
        "claudeShimmer": shimmer(f["pink"]),
        "text": f["ink"],
        "inverseText": f["bg"],
        "inactive": f["muted"],
        "inactiveShimmer": shimmer(f["muted"]),
        "subtle": f["edge"],
        "suggestion": f["pink"],
        "permission": f["purple"],
        "permissionShimmer": shimmer(f["purple"]),
        "remember": f["purple"],
        "success": f["add"],
        "error": f["del"],
        "warning": f["string"],
        "warningShimmer": shimmer(f["string"]),
        "merged": f["purple"],
        "promptBorder": f["edge"],
        "promptBorderShimmer": f["muted"],
        "planMode": f["purple"],
        "autoAccept": f["pink"],
        "autoAcceptShimmer": shimmer(f["pink"]),
        "skill": f["purple"],
        "bashBorder": f["pink"],
        "ide": f["purple"],
        "fastMode": f["string"],
        "fastModeShimmer": shimmer(f["string"]),
        "diffAdded": diff("diff-add-bg"),
        "diffRemoved": diff("diff-del-bg"),
        "diffAddedDimmed": f["add-bg"],
        "diffRemovedDimmed": f["del-bg"],
        "diffAddedWord": diff("diff-add-refine"),
        "diffRemovedWord": diff("diff-del-refine"),
        "userMessageBackground": f["panel"],
        "userMessageBackgroundHover": f["wash-strong"],
        "bashMessageBackgroundColor": f["panel"],
        "memoryBackgroundColor": f["panel"],
        "selectionBg": f["select"],
        "composerSidebarBackground": f["panel"],
        "rate_limit_fill": f["pink"],
        "rate_limit_empty": f["line"],
        "briefLabelYou": f["purple"],
        "briefLabelClaude": f["pink"],
        # Not in the docs' list, but in /theme's editor: the mascot on the
        # welcome screen (its eyes dark in both, as Claude Code's own themes
        # draw them), and the spinner while Claude Code works on its own.
        "clawd_body": f["pink"],
        "clawd_background": min(f["bg"], f["ink"], key=tokens.luminance),
        "claudeBlue_FOR_SYSTEM_SPINNER": f["purple"],
        "claudeBlueShimmer_FOR_SYSTEM_SPINNER": shimmer(f["purple"]),
    }


def outputs():
    for variant in tokens.VARIANTS:
        theme = {"name": NAMES[variant], "base": variant, "overrides": overrides(variant)}
        yield OUT / f"neon-doll-{variant}.json", (json.dumps(theme, indent=2) + "\n").encode()


def main():
    check = "--check" in sys.argv
    stale = []
    for path, data in outputs():
        if check:
            if not path.exists() or path.read_bytes() != data:
                stale.append(path.relative_to(ROOT))
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
            print(path.relative_to(ROOT))
    if stale:
        sys.exit("stale: " + ", ".join(map(str, stale)) + " (run tools/build-claude-code.py)")


main()
