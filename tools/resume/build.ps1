#!/usr/bin/env pwsh
# Resume Cascade Build Script (Windows)
# Assembles all variants from master.yaml and renders to PDF.

$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8
$env:PYTHONIOENCODING = "utf-8"
$env:PYTHONUTF8 = "1"
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition

Write-Host "`n=== Resume Cascade Build ===" -ForegroundColor Cyan

# Check Python availability
$pythonExe = if (Get-Command py -ErrorAction SilentlyContinue) { "py" } elseif (Get-Command python -ErrorAction SilentlyContinue) { "python" } else { "python" }
$useUv = $false
if (-not (Get-Command py -ErrorAction SilentlyContinue) -and -not (Get-Command python -ErrorAction SilentlyContinue) -and (Get-Command uv -ErrorAction SilentlyContinue)) {
    $useUv = $true
}

$runPy = {
    param([string[]]$cmdArgs)
    if ($useUv) {
        & uv run python @cmdArgs
    } else {
        & $pythonExe @cmdArgs
    }
}

# Step 1: Assemble all variants
Write-Host "`n[1/2] Assembling variants..." -ForegroundColor Yellow
& $runPy @("$scriptDir\assemble.py")

if ($LASTEXITCODE -ne 0) {
    Write-Host "Assembly failed!" -ForegroundColor Red
    exit 1
}

# Step 2: Render each generated YAML to PDF
Write-Host "`n[2/2] Rendering PDFs..." -ForegroundColor Yellow
$generatedDir = "$scriptDir\generated"
$outputDir = "$scriptDir\output"
New-Item -ItemType Directory -Force -Path $outputDir | Out-Null

$yamlFiles = Get-ChildItem "$generatedDir\*.yaml" -ErrorAction SilentlyContinue
if (-not $yamlFiles -or $yamlFiles.Count -eq 0) {
    Write-Host "  No generated YAML files found in $generatedDir." -ForegroundColor Gray
    Write-Host "  Create a variant file in tools/resume/variants/ first (e.g. copy _template.yaml to A_Role.yaml)." -ForegroundColor Gray
    Write-Host "`n=== Build Complete ===" -ForegroundColor Cyan
    exit 0
}

# Ensure UTF-8 console output for RenderCV rich logging
$env:PYTHONIOENCODING = "utf-8"
$env:PYTHONUTF8 = "1"

# Check if rendercv is available
$rendercvMode = if (Get-Command rendercv -ErrorAction SilentlyContinue) {
    "cli"
} else {
    # Check if python -m rendercv works
    $testRc = & $runPy @("-m", "rendercv", "--version") 2>&1
    if ($LASTEXITCODE -eq 0) { "module" } else { $null }
}

if (-not $rendercvMode) {
    Write-Host "  RenderCV CLI not found." -ForegroundColor Yellow
    Write-Host "  Install with: pip install rendercv" -ForegroundColor Yellow
    Write-Host "  Generated YAMLs are ready in: $generatedDir" -ForegroundColor Cyan
    exit 0
}

Push-Location $scriptDir
try {
    foreach ($file in $yamlFiles) {
        $name = $file.BaseName
        Write-Host "  Rendering $name..." -ForegroundColor Gray
        $variantOutputDir = Join-Path $outputDir $name
        New-Item -ItemType Directory -Force -Path $variantOutputDir | Out-Null

        if ($rendercvMode -eq "cli") {
            rendercv render $file.FullName -o $variantOutputDir 2>&1
        } else {
            & $runPy @("-m", "rendercv", "render", $file.FullName, "-o", $variantOutputDir) 2>&1
        }
        if ($LASTEXITCODE -ne 0) {
            Write-Host "  ❌ Failed: $name" -ForegroundColor Red
        } else {
            $generatedPdf = Get-ChildItem "$variantOutputDir\*.pdf" -ErrorAction SilentlyContinue | Select-Object -First 1
            if ($generatedPdf) {
                Copy-Item -Path $generatedPdf.FullName -Destination "$outputDir\$name.pdf" -Force
                Write-Host "  ✅ $name -> output\$name.pdf" -ForegroundColor Green
            } else {
                Write-Host "  ✅ $name" -ForegroundColor Green
            }
        }
    }
} finally {
    Pop-Location
}

Write-Host "`n=== Build Complete ===" -ForegroundColor Cyan
Write-Host "PDFs are in: $outputDir`n"
