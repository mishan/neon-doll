#!/usr/bin/env python3
"""Run a command in a pseudo-terminal and answer its questions.

    tests/pty_run.py STEP... -- COMMAND [ARG...]

The steps run in order:

    expect:REGEX   wait until REGEX turns up in what the command has
                   written since the last thing sent
    send:TEXT      type TEXT; \\r, \\n, \\x1b and the like are unescaped
    tick:TAG       type the number the text picker shows before TAG, then
                   Enter

Then it waits for the command to exit, prints everything it wrote with the
terminal escapes taken out, and exits with its status. A step that times out
prints what there was and exits 124.

The installers' pickers want a terminal, which a test harness hasn't got.
PowerShell on Unix asks the terminal where the cursor is before reading a
line, so that question gets an answer too.
"""

import os
import pty
import re
import select
import signal
import sys
import time

TIMEOUT = float(os.environ.get("PTY_TIMEOUT", "30"))
ESCAPES = re.compile(rb"\x1b\[[0-9;?]*[ -/]*[@-~]|\x1b[()][A-Z0-9]|\x1b[=>78]|\x1b\][^\x07]*\x07|\x0f|\x0e")


def main():
    args = sys.argv[1:]
    if "--" not in args:
        sys.exit(__doc__)
    split = args.index("--")
    steps, command = args[:split], args[split + 1:]

    pid, fd = pty.fork()
    if pid == 0:
        os.environ.setdefault("TERM", "xterm")
        os.execvp(command[0], command)

    try:
        import fcntl
        import struct
        import termios
        fcntl.ioctl(fd, termios.TIOCSWINSZ, struct.pack("HHHH", 40, 100, 0, 0))
    except (ImportError, OSError):
        pass

    out = bytearray()
    mark = 0

    def read(timeout):
        """Read what there is for up to `timeout` seconds; False at EOF."""
        r, _, _ = select.select([fd], [], [], timeout)
        if not r:
            return True
        try:
            chunk = os.read(fd, 65536)
        except OSError:
            return False
        if not chunk:
            return False
        out.extend(chunk)
        if b"\x1b[6n" in chunk:
            os.write(fd, b"\x1b[1;1R")
        return True

    def text(start=0):
        return ESCAPES.sub(b"", bytes(out[start:])).decode(errors="replace").replace("\r", "")

    def fail(why):
        print(text())
        print(f"pty_run: {why}", file=sys.stderr)
        os.kill(pid, signal.SIGKILL)
        sys.exit(124)

    def wait_for(pattern):
        deadline = time.time() + TIMEOUT
        while time.time() < deadline:
            m = re.search(pattern, text(mark), re.M)
            if m:
                return m
            if not read(0.1):
                break
        fail(f"never saw /{pattern}/")

    def send(s):
        nonlocal mark
        mark = len(out)
        os.write(fd, s.encode())

    for step in steps:
        kind, _, arg = step.partition(":")
        if kind == "expect":
            wait_for(arg)
        elif kind == "send":
            send(arg.encode().decode("unicode_escape"))
        elif kind == "tick":
            m = wait_for(rf"^\s*(\d+)\s+\[.\]\s+{re.escape(arg)}(\s|$)")
            wait_for(r"Enter to go on")
            send(m.group(1) + "\r")
        else:
            sys.exit(f"pty_run: unknown step {step!r}")

    deadline = time.time() + TIMEOUT
    while time.time() < deadline and read(0.1):
        pass
    deadline = time.time() + 10
    while True:
        done, status = os.waitpid(pid, os.WNOHANG)
        if done:
            break
        if time.time() > deadline:
            fail("the command didn't exit")
        time.sleep(0.05)
    print(text())
    sys.exit(os.waitstatus_to_exitcode(status))


main()
