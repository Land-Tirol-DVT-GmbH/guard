# Define model names
$spacyModels = @('en_core_web_lg', 'de_core_news_lg', 'it_core_news_lg')
$summaries = @()
$totalSize = 0

Write-Host "`nCalculating model storage usage...`n"

# SpaCy models
foreach ($model in $spacyModels) {
    $path = python -c "import spacy; print(spacy.util.get_package_path('$model'))" 2>$null
    if (Test-Path $path) {
        $size = (Get-ChildItem -Path $path -Recurse -Force | Measure-Object -Property Length -Sum).Sum
        $sizeMB = [math]::Round($size / 1MB, 2)
        $totalSize += $size
        $summaries += [PSCustomObject]@{
            Name = "SpaCy: $model"
            SizeMB = $sizeMB
            Path = $path
        }
    }
}

# Hugging Face Transformer models
$hfCache = "$env:USERPROFILE\.cache\huggingface\hub"
if (Test-Path $hfCache) {
    $size = (Get-ChildItem -Path $hfCache -Recurse -Force | Measure-Object -Property Length -Sum).Sum
    $sizeMB = [math]::Round($size / 1MB, 2)
    $totalSize += $size
    $summaries += [PSCustomObject]@{
        Name = "Hugging Face cache"
        SizeMB = $sizeMB
        Path = $hfCache
    }
}

# Flair embeddings
$flairEmbCache = "$env:USERPROFILE\.flair\embeddings"
if (Test-Path $flairEmbCache) {
    $size = (Get-ChildItem -Path $flairEmbCache -Recurse -Force | Measure-Object -Property Length -Sum).Sum
    $sizeMB = [math]::Round($size / 1MB, 2)
    $totalSize += $size
    $summaries += [PSCustomObject]@{
        Name = "Flair embeddings"
        SizeMB = $sizeMB
        Path = $flairEmbCache
    }
}

# Flair models
$flairModelsPath = Join-Path $env:USERPROFILE ".flair\models"
if (Test-Path $flairModelsPath) {
    $size = (Get-ChildItem -Path $flairModelsPath -Recurse -Force | Measure-Object -Property Length -Sum).Sum
    $sizeMB = [math]::Round($size / 1MB, 2)
    $totalSize += $size
    $summaries += [PSCustomObject]@{
        Name = "Flair models"
        SizeMB = $sizeMB
        Path = $flairModelsPath
    }
}

# Display summary table
$summaries | Format-Table Name, SizeMB, Path -AutoSize

# Print grand total
$totalMB = [math]::Round($totalSize / 1MB, 2)
Write-Host "`nTOTAL: $totalMB MB" -ForegroundColor Green