#!/bin/sh
# Install Neon Doll.
#
#   ./install.sh [--link] [--remove] [PART...]
#
# PART is any of: gtk4 gtk3 shell cursor gtksourceview tilix emacs dircolors git man glow newt ag ghostty vim irssi
# (default: all).
# Files are copied; --link symlinks them into this checkout instead, so edits
# here show up on the next app launch. --remove takes out only what install
# put in: links, and copies that still match this checkout.
#
# Nothing is switched on: gsettings and app preferences are left alone, and
# the commands to turn each part on are printed at the end.
set -eu

here=$(cd "$(dirname "$0")" && pwd)
config=${XDG_CONFIG_HOME:-$HOME/.config}
data=${XDG_DATA_HOME:-$HOME/.local/share}
emacs_dir=${EMACS_THEMES_DIR:-$HOME/.emacs.d/themes}

mode=copy
parts=
for arg in "$@"; do
  case $arg in
    --link) mode=link ;;
    --remove) mode=remove ;;
    -h|--help) sed -n '2,13s/^# \{0,1\}//p' "$0"; exit 0 ;;
    gtk4|gtk3|shell|cursor|gtksourceview|tilix|emacs|dircolors|git|man|glow|newt|ag|ghostty|vim|irssi) parts="$parts $arg" ;;
    *) echo "unknown argument: $arg" >&2; exit 2 ;;
  esac
done
[ -n "$parts" ] || parts="gtk4 gtk3 shell cursor gtksourceview tilix emacs dircolors git man glow newt ag ghostty vim irssi"

same() { diff -rq "$1" "$2" >/dev/null 2>&1; }

# place SRC DEST: copy, link or remove one file or directory.
place() {
  src=$1 dst=$2
  if [ "$mode" = remove ]; then
    if [ -L "$dst" ] || { [ -e "$dst" ] && same "$src" "$dst"; }; then
      rm -rf "$dst"; echo "removed $dst"
    elif [ -e "$dst" ]; then
      echo "left $dst alone: it differs from this checkout"
    fi
    return
  fi
  mkdir -p "$(dirname "$dst")"
  # A real file of the user's own is moved aside, never overwritten.
  if [ -e "$dst" ] && [ ! -L "$dst" ] && ! same "$src" "$dst"; then
    mv "$dst" "$dst.bak.$(date +%Y%m%d%H%M%S)"
    echo "moved existing $dst aside"
  fi
  rm -rf "$dst"
  if [ "$mode" = link ]; then
    ln -s "$src" "$dst"
  else
    cp -RL "$src" "$dst"   # -L: the theme dirs share CSS through relative links
  fi
  echo "$dst"
}

hints=
hint() { hints="$hints
  $*"; }
themes_done=

for part in $parts; do
  case $part in
    gtk4)
      place "$here/gtk-4.0/gtk.css" "$config/gtk-4.0/gtk.css"
      hint "GTK 4 / libadwaita: restart apps. Light or dark follows Settings → Appearance."
      ;;
    gtk3|shell)
      # GTK 3 and the Shell share the two theme dirs; install them once.
      if [ -z "$themes_done" ]; then
        themes_done=1
        for t in "$here"/themes/*/; do
          t=${t%/}
          place "$t" "$data/themes/$(basename "$t")"
        done
      fi
      if [ "$part" = gtk3 ]; then
        hint "GTK 3: gsettings set org.gnome.desktop.interface gtk-theme Neon-Doll-Dark   # or Neon-Doll-Light"
      else
        hint "Shell: gsettings set org.gnome.shell.extensions.user-theme name Neon-Doll-Dark   # or Neon-Doll-Light; add -Hearts for a heart-shaped Locate Pointer; needs the User Themes extension"
      fi
      ;;
    cursor)
      # A cursor theme is an icon theme, not a GTK one: it goes under icons/.
      place "$here/icons/Neon-Doll-Cursors" "$data/icons/Neon-Doll-Cursors"
      hint "Cursor: gsettings set org.gnome.desktop.interface cursor-theme Neon-Doll-Cursors   # one theme for light and dark"
      ;;
    gtksourceview)
      for f in "$here"/gtksourceview/*.xml; do
        place "$f" "$data/gtksourceview-5/styles/$(basename "$f")"
      done
      for f in "$here"/gtksourceview/gtksourceview-4/*.xml; do
        place "$f" "$data/gtksourceview-4/styles/$(basename "$f")"
      done
      hint "Text Editor: pick Neon Doll in the style menu; it follows light and dark on its own."
      ;;
    tilix)
      for f in "$here"/tilix/*.json; do
        place "$f" "$config/tilix/schemes/$(basename "$f")"
      done
      hint "Tilix: restart it, then Preferences → Profile → Color → Color scheme."
      ;;
    emacs)
      for f in "$here"/emacs/*.el; do
        place "$f" "$emacs_dir/$(basename "$f")"
      done
      hint "Emacs: (add-to-list 'custom-theme-load-path \"$emacs_dir\") (load-theme 'neon-doll-dark t)"
      ;;
    git)
      place "$here/git/neon-doll.gitconfig" "$config/neon-doll/gitconfig"
      hint "git: git config --global include.path $config/neon-doll/gitconfig   # after any [color] sections of your own, or they win"
      ;;
    glow)
      for f in "$here"/glow/neon-doll-*.json; do
        place "$f" "$config/neon-doll/glow/$(basename "$f")"
      done
      hint "glow: set  style: \"$config/neon-doll/glow/neon-doll-dark.json\"  in ~/.config/glow/glow.yml (or -light); the full path, since glow doesn't expand ~"
      ;;
    vim)
      place "$here/vim/colors/neon-doll.vim" "$HOME/.vim/colors/neon-doll.vim"
      hint "vim: add to ~/.vimrc:  colorscheme neon-doll   (set background=light for the light variant; set termguicolors for exact colors)"
      ;;
    irssi)
      for f in "$here"/irssi/*.theme; do
        place "$f" "$HOME/.irssi/$(basename "$f")"
      done
      hint "irssi: /set theme neon-doll  (or neon-doll-light), and  /set colors_ansi_24bit on  for the exact colors; then /save"
      ;;
    ghostty)
      for f in "$here"/ghostty/themes/*; do
        place "$f" "$config/ghostty/themes/$(basename "$f")"
      done
      hint "Ghostty: add to ~/.config/ghostty/config.ghostty:  theme = light:Neon Doll Light,dark:Neon Doll Dark"
      ;;
    newt)
      place "$here/newt/neon-doll.sh" "$config/neon-doll/newt.sh"
      hint "whiptail/debconf: add to ~/.bashrc:  . $config/neon-doll/newt.sh"
      ;;
    ag)
      place "$here/ag/neon-doll.sh" "$config/neon-doll/ag.sh"
      hint "ag: add to ~/.bashrc:  . $config/neon-doll/ag.sh"
      ;;
    man)
      place "$here/man/neon-doll.sh" "$config/neon-doll/man.sh"
      hint "man: add to ~/.bashrc:  . $config/neon-doll/man.sh"
      ;;
    dircolors)
      place "$here/dircolors/neon-doll" "$config/neon-doll/dircolors"
      hint "ls: add to ~/.bashrc:  eval \"\$(dircolors -b $config/neon-doll/dircolors)\""
      ;;
  esac
done

if [ "$mode" != remove ] && [ -n "$hints" ]; then
  echo
  echo "To turn it on:$hints"
fi
