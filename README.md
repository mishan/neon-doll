# Neon Doll

**Hot pink neon on midnight plum.**

A desktop theme for GNOME and the tools around it. One fuchsia light marks
exactly where you are: the cursor, the current tab, the selected line. Violet
marks everything you can touch; the rest stays in the dark. Terminal type on
the chrome, soft sans for the words. Hard corners, no drop shadows, nothing
fades in. Cyberpunk, with a manicure.

It dresses the GNOME desktop (GTK 4 / libadwaita, GTK 3, GNOME Shell and the
mouse cursor) and the tools around it: Chrome, Firefox, GNOME Text Editor,
Tilix, Emacs, `ls`, `git`, man pages and glow, plus Windows Terminal and
PowerShell for the times you're on Windows. Every part comes in dark and
light, except the cursor: GNOME has one cursor setting, so there is one cursor
theme, drawn to stand out on both.

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
| Chrome | ![](screenshots/chrome-dark.png) | ![](screenshots/chrome-light.png) |
| Firefox | ![](screenshots/firefox-dark.png) | ![](screenshots/firefox-light.png) |
| git in Tilix | ![](screenshots/git-dark.png) | ![](screenshots/git-light.png) |
| man pages | ![](screenshots/man-dark.png) | ![](screenshots/man-light.png) |
| glow | ![](screenshots/glow-dark.png) | ![](screenshots/glow-light.png) |
| PowerShell | ![](screenshots/powershell-dark.png) | ![](screenshots/powershell-light.png) |

![Every cursor at 64 and 32 px on dark, light, grey and a busy photo-like background](screenshots/cursors.png)

## Install

```
git clone https://github.com/mishan/neon-doll.git && cd neon-doll
./install.sh                  # everything
./install.sh gtk4 shell       # or pick: gtk4 gtk3 shell cursor gtksourceview tilix emacs dircolors git man glow
./install.sh --remove         # take it out again
```

`install.sh` copies files into your home directory and changes no settings; it
prints what to switch on afterwards. `--link` symlinks instead of copying, so
edits in the checkout show up on the next app launch.

