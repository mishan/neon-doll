#!/usr/bin/env python3
"""Build the irssi themes from the editor schemes' colors.

    tools/build-irssi.py            write irssi/neon-doll{,-light}.theme
    tools/build-irssi.py --check    fail if the output is stale

Two themes, neon-doll (dark) and neon-doll-light, in the exact colors, read
from gtksourceview/neon-doll-{dark,light}.xml. Irssi sends them as 24-bit
color with `/set colors_ansi_24bit on`; without it, it picks the nearest of
the 256 colors, which is close but not exact.

What's where, by the site's rules: the prompt, which names the window you're
typing into, is fuchsia, since that's where you are, like the working
directory in the bash prompt. You are purple, like user@host there: your own
nick and your own messages to others. Channel names are purple too, as things
you'd /join. Lines that mention you, and the windows holding them, are yellow;
new messages elsewhere are ink; everything the server says about itself
(timestamps, brackets, hostmasks, joins and parts) steps back into the muted
greys. The status bars sit on the panel color, like the other editors'.
"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "irssi"

VARIANTS = {"dark": "neon-doll.theme", "light": "neon-doll-light.theme"}


def palette(variant):
    xml = (ROOT / "gtksourceview" / f"neon-doll-{variant}.xml").read_text()
    return dict(re.findall(r'<color name="([a-z-]+)"\s+value="#([0-9a-f]{6})"', xml))


# {name} is a foreground color and {bg:name} a background, by palette name.
# $0, $1-, %n, %_ (bold) and %| (indent here) are irssi's own.
ABSTRACTS = [
    # Every info line starts with this; the server talking, so it's quiet.
    ("line_start", "{dimmest}-{muted}!{dimmest}-%n "),
    ("timestamp", "{dimmest}$*%n"),
    ("hilight", "%_$*%_"),
    ("error", "{del}$*%n"),
    ("channel", "{purple}$*%n"),
    ("nick", "%_$*%_"),
    ("nickhost", "{dimmest}[$*{dimmest}]%n"),
    ("server", "%_$*%_"),
    ("comment", "{dimmest}[{muted}$*{dimmest}]%n"),
    ("reason", "{comment $*}"),
    ("mode", "{comment $*}"),
    # Joins in green, as something added; the rest of the traffic muted.
    ("channick_hilight", "{add}$*%n"),
    ("chanhost_hilight", "{nickhost {dimmest}$*}"),
    ("channick", "{muted}$*%n"),
    ("chanhost", "{nickhost {dimmest}$*}"),
    ("channelhilight", "{purple}$*%n"),
    ("ban", "{muted}$*%n"),
    # <@nick> with the brackets stepped back and the mode character muted.
    ("msgnick", "{dimmest}<{muted}$0%n$1-{dimmest}>%n %|"),
    ("ownmsgnick", "{msgnick $0 $1-}"),
    ("ownnick", "{purple}$*%n"),
    ("pubmsgnick", "{msgnick $0 $1-}"),
    ("pubnick", "$*"),
    # Someone said your nick: their nick in yellow, the line left alone.
    ("pubmsgmenick", "{msgnick $0 $1-}"),
    ("menick", "{string}%_$*%_%n"),
    ("pubmsghinick", "{msgnick $1 $0$2-%n}"),
    ("msgchannel", "{dimmest}:{purple}$*%n"),
    ("privmsg", "{dimmest}[{string}$0{dimmest}({muted}$1-{dimmest})%n] "),
    ("ownprivmsg", "{dimmest}[{purple}$0{dimmest}({muted}$1-{dimmest})%n] "),
    ("ownprivmsgnick", "{msgnick  $*}"),
    ("ownprivnick", "{purple}$*%n"),
    ("privmsgnick", "{msgnick  $*}"),
    # /me: a purple star, then the nick in bold.
    ("action_core", "{purple}*%n %_$*%_"),
    ("action", "{action_core $*} "),
    ("ownaction", "{purple}*%n {purple}$*%n "),
    ("ownaction_target", "{action_core $0}{dimmest}:{purple}$1%n "),
    ("pvtaction", "{purple}(*)%n %_$*%_ "),
    ("pvtaction_query", "{action $*}"),
    ("pubaction", "{action $*}"),
    ("whois", "%# {muted}$[8]0%n {dimmest}:%n $1-"),
    ("ownnotice", "{dimmest}[{purple}$0{dimmest}({muted}$1-{dimmest})]%n "),
    ("notice", "{dimmest}-{muted}$*{dimmest}-%n "),
    ("pubnotice_channel", "{dimmest}:{purple}$*"),
    ("pvtnotice_host", "{dimmest}({muted}$*{dimmest})"),
    ("servernotice", "{muted}!$*%n "),
    ("ownctcp", "{dimmest}[{purple}$0{dimmest}({muted}$1-{dimmest})]%n "),
    ("ctcp", "{muted}$*%n"),
    ("wallop", "%_$*%_: "),
    ("wallop_nick", "%n$*"),
    ("wallop_action", "{purple}*%n %_$*%_ "),
    ("netsplit", "{del}$*%n"),
    ("netjoin", "{add}$*%n"),
    ("names_prefix", ""),
    ("names_nick", "{dimmest}[{muted}$0%n$1-{dimmest}]%n "),
    ("names_nick_op", "{names_nick $*}"),
    ("names_nick_halfop", "{names_nick $*}"),
    ("names_nick_voice", "{names_nick $*}"),
    ("names_users", "{dimmest}[{muted}$*{dimmest}]%n"),
    ("names_channel", "{purple}$*%n"),
    ("dcc", "{muted}$*%n"),
    ("dccfile", "%_$*%_"),
    ("dccownmsg", "{dimmest}[{purple}$0{dimmest}({muted}$1-{dimmest})%n] "),
    ("dccownnick", "{purple}$*%n"),
    ("dccownquerynick", "{purple}$*%n"),
    ("dccownaction", "{action $*}"),
    ("dccownaction_target", "{action_core $0}{dimmest}:{purple}$1%n "),
    ("dccmsg", "{dimmest}[{string}$1-{dimmest}({muted}$0{dimmest})%n] "),
    ("dccquerynick", "{string}$*%n"),
    ("dccaction", "{purple}(*dcc*)%n %_$*%_ %|"),
    # Status bars on the panel, in ink; %n inside a bar goes back to this.
    ("sb_background", "{bg:panel}{ink}"),
    ("sb_topic_bg", "{bg:panel}{ink}"),
    ("window_border", "{bg:panel}{line}"),
    ("sb_prompt_bg", "%n"),
    ("sb_info_bg", "{bg:panel}{ink}"),
    ("sbstart", ""),
    ("sbend", " "),
    ("topicsbstart", "{sbstart $*}"),
    ("topicsbend", "{sbend $*}"),
    # The prompt names the window you're typing into: where you are.
    ("prompt", "{dimmest}[{pink}$*{dimmest}]%n "),
    ("sb", " {dimmest}[%n$*{dimmest}]%n"),
    ("sbmode", "{dimmest}({purple}+%n$*{dimmest})%n"),
    ("sbaway", " {dimmest}({muted}zZzZ{dimmest})%n"),
    ("sbservertag", "{dimmest}:%n$0 {muted}(change with ^X)%n"),
    ("sbnickmode", "{muted}$0%n"),
    # Act: windows with news. Quiet chatter muted, messages ink, you yellow.
    ("sb_act_sep", "{dimmest}$*"),
    ("sb_act_text", "{muted}$*"),
    ("sb_act_msg", "{ink}$*"),
    ("sb_act_hilight", "{string}$*"),
    ("sb_act_hilight_color", "$0$1-%n"),
]


def color(spec, p):
    def sub(m):
        if m.group(1):
            return "%z" + p[m.group(2)].upper()
        return "%Z" + p[m.group(2)].upper()
    return re.sub(r"\{(bg:)?([a-z-]+)\}", lambda m: sub(m) if m.group(2) in p else m.group(0), spec)


def quote(s):
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'


def render(variant):
    p = palette(variant)
    name = "Neon Doll" + (" Light" if variant == "light" else "")
    out = [
        f"# {name}: hot pink neon on midnight plum, for irssi.",
        "# Generated by tools/build-irssi.py; edit that, not this.",
        "#",
        "# Exact colors: /set colors_ansi_24bit on",
        f"# Use it:       /set theme {VARIANTS[variant][:-6]}",
        "",
        'default_color = "-1";',
        'info_eol = "false";',
        "",
        f"replaces = {{ \"[]=\" = {quote(color('{dimmest}$*%n', p))}; }};",
        "",
        "abstracts = {",
    ]
    out += [f"  {k} = {quote(color(v, p))};" for k, v in ABSTRACTS]
    out += ["};", ""]
    return "\n".join(out)


def main():
    check = "--check" in sys.argv
    stale = []
    for variant, fname in VARIANTS.items():
        path, data = OUT / fname, render(variant).encode()
        if check:
            if not path.exists() or path.read_bytes() != data:
                stale.append(path.relative_to(ROOT))
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
            print(path.relative_to(ROOT))
    if stale:
        sys.exit("stale: " + ", ".join(map(str, stale)) + " (run tools/build-irssi.py)")


main()
