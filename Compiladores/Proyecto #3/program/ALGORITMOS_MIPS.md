# Algoritmos de Generación de Código MIPS

## 1. Algoritmo de Selección de Registros (20%)

### Descripción General
El algoritmo de selección de registros es responsable de mapear las variables temporales del código TAC (Three-Address Code) a los registros físicos disponibles en MIPS. En MIPS, los registros temporales son `$t0` a `$t9` (10 registros en total).

### Implementación Actual

#### Función `temp_reg()` (líneas 51-58)
```python
def temp_reg(self, tname: str) -> str:
    """Mapea t0, t1, ... a $t0..$t9 (cíclico)."""
    try:
        n = int(tname[1:])
    except ValueError:
        n = 0
    n = n % 10
    return f"$t{n}"
```

**Algoritmo:**
1. Extrae el número del temporal TAC (ej: `t5` → `5`)
2. Aplica módulo 10 para obtener un valor entre 0-9
3. Retorna el registro MIPS correspondiente (`$t0` a `$t9`)

**Ejemplo:**
- `t0` → `$t0`
- `t5` → `$t5`
- `t10` → `$t0` (cíclico: 10 % 10 = 0)
- `t15` → `$t5` (cíclico: 15 % 10 = 5)

### Función `load_operand_to_reg()` (líneas 92-137)

Esta función garantiza que un operando (temporal, inmediato, string, o variable global) quede cargado en un registro específico.

**Algoritmo:**
1. **Si es acceso a arreglo** (`xs[idx]`):
   - Carga la dirección base en `$t0`
   - Calcula el offset en `$t1` (índice × 4 bytes)
   - Suma base + offset
   - Carga el valor en el registro destino

2. **Si es temporal** (`tN`):
   - Obtiene el registro MIPS usando `temp_reg()`
   - Si no está en el registro destino, hace `move` para copiarlo

3. **Si es inmediato** (número):
   - Usa `li` (load immediate) para cargar el valor

4. **Si es string literal**:
   - Obtiene la etiqueta del string
   - Usa `la` (load address) para cargar la dirección

5. **Si es variable global**:
   - Registra la variable como global
   - Usa `lw` (load word) para cargar el valor desde memoria

### Estrategia de Asignación

**Ventajas del mapeo cíclico:**
- Simple y rápido de implementar
- No requiere análisis de liveness
- Funciona para programas pequeños/medianos

**Limitaciones:**
- Puede sobrescribir valores de temporales que aún se necesitan
- No optimiza el uso de registros
- Requiere guardar/cargar desde memoria cuando hay conflictos

**Ejemplo de uso:**
```mips
# TAC: t0 = ADD t1, t2
# t1 → $t1, t2 → $t2, t0 → $t0
lw $t1, var1      # Cargar t1
lw $t2, var2      # Cargar t2
add $t0, $t1, $t2 # Resultado en $t0
```

---

## 2. Algoritmo para Llamadas a Procedimientos y Retornos

### Descripción General
Este algoritmo maneja la convención de llamadas a funciones en MIPS, incluyendo:
- Paso de argumentos
- Guardado/restauración del frame pointer y return address
- Manejo del stack
- Retorno de valores

### Componentes del Algoritmo

#### A. Prologue (Prólogo) - Líneas 304-308

Cuando se encuentra una etiqueta de función (`LABEL func_xxx`):

```python
# Prologue estándar para TODA función
self.emit("    addi $sp, $sp, -32")    # Reservar espacio en stack
self.emit("    sw $ra, 28($sp)")       # Guardar return address
self.emit("    sw $fp, 24($sp)")       # Guardar frame pointer anterior
self.emit("    move $fp, $sp")         # Nuevo frame pointer = stack pointer
```

**Stack Frame Layout:**
```
$sp (antes) ──┐
              │
              ├─ 28($sp): $ra (return address)
              ├─ 24($sp): $fp (frame pointer anterior)
              │
              │ (espacio para variables locales)
              │
$fp = $sp ────┘
```

#### B. Paso de Argumentos - Líneas 422-427

**Instrucción ARG:**
```python
if op == "ARG":
    if a is not None:
        self.pending_args.append(a)  # Acumula argumentos
```

Los argumentos se acumulan en `self.pending_args` hasta encontrar un `CALL`.

#### C. Llamada a Función (CALL) - Líneas 429-460

**Algoritmo completo:**

