<#
.SYNOPSIS
    Registers (or removes) a watchdog task for the relay watcher.

.DESCRIPTION
    The watcher holds a singleton lock, so launching it again while it is alive
    exits 3 and changes nothing. That turns a plain every-N-minutes task into a
    restart-if-dead watchdog: no supervisor process, no PID file to babysit.

    Runs in the current user's context, so it needs no elevation. Elevation only
    buys a boot-time start (-AtStartup), which requires an elevated shell.

.EXAMPLE
    pwsh -File tools/relay_watchdog.ps1              # register, 5-minute cadence
    pwsh -File tools/relay_watchdog.ps1 -Minutes 15
    pwsh -File tools/relay_watchdog.ps1 -Remove
#>
[CmdletBinding()]
param(
    [int]    $Minutes    = $(if ($env:NOUGEN_WATCHDOG_MINUTES) { [int]$env:NOUGEN_WATCHDOG_MINUTES } else { 5 }),
    [string] $TaskName   = $(if ($env:NOUGEN_WATCHDOG_TASK) { $env:NOUGEN_WATCHDOG_TASK } else { 'NouGen Relay Watcher' }),
    [string] $PythonPath = $env:NOUGEN_PYTHON,
    [switch] $Remove
)

$ErrorActionPreference = 'Stop'

if ($Remove) {
    schtasks /delete /tn $TaskName /f
    return
}

# Resolve the daemon relative to this script, never from a baked-in path.
$script = Join-Path $PSScriptRoot 'relay_daemon.py'
if (-not (Test-Path $script)) { throw "relay_daemon.py not found beside this script ($PSScriptRoot)" }

# Resolve the interpreter: env override -> PATH -> the py launcher's own answer.
# WindowsApps entries are app-execution aliases; the launcher stub is not the
# interpreter, so ask it where the real one lives rather than scheduling the stub.
if (-not $PythonPath) {
    $PythonPath = (Get-Command python -ErrorAction SilentlyContinue |
        Where-Object { $_.Source -notlike '*WindowsApps*' } |
        Select-Object -First 1 -ExpandProperty Source)
}
if (-not $PythonPath) {
    $launcher = (Get-Command py -ErrorAction SilentlyContinue | Select-Object -First 1 -ExpandProperty Source)
    if ($launcher) {
        $resolved = & $launcher -3 -c 'import sys; print(sys.executable)' 2>$null
        if ($LASTEXITCODE -eq 0 -and $resolved -and (Test-Path $resolved)) { $PythonPath = $resolved.Trim() }
    }
}
if (-not $PythonPath) { throw 'No python interpreter found. Set NOUGEN_PYTHON.' }

Write-Output "python : $PythonPath"
Write-Output "daemon : $script"
Write-Output "cadence: every $Minutes min"

$tr = '"{0}" "{1}" --daemon' -f $PythonPath, $script
schtasks /create /tn $TaskName /tr $tr /sc minute /mo $Minutes /f

schtasks /query /tn $TaskName /fo LIST | Select-String -Pattern 'TaskName|Status|Next Run|Task To Run'
