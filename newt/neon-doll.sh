# Neon Doll colors for newt: whiptail, and the Debian and Ubuntu tools built
# on it (debconf dialogs, dpkg-reconfigure, the installer). Source it from
# ~/.bashrc:
#
#   . ~/.config/neon-doll/newt.sh
#
# newt's own palette assumes a VGA console: a blue desktop, light-grey boxes,
# red buttons. On the Neon Doll palette, where blue is a pastel and "white"
# (7) is a mid grey, that comes out washed out. This names the terminal's
# colors by role instead, so it follows either Neon Doll scheme:
#
#   default  the terminal's page     black (0)  the border color, used as the
#   white    ink (15)                           box's panel
#   gray     muted (8)               magenta    purple (5)
#
# The box is a panel lifted off the page, edged and titled in purple; the
# focused item is reverse purple; entry fields are slots cut into the page. No
# drop shadow: the shadow is drawn in the page color.
#
# Format: element=foreground,background, separated by spaces.

export NEWT_COLORS='
  root=white,default         roottext=gray,default      helpline=gray,default
  window=white,black         border=magenta,black       title=magenta,black
  shadow=default,default
  label=white,black          textbox=white,black        acttextbox=black,magenta
  button=white,black         actbutton=black,magenta
  compactbutton=white,black
  checkbox=white,black       actcheckbox=black,magenta
  listbox=white,black        actlistbox=black,magenta
  sellistbox=magenta,black   actsellistbox=black,magenta
  entry=white,default        disentry=gray,default
  emptyscale=white,default   fullscale=black,magenta
'
