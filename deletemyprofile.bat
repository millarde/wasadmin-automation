@echo off
IF DEFINED SPNG_PREREQS GOTO PROCEED
GOTO NOVARS

:PROCEED
call checkwasstatus.bat

IF "%WAS_SERVER_STARTED%" == "" GOTO SERVERNOTRUNNING

set USER_SEZ=
set /P USER_SEZ=Need to stop WAS in order to delete profile. Okay [y/n]? 
if NOT "%USER_SEZ%" == "y" GOTO ABORT
call stopmywas

:SERVERNOTRUNNING
call %WAS_ROOT%\bin\manageprofiles.bat -delete -profileName %WAS_PROFILE_NAME%

echo About to delete profile directory but want you to confirm you have logs and anything else you need first...
rmdir /s "%WAS_ROOT%\profiles\%WAS_PROFILE_NAME%"

GOTO DONE

:NOVARS
echo You have not set the required environment variables, please run setmywasvars.bat
GOTO DONE

:ABORT
echo Server not stopped, profile not deleted.

:DONE
