#!/bin/sh
# Install Neon Doll.
#
#   ./install.sh                  ask which parts, from a terminal
#   ./install.sh [--link] [--remove] [--desktop-grid] [all | PART...]
#
# With no PART and a terminal to ask in, it lists the parts that fit this
# system, the ones whose apps it finds already ticked, and asks. Without a
# terminal, or with `all`, it installs every part that fits. PART is any of:
#   gtk4 gtk3 shell cursor gtksourceview cosmic kde kvantum konsole kate qtct
#   tilix newt  (Linux and BSD)
#   ghostty vscode firefox emacs vim irssi git dircolors man glow ag
# Files are copied; --link symlinks them into this checkout instead, so edits
# here show up on the next app launch. --remove takes out only what install
# put in: links, and copies that still match this checkout. --desktop-grid
# keeps GTK 4's graph paper on the desktop too (over the wallpaper, under
# Desktop Icons NG's icons); by default it stops at app windows.
#
# Nothing is switched on: gsettings and app preferences are left alone, and
# the commands to turn each part on are printed at the end.
#
# It asks in whiptail, else dialog, else as a numbered list;
# NEON_DOLL_UI=whiptail, dialog or text picks one.
set -eu

here=$(cd "$(dirname "$0")" && pwd)
config=${XDG_CONFIG_HOME:-$HOME/.config}
data=${XDG_DATA_HOME:-$HOME/.local/share}
emacs_dir=${EMACS_THEMES_DIR:-$HOME/.emacs.d/themes}

all_parts="gtk4 gtk3 shell cursor gtksourceview cosmic kde kvantum konsole kate qtct tilix ghostty vscode firefox emacs vim irssi git dircolors man glow ag newt"

case $(uname -s) in
  Darwin) os=macos ;;
  MINGW*|MSYS*|CYGWIN*)
    echo "On Windows, run .\\windows\\install.ps1 from PowerShell instead." >&2
    exit 2 ;;
  *) os=linux ;;   # and the BSDs: the same desktops, the same paths
esac

usage() { awk 'NR > 1 && !/^#/ { exit } NR > 1 { sub(/^# ?/, ""); print }' "$0"; }

mode=copy
desktop_grid=
parts=
every=
for arg in "$@"; do
  case $arg in
    --link) mode="link" ;;
    --remove) mode=remove ;;
    --desktop-grid) desktop_grid=1 ;;
    -h|--help) usage; exit 0 ;;
    all) parts="$parts $all_parts" every=1 ;;
    gtk4|gtk3|shell|cursor|gtksourceview|tilix|emacs|dircolors|git|man|glow|newt|ag|ghostty|vim|irssi|cosmic|kde|kvantum|konsole|kate|qtct|vscode|firefox)
      parts="$parts $arg" ;;
    *) echo "unknown argument: $arg" >&2; exit 2 ;;
  esac
done

# --- What fits this system, and what's on it -------------------------------

have() { command -v "$1" >/dev/null 2>&1; }

