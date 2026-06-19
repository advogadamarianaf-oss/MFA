@echo off
chcp 65001 >nul
echo Instalando dependencias (so na primeira vez)...
python -m pip install --quiet --disable-pip-version-check google-auth google-api-python-client
echo.
echo Escrevendo os resumos na planilha via Google Sheets API...
python "%~dp0escrever_planilha.py"
