#!/usr/bin/env python3
"""Build the VS Code color themes into vscode/.

A VS Code theme is a map of workbench color ids, TextMate token rules and
semantic token rules. Colors take alpha (#rrggbbaa), so the tints here are
the gtk.css rgba tokens as they are, not flattened; VS Code composites them.
Output is committed, so packaging needs no Python beyond the .vsix step.

    tools/build-vscode.py              write both themes and the icon
    tools/build-vscode.py --check      fail if the output is stale
    tools/build-vscode.py --vsix OUT   also zip vscode/ into OUT as a .vsix,
                                       for when @vscode/vsce isn't at hand

Mapping. The editor is the page; the side bar, panel, title bar, status bar,
tab strip and every widget are panels, each edged with a 1px line. Chrome
text is muted and nothing casts a shadow.

Fuchsia is position: the cursor, the current line number, the matching
bracket, the selection, the current find match, the active tab's top rail
and title, the focus border, the focused list row, the active activity-bar
item's indicator, the active panel tab's underline, a checked input toggle.
Hover is a position too, so hover is a faint fuchsia wash. Purple is
interactive at rest: links, badges, the other find matches, and the primary
button. VS Code buttons are fills with an optional border for all kinds, so
the primary button is the nearest thing to the desktop's outline: a purple
wash, purple text and a purple 1px border. Its text can't change on hover,
so hover only turns the wash fuchsia.

Syntax is the editor schemes' four colors (see tools/scheme-colors.py):
keywords fuchsia; numbers, constants, types and builtins purple; strings
yellow; comments muted italic; everything else ink. Bracket-pair colors are
all ink, so the matching bracket is the only one that lights up. Diffs are
green and red text on a green and red row tint. The integrated terminal's
sixteen colors are the Tilix schemes', entry for entry.
"""

import json
import struct
import sys
import zipfile
import zlib
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "vscode"

PALETTES = {
    "dark": {
        "bg": "#0f0d14", "panel": "#16131d", "line": "#2a2438",
        "ink": "#ebe6f0", "muted": "#9c93ab", "dimmest": "#6f6880",
        "pink": "#ff2d95", "purple": "#b48cff",
        "string": "#e5c07b", "add": "#7ee787", "del": "#ff7b72",
        # Row tints in the diff editor: gtk.css's --diff-*-bg, which are not
        # quite the text colors.
        "add-tint": "#3fb950", "del-tint": "#f85149",
        # Alphas, from gtk.css.
        "wash": 0.06, "wash-strong": 0.10, "press": 0.16, "edge": 0.30,
        "select": 0.30, "wash-pink": 0.16, "diff": 0.10, "refine": 0.25,
    },
    "light": {
        "bg": "#f7f4fa", "panel": "#ede7f3", "line": "#d6cce2",
        "ink": "#1a1522", "muted": "#5f5670", "dimmest": "#8d84a0",
        "pink": "#c8006a", "purple": "#6a3fd0",
        "string": "#8a6100", "add": "#1f7a33", "del": "#c4312a",
        "add-tint": "#1f7a33", "del-tint": "#c4312a",
        # Light diff rows are 7%: at 10% the row's own text drops below 4.5:1.
        "wash": 0.05, "wash-strong": 0.09, "press": 0.14, "edge": 0.30,
        "select": 0.18, "wash-pink": 0.08, "diff": 0.07, "refine": 0.20,
    },
}

ANSI = ["black", "red", "green", "yellow", "blue", "magenta", "cyan", "white"]


def a(color, alpha):
    """`color` at `alpha`, as #rrggbbaa."""
    return "%s%02x" % (color, round(alpha * 255))


CLEAR = "#00000000"


