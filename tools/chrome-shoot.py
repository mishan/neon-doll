#!/usr/bin/env python3
"""Screenshot a Neon Doll Chrome theme in a throwaway Chrome profile.

    tools/chrome-shoot.py dark|light out.png

Branded Chrome ignores --load-extension, so the theme goes in over the
DevTools protocol (Extensions.loadUnpacked), which Chrome allows only with
--remote-debugging-pipe and --enable-unsafe-extension-debugging. Nothing
touches the real profile: it runs in a sealed shotbox session, which it
starts itself.
"""

import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if len(sys.argv) != 3 or sys.argv[1] not in ("dark", "light"):
    sys.exit(__doc__)
variant, out = sys.argv[1], Path(sys.argv[2]).resolve()

# In a sealed shotbox session (https://github.com/mishan/shotbox, on PATH),
# started around this script if it isn't in one already.
if not os.environ.get("SHOTBOX_SCRATCH"):
    os.execvp("shotbox", ["shotbox", "run", "--screen", "1200x760", "--",
                          sys.executable, os.path.abspath(__file__), *sys.argv[1:]])


def shotbox(*args):
    subprocess.run(["shotbox", *map(str, args)], check=True)

profile = tempfile.mkdtemp()
# Chrome writes "Cached Theme.pak" into an unpacked theme; keep it out of the repo.
theme = Path(profile) / "theme"
shutil.copytree(ROOT / "chrome" / f"neon-doll-{variant}", theme)

to_chrome_r, to_chrome_w = os.pipe()
from_chrome_r, from_chrome_w = os.pipe()
chrome = subprocess.Popen(
    ["google-chrome", f"--user-data-dir={profile}", "--no-first-run",
     "--no-default-browser-check", "--disable-gpu", "--ozone-platform=x11",
     "--remote-debugging-pipe", "--enable-unsafe-extension-debugging",
     "--window-position=0,0", "--window-size=1200,760", "about:blank"],
    # The protocol pipe is fds 3 (to Chrome) and 4 (from Chrome).
    pass_fds=(3, 4), preexec_fn=lambda: (os.dup2(to_chrome_r, 3), os.dup2(from_chrome_w, 4)),
    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
os.close(to_chrome_r)
os.close(from_chrome_w)
reader = os.fdopen(from_chrome_r, "rb")
buffer = b""


def call(i, method, **params):
    global buffer
    os.write(to_chrome_w, json.dumps({"id": i, "method": method, "params": params}).encode() + b"\0")
    while True:
        while b"\0" not in buffer:
            buffer += reader.read1(65536)
        msg, buffer = buffer.split(b"\0", 1)
        reply = json.loads(msg)
        if reply.get("id") == i:
            if "error" in reply:
                sys.exit(f"{method}: {reply['error']}")
            return reply.get("result")


try:
    shotbox("wait", "window", ".* - Google Chrome")
    call(1, "Extensions.loadUnpacked", path=str(theme))
    # The theme goes in after the call returns, with a bar saying so on the
    # tab in front: let that be about:blank, not the new tab in the picture.
    shotbox("wait", "stable", "1")
    target = call(2, "Target.createTarget", url="chrome://newtab/")
    call(3, "Target.createTarget", url="data:text/html,<title>man neon-doll</title>")
    call(4, "Target.activateTarget", targetId=target["targetId"])
    # The new tab page loads in pieces; a second without a change is done.
    shotbox("wait", "stable", "1")
    shotbox("capture", out)
finally:
    chrome.terminate()
    chrome.wait(timeout=10)
    shutil.rmtree(profile, ignore_errors=True)
print(out)
