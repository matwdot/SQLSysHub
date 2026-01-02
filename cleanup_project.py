#!/usr/bin/env python3
"""
Script de limpeza do projeto SQL SysHub.

Remove arquivos desnecessários como cache Python, arquivos temporários
e outros artefatos de build.
"""

import os
import shutil
import glob
from pathlib import Path


def remove_pycache_dirs():
    """Remove todos os diretórios __pycache__."""
    print("Removendo diretórios __pycache__...")
    
    for root, dirs, files in os.walk('.'):
        if '__pycache__' in dirs:
            pycache_path = os.path.join(root, '__pycache__')
            print(f"  Removendo: {pycache_path}")
            shutil.rmtree(pycache_path, ignore_errors=True)
            dirs.remove('__pycache__')


def remove_pyc_files():
    """Remove todos os arquivos .pyc."""
    print("Removendo arquivos .pyc...")
    
    pyc_files = glob.glob('**/*.pyc', recursive=True)
    for pyc_file in pyc_files:
        print(f"  Removendo: {pyc_file}")
        os.remove(pyc_file)


def remove_pytest_cache():
    """Remove cache do pytest."""
    print("Removendo cache do pytest...")
    
    pytest_cache = Path('.pytest_cache')
    if pytest_cache.exists():
        print(f"  Removendo: {pytest_cache}")
        shutil.rmtree(pytest_cache, ignore_errors=True)


def remove_build_artifacts():
    """Remove artefatos de build."""
    print("Removendo artefatos de build...")
    
    build_dirs = ['build', 'dist', '*.egg-info']
    
    for pattern in build_dirs:
        for path in glob.glob(pattern):
            if os.path.isdir(path):
                print(f"  Removendo diretório: {path}")
                shutil.rmtree(path, ignore_errors=True)
            elif os.path.isfile(path):
                print(f"  Removendo arquivo: {path}")
                os.remove(path)


def remove_temp_files():
    """Remove arquivos temporários."""
    print("Removendo arquivos temporários...")
    
    temp_patterns = ['*.tmp', '*.temp', '*~', '.DS_Store', 'Thumbs.db']
    
    for pattern in temp_patterns:
        for temp_file in glob.glob(f'**/{pattern}', recursive=True):
            print(f"  Removendo: {temp_file}")
            os.remove(temp_file)


def main():
    """Executa a limpeza completa do projeto."""
    print("=== Limpeza do Projeto SQL SysHub ===\n")
    
    try:
        remove_pycache_dirs()
        remove_pyc_files()
        remove_pytest_cache()
        remove_build_artifacts()
        remove_temp_files()
        
        print("\n✅ Limpeza concluída com sucesso!")
        
    except Exception as e:
        print(f"\n❌ Erro durante a limpeza: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())