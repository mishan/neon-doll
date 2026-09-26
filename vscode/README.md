# Neon Doll for VS Code

**Hot pink neon on midnight plum.**

One fuchsia light marks exactly where you are: the cursor, the current line
number, the matching bracket, the selection, the current tab and the focused
row. Purple marks what you can touch: links, badges, buttons. The rest stays
in the dark. Dark and light, part of [Neon Doll](https://github.com/mishan/neon-doll),
a desktop theme for GNOME and the tools around it.

![Neon Doll Dark](https://raw.githubusercontent.com/mishan/neon-doll/main/screenshots/vscode-dark.png)

![Neon Doll Light](https://raw.githubusercontent.com/mishan/neon-doll/main/screenshots/vscode-light.png)

## Syntax

Four colors and no more: keywords fuchsia; numbers, constants, types and
builtins purple; strings yellow; comments muted and italic; everything else
ink. Bracket pairs stay ink, so only the matching one lights up. Diffs are
green and red on a tinted row, and the terminal takes the Neon Doll terminal
colors, which leave fuchsia out: it's the cursor.

## Light and dark

To follow the system's light or dark mode, add to your settings:

```json
"window.autoDetectColorScheme": true,
"workbench.preferredDarkColorTheme": "Neon Doll Dark",
"workbench.preferredLightColorTheme": "Neon Doll Light"
```

## Known limits

- VS Code buttons are fills, so the primary button is a purple wash with a
  purple edge rather than the desktop's bare outline, and hover can change
  its fill but not its text.
- List rows can't carry the desktop's rail; the focused row is a fuchsia wash
  with fuchsia text instead. Newer VS Code's rounded-card layout marks the
  active tab and activity-bar item with a pill rather than a rail, so there
  the pill is fuchsia.
- The chat and agent views keep VS Code's colors.
- Corners, fonts and weights are VS Code's own. A theme sets colors only.

## License

GPL-3.0-or-later.
