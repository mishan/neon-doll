# Install Neon Doll on Windows.
#
#   .\windows\install.ps1                      ask which parts
#   .\windows\install.ps1 all                  every part there is here
#   .\windows\install.ps1 terminal powershell  just these
#   .\windows\install.ps1 -Remove              take it out again
#
# With no part named and a console to ask in, it lists the parts, the ones
# whose apps it finds already ticked, and asks. The parts:
#
#   terminal    Windows Terminal's color schemes, into its Fragments folder,
#               where it picks them up without settings.json being touched
#   powershell  the PowerShell colors, next to your profile
#   contrast    the desktop's contrast themes, into your Themes folder
#   vscode      the VS Code extension, into VS Code's extensions folder
#   firefox     userChrome.css, into Firefox profiles
#   git         the git colors
#   vim         the vim color scheme, into vimfiles
#
# Parts whose files aren't in this copy aren't offered. Files of your own in
# the way are moved aside, and -Remove takes out only copies that still
# match. Like install.sh it changes no settings: it
# prints what turns each part on.
#
# Run it from the shell you want colored: Windows PowerShell 5.1 and
# PowerShell 7 keep separate profiles.

param(
    [switch]$Remove,
    [Parameter(Position = 0, ValueFromRemainingArguments = $true)]
    [string[]]$Parts
)
$ErrorActionPreference = 'Stop'

function P { [IO.Path]::Combine([string[]]$args) }

$here = Split-Path -Parent $MyInvocation.MyCommand.Path
$root = Split-Path -Parent $here
# Your home folder; USERPROFILE on Windows, where $HOME ignores it.
$userHome = if ($env:USERPROFILE) { $env:USERPROFILE } else { $HOME }
$fragments = P $env:LOCALAPPDATA 'Microsoft' 'Windows Terminal' 'Fragments' 'Neon Doll'
# Empty when Windows PowerShell can't find your Documents folder.
$profileDir = if ($PROFILE) { Split-Path -Parent $PROFILE }
$themes = P $env:LOCALAPPDATA 'Microsoft' 'Windows' 'Themes' 'Neon Doll'
$allParts = 'terminal', 'powershell', 'contrast', 'vscode', 'firefox', 'git', 'vim'

function Have($name) { [bool](Get-Command $name -ErrorAction SilentlyContinue) }

# The extensions folders of VS Code and the editors built from it.
function VSCodeDirs {
    foreach ($e in @{ Cli = 'code'; Dir = '.vscode' }, @{ Cli = 'codium'; Dir = '.vscode-oss' },
                   @{ Cli = 'cursor'; Dir = '.cursor' }, @{ Cli = 'windsurf'; Dir = '.windsurf' }) {
        if ((Test-Path (P $userHome $e.Dir)) -or (Have $e.Cli)) { P $userHome $e.Dir 'extensions' }
    }
}

# Firefox's profiles, with which ones are defaults.
function FirefoxProfiles {
    $base = P $env:APPDATA 'Mozilla' 'Firefox'
    $ini = P $base 'profiles.ini'
    if (-not (Test-Path $ini)) { return }
    $sections = [ordered]@{}
    $defaults = @{}
    $section = $null
    foreach ($line in Get-Content $ini) {
        if ($line -match '^\[(.*)\]$') { $section = $Matches[1]; $sections[$section] = @{}; continue }
        if ($section -and $line -match '^([^=]+)=(.*)$') {
            $sections[$section][$Matches[1]] = $Matches[2]
            if ($section -like 'Install*' -and $Matches[1] -eq 'Default') { $defaults[$Matches[2]] = $true }
        }
    }
    foreach ($s in $sections.Keys) {
        $p = $sections[$s]
        if ($s -notlike 'Profile*' -or -not $p.Path) { continue }
        $dir = if ($p.IsRelative -eq '0') { $p.Path } else { P $base ($p.Path -replace '/', [IO.Path]::DirectorySeparatorChar) }
        if (-not (Test-Path $dir)) { continue }
        [pscustomobject]@{
            Dir     = $dir
            Name    = if ($p.Name) { $p.Name } else { $p.Path }
            Default = [bool]($defaults[$p.Path] -or $p.Default -eq '1')
        }
    }
}

