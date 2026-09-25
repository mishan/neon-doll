#!/usr/bin/env python3
"""Derive the Neon Doll text-scheme colors and report their contrast.

The GtkSourceView, Tilix and Emacs schemes all take solid colors, because none
of them composites alpha the way a browser does. So every tint here is one of
the site's (or gtk.css's) rgba tokens flattened onto --bg, and every ANSI color
the palette has no token for is derived by a stated rule. The dark and light
variants go through the same rules; only the eight core colors and the three
code colors differ.

    tools/scheme-colors.py            # report both variants
    tools/scheme-colors.py dark       # report one variant
    tools/scheme-colors.py --write    # regenerate gtksourceview/ and tilix/
    tools/scheme-colors.py --elisp    # print the Emacs palettes to paste into
                                      # emacs/neon-doll-*-theme.el

The GtkSourceView and Tilix files are generated from here; the Emacs palettes
are pasted by hand, because the theme files have to stand alone.
"""
import colorsys
import json
import os
import sys

# Dark: the source website's design-system tokens (see gtk-4.0/gtk.css).
# Light: the prefers-color-scheme: light block in gtk-4.0/gtk.css. One
# deliberate departure: gtk.css tints light diff rows at 10%, but in an editor
# the row's text is --diff-add / --diff-del itself, and on paper 10% leaves it
# at 4.3:1. 7% is the most tint that keeps it at 4.5:1. For the same reason
# the light bracket-match field is --wash-pink's own 8%, not the dark 16%.
PALETTES = {
    "dark": {
        "bg": "#0f0d14", "panel": "#16131d", "line": "#2a2438",
        "ink": "#ebe6f0", "muted": "#9c93ab", "dimmest": "#6f6880",
        "pink": "#ff2d95", "purple": "#b48cff",
        "string": "#e5c07b", "add": "#7ee787", "del": "#ff7b72",
        # rgba tokens as (source color, alpha); the diff tints are the site's
        # own, which are not quite --diff-add / --diff-del.
        "_a": {
            "wash": ("purple", 0.06), "wash-strong": ("purple", 0.10),
            "grid": ("purple", 0.09), "press": ("purple", 0.16),
            "edge-purple": ("purple", 0.30),
            "ul-purple": ("purple", 0.35), "select": ("pink", 0.30),
            "wash-pink": ("pink", 0.16),
            "add-bg": ("#3fb950", 0.10), "del-bg": ("#f85149", 0.10),
            "add-refine": ("#3fb950", 0.25), "del-refine": ("#f85149", 0.25),
            "change-bg": ("string", 0.10),
        },
    },
    "light": {
        "bg": "#f7f4fa", "panel": "#ede7f3", "line": "#d6cce2",
        "ink": "#1a1522", "muted": "#5f5670", "dimmest": "#8d84a0",
        "pink": "#c8006a", "purple": "#6a3fd0",
        "string": "#8a6100", "add": "#1f7a33", "del": "#c4312a",
        "_a": {
            "wash": ("purple", 0.05), "wash-strong": ("purple", 0.09),
            "grid": ("purple", 0.07), "press": ("purple", 0.14),
            "edge-purple": ("purple", 0.30),
            "ul-purple": ("purple", 0.40), "select": ("pink", 0.18),
            "wash-pink": ("pink", 0.08),
            "add-bg": ("add", 0.07), "del-bg": ("del", 0.07),
            "add-refine": ("add", 0.20), "del-refine": ("del", 0.20),
            "change-bg": ("string", 0.07),
        },
    },
}


def rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def hexs(c):
    return "#%02x%02x%02x" % tuple(max(0, min(255, round(v))) for v in c)


def over(base, color, alpha):
    """`color` at `alpha` composited over `base`, as a browser would."""
    b, c = rgb(base), rgb(color)
    return hexs([b[i] + (c[i] - b[i]) * alpha for i in range(3)])


def hsl(h, s, l):
    r, g, b = colorsys.hls_to_rgb(h / 360, l, s)
    return hexs((r * 255, g * 255, b * 255))


