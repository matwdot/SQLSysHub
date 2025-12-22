# 📦 Instruções de Build - SQL SysHub

Este documento explica como criar um executável standalone do SQL SysHub.

## 🔧 Pré-requisitos

### 1. Python
- Python 3.7 ou superior
- pip (gerenciador de pacotes Python)

### 2. Dependências
Instale as dependências necessárias:

```bash
# Instalar dependências básicas
pip install -r requirements_build.txt

# Ou instalar manualmente:
pip install PyInstaller PyQt5 qtawesome firebirdsql passlib
```

## 🚀 Métodos de Build

### Método 1: Build Automático (Recomendado)

#### Windows:
```cmd
# Execute o arquivo batch
build.bat
```

#### Linux/Mac:
```bash
# Execute o script Python
python build_exe.py
```

### Método 2: Build Manual

1. **Instalar PyInstaller:**
   ```bash
   pip install PyInstaller
   ```

2. **Executar build básico:**
   ```bash
   python -m PyInstaller --onefile --windowed --name SQLSysHub run_sqltools.py
   ```

3. **Build avançado com configurações:**
   ```bash
   python build_exe.py
   ```

## 📁 Estrutura de Saída

Após o build, a pasta `dist/` conterá:

```
dist/
├── SQLSysHub.exe          # Executável principal
├── instalar.bat           # Script de instalação
├── LEIA-ME.txt           # Instruções para usuário final
└── imagens/              # Recursos de imagem (se existirem)
```

## 🎯 Opções de Distribuição

### 1. Distribuição Simples
- Comprima a pasta `dist/` em um arquivo ZIP
- Envie o ZIP para os usuários
- Usuários executam `SQLSysHub.exe` diretamente

### 2. Instalação Automática
- Usuários executam `instalar.bat` como Administrador
- O programa é instalado em `C:\Program Files\SQLSysHub`
- Atalhos são criados automaticamente

## ⚙️ Configurações Avançadas

### Incluir Drivers Específicos

Edite `build_exe.py` e modifique a lista `optional_drivers`:

```python
optional_drivers = [
    'firebirdsql',    # Firebird (recomendado)
    'fdb',           # Firebird alternativo
    'pyodbc',        # SQL Server
    'psycopg2',      # PostgreSQL
    'mysql.connector' # MySQL
]
```

### Personalizar Ícone

1. Coloque seu ícone em `imagens/icon.ico`
2. Modifique o arquivo `.spec` gerado:
   ```python
   icon='imagens/icon.ico'
   ```

### Reduzir Tamanho do Executável

Adicione exclusões no arquivo `.spec`:

```python
excludes=[
    'tkinter',
    'matplotlib', 
    'numpy',
    'pandas',
    'scipy',
    'PIL',
    'cv2',
    # Adicione outros módulos não utilizados
]
```

## 🐛 Solução de Problemas

### Erro: "PyInstaller não encontrado"
```bash
pip install PyInstaller
```

### Erro: "Módulo não encontrado"
```bash
# Instalar dependências ausentes
pip install PyQt5 qtawesome

# Ou instalar tudo:
pip install -r requirements_build.txt
```

### Executável muito grande
- Use `--exclude-module` para remover módulos desnecessários
- Remova drivers de banco não utilizados
- Use UPX para compressão (incluído automaticamente)

### Erro de DLL no Windows
- Instale Microsoft Visual C++ Redistributable
- Use `--collect-all` para incluir todas as DLLs necessárias

### Antivírus bloqueando
- Adicione exceção para a pasta de build
- Use certificado de código para assinar o executável

## 📋 Checklist de Build

- [ ] Python 3.7+ instalado
- [ ] Dependências instaladas (`pip install -r requirements_build.txt`)
- [ ] PyInstaller instalado
- [ ] Projeto testado e funcionando
- [ ] Executar `build.bat` ou `python build_exe.py`
- [ ] Testar executável gerado
- [ ] Verificar tamanho do arquivo (< 100MB recomendado)
- [ ] Testar em máquina limpa (sem Python)
- [ ] Criar documentação de distribuição

## 🔄 Automatização CI/CD

Para builds automáticos, use GitHub Actions ou similar:

```yaml
name: Build Executable
on: [push, pull_request]
jobs:
  build:
    runs-on: windows-latest
    steps:
    - uses: actions/checkout@v2
    - uses: actions/setup-python@v2
      with:
        python-version: '3.9'
    - run: pip install -r requirements_build.txt
    - run: python build_exe.py
    - uses: actions/upload-artifact@v2
      with:
        name: SQLSysHub-Windows
        path: dist/
```

## 📞 Suporte

Para problemas de build, verifique:

1. **Logs de erro** - PyInstaller gera logs detalhados
2. **Dependências** - Todas instaladas corretamente
3. **Versões** - Python e PyQt5 compatíveis
4. **Espaço em disco** - Pelo menos 1GB livre
5. **Permissões** - Acesso de escrita na pasta do projeto

---

**Dica:** Sempre teste o executável em uma máquina sem Python instalado para garantir que funciona standalone.