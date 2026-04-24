REM refresh a hosted feature layer, then swap the view(s) source
REM statefile tracks which color is next, blue or green
REM if overwrite fails the color returned is unchanged; next time retry
REM if swap fails, same thing: retry the same color and swap
REM if no state file exists, state_manager initializes blue to green
set GREENITEMID=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
set BLUEITEMID=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
set VIEWITEMID1=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
set VIEWITEMID2=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
set ENV=xxx
set BASEPATH=X:\xxx
rem csv source is out of scope for this batch file
set BLUECSV=%BASEPATH%\geodatabase-scripts\data\agol_pub_livexyz\livexyz_source_blue_%ENV%.csv
set GREENCSV=%BASEPATH%\geodatabase-scripts\data\agol_pub_livexyz\livexyz_source_green_%ENV%.csv
rem set these if not authenticating to ArcGIS Online with ArcGIS Pro
set NYCMAPSUSER=xxxxxxx.xxx.xxxxxxx
set NYCMAPSCREDS=xxxxxxxxxxxxxxxxxxxxxxxxxxx
set NOTIFY=xxxxxxxxxx@xxx.xxx.xxx
set NOTIFYFROM=xxxxxxxxxx@xxx.xxx.xxx
set SMTPFROM=xxxxxxx.xxxxxxxx
set PROXY=http://xxxxx.xxxxx:xxxx
set HTTP_PROXY=%PROXY%
set HTTPS_PROXY=%PROXY%
REM assumes manual creation of statefile path
set STATEFILE=%BASEPATH%\geodatabase-scripts\data\agol_pub_livexyz\statefiles\livexyz.json
set PYTHON1=C:\Progra~1\ArcGIS\Pro\bin\Python\envs\arcgispro-py3\python.exe
set PYTHON2=C:\Users\%USERNAME%\AppData\Local\Programs\ArcGIS\Pro\bin\Python\envs\arcgispro-py3\python.exe
if exist "%PYTHON1%" (
    set PROPY=%PYTHON1%
) else if exist "%PYTHON2%" (
    set PROPY=%PYTHON2%
) 
set AGOLPUB=%BASEPATH%\agol_pub
if "%TARGET_COLOR%"=="" (
  REM Get target (will be "green" or "blue")
  for /f "tokens=*" %%A in (
    '%PROPY% %AGOLPUB%\src\py\state_manager.py get-target %STATEFILE%'
  ) do set TARGET_COLOR=%%A
) else (
  REM TARGET_COLOR was supplied by caller (for example sample-fetchlivexyz-all.bat)
)
echo Target color: %TARGET_COLOR%
if "%TARGET_COLOR%"=="green" (
  set TARGETITEMID=%GREENITEMID%
  set CSV=%GREENCSV%
) else (
  set TARGETITEMID=%BLUEITEMID%
  set CSV=%BLUECSV%
)
set TARGETLOGDIR=%BASEPATH%\geodatabase-scripts\logs\agol_pub_livexyz
set BATLOG=%TARGETLOGDIR%\livexyz-bluegreen_to_%TARGET_COLOR%.log
set PYTHONPATH0=%PYTHONPATH%
set PYTHONPATH=%AGOLPUB%\src\py;%PYTHONPATH%
echo starting swap to %TARGET_COLOR% on %date% at %time% > %BATLOG%
%PROPY% %AGOLPUB%\replace-hfl.py overwrite ^
                                 %TARGETITEMID% ^
                                 %CSV%
if errorlevel 1 (
  %PROPY% %AGOLPUB%\src\py\state_manager.py set-failed %STATEFILE%
  echo. >> %BATLOG% && echo Overwrite failed on %date% at %time%. Not swapping view >> %BATLOG%
  echo 
  %PROPY% %AGOLPUB%\notify.py "Failed to overwrite %TARGET_COLOR% HFL %TARGETITEMID%" %NOTIFY% "replace-hfl-%TARGETITEMID%"
  set PYTHONPATH=%PYTHONPATH0%
  exit /b 1
)
echo. >> %BATLOG% && echo Swapping view %VIEWITEMID1% to point to %TARGETITEMID% >> %BATLOG%
%PROPY% %AGOLPUB%\replace-hfl.py swap-view ^
                                 %VIEWITEMID1% ^
                                 0 ^
                                 %TARGETITEMID%
if errorlevel 1 (
  %PROPY% %AGOLPUB%\src\py\state_manager.py set-failed %STATEFILE%
  echo. >> %BATLOG% && echo Swap failed on %date% at %time%. Investigate and decide rollback. >> %BATLOG%
  echo 
  %PROPY% %AGOLPUB%\notify.py "Failed to swap view %VIEWITEMID1% to %TARGET_COLOR%" %NOTIFY% "replace-hfl-%VIEWITEMID1%"
  set PYTHONPATH=%PYTHONPATH0%
  exit /b 1
)
echo. >> %BATLOG% && echo Swapping view %VIEWITEMID2% to point to %TARGETITEMID% >> %BATLOG%
%PROPY% %AGOLPUB%\replace-hfl.py swap-view ^
                                 %VIEWITEMID2% ^
                                 0 ^
                                 %TARGETITEMID%
if errorlevel 1 (
  %PROPY% %AGOLPUB%\src\py\state_manager.py set-failed %STATEFILE%
  echo. >> %BATLOG% && echo Swap failed on %date% at %time%. Investigate and decide rollback. >> %BATLOG%
  echo 
  %PROPY% %AGOLPUB%\notify.py "Failed to swap view %VIEWITEMID2% to %TARGET_COLOR%" %NOTIFY% "replace-hfl-%VIEWITEMID2%"
  set PYTHONPATH=%PYTHONPATH0%
  exit /b 1
)
%PROPY% %AGOLPUB%\src\py\state_manager.py set-success %STATEFILE% %TARGET_COLOR%
echo. >> %BATLOG% && echo Success: %TARGET_COLOR% %TARGETITEMID% overwritten and views %VIEWITEMID1% and %VIEWITEMID2% now swapped to %TARGET_COLOR%. >> %BATLOG%
set PYTHONPATH=%PYTHONPATH0%