def hsl_of(c):
    h, l, s = colorsys.rgb_to_hls(*[v / 255 for v in rgb(c)])
    return h * 360, s, l


def luminance(c):
    def ch(v):
        v /= 255
        return v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4
    r, g, b = map(ch, rgb(c))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast(a, b):
    hi, lo = sorted((luminance(a), luminance(b)), reverse=True)
    return (hi + 0.05) / (lo + 0.05)


def derive(name):
    p = dict(PALETTES[name])
    alphas = p.pop("_a")
    for key, (src, a) in alphas.items():
        p[key] = over(p["bg"], p.get(src, src), a)
    # Diff rows under the current-line tint (magit's highlighted hunk): 1.6x
    # the row tint over the wash. Text on these rows takes the bright ANSI
    # variant of its color, which is what keeps it above 4.5:1. Word-level
    # refine tints carry --ink.
    p["add-bg-hl"] = over(p["wash"], p.get(alphas["add-bg"][0], alphas["add-bg"][0]), alphas["add-bg"][1] * 1.6)
    p["del-bg-hl"] = over(p["wash"], p.get(alphas["del-bg"][0], alphas["del-bg"][0]), alphas["del-bg"][1] * 1.6)

    # ANSI. Normal colors reuse palette tokens where one exists. The two hues
    # the site has no token for keep a sibling's saturation and lightness and
    # rotate only the hue, so they sit at the same weight as the rest:
    #   blue = --purple's S and L at hue 228 (a violet-leaning periwinkle)
    #   cyan = --diff-add's S and L at hue 188 (a mint-cyan)
    # Bright variants are the normal color mixed 40% toward --ink: lighter on
    # dark, deeper on light, and plum-tinted either way. Black and white are
    # assigned by role, not by lightness: 0 is --line and 15 is --ink in both
    # variants, so "white" text is always the foreground and never vanishes.
    # Fuchsia is kept out of the sixteen so no program can use it as
    # decoration; it is the cursor.
    _, ps, pl = hsl_of(p["purple"])
    _, as_, al = hsl_of(p["add"])
    blue = hsl(228, ps, pl)
    cyan = hsl(188, as_, al)
    gray = over(p["muted"], p["ink"], 0.5)

    def bright(c):
        return over(c, p["ink"], 0.4)

    p["ansi"] = [
        ("0 black", p["line"], "--line"),
        ("1 red", p["del"], "--diff-del"),
        ("2 green", p["add"], "--diff-add"),
        ("3 yellow", p["string"], "--code-string"),
        ("4 blue", blue, "hsl(228, S and L of --purple)"),
        ("5 magenta", p["purple"], "--purple"),
        ("6 cyan", cyan, "hsl(188, S and L of --diff-add)"),
        ("7 white", gray, "--muted + 50% --ink"),
        ("8 bright black", p["muted"], "--muted"),
        ("9 bright red", bright(p["del"]), "red + 40% --ink"),
        ("10 bright green", bright(p["add"]), "green + 40% --ink"),
        ("11 bright yellow", bright(p["string"]), "yellow + 40% --ink"),
        ("12 bright blue", bright(blue), "blue + 40% --ink"),
        ("13 bright magenta", bright(p["purple"]), "magenta + 40% --ink"),
        ("14 bright cyan", bright(cyan), "cyan + 40% --ink"),
        ("15 bright white", p["ink"], "--ink"),
    ]
    p["bright-red"] = bright(p["del"])
    p["bright-green"] = bright(p["add"])
    return p


