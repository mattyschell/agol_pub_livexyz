@echo off
call "sample-fetchlivexyz-all.bat"
if errorlevel 1 (
    echo livexyz-fetch failed. Exiting.
    exit /b 1
)
call "sample-bluegreen.bat"
if errorlevel 1 (
    echo livexyz-bluegreen failed. Exiting.
    exit /b 1
)
call "sample-livexyz-qa.bat"
if errorlevel 1 (
    echo livexyz-qa-alltime failed. Exiting.
    exit /b 1
)
rem probably 2 versions of QA here
rem call "D:\gis\geodatabase-scripts\livexyz-qa-today-stg.bat"
rem if errorlevel 1 (
rem     echo livexyz-qa-alltime failed. Exiting.
rem     exit /b 1
rem )
