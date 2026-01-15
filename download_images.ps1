# PowerShell script to download images from CSV
$csvPath = "static\directory.csv"
$staticDir = "static"
$baseDomain = "https://adgsenpai.github.io/leagueoflegendsstaticapi/"

# Create static directory if it doesn't exist
if (-not (Test-Path $staticDir)) {
    New-Item -ItemType Directory -Path $staticDir | Out-Null
}

# Read CSV
$csvData = Import-Csv -Path $csvPath

# Array to store image data
$imageData = @()
$successCount = 0
$failCount = 0

Write-Host "Starting image downloads..." -ForegroundColor Green
Write-Host "Total images to download: $($csvData.Count)" -ForegroundColor Cyan

foreach ($row in $csvData) {
    $id = $row.id
    $description = $row.description
    $url = $row.url
    
    # Extract filename and create new one
    $extension = [System.IO.Path]::GetExtension($url)
    $newFilename = "lol_meme_$id$extension"
    $savePath = Join-Path $staticDir $newFilename
    
    Write-Host "[$id/20] Downloading $description..." -ForegroundColor Yellow
    
    try {
        # Download with proper headers and timeout
        $webClient = New-Object System.Net.WebClient
        $webClient.Headers.Add("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
        $webClient.Headers.Add("Referer", "https://imgur.com/")
        $webClient.DownloadFile($url, $savePath)
        
        Write-Host "  ✓ Saved as: $newFilename" -ForegroundColor Green
        
        # Add to JSON data
        $imageData += @{
            id = [int]$id
            description = $description
            filename = $newFilename
            url = "$baseDomain" + "static/$newFilename"
            original_url = $url
        }
        
        $successCount++
        
        # Add delay to avoid rate limiting (2 seconds)
        Start-Sleep -Seconds 2
        
    } catch {
        Write-Host "  ✗ Error: $($_.Exception.Message)" -ForegroundColor Red
        $failCount++
        
        # Wait longer after an error
        Start-Sleep -Seconds 3
    }
}

# Create JSON output
$jsonOutput = @{
    base_url = $baseDomain
    total_images = $imageData.Count
    images = $imageData
} | ConvertTo-Json -Depth 10

# Save JSON file
$jsonPath = "static\directory.json"
$jsonOutput | Out-File -FilePath $jsonPath -Encoding UTF8

Write-Host "`n================================" -ForegroundColor Cyan
Write-Host "Download complete!" -ForegroundColor Green
Write-Host "✓ Successfully downloaded: $successCount images" -ForegroundColor Green
Write-Host "✗ Failed: $failCount images" -ForegroundColor Red
Write-Host "📄 Created mapping file: $jsonPath" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
