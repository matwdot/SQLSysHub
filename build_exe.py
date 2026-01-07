#!/usr/bin/env python3
"""
Build script para criar executável do SQL SysHub v2.0.1

Este script usa PyInstaller para criar um executável standalone
do SQL SysHub com todas as dependências incluídas.
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

# Metadados do produto
PRODUCT_NAME = "SQL SysHub"
PRODUCT_VERSION = "2.0.1"
FILE_VERSION = "2.0.1.0"
COMPANY_NAME = "SQL SysHub"
FILE_DESCRIPTION = "SQL SysHub - Utilitários de Banco de Dados"
INTERNAL_NAME = "SQLSysHub"
ORIGINAL_FILENAME = "SQLSysHub.exe"
COPYRIGHT = "Copyright © 2026 SQL SysHub"


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


def create_icon_from_png():
    """Converte o logo PNG para ICO se necessário."""
    png_path = Path('imagens/cmLogo.png')
    ico_path = Path('imagens/sqlsyshub.ico')
    
    if ico_path.exists():
        print(f"✅ Ícone já existe: {ico_path}")
        return str(ico_path)
    
    if not png_path.exists():
        print("⚠️  Logo PNG não encontrado, executável será criado sem ícone")
        return None
    
    try:
        from PIL import Image
        
        img = Image.open(png_path)
        
        # Criar múltiplos tamanhos para o ICO
        sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
        icons = []
        
        for size in sizes:
            resized = img.resize(size, Image.Resampling.LANCZOS)
            if resized.mode != 'RGBA':
                resized = resized.convert('RGBA')
            icons.append(resized)
        
        # Salvar como ICO
        icons[0].save(str(ico_path), format='ICO', sizes=[(s[0], s[1]) for s in sizes])
        print(f"✅ Ícone criado: {ico_path}")
        return str(ico_path)
        
    except ImportError:
        print("⚠️  Pillow não instalado, tentando usar PNG diretamente")
        return str(png_path)
    except Exception as e:
        print(f"⚠️  Erro ao criar ícone: {e}")
        return None


def create_version_file():
    """Cria arquivo de versão para Windows."""
    version_parts = FILE_VERSION.split('.')
    while len(version_parts) < 4:
        version_parts.append('0')
    
    version_tuple = ', '.join(version_parts[:4])
    
    version_content = f'''# UTF-8
VSVersionInfo(
  ffi=FixedFileInfo(
    filevers=({version_tuple}),
    prodvers=({version_tuple}),
    mask=0x3f,
    flags=0x0,
    OS=0x40004,
    fileType=0x1,
    subtype=0x0,
    date=(0, 0)
  ),
  kids=[
    StringFileInfo(
      [
        StringTable(
          u'041604B0',
          [
            StringStruct(u'CompanyName', u'{COMPANY_NAME}'),
            StringStruct(u'FileDescription', u'{FILE_DESCRIPTION}'),
            StringStruct(u'FileVersion', u'{FILE_VERSION}'),
            StringStruct(u'InternalName', u'{INTERNAL_NAME}'),
            StringStruct(u'LegalCopyright', u'{COPYRIGHT}'),
            StringStruct(u'OriginalFilename', u'{ORIGINAL_FILENAME}'),
            StringStruct(u'ProductName', u'{PRODUCT_NAME}'),
            StringStruct(u'ProductVersion', u'{PRODUCT_VERSION}'),
          ]
        )
      ]
    ),
    VarFileInfo([VarStruct(u'Translation', [1046, 1200])])
  ]
)
'''
    
    version_file_path = 'version_info.txt'
    with open(version_file_path, 'w', encoding='utf-8') as f:
        f.write(version_content)
    
    print(f"✅ Arquivo de versão criado: {version_file_path}")
    return version_file_path


def clean_build_dirs():
    """Remove diretórios de build anteriores."""
    dirs_to_clean = ['build', 'dist', '__pycache__']
    
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            print(f"🧹 Removendo {dir_name}/")
            shutil.rmtree(dir_name)
    
    # Remove arquivos temporários anteriores
    files_to_clean = ['version_info.txt']
    for file_name in files_to_clean:
        if os.path.exists(file_name):
            print(f"🧹 Removendo {file_name}")
            os.remove(file_name)


def create_pyinstaller_spec(icon_path, version_file):
    """Cria arquivo .spec personalizado para PyInstaller."""
    
    icon_line = f"icon=r'{icon_path}'," if icon_path else "icon=None,"
    version_line = f"version=r'{version_file}'," if version_file else "version=None,"
    
    spec_content = f'''# -*- mode: python ; coding: utf-8 -*-
# SQL SysHub v{PRODUCT_VERSION} - Build Spec

import os
import sys
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

# Adicionar diretório atual ao path
current_dir = os.path.dirname(os.path.abspath(SPEC))
sys.path.insert(0, current_dir)

# Coletar dados do qtawesome (ícones)
qtawesome_datas = collect_data_files('qtawesome')

# Hidden imports - todos os módulos do projeto
hidden_imports = [
    # PyQt5
    'PyQt5.QtCore',
    'PyQt5.QtGui', 
    'PyQt5.QtWidgets',
    'PyQt5.sip',
    
    # QtAwesome
    'qtawesome',
    'qtawesome.iconic_font',
    
    # Módulo principal
    'refactored_sqltools',
    'refactored_sqltools.main',
    
    # Config
    'refactored_sqltools.config',
    'refactored_sqltools.config.config_manager',
    
    # Core
    'refactored_sqltools.core',
    
    # Database
    'refactored_sqltools.core.database',
    'refactored_sqltools.core.database.manager',
    'refactored_sqltools.core.database.drivers',
    'refactored_sqltools.core.database.drivers.base',
    'refactored_sqltools.core.database.drivers.firebird',
    'refactored_sqltools.core.database.drivers.sqlserver',
    
    # Operations
    'refactored_sqltools.core.operations',
    'refactored_sqltools.core.operations.base',
    'refactored_sqltools.core.operations.predefined',
    'refactored_sqltools.core.operations.registry',
    'refactored_sqltools.core.operations.individual',
    'refactored_sqltools.core.operations.individual.apagar_certificado',
    'refactored_sqltools.core.operations.individual.cancelar_cupom',
    'refactored_sqltools.core.operations.individual.consultar_ncm_inexistente',
    'refactored_sqltools.core.operations.individual.corrigir_erro_equipamento',
    'refactored_sqltools.core.operations.individual.limpar_tabelas_fisco',
    'refactored_sqltools.core.operations.individual.ver_ncms_a_vencer',
    
    # Workers
    'refactored_sqltools.core.workers',
    'refactored_sqltools.core.workers.database_worker',
    
    # UI
    'refactored_sqltools.ui',
    'refactored_sqltools.ui.windows',
    'refactored_sqltools.ui.windows.main_window',
    'refactored_sqltools.ui.windows.parameter_dialog',
    'refactored_sqltools.ui.windows.splash_screen',
    'refactored_sqltools.ui.components',
    'refactored_sqltools.ui.components.connection_panel',
    'refactored_sqltools.ui.components.enhanced_parameters',
    'refactored_sqltools.ui.components.operation_selector',
    'refactored_sqltools.ui.components.progress_indicator',
    'refactored_sqltools.ui.components.results_display',
    'refactored_sqltools.ui.components.sql_editor',
    'refactored_sqltools.ui.components.status_progress',
    'refactored_sqltools.ui.components.styled_calendar',
    
    # Utils
    'refactored_sqltools.utils',
    'refactored_sqltools.utils.exceptions',
    'refactored_sqltools.utils.ncm_manager',
    'refactored_sqltools.utils.validators',
]

# Adicionar drivers de banco opcionais se disponíveis
optional_drivers = ['firebirdsql', 'fdb', 'pyodbc', 'psycopg2', 'mysql.connector']
for driver in optional_drivers:
    try:
        __import__(driver)
        hidden_imports.append(driver)
        print(f"Incluindo driver: {{driver}}")
    except ImportError:
        print(f"Driver opcional nao encontrado: {{driver}}")

# Dados adicionais a incluir
# Nota: settings.ini é criado na pasta do usuário (%LOCALAPPDATA%/SQLSysHub)
#       json é salvo na pasta do usuário, mas incluímos o padrão como fallback
datas = qtawesome_datas + [
    ('imagens', 'imagens'),
    ('refactored_sqltools/json', 'refactored_sqltools/json'),
]

a = Analysis(
    ['run_sqltools.py'],
    pathex=[current_dir],
    binaries=[],
    datas=datas,
    hiddenimports=hidden_imports,
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=[
        'tkinter',
        'matplotlib',
        'numpy',
        'pandas',
        'scipy',
        'cv2',
        'IPython',
        'jupyter',
        'notebook',
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
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    {icon_line}
    {version_line}
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
        if result.stdout:
            # Mostrar apenas as últimas linhas relevantes
            lines = result.stdout.strip().split('\n')
            for line in lines[-10:]:
                if line.strip():
                    print(f"   {line}")
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
    installer_content = f'''@echo off
chcp 65001 >nul
echo ========================================
echo   {PRODUCT_NAME} v{PRODUCT_VERSION} - Instalador
echo ========================================
echo.

set "INSTALL_DIR=%PROGRAMFILES%\\SQLSysHub"
set "DESKTOP_SHORTCUT=%USERPROFILE%\\Desktop\\{PRODUCT_NAME}.lnk"
set "STARTMENU_SHORTCUT=%APPDATA%\\Microsoft\\Windows\\Start Menu\\Programs\\{PRODUCT_NAME}.lnk"

echo Criando diretório de instalação...
if not exist "%INSTALL_DIR%" mkdir "%INSTALL_DIR%"

echo Copiando arquivos...
copy "SQLSysHub.exe" "%INSTALL_DIR%\\" >nul
if exist "imagens" xcopy "imagens" "%INSTALL_DIR%\\imagens\\" /E /I /Q >nul

echo Criando atalhos...
powershell -Command "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%DESKTOP_SHORTCUT%'); $Shortcut.TargetPath = '%INSTALL_DIR%\\SQLSysHub.exe'; $Shortcut.WorkingDirectory = '%INSTALL_DIR%'; $Shortcut.Description = '{PRODUCT_NAME} v{PRODUCT_VERSION}'; $Shortcut.Save()"
powershell -Command "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%STARTMENU_SHORTCUT%'); $Shortcut.TargetPath = '%INSTALL_DIR%\\SQLSysHub.exe'; $Shortcut.WorkingDirectory = '%INSTALL_DIR%'; $Shortcut.Description = '{PRODUCT_NAME} v{PRODUCT_VERSION}'; $Shortcut.Save()"

echo.
echo Instalação concluída!
echo.
echo O {PRODUCT_NAME} foi instalado em: %INSTALL_DIR%
echo Atalhos criados na Área de Trabalho e Menu Iniciar
echo.
pause
'''
    
    with open('dist/instalar.bat', 'w', encoding='utf-8') as f:
        f.write(installer_content)
    
    print("✅ Script de instalação criado: dist/instalar.bat")


def create_readme():
    """Cria arquivo README para distribuição."""
    readme_content = f'''# {PRODUCT_NAME} v{PRODUCT_VERSION}

## Instalação

### Opção 1: Instalação Automática (Recomendada)
1. Execute o arquivo "instalar.bat" como Administrador
2. O programa será instalado automaticamente em "C:\\Program Files\\SQLSysHub"
3. Atalhos serão criados na Área de Trabalho e Menu Iniciar

### Opção 2: Execução Direta
1. Execute diretamente o arquivo "SQLSysHub.exe"
2. O programa funcionará a partir da pasta atual

## Requisitos do Sistema

- Windows 7 ou superior (64-bit recomendado)
- 100 MB de espaço livre em disco
- Drivers de banco de dados instalados conforme necessário

## Drivers de Banco Suportados

- Firebird (firebirdsql) - Incluído
- SQL Server (requer ODBC Driver 17)

## Solução de Problemas

### Erro "MSVCP140.dll não encontrado"
Instale o Microsoft Visual C++ Redistributable:
https://aka.ms/vs/17/release/vc_redist.x64.exe

### Erro de conexão SQL Server
Instale o ODBC Driver 17 for SQL Server:
https://go.microsoft.com/fwlink/?linkid=2249006

### Antivírus bloqueando o executável
Adicione exceção para o arquivo SQLSysHub.exe no seu antivírus.

---
{PRODUCT_NAME} v{PRODUCT_VERSION} - {FILE_DESCRIPTION}
{COPYRIGHT}
'''
    
    with open('dist/LEIA-ME.txt', 'w', encoding='utf-8') as f:
        f.write(readme_content)
    
    print("✅ Arquivo LEIA-ME.txt criado")


def main():
    """Função principal do script de build."""
    print(f"🚀 {PRODUCT_NAME} v{PRODUCT_VERSION} - Build para Executável")
    print("=" * 55)
    
    # Verificar dependências
    if not check_dependencies():
        return 1
    
    # Limpar builds anteriores
    print("\n🧹 Limpando builds anteriores...")
    clean_build_dirs()
    
    # Criar ícone
    print("\n🎨 Preparando ícone...")
    icon_path = create_icon_from_png()
    
    # Criar arquivo de versão
    print("\n📋 Criando metadados de versão...")
    version_file = create_version_file()
    
    # Criar arquivo .spec
    print("\n📝 Criando configuração do PyInstaller...")
    create_pyinstaller_spec(icon_path, version_file)
    
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
    
    # Limpar arquivo de versão temporário
    if os.path.exists('version_info.txt'):
        os.remove('version_info.txt')
    
    print("\n" + "=" * 55)
    print(f"🎉 Build do {PRODUCT_NAME} v{PRODUCT_VERSION} concluído!")
    print(f"📁 Executável: {os.path.abspath('dist/SQLSysHub.exe')}")
    print("=" * 55)
    
    if os.path.exists('dist'):
        print("\n📋 Arquivos criados:")
        for item in os.listdir('dist'):
            item_path = os.path.join('dist', item)
            if os.path.isfile(item_path):
                size = os.path.getsize(item_path)
                if size > 1024 * 1024:
                    size_str = f"{size / (1024*1024):.1f} MB"
                else:
                    size_str = f"{size / 1024:.1f} KB"
                print(f"   📄 {item} ({size_str})")
            else:
                print(f"   📁 {item}/")
    
    print("\n💡 Para distribuir, comprima a pasta 'dist' em um arquivo ZIP")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
