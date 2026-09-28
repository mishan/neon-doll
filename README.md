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
glow and `whiptail`, plus the COSMIC desktop and its terminal, KDE Plasma and the Qt apps on it, and Windows Terminal and PowerShell for the times you're on Windows. Every part comes in dark and
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
| vim | ![](screenshots/vim-dark.png) | ![](screenshots/vim-light.png) |
| VS Code | ![](screenshots/vscode-dark.png) | ![](screenshots/vscode-light.png) |
| Chrome | ![](screenshots/chrome-dark.png) | ![](screenshots/chrome-light.png) |
| Firefox | ![](screenshots/firefox-dark.png) | ![](screenshots/firefox-light.png) |
| Roundcube | ![](screenshots/roundcube-mail-dark.png) | ![](screenshots/roundcube-mail-light.png) |
| irssi | ![](screenshots/irssi-dark.png) | ![](screenshots/irssi-light.png) |
| Ghostty | ![](screenshots/ghostty-dark.png) | ![](screenshots/ghostty-light.png) |
| COSMIC, with Files and Terminal | ![](screenshots/cosmic-desktop-dark.png) | ![](screenshots/cosmic-desktop-light.png) |
| COSMIC Settings | ![](screenshots/cosmic-settings-dark.png) | ![](screenshots/cosmic-settings-light.png) |
| KDE Plasma, with Dolphin and Konsole | ![](screenshots/plasma-desktop-dark.png) | ![](screenshots/plasma-desktop-light.png) |
| Kate | ![](screenshots/plasma-kate-dark.png) | ![](screenshots/plasma-kate-light.png) |
| Qt widgets, in Kvantum | ![](screenshots/plasma-widgets-dark.png) | ![](screenshots/plasma-widgets-light.png) |
| Plasma's global themes | ![](screenshots/plasma-settings-dark.png) | ![](screenshots/plasma-settings-light.png) |
| git in Tilix | ![](screenshots/git-dark.png) | ![](screenshots/git-light.png) |
| ag | ![](screenshots/ag-dark.png) | ![](screenshots/ag-light.png) |
| man pages | ![](screenshots/man-dark.png) | ![](screenshots/man-light.png) |
| glow | ![](screenshots/glow-dark.png) | ![](screenshots/glow-light.png) |
| PowerShell | ![](screenshots/powershell-dark.png) | ![](screenshots/powershell-light.png) |
| whiptail | ![](screenshots/whiptail-dark.png) | ![](screenshots/whiptail-light.png) |

![Every cursor at 64 and 32 px on dark, light, grey and a busy photo-like background](screenshots/cursors.png)

## Install

```
git clone https://github.com/mishan/neon-doll.git && cd neon-doll
./install.sh                  # everything
./install.sh gtk4 shell       # or pick: gtk4 gtk3 shell cursor gtksourceview tilix emacs dircolors git man glow newt ag ghostty vim irssi cosmic kde kvantum konsole kate qtct
./install.sh --remove         # take it out again
./install.sh --desktop-grid gtk4   # graph paper over the wallpaper too (with Desktop Icons NG)
```

`install.sh` copies files into your home directory and changes no settings; it
prints what to switch on afterwards. `--link` symlinks instead of copying, so
edits in the checkout show up on the next app launch.

