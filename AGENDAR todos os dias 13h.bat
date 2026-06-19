@echo off
chcp 65001 >nul
echo Agendando o pipeline para rodar TODOS OS DIAS as 13:00...
schtasks /Create /SC DAILY /ST 13:00 /TN "AtendeDireito_PlanilhaDiaria" /TR "cmd /c \"\"%~dp0RODAR - Pipeline diario (tudo).bat\"\"" /F
echo.
if %errorlevel%==0 (
  echo OK! Tarefa "AtendeDireito_PlanilhaDiaria" criada para as 13:00 diarias.
  echo Para conferir/remover: abra o "Agendador de Tarefas" do Windows.
) else (
  echo Nao consegui agendar. Tente clicar com o botao direito neste arquivo e "Executar como administrador".
)
echo.
pause
