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
#   accent      no files: the Settings steps to dark mode and the fuchsia accent
#   cursors     the mouse pointers, as a pointer scheme to pick (not ticked)
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
$pointers = P $env:LOCALAPPDATA 'Neon Doll' 'Cursors'
$allParts = 'terminal', 'powershell', 'accent', 'cursors', 'vscode', 'firefox', 'git', 'vim'
# Offered but not ticked: wanted by fewer people than the rest.
$optIn = 'cursors'
$onWindows = $PSVersionTable.PSEdition -eq 'Desktop' -or $IsWindows

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
        'accent'     { $true }
        'cursors'    { $true }
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
        'accent'     { 'Windows dark mode and fuchsia accent (shows the steps)' }
        'cursors'    { 'Mouse pointers' }
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
    # A clone from a downloaded zip carries the web mark, and PowerShell
    # under RemoteSigned won't load neon-doll.ps1 from your profile with it.
    if ($onWindows) { Get-ChildItem -Recurse -File $to | Unblock-File }
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
        $found = [bool](Found $p)
        [pscustomobject]@{ Tag = $p; Label = (Label $p) + $(if ($found) { '' } else { ' (not found)' }); On = $found -and $optIn -notcontains $p }
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

# Whether PowerShell will skip your profile: Windows PowerShell's default,
# Restricted, runs no scripts, and AllSigned runs no unsigned ones. This
# window's own policy, the Process scope, is left out.
function ScriptsOff {
    if (-not $onWindows) { return $false }
    $set = Get-ExecutionPolicy -List | Where-Object { $_.Scope -ne 'Process' -and "$($_.ExecutionPolicy)" -ne 'Undefined' } |
        Select-Object -First 1
    $policy = if ($set) { "$($set.ExecutionPolicy)" } else { 'Restricted' }
    $policy -eq 'Restricted' -or $policy -eq 'AllSigned'
}