# have_lib PATTERN: a shared library matching PATTERN in a usual lib dir.
have_lib() {
  for d in /usr/lib /usr/lib64 /usr/lib/*-linux-gnu /usr/local/lib /run/current-system/sw/lib; do
    for f in "$d"/$1; do
      [ -e "$f" ] && return 0
    done
  done
  return 1
}

have_flatpak() { [ -d "$data/flatpak/app/$1" ] || [ -d "/var/lib/flatpak/app/$1" ]; }

have_app() {
  [ "$os" = macos ] && { [ -d "/Applications/$1.app" ] || [ -d "$HOME/Applications/$1.app" ]; }
}

# Desktop Icons NG, the one thing that shows GTK 4 windows over the wallpaper.
have_ding() {
  for d in "$data/gnome-shell/extensions" /usr/share/gnome-shell/extensions; do
    for e in ding@rastersoft.com gtk4-ding@smedius.gitlab.com; do
      [ -d "$d/$e" ] && return 0
    done
  done
  return 1
}

# fits PART: whether PART means anything on this OS at all.
fits() {
  case $1 in
    gtk4|gtk3|shell|cursor|gtksourceview|cosmic|kde|kvantum|konsole|kate|qtct|tilix|newt) [ "$os" = linux ] ;;
    *) true ;;
  esac
}

# The extensions dirs of VS Code and the editors built from it, one a line.
vscode_dirs() {
  {
    for e in code:.vscode codium:.vscode-oss code-oss:.vscode-oss cursor:.cursor windsurf:.windsurf; do
      if [ -d "$HOME/${e#*:}" ] || have "${e%%:*}"; then
        echo "$HOME/${e#*:}/extensions"
      fi
    done
    have_flatpak com.visualstudio.code && echo "$HOME/.var/app/com.visualstudio.code/data/vscode/extensions"
    have_flatpak com.vscodium.codium && echo "$HOME/.var/app/com.vscodium.codium/data/codium/extensions"
  } | awk '!seen[$0]++'
}

# Firefox's profiles, one a line: DIR<tab>NAME<tab>1 if it's a default.
firefox_profiles() {
  if [ "$os" = macos ]; then
    echo "$HOME/Library/Application Support/Firefox"
  else
    # Firefox 147 and later start new profiles under XDG_CONFIG_HOME.
    printf '%s\n' "$config/mozilla/firefox" "$HOME/.mozilla/firefox" \
      "$HOME/snap/firefox/common/.mozilla/firefox" \
      "$HOME/.var/app/org.mozilla.firefox/config/mozilla/firefox" \
      "$HOME/.var/app/org.mozilla.firefox/.mozilla/firefox"
  fi | while IFS= read -r root; do
    [ -f "$root/profiles.ini" ] || continue
    awk -v root="$root" '
      { sub(/\r$/, "") }
      /^\[/ { sec = $0; if (sec ~ /^\[Profile/) order[++n] = sec; next }
      { eq = index($0, "="); key = substr($0, 1, eq - 1); val = substr($0, eq + 1) }
      sec ~ /^\[Profile/ { p[sec, key] = val }
      sec ~ /^\[Install/ && key == "Default" { dflt[val] = 1 }
      END {
        for (i = 1; i <= n; i++) {
          s = order[i]; path = p[s, "Path"]
          if (path == "") continue
          dir = p[s, "IsRelative"] == "0" ? path : root "/" path
          name = p[s, "Name"] != "" ? p[s, "Name"] : path
          print dir "\t" name "\t" (dflt[path] || p[s, "Default"] == "1" ? 1 : 0)
        }
      }' "$root/profiles.ini"
  done | while IFS= read -r line; do
    [ -d "${line%%	*}" ] && printf '%s\n' "$line"
  done
}

# The profiles to use when nobody picked: the default ones, or every one if
# none is marked.
firefox_default_dirs() {
  profiles=$(firefox_profiles)
  dirs=$(printf '%s\n' "$profiles" | awk -F '\t' '$3 == 1 { print $1 }')
  [ -n "$dirs" ] || dirs=$(printf '%s\n' "$profiles" | cut -f1)
  printf '%s\n' "$dirs"
}

# found PART: whether the app PART themes seems to be installed.
found() {
  case $1 in
    gtk4) have_lib 'libgtk-4.so*' ;;
    gtk3) have_lib 'libgtk-3.so*' ;;
    shell) have gnome-shell ;;
    cursor) [ -n "${XDG_CURRENT_DESKTOP:-}${WAYLAND_DISPLAY:-}${DISPLAY:-}" ] || have gsettings ;;
    gtksourceview) have_lib 'libgtksourceview-[45].so*' || have gnome-text-editor || have gedit ;;
    cosmic)
      have cosmic-comp || have cosmic-settings ||
        case ${XDG_CURRENT_DESKTOP:-} in *COSMIC*) true ;; *) false ;; esac ;;
    kde) have plasmashell || have plasma-apply-colorscheme ;;
    kvantum) have kvantummanager ;;
    konsole) have konsole || have_flatpak org.kde.konsole ;;
    kate) have kate || have kwrite || have_flatpak org.kde.kate ;;
    qtct) have qt5ct || have qt6ct ;;
    tilix) have tilix || have_flatpak com.gexperts.Tilix ;;
    ghostty) have ghostty || have_flatpak com.mitchellh.ghostty || have_app Ghostty ;;
    vscode) [ -n "$(vscode_dirs)" ] ;;
    firefox) [ -n "$(firefox_profiles)" ] ;;
    emacs) have emacs || have_app Emacs ;;
    vim) have vim ;;
    irssi) have irssi ;;
    git) have git ;;
    dircolors) have dircolors || have gdircolors ;;
    man) have man && have less ;;
    glow) have glow ;;
    ag) have ag ;;
    newt) have whiptail ;;
  esac
}

label() {
  case $1 in
    gtk4) echo "GTK 4 / libadwaita apps" ;;
    gtk3) echo "GTK 3 and GTK 2 apps" ;;
    shell) echo "GNOME Shell" ;;
    cursor) echo "Mouse cursor" ;;
    gtksourceview) echo "Text Editor and GtkSourceView apps" ;;
    cosmic) echo "COSMIC desktop and COSMIC Terminal" ;;
    kde) echo "KDE Plasma colors and global themes" ;;
    kvantum) echo "Kvantum widget style (Qt apps)" ;;
    konsole) echo "Konsole" ;;
    kate) echo "Kate and KWrite" ;;
    qtct) echo "qt5ct / qt6ct palettes" ;;
    tilix) echo "Tilix" ;;
    ghostty) echo "Ghostty" ;;
    vscode) echo "VS Code, VSCodium, Cursor" ;;
    firefox) echo "Firefox's userChrome.css (shapes)" ;;
    emacs) echo "Emacs" ;;
    vim) echo "vim" ;;
    irssi) echo "irssi" ;;
    git) echo "git colors" ;;
    dircolors) echo "ls colors" ;;
    man) echo "man pages" ;;
    glow) echo "glow" ;;
    ag) echo "ag" ;;
    newt) echo "whiptail and debconf" ;;
  esac
}

# --- Asking ----------------------------------------------------------------

case ${NEON_DOLL_UI:-} in
  whiptail|dialog|text) ui=$NEON_DOLL_UI ;;
  *)
    if have whiptail; then ui=whiptail
    elif have dialog; then ui=dialog
    else ui=text
    fi ;;
esac

# checklist TITLE TEXT ITEMS [notags]: ITEMS is TAG|LABEL|ON-or-OFF lines.
# Prints the tags picked, one a line; fails if cancelled.
checklist() {
  title=$1 text=$2 items=$3 notags=${4:-}
  n=$(printf '%s\n' "$items" | wc -l)
  if [ "$ui" = text ]; then
    text_checklist "$title" "$text" "$items" "$notags"
    return
  fi
  rows=$(stty size </dev/tty 2>/dev/null | cut -d' ' -f1) || rows=
  cols=$(stty size </dev/tty 2>/dev/null | cut -d' ' -f2) || cols=
  rows=${rows:-24} cols=${cols:-80}
  list=$n
  [ "$list" -le $((rows - 9)) ] || list=$((rows - 9))
  [ "$list" -ge 3 ] || list=3
  width=76
  [ "$width" -le $((cols - 4)) ] || width=$((cols - 4))
  set --
  if [ -n "$notags" ]; then
    if [ "$ui" = whiptail ]; then set -- --notags; else set -- --no-tags; fi
  fi
  set -- "$@" --checklist "$text" $((list + 8)) "$width" "$list"
  while IFS='|' read -r tag text_ state; do
    set -- "$@" "$tag" "$text_" "$state"
  done <<EOF
$items
EOF
  (
    # whiptail in the theme's own newt colors, unless you have yours.
    [ "$ui" != whiptail ] || [ -n "${NEWT_COLORS:-}" ] || . "$here/newt/neon-doll.sh"
    "$ui" --title "$title" --separate-output "$@" 3>&1 1>&2 2>&3
  )
}

text_checklist() {
  title=$1 text=$2 items=$3 notags=$4
  {
    echo
    echo "$title"
    echo "$text" | fold -s -w 76
  } >/dev/tty
  while :; do
    echo >/dev/tty
    printf '%s\n' "$items" | awk -F '|' -v notags="$notags" '
      { printf "  %2d  [%s] ", NR, $3 == "ON" ? "x" : " " }
      notags { print $2; next }
      { printf "%-14s %s\n", $1, $2 }' >/dev/tty
    printf '\nNumbers to tick or untick, a for all, n for none, Enter to go on, q to quit: ' >/dev/tty
    IFS= read -r reply </dev/tty || return 1
    case $reply in
      '') break ;;
      q|Q) return 1 ;;
    esac
    for r in $reply; do
      items=$(printf '%s\n' "$items" | awk -F '|' -v r="$r" 'BEGIN { OFS = "|" }
        r == "a" || r == "A" { $3 = "ON" }
        r == "n" || r == "N" { $3 = "OFF" }
        r == NR { $3 = $3 == "ON" ? "OFF" : "ON" }
        { print }')
    done
  done
  printf '%s\n' "$items" | awk -F '|' '$3 == "ON" { print $1 }'
}

# yesno TITLE TEXT: fails for no, the default.
yesno() {
  if [ "$ui" = text ]; then
    printf '\n%s\n' "$2" | fold -s -w 76 >/dev/tty
    printf '[y/N] ' >/dev/tty
    IFS= read -r reply </dev/tty || return 1
    case $reply in y|Y|yes|Yes) return 0 ;; *) return 1 ;; esac
  fi
  (
    [ "$ui" != whiptail ] || [ -n "${NEWT_COLORS:-}" ] || . "$here/newt/neon-doll.sh"
    "$ui" --title "$1" --defaultno --yesno "$2" 12 72
  )
}

has_part() { case " $parts " in *" $1 "*) true ;; *) false ;; esac; }

firefox_dirs=
firefox_picked=

if [ -z "$parts" ] && [ "$mode" != remove ] && [ -t 0 ] && [ -t 1 ]; then
  items=
  for part in $all_parts; do
    fits "$part" || continue
    if found "$part"; then
      items="$items$part|$(label "$part")|ON
"
    else
      items="$items$part|$(label "$part") (not found)|OFF
"
    fi
  done
  items=${items%?}   # the last newline
  verb=Install; [ "$mode" = link ] && verb=Link
  keys=
  [ "$ui" = text ] || keys=" Space ticks, Enter goes on."
  if ! picked=$(checklist "Neon Doll" "$verb which parts? The apps found on this system are ticked.$keys" "$items"); then
    echo "Nothing installed."
    exit 0
  fi
  if [ -z "$picked" ]; then
    echo "Nothing picked."
    exit 0
  fi
  parts=$(printf '%s\n' "$picked" | tr '\n' ' ')

  # More than one Firefox profile: which ones.
  if has_part firefox; then
    profiles=$(firefox_profiles)
    if [ "$(printf '%s\n' "$profiles" | grep -c .)" -gt 1 ]; then
      items=$(printf '%s\n' "$profiles" | awk -F '\t' '
        { printf "%d|%s%s|%s\n", NR, $2, $3 == 1 ? " (default)" : "", $3 == 1 ? "ON" : "OFF" }')
      if chosen=$(checklist "Firefox" "Put userChrome.css in which profiles?" "$items" notags); then
        firefox_dirs=$(printf '%s\n' "$profiles" | awk -F '\t' -v chosen=" $(printf '%s\n' "$chosen" | tr '\n' ' ')" '
          index(chosen, " " NR " ") { print $1 }')
      fi
      firefox_picked=1
      [ -n "$firefox_dirs" ] || parts=$(echo " $parts " | sed 's/ firefox / /')
    fi
  fi

  if has_part gtk4 && [ "$mode" = copy ] && [ -z "$desktop_grid" ] && have_ding; then
    if yesno "Desktop Icons NG" "Desktop Icons NG draws the desktop as a see-through GTK 4 window, so GTK 4's graph paper would cover the wallpaper too. Put it there as well?"; then
      desktop_grid=1
    fi
  fi
elif [ -z "$parts" ]; then
  parts=$all_parts every=1
fi

# Keep the parts that fit, once each, in the usual order.
wanted=$parts
parts=
for part in $all_parts; do
  case " $wanted " in *" $part "*) ;; *) continue ;; esac
  case " $parts " in *" $part "*) continue ;; esac
  if fits "$part"; then
    parts="$parts $part"
  elif [ -z "$every" ]; then
    echo "skipped $part: it's for Linux and BSD desktops" >&2
  fi
done

# --- Installing ------------------------------------------------------------

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

# Where the shell snippets get sourced from.
# shellcheck disable=SC2088  # printed, not expanded
case ${SHELL:-} in
  */zsh) rc='~/.zshrc' ;;
  */bash) rc='~/.bashrc' ;;
  *) rc="your shell's rc file" ;;
