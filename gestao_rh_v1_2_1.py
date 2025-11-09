# gestao_rh.py
import os
import shutil
import sqlite3
import traceback
import sys
from datetime import datetime
import customtkinter as ctk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageDraw, ImageOps

# opcionais
try:
    import pandas as pd
except Exception:
    pd = None

try:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.pdfgen import canvas as rcanvas
except Exception:
    rcanvas = None

# -----------------------
# CONFIG
APP_DIR = r"C:\GestaoRH"
DB_PATH = os.path.join(APP_DIR, "employees.db")
LOGO_PATH = os.path.join(APP_DIR, "logo.png")
REPORTS_DIR = os.path.join(APP_DIR, "Relatorios")
os.makedirs(REPORTS_DIR, exist_ok=True)

# -----------------------
# DB: esquema base (colunas atuais)
BASE_COLUMNS = [
    ("id", "INTEGER PRIMARY KEY AUTOINCREMENT"),
    ("nome", "TEXT"),
    ("identidade", "TEXT"),
    ("nome_mae", "TEXT"),
    ("nome_pai", "TEXT"),
    ("cpf", "TEXT"),
    ("cep", "TEXT"),
    ("endereco", "TEXT"),
    ("numero", "TEXT"),
    ("bairro", "TEXT"),
    ("complemento", "TEXT"),
    ("nascimento", "TEXT"),
    ("telefone", "TEXT"),
    ("email", "TEXT"),
    ("cargo", "TEXT"),
    ("salario_inicial", "REAL"),
    ("salario_bruto", "REAL"),
    ("optante_passagem", "TEXT"),
    ("valor_passagem", "REAL"),
    ("abono_salarial", "TEXT"),
    ("valor_abono", "REAL"),
    ("salario_liquido", "REAL"),
    ("fim_contrato", "TEXT"),
    ("empresa", "TEXT"),
    ("endereco_empresa", "TEXT"),
    ("numero_empresa", "TEXT"),
    ("cidade", "TEXT"),
    ("bairro_empresa", "TEXT"),
    ("cnpj", "TEXT"),
    ("telefone_empresa", "TEXT"),
    ("email_empresa", "TEXT"),
    ("anexo_pdf", "TEXT")  # caminho para PDF anexado (opcional)
]

# -----------------------
# WIZARD / INIT
def inicializar_sistema():
    os.makedirs(APP_DIR, exist_ok=True)
    os.makedirs(REPORTS_DIR, exist_ok=True)
    # cria logo exemplo se não existir
    if not os.path.exists(LOGO_PATH):
        try:
            img = Image.new("RGB", (480, 140), color="#2b5797")
            draw = ImageDraw.Draw(img)
            text = "Gestão RH"
            # centraliza texto grosso
            w, h = draw.textsize(text)
            draw.text(((480 - w) / 2, (140 - h) / 2), text, fill="white")
            img.save(LOGO_PATH)
        except Exception:
            pass
    # criar DB e migrar esquema
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    # cria tabela se não existir (com apenas id e nome para evitar erros), depois atualiza colunas
    c.execute("""
        CREATE TABLE IF NOT EXISTS colaboradores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT
        )
    """)
    conn.commit()
    # garantir colunas do BASE_COLUMNS
    cur_cols = {}
    cur = conn.cursor()
    cur.execute("PRAGMA table_info(colaboradores)")
    for r in cur.fetchall():
        cur_cols[r[1]] = r[2]  # name: type
    # add missing columns
    for col_name, col_type in BASE_COLUMNS:
        if col_name in cur_cols:
            continue
        if col_name == "id":  # já existe
            continue
        try:
            conn.execute(f"ALTER TABLE colaboradores ADD COLUMN {col_name} {col_type}")
            conn.commit()
        except Exception:
            # se falhar, ignore e continue
            pass
    conn.close()

# -----------------------
# DB helpers
def conectar():
    return sqlite3.connect(DB_PATH)

def listar_colaboradores(filtro=""):
    conn = conectar()
    cur = conn.cursor()
    if filtro:
        q = "SELECT * FROM colaboradores WHERE nome LIKE ? OR cargo LIKE ? ORDER BY id DESC"
        cur.execute(q, (f"%{filtro}%", f"%{filtro}%"))
    else:
        q = "SELECT * FROM colaboradores ORDER BY id DESC"
        cur.execute(q)
    rows = cur.fetchall()
    conn.close()
    return rows

