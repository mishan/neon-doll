# Install Neon Doll for Windows Terminal and PowerShell.
#
#   .\windows\install.ps1            install
#   .\windows\install.ps1 -Remove    take it out again
#
# Copies the color schemes into Windows Terminal's Fragments folder, where it
# picks them up without settings.json being touched, and the PowerShell colors
# next to your profile. Like install.sh it changes no settings: it prints the
# two lines that turn each part on.
#
# Run it from the shell you want colored: Windows PowerShell 5.1 and
# PowerShell 7 keep separate profiles.

param([switch]$Remove)
$ErrorActionPreference = 'Stop'

$here = Split-Path -Parent $MyInvocation.MyCommand.Path
$fragments = Join-Path $env:LOCALAPPDATA 'Microsoft\Windows Terminal\Fragments\Neon Doll'
$profileDir = Split-Path -Parent $PROFILE
$places = @(
    @{ From = Join-Path $here 'terminal\neon-doll.json';     To = Join-Path $fragments 'neon-doll.json' },
    @{ From = Join-Path $here 'powershell\neon-doll.ps1';    To = Join-Path $profileDir 'neon-doll.ps1' }
)

foreach ($p in $places) {
    if ($Remove) {
        if (Test-Path $p.To) { Remove-Item $p.To; "removed $($p.To)" }
        continue
    }
    New-Item -ItemType Directory -Force -Path (Split-Path -Parent $p.To) | Out-Null
    Copy-Item -Force $p.From $p.To
    $p.To
}
if ($Remove) {
    if ((Test-Path $fragments) -and -not (Get-ChildItem $fragments)) { Remove-Item $fragments }
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
"@
