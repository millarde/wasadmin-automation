@echo off
REM check that our env vars have been set
IF DEFINED SPNG_PREREQS GOTO PROCEED
GOTO NOVARS

:PROCEED
call checkwasstatus.bat

IF "%WAS_SERVER_STARTED%" == "" GOTO SERVERNOTRUNNING

GOTO CONFIGUREIT

:SERVERNOTRUNNING
echo WAS is not running and needs to be started to configure your profile.

set USER_SEZ=
set /P USER_SEZ=Start WAS for you [y/n]? 
if NOT "%USER_SEZ%" == "y" GOTO ABORT

call startmywas

:CONFIGUREIT
call startwasadmin.bat -f J2CAuthEntries.py

echo Patience, please, have to restart the server to force the J2CAuth Entries to get picked up
REM https://developer.ibm.com/answers/questions/173073/test-connection-fail.html

call stopmywas.bat
call startmywas.bat

call startwasadmin.bat -f ConfigureServer.py

GOTO DONE

:NOVARS
echo You have not set the required environment variables, please run setmywasvars.bat
GOTO DONE

:ABORT
echo Okay, some other time then.

:DONE
