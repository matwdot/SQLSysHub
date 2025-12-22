#!/bin/bash

echo "========================================"
echo "   SQL SysHub - Build para Executável"
echo "========================================"
echo

# Verificar se Python está instalado
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 não encontrado! Instale Python 3.7+ primeiro."
    exit 1
fi

echo "✅ Python encontrado: $(python3 --version)"
echo

# Verificar se pip está disponível
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 não encontrado! Instale pip primeiro."
    exit 1
fi

echo "✅ pip disponível"
echo

# Verificar se PyInstaller está instalado
if ! python3 -c "import PyInstaller" &> /dev/null; then
    echo "⚠️  PyInstaller não encontrado. Instalando..."
    pip3 install PyInstaller
    if [ $? -ne 0 ]; then
        echo "❌ Falha ao instalar PyInstaller"
        exit 1
    fi
fi

echo "✅ PyInstaller disponível"

# Testar comando PyInstaller
if ! python3 -m PyInstaller --version &> /dev/null; then
    echo "❌ Erro ao executar PyInstaller"
    echo "Tentando reinstalar..."
    pip3 install --upgrade PyInstaller
fi

echo "✅ PyInstaller funcionando"
echo

# Executar script de build
echo "🚀 Iniciando build..."
python3 build_exe.py

if [ $? -eq 0 ]; then
    echo
    echo "🎉 Build concluído com sucesso!"
    echo "📁 Verifique a pasta 'dist' para os arquivos gerados"
else
    echo
    echo "❌ Erro durante o build"
    exit 1
fi

echo
echo "Pressione Enter para continuar..."
read