@echo off
IF DEFINED WAS_ROOT GOTO PROCEED
GOTO NOVARS

:PROCEED
call checkwasstatus.bat

IF "%WAS_SERVER_STARTED%" == "" GOTO SERVERNOTRUNNING

call %WAS_ROOT%\bin\stopServer.bat %WAS_PROFILE_SERVER_NAME% -username %WAS_ADMIN_USER% -password %WAS_ADMIN_PASSWORD%

GOTO DONE

:SERVERNOTRUNNING
echo Server is not running.

GOTO DONE

:NOVARS
echo You have not set the required environment variables, please run setmywasvars.bat

:DONE
