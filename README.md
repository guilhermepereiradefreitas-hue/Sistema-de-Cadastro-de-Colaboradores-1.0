# 💼 Gestão de RH — Sistema de Colaboradores e Folha de Pagamento

Sistema completo de **Gestão de Recursos Humanos** desenvolvido em **Python + CustomTkinter + SQLite + ReportLab**, com interface moderna, banco de dados local, geração de contracheques e controle de colaboradores.

## 🖥️ Interface Moderna
- Tema escuro com **CustomTkinter** (layout 16:9 centralizado)
- Logo da empresa exibido automaticamente (`C:\GestaoRH\logo.png`)
- Abas organizadas:
  - **Colaboradores** → cadastro e edição completa
  - **Registros** → tabela interativa com filtros, relatórios e exportações

## ⚙️ Funcionalidades Principais

### 👤 Aba “Colaboradores”
- Layout em **3 colunas**, dividido por grupos de informações:
  - **Coluna 1:** Dados pessoais do colaborador  
  - **Coluna 2:** Dados salariais e contratuais  
  - **Coluna 3:** Dados da empresa
- Cálculo automático de **salário líquido**
- CRUD completo (Salvar, Atualizar, Excluir, Limpar)
- Geração de **contracheque em PDF corporativo**
- Abertura automática do PDF após gerar

### 📋 Aba “Registros”
- Tabela `Treeview` com:
  - **Efeito zebra** (linhas alternadas cinza-claro/escuro)
  - **Scroll horizontal e vertical**
  - **Edição direta nas células**
  - **Ajuste automático de largura**
- Botões de ações rápidas:
  - 🔎 Filtrar registros (por nome ou cargo)
  - 📄 Gerar contracheque direto
  - 📤 Exportar para **PDF** ou **Excel**
  - 💾 Criar **backup** do banco de dados
- Integração direta com o banco `employees.db`

### 🧱 Banco de Dados
- SQLite local (arquivo: `C:\GestaoRH\employees.db`)
- Tabela: **colaboradores**
- Criação e atualização automáticas ao iniciar o sistema
- Backup manual (botão na aba “Registros”)

### 🧾 Contracheque (PDF)
- Layout corporativo simples, limpo e assinado
- Cabeçalho com logo e nome da empresa
- Campos:
  - Nome, cargo, empresa, salário bruto, líquido, abono e vale-transporte
- Arquivo salvo automaticamente em:
  ```
  C:\GestaoRH\Contracheque_<NOME>.pdf
  ```
- Aberto automaticamente no leitor padrão

## 🚀 Instalação

### 1️⃣ Instalar o Python
Baixe e instale o [Python 3.10+](https://www.python.org/downloads/)  
> ✅ Marque a opção *“Add Python to PATH”* durante a instalação.

### 2️⃣ Instalar dependências
Abra o Prompt de Comando e execute:

```bash
pip install customtkinter pillow reportlab pywin32 openpyxl
```

### 3️⃣ Executar o sistema
```bash
python gestao_rh.py
```

Na primeira execução:
- A pasta `C:\GestaoRH` será criada automaticamente.
- Um logo de exemplo será gerado (`logo.png`).
- O banco `employees.db` será inicializado.

## 🧰 Estrutura de Pastas

```
C:\
 └── GestaoRH\
      ├── gestao_rh.py          ← Aplicativo principal
      ├── employees.db          ← Banco de dados SQLite
      ├── logo.png              ← Logo da empresa
      ├── Contracheque_*.pdf    ← PDFs gerados
      └── backup\               ← (opcional) cópias de segurança
```

## 💡 Atalhos úteis

| Ação | Atalho |
|------|---------|
| Salvar colaborador | **Ctrl + S** |
| Gerar contracheque | **Ctrl + P** |
| Atualizar tabela | **F5** |
| Sair do sistema | **Ctrl + Q** |

## 🧠 Requisitos Técnicos
- Python 3.10 ou superior  
- Windows 10/11 (com suporte ao `pywin32`)
- Resolução recomendada: **16:9 (1200x720 ou superior)**

## 🔐 Segurança
- Banco de dados local seguro e fechado ao sair.
- Nenhum dado é enviado para a internet.
- Backups podem ser gerados manualmente em um clique.

## 🧩 Desenvolvido com
- [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter)
- [SQLite3](https://www.sqlite.org)
- [ReportLab](https://www.reportlab.com)
- [Pillow (PIL)](https://pillow.readthedocs.io)

## 🧾 Licença
Projeto de uso interno e educacional.  
© 2025 — Gestão RH Software by Guilherme Pereira.
