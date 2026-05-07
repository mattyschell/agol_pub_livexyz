set LIVEXYZ_SERVICE_ACCOUNT_NAME="your-service-account-name"
set LIVEXYZ_SERVICE_ACCOUNT_KEY="your-65-character-service-account-key"
rem Optional alternative to service-account auth:
rem set LIVEXYZTOKEN="your-jwt-token"
set OUTPUT="X:\XXX\livexyzspecimen.csv"
set LINESPERPAGE=5
set TOTALPAGES=5
set BASEPATH=X:\xxx
set AGOLPUBLIVEXYZ=%BASEPATH%\agol_pub_livexyz
set TARGETLOGDIR=X:\xxx
set BATLOG=%TARGETLOGDIR%\fetchlivexyz-specimen.log
rem unsure if proxy is necessary
set HTTP_PROXY=http://xxx.xxx:xxxx
set HTTPS_PROXY=http://xxx.xxx:xxxx
set http_proxy=%HTTP_PROXY%
set https_proxy=%HTTP_PROXY%
set PYTHON1=C:\Progra~1\ArcGIS\Pro\bin\Python\envs\arcgispro-py3\python.exe
set PYTHON2=C:\Users\%USERNAME%\AppData\Local\Programs\ArcGIS\Pro\bin\Python\envs\arcgispro-py3\python.exe
if exist "%PYTHON1%" (
    set PROPY=%PYTHON1%
) else if exist "%PYTHON2%" (
    set PROPY=%PYTHON2%
) 
echo starting sample download to %OUTPUT% on %date% at %time% > %BATLOG%
CALL %PROPY% %AGOLPUBLIVEXYZ%\livexyz_api\fetch_livexyz.py ^
             --page_count %LINESPERPAGE% ^
             --output_format csv ^
             --max_pages %TOTALPAGES% ^
             --output_path %OUTPUT% ^
             --log_path %TARGETLOGDIR%
echo. >> %BATLOG% && echo completed sample download to %OUTPUT% on %date% at %time% >> %BATLOG%