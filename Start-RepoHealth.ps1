$ErrorActionPreference = "Continue"

$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$BackendPort = 8002
$FrontendPort = 5174
$FrontendHost = "127.0.0.1"
$BackendUrl = "http://127.0.0.1:$BackendPort/health"
$FrontendUrl = "http://127.0.0.1:$FrontendPort/?theme=dark"
$LogDir = Join-Path $env:TEMP "repo-health-check"

New-Item -ItemType Directory -Force -Path $LogDir | Out-Null

function Find-CommandPath {
    param(
        [string] $Name,
        [string] $Fallback
    )
    $cmd = Get-Command $Name -ErrorAction SilentlyContinue
    if ($cmd) {
        return $cmd.Source
    }
    if ($Fallback -and (Test-Path -LiteralPath $Fallback)) {
        return $Fallback
    }
    return $null
}

function Test-UrlReady {
    param([string] $Url)
    try {
        $response = Invoke-WebRequest -UseBasicParsing -Uri $Url -TimeoutSec 2
        return $response.StatusCode -eq 200
    } catch {
        return $false
    }
}

function Quote-ForPs {
    param([string] $Value)
    return "'" + ($Value -replace "'", "''") + "'"
}

function Start-DevWindow {
    param(
        [string] $Title,
        [string] $Command
    )
    $encoded = [Convert]::ToBase64String([Text.Encoding]::Unicode.GetBytes($Command))
    Start-Process -FilePath "powershell.exe" -ArgumentList @(
        "-NoExit",
        "-ExecutionPolicy", "Bypass",
        "-EncodedCommand", $encoded
    ) -WindowStyle Normal | Out-Null
}

$BundledPython = Join-Path $env:USERPROFILE ".cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"
$BundledNode = Join-Path $env:USERPROFILE ".cache\codex-runtimes\codex-primary-runtime\dependencies\node\bin\node.exe"
$BundledPnpm = Join-Path $env:USERPROFILE ".cache\codex-runtimes\codex-primary-runtime\dependencies\bin\pnpm.cmd"

$PythonExe = Find-CommandPath -Name "python.exe" -Fallback $BundledPython
$NodeExe = Find-CommandPath -Name "node.exe" -Fallback $BundledNode
$PnpmExe = Find-CommandPath -Name "pnpm.cmd" -Fallback $BundledPnpm

Write-Host "======================================"
Write-Host "Repo Health Check - local dev launcher"
Write-Host "======================================"
Write-Host "Project : $Root"
Write-Host "Backend : http://127.0.0.1:$BackendPort"
Write-Host "Frontend: $FrontendUrl"
Write-Host "Logs    : $LogDir"
Write-Host "Python  : $PythonExe"
Write-Host "Node    : $NodeExe"
Write-Host "pnpm    : $PnpmExe"
Write-Host ""

if (-not $PythonExe) {
    throw "Python was not found. Install Python or add it to PATH."
}
if (-not $NodeExe) {
    throw "node.exe was not found. Install Node.js or add it to PATH."
}
if (-not (Test-Path -LiteralPath (Join-Path $Root "backend\main.py"))) {
    throw "backend\main.py was not found. Keep this launcher in the project root."
}
if (-not (Test-Path -LiteralPath (Join-Path $Root "frontend\package.json"))) {
    throw "frontend\package.json was not found. Keep this launcher in the project root."
}

$EnvFile = Join-Path $Root ".env"
$EnvExample = Join-Path $Root ".env.example"
if (-not (Test-Path -LiteralPath $EnvFile) -and (Test-Path -LiteralPath $EnvExample)) {
    Copy-Item -LiteralPath $EnvExample -Destination $EnvFile
}

Write-Host "[INFO] Checking backend dependencies..."
Push-Location -LiteralPath $Root
try {
    & $PythonExe -c "import fastapi, uvicorn, dotenv, itsdangerous" > (Join-Path $LogDir "backend-check.log") 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[INFO] Backend dependencies are missing. Installing now..."
        & $PythonExe -m pip install -r "backend\requirements.txt" > (Join-Path $LogDir "backend-install.log") 2>&1
        if ($LASTEXITCODE -ne 0) {
            throw "Backend dependency installation failed. Log: $(Join-Path $LogDir 'backend-install.log')"
        }
    } else {
        Write-Host "[INFO] Backend dependencies are ready."
    }
} finally {
    Pop-Location
}

Write-Host "[INFO] Checking frontend dependencies..."
$ViteBin = Join-Path $Root "frontend\node_modules\vite\bin\vite.js"
if (-not (Test-Path -LiteralPath $ViteBin)) {
    if (-not $PnpmExe) {
        throw "Frontend dependencies are missing and pnpm.cmd was not found."
    }
    Push-Location -LiteralPath (Join-Path $Root "frontend")
    try {
        & $PnpmExe install > (Join-Path $LogDir "frontend-install.log") 2>&1
        if ($LASTEXITCODE -ne 0) {
            throw "Frontend dependency installation failed. Log: $(Join-Path $LogDir 'frontend-install.log')"
        }
    } finally {
        Pop-Location
    }
}

$BackendReady = Test-UrlReady $BackendUrl
$FrontendReady = Test-UrlReady $FrontendUrl

if ($BackendReady) {
    Write-Host "[INFO] Backend is already running."
} else {
    Write-Host "[INFO] Starting backend window..."
    $backendCommand = @"
`$Host.UI.RawUI.WindowTitle = 'Repo Health Backend :$BackendPort'
Set-Location -LiteralPath $(Quote-ForPs $Root)
& $(Quote-ForPs $PythonExe) -m uvicorn backend.main:app --host 127.0.0.1 --port $BackendPort --reload
"@
    Start-DevWindow -Title "Repo Health Backend" -Command $backendCommand
}

if ($FrontendReady) {
    Write-Host "[INFO] Frontend is already running."
} else {
    Write-Host "[INFO] Starting frontend window..."
    $frontendRoot = Join-Path $Root "frontend"
    $frontendCommand = @"
`$Host.UI.RawUI.WindowTitle = 'Repo Health Frontend :$FrontendPort'
Set-Location -LiteralPath $(Quote-ForPs $frontendRoot)
& $(Quote-ForPs $NodeExe) 'node_modules\vite\bin\vite.js' --host $FrontendHost
"@
    Start-DevWindow -Title "Repo Health Frontend" -Command $frontendCommand
}

Write-Host ""
Write-Host "[INFO] Waiting for backend and frontend to become ready..."
for ($i = 0; $i -lt 90; $i++) {
    $BackendReady = Test-UrlReady $BackendUrl
    $FrontendReady = Test-UrlReady $FrontendUrl
    if ($BackendReady -and $FrontendReady) {
        Write-Host ""
        Write-Host "[OK] Backend and frontend are ready."
        Write-Host "[INFO] Opening browser: $FrontendUrl"
        Start-Process $FrontendUrl | Out-Null
        Start-Sleep -Seconds 2
        exit 0
    }
    Start-Sleep -Seconds 2
}

Write-Host ""
Write-Host "[ERROR] Services did not become ready in time."
Write-Host "Backend ready : $BackendReady"
Write-Host "Frontend ready: $FrontendReady"
Write-Host "Logs: $LogDir"
Read-Host "Press Enter to exit"
exit 1
