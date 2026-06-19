@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo Levantando TODOS os leads com erro nas 3 primeiras mensagens (conta inteira)...
echo (Reaproveita conversas ja baixadas e salva as novas; pode demorar alguns minutos.)
echo.
python "%~dp0levantar_erros_3primeiras.py"
if errorlevel 1 (
  echo.
  echo [!] O Python pode nao estar instalado/no PATH. Tente: py "%~dp0levantar_erros_3primeiras.py"
  py "%~dp0levantar_erros_3primeiras.py"
)
echo.
pause