# Whether this copy has the files the part installs.
function Fits($part) {
    switch ($part) {
        'vscode'  { Test-Path (P $root 'vscode' 'package.json') }
        'firefox' { Test-Path (P $root 'firefox' 'userChrome.css') }
        'git'     { Test-Path (P $root 'git' 'neon-doll.gitconfig') }
        'vim'     { Test-Path (P $root 'vim' 'colors' 'neon-doll.vim') }
        default   { $true }
    }
}

# Whether the app the part themes seems to be here.
function Found($part) {
    switch ($part) {
        'terminal' {
            (Have 'wt') -or
            (Test-Path (P $env:LOCALAPPDATA 'Packages' 'Microsoft.WindowsTerminal*')) -or
            (Test-Path (P $env:LOCALAPPDATA 'Microsoft' 'Windows Terminal'))
        }
        'powershell' { $true }
        'contrast'   { $true }
        'vscode'     { [bool](VSCodeDirs) }
        'firefox'    { [bool](FirefoxProfiles) }
        'git'        { Have 'git' }
        'vim'        { (Have 'vim') -or (Have 'gvim') -or (Test-Path (P $env:ProgramFiles 'Vim')) }
    }
}

function Label($part) {
    switch ($part) {
        'terminal'   { 'Windows Terminal color schemes' }
        'powershell' { "PowerShell $($PSVersionTable.PSVersion.Major) colors (this shell)" }
        'contrast'   { 'Windows desktop, as a contrast theme' }
        'vscode'     { 'VS Code, VSCodium, Cursor' }
        'firefox'    { "Firefox's userChrome.css (shapes)" }
        'git'        { 'git colors' }
        'vim'        { 'vim' }
    }
}

# Checklist: items are objects with Tag, Label and On. Returns the tags
# picked, or $null if cancelled.
function Checklist($title, $text, $items, [switch]$NoTags) {
    Write-Host ''
    Write-Host $title -ForegroundColor Magenta
    Write-Host $text
    while ($true) {
        Write-Host ''
        for ($i = 0; $i -lt $items.Count; $i++) {
            $it = $items[$i]
            $box = if ($it.On) { '[x]' } else { '[ ]' }
            $line = if ($NoTags) { $it.Label } else { '{0,-11} {1}' -f $it.Tag, $it.Label }
            Write-Host ('  {0,2}  ' -f ($i + 1)) -NoNewline
            Write-Host $box -NoNewline -ForegroundColor $(if ($it.On) { 'Magenta' } else { 'DarkGray' })
            Write-Host " $line"
        }
        Write-Host ''
        $reply = Read-Host 'Numbers to tick or untick, a for all, n for none, Enter to go on, q to quit'
        if ($null -eq $reply) { return $null }
        $reply = $reply.Trim()
        if ($reply -eq '') { break }
        if ($reply -eq 'q') { return $null }
        foreach ($r in $reply -split '[\s,]+') {
            if ($r -eq 'a') { $items | ForEach-Object { $_.On = $true } }
            elseif ($r -eq 'n') { $items | ForEach-Object { $_.On = $false } }
            elseif ($r -match '^\d+$' -and [int]$r -ge 1 -and [int]$r -le $items.Count) {
                $items[[int]$r - 1].On = -not $items[[int]$r - 1].On
            }
        }
    }
    , @($items | Where-Object On | ForEach-Object Tag)
}

# Same: whether two files, or two folders file for file, match.
function Same($a, $b) {
    if (-not (Test-Path $b)) { return $false }
    if ((Test-Path $a -PathType Leaf) -ne (Test-Path $b -PathType Leaf)) { return $false }
    $hash = {
        param($d)
        Get-ChildItem -Recurse -File $d | Sort-Object FullName | ForEach-Object {
            $_.FullName.Substring($d.Length) + ' ' + (Get-FileHash $_.FullName).Hash
        }
    }
    if (Test-Path $a -PathType Leaf) { return (Get-FileHash $a).Hash -eq (Get-FileHash $b).Hash }
    ((& $hash (Resolve-Path $a).Path) -join "`n") -eq ((& $hash (Resolve-Path $b).Path) -join "`n")
}

