#!/bin/sh
# The terminal palette, as tools/cli-shoot.sh shows it: each of the 16
# colors as text and as a swatch, then the colors in use: a prompt, git
# status, ls and a comment. VARIANT names the scheme it's shown in.
#
#   tools/cli-palette.sh dark|light
set -eu
case $1 in dark) title="Neon Doll Dark" ;; light) title="Neon Doll Light" ;; *) exit 2 ;; esac
e=$(printf '\033')
printf '%s    fg on bg\n\n' "$title"
names="black red green yellow blue magenta cyan white"
i=0
for n in $names; do
  printf ' %s%d %-8s%s   %s[4%dm  %s[0m  %s[3%dmnormal text%s[0m    %2d bright   %s[10%dm  %s[0m\n' \
    "${e}[3${i}m" $i "$n" "${e}[0m" "$e" $i "$e" "$e" $i "$e" $((i + 8)) "$e" $i "$e"
  i=$((i + 1))
done
printf '\n%s[35mdoll@neon%s[0m:%s[34m~/w/neon-doll%s[0m$ git status -s\n' "$e" "$e" "$e" "$e"
printf ' %s[31mM%s[0m README.md\n%s[32mA%s[0m  tilix/neon-doll-dark.json\n%s[31m??%s[0m emacs/\n\n' "$e" "$e" "$e" "$e" "$e" "$e"
printf 'drwxr-xr-x  %s[34mgtksourceview/%s[0m\n-rwxr-xr-x  %s[32minstall.sh%s[0m      lrwxrwxrwx  %s[36mgtk.css%s[0m\n' "$e" "$e" "$e" "$e" "$e" "$e"
printf '%s[90m# a comment in bright black%s[0m\n%s[7m reverse video %s[0m\n' "$e" "$e" "$e" "$e"
exec cat >/dev/null
