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
        # Append text to the console widget
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
        # Redirect stdout/stderr
        sys.stdout = StdoutRedirector(self.console)
        sys.stderr = StdoutRedirector(self.console)

    def _build_ui(self):
        # Top controls
        top = tk.Frame(self)
        top.pack(fill=tk.X, padx=5, pady=5)

        btn_yal = tk.Button(top, text="Elegir .yal", command=self.choose_yal)
        btn_yal.pack(side=tk.LEFT)
        self.yal_label = tk.Label(top, text="Ningún .yal seleccionado")
        self.yal_label.pack(side=tk.LEFT, padx=5)

        btn_txt = tk.Button(top, text="Elegir .txt", command=self.choose_txt)
        btn_txt.pack(side=tk.LEFT, padx=(20,0))
        self.txt_label = tk.Label(top, text="Ningún .txt seleccionado")
        self.txt_label.pack(side=tk.LEFT, padx=5)

        btn_run = tk.Button(top, text="Ejecutar Generador/Simulación", command=self.run_simulation)
        btn_run.pack(side=tk.RIGHT)

        # Main pane
        pane = tk.PanedWindow(self, orient=tk.HORIZONTAL, sashrelief=tk.RAISED)
        pane.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Diagram frame
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

        # Console frame
        console_frame = tk.LabelFrame(pane, text="Consola de Tokens/Errores")
        self.console = scrolledtext.ScrolledText(console_frame, wrap=tk.WORD, state='disabled')
        self.console.pack(fill=tk.BOTH, expand=True)
        pane.add(console_frame)

    def clear_diagrams(self):
        for w in self.diagram_widgets:
            w.destroy()
        self.diagram_widgets.clear()

    def load_diagrams(self):
        # Display all AFD diagram PNGs in the working directory
        self.clear_diagrams()
        root_dir = os.path.dirname(os.path.abspath(__file__))
        for fn in sorted(os.listdir(root_dir)):
            if fn.lower().endswith('.png') and fn.lower().startswith('afd'):
                path = os.path.join(root_dir, fn)
                try:
                    img = Image.open(path)
                    img.thumbnail((350,350))
                    tk_img = ImageTk.PhotoImage(img)
                    lbl = tk.Label(self.frame_diags, image=tk_img)
                    lbl.image = tk_img
                    lbl.pack(padx=5, pady=5)
                    self.diagram_widgets.append(lbl)
                except Exception:
                    continue

    def choose_yal(self):
        path = filedialog.askopenfilename(
            title="Seleccione especificación YALex", filetypes=[("YAL files","*.yal")]
        )
        if not path:
            return
        self.yal_path = path
        self.yal_label.config(text=os.path.basename(path))

    def choose_txt(self):
        path = filedialog.askopenfilename(
            title="Seleccione texto de entrada", filetypes=[("Text files","*.txt")]
        )
        if not path:
            return
        self.txt_path = path
        self.txt_label.config(text=os.path.basename(path))

    def run_simulation(self):
        if not self.yal_path or not self.txt_path:
            messagebox.showwarning("Archivos faltantes", "Seleccione ambos .yal y .txt antes de ejecutar.")
            return
        root_dir = os.path.dirname(os.path.abspath(__file__))

        # Clear console and diagrams
        self.console.configure(state='normal')
        self.console.delete('1.0', tk.END)
        self.console.configure(state='disabled')
        # Remove old diagram files
        for fn in os.listdir(root_dir):
            if fn.lower().endswith('.png') and fn.lower().startswith('afd'):
                try: os.remove(os.path.join(root_dir, fn))
                except: pass
        # Run main.py with UTF-8 output
        try:
            env = os.environ.copy()
            env['PYTHONIOENCODING'] = 'utf-8'
            result = subprocess.run(
                [sys.executable, os.path.join(root_dir, 'main.py')],
                capture_output=True, text=True, cwd=root_dir, env=env
            )
            # Output to console
            sys.stdout.write(result.stdout)
            if result.stderr:
                sys.stdout.write(result.stderr)
        except Exception as e:
            messagebox.showerror("Error ejecución", str(e))
            return
        # Load generated diagrams
        self.load_diagrams()

if __name__ == "__main__":
    AppGUI().mainloop()