# Place: copy, or with -Remove take out, one file or folder.
function Place($from, $to) {
    if ($Remove) {
        if (Same $from $to) { Remove-Item -Recurse -Force $to; "removed $to" }
        elseif (Test-Path $to) { "left $to alone: it differs from this copy" }
        return
    }
    New-Item -ItemType Directory -Force -Path (Split-Path -Parent $to) | Out-Null
    # A file of your own is moved aside, never overwritten.
    if ((Test-Path $to) -and -not (Same $from $to)) {
        Move-Item $to "$to.bak.$(Get-Date -Format yyyyMMddHHmmss)"
        "moved existing $to aside"
    }
    if (Test-Path $to) { Remove-Item -Recurse -Force $to }
    Copy-Item -Recurse -Force $from $to
    # A clone from a downloaded zip carries the web mark, and Windows
    # refuses to apply a .theme file that has it.
    if ($PSVersionTable.PSEdition -eq 'Desktop' -or $IsWindows) { Get-ChildItem -Recurse -File $to | Unblock-File }
    $to
}

# Which parts.
$firefoxDirs = $null
$interactive = [Environment]::UserInteractive -and
    -not [Console]::IsInputRedirected -and -not [Console]::IsOutputRedirected
if ($Parts) {
    $wanted = $Parts | ForEach-Object { $_ -split ',' } | Where-Object { $_ }
    foreach ($w in $wanted) {
        if ($w -ne 'all' -and $allParts -notcontains $w) {
            throw "unknown part: $w (the parts: all, $($allParts -join ', '))"
        }
    }
    $every = $wanted -contains 'all'
    $picked = $allParts | Where-Object { $every -or $wanted -contains $_ }
    foreach ($p in $picked) {
        if (-not $every -and -not (Fits $p)) { Write-Warning "skipped ${p}: its files are not in this copy" }
    }
    $picked = @($picked | Where-Object { Fits $_ })
} elseif ($Remove -or -not $interactive) {
    $picked = @($allParts | Where-Object { Fits $_ })
} else {
    $items = @(foreach ($p in $allParts) {
        if (-not (Fits $p)) { continue }
        $on = [bool](Found $p)
        [pscustomobject]@{ Tag = $p; Label = (Label $p) + $(if ($on) { '' } else { ' (not found)' }); On = $on }
    })
    $picked = Checklist 'Neon Doll' 'Install which parts? The apps found on this system are ticked.' $items
    if ($null -eq $picked -or $picked.Count -eq 0) { 'Nothing installed.'; return }

    # More than one Firefox profile: which ones.
    $profiles = @(FirefoxProfiles)
    if ($picked -contains 'firefox' -and $profiles.Count -gt 1) {
        $items = @(for ($i = 0; $i -lt $profiles.Count; $i++) {
            $p = $profiles[$i]
            [pscustomobject]@{ Tag = $i; Label = $p.Name + $(if ($p.Default) { ' (default)' } else { '' }); On = $p.Default }
        })
        $chosen = Checklist 'Firefox' 'Put userChrome.css in which profiles?' $items -NoTags
        $firefoxDirs = @(foreach ($c in $chosen) { $profiles[$c].Dir })
        if (-not $firefoxDirs) { $picked = @($picked | Where-Object { $_ -ne 'firefox' }) }
    }
}

