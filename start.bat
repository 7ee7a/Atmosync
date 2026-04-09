@echo off
echo Starting AEROS Services...
echo.

echo Starting backend server...
start "AEROS Backend" cmd /k "cd backend && title AEROS Backend && echo Starting FastAPI Backend... && uvicorn main:app --reload"

echo Starting frontend server...
start "AEROS Frontend" cmd /k "cd frontend && title AEROS Frontend && echo Starting Vite Frontend... && npm run dev"

echo Both services have been launched in separate terminal windows!
echo You can now access the frontend at http://localhost:5174 (or whatever port Vite assigned)
echo Closing this launcher...
timeout /t 3 >nul
