@echo off
REM test to see if server is running 

IF DEFINED WAS_ROOT GOTO PROCEED
GOTO NOVARS

:PROCEED
call checkwasstatus.bat

IF "%WAS_SERVER_STARTED%" == "" GOTO SERVERNOTRUNNING

echo Cool, WAS is running.
GOTO DONE

:SERVERNOTRUNNING
echo WAS server is not started!

GOTO DONE

:NOVARS
echo You have not set the required environment variables, please run setmywasvars.bat

:DONE
