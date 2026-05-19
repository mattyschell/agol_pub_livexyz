set HTTP_PROXY=http://xxx.xxx:xxxx
set HTTPS_PROXY=http://xxxx.xxx:xxxx
set http_proxy=%HTTP_PROXY%
set https_proxy=%HTTP_PROXY%
rem if empty all will be mocked
rem add a real name and key to integration test
set LIVEXYZ_SERVICE_ACCOUNT_NAME=
set LIVEXYZ_SERVICE_ACCOUNT_KEY=
rem Optional alternative to service-account auth:
rem set LIVEXYZTOKEN=your-jwt-token
set PYTHON1=C:\Progra~1\ArcGIS\Pro\bin\Python\envs\arcgispro-py3\python.exe
set PYTHON2=C:\Users\%USERNAME%\AppData\Local\Programs\ArcGIS\Pro\bin\Python\envs\arcgispro-py3\python.exe
if exist "%PYTHON1%" (
    set PROPY=%PYTHON1%
) else if exist "%PYTHON2%" (
    set PROPY=%PYTHON2%
) 
CALL %PROPY% -m unittest livexyz_api.test_graphql_fetcher -v