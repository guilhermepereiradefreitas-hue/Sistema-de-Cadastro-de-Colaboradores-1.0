import os
import shutil
import sqlite3
import uuid
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk

# Optional libraries for export
try:
    import pandas as pd
except Exception:
    pd = None

try:
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfgen import canvas as pdf_canvas
    from reportlab.lib.utils import ImageReader
except Exception:
    pdf_canvas = None

# Paths
APP_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(APP_DIR, 'employees.db')
PHOTOS_DIR = os.path.join(APP_DIR, 'photos')
LOGO_PATH = os.path.join(APP_DIR, 'logo.png')

os.makedirs(PHOTOS_DIR, exist_ok=True)

# Database connection
conn = sqlite3.connect(DB_PATH)
conn.row_factory = sqlite3.Row
c = conn.cursor()

# Create table if not exists (includes the new fields)
c.execute('''
CREATE TABLE IF NOT EXISTS employees (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT,
    cidade TEXT,
    endereco TEXT,
    numero TEXT,
    bairro TEXT,
    loja TEXT,
    endereco_loja TEXT,
    cnpj_loja TEXT,
    cargo TEXT,
    salario REAL,
    desconto_percent REAL,
    salario_liquido REAL,
    foto_path TEXT,
    data_admissao TEXT,
    fim_contrato TEXT,
    observacoes TEXT
)
''')
conn.commit()

# Ensure any older DB gets new columns (safe ALTER TABLE for missing columns)
def ensure_columns():
    cols_needed = [
        ('numero','TEXT'), ('endereco_loja','TEXT'), ('cnpj_loja','TEXT'), ('observacoes','TEXT')
    ]
    cur = conn.cursor()
    cur.execute("PRAGMA table_info(employees)")
    existing = [r['name'] for r in cur.fetchall()]
    for col, ctype in cols_needed:
        if col not in existing:
            try:
                cur.execute(f"ALTER TABLE employees ADD COLUMN {col} {ctype}")
            except Exception:
                pass
    conn.commit()

ensure_columns()

# Helpers

def calcular_salario_liquido(salario, desconto_percent):
    try:
        s = float(salario)
        d = float(desconto_percent) if desconto_percent not in (None, '') else 0.0
        return round(s - (s * d / 100.0), 2)
    except Exception:
        return 0.0


def salvar_foto(src_path):
    if not src_path or not os.path.exists(src_path):
        return ''
    ext = os.path.splitext(src_path)[1]
    new_name = f"{uuid.uuid4().hex}{ext}"
    dst = os.path.join(PHOTOS_DIR, new_name)
    shutil.copy2(src_path, dst)
    return dst

# UI
root = tk.Tk()
root.title('Sistema de Cadastro de Funcionários')
root.geometry('1250x820')
style = ttk.Style()
style.theme_use('clam')
style.configure('Treeview', rowheight=26)

# Header with logo
header = ttk.Frame(root)
header.pack(fill='x', padx=8, pady=6)
logo_lbl = ttk.Label(header)
logo_lbl.pack(side='left')

def load_logo_preview():
    if os.path.exists(LOGO_PATH):
        try:
            img = Image.open(LOGO_PATH)
            img.thumbnail((220,90))
            ph = ImageTk.PhotoImage(img)
            logo_lbl.image = ph
            logo_lbl.configure(image=ph)
        except Exception:
            pass

load_logo_preview()

# Layout
main_pane = ttk.Panedwindow(root, orient='horizontal')
main_pane.pack(fill='both', expand=True, padx=8, pady=8)

form_frame = ttk.Frame(main_pane, width=480)
main_pane.add(form_frame, weight=1)

table_frame = ttk.Frame(main_pane)
main_pane.add(table_frame, weight=3)

# Form fields (including new ones)
field_order = [
    ('nome','Nome'), ('cidade','Cidade'), ('endereco','Endereço'), ('numero','Número'),
    ('bairro','Bairro'), ('loja','Loja'), ('endereco_loja','Endereço Loja'), ('cnpj_loja','CNPJ Loja'),
    ('cargo','Cargo'), ('salario','Salário (bruto)'), ('desconto_percent','% Desconto'), ('salario_liquido','Salário Líquido'),
    ('data_admissao','Data de Admissão'), ('fim_contrato','Fim do Contrato'), ('observacoes','Observações')
]

