@echo off
setlocal
cd /d "%~dp0"

echo ============================================
echo          TG Uploader - Build Portatil
echo ============================================
echo.

where py >nul 2>nul
if %errorlevel%==0 (
    set "PYTHON=py"
) else (
    set "PYTHON=python"
)

%PYTHON% --version >nul 2>nul
if not %errorlevel%==0 (
    echo [ERRO] Python nao foi encontrado.
    echo Instale o Python 3.11 ou mais recente e tente novamente.
    echo.
    pause
    exit /b 1
)

if not exist ".venv-build\Scripts\python.exe" (
    echo [1/7] Criando ambiente de compilacao...
    %PYTHON% -m venv .venv-build
    if not %errorlevel%==0 goto :error
)

set "VPY=.venv-build\Scripts\python.exe"

echo [2/7] Atualizando ferramentas...
"%VPY%" -m pip install --upgrade pip
if not %errorlevel%==0 goto :error

echo [3/7] Instalando dependencias...
"%VPY%" -m pip install -r requirements.txt "pyinstaller>=6.10,<7"
if not %errorlevel%==0 goto :error

echo [4/7] Verificando o codigo Python...
"%VPY%" -m compileall -q main.py src tests
if not %errorlevel%==0 goto :error

echo [5/7] Executando testes...
"%VPY%" -m unittest discover -s tests -v
if not %errorlevel%==0 goto :error

echo [6/7] Gerando a versao portatil...
"%VPY%" -m PyInstaller ^
  --noconfirm ^
  --clean ^
  --windowed ^
  --onedir ^
  --name "TG-Uploader" ^
  --collect-all customtkinter ^
  --collect-submodules telethon ^
  main.py
if not %errorlevel%==0 goto :error

echo [7/7] Preparando a pasta final...
if not exist "dist\TG-Uploader\data" mkdir "dist\TG-Uploader\data"
copy /Y "README.md" "dist\TG-Uploader\README.md" >nul
copy /Y "README.en.md" "dist\TG-Uploader\README.en.md" >nul
copy /Y "README.es.md" "dist\TG-Uploader\README.es.md" >nul
copy /Y "PORTABLE.md" "dist\TG-Uploader\PORTABLE.md" >nul

echo.
echo ============================================
echo Build concluido com sucesso.
echo.
echo Pasta portatil:
echo %CD%\dist\TG-Uploader
echo.
echo Para usar em outro PC, copie a pasta TG-Uploader inteira.
echo O usuario final NAO precisa ter Python instalado.
echo ============================================
echo.
pause
exit /b 0

:error
echo.
echo [ERRO] A compilacao nao foi concluida.
echo Veja as mensagens acima para identificar a causa.
echo.
pause
exit /b 1
