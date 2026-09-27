#!/usr/bin/env python3
"""Screenshot the Roundcube skin, in a scratch Roundcube with a pretend
mailbox.

    tools/roundcube-shoot.py OUTDIR [dark|light ...] [--keep] [--scene NAME ...]
    tools/roundcube-shoot.py --thumbnail    the skin chooser's picture

Starts two containers, Roundcube with roundcube/neon-doll mounted as its
skin and GreenMail for IMAP, fills the mailbox (tools/roundcube-mail.py),
then drives headless Chrome over the DevTools protocol: logs in, and for
each variant and scene writes OUTDIR/roundcube-SCENE-VARIANT.png. Light or
dark is the system preference Chrome reports, which Roundcube follows.
--thumbnail
shrinks the dark mail scene into roundcube/neon-doll/thumbnail.png, the
64px picture in Settings' skin chooser. --keep leaves the containers up (Roundcube on localhost:8089, user doll,
password doll) for poking at by hand, and reuses them next time.

Needs docker and google-chrome. ROUNDCUBE_IMAGE picks another Roundcube,
e.g. roundcube/roundcubemail:1.6.18-apache.
"""

import base64
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ROUNDCUBE = os.environ.get("ROUNDCUBE_IMAGE", "roundcube/roundcubemail:1.7.4-apache")
GREENMAIL = "greenmail/standalone:2.1.3"
NET, WEB, MAIL = "nd-roundcube", "nd-roundcube-web", "nd-roundcube-mail"
URL = "http://localhost:8089/"
SIZE = (1280, 800)


def docker(*args, check=True):
    return subprocess.run(["docker", *args], check=check, capture_output=True, text=True)


def running(name):
    r = docker("inspect", "-f", "{{.State.Running}}", name, check=False)
    return r.stdout.strip() == "true"


def start():
    if running(WEB) and running(MAIL):
        return
    stop()
    docker("network", "create", NET, check=False)
    docker("run", "-d", "--name", MAIL, "--network", NET, "-p", "3143:3143",
           "-e", "GREENMAIL_OPTS=-Dgreenmail.setup.test.all -Dgreenmail.hostname=0.0.0.0 "
                 "-Dgreenmail.auth.disabled -Dgreenmail.users=doll:doll@neon.test",
           GREENMAIL)
    docker("run", "-d", "--name", WEB, "--network", NET, "-p", "8089:80",
           "-v", f"{ROOT / 'roundcube' / 'neon-doll'}:/var/www/html/skins/neon-doll:ro",
           "-e", f"ROUNDCUBEMAIL_DEFAULT_HOST={MAIL}", "-e", "ROUNDCUBEMAIL_DEFAULT_PORT=3143",
           "-e", f"ROUNDCUBEMAIL_SMTP_SERVER={MAIL}", "-e", "ROUNDCUBEMAIL_SMTP_PORT=3025",
           "-e", "ROUNDCUBEMAIL_DB_TYPE=sqlite", "-e", "ROUNDCUBEMAIL_SKIN=neon-doll",
           ROUNDCUBE)
    for _ in range(60):
        try:
            urllib.request.urlopen(URL, timeout=2)
            break
        except OSError:
            time.sleep(1)
    else:
        sys.exit("Roundcube didn't come up on " + URL)


def stop():
    docker("rm", "-f", WEB, MAIL, check=False)
    docker("network", "rm", NET, check=False)


