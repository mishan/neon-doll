# Neon Doll

**Hot pink neon on midnight plum.**

A desktop theme for GNOME and the tools around it. One fuchsia light marks
exactly where you are: the cursor, the current tab, the selected line. Violet
marks everything you can touch; the rest stays in the dark. Terminal type on
the chrome, soft sans for the words. Hard corners, no drop shadows, nothing
fades in. Cyberpunk, with a manicure.

It dresses the GNOME desktop (GTK 4 / libadwaita, GTK 3, GNOME Shell and the
mouse cursor) and the tools around it: Chrome, Firefox, Roundcube, GNOME Text Editor,
VS Code, Tilix, Ghostty, Emacs, vim, irssi, `ls`, `git`, `ag`, man pages,
glow and `whiptail`, plus the COSMIC desktop and its terminal, KDE Plasma and the Qt apps on it, and Windows Terminal, PowerShell and a Windows contrast theme for the times you're on Windows. Every part comes in dark and
light, except the cursor: GNOME has one cursor setting, so there is one cursor
theme, drawn to stand out on both.

![GNOME Shell overview, dark](screenshots/shell-overview-dark.png)

## Install

On Linux, the BSDs or macOS:

```sh
git clone https://github.com/mishan/neon-doll.git && cd neon-doll
./install.sh
```

On Windows, from a clone or the Windows zip, in PowerShell:

```powershell
.\windows\install.ps1
```

Each installer asks which parts to install, with the ones whose apps it finds
ticked. It copies files into your home directory and changes no settings; it
prints what to switch on afterwards. `--remove` (`-Remove` on Windows) takes
it out again.

Chrome, Roundcube and the Firefox theme itself are installed by hand. The
[install guide](docs/install.md) covers every part: what to name, where it
goes, how to turn it on, and what it can't reach.

## What it themes

- **Desktops:** [GNOME](docs/install.md#gnome) (GTK 4 / libadwaita, GTK 3 and 2, the Shell, the cursor, Text Editor), [COSMIC](docs/install.md#cosmic) and its terminal, [KDE Plasma and Qt](docs/install.md#kde-plasma-and-qt) (Kvantum, Konsole, Kate, qt5ct/qt6ct), and [Windows](docs/install.md#the-windows-desktop) as a contrast theme
- **Terminals and the command line:** [Tilix](docs/install.md#tilix), [Ghostty](docs/install.md#ghostty), [Windows Terminal and PowerShell](docs/install.md#windows-terminal-and-powershell), [`ls`](docs/install.md#ls-colors), [`git`](docs/install.md#git-colors), [`ag`](docs/install.md#ag), [man pages](docs/install.md#man-pages), [glow](docs/install.md#glow), [`whiptail`](docs/install.md#whiptail), [irssi](docs/install.md#irssi)
- **Editors:** [VS Code](docs/install.md#vs-code), [vim](docs/install.md#vim), [Emacs](docs/install.md#emacs-29)
- **On the web:** [Chrome](docs/install.md#chrome), [Firefox](docs/install.md#firefox), [Roundcube](docs/install.md#roundcube)

## Screenshots

| App | Dark | Light |
|---|---|---|
| Calendar | ![GNOME Shell calendar, dark](screenshots/shell-calendar-dark.png) | ![GNOME Shell calendar, light](screenshots/shell-calendar-light.png) |
| Quick settings | ![GNOME Shell quick settings, dark](screenshots/shell-quick-settings-dark.png) | ![GNOME Shell quick settings, light](screenshots/shell-quick-settings-light.png) |
| GTK 4 / libadwaita | ![GTK 4 / libadwaita, dark](screenshots/gtk4-dark.png) | ![GTK 4 / libadwaita, light](screenshots/gtk4-light.png) |
| VS Code | ![VS Code, dark](screenshots/vscode-dark.png) | ![VS Code, light](screenshots/vscode-light.png) |
| COSMIC, with Files and Terminal | ![COSMIC, with Files and Terminal, dark](screenshots/cosmic-desktop-dark.png) | ![COSMIC, with Files and Terminal, light](screenshots/cosmic-desktop-light.png) |
| KDE Plasma, with Dolphin and Konsole | ![KDE Plasma, with Dolphin and Konsole, dark](screenshots/plasma-desktop-dark.png) | ![KDE Plasma, with Dolphin and Konsole, light](screenshots/plasma-desktop-light.png) |

Every other app, in both variants, and the cursors are in the
[full gallery](docs/screenshots.md).

## The rules

| Rule | On the desktop |
|---|---|
| Fuchsia means position | Libadwaita's accent: selection, focus ring, caret, checked toggles, the switch, progress, the current tab, the current sidebar row, today in the calendar, the active workspace. In code: the cursor, the current line number, the matching bracket. Never decoration — even the terminal palette leaves it out. |
| Purple is interactive at rest | Links, and the suggested action, drawn as an outline rather than a filled pill. The two colors never swap roles. |
| Hover is a position too | Hovering turns things fuchsia, as a link does. Keyboard focus does the same and adds the ring. |
| The rail | A selected row carries a fuchsia bar on its left; a sidebar row gets the rail and fuchsia text. The current tab gets it across the top. |
| Page and panel | Windows are the page, with a 24px graph paper where the window shows through. Header bars, sidebars, cards, popovers and menus are panels with a 1px edge. That is the only box there is. |
| Mono chrome, sans prose | Header bars, buttons, menus, tabs, headings and text fields are mono; row titles, dialog bodies and documents keep sans. Weight 400 throughout. |
| No radii, shadows or motion | Radios and avatars stay round, since round is how a radio differs from a check. Windows get a 1px outline instead of a shadow. |
| Contrast floors | Text you need to read clears 4.5:1 on the page and on panels; the edge of a field, button or switch clears 3:1. `tools/build.sh --check` fails on a color below either. Line numbers are the one exception. |
| Redundant cues | A switch shows `\|` when on and `□` when off as well as its color; diff lines keep their `+`/`-` along with color and tint. |

Light keeps the roles but not the values: the dark fuchsia `#ff2d95` and
purple `#b48cff` are too faint on paper, so light uses `#b80061` and `#6a3fd0`,
both above 4.5:1 on its panels.

## Working on it

Every color is in [`tokens.toml`](tokens.toml); [CONTRIBUTING.md](CONTRIBUTING.md)
covers building, testing and screenshotting.

## License

GPL-3.0-or-later. See [COPYING](COPYING).

The Roundcube skin is the exception: its own files are GPL-3.0-or-later or
CC BY-SA 4.0, your choice, and its compiled CSS, which contains Roundcube's
Elastic skin (CC BY-SA 3.0), is CC BY-SA 4.0. See
[`roundcube/neon-doll/README.md`](roundcube/neon-doll/README.md).
