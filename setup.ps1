#Requires -Version 5.1
<#
.SYNOPSIS
    faster-whisper skill setup for Windows
.DESCRIPTION
    Creates venv and installs dependencies (with GPU support where available).
    Auto-installs Python and ffmpeg if missing (via winget).
#>

param(
    [switch]$SkipPrereqs,
    [switch]$Force
)

$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"  # Speed up Invoke-WebRequest

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$VenvDir = Join-Path $ScriptDir ".venv"
$RequirementsFile = Join-Path $ScriptDir "requirements.txt"

Write-Host "🎙️ Setting up faster-whisper skill..." -ForegroundColor Cyan
Write-Host ""

# ============================================================================
# Helper Functions
# ============================================================================

function Test-Command {
    param([string]$Command)
    $null = Get-Command $Command -ErrorAction SilentlyContinue
    return $?
}

function Test-WinGet {
    return Test-Command "winget"
}

function Install-WithWinget {
    param(
        [string]$PackageId,
        [string]$FriendlyName
    )
    
    Write-Host "📦 Installing $FriendlyName via winget..." -ForegroundColor Yellow
    
    try {
        $result = winget install --id $PackageId --accept-source-agreements --accept-package-agreements --silent 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✓ $FriendlyName installed" -ForegroundColor Green
            # Refresh PATH
            $env:Path = [System.Environment]::GetEnvironmentVariable("Path", "Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path", "User")
            return $true
        } else {
            Write-Host "⚠️  winget install returned: $LASTEXITCODE" -ForegroundColor Yellow
            return $false
        }
    } catch {
        Write-Host "❌ Failed to install $FriendlyName`: $_" -ForegroundColor Red
        return $false
    }
}

function Get-PythonCommand {
    # Try various Python commands
    foreach ($cmd in @("python", "python3", "py")) {
        if (Test-Command $cmd) {
            try {
                $version = & $cmd --version 2>&1
                if ($version -match "Python (\d+)\.(\d+)") {
                    $major = [int]$Matches[1]
                    $minor = [int]$Matches[2]
                    if ($major -ge 3 -and $minor -ge 10) {
                        return $cmd
                    }
                }
            } catch {
                continue
            }
        }
    }
    return $null
}

function Test-NvidiaGPU {
    # Check for NVIDIA GPU via nvidia-smi
    $nvidiaSmi = $null
    
    # Common paths for nvidia-smi
    $searchPaths = @(
        "nvidia-smi",
        "C:\Windows\System32\nvidia-smi.exe",
        "C:\Program Files\NVIDIA Corporation\NVSMI\nvidia-smi.exe"
    )
    
    foreach ($path in $searchPaths) {
        if (Test-Command $path) {
            $nvidiaSmi = $path
            break
        }
        if (Test-Path $path) {
            $nvidiaSmi = $path
            break
        }
    }
    
    if ($nvidiaSmi) {
        try {
            $gpuName = & $nvidiaSmi --query-gpu=name --format=csv,noheader 2>$null | Select-Object -First 1
            if ($gpuName) {
                return @{ Available = $true; Name = $gpuName.Trim() }
            }
        } catch {
            # nvidia-smi exists but failed
        }
    }
    
    return @{ Available = $false; Name = $null }
}

# ============================================================================
# Prerequisites Check/Install
# ============================================================================

if (-not $SkipPrereqs) {
    Write-Host "Checking prerequisites..." -ForegroundColor Cyan
    Write-Host ""
    
    $hasWinget = Test-WinGet
    if (-not $hasWinget) {
        Write-Host "⚠️  winget not found. Auto-install of prerequisites disabled." -ForegroundColor Yellow
        Write-Host "   Install App Installer from Microsoft Store for auto-install support." -ForegroundColor Yellow
        Write-Host ""
    }
    
    # Check Python
    $pythonCmd = Get-PythonCommand
    if (-not $pythonCmd) {
        Write-Host "❌ Python 3.10+ not found" -ForegroundColor Red
        
        if ($hasWinget) {
            $installed = Install-WithWinget -PackageId "Python.Python.3.12" -FriendlyName "Python 3.12"
            if ($installed) {
                # Re-check after install
                $pythonCmd = Get-PythonCommand
                if (-not $pythonCmd) {
                    Write-Host "⚠️  Python installed but not in PATH. Please restart your terminal." -ForegroundColor Yellow
                    Write-Host "   Then run this setup script again." -ForegroundColor Yellow
                    exit 1
                }
            } else {
                Write-Host ""
                Write-Host "Please install Python 3.10+ manually from https://python.org" -ForegroundColor Yellow
                Write-Host "Make sure to check 'Add Python to PATH' during installation." -ForegroundColor Yellow
                exit 1
            }
        } else {
            Write-Host "Please install Python 3.10+ from https://python.org" -ForegroundColor Yellow
            Write-Host "Make sure to check 'Add Python to PATH' during installation." -ForegroundColor Yellow
            exit 1
        }
    }
    
    $pythonVersion = & $pythonCmd --version 2>&1
    Write-Host "✓ $pythonVersion" -ForegroundColor Green
    
    # Check ffmpeg
    if (-not (Test-Command "ffmpeg")) {
        Write-Host "⚠️  ffmpeg not found" -ForegroundColor Yellow
        
        if ($hasWinget) {
            $installed = Install-WithWinget -PackageId "Gyan.FFmpeg" -FriendlyName "ffmpeg"
            if (-not $installed) {
                Write-Host "   ffmpeg is optional but recommended for audio format support." -ForegroundColor Yellow
                Write-Host "   Install manually from https://ffmpeg.org or via: winget install Gyan.FFmpeg" -ForegroundColor Yellow
            }
        } else {
            Write-Host "   ffmpeg is optional but recommended for audio format support." -ForegroundColor Yellow
            Write-Host "   Install from https://ffmpeg.org or via: winget install Gyan.FFmpeg" -ForegroundColor Yellow
        }
    } else {
        Write-Host "✓ ffmpeg found" -ForegroundColor Green
    }
    
    Write-Host ""
}

