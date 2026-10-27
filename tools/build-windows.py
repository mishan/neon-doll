#!/usr/bin/env python3
"""Build the Windows files: Terminal's color schemes and window themes, and
the Windhawk styler themes.

    tools/build-windows.py            write windows/terminal/ and windows/windhawk/
    tools/build-windows.py --check    fail if the output is stale

windows/terminal/neon-doll.json is a Windows Terminal *fragment*: dropped in
%LOCALAPPDATA%\\Microsoft\\Windows Terminal\\Fragments\\Neon Doll\\, it adds
both color schemes without anyone editing settings.json. The colors are the
Tilix schemes', entry for entry, so a terminal on either OS looks the same.

windows/terminal/themes.json holds the window themes (tab row and tab colors),
which fragments can't carry; they go into settings.json by hand. Same mapping
as Chrome's: the tab row is the page, the current tab is the panel lifted off
it.

windows/windhawk/{taskbar,start-menu}.yaml are themes for Windhawk's Windows
11 Taskbar Styler and Start Menu Styler mods, pasted into the mod's settings
in textual mode. Their colors are theme resources with a @Dark and a @Light
value, so they follow Windows' own light/dark mode; tints are #AARRGGBB.
"""

import json
import sys
from pathlib import Path

import tokens

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "windows" / "terminal"
WINDHAWK_OUT = ROOT / "windows" / "windhawk"

ANSI = ["black", "red", "green", "yellow", "blue", "purple", "cyan", "white",
        "brightBlack", "brightRed", "brightGreen", "brightYellow",
        "brightBlue", "brightPurple", "brightCyan", "brightWhite"]

PANEL = {v: tokens.palette(v)["panel"] for v in tokens.VARIANTS}


def scheme(variant):
    t = json.loads((ROOT / "tilix" / f"neon-doll-{variant}.json").read_text())
    s = {
        "name": t["name"],
        "background": t["background-color"],
        "foreground": t["foreground-color"],
        "cursorColor": t["cursor-background-color"],
        "selectionBackground": t["highlight-background-color"],
    }
    s.update(zip(ANSI, t["palette"]))
    return s


def theme(variant):
    bg = scheme(variant)["background"]
    return {
        "name": f"Neon Doll {variant.title()}",
        "window": {"applicationTheme": variant},
        "tabRow": {"background": bg + "ff", "unfocusedBackground": bg + "ff"},
        "tab": {
            "background": PANEL[variant] + "ff",
            "unfocusedBackground": bg + "ff",
            "showCloseButton": "hover",
        },
    }


# Windhawk style constant -> token or tint. Hover is wash-strong and pressed
# is press, as in GTK; the window you're in gets wash-pink and a pink rail.
WINDHAWK_COLORS = {
    "bg": "bg", "panel": "panel", "line": "line", "edge": "edge", "ink": "ink",
    "muted": "muted", "pink": "pink", "purple": "purple", "wash": "wash-strong",
    "press": "press", "washPink": "wash-pink", "edgePurple": "edge-purple",
}

