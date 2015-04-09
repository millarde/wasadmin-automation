@echo off
IF NOT DEFINED SPNG_PREREQS GOTO NOVARS

call %WAS_ROOT%\bin\manageprofiles.bat -create -profileName %WAS_PROFILE_NAME% -profilePath "%WAS_ROOT%/profiles/%WAS_PROFILE_NAME%" -templatePath "%WAS_ROOT%/profileTemplates/default" -serverName %WAS_PROFILE_SERVER_NAME% -enableAdminSecurity true -adminUserName %WAS_ADMIN_USER% -adminPassword %WAS_ADMIN_PASSWORD%

set USER_SEZ=
set /P USER_SEZ=Start WAS for you [y/n]? 
if NOT "%USER_SEZ%" == "y" GOTO ABORT

call startmywas

GOTO DONE

:NOVARS
echo You have not set the required environment variables, please run setmywasvars.bat

GOTO DONE

:ABORT
echo WAS not started.

:DONE