| Part | Goes to | Turn it on |
|---|---|---|
| GTK 4 / libadwaita | `~/.config/gtk-4.0/gtk.css` | Restart apps. Light or dark follows Settings → Appearance. Window backgrounds are graph paper, but not the desktop: Desktop Icons NG draws its icons in a transparent GTK 4 window over the wallpaper, so the paper would land on the wallpaper too. Install with `--desktop-grid` to have it there as well. |
| GTK 3 and 2 | `~/.local/share/themes/Neon-Doll-{Dark,Light}/` | `gsettings set org.gnome.desktop.interface gtk-theme Neon-Doll-Dark`. The same setting reaches GTK 2 apps like HexChat: they get Adwaita's GTK 2 widgets in Neon Doll's colors, so they need Adwaita's GTK 2 theme (`gnome-themes-extra`). |
| GNOME Shell | the same two theme dirs, plus `Neon-Doll-{Dark,Light}-Hearts` | `gsettings set org.gnome.shell.extensions.user-theme name Neon-Doll-Dark` (needs the [User Themes](https://extensions.gnome.org/extension/19/user-themes/) extension). The `-Hearts` themes are the same, except that Locate Pointer (press Ctrl) ripples out as a heart instead of a ring. |
| Cursor | `~/.local/share/icons/Neon-Doll-Cursors/` | `gsettings set org.gnome.desktop.interface cursor-theme Neon-Doll-Cursors`. One theme for light and dark: black, with a 1 px light edge that finds it on dark backgrounds. The everyday pointers, the arrow, the hand and the text beam, are edged in fuchsia instead, with a faint halo, since they are where you are. The size is Settings → Accessibility → Seeing → Cursor Size; every size from 24 to 96 is drawn. |
| Text Editor | `~/.local/share/gtksourceview-5/styles/` (and `-4`) | Pick Neon Doll in the style menu. |
| Tilix | `~/.config/tilix/schemes/` | Restart Tilix; Preferences → Profile → Color. |
| Ghostty | `~/.config/ghostty/themes/` | `theme = light:Neon Doll Light,dark:Neon Doll Dark` in `~/.config/ghostty/config.ghostty`, which follows the system style. The Tilix colors, plus a border-colored split divider, unfocused splits fading toward the page, and search matches in purple with the current one in fuchsia. Its tabs and header bar are libadwaita, so they take the GTK 4 stylesheet. |
| COSMIC | `~/.config/neon-doll/cosmic/` | `cosmic-settings appearance import ~/.config/neon-doll/cosmic/Neon-Doll-Dark.ron`, then the same with `-Light`; each lands in its own mode, and COSMIC switches between them as it does its own. Or Settings → Desktop → Appearance → Import. The page, the panel as containers, ink as the text tint, purple as the accent, fuchsia on the focused window's outline, square corners, nothing frosted; COSMIC derives the rest. Leave *Apply this theme to GNOME apps* off: it replaces `~/.config/gtk-4.0/gtk.css` with COSMIC's own. |
| COSMIC Terminal | `~/.config/neon-doll/cosmic/terminal/` | View → Color schemes… → Import, and pick `Neon Doll Dark.ron`; the list is the current mode's, so switch to light and import `Neon Doll Light.ron` there. The Tilix colors. |
| KDE Plasma | `~/.local/share/color-schemes/`, `~/.local/share/plasma/look-and-feel/` | `kvantummanager --set NeonDoll` (the kvantum part), then System Settings → Colors & Themes → Global Theme → Neon Doll Dark or Light. The global theme sets the color scheme, Kvantum, the cursor and the chrome fonts: toolbars, menus and window titles in your monospace font. To follow the time of day, turn on *Switch to Dark Mode at Night* on that page and pick the two there; Kvantum switches with them. Window decorations and the Plasma style stay Breeze's, in Neon Doll's colors. For the colors alone, on Breeze's shapes: `plasma-apply-colorscheme NeonDollDark`. |
| Kvantum | `~/.config/Kvantum/NeonDoll/` | `kvantummanager --set NeonDoll`, then the widget style `kvantum-dark`, or `kvantum` for light: the theme is NeonDoll, and its dark variant NeonDollDark. The shapes for every Qt app, which Breeze and a color scheme can't change: square buttons and fields with a hairline edge, the rail on the selected row and across the current tab, graph paper in the windows, no shadows. Outside Plasma, set `QT_STYLE_OVERRIDE=kvantum-dark`, or pick it in qt6ct. |
| Konsole | `~/.local/share/konsole/` | Settings → Manage Profiles → Neon Doll Dark (or Light) → Set as Default. The Tilix colors; the profile carries the fuchsia cursor, which a Konsole color scheme can't. |
| Kate | `~/.local/share/org.kde.syntax-highlighting/themes/` | Settings → Configure Kate → Color Themes. KWrite, KDevelop and anything else on KTextEditor list it too. The editor schemes' four syntax colors. |
| qt5ct, qt6ct | `~/.config/qt5ct/colors/`, `~/.config/qt6ct/colors/` | Appearance → Palette → Custom → NeonDollDark (or NeonDollLight), for Qt apps outside Plasma on the Fusion style. With Kvantum, apps take its colors instead. |
| vim | `~/.vim/colors/neon-doll.vim` | `colorscheme neon-doll` in `~/.vimrc`. One scheme for both variants: it follows `background`. With `termguicolors` it uses the exact colors, matching the other editors; without, it uses the 16 terminal colors and follows the terminal's Neon Doll scheme. |
| irssi | `~/.irssi/neon-doll{,-light}.theme` | `/set theme neon-doll` (or `neon-doll-light`) and `/set colors_ansi_24bit on`, then `/save`. The prompt, which names the window you're typing into, is fuchsia; you and the channels are purple; lines that mention you, and the windows holding them, are yellow; timestamps, hostmasks, joins and parts step back into grey. Without 24-bit color irssi uses the nearest of the 256 colors. |
| Emacs 29+ | `~/.emacs.d/themes/` (or `$EMACS_THEMES_DIR`) | `(add-to-list 'custom-theme-load-path "~/.emacs.d/themes/")` `(load-theme 'neon-doll-dark t)` |
| `ls` colors | `~/.config/neon-doll/dircolors` | `eval "$(dircolors -b ~/.config/neon-doll/dircolors)"` in `~/.bashrc`. Uses only the 16 terminal colors, so it follows either Neon Doll terminal scheme; odd permissions are underlined rather than filled. |
| `ag` | `~/.config/neon-doll/ag.sh` | `. ~/.config/neon-doll/ag.sh` in `~/.bashrc`. ag has no config file, so it's an alias with ag's three color flags: file names purple, line numbers muted, matches purple and underlined, as `git grep` has them under the Neon Doll git colors. Nothing bold, and only the 16 terminal colors. |
| man pages | `~/.config/neon-doll/man.sh` | `. ~/.config/neon-doll/man.sh` in `~/.bashrc`. Headings and literal options purple, arguments cyan and underlined, nothing bold; only `man`'s pager changes, not `less` in general. |
| glow | `~/.config/neon-doll/glow/` | `alias glow='glow -s ~/.config/neon-doll/glow/neon-doll-dark.json'` (or `-light`) in `~/.bashrc`, or the full path as `style:` in `~/.config/glow/glow.yml`; glow doesn't expand `~` there. Markdown as a man page: capitalized purple section headings, code in the editor schemes' colors. |
| `whiptail` | `~/.config/neon-doll/newt.sh` | `. ~/.config/neon-doll/newt.sh` in `~/.bashrc`. For whiptail and everything built on newt, like debconf and `dpkg-reconfigure`: the box a panel with a purple edge, the focused item reverse purple, no drop shadow. newt's own colors assume a VGA console and wash out on this palette. |
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

**VS Code** gets an extension with *Neon Doll Dark* and *Neon Doll Light*.
Once it's on the Marketplace and Open VSX, it installs from the Extensions
view; until then, build it with `tools/build-vscode.py --vsix neon-doll.vsix`
(or take the `.vsix` from a release) and run
`code --install-extension neon-doll.vsix`, then pick the theme with
*Preferences: Color Theme*. The editor is the page and everything around it a
panel; the syntax is the editor schemes', the terminal the Tilix colors. The
current tab, the focused row, the active activity-bar item, the selection and
the current find match are fuchsia; links, badges and the primary button,
drawn as a purple wash with a purple edge, are purple.

**Roundcube** gets a skin, a child of Elastic, the default one, which it
needs installed beside it. Copy `roundcube/neon-doll` into Roundcube's
`skins/` folder (or unpack the `neon-doll-roundcube` archive from a release
there), then pick *Neon Doll* in Settings → Preferences → User Interface, or
set `$config['skin'] = 'neon-doll';` to make it everyone's. One skin holds
both variants and follows Roundcube's own switch, the *Dark mode* / *Light
mode* button in the menu, which follows the system until it's pressed. The
current task, folder and message carry the fuchsia rail; unread mail is ink
with a purple dot and read mail is muted, flagged mail is yellow and deleted
mail is struck through, all at weight 400. The list and the message are the
page, and an empty preview pane is graph paper, as is the login page; the
menu, the folders and the header bars are panels. Its CSS is compiled against
Roundcube 1.7.4's Elastic; for another version, rebuild it against that
version's with `tools/build-roundcube.py --elastic /path/to/roundcube/skins/elastic`.

Tested on GNOME 51 with GTK 4.24, libadwaita 1.10 and GTK 3.24, Chrome 154,
Firefox 156, VS Code 1.139 and Roundcube 1.7.4 and 1.6.18 (upstream and
Debian 13's package).

### Light and dark

GTK 4, Text Editor, Firefox, Roundcube and COSMIC switch with the system style on
their own, and Plasma does once it has the two global themes as its pair.
GTK 3 and the Shell can't: a GTK 3 theme name and a Shell user theme are each
one choice, so there are two, `Neon-Doll-Dark` and `Neon-Doll-Light`. GTK 3
apps that ask for a dark style get it from either. Tilix and Emacs have a
scheme per variant. VS Code switches when told to, in its settings:

```json
"window.autoDetectColorScheme": true,
"workbench.preferredDarkColorTheme": "Neon Doll Dark",
"workbench.preferredLightColorTheme": "Neon Doll Light"
```

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
- **COSMIC** themes are a handful of seed colors that COSMIC derives every
  surface and state from, so purple, the accent, is also the focus ring and
  the selection, and fuchsia marks only the focused window. Fonts are
  COSMIC's own setting, not the theme's, and the desktop has no graph paper
  unless you set one as the wallpaper. Tested only in a nested COSMIC 1.8
  (`tools/cosmic-shoot.sh`), where COSMIC Terminal started on its dark scheme
  in light mode unless its own View → Settings → Theme was set to Light.
- **KDE Plasma** keeps Breeze for the window decorations and the Plasma style,
  so title bars, the panel and its popups take Neon Doll's colors but keep
  Breeze's rounded corners and shadows, and the focused window has no fuchsia
  outline. Kvantum draws its focus frame whenever a widget has focus, so a
  clicked item gets a fuchsia box, not only one reached from the keyboard. A
  selected tree row carries its rail at the item's indent rather than the
  row's edge. Kirigami apps, System Settings among them, reach Kvantum through
  KDE's Qt Quick style and draw a few controls of their own, like the switch.
  Breeze's folder icons take the selection color, so folders are plum in
  dark and pink in light. QToolBox keeps Qt's slanted tab outline. Tested only
  in a nested Plasma 6.7 with Kvantum 1.1.6 and KDE Gear 26.08
  (`tools/kde-shoot.sh`).
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
- **VS Code** themes set colors only, so corners and fonts stay VS Code's.
  Buttons are fills, so the primary button is a purple wash with a purple
  edge rather than a bare outline, and hover can change its fill but not its
  text. List rows can't take a rail; the focused row is a fuchsia wash with
  fuchsia text instead. Newer VS Code draws the side bar, editor and panel as
  rounded cards and marks the active tab and activity-bar item with a pill
  rather than a rail; the theme colors both layouts. The chat and agent views
  keep VS Code's colors.
- **Roundcube** keeps Elastic's layout, icons and logo. HTML mail is the
  sender's page: it keeps its own fonts, weights and corners, and in dark
  mode it sits on white, as in Elastic, with the light colors around its
  links and quotes. The HTML editor's page stays white too, since it is the
  message as it will be sent.

## Working on it

Every color is in [`tokens.toml`](tokens.toml), dark and light: the core
palette under the design system's names, and each tint as a color at an
alpha. `tools/tokens.py` reads it for the builders, and flattens the tints
onto the page for the themes that only take solid colors (the editor and
terminal schemes). Change a color there, then run `tools/build.sh`: it
rewrites every generated theme, and the palette copies inside the
hand-written ones (the GTK stylesheets and the Emacs themes, between
markers). `tools/build.sh --check` fails if anything is stale. Generated files
are committed, so installing needs nothing but `sh`.

```
tools/build.sh [--check]                          # rebuild everything from tokens.toml
tools/build-palettes.py [--check]                 # just the palette copies in the GTK and Emacs themes
tools/build-gtk2.py [--check]                     # the GTK 2 part of the theme dirs
tools/preview.py [--light] [--menu] [--dialog]    # GTK 4 widget sampler
tools/shoot.sh out.png [flags]                    # the same, screenshotted in a sealed session
tools/preview3.py / tools/shoot3.sh               # GTK 3
tools/build-shell.py [--check|--coverage]         # regenerate the Shell theme
tools/shoot-shell.sh OUTDIR [dark|light]          # screenshot a headless, fully themed GNOME Shell
tools/scheme-colors.py [--write|--check]          # contrast report; write the GtkSourceView and Tilix schemes
tools/scheme-shoot.sh out.png gsv|emacs [variant] # screenshot them
tools/term-shoot.sh out.png                       # ls colors in both terminal schemes, GNU defaults vs Neon Doll
tools/build-chrome.py [--check]                   # regenerate the Chrome themes
tools/chrome-shoot.py dark|light out.png          # screenshot one in a scratch Chrome profile
tools/build-firefox.py [--check]                  # regenerate the Firefox theme
tools/firefox-shoot.py dark|light out.png [--menu] [--userchrome]
                                                  # screenshot it in a scratch Firefox profile
tools/build-glow.py [--check]                     # regenerate the glow styles
tools/build-cursor.py [--check|--sheet out.png]   # regenerate the cursor theme from cursor/src/*.svg
tools/build-vim.py [--check]                      # regenerate the vim colorscheme from the editor schemes
tools/build-ghostty.py [--check]                  # regenerate the Ghostty themes from the Tilix schemes
tools/build-cosmic.py [--check]                   # regenerate the COSMIC themes and COSMIC Terminal schemes
tools/cosmic-shoot.sh OUTDIR [dark|light ...]     # screenshot them in a nested COSMIC (docker, software rendering)
tools/build-kde.py [--check]                      # regenerate the KDE and Qt parts: color schemes, Kvantum, global themes, Konsole, Kate, qt5ct/qt6ct
tools/kde-shoot.sh OUTDIR [dark|light ...]        # screenshot them in a nested Plasma (docker, software rendering)
tools/build-irssi.py [--check]                    # regenerate the irssi themes from the editor schemes
tools/irssi-shoot.sh OUTDIR                       # screenshot them, against a pretend IRC server on localhost
tools/ag-shoot.sh OUTDIR                          # screenshot ag through the alias
tools/build-windows.py [--check]                  # regenerate the Windows Terminal files from the Tilix schemes
tools/build-vscode.py [--check] [--vsix OUT]      # regenerate the VS Code themes and icon; --vsix packs the extension
tools/vscode-shoot.py dark|light out.png          # screenshot it in a scratch VS Code
tools/build-roundcube.py [--check] [--elastic DIR] # regenerate the Roundcube skin's palette and compile its CSS against Elastic
tools/roundcube-shoot.py OUTDIR [--scene NAME]    # screenshot it in a scratch Roundcube and IMAP server (docker), with a pretend mailbox
tools/dist.sh [VERSION]                           # release archives into dist/
```

The screenshot scripts need [shotbox](https://github.com/mishan/shotbox) on
your `PATH`: each program runs in a sealed session, with a scratch home and
none of your settings, and the picture is taken once it's ready rather than
after a guess. `tools/cosmic-shoot.sh` runs COSMIC in a Wayland shotbox
session inside its container, from a shotbox checkout beside this one (or
where `SHOTBOX_DIR` points). `tools/shoot-shell.sh` still runs its own
headless GNOME Shell, and `tools/roundcube-shoot.py` drives a headless
Chrome.

`tools/build-roundcube.py` compiles with lessc, which it runs through `npx`,
against Roundcube's Elastic sources, which it fetches once into
`~/.cache/neon-doll`; without either, it leaves the committed CSS alone and
says so. `tools/roundcube-shoot.py` needs docker and Chrome,
`tools/cosmic-shoot.sh` docker and shotbox, and `tools/kde-shoot.sh` docker
alone; those two build a Fedora image with their desktop. `KDE_SHOOT_PREVIEWS=1
tools/kde-shoot.sh` also redraws the global themes' preview images from the
desktop shot.

`tools/check-tokens.py` and `tools/check-tokens3.py` compare the palette
against the design system it came from; they need that project's
`system.css` as an argument.

## License

GPL-3.0-or-later. See [COPYING](COPYING).

The Roundcube skin is the exception: its own files are GPL-3.0-or-later or
CC BY-SA 4.0, your choice, and its compiled CSS, which contains Roundcube's
Elastic skin (CC BY-SA 3.0), is CC BY-SA 4.0. See
[`roundcube/neon-doll/README.md`](roundcube/neon-doll/README.md).
