# Neon Doll

A GNOME theme that treats the desktop as a man page in a terminal that never
existed. Near-black plum or plum-tinted paper, a fuchsia that means "you are
here", mono for the chrome and sans for what you read. No rounded corners, no
drop shadows, no transitions.

It covers GTK 4 / libadwaita, GTK 3, GNOME Shell, and color schemes for GNOME
Text Editor, Tilix and Emacs, each in dark and light.

![The overview, dark](screenshots/shell-overview-dark.png)

| | Dark | Light |
|---|---|---|
| GNOME Shell overview | ![](screenshots/shell-overview-dark.png) | ![](screenshots/shell-overview-light.png) |
| Calendar | ![](screenshots/shell-calendar-dark.png) | ![](screenshots/shell-calendar-light.png) |
| Quick settings | ![](screenshots/shell-quick-settings-dark.png) | ![](screenshots/shell-quick-settings-light.png) |
| GTK 4 / libadwaita | ![](screenshots/gtk4-dark.png) | ![](screenshots/gtk4-light.png) |
| GTK 3 | ![](screenshots/gtk3-dark.png) | ![](screenshots/gtk3-light.png) |
| Text Editor | ![](screenshots/text-editor-dark.png) | ![](screenshots/text-editor-light.png) |
| Emacs | ![](screenshots/emacs-dark.png) | ![](screenshots/emacs-light.png) |

## Install

```
git clone <this repository> neon-doll && cd neon-doll
./install.sh                  # everything
./install.sh gtk4 shell       # or pick: gtk4 gtk3 shell gtksourceview tilix emacs
./install.sh --remove         # take it out again
```

`install.sh` copies files into your home directory and changes no settings; it
prints what to switch on afterwards. `--link` symlinks instead of copying, so
edits in the checkout show up on the next app launch.

| Part | Goes to | Turn it on |
|---|---|---|
| GTK 4 / libadwaita | `~/.config/gtk-4.0/gtk.css` | Restart apps. Light or dark follows Settings → Appearance. |
| GTK 3 | `~/.local/share/themes/Neon-Doll-{Dark,Light}/` | `gsettings set org.gnome.desktop.interface gtk-theme Neon-Doll-Dark` |
| GNOME Shell | the same two theme dirs | `gsettings set org.gnome.shell.extensions.user-theme name Neon-Doll-Dark` (needs the [User Themes](https://extensions.gnome.org/extension/19/user-themes/) extension) |
| Text Editor | `~/.local/share/gtksourceview-5/styles/` (and `-4`) | Pick Neon Doll in the style menu. |
| Tilix | `~/.config/tilix/schemes/` | Restart Tilix; Preferences → Profile → Color. |
| Emacs 29+ | `~/.emacs.d/themes/` (or `$EMACS_THEMES_DIR`) | `(add-to-list 'custom-theme-load-path "~/.emacs.d/themes/")` `(load-theme 'neon-doll-dark t)` |

Tested on GNOME 51 with GTK 4.24, libadwaita 1.10 and GTK 3.24.

### Light and dark

GTK 4 and Text Editor switch with the system style on their own. GTK 3 and the
Shell can't: a GTK 3 theme name and a Shell user theme are each one choice, so
there are two, `Neon-Doll-Dark` and `Neon-Doll-Light`. GTK 3 apps that ask for
a dark style get it from either. Tilix and Emacs have a scheme per variant.

## The rules

| Rule | On the desktop |
|---|---|
| Fuchsia means position | Libadwaita's accent: selection, focus ring, caret, checked toggles, the switch, progress, the current tab, the current sidebar row, today in the calendar, the active workspace. In code: the cursor, the current line number, the matching bracket. Never decoration — even the terminal palette leaves it out. |
| Purple is interactive at rest | Links, and the suggested action, drawn as an outline rather than a filled pill. The two colors never swap roles. |
| Hover is a position too | Hovering turns things fuchsia, as a link does. |
| The rail | A selected row carries a fuchsia bar on its left; a sidebar row gets the rail and fuchsia text. The current tab gets it across the top. |
| Page and panel | Windows are the page, with a 24px graph paper where the window shows through. Header bars, sidebars, cards, popovers and menus are panels with a 1px edge. That is the only box there is. |
| Mono chrome, sans prose | Header bars, buttons, menus, tabs, headings and text fields are mono; row titles, dialog bodies and documents keep sans. Weight 400 throughout. |
| No radii, shadows or motion | Radios and avatars stay round, since round is how a radio differs from a check. Windows get a 1px outline instead of a shadow. |
| Redundant cues | A switch shows `\|` when on and `□` when off as well as its color; diff lines keep their `+`/`-` along with color and tint. |

Light keeps the roles but not the values: the dark fuchsia `#ff2d95` and
purple `#b48cff` are too faint on paper, so light uses `#c8006a` and `#6a3fd0`,
both above 4.5:1 on its panels.

## Known limits

- **GNOME Shell** draws a few things in code, out of a theme's reach: the
  overview's rounded workspace corners, the round slider knob, and the handle's
  slide. The login screen uses the stock theme.
- **GTK 3** has no `:focus-visible`, so its focus ring appears only once the
  keyboard is in use. Message-dialog headings stay bold.
- **Apps that paint their own colors** — browsers, Electron apps, terminals
  other than Tilix — pick up little or nothing.
- **Line numbers** in the editor schemes use the dimmest color on purpose and
  sit below 4.5:1.
- **Emacs** faces for magit, vertico and similar packages are set but untested;
  there are no 256-color terminal specs.

## Working on it

The palette lives in a few places because each target reads colors
differently: CSS custom properties in `gtk-4.0/gtk.css`, `@define-color` in
`gtk-3.0/_colors-*.css`, and Python dicts in `tools/build-shell.py` and
`tools/scheme-colors.py`, which generate the Shell theme and the text schemes.
Generated files are committed, so installing needs nothing but `sh`.

```
tools/preview.py [--light] [--menu] [--dialog]    # GTK 4 widget sampler
tools/shoot.sh out.png [flags]                    # the same, screenshotted on Xvfb
tools/preview3.py / tools/shoot3.sh               # GTK 3
tools/build-shell.py [--check|--coverage]         # regenerate the Shell theme
tools/shoot-shell.sh OUTDIR [dark|light]          # screenshot a headless, fully themed GNOME Shell
tools/scheme-colors.py [--write|--elisp]          # derive and check the text schemes
tools/scheme-shoot.sh out.png gsv|emacs [variant] # screenshot them
```

`tools/check-tokens.py` and `tools/check-tokens3.py` compare the palette
against the design system it came from; they need that project's
`system.css` as an argument.

## License

GPL-3.0-or-later. See [COPYING](COPYING).
