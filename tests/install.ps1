# Tests for windows/install.ps1. Each one runs the installer against scratch
# folders, never your own.
#
#   pwsh tests/install.ps1
#   powershell -ExecutionPolicy Bypass -File tests\install.ps1   (Windows PowerShell 5.1)
#
# The installer runs in the same PowerShell as the tests. It runs on Linux and
# macOS too, with the Windows folders played by scratch ones, which is also
# where the picker tests run: they need a terminal, which tests/pty_run.py
# gives them, and python3. On Windows, $PROFILE can't be moved to a scratch
# folder, so the powershell part is only tested there under CI.

$ErrorActionPreference = 'Stop'
function P { [IO.Path]::Combine([string[]]$args) }

$root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$installer = P $root 'windows' 'install.ps1'
$shell = (Get-Process -Id $PID).Path
$onWindows = $PSVersionTable.PSEdition -eq 'Desktop' -or $IsWindows
$scratch = P ([IO.Path]::GetTempPath()) ("neon-doll-test-" + [guid]::NewGuid())
New-Item -ItemType Directory $scratch | Out-Null
$saved = @{}
foreach ($v in 'HOME', 'USERPROFILE', 'LOCALAPPDATA', 'APPDATA', 'ProgramFiles', 'XDG_CONFIG_HOME', 'XDG_DATA_HOME', 'XDG_CACHE_HOME') {
    $saved[$v] = [Environment]::GetEnvironmentVariable($v)
}
$script:pass = 0; $script:fail = 0; $script:skipped = 0
$script:n = 0

function Check($name, [scriptblock]$test) {
    if (& $test) { $script:pass++; "ok    $name" }
    else {
        $script:fail++; "FAIL  $name"
        ($script:out -split "`n") | ForEach-Object { "      | $_" }
    }
}
function Skip($name, $why) { $script:skipped++; "skip  ${name}: $why" }

# Fresh scratch folders, with the environment pointing at them.
function Fresh {
    $script:n++
    $script:h = P $scratch "home$($script:n)"
    foreach ($d in 'home', 'local', 'roaming', 'pf') { New-Item -ItemType Directory -Force (P $h $d) | Out-Null }
    $env:HOME = $env:USERPROFILE = P $h 'home'
    $env:LOCALAPPDATA = P $h 'local'
    $env:APPDATA = P $h 'roaming'
    $env:ProgramFiles = P $h 'pf'
    # PowerShell on Unix finds $PROFILE through these, when they're set.
    $env:XDG_CONFIG_HOME = P $env:HOME '.config'
    $env:XDG_DATA_HOME = P $env:HOME '.local' 'share'
    $env:XDG_CACHE_HOME = P $env:HOME '.cache'
    $script:out = ''
}

# Run: the installer with no console to ask in. Output in $out, status in $st.
function Run {
    param([string]$Script = $installer, [Parameter(ValueFromRemainingArguments = $true)][string[]]$Arguments)
    $ErrorActionPreference = 'Continue'
    $script:out = (@($null | & $shell -NoProfile -ExecutionPolicy Bypass -File $Script @Arguments 2>&1) |
        ForEach-Object { "$_" }) -join "`n"
    $script:st = $LASTEXITCODE
}

# Pick: the installer in a terminal, answered by STEPs; see tests/pty_run.py.
function Pick {
    $ErrorActionPreference = 'Continue'
    $script:out = (@(& python3 (P $root 'tests' 'pty_run.py') @args '--' $shell -NoProfile -File $installer 2>&1) |
        ForEach-Object { "$_" }) -join "`n"
    $script:st = $LASTEXITCODE
}

