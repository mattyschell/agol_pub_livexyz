set LIVEXYZTOKEN="abc.123"
rem set OUTPUT="data/all.jsonl"
set OUTPUT="data/all.csv"
set LINESPERPAGE=5000
set TARGETLOGDIR=C:\gis\geodatabase-scripts\logs\agol_pub_livexyz\
set BATLOG=%TARGETLOGDIR%fetch-all-local.log
rem unsure if proxy is necessary
set HTTP_PROXY=http://bcpxy.nycnet:8080
set HTTPS_PROXY=http://bcpxy.nycnet:8080
set http_proxy=%HTTP_PROXY%
set https_proxy=%HTTP_PROXY%
set PYTHON1=C:\Progra~1\ArcGIS\Pro\bin\Python\envs\arcgispro-py3\python.exe
set PYTHON2=C:\Users\%USERNAME%\AppData\Local\Programs\ArcGIS\Pro\bin\Python\envs\arcgispro-py3\python.exe
if exist "%PYTHON1%" (
    set PROPY=%PYTHON1%
) else if exist "%PYTHON2%" (
    set PROPY=%PYTHON2%
) 
echo starting download to %OUTPUT% on %date% at %time% > %BATLOG%
CALL %PROPY% livexyz_api/fetch_livexyz.py ^
             --page_count %LINESPERPAGE% ^
             --output_format csv ^
             --output_path %OUTPUT% ^
             --log_path %TARGETLOGDIR%
echo. >> %BATLOG% && echo completed download to %OUTPUT% on %date% at %time% >> %BATLOG%