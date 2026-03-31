set LIVEXYZTOKEN="abc....z"
set OUTPUT="data/sample.jsonl"
set LINESPERPAGE=5
set TOTALPAGES=5
rem proxy may be necessary
set HTTP_PROXY=http://xxxxx.xxxx:xxxx
set HTTPS_PROXY=http://xxxxx.xxxxx:xxxx
set http_proxy=%HTTP_PROXY%
set https_proxy=%HTTP_PROXY%
set PYTHON1=C:\Progra~1\ArcGIS\Pro\bin\Python\envs\arcgispro-py3\python.exe
set PYTHON2=C:\Users\%USERNAME%\AppData\Local\Programs\ArcGIS\Pro\bin\Python\envs\arcgispro-py3\python.exe
if exist "%PYTHON1%" (
    set PROPY=%PYTHON1%
) else if exist "%PYTHON2%" (
    set PROPY=%PYTHON2%
) 
CALL %PROPY% livexyz_api/fetch_livexyz.py ^
             --page_count %LINESPERPAGE% ^
             --max_pages %TOTALPAGES% ^
             --output_path %OUTPUT%