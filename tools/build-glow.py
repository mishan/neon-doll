#!/usr/bin/env python3
"""Build the glow (glamour) styles into glow/neon-doll-{dark,light}.json.

    tools/build-glow.py            write both styles
    tools/build-glow.py --check    fail if the output is stale

Markdown rendered as a man page: h1 and h2 in capitals like a man page's
section names, headings purple, links purple over a muted URL, block quotes
behind a muted rule, nothing bold but **strong** (the one exception the site
makes too).

Everything outside code blocks names the 16 terminal colors, like the ls and
git colors, so it follows the terminal scheme. Code blocks can't: glamour hands
them to chroma, which takes hex only. So there are two files, differing only
in their code colors, which match the editor schemes: fuchsia keywords, purple
numbers, yellow strings, muted italic comments.
"""

import json
import sys
from pathlib import Path

import tokens

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "glow"

PALETTES = {
    v: {k: tokens.palette(v)[k] for k in ("ink", "muted", "pink", "purple", "string", "add", "del")}
    for v in tokens.VARIANTS
}

# ANSI indices, as in the Tilix schemes: 0 the border color, 1 red, 2 green,
# 3 yellow, 4 blue, 5 purple, 8 muted.
BASE = {
    "document": {"block_prefix": "\n", "block_suffix": "\n", "margin": 2},
    "block_quote": {"indent": 1, "indent_token": "│ ", "color": "8"},
    "paragraph": {},
    "list": {"level_indent": 2},
    "heading": {"block_suffix": "\n", "color": "5"},
    "h1": {"upper": True},
    "h2": {"upper": True},
    "h3": {},
    "h4": {"color": "8"},
    "h5": {"color": "8"},
    "h6": {"color": "8"},
    "text": {},
    "strikethrough": {"crossed_out": True},
    "emph": {"italic": True},
    "strong": {"bold": True},
    "hr": {"color": "8", "format": "\n" + "─" * 32 + "\n"},
    "item": {"block_prefix": "- "},
    "enumeration": {"block_prefix": ". "},
    "task": {"ticked": "[x] ", "unticked": "[ ] "},
    "link": {"color": "8", "underline": True},
    "link_text": {"color": "5"},
    "image": {"color": "8", "underline": True},
    "image_text": {"color": "4", "format": "image: {{.text}} →"},
    # Inline code on the border color, the nearest the terminal has to the
    # site's faint code field.
    "code": {"prefix": " ", "suffix": " ", "background_color": "0"},
    "table": {"center_separator": "┼", "column_separator": "│", "row_separator": "─"},
    "definition_list": {},
    "definition_term": {"color": "5"},
    "definition_description": {"block_prefix": "\n  "},
    "html_block": {"color": "8"},
    "html_span": {"color": "8"},
}


def chroma(p):
    c = lambda color, **kw: {"color": color, **kw}
    return {
        "text": c(p["ink"]),
        "error": c(p["del"]),
        "comment": c(p["muted"], italic=True),
        "comment_preproc": c(p["pink"]),
        "keyword": c(p["pink"]),
        "keyword_reserved": c(p["pink"]),
        "keyword_namespace": c(p["pink"]),
        "keyword_type": c(p["purple"]),
        "operator": c(p["ink"]),
        "punctuation": c(p["ink"]),
        "name": c(p["ink"]),
        "name_builtin": c(p["purple"]),
        "name_tag": c(p["pink"]),
        "name_attribute": c(p["string"]),
        "name_class": c(p["ink"]),
        "name_constant": c(p["purple"]),
        "name_decorator": c(p["pink"]),
        "name_exception": c(p["del"]),
        "name_function": c(p["ink"]),
        "name_other": c(p["ink"]),
        "literal": c(p["ink"]),
        "literal_number": c(p["purple"]),
        "literal_date": c(p["string"]),
        "literal_string": c(p["string"]),
        "literal_string_escape": c(p["purple"]),
        "generic_deleted": c(p["del"]),
        "generic_emph": {"italic": True},
        "generic_inserted": c(p["add"]),
        "generic_strong": {"bold": True},
        "generic_subheading": c(p["purple"]),
    }


def outputs():
    for variant, p in PALETTES.items():
        style = json.loads(json.dumps(BASE))
        style["code_block"] = {"margin": 2, "chroma": chroma(p)}
        text = json.dumps(style, indent=2, ensure_ascii=False) + "\n"
        yield OUT / f"neon-doll-{variant}.json", text.encode()


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
        sys.exit("stale: " + ", ".join(map(str, stale)) + " (run tools/build-glow.py)")


main()
