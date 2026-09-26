#!/usr/bin/env python3
"""Write tokens.toml's colors into the hand-written themes.

    tools/build-palettes.py            write them
    tools/build-palettes.py --check    fail if any is stale

The GTK stylesheets and the Emacs themes are written by hand, but each has
to carry its own copy of the palette. This writes those copies:

    gtk-4.0/gtk.css             between /* palette:begin */ and /* palette:end */,
                                and the old named colors between
                                /* named-colors:begin */ and /* named-colors:end */
    gtk-3.0/_colors-*.css       the whole file
    emacs/neon-doll-*-theme.el  the neon-doll-*-palette list, flattened as for
                                the editor schemes (tools/tokens.py)
"""

import re
import sys
from pathlib import Path

import tokens

ROOT = Path(__file__).resolve().parent.parent
CORE = ("bg", "panel", "line", "ink", "muted", "dimmest", "pink", "purple",
        "code-string", "diff-add", "diff-del")

# Plain GTK 4 apps (no libadwaita) and GTK 3 read these by name.
NAMED = [
    ("accent_bg_color", "pink"), ("accent_fg_color", "bg"), ("accent_color", "pink"),
    ("destructive_bg_color", "diff-del"), ("destructive_fg_color", "bg"),
    ("destructive_color", "diff-del"), ("success_color", "diff-add"),
    ("warning_color", "code-string"), ("error_color", "diff-del"),
    ("window_bg_color", "bg"), ("window_fg_color", "ink"),
    ("view_bg_color", "bg"), ("view_fg_color", "ink"),
    ("headerbar_bg_color", "panel"), ("headerbar_fg_color", "ink"),
    ("headerbar_backdrop_color", "bg"),
    ("sidebar_bg_color", "panel"), ("sidebar_fg_color", "ink"),
    ("card_bg_color", "panel"), ("card_fg_color", "ink"),
    ("popover_bg_color", "panel"), ("popover_fg_color", "ink"),
    ("dialog_bg_color", "bg"), ("dialog_fg_color", "ink"),
]


def values(variant):
    """Every token as CSS: solid colors as hex, tints as rgba()."""
    p = tokens.palette(variant)
    out = [(k, p[k]) for k in CORE]
    out += [(k, tokens.css(variant, k)) for k in tokens.tints(variant)]
    return out


def custom_properties(variant, indent):
    rows = values(variant)
    width = max(len(k) for k, _ in rows) + 3
    return "\n".join(f"{indent}{f'--{k}:':<{width}} {v};" for k, v in rows)


def gtk4_palette():
    return "\n".join([
        ":root {",
        custom_properties("dark", "  "),
        "}",
        "@media (prefers-color-scheme: light) {",
        "  :root {",
        custom_properties("light", "    "),
        "  }",
        "}",
    ])


def gtk4_named():
    dark, light = tokens.palette("dark"), tokens.palette("light")
    out = [f"@define-color {n} {dark[t]};" for n, t in NAMED]
    out.append("@media (prefers-color-scheme: light) {")
    out += [f"  @define-color {n} {light[t]};" for n, t in NAMED]
    out.append("}")
    return "\n".join(out)


def region(text, name, body):
    pattern = re.compile(r"(/\* %s:begin \*/\n).*?(/\* %s:end \*/)" % (name, name), re.S)
    if not pattern.search(text):
        sys.exit(f"no /* {name}:begin */ ... /* {name}:end */ in gtk-4.0/gtk.css")
    return pattern.sub(lambda m: m.group(1) + body + "\n" + m.group(2), text)


def gtk4():
    text = (ROOT / "gtk-4.0" / "gtk.css").read_text()
    text = region(text, "palette", gtk4_palette())
    return region(text, "named-colors", gtk4_named())


GTK3_HEAD = {
    "dark": """/* Neon Doll, dark. The palette of the website design system this theme
   comes from, under its site names and with its site values, plus the
   desktop's own tints of them. Written from tokens.toml by
   tools/build-palettes.py; edit that, not this. Fuchsia is position; purple
   is interactive at rest. */
""",
    "light": """/* Neon Doll, light. The site has no light mode, so this is derived: the page
   becomes paper, still plum-tinted, and fuchsia and purple keep their roles
   but are taken down until they clear 4.5:1 on panel. Written from
   tokens.toml by tools/build-palettes.py; edit that, not this. The names
   match _colors-dark.css one for one. */
""",
}


def gtk3(variant):
    rows = values(variant)
    width = max(len(k) for k, _ in rows)
    body = "\n".join(f"@define-color {k:<{width}} {v};" for k, v in rows)
    return GTK3_HEAD[variant] + "\n" + body + "\n"


ANSI_NAMES = ("black", "red", "green", "yellow", "blue", "magenta", "cyan", "white")
ELISP_KEYS = ("bg", "panel", "line", "ink", "muted", "dimmest", "pink", "purple",
              "string", "add", "del", "wash", "wash-strong", "grid", "press",
              "select", "wash-pink", "edge-purple", "ul-purple", "add-bg",
              "del-bg", "add-bg-hl", "del-bg-hl", "add-refine", "del-refine",
              "change-bg", "bright-red", "bright-green")


def elisp(variant):
    p = tokens.flat(variant)
    rows = ["(%s . \"%s\")" % (k, p[k]) for k in ELISP_KEYS]
    for i, (_, c, _) in enumerate(p["ansi"]):
        name = ("ansi-" if i < 8 else "ansi-bright-") + ANSI_NAMES[i % 8]
        rows.append("(%s . \"%s\")" % (name, c))
    return "  '(" + "\n    ".join(rows) + ")"


def emacs(variant):
    path = ROOT / "emacs" / f"neon-doll-{variant}-theme.el"
    text = path.read_text()
    pattern = re.compile(r"(\(defconst neon-doll-%s-palette\n).*?(\n  \"The Neon Doll)" % variant, re.S)
    if not pattern.search(text):
        sys.exit(f"no neon-doll-{variant}-palette in {path.relative_to(ROOT)}")
    return pattern.sub(lambda m: m.group(1) + elisp(variant) + m.group(2), text)


def outputs():
    yield ROOT / "gtk-4.0" / "gtk.css", gtk4()
    for v in tokens.VARIANTS:
        yield ROOT / "gtk-3.0" / f"_colors-{v}.css", gtk3(v)
        yield ROOT / "emacs" / f"neon-doll-{v}-theme.el", emacs(v)


def main():
    check = "--check" in sys.argv
    stale = []
    for path, text in outputs():
        if check:
            if path.read_text() != text:
                stale.append(path.relative_to(ROOT))
        elif path.read_text() != text:
            path.write_text(text)
            print(path.relative_to(ROOT))
    if stale:
        sys.exit("stale: " + ", ".join(map(str, stale)) + " (run tools/build-palettes.py)")


main()