# Installing. Each part leaves a hint: its name, then lines, where one
# starting "> " is something to copy (a command, a path).
$hints = [Collections.Generic.List[object]]::new()
function Hint($name) { $hints.Add([pscustomobject]@{ Name = $name; Lines = $args }) }
foreach ($part in $picked) {
    switch ($part) {
        'terminal' {
            Place (P $here 'terminal' 'neon-doll.json') (P $fragments 'neon-doll.json')
            if ($Remove -and (Test-Path $fragments) -and -not (Get-ChildItem $fragments)) { Remove-Item $fragments }
            Hint 'Windows Terminal' 'Close every Terminal window, so it reads the new schemes when it starts again. Then' `
                'Settings -> your profile -> Appearance -> Color scheme -> Neon Doll Dark (or Light).' `
                'For the tab row too, paste the two entries in this file into the "themes" list of settings.json:' `
                "> $(P $here 'terminal' 'themes.json')" `
                'then Settings -> Appearance -> Theme -> Neon Doll Dark.'
        }
        'powershell' {
            if (-not $profileDir) {
                if (-not $Remove) { Write-Warning "skipped powershell: this PowerShell doesn't know where your profile goes" }
                break
            }
            $ps1 = P $profileDir 'neon-doll.ps1'
            Place (P $here 'powershell' 'neon-doll.ps1') $ps1
            $line = ". `"$ps1`"" -replace "'", "''"
            $lines = @('Add it to your profile:', "> Add-Content `$PROFILE '$line'",
                       "For the bash prompt's look too (-Variant Light for the light scheme):",
                       "> Add-Content `$PROFILE 'Enable-NeonDollPrompt'")
            if (ScriptsOff) {
                $lines += 'Windows runs no scripts for you yet, so PowerShell skips your profile. To let it:',
                          '> Set-ExecutionPolicy -Scope CurrentUser RemoteSigned'
            }
            Hint "PowerShell $($PSVersionTable.PSVersion.Major)" @lines
        }
        'accent' {
            Hint 'Dark mode and the fuchsia accent' 'Settings -> Personalization -> Colors:' `
                'Choose your mode -> Dark' `
                'Accent color -> Manual, then Custom colors -> View colors -> More, and type in' `
                '> FF2D95' `
                'Show accent color on Start and taskbar -> On' `
                'Show accent color on title bars and window borders -> On'
        }
        'cursors' {
            # Added to Windows' list of pointer schemes, for you to pick.
            $cursorsKey = 'HKCU:\Control Panel\Cursors'
            $inUse = $onWindows -and (Get-ItemProperty $cursorsKey).'(default)' -eq 'Neon Doll'
            if ($Remove -and $inUse) {
                Write-Warning "left the pointers alone: they're in use; pick another pointer scheme first"
                break
            }
            Place (P $here 'cursors') $pointers
            if ($Remove -and (Test-Path (Split-Path $pointers)) -and -not (Get-ChildItem (Split-Path $pointers))) { Remove-Item (Split-Path $pointers) }
            if ($onWindows -and $Remove) { Remove-ItemProperty "$cursorsKey\Schemes" 'Neon Doll' -ErrorAction SilentlyContinue }
            elseif ($onWindows) {
                # Windows' pointer roles, in the order a scheme lists them; a
                # role with no file here keeps Windows' own.
                $roles = 'Arrow', 'Help', 'AppStarting', 'Wait', 'Crosshair', 'IBeam', 'NWPen', 'No', 'SizeNS',
                         'SizeWE', 'SizeNWSE', 'SizeNESW', 'SizeAll', 'UpArrow', 'Hand', 'Pin', 'Person'
                $files = foreach ($r in $roles) { $f = P $pointers "$r.cur"; if (Test-Path $f) { $f } else { '' } }
                if (-not (Test-Path "$cursorsKey\Schemes")) { New-Item "$cursorsKey\Schemes" | Out-Null }
                New-ItemProperty "$cursorsKey\Schemes" 'Neon Doll' -Value ($files -join ',') -PropertyType ExpandString -Force | Out-Null
            }
            Hint 'Mouse pointers' 'Settings -> Bluetooth & devices -> Mouse -> Additional mouse settings -> Pointers:' `
                'Scheme -> Neon Doll, then OK.'
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
            Hint 'VS Code' 'Restart it, then Preferences: Color Theme -> Neon Doll Dark (or Light).'
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
                Hint 'Firefox' "In about:config, set this to true (profiles $($unset -join ', ')), then restart Firefox:" `
                    '> toolkit.legacyUserProfileCustomizations.stylesheets'
            } else {
                Hint 'Firefox' 'Restart it. The color theme itself loads from about:debugging; see docs/install.md.'
            }
        }
        'git' {
            $gitconfig = P $userHome '.config' 'neon-doll' 'gitconfig'
            Place (P $root 'git' 'neon-doll.gitconfig') $gitconfig
            Hint 'git' 'Run this; it goes after any [color] settings of your own, so its colors win:' `
                "> git config --global include.path `"$($gitconfig -replace '\\', '/')`""
        }
        'vim' {
            Place (P $root 'vim' 'colors' 'neon-doll.vim') (P $userHome 'vimfiles' 'colors' 'neon-doll.vim')
            Hint 'vim' 'Add to ~\_vimrc (with set background=light for the light variant, set termguicolors for exact colors):' `
                '> colorscheme neon-doll'
        }
    }
}

if (-not $Remove -and $hints.Count) {
    Write-Host ''
    Write-Host 'To turn it on:' -ForegroundColor Magenta
    foreach ($h in $hints) {
        Write-Host ''
        Write-Host "  $($h.Name)" -ForegroundColor Magenta
        foreach ($l in $h.Lines) {
            if ($l.StartsWith('> ')) { Write-Host "      $($l.Substring(2))" -ForegroundColor Cyan }
            else { Write-Host "    $l" }
        }
    }
}
