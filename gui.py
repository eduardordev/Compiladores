import os
import sys
import tkinter as tk
from tkinter import filedialog, messagebox
import subprocess
import shutil

class SimuladorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Simulador YAL + YAPAR")
        self.root.geometry("1000x600")

        self.yal_path = ""
        self.txt_path = ""
        self.yapar_path = ""

        # Encabezado de botones
        self.frame_top = tk.Frame(self.root)
        self.frame_top.pack(pady=10)

        tk.Button(self.frame_top, text="Cargar archivo .yal", command=self.load_yal).grid(row=0, column=0, padx=5)
        tk.Button(self.frame_top, text="Cargar archivo .txt", command=self.load_txt).grid(row=0, column=1, padx=5)
        tk.Button(self.frame_top, text="Cargar archivo .yapar", command=self.load_yapar).grid(row=0, column=2, padx=5)
        tk.Button(self.frame_top, text="Ejecutar Generador/Simulación", command=self.run_simulation).grid(row=0, column=3, padx=5)

        # Consola
        self.console = tk.Text(self.root, wrap=tk.WORD, height=25)
        self.console.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.console.configure(state='disabled')

        # Imagen AFD
        self.image_label = tk.Label(self.root)
        self.image_label.pack()

    def load_yal(self):
        path = filedialog.askopenfilename(filetypes=[("Archivos .yal", "*.yal")])
        if path:
            self.yal_path = path
            messagebox.showinfo("Archivo .yal", f"Archivo cargado:\n{path}")

    def load_txt(self):
        path = filedialog.askopenfilename(filetypes=[("Archivos .txt", "*.txt")])
        if path:
            self.txt_path = path
            messagebox.showinfo("Archivo .txt", f"Archivo cargado:\n{path}")

    def load_yapar(self):
        path = filedialog.askopenfilename(filetypes=[("Archivos .yapar", "*.yapar")])
        if path:
            self.yapar_path = path
            messagebox.showinfo("Archivo .yapar", f"Archivo cargado:\n{path}")

    def run_simulation(self):
        if not self.yal_path or not self.txt_path or not self.yapar_path:
            messagebox.showwarning("Archivos faltantes", "Seleccione .yal, .txt y .yapar antes de ejecutar.")
            return

        root_dir = os.path.dirname(os.path.abspath(__file__))
        self.console.configure(state='normal')
        self.console.delete('1.0', tk.END)
        self.console.configure(state='disabled')

        # Borrar imágenes AFD anteriores
        for fn in os.listdir(root_dir):
            if fn.lower().endswith('.png') and fn.lower().startswith('afd'):
                try:
                    os.remove(os.path.join(root_dir, fn))
                except:
                    pass

        yal_path = self.yal_path
        txt_path = self.txt_path
        yapar_path = self.yapar_path

        # Validar rutas seleccionadas
        if not os.path.isfile(yal_path) or not os.path.isfile(txt_path) or not os.path.isfile(yapar_path):
            messagebox.showerror("Error", "Uno de los archivos seleccionados no existe.")
            return

        # Ejecutar main.py (análisis léxico)
        try:
            env = os.environ.copy()
            env['PYTHONIOENCODING'] = 'utf-8'
            result = subprocess.run(
                [sys.executable, os.path.join(root_dir, 'main.py'),  yal_path, txt_path],
                capture_output=True,
                text=True,
                cwd=root_dir,
                env=env,
                encoding='utf-8',       # ✅ Soluciona el problema de Unicode
                errors='replace'        # ✅ Evita que se caiga por caracteres especiales
            )

            self.console.configure(state='normal')
            self.console.insert(tk.END, result.stdout)
            if result.stderr:
                self.console.insert(tk.END, "\n--- STDERR ---\n")
                self.console.insert(tk.END, result.stderr)
            self.console.configure(state='disabled')
        except Exception as e:
            messagebox.showerror("Error ejecución", str(e))
            return

        # Ejecutar análisis sintáctico
        try:
            from SimuladorTxT import SimuladorTxT
            from implmentacion import diccionarios, iniciales, finales, archiv as archivo, reservadas, operadores_reservados, tokens, tabla
            from parser_integration import parse_from_tokens

            sim = SimuladorTxT(diccionarios, iniciales, finales, archivo, reservadas, operadores_reservados, tokens, tabla)
            tokens_parser = sim.get_tokens_for_parser()
            parse_from_tokens(tokens_parser, self.yapar_path)

            self.console.configure(state='normal')
            self.console.insert(tk.END, "\n--- Análisis completo ---\n")
            self.console.configure(state='disabled')

        except Exception as e:
            messagebox.showerror("Error en análisis sintáctico", str(e))

        self.load_diagrams()

    def load_diagrams(self):
        root_dir = os.path.dirname(os.path.abspath(__file__))
        afd_path = os.path.join(root_dir, "afd.png")
        if os.path.exists(afd_path):
            from PIL import Image, ImageTk
            img = Image.open(afd_path)
            img = img.resize((500, 300), Image.ANTIALIAS)
            self.image = ImageTk.PhotoImage(img)
            self.image_label.configure(image=self.image)
        else:
            self.image_label.configure(image='')


if __name__ == "__main__":
    root = tk.Tk()
    app = SimuladorApp(root)
    root.mainloop()
