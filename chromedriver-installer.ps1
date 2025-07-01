# Chromedriver Automated Installer
# Downloads and extracts Chromedriver for Windows
param(
    [string]$Version = "stable"  # Default to stable version
)

# Ensure secure TLS protocol for downloads
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12

# Retrieve version information
$jsonUrl = "https://googlechromelabs.github.io/chrome-for-testing/last-known-good-versions-with-downloads.json"
try {
    $response = Invoke-RestMethod -Uri $jsonUrl -ErrorAction Stop
}
catch {
    Write-Host "Failed to retrieve version information: $_" -ForegroundColor Red
    exit 1
}

# Parse version data
$availableVersions = $response.channels.PSObject.Properties.Name | Sort-Object
$versionMap = @{
    "stable"  = $response.channels.Stable.version
    "beta"    = $response.channels.Beta.version
    "dev"     = $response.channels.Dev.version
    "canary"  = $response.channels.Canary.version
}

# Display version selection menu
if ($Version -eq "interactive") {
    Write-Host "`nAvailable Versions:" -ForegroundColor Cyan
    $availableVersions | ForEach-Object {
        $verNum = $versionMap[$_]
        Write-Host "  [$($_[0])] $_ (v$verNum)"
    }
    
    $choice = Read-Host "`nSelect version (enter first letter or full name, default stable)"
    if (-not $choice) { $choice = "s" }
    
    $selected = $availableVersions | Where-Object { $_ -like "$choice*" } | Select-Object -First 1
    if (-not $selected) {
        Write-Host "Invalid selection" -ForegroundColor Red
        exit 1
    }
    
    $Version = $selected
    $chromeVersion = $versionMap[$Version]
}
else {
    if ($versionMap.ContainsKey($Version)) {
        $chromeVersion = $versionMap[$Version]
    }
    else {
        Write-Host "Invalid version: $Version" -ForegroundColor Red
        Write-Host "Available versions: $($availableVersions -join ', ')"
        exit 1
    }
}

# Find Windows download URL
$downloads = $response.channels.$Version.downloads.chromedriver
$winDownload = $downloads | Where-Object { $_.platform -eq "win64" }

if (-not $winDownload) {
    Write-Host "Windows download link not found" -ForegroundColor Red
    exit 1
}

# Download archive
$zipFile = "chromedriver_$chromeVersion.zip"
$downloadUrl = $winDownload.url

Write-Host "`nDownloading $Version version (v$chromeVersion)..." -ForegroundColor Cyan
Write-Host "Source: $downloadUrl"

try {
    Invoke-WebRequest -Uri $downloadUrl -OutFile $zipFile -ErrorAction Stop
}
catch {
    Write-Host "Download failed: $_" -ForegroundColor Red
    exit 1
}

# Extract files
Write-Host "`nExtracting files..." -ForegroundColor Cyan
$extractPath = "chromedriver_$chromeVersion"
Expand-Archive -Path $zipFile -DestinationPath $extractPath -Force

# Locate chromedriver.exe
$driverPath = Get-ChildItem -Path $extractPath -Recurse -Filter "chromedriver.exe" | 
              Select-Object -First 1 -ExpandProperty FullName

if (-not $driverPath) {
    Write-Host "chromedriver.exe not found" -ForegroundColor Red
    exit 1
}

# Move to current directory
$destination = Join-Path -Path $PWD.Path -ChildPath "chromedriver.exe"
Move-Item -Path $driverPath -Destination $destination -Force

# Cleanup temporary files
Remove-Item -Path $zipFile -Force
Remove-Item -Path $extractPath -Recurse -Force -ErrorAction SilentlyContinue

Write-Host "`nSuccessfully installed Chromedriver v$chromeVersion!" -ForegroundColor Green
Write-Host "Location: $destination" -ForegroundColor Green