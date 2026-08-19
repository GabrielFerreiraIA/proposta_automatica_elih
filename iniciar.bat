@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo.
echo  Elih - Gerador de Propostas
echo  Abrindo em http://127.0.0.1:8000
echo  (feche esta janela para parar o servidor)
echo.
start "" http://127.0.0.1:8000
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
pause