def inserir_colaborador(d):
    conn = conectar()
    cur = conn.cursor()
    cols = [c[0] for c in BASE_COLUMNS if c[0] != "id"]
    placeholders = ",".join("?" for _ in cols)
    q = f"INSERT INTO colaboradores ({','.join(cols)}) VALUES ({placeholders})"
    cur.execute(q, tuple(d.get(col, "") for col in cols))
    conn.commit()
    conn.close()
    return cur.lastrowid

def atualizar_colaborador_db(id_, d):
    conn = conectar()
    cur = conn.cursor()
    cols = [c[0] for c in BASE_COLUMNS if c[0] != "id"]
    set_clause = ",".join(f"{c}=?" for c in cols)
    q = f"UPDATE colaboradores SET {set_clause} WHERE id=?"
    cur.execute(q, tuple(d.get(col, "") for col in cols) + (id_,))
    conn.commit()
    conn.close()

def excluir_colaborador_db(id_):
    conn = conectar()
    cur = conn.cursor()
    cur.execute("DELETE FROM colaboradores WHERE id=?", (id_,))
    conn.commit()
    conn.close()

# export/import helpers
def export_csv(path):
    rows = listar_colaboradores()
    if not rows:
        return False, "Nenhum registro"
    import csv
    cols = [c[0] for c in BASE_COLUMNS]
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(cols)
        for r in rows:
            w.writerow(r)
    return True, f"CSV salvo em {path}"

def import_csv(path):
    import csv
    with open(path, newline="", encoding="utf-8") as f:
        r = csv.reader(f)
        header = next(r, None)
        # map header to our columns where possible
        for row in r:
            # build dict
            d = {}
            for i, v in enumerate(row):
                if i < len(header):
                    col = header[i]
                    if col in [c[0] for c in BASE_COLUMNS]:
                        d[col] = v
            # insert
            inserir_colaborador(d)
    return True, "Importado CSV (tentativa) - verifique dados"

def export_excel(path):
    if pd is None:
        return False, "pandas não instalado"
    rows = listar_colaboradores()
    cols = [c[0] for c in BASE_COLUMNS]
    df = pd.DataFrame(rows, columns=cols)
    df.to_excel(path, index=False)
    return True, f"Excel salvo em {path}"

def import_excel(path):
    if pd is None:
        return False, "pandas não instalado"
    df = pd.read_excel(path)
    for _, row in df.iterrows():
        d = {}
        for col in df.columns:
            if col in [c[0] for c in BASE_COLUMNS]:
                d[col] = row[col]
        inserir_colaborador(d)
    return True, "Excel importado"

# -----------------------
# PDF contracheque
def gerar_contracheque_pdf(record):
    if rcanvas is None:
        raise RuntimeError("reportlab não instalado")
    # record is tuple matching SELECT *
    cols = [c[0] for c in BASE_COLUMNS]
    data = dict(zip(cols, record))
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_name = (data.get("nome") or "colaborador").replace(" ", "_")
    out_path = os.path.join(REPORTS_DIR, f"contracheque_{safe_name}_{ts}.pdf")
    c = rcanvas.Canvas(out_path, pagesize=A4)
    w, h = A4

    # header band
    c.setFillColor(colors.HexColor("#2b5797"))
    c.rect(0, h - 90, w, 90, fill=1, stroke=0)
    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 18)
    c.drawString(40, h - 55, "CONTRACHEQUE")
    # logo right
    try:
        if os.path.exists(LOGO_PATH):
            c.drawImage(LOGO_PATH, w - 160, h - 80, width=120, height=60, preserveAspectRatio=True)
    except Exception:
        pass

    # sections
    left_x = 40
    right_x = w / 2 + 10
    y = h - 120
    line_h = 16
    c.setFont("Helvetica", 10)
    # employee & company
    c.setFillColor(colors.black)
    c.drawString(left_x, y, f"Nome: {data.get('nome','')}")
    c.drawString(right_x, y, f"Empresa: {data.get('empresa','')}")
    y -= line_h
    c.drawString(left_x, y, f"Cargo: {data.get('cargo','')}")
    c.drawString(right_x, y, f"CNPJ: {data.get('cnpj','')}")
    y -= line_h
    c.drawString(left_x, y, f"CPF: {data.get('cpf','')}")
    c.drawString(right_x, y, f"Endereço: {data.get('endereco_empresa','')} {data.get('numero_empresa','')}")
    y -= line_h * 1.2

    # financial block with border
    box_x = left_x
    box_w = w - 2 * left_x
    box_h = 140
    c.setStrokeColor(colors.HexColor("#cfcfcf"))
    c.setLineWidth(0.5)
    c.rect(box_x, y - box_h + 20, box_w, box_h, stroke=1, fill=0)
    inner_y = y - 10
    c.setFont("Helvetica-Bold", 11)
    c.drawString(box_x + 8, inner_y, "Detalhamento Salarial")
    inner_y -= 18
    c.setFont("Helvetica", 10)
    bruto = float(data.get("salario_bruto") or 0)
    passagem = float(data.get("valor_passagem") or 0)
    abono = float(data.get("valor_abono") or 0)
    liquido = float(data.get("salario_liquido") or max(0, bruto - (passagem + abono)))
    c.drawString(box_x + 12, inner_y, f"Salário Bruto: R$ {bruto:,.2f}")
    c.drawRightString(box_x + box_w - 12, inner_y, f"Salário Líquido: R$ {liquido:,.2f}")
    inner_y -= 16
    c.drawString(box_x + 12, inner_y, f"Valor Passagem: R$ {passagem:,.2f}")
    c.drawString(box_x + 220, inner_y, f"Abono Salarial: R$ {abono:,.2f}")
    inner_y -= 18
    c.drawString(box_x + 12, inner_y, f"Fim do Contrato: {data.get('fim_contrato') or 'Indeterminado'}")

    # signature lines
    sig_y = box_y = y - box_h - 40
    c.line(left_x + 20, sig_y, left_x + 200, sig_y)
    c.drawString(left_x + 25, sig_y - 14, "Assinatura do Colaborador")
    c.line(w - 220, sig_y, w - 40, sig_y)
    c.drawString(w - 215, sig_y - 14, "Assinatura da Empresa")

    c.showPage()
    c.save()
    # open file
    try:
        os.startfile(out_path)
    except Exception:
        # fallback: print path
        messagebox.showinfo("Contracheque gerado", f"Arquivo salvo em:\n{out_path}")
    return out_path

# -----------------------
# UI main
class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Gestão RH - Colaboradores e Folha")
        # ajusta proporção 16:9 baseada na tela (85% largura)
        sw = self.winfo_screenwidth()
        width = int(sw * 0.85)
        height = int(width * 9 / 16)
        self.geometry(f"{width}x{height}")
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # top header com logo à direita
        header = ctk.CTkFrame(self, height=80)
        header.pack(side="top", fill="x")
        header.pack_propagate(False)
        tk_label = ctk.CTkLabel(header, text="Gestão RH — Colaboradores e Folha", font=ctk.CTkFont(size=18, weight="bold"))
        tk_label.pack(side="left", padx=20)
        if os.path.exists(LOGO_PATH):
            try:
                img = Image.open(LOGO_PATH)
                img = ImageOps.contain(img, (180, 60))
                logo_img = ctk.CTkImage(img, size=(180, 60))
                ctk.CTkLabel(header, image=logo_img, text="📷").pack(side="right", padx=20)
                # keep reference
                self.logo_image = logo_img
            except Exception:
                pass

        # tabs
        self.tabs = ctk.CTkTabview(self)
        self.tabs.pack(expand=True, fill="both", padx=12, pady=12)
        self.tab_col = self.tabs.add("Colaboradores")
        self.tab_reg = self.tabs.add("Registros")
        # create tab contents
        self.create_colaboradores_tab()
        self.create_registros_tab()
        # menu quick
        self.create_menu()

    # -----------------------
    # Aba Colaboradores (form 3 colunas)
    def create_colaboradores_tab(self):
        frame = ctk.CTkFrame(self.tab_col)
        frame.pack(fill="both", expand=True, padx=12, pady=12)

        # card central
        card = ctk.CTkFrame(frame)
        card.place(relx=0.5, rely=0.02, anchor="n", relwidth=0.96, relheight=0.90)

        # create 3 columns
        left = ctk.CTkFrame(card)
        center = ctk.CTkFrame(card)
        right = ctk.CTkFrame(card)
        left.pack(side="left", expand=True, fill="both", padx=8, pady=12)
        center.pack(side="left", expand=True, fill="both", padx=8, pady=12)
        right.pack(side="left", expand=True, fill="both", padx=8, pady=12)

        # fields mapping to DB columns (left, center, right)
        left_fields = [
            ("nome", "Nome Colaborador"),
            ("identidade", "Identidade"),
            ("nome_mae", "Nome da mãe"),
            ("nome_pai", "Nome do pai"),
            ("cpf", "CPF"),
            ("cep", "CEP"),
            ("endereco", "Endereço"),
            ("numero", "Número"),
            ("bairro", "Bairro"),
            ("complemento", "Complemento"),
            ("nascimento", "Data de Nascimento"),
            ("telefone", "Telefone"),
            ("email", "E-mail"),
        ]
        center_fields = [
            ("cargo", "Cargo"),
            ("salario_inicial", "Salário Inicial"),
            ("salario_bruto", "Salário Bruto"),
            ("optante_passagem", "Optante por passagem (S/N)"),
            ("valor_passagem", "Valor passagem"),
            ("abono_salarial", "Abono salarial (S/N)"),
            ("valor_abono", "Valor abono"),
            ("salario_liquido", "Salário líquido (auto)"),
            ("fim_contrato", "Fim do contrato (texto)")
        ]
        right_fields = [
            ("empresa", "Nome da empresa"),
            ("endereco_empresa", "Endereço da empresa"),
            ("numero_empresa", "Número empresa"),
            ("cidade", "Cidade"),
            ("bairro_empresa", "Bairro empresa"),
            ("cnpj", "CNPJ"),
            ("telefone_empresa", "Telefone da empresa"),
            ("email_empresa", "E-mail da empresa"),
            ("anexo_pdf", "Anexo PDF (caminho)")
        ]

        # store entries
        self.form_vars = {}
        def make_field(container, key, label_text):
            lbl = ctk.CTkLabel(container, text=label_text)
            lbl.pack(anchor="w", pady=(6,2))
            ent = ctk.CTkEntry(container)
            ent.pack(fill="x", pady=(0,6))
            self.form_vars[key] = ent
            return ent

        for k, label in left_fields:
            make_field(left, k, label)
        for k, label in center_fields:
            make_field(center, k, label)
        for k, label in right_fields:
            make_field(right, k, label)

        # attach PDF button for anexo_pdf
        def attach_pdf():
            path = filedialog.askopenfilename(title="Selecionar PDF de anexo", filetypes=[("PDF files", "*.pdf")])
            if not path:
                return
            self.form_vars["anexo_pdf"].delete(0, "end")
            self.form_vars["anexo_pdf"].insert(0, path)

        attach_btn = ctk.CTkButton(right, text="Anexar PDF", command=attach_pdf)
        attach_btn.pack(pady=(0,6))

        # action buttons
        actions = ctk.CTkFrame(card)
        actions.place(relx=0.5, rely=0.93, anchor="s")
        self.btn_save = ctk.CTkButton(actions, text="Salvar", width=110, command=self.on_salvar)
        self.btn_update = ctk.CTkButton(actions, text="Atualizar", width=110, command=self.on_atualizar)
        self.btn_delete = ctk.CTkButton(actions, text="Excluir", width=110, command=self.on_excluir)
        self.btn_clear = ctk.CTkButton(actions, text="Limpar", width=110, command=self.on_limpar)
        self.btn_pdf = ctk.CTkButton(actions, text="Gerar Contracheque (PDF)", width=200, command=self.on_gerar_pdf_selected)
        for w in (self.btn_save, self.btn_update, self.btn_delete, self.btn_clear, self.btn_pdf):
            w.pack(side="left", padx=8)

    # -----------------------
    # Aba Registros (Treeview)
    def create_registros_tab(self):
        frame = ctk.CTkFrame(self.tab_reg)
        frame.pack(fill="both", expand=True, padx=8, pady=8)

        top = ctk.CTkFrame(frame)
        top.pack(fill="x", pady=(6,8))
        self.search_var = ctk.CTkEntry(top, placeholder_text="Buscar por nome ou cargo...")
        self.search_var.pack(side="left", padx=(8,4), fill="x", expand=True)
        ctk.CTkButton(top, text="Buscar", width=100, command=self.on_buscar).pack(side="left", padx=4)
        # quick action buttons
        ctk.CTkButton(top, text="Gerar Contracheque", width=140, command=self.on_gerar_pdf_selected).pack(side="left", padx=6)
        ctk.CTkButton(top, text="Importar Excel/CSV", width=140, command=self.on_import).pack(side="left", padx=6)
        ctk.CTkButton(top, text="Exportar Excel/CSV", width=140, command=self.on_export).pack(side="left", padx=6)
        ctk.CTkButton(top, text="Backup DB", width=120, command=self.on_backup).pack(side="left", padx=6)
        ctk.CTkButton(top, text="Restaurar DB", width=120, command=self.on_restore).pack(side="left", padx=6)

        # Tree view area
        tv_frame = ctk.CTkFrame(frame)
        tv_frame.pack(fill="both", expand=True, padx=6, pady=6)

        cols = [c[0] for c in BASE_COLUMNS]
        self.tree = ttk.Treeview(tv_frame, columns=cols, show="headings")
        # headings
        for col in cols:
            self.tree.heading(col, text=col.capitalize())
            # column defaults
            if col == "id":
                self.tree.column(col, width=60, anchor="center", stretch=False)
            elif col in ("nome", "empresa", "cargo"):
                self.tree.column(col, width=220, anchor="w")
            else:
                self.tree.column(col, width=140, anchor="center")
        # scrollbars
        ysb = ttk.Scrollbar(tv_frame, orient="vertical", command=self.tree.yview)
        xsb = ttk.Scrollbar(tv_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscroll=ysb.set, xscroll=xsb.set)
        ysb.pack(side="right", fill="y")
        xsb.pack(side="bottom", fill="x")
        self.tree.pack(fill="both", expand=True, side="left")
        # zebra tags
        self.tree.tag_configure('odd', background='#f0f0f0')
        self.tree.tag_configure('even', background='#e0e0e0')

        # bind selection / double click edit
        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)
        self.tree.bind("<Double-1>", self.on_double_click_cell)

        # navigation buttons
        nav = ctk.CTkFrame(frame)
        nav.pack(fill="x", pady=6)
        self.idx_label = ctk.CTkLabel(nav, text="Registros: 0")
        self.idx_label.pack(side="left", padx=8)
        ctk.CTkButton(nav, text="<< Primeiro", command=self.on_first).pack(side="left", padx=6)
        ctk.CTkButton(nav, text="< Anterior", command=self.on_prev).pack(side="left", padx=6)
        ctk.CTkButton(nav, text="Próximo >", command=self.on_next).pack(side="left", padx=6)
        ctk.CTkButton(nav, text="Último >>", command=self.on_last).pack(side="left", padx=6)

        # load data
        self.current_index = 0
        self.records_cache = []
        self.reload_records()

    # -----------------------
    # Actions: form handlers
    def on_salvar(self):
        try:
            d = {}
            for col in [c[0] for c in BASE_COLUMNS if c[0] != "id"]:
                v = self.form_vars[col].get() if hasattr(self.form_vars[col], "get") else ""
                d[col] = v
            # calculate salario_liquido if not provided
            try:
                bruto = float(d.get("salario_bruto") or 0)
            except Exception:
                bruto = 0
            try:
                passagem = float(d.get("valor_passagem") or 0)
            except Exception:
                passagem = 0
            try:
                abono = float(d.get("valor_abono") or 0)
            except Exception:
                abono = 0
            d["salario_liquido"] = round(bruto - (passagem + abono), 2)
            inserir_colaborador(d)
            messagebox.showinfo("Sucesso", "Colaborador salvo.")
            self.reload_records()
            self.on_limpar()
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao salvar:\n{e}\n\n{traceback.format_exc()}")

    def on_atualizar(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Aviso", "Selecione um registro para atualizar.")
            return
        id_ = int(self.tree.item(sel[0], "values")[0])
        d = {}
        for col in [c[0] for c in BASE_COLUMNS if c[0] != "id"]:
            d[col] = self.form_vars[col].get()
        # recalc
        try:
            bruto = float(d.get("salario_bruto") or 0)
            passagem = float(d.get("valor_passagem") or 0)
            abono = float(d.get("valor_abono") or 0)
            d["salario_liquido"] = round(bruto - (passagem + abono), 2)
        except Exception:
            pass
        atualizar_colaborador_db(id_, d)
        messagebox.showinfo("Atualizado", "Registro atualizado.")
        self.reload_records()

    def on_excluir(self):
        sel = self.tree.selection()
        if not sel:
            return
        if not messagebox.askyesno("Confirmar", "Deseja realmente excluir o registro?"):
            return
        id_ = int(self.tree.item(sel[0], "values")[0])
        excluir_colaborador_db(id_)
        messagebox.showinfo("Excluído", "Registro excluído.")
        self.reload_records()
        self.on_limpar()

    def on_limpar(self):
        for col in [c[0] for c in BASE_COLUMNS if c[0] != "id"]:
            widget = self.form_vars.get(col)
            if widget:
                try:
                    widget.delete(0, "end")
                except Exception:
                    pass

    # -----------------------
    # Tree / navigation operations
    def reload_records(self, filtro=""):
        rows = listar_colaboradores(filtro)
        self.records_cache = rows
        # clear tree
        for it in self.tree.get_children():
            self.tree.delete(it)
        # insert
        for idx, r in enumerate(rows):
            tag = 'odd' if idx % 2 == 0 else 'even'
            self.tree.insert("", "end", values=r, tags=(tag,))
        self.idx_label.configure(text=f"Registros: {len(rows)}")
        # auto select first
        if rows:
            self.tree.selection_set(self.tree.get_children()[0])
            self.tree.focus(self.tree.get_children()[0])
            self.on_tree_select(None)
            self.current_index = 0
        else:
            self.current_index = -1

    def on_buscar(self):
        filtro = self.search_var.get()
        self.reload_records(filtro)

    def on_tree_select(self, event):
        sel = self.tree.selection()
        if not sel:
            return
        vals = self.tree.item(sel[0], "values")
        # map to form
        cols = [c[0] for c in BASE_COLUMNS]
        for i, col in enumerate(cols):
            if col == "id":
                continue
            widget = self.form_vars.get(col)
            if widget:
                try:
                    widget.delete(0, "end")
                    widget.insert(0, vals[i] if vals[i] is not None else "")
                except Exception:
                    pass
        # update current_index
        try:
            # find index in cache by id
            id_ = int(vals[0])
            for idx, r in enumerate(self.records_cache):
                if r[0] == id_:
                    self.current_index = idx
                    break
        except Exception:
            pass

    def on_double_click_cell(self, event):
        # enable quick edit cell (creates entry over cell; updates DB only on Enter)
        region = self.tree.identify("region", event.x, event.y)
        if region != "cell":
            return
        row_id = self.tree.identify_row(event.y)
        col = self.tree.identify_column(event.x)  # "#1"
        if not row_id or not col:
            return
        col_index = int(col.replace("#", "")) - 1
        if col_index == 0:  # id não edita
            return
        x, y, width, height = self.tree.bbox(row_id, col)
        value = self.tree.set(row_id, column=col)
        edit = ctk.CTkEntry(self.tree)
        edit.place(x=x, y=y, width=width, height=height)
        edit.insert(0, value)
        edit.focus_set()
        def salvar_edicao(e=None):
            nv = edit.get()
            edit.destroy()
            self.tree.set(row_id, column=col, value=nv)
            # atualizar DB (somente essa coluna)
            id_ = int(self.tree.item(row_id, "values")[0])
            col_name = [c[0] for c in BASE_COLUMNS][col_index]
            # leitura row values into dict
            conn = conectar(); cur = conn.cursor()
            try:
                # type handling numeric
                if col_name in ("salario_bruto","valor_passagem","valor_abono","salario_liquido","salario_inicial"):
                    try:
                        nv_eval = float(nv.replace(",",".")) if isinstance(nv, str) else float(nv)
                    except Exception:
                        nv_eval = 0.0
                    cur.execute(f"UPDATE colaboradores SET {col_name}=? WHERE id=?", (nv_eval, id_))
                else:
                    cur.execute(f"UPDATE colaboradores SET {col_name}=? WHERE id=?", (nv, id_))
                conn.commit()
            except Exception:
                pass
            finally:
                conn.close()
            # reload to recalc zebra & values
            self.reload_records(self.search_var.get())
        edit.bind("<Return>", salvar_edicao)
        edit.bind("<FocusOut>", salvar_edicao)

    # navigation
    def on_first(self): 
        if not self.records_cache:
            return
        self.current_index = 0
        self._select_index(self.current_index)

    def on_prev(self):
        if self.current_index > 0:
            self.current_index -= 1
            self._select_index(self.current_index)

    def on_next(self):
        if self.current_index < len(self.records_cache) - 1:
            self.current_index += 1
            self._select_index(self.current_index)

    def on_last(self):
        if self.records_cache:
            self.current_index = len(self.records_cache) - 1
            self._select_index(self.current_index)

    def _select_index(self, idx):
        if idx < 0 or idx >= len(self.records_cache):
            return
        rid = self.tree.get_children()[idx]
        self.tree.selection_set(rid)
        self.tree.focus(rid)
        self.tree.see(rid)
        self.on_tree_select(None)

    # -----------------------
    # Import / Export / Backup / Restore / Attach
    def on_import(self):
        path = filedialog.askopenfilename(title="Importar (Excel ou CSV)", filetypes=[("Excel/CSV", "*.xlsx;*.xls;*.csv")])
        if not path:
            return
        try:
            if path.lower().endswith((".xls", ".xlsx")):
                if pd is None:
                    messagebox.showerror("Erro", "pandas não instalado. Instale pandas e openpyxl para importar Excel.")
                    return
                ok, msg = import_excel(path)
            else:
                ok, msg = import_csv(path)
            if ok:
                messagebox.showinfo("Importar", msg)
                self.reload_records()
            else:
                messagebox.showerror("Importar", msg)
        except Exception as e:
            messagebox.showerror("Erro", f"Falha na importação:\n{e}")

    def on_export(self):
        path = filedialog.asksaveasfilename(title="Exportar (CSV/Excel)", defaultextension=".csv", filetypes=[("CSV", "*.csv"), ("Excel", "*.xlsx")])
        if not path:
            return
        try:
            if path.lower().endswith(".xlsx"):
                ok, msg = export_excel(path)
            else:
                ok, msg = export_csv(path)
            if ok:
                messagebox.showinfo("Exportar", msg)
            else:
                messagebox.showerror("Exportar", msg)
        except Exception as e:
            messagebox.showerror("Erro", f"Falha na exportação:\n{e}")

    def on_backup(self):
        path = filedialog.asksaveasfilename(title="Salvar backup do DB", defaultextension=".db", initialfile=f"employees_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db")
        if not path:
            return
        try:
            shutil.copy2(DB_PATH, path)
            messagebox.showinfo("Backup", f"Backup salvo em:\n{path}")
        except Exception as e:
            messagebox.showerror("Erro", f"Falha no backup:\n{e}")

    def on_restore(self):
        path = filedialog.askopenfilename(title="Selecionar backup para restaurar", filetypes=[("DB", "*.db")])
        if not path:
            return
        if not messagebox.askyesno("Restaurar", "Restaurar sobrescreverá o banco atual. Continuar?"):
            return
        try:
            shutil.copy2(path, DB_PATH)
            messagebox.showinfo("Restaurar", "Backup restaurado. Reinicie o aplicativo.")
            # optional: reload
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao restaurar:\n{e}")

    # -----------------------
    # Gerar contracheque para registro selecionado
    def on_gerar_pdf_selected(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Aviso", "Selecione um registro para gerar o contracheque.")
            return
        vals = self.tree.item(sel[0], "values")
        try:
            out = gerar_contracheque_pdf(vals)
            messagebox.showinfo("OK", f"Contracheque gerado:\n{out}")
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao gerar o PDF:\n{e}\n\nVerifique se reportlab está instalado.")

    # -----------------------
    # Menu
    def create_menu(self):
        menubar = ctk.CTkFrame(self, height=40)
        menubar.pack(side="bottom", fill="x")
        # Add quick small buttons (simulate menu)
        ctk.CTkButton(menubar, text="Importar", width=120, command=self.on_import).pack(side="left", padx=6, pady=6)
        ctk.CTkButton(menubar, text="Exportar", width=120, command=self.on_export).pack(side="left", padx=6, pady=6)
        ctk.CTkButton(menubar, text="Backup", width=120, command=self.on_backup).pack(side="left", padx=6, pady=6)
        ctk.CTkButton(menubar, text="Restaurar", width=120, command=self.on_restore).pack(side="left", padx=6, pady=6)

    # -----------------------
    def on_close(self):
        # aqui poderia fechar conexões, etc.
        if messagebox.askokcancel("Sair", "Deseja sair do sistema?"):
            self.destroy()

# -----------------------
# Exec
def main():
    inicializar_sistema()
    app = App()
    app.mainloop()

if __name__ == "__main__":
    main()