fields = {}
row = 0
for key,label in field_order:
    ttk.Label(form_frame, text=label).grid(column=0, row=row, sticky='w', padx=6, pady=4)
    ent = ttk.Entry(form_frame)
    ent.grid(column=1, row=row, sticky='ew', padx=6, pady=4)
    if key == 'salario_liquido':
        ent.configure(state='readonly')
    fields[key] = ent
    row += 1

form_frame.columnconfigure(1, weight=1)

# Photo
photo_preview = ttk.Label(form_frame)
photo_preview.grid(column=0, row=row, columnspan=2, pady=6)
selected_photo = None

def selecionar_foto():
    global selected_photo
    p = filedialog.askopenfilename(title='Foto do Colaborador', filetypes=[('Imagens','*.png;*.jpg;*.jpeg;*.bmp;*.gif')])
    if not p:
        return
    selected_photo = p
    fields['foto_path'] = p  # temporary
    try:
        img = Image.open(p)
        img.thumbnail((220,220))
        ph = ImageTk.PhotoImage(img)
        photo_preview.image = ph
        photo_preview.configure(image=ph)
    except Exception:
        pass

ttk.Button(form_frame, text='Selecionar Foto', command=selecionar_foto).grid(column=0, row=row+1, sticky='w', padx=6)

# Buttons
current_id = None

def preencher_salario(event=None):
    s = fields['salario'].get()
    d = fields['desconto_percent'].get()
    val = calcular_salario_liquido(s,d)
    fields['salario_liquido'].configure(state='normal')
    fields['salario_liquido'].delete(0, tk.END)
    fields['salario_liquido'].insert(0, str(val))
    fields['salario_liquido'].configure(state='readonly')

fields['salario'].bind('<FocusOut>', preencher_salario)
fields['desconto_percent'].bind('<FocusOut>', preencher_salario)

# CRUD
def limpar_form():
    global current_id, selected_photo
    current_id = None
    selected_photo = None
    for k in [f[0] for f in field_order]:
        fields[k].configure(state='normal')
        fields[k].delete(0, tk.END)
    photo_preview.configure(image='')

def salvar():
    global selected_photo
    data = {k: fields[k].get().strip() for k,_ in field_order}
    if not data['nome']:
        messagebox.showwarning('Validação','Nome é obrigatório')
        return
    foto_db = ''
    if selected_photo:
        foto_db = salvar_foto(selected_photo)
    salario_liq = calcular_salario_liquido(data['salario'], data['desconto_percent'])
    with conn:
        conn.execute('''INSERT INTO employees (nome,cidade,endereco,numero,bairro,loja,endereco_loja,cnpj_loja,cargo,salario,desconto_percent,salario_liquido,foto_path,data_admissao,fim_contrato,observacoes)
                        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)''', (
            data['nome'], data['cidade'], data['endereco'], data['numero'], data['bairro'], data['loja'], data['endereco_loja'], data['cnpj_loja'],
            data['cargo'], float(data['salario'] or 0), float(data['desconto_percent'] or 0), salario_liq, foto_db, data['data_admissao'], data['fim_contrato'], data['observacoes']
        ))
    messagebox.showinfo('Sucesso','Registro salvo')
    carregar_tabela()
    limpar_form()

