@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo Instalando dependencias (so na primeira vez)...
python -m pip install --quiet --disable-pip-version-check google-auth google-api-python-client
echo.
echo Rodando o pipeline completo (le planilha, baixa API, resume, escreve)...
python "%~dp0pipeline_diario.py"
echo.
echo (Detalhes salvos em pipeline_log.txt)
pause
