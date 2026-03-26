rem set PROXY=http://xxxx:xxxxx@xxxx.xxxx:xxxx
set LIVEXYZTOKEN="whywasthe6scared?because789"
set PYTHON1=C:\Progra~1\ArcGIS\Pro\bin\Python\envs\arcgispro-py3\python.exe
set PYTHON2=C:\Users\%USERNAME%\AppData\Local\Programs\ArcGIS\Pro\bin\Python\envs\arcgispro-py3\python.exe
if exist "%PYTHON1%" (
    set PROPY=%PYTHON1%
) else if exist "%PYTHON2%" (
    set PROPY=%PYTHON2%
) 
CALL %PROPY% -m unittest livexyz_api.test_graphql_fetcher -v