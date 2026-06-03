set BASEPATH=X:\xxx
set GROUPID=xxxxxxxxxxx
set NYCMAPSUSER=xxxxxxxxxx  
set NYCMAPSCREDS=xxxxxxxxx
set TARGETLOGDIR=%BASEPATH%\geodatabase-scripts\logs\agol_pub_livexyz
set REPORTFILE=%TARGETLOGDIR%\livexyz-group-report.csv 
set NOTIFY=xxx@xxx.xxx.xxx
set NOTIFYFROM=xxx@xxx.xxx.xxx
set SMTPFROM=xxxx.xxx
set BATLOG=%TARGETLOGDIR%\livexyz-group-report.log
set HTTP_PROXY=http://xxxxx:xxxx@xxxx.xxxx:xxxx
set HTTPS_PROXY=%HTTP_PROXY%
set PROXY=%HTTP_PROXY%
set PYTHON1=C:\Progra~1\ArcGIS\Pro\bin\Python\envs\arcgispro-py3\python.exe
set PYTHON2=C:\Users\%USERNAME%\AppData\Local\Programs\ArcGIS\Pro\bin\Python\envs\arcgispro-py3\python.exe
if exist "%PYTHON1%" (
    set PROPY=%PYTHON1%
) else if exist "%PYTHON2%" (
    set PROPY=%PYTHON2%
) 
echo writing full group report for %GROUPID% to %REPORTFILE% > %BATLOG%
%PROPY% %BASEPATH%\agol_pub\group_members_report.py %GROUPID% %REPORTFILE%
if errorlevel 1 (
  echo. >> %BATLOG% && echo group members report failed >> %BATLOG%
  echo
  %PROPY% %BASEPATH%\agol_pub\notify.py "Failed to write livexyz group report for %GROUPID%" %NOTIFY% "*"
  set PYTHONPATH=%PYTHONPATH0%
  exit /b 1
)
echo. >> %BATLOG% && echo filtering group report to timestamped csv in %TARGETLOGDIR% >> %BATLOG%
%PROPY% %BASEPATH%\agol_pub_livexyz\filter_group_report.py %REPORTFILE%
if errorlevel 1 (
  echo. >> %BATLOG% && echo filtering group report failed >> %BATLOG%
  echo
  %PROPY% %BASEPATH%\agol_pub\notify.py "Failed to filter livexyz group report for %GROUPID%" %NOTIFY% "*"
  set PYTHONPATH=%PYTHONPATH0%
  exit /b 1
)
%PROPY% %BASEPATH%\agol_pub\notify.py "LiveXYZ Group Report for %GROUPID%" %NOTIFY% "livexyz-group-report-2"
echo. >> %BATLOG% && echo completed livexyz group reporting. >> %BATLOG%
