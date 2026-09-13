@echo off
REM Cấu hình API Key và Gmail
set GEMINI_API_KEY=YOUR_GEMINI_API_KEY_HERE
set GMAIL_USER=YOUR_EMAIL@gmail.com
set GMAIL_APP_PASSWORD=YOUR_16_CHAR_APP_PASSWORD

:: Tìm và tắt server cũ đang chạy ở cổng 5000 (nếu có)
for /f "tokens=5" %%a in ('netstat -aon ^| find ":5000" ^| find "LISTENING"') do taskkill /F /PID %%a >nul 2>&1

:: Khởi động server CHẠY NGẦM bằng pythonw (không hiện bảng đen)
start pythonw.exe app.py

:: Đợi 1 giây để server kịp khởi động rồi mở trình duyệt web
timeout /t 1 /nobreak >nul
start http://localhost:5000