def atualizar():
    global current_id, selected_photo
    if not current_id:
        messagebox.showwarning('Seleção','Selecione um registro para atualizar')
        return
    data = {k: fields[k].get().strip() for k,_ in field_order}
    foto_db = ''
    if selected_photo:
        foto_db = salvar_foto(selected_photo)
    salario_liq = calcular_salario_liquido(data['salario'], data['desconto_percent'])
    with conn:
        conn.execute('''UPDATE employees SET nome=?,cidade=?,endereco=?,numero=?,bairro=?,loja=?,endereco_loja=?,cnpj_loja=?,cargo=?,salario=?,desconto_percent=?,salario_liquido=?,foto_path=?,data_admissao=?,fim_contrato=?,observacoes=? WHERE id=?''', (
            data['nome'], data['cidade'], data['endereco'], data['numero'], data['bairro'], data['loja'], data['endereco_loja'], data['cnpj_loja'],
            data['cargo'], float(data['salario'] or 0), float(data['desconto_percent'] or 0), salario_liq, foto_db, data['data_admissao'], data['fim_contrato'], data['observacoes'], current_id
        ))
    messagebox.showinfo('Sucesso','Registro atualizado')
    carregar_tabela()
    limpar_form()

def deletar():
    global current_id
    if not current_id:
        messagebox.showwarning('Seleção','Selecione um registro para deletar')
        return
    if not messagebox.askyesno('Confirmar','Deletar este registro?'):
        return
    with conn:
        conn.execute('DELETE FROM employees WHERE id=?', (current_id,))
    messagebox.showinfo('Sucesso','Deletado')
    carregar_tabela()
    limpar_form()

# Filters and pagination
page_size = 30
current_page = 1
total_pages = 1
filtro_nome = tk.StringVar()
filtro_cargo = tk.StringVar()
filtro_loja = tk.StringVar()

def build_filter_sql():
    filtro_sql = 'WHERE 1=1'
    params = []
    if filtro_nome.get().strip():
        filtro_sql += ' AND nome LIKE ?'
        params.append(f'%{filtro_nome.get().strip()}%')
    if filtro_cargo.get().strip():
        filtro_sql += ' AND cargo LIKE ?'
        params.append(f'%{filtro_cargo.get().strip()}%')
    if filtro_loja.get().strip():
        filtro_sql += ' AND loja LIKE ?'
        params.append(f'%{filtro_loja.get().strip()}%')
    return filtro_sql, params

cols = ('id','nome','cidade','endereco','numero','bairro','loja','endereco_loja','cnpj_loja','cargo','salario','desconto_percent','salario_liquido','data_admissao','fim_contrato')

# Treeview with scrollbars
trv_frame = ttk.Frame(table_frame)
trv_frame.pack(fill='both', expand=True, padx=6, pady=6)

scroll_y = ttk.Scrollbar(trv_frame, orient='vertical')
scroll_x = ttk.Scrollbar(trv_frame, orient='horizontal')

trv = ttk.Treeview(trv_frame, columns=cols, show='headings', yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)
for c in cols:
    trv.heading(c, text=c.replace('_',' ').capitalize())
    trv.column(c, width=120)

scroll_y.config(command=trv.yview)
scroll_x.config(command=trv.xview)
scroll_y.pack(side='right', fill='y')
scroll_x.pack(side='bottom', fill='x')
trv.pack(fill='both', expand=True)

# Pagination label (defined before loading table)
pagination_frame = ttk.Frame(table_frame)
pagination_frame.pack(fill='x', pady=6)

btn_first = ttk.Button(pagination_frame, text='<< Primeiro')
btn_prev = ttk.Button(pagination_frame, text='< Anterior')
btn_next = ttk.Button(pagination_frame, text='Próximo >')
btn_last = ttk.Button(pagination_frame, text='Último >>')

btn_first.pack(side='left', padx=4)
btn_prev.pack(side='left', padx=4)
btn_next.pack(side='left', padx=4)
btn_last.pack(side='left', padx=4)

lbl_paginacao = ttk.Label(pagination_frame, text='Página 1 de 1')
lbl_paginacao.pack(side='right', padx=6)