def report(name):
    p = derive(name)
    bg = p["bg"]
    print("== %s ==" % name)
    print("Flattened tints over --bg %s" % bg)
    for k in ("wash", "wash-strong", "grid", "press", "select", "wash-pink",
              "ul-purple", "add-bg", "del-bg", "add-bg-hl", "del-bg-hl",
              "add-refine", "del-refine", "change-bg"):
        print("  %-12s %s" % (k, p[k]))

    print("\nText on --bg / on the current-line wash %s" % p["wash"])
    for k in ("ink", "pink", "string", "muted", "purple", "dimmest", "add", "del"):
        print("  %-8s %s  %5.2f  %5.2f" % (k, p[k], contrast(p[k], bg), contrast(p[k], p["wash"])))

    print("\nOn tinted rows")
    for label, fg, b in [
        ("ink on selection", "ink", "select"), ("pink on selection", "pink", "select"),
        ("ink on press", "ink", "press"), ("pink on wash-pink", "pink", "wash-pink"),
        ("add on add-bg", "add", "add-bg"), ("del on del-bg", "del", "del-bg"),
        ("string on change-bg", "string", "change-bg"),
        ("bright green on add-bg-hl", "bright-green", "add-bg-hl"),
        ("bright red on del-bg-hl", "bright-red", "del-bg-hl"),
        ("ink on add-refine", "ink", "add-refine"),
        ("ink on del-refine", "ink", "del-refine"),
        ("bg on pink", "bg", "pink"), ("pink on panel", "pink", "panel"),
        ("ink on panel", "ink", "panel"), ("muted on panel", "muted", "panel"),
    ]:
        print("  %-26s %5.2f" % (label, contrast(p[fg], p[b])))

    print("\nANSI palette, contrast on --bg %s" % bg)
    for label, c, how in p["ansi"]:
        r = contrast(c, bg)
        flag = "" if r >= 4.5 or label.startswith("0 ") else "   < 4.5"
        print("  %-18s %s  %5.2f:1  %s%s" % (label, c, r, how, flag))
    print("  %-18s %s  %5.2f:1  --pink, not in the sixteen"
          % ("cursor", p["pink"], contrast(p["pink"], bg)))
    print()


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Colors named in the GtkSourceView scheme, in this order.
GSV_COLORS = ("bg", "panel", "line", "ink", "muted", "dimmest", "pink", "purple",
              "string", "add", "del", "wash", "wash-strong", "grid", "press",
              "select", "wash-pink", "edge-purple", "add-bg", "del-bg",
              "change-bg")

