set LIVEXYZ_SERVICE_ACCOUNT_NAME="your-service-account-name"
set LIVEXYZ_SERVICE_ACCOUNT_KEY="your-65-character-service-account-key"
rem Optional alternative to service-account auth:
rem set LIVEXYZTOKEN="your-jwt-token"
set BASEPATH=X:\xxx
set AGOLPUB=%BASEPATH%\agol_pub
set STATEFILE=%BASEPATH%\geodatabase-scripts\data\agol_pub_livexyz\statefiles\livexyz.json
set TARGET_COLOR=
set LINESPERPAGE=5000
set TARGETLOGDIR=%BASEPATH%\geodatabase-scripts\logs\agol_pub_livexyz\
set BATLOG=%TARGETLOGDIR%fetch-all.log
set ENV=xxx
set BLUEOUTPUT=%BASEPATH%\geodatabase-scripts\data\agol_pub_livexyz\livexyz_source_blue_%ENV%.csv
set GREENOUTPUT=%BASEPATH%\geodatabase-scripts\data\agol_pub_livexyz\livexyz_source_green_%ENV%.csv
set OUTPUT=
set NOTIFY=xxx@xxx.xxx.xxx
set NOTIFYFROM=xxx@xxx.xxx.xxx
set SMTPFROM=xxxxx.xxxxx
rem unsure if proxy is necessary
set HTTP_PROXY=http://xxxx.xxxx:xxxx
set HTTPS_PROXY=%HTTP_PROXY%
set http_proxy=%HTTP_PROXY%
set https_proxy=%HTTP_PROXY%
set PYTHON1=C:\Progra~1\ArcGIS\Pro\bin\Python\envs\arcgispro-py3\python.exe
set PYTHON2=C:\Users\%USERNAME%\AppData\Local\Programs\ArcGIS\Pro\bin\Python\envs\arcgispro-py3\python.exe
if exist "%PYTHON1%" (
    set PROPY=%PYTHON1%
) else if exist "%PYTHON2%" (
    set PROPY=%PYTHON2%
) 
for /f "tokens=*" %%A in (
  '%PROPY% %AGOLPUB%\src\py\state_manager.py get-target %STATEFILE%'
) do set TARGET_COLOR=%%A
if "%TARGET_COLOR%"=="green" (
    set OUTPUT=%GREENOUTPUT%
) else (
    set TARGET_COLOR=blue
    set OUTPUT=%BLUEOUTPUT%
)
echo starting download to %OUTPUT% on %date% at %time% > %BATLOG%
CALL %PROPY% %BASEPATH%\agol_pub_livexyz\livexyz_api\fetch_livexyz.py ^
             --page_count %LINESPERPAGE% ^
             --output_format csv ^
             --output_path %OUTPUT% ^
             --log_path %TARGETLOGDIR%
if %ERRORLEVEL% NEQ 0 (
    echo. >> %BATLOG%
    echo fetchlivexyz-all failed >> %BATLOG%
    %PROPY% %BASEPATH%\agol_pub\notify.py "LiveXYZ data fetch failed (%ENV%)" %NOTIFY% fetch_livexyz_ %TARGETLOGDIR% %NOTIFYFROM% %SMTPFROM%
    EXIT /B 1
) 
rem testing success notification
rem %PROPY% %BASEPATH%\agol_pub\notify.py "LiveXYZ data fetch success (%ENV%)" %NOTIFY% fetch_livexyz_ %TARGETLOGDIR% %NOTIFYFROM% %SMTPFROM%
echo. >> %BATLOG% && echo completed download to %OUTPUT% (%TARGET_COLOR%) on %date% at %time% >> %BATLOG%