# Install Neon Doll for Windows Terminal, PowerShell and the desktop.
#
#   .\windows\install.ps1            install
#   .\windows\install.ps1 -Remove    take it out again
#
# Copies the color schemes into Windows Terminal's Fragments folder, where it
# picks them up without settings.json being touched, and the PowerShell colors
# next to your profile, and the contrast themes into your Themes folder. Like
# install.sh it changes no settings: it prints what turns each part on.
#
# Run it from the shell you want colored: Windows PowerShell 5.1 and
# PowerShell 7 keep separate profiles.

param([switch]$Remove)
$ErrorActionPreference = 'Stop'

$here = Split-Path -Parent $MyInvocation.MyCommand.Path
$fragments = Join-Path $env:LOCALAPPDATA 'Microsoft\Windows Terminal\Fragments\Neon Doll'
$profileDir = Split-Path -Parent $PROFILE
$themes = Join-Path $env:LOCALAPPDATA 'Microsoft\Windows\Themes\Neon Doll'
$places = @(
    @{ From = Join-Path $here 'terminal\neon-doll.json';     To = Join-Path $fragments 'neon-doll.json' },
    @{ From = Join-Path $here 'powershell\neon-doll.ps1';    To = Join-Path $profileDir 'neon-doll.ps1' },
    @{ From = Join-Path $here 'contrast\neon-doll-dark.theme';  To = Join-Path $themes 'neon-doll-dark.theme' },
    @{ From = Join-Path $here 'contrast\neon-doll-light.theme'; To = Join-Path $themes 'neon-doll-light.theme' }
)

foreach ($p in $places) {
    if ($Remove) {
        if (Test-Path $p.To) { Remove-Item $p.To; "removed $($p.To)" }
        continue
    }
    New-Item -ItemType Directory -Force -Path (Split-Path -Parent $p.To) | Out-Null
    Copy-Item -Force $p.From $p.To
    # A clone from a downloaded zip carries the web mark, and Windows
    # refuses to apply a .theme file that has it.
    Unblock-File $p.To
    $p.To
}
if ($Remove) {
    foreach ($d in $fragments, $themes) {
        if ((Test-Path $d) -and -not (Get-ChildItem $d)) { Remove-Item $d }
    }
    return
}

$ps1 = Join-Path $profileDir 'neon-doll.ps1'
@"

To turn it on:
  Windows Terminal: Settings -> your profile -> Appearance -> Color scheme -> Neon Doll Dark (or Light).
    For the tab row too, paste the two entries from windows\terminal\themes.json into the
    "themes" list of settings.json, then Settings -> Appearance -> Theme -> Neon Doll Dark.
  PowerShell: add to $PROFILE
    . "$ps1"
    Enable-NeonDollPrompt        # optional; -Variant Light for the light scheme
  The whole desktop, as a contrast theme: open it, and Windows applies it
    Start-Process "$(Join-Path $themes 'neon-doll-dark.theme')"
    To go back: Settings -> Accessibility -> Contrast themes -> None.
"@