esac

for part in $parts; do
  case $part in
    gtk4)
      css=$here/gtk-4.0/gtk.css
      if [ -n "$desktop_grid" ]; then
        if [ "$mode" = link ]; then
          echo "--desktop-grid needs a copy, not --link: left gtk.css as it is" >&2
        else
          # The same stylesheet, minus the rule that keeps the paper off
          # the desktop.
          css=$(mktemp -d)/gtk.css
          sed '/desktop-grid:begin/,/desktop-grid:end/d' "$here/gtk-4.0/gtk.css" > "$css"
        fi
      fi
      # Either variant installed before is ours to replace, not a file of
      # the user's own to move aside.
      dst=$config/gtk-4.0/gtk.css
      if [ "$mode" != remove ] && [ -f "$dst" ] && [ ! -L "$dst" ] &&
         { same "$here/gtk-4.0/gtk.css" "$dst" ||
           sed '/desktop-grid:begin/,/desktop-grid:end/d' "$here/gtk-4.0/gtk.css" | cmp -s - "$dst"; }; then
        rm -f "$dst"
      fi
      place "$css" "$dst"
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
        # GTK 2 only looks in ~/.themes, not ~/.local/share/themes, so the
        # themes with a gtk-2.0 get a link there too.
        for t in "$here"/themes/*/gtk-2.0; do
          name=$(basename "$(dirname "$t")")
          link=$HOME/.themes/$name
          if [ "$mode" = remove ]; then
            [ -L "$link" ] && rm -f "$link" && echo "removed $link"
          elif [ -e "$link" ] && [ ! -L "$link" ]; then
            echo "left $link alone: it isn't ours"
          else
            mkdir -p "$HOME/.themes"
            ln -sfn "$data/themes/$name" "$link"
            echo "$link"
          fi
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
      glow_yml=$config/glow/glow.yml
      [ "$os" = macos ] && glow_yml=$HOME/Library/Preferences/glow/glow.yml
      hint "glow: set  style: \"$config/neon-doll/glow/neon-doll-dark.json\"  in $glow_yml (or -light); the full path, since glow doesn't expand ~"
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
    cosmic)
      for f in "$here"/cosmic/*.ron "$here"/cosmic/terminal/*.ron; do
        place "$f" "$config/neon-doll/${f#"$here"/}"
      done
      hint "COSMIC: cosmic-settings appearance import $config/neon-doll/cosmic/Neon-Doll-Dark.ron   (or -Light)"
      hint "COSMIC Terminal: View → Color schemes… → Import, and pick $config/neon-doll/cosmic/terminal/Neon Doll Dark.ron; the list is the current mode's, so import Light from light mode"
      ;;
    kde)
      for f in "$here"/kde/color-schemes/*.colors; do
        place "$f" "$data/color-schemes/$(basename "$f")"
      done
      for t in "$here"/kde/look-and-feel/*/; do
        t=${t%/}
        place "$t" "$data/plasma/look-and-feel/$(basename "$t")"
      done
      hint "Plasma: kvantummanager --set NeonDoll  (the kvantum part), then System Settings → Colors & Themes → Global Theme → Neon Doll Dark (or Light); for the colors alone,  plasma-apply-colorscheme NeonDollDark"
      ;;
    kvantum)
      place "$here/kde/Kvantum/NeonDoll" "$config/Kvantum/NeonDoll"
      hint "Kvantum: kvantummanager --set NeonDoll, then the widget style  kvantum-dark  (or  kvantum  for light); outside Plasma, QT_STYLE_OVERRIDE=kvantum-dark"
      ;;
    konsole)
      for f in "$here"/kde/konsole/*; do
        place "$f" "$data/konsole/$(basename "$f")"
      done
      hint "Konsole: Settings → Manage Profiles → Neon Doll Dark (or Light) → Set as Default"
      ;;
    kate)
      for f in "$here"/kde/syntax-highlighting/*.theme; do
        place "$f" "$data/org.kde.syntax-highlighting/themes/$(basename "$f")"
      done
      hint "Kate: Settings → Configure Kate → Color Themes → Neon Doll Dark (or Light)"
      ;;
    qtct)
      for v in qt5ct qt6ct; do
        for f in "$here"/kde/qtct/*.conf; do
          place "$f" "$config/$v/colors/$(basename "$f")"
        done
      done
      hint "qt5ct/qt6ct: Appearance → Palette → Custom → NeonDollDark (or NeonDollLight), with the Fusion style"
      ;;
    vscode)
      # The extension dir as it is: VS Code picks up an unpacked extension
      # in its extensions dir on the next start, no .vsix needed.
      version=$(sed -n 's/^  "version": *"\([^"]*\)".*/\1/p' "$here/vscode/package.json")
      dirs=$(vscode_dirs)
      [ -n "$dirs" ] || dirs=$HOME/.vscode/extensions
      while IFS= read -r d; do
        place "$here/vscode" "$d/mishan.neon-doll-$version"
        # Taking the dir out leaves VS Code's list of extensions naming it;
        # its own uninstall clears that.
        if [ "$mode" = remove ] && [ ! -e "$d/mishan.neon-doll-$version" ] &&
           grep -qs '"mishan.neon-doll"' "$d/extensions.json"; then
          for cli in code codium code-oss cursor windsurf; do
            if have "$cli"; then
              "$cli" --extensions-dir "$d" --uninstall-extension mishan.neon-doll >/dev/null 2>&1 || true
              break
            fi
          done
        fi
      done <<EOF
