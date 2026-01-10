<#
.SYNOPSIS
    Automated Cloudflare Tunnel Setup Script for TalentOS
    
.DESCRIPTION
    This script automates the setup of Cloudflare Tunnel to expose:
    1. Streamlit Web App (http://localhost:8501) -> https://bmwuv.com/
    2. FastAPI Backend (http://localhost:8000/analyze) -> https://bmwuv.com/analyze
    
    It handles:
    - Tunnel creation (talentos-tunnel)
    - Configuration file generation (tunnel_config.yml)
    - DNS routing (bmwuv.com)
    
.NOTES
    Author: AI Assistant (ESTJ Persona)
    Date: 2026-01-08
#>

$ErrorActionPreference = "Stop"
$TunnelName = "talentos-tunnel"
$Domain = "bmwuv.com"
$ConfigFile = "tunnel_config.yml"
$UserHome = $env:USERPROFILE
$CloudflaredDir = "$UserHome\.cloudflared"

function Write-Log {
    param([string]$Message, [string]$Level="INFO")
    $Color = @{ "INFO"="Cyan"; "SUCCESS"="Green"; "WARNING"="Yellow"; "ERROR"="Red" }
    Write-Host "[$Level] $Message" -ForegroundColor $Color[$Level]
}

# 1. Check Pre-requisites
Write-Log "Checking pre-requisites..."
if (-not (Get-Command "cloudflared" -ErrorAction SilentlyContinue)) {
    Write-Log "cloudflared.exe not found in PATH!" "ERROR"
    Write-Log "Please ensure cloudflared is installed and added to your PATH." "ERROR"
    exit 1
}

# 2. Check Authentication
if (-not (Test-Path "$CloudflaredDir\cert.pem")) {
    Write-Log "Authentication required. Opening browser..." "WARNING"
    cloudflared tunnel login
    if (-not (Test-Path "$CloudflaredDir\cert.pem")) {
        Write-Log "Authentication failed or cancelled." "ERROR"
        exit 1
    }
} else {
    Write-Log "Already authenticated." "SUCCESS"
}

# 3. Create/Get Tunnel
Write-Log "Checking tunnel '$TunnelName'..."
$TunnelList = cloudflared tunnel list | Out-String
$TunnelId = ""

# Regex to match UUID strictly
$UuidPattern = "([a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})"

if ($TunnelList -match "$TunnelName\s+.*?$UuidPattern" -or $TunnelList -match "$UuidPattern\s+$TunnelName") {
    # Check which group captured the UUID
    $TunnelId = if ($matches[1] -match "^$UuidPattern$") { $matches[1] } else { $matches[2] }
    Write-Log "Tunnel '$TunnelName' exists (ID: $TunnelId)." "SUCCESS"
} else {
    Write-Log "Creating tunnel '$TunnelName'..."
    try {
        cloudflared tunnel create $TunnelName 2>&1 | Out-Null
    } catch {
        # Check if it failed because it already exists
        if ($_ -match "already exists") {
             Write-Log "Tunnel already exists (caught in error), retrieving ID..." "WARNING"
        } else {
             Write-Log "Failed to create tunnel: $_" "ERROR"
             # Try to continue if we can find the ID anyway
        }
    }
    
    # Re-fetch ID regardless of creation success/fail
    $TunnelList = cloudflared tunnel list | Out-String
    if ($TunnelList -match "$TunnelName\s+.*?$UuidPattern" -or $TunnelList -match "$UuidPattern\s+$TunnelName") {
        $TunnelId = if ($matches[1] -match "^$UuidPattern$") { $matches[1] } else { $matches[2] }
        Write-Log "Tunnel ID retrieved: $TunnelId" "SUCCESS"
    } else {
        Write-Log "FATAL: Could not retrieve Tunnel ID." "ERROR"
        exit 1
    }
}

# 4. Generate Config File
Write-Log "Generating $ConfigFile..."
$CredFile = "$CloudflaredDir\$TunnelId.json".Replace("\", "\\")

$ConfigContent = @"
tunnel: $TunnelId
credentials-file: $CredFile

ingress:
  # FastAPI Backend (Specific Paths)
  - hostname: $Domain
    path: /analyze
    service: http://localhost:8000
  - hostname: $Domain
    path: /health
    service: http://localhost:8000
  - hostname: $Domain
    path: /docs
    service: http://localhost:8000
  - hostname: $Domain
    path: /openapi.json
    service: http://localhost:8000

  # Streamlit Web App (Root & Assets)
  - hostname: $Domain
    service: http://localhost:8501

  # Catch-all
  - service: http_status:404
"@

Set-Content -Path $ConfigFile -Value $ConfigContent -Encoding UTF8
Write-Log "Configuration saved to $ConfigFile." "SUCCESS"

# 5. Route DNS
Write-Log "Routing DNS for $Domain..."
# Use cmd /c to prevent PowerShell from treating stderr as NativeCommandError
$RouteOutput = cmd /c "cloudflared tunnel route dns -f $TunnelId $Domain 2>&1" | Out-String
Write-Host $RouteOutput

if ($RouteOutput -match "Added CNAME (.*?) which") {
    $CreatedDomain = $matches[1].Trim()
    if ($CreatedDomain -ne $Domain) {
        Write-Log "DOMAIN MISMATCH WARNING!" "ERROR"
        Write-Log "Requested: $Domain" "ERROR"
        Write-Log "Created:   $CreatedDomain" "ERROR"
        Write-Log "Reason:    Cloudflare likely does not recognize '$Domain' as a Zone in your account." "ERROR"
        Write-Log "Solution:  1. Add '$Domain' to Cloudflare Dashboard." "ERROR"
        Write-Log "           2. Run 'cloudflared tunnel login' to refresh permissions." "ERROR"
    } else {
        Write-Log "DNS routed successfully." "SUCCESS"
    }
} elseif ($RouteOutput -match "already configured") {
     # Check if it mentions the WRONG domain (e.g., bmwuv.com.seeingpure.com)
     if ($RouteOutput -match "$Domain\.([a-zA-Z0-9-]+\.[a-zA-Z]+)") {
        Write-Log "DOMAIN MISMATCH WARNING (Existing Route)!" "ERROR"
        Write-Log "Cloudflare thinks '$Domain' is a subdomain of $($matches[1])." "ERROR"
        Write-Log "Solution:  1. Add '$Domain' to Cloudflare Dashboard." "ERROR"
        Write-Log "           2. Run 'cloudflared tunnel login' to refresh permissions." "ERROR"
     } else {
        Write-Log "DNS routed successfully (already existed)." "SUCCESS"
     }
} else {
    Write-Log "DNS routing completed (check output above)." "INFO"
}

# 6. Final Instructions
Write-Log "`n=== Setup Complete! ===" "SUCCESS"
Write-Log "To start the tunnel, run:" "INFO"
Write-Log "cloudflared tunnel run $TunnelName" "INFO"
Write-Log "   OR" "INFO"
Write-Log "cloudflared tunnel --config $ConfigFile run" "INFO"
