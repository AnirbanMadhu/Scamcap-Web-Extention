@echo off
echo Starting ScamCap Backend Server...
echo.
echo Virtual Environment: D:\Coding Junction\Projects\ScamCap Extention\venvs\scamcap
echo Backend Path: D:\Coding Junction\Projects\ScamCap Extention\backend
echo.
echo Server will start at: http://127.0.0.1:8000
echo Press Ctrl+C to stop the server
echo.

cd "D:\Coding Junction\Projects\ScamCap Extention"
"D:\Coding Junction\Projects\ScamCap Extention\venvs\scamcap\Scripts\python.exe" -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload

pause
