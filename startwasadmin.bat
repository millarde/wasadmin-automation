@echo off
REM check that our env vars have been set
IF DEFINED SPNG_PREREQS GOTO PROCEED
GOTO NOVARS

:PROCEED
call %WAS_ROOT%\bin\wsadmin.bat -p wsadmin.properties -user %WAS_ADMIN_USER% -password %WAS_ADMIN_PASSWORD% %1 %2 %3 %4 %5 %6 %7 %8

GOTO DONE

:NOVARS
echo You have not set the required environment variables, please run setmywasvars.bat

:DONE