# Installing.
$hints = [Collections.Generic.List[string]]::new()
foreach ($part in $picked) {
    switch ($part) {
        'terminal' {
            Place (P $here 'terminal' 'neon-doll.json') (P $fragments 'neon-doll.json')
            if ($Remove -and (Test-Path $fragments) -and -not (Get-ChildItem $fragments)) { Remove-Item $fragments }
            $hints.Add(@"
  Windows Terminal: Settings -> your profile -> Appearance -> Color scheme -> Neon Doll Dark (or Light).
    For the tab row too, paste the two entries from $(P $here 'terminal' 'themes.json') into the
    "themes" list of settings.json, then Settings -> Appearance -> Theme -> Neon Doll Dark.
"@)
        }
        'powershell' {
            if (-not $profileDir) {
                if (-not $Remove) { Write-Warning "skipped powershell: this PowerShell doesn't know where your profile goes" }
                break
            }
            $ps1 = P $profileDir 'neon-doll.ps1'
            Place (P $here 'powershell' 'neon-doll.ps1') $ps1
            $hints.Add(@"
  PowerShell: add to $PROFILE
    . "$ps1"
    Enable-NeonDollPrompt        # optional; -Variant Light for the light scheme
"@)
        }
        'contrast' {
            foreach ($v in 'dark', 'light') {
                Place (P $here 'contrast' "neon-doll-$v.theme") (P $themes "neon-doll-$v.theme")
            }
            if ($Remove -and (Test-Path $themes) -and -not (Get-ChildItem $themes)) { Remove-Item $themes }
            $hints.Add(@"
  The whole desktop, as a contrast theme: open it, and Windows applies it
    Start-Process "$(P $themes 'neon-doll-dark.theme')"
    To go back: Settings -> Accessibility -> Contrast themes -> None.
"@)
        }
        'vscode' {
            # The extension folder as it is: VS Code picks up an unpacked
            # extension in its extensions folder on the next start.
            $version = (Get-Content -Raw (P $root 'vscode' 'package.json') | ConvertFrom-Json).version
            $dirs = @(VSCodeDirs)
            if (-not $dirs) { $dirs = @(P $userHome '.vscode' 'extensions') }
            foreach ($d in $dirs) {
                $to = P $d "mishan.neon-doll-$version"
                Place (P $root 'vscode') $to
                # Taking the folder out leaves VS Code's list of extensions
                # naming it; its own uninstall clears that.
                $list = P $d 'extensions.json'
                if ($Remove -and -not (Test-Path $to) -and (Test-Path $list) -and
                    (Select-String -Quiet -SimpleMatch '"mishan.neon-doll"' $list)) {
                    $cli = 'code', 'codium', 'cursor', 'windsurf' | Where-Object { Have $_ } | Select-Object -First 1
                    if ($cli) { & $cli --extensions-dir $d --uninstall-extension mishan.neon-doll *> $null }
                }
            }
            $hints.Add('  VS Code: restart it, then Preferences: Color Theme -> Neon Doll Dark (or Light).')
        }
        'firefox' {
            $profiles = @(FirefoxProfiles)
            $dirs = if ($Remove) { $profiles.Dir }
                    elseif ($null -ne $firefoxDirs) { $firefoxDirs }
                    elseif ($profiles | Where-Object Default) { ($profiles | Where-Object Default).Dir }
                    else { $profiles.Dir }
            if (-not $dirs) {
                if (-not $Remove) { Write-Warning 'skipped firefox: no Firefox profile found; start Firefox once first' }
                break
            }
            $unset = @()
            foreach ($d in $dirs) {
                Place (P $root 'firefox' 'userChrome.css') (P $d 'chrome' 'userChrome.css')
                $prefs = @((P $d 'prefs.js'), (P $d 'user.js')) | Where-Object { Test-Path $_ }
                if (-not ($prefs -and (Select-String -Quiet 'toolkit.legacyUserProfileCustomizations.stylesheets", *true' $prefs))) {
                    $unset += Split-Path -Leaf $d
                }
            }
            if ($unset) {
                $hints.Add("  Firefox: set toolkit.legacyUserProfileCustomizations.stylesheets to true in about:config (profiles $($unset -join ', ')), then restart Firefox.")
            } else {
                $hints.Add('  Firefox: restart it. The color theme itself loads from about:debugging; see the README.')
            }
        }
        'git' {
            $gitconfig = P $userHome '.config' 'neon-doll' 'gitconfig'
            Place (P $root 'git' 'neon-doll.gitconfig') $gitconfig
            $hints.Add("  git: git config --global include.path `"$($gitconfig -replace '\\', '/')`"   # after any [color] sections of your own")
        }
        'vim' {
            Place (P $root 'vim' 'colors' 'neon-doll.vim') (P $userHome 'vimfiles' 'colors' 'neon-doll.vim')
            $hints.Add('  vim: add to ~\_vimrc:  colorscheme neon-doll   (set background=light for the light variant; set termguicolors for exact colors)')
        }
    }
}

if (-not $Remove -and $hints.Count) {
    ''
    'To turn it on:'
    $hints
}
