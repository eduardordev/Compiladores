# gui.py

import os
import sys
import shutil
import subprocess
import tkinter as tk
from tkinter import filedialog, scrolledtext, messagebox
from PIL import Image, ImageTk

class StdoutRedirector:
    def __init__(self, text_widget):
        self.text_widget = text_widget
    def write(self, s):
        self.text_widget.configure(state='normal')
        self.text_widget.insert(tk.END, s)
        self.text_widget.see(tk.END)
        self.text_widget.configure(state='disabled')
    def flush(self):
        pass

class AppGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Generador y Simulador Léxico")
        self.geometry("1000x600")
        self.yal_path = None
        self.txt_path = None
        self.diagram_widgets = []
        self._build_ui()
        sys.stdout = StdoutRedirector(self.console)
        sys.stderr = StdoutRedirector(self.console)

    def _build_ui(self):
        top = tk.Frame(self)
        top.pack(fill=tk.X, padx=5, pady=5)

        tk.Button(top, text="Elegir .yal", command=self.choose_yal).pack(side=tk.LEFT)
        self.yal_label = tk.Label(top, text="Ningún .yal seleccionado")
        self.yal_label.pack(side=tk.LEFT, padx=5)

        tk.Button(top, text="Elegir .txt", command=self.choose_txt).pack(side=tk.LEFT, padx=(20,0))
        self.txt_label = tk.Label(top, text="Ningún .txt seleccionado")
        self.txt_label.pack(side=tk.LEFT, padx=5)

        tk.Button(top, text="Ejecutar Generador/Simulación", command=self.run_simulation).pack(side=tk.RIGHT)

        pane = tk.PanedWindow(self, orient=tk.HORIZONTAL)
        pane.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        diag_frame = tk.LabelFrame(pane, text="Diagramas AFD")
        self.canvas_diags = tk.Canvas(diag_frame)
        self.scroll_diags = tk.Scrollbar(diag_frame, orient=tk.VERTICAL, command=self.canvas_diags.yview)
        self.frame_diags = tk.Frame(self.canvas_diags)
        self.canvas_diags.create_window((0,0), window=self.frame_diags, anchor='nw')
        self.canvas_diags.configure(yscrollcommand=self.scroll_diags.set)
        self.frame_diags.bind('<Configure>', lambda e: self.canvas_diags.configure(scrollregion=self.canvas_diags.bbox('all')))
        self.canvas_diags.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scroll_diags.pack(side=tk.RIGHT, fill=tk.Y)
        pane.add(diag_frame, width=400)

        console_frame = tk.LabelFrame(pane, text="Consola de Tokens/Errores")
        self.console = scrolledtext.ScrolledText(console_frame, wrap=tk.WORD, state='disabled')
        self.console.pack(fill=tk.BOTH, expand=True)
        pane.add(console_frame)

    def choose_yal(self):
        path = filedialog.askopenfilename(title="Seleccione especificación YALex", filetypes=[("YAL files","*.yal")])
        if path:
            self.yal_path = path
            self.yal_label.config(text=os.path.basename(path))

    def choose_txt(self):
        path = filedialog.askopenfilename(title="Seleccione texto de entrada", filetypes=[("Text files","*.txt")])
        if path:
            self.txt_path = path
            self.txt_label.config(text=os.path.basename(path))

    def clear_diagrams(self):
        for w in self.diagram_widgets:
            w.destroy()
        self.diagram_widgets.clear()

    def load_diagrams(self):
        self.clear_diagrams()
        root_dir = os.path.dirname(os.path.abspath(__file__))
        for fn in sorted(os.listdir(root_dir)):
            if fn.lower().endswith('.png') and fn.lower().startswith('afd'):
                try:
                    img = Image.open(os.path.join(root_dir, fn))
                    img.thumbnail((350,350))
                    tk_img = ImageTk.PhotoImage(img)
                    lbl = tk.Label(self.frame_diags, image=tk_img)
                    lbl.image = tk_img
                    lbl.pack(padx=5, pady=5)
                    self.diagram_widgets.append(lbl)
                except:
                    continue

    def run_simulation(self):
        if not self.yal_path or not self.txt_path:
            messagebox.showwarning("Archivos faltantes", "Seleccione ambos .yal y .txt antes de ejecutar.")
            return

        root_dir = os.path.dirname(os.path.abspath(__file__))
        self.console.configure(state='normal')
        self.console.delete('1.0', tk.END)
        self.console.configure(state='disabled')

        for fn in os.listdir(root_dir):
            if fn.lower().endswith('.png') and fn.lower().startswith('afd'):
                try:
                    os.remove(os.path.join(root_dir, fn))
                except:
                    pass

        # Destinos esperados
        yal_dest = os.path.join(root_dir, "alta.yal")
        txt_dest = os.path.join(root_dir, "alta.txt")

        try:
            if not (os.path.exists(yal_dest) and os.path.samefile(self.yal_path, yal_dest)):
                shutil.copyfile(self.yal_path, yal_dest)

            if not (os.path.exists(txt_dest) and os.path.samefile(self.txt_path, txt_dest)):
                shutil.copyfile(self.txt_path, txt_dest)

        except Exception as e:
            messagebox.showerror("Error al copiar archivos", str(e))
            return

        try:
            env = os.environ.copy()
            env['PYTHONIOENCODING'] = 'utf-8'
            result = subprocess.run(
                [sys.executable, os.path.join(root_dir, 'main.py')],
                capture_output=True, text=True, cwd=root_dir, env=env
            )
            sys.stdout.write(result.stdout)
            if result.stderr:
                sys.stdout.write(result.stderr)
        except Exception as e:
            messagebox.showerror("Error ejecución", str(e))
            return

        self.load_diagrams()

if __name__ == "__main__":
    AppGUI().mainloop()
