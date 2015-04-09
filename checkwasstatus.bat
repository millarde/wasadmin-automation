@echo off
REM test to see if server is running so we can stop scripts if it is not

echo Checking server status...
call %WAS_ROOT%\bin\ServerStatus.bat %WAS_PROFILE_SERVER_NAME% -username %WAS_ADMIN_USER% -password %WAS_ADMIN_PASSWORD% > serverstatus.txt

findstr "STARTED" serverstatus.txt > started.txt

REM Clear variable we're about to test
SET WAS_SERVER_STARTED=

SET /p WAS_SERVER_STARTED=<started.txt
