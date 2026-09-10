@echo off
title Debt Manager API & UI
echo ========================================================
echo    Qarzlarni Hisoblash va Monitoring Qilish Tizimi
echo ========================================================
echo.
echo Server ishga tushirilmoqda...
echo.
echo Brauzerda ochish uchun:
echo    Web Ilova:    http://127.0.0.1:8000
echo    Swagger API:  http://127.0.0.1:8000/docs
echo.
echo To'xtatish uchun CTRL+C bosing.
echo ========================================================
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
pause