$dirs
EOF
      hint "VS Code: restart it, then Preferences: Color Theme → Neon Doll Dark (or Light). To follow the system, see the README's Light and dark."
      ;;
    firefox)
      # Removing looks in every profile; installing in the ones picked, or
      # the default ones.
      if [ "$mode" = remove ]; then
        dirs=$(firefox_profiles | cut -f1)
      elif [ -n "$firefox_picked" ]; then
        dirs=$firefox_dirs
      else
        dirs=$(firefox_default_dirs)
      fi
      if [ -z "$dirs" ]; then
        [ "$mode" = remove ] || echo "skipped firefox: no Firefox profile found; start Firefox once first" >&2
        continue
      fi
      unset_in=
      while IFS= read -r d; do
        place "$here/firefox/userChrome.css" "$d/chrome/userChrome.css"
        grep -qs 'toolkit.legacyUserProfileCustomizations.stylesheets", *true' "$d/prefs.js" "$d/user.js" ||
          unset_in="$unset_in, $(basename "$d")"
      done <<EOF
$dirs
EOF
      if [ -n "$unset_in" ]; then
        hint "Firefox: set toolkit.legacyUserProfileCustomizations.stylesheets to true in about:config (profiles ${unset_in#, }), then restart Firefox"
      else
        hint "Firefox: restart it. The color theme itself loads from about:debugging; see the README."
      fi
      ;;
    newt)
      place "$here/newt/neon-doll.sh" "$config/neon-doll/newt.sh"
      hint "whiptail/debconf: add to $rc:  . $config/neon-doll/newt.sh"
      ;;
    ag)
      place "$here/ag/neon-doll.sh" "$config/neon-doll/ag.sh"
      hint "ag: add to $rc:  . $config/neon-doll/ag.sh"
      ;;
    man)
      place "$here/man/neon-doll.sh" "$config/neon-doll/man.sh"
      hint "man: add to $rc:  . $config/neon-doll/man.sh"
      ;;
    dircolors)
      place "$here/dircolors/neon-doll" "$config/neon-doll/dircolors"
      dircolors=dircolors
      ! have dircolors && have gdircolors && dircolors=gdircolors
      hint "ls: add to $rc:  eval \"\$($dircolors -b $config/neon-doll/dircolors)\""
      ;;
  esac
done

if [ "$mode" != remove ] && [ -n "$hints" ]; then
  echo
  echo "To turn it on:$hints"
fi