```python
if op == "CALL":
    func_name = a
    num_args = len(self.pending_args)
    
    # 1. Reservar espacio en stack para argumentos
    if num_args > 0:
        self.emit(f"    addi $sp, $sp, -{4 * num_args}")
    
    # 2. Guardar cada argumento en el stack
    for idx, arg in enumerate(self.pending_args):
        reg = self.load_operand_to_reg(arg, "$t9")
        self.emit(f"    sw {reg}, {idx * 4}($sp)")
    
    # 3. Llamar a la función (jal salta y guarda $ra)
    self.emit(f"    jal {func_name}")
    
    # 4. Liberar espacio de argumentos del stack
    if num_args > 0:
        self.emit(f"    addi $sp, $sp, {4 * num_args}")
    
    # 5. Guardar resultado si hay destino
    if dst is not None:
        if self.is_temp(dst):
            rd = self.temp_reg(dst)
            self.emit(f"    move {rd}, $v0")  # $v0 contiene el retorno
        else:
            self.emit(f"    sw $v0, {dst}")   # Guardar en variable global
    
    # 6. Limpiar lista de argumentos
    self.pending_args = []
```

**Convención MIPS:**
- `$v0`: Registro de retorno (valor devuelto)
- `$ra`: Return address (guardado automáticamente por `jal`)
- `$fp`: Frame pointer (apunta al inicio del frame actual)
- `$sp`: Stack pointer (apunta al tope del stack)

**Ejemplo de llamada:**
```mips
# TAC: ARG 10; ARG 20; CALL Sumar
addi $sp, $sp, -8      # Reservar espacio para 2 argumentos
li $t9, 10
sw $t9, 0($sp)         # Primer argumento en 0($sp)
li $t9, 20
sw $t9, 4($sp)         # Segundo argumento en 4($sp)
jal Sumar              # Llamar función
addi $sp, $sp, 8       # Liberar espacio
move $t0, $v0          # Guardar resultado si hay destino
```

#### D. Retorno de Función (RET) - Líneas 462-471

```python
if op == "RET":
    val = dst if dst is not None else a
    
    # 1. Cargar valor de retorno en $v0
    if val is not None:
        reg = self.load_operand_to_reg(val, "$v0")
        if reg != "$v0":
            self.emit(f"    move $v0, {reg}")
    
    # 2. Ejecutar epílogo
    self.emit_epilogue()
```

#### E. Epilogue (Epílogo) - Líneas 149-160

```python
def emit_epilogue(self):
    # 1. Restaurar stack pointer al frame pointer
    self.emit("    move $sp, $fp")
    
    # 2. Restaurar return address
    self.emit("    lw $ra, 28($sp)")
    
    # 3. Restaurar frame pointer anterior
    self.emit("    lw $fp, 24($sp)")
    
    # 4. Liberar espacio del frame
    self.emit("    addi $sp, $sp, 32")
    
    # 5. Retornar o terminar programa
    if es_main:
        self.emit("    li $v0, 10")    # syscall exit
        self.emit("    syscall")
    else:
        self.emit("    jr $ra")        # Jump to return address
```

### Flujo Completo de una Llamada

**Función llamadora:**
```mips
# 1. Preparar argumentos
ARG 10
ARG 20

# 2. Llamar función
CALL Sumar
# Genera:
addi $sp, $sp, -8
li $t9, 10
sw $t9, 0($sp)
li $t9, 20
sw $t9, 4($sp)
jal Sumar
addi $sp, $sp, 8
move $t0, $v0
```

**Función llamada (Sumar):**
```mips
Sumar:
    # Prologue
    addi $sp, $sp, -32
    sw $ra, 28($sp)
    sw $fp, 24($sp)
    move $fp, $sp
    
    # Cuerpo de la función
    # (acceder a argumentos desde stack si es necesario)
    
    # Return
    # (cargar resultado en $v0)
    
    # Epilogue
    move $sp, $fp
    lw $ra, 28($sp)
    lw $fp, 24($sp)
    addi $sp, $sp, 32
    jr $ra
```

### Consideraciones Importantes

1. **Stack crece hacia abajo**: `addi $sp, $sp, -N` reserva espacio
2. **Frame pointer**: Permite acceso consistente a variables locales y argumentos
3. **Return address**: Se guarda automáticamente por `jal`, pero se debe preservar si hay llamadas anidadas
4. **Registro de retorno**: Siempre en `$v0` (y `$v1` si hay dos valores)
5. **Argumentos en stack**: Se pasan en el stack, no en registros (convención simplificada)

### Mejoras Posibles

1. **Pasar argumentos en registros**: Usar `$a0-$a3` para los primeros 4 argumentos (convención MIPS estándar)
2. **Guardar registros callee-saved**: Guardar `$s0-$s7` si la función los usa
3. **Optimización de stack**: Calcular tamaño exacto del frame en lugar de usar 32 bytes fijos
4. **Análisis de liveness**: Para mejor asignación de registros y evitar guardar/cargar innecesarios

