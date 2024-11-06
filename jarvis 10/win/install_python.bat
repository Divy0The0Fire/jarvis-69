@echo off
REM Set Python version and installer URL
set PYTHON_VERSION=3.10.10
set PYTHON_INSTALLER=https://www.python.org/ftp/python/%PYTHON_VERSION%/python-%PYTHON_VERSION%-amd64.exe
set INSTALL_DIR=C:\Python%PYTHON_VERSION:~0,1%

REM Download the Python installer
echo Downloading Python %PYTHON_VERSION%...
curl -o python-installer.exe %PYTHON_INSTALLER%

REM Install Python
echo Installing Python %PYTHON_VERSION%...
start /wait python-installer.exe /quiet InstallAllUsers=1 PrependPath=1 TargetDir=%INSTALL_DIR%

REM Clean up
del python-installer.exe

echo Python %PYTHON_VERSION% installed successfully!
pause
