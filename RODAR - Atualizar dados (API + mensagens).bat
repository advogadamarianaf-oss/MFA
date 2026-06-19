@echo off
chcp 65001 >nul
echo === Etapa 1/2: baixando subscribers (API) ===
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0atende_pull.ps1"
echo.
echo === Etapa 2/2: baixando as conversas (mensagens) ===
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0atende_mensagens.ps1"
echo.
echo Pronto! Avise o Claude que terminou.
pause
