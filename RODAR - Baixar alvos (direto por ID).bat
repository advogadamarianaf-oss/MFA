@echo off
chcp 65001 >nul
echo Baixando mensagens DIRETO por user_ns (inclui quem nao esta no snapshot de subscribers)...
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0baixar_alvos_msgs.ps1"
