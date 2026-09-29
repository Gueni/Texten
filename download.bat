
@echo off

set /P DEST="Please Enter The Path Where You Want To Download The Wheel libraries : "

echo Downloading all libraries in requirements.txt into /Wheelhouse directory...
python -m pip download --no-cache-dir -i https://nexus.bmwgroup.net/repository/pypi/simple -r Script\assets\Configuration\requirements.txt -d "%DEST%"

echo.
echo Libraries .whl packages have been downloaded to : "%DEST%"
pause