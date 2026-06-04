@echo off
chcp 65001
echo Installing required packages...
py -m pip install -r requirements.txt
echo.
echo Starting the server... (Please DO NOT close this black window)
py run.py
pause