WINDHAWK_TASKBAR = """\
  - target: Taskbar.TaskbarFrame > Grid#RootGrid > Taskbar.TaskbarBackground > Grid > Rectangle#BackgroundFill
    styles:
      - Fill:=$bg
  - target: Rectangle#BackgroundStroke
    styles:
      - Fill:=$line
  - target: Taskbar.TaskbarBackground#HoverFlyoutBackgroundControl > Grid > Rectangle#BackgroundFill
    styles:
      - Fill:=$bg
      - RadiusX=0
      - RadiusY=0
  - target: Taskbar.TaskbarBackground#HoverFlyoutBackgroundControl > Grid > Rectangle#BackgroundStroke
    styles:
      - Fill:=$none
      - Stroke:=$line
      - StrokeThickness=1
      - RadiusX=0
      - RadiusY=0
  - target: Taskbar.ExperienceToggleButton
    styles:
      - CornerRadius=0
  - target: Taskbar.SearchBoxButton
    styles:
      - CornerRadius=0
  - target: Taskbar.TaskListButton
    styles:
      - CornerRadius=0
  - target: Taskbar.TaskListButton > Grid#IconPanel@CommonStates > Border#BackgroundElement, Taskbar.TaskListButton > Taskbar.TaskListLabeledButtonPanel@CommonStates > Border#BackgroundElement
    styles:
      - CornerRadius=0
      - BorderThickness=0
      - Background:=$none
      - Background@ActiveNormal:=$washPink
      - Background@MultiWindowActive:=$washPink
      - Background@InactivePointerOver:=$wash
      - Background@ActivePointerOver:=$wash
      - Background@MultiWindowPointerOver:=$wash
      - Background@InactivePressed:=$press
      - Background@ActivePressed:=$press
      - Background@MultiWindowPressed:=$press
  - target: Taskbar.TaskListButtonPanel@CommonStates > Grid > Border#BackgroundElement, Taskbar.TaskListButtonPanel@CommonStates > Border#BackgroundElement
    styles:
      - CornerRadius=0
      - BorderThickness=0
      - Background:=$none
      - Background@InactivePointerOver:=$wash
      - Background@ActivePointerOver:=$wash
      - Background@InactivePressed:=$press
      - Background@ActivePressed:=$press
  - target: Grid#IconPanel@RunningIndicatorStates > Rectangle#RunningIndicator, Taskbar.TaskListLabeledButtonPanel@RunningIndicatorStates > Rectangle#RunningIndicator
    styles:
      - RadiusX=0
      - RadiusY=0
      - Height=2
      - Fill:=$purple
      - Fill@ActiveRunningIndicator:=$pink
      - Width@ActiveRunningIndicator=24
  - target: Border#SearchPillBackgroundElement
    styles:
      - CornerRadius=0
      - Background:=$panel
      - BorderBrush:=$edge
      - BorderThickness=1
  - target: TextBlock#SearchBoxTextBlock
    styles:
      - FontFamily=$mono
      - Foreground:=$muted
  - target: TextBlock#TimeInnerTextBlock, TextBlock#DateInnerTextBlock
    styles:
      - FontFamily=$mono
      - Foreground:=$ink
  - target: Border#OverflowFlyoutBackgroundBorder
    styles:
      - CornerRadius=0
      - Background:=$bg
      - BorderBrush:=$line
      - BorderThickness=1
  - target: SearchUx.SearchUI.SearchButtonRootGrid@CommonStates > Grid > Border#BackgroundElement, SearchUx.SearchUI.SearchButtonRootGrid@CommonStates > Border#BackgroundElement
    styles:
      - CornerRadius=0
      - BorderThickness=1
      - Background:=$panel
      - BorderBrush:=$edge
      - Background@InactivePointerOver:=$wash
      - Background@ActivePointerOver:=$wash
      - Background@InactivePressed:=$press
      - Background@ActivePressed:=$press
  - target: SystemTray.OmniButton > Grid@CommonStates > Border#BackgroundBorder, SystemTray.IconView > Grid#ContainerGrid@ > Border#BackgroundBorder
    styles:
      - CornerRadius=0
      - Background@PointerOver:=$wash
      - Background@Pressed:=$press
"""

