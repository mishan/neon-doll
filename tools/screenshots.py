#!/usr/bin/env python3
"""Make every screenshot in screenshots/, and tell which are out of date.

    tools/screenshots.py NAME...      make these shots, into screenshots/
    tools/screenshots.py --all        make all of them
    tools/screenshots.py --list       each shot, its files and its inputs
    tools/screenshots.py --check      fail if any is stale, unmade or unknown

Each shot is a tool that writes its pictures to a scratch directory; this
crops each to its size, puts it in screenshots/, and records a hash of the
shot's inputs (the theme files it shows and the tools that draw it) in
screenshots/sources.json. --check renders nothing: it fails when a shot's
inputs no longer hash to what's recorded, so a change to the theme can't
land with screenshots that don't show it; when a file in screenshots/ is
made by no shot; and when a shot's file is missing. It runs in CI.

Most shots need shotbox (https://github.com/mishan/shotbox) on PATH, and
the programs they show; plasma, cosmic and roundcube need docker.
"""

import glob
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SHOTS_DIR = ROOT / "screenshots"
SOURCES = SHOTS_DIR / "sources.json"
VARIANTS = ("dark", "light")


@dataclass
class Shot:
    # The command, run from the repo root; {out} is a scratch directory,
    # {v} a variant when it runs once per variant.
    command: list
    # Each file it writes in {out}, by the name it has in screenshots/.
    files: dict
    inputs: list
    per_variant: bool = False
    # Cropped from the top left to WxH.
    crop: tuple = None
    extra: dict = field(default_factory=dict)


def both(pattern):
    """One picture per variant, by the same name in screenshots/."""
    return {pattern: pattern}


TERM = ["tilix/*.json"]

SHOTS = {
    "gtk4": Shot(["tools/shoot.sh", "{out}/gtk4-{v}.png", "{light}"], both("gtk4-{v}.png"),
                 ["gtk-4.0/gtk.css", "tools/preview.py", "tools/shoot.sh"],
                 per_variant=True, crop=(1180, 980)),
    "gtk3": Shot(["tools/shoot3.sh", "Neon-Doll-{V}", "{out}/gtk3-{v}.png"], both("gtk3-{v}.png"),
                 ["gtk-3.0/*.css", "themes/Neon-Doll-Dark/gtk-3.0/**", "themes/Neon-Doll-Light/gtk-3.0/**",
                  "tools/preview3.py", "tools/shoot3.sh"],
                 per_variant=True, crop=(1190, 1040)),
    "shell": Shot(["tools/shoot-shell.sh", "{out}", "{v}"],
                  {f"shell-{scene}-{{v}}.png": f"{n}.png"
                   for scene, n in (("overview", "08-overview"), ("calendar", "03-calendar"),
                                    ("quick-settings", "04-quick-settings"))},
                  ["gnome-shell/**", "themes/**", "gtk-4.0/gtk.css", "gtksourceview/*.xml",
                   "tools/check-tokens.py", "tools/shoot-shell.sh"],
                  per_variant=True),
    "text-editor": Shot(["tools/text-editor-shoot.sh", "{out}"], both("text-editor-{v}.png"),
                        ["gtk-4.0/gtk.css", "gtksourceview/*.xml", "tools/check-tokens.py",
                         "tools/text-editor-shoot.sh"]),
    "emacs": Shot(["tools/scheme-shoot.sh", "{out}/emacs-{v}.png", "emacs", "{v}"], both("emacs-{v}.png"),
                  ["emacs/*.el", "tools/scheme-shoot.sh", "tools/scheme-emacs-sample.el"],
                  per_variant=True),
    "vscode": Shot(["tools/vscode-shoot.py", "{v}", "{out}/vscode-{v}.png"], both("vscode-{v}.png"),
                   ["vscode/**", "tools/build-vscode.py", "tools/vscode-shoot.py"], per_variant=True),
    "chrome": Shot(["tools/chrome-shoot.py", "{v}", "{out}/chrome-{v}.png"], both("chrome-{v}.png"),
                   ["chrome/**", "tools/chrome-shoot.py"], per_variant=True),
    "firefox": Shot(["tools/firefox-shoot.py", "{v}", "{out}/firefox-{v}.png"], both("firefox-{v}.png"),
                    ["firefox/**", "tools/firefox-shoot.py"], per_variant=True),
    "roundcube": Shot(["tools/roundcube-shoot.py", "{out}", "dark", "light", "--scene", "mail"],
                      both("roundcube-mail-{v}.png"),
                      ["roundcube/neon-doll/**", "tools/roundcube-shoot.py", "tools/roundcube-mail.py"]),
    "irssi": Shot(["tools/irssi-shoot.sh", "{out}"], both("irssi-{v}.png"),
                  [*TERM, "irssi/*", "tools/irssi-shoot.sh", "tools/irssi-server.py"]),
    "ag": Shot(["tools/ag-shoot.sh", "{out}"], both("ag-{v}.png"),
               [*TERM, "ag/*", "tools/ag-shoot.sh"]),
    "ghostty": Shot(["tools/ghostty-shoot.sh", "{out}"], both("ghostty-{v}.png"),
                    ["ghostty/themes/*", "dircolors/*", "tools/ghostty-shoot.sh"]),
    "cosmic": Shot(["tools/cosmic-shoot.sh", "{out}", "dark", "light"],
                   {**both("cosmic-desktop-{v}.png"), **both("cosmic-settings-{v}.png")},
                   ["cosmic/**", "tilix/*.json", "dircolors/*", "tools/cosmic-shoot.sh",
                    "tools/cosmic-scene.sh"]),
    "plasma": Shot(["tools/kde-shoot.sh", "{out}", "dark", "light"],
                   {**both("plasma-desktop-{v}.png"), **both("plasma-kate-{v}.png"),
                    **both("plasma-widgets-{v}.png"), **both("plasma-settings-{v}.png")},
                   ["kde/**", "tools/kde-shoot.sh"]),
    "cursors": Shot(["tools/build-cursor.py", "--sheet", "{out}/cursors.png"], {"cursors.png": "cursors.png"},
                    ["cursor/src/*.svg", "tools/build-cursor.py"]),
}
for part, config in (("git", ["git/*"]), ("man", ["man/*"]), ("glow", ["glow/*"]),
                     ("whiptail", ["newt/*"]), ("vim", ["vim/**"]),
                     ("powershell", ["windows/powershell/*"])):
    SHOTS[part] = Shot(["tools/cli-shoot.sh", "{out}", part], both(part + "-{v}.png"),
                       [*TERM, *config, "tools/cli-shoot.sh"])
