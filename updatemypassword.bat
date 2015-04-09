@echo off
REM check that our env vars have been set
IF DEFINED SPNG_PREREQS GOTO PROCEED
GOTO NOVARS

:PROCEED
call checkwasstatus.bat

IF "%WAS_SERVER_STARTED%" == "" GOTO SERVERNOTRUNNING
GOTO UPDATEAUTH

:SERVERNOTRUNNING
echo WAS is not running and needs to be started to update your profile.

set USER_SEZ=
set /P USER_SEZ=Start WAS for you [y/n]? 
if NOT "%USER_SEZ%" == "y" GOTO ABORT

call startmywas

:UPDATEAUTH
call startwasadmin.bat -f UpdateAuthEntries.py

echo Patience, please, have to restart the server to force the J2CAuth Entries to get picked up
REM https://developer.ibm.com/answers/questions/173073/test-connection-fail.html

call stopmywas.bat
call startmywas.bat

GOTO DONE

:NOVARS
echo You have not set the required environment variables, please run setmywasvars.bat
GOTO DONE

:ABORT
echo Server not started so update cannot be performed at this time.

:DONE
