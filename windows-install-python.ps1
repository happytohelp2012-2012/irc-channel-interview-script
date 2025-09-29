# Accept Python >= 3.10; otherwise install via winget (fallback: download installer).
$ErrorActionPreference = "Stop"
$RequiredMajor = 3
$RequiredMinor = 10

function Get-PyVersion {
  try {
    $v = & py -3 --version 2>$null
    if (-not $v) { $v = & python --version 2>$null }
    if ($v) {
      if ($v -match '(\d+)\.(\d+)\.(\d+)') {
        return [pscustomobject]@{ Major = [int]$Matches[1]; Minor = [int]$Matches[2]; Raw = $v.Trim() }
      }
    }
  } catch { }
  return $null
}

function Version-OK($ver) {
  if (-not $ver) { return $false }
  return ($ver.Major -gt $RequiredMajor) -or (($ver.Major -eq $RequiredMajor) -and ($ver.Minor -ge $RequiredMinor))
}

Write-Host "▶ Checking Python (need >= $RequiredMajor.$RequiredMinor)..."
$ver = Get-PyVersion
if (Version-OK $ver) {
  Write-Host $ver.Raw
  Write-Host "✅ Python is ready."
  exit 0
}

# Try winget first
$haveWinget = (Get-Command winget -ErrorAction SilentlyContinue) -ne $null
if ($haveWinget) {
  Write-Host "↺ Installing/Upgrading Python via winget..."
  try {
    winget install -e --id Python.Python.3.12 --accept-package-agreements --accept-source-agreements
  } catch {
    Write-Warning "winget install failed: $_"
  }
} else {
  Write-Warning "winget not found; attempting direct installer from python.org..."
  # Minimal fallback: download a 3.12 x64 installer (adjust if needed)
  $Version = "3.12.6"
  $Url = "https://www.python.org/ftp/python/$Version/python-$Version-amd64.exe"
  $Installer = "$env:TEMP\python-$Version-amd64.exe"
  Invoke-WebRequest -Uri $Url -OutFile $Installer
  Start-Process -FilePath $Installer -ArgumentList "/quiet InstallAllUsers=1 PrependPath=1 Include_pip=1" -Wait
}

# Verify
$ver = Get-PyVersion
if (Version-OK $ver) {
  Write-Host $ver.Raw
  Write-Host "✅ Python is ready. Use: py -3  (or 'python')"
  exit 0
} else {
  Write-Error "Python installation did not meet the version requirement (need >= $RequiredMajor.$RequiredMinor)."
  exit 1
}
