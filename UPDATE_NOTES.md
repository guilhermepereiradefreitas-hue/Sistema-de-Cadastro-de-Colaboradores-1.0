# 🧾 Gestão de RH — Notas de Atualização e Bugs Conhecidos
### Versão atual: 1.2.1 (2025-11)

## 🆕 Novidades Principais
- Interface moderna com **CustomTkinter** (tema escuro 16:9)
- **Logo automático** em `C:\GestaoRH\logo.png` (gera exemplo se não existir)
- **Layout de formulário em 3 colunas** (colaborador, salário, empresa)
- Geração de **contracheque em PDF** com layout corporativo
- Banco **SQLite** local (`C:\GestaoRH\employees.db`) criado e atualizado automaticamente
- **Tabela TreeView** aprimorada:
  - Scroll vertical e horizontal
  - Efeito zebra (cinza-claro/escuro)
  - Edição direta nas células
  - Ajuste automático de largura
- Filtros rápidos por nome e cargo
- Abertura automática do PDF após gerar

---

## 🔧 Melhorias Técnicas
| Área | Melhoria |
|------|-----------|
| Banco de dados | Criação automática e estrutura atualizada |
| Interface | Tema escuro com espaçamento uniforme e fontes modernas |
| Layout | 3 colunas responsivas + botões em barra inferior |
| PDFs | Cabeçalho azul corporativo + assinatura + logo |
| Cálculos | Salário líquido calculado automaticamente |
| Pastas | Wizard cria `C:\GestaoRH` e subpastas se ausentes |

---

## 🪲 Bugs Conhecidos
| Módulo | Problema | Status |
|--------|-----------|--------|
| TreeView | Edição direta perde foco e pode não salvar valor corretamente | ⚠️ Em análise |
| Salário líquido | Depende da ordem dos campos e não recalcula em edição | ⚠️ Corrigir para recálculo dinâmico |
| Filtro de busca | Não possui botão “Limpar filtro” | ⚠️ Planejado |
| Layout | Em telas pequenas, colunas sobrepõem-se | ⚠️ Ajustar `grid_rowconfigure` |
| Backup | Ainda não gera cópia automática ao fechar | 🚧 Implementação pendente |
| Wizard | Falta tratamento de erro de permissão em `C:\GestaoRH` | ⚠️ Adicionar try/except |
| PDF | Campos longos quebram fora da página | ⚠️ Usar `wrapString` e margens dinâmicas |

---

## 📈 Roadmap — Versão 1.3.0 (Planejada)
- 🔐 Login com níveis de acesso (Admin / RH / Leitura)
- 📊 Dashboard visual com gráficos (folha mensal, total de colaboradores, salários)
- 🗂️ Backup automático ao fechar o sistema
- 🔄 Atualizador interno (verifica nova versão online)
- 📤 Exportação avançada (PDF/Excel/CSV)
- 🧮 Novo módulo “Financeiro” (controle de abonos e descontos)
- 🪪 Assinatura digital no contracheque (imagem ou QR Code)

---

## 🧰 Requisitos e Instalação
```bash
pip install customtkinter pillow reportlab openpyxl pywin32
python gestao_rh.py
```
Na primeira execução:
- Cria `C:\GestaoRH\`
- Gera `logo.png` de exemplo
- Inicializa banco `employees.db`

---

## 📜 Histórico
| Versão | Data | Mudanças |
|---------|------|-----------|
| 1.2.1 | 09/11/2025 | Interface moderna, PDF corporativo e TreeView aprimorada |
| 1.2.0 | 30/10/2025 | Versão estável com relatórios e login |
| 1.1.0 | 15/10/2025 | Sistema básico de cadastro |
| 1.0.0 | 01/10/2025 | Protótipo inicial |

---
© 2025 — Gestão RH Software by Guilherme Pereira
