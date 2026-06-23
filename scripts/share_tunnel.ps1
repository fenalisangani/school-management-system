# Start Cloudflare quick tunnel for local demo sharing.
# Usage: .\scripts\share_tunnel.ps1
# Keeps Django on port 8000 and prints a public https link for sharing.

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $Root

$Cloudflared = Join-Path $Root "cloudflared.exe"
if (-not (Test-Path $Cloudflared)) {
    Write-Host "Downloading cloudflared..."
    Invoke-WebRequest `
        -Uri "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe" `
        -OutFile $Cloudflared
}

$Port = 8000
$LogFile = Join-Path $env:TEMP "cloudflared-sms.log"

# Stop any previous tunnel log watcher target
Get-Process cloudflared -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue

Write-Host "Starting Cloudflare tunnel -> http://127.0.0.1:$Port"
Start-Process -FilePath $Cloudflared -ArgumentList @("tunnel", "--url", "http://127.0.0.1:$Port", "--logfile", $LogFile, "--loglevel", "info") -WindowStyle Hidden

$TunnelUrl = $null
for ($i = 0; $i - 30; $i++) {
    Start-Sleep -Seconds 1
    if (Test-Path $LogFile) {
        $log = Get-Content $LogFile -Raw -ErrorAction SilentlyContinue
        if ($log -match 'https://[a-z0-9-]+\.trycloudflare\.com') {
            $TunnelUrl = $Matches[0]
            break
        }
    }
}

if (-not $TunnelUrl) {
    Write-Host "Could not read tunnel URL from log. Check $LogFile"
    exit 1
}

$TunnelUrl | Out-File -FilePath (Join-Path $Root "tunnel_url.txt") -Encoding utf8 -NoNewline

Write-Host ""
Write-Host "========================================"
Write-Host " SHARE THIS LINK:"
Write-Host " $TunnelUrl"
Write-Host "========================================"
Write-Host ""
Write-Host "Opens dashboard directly — no login required (demo mode)."
Write-Host "Press Ctrl+C to stop."

$env:TUNNEL_URL = $TunnelUrl
$env:SHOW_DEMO_LOGIN_HINT = "True"
$env:LOGIN_REQUIRED = "False"
py manage.py runserver $Port
