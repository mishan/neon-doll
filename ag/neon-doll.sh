# Neon Doll colors for ag, the silver searcher. Source it from ~/.bashrc (or
# any POSIX shell's rc):
#
#   . ~/.config/neon-doll/ag.sh
#
# ag has no config file, only flags, so this is an alias. The colors are
# git grep's under the Neon Doll git colors, so the two searches look alike:
# file names purple, line numbers muted, and each match purple and
# underlined, in place of ag's black-on-yellow. Nothing is bold. Only the 16
# terminal colors are named, so this follows whichever Neon Doll terminal
# scheme is active.
#
# 35 purple (ANSI magenta), 90 muted (bright black), 4 underline.
alias ag="ag --color-path=35 --color-line-number=90 --color-match='4;35'"