GSV_TEMPLATE = """<?xml version="1.0" encoding="UTF-8"?>
<!--
  Neon Doll {Title}: a GtkSourceView style scheme (GNOME Text Editor, gedit,
  Builder and anything else built on GtkSourceView).

  Copyright (C) 2026 Misha Nasledov <misha@nasledov.com>
  SPDX-License-Identifier: GPL-3.0-or-later
  This scheme is free software under the GNU General Public License, version 3
  or (at your option) any later version. It comes with NO WARRANTY. See COPYING.

  Generated by tools/scheme-colors.py; edit that, not this.

  The editor is the page, so the text area is bg rather than the site's
  code-block field; that field (wash) becomes the current line instead.

  Four syntax colors and no more. Every extra class folds onto one of them:
    pink    keywords, statements, preprocessor, tags, attributes and macros
    purple  numbers, constants, booleans, types, builtins, escapes,
            variables with a sigil ($var), link text
    string  strings and characters
    muted   comments (italic), doc comments, shebangs
    ink     identifiers, functions, operators: everything else
  Fuchsia is also position: the cursor, the current line number, the matching
  bracket and the selection (which is where the search match under the cursor
  lands). Purple is the resting state: other search matches, the secondary
  cursor, links. Diff rows carry both a text color and a full-width tint.
-->
<style-scheme id="neon-doll-{variant}" name="Neon Doll {Title}" version="1.0">
  <author>Misha Nasledov</author>
  <description>{description}</description>
  <metadata>
    <property name="variant">{variant}</property>
    <property name="{other}-variant">neon-doll-{other}</property>
  </metadata>

{colors}

  <!-- Global -->
  <style name="text"                  foreground="ink" background="bg"/>
  <style name="selection"             foreground="ink" background="select"/>
  <style name="selection-unfocused"   foreground="ink" background="press"/>
  <style name="cursor"                foreground="pink"/>
  <style name="secondary-cursor"      foreground="purple"/>
  <style name="current-line"          background="wash"/>
  <style name="line-numbers"          foreground="dimmest" background="bg"/>
  <style name="current-line-number"   foreground="pink" background="wash"/>
  <style name="line-numbers-border"   background="edge-purple"/>
  <style name="right-margin"          foreground="line" background="line"/>
  <style name="draw-spaces"           foreground="dimmest"/>
  <style name="background-pattern"    background="grid"/>
  <style name="bracket-match"         foreground="pink" background="wash-pink"/>
  <style name="bracket-mismatch"      foreground="del" background="del-bg" underline="single"/>
  <style name="search-match"          foreground="ink" background="press"/>
  <style name="snippet-focus"         background="wash-pink"/>
  <style name="map-overlay"           background="{map_overlay}"/>

  <!-- Comments -->
  <style name="def:comment"              foreground="muted" italic="true"/>
  <style name="def:shebang"              foreground="muted" italic="true"/>
  <style name="def:doc-comment"          foreground="muted" italic="true"/>
  <style name="def:doc-comment-element"  foreground="purple" italic="true"/>

  <!-- Constants -->
  <style name="def:constant"             foreground="purple"/>
  <style name="def:special-constant"     foreground="purple"/>
  <style name="def:boolean"              foreground="purple"/>
  <style name="def:number"               foreground="purple"/>
  <style name="def:decimal"              foreground="purple"/>
  <style name="def:base-n-integer"       foreground="purple"/>
  <style name="def:floating-point"       foreground="purple"/>
  <style name="def:complex"              foreground="purple"/>
  <style name="def:character"            foreground="string"/>
  <style name="def:string"               foreground="string"/>
  <style name="def:special-char"         foreground="purple"/>

  <!-- Code -->
  <style name="def:keyword"              foreground="pink"/>
  <style name="def:statement"            foreground="pink"/>
  <style name="def:preprocessor"         foreground="pink"/>
  <style name="def:type"                 foreground="purple"/>
  <style name="def:identifier"           foreground="ink"/>
  <style name="def:function"             foreground="ink"/>
  <style name="def:builtin"              foreground="purple"/>
  <style name="def:operator"             foreground="ink"/>

  <!-- Diagnostics -->
  <style name="def:error"                underline="error" underline-color="del"/>
  <style name="def:warning"              underline="error" underline-color="string"/>
  <style name="def:note"                 foreground="string" italic="true"/>
  <style name="def:underlined"           underline="single"/>

  <!-- Markup. Headings are mono and weight 400, as on the site. -->
  <style name="def:heading"              foreground="ink"/>
  <style name="def:emphasis"             italic="true"/>
  <style name="def:strong-emphasis"      bold="true"/>
  <style name="def:inline-code"          foreground="ink" background="wash-strong"/>
  <style name="def:preformatted-section" foreground="ink" background="wash"/>
  <style name="def:list-marker"          foreground="muted"/>
  <style name="def:thematic-break"       foreground="muted"/>
  <style name="def:link-text"            foreground="purple"/>
  <style name="def:link-symbol"          foreground="muted"/>
  <style name="def:link-destination"     foreground="muted" underline="single"/>
  <style name="def:net-address"          foreground="purple" underline="single"/>
  <style name="def:insertion"            foreground="add"/>
  <style name="def:deletion"             foreground="del" strikethrough="true"/>

  <!-- Diff: text color and a full-width row tint, and the +/- stays. -->
  <style name="diff:added-line"          foreground="add" line-background="add-bg"/>
  <style name="diff:removed-line"        foreground="del" line-background="del-bg"/>
  <style name="diff:changed-line"        foreground="string" line-background="change-bg"/>
  <style name="diff:location"            foreground="purple"/>
  <style name="diff:diff-file"           foreground="muted"/>
  <style name="diff:special-case"        foreground="muted"/>

  <!-- A variable with a sigil is purple, as $slot is on the site. -->
  <style name="php:variable"             foreground="purple"/>
  <style name="sh:variable"              foreground="purple"/>
  <style name="perl:variable"            foreground="purple"/>
  <style name="ruby:instance-variable"   foreground="purple"/>

  <!-- Markup tags are keywords; attributes are keys. -->
  <style name="xml:element-name"         foreground="pink"/>
  <style name="xml:attribute-name"       foreground="purple"/>
  <style name="xml:attribute-value"      foreground="string"/>
  <style name="xml:namespace"            foreground="purple"/>
  <style name="xml:processing-instruction" foreground="pink"/>
  <style name="css:property-name"        foreground="purple"/>
  <style name="css:vendor-specific"      foreground="purple"/>

  <!-- Language odds and ends, folded onto the four. -->
  <style name="c:printf"                 foreground="purple"/>
  <style name="rust:macro"               foreground="pink"/>
  <style name="rust:attribute"           foreground="pink"/>
  <style name="rust:lifetime"            foreground="purple"/>
  <style name="python:decorator"         foreground="pink"/>
  <style name="json:keyname"             foreground="purple"/>
</style-scheme>
"""


