# gnome-look.org listings

Three products, one per category. The two theme listings upload the same
`neon-doll-themes-VERSION.tar.xz` from `tools/dist.sh`, with the full
`neon-doll-VERSION.tar.xz` alongside it; the cursor listing uploads
`neon-doll-cursors-VERSION.tar.xz`. License: GPL-3.0-or-later.
Screenshots: `screenshots/`, the Shell overview first.

## GTK3/4 Themes — "Neon Doll"

Hot pink neon on midnight plum.

A desktop theme for GNOME and the tools around it. One fuchsia light marks
exactly where you are: the cursor, the current tab, the selected line. Violet
marks everything you can touch; the rest stays in the dark. Terminal type on
the chrome, soft sans for the words. Hard corners, no drop shadows, nothing
fades in. Cyberpunk, with a manicure. Dark and light.

Two themes: Neon-Doll-Dark and Neon-Doll-Light. Each covers GTK 3 and GNOME
Shell.

GTK 4 / libadwaita apps don't read GTK themes, so their part is a separate
stylesheet, ~/.config/gtk-4.0/gtk.css, which follows the system's light or
dark style on its own. It is in the full archive, or install everything with:

    git clone https://github.com/mishan/neon-doll.git
    cd neon-doll && ./install.sh

That also installs the rest of the set: color schemes for GNOME Text Editor,
Tilix and Emacs, and colors for ls, git, man pages and glow. Chrome and
Firefox themes are in the repository too, with instructions for loading them.

Tested on GNOME 51 (GTK 4.24, libadwaita 1.10, GTK 3.24).

Source, issues and the full install guide: https://github.com/mishan/neon-doll

## GNOME Shell Themes — "Neon Doll"

Hot pink neon on midnight plum, for the Shell: top bar, overview, quick
settings, calendar and notifications, OSDs, the app switcher, dialogs and the
lock screen. The same rules as the GTK theme: one fuchsia light for where you
are, violet for what you can touch, terminal type, hard corners, no shadows.
Dark and light.

Needs the User Themes extension. Unpack into ~/.themes or
~/.local/share/themes, then pick Neon-Doll-Dark or Neon-Doll-Light in User
Themes, or:

    gsettings set org.gnome.shell.extensions.user-theme name Neon-Doll-Dark

Pair it with the GTK theme of the same name for a matching desktop.

Also included: Neon-Doll-Dark-Hearts and Neon-Doll-Light-Hearts, the same
themes with one difference: Locate Pointer (press Ctrl) ripples out from the
pointer as a heart instead of a ring.

Known limits: the overview's workspace corners stay rounded and the slider
knob stays round, because the shell draws both in code; the login screen uses
the stock theme.

Source and the full install guide: https://github.com/mishan/neon-doll

## Cursors — "Neon Doll Cursors"

A black pointer with a hot pink neon edge. The arrow, the hand and the text
cursor glow faintly, since in Neon Doll fuchsia marks where you are; every
other cursor is black inside a thin light edge, easy to find on dark desktops,
light ones, and busy photos alike. One theme for both light and dark. Square
and flat, with no animation: wait is a still hourglass.

The full standard set that GNOME and GTK ask for, with the legacy X11 names
linked, at 24, 32, 48, 64 and 96 px.

Unpack into ~/.icons or ~/.local/share/icons, then:

    gsettings set org.gnome.desktop.interface cursor-theme Neon-Doll-Cursors

Screenshot: `screenshots/cursors.png`.

Source and the full install guide: https://github.com/mishan/neon-doll
