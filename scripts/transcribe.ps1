#Requires -Version 5.1
<#
.SYNOPSIS
    Transcribe audio using faster-whisper
.DESCRIPTION
    Wrapper script that activates venv and runs the Python transcriber.
    Auto-runs setup if venv doesn't exist.
.EXAMPLE
    .\transcribe.ps1 audio.mp3
    .\transcribe.ps1 audio.wav -Model large-v3-turbo -Language en
    .\transcribe.ps1 audio.mp3 -Json -WordTimestamps
#>

param(
    [Parameter(Position=0, Mandatory=$true)]
    [string]$Audio,
    
    [Alias("m")]
    [string]$Model,
    
    [Alias("l")]
    [string]$Language,
    
    [switch]$WordTimestamps,
    
    [int]$BeamSize,
    
    [switch]$Vad,
    
    [Alias("j")]
    [switch]$Json,
    
    [Alias("o")]
    [string]$Output,
    
    [string]$Device,
    
    [string]$ComputeType,
    
    [Alias("q")]
    [switch]$Quiet,
    
    # Pass-through for any other args
    [Parameter(ValueFromRemainingArguments=$true)]
    [string[]]$RemainingArgs
)

$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$SkillDir = Split-Path -Parent $ScriptDir
$VenvPython = Join-Path $SkillDir ".venv\Scripts\python.exe"
$SetupScript = Join-Path $SkillDir "setup.ps1"
$TranscribePy = Join-Path $ScriptDir "transcribe.py"

# Auto-setup if venv doesn't exist
if (-not (Test-Path $VenvPython)) {
    Write-Host "🎙️ faster-whisper not set up yet. Running setup..." -ForegroundColor Cyan
    Write-Host ""
    
    if (Test-Path $SetupScript) {
        & $SetupScript
        Write-Host ""
        
        if (-not (Test-Path $VenvPython)) {
            Write-Host "❌ Setup failed. Please check errors above." -ForegroundColor Red
            exit 1
        }
    } else {
        Write-Host "❌ Setup script not found: $SetupScript" -ForegroundColor Red
        exit 1
    }
}

# Build arguments for Python script
$pyArgs = @($TranscribePy, $Audio)

if ($Model) { $pyArgs += "--model", $Model }
if ($Language) { $pyArgs += "--language", $Language }
if ($WordTimestamps) { $pyArgs += "--word-timestamps" }
if ($BeamSize) { $pyArgs += "--beam-size", $BeamSize }
if ($Vad) { $pyArgs += "--vad" }
if ($Json) { $pyArgs += "--json" }
if ($Output) { $pyArgs += "--output", $Output }
if ($Device) { $pyArgs += "--device", $Device }
if ($ComputeType) { $pyArgs += "--compute-type", $ComputeType }
if ($Quiet) { $pyArgs += "--quiet" }
if ($RemainingArgs) { $pyArgs += $RemainingArgs }

# Run transcription
& $VenvPython @pyArgs
exit $LASTEXITCODE
