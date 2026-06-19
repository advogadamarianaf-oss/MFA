@echo off
chcp 65001 >nul
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0carregar_aba.ps1" "paste_ORGANICO.tsv"
