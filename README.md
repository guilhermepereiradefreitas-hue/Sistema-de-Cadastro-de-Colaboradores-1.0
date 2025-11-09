# 🧾 Sistema de Cadastro de Colaboradores

Um sistema completo para **cadastro, controle e exportação de informações de colaboradores**, desenvolvido em **Python (Tkinter)** com **banco de dados SQLite**.

---

## 🚀 Recursos Principais

✅ Cadastro completo de funcionários com:
- Nome, cidade, endereço, bairro, loja, cargo e salário  
- Percentual de desconto e cálculo automático do salário líquido  
- Data de admissão e fim de contrato  
- Número, endereço da loja, CNPJ da loja e observações adicionais  
- Upload e visualização da **foto do colaborador**

✅ Banco de dados **SQLite** (arquivo local `employees.db`)

✅ Exportação de relatórios:
- **CSV** — para uso em planilhas simples  
- **Excel (.xlsx)** — formato profissional, usando `pandas` e `openpyxl`  
- **PDF** — relatório formatado, com possibilidade de exibir o logotipo da empresa

✅ Interface moderna com **temas `ttk`** e **layout responsivo**

✅ **Paginação e filtros de busca** (por nome, cargo e loja)

✅ Salvamento automático de fotos na pasta `/photos`

✅ Compatível com Windows, Linux e macOS

---

## 🧩 Estrutura do Projeto

```
Sistema_Cadastro_Funcionarios/
│
├── Sistema_Registro_IA.py        # Arquivo principal (Tkinter)
├── employees.db                  # Banco de dados (gerado automaticamente)
├── photos/                       # Pasta onde as fotos são salvas
├── logo.png                      # Logotipo opcional da empresa
└── README.md                     # Este arquivo
```

---

## ⚙️ Instalação e Execução

1. **Instale o Python 3.8+**

   [Baixar Python](https://www.python.org/downloads/)

2. **Instale as dependências:**

```bash
pip install customtkinter pillow reportlab pywin32 openpyxl
```

3. **Execute o sistema:**

   ```bash
   python Sistema_Registro_IA.py
   ```

4. **(Opcional)**: Para gerar um executável `.exe`:

   ```bash
   pip install pyinstaller
   pyinstaller --onefile --windowed Sistema_Registro_IA.py
   ```

---

## 🧮 Funcionalidades de Exportação

| Formato | Descrição | Dependências |
|----------|------------|---------------|
| **CSV** | Arquivo separado por vírgulas, compatível com Excel/Google Sheets | Nenhuma |
| **Excel (.xlsx)** | Relatório formatado e organizado em planilhas | `pandas`, `openpyxl` |
| **PDF** | Relatório em PDF com logo e colunas principais | `reportlab` |

> Todos os relatórios respeitam os **filtros de busca** aplicados no sistema.

---

## 🖼️ Fotos e Logotipo

- As **fotos dos colaboradores** são salvas automaticamente na pasta `photos/`.  
- O **logotipo da empresa** pode ser carregado pelo menu superior e fica armazenado como `logo.png`.

---

## 💡 Dicas de Uso

- Clique em **Selecionar Foto** para anexar a imagem do colaborador.  
- Use os campos de busca e o botão **Buscar** para filtrar os resultados.  
- Use os botões **CSV / Excel / PDF** para exportar relatórios.  
- A tabela de funcionários possui **barra de rolagem** e **paginação**.

---

## 🧰 Tecnologias Utilizadas

- **Python 3.8+**
- **Tkinter (ttk themes)**
- **SQLite3**
- **Pandas / OpenPyXL / ReportLab / Pillow**

---

## 🏢 Sobre o Projeto

Este sistema foi criado para **empresas que precisam manter um registro organizado de funcionários**, com relatórios rápidos e interface intuitiva.

Ele pode ser facilmente:
- Adaptado para uso **em rede (intranet)** via **Flask**
- Integrado com **planilhas financeiras**
- Expandido com autenticação ou controle de acesso

---

## 📄 Licença

Este projeto é de uso **livre para fins comerciais ou educacionais**, desde que mantidos os créditos do autor original.

---

© 2025 — Sistema de Registro DE Colaboradores. Todos os direitos reservados.