SHOTS["tilix-palettes"] = Shot(["tools/cli-shoot.sh", "{out}", "palettes"],
                               {"tilix-palettes.png": "tilix-palettes.png"},
                               [*TERM, "tools/cli-shoot.sh", "tools/cli-palette.sh"])


def inputs(shot):
    files = set()
    for pattern in shot.inputs:
        found = [Path(p) for p in glob.glob(str(ROOT / pattern), recursive=True)]
        found = [p for p in found if p.is_file()]
        if not found:
            sys.exit(f"screenshots.py: no input matches {pattern}")
        files.update(found)
    return sorted(files)


def digest(shot):
    h = hashlib.sha256()
    for path in inputs(shot):
        h.update(str(path.relative_to(ROOT)).encode() + b"\0")
        h.update(path.read_bytes() + b"\0")
    return h.hexdigest()


def names(shot):
    """The shot's files in screenshots/, with the variants filled in."""
    return sorted({dest.format(v=v) for dest in shot.files for v in VARIANTS})


def recorded():
    return json.loads(SOURCES.read_text()) if SOURCES.exists() else {}


def check():
    problems = []
    sources = recorded()
    made = set()
    for name, shot in SHOTS.items():
        made.update(names(shot))
        missing = [f for f in names(shot) if not (SHOTS_DIR / f).exists()]
        if missing:
            problems.append(f"{name}: missing {', '.join(missing)}")
        elif sources.get(name) != digest(shot):
            problems.append(f"{name}: stale, its inputs changed since it was made")
    for path in sorted(SHOTS_DIR.glob("*.png")):
        if path.name not in made:
            problems.append(f"{path.name}: no shot makes it")
    if problems:
        sys.exit("screenshots out of date (tools/screenshots.py NAME... remakes them):\n  "
                 + "\n  ".join(problems))
    print(f"all {len(SHOTS)} shots up to date")


def make(name):
    from PIL import Image
    shot = SHOTS[name]
    with tempfile.TemporaryDirectory() as tmp:
        # A shot run once per variant gets a directory per variant, since
        # some write the same names for each.
        def out(v):
            d = Path(tmp) / (v if shot.per_variant else "all")
            d.mkdir(exist_ok=True)
            return d
        for v in VARIANTS if shot.per_variant else [None]:
            words = {"out": str(out(v))}
            if v:
                words |= {"v": v, "V": v.capitalize(), "light": "--light" if v == "light" else ""}
            command = [w.format(**words) for w in shot.command]
            subprocess.run([w for w in command if w], cwd=ROOT, check=True)
        for dest, src in shot.files.items():
            for v in VARIANTS:
                picture = Image.open(out(v) / src.format(v=v))
                if shot.crop:
                    picture = picture.crop((0, 0, *shot.crop))
                picture.save(SHOTS_DIR / dest.format(v=v), optimize=True)
    sources = recorded()
    sources[name] = digest(shot)
    SOURCES.write_text(json.dumps(dict(sorted(sources.items())), indent=2) + "\n")
    print(f"made {name}: {', '.join(names(shot))}")


def main(args):
    if args == ["--check"]:
        check()
    elif args == ["--list"]:
        for name, shot in SHOTS.items():
            print(f"{name}: {' '.join(names(shot))}\n  from {' '.join(shot.command)}\n"
                  f"  inputs {' '.join(shot.inputs)}")
    elif args == ["--all"]:
        for name in SHOTS:
            make(name)
    elif args and not any(a.startswith("-") for a in args):
        unknown = [a for a in args if a not in SHOTS]
        if unknown:
            sys.exit(f"screenshots.py: no such shot: {' '.join(unknown)} (--list lists them)")
        for name in args:
            make(name)
    else:
        sys.exit(__doc__.strip())


if __name__ == "__main__":
    main(sys.argv[1:])
