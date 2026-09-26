#!/usr/bin/env python3
"""A pretend IRC server with a scripted channel, for irssi screenshots.

    tools/irssi-server.py PORT

Takes one client on 127.0.0.1:PORT, calls it doll, puts it in #neon-doll
and #cyberpunk, and plays a few minutes of IRC in a few seconds: talk, a
mention, an action, joins, parts, a quit, a mode change and a query. Run by
tools/irssi-shoot.sh.
"""

import socket
import sys
import time

NICK = "doll"
S = ":irc.example"


def host(n):
    return f":{n}!~{n}@{n}.example"


SCRIPT = [
    f"{S} 001 {NICK} :Welcome to the pretend network",
    f"{S} 376 {NICK} :End of MOTD",
    f"{host(NICK)} JOIN #neon-doll",
    f"{S} 332 {NICK} #neon-doll :hot pink neon on midnight plum | cyberpunk, with a manicure",
    f"{S} 353 {NICK} = #neon-doll :{NICK} @kestrel +nyx orchid zephyr",
    f"{S} 366 {NICK} #neon-doll :End of /NAMES list.",
    f"{host(NICK)} JOIN #cyberpunk",
    f"{S} 353 {NICK} = #cyberpunk :{NICK} @rook glitch",
    f"{S} 366 {NICK} #cyberpunk :End of /NAMES list.",
    f"{host('kestrel')} PRIVMSG #neon-doll :anyone tried the new cursor theme?",
    f"{host('vesper')} JOIN #neon-doll",
    f"{host('vesper')} PRIVMSG #neon-doll :the black one with the pink halo? it's lovely",
    f"{host('orchid')} QUIT :Ping timeout: 240 seconds",
    f"{host('nyx')} PRIVMSG #neon-doll :{NICK}: does the light one work in tilix?",
    f"{host('kestrel')} MODE #neon-doll +o nyx",
    f"{host('kestrel')} PRIVMSG #neon-doll :\x01ACTION does a little spin\x01",
    f"{host('zephyr')} PART #neon-doll :off to bed",
    f"{host('vesper')} NICK vesper_",
    f"{host('rook')} PRIVMSG #cyberpunk :{NICK}, is the fuchsia only for where you are?",
    f"{host('glitch')} PRIVMSG #cyberpunk :rain again",
    f"{host('vesper_')} PRIVMSG {NICK} :sent you the screenshot",
]


def main():
    srv = socket.socket()
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind(("127.0.0.1", int(sys.argv[1])))
    srv.listen(1)
    conn, _ = srv.accept()
    conn.settimeout(0.05)
    for line in SCRIPT:
        conn.sendall((line + "\r\n").encode())
        time.sleep(0.1)
    # Stay up, answering pings, until the screenshot's taken.
    end = time.time() + 60
    while time.time() < end:
        try:
            data = conn.recv(4096)
        except socket.timeout:
            continue
        if not data:
            break
        for line in data.decode(errors="replace").splitlines():
            if line.startswith("PING"):
                conn.sendall(("PONG" + line[4:] + "\r\n").encode())


main()
