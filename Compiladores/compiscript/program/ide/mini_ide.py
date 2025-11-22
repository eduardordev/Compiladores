import os, sys, tempfile, subprocess
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

HERE = os.path.dirname(__file__)
ROOT = os.path.abspath(os.path.join(HERE, '..'))

class MiniIDE(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('Compiscript IDE (mínimo)')
        self.geometry('900x600')

        self.text = tk.Text(self, wrap='none', font=('Consolas', 11))
        self.text.pack(fill='both', expand=True)

        bottom = ttk.Frame(self)
        bottom.pack(fill='x')
        ttk.Button(bottom, text='Abrir', command=self.abrir).pack(side='left')
        ttk.Button(bottom, text='Guardar', command=self.guardar).pack(side='left')
        ttk.Button(bottom, text='Compilar', command=self.compilar).pack(side='left')

        self.status = tk.StringVar(value='Listo')
        ttk.Label(self, textvariable=self.status, anchor='w').pack(fill='x')

        self.current_file = None

    def abrir(self):
        path = filedialog.askopenfilename(filetypes=[('Compiscript', '*.cps'), ('Todos', '*.*')])
        if not path: return
        self.current_file = path
        with open(path, 'r', encoding='utf-8') as f:
            self.text.delete('1.0', 'end')
            self.text.insert('1.0', f.read())
        self.status.set(f'Abrí: {os.path.basename(path)}')

    def guardar(self):
        if not self.current_file:
            path = filedialog.asksaveasfilename(defaultextension='.cps', filetypes=[('Compiscript', '*.cps')])
            if not path: return
            self.current_file = path
        with open(self.current_file, 'w', encoding='utf-8') as f:
            f.write(self.text.get('1.0', 'end-1c'))
        self.status.set(f'Guardé: {os.path.basename(self.current_file)}')

    def compilar(self):
        code = self.text.get('1.0', 'end-1c')
        with tempfile.NamedTemporaryFile('w', delete=False, suffix='.cps', encoding='utf-8') as tmp:
            tmp.write(code)
            tmp_path = tmp.name
        try:
            p = subprocess.run([sys.executable, os.path.join(ROOT, 'Driver.py'), tmp_path], capture_output=True, text=True)
            if p.returncode == 0:
                messagebox.showinfo('Compilación', '✔ Código válido (sin errores)')
            else:
                messagebox.showerror('Errores', p.stdout + '\n' + p.stderr)
        finally:
            os.unlink(tmp_path)

if __name__ == '__main__':
    MiniIDE().mainloop()
