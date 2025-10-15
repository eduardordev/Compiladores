# Compiscript IDE Completo con AST y TAC integrados
import os, sys, tempfile, subprocess
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog

HERE = os.path.dirname(__file__)
ROOT = os.path.abspath(os.path.join(HERE, '..'))


class CompiscriptIDE(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('Compiscript IDE')
        self.geometry('1200x800')

        # estado
        self.current_file = None
        self.status = tk.StringVar(value='Listo')
        self.cursor_pos = tk.StringVar(value='Ln 1, Col 1')

        # temas
        self.themes = {
            'light': {
                'bg': '#ffffff', 'fg': '#000000',
                'editor_bg': '#ffffff', 'gutter_bg': '#f3f3f3',
                'error_bg': '#fff5f5', 'status_bg': '#eeeeee'
            },
            'dark': {
                'bg': '#1e1e1e', 'fg': '#d4d4d4',
                'editor_bg': '#1e1e1e', 'gutter_bg': '#252526',
                'error_bg': '#2a1a1a', 'status_bg': '#333333'
            }
        }
        self.current_theme = 'dark'

        self.create_menu()
        self.create_widgets()
        self.apply_theme(self.current_theme)
        self.bind_shortcuts()

    # ======================================
    # MENÚ
    # ======================================
    def create_menu(self):
        menubar = tk.Menu(self)

        # --- Archivo ---
        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label='Abrir', command=self.abrir, accelerator='Ctrl+O')
        filemenu.add_command(label='Guardar', command=self.guardar, accelerator='Ctrl+S')
        filemenu.add_command(label='Guardar como...', command=self.guardar_como)
        filemenu.add_separator()
        filemenu.add_command(label='Salir', command=self.quit)
        menubar.add_cascade(label='Archivo', menu=filemenu)

        # --- Edición ---
        editmenu = tk.Menu(menubar, tearoff=0)
        editmenu.add_command(label='Buscar', command=self.buscar, accelerator='Ctrl+F')
        editmenu.add_command(label='Reemplazar', command=self.reemplazar, accelerator='Ctrl+H')
        menubar.add_cascade(label='Edición', menu=editmenu)

        # --- Herramientas ---
        toolsmenu = tk.Menu(menubar, tearoff=0)
        toolsmenu.add_command(label='Compilar', command=self.compilar, accelerator='F5')
        toolsmenu.add_command(label='Ver AST', command=self.ver_ast)
        toolsmenu.add_command(label='Ver TAC', command=self.ver_tac)
        menubar.add_cascade(label='Herramientas', menu=toolsmenu)

        # --- Vista ---
        viewmenu = tk.Menu(menubar, tearoff=0)
        viewmenu.add_command(label='Cambiar tema (claro/oscuro)', command=self.toggle_theme)
        menubar.add_cascade(label='Ver', menu=viewmenu)

        # --- Ayuda ---
        helpmenu = tk.Menu(menubar, tearoff=0)
        helpmenu.add_command(label='Acerca de', command=self.acerca_de)
        menubar.add_cascade(label='Ayuda', menu=helpmenu)

        self.config(menu=menubar)

    # ======================================
    # INTERFAZ PRINCIPAL
    # ======================================
    def create_widgets(self):
        container = ttk.Frame(self)
        container.pack(fill='both', expand=True)

        # Toolbar
        toolbar = ttk.Frame(container)
        toolbar.pack(fill='x')
        btn_open = ttk.Button(toolbar, text='📂 Abrir', command=self.abrir)
        btn_save = ttk.Button(toolbar, text='💾 Guardar', command=self.guardar)
        btn_run = ttk.Button(toolbar, text='▶ Compilar', command=self.compilar)
        btn_ast = ttk.Button(toolbar, text='🌳 AST', command=self.ver_ast)
        btn_tac = ttk.Button(toolbar, text='⚙️ TAC', command=self.ver_tac)
        btn_theme = ttk.Button(toolbar, text='🌓 Tema', command=self.toggle_theme)
        for b in (btn_open, btn_save, btn_run, btn_ast, btn_tac, btn_theme):
            b.pack(side='left', padx=3, pady=2)

        # Panel principal
        main = ttk.PanedWindow(container, orient='horizontal')
        main.pack(fill='both', expand=True)

        # Sidebar izquierda
        sidebar = ttk.Frame(main, width=50)
        main.add(sidebar, weight=0)
        for ico, cmd, tip in [('📁', self.abrir, 'Abrir'),
                              ('💾', self.guardar, 'Guardar'),
                              ('⚙️', self.compilar, 'Compilar')]:
            b = ttk.Button(sidebar, text=ico, width=3, command=cmd)
            b.pack(pady=6)

        # Centro: Editor + panel inferior
        center = ttk.Frame(main)
        main.add(center, weight=3)

        center_paned = ttk.PanedWindow(center, orient='vertical')
        center_paned.pack(fill='both', expand=True)

        # Editor de código
        editor_container = ttk.Frame(center_paned)
        center_paned.add(editor_container, weight=3)

        self.line_numbers = tk.Text(editor_container, width=5, padx=4, takefocus=0,
                                    border=0, state='disabled', font=('Consolas', 11))
        self.line_numbers.pack(side='left', fill='y')

        editor_frame = ttk.Frame(editor_container)
        editor_frame.pack(side='left', fill='both', expand=True)
        yscroll = ttk.Scrollbar(editor_frame, orient='vertical')
        xscroll = ttk.Scrollbar(editor_frame, orient='horizontal')
        self.text = tk.Text(editor_frame, wrap='none', font=('Consolas', 11),
                            undo=True, yscrollcommand=yscroll.set, xscrollcommand=xscroll.set)
        yscroll.config(command=self.text.yview)
        xscroll.config(command=self.text.xview)
        yscroll.pack(side='right', fill='y')
        xscroll.pack(side='bottom', fill='x')
        self.text.pack(side='left', fill='both', expand=True)
        self.text.bind('<KeyRelease>', self.on_text_change)
        self.text.bind('<ButtonRelease>', self.on_text_change)
        self.update_line_numbers()

        # Panel inferior dividido (Errores, AST, TAC)
        bottom_panel = ttk.PanedWindow(center_paned, orient='horizontal')
        center_paned.add(bottom_panel, weight=1)

        self.errors_panel = self._create_output_panel(bottom_panel, '🧩 Errores / Consola')
        self.ast_panel = self._create_output_panel(bottom_panel, '🌳 AST')
        self.tac_panel = self._create_output_panel(bottom_panel, '⚙️ TAC')

        bottom_panel.add(self.errors_panel['frame'], weight=1)
        bottom_panel.add(self.ast_panel['frame'], weight=1)
        bottom_panel.add(self.tac_panel['frame'], weight=1)

        # Status bar
        statusbar = ttk.Frame(self)
        statusbar.pack(fill='x')
        lbl_status = ttk.Label(statusbar, textvariable=self.status, anchor='w')
        lbl_status.pack(side='left', fill='x', expand=True)
        lbl_pos = ttk.Label(statusbar, textvariable=self.cursor_pos, anchor='e')
        lbl_pos.pack(side='right')

    # ======================================
    # PANELES DE SALIDA
    # ======================================
    def _create_output_panel(self, parent, title):
        frame = ttk.Frame(parent)
        label = ttk.Label(frame, text=title, anchor='center', font=('Consolas', 10, 'bold'))
        label.pack(fill='x')
        text = tk.Text(frame, height=10, font=('Consolas', 10))
        text.pack(fill='both', expand=True)
        text.config(state='disabled')
        return {'frame': frame, 'text': text}

    # ======================================
    # FUNCIONES DE UTILIDAD
    # ======================================
    def bind_shortcuts(self):
        self.bind('<Control-o>', lambda e: self.abrir())
        self.bind('<Control-s>', lambda e: self.guardar())
        self.bind('<F5>', lambda e: self.compilar())

    def update_line_numbers(self, event=None):
        self.line_numbers.config(state='normal')
        self.line_numbers.delete('1.0', 'end')
        lines = self.text.get('1.0', 'end-1c').split('\n')
        for i in range(1, len(lines)+1):
            self.line_numbers.insert('end', f'{i}\n')
        self.line_numbers.config(state='disabled')

    def update_cursor_pos(self):
        try:
            idx = self.text.index('insert')
            line, col = idx.split('.')
            self.cursor_pos.set(f'Ln {line}, Col {int(col)+1}')
        except Exception:
            self.cursor_pos.set('Ln ?, Col ?')

    def on_text_change(self, event=None):
        self.update_line_numbers()
        self.update_cursor_pos()

    # ======================================
    # BÚSQUEDA Y REEMPLAZO
    # ======================================
    def buscar(self):
        term = simpledialog.askstring('Buscar', 'Texto a buscar:')
        if not term:
            return
        self.text.tag_remove('search', '1.0', 'end')
        idx = '1.0'
        found = False
        while True:
            idx = self.text.search(term, idx, nocase=1, stopindex='end')
            if not idx:
                break
            lastidx = f'{idx}+{len(term)}c'
            self.text.tag_add('search', idx, lastidx)
            found = True
            idx = lastidx
        if found:
            self.text.tag_config('search', background='yellow', foreground='black')
            self.status.set(f'Resultados para "{term}"')
        else:
            messagebox.showinfo('Buscar', f'No se encontró: {term}')

    def reemplazar(self):
        term = simpledialog.askstring('Reemplazar', 'Texto a buscar:')
        if not term:
            return
        repl = simpledialog.askstring('Reemplazar', f'Reemplazar "{term}" por:')
        if repl is None:
            return
        content = self.text.get('1.0', 'end-1c').replace(term, repl)
        self.text.delete('1.0', 'end')
        self.text.insert('1.0', content)
        self.update_line_numbers()
        self.status.set(f'Reemplazado "{term}" por "{repl}"')

    # ======================================
    # OPERACIONES DE ARCHIVO
    # ======================================
    def abrir(self):
        path = filedialog.askopenfilename(filetypes=[('Compiscript', '*.cps'), ('Todos', '*.*')])
        if not path: return
        self.current_file = path
        with open(path, 'r', encoding='utf-8') as f:
            self.text.delete('1.0', 'end')
            self.text.insert('1.0', f.read())
        self.status.set(f'Abrí: {os.path.basename(path)}')
        self.update_line_numbers()
        self.update_cursor_pos()

    def guardar(self):
        if not self.current_file:
            self.guardar_como()
            return
        with open(self.current_file, 'w', encoding='utf-8') as f:
            f.write(self.text.get('1.0', 'end-1c'))
        self.status.set(f'Guardé: {os.path.basename(self.current_file)}')

    def guardar_como(self):
        path = filedialog.asksaveasfilename(defaultextension='.cps',
                                            filetypes=[('Compiscript', '*.cps')])
        if not path: return
        self.current_file = path
        self.guardar()

    # ======================================
    # COMPILACIÓN Y ANÁLISIS
    # ======================================
    def compilar(self):
        code = self.text.get('1.0', 'end-1c')
        with tempfile.NamedTemporaryFile('w', delete=False, suffix='.cps', encoding='utf-8') as tmp:
            tmp.write(code)
            tmp_path = tmp.name
        try:
            p = subprocess.run(
                [sys.executable, os.path.join(ROOT, 'Driver.py'), tmp_path],
                capture_output=True, text=True
            )
            self._update_output(self.errors_panel['text'], p.stdout + p.stderr)
            if p.returncode == 0:
                self.status.set('✔ Compilación exitosa')
            else:
                self.status.set('❌ Errores detectados')
        finally:
            os.unlink(tmp_path)

    def ver_ast(self):
        code = self.text.get('1.0', 'end-1c')
        with tempfile.NamedTemporaryFile('w', delete=False, suffix='.cps', encoding='utf-8') as tmp:
            tmp.write(code)
            tmp_path = tmp.name
        try:
            p = subprocess.run(
                [sys.executable, os.path.join(ROOT, 'Driver.py'), tmp_path, '--ast'],
                capture_output=True, text=True
            )
            self._update_output(self.ast_panel['text'], p.stdout)
        finally:
            os.unlink(tmp_path)

    def ver_tac(self):
        code = self.text.get('1.0', 'end-1c')
        with tempfile.NamedTemporaryFile('w', delete=False, suffix='.cps', encoding='utf-8') as tmp:
            tmp.write(code)
            tmp_path = tmp.name
        try:
            p = subprocess.run(
                [sys.executable, os.path.join(ROOT, 'Driver.py'), tmp_path, '--tac'],
                capture_output=True, text=True
            )
            self._update_output(self.tac_panel['text'], p.stdout)
        finally:
            os.unlink(tmp_path)

    # ======================================
    # ACTUALIZACIÓN DE PANELES DE SALIDA
    # ======================================
    def _update_output(self, panel, text):
        panel.config(state='normal')
        panel.delete('1.0', 'end')
        panel.insert('end', text if text.strip() else '(sin salida)')
        panel.config(state='disabled')

    # ======================================
    # TEMA Y ACERCA DE
    # ======================================
    def apply_theme(self, theme_name):
        t = self.themes.get(theme_name, self.themes['dark'])
        self.configure(bg=t['bg'])
        try:
            self.text.config(background=t['editor_bg'], foreground=t['fg'], insertbackground=t['fg'])
            self.line_numbers.config(background=t['gutter_bg'], foreground=t['fg'])
            for panel in [self.errors_panel, self.ast_panel, self.tac_panel]:
                panel['text'].config(background=t['error_bg'], foreground=t['fg'])
        except Exception:
            pass

    def toggle_theme(self):
        self.current_theme = 'light' if self.current_theme == 'dark' else 'dark'
        self.apply_theme(self.current_theme)
        self.status.set(f'Tema: {self.current_theme}')

    def acerca_de(self):
        messagebox.showinfo('Acerca de', 'Compiscript IDE\nCompis 2\nAutor: Las Momias Carnet 19')


if __name__ == '__main__':
    CompiscriptIDE().mainloop()
