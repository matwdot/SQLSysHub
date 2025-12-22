#!/usr/bin/env python3
"""
Build script para criar executável do SQL SysHub.

Este script usa PyInstaller para criar um executável standalone
do SQL SysHub com todas as dependências incluídas.
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path


def check_dependencies():
    """Verifica se as dependências necessárias estão instaladas."""
    required_packages = {
        'PyInstaller': 'PyInstaller',
        'PyQt5': 'PyQt5',
        'qtawesome': 'qtawesome'
    }
    
    missing_packages = []
    
    for display_name, import_name in required_packages.items():
        try:
            __import__(import_name)
            print(f"✅ {display_name} encontrado")
        except ImportError:
            missing_packages.append(display_name)
            print(f"❌ {display_name} não encontrado")
    
    if missing_packages:
        print(f"\n❌ Pacotes ausentes: {', '.join(missing_packages)}")
        print("Instale com: pip install " + " ".join(missing_packages))
        return False
    
    # Testar se PyInstaller funciona corretamente
    try:
        result = subprocess.run([sys.executable, '-m', 'PyInstaller', '--version'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print(f"✅ PyInstaller funcionando: {result.stdout.strip()}")
        else:
            print("❌ PyInstaller não funciona corretamente")
            print("Tente reinstalar: pip install --upgrade PyInstaller")
            return False
    except Exception as e:
        print(f"❌ Erro ao testar PyInstaller: {e}")
        print("Tente reinstalar: pip install --upgrade PyInstaller")
        return False
    
    return True


def clean_build_dirs():
    """Remove diretórios de build anteriores."""
    dirs_to_clean = ['build', 'dist', '__pycache__']
    
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            print(f"🧹 Removendo {dir_name}/")
            shutil.rmtree(dir_name)
    
    # Remove arquivos .spec anteriores
    spec_files = list(Path('.').glob('*.spec'))
    for spec_file in spec_files:
        print(f"🧹 Removendo {spec_file}")
        spec_file.unlink()


def create_pyinstaller_spec():
    """Cria arquivo .spec personalizado para PyInstaller."""
    spec_content = '''# -*- mode: python ; coding: utf-8 -*-

import os
import sys
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

# Adicionar diretório atual ao path
current_dir = os.path.dirname(os.path.abspath(SPEC))
sys.path.insert(0, current_dir)

# Coletar dados do qtawesome (ícones)
qtawesome_datas = collect_data_files('qtawesome')

# Coletar submódulos do projeto
hidden_imports = [
    'PyQt5.QtCore',
    'PyQt5.QtGui', 
    'PyQt5.QtWidgets',
    'qtawesome',
    'qtawesome.iconic_font',
    'refactored_sqltools',
    'refactored_sqltools.main',
    'refactored_sqltools.ui',
    'refactored_sqltools.ui.windows',
    'refactored_sqltools.ui.components',
    'refactored_sqltools.core',
    'refactored_sqltools.core.database',
    'refactored_sqltools.core.database.drivers',
    'refactored_sqltools.core.operations',
    'refactored_sqltools.core.workers',
    'refactored_sqltools.utils',
]

# Adicionar drivers de banco opcionais se disponíveis
optional_drivers = ['firebirdsql', 'fdb', 'pyodbc', 'psycopg2', 'mysql.connector']
for driver in optional_drivers:
    try:
        __import__(driver)
        hidden_imports.append(driver)
        print(f"Incluindo driver: {driver}")
    except ImportError:
        print(f"Driver opcional nao encontrado: {driver}")

a = Analysis(
    ['run_sqltools.py'],
    pathex=[current_dir],
    binaries=[],
    datas=qtawesome_datas + [
        ('imagens', 'imagens'),  # Incluir pasta de imagens se existir
    ],
    hiddenimports=hidden_imports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'tkinter',
        'matplotlib',
        'numpy',
        'pandas',
        'scipy',
        'PIL',
        'cv2',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='SQLSysHub',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Não mostrar console
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # Remover ícone para evitar problemas com PIL
    version_file=None,
)
'''
    
    with open('sqlsyshub.spec', 'w', encoding='utf-8') as f:
        f.write(spec_content)
    
    print("✅ Arquivo sqlsyshub.spec criado")


def build_executable():
    """Executa o PyInstaller para criar o executável."""
    print("🔨 Iniciando build do executável...")
    
    cmd = [
        sys.executable, '-m', 'PyInstaller',
        '--clean',
        '--noconfirm',
        'sqlsyshub.spec'
    ]
    
    print(f"Executando: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("✅ Build concluído com sucesso!")
        print("📋 Saída do PyInstaller:")
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro durante o build:")
        print(f"Código de saída: {e.returncode}")
        if e.stdout:
            print(f"Stdout: {e.stdout}")
        if e.stderr:
            print(f"Stderr: {e.stderr}")
        return False


def create_installer_script():
    """Cria script batch para facilitar a instalação."""
    installer_content = '''@echo off
echo ========================================
echo   SQL SysHub - Instalador Simples
echo ========================================
echo.

set "INSTALL_DIR=%PROGRAMFILES%\\SQLSysHub"
set "DESKTOP_SHORTCUT=%USERPROFILE%\\Desktop\\SQL SysHub.lnk"
set "STARTMENU_SHORTCUT=%APPDATA%\\Microsoft\\Windows\\Start Menu\\Programs\\SQL SysHub.lnk"

echo Criando diretório de instalação...
if not exist "%INSTALL_DIR%" mkdir "%INSTALL_DIR%"

echo Copiando arquivos...
copy "SQLSysHub.exe" "%INSTALL_DIR%\\" >nul
if exist "imagens" xcopy "imagens" "%INSTALL_DIR%\\imagens\\" /E /I /Q >nul

echo Criando atalhos...
powershell -Command "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%DESKTOP_SHORTCUT%'); $Shortcut.TargetPath = '%INSTALL_DIR%\\SQLSysHub.exe'; $Shortcut.WorkingDirectory = '%INSTALL_DIR%'; $Shortcut.Save()"
powershell -Command "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%STARTMENU_SHORTCUT%'); $Shortcut.TargetPath = '%INSTALL_DIR%\\SQLSysHub.exe'; $Shortcut.WorkingDirectory = '%INSTALL_DIR%'; $Shortcut.Save()"

echo.
echo ✅ Instalação concluída!
echo.
echo O SQL SysHub foi instalado em: %INSTALL_DIR%
echo Atalhos criados na Área de Trabalho e Menu Iniciar
echo.
pause
'''
    
    with open('dist/instalar.bat', 'w', encoding='utf-8') as f:
        f.write(installer_content)
    
    print("✅ Script de instalação criado: dist/instalar.bat")


def create_readme():
    """Cria arquivo README para distribuição."""
    readme_content = '''# SQL SysHub - Executável

## Instalação

### Opção 1: Instalação Automática (Recomendada)
1. Execute o arquivo `instalar.bat` como Administrador
2. O programa será instalado automaticamente em `C:\\Program Files\\SQLSysHub`
3. Atalhos serão criados na Área de Trabalho e Menu Iniciar

### Opção 2: Execução Direta
1. Execute diretamente o arquivo `SQLSysHub.exe`
2. O programa funcionará a partir da pasta atual

## Requisitos do Sistema

- Windows 7 ou superior (64-bit recomendado)
- 100 MB de espaço livre em disco
- Drivers de banco de dados instalados conforme necessário:
  - **Firebird**: Não requer instalação adicional
  - **SQL Server**: Requer ODBC Driver 17 for SQL Server

## Drivers de Banco Incluídos

Este executável inclui suporte para:
- ✅ Firebird (firebirdsql)
- ⚠️  SQL Server (requer ODBC Driver 17)

## Solução de Problemas

### Erro "MSVCP140.dll não encontrado"
Instale o Microsoft Visual C++ Redistributable:
https://aka.ms/vs/17/release/vc_redist.x64.exe

### Erro de conexão SQL Server
Instale o ODBC Driver 17 for SQL Server:
https://go.microsoft.com/fwlink/?linkid=2249006

### Antivírus bloqueando o executável
Adicione exceção para o arquivo SQLSysHub.exe no seu antivírus.

## Suporte

Para suporte técnico ou reportar problemas, entre em contato com a equipe de desenvolvimento.

---
SQL SysHub v2.0 - Utilitários de Banco de Dados
'''
    
    with open('dist/LEIA-ME.txt', 'w', encoding='utf-8') as f:
        f.write(readme_content)
    
    print("✅ Arquivo LEIA-ME.txt criado")


def main():
    """Função principal do script de build."""
    print("🚀 SQL SysHub - Build para Executável")
    print("=" * 50)
    
    # Verificar dependências
    if not check_dependencies():
        return 1
    
    # Limpar builds anteriores
    print("\n🧹 Limpando builds anteriores...")
    clean_build_dirs()
    
    # Criar arquivo .spec
    print("\n📝 Criando configuração do PyInstaller...")
    create_pyinstaller_spec()
    
    # Executar build
    print("\n🔨 Executando build...")
    if not build_executable():
        return 1
    
    # Criar arquivos auxiliares
    print("\n📦 Criando arquivos de distribuição...")
    if os.path.exists('dist'):
        create_installer_script()
        create_readme()
        
        # Copiar imagens se existirem
        if os.path.exists('imagens'):
            shutil.copytree('imagens', 'dist/imagens', dirs_exist_ok=True)
            print("✅ Pasta de imagens copiada")
    
    print("\n🎉 Build concluído com sucesso!")
    print(f"📁 Executável criado em: {os.path.abspath('dist')}")
    print("📋 Arquivos criados:")
    
    if os.path.exists('dist'):
        for item in os.listdir('dist'):
            print(f"   - {item}")
    
    print("\n💡 Para distribuir:")
    print("   1. Comprima a pasta 'dist' em um arquivo ZIP")
    print("   2. Ou execute 'instalar.bat' como Administrador no computador de destino")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())