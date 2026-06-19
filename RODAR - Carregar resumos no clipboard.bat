@echo off
chcp 65001 >nul
echo Carregando os resumos na area de transferencia...
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0carregar_clipboard.ps1"
