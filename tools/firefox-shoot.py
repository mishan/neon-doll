#!/usr/bin/env python3
"""Screenshot the Neon Doll Firefox theme in a throwaway Firefox profile.

    env -u DISPLAY -u WAYLAND_DISPLAY MOZ_ENABLE_WAYLAND=0 \\
      xvfb-run -a -s "-screen 0 1200x760x24" tools/firefox-shoot.py dark out.png

    --userchrome    also load firefox/userChrome.css
    --menu          open the main menu instead of the address bar

Release Firefox won't install an unsigned add-on from a pref or the command
line, so the theme goes in as a temporary add-on over Marionette
(Addon:Install), which Firefox allows with --marionette; the tabs and the
open address bar or menu are set up from browser chrome, which also needs
-remote-allow-system-access. The system color scheme is forced with
ui.systemUsesDarkTheme, which is what the theme's dark_theme follows. It
refuses to run outside xvfb-run, and nothing touches the real profile.
"""

import json
import os
import shutil
import socket
import subprocess
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
args = [a for a in sys.argv[1:] if not a.startswith("--")]
if len(args) != 2 or args[0] not in ("dark", "light"):
    sys.exit(__doc__)
variant, out = args[0], Path(args[1]).resolve()
userchrome = "--userchrome" in sys.argv
menu = "--menu" in sys.argv

# xvfb-run points XAUTHORITY at its own temp file; a real session never does.
if "xvfb-run" not in os.environ.get("XAUTHORITY", "") or not os.environ.get("DISPLAY"):
    sys.exit("run this under xvfb-run (see the docstring)")
env = {k: v for k, v in os.environ.items() if k != "WAYLAND_DISPLAY"}
env["MOZ_ENABLE_WAYLAND"] = "0"
env["MOZ_CRASHREPORTER_DISABLE"] = "1"

with socket.socket() as s:
    s.bind(("127.0.0.1", 0))
    port = s.getsockname()[1]

profile = Path(tempfile.mkdtemp(prefix="neon-doll-firefox-"))
# Even with -profile, the crash helper writes into ~/.mozilla unless told
# otherwise.
env["MOZ_CRASHREPORTER_DATA_DIRECTORY"] = str(profile / "crashes")
prefs = {
    "marionette.port": port,
    # Marionette's own defaults blank the New Tab page; the rest of this
    # list keeps a fresh profile quiet and offline instead.
    "remote.prefs.recommended": False,
    "ui.systemUsesDarkTheme": 1 if variant == "dark" else 0,
    "toolkit.legacyUserProfileCustomizations.stylesheets": userchrome,
    "browser.shell.checkDefaultBrowser": False,
    "browser.aboutwelcome.enabled": False,
    "browser.startup.homepage_override.mstone": "ignore",
    "startup.homepage_welcome_url": "",
    "browser.startup.firstrunSkipsHomepage": True,
    "datareporting.policy.dataSubmissionEnabled": False,
    "datareporting.healthreport.uploadEnabled": False,
    "toolkit.telemetry.reportingpolicy.firstRun": False,
    "browser.urlbar.suggest.openpage": False,
    "browser.urlbar.suggest.history": False,
    "browser.newtabpage.activity-stream.feeds.section.topstories": False,
    "browser.newtabpage.activity-stream.showSponsored": False,
    "browser.newtabpage.activity-stream.showSponsoredTopSites": False,
    "browser.search.suggest.enabled": False,
    "browser.urlbar.suggest.quicksuggest.sponsored": False,
    "browser.urlbar.suggest.trending": False,
    "browser.newtabpage.activity-stream.showWeather": False,
    "browser.newtabpage.activity-stream.system.showWeather": False,
    "browser.toolbars.bookmarks.visibility": "never",
    "browser.ipProtection.enabled": False,
    "app.normandy.enabled": False,
    "app.shield.optoutstudies.enabled": False,
    "messaging-system.rsexperimentloader.enabled": False,
    "extensions.update.enabled": False,
    "app.update.disabledForTesting": True,
    "app.update.auto": False,
    "sidebar.revamp": False,
    "browser.tabs.inTitlebar": 0,
}
(profile / "user.js").write_text(
    "".join(f"user_pref({json.dumps(k)}, {json.dumps(v)});\n" for k, v in prefs.items()))
if userchrome:
    (profile / "chrome").mkdir()
    shutil.copy(ROOT / "firefox" / "userChrome.css", profile / "chrome")

firefox = subprocess.Popen(
    ["firefox", "--marionette", "-remote-allow-system-access", "-no-remote",
     "-profile", str(profile), "about:blank"],
    env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


class Marionette:
    def __init__(self):
        for _ in range(60):
            try:
                self.sock = socket.create_connection(("127.0.0.1", port))
                break
            except OSError:
                time.sleep(0.5)
        else:
            sys.exit("Marionette never came up")
        self.buf = b""
        self.id = 0
        self.read()  # the server's hello

    def read(self):
        while b":" not in self.buf:
            self.buf += self.sock.recv(65536)
        size, rest = self.buf.split(b":", 1)
        while len(rest) < int(size):
            rest += self.sock.recv(65536)
        msg, self.buf = rest[:int(size)], rest[int(size):]
        return json.loads(msg)

    def __call__(self, command, **params):
        self.id += 1
        data = json.dumps([0, self.id, command, params]).encode()
        self.sock.sendall(str(len(data)).encode() + b":" + data)
        while True:
            _, i, error, result = self.read()
            if i == self.id:
                if error:
                    sys.exit(f"{command}: {error}")
                return result


def chrome_js(m, script):
    return m("WebDriver:ExecuteScript", script=script, args=[])["value"]


try:
    m = Marionette()
    m("WebDriver:NewSession", capabilities={})
    m("Addon:Install", path=str(ROOT / "firefox"), temporary=True)
    m("WebDriver:SetWindowRect", x=0, y=0, width=1200, height=760)
    m("WebDriver:Navigate", url="about:newtab")
    m("Marionette:SetContext", value="chrome")
    chrome_js(m, """
        const p = Services.scriptSecurityManager.getSystemPrincipal();
        const titles = ["man neon-doll", "NEON-DOLL(7) - rules", "palette.css"];
        titles.forEach((title, index) => gBrowser.addTab("data:text/html," + encodeURIComponent(
          `<meta name=color-scheme content="light dark"><title>${title}</title>`),
          {index, triggeringPrincipal: p}));
    """)
    time.sleep(6)
    # Marionette stripes the address bar red while it drives the browser.
    chrome_js(m, 'document.documentElement.removeAttribute("remotecontrol");')
    if menu:
        chrome_js(m, 'PanelUI.show();')
    else:
        chrome_js(m, 'gURLBar.focus(); gURLBar.search("neon doll");')
    time.sleep(2)
    subprocess.run(["import", "-window", "root", "-crop", "1200x760+0+0", "-strip", str(out)],
                   check=True, env=env)
finally:
    firefox.terminate()
    try:
        firefox.wait(timeout=15)
    except subprocess.TimeoutExpired:
        firefox.kill()
    shutil.rmtree(profile, ignore_errors=True)
print(out)