def colors(variant, p):
    tilix = json.loads((ROOT / "tilix" / f"neon-doll-{variant}.json").read_text())
    ansi = tilix["palette"]
    bg, panel, line = p["bg"], p["panel"], p["line"]
    ink, muted, dimmest = p["ink"], p["muted"], p["dimmest"]
    pink, purple = p["pink"], p["purple"]
    string, add, dele = p["string"], p["add"], p["del"]
    blue = ansi[4]

    wash = a(purple, p["wash"])
    wash_strong = a(purple, p["wash-strong"])
    press = a(purple, p["press"])
    edge = a(purple, p["edge"])
    select = a(pink, p["select"])
    wash_pink = a(pink, p["wash-pink"])
    hover = a(pink, p["wash-pink"] / 2)
    add_bg, del_bg = a(p["add-tint"], p["diff"]), a(p["del-tint"], p["diff"])
    add_refine, del_refine = a(p["add-tint"], p["refine"]), a(p["del-tint"], p["refine"])

    c = {
        # --- base ---------------------------------------------------------
        "foreground": ink,
        "descriptionForeground": muted,
        "disabledForeground": dimmest,
        "errorForeground": dele,
        "icon.foreground": muted,
        "focusBorder": pink,
        "contrastBorder": CLEAR,
        "contrastActiveBorder": CLEAR,
        "selection.background": select,
        "widget.shadow": CLEAR,
        "widget.border": line,
        "sash.hoverBorder": pink,
        "textLink.foreground": purple,
        "textLink.activeForeground": pink,
        "textPreformat.foreground": ink,
        "textPreformat.background": wash_strong,
        "textBlockQuote.background": wash,
        "textBlockQuote.border": edge,
        "textCodeBlock.background": wash,
        "textSeparator.foreground": line,
        "toolbar.hoverBackground": hover,
        "toolbar.activeBackground": wash_pink,
        "progressBar.background": pink,

        # --- window: title bar, activity bar, side bar, panel -------------
        "titleBar.activeBackground": panel,
        "titleBar.activeForeground": muted,
        "titleBar.inactiveBackground": panel,
        "titleBar.inactiveForeground": dimmest,
        "titleBar.border": line,
        "commandCenter.background": bg,
        "commandCenter.foreground": muted,
        "commandCenter.activeBackground": hover,
        "commandCenter.activeForeground": ink,
        "commandCenter.border": line,
        "commandCenter.activeBorder": line,
        "commandCenter.inactiveForeground": dimmest,
        "commandCenter.inactiveBorder": line,
        "menubar.selectionBackground": hover,
        "menubar.selectionForeground": ink,
        "menu.background": panel,
        "menu.foreground": ink,
        "menu.border": line,
        "menu.selectionBackground": wash_pink,
        "menu.selectionForeground": ink,
        "menu.separatorBackground": line,

        "activityBar.background": panel,
        "activityBar.foreground": ink,
        "activityBar.inactiveForeground": muted,
        "activityBar.border": line,
        "activityBar.activeBorder": pink,
        "activityBar.activeBackground": CLEAR,
        "activityBar.activeFocusBorder": pink,
        "activityBar.dropBorder": pink,
        "activityBarBadge.background": purple,
        "activityBarBadge.foreground": bg,
        "activityBarTop.foreground": ink,
        "activityBarTop.inactiveForeground": muted,
        "activityBarTop.activeBorder": pink,

        "sideBar.background": panel,
        "sideBar.foreground": ink,
        "sideBar.border": line,
        "sideBar.dropBackground": wash_pink,
        "sideBarTitle.foreground": muted,
        "sideBarSectionHeader.background": panel,
        "sideBarSectionHeader.foreground": muted,
        "sideBarSectionHeader.border": line,
        "sideBarStickyScroll.background": panel,
        "sideBarStickyScroll.border": line,
        "sideBarStickyScroll.shadow": CLEAR,

        "panel.background": panel,
        "panel.border": line,
        "panel.dropBorder": pink,
        "panelTitle.activeForeground": ink,
        "panelTitle.inactiveForeground": muted,
        "panelTitle.activeBorder": pink,
        "panelSection.border": line,
        "panelSection.dropBackground": wash_pink,
        "panelSectionHeader.background": panel,
        "panelSectionHeader.foreground": muted,
        "panelSectionHeader.border": line,
        "panelInput.border": line,
        "outputView.background": panel,
        "outputViewStickyScroll.background": panel,

        # --- status bar -----------------------------------------------------
        "statusBar.background": panel,
        "statusBar.foreground": muted,
        "statusBar.border": line,
        "statusBar.focusBorder": pink,
        "statusBar.noFolderBackground": panel,
        "statusBar.noFolderForeground": muted,
        "statusBar.noFolderBorder": line,
        # Debugging is a state, not a place: a purple wash, purple text.
        "statusBar.debuggingBackground": press,
        "statusBar.debuggingForeground": purple,
        "statusBar.debuggingBorder": edge,
        "statusBarItem.hoverBackground": hover,
        "statusBarItem.hoverForeground": ink,
        "statusBarItem.activeBackground": wash_pink,
        "statusBarItem.focusBorder": pink,
        "statusBarItem.compactHoverBackground": hover,
        "statusBarItem.remoteBackground": CLEAR,
        "statusBarItem.remoteForeground": purple,
        "statusBarItem.remoteHoverBackground": hover,
        "statusBarItem.remoteHoverForeground": ink,
        "statusBarItem.offlineBackground": a(dele, 0.16),
        "statusBarItem.offlineForeground": dele,
        "statusBarItem.prominentBackground": press,
        "statusBarItem.prominentForeground": purple,
        "statusBarItem.prominentHoverBackground": hover,
        "statusBarItem.errorBackground": CLEAR,
        "statusBarItem.errorForeground": dele,
        "statusBarItem.errorHoverBackground": hover,
        "statusBarItem.warningBackground": CLEAR,
        "statusBarItem.warningForeground": string,
        "statusBarItem.warningHoverBackground": hover,

        # --- tabs and breadcrumbs -------------------------------------------
        "editorGroupHeader.tabsBackground": panel,
        "editorGroupHeader.tabsBorder": line,
        "editorGroupHeader.noTabsBackground": panel,
        "editorGroupHeader.border": line,
        "editorGroup.border": line,
        "editorGroup.dropBackground": wash_pink,
        "editorGroup.dropIntoPromptBackground": panel,
        "editorGroup.dropIntoPromptForeground": ink,
        "editorGroup.dropIntoPromptBorder": line,
        "editorGroup.emptyBackground": bg,
        "editorPane.background": bg,
        "tab.activeBackground": bg,
        "tab.activeForeground": pink,
        "tab.activeBorderTop": pink,
        "tab.activeBorder": bg,
        "tab.activeModifiedBorder": pink,
        "tab.unfocusedActiveBackground": bg,
        "tab.unfocusedActiveForeground": ink,
        "tab.unfocusedActiveBorderTop": edge,
        "tab.unfocusedActiveBorder": bg,
        "tab.unfocusedActiveModifiedBorder": edge,
        "tab.inactiveBackground": panel,
        "tab.inactiveForeground": muted,
        "tab.inactiveModifiedBorder": edge,
        "tab.unfocusedInactiveBackground": panel,
        "tab.unfocusedInactiveForeground": dimmest,
        "tab.unfocusedInactiveModifiedBorder": edge,
        "tab.hoverBackground": hover,
        "tab.hoverForeground": ink,
        "tab.unfocusedHoverBackground": hover,
        "tab.unfocusedHoverForeground": ink,
        "tab.border": line,
        "tab.lastPinnedBorder": line,
        "tab.dragAndDropBorder": pink,
        "tab.selectedBackground": bg,
        "tab.selectedForeground": ink,
        "tab.selectedBorderTop": edge,
        "breadcrumb.background": bg,
        "breadcrumb.foreground": muted,
        "breadcrumb.focusForeground": ink,
        "breadcrumb.activeSelectionForeground": pink,
        "breadcrumbPicker.background": panel,

        # --- editor ---------------------------------------------------------
        "editor.background": bg,
        "editor.foreground": ink,
        "editorCursor.foreground": pink,
        "editorCursor.background": bg,
        "editorMultiCursor.primary.foreground": pink,
        "editorMultiCursor.primary.background": bg,
        "editorMultiCursor.secondary.foreground": purple,
        "editorMultiCursor.secondary.background": bg,
        "editor.lineHighlightBackground": wash,
        "editor.lineHighlightBorder": CLEAR,
        "editor.rangeHighlightBackground": wash_strong,
        "editor.symbolHighlightBackground": wash_pink,
        "editorLineNumber.foreground": dimmest,
        "editorLineNumber.activeForeground": pink,
        "editorLineNumber.dimmedForeground": line,
        "editorGutter.background": bg,
        "editorGutter.addedBackground": add,
        "editorGutter.modifiedBackground": string,
        "editorGutter.deletedBackground": dele,
        "editorGutter.addedSecondaryBackground": a(add, 0.5),
        "editorGutter.modifiedSecondaryBackground": a(string, 0.5),
        "editorGutter.deletedSecondaryBackground": a(dele, 0.5),
        "editorGutter.foldingControlForeground": muted,
        "editorGutter.commentRangeForeground": dimmest,
        "editorGutter.commentGlyphForeground": muted,
        "editorGutter.commentUnresolvedGlyphForeground": purple,
        "editor.foldBackground": wash,
        "editor.foldPlaceholderForeground": muted,
        "editorRuler.foreground": line,
        "editorIndentGuide.background1": line,
        "editorIndentGuide.activeBackground1": edge,
        "editorWhitespace.foreground": a(dimmest, 0.6),
        "editorCodeLens.foreground": dimmest,
        "editorLink.activeForeground": pink,
        "editorInlayHint.background": wash_strong,
        "editorInlayHint.foreground": muted,
        "editorInlayHint.typeForeground": muted,
        "editorInlayHint.parameterForeground": muted,
        "editorGhostText.foreground": dimmest,
        "editorUnnecessaryCode.opacity": "#000000a0",
        "editorStickyScroll.background": bg,
        "editorStickyScroll.border": line,
        "editorStickyScroll.shadow": CLEAR,
        "editorStickyScrollHover.background": hover,
        "editorStickyScrollGutter.background": bg,

        # Selection is where you are; other occurrences are purple.
        "editor.selectionBackground": select,
        "editor.selectionForeground": ink,
        "editor.inactiveSelectionBackground": press,
        "editor.selectionHighlightBackground": press,
        "editor.selectionHighlightBorder": CLEAR,
        "editor.wordHighlightBackground": press,
        "editor.wordHighlightBorder": CLEAR,
        "editor.wordHighlightStrongBackground": a(purple, 0.25),
        "editor.wordHighlightStrongBorder": CLEAR,
        "editor.wordHighlightTextBackground": press,
        # Find: the current match is fuchsia, the rest purple.
        "editor.findMatchBackground": select,
        "editor.findMatchForeground": ink,
        "editor.findMatchBorder": pink,
        "editor.findMatchHighlightBackground": a(purple, 0.25),
        "editor.findMatchHighlightBorder": CLEAR,
        "editor.findRangeHighlightBackground": wash,
        "editor.findRangeHighlightBorder": CLEAR,
        "searchEditor.findMatchBackground": a(purple, 0.25),
        "searchEditor.textInputBorder": line,
        "search.resultsInfoForeground": muted,

        # Brackets: the matching pair is position; pair colors are all ink.
        "editorBracketMatch.background": wash_pink,
        "editorBracketMatch.border": pink,
        **{f"editorBracketHighlight.foreground{i}": ink for i in range(1, 7)},
        "editorBracketHighlight.unexpectedBracket.foreground": dele,
        **{f"editorBracketPairGuide.background{i}": CLEAR for i in range(1, 7)},
        **{f"editorBracketPairGuide.activeBackground{i}": edge for i in range(1, 7)},

        # Diagnostics.
        "editorError.foreground": dele,
        "editorError.background": CLEAR,
        "editorError.border": CLEAR,
        "editorWarning.foreground": string,
        "editorWarning.background": CLEAR,
        "editorWarning.border": CLEAR,
        "editorInfo.foreground": blue,
        "editorInfo.background": CLEAR,
        "editorInfo.border": CLEAR,
        "editorHint.foreground": muted,
        "editorHint.border": CLEAR,
        "problemsErrorIcon.foreground": dele,
        "problemsWarningIcon.foreground": string,
        "problemsInfoIcon.foreground": blue,
        "editorLightBulb.foreground": string,
        "editorLightBulbAutoFix.foreground": purple,
        "editorLightBulbAi.foreground": purple,

        # Overview ruler: the scrollbar's map of the file.
        "editorOverviewRuler.border": line,
        "editorOverviewRuler.background": bg,
        "editorOverviewRuler.findMatchForeground": a(purple, 0.8),
        "editorOverviewRuler.rangeHighlightForeground": a(purple, 0.4),
        "editorOverviewRuler.selectionHighlightForeground": a(purple, 0.6),
        "editorOverviewRuler.wordHighlightForeground": a(purple, 0.5),
        "editorOverviewRuler.wordHighlightStrongForeground": a(purple, 0.7),
        "editorOverviewRuler.wordHighlightTextForeground": a(purple, 0.5),
        "editorOverviewRuler.modifiedForeground": a(string, 0.7),
        "editorOverviewRuler.addedForeground": a(add, 0.7),
        "editorOverviewRuler.deletedForeground": a(dele, 0.7),
        "editorOverviewRuler.errorForeground": dele,
        "editorOverviewRuler.warningForeground": string,
        "editorOverviewRuler.infoForeground": blue,
        "editorOverviewRuler.bracketMatchForeground": pink,
        "editorOverviewRuler.inlineChatInserted": a(add, 0.6),
        "editorOverviewRuler.inlineChatRemoved": a(dele, 0.6),
        "editorOverviewRuler.currentContentForeground": a(add, 0.7),
        "editorOverviewRuler.incomingContentForeground": a(blue, 0.7),
        "editorOverviewRuler.commonContentForeground": a(muted, 0.7),

        # --- widgets: find, suggest, hover, peek ----------------------------
        "editorWidget.background": panel,
        "editorWidget.foreground": ink,
        "editorWidget.border": line,
        "editorWidget.resizeBorder": pink,
        "editorSuggestWidget.background": panel,
        "editorSuggestWidget.foreground": ink,
        "editorSuggestWidget.border": line,
        "editorSuggestWidget.selectedBackground": wash_pink,
        "editorSuggestWidget.selectedForeground": ink,
        "editorSuggestWidget.selectedIconForeground": pink,
        "editorSuggestWidget.highlightForeground": purple,
        "editorSuggestWidget.focusHighlightForeground": pink,
        "editorSuggestWidgetStatus.foreground": muted,
        "editorHoverWidget.background": panel,
        "editorHoverWidget.foreground": ink,
        "editorHoverWidget.border": line,
        "editorHoverWidget.highlightForeground": purple,
        "editorHoverWidget.statusBarBackground": panel,
        "editorMarkerNavigation.background": panel,
        "editorMarkerNavigationError.background": dele,
        "editorMarkerNavigationError.headerBackground": a(dele, 0.10),
        "editorMarkerNavigationWarning.background": string,
        "editorMarkerNavigationWarning.headerBackground": a(string, 0.10),
        "editorMarkerNavigationInfo.background": blue,
        "editorMarkerNavigationInfo.headerBackground": a(blue, 0.10),
        "debugExceptionWidget.background": panel,
        "debugExceptionWidget.border": dele,
        "peekView.border": edge,
        "peekViewTitle.background": panel,
        "peekViewTitleLabel.foreground": ink,
        "peekViewTitleDescription.foreground": muted,
        "peekViewEditor.background": bg,
        "peekViewEditorGutter.background": bg,
        "peekViewEditorStickyScroll.background": bg,
        "peekViewEditor.matchHighlightBackground": select,
        "peekViewEditor.matchHighlightBorder": CLEAR,
        "peekViewResult.background": panel,
        "peekViewResult.fileForeground": ink,
        "peekViewResult.lineForeground": muted,
        "peekViewResult.matchHighlightBackground": a(purple, 0.25),
        "peekViewResult.selectionBackground": wash_pink,
        "peekViewResult.selectionForeground": ink,

        # --- diff editor and merge conflicts --------------------------------
        "diffEditor.insertedLineBackground": add_bg,
        "diffEditor.removedLineBackground": del_bg,
        "diffEditor.insertedTextBackground": add_refine,
        "diffEditor.removedTextBackground": del_refine,
        "diffEditor.insertedTextBorder": CLEAR,
        "diffEditor.removedTextBorder": CLEAR,
        "diffEditor.border": line,
        "diffEditor.diagonalFill": line,
        "diffEditor.unchangedRegionBackground": panel,
        "diffEditor.unchangedRegionForeground": muted,
        "diffEditor.unchangedRegionShadow": CLEAR,
        "diffEditor.unchangedCodeBackground": CLEAR,
        "diffEditor.move.border": edge,
        "diffEditor.moveActive.border": pink,
        "diffEditorGutter.insertedLineBackground": a(p["add-tint"], p["diff"] * 2),
        "diffEditorGutter.removedLineBackground": a(p["del-tint"], p["diff"] * 2),
        "diffEditorOverview.insertedForeground": a(add, 0.7),
        "diffEditorOverview.removedForeground": a(dele, 0.7),
        "multiDiffEditor.headerBackground": panel,
        "multiDiffEditor.background": bg,
        "multiDiffEditor.border": line,
        # Merge: current is green, incoming the terminal's blue, their common
        # ancestor muted. Headers are the stronger tint.
        "merge.currentHeaderBackground": a(add, 0.30),
        "merge.currentContentBackground": a(add, 0.10),
        "merge.incomingHeaderBackground": a(blue, 0.30),
        "merge.incomingContentBackground": a(blue, 0.10),
        "merge.commonHeaderBackground": a(muted, 0.30),
        "merge.commonContentBackground": a(muted, 0.10),
        "merge.border": line,
        "mergeEditor.change.background": a(string, 0.12),
        "mergeEditor.change.word.background": a(string, 0.25),
        "mergeEditor.conflict.unhandledUnfocused.border": a(string, 0.6),
        "mergeEditor.conflict.unhandledFocused.border": string,
        "mergeEditor.conflict.handledUnfocused.border": edge,
        "mergeEditor.conflict.handledFocused.border": purple,
        "mergeEditor.conflict.handled.minimapOverViewRuler": purple,
        "mergeEditor.conflict.unhandled.minimapOverViewRuler": string,
        "mergeEditor.conflictingLines.background": a(string, 0.10),

        # --- minimap and scrollbars -----------------------------------------
        "minimap.background": bg,
        "minimap.foregroundOpacity": "#000000c0",
        "minimap.selectionHighlight": select,
        "minimap.selectionOccurrenceHighlight": press,
        "minimap.findMatchHighlight": a(purple, 0.6),
        "minimap.errorHighlight": dele,
        "minimap.warningHighlight": string,
        "minimap.infoHighlight": blue,
        "minimapSlider.background": wash_strong,
        "minimapSlider.hoverBackground": a(pink, 0.10),
        "minimapSlider.activeBackground": wash_pink,
        "minimapGutter.addedBackground": add,
        "minimapGutter.modifiedBackground": string,
        "minimapGutter.deletedBackground": dele,
        "scrollbar.shadow": CLEAR,
        "scrollbarSlider.background": a(muted, 0.25),
        "scrollbarSlider.hoverBackground": a(pink, 0.30),
        "scrollbarSlider.activeBackground": a(pink, 0.45),

        # --- lists and trees ------------------------------------------------
        # The focused row is where you are: a fuchsia wash with fuchsia text.
        # VS Code draws no left rail on list rows, so the wash is it.
        "list.activeSelectionBackground": wash_pink,
        "list.activeSelectionForeground": pink,
        "list.activeSelectionIconForeground": pink,
        "list.focusBackground": wash_pink,
        "list.focusForeground": pink,
        "list.focusOutline": CLEAR,
        "list.focusAndSelectionOutline": CLEAR,
        "list.inactiveSelectionBackground": press,
        "list.inactiveSelectionForeground": ink,
        "list.inactiveFocusBackground": CLEAR,
        "list.inactiveFocusOutline": CLEAR,
        "list.hoverBackground": hover,
        "list.hoverForeground": ink,
        "list.dropBackground": wash_pink,
        "list.dropBetweenBackground": pink,
        "list.highlightForeground": purple,
        "list.focusHighlightForeground": pink,
        "list.invalidItemForeground": dele,
        "list.errorForeground": dele,
        "list.warningForeground": string,
        "list.deemphasizedForeground": dimmest,
        "list.filterMatchBackground": a(purple, 0.25),
        "list.filterMatchBorder": CLEAR,
        "listFilterWidget.background": panel,
        "listFilterWidget.outline": pink,
        "listFilterWidget.noMatchesOutline": dele,
        "listFilterWidget.shadow": CLEAR,
        "tree.indentGuidesStroke": line,
        "tree.inactiveIndentGuidesStroke": a(line, 0.6),
        "tree.tableColumnsBorder": line,
        "tree.tableOddRowsBackground": wash,

        # --- quick input (command palette) ----------------------------------
        "quickInput.background": panel,
        "quickInput.foreground": ink,
        "quickInputTitle.background": panel,
        "quickInputList.focusBackground": wash_pink,
        "quickInputList.focusForeground": pink,
        "quickInputList.focusIconForeground": pink,
        "pickerGroup.foreground": purple,
        "pickerGroup.border": line,

        # --- inputs, dropdowns, buttons, badges -----------------------------
        # A text field is a slot: page-colored, line-edged; focused, the edge
        # is focusBorder's fuchsia.
        "input.background": bg,
        "input.foreground": ink,
        "input.border": line,
        "input.placeholderForeground": dimmest,
        "inputOption.activeBackground": wash_pink,
        "inputOption.activeForeground": pink,
        "inputOption.activeBorder": pink,
        "inputOption.hoverBackground": hover,
        "inputValidation.infoBackground": panel,
        "inputValidation.infoForeground": ink,
        "inputValidation.infoBorder": blue,
        "inputValidation.warningBackground": panel,
        "inputValidation.warningForeground": ink,
        "inputValidation.warningBorder": string,
        "inputValidation.errorBackground": panel,
        "inputValidation.errorForeground": ink,
        "inputValidation.errorBorder": dele,
        "dropdown.background": bg,
        "dropdown.foreground": ink,
        "dropdown.border": line,
        "dropdown.listBackground": panel,
        "checkbox.background": bg,
        "checkbox.foreground": pink,
        "checkbox.border": line,
        "checkbox.selectBackground": panel,
        "checkbox.selectBorder": pink,
        "radio.activeBackground": wash_pink,
        "radio.activeForeground": pink,
        "radio.activeBorder": pink,
        "radio.inactiveBackground": CLEAR,
        "radio.inactiveForeground": muted,
        "radio.inactiveBorder": line,
        "radio.inactiveHoverBackground": hover,
        # VS Code buttons are fills. The nearest to the desktop's outlined
        # suggested action: a purple wash, purple text, a purple border.
        "button.background": press,
        "button.foreground": purple,
        "button.border": purple,
        "button.hoverBackground": wash_pink,
        "button.separator": edge,
        "button.secondaryBackground": CLEAR,
        "button.secondaryForeground": ink,
        "button.secondaryHoverBackground": hover,
        "badge.background": purple,
        "badge.foreground": bg,
        "extensionBadge.remoteBackground": purple,
        "extensionBadge.remoteForeground": bg,
        "extensionButton.background": press,
        "extensionButton.foreground": purple,
        "extensionButton.hoverBackground": wash_pink,
        "extensionButton.separator": edge,
        "extensionButton.prominentBackground": press,
        "extensionButton.prominentForeground": purple,
        "extensionButton.prominentHoverBackground": wash_pink,
        "extensionIcon.starForeground": string,
        "extensionIcon.verifiedForeground": purple,
        "extensionIcon.preReleaseForeground": purple,
        "extensionIcon.sponsorForeground": pink,
        "keybindingLabel.background": wash_strong,
        "keybindingLabel.foreground": ink,
        "keybindingLabel.border": line,
        "keybindingLabel.bottomBorder": line,
        "settings.headerForeground": ink,
        "settings.modifiedItemIndicator": purple,
        "settings.focusedRowBackground": wash,
        "settings.focusedRowBorder": CLEAR,
        "settings.rowHoverBackground": hover,
        "settings.headerBorder": line,
        "settings.sashBorder": line,
        "settings.textInputBackground": bg,
        "settings.textInputBorder": line,
        "settings.numberInputBackground": bg,
        "settings.numberInputBorder": line,
        "settings.dropdownBackground": bg,
        "settings.dropdownBorder": line,
        "settings.checkboxBackground": bg,
        "settings.checkboxBorder": line,

        # --- notifications --------------------------------------------------
        "notifications.background": panel,
        "notifications.foreground": ink,
        "notifications.border": line,
        "notificationToast.border": line,
        "notificationCenter.border": line,
        "notificationCenterHeader.background": panel,
        "notificationCenterHeader.foreground": muted,
        "notificationLink.foreground": purple,
        "notificationsErrorIcon.foreground": dele,
        "notificationsWarningIcon.foreground": string,
        "notificationsInfoIcon.foreground": blue,
        "banner.background": panel,
        "banner.foreground": ink,
        "banner.iconForeground": purple,

        # --- terminal -------------------------------------------------------
        "terminal.background": panel,
        "terminal.foreground": tilix["foreground-color"],
        "terminal.border": line,
        "terminal.tab.activeBorder": pink,
        "terminalCursor.foreground": tilix["cursor-background-color"],
        "terminalCursor.background": tilix["cursor-foreground-color"],
        "terminal.selectionBackground": tilix["highlight-background-color"],
        "terminal.selectionForeground": tilix["highlight-foreground-color"],
        "terminal.inactiveSelectionBackground": press,
        "terminal.findMatchBackground": select,
        "terminal.findMatchBorder": pink,
        "terminal.findMatchHighlightBackground": a(purple, 0.25),
        "terminal.hoverHighlightBackground": hover,
        "terminal.dropBackground": wash_pink,
        "terminalCommandDecoration.defaultBackground": dimmest,
        "terminalCommandDecoration.successBackground": add,
        "terminalCommandDecoration.errorBackground": dele,
        "terminalOverviewRuler.cursorForeground": pink,
        "terminalOverviewRuler.findMatchForeground": a(purple, 0.8),
        "terminalStickyScroll.background": panel,
        "terminalStickyScrollHover.background": hover,
        "terminalSymbolIcon.aliasForeground": purple,
        "terminalSymbolIcon.flagForeground": purple,
        **{f"terminal.ansi{name.capitalize()}": ansi[i] for i, name in enumerate(ANSI)},
        **{f"terminal.ansiBright{name.capitalize()}": ansi[i + 8] for i, name in enumerate(ANSI)},

        # --- source control and git decorations -----------------------------
        "gitDecoration.addedResourceForeground": add,
        "gitDecoration.untrackedResourceForeground": add,
        "gitDecoration.modifiedResourceForeground": string,
        "gitDecoration.renamedResourceForeground": add,
        "gitDecoration.deletedResourceForeground": dele,
        "gitDecoration.conflictingResourceForeground": dele,
        "gitDecoration.stageModifiedResourceForeground": string,
        "gitDecoration.stageDeletedResourceForeground": dele,
        "gitDecoration.ignoredResourceForeground": dimmest,
        "gitDecoration.submoduleResourceForeground": muted,
        "scmGraph.historyItemHoverDefaultLabelForeground": bg,
        "scmGraph.historyItemHoverLabelForeground": bg,
        "scmGraph.historyItemRefColor": purple,
        "scmGraph.historyItemRemoteRefColor": blue,
        "scmGraph.historyItemBaseRefColor": string,
        "scmGraph.foreground1": purple,
        "scmGraph.foreground2": blue,
        "scmGraph.foreground3": string,
        "scmGraph.foreground4": add,
        "scmGraph.foreground5": ansi[6],

        # --- debugging and testing ------------------------------------------
        "debugToolBar.background": panel,
        "debugToolBar.border": line,
        "debugIcon.breakpointForeground": dele,
        "debugIcon.breakpointDisabledForeground": dimmest,
        "debugIcon.breakpointUnverifiedForeground": muted,
        "debugIcon.breakpointCurrentStackframeForeground": pink,
        "debugIcon.breakpointStackframeForeground": purple,
        "debugIcon.startForeground": add,
        "debugIcon.pauseForeground": purple,
        "debugIcon.stopForeground": dele,
        "debugIcon.disconnectForeground": dele,
        "debugIcon.restartForeground": add,
        "debugIcon.stepOverForeground": purple,
        "debugIcon.stepIntoForeground": purple,
        "debugIcon.stepOutForeground": purple,
        "debugIcon.continueForeground": purple,
        "debugIcon.stepBackForeground": purple,
        "editor.stackFrameHighlightBackground": a(string, 0.12),
        "editor.focusedStackFrameHighlightBackground": wash_pink,
        "debugTokenExpression.name": pink,
        "debugTokenExpression.value": muted,
        "debugTokenExpression.string": string,
        "debugTokenExpression.number": purple,
        "debugTokenExpression.boolean": purple,
        "debugTokenExpression.error": dele,
        "debugView.valueChangedHighlight": pink,
        "debugView.stateLabelBackground": wash_strong,
        "debugView.stateLabelForeground": muted,
        "debugView.exceptionLabelBackground": dele,
        "debugView.exceptionLabelForeground": bg,
        "debugConsole.infoForeground": blue,
        "debugConsole.warningForeground": string,
        "debugConsole.errorForeground": dele,
        "debugConsole.sourceForeground": muted,
        "debugConsoleInputIcon.foreground": pink,
        "testing.iconPassed": add,
        "testing.iconFailed": dele,
        "testing.iconErrored": dele,
        "testing.iconQueued": string,
        "testing.iconUnset": dimmest,
        "testing.iconSkipped": dimmest,
        "testing.runAction": add,
        "testing.peekBorder": dele,
        "testing.peekHeaderBackground": a(dele, 0.10),
        "testing.message.error.lineBackground": a(dele, 0.10),
        "testing.message.info.lineBackground": a(blue, 0.10),

        # --- the modern layout ----------------------------------------------
        # Newer VS Code draws the side bar, editor and panel as cards on a
        # shell, with pills for the active tab and activity-bar item and no
        # rails. The shell is the panel color, as the title and status bars
        # are; the cards keep their own colors and a line edge. The pills are
        # position: a fuchsia wash and fuchsia text. The active editor tab is
        # connected to the editor, so it stays the page, titled in fuchsia.
        "modernUI.shellBackground": panel,
        "modernUI.inactiveShellBackground": panel,
        "surface.background": panel,
        "surface.foreground": ink,
        "surface.border": line,
        "editor.border": line,
        "modernPanel.border": line,
        "modernActivityBar.background": panel,
        "modernActivityBar.inactiveBackground": panel,
        "modernActivityBar.border": line,
        "modernActivityBarItem.activeBackground": wash_pink,
        "modernActivityBarItem.activeForeground": pink,
        "modernActivityBarItem.hoverBackground": hover,
        "modernActivityBarItem.hoverForeground": ink,
        "modernTab.activeBackground": wash_pink,
        "modernTab.activeForeground": pink,
        "modernTab.hoverBackground": hover,
        "modernTab.hoverForeground": ink,
        "modernEditorTab.activeBackground": bg,
        "modernEditorTab.activeForeground": pink,
        "modernEditorTab.activeHoverBackground": bg,
        "modernEditorTab.inactiveBackground": CLEAR,
        "modernEditorTab.hoverBackground": hover,
        "modernEditorTab.hoverForeground": ink,
        "modernSash.gripForeground": dimmest,
        "window.activeBorder": line,
        "window.inactiveBorder": line,

        # --- the rest -------------------------------------------------------
        "editorBracketMatch.foreground": pink,
        "editor.placeholder.foreground": dimmest,
        "editor.linkedEditingBackground": wash_pink,
        "editor.hoverHighlightBackground": press,
        "editor.snippetTabstopHighlightBackground": wash_strong,
        "editor.snippetFinalTabstopHighlightBorder": edge,
        "editor.inlineValuesBackground": wash_strong,
        "editor.inlineValuesForeground": muted,
        "editorIndentGuide.background": line,
        "editorIndentGuide.activeBackground": edge,
        "editorUnicodeHighlight.border": string,
        "editorActionList.background": panel,
        "editorActionList.foreground": ink,
        "editorActionList.focusBackground": wash_pink,
        "editorActionList.focusForeground": ink,
        "quickInputList.focusHighlightForeground": pink,
        "activityErrorBadge.background": dele,
        "activityErrorBadge.foreground": bg,
        "activityWarningBadge.background": string,
        "activityWarningBadge.foreground": bg,
        "activityBarTop.background": panel,
        "panelTitleBadge.background": purple,
        "panelTitleBadge.foreground": bg,
        "profileBadge.background": purple,
        "profileBadge.foreground": bg,
        "sideBarTitle.background": panel,
        "panelStickyScroll.background": panel,
        "panelStickyScroll.border": line,
        "panelStickyScroll.shadow": CLEAR,
        "statusBar.inactiveBackground": panel,
        "commandCenter.debuggingBackground": press,
        "sideBySideEditor.horizontalBorder": line,
        "sideBySideEditor.verticalBorder": line,
        "button.secondaryBorder": line,
        "extensionButton.border": purple,
        "list.inactiveSelectionIconForeground": ink,
        "textPreformat.border": line,
        "markdownAlert.note.foreground": blue,
        "markdownAlert.tip.foreground": add,
        "markdownAlert.important.foreground": purple,
        "markdownAlert.warning.foreground": string,
        "markdownAlert.caution.foreground": dele,
        "welcomePage.background": bg,
        "welcomePage.tileBackground": panel,
        "welcomePage.tileHoverBackground": a(pink, 0.06),
        "welcomePage.tileBorder": line,
        "welcomePage.progress.background": line,
        "welcomePage.progress.foreground": pink,
        "walkThrough.embeddedEditorBackground": panel,
        "walkthrough.stepTitle.foreground": ink,
        "chat.requestBackground": wash,
        "chat.requestBorder": line,
        "chat.slashCommandBackground": press,
        "chat.slashCommandForeground": purple,
        "chat.avatarBackground": panel,
        "chat.avatarForeground": muted,
        "inlineChat.background": panel,
        "inlineChat.border": line,
        "inlineChat.shadow": CLEAR,
        "inlineChatInput.background": bg,
        "inlineChatInput.border": line,
        "inlineChatInput.focusBorder": pink,
        "inlineChatDiff.inserted": add_bg,
        "inlineChatDiff.removed": del_bg,
        "notebook.editorBackground": bg,
        "notebook.cellEditorBackground": wash,
        "notebook.cellBorderColor": line,
        "notebook.focusedCellBorder": pink,
        "notebook.inactiveFocusedCellBorder": edge,
        "notebook.selectedCellBackground": wash,
        "notebook.selectedCellBorder": line,
        "notebook.cellHoverBackground": a(pink, 0.04),
        "notebook.focusedEditorBorder": pink,
        "notebook.outputContainerBackgroundColor": panel,
        "notebook.cellToolbarSeparator": line,
        "notebook.symbolHighlightBackground": wash_pink,
        "notebookStatusSuccessIcon.foreground": add,
        "notebookStatusErrorIcon.foreground": dele,
        "notebookStatusRunningIcon.foreground": purple,
        "charts.foreground": ink,
        "charts.lines": line,
        "charts.red": dele,
        "charts.blue": blue,
        "charts.yellow": string,
        "charts.orange": string,
        "charts.green": add,
        "charts.purple": purple,
        "symbolIcon.classForeground": purple,
        "symbolIcon.constantForeground": purple,
        "symbolIcon.enumeratorForeground": purple,
        "symbolIcon.enumeratorMemberForeground": purple,
        "symbolIcon.interfaceForeground": purple,
        "symbolIcon.structForeground": purple,
        "symbolIcon.typeParameterForeground": purple,
        "symbolIcon.numberForeground": purple,
        "symbolIcon.booleanForeground": purple,
        "symbolIcon.stringForeground": string,
        "symbolIcon.keywordForeground": pink,
        "symbolIcon.functionForeground": ink,
        "symbolIcon.methodForeground": ink,
        "symbolIcon.constructorForeground": ink,
        "symbolIcon.variableForeground": ink,
        "symbolIcon.fieldForeground": ink,
        "symbolIcon.propertyForeground": ink,
        "symbolIcon.moduleForeground": muted,
        "symbolIcon.namespaceForeground": muted,
        "symbolIcon.packageForeground": muted,
        "symbolIcon.fileForeground": muted,
        "symbolIcon.folderForeground": muted,
        "symbolIcon.snippetForeground": muted,
        "symbolIcon.textForeground": muted,
        "symbolIcon.unitForeground": purple,
        "symbolIcon.colorForeground": purple,
        "symbolIcon.eventForeground": ink,
        "symbolIcon.keyForeground": purple,
        "symbolIcon.nullForeground": purple,
        "symbolIcon.objectForeground": ink,
        "symbolIcon.arrayForeground": ink,
        "symbolIcon.operatorForeground": ink,
        "symbolIcon.referenceForeground": ink,
    }
    return c


def token_colors(p):
    pink, purple, string = p["pink"], p["purple"], p["string"]
    ink, muted = p["ink"], p["muted"]

    def rule(name, scopes, fg=None, style=None):
        s = {}
        if fg:
            s["foreground"] = fg
        if style is not None:
            s["fontStyle"] = style
        return {"name": name, "scope": scopes, "settings": s}

    # Later rules win over earlier ones at equal specificity, and a longer
    # scope beats a shorter one, so the general folds come first and the
    # exceptions after.
    return [
        rule("Everything else", ["source", "text", "variable", "entity.name.function",
                                 "punctuation", "meta.embedded",
                                 "meta.template.expression"], ink),
        rule("Comments", ["comment", "punctuation.definition.comment"], muted, "italic"),
        rule("Doc comment tags", ["comment storage.type", "comment keyword",
                                  "comment entity.name.type", "comment variable",
                                  "comment punctuation.definition.block.tag",
                                  "comment punctuation.definition.tag"], purple, "italic"),
        rule("Keywords", ["keyword", "storage.type", "storage.modifier",
                          "keyword.control", "keyword.other"], pink),
        rule("Operators and punctuation", ["keyword.operator"], ink),
        rule("Word operators", ["keyword.operator.new", "keyword.operator.expression",
                                "keyword.operator.logical.python", "keyword.operator.word",
                                "keyword.operator.sizeof", "keyword.operator.alignof",
                                "keyword.operator.typeid", "keyword.operator.cast",
                                "keyword.operator.instanceof", "keyword.operator.delete",
                                "keyword.operator.and", "keyword.operator.or",
                                "keyword.operator.not", "keyword.operator.in",
                                "keyword.operator.is", "keyword.operator.of"], pink),
        rule("Decorators, macros, preprocessor", [
            "meta.decorator", "punctuation.decorator", "entity.name.function.decorator",
            "meta.function.decorator", "entity.name.function.macro",
            "support.function.macro", "entity.name.function.preprocessor",
            "meta.preprocessor", "punctuation.definition.directive",
            "meta.attribute.rust", "punctuation.definition.attribute"], pink),
        rule("Tags", ["entity.name.tag"], pink),
        rule("Numbers, constants, escapes", [
            "constant", "constant.numeric", "constant.language",
            "constant.character", "constant.character.escape", "constant.other",
            "support.constant", "keyword.other.unit",
            "constant.character.format.placeholder", "variable.language",
            "variable.parameter.function.language.special",
            "punctuation.definition.template-expression",
            "string.regexp constant.character", "constant.other.placeholder"], purple),
        rule("Types and builtins", [
            "entity.name.type", "entity.name.class", "entity.name.namespace",
            "entity.name.enum", "entity.name.interface", "entity.name.struct",
            "entity.other.inherited-class", "support.type", "support.class",
            "support.function", "storage.type.primitive", "storage.type.built-in",
            "storage.type.numeric", "storage.type.boolean", "storage.type.string",
            "storage.type.char", "storage.type.java", "entity.name.type.lifetime",
            "storage.modifier.lifetime", "support.variable",
            "support.type.primitive", "support.type.builtin"], purple),
        rule("Attributes and keys", [
            "entity.other.attribute-name", "support.type.property-name",
            "meta.object-literal.key", "entity.name.tag.yaml",
            "support.type.property-name.json", "support.type.property-name.css",
            "support.type.vendored.property-name"], purple),
        rule("Variables with a sigil", [
            "variable.other.php", "variable.other.normal.shell",
            "variable.other.special.shell", "variable.other.positional.shell",
            "variable.other.bracket.shell",
            "punctuation.definition.variable", "variable.other.readwrite.instance.ruby",
            "variable.other.global.perl", "variable.other.readwrite.global.perl",
            "variable.other.predefined.perl"], purple),
        rule("Strings", ["string", "punctuation.definition.string",
                         "string.quoted", "string.template", "string.unquoted",
                         "markup.inline.raw.string", "storage.type.string.python",
                         "string.regexp"], string),
        rule("Embedded code is code", ["string meta.embedded", "string meta.template.expression",
                                       "meta.fstring.python meta.embedded",
                                       "string.quoted.docstring punctuation"], ink),
        rule("Docstrings are comments", ["string.quoted.docstring",
                                         "string.quoted.docstring punctuation.definition.string",
                                         "comment.block.documentation"], muted, "italic"),
        rule("Invalid", ["invalid", "invalid.illegal"], p["del"], "underline"),
        rule("Deprecated", ["invalid.deprecated"], muted, "strikethrough"),

        # Markup: headings are ink and weight 400, as on the site.
        rule("Headings", ["markup.heading", "entity.name.section",
                          "markup.heading punctuation.definition.heading"], ink),
        rule("Heading marks", ["punctuation.definition.heading.markdown"], muted),
        rule("Emphasis", ["markup.italic"], None, "italic"),
        rule("Strong", ["markup.bold"], None, "bold"),
        rule("Strike", ["markup.strikethrough"], None, "strikethrough"),
        rule("Links", ["markup.underline.link", "string.other.link",
                       "meta.link.inline.markdown string.other.link.title"], purple),
        rule("Link punctuation", ["punctuation.definition.link", "punctuation.definition.metadata",
                                  "markup.underline.link.image"], muted),
        rule("Inline code", ["markup.inline.raw", "markup.fenced_code", "markup.raw"], ink),
        rule("Lists and quotes", ["punctuation.definition.list", "beginning.punctuation.definition.list",
                                  "markup.quote", "punctuation.definition.quote"], muted),
        rule("Fence language", ["fenced_code.block.language"], muted),

        # Diff: text colors; the row tint is the diff editor's.
        rule("Inserted", ["markup.inserted", "meta.diff.header.to-file",
                          "punctuation.definition.inserted"], p["add"]),
        rule("Deleted", ["markup.deleted", "meta.diff.header.from-file",
                         "punctuation.definition.deleted"], p["del"]),
        rule("Changed", ["markup.changed", "punctuation.definition.changed"], string),
        rule("Hunk header", ["meta.diff.range", "meta.diff.range punctuation"], purple),
        rule("Diff file", ["meta.diff.header", "meta.diff.index",
                           "meta.separator.diff"], muted),
        rule("Commit messages", ["meta.scope.message.git-commit"], ink),
    ]


def semantic_colors(p):
    pink, purple, string, ink, muted = p["pink"], p["purple"], p["string"], p["ink"], p["muted"]
    return {
        "keyword": pink,
        "modifier": pink,
        "decorator": pink,
        "macro": pink,
        "comment": {"foreground": muted, "italic": True},
        "string": string,
        "regexp": string,
        "number": purple,
        "enumMember": purple,
        "type": purple,
        "class": purple,
        "interface": purple,
        "enum": purple,
        "struct": purple,
        "typeParameter": purple,
        "typeAlias": purple,
        "builtinType": purple,
        "boolean": purple,
        "selfKeyword": purple,
        "lifetime": purple,
        # Builtins: global functions, objects and classes. Methods of builtin
        # types (.map, .slice) stay ink, as a scheme without types sees them.
        "function.defaultLibrary": purple,
        "variable.defaultLibrary": purple,
        "class.defaultLibrary": purple,
        "namespace.defaultLibrary": purple,
        "namespace": ink,
        "function": ink,
        "method": ink,
        "variable": ink,
        "variable.readonly": ink,
        "parameter": ink,
        "property": ink,
        "property.readonly": ink,
        "label": ink,
        "operator": ink,
        "event": ink,
        "*.deprecated": {"strikethrough": True},
    }


