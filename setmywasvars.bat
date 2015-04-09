@echo off
REM set required variables for environment creation
REM This file must be run in a command window before any of the others will work
REM Since these changes are local to the command window, you must re-run this if you close the window and want to proceed

REM ======= ACTION REQUIRED =======
REM REQUIRED! You must update these to match your system
REM Set to your WAS ROOT. This is the folder where /bin lives. 
REM If you installed to /websphere85/appserver, that is your WAS_ROOT (not just the /websphere85 part)
REM You MUST do this one before running makemyprofile.bat

REM Example: WAS_ROOT=C:/websphere85/appserver
set WAS_ROOT=

set WAS_ADMIN_USER=
set WAS_ADMIN_PASSWORD=

REM AFTER creating your profile, set your NODE name, typically your computer name
REM Set to your WAS Node name (can't be known for sure until after profile is created)

REM Example: MY_WAS_NODE=ADMINIB-3OAPBALNode01
set MY_WAS_NODE=

REM Set JAAS J2C Authentication data
REM Your ID is typically the first 5 letters of your IID followed by 08b/23b

REM Example: MY_SP_ID_08=milla08b
set MY_SP_ID_08=
set MY_SP_PASSWORD_08=
set MY_SP_ID_23=
set MY_SP_PASSWORD_23=

REM ===== END REQUIRED ITEMS ======

REM A couple quick sanity checks...
REM Make sure WAS_ROOT is correct
IF NOT DEFINED WAS_ROOT GOTO NOWASROOT
IF NOT EXIST %WAS_ROOT%\bin GOTO NOWASROOT

REM Make sure password was changed from the default
IF NOT DEFINED MY_SP_PASSWORD_08 GOTO NOPASSWORD
IF NOT DEFINED MY_SP_PASSWORD_23 GOTO NOPASSWORD

REM ======= Optional argument updates =======
REM Change these if the defaults are not acceptable or don't match your system

set DATABASE_PATH=c:/Program Files/IBM/SQLLIB

set WAS_PROFILE_NAME=AppSrv01
set WAS_PROFILE_SERVER_NAME=server1

REM ==========================================

REM Move along, nothing to see here....
REM Used by other scripts to test that this file has been executed in the current environment
set SPNG_PREREQS=TRUE
goto CONFIRM

:NOWASROOT
ECHO .
ECHO ------- STOP RIGHT THERE! -------
ECHO You did not update the WAS_ROOT variable successfully. Nothing will work right until you do.
ECHO It should be directory where /bin exists, so if you installed to c:/spng/websphere85/appserver,
ECHO then your WAS_ROOT is c:/spng/websphere85/appserver because /bin (where WAS executables live)
ECHO is under /appserver, not /websphere85

goto DONE

:NOPASSWORD
ECHO .
ECHO ------- STOP RIGHT THERE! -------
ECHO You did not update the J2C Authentication settings in this file, no point in continuing until you do.
goto DONE

:CONFIRM
ECHO Done, settings are:
call showmywasvars.bat

:DONE
