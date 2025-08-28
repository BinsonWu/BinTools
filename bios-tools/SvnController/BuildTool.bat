@echo off
REM Change directory to the location of this batch file (where SvnController.py is located)
cd /d "%~dp0"
set "WORK_DIR=%~dp0"

REM Install PyInstaller
python -m pip install pyinstaller

REM Use PyInstaller to create a standalone executable (one file)
python -m PyInstaller --onefile --add-binary "C:\Python312\python312.dll;." --add-binary "C:\Windows\System32\msvcrt.dll;." SvnController.py

echo WORK_DIR %WORK_DIR%

REM Construct the absolute path for the generated executable in the dist folder
set "SRC_EXE=%WORK_DIR%dist\SvnController.exe"

copy /Y "%SRC_EXE%" "%WORK_DIR%SvnController.exe"

REM Copy the executable to a directory in the system PATH (requires admin privileges)
copy /Y "%SRC_EXE%" "C:\Windows\System32\SvnController.exe"

REM Set file permissions to grant full access to Everyone
icacls "C:\Windows\System32\SvnController.exe" /grant Everyone:F

echo Build completed