# ============================================================================
# GPU Detection
# ============================================================================

Write-Host "Detecting GPU..." -ForegroundColor Cyan
$gpu = Test-NvidiaGPU

if ($gpu.Available) {
    Write-Host "✓ NVIDIA GPU detected: $($gpu.Name)" -ForegroundColor Green
} else {
    Write-Host "ℹ️  No NVIDIA GPU detected (CPU mode)" -ForegroundColor Yellow
}
Write-Host ""

# ============================================================================
# Virtual Environment Setup
# ============================================================================

$pythonCmd = Get-PythonCommand
if (-not $pythonCmd) {
    Write-Host "❌ Python not found after prereq check. Please restart terminal and try again." -ForegroundColor Red
    exit 1
}

$venvPython = Join-Path $VenvDir "Scripts\python.exe"
$venvPip = Join-Path $VenvDir "Scripts\pip.exe"

if ((Test-Path $VenvDir) -and -not $Force) {
    Write-Host "✓ Virtual environment exists" -ForegroundColor Green
} else {
    if ($Force -and (Test-Path $VenvDir)) {
        Write-Host "Removing existing venv (--Force)..." -ForegroundColor Yellow
        Remove-Item -Recurse -Force $VenvDir
    }
    
    Write-Host "Creating virtual environment..." -ForegroundColor Cyan
    
    # Check for uv
    if (Test-Command "uv") {
        & uv venv $VenvDir --python $pythonCmd
    } else {
        & $pythonCmd -m venv $VenvDir
    }
    
    if (-not (Test-Path $venvPython)) {
        Write-Host "❌ Failed to create virtual environment" -ForegroundColor Red
        exit 1
    }
    
    Write-Host "✓ Virtual environment created" -ForegroundColor Green
}
Write-Host ""

# ============================================================================
# Install Dependencies
# ============================================================================

Write-Host "Installing faster-whisper..." -ForegroundColor Cyan

if (Test-Command "uv") {
    & uv pip install --python $venvPython -r $RequirementsFile
} else {
    & $venvPython -m pip install --upgrade pip 2>$null
    & $venvPython -m pip install -r $RequirementsFile
}

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to install dependencies" -ForegroundColor Red
    exit 1
}
Write-Host "✓ Dependencies installed" -ForegroundColor Green
Write-Host ""

# ============================================================================
# Install PyTorch (with CUDA if available)
# ============================================================================

if ($gpu.Available) {
    Write-Host "🚀 Installing PyTorch with CUDA support..." -ForegroundColor Cyan
    Write-Host "   This enables 10-20x faster transcription on your GPU." -ForegroundColor Gray
    Write-Host ""
    
    if (Test-Command "uv") {
        & uv pip install --python $venvPython torch --index-url https://download.pytorch.org/whl/cu121
    } else {
        & $venvPython -m pip install torch --index-url https://download.pytorch.org/whl/cu121
    }
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ PyTorch with CUDA installed" -ForegroundColor Green
    } else {
        Write-Host "⚠️  CUDA PyTorch install failed, falling back to CPU" -ForegroundColor Yellow
        & $venvPython -m pip install torch
    }
} else {
    Write-Host "Installing PyTorch (CPU)..." -ForegroundColor Cyan
    
    if (Test-Command "uv") {
        & uv pip install --python $venvPython torch
    } else {
        & $venvPython -m pip install torch
    }
    
    Write-Host "✓ PyTorch installed" -ForegroundColor Green
}
Write-Host ""

# ============================================================================
# Done!
# ============================================================================

Write-Host "✅ Setup complete!" -ForegroundColor Green
Write-Host ""

if ($gpu.Available) {
    Write-Host "🚀 GPU acceleration enabled — expect ~20x realtime speed" -ForegroundColor Cyan
} else {
    Write-Host "💻 CPU mode — transcription will be slower but functional" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Usage:" -ForegroundColor Cyan
Write-Host "  .\scripts\transcribe.cmd audio.mp3" -ForegroundColor White
Write-Host "  .\scripts\transcribe.ps1 audio.mp3" -ForegroundColor White
Write-Host ""
Write-Host "First run will download the model (~756MB for distil-large-v3)." -ForegroundColor Gray
