::::::::::::::::::::::::::::::::::
:: Script to build Tifinity exe ::
::::::::::::::::::::::::::::::::::

@echo off
SETLOCAL

IF EXIST .\venv_32\ ( CALL :Build 32 ) ELSE ( echo "Requires virtual environment (named venv_32) with pyinstall and numpy dependencies installed" )
IF EXIST .\venv_64\ ( CALL :Build 64 ) ELSE ( echo "Requires virtual environment (named venv_64) with pyinstall and numpy dependencies installed" )
EXIT /B %ERRORLEVEL%
:::::::::::::::::::::::::::::::::::::::::

:Build
  SET bitness=%~1
  echo Building %bitness%-bit Tifinity
  :: switch to correct bitness venv
  CALL venv_%bitness%\Scripts\activate.bat

  :: run pyinstaller to build
  pyinstaller --workpath=build\pyi.win%bitness% --distpath=dist\win%bitness% -y tifinity-onefile.spec

  :: switch back out of venv  
  CALL venv_%bitness%\Scripts\deactivate.bat
  echo Finished building %bitness%-bit Tifinity
  echo.
  EXIT /B 0

:End
