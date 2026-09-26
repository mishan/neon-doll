#!/usr/bin/env python3
"""Build vim/colors/neon-doll.vim from the editor schemes' colors.

    tools/build-vim.py            write vim/colors/neon-doll.vim
    tools/build-vim.py --check    fail if the output is stale

One colorscheme, both variants: it follows 'background', so `set
background=light` switches to Neon Doll Light. With 'termguicolors' it uses
the exact colors; without, it names the 16 terminal colors and follows the
terminal's Neon Doll scheme, like the ls and git colors. The one thing the
16 colors can't say is fuchsia, which the terminal palette leaves out; there
keywords and the cursor's line number fall back to the lighter purple. (Not
reverse video: with 'termguicolors' Vim applies the cterm attributes too.)

The colors are read from gtksourceview/neon-doll-{dark,light}.xml, so vim
matches Text Editor and the other editors: fuchsia keywords, purple numbers,
constants and types, yellow strings, muted italic comments; fuchsia for
position (the cursor's line number, the matching bracket, the current search
match, the selected menu item, the current tab).
"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "vim" / "colors" / "neon-doll.vim"

NONE = None


def palette(variant):
    xml = (ROOT / "gtksourceview" / f"neon-doll-{variant}.xml").read_text()
    return dict(re.findall(r'<color name="([a-z-]+)"\s+value="(#[0-9a-f]{6})"', xml))


# group: (gui fg, gui bg, cterm fg, cterm bg, attrs), colors by palette name.
# cterm numbers are the Neon Doll terminal palette: 0 border, 1 red, 2 green,
# 3 yellow, 4 blue, 5 purple, 6 cyan, 7 soft ink, 8 muted, 13 light purple.
GROUPS = {
    "Normal":       ("ink", "bg", NONE, NONE, ""),
    "NonText":      ("dimmest", NONE, 8, NONE, ""),
    "EndOfBuffer":  ("line", NONE, 0, NONE, ""),
    "SpecialKey":   ("dimmest", NONE, 8, NONE, ""),
    "Whitespace":   ("line", NONE, 0, NONE, ""),
    "LineNr":       ("dimmest", NONE, 8, NONE, ""),
    "CursorLineNr": ("pink", "wash", 13, NONE, ""),
    "CursorLine":   (NONE, "wash", NONE, NONE, ""),
    "CursorColumn": (NONE, "wash", NONE, NONE, ""),
    "ColorColumn":  (NONE, "wash", NONE, 0, ""),
    "SignColumn":   ("muted", NONE, 8, NONE, ""),
    "FoldColumn":   ("dimmest", NONE, 8, NONE, ""),
    "Folded":       ("muted", "wash", 8, NONE, "italic"),
    "WinSeparator": ("line", NONE, 0, NONE, ""),
    "VertSplit":    ("line", NONE, 0, NONE, ""),
    "StatusLine":   ("ink", "panel", NONE, 0, ""),
    "StatusLineNC": ("muted", "bg", 8, NONE, ""),
    "StatusLineTerm":   ("ink", "panel", NONE, 0, ""),
    "StatusLineTermNC": ("muted", "bg", 8, NONE, ""),
    "TabLine":      ("muted", "panel", 8, 0, ""),
    "TabLineFill":  (NONE, "bg", NONE, NONE, ""),
    "TabLineSel":   ("pink", "bg", 5, NONE, ""),
    "Pmenu":        ("ink", "panel", NONE, 0, ""),
    "PmenuSel":     ("pink", "wash-pink", 0, 5, ""),
    "PmenuSbar":    (NONE, "panel", NONE, 0, ""),
    "PmenuThumb":   (NONE, "dimmest", NONE, 8, ""),
    "WildMenu":     ("pink", "wash-pink", 0, 5, ""),
    "Visual":       (NONE, "select", NONE, 0, ""),
    "VisualNOS":    (NONE, "select", NONE, 0, ""),
    "Search":       ("bg", "purple", 0, 5, ""),
    "CurSearch":    ("bg", "pink", 0, 13, ""),
    "IncSearch":    ("bg", "pink", 0, 13, ""),
    "MatchParen":   ("pink", "wash-pink", 5, NONE, "underline"),
    "QuickFixLine": (NONE, "wash-pink", NONE, 0, ""),
    "Title":        ("purple", NONE, 5, NONE, ""),
    "Directory":    ("purple", NONE, 5, NONE, ""),
    "Question":     ("purple", NONE, 5, NONE, ""),
    "MoreMsg":      ("purple", NONE, 5, NONE, ""),
    "ModeMsg":      ("muted", NONE, 8, NONE, ""),
    "ErrorMsg":     ("del", NONE, 1, NONE, ""),
    "WarningMsg":   ("string", NONE, 3, NONE, ""),
    "Cursor":       ("bg", "pink", NONE, NONE, ""),
    "lCursor":      ("bg", "pink", NONE, NONE, ""),
    "SpellBad":     (NONE, NONE, 1, NONE, "undercurl:del"),
    "SpellCap":     (NONE, NONE, 3, NONE, "undercurl:string"),
    "SpellRare":    (NONE, NONE, 5, NONE, "undercurl:purple"),
    "SpellLocal":   (NONE, NONE, 6, NONE, "undercurl:muted"),
    "DiffAdd":      ("add", "add-bg", 2, NONE, ""),
    "DiffDelete":   ("del", "del-bg", 1, NONE, ""),
    "DiffChange":   (NONE, "change-bg", NONE, NONE, ""),
    "DiffText":     ("string", "change-bg", 3, NONE, "underline"),
    # Syntax
    "Comment":      ("muted", NONE, 8, NONE, "italic"),
    "Constant":     ("purple", NONE, 5, NONE, ""),
    "String":       ("string", NONE, 3, NONE, ""),
    "Character":    ("string", NONE, 3, NONE, ""),
    "Number":       ("purple", NONE, 5, NONE, ""),
    "Boolean":      ("purple", NONE, 5, NONE, ""),
    "Float":        ("purple", NONE, 5, NONE, ""),
    "Identifier":   ("ink", NONE, NONE, NONE, ""),
    "Function":     ("ink", NONE, NONE, NONE, ""),
    "Statement":    ("pink", NONE, 13, NONE, ""),
    "Operator":     ("ink", NONE, NONE, NONE, ""),
    "PreProc":      ("pink", NONE, 13, NONE, ""),
    "Type":         ("purple", NONE, 5, NONE, ""),
    "Special":      ("purple", NONE, 5, NONE, ""),
    "Delimiter":    ("ink", NONE, NONE, NONE, ""),
    "Underlined":   ("purple", NONE, 5, NONE, "underline"),
    "Ignore":       ("dimmest", NONE, 8, NONE, ""),
    "Error":        ("del", "del-bg", 1, NONE, ""),
    "Todo":         ("string", NONE, 3, NONE, "italic"),
    "Added":        ("add", NONE, 2, NONE, ""),
    "Removed":      ("del", NONE, 1, NONE, ""),
    "Changed":      ("string", NONE, 3, NONE, ""),
}

LINKS = {
    "diffAdded": "Added", "diffRemoved": "Removed", "diffChanged": "Changed",
    "diffLine": "Title", "diffFile": "Comment", "diffIndexLine": "Comment",
    "diffSubname": "Comment", "helpHyperTextJump": "Underlined",
    "helpOption": "Constant", "gitcommitSummary": "Normal",
    "Terminal": "Normal", "ToolbarLine": "TabLineFill", "ToolbarButton": "TabLine",
}


def hi(group, spec, p):
    fg, bg, cfg, cbg, attrs = spec
    parts = [f"hi {group}"]
    parts.append(f"guifg={p[fg]}" if fg else "guifg=NONE")
    parts.append(f"guibg={p[bg]}" if bg else "guibg=NONE")
    parts.append(f"ctermfg={cfg}" if cfg is not None else "ctermfg=NONE")
    parts.append(f"ctermbg={cbg}" if cbg is not None else "ctermbg=NONE")
    gui, cterm, sp = "NONE", "NONE", None
    if attrs.startswith("undercurl:"):
        gui, cterm, sp = "undercurl", "underline", attrs.split(":")[1]
    elif attrs:
        gui = cterm = attrs
    parts += [f"gui={gui}", f"cterm={cterm}"]
    if sp:
        parts.append(f"guisp={p[sp]}")
    return " ".join(parts)


def render():
    dark, light = palette("dark"), palette("light")
    out = [
        '" Neon Doll: hot pink neon on midnight plum.',
        '" Generated by tools/build-vim.py; edit that, not this.',
        '" Follows \'background\'. Exact colors with \'termguicolors\', the 16',
        '" terminal colors (and so the terminal\'s Neon Doll scheme) without.',
        "",
        "hi clear",
        "if exists('syntax_on') | syntax reset | endif",
        "let g:colors_name = 'neon-doll'",
        "",
    ]
    for name, p in (("light", light), ("dark", dark)):
        out.append(("if" if name == "light" else "else") + (" &background ==# 'light'" if name == "light" else ""))
        out += ["  " + hi(g, s, p) for g, s in GROUPS.items()]
    out.append("endif")
    out.append("")
    out += [f"hi! link {a} {b}" for a, b in LINKS.items()]
    out += [
        "",
        "\" The integrated terminal, :terminal, in the Neon Doll palette.",
        "if &background ==# 'light'",
        f"  let g:terminal_ansi_colors = {terminal('light')}",
        "else",
        f"  let g:terminal_ansi_colors = {terminal('dark')}",
        "endif",
    ]
    return "\n".join(out) + "\n"


def terminal(variant):
    import json
    t = json.loads((ROOT / "tilix" / f"neon-doll-{variant}.json").read_text())
    return "[" + ", ".join(f"'{c}'" for c in t["palette"]) + "]"


def main():
    data = render().encode()
    if "--check" in sys.argv:
        if not OUT.exists() or OUT.read_bytes() != data:
            sys.exit("stale: vim/colors/neon-doll.vim (run tools/build-vim.py)")
        return
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_bytes(data)
    print(OUT.relative_to(ROOT))


main()