# carregar_tabela respects filters
def carregar_tabela(page=1):
    global current_page, total_pages
    current_page = page
    for i in trv.get_children():
        trv.delete(i)

    filtro_sql, params = build_filter_sql()
    cur = conn.cursor()
    cur.execute(f'SELECT COUNT(*) as total FROM employees {filtro_sql}', params)
    total = cur.fetchone()['total']
    total_pages = max(1, (total + page_size - 1)//page_size)
    offset = (current_page - 1) * page_size

    query = f'''SELECT {', '.join(cols)} FROM employees {filtro_sql} ORDER BY id DESC LIMIT ? OFFSET ?'''
    cur.execute(query, (*params, page_size, offset))
    for row in cur.fetchall():
        trv.insert('', 'end', values=[row[c] for c in cols])

    lbl_paginacao.configure(text=f'Página {current_page} de {total_pages}')

# Pagination button commands
btn_first.config(command=lambda: carregar_tabela(1))
btn_prev.config(command=lambda: carregar_tabela(max(1, current_page-1)))
btn_next.config(command=lambda: carregar_tabela(min(total_pages, current_page+1)))
btn_last.config(command=lambda: carregar_tabela(total_pages))

# Filters UI
filter_frame = ttk.LabelFrame(table_frame, text='Filtros')
filter_frame.pack(fill='x', padx=6, pady=6)

ttk.Label(filter_frame, text='Nome').pack(side='left', padx=4)
ttk.Entry(filter_frame, textvariable=filtro_nome, width=18).pack(side='left')
ttk.Label(filter_frame, text='Cargo').pack(side='left', padx=4)
ttk.Entry(filter_frame, textvariable=filtro_cargo, width=18).pack(side='left')
ttk.Label(filter_frame, text='Loja').pack(side='left', padx=4)
ttk.Entry(filter_frame, textvariable=filtro_loja, width=18).pack(side='left')
ttk.Button(filter_frame, text='Buscar', command=lambda: carregar_tabela(1)).pack(side='left', padx=8)
ttk.Button(filter_frame, text='Limpar Filtros', command=lambda: [filtro_nome.set(''), filtro_cargo.set(''), filtro_loja.set(''), carregar_tabela(1)]).pack(side='left')

# Selection handling

def on_select(event):
    global current_id, selected_photo
    sel = trv.focus()
    if not sel:
        return
    vals = trv.item(sel,'values')
    emp_id = vals[0]
    cur = conn.cursor(); cur.execute('SELECT * FROM employees WHERE id=?', (emp_id,))
    r = cur.fetchone()
    if not r:
        return
    current_id = r['id']
    selected_photo = None
    # fill form fields
    for key, _ in field_order:
        if key in r.keys():
            fields[key].delete(0, tk.END)
            fields[key].insert(0, str(r[key] or ''))
    # show photo if exists
    foto = r['foto_path']
    if foto and os.path.exists(foto):
        try:
            img = Image.open(foto); img.thumbnail((220,220)); ph = ImageTk.PhotoImage(img)
            photo_preview.image = ph; photo_preview.configure(image=ph)
        except Exception:
            photo_preview.configure(image='')
    else:
        photo_preview.configure(image='')

trv.bind('<<TreeviewSelect>>', on_select)

# Export functions (respect filters)

def fetch_records_for_export():
    filtro_sql, params = build_filter_sql()
    cur = conn.cursor()
    cur.execute(f"SELECT * FROM employees {filtro_sql} ORDER BY id DESC", params)
    rows = [dict(r) for r in cur.fetchall()]
    return rows

def export_csv():
    path = filedialog.asksaveasfilename(defaultextension='.csv', filetypes=[('CSV','*.csv')])
    if not path:
        return
    rows = fetch_records_for_export()
    if not rows:
        messagebox.showinfo('Exportar','Nenhum registro para exportar')
        return
    keys = list(rows[0].keys())
    try:
        import csv
        with open(path, 'w', newline='', encoding='utf-8') as f:
            w = csv.DictWriter(f, fieldnames=keys)
            w.writeheader(); w.writerows(rows)
        messagebox.showinfo('Exportar','Exportado para CSV')
    except Exception as e:
        messagebox.showerror('Erro', str(e))

def export_excel():
    if pd is None:
        messagebox.showerror('Dependência','pandas não está instalado. Instale: pip install pandas openpyxl')
        return
    path = filedialog.asksaveasfilename(defaultextension='.xlsx', filetypes=[('Excel','*.xlsx')])
    if not path:
        return
    rows = fetch_records_for_export()
    if not rows:
        messagebox.showinfo('Exportar','Nenhum registro para exportar')
        return
    try:
        df = pd.DataFrame(rows)
        df.to_excel(path, index=False)
        messagebox.showinfo('Exportar','Exportado para Excel')
    except Exception as e:
        messagebox.showerror('Erro', str(e))

def export_pdf():
    if pdf_canvas is None:
        messagebox.showerror('Dependência','reportlab não está instalado. Instale: pip install reportlab')
        return
    path = filedialog.asksaveasfilename(defaultextension='.pdf', filetypes=[('PDF','*.pdf')])
    if not path:
        return
    rows = fetch_records_for_export()
    if not rows:
        messagebox.showinfo('Exportar','Nenhum registro para exportar')
        return
    try:
        c = pdf_canvas.Canvas(path, pagesize=A4)
        w, h = A4
        y = h - 50
        # logo if exists
        if os.path.exists(LOGO_PATH):
            try:
                img = Image.open(LOGO_PATH)
                img_w, img_h = img.size
                max_w = 120
                ratio = max_w / img_w
                img_reader = ImageReader(img)
                c.drawImage(img_reader, 40, y - (img_h*ratio), width=img_w*ratio, height=img_h*ratio)
            except Exception:
                pass
        c.setFont('Helvetica-Bold', 16)
        c.drawString(200, y, 'Relatório de Funcionários')
        y -= 40
        c.setFont('Helvetica', 10)
        for r in rows:
            line = f"{r['id']} - {r['nome']} | {r.get('cargo','')} | {r.get('loja','')} | Bruto: {r.get('salario','')} | Líquido: {r.get('salario_liquido','')}"
            c.drawString(40, y, line)
            y -= 16
            if y < 60:
                c.showPage()
                y = h - 40
                c.setFont('Helvetica', 10)
        c.save()
        messagebox.showinfo('Exportar','Exportado para PDF')
    except Exception as e:
        messagebox.showerror('Erro', str(e))

# Export buttons
export_frame = ttk.Frame(form_frame)
export_frame.grid(column=0, row=row+2, columnspan=2, pady=8)

ttk.Button(export_frame, text='Exportar CSV', command=export_csv).grid(column=0, row=0, padx=6)
ttk.Button(export_frame, text='Exportar Excel', command=export_excel).grid(column=1, row=0, padx=6)
ttk.Button(export_frame, text='Exportar PDF', command=export_pdf).grid(column=2, row=0, padx=6)

# CRUD buttons
btn_frame = ttk.Frame(form_frame)
btn_frame.grid(column=0, row=row+3, columnspan=2, pady=4)

ttk.Button(btn_frame, text='Salvar', command=salvar).grid(column=0, row=0, padx=6)
ttk.Button(btn_frame, text='Atualizar', command=atualizar).grid(column=1, row=0, padx=6)
ttk.Button(btn_frame, text='Deletar', command=deletar).grid(column=2, row=0, padx=6)
ttk.Button(btn_frame, text='Limpar', command=limpar_form).grid(column=3, row=0, padx=6)

# Filters controls (placed above treeview)
filter_controls = ttk.Frame(table_frame)
filter_controls.pack(fill='x', padx=6, pady=6)

ttk.Label(filter_controls, text='Nome:').pack(side='left', padx=4)
ttk.Entry(filter_controls, textvariable=filtro_nome, width=18).pack(side='left')
ttk.Label(filter_controls, text='Cargo:').pack(side='left', padx=4)
ttk.Entry(filter_controls, textvariable=filtro_cargo, width=18).pack(side='left')
ttk.Label(filter_controls, text='Loja:').pack(side='left', padx=4)
ttk.Entry(filter_controls, textvariable=filtro_loja, width=18).pack(side='left')
ttk.Button(filter_controls, text='Buscar', command=lambda: carregar_tabela(1)).pack(side='left', padx=8)

# Start
carregar_tabela(1)
root.mainloop()
