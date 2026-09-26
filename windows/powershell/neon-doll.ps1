# Neon Doll colors for PowerShell. Dot-source it from your profile:
#
#   . "$HOME\neon-doll\windows\powershell\neon-doll.ps1"    # wherever it lives
#
# and, for the prompt too, add `Enable-NeonDollPrompt` on the line after.
#
# Like the ls and git colors, only the 16 terminal colors are named, so this
# follows whichever Neon Doll scheme the terminal uses, dark or light. The
# roles are the man-page ones: commands and parameters purple, the values you
# fill in cyan, strings yellow, comments muted and italic. Nothing is bold.
# Fuchsia isn't in the terminal palette; only the opt-in prompt uses it, for
# the working directory, since that's where you are.
#
# Works in Windows PowerShell 5.1 (the one built into Windows) and in
# PowerShell 7; the $PSStyle parts (Get-ChildItem, tables, errors, progress)
# need 7.2 or newer and are skipped before that.

$e = [char]27

# --- As you type (PSReadLine) -----------------------------------------------

if (Get-Module -ListAvailable PSReadLine) {
    $colors = @{
        Command   = "$e[35m"        # purple, as man sets commands
        Parameter = "$e[35m"
        Keyword   = "$e[95m"        # a lighter purple, apart from commands
        Variable  = "$e[36m"        # cyan: the values you fill in
        Member    = "$e[36m"
        Type      = "$e[36m"
        String    = "$e[33m"        # yellow, the string color everywhere
        Number    = "$e[35m"
        Operator  = "$e[90m"        # muted
        Comment   = "$e[3;90m"      # muted italic
        Default   = "$e[39m"
        Error     = "$e[31m"
        Emphasis  = "$e[4;35m"      # the matched text in history search
    }
    # Keys that only newer PSReadLine versions know about.
    $newer = @{
        InlinePrediction      = "$e[90m"
        ListPrediction        = "$e[90m"
        ListPredictionSelected = "$e[7m"
        Selection             = "$e[7m"
    }
    $known = (Get-PSReadLineOption).PSObject.Properties.Name
    foreach ($k in $newer.Keys) {
        if ($known -contains "${k}Color") { $colors[$k] = $newer[$k] }
    }
    Set-PSReadLineOption -Colors $colors
}

# --- Output ($PSStyle, PowerShell 7.2+) -------------------------------------

if ($PSVersionTable.PSVersion -ge [version]'7.2') {
    $PSStyle.Formatting.TableHeader            = "$e[35m"
    $PSStyle.Formatting.CustomTableHeaderLabel = "$e[3;35m"
    $PSStyle.Formatting.FormatAccent           = "$e[35m"
    $PSStyle.Formatting.ErrorAccent            = "$e[31m"
    $PSStyle.Formatting.Error                  = "$e[31m"
    $PSStyle.Formatting.Warning                = "$e[33m"
    $PSStyle.Formatting.Verbose                = "$e[90m"
    $PSStyle.Formatting.Debug                  = "$e[90m"
    $PSStyle.Progress.Style                    = "$e[35m"

    # Get-ChildItem, matching the Neon Doll dircolors.
    $PSStyle.FileInfo.Directory    = "$e[35m"
    $PSStyle.FileInfo.SymbolicLink = "$e[36m"
    $PSStyle.FileInfo.Executable   = "$e[32m"
    $ext = $PSStyle.FileInfo.Extension
    $ext.Clear()
    foreach ($x in '.zip','.7z','.rar','.tar','.gz','.xz','.zst','.bz2','.cab','.msi','.iso','.img','.jar','.nupkg') { $ext[$x] = "$e[33m" }
    foreach ($x in '.png','.jpg','.jpeg','.gif','.webp','.avif','.heic','.bmp','.tif','.tiff','.svg','.mp4','.mkv','.webm','.mov','.avi') { $ext[$x] = "$e[34m" }
    foreach ($x in '.flac','.mp3','.ogg','.opus','.wav','.m4a','.aac') { $ext[$x] = "$e[36m" }
    foreach ($x in '.ps1','.psm1','.psd1','.bat','.cmd') { $ext[$x] = "$e[32m" }
    foreach ($x in '.bak','.old','.orig','.tmp','.log') { $ext[$x] = "$e[90m" }
}

# --- The prompt (opt-in) -----------------------------------------------------

# The bash prompt's layout and colors: [time] [user@host:path], then $ on its
# own line. Time muted, user@host purple, the path fuchsia. Fuchsia isn't in
# the palette, so it's 24-bit: -Variant Light picks the shade that reads on
# paper.
function Enable-NeonDollPrompt {
    param([ValidateSet('Dark', 'Light')][string]$Variant = 'Dark')
    $script:NeonDollPink = if ($Variant -eq 'Light') { "$e[38;2;200;0;106m" } else { "$e[38;2;255;45;149m" }
    function global:prompt {
        $esc = [char]27
        $user = [Environment]::UserName
        $hostName = [Environment]::MachineName.ToLower()
        $path = $ExecutionContext.SessionState.Path.CurrentLocation.Path
        if ($path.StartsWith($HOME, [StringComparison]::OrdinalIgnoreCase)) {
            $path = '~' + $path.Substring($HOME.Length)
        }
        $time = Get-Date -Format 'HH:mm:ss'
        "$esc[90m[$time]$esc[0m [$esc[35m$user@${hostName}:$($script:NeonDollPink)$path$esc[0m]`n$ "
    }
}
