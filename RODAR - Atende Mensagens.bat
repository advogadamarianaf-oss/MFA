@echo off
chcp 65001 >nul
echo Baixando as mensagens (transcripts) dos leads do Atende Direito...
echo (Retomavel: pode cancelar e rodar de novo; pula quem ja baixou.)
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0atende_mensagens.ps1"