# Files: what's in the scratch folders, less PowerShell's own caches (under
# .cache and .local/share/powershell on Unix, Microsoft\PowerShell and
# Microsoft\Windows\PowerShell in LOCALAPPDATA on Windows).
function Files {
    @(Get-ChildItem -Recurse -Force -File $h | ForEach-Object { $_.FullName.Substring($h.Length) } |
        Where-Object { $_ -notmatch '[\\/](\.cache|\.local[\\/]share[\\/]powershell|Microsoft[\\/](Windows[\\/])?PowerShell)[\\/]' } | Sort-Object) -join "`n"
}
function Has($path) { Test-Path (P $h $path) }
function Says($pattern) { $script:out -match $pattern }

# Two Firefox profiles: "main", the default, and "spare", which already lets
# userChrome.css in.
function FirefoxFixture {
    $script:ff = P $env:APPDATA 'Mozilla' 'Firefox'
    foreach ($p in 'a.main', 'b.spare') { New-Item -ItemType Directory -Force (P $ff 'Profiles' $p) | Out-Null }
    Set-Content (P $ff 'profiles.ini') @(
        '[Profile1]', 'Name=spare', 'IsRelative=1', 'Path=Profiles/b.spare', '',
        '[Profile0]', 'Name=main', 'IsRelative=1', 'Path=Profiles/a.main', '',
        '[Install308046B0AF4A39CB]', 'Default=Profiles/a.main', 'Locked=1')
    Set-Content (P $ff 'Profiles' 'b.spare' 'prefs.js') 'user_pref("toolkit.legacyUserProfileCustomizations.stylesheets", true);'
}

$parts = 'terminal', 'powershell', 'contrast', 'vscode', 'firefox', 'git', 'vim'
$profileSafe = -not $onWindows -or $env:CI
$vimFile = P 'home' 'vimfiles' 'colors' 'neon-doll.vim'

