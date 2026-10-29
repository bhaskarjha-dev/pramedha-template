#!/usr/bin/env pwsh
# Resume Cascade Build Script (Windows)
# Assembles all variants from master.yaml and renders to PDF.

$ErrorActionPreference = "Continue"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8
$env:PYTHONIOENCODING = "utf-8"
$env:PYTHONUTF8 = "1"
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
$repoRoot = Split-Path -Parent (Split-Path -Parent $scriptDir)

Write-Host "`n=== Resume Cascade Build ===" -ForegroundColor Cyan

# Use the repository's virtual environment (README Quick Start), else the active one, else python or py
$repoVenv = Join-Path $repoRoot ".venv\Scripts\python.exe"
if (Test-Path $repoVenv) {
    $pythonExe = $repoVenv
} elseif ($env:VIRTUAL_ENV -and (Test-Path (Join-Path $env:VIRTUAL_ENV "Scripts\python.exe"))) {
    $pythonExe = Join-Path $env:VIRTUAL_ENV "Scripts\python.exe"
} elseif (Get-Command python -ErrorAction SilentlyContinue) {
    $pythonExe = "python"
} elseif (Get-Command py -ErrorAction SilentlyContinue) {
    $pythonExe = "py"
} else {
    Write-Host "Python not found. Install Python 3.12+ and create .venv as README Quick Start shows." -ForegroundColor Red
    exit 1
}

# Step 1: Assemble. generated\ holds only build output: clear it so removed or renamed variants aren't rendered again
Write-Host "`n[1/2] Assembling variants..." -ForegroundColor Yellow
Remove-Item "$scriptDir\generated\*.yaml" -ErrorAction SilentlyContinue
& $pythonExe "$scriptDir\assemble.py"
if ($LASTEXITCODE -ne 0) {
    Write-Host "Assembly failed!" -ForegroundColor Red
    exit 1
}

# Step 2: Render each generated YAML to PDF
Write-Host "`n[2/2] Rendering PDFs..." -ForegroundColor Yellow
$generatedDir = "$scriptDir\generated"
$outputDir = "$scriptDir\output"
New-Item -ItemType Directory -Force -Path $outputDir | Out-Null

$yamlFiles = @(Get-ChildItem "$generatedDir\*.yaml" -ErrorAction SilentlyContinue)
if ($yamlFiles.Count -eq 0) {
    Write-Host "  Nothing to render: no files in $generatedDir." -ForegroundColor Red
    Write-Host "  Run python tools\resume\sync.py, copy tools\resume\variants\_template.yaml to tools\resume\variants\A_Role.yaml, select bullets, then run this script again." -ForegroundColor Yellow
    Write-Host "`n=== Build FAILED: no PDF was rendered ===" -ForegroundColor Red
    exit 1
}

& $pythonExe -m rendercv --version *> $null
if ($LASTEXITCODE -eq 0) {
    $useModule = $true
} elseif (Get-Command rendercv -ErrorAction SilentlyContinue) {
    $useModule = $false
} else {
    $pyVersion = & $pythonExe --version
    Write-Host "  RenderCV not found. It needs Python 3.12+ (this is $pyVersion)." -ForegroundColor Red
    Write-Host "  Install it in the virtual environment: python -m pip install -r tools\resume\requirements.txt" -ForegroundColor Yellow
    Write-Host "  Generated YAMLs are ready in: $generatedDir" -ForegroundColor Cyan
    Write-Host "`n=== Build FAILED: no PDF was rendered ===" -ForegroundColor Red
    exit 1
}

$failed = 0
Push-Location $scriptDir
try {
    foreach ($file in $yamlFiles) {
        $name = $file.BaseName
        Write-Host "  Rendering $name..." -ForegroundColor Gray
        $variantOutputDir = Join-Path $outputDir $name
        New-Item -ItemType Directory -Force -Path $variantOutputDir | Out-Null
        if ($useModule) {
            & $pythonExe -m rendercv render $file.FullName -o $variantOutputDir
        } else {
            rendercv render $file.FullName -o $variantOutputDir
        }
        $renderCode = $LASTEXITCODE
        $generatedPdf = Get-ChildItem "$variantOutputDir\*.pdf" -ErrorAction SilentlyContinue | Select-Object -First 1
        if ($renderCode -ne 0 -or -not $generatedPdf) {
            Write-Host "  ❌ Failed: $name" -ForegroundColor Red
            $failed++
        } else {
            Copy-Item -Path $generatedPdf.FullName -Destination "$outputDir\$name.pdf" -Force
            Write-Host "  ✅ $name -> output\$name.pdf" -ForegroundColor Green
        }
    }
} finally {
    Pop-Location
}

if ($failed -gt 0) {
    Write-Host "`n=== Build FAILED: $failed file(s) did not render ===" -ForegroundColor Red
    exit 1
}
Write-Host "`n=== Build Complete ===" -ForegroundColor Cyan
Write-Host "PDFs are in: $outputDir`n"
