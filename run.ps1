$ErrorActionPreference = "Stop"

try { [Console]::OutputEncoding = [System.Text.Encoding]::UTF8 } catch {}

New-Item -ItemType Directory -Force ".tmp" | Out-Null
$env:TEMP = (Resolve-Path ".tmp").Path
$env:TMP = $env:TEMP

function Find-PreferredPython {
  if (-not [string]::IsNullOrWhiteSpace($env:PYTHON_EXE)) {
    return $env:PYTHON_EXE
  }

  $candidates = @()
  $userBase = Join-Path $env:LOCALAPPDATA "Programs\Python"
  foreach ($dir in @("Python313", "Python312")) {
    $exe = Join-Path (Join-Path $userBase $dir) "python.exe"
    if (Test-Path $exe) { $candidates += $exe }
  }

  $pf = ${env:ProgramFiles}
  foreach ($dir in @("Python313", "Python312")) {
    $exe = Join-Path (Join-Path $pf $dir) "python.exe"
    if (Test-Path $exe) { $candidates += $exe }
  }

  if ($candidates.Count -gt 0) { return $candidates[0] }
  return "python"
}

$env:PYTHONPATH = (Resolve-Path "tools").Path

function Get-PythonVersionTuple {
  param([string]$PythonExe)
  $v = & $PythonExe -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}')"
  return $v
}

$py = Find-PreferredPython

try {
  $ver = Get-PythonVersionTuple -PythonExe $py
} catch {
  Write-Host "Python não encontrado. Instale Python 3.12 ou 3.13 e tente novamente." -ForegroundColor Red
  Write-Host "Ou defina PYTHON_EXE para o caminho do python.exe (ex.: `$env:PYTHON_EXE='C:\\...\\Python313\\python.exe')." -ForegroundColor Red
  exit 1
}

$parts = $ver.Split(".") | ForEach-Object { [int]$_ }
if ($parts[0] -eq 3 -and $parts[1] -ge 14) {
  Write-Host "Detectado Python $ver. FastAPI/Pydantic ainda não suportam bem Python 3.14 neste projeto." -ForegroundColor Yellow
  Write-Host "Instale Python 3.12 ou 3.13 e volte a correr este script." -ForegroundColor Yellow
  Write-Host "Alternativa: aponte PYTHON_EXE para Python 3.12/3.13 e corra de novo." -ForegroundColor Yellow
  exit 1
}

function Get-VenvPythonVersion {
  if (!(Test-Path ".venv\\pyvenv.cfg")) { return $null }
  $cfg = Get-Content ".venv\\pyvenv.cfg" -ErrorAction SilentlyContinue
  $line = $cfg | Where-Object { $_ -match '^version\s*=' } | Select-Object -First 1
  if (-not $line) { return $null }
  return ($line -replace '^version\s*=\s*', '').Trim()
}

$venvVer = Get-VenvPythonVersion
if (!(Test-Path ".venv") -or ($venvVer -and $venvVer.StartsWith("3.14"))) {
  if (Test-Path ".venv") { Remove-Item -Recurse -Force ".venv" }
  # Criar venv sem pip e instalar pip num passo separado.
  # (Workaround para erros de ensurepip em alguns ambientes Windows.)
  & $py -m venv ".venv" --without-pip
  & .\.venv\Scripts\python.exe -m ensurepip --upgrade --default-pip
}

& .\.venv\Scripts\Activate.ps1
if (Test-Path "wheels") {
  python -m pip install --no-index --find-links "wheels" -r requirements.txt
} else {
  python -m pip install -r requirements.txt
}

$port = $env:PORT
if ([string]::IsNullOrWhiteSpace($port)) { $port = "3001" }

$reload = $env:DEV_RELOAD
if ($reload -eq "1" -or $reload -eq "true") {
  python -m uvicorn app.main:app --host 0.0.0.0 --port $port --reload
} else {
  python -m uvicorn app.main:app --host 0.0.0.0 --port $port
}