def gsv(variant):
    p = derive(variant)
    other = "light" if variant == "dark" else "dark"
    colors = "\n".join('  <color name="%s"%s value="%s"/>'
                       % (k, " " * (12 - len(k)), p[k]) for k in GSV_COLORS)
    desc = ("A dark plum page, fuchsia for position, purple for the rest."
            if variant == "dark" else
            "Plum-tinted paper, fuchsia for position, purple for the rest.")
    # Text Editor drops the alpha on the map slider, so it gets the tint
    # already composited over the page.
    return GSV_TEMPLATE.format(Title=variant.title(), variant=variant, other=other,
                               description=desc, colors=colors,
                               map_overlay=over(p["bg"], p["pink"], 0.10))


def gsv4(variant):
    """GtkSourceView 4 (gedit, older apps) rejects the whole file on an
    unknown <metadata> node, so its copy goes without; nothing else differs."""
    text = gsv(variant)
    start, end = text.index("  <metadata>"), text.index("</metadata>\n") + len("</metadata>\n")
    return text[:start] + text[end:]


def tilix(variant):
    p = derive(variant)
    return json.dumps({
        "name": "Neon Doll %s" % variant.title(),
        "comment": "Fuchsia is the cursor and nothing else",
        "use-theme-colors": False,
        "foreground-color": p["ink"],
        "background-color": p["bg"],
        "use-cursor-color": True,
        "cursor-background-color": p["pink"],
        "cursor-foreground-color": p["bg"],
        "use-highlight-color": True,
        "highlight-background-color": p["select"],
        "highlight-foreground-color": p["ink"],
        "use-badge-color": True,
        "badge-color": p["muted"],
        "use-bold-color": True,
        "bold-color": p["ink"],
        "palette": [c for _, c, _ in p["ansi"]],
    }, indent=4) + "\n"


ELISP_KEYS = ("bg", "panel", "line", "ink", "muted", "dimmest", "pink", "purple",
              "string", "add", "del", "wash", "wash-strong", "grid", "press",
              "select", "wash-pink", "edge-purple", "ul-purple", "add-bg",
              "del-bg", "add-bg-hl", "del-bg-hl", "add-refine", "del-refine",
              "change-bg", "bright-red", "bright-green")
ANSI_NAMES = ("black", "red", "green", "yellow", "blue", "magenta", "cyan", "white")


def elisp(variant):
    p = derive(variant)
    rows = ["(%s . \"%s\")" % (k, p[k]) for k in ELISP_KEYS]
    for i, (_, c, _) in enumerate(p["ansi"]):
        name = ("ansi-" if i < 8 else "ansi-bright-") + ANSI_NAMES[i % 8]
        rows.append("(%s . \"%s\")" % (name, c))
    return "  '(" + "\n    ".join(rows) + ")"


def write(path, text):
    full = os.path.join(ROOT, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w") as f:
        f.write(text)
    print("wrote", path)


if __name__ == "__main__":
    args = sys.argv[1:]
    if args == ["--write"]:
        for v in ("dark", "light"):
            write("gtksourceview/neon-doll-%s.xml" % v, gsv(v))
            write("gtksourceview/gtksourceview-4/neon-doll-%s.xml" % v, gsv4(v))
            write("tilix/neon-doll-%s.json" % v, tilix(v))
    elif args == ["--elisp"]:
        for v in ("dark", "light"):
            print(";; %s\n%s\n" % (v, elisp(v)))
    else:
        for n in args or ("dark", "light"):
            report(n)
