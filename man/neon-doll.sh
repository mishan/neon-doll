# Neon Doll colors for man pages. Source it from ~/.bashrc (or any POSIX
# shell's rc):
#
#   . ~/.config/neon-doll/man.sh
#
# The theme is a man page in a terminal that never existed, so its own
# subject gets the site's rules: section headings and literal commands and
# options (what man sets in bold) are purple, and the arguments you fill in
# (underlined) are cyan and stay underlined, a cue that still reads without
# color. Nothing is bold. Only the 16 terminal colors are named, so this
# follows whichever Neon Doll terminal scheme is active.
#
# groff now sends real bold and underline escapes, and less can only recolor
# the older overstruck kind, so man is asked for overstrike first. Both
# settings are man's own, so the plain `less` pager is left alone.

# grotty -c: overstrike instead of escapes, for less to recolor.
export MANROFFOPT='-P -c'

# -Ddm   bold -> purple, no longer bold
# -Du+c  underline -> cyan, still underlined
# -DP8   the prompt line in muted (8-bit color 8, bright black), not reversed
# -DSkm  search matches: the border color on purple
export MANPAGER='less -R --use-color -Ddm -Du+c -DP8 -DSkm'