try {
    # --- Arguments ---------------------------------------------------------

    Fresh; Run -Arguments 'bogus'
    Check 'an unknown part fails' { $st -ne 0 -and (Says 'unknown part: bogus') }

    Fresh; Run -Arguments 'terminal,vim'
    Check 'parts can be comma-separated' { $st -eq 0 -and (Has 'local/Microsoft/Windows Terminal/Fragments/Neon Doll/neon-doll.json') -and (Has $vimFile) }

    # --- Every part ----------------------------------------------------------

    foreach ($part in $parts) {
        if ($part -eq 'powershell' -and -not $profileSafe) { Skip "${part}: installs, then removes cleanly" 'it would write to your real profile folder'; continue }
        Fresh
        if ($part -eq 'firefox') { FirefoxFixture }
        $before = Files
        Run -Arguments $part
        $st1 = $st; $after = Files
        Run -Arguments '-Remove', $part
        Check "${part}: installs, then removes cleanly" { $st1 -eq 0 -and $after -ne $before -and $st -eq 0 -and (Files) -eq $before }
    }

    if ($profileSafe) {
        Fresh; FirefoxFixture
        $before = Files
        Run
        Check 'with no console, it installs every part' {
            $st -eq 0 -and (Has $vimFile) -and (Has 'local/Microsoft/Windows/Themes/Neon Doll/neon-doll-dark.theme') -and (Says 'To turn it on')
        }
        Run -Arguments '-Remove'
        Check '-Remove with no parts takes all of it out' { $st -eq 0 -and (Files) -eq $before }
    } else {
        Skip 'with no console, it installs every part' 'it would write to your real profile folder'
    }

    # --- Files of your own ----------------------------------------------------

    Fresh
    $vim = P $h $vimFile
    New-Item -ItemType Directory -Force (Split-Path -Parent $vim) | Out-Null
    Set-Content $vim 'mine'
    Run -Arguments 'vim'
    $bak = @(Get-ChildItem "$vim.bak.*")
    Check 'a file of yours is moved aside' {
        $st -eq 0 -and $bak.Count -eq 1 -and (Get-Content $bak[0]) -eq 'mine' -and
        (Get-FileHash $vim).Hash -eq (Get-FileHash (P $root 'vim' 'colors' 'neon-doll.vim')).Hash
    }
    Run -Arguments '-Remove', 'vim'
    Check '-Remove leaves the moved-aside file' { $st -eq 0 -and -not (Test-Path $vim) -and (Test-Path $bak[0].FullName) }

    Fresh
    Run -Arguments 'vim'
    Add-Content (P $h $vimFile) '" my edit'
    Run -Arguments '-Remove', 'vim'
    Check "-Remove leaves a copy you've changed" { $st -eq 0 -and (Has $vimFile) -and (Says 'left .* alone') }

    Fresh
    Run -Arguments 'vscode'
    Run -Arguments 'vscode'
    Check 'installing a folder twice keeps no backup' { $st -eq 0 -and -not ((Files) -match '\.bak\.') }

    # --- Firefox -----------------------------------------------------------------

    Fresh; FirefoxFixture
    Run -Arguments 'firefox'
    Check 'firefox goes to the default profile only' {
        $st -eq 0 -and (Test-Path (P $ff 'Profiles' 'a.main' 'chrome' 'userChrome.css')) -and -not (Test-Path (P $ff 'Profiles' 'b.spare' 'chrome'))
    }
    Check 'firefox names the profile that needs the pref' { Says 'profiles a\.main' }

    Fresh
    Run -Arguments 'firefox'
    Check 'firefox with no profile is skipped' { $st -eq 0 -and (Says 'no Firefox profile found') }

    # --- The Windows zip ------------------------------------------------------------

    Fresh
    $zip = P $h 'zip'
    New-Item -ItemType Directory $zip | Out-Null
    Copy-Item -Recurse (P $root 'windows') $zip
    $zipInstaller = P $zip 'windows' 'install.ps1'
    Run -Script $zipInstaller -Arguments 'vim'
    Check "a part whose files aren't there is skipped" { $st -eq 0 -and (Says 'skipped vim') -and -not (Has $vimFile) }
    Run -Script $zipInstaller -Arguments 'terminal', 'contrast'
    Check 'the zip installs its own parts' { $st -eq 0 -and (Has 'local/Microsoft/Windows/Themes/Neon Doll/neon-doll-light.theme') }

    # --- The picker ----------------------------------------------------------------

    if ($onWindows) {
        Skip 'the picker' 'tests/pty_run.py needs a Unix terminal'
    } elseif (-not (Get-Command python3 -ErrorAction SilentlyContinue)) {
        Skip 'the picker' 'no python3 to drive it'
    } else {
        Fresh
        Pick 'expect:Enter to go on' 'send:n\r' 'tick:vim' 'expect:Enter to go on' 'send:\r'
        Check "the picker installs what's ticked" { $st -eq 0 -and (Files) -eq ([IO.Path]::DirectorySeparatorChar + $vimFile) }

        Fresh
        Pick 'expect:Enter to go on' 'send:q\r'
        Check "the picker's q installs nothing" { $st -eq 0 -and (Says 'Nothing installed') -and -not (Has $vimFile) }

        Fresh; FirefoxFixture
        Pick 'expect:Enter to go on' 'send:n\r' 'tick:firefox' 'expect:Enter to go on' 'send:\r' `
            'expect:which profiles' 'tick:main' 'tick:spare' 'expect:Enter to go on' 'send:\r'
        Check 'the picker asks which Firefox profiles' {
            $st -eq 0 -and (Test-Path (P $ff 'Profiles' 'b.spare' 'chrome' 'userChrome.css')) -and -not (Test-Path (P $ff 'Profiles' 'a.main' 'chrome'))
        }
    }
} finally {
    foreach ($v in $saved.Keys) { [Environment]::SetEnvironmentVariable($v, $saved[$v]) }
    Remove-Item -Recurse -Force $scratch -ErrorAction SilentlyContinue
}

''
"$pass passed, $fail failed, $skipped skipped (install.ps1 under PowerShell $($PSVersionTable.PSVersion))"
if ($fail) { exit 1 }