class Chrome:
    """Just enough of the DevTools protocol, over --remote-debugging-pipe."""

    def __init__(self):
        self.profile = tempfile.mkdtemp()
        to_r, self.to_w = os.pipe()
        from_r, from_w = os.pipe()
        self.proc = subprocess.Popen(
            ["google-chrome", "--headless=new", f"--user-data-dir={self.profile}",
             "--no-first-run", "--no-default-browser-check", "--disable-gpu",
             "--hide-scrollbars", "--remote-debugging-pipe", "about:blank"],
            pass_fds=(3, 4), preexec_fn=lambda: (os.dup2(to_r, 3), os.dup2(from_w, 4)),
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        os.close(to_r)
        os.close(from_w)
        self.reader = os.fdopen(from_r, "rb")
        self.buffer = b""
        self.id = 0
        target = self.call("Target.createTarget", url="about:blank")["targetId"]
        self.session = self.call("Target.attachToTarget", targetId=target, flatten=True)["sessionId"]
        self.page("Page.enable")
        self.page("Emulation.setDeviceMetricsOverride", width=SIZE[0], height=SIZE[1],
                  deviceScaleFactor=1, mobile=False)

    def call(self, method, session=None, **params):
        self.id += 1
        msg = {"id": self.id, "method": method, "params": params}
        if session:
            msg["sessionId"] = session
        os.write(self.to_w, json.dumps(msg).encode() + b"\0")
        while True:
            while b"\0" not in self.buffer:
                self.buffer += self.reader.read1(65536)
            raw, self.buffer = self.buffer.split(b"\0", 1)
            reply = json.loads(raw)
            if reply.get("id") == self.id:
                if "error" in reply:
                    sys.exit(f"{method}: {reply['error']}")
                return reply.get("result")

    def page(self, method, **params):
        return self.call(method, session=self.session, **params)

    def js(self, expr):
        r = self.page("Runtime.evaluate", expression=expr, awaitPromise=True, returnByValue=True)
        if "exceptionDetails" in r:
            sys.exit(f"{expr}: {r['exceptionDetails']}")
        return r["result"].get("value")

    def wait(self, expr, timeout=20):
        end = time.time() + timeout
        while time.time() < end:
            if self.js(expr):
                return
            time.sleep(0.25)
        sys.exit("timed out waiting for " + expr)

    def go(self, url, ready="document.readyState == 'complete'"):
        self.page("Page.navigate", url=url)
        time.sleep(0.5)
        self.wait(ready)

    def shoot(self, path):
        time.sleep(1.2)
        data = self.page("Page.captureScreenshot", format="png")["data"]
        Path(path).write_bytes(base64.b64decode(data))
        print(path)

    def close(self):
        self.proc.terminate()
        self.proc.wait(timeout=10)
        shutil.rmtree(self.profile, ignore_errors=True)


# Each scene: (URL, JavaScript that sets it up once loaded, what to wait for).
MAIL_READY = "!!document.querySelector('#messagelist tbody tr')"
SCENES = {
    "login": (URL, None, "!!document.querySelector('#rcmloginuser')"),
    "mail": (URL + "?_task=mail&_mbox=INBOX", """
        rcmail.message_list.select(rcmail.message_list.rows[
          Object.keys(rcmail.message_list.rows).sort((a, b) => b - a)[0]].uid);
        """, MAIL_READY),
    "contacts": (URL + "?_task=addressbook", """
        rcmail.display_message('Contact saved', 'confirmation');
        """, "!!document.querySelector('#contacts-table')"),
    "search": (URL + "?_task=mail&_mbox=INBOX", """
        document.querySelector('#mailsearchform').value = 'rooftop';
        document.querySelector('#layout-list .searchbar a.options').click();
        """, MAIL_READY),
    "compose": (URL + "?_task=mail&_action=compose", """
        document.querySelector('#compose-subject').value = 'Neon for the rooftop';
        """, "!!document.querySelector('#compose-subject')"),
    "settings": (URL + "?_task=settings&_action=preferences", """
        rcmail.sections_list.select('general');
        """, "!!document.querySelector('#sections-table')"),
    "menu": (URL + "?_task=mail&_mbox=INBOX", """
        rcmail.message_list.select(rcmail.message_list.rows[
          Object.keys(rcmail.message_list.rows).sort((a, b) => b - a)[0]].uid);
        setTimeout(() => document.querySelector('a.more').click(), 1200);
        """, MAIL_READY),
    "dialog": (URL + "?_task=mail&_mbox=INBOX", """
        rcmail.simple_dialog('<p>Delete the 3 selected messages? This can\\'t be undone.</p>',
          'Delete messages', function(){}, {button: 'delete', button_class: 'delete'});
        """, MAIL_READY),
}


def login(chrome):
    chrome.go(URL + "?_task=mail", "!!document.querySelector('#rcmloginuser, #messagelist')")
    if chrome.js("!!document.querySelector('#rcmloginuser')"):
        chrome.js("""
            document.querySelector('#rcmloginuser').value = 'doll';
            document.querySelector('#rcmloginpwd').value = 'doll';
            document.querySelector('#rcmloginsubmit').click();
            """)
        time.sleep(1)
        chrome.wait("!!document.querySelector('#messagelist')")


def main():
    args = sys.argv[1:]
    keep = "--keep" in args
    scenes = []
    while "--scene" in args:
        i = args.index("--scene")
        scenes.append(args[i + 1])
        del args[i:i + 2]
    args = [a for a in args if a != "--keep"]
    if "--thumbnail" in args:
        tmp = Path(tempfile.mkdtemp())
        args = [str(tmp), "dark"]
        scenes = ["mail"]
    out = Path(args[0])
    variants = [a for a in args[1:] if a in ("dark", "light")] or ["dark", "light"]
    out.mkdir(parents=True, exist_ok=True)

    start()
    subprocess.run([sys.executable, str(ROOT / "tools" / "roundcube-mail.py"),
                    "localhost", "3143", "doll", "doll"], check=True)
    chrome = Chrome()
    try:
        for variant in variants:
            chrome.page("Emulation.setEmulatedMedia", features=[
                {"name": "prefers-color-scheme", "value": variant}])
            for name in scenes or list(SCENES):
                url, setup, ready = SCENES[name]
                if name == "login":
                    chrome.page("Network.clearBrowserCookies")
                else:
                    login(chrome)
                chrome.go(url, ready)
                time.sleep(0.8)
                if setup:
                    chrome.js(setup + "; void 0")
                chrome.shoot(out / f"roundcube-{name}-{variant}.png")
    finally:
        chrome.close()
        if not keep:
            stop()
    if "--thumbnail" in sys.argv:
        # The folders, the list and the start of the message, squared off.
        subprocess.run(["convert", str(out / "roundcube-mail-dark.png"), "-crop", "800x800+0+0",
                        "-resize", "64x64", "-strip", "-colors", "256",
                        str(ROOT / "roundcube" / "neon-doll" / "thumbnail.png")], check=True)
        shutil.rmtree(out)
        print(ROOT / "roundcube" / "neon-doll" / "thumbnail.png")


if __name__ == "__main__":
    main()
