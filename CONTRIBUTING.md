# Working on Neon Doll

Every color is in [`tokens.toml`](tokens.toml), dark and light: the core
palette under the design system's names, and each tint as a color at an
alpha. `tools/tokens.py` reads it for the builders, and flattens the tints
onto the page for the themes that only take solid colors (the editor and
terminal schemes). Change a color there, then run `tools/build.sh`: it
rewrites every generated theme, and the palette copies inside the
hand-written ones (the GTK stylesheets and the Emacs themes, between
markers). `tools/build.sh --check` fails if anything is stale. Generated files
are committed, so installing needs nothing but `sh`.

The installers have tests, which run them against scratch home folders:
`tests/install.sh` for `install.sh` (`SH=dash` or another shell to run it
under that), and `tests/install.ps1` for `install.ps1`, under PowerShell 7 on
any system or Windows PowerShell 5.1. CI runs both on Linux, macOS and
Windows, with `tools/build.sh --check`, shellcheck and PSScriptAnalyzer.

```
tests/install.sh                                  # test install.sh
pwsh tests/install.ps1                            # test windows/install.ps1
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
your `PATH` (`pipx install --system-site-packages shotbox`): each program
runs in a sealed session, with a scratch home and none of your settings,
and the picture is taken once it's ready rather than after a guess.
`tools/cosmic-shoot.sh` runs COSMIC in a Wayland shotbox session inside its
container, which has its own shotbox, pinned; `SHOTBOX_DIR` runs a checkout
of shotbox there instead. `tools/shoot-shell.sh` still runs its own
headless GNOME Shell, and `tools/roundcube-shoot.py` drives a headless
Chrome.

`tools/build-roundcube.py` compiles with lessc, which it runs through `npx`,
against Roundcube's Elastic sources, which it fetches once into
`~/.cache/neon-doll`; without either, it leaves the committed CSS alone and
says so. `tools/roundcube-shoot.py` needs docker and Chrome,
and `tools/cosmic-shoot.sh` and `tools/kde-shoot.sh` docker alone; those
two build a Fedora image with their desktop. `KDE_SHOOT_PREVIEWS=1
tools/kde-shoot.sh` also redraws the global themes' preview images from the
desktop shot.

`tools/check-tokens.py` and `tools/check-tokens3.py` compare the palette
against the design system it came from; they need that project's
`system.css` as an argument.