def theme(variant, p):
    return {
        "$schema": "vscode://schemas/color-theme",
        "name": f"Neon Doll {variant.capitalize()}",
        "type": variant,
        "semanticHighlighting": True,
        "colors": colors(variant, p),
        "tokenColors": token_colors(p),
        "semanticTokenColors": semantic_colors(p),
    }


def png(width, height, pixel):
    """A minimal RGB PNG; pixel(x, y) returns [r, g, b]."""
    raw = b"".join(b"\0" + bytes(v for x in range(width) for v in pixel(x, y))
                   for y in range(height))

    def chunk(kind, data):
        body = kind + data
        return struct.pack(">I", len(data)) + body + struct.pack(">I", zlib.crc32(body))

    return (b"\x89PNG\r\n\x1a\n"
            + chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0))
            + chunk(b"IDAT", zlib.compress(raw, 9))
            + chunk(b"IEND", b""))


def rgb(h):
    h = h.lstrip("#")
    return [int(h[i:i + 2], 16) for i in (0, 2, 4)]


def over(base, color, alpha):
    return [round(b + (c - b) * alpha) for b, c in zip(base, color)]


def icon():
    """128px: the prompt on graph paper, a purple chevron and a fuchsia block
    cursor, inside a 1px-per-4 line edge. Drawn at 4x and box-filtered, so
    the chevron's diagonals are smooth."""
    p = PALETTES["dark"]
    bg, line, purple, pink = rgb(p["bg"]), rgb(p["line"]), rgb(p["purple"]), rgb(p["pink"])
    grid = over(bg, purple, 0.09)
    s = 4
    size = 128 * s

    def chevron(x, y):
        # ">" from (28,40) to (60,64) to (28,88), stroke 12px, in 128 space.
        u, v = x / s, y / s
        t = 12 / 2
        for (x0, y0, x1, y1) in ((30, 38, 58, 64), (58, 64, 30, 90)):
            dx, dy = x1 - x0, y1 - y0
            k = max(0, min(1, ((u - x0) * dx + (v - y0) * dy) / (dx * dx + dy * dy)))
            px, py = x0 + k * dx, y0 + k * dy
            if (u - px) ** 2 + (v - py) ** 2 <= t * t:
                return True
        return False

    def hi(x, y):
        u, v = x / s, y / s
        if u < 4 or v < 4 or u >= 124 or v >= 124:
            return line
        if 70 <= u < 100 and 36 <= v < 92:
            return pink
        if chevron(x, y):
            return purple
        if int(u) % 16 == 0 or int(v) % 16 == 0:
            return grid
        return bg

    big = [[hi(x, y) for x in range(size)] for y in range(size)]

    def pixel(x, y):
        acc = [0, 0, 0]
        for j in range(s):
            row = big[y * s + j]
            for i in range(s):
                c = row[x * s + i]
                acc[0] += c[0]
                acc[1] += c[1]
                acc[2] += c[2]
        return [round(v / (s * s)) for v in acc]

    return png(128, 128, pixel)


