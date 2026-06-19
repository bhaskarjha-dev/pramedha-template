#!/usr/bin/env pwsh
# Resume Cascade Build Script (Windows)
# Assembles all variants from master.yaml and renders to PDF.

$ErrorActionPreference = "Stop"
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition

Write-Host "`n=== Resume Cascade Build ===" -ForegroundColor Cyan

# Step 1: Assemble all variants
Write-Host "`n[1/2] Assembling variants..." -ForegroundColor Yellow
python "$scriptDir\assemble.py"
if ($LASTEXITCODE -ne 0) {
    Write-Host "Assembly failed!" -ForegroundColor Red
    exit 1
}

# Step 2: Render each generated YAML to PDF
Write-Host "`n[2/2] Rendering PDFs..." -ForegroundColor Yellow
$generatedDir = "$scriptDir\generated"
$outputDir = "$scriptDir\output"
New-Item -ItemType Directory -Force -Path $outputDir | Out-Null

Get-ChildItem "$generatedDir\*.yaml" | ForEach-Object {
    $name = $_.BaseName
    Write-Host "  Rendering $name..." -ForegroundColor Gray
    rendercv render $_.FullName --output-folder-name $outputDir 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Host "  ❌ Failed: $name" -ForegroundColor Red
    } else {
        Write-Host "  ✅ $name" -ForegroundColor Green
    }
}

Write-Host "`n=== Build Complete ===" -ForegroundColor Cyan
Write-Host "PDFs are in: $outputDir`n"
