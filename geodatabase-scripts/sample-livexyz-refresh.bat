@echo off
call "sample-fetchlivexyz-all.bat"
if errorlevel 1 (
    echo fetchlivexyz-all failed. Exiting.
    exit /b 1
)
call "sample-bluegreen.bat"
