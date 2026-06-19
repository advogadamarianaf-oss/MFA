@echo off
chcp 65001 >nul
echo Rodando o puxador de amostra do Atende Direito...
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0atende_pull.ps1"