def outputs():
    for variant, p in PALETTES.items():
        yield (OUT / "themes" / f"neon-doll-{variant}-color-theme.json",
               (json.dumps(theme(variant, p), indent=2) + "\n").encode())
    yield OUT / "icon.png", icon()


# --- .vsix -------------------------------------------------------------------
# A .vsix is a zip: extension.vsixmanifest and [Content_Types].xml at the top,
# the extension itself under extension/. This is what `vsce package` writes
# for an extension with no code.

VSIX_FILES = ["package.json", "README.md", "CHANGELOG.md", "icon.png",
              "themes/neon-doll-dark-color-theme.json",
              "themes/neon-doll-light-color-theme.json"]


def vsix_manifest(pkg):
    repo = pkg["repository"]["url"]
    home = repo.removesuffix(".git")
    props = {
        "Microsoft.VisualStudio.Code.Engine": pkg["engines"]["vscode"],
        "Microsoft.VisualStudio.Code.ExtensionDependencies": "",
        "Microsoft.VisualStudio.Code.ExtensionPack": "",
        "Microsoft.VisualStudio.Code.ExtensionKind": "ui,workspace",
        "Microsoft.VisualStudio.Code.LocalizedLanguages": "",
        "Microsoft.VisualStudio.Services.Links.Source": repo,
        "Microsoft.VisualStudio.Services.Links.Getstarted": repo,
        "Microsoft.VisualStudio.Services.Links.GitHub": repo,
        "Microsoft.VisualStudio.Services.Links.Support": home + "/issues",
        "Microsoft.VisualStudio.Services.Links.Learn": home + "#readme",
        "Microsoft.VisualStudio.Services.GitHubFlavoredMarkdown": "true",
        "Microsoft.VisualStudio.Services.Content.Pricing": "Free",
    }
    props_xml = "\n".join(
        f'      <Property Id="{k}" Value="{escape(v, {chr(34): "&quot;"})}" />'
        for k, v in props.items())
    assets = [
        ("Microsoft.VisualStudio.Code.Manifest", "extension/package.json"),
        ("Microsoft.VisualStudio.Services.Content.Details", "extension/README.md"),
        ("Microsoft.VisualStudio.Services.Content.Changelog", "extension/CHANGELOG.md"),
        ("Microsoft.VisualStudio.Services.Content.License", "extension/LICENSE.txt"),
        ("Microsoft.VisualStudio.Services.Icons.Default", "extension/icon.png"),
    ]
    assets_xml = "\n".join(
        f'    <Asset Type="{t}" Path="{path}" Addressable="true" />' for t, path in assets)
    return f"""<?xml version="1.0" encoding="utf-8"?>
<PackageManifest Version="2.0.0" xmlns="http://schemas.microsoft.com/developer/vsx-schema/2011" xmlns:d="http://schemas.microsoft.com/developer/vsx-schema-design/2011">
  <Metadata>
    <Identity Language="en-US" Id="{pkg["name"]}" Version="{pkg["version"]}" Publisher="{pkg["publisher"]}" />
    <DisplayName>{escape(pkg["displayName"])}</DisplayName>
    <Description xml:space="preserve">{escape(pkg["description"])}</Description>
    <Tags>{escape(",".join(pkg.get("keywords", []) + ["theme", "color-theme"]))}</Tags>
    <Categories>{escape(",".join(pkg["categories"]))}</Categories>
    <GalleryFlags>Public</GalleryFlags>
    <Properties>
{props_xml}
    </Properties>
    <License>extension/LICENSE.txt</License>
    <Icon>extension/icon.png</Icon>
  </Metadata>
  <Installation>
    <InstallationTarget Id="Microsoft.VisualStudio.Code" />
  </Installation>
  <Dependencies />
  <Assets>
{assets_xml}
  </Assets>
</PackageManifest>
"""


CONTENT_TYPES = """<?xml version="1.0" encoding="utf-8"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension=".json" ContentType="application/json" /><Default Extension=".md" ContentType="text/markdown" /><Default Extension=".png" ContentType="image/png" /><Default Extension=".txt" ContentType="text/plain" /><Default Extension=".vsixmanifest" ContentType="text/xml" /></Types>
"""


def vsix(out):
    pkg = json.loads((OUT / "package.json").read_text())
    entries = [("extension.vsixmanifest", vsix_manifest(pkg).encode()),
               ("[Content_Types].xml", CONTENT_TYPES.encode())]
    entries += [(f"extension/{f}", (OUT / f).read_bytes()) for f in VSIX_FILES]
    entries.append(("extension/LICENSE.txt", (ROOT / "COPYING").read_bytes()))
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        for name, data in entries:
            info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            z.writestr(info, data)
    print(out)


def main():
    args = sys.argv[1:]
    check = "--check" in args
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
        sys.exit("stale: " + ", ".join(map(str, stale)) + " (run tools/build-vscode.py)")
    if "--vsix" in args:
        i = args.index("--vsix")
        if i + 1 >= len(args):
            sys.exit("--vsix needs an output path")
        vsix(Path(args[i + 1]))


main()
