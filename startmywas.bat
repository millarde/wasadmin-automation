@echo off
IF DEFINED WAS_ROOT GOTO PROCEED
GOTO NOVARS

:PROCEED

call checkwasstatus.bat

IF "%WAS_SERVER_STARTED%" == "" GOTO SERVERNOTRUNNING

echo Server is already started

GOTO DONE

:SERVERNOTRUNNING

call %WAS_ROOT%\bin\startServer.bat %WAS_PROFILE_SERVER_NAME%

GOTO DONE

:NOVARS
echo You have not set the required environment variables, please run setmywasvars.bat

:DONE
