set ITEMID=whywasthe6scaredbecause789
set MINROWS=400000
set MAXROWS=500000
set BASEPATH=X:\xxxxxxxxxxxxxx
set NOTIFY=xxxxxxxxx@xxxxx.xxxxxx.xxx
set NOTIFYFROM=xxxxxxxxxxx@xxxx.xxx.xxx
set SMTPFROM=xxxxxxxx.xxxxxxxxx
set PROXY=http://xxxxxxxxx.xxxxxxx:xxxx
rem set if not using ArcGIS Pro auth
rem set NYCMAPSUSER=xxxx.xxx.xxx  
rem set NYCMAPSCREDS=xxxxxx
set AGOLPUB=%BASEPATH%\agol_pub
set AGOLPUBLIVEXYZ=%BASEPATH%\agol_pub_livexyz
set PYTHONPATH=%AGOLPUB%\src\py;%AGOLPUBLIVEXYZ%
set TARGETLOGDIR=%BASEPATH%\geodatabase-scripts\logs\agol_pub_livexyz
set BATLOG=%TARGETLOGDIR%\livexyz-qa-%ITEMID%.log
set PYTHON1=C:\Progra~1\ArcGIS\Pro\bin\Python\envs\arcgispro-py3\python.exe
set PYTHON2=C:\Users\%USERNAME%\AppData\Local\Programs\ArcGIS\Pro\bin\Python\envs\arcgispro-py3\python.exe
if exist "%PYTHON1%" (
    set PROPY=%PYTHON1%
) else if exist "%PYTHON2%" (
    set PROPY=%PYTHON2%
) 
echo starting qa of %ITEMID% on %date% at %time% > %BATLOG%
%PROPY% %AGOLPUBLIVEXYZ%\qa_livexyz.py %ITEMID% %MINROWS% %MAXROWS% && (
    echo. >> %BATLOG% && echo PASSED: qa of LiveXYZ item %ITEMID% on %date% at %time% >> %BATLOG%
) || (
    echo. >> %BATLOG% && echo FAILED: qa of LiveXYZ item %ITEMID% on %date% at %time% >> %BATLOG%
    %PROPY% %AGOLPUB%\notify.py "Failed QA of LiveXYZ item %ITEMID%" %NOTIFY% "qa-livexyz-"
) 
echo. >> %BATLOG% && echo completed qa %ITEMID% on %date% at %time% >> %BATLOG%
set PYTHONPATH=%PYTHONPATH0% 