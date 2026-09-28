#!/bin/sh
# Tests for install.sh. Each one runs the installer against a scratch home
# folder, never yours.
#
#   tests/install.sh             run them all
#   SH=dash tests/install.sh     run install.sh under another shell
#
# The picker tests need python3 (tests/pty_run.py gives them a terminal) and
# the whiptail ones whiptail; tests that can't run here are skipped, and say
# why. On Linux, macOS is played by a uname that says Darwin.
# shellcheck disable=SC2034,SC2086  # st1 and ff are read in eval'd checks; $SH may carry flags
set -u

root=$(cd "$(dirname "$0")/.." && pwd)
SH=${SH:-sh}
os=$(uname -s)
pass=0 fail=0 skipped=0
scratch=$(mktemp -d)
trap 'rm -rf "$scratch"' EXIT

ok() { pass=$((pass + 1)); echo "ok    $1"; }
nok() {
  fail=$((fail + 1)); echo "FAIL  $1"
  [ -f "$out" ] && sed 's/^/      | /' "$out"
}
skip() { skipped=$((skipped + 1)); echo "skip  $1: $2"; }

# check NAME COMMAND...: pass if COMMAND succeeds.
check() { name=$1; shift; if "$@"; then ok "$name"; else nok "$name"; fi; }

# A fresh home folder, $h, and a file for the run's output, $out.
n=0
fresh() {
  n=$((n + 1))
  h=$scratch/home$n out=$scratch/out$n
  mkdir -p "$h"
  : >"$out"
}

# Settings for the next run: a folder put first on PATH, and the login shell.
bin='' login=/bin/bash

# run ARG...: install.sh with no terminal. Its status is in $st.
run() {
  env HOME="$h" XDG_CONFIG_HOME= XDG_DATA_HOME= EMACS_THEMES_DIR= NEWT_COLORS= \
    SHELL="$login" PATH="${bin:+$bin:}$PATH" \
    $SH "$root/install.sh" "$@" </dev/null >"$out" 2>&1
  st=$?
}

# pick UI STEP...: install.sh in a terminal, asking with UI (text or
# whiptail) and answered by STEPs; see tests/pty_run.py.
pick() {
  ui=$1; shift
  env HOME="$h" XDG_CONFIG_HOME= XDG_DATA_HOME= EMACS_THEMES_DIR= NEWT_COLORS= \
    SHELL="$login" PATH="${bin:+$bin:}$PATH" NEON_DOLL_UI="$ui" \
    python3 "$root/tests/pty_run.py" "$@" -- $SH "$root/install.sh" >"$out" 2>&1
  st=$?
}

has() { [ -e "$h/$1" ] || [ -L "$h/$1" ]; }
says() { grep -q -- "$1" "$out"; }
files() { (cd "$h" && find . \( -type f -o -type l \) | sort); }
exits() { [ "$st" -eq "$1" ]; }

# stub NAME [OUTPUT]: a command on the next run's PATH that prints OUTPUT.
stub() {
  [ -n "$bin" ] || { bin=$scratch/bin$n; mkdir -p "$bin"; }
  printf '#!/bin/sh\necho %s\n' "${2:-}" >"$bin/$1"
  chmod +x "$bin/$1"
}

# Two Firefox profiles: "main", the default, and "spare", which already
# lets userChrome.css in.
firefox_fixture() {
  if [ "$os" = Darwin ]; then ff="$h/Library/Application Support/Firefox"
  else ff=$h/.mozilla/firefox
  fi
  mkdir -p "$ff/Profiles/a.main" "$ff/Profiles/b.spare"
  printf '%s\n' '[Profile1]' 'Name=spare' 'IsRelative=1' 'Path=Profiles/b.spare' '' \
    '[Profile0]' 'Name=main' 'IsRelative=1' 'Path=Profiles/a.main' '' \
    '[Install4F96D1932A9F858E]' 'Default=Profiles/a.main' 'Locked=1' >"$ff/profiles.ini"
  echo 'user_pref("toolkit.legacyUserProfileCustomizations.stylesheets", true);' \
    >"$ff/Profiles/b.spare/prefs.js"
}

all_parts=$(sed -n 's/^all_parts="\(.*\)"$/\1/p' "$root/install.sh")
[ -n "$all_parts" ] || { echo "can't find all_parts in install.sh" >&2; exit 2; }

