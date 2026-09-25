#!/usr/bin/env python3
"""Screenshot a Neon Doll Chrome theme in a throwaway Chrome profile.

    xvfb-run -a -s "-screen 0 1200x760x24" tools/chrome-shoot.py dark out.png

Branded Chrome ignores --load-extension, so the theme goes in over the
DevTools protocol (Extensions.loadUnpacked), which Chrome allows only with
--remote-debugging-pipe and --enable-unsafe-extension-debugging. Nothing
touches the real profile.
"""

import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
variant, out = sys.argv[1], Path(sys.argv[2]).resolve()
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
    time.sleep(3)
    call(1, "Extensions.loadUnpacked", path=str(theme))
    target = call(2, "Target.createTarget", url="chrome://newtab/")
    call(3, "Target.createTarget", url="data:text/html,<title>man neon-doll</title>")
    call(4, "Target.activateTarget", targetId=target["targetId"])
    time.sleep(4)
    subprocess.run(["import", "-window", "root", "-crop", "1200x760+0+0", "-strip", str(out)], check=True)
finally:
    chrome.terminate()
    chrome.wait(timeout=10)
    shutil.rmtree(profile, ignore_errors=True)
print(out)
