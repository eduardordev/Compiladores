import os, sys, tempfile, subprocess
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog

try:
    from antlr4 import InputStream, CommonTokenStream
    from CompiscriptLexer import CompiscriptLexer
    from CompiscriptParser import CompiscriptParser
except Exception:
    InputStream = None
    CommonTokenStream = None
    CompiscriptLexer = None
    CompiscriptParser = None

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
        toolsmenu.add_command(label='Ver AST (Texto)', command=self.ver_ast)
        toolsmenu.add_command(label='Ver AST (Visual)', command=self.ver_ast_visual)
        toolsmenu.add_command(label='Ver TAC', command=self.ver_tac)
        toolsmenu.add_command(label='Guardar TAC (.cspt)', command=self.guardar_cspt)
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
        btn_ast_vis = ttk.Button(toolbar, text='🌲 AST (Vis)', command=self.ver_ast_visual)
        btn_tac = ttk.Button(toolbar, text='⚙️ TAC', command=self.ver_tac)
        btn_save_tac = ttk.Button(toolbar, text='💾 TAC', command=self.guardar_cspt)
        btn_theme = ttk.Button(toolbar, text='🌓 Tema', command=self.toggle_theme)
        btn_misp = ttk.Button(toolbar, text='💾 MISP', command=self.guardar_misp)
        for b in (btn_open, btn_save, btn_run, btn_ast, btn_ast_vis, btn_tac, btn_save_tac, btn_theme, btn_misp):
            b.pack(side='left', padx=3, pady=2)

        main = ttk.PanedWindow(container, orient='horizontal')
        main.pack(fill='both', expand=True)


        sidebar = ttk.Frame(main, width=50)
        main.add(sidebar, weight=0)
        for ico, cmd, tip in [('📁', self.abrir, 'Abrir'),
                              ('💾', self.guardar, 'Guardar'),
                              ('⚙️', self.compilar, 'Compilar')]:
            b = ttk.Button(sidebar, text=ico, width=3, command=cmd)
            b.pack(pady=6)


        center = ttk.Frame(main)
        main.add(center, weight=3)

        center_paned = ttk.PanedWindow(center, orient='vertical')
        center_paned.pack(fill='both', expand=True)

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

    def _create_output_panel(self, parent, title):
        frame = ttk.Frame(parent)
        label = ttk.Label(frame, text=title, anchor='center', font=('Consolas', 10, 'bold'))
        label.pack(fill='x')
        text = tk.Text(frame, height=10, font=('Consolas', 10))
        text.pack(fill='both', expand=True)
        text.config(state='disabled')
        return {'frame': frame, 'text': text}


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

    def _generate_tac(self):
        """Genera TAC usando Driver.py --tac"""
        code = self.text.get('1.0', 'end-1c')
        with tempfile.NamedTemporaryFile('w', delete=False, suffix='.cps', encoding='utf-8') as tmp:
            tmp.write(code)
            tmp_path = tmp.name
        try:
            p = subprocess.run(
                [sys.executable, os.path.join(ROOT, 'Driver.py'), tmp_path, '--tac'],
                capture_output=True,
                text=True
            )
            output = p.stdout if p.stdout.strip() else p.stderr
            return output or '', p.returncode, p.stderr
        finally:
            os.unlink(tmp_path)


    def ver_ast_visual(self):
        """Show a visual AST in a new window. If ANTLR parser is importable, parse in-process
        and build a tree; otherwise fall back to textual AST produced by Driver.py and show
        its parsed structure (simple)."""
        code = self.text.get('1.0', 'end-1c')

        # Try in-process parse
        tree = None
        parser = None
        if InputStream and CompiscriptLexer and CompiscriptParser:
            try:
                stream = InputStream(code)
                lexer = CompiscriptLexer(stream)
                tokens = CommonTokenStream(lexer)
                parser = CompiscriptParser(tokens)
                tree = parser.program()
            except Exception as e:
                tree = None

        # If no in-process tree, call Driver.py --ast and parse textual tree into a simple node structure
        textual = None
        if tree is None:
            with tempfile.NamedTemporaryFile('w', delete=False, suffix='.cps', encoding='utf-8') as tmp:
                tmp.write(code)
                tmp_path = tmp.name
            try:
                p = subprocess.run([sys.executable, os.path.join(ROOT, 'Driver.py'), tmp_path, '--ast'], capture_output=True, text=True)
                textual = p.stdout
            finally:
                os.unlink(tmp_path)

        # Build node structure
        if tree is not None:
            root = self._build_ast_tree(tree, parser)
        else:
            # crude textual parse: lines with parentheses from toStringTree
            root = {'label': 'AST', 'children': []}
            if textual:
                # naive tokenization: treat parentheses as tree structure
                tokens = textual.replace('(', ' ( ').replace(')', ' ) ').split()
                stack = [root]
                for tok in tokens:
                    if tok == '(':
                        # start child with next token as label
                        continue
                    elif tok == ')':
                        if len(stack) > 1:
                            stack.pop()
                    else:
                        node = {'label': tok, 'children': []}
                        stack[-1]['children'].append(node)
                        stack.append(node)

        # Open visual window and draw
        win = tk.Toplevel(self)
        win.title('AST Visual')
        canvas = tk.Canvas(win, background='white')
        hbar = ttk.Scrollbar(win, orient='horizontal', command=canvas.xview)
        vbar = ttk.Scrollbar(win, orient='vertical', command=canvas.yview)
        canvas.config(xscrollcommand=hbar.set, yscrollcommand=vbar.set)
        hbar.pack(side='bottom', fill='x')
        vbar.pack(side='right', fill='y')
        canvas.pack(side='left', fill='both', expand=True)

        # layout and draw nodes
        try:
            self._layout_and_draw(canvas, root)
        except Exception as e:
            canvas.create_text(10, 10, anchor='nw', text=f'Error drawing AST: {e}')

    def _build_ast_tree(self, tree, parser):
        """Convert ANTLR parse tree to a simple nested dict structure: {'label': str, 'children': [...]}
        This walks children using getChildCount/getChild
        """
        def node_of(t):
            lab = t.getText() if hasattr(t, 'getText') else str(t)
            # prefer rule name when possible
            try:
                ridx = t.getRuleIndex()
                ruleName = parser.ruleNames[ridx]
                lab = ruleName
            except Exception:
                pass
            n = {'label': lab, 'children': []}
            try:
                cnt = t.getChildCount()
                for i in range(cnt):
                    ch = t.getChild(i)
                    n['children'].append(node_of(ch))
            except Exception:
                pass
            return n
        return node_of(tree)

    def _layout_and_draw(self, canvas, root):
        """Simple top-down layout: assign x positions by subtree width, y by depth, then draw boxes and lines."""
        node_w = 100
        node_h = 30
        hsep = 20
        vsep = 60

        # compute widths
        def compute_width(n):
            if not n.get('children'):
                n['_width'] = node_w
            else:
                w = 0
                for c in n['children']:
                    compute_width(c)
                    w += c['_width'] + hsep
                w = max(node_w, w - hsep)
                n['_width'] = w
        compute_width(root)

        # assign positions
        x0 = 20
        y0 = 20

        def assign_pos(n, x, y):
            n['_x'] = x + n['_width'] / 2
            n['_y'] = y
            cx = x
            for c in n['children']:
                assign_pos(c, cx, y + vsep)
                cx += c['_width'] + hsep
        assign_pos(root, x0, y0)

        # draw
        def draw_node(n):
            x = n['_x']
            y = n['_y']
            left = x - node_w/2
            right = x + node_w/2
            top = y
            bottom = y + node_h
            canvas.create_rectangle(left, top, right, bottom, fill='#eef', outline='#66a')
            canvas.create_text(x, y + node_h/2, text=str(n.get('label') or ''), font=('Consolas', 9))
            for c in n['children']:
                cx = c['_x']
                cy = c['_y']
                # line from bottom center to child's top center
                canvas.create_line(x, bottom, cx, cy, fill='#444')
                draw_node(c)
        draw_node(root)

        # helper iterator
        def _iter_nodes(n):
            yield n
            for c in n.get('children', []):
                for x in _iter_nodes(c):
                    yield x

        # set scroll region
        nodes = list(_iter_nodes(root))
        minx = min(n['_x'] - node_w/2 for n in nodes)
        maxx = max(n['_x'] + node_w/2 for n in nodes)
        miny = min(n['_y'] for n in nodes)
        maxy = max(n['_y'] + node_h for n in nodes)
        canvas.config(scrollregion=(minx-20, miny-20, maxx+20, maxy+20))


    def ver_tac(self):
        tac_text, _, _ = self._generate_tac()
        self._update_output(self.tac_panel['text'], tac_text)

    def guardar_cspt(self):
        tac_text, retcode, errors = self._generate_tac()
        if retcode != 0:
            messagebox.showerror('Error al generar TAC', errors or 'No se pudo generar TAC.')
            return

        tac_clean = tac_text.strip()
        if not tac_clean:
            messagebox.showinfo('Sin TAC', 'No se generó código intermedio para guardar.')
            return

        path = filedialog.asksaveasfilename(
            defaultextension='.cspt',
            filetypes=[('Compiscript TAC', '*.cspt'), ('Todos', '*.*')],
            title='Guardar TAC como .cspt'
        )
        if not path:
            return

        try:
            with open(path, 'w', encoding='utf-8') as f:
                f.write('// TAC generado por Compiscript IDE\n')
                f.write(tac_clean + ('\n' if not tac_clean.endswith('\n') else ''))
            self.status.set(f'TAC guardado en {os.path.basename(path)}')
        except Exception as e:
            messagebox.showerror('Error al guardar', f'No se pudo escribir el archivo: {e}')

    def guardar_misp(self):
        # Guardar archivo MIPS
        path = filedialog.asksaveasfilename(
            defaultextension='.s',
            filetypes=[('MIPS Assembly', '*.s'), ('Todos', '*.*')],
            title='Guardar MIPS como .s'
        )
        if not path:
            return
        
        try:
            # Obtener el código fuente
            code = self.text.get('1.0', 'end-1c')
            
            # Importar módulos necesarios
            import sys
            sys.path.insert(0, ROOT)
            from antlr4 import InputStream, CommonTokenStream
            from CompiscriptLexer import CompiscriptLexer
            from CompiscriptParser import CompiscriptParser
            from codegen.codegen import CodeGenVisitor
            import importlib
            import codegen.mips_backend
            importlib.reload(codegen.mips_backend)
            emit_mips = codegen.mips_backend.emit_mips
            
            # Parsear el código para generar TAC y static_arrays
            input_stream = InputStream(code)
            lexer = CompiscriptLexer(input_stream)
            token_stream = CommonTokenStream(lexer)
            parser = CompiscriptParser(token_stream)
            tree = parser.program()
            
            # Generar TAC y obtener static_arrays
            visitor = CodeGenVisitor()
            result = visitor.visit(tree)
            
            # El visitor retorna (emitter, static_arrays)
            if isinstance(result, tuple) and len(result) == 2:
                emitter, static_arrays = result
            else:
                emitter = result
                static_arrays = {}
            
            # DEBUG: Mostrar qué hay en static_arrays
            print(f"DEBUG static_arrays: {static_arrays}")
            
            # Generar código MIPS con static_arrays
            mips_code = emit_mips(emitter, symtab=None, out_path=None, static_arrays=static_arrays)
            
            if not mips_code or not mips_code.strip():
                messagebox.showinfo('Sin MIPS', 'No se generó código MIPS para guardar.')
                return
            
            # Guardar el código MIPS
            with open(path, 'w', encoding='utf-8') as f:
                f.write(mips_code)
                if not mips_code.endswith('\n'):
                    f.write('\n')
            
            self.status.set(f'✓ MIPS guardado en {os.path.basename(path)}')
            messagebox.showinfo('Éxito', f'Código MIPS guardado en:\n{os.path.basename(path)}')
            
        except Exception as e:
            import traceback
            error_detail = traceback.format_exc()
            messagebox.showerror('Error al generar MIPS', f'Error:\n{str(e)}\n\nDetalle:\n{error_detail[:500]}')
            def _generate_tac(self):
                code = self.text.get('1.0', 'end-1c')
                with tempfile.NamedTemporaryFile('w', delete=False, suffix='.cps', encoding='utf-8') as tmp:
                    tmp.write(code)
                    tmp_path = tmp.name
                try:
                    p = subprocess.run(
                        [sys.executable, os.path.join(ROOT, 'Driver.py'), tmp_path, '--tac'],
                        capture_output=True,
                        text=True
                    )
                    output = p.stdout if p.stdout.strip() else p.stderr
                    return output or '', p.returncode, p.stderr
                finally:
                    os.unlink(tmp_path)


    def _update_output(self, panel, text):
        panel.config(state='normal')
        panel.delete('1.0', 'end')
        panel.insert('end', text if text.strip() else '(sin salida)')
        panel.config(state='disabled')

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
