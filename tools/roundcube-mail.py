#!/usr/bin/env python3
"""Fill a scratch IMAP account with a pretend mailbox, for the Roundcube
screenshots.

    tools/roundcube-mail.py HOST PORT USER PASSWORD

Appends straight over IMAP, so flags and dates are set as they land: a few
unread, one flagged, one answered, one with an attachment, one deleted but
not yet expunged, and an open one with quoting, a link and a signature. Made
for GreenMail, which takes any password; it empties the account first.
"""

import imaplib
import sys
import time
from email.message import EmailMessage
from email.utils import format_datetime
from datetime import datetime, timedelta, timezone

ME = "Doll <doll@neon.test>"
NOW = datetime(2026, 9, 26, 18, 40, tzinfo=timezone.utc)

FOLDERS = ["Drafts", "Sent", "Junk", "Trash", "Archive", "Archive.2025",
           "Lists", "Lists.gnome-shell", "Lists.gtk"]

# (from, subject, minutes ago, flags, body)
MAIL = [
    ("Vex Nakamura <vex@arcology.test>", "Re: the sign over the noodle bar", 12, "",
     "It's fixed. The second O flickers on purpose now.\n\n"
     "Photos are at https://arcology.test/sign and the invoice follows.\n\n"
     "On Sat, Sep 26, Doll wrote:\n"
     "> Can we keep the pink, but lose the buzz?\n"
     "> The whole block hears it at 3am.\n\n"
     "-- \nVex, neon and noise\n"),
    ("Juno Park <juno@lowcity.test>", "Rooftop, Friday?", 47, "",
     "Bring the cables. And the good speaker, not the one with the dent.\n"),
    ("Arcology Transit <noreply@transit.test>", "Your pass renews in 3 days", 95, "",
     "Your monthly pass renews on 29 September.\n"),
    ("Kit Okafor <kit@synth.test>", "Patch notes for the drum machine", 180, "\\Flagged",
     "Swing is back, and the hi-hat stops eating the snare.\n"),
    ("Mira Solis <mira@lowcity.test>", "Photos from the night market", 60 * 5, "\\Seen \\Answered",
     "The fish-ball stall came out best. Attached.\n"),
    ("Dex <dex@arcology.test>", "Your soldering iron", 60 * 9, "\\Seen",
     "I still have it. It still works. Mostly.\n"),
    ("Low City Library <desk@library.test>", "Hold ready: Neuromancer", 60 * 26, "\\Seen",
     "Your hold is ready at the front desk until Thursday.\n"),
    ("Juno Park <juno@lowcity.test>", "Old flyer", 60 * 30, "\\Seen \\Deleted",
     "Found this in a drawer.\n"),
    ("Sable Ito <sable@synth.test>", "Mix for the rooftop", 60 * 50, "\\Seen",
     "Ninety minutes, no ballads. You're welcome.\n"),
    ("Arcology Power <billing@power.test>", "September statement", 60 * 72, "\\Seen",
     "Your statement is ready.\n"),
    ("Vex Nakamura <vex@arcology.test>", "Quote for the sign", 60 * 100, "\\Seen",
     "Tube, transformer and a Saturday. Numbers below.\n"),
    ("Kit Okafor <kit@synth.test>", "Tape delay", 60 * 140, "\\Seen",
     "Found one. It hisses like a cat, which is the point.\n"),
]


def message(sender, subject, when, body, attach=False):
    m = EmailMessage()
    m["From"] = sender
    m["To"] = ME
    m["Subject"] = subject
    m["Date"] = format_datetime(when)
    m.set_content(body)
    if attach:
        m.add_attachment(b"\x89PNG\r\n\x1a\n", maintype="image", subtype="png",
                         filename="night-market.png")
    return m.as_bytes()


def main():
    host, port, user, password = sys.argv[1], int(sys.argv[2]), sys.argv[3], sys.argv[4]
    imap = imaplib.IMAP4(host, port)
    imap.login(user, password)
    for f in ["INBOX"] + FOLDERS:
        imap.create(f)
        imap.subscribe(f)
        imap.select(f)
        imap.store("1:*", "+FLAGS", "\\Deleted")
        imap.expunge()
    # Oldest first, so the UIDs run with the dates.
    for sender, subject, ago, flags, body in reversed(MAIL):
        when = NOW - timedelta(minutes=ago)
        data = message(sender, subject, when, body, attach="night market" in subject)
        imap.append("INBOX", f"({flags})" if flags else None,
                    imaplib.Time2Internaldate(time.mktime(when.timetuple())), data)
    for i in range(3):
        imap.append("Lists.gtk", "(\\Seen)" if i else None, None,
                    message("gtk-devel <gtk@lists.test>", f"GtkListView row {i}", NOW, "..."))
    imap.logout()


if __name__ == "__main__":
    main()
