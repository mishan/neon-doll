#!/bin/sh
# Screenshot the command-line parts in each Neon Doll terminal scheme: git,
# man, glow, whiptail, vim and PowerShell with their Neon Doll colors, and a
# sheet of both palettes.
#
#   tools/cli-shoot.sh DIR [git|man|glow|whiptail|vim|powershell|palettes ...]
#
# Writes DIR/NAME-{dark,light}.png, and DIR/tilix-palettes.png for
# palettes; with no names, all of them. Each program runs in a sealed
# session with a scratch home, in the Tilix scheme, configured the way the
# installer leaves it. Prompts are fixed (doll@neon), and the git history
# has fixed dates, so a reshoot changes only with the theme.
#
# Needs shotbox (https://github.com/mishan/shotbox) on PATH, and each
# program it's asked to shoot; PowerShell is pwsh.
set -eu
command -v shotbox >/dev/null || { echo "needs shotbox on PATH: pipx install --system-site-packages shotbox" >&2; exit 1; }
dir=$(realpath -m "$1"); shift
[ $# -gt 0 ] || set -- git man glow whiptail vim powershell palettes
here=$(cd "$(dirname "$0")" && pwd)
root=$(dirname "$here")
tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT
mkdir -p "$dir"

# shoot NAME VARIANT COLSxROWS WHEN -- COMMAND...: one picture.
shoot() {
  name=$1 variant=$2 size=$3 when=$4; shift 5
  shotbox term --shoot "$dir/$name-$variant.png" --scheme "$root/tilix/neon-doll-$variant.json" \
      --size "$size" --when "$when" --env "HOME=$tmp/home" -- "$@"
}
mkdir -p "$tmp/home"

# A small repo: three commits on two branches, a tag, a change and a new file.
repo() {
  r=$tmp/repo
  [ -d "$r" ] && return
  mkdir -p "$r" && cd "$r"
  export GIT_AUTHOR_NAME=Doll GIT_AUTHOR_EMAIL=doll@neon.test
  export GIT_COMMITTER_NAME=Doll GIT_COMMITTER_EMAIL=doll@neon.test
  export GIT_AUTHOR_DATE="2026-09-25T17:00:00Z" GIT_COMMITTER_DATE="2026-09-25T17:00:00Z"
  git init -q -b main
  printf 'a\nb\nc\nd\n' > f.txt && git add f.txt && git commit -qm one
  printf 'a\nB\nc\nd\n' > f.txt && git commit -qam "two: capitalize"
  git tag v0.1
  git checkout -qb feature
  echo e >> f.txt && git commit -qam three
  git checkout -q main
  printf 'a\nB\nC\nd\n' > f.txt && echo g > g.txt
  cd - >/dev/null
}

for name; do
  for v in dark light; do
    case $name in
      git)
        repo
        shoot git $v 52x22 'index .*' -- bash --norc -c "
          export GIT_CONFIG_GLOBAL='$tmp/gitconfig' PAGER=cat
          printf '[include]\n\tpath = %s\n' '$root/git/neon-doll.gitconfig' > \"\$GIT_CONFIG_GLOBAL\"
          cd '$tmp/repo' && git log --oneline --graph --decorate --all && echo &&
          git branch && echo && git status -sb && echo && git diff | head -10; exec cat" ;;
      man)
        shoot man $v 73x23 'Manual page ls' -- bash --norc -c "
          . '$root/man/neon-doll.sh'; exec man ls" ;;
      glow)
        cat > "$tmp/glow.md" <<'MD'
link at rest https://github.com/mishan/neon-doll.

## Synopsis

Run `./install.sh` with any of:

- `gtk4`, `gtk3`, `shell`
- `tilix`, `emacs`, `man`
- [x] light and dark
- [ ] a 256-color palette

> Contrast is measured against the surface the token lands on.

```python
def switch(on: bool) -> str:
    # the mark means "on" without color
    return "|" if on else "□"  # width: 24
```

| part | goes to |
|------|---------|
| gtk4 | ~/.config/gtk-4.0 |
| man  | ~/.config/neon-doll |
MD
        shoot glow $v 69x28 'neon-doll' -- bash --norc -c "
          glow -w 66 -s '$root/glow/neon-doll-$v.json' '$tmp/glow.md'; exec cat" ;;
      whiptail)
        shoot whiptail $v 72x23 'Cancel' -- bash --norc -c "
          . '$root/newt/neon-doll.sh'
          exec whiptail --backtitle 'Neon Doll setup' --title neon-doll --menu \
            'Pick the parts to install:' 16 56 5 \
            gtk4 'GTK 4 / libadwaita' shell 'GNOME Shell' cursor 'Mouse cursor' \
            tilix 'Tilix schemes' man 'man pages'" ;;
      vim)
        mkdir -p "$tmp/vim"
        cat > "$tmp/vim/listing.rs" <<'RS'
// ls -l, as the theme sees it: a mode, a size, a name.
use std::fs;

const WIDTH: usize = 80;

fn listing(dir: &str) -> std::io::Result<Vec<String>> {
    let mut rows = Vec::new();
    for entry in fs::read_dir(dir)? {
        let entry = entry?;
        let size = entry.metadata()?.len();
        let mode = if entry.file_type()?.is_dir() { 'd' } else { '-' };
        rows.push(format!("{mode}rw-r--r-- {size:>6} {:?}", entry.file_name()));
    }
    Ok(rows) // TODO: owner and group
}
RS
        shoot vim $v 73x24 'All' -- bash --norc -c "
          cd '$tmp/vim' && exec vim -u NONE -N --cmd 'set rtp^=$root/vim' \
            -c 'set background=$v termguicolors number laststatus=2 ruler' \
            -c 'colorscheme neon-doll' -c 'syntax on' -c 'call cursor(10, 9)' listing.rs" ;;
      powershell)
        command -v pwsh >/dev/null || { echo "$0: powershell needs pwsh on PATH" >&2; exit 1; }
        d=$tmp/home/psdemo
        mkdir -p "$d/src"
        for f in build.ps1 notes.md old.bak photo.png release.zip song.flac; do : > "$d/$f"; done
        touch -d "2026-09-25 17:01 UTC" "$d"/*
        # The theme's own prompt, with who, where and when made fixed: it
        # reads them from the machine and the clock.
        shoot powershell $v 73x24 'looks like this' -- env TZ=UTC pwsh -NoLogo -NoProfile -NoExit -Command "
          . '$root/windows/powershell/neon-doll.ps1'
          Enable-NeonDollPrompt -Variant $v
          \$theme = \$function:prompt
          function global:prompt {
            \$who = [Environment]::UserName + '@' + [Environment]::MachineName.ToLower()
            (& \$theme).Replace(\$who, 'doll@neon') -replace '\[\d\d:\d\d:\d\d\]', '[17:01:56]'
          }
          Set-Location '$d'
          Get-ChildItem | Format-Table UnixMode, LastWriteTime, Size, @{ Name = 'Name'; Expression = { \$_.NameString } }
          Write-Warning 'a warning looks like this'" ;;
      palettes)
        shoot palettes $v 62x21 'reverse video' -- bash --norc -c "exec '$here/cli-palette.sh' '$v'" ;;
      *) echo "$0: no such part: $name" >&2; exit 2 ;;
    esac
  done
  if [ "$name" = palettes ]; then
    magick "$dir/palettes-dark.png" "$dir/palettes-light.png" +append "$dir/tilix-palettes.png"
    rm "$dir/palettes-dark.png" "$dir/palettes-light.png"
  fi
done
