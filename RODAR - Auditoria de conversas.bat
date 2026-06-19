@echo off
chcp 65001 >nul
cd /d "%~dp0.claude\skills\analisar-conversas\scripts"
echo ==================================================
echo   AUDITORIA DE CONVERSAS  (Atende Direito + IA)
echo ==================================================
echo.
set /p N=Quantos leads auditar? (Enter = 15): 
if "%N%"=="" set N=15
set /p J=Janela em dias? (Enter = 30): 
if "%J%"=="" set J=30
echo.
echo Rodando auditoria de %N% leads (janela %J% dias)...
echo (Le as conversas ja baixadas; classifica cada lead com IA.)
echo.
python run_atende.py %N% --janela %J%
echo.
echo --------------------------------------------------
echo  Pronto. Resultados na pasta do projeto:
echo    - auditoria_resumo.md      (tabela legivel)
echo    - auditoria_resultado.json (dados completos)
echo --------------------------------------------------
pause
