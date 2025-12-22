@echo off
echo ========================================
echo   SQL SysHub - Build para Executavel
echo ========================================
echo.

REM Verificar se Python está instalado
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python não encontrado! Instale Python 3.7+ primeiro.
    pause
    exit /b 1
)

echo ✅ Python encontrado
echo.

REM Verificar se PyInstaller está instalado
python -c "import PyInstaller" >nul 2>&1
if %errorlevel% neq 0 (
    echo ⚠️  PyInstaller não encontrado. Instalando...
    pip install PyInstaller
    if %errorlevel% neq 0 (
        echo ❌ Falha ao instalar PyInstaller
        pause
        exit /b 1
    )
)

echo ✅ PyInstaller disponível
echo.

REM Testar comando PyInstaller
python -m PyInstaller --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Erro ao executar PyInstaller
    echo Tentando reinstalar...
    pip install --upgrade PyInstaller
)

echo ✅ PyInstaller funcionando
echo.

REM Executar script de build
echo 🚀 Iniciando build...
python build_exe.py

if %errorlevel% equ 0 (
    echo.
    echo 🎉 Build concluído com sucesso!
    echo 📁 Verifique a pasta 'dist' para os arquivos gerados
) else (
    echo.
    echo ❌ Erro durante o build
)

echo.
pause