| Part | Goes to | Turn it on |
|---|---|---|
| GTK 4 / libadwaita | `~/.config/gtk-4.0/gtk.css` | Restart apps. Light or dark follows Settings → Appearance. |
| GTK 3 | `~/.local/share/themes/Neon-Doll-{Dark,Light}/` | `gsettings set org.gnome.desktop.interface gtk-theme Neon-Doll-Dark` |
| GNOME Shell | the same two theme dirs, plus `Neon-Doll-{Dark,Light}-Hearts` | `gsettings set org.gnome.shell.extensions.user-theme name Neon-Doll-Dark` (needs the [User Themes](https://extensions.gnome.org/extension/19/user-themes/) extension). The `-Hearts` themes are the same, except that Locate Pointer (press Ctrl) ripples out as a heart instead of a ring. |
| Cursor | `~/.local/share/icons/Neon-Doll-Cursors/` | `gsettings set org.gnome.desktop.interface cursor-theme Neon-Doll-Cursors`. One theme for light and dark: black, with a 1 px light edge that finds it on dark backgrounds. The everyday pointers, the arrow, the hand and the text beam, are edged in fuchsia instead, with a faint halo, since they are where you are. The size is Settings → Accessibility → Seeing → Cursor Size; every size from 24 to 96 is drawn. |
| Text Editor | `~/.local/share/gtksourceview-5/styles/` (and `-4`) | Pick Neon Doll in the style menu. |
| Tilix | `~/.config/tilix/schemes/` | Restart Tilix; Preferences → Profile → Color. |
| Emacs 29+ | `~/.emacs.d/themes/` (or `$EMACS_THEMES_DIR`) | `(add-to-list 'custom-theme-load-path "~/.emacs.d/themes/")` `(load-theme 'neon-doll-dark t)` |
| `ls` colors | `~/.config/neon-doll/dircolors` | `eval "$(dircolors -b ~/.config/neon-doll/dircolors)"` in `~/.bashrc`. Uses only the 16 terminal colors, so it follows either Neon Doll terminal scheme; odd permissions are underlined rather than filled. |
| man pages | `~/.config/neon-doll/man.sh` | `. ~/.config/neon-doll/man.sh` in `~/.bashrc`. Headings and literal options purple, arguments cyan and underlined, nothing bold; only `man`'s pager changes, not `less` in general. |
| glow | `~/.config/neon-doll/glow/` | `style: "~/.config/neon-doll/glow/neon-doll-dark.json"` (or `-light`) in `~/.config/glow/glow.yml`. Markdown as a man page: capitalized purple section headings, code in the editor schemes' colors. |
| `git` colors | `~/.config/neon-doll/gitconfig` | `git config --global include.path ~/.config/neon-doll/gitconfig`, placed after any `[color]` sections of your own. Diff, log, status, branch, grep and `add -p`, in the 16 terminal colors; nothing bold. |

**Chrome** can't be installed from a script. Open `chrome://extensions`, turn
on Developer mode, choose *Load unpacked* and pick `chrome/neon-doll-dark` or
`chrome/neon-doll-light`. Chrome themes are colors only, and one theme can't
follow the system's light or dark mode, so pick the one that matches it. The
current tab is the lifted panel, titled in fuchsia; the dark New Tab page gets
the graph paper, while the light one stays plain, since Chrome treats any New
Tab image as a photo and whitens the logo over it.

**Firefox** is one theme that carries both variants and follows the system's
light or dark mode. Until it's on addons.mozilla.org, load it for the session
from `about:debugging` → *This Firefox* → *Load Temporary Add-on*, picking
`firefox/manifest.json`; release Firefox only keeps signed add-ons across
restarts. The current tab is the lifted panel, titled and outlined in fuchsia;
the address bar is a slot that takes a fuchsia edge when focused; menus and the
address bar's results are panels, the highlighted result washed in fuchsia; and
the graph paper shows in the tab strip.

A theme sets colors only. For the shapes, `firefox/userChrome.css` squares the
corners, drops the shadows, sets the chrome in mono and turns the current tab's
outline into a rail across its top. It is optional and goes in by hand: set
`toolkit.legacyUserProfileCustomizations.stylesheets` to `true` in
`about:config`, copy the file into a `chrome/` folder inside your profile
folder (`about:support` → *Profile Folder*) and restart Firefox.

**Windows Terminal and PowerShell.** From a clone on Windows, run
`.\windows\install.ps1` (`-Remove` to take it out) in the shell you want
colored. It copies the color schemes into Windows Terminal's Fragments folder,
where Terminal finds them on its own, and the PowerShell colors next to your
profile, then prints the two lines to add: pick *Neon Doll Dark* or *Light* as
the profile's color scheme, and dot-source `neon-doll.ps1` from `$PROFILE`.
The schemes are the Tilix ones entry for entry. The PowerShell colors cover
typing (commands and parameters purple, values cyan, strings yellow, comments
muted) and, on PowerShell 7.2+, `Get-ChildItem`, tables, errors and progress,
matching the `ls` colors. `Enable-NeonDollPrompt` adds the bash prompt's
look. The tab row's colors are a Terminal *theme*, which fragments can't carry:
paste the entries from `windows/terminal/themes.json` into `settings.json`.

Tested on GNOME 51 with GTK 4.24, libadwaita 1.10 and GTK 3.24, Chrome 154 and
Firefox 156.

### Light and dark

GTK 4, Text Editor and Firefox switch with the system style on their own.
GTK 3 and the Shell can't: a GTK 3 theme name and a Shell user theme are each
one choice, so there are two, `Neon-Doll-Dark` and `Neon-Doll-Light`. GTK 3
apps that ask for a dark style get it from either. Tilix and Emacs have a
scheme per variant.

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
- **Apps that paint their own colors** — Electron apps, terminals other than
  Tilix — pick up little or nothing.
- **Chrome** themes set colors only: tabs keep Chrome's rounded shapes, and
  focus rings and hover states stay Chrome's own.
- **Firefox** themes set colors only, and the current tab's indicator is an
  outline all round, so without `userChrome.css` tabs and fields stay rounded,
  the chrome stays sans, and the tab gets a fuchsia box rather than a rail.
  Hover can tint a toolbar button but not turn its icon fuchsia. The account
  banner in the main menu and the New Tab page's own buttons keep Firefox's
  colors. `userChrome.css` leans on Firefox's internal design tokens, which
  can change in any release.
- **The cursor** doesn't move: wait is a still hourglass, and progress the
  arrow with a small one. Names it doesn't have, such as the hashed ones a
  few older Qt and X apps ask for, fall back to Adwaita's.
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
tools/term-shoot.sh out.png                       # ls colors in both terminal schemes, GNU defaults vs Neon Doll
tools/build-chrome.py [--check]                   # regenerate the Chrome themes
tools/chrome-shoot.py dark|light out.png          # screenshot one in a scratch Chrome profile (under xvfb-run)
tools/build-firefox.py [--check]                  # regenerate the Firefox theme
tools/firefox-shoot.py dark|light out.png [--menu] [--userchrome]
                                                  # screenshot it in a scratch Firefox profile (under xvfb-run)
tools/build-glow.py [--check]                     # regenerate the glow styles
tools/build-cursor.py [--check|--sheet out.png]   # regenerate the cursor theme from cursor/src/*.svg
tools/build-windows.py [--check]                  # regenerate the Windows Terminal files from the Tilix schemes
tools/dist.sh [VERSION]                           # release archives into dist/
```

`tools/check-tokens.py` and `tools/check-tokens3.py` compare the palette
against the design system it came from; they need that project's
`system.css` as an argument.

## License

GPL-3.0-or-later. See [COPYING](COPYING).
