@echo off
REM faster-whisper transcription wrapper
REM Auto-runs setup if venv doesn't exist

setlocal EnableDelayedExpansion

set "SCRIPT_DIR=%~dp0"
set "SKILL_DIR=%SCRIPT_DIR%.."
set "VENV_PYTHON=%SKILL_DIR%\.venv\Scripts\python.exe"
set "SETUP_SCRIPT=%SKILL_DIR%\setup.ps1"
set "TRANSCRIBE_PY=%SCRIPT_DIR%transcribe.py"

REM Auto-setup if venv doesn't exist
if not exist "%VENV_PYTHON%" (
    echo 🎙️ faster-whisper not set up yet. Running setup...
    echo.
    
    if exist "%SETUP_SCRIPT%" (
        powershell -ExecutionPolicy Bypass -File "%SETUP_SCRIPT%"
        echo.
        
        if not exist "%VENV_PYTHON%" (
            echo ❌ Setup failed. Please check errors above.
            exit /b 1
        )
    ) else (
        echo ❌ Setup script not found: %SETUP_SCRIPT%
        exit /b 1
    )
)

REM Run transcription with all arguments
"%VENV_PYTHON%" "%TRANSCRIBE_PY%" %*
exit /b %ERRORLEVEL%
