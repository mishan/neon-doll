# gnome-look.org listings

Two products, one per category, both uploading the same
`neon-doll-themes-VERSION.tar.xz` from `tools/dist.sh`, with the full
`neon-doll-VERSION.tar.xz` alongside it. License: GPL-3.0-or-later.
Screenshots: `screenshots/`, the Shell overview first.

## GTK3/4 Themes — "Neon Doll"

A GNOME theme that treats the desktop as a man page in a terminal that never
existed: near-black plum or plum-tinted paper, a fuchsia that means "you are
here", mono for the chrome and sans for what you read. No rounded corners, no
drop shadows, no transitions. Dark and light.

Two themes: Neon-Doll-Dark and Neon-Doll-Light. Each covers GTK 3 and GNOME
Shell.

GTK 4 / libadwaita apps don't read GTK themes, so their part is a separate
stylesheet, ~/.config/gtk-4.0/gtk.css. It is in the full archive, or install
everything with:

    git clone https://github.com/mishan/neon-doll.git
    cd neon-doll && ./install.sh

That also installs matching color schemes for GNOME Text Editor, Tilix and
Emacs.

Tested on GNOME 51 (GTK 4.24, libadwaita 1.10, GTK 3.24).

Source, issues and the full install guide: https://github.com/mishan/neon-doll

## GNOME Shell Themes — "Neon Doll"

The GNOME Shell half of Neon Doll: top bar, overview, quick settings, calendar
and notifications, OSDs, the app switcher, dialogs and the lock screen, in the
same plum, fuchsia and mono as the GTK theme. Dark and light.

Needs the User Themes extension. Unpack into ~/.themes or
~/.local/share/themes, then pick Neon-Doll-Dark or Neon-Doll-Light in User
Themes, or:

    gsettings set org.gnome.shell.extensions.user-theme name Neon-Doll-Dark

Pair it with the GTK theme of the same name for a matching desktop.

Known limits: the overview's workspace corners stay rounded and the slider
knob stays round, because the shell draws both in code; the login screen uses
the stock theme.

Source and the full install guide: https://github.com/mishan/neon-doll