WINDHAWK_START = """\
  - target: Border#AcrylicBorder
    styles:
      - Background:=$bg
      - BorderBrush:=$line
      - BorderThickness=1
      - CornerRadius=0
  - target: Border#AcrylicOverlay
    styles:
      - Opacity=0
  - target: StartMenu.StartBlendedFlexFrame, Grid#OuterBorderGrid
    styles:
      - CornerRadius=0
  - target: Border#StartDropShadow, Border#RightCompanionDropShadow
    styles:
      - Visibility=Collapsed
  - target: Border#TaskbarSearchBackground
    styles:
      - CornerRadius=0
      - Background:=$panel
      - BorderBrush:=$edge
      - BorderThickness=1
  - target: TextBlock#PlaceholderText
    styles:
      - FontFamily=$mono
      - Foreground:=$muted
  - target: TextBlock#PinnedListHeaderText, TextBlock#TopLevelSuggestionsListHeaderText, TextBlock#MoreSuggestionsListHeaderText, TextBlock#AllAppsHeading
    styles:
      - FontFamily=$mono
  - target: Border#BackgroundBorder
    styles:
      - CornerRadius=0
  - target: StartMenu.SearchBoxToggleButton#SearchBoxToggleButton
    styles:
      - CornerRadius=0
  - target: StartMenu.SearchBoxToggleButton#SearchBoxToggleButton > Grid > Border#BorderElement
    styles:
      - CornerRadius=0
      - Background:=$panel
      - BorderBrush:=$edge
      - BorderThickness=1
  - target: Button#ShowAllAppsButton, Button#CloseAllAppsButton, Button#ShowMorePinnedButton, Microsoft.UI.Xaml.Controls.DropDownButton
    styles:
      - CornerRadius=0
  - target: StartDocked.NavigationPaneButton#UserTileButton > Grid@CommonStates > Border, StartDocked.NavigationPaneButton#PowerButton > Grid@CommonStates > Border
    styles:
      - CornerRadius=0
  - target: StartDocked.SearchBoxToggleButton > Grid > Border
    styles:
      - CornerRadius=0
      - Background:=$panel
      - BorderBrush:=$edge
      - BorderThickness=1
  - target: Button#ShowAllAppsButton > ContentPresenter@CommonStates, Button#CloseAllAppsButton > ContentPresenter@CommonStates
    styles:
      - CornerRadius=0
      - BorderThickness=1
      - Background:=$none
      - BorderBrush:=$edgePurple
      - Foreground:=$purple
      - Background@PointerOver:=$wash
      - Foreground@PointerOver:=$purple
      - BorderBrush@PointerOver:=$purple
      - Background@Pressed:=$press
      - Foreground@Pressed:=$purple
  - target: Border#ContentBorder@CommonStates > Grid#DroppedFlickerWorkaroundWrapper > Border#BackgroundBorder
    styles:
      - Background@PointerOver:=$wash
      - Background@Pressed:=$press
"""


def windhawk(styles):
    resources = []
    constants = ["mono=Cascadia Mono"]
    for name, token in WINDHAWK_COLORS.items():
        key = "Nd" + name[0].upper() + name[1:]
        for v in ("dark", "light"):
            if token in tokens.tints(v):
                color, alpha = tokens.tint(v, token)
                value = f"#{round(alpha * 255):02X}{color.lstrip('#').upper()}"
            else:
                value = tokens.palette(v)[token]
            resources.append(f"{key}@{v.title()}={value}")
        constants.append(f'{name}=<SolidColorBrush Color="{{ThemeResource {key}}}"/>')
    constants.append('none=<SolidColorBrush Color="Transparent"/>')
    lines = ["themeResourceVariables:", *(f"  - {r}" for r in resources),
             "styleConstants:", *(f"  - {c}" for c in constants), "controlStyles:"]
    return ("\n".join(lines) + "\n" + styles).encode()


def outputs():
    variants = ("dark", "light")
    dump = lambda o: (json.dumps(o, indent=2) + "\n").encode()
    yield OUT / "neon-doll.json", dump({"schemes": [scheme(v) for v in variants]})
    yield OUT / "themes.json", dump({"themes": [theme(v) for v in variants]})
    yield WINDHAWK_OUT / "taskbar.yaml", windhawk(WINDHAWK_TASKBAR)
    yield WINDHAWK_OUT / "start-menu.yaml", windhawk(WINDHAWK_START)


def main():
    check = "--check" in sys.argv
    stale = []
    for path, data in outputs():
        if check:
            if not path.exists() or path.read_bytes() != data:
                stale.append(path.relative_to(ROOT))
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
            print(path.relative_to(ROOT))
    if stale:
        sys.exit("stale: " + ", ".join(map(str, stale)) + " (run tools/build-windows.py)")


main()
