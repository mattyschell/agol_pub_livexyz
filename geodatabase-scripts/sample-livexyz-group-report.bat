set BASEPATH=X:\xxx
set GROUPID=xxxxxxxxxxxxxxxxx
set NYCMAPSUSER=xx.xx.xx  
set NYCMAPSCREDS=xxxx
set REPORTDIR=X:\xxx
set REPORTFILE=%REPORTDIR%\livexyz-group-report.csv 
set NOTIFY=xxx@xxx.xxx.xxx
set NOTIFYFROM=xxx@xxx.xxx.xxx
set SMTPFROM=xxxx.xxx
set HTTP_PROXY=http://xxx:xxx@xxx.xxx:xxx
set HTTPS_PROXY=%HTTP_PROXY%
set PROXY=%HTTP_PROXY%
set PYTHON1=C:\Progra~1\ArcGIS\Pro\bin\Python\envs\arcgispro-py3\python.exe
set PYTHON2=C:\Users\%USERNAME%\AppData\Local\Programs\ArcGIS\Pro\bin\Python\envs\arcgispro-py3\python.exe
if exist "%PYTHON1%" (
    set PROPY=%PYTHON1%
) else if exist "%PYTHON2%" (
    set PROPY=%PYTHON2%
) 
%PROPY% %BASEPATH%\agol_pub\group_members_report.py %GROUPID% %REPORTFILE%
%PROPY% %BASEPATH%\agol_pub_livexyz\filter_group_report.py %REPORTFILE%