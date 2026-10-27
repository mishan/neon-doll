# Installing Neon Doll

- [The installer](#the-installer)
- [GNOME](#gnome): [GTK 4](#gtk-4--libadwaita), [GTK 3 and 2](#gtk-3-and-2), [Shell](#gnome-shell), [cursor](#cursor), [Text Editor](#text-editor)
- [COSMIC](#cosmic): [desktop](#cosmic-desktop), [Terminal](#cosmic-terminal)
- [KDE Plasma and Qt](#kde-plasma-and-qt): [Plasma](#kde-plasma), [Kvantum](#kvantum), [Konsole](#konsole), [Kate](#kate), [qt5ct and qt6ct](#qt5ct-qt6ct)
- [Terminals and the command line](#terminals-and-the-command-line): [Tilix](#tilix), [Ghostty](#ghostty), [`ls`](#ls-colors), [`git`](#git-colors), [`ag`](#ag), [man pages](#man-pages), [glow](#glow), [`whiptail`](#whiptail), [irssi](#irssi)
- [Editors](#editors): [VS Code](#vs-code), [vim](#vim), [Emacs](#emacs-29)
- [Browsers](#browsers): [Chrome](#chrome), [Firefox](#firefox)
- [Windows](#windows): [Terminal and PowerShell](#windows-terminal-and-powershell), [the desktop](#the-windows-desktop), [the taskbar and Start](#the-taskbar-and-start-windhawk)
- [Roundcube](#roundcube)
- [Light and dark](#light-and-dark)
- [High contrast](#high-contrast)

## The installer

```sh
git clone https://github.com/mishan/neon-doll.git && cd neon-doll
./install.sh                  # asks which parts
./install.sh all              # every part that fits this system
./install.sh gtk4 shell       # or name them: gtk4 gtk3 shell cursor gtksourceview cosmic kde kvantum konsole kate qtct tilix ghostty vscode firefox emacs vim irssi git dircolors man glow ag newt
./install.sh --remove         # take it out again
./install.sh --desktop-grid gtk4   # graph paper over the wallpaper too (with Desktop Icons NG)
```

Run from a terminal with no parts named, `install.sh` lists the parts that fit
the system, ticks the ones whose apps it finds, and asks, in whiptail or
dialog if either is there and as a numbered list if not. On macOS it offers
only the parts that make sense there, the terminal and editor ones; the
desktop parts are for Linux and the BSDs. If Firefox has more than one
profile it asks which get `userChrome.css`, and if Desktop Icons NG is on it
asks whether the graph paper goes over the wallpaper too. Without a terminal
to ask in, it installs every part that fits.

`install.sh` copies files into your home directory and changes no settings; it
prints what to switch on afterwards. `--link` symlinks instead of copying, so
edits in the checkout show up on the next app launch. Each section below says
which part to name, where it goes, and how to turn it on.

On Windows, see [Windows](#windows).

Tested on GNOME 51 with GTK 4.24, libadwaita 1.10 and GTK 3.24, Chrome 154,
Firefox 156, VS Code 1.139 and Roundcube 1.7.4 and 1.6.18 (upstream and
Debian 13's package).

Apps that paint their own colors — Electron apps, terminals other than the
ones below — pick up little or nothing.

## GNOME

### GTK 4 / libadwaita

Part `gtk4`, into `~/.config/gtk-4.0/gtk.css`.

Restart apps. Light or dark follows Settings → Appearance; its accent color
doesn't, as fuchsia is Neon Doll's own accent (the Shell keeps it too). Window
backgrounds are graph paper, but not the desktop: Desktop Icons NG draws its
icons in a transparent GTK 4 window over the wallpaper, so the paper would
land on the wallpaper too. Install with `--desktop-grid` to have it there as
well.

### GTK 3 and 2

Part `gtk3`, into `~/.local/share/themes/Neon-Doll{,-dark}/`.

`gsettings set org.gnome.desktop.interface gtk-theme Neon-Doll-dark`, or
`Neon-Doll` for light. (Before, they were `Neon-Doll-Dark` and
`Neon-Doll-Light`: switch to the new names, then delete the old
`Neon-Doll-Dark*` and `Neon-Doll-Light*` folders and their `~/.themes` links.)
The names pair the way theme switchers expect (as `Adwaita` and `Adwaita-dark`
do), so an extension like [Legacy (GTK3) Theme Scheme Auto
Switcher](https://extensions.gnome.org/extension/4998/) can follow Settings →
Appearance; GTK 3 itself can't. The same setting reaches GTK 2 apps like
HexChat: they get Adwaita's GTK 2 widgets in Neon Doll's colors, so they need
Adwaita's GTK 2 theme (`gnome-themes-extra`).

GTK 3 has no `:focus-visible`, so its focus ring appears only once the
keyboard is in use. Message-dialog headings stay bold.

### GNOME Shell

Part `shell`, into the same two theme dirs, plus `Neon-Doll{,-dark}-Hearts`,
and the Neon Doll extension.

The extension puts the theme on, and switches it the way the Shell switches
its own: light or dark with Settings → Appearance, and the Shell's
high-contrast theme while High Contrast is on. Log out and in once, so the
Shell sees it, turn User Themes off if it's on, then
`gnome-extensions enable neon-doll@mishan.github.io`. Its one setting,
`gnome-extensions prefs neon-doll@mishan.github.io`, makes Locate Pointer
(press Ctrl) ripple out as a heart instead of a ring.

Without the extension, [User Themes](https://extensions.gnome.org/extension/19/user-themes/)
takes one of the four by name and keeps it:
`gsettings set org.gnome.shell.extensions.user-theme name Neon-Doll-dark`.

The Shell draws a few things in code, out of a theme's reach: the overview's
rounded workspace corners, the round slider knob, and the handle's slide. The
login screen uses the stock theme.

### Cursor

Part `cursor`, into `~/.local/share/icons/Neon-Doll-Cursors/`.

`gsettings set org.gnome.desktop.interface cursor-theme Neon-Doll-Cursors`. One
theme for light and dark: black, with a 1 px light edge that finds it on dark
backgrounds. The everyday pointers, the arrow, the hand and the text beam, are
edged in fuchsia instead, with a faint halo, since they are where you are. The
size is Settings → Accessibility → Seeing → Cursor Size; every size from 24 to
96 is drawn.

The cursor doesn't move: wait is a still hourglass, and progress the arrow
with a small one. Names it doesn't have, such as the hashed ones a few older
Qt and X apps ask for, fall back to Adwaita's.

### Text Editor

Part `gtksourceview`, into `~/.local/share/gtksourceview-5/styles/` (and `-4`).

Pick Neon Doll in the style menu.

## COSMIC

### COSMIC desktop

Part `cosmic`, into `~/.config/neon-doll/cosmic/`.

`cosmic-settings appearance import ~/.config/neon-doll/cosmic/Neon-Doll-Dark.ron`,
then the same with `-Light`; each lands in its own mode, and COSMIC switches
between them as it does its own. Or Settings → Desktop → Appearance → Import.
The page, the panel as containers, ink as the text tint, purple as the accent,
fuchsia on the focused window's outline, square corners, nothing frosted;
COSMIC derives the rest. Leave *Apply this theme to GNOME apps* off: it
replaces `~/.config/gtk-4.0/gtk.css` with COSMIC's own.

COSMIC themes are a handful of seed colors that COSMIC derives every surface
and state from, so purple, the accent, is also the focus ring and the
selection, and fuchsia marks only the focused window. Fonts are COSMIC's own
setting, not the theme's, and the desktop has no graph paper unless you set
one as the wallpaper. Tested only in a nested COSMIC 1.8
(`tools/cosmic-shoot.sh`), where COSMIC Terminal started on its dark scheme in
light mode unless its own View → Settings → Theme was set to Light.

### COSMIC Terminal

Part `cosmic`, into `~/.config/neon-doll/cosmic/terminal/`.

View → Color schemes… → Import, and pick `Neon Doll Dark.ron`; the list is the
current mode's, so switch to light and import `Neon Doll Light.ron` there. The
Tilix colors.

## KDE Plasma and Qt

### KDE Plasma

Part `kde`, into `~/.local/share/color-schemes/`, `~/.local/share/plasma/look-and-feel/`.

`kvantummanager --set NeonDoll` (the kvantum part), then System Settings →
Colors & Themes → Global Theme → Neon Doll Dark or Light. The global theme
sets the color scheme, Kvantum, the cursor and the chrome fonts: toolbars,
menus and window titles in your monospace font. To follow the time of day,
turn on *Switch to Dark Mode at Night* on that page and pick the two there;
Kvantum switches with them. Window decorations and the Plasma style stay
Breeze's, in Neon Doll's colors. For the colors alone, on Breeze's shapes:
`plasma-apply-colorscheme NeonDollDark`.

Plasma keeps Breeze for the window decorations and the Plasma style, so title
bars, the panel and its popups take Neon Doll's colors but keep Breeze's
rounded corners and shadows, and the focused window has no fuchsia outline.
Kirigami apps, System Settings among them, reach Kvantum through KDE's Qt
Quick style and draw a few controls of their own, like the switch. Breeze's
folder icons take the selection color, so folders are plum in dark and pink in
light. Tested only in a nested Plasma 6.7 with Kvantum 1.1.6 and KDE Gear
26.08 (`tools/kde-shoot.sh`).

### Kvantum

Part `kvantum`, into `~/.config/Kvantum/NeonDoll/`.

`kvantummanager --set NeonDoll`, then the widget style `kvantum-dark`, or
`kvantum` for light: the theme is NeonDoll, and its dark variant NeonDollDark.
The shapes for every Qt app, which Breeze and a color scheme can't change:
square buttons and fields with a visible edge, the rail on the selected row
and across the current tab, graph paper in the windows, no shadows. Outside
Plasma, set `QT_STYLE_OVERRIDE=kvantum-dark`, or pick it in qt6ct.

Kvantum draws its focus frame whenever a widget has focus, so a clicked item
gets a fuchsia box, not only one reached from the keyboard. A selected tree
row carries its rail at the item's indent rather than the row's edge.
QToolBox keeps Qt's slanted tab outline.

### Konsole

Part `konsole`, into `~/.local/share/konsole/`.

Settings → Manage Profiles → Neon Doll Dark (or Light) → Set as Default. The
Tilix colors; the profile carries the fuchsia cursor, which a Konsole color
scheme can't.

### Kate

Part `kate`, into `~/.local/share/org.kde.syntax-highlighting/themes/`.

Settings → Configure Kate → Color Themes. KWrite, KDevelop and anything else
on KTextEditor list it too. The editor schemes' four syntax colors.

### qt5ct, qt6ct

Part `qtct`, into `~/.config/qt5ct/colors/`, `~/.config/qt6ct/colors/`.

Appearance → Palette → Custom → NeonDollDark (or NeonDollLight), for Qt apps
outside Plasma on the Fusion style. With Kvantum, apps take its colors
instead.

## Terminals and the command line

The terminal schemes assign black and white by role, not lightness: black
is the page's edge color and bright white is the text color in both
variants. In the light schemes that makes black a pale gray, so text a
program prints in black, assuming a light page, almost vanishes; text it
prints in white, assuming a dark one, stays readable.

### Tilix

Part `tilix`, into `~/.config/tilix/schemes/`.

Restart Tilix; Preferences → Profile → Color.

### Ghostty

Part `ghostty`, into `~/.config/ghostty/themes/`.

`theme = light:Neon Doll Light,dark:Neon Doll Dark` in
`~/.config/ghostty/config.ghostty`, which follows the system style. The Tilix
colors, plus a border-colored split divider, unfocused splits fading toward
the page, and search matches in purple with the current one in fuchsia. Its
tabs and header bar are libadwaita, so they take the GTK 4 stylesheet.

### `ls` colors

Part `dircolors`, into `~/.config/neon-doll/dircolors`.

`eval "$(dircolors -b ~/.config/neon-doll/dircolors)"` in `~/.bashrc`. Uses
only the 16 terminal colors, so it follows either Neon Doll terminal scheme;
odd permissions are underlined rather than filled.

### `git` colors

Part `git`, into `~/.config/neon-doll/gitconfig`.

`git config --global include.path ~/.config/neon-doll/gitconfig`, placed after
any `[color]` sections of your own. Diff, log, status, branch, grep and
`add -p`, in the 16 terminal colors; nothing bold.

### `ag`

Part `ag`, into `~/.config/neon-doll/ag.sh`.

`. ~/.config/neon-doll/ag.sh` in `~/.bashrc`. ag has no config file, so it's
an alias with ag's three color flags: file names purple, line numbers muted,
matches purple and underlined, as `git grep` has them under the Neon Doll git
colors. Nothing bold, and only the 16 terminal colors.

### man pages

Part `man`, into `~/.config/neon-doll/man.sh`.

`. ~/.config/neon-doll/man.sh` in `~/.bashrc`. Headings and literal options
purple, arguments cyan and underlined, nothing bold; only `man`'s pager
changes, not `less` in general.

### glow

Part `glow`, into `~/.config/neon-doll/glow/`.

`alias glow='glow -s ~/.config/neon-doll/glow/neon-doll-dark.json'` (or
`-light`) in `~/.bashrc`, or the full path as `style:` in
`~/.config/glow/glow.yml`; glow doesn't expand `~` there. Markdown as a man
page: capitalized purple section headings, code in the editor schemes' colors.

### `whiptail`

Part `newt`, into `~/.config/neon-doll/newt.sh`.

`. ~/.config/neon-doll/newt.sh` in `~/.bashrc`. For whiptail and everything
built on newt, like debconf and `dpkg-reconfigure`: the box a panel with a
purple edge, the focused item reverse purple, no drop shadow. newt's own
colors assume a VGA console and wash out on this palette.

### irssi

Part `irssi`, into `~/.irssi/neon-doll{,-light}.theme`.

`/set theme neon-doll` (or `neon-doll-light`) and `/set colors_ansi_24bit on`,
then `/save`. The prompt, which names the window you're typing into, is
fuchsia; you and the channels are purple; lines that mention you, and the
windows holding them, are yellow; timestamps, hostmasks, joins and parts step
back into grey. Without 24-bit color irssi uses the nearest of the 256 colors.

## Editors

Line numbers in the editor schemes use the dimmest color on purpose and sit
below 4.5:1.

### VS Code

VS Code gets an extension with *Neon Doll Dark* and *Neon Doll Light*. Once
it's on the Marketplace and Open VSX, it installs from the Extensions view;
until then, the installers' `vscode` part copies it into the extensions folder
of VS Code, VSCodium, Cursor or Windsurf, whichever it finds. Or build it with
`tools/build-vscode.py --vsix neon-doll.vsix` (or take the `.vsix` from a
release) and run `code --install-extension neon-doll.vsix`, then pick the
theme with *Preferences: Color Theme*. The editor is the page and everything
around it a panel; the syntax is the editor schemes', the terminal the Tilix
colors. The current tab, the focused row, the active activity-bar item, the
selection and the current find match are fuchsia; links, badges and the
primary button, drawn as a purple wash with a purple edge, are purple.

VS Code themes set colors only, so corners and fonts stay VS Code's. Buttons
are fills, so the primary button is a purple wash with a purple edge rather
than a bare outline, and hover can change its fill but not its text. List rows
can't take a rail; the focused row is a fuchsia wash with fuchsia text
instead. Newer VS Code draws the side bar, editor and panel as rounded cards
and marks the active tab and activity-bar item with a pill rather than a rail;
the theme colors both layouts. The chat and agent views keep VS Code's colors.

### vim

Part `vim`, into `~/.vim/colors/neon-doll.vim`.

`colorscheme neon-doll` in `~/.vimrc`. One scheme for both variants: it
follows `background`. With `termguicolors` it uses the exact colors, matching
the other editors; without, it uses the 16 terminal colors and follows the
terminal's Neon Doll scheme.

### Emacs 29+

Part `emacs`, into `~/.emacs.d/themes/` (or `$EMACS_THEMES_DIR`).

`(add-to-list 'custom-theme-load-path "~/.emacs.d/themes/")`
`(load-theme 'neon-doll-dark t)`

Faces for magit, vertico and similar packages are set but untested; there are
no 256-color terminal specs.

## Browsers

### Chrome

Chrome can't be installed from a script. Open `chrome://extensions`, turn on
Developer mode, choose *Load unpacked* and pick `chrome/neon-doll-dark` or
`chrome/neon-doll-light`. Chrome themes are colors only, and one theme can't
follow the system's light or dark mode, so pick the one that matches it. The
current tab is the lifted panel, titled in fuchsia; the dark New Tab page gets
the graph paper, while the light one stays plain, since Chrome treats any New
Tab image as a photo and whitens the logo over it.

Tabs keep Chrome's rounded shapes, and focus rings and hover states stay
Chrome's own.

### Firefox

Firefox is one theme that carries both variants and follows the system's
light or dark mode. Until it's on addons.mozilla.org, load it for the session
from `about:debugging` → *This Firefox* → *Load Temporary Add-on*, picking
`firefox/manifest.json`; release Firefox only keeps signed add-ons across
restarts. The current tab is the lifted panel, titled and outlined in fuchsia;
the address bar is a slot that takes a fuchsia edge when focused; menus and the
address bar's results are panels, the highlighted result washed in fuchsia; and
the graph paper shows in the tab strip.

A theme sets colors only. For the shapes, `firefox/userChrome.css` squares the
corners, drops the shadows, sets the chrome in mono and turns the current tab's
outline into a rail across its top. It is optional: the installers' `firefox`
part copies it into the profile's `chrome/` folder (or copy it there yourself:
`about:support` → *Profile Folder*); then set
`toolkit.legacyUserProfileCustomizations.stylesheets` to `true` in
`about:config` and restart Firefox.

The current tab's indicator is an outline all round, so without
`userChrome.css` tabs and fields stay rounded, the chrome stays sans, and the
tab gets a fuchsia box rather than a rail. Hover can tint a toolbar button but
not turn its icon fuchsia. The account banner in the main menu and the New Tab
page's own buttons keep Firefox's colors. `userChrome.css` leans on Firefox's
internal design tokens, which can change in any release.

## Windows

### Windows Terminal and PowerShell

Unzip the Windows zip (or clone the repo), and open PowerShell in the
`neon-doll` folder: right-click it in Explorer and pick *Open in Terminal*. Use
the PowerShell you want colored, since Windows PowerShell 5.1 and PowerShell 7
keep separate profiles; Command Prompt can't run the installer. Then:

```powershell
Set-ExecutionPolicy Bypass -Scope Process -Force
.\windows\install.ps1
```

Windows runs no scripts by default, and none from a downloaded zip that aren't
signed, so without the first line PowerShell says running scripts is disabled
or that the script isn't digitally signed. `-Scope Process` lets just this
window run them, and lapses when it closes; nothing is changed for good. From
another folder, give the full path, with `&` in front when it's in quotes:
`& "C:\Users\you\Downloads\neon-doll\windows\install.ps1"`. A quoted path on
its own is only a string, which PowerShell prints back without running
anything.

`-Remove` takes it out again. Like `install.sh` it asks which
parts, with the ones it finds ticked, or takes them by name: `terminal`,
`powershell`, `accent` and `cursors` (below), and `vscode`, `firefox`, `git` and `vim` as on
Linux, or `all`. It copies the color schemes into Windows Terminal's Fragments
folder, where Terminal finds them on its own, and the PowerShell colors next to
your profile, then prints the two lines to add: pick *Neon Doll Dark* or
*Light* as the profile's color scheme, and dot-source `neon-doll.ps1` from
`$PROFILE`. Terminal reads the schemes when it starts, so close every
Terminal window first. PowerShell loads no profile while scripts are off for
you, which is Windows PowerShell's default; the installer says when they are,
and `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` turns them on for
your own scripts and the ones it unblocked.
The schemes are the Tilix ones entry for entry. The PowerShell
colors cover typing (commands and parameters purple, values cyan, strings
yellow, comments muted) and, on PowerShell 7.2+, `Get-ChildItem`, tables,
errors and progress, matching the `ls` colors. `Enable-NeonDollPrompt` adds
the bash prompt's look. The tab row's colors are a Terminal *theme*, which
fragments can't carry: paste the entries from `windows/terminal/themes.json`
into `settings.json`.

### The Windows desktop

Windows gets dark mode and the fuchsia accent, which go on Start, the taskbar,
title bars and window borders, and in toggles and selections inside apps. On
the taskbar and Start, Windows deepens it to a darker magenta.
They're Windows' own settings, so nothing is installed for them: part
`accent` prints the steps, which are, in *Settings → Personalization →
Colors*:

- *Choose your mode*: **Dark**
- *Accent color*: **Manual**, then *Custom colors → View colors → More*, and
  type in `FF2D95`
- *Show accent color on Start and taskbar*: **On**
- *Show accent color on title bars and window borders*: **On**

A Windows `.theme` file could set these with a double-click, but it resets
whatever it doesn't name, the pointers and sounds included, so there isn't
one.

Part `cursors`, offered but not ticked, adds the Neon Doll pointers to
Windows' list of pointer schemes, without switching to them: pick *Neon Doll*
under *Settings → Bluetooth & devices → Mouse → Additional mouse settings →
Pointers → Scheme*. They're the Linux cursors (black, the everyday ones edged
in fuchsia), at 32 to 96 px; the roles there's no Neon Doll cursor for
(handwriting, alternate select, location and person) keep Windows' own.
`-Remove` leaves them while they're in use.

### The taskbar and Start (Windhawk)

[Windhawk](https://windhawk.net) restyles the parts of Windows 11's shell
that no Windows theme reaches, through mods. Neon Doll has a theme for two of
them: `windows/windhawk/taskbar.yaml` for *Windows 11 Taskbar Styler* and
`windows/windhawk/start-menu.yaml` for *Windows 11 Start Menu Styler*. Both
follow Windows' light or dark mode on their own: plum or paper, square
corners and 1px edges, no drop shadow. The window you're in gets the fuchsia
rail and tint on its taskbar button, the others a purple rail; hover is the
purple wash; the clock, the search boxes and Start's headings are in Cascadia
Mono, which Windows 11 ships.

Windhawk works by loading itself into almost every program, so some antivirus
tools flag it and some games' anti-cheat won't start alongside it (Windhawk
skips the games it knows). `install.ps1` leaves it alone. To use it:

1. Install Windhawk from [windhawk.net](https://windhawk.net).
2. In Windhawk, *Explore → Windows 11 Taskbar Styler → Install*.
3. On the mod's *Settings* tab, pick *Textual mode*, replace the text with
   the contents of `windows/windhawk/taskbar.yaml`, and *Save settings*.
4. The same for *Windows 11 Start Menu Styler*, with `start-menu.yaml`.

Tested on Windows 11 25H2, with the Start menu's pinned-and-recommended
layout. Switching between light and dark while signed in can leave the
taskbar's search box in Windows' own shape until Explorer restarts (sign out
and back in).

## Roundcube

Roundcube gets a skin, a child of Elastic, the default one, which it needs
installed beside it. Copy `roundcube/neon-doll` into Roundcube's `skins/`
folder (or unpack the `neon-doll-roundcube` archive from a release there),
then pick *Neon Doll* in Settings → Preferences → User Interface, or set
`$config['skin'] = 'neon-doll';` to make it everyone's. One skin holds both
variants and follows Roundcube's own switch, the *Dark mode* / *Light mode*
button in the menu, which follows the system until it's pressed. The current
task, folder and message carry the fuchsia rail; unread mail is ink with a
purple dot and read mail is muted, flagged mail is yellow and deleted mail is
struck through, all at weight 400. The list and the message are the page, and
an empty preview pane is graph paper, as is the login page; the menu, the
folders and the header bars are panels. Its CSS is compiled against Roundcube
1.7.4's Elastic; for another version, rebuild it against that version's with
`tools/build-roundcube.py --elastic /path/to/roundcube/skins/elastic`.

Roundcube keeps Elastic's layout, icons and logo. HTML mail is the sender's
page: it keeps its own fonts, weights and corners, and in dark mode it sits on
white, as in Elastic, with the light colors around its links and quotes. The
HTML editor's page stays white too, since it is the message as it will be
sent.

## Light and dark

GTK 4, Text Editor, Firefox, Roundcube and COSMIC switch with the system style on
their own, and Plasma does once it has the two global themes as its pair.
So does the Shell, with the Neon Doll extension. GTK 3 can't: a GTK 3 theme
is one name, so there are two, `Neon-Doll` and `Neon-Doll-dark`, named the
way theme switcher extensions pair them (see [GTK 3 and 2](#gtk-3-and-2)).
GTK 3 apps that ask for a dark style get it from either. Tilix and Emacs have a
scheme per variant. VS Code switches when told to, in its settings:

```json
"window.autoDetectColorScheme": true,
"workbench.preferredDarkColorTheme": "Neon Doll Dark",
"workbench.preferredLightColorTheme": "Neon Doll Light"
```

## High contrast

GTK 4 apps follow Settings → Accessibility → High Contrast: every edge goes
to full strength, the selection goes solid, and the graph paper goes. With the
Neon Doll extension the Shell switches to its own high-contrast theme. GTK 3
can't follow it, since it takes one theme name: while it's on, set GTK 3's
theme to `HighContrast`.
