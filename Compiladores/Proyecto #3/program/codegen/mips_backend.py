from typing import List, Dict, Optional
from codegen.tac import Instr, Emitter

class MIPSBackend:
    def __init__(self) -> None:
        # líneas de código de la sección .text
        self.text_lines: List[str] = []
        # nombres de variables globales detectadas
        self.global_vars = set()
        # literales de string: texto -> label
        self.string_literals: Dict[str, str] = {}
        self.next_string_id: int = 0

        # campos de objetos: nombre_campo -> offset en bytes
        self.field_offsets: Dict[str, int] = {}
        self.next_field_offset: int = 0  # en bytes

        # si se detecta uso de heap (NEWOBJ o ALLOC)
        self.uses_heap: bool = False

        # estado de funciones
        self.current_func: Optional[str] = None
        self.has_main: bool = False

        # argumentos pendientes antes de un CALL
        self.pending_args: List[str] = []

        # arreglos/variables inicializados en .data
        self.static_arrays = {}
        
        # Mejoras: rastreo de parámetros y variables locales
        self.func_params: Dict[str, List[str]] = {}  # función -> lista de parámetros
        self.func_local_vars: Dict[str, set] = {}  # función -> set de variables locales
        self.current_func_params: List[str] = []  # parámetros de la función actual
        self.current_func_locals: set = set()  # variables locales de la función actual
        
        # Frame size dinámico
        self.func_frame_sizes: Dict[str, int] = {}  # función -> tamaño del frame
        
        # Registros en uso (para mejor selección)
        self.reg_in_use: Dict[str, str] = {}  # temporal -> registro actual
        
        # Herencia y vtable
        self.class_hierarchy: Dict[str, Optional[str]] = {}  # clase -> clase padre
        self.class_vtables: Dict[str, Dict[str, str]] = {}  # clase -> {método -> label}
        self.vtable_registry: Dict[str, str] = {}  # vtable_label -> dirección
        
        # Try-catch
        self.exception_handler_stack: List[str] = []  # Stack de handlers de excepción
        self.current_exception_var: Optional[str] = None

    def emit(self, line: str) -> None:
        """Agrega una línea al código .text."""
        self.text_lines.append(line)

    def is_temp(self, name: Optional[str]) -> bool:
        return isinstance(name, str) and name.startswith("t") and name[1:].isdigit()

    def is_immediate(self, x: Optional[str]) -> bool:
        if not isinstance(x, str):
            return False
        if x.isdigit():
            return True
        if x.startswith("-") and x[1:].isdigit():
            return True
        return False

    def is_string_literal(self, x: Optional[str]) -> bool:
        # Heurística: en tu TAC los strings suelen venir entre comillas
        return isinstance(x, str) and len(x) >= 2 and x[0] == '"' and x[-1] == '"'

    def temp_reg(self, tname: str) -> str:
        """Mapea t0, t1, ... a $t0..$t9 (cíclico mejorado)."""
        try:
            n = int(tname[1:])
        except ValueError:
            n = 0
        n = n % 10
        reg = f"$t{n}"
        # Rastrear qué temporal está en qué registro
        self.reg_in_use[tname] = reg
        return reg

    def ensure_global(self, name: str) -> None:
        """Registra un nombre como variable global si no es temp, ni literal, ni None."""
        if not isinstance(name, str):
            return
        if self.is_temp(name):
            return
        if self.is_immediate(name):
            return
        if self.is_string_literal(name):
            return
        if name in ("None", "", None):
            return
        # parámetros como "arg0" los tratamos como globales por simplicidad
        self.global_vars.add(name)

    def string_label_for(self, literal: str) -> str:
        """Devuelve etiqueta de .data para un literal de string."""
        if literal in self.string_literals:
            return self.string_literals[literal]
        label = f"__str{self.next_string_id}"
        self.next_string_id += 1
        self.string_literals[literal] = label
        return label

    def field_offset(self, field_name: str) -> int:
        """Devuelve offset en bytes para un campo de objeto (global, no por clase)."""
        if field_name not in self.field_offsets:
            self.field_offsets[field_name] = self.next_field_offset
            self.next_field_offset += 4
        return self.field_offsets[field_name]


    def load_operand_to_reg(self, operand: str, target_reg: str, is_array: bool = False) -> str:
        """
        Garantiza que 'operand' quede en 'target_reg'.
        Mejorado: detecta parámetros y variables locales, evita moves innecesarios.
        """
        # Si es acceso a arreglo tipo xs[idx]
        if isinstance(operand, str) and '[' in operand and ']' in operand:
            # Extraer nombre y el índice
            arr_name = operand[:operand.index('[')]
            idx_str = operand[operand.index('[')+1:operand.index(']')]
            try:
                idx = int(idx_str)
            except Exception:
                idx = idx_str
            # la $t0, xs
            self.emit(f"    la $t0, {arr_name}")
            # li $t1, idx
            self.emit(f"    li $t1, {idx}")
            # mul $t1, $t1, 4
            self.emit(f"    mul $t1, $t1, 4")
            # add $t0, $t0, $t1
            self.emit(f"    add $t0, $t0, $t1")
            # lw $t2, 0($t0)
            self.emit(f"    lw {target_reg}, 0($t0)")
            return target_reg
        
        # Si es temporal
        if self.is_temp(operand):
            reg = self.temp_reg(operand)
            # Mejora: evitar move si ya está en el registro destino
            if reg != target_reg:
                self.emit(f"    move {target_reg}, {reg}")
            return target_reg
        
        elif self.is_immediate(operand):
            self.emit(f"    li {target_reg}, {operand}")
            return target_reg
        
        elif self.is_string_literal(operand):
            lbl = self.string_label_for(operand)
            self.emit(f"    la {target_reg}, {lbl}")
            return target_reg
        
        else:
            # Puede ser: variable global, parámetro, o variable local
            # Si estamos en una función, verificar si es parámetro
            if self.current_func and operand in self.current_func_params:
                # Es un parámetro: cargar desde stack frame
                param_idx = self.current_func_params.index(operand)
                # Los argumentos fueron guardados por el llamador ANTES del frame de esta función
                # Después del prologue: $fp apunta al inicio del frame actual
                # Los argumentos están ANTES del frame, en offsets positivos desde $fp
                # Frame actual: $fp apunta aquí
                # Argumentos: están en $fp + frame_size, $fp + frame_size + 4, etc.
                frame_size = self.func_frame_sizes.get(self.current_func, 32)
                arg_offset = frame_size + (param_idx * 4)
                self.emit(f"    lw {target_reg}, {arg_offset}($fp)")
                return target_reg
            
            # Si es variable local (detectada por STORE previo)
            if self.current_func and operand in self.current_func_locals:
                # Variable local: está en el stack frame (offsets negativos)
                # Por ahora, tratarla como global (se mejorará con frame dinámico)
                self.ensure_global(operand)
                self.emit(f"    lw {target_reg}, {operand}")
                return target_reg
            
            # Variable global
            self.ensure_global(operand)
            if is_array:
                self.emit(f"    la {target_reg}, {operand}")
            else:
                self.emit(f"    lw {target_reg}, {operand}")
            return target_reg

    def is_temp_addr(self, name: Optional[str]) -> bool:
        # Heurística: si es un temporal (tN) lo tratamos como dirección calculada
        return self.is_temp(name)

    def is_static_array(self, name: str) -> bool:
        """Verifica si un nombre es un array estático"""
        # Necesitamos pasar static_arrays como atributo de la clase
        return hasattr(self, 'static_arrays') and name in self.static_arrays


    def emit_epilogue(self):
        """Emite el epílogo mejorado con frame size dinámico."""
        func_name = getattr(self, 'current_func', None)
        frame_size = self.func_frame_sizes.get(func_name, 32) if func_name else 32
        
        self.emit("    move $sp, $fp")
        self.emit(f"    lw $ra, {frame_size - 4}($sp)")
        self.emit(f"    lw $fp, {frame_size - 8}($sp)")
        self.emit(f"    addi $sp, $sp, {frame_size}")
        
        # Si estamos en main, terminar con syscall
        if func_name == 'func_main' or func_name == 'main':
            self.emit("    li $v0, 10                # service: exit")
            self.emit("    syscall")
        else:
            self.emit("    jr $ra")

    # ---------------------------------------------------------
    # ACA PASA LA MAGIA DEL TAC
    # ---------------------------------------------------------
    def instr_to_mips(self, instr: Instr) -> None:
        op = instr.op
        dst = getattr(instr, "dst", None)
        a = getattr(instr, "a", None)
        b = getattr(instr, "b", None)

        # ---------- Relacionales ----------
        if op in ("EQ", "NE", "LT", "LE", "GT", "GE"):
            if dst is None or not self.is_temp(dst):
                return

            rd = self.temp_reg(dst)
            ra = self.load_operand_to_reg(a, "$t9")
            rb = self.load_operand_to_reg(b, "$t8")

            if op == "EQ":
                self.emit(f"    seq {rd}, {ra}, {rb}")
            elif op == "NE":
                self.emit(f"    sne {rd}, {ra}, {rb}")
            elif op == "LT":
                self.emit(f"    slt {rd}, {ra}, {rb}")
            elif op == "LE":
                self.emit(f"    sle {rd}, {ra}, {rb}")
            elif op == "GT":
                self.emit(f"    sgt {rd}, {ra}, {rb}")
            elif op == "GE":
                self.emit(f"    sge {rd}, {ra}, {rb}")

            return

        # ---------- Lógicos ----------
        if op in ("AND", "OR"):
            if dst is None or not self.is_temp(dst):
                return

            rd = self.temp_reg(dst)
            ra = self.load_operand_to_reg(a, "$t9")
            rb = self.load_operand_to_reg(b, "$t8")

            if op == "AND":
                self.emit(f"    and {rd}, {ra}, {rb}")
            elif op == "OR":
                self.emit(f"    or {rd}, {ra}, {rb}")

            return

        # ---------- NOT ----------
        if op == "NOT":
            if dst is None or not self.is_temp(dst):
                return

            rd = self.temp_reg(dst)
            ra = self.load_operand_to_reg(a, "$t9")
            self.emit(f"    seq {rd}, {ra}, $zero")
            return

        # Soporte para CALL con asignación: tX = CALL foo
        if op == "CALL" and dst is not None and dst not in ("None", ""):
            # Llama como siempre, pero mueve el resultado a dst
            # Simula como si fuera CALL a; dst = $v0
            # Llama a la función normalmente
            self.instr_to_mips(Instr("CALL", a=a))
            if self.is_temp(dst):
                rd = self.temp_reg(dst)
                self.emit(f"    move {rd}, $v0")
            else:
                self.ensure_global(dst)
                self.emit(f"    sw $v0, {dst}")
            return

        # Soporte para PRINT con asignación a None: None = PRINT t1
        if op == "PRINT" and dst == "None":
            # Ejecuta como PRINT normal
            instr2 = Instr("PRINT", a=a)
            self.instr_to_mips(instr2)
            return

        # Soporte para tX = LOAD var o tX = LOAD t_addr (acceso a memoria)
        if op == "LOAD" and dst is not None and self.is_temp(dst):
            rd = self.temp_reg(dst)
            if a is None:
                return
            if self.is_immediate(a) or self.is_string_literal(a):
                self.load_operand_to_reg(a, rd)
            elif self.is_temp_addr(a):
                reg_addr = self.temp_reg(a)
                self.emit(f"    lw {rd}, 0({reg_addr})")
            else:
                is_arr = self.is_static_array(a)
                self.ensure_global(a)
                if is_arr:
                    self.emit(f"    la {rd}, {a}")  # Load address para arrays
                else:
                    self.emit(f"    lw {rd}, {a}")  # Load word para variables normales
            return

        # Soporte para tX = GETPROP tY, campo
        if op == "GETPROP" and dst is not None and self.is_temp(dst):
            # Espera: GETPROP dst, obj, campo
            # Si a y b no están, pero hay un campo extra, intenta extraerlo
            if a is not None and b is not None:
                rd = self.temp_reg(dst)
                obj = a
                field = b
                offset = self.field_offset(field)
                self.load_operand_to_reg(obj, "$t9")
                if offset != 0:
                    self.emit(f"    addi $t9, $t9, {offset}")
                self.emit(f"    lw {rd}, 0($t9)")
                return

        # Soporte para SETPROP tY, campo, tX
        if op == "SETPROP" and a is not None and b is not None and dst is not None:
            obj = a
            field = b
            val = dst
            offset = self.field_offset(field)
            self.load_operand_to_reg(obj, "$t9")
            if offset != 0:
                self.emit(f"    addi $t9, $t9, {offset}")
            reg_val = self.load_operand_to_reg(val, "$t8")
            if reg_val != "$t8":
                self.emit(f"    move $t8, {reg_val}")
            self.emit("    sw $t8, 0($t9)")
            return

        # ---------- LABEL ----------
        if op == "LABEL":
            lbl = dst
            if not lbl:
                return

            if lbl.startswith("func_") or lbl.startswith("method_"):
                self.current_func = lbl
                # Inicializar parámetros y locales para esta función
                self.current_func_params = self.func_params.get(lbl, [])
                self.current_func_locals = self.func_local_vars.get(lbl, set())
                
                if lbl == "func_main":
                    self.has_main = True
                    self.emit("main:")
                else:
                    self.emit(f"{lbl}:")
                
                # Calcular frame size dinámico
                # Base: 8 bytes para $ra y $fp
                # + 4 bytes por cada variable local
                num_locals = len(self.current_func_locals)
                frame_size = 8 + (num_locals * 4)
                # Mínimo 32 bytes para compatibilidad
                if frame_size < 32:
                    frame_size = 32
                # Alinear a múltiplo de 8 (convención MIPS)
                if frame_size % 8 != 0:
                    frame_size = ((frame_size // 8) + 1) * 8
                
                self.func_frame_sizes[lbl] = frame_size
                
                # Prologue mejorado con frame size dinámico
                self.emit(f"    addi $sp, $sp, -{frame_size}")
                self.emit(f"    sw $ra, {frame_size - 4}($sp)")
                self.emit(f"    sw $fp, {frame_size - 8}($sp)")
                self.emit("    move $fp, $sp")
                
                # Si es un constructor (newClase), reservar heap aquí
                if lbl.startswith("func_new") or lbl.startswith("method_new"):
                    self.emit("    lw $t9, heap_ptr")
                    self.emit("    move $v0, $t9")
                    self.emit("    addi $t9, $t9, 32")
                    self.emit("    sw $t9, heap_ptr")
            else:
                self.emit(f"{lbl}:")
            return
        # ---------- GOTO ----------
        if op == "GOTO":
            if dst:
                self.emit(f"    j {dst}")
            return

        # ---------- IFZ ----------
        if op == "IFZ":
            # if a == 0: goto dst
            if a is None or dst is None:
                return
            reg = self.load_operand_to_reg(a, "$t9")
            # Salta si la condición es falsa (a == 0)
            self.emit(f"    beq {reg}, $zero, {dst}")
            # El flujo sigue al bloque if si la condición es verdadera
            return
        # ---------- STORE ----------
        if op == "STORE":
            if dst is None:
                return
            
            # IGNORAR STORE a arrays estáticos
            if hasattr(self, 'static_arrays') and dst in self.static_arrays:
                return  # No emitir nada para arrays estáticos
        
            # dst = a   (asignación a temporal)
            if self.is_temp(dst):
                rd = self.temp_reg(dst)
                if a is None:
                    return
                self.load_operand_to_reg(a, rd)
                return

            # Si dst es un temporal (dirección calculada), acceso a memoria (arreglo)
            if self.is_temp_addr(dst):
                reg_addr = self.temp_reg(dst)
                reg_val = self.load_operand_to_reg(a, "$t9")
                self.emit(f"    sw {reg_val}, 0({reg_addr})")
                return

            # Si estamos en una función y dst no es global conocida, es variable local
            if self.current_func and not self.is_temp(dst) and dst not in self.global_vars:
                # Registrar como variable local
                if self.current_func not in self.func_local_vars:
                    self.func_local_vars[self.current_func] = set()
                self.func_local_vars[self.current_func].add(dst)
                self.current_func_locals.add(dst)
                # Por ahora, tratarla como global (se mejorará con frame dinámico completo)
                self.ensure_global(dst)

            # global = a o local = a
            self.ensure_global(dst)
            # Si la variable global ya está inicializada en .data y a == 0, NO sobrescribas
            if hasattr(self, 'static_arrays') and dst in self.static_arrays:
                return
            if a is None:
                return
            # Si la variable global es un arreglo inicializado, no sobrescribas
            if hasattr(self, 'static_arrays') and dst in self.static_arrays:
                return
            reg = self.load_operand_to_reg(a, "$t9")
            self.emit(f"    sw {reg}, {dst}")
            return

        # ---------- LOAD ----------
        if op == "LOAD":
            # LOAD dst, a   => dst = contenido de variable/parámetro a
            if dst is None or not self.is_temp(dst):
                return
            rd = self.temp_reg(dst)
            if a is None:
                return
            if self.is_immediate(a) or self.is_string_literal(a):
                # caso degenerado: lo tratamos como literal
                self.load_operand_to_reg(a, rd)
            else:
                # Usar load_operand_to_reg que ahora maneja parámetros y locales
                self.load_operand_to_reg(a, rd)
            return

        # ---------- Aritmética ----------
        if op in ("ADD", "SUB", "MUL", "DIV"):
            if dst is None or not self.is_temp(dst):
                return
            rd = self.temp_reg(dst)
            if a is None or b is None:
                return
            # Si alguno de los operandos es acceso a arreglo, usa el patrón profesional
            if (isinstance(a, str) and '[' in a and ']' in a) or (isinstance(b, str) and '[' in b and ']' in b):
                # a y/o b pueden ser acceso a arreglo
                if isinstance(a, str) and '[' in a and ']' in a:
                    self.load_operand_to_reg(a, "$t7")
                    ra = "$t7"
                else:
                    ra = self.load_operand_to_reg(a, "$t7")
                if isinstance(b, str) and '[' in b and ']' in b:
                    self.load_operand_to_reg(b, "$t1")
                    rb = "$t1"
                else:
                    rb = self.load_operand_to_reg(b, "$t1")
            else:
                ra = self.load_operand_to_reg(a, "$t7")
                rb = self.load_operand_to_reg(b, "$t1")
            if op == "ADD":
                self.emit(f"    add {rd}, {ra}, {rb}")
            elif op == "SUB":
                self.emit(f"    sub {rd}, {ra}, {rb}")
            elif op == "MUL":
                self.emit(f"    mul {rd}, {ra}, {rb}")
            elif op == "DIV":
                self.emit(f"    div {ra}, {rb}")
                self.emit(f"    mflo {rd}")
            return

        # ---------- ARG ----------
        if op == "ARG":
            # vamos acumulando los argumentos hasta ver CALL
            if a is not None:
                self.pending_args.append(a)
            return

        # ---------- CALL ----------
        if op == "CALL":
            func_name = a
            if func_name is None:
                return

            num_args = len(self.pending_args)
            
            # Mejora: Guardar registros caller-saved que están en uso
            # Por simplicidad, guardamos $t0-$t9 si contienen valores importantes
            # (En una implementación completa, haríamos análisis de liveness)
            
            if num_args > 0:
                # Guardar cada argumento en el stack ANTES de llamar
                # Los argumentos se guardan en el stack del llamador
                # IMPORTANTE: Guardar ANTES de hacer jal, porque jal puede modificar $ra
                
                # Mejora: usar $a0-$a3 para primeros 4 argumentos (convención MIPS)
                # Pero también guardarlos en stack para que la función los lea desde ahí
                for idx, arg in enumerate(self.pending_args):
                    if idx < 4:
                        # Primeros 4: cargar en $a0-$a3 Y guardar en stack
                        arg_reg = f"$a{idx}"
                        reg = self.load_operand_to_reg(arg, arg_reg)
                        if reg != arg_reg:
                            self.emit(f"    move {arg_reg}, {reg}")
                    else:
                        # Resto: solo cargar en registro temporal
                        reg = self.load_operand_to_reg(arg, "$t9")
                
                # Reservar espacio para args en el stack
                self.emit(f"    addi $sp, $sp, -{4 * num_args}")
                
                # Guardar todos los argumentos en el stack
                for idx, arg in enumerate(self.pending_args):
                    if idx < 4:
                        # Usar $a0-$a3 que ya tienen el valor
                        arg_reg = f"$a{idx}"
                        self.emit(f"    sw {arg_reg}, {idx * 4}($sp)")
                    else:
                        # Usar el registro donde se cargó
                        reg = self.load_operand_to_reg(arg, "$t9")
                        self.emit(f"    sw {reg}, {idx * 4}($sp)")
            
            # Llamada
            self.emit(f"    jal {func_name}")
            
            # Liberar espacio de argumentos
            if num_args > 0:
                self.emit(f"    addi $sp, $sp, {4 * num_args}")
            
            # Resultado en dst si corresponde
            if dst is not None and dst not in ("None", ""):
                if self.is_temp(dst):
                    rd = self.temp_reg(dst)
                    self.emit(f"    move {rd}, $v0")
                else:
                    self.ensure_global(dst)
                    self.emit(f"    sw $v0, {dst}")
            
            # Limpiar lista de args
            self.pending_args = []
            return

        # ---------- RET (RETURN) ----------
        if op == "RET":
            val = dst if dst is not None else a
            if val is not None:
                reg = self.load_operand_to_reg(val, "$v0")
                if reg != "$v0":
                    self.emit(f"    move $v0, {reg}")
            # epílogo profesional
            self.emit_epilogue()
            return

        # ---------- NEWOBJ ----------
        if op == "NEWOBJ":
            # NEWOBJ dst, Clase
            if dst is None or a is None:
                return
            class_name = a
            self.uses_heap = True
            
            rd = self.temp_reg(dst) if self.is_temp(dst) else "$t9"
            
            # Reservar espacio en heap: objeto + vtable pointer
            self.emit("    lw $t9, heap_ptr")
            self.emit(f"    move {rd}, $t9")
            
            # Reservar 32 bytes para objeto + 4 bytes para vtable pointer = 36 bytes
            self.emit("    addi $t9, $t9, 36")
            self.emit("    sw $t9, heap_ptr")
            
            # Inicializar vtable pointer en offset 0 del objeto
            vtable_label = f"__vtable_{class_name}"
            self.emit(f"    la $t8, {vtable_label}")
            self.emit(f"    sw $t8, 0({rd})")
            
            if not self.is_temp(dst):
                self.ensure_global(dst)
                self.emit(f"    sw {rd}, {dst}")
            return

        # ---------- ALLOC ----------
        if op == "ALLOC":
            # ALLOC dst, a   ; a = número de enteros
            if dst is None or not self.is_temp(dst):
                return
            if a is None:
                return
            self.uses_heap = True
            rd = self.temp_reg(dst)
            # bytes = a * 4
            if self.is_immediate(a):
                bytes_num = int(a) * 4
                self.emit("    lw $t9, heap_ptr")
                self.emit(f"    move {rd}, $t9")
                self.emit(f"    addi $t9, $t9, {bytes_num}")
                self.emit("    sw $t9, heap_ptr")
            else:
                # a en registro
                ra = self.load_operand_to_reg(a, "$t8")
                self.emit("    lw $t9, heap_ptr")
                self.emit(f"    move {rd}, $t9")
                # bytes = a * 4
                self.emit("    sll $t8, $t8, 2")
                self.emit("    add $t9, $t9, $t8")
                self.emit("    sw $t9, heap_ptr")
            return

        # ---------- GETPROP ----------
        if op == "GETPROP":
            # GETPROP dst, obj, campo
            if dst is None or not self.is_temp(dst):
                return
            if a is None or b is None:
                return
            rd = self.temp_reg(dst)
            obj = a
            field = b
            offset = self.field_offset(field)  # bytes
            # cargar puntero obj en $t9
            self.load_operand_to_reg(obj, "$t9")
            if offset != 0:
                self.emit(f"    addi $t9, $t9, {offset}")
            self.emit(f"    lw {rd}, 0($t9)")
            return

        # ---------- SETPROP ----------
        if op == "SETPROP":
            # SETPROP obj, campo, val  (a=obj, b=campo, dst=val)
            if a is None or b is None or dst is None:
                return
            obj = a
            field = b
            val = dst
            offset = self.field_offset(field)
            # obj -> $t9
            self.load_operand_to_reg(obj, "$t9")
            if offset != 0:
                self.emit(f"    addi $t9, $t9, {offset}")
            # val -> $t8
            reg_val = self.load_operand_to_reg(val, "$t8")
            if reg_val != "$t8":
                self.emit(f"    move $t8, {reg_val}")
            self.emit("    sw $t8, 0($t9)")
            return

        # ---------- PRINT ----------
        if op == "PRINT":
            if a is None:
                return
            # Detectar si es string o entero
            if self.is_string_literal(a):
                reg = self.load_operand_to_reg(a, "$a0")
                if reg != "$a0":
                    self.emit(f"    move $a0, {reg}")
                self.emit("    li $v0, 4")
                self.emit("    syscall")
            else:
                reg = self.load_operand_to_reg(a, "$a0")
                if reg != "$a0":
                    self.emit(f"    move $a0, {reg}")
                self.emit("    li $v0, 1")
                self.emit("    syscall")
            return

        # ---------- THROW (para excepciones) ----------
        if op == "THROW":
            # THROW a  -> lanzar excepción con valor a
            if a is None:
                return
            # Cargar valor de excepción
            reg = self.load_operand_to_reg(a, "$v0")
            if reg != "$v0":
                self.emit(f"    move $v0, {reg}")
            # Saltar al handler de excepción más reciente
            if self.exception_handler_stack:
                handler_label = self.exception_handler_stack[-1]
                self.emit(f"    j {handler_label}")
            else:
                # Si no hay handler, terminar programa
                self.emit("    li $v0, 10")
                self.emit("    syscall")
            return

        # ---------- VTABLE (para herencia y polimorfismo) ----------
        if op == "VTABLE":
            # VTABLE dst, class_name  -> cargar vtable de clase en dst
            if dst is None or a is None:
                return
            class_name = a
            vtable_label = f"__vtable_{class_name}"
            rd = self.temp_reg(dst) if self.is_temp(dst) else "$t9"
            self.emit(f"    la {rd}, {vtable_label}")
            if not self.is_temp(dst):
                self.ensure_global(dst)
                self.emit(f"    sw {rd}, {dst}")
            return

        # ---------- VCALL (llamada virtual/polimórfica) ----------
        if op == "VCALL":
            # VCALL dst, obj, method_name, args...
            # obj es un temporal que contiene el puntero al objeto
            # method_name es el nombre del método
            # Los argumentos vienen en pending_args
            if a is None or b is None:
                return
            obj_temp = a
            method_name = b
            
            # Cargar objeto
            obj_reg = self.load_operand_to_reg(obj_temp, "$t9")
            
            # La vtable está en el offset 0 del objeto
            # Cargar vtable
            self.emit(f"    lw $t8, 0({obj_reg})")
            
            # Buscar método en vtable (simplificado: asumimos offset conocido)
            # En una implementación real, buscaríamos el índice del método
            method_offset = 0  # Por ahora, simplificado
            
            # Cargar dirección del método desde vtable
            self.emit(f"    lw $t7, {method_offset}($t8)")
            
            # Preparar argumentos (similar a CALL normal)
            num_args = len(self.pending_args)
            if num_args > 0:
                self.emit(f"    addi $sp, $sp, -{4 * num_args}")
                for idx, arg in enumerate(self.pending_args):
                    if idx < 4:
                        arg_reg = f"$a{idx}"
                        reg = self.load_operand_to_reg(arg, arg_reg)
                        if reg != arg_reg:
                            self.emit(f"    move {arg_reg}, {reg}")
                        self.emit(f"    sw {arg_reg}, {idx * 4}($sp)")
                    else:
                        reg = self.load_operand_to_reg(arg, "$t9")
                        self.emit(f"    sw {reg}, {idx * 4}($sp)")
            
            # Llamar método virtual (jalr usa registro)
            self.emit("    jalr $t7")
            
            # Liberar argumentos
            if num_args > 0:
                self.emit(f"    addi $sp, $sp, {4 * num_args}")
            
            # Guardar resultado
            if dst is not None and dst not in ("None", ""):
                if self.is_temp(dst):
                    rd = self.temp_reg(dst)
                    self.emit(f"    move {rd}, $v0")
                else:
                    self.ensure_global(dst)
                    self.emit(f"    sw $v0, {dst}")
            
            self.pending_args = []
            return

        # Si llega aquí, es un opcode no soportado explícitamente.
        # Lo ignoramos silenciosamente para no romper el backend.
        return

    def emit_from_emitter(self, emitter: Emitter, out_path: Optional[str] = None, static_arrays: Optional[dict] = None, symtab=None) -> str:
        """Convierte todas las instrucciones TAC en código MIPS."""
        
        self.static_arrays = static_arrays or {}
        
        # Primera pasada: detectar parámetros de funciones desde symtab si está disponible
        if symtab:
            # Buscar funciones en symtab y extraer sus parámetros
            for scope in getattr(symtab, 'scopes', []):
                for name, symbol in getattr(scope, 'symbols', {}).items():
                    if hasattr(symbol, 'params') and hasattr(symbol, 'name'):
                        # Es una función
                        func_name = symbol.name
                        func_label = f"func_{func_name}"
                        if hasattr(symbol, 'params') and symbol.params:
                            param_names = [p.name for p in symbol.params if hasattr(p, 'name')]
                            self.func_params[func_label] = param_names
        
        # recorrer instrucciones TAC
        for instr in emitter.instrs:
            self.instr_to_mips(instr)

        # construir salida final
        out_lines: List[str] = []

        # Sección .data
        out_lines.append(".data")
        
        # ✅ Primero emitir los arrays estáticos
        if static_arrays:
            for name, elems in static_arrays.items():
                elems_str = ", ".join(str(e) for e in elems)
                out_lines.append(f"{name}: .word {elems_str}")
        
        # Luego emitir las variables globales normales
        for name in sorted(self.global_vars):
            # ✅ Saltar si ya está en static_arrays
            if static_arrays and name in static_arrays:
                continue
            out_lines.append(f"{name}: .word 0")

        # literales de string
        for literal, lbl in self.string_literals.items():
            val = literal[1:-1]
            out_lines.append(f'{lbl}: .asciiz "{val}"')

        # heap si es necesario
        if self.uses_heap:
            out_lines.append("heap: .space 4096")
            out_lines.append("heap_ptr: .word heap")

        # Vtables para herencia (generar una por cada clase)
        # Construir vtables completas incluyendo métodos heredados recursivamente
        complete_vtables = {}
        for class_name in self.class_vtables.keys():
            complete_vtable = {}
            # Agregar métodos de la clase (estos sobrescriben los heredados)
            if class_name in self.class_vtables:
                complete_vtable.update(self.class_vtables[class_name])
            
            # Agregar métodos heredados (recursivamente por la jerarquía)
            parent = self.class_hierarchy.get(class_name)
            visited_parents = set()
            while parent and parent in self.class_vtables and parent not in visited_parents:
                visited_parents.add(parent)
                for method_name, method_label in self.class_vtables[parent].items():
                    # Solo agregar si no está sobrescrito
                    if method_name not in complete_vtable:
                        complete_vtable[method_name] = method_label
                parent = self.class_hierarchy.get(parent)
            
            complete_vtables[class_name] = complete_vtable
        
        # Generar vtables en .data
        for class_name, methods in complete_vtables.items():
            vtable_label = f"__vtable_{class_name}"
            out_lines.append(f"{vtable_label}:")
            # Generar entradas de vtable (una por método, ordenadas por nombre)
            for method_name, method_label in sorted(methods.items()):
                out_lines.append(f"    .word {method_label}")

        out_lines.append("")

        # Sección .text
        out_lines.append(".text")
        if self.has_main:
            out_lines.append(".globl main")

        for line in self.text_lines:
            # No emitir la etiqueta 'end_main:'
            if line.strip() == 'end_main:':
                continue
            out_lines.append(line)

        out = "\n".join(out_lines)


        # Si el final profesional no está presente al final, agregarlo
        out_lines_clean = [line.strip() for line in out.splitlines() if line.strip()]
        if not any(l.startswith('li $v0, 10') for l in out_lines_clean[-4:]) and not any(l == 'syscall' for l in out_lines_clean[-2:]):
            out = out.rstrip() + '\n    li $v0, 10                # service: exit\n    syscall\n'

        if out_path is not None:
            with open(out_path, "w", encoding="utf-8") as f:
                f.write(out)

        return out


def emit_mips(emitter: Emitter, symtab=None, out_path: Optional[str] = None, static_arrays: Optional[dict] = None) -> str:
    backend = MIPSBackend()
    return backend.emit_from_emitter(emitter, out_path, static_arrays=static_arrays, symtab=symtab)