# --- Arguments ---------------------------------------------------------------

fresh; run --help
check "--help prints the usage" eval 'exits 0 && says "PART is any of"'

fresh; run --bogus
check "an unknown argument fails" eval 'exits 2 && says "unknown argument: --bogus"'

fresh; bin=; stub uname MINGW64_NT-10.0; run vim; bin=
check "on Windows it points at install.ps1" eval 'exits 2 && says "install.ps1"'

# --- Every part ----------------------------------------------------------------

for part in $all_parts; do
  fresh
  before=$(files)
  run "$part"
  if says "skipped $part: it's for Linux"; then
    check "$part: skipped on $os" exits 0
    continue
  fi
  st1=$st
  run --remove "$part"
  check "$part: installs, then removes cleanly" \
    eval '[ "$st1" -eq 0 ] && exits 0 && [ "$(files)" = "$before" ]'
done

fresh
firefox_fixture
before=$(files)
run
st1=$st
if [ "$os" = Darwin ]; then
  check "with no terminal, it installs the parts for macOS" \
    eval '[ "$st1" -eq 0 ] && has .vim/colors/neon-doll.vim && ! has .config/gtk-4.0/gtk.css && says "To turn it on"'
else
  check "with no terminal, it installs every part" \
    eval '[ "$st1" -eq 0 ] && has .config/gtk-4.0/gtk.css && has .local/share/themes/Neon-Doll-Dark &&
          has .local/share/icons/Neon-Doll-Cursors && has .vim/colors/neon-doll.vim && says "To turn it on"'
fi
run --remove
check "--remove with no parts takes all of it out" eval 'exits 0 && [ "$(files)" = "$before" ]'

# --- Files of your own ----------------------------------------------------------

fresh
mkdir -p "$h/.vim/colors"
echo mine >"$h/.vim/colors/neon-doll.vim"
run vim
check "a file of yours is moved aside" \
  eval 'exits 0 && cmp -s "$h/.vim/colors/neon-doll.vim" "$root/vim/colors/neon-doll.vim" &&
        grep -qsx mine "$h"/.vim/colors/neon-doll.vim.bak.*'
run --remove vim
check "--remove leaves the moved-aside file" \
  eval 'exits 0 && ! has .vim/colors/neon-doll.vim && grep -qsx mine "$h"/.vim/colors/neon-doll.vim.bak.*'

fresh
run vim
echo '" my edit' >>"$h/.vim/colors/neon-doll.vim"
run --remove vim
check "--remove leaves a copy you've changed" \
  eval 'exits 0 && has .vim/colors/neon-doll.vim && says "left .* alone"'

fresh
run vim
run vim
check "installing twice keeps no backup" eval 'exits 0 && [ "$(files)" = "./.vim/colors/neon-doll.vim" ]'

fresh
run --link vim
check "--link links into the checkout" \
  eval 'exits 0 && [ -L "$h/.vim/colors/neon-doll.vim" ] &&
        [ "$(readlink "$h/.vim/colors/neon-doll.vim")" = "$root/vim/colors/neon-doll.vim" ]'
run --remove vim
check "--remove takes the link out" eval 'exits 0 && ! has .vim/colors/neon-doll.vim'

if [ "$os" = Darwin ]; then
  skip "--desktop-grid" "GTK 4 isn't offered on macOS"
else
  fresh
  run --desktop-grid gtk4
  check "--desktop-grid drops the rule that keeps the paper off the desktop" \
    eval 'exits 0 && grep -q desktop-grid:begin "$root/gtk-4.0/gtk.css" &&
          ! grep -q desktop-grid:begin "$h/.config/gtk-4.0/gtk.css"'
  run gtk4
  check "the desktop-grid copy is replaced, not backed up" \
    eval 'exits 0 && cmp -s "$h/.config/gtk-4.0/gtk.css" "$root/gtk-4.0/gtk.css" && [ "$(files)" = "./.config/gtk-4.0/gtk.css" ]'
fi

# --- Firefox ----------------------------------------------------------------------

fresh
firefox_fixture
run firefox
check "firefox goes to the default profile only" \
  eval 'exits 0 && [ -f "$ff/Profiles/a.main/chrome/userChrome.css" ] && [ ! -e "$ff/Profiles/b.spare/chrome" ]'
check "firefox names the profile that needs the pref" says "profiles a.main"
echo 'user_pref("toolkit.legacyUserProfileCustomizations.stylesheets", true);' >"$ff/Profiles/a.main/user.js"
run firefox
check "firefox doesn't ask for a pref that's set" eval 'exits 0 && ! says "about:config" && says "Firefox: restart it"'

fresh
run firefox
check "firefox with no profile is skipped" eval 'exits 0 && says "no Firefox profile found"'

# --- Hints ------------------------------------------------------------------------

fresh; login=/bin/zsh; run ag; login=/bin/bash
check "hints name the rc file of your shell" eval 'exits 0 && says "add to ~/.zshrc"'

# --- macOS, played on Linux ----------------------------------------------------------

if [ "$os" = Darwin ]; then
  fresh; run gtk4 vim
else
  fresh; stub uname Darwin; run gtk4 vim; bin=
fi
check "on macOS the desktop parts are skipped" \
  eval 'exits 0 && says "skipped gtk4" && ! has .config/gtk-4.0/gtk.css && has .vim/colors/neon-doll.vim'

# --- The picker ------------------------------------------------------------------------

if ! command -v python3 >/dev/null 2>&1; then
  skip "the picker" "no python3 to drive it"
else
  fresh
  pick text 'expect:Enter to go on' 'send:n\r' tick:vim 'expect:Enter to go on' 'send:\r'
  check "the text picker installs what's ticked" eval 'exits 0 && [ "$(files)" = "./.vim/colors/neon-doll.vim" ]'

  fresh
  pick text 'expect:Enter to go on' 'send:q\r'
  check "the text picker's q installs nothing" eval 'exits 0 && says "Nothing installed" && [ -z "$(files)" ]'

  fresh
  pick text 'expect:Enter to go on' 'send:n\r' 'expect:Enter to go on' 'send:\r'
  check "picking nothing installs nothing" eval 'exits 0 && says "Nothing picked" && [ -z "$(files)" ]'

  fresh
  firefox_fixture
  pick text 'expect:Enter to go on' 'send:n\r' tick:firefox 'expect:Enter to go on' 'send:\r' \
    'expect:which profiles' tick:main tick:spare 'expect:Enter to go on' 'send:\r'
  check "the picker asks which Firefox profiles" \
    eval 'exits 0 && [ -f "$ff/Profiles/b.spare/chrome/userChrome.css" ] && [ ! -e "$ff/Profiles/a.main/chrome" ]'

  fresh
  firefox_fixture
  pick text 'expect:Enter to go on' 'send:n\r' tick:firefox 'expect:Enter to go on' 'send:\r' \
    'expect:which profiles' 'send:n\r' 'expect:Enter to go on' 'send:\r'
  check "no Firefox profile picked drops firefox" eval 'exits 0 && [ -z "$(find "$h" -name userChrome.css)" ]'

  fresh
  stub irssi
  pick text 'expect:Enter to go on' 'send:q\r'
  bin=
  check "an app on PATH is ticked" eval 'grep -q "\[x\] irssi  *irssi$" "$out"'

  if command -v glow >/dev/null 2>&1; then
    skip "an app not found is unticked" "glow is installed here"
  else
    fresh
    pick text 'expect:Enter to go on' 'send:q\r'
    check "an app not found is unticked" eval 'grep -q "\[ \] glow  *glow (not found)$" "$out"'
  fi

  fresh
  [ "$os" = Darwin ] || stub uname Darwin
  pick text 'expect:Enter to go on' 'send:q\r'
  bin=
  check "on macOS the picker leaves out the desktop parts" \
    eval 'exits 0 && says "] vim " && ! says "] gtk4 " && ! says "] konsole "'

  if ! command -v whiptail >/dev/null 2>&1; then
    skip "the whiptail picker" "no whiptail"
  else
    fresh
    pick whiptail 'expect:Install which parts' 'send:\x1b'
    check "whiptail's Esc installs nothing" eval 'exits 0 && says "Nothing installed" && [ -z "$(files)" ]'

    fresh
    stub irssi
    pick whiptail 'expect:Install which parts' 'send:\r'
    bin=
    check "whiptail's Enter installs what was found" \
      eval 'exits 0 && has .irssi/neon-doll.theme && says "To turn it on"'
  fi
fi

echo
echo "$pass passed, $fail failed, $skipped skipped (install.sh under $SH)"
[ "$fail" -eq 0 ]
