
# Compiscript IDE Completo
import os, sys, tempfile, subprocess
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog

HERE = os.path.dirname(__file__)
ROOT = os.path.abspath(os.path.join(HERE, '..'))

class ASTDialog(tk.Toplevel):
    def __init__(self, master, ast_text):
        super().__init__(master)
        self.title('AST Visual')
        self.geometry('600x400')
        text = tk.Text(self, wrap='none', font=('Consolas', 10))
        text.insert('1.0', ast_text)
        text.config(state='disabled')
        text.pack(fill='both', expand=True)

class CompiscriptIDE(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('Compiscript IDE')
        self.geometry('1100x700')

        self.current_file = None
        self.status = tk.StringVar(value='Listo')

        self.create_menu()
        self.create_widgets()
        self.bind_shortcuts()

    def create_menu(self):
        menubar = tk.Menu(self)
        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label='Abrir', command=self.abrir, accelerator='Ctrl+O')
        filemenu.add_command(label='Guardar', command=self.guardar, accelerator='Ctrl+S')
        filemenu.add_command(label='Guardar como...', command=self.guardar_como)
        filemenu.add_separator()
        filemenu.add_command(label='Salir', command=self.quit)
        menubar.add_cascade(label='Archivo', menu=filemenu)

        editmenu = tk.Menu(menubar, tearoff=0)
        editmenu.add_command(label='Buscar', command=self.buscar, accelerator='Ctrl+F')
        editmenu.add_command(label='Reemplazar', command=self.reemplazar, accelerator='Ctrl+H')
        menubar.add_cascade(label='Edición', menu=editmenu)

        toolsmenu = tk.Menu(menubar, tearoff=0)
        toolsmenu.add_command(label='Compilar', command=self.compilar, accelerator='F5')
        toolsmenu.add_command(label='Ver AST', command=self.ver_ast)
        menubar.add_cascade(label='Herramientas', menu=toolsmenu)

        helpmenu = tk.Menu(menubar, tearoff=0)
        helpmenu.add_command(label='Acerca de', command=self.acerca_de)
        menubar.add_cascade(label='Ayuda', menu=helpmenu)

        self.config(menu=menubar)

    def create_widgets(self):
        main = ttk.PanedWindow(self, orient='horizontal')
        main.pack(fill='both', expand=True)

        left = ttk.Frame(main)
        main.add(left, weight=3)

        self.line_numbers = tk.Text(left, width=4, padx=4, takefocus=0, border=0, background='#eee', state='disabled', font=('Consolas', 11))
        self.line_numbers.pack(side='left', fill='y')

        self.text = tk.Text(left, wrap='none', font=('Consolas', 11), undo=True)
        self.text.pack(side='left', fill='both', expand=True)
        self.text.bind('<KeyRelease>', self.update_line_numbers)
        self.update_line_numbers()

        right = ttk.Frame(main)
        main.add(right, weight=1)

        self.errors_panel = tk.Text(right, height=10, font=('Consolas', 10), background='#fee')
        self.errors_panel.pack(fill='both', expand=True)
        self.errors_panel.config(state='disabled')

        statusbar = ttk.Label(self, textvariable=self.status, anchor='w')
        statusbar.pack(fill='x')

    def bind_shortcuts(self):
        self.bind('<Control-o>', lambda e: self.abrir())
        self.bind('<Control-s>', lambda e: self.guardar())
        self.bind('<Control-h>', lambda e: self.reemplazar())
        self.bind('<Control-f>', lambda e: self.buscar())
        self.bind('<F5>', lambda e: self.compilar())

    def update_line_numbers(self, event=None):
        self.line_numbers.config(state='normal')
        self.line_numbers.delete('1.0', 'end')
        lines = self.text.get('1.0', 'end-1c').split('\n')
        for i in range(1, len(lines)+1):
            self.line_numbers.insert('end', f'{i}\n')
        self.line_numbers.config(state='disabled')

    def abrir(self):
        path = filedialog.askopenfilename(filetypes=[('Compiscript', '*.cps'), ('Todos', '*.*')])
        if not path: return
        self.current_file = path
        with open(path, 'r', encoding='utf-8') as f:
            self.text.delete('1.0', 'end')
            self.text.insert('1.0', f.read())
        self.status.set(f'Abrí: {os.path.basename(path)}')
        self.update_line_numbers()

    def guardar(self):
        if not self.current_file:
            self.guardar_como()
            return
        with open(self.current_file, 'w', encoding='utf-8') as f:
            f.write(self.text.get('1.0', 'end-1c'))
        self.status.set(f'Guardé: {os.path.basename(self.current_file)}')

    def guardar_como(self):
        path = filedialog.asksaveasfilename(defaultextension='.cps', filetypes=[('Compiscript', '*.cps')])
        if not path: return
        self.current_file = path
        self.guardar()

    def buscar(self):
        term = simpledialog.askstring('Buscar', 'Texto a buscar:')
        if not term: return
        self.text.tag_remove('search', '1.0', 'end')
        idx = '1.0'
        while True:
            idx = self.text.search(term, idx, nocase=1, stopindex='end')
            if not idx: break
            lastidx = f'{idx}+{len(term)}c'
            self.text.tag_add('search', idx, lastidx)
            self.text.tag_config('search', background='yellow')
            idx = lastidx

    def reemplazar(self):
        term = simpledialog.askstring('Reemplazar', 'Texto a buscar:')
        if not term: return
        repl = simpledialog.askstring('Reemplazar', f'Reemplazar "{term}" por:')
        if repl is None: return
        content = self.text.get('1.0', 'end-1c').replace(term, repl)
        self.text.delete('1.0', 'end')
        self.text.insert('1.0', content)
        self.update_line_numbers()

    def compilar(self):
        code = self.text.get('1.0', 'end-1c')
        with tempfile.NamedTemporaryFile('w', delete=False, suffix='.cps', encoding='utf-8') as tmp:
            tmp.write(code)
            tmp_path = tmp.name
        try:
            p = subprocess.run([sys.executable, os.path.join(ROOT, 'Driver.py'), tmp_path], capture_output=True, text=True)
            self.errors_panel.config(state='normal')
            self.errors_panel.delete('1.0', 'end')
            if p.returncode == 0:
                self.errors_panel.insert('end', '✔ Código válido (sin errores)\n')
                self.status.set('Compilación exitosa')
            else:
                self.errors_panel.insert('end', p.stdout + '\n' + p.stderr)
                self.status.set('Errores de compilación')
            self.errors_panel.config(state='disabled')
        finally:
            os.unlink(tmp_path)

    def ver_ast(self):
        code = self.text.get('1.0', 'end-1c')
        with tempfile.NamedTemporaryFile('w', delete=False, suffix='.cps', encoding='utf-8') as tmp:
            tmp.write(code)
            tmp_path = tmp.name
        try:
            # AST textual usando ANTLR
            p = subprocess.run([sys.executable, os.path.join(ROOT, 'Driver.py'), tmp_path, '--ast'], capture_output=True, text=True)
            ast_text = p.stdout if p.stdout else 'No se pudo generar el AST.'
            ASTDialog(self, ast_text)
        finally:
            os.unlink(tmp_path)

    def acerca_de(self):
        messagebox.showinfo('Acerca de', 'Compiscript IDE\nProyecto universitario\nAutor: Tu Nombre')

if __name__ == '__main__':
    CompiscriptIDE().mainloop()
