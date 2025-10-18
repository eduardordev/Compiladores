# Generación de Código Intermedio (TAC)

Este documento explica el formato del TAC (Three Address Code) que genera el proyecto, cómo ejecutar
la generación desde los scripts incluidos y cómo integrar/depurar la salida.

Resumen rápido
- El generador principal es `program/codegen/generate_tac.py`.
- `program/codegen/tac.py` contiene la representación y el emisor (clase `Emitter`).
- `program/codegen/generate_tac.py` invoca el analizador ANTLR, la comprobación semántica y el visitante de generación de TAC.

Formato y ejemplos de instrucciones TAC
- Operación binaria: `t0 = a ADD b` (ADD, SUB, MUL, DIV, etc.)
- Almacenamiento/lectura: `STORE t0 -> x` / `x = LOAD t0`
- Saltos y etiquetas: `IFZ cond GOTO L1` / `LABEL L1:` / `GOTO L2`
- Retorno: `RETURN val` (representado como `RET` internamente en el emisor)

Ejemplo mínimo

Código fuente (Compiscript `.cps`):

```cps
let a = 1;
let b = 2;
let c = a + b;
```

Salida TAC esperada (ejemplo):

```
t0 = 1
t1 = 2
t2 = t0 ADD t1
STORE t2 -> c
```

Cómo ejecutar

- Desde el directorio `program/codegen` (o desde la raíz del proyecto asegurando que `program/` esté en PYTHONPATH):

	Windows PowerShell:

```powershell
# desde la raíz del repo (donde está la carpeta "program")
python -m program.codegen.generate_tac path\to\file.cps
```

	O directamente:

```powershell
python program\codegen\generate_tac.py path\to\file.cps
```

- También puedes generar TAC desde el `Driver.py` usando la opción `--tac`:

```powershell
python program\Driver.py path\to\file.cps --tac
```

Nota: los scripts usan ANTLR runtime (`antlr4-python3-runtime`) y las clases generadas por ANTLR (p. ej. `CompiscriptLexer.py`, `CompiscriptParser.py`).

Problemas comunes y soluciones

- Error: import error de `antlr4` o `CompiscriptParser` / `CompiscriptLexer`
	- Asegúrate de tener instalado el runtime de ANTLR para Python 3: `pip install antlr4-python3-runtime`.
	- Verifica que los ficheros `CompiscriptParser.py` y `CompiscriptLexer.py` existen en `program/` (ya están incluidos en el repo).

- Error: `No se generó ningún código intermedio` o `(sin instrucciones TAC)` como salida
	- Puede indicar que el programa fuente no produce instrucciones TAC (por ejemplo, solo declaraciones sin efecto) o que
		el visitante de generación falló silenciosamente. Ejecuta `generate_tac.py` desde la terminal y revisa salida y errores.

- Problemas semánticos detectados durante generación
	- `generate_tac.py` ejecuta el `SemanticVisitor`. Si hay errores semánticos, aparecerán en stdout/stderr.
	- Para depurar, ejecuta `Driver.py` primero sin `--tac` y con el archivo de prueba para ver mensajes semánticos:

```powershell
python program\Driver.py path\to\file.cps
```

Integración con la IDE

- El IDE `program/ide/mini_ide.py` ya tiene botones para "Ver TAC" que llaman a `Driver.py --tac` y muestran la salida en el panel "TAC".


Detalles técnicos del emisor (`program/codegen/tac.py`)

- `Instr`: dataclass que modela una instrucción. El método `__str__` formatea la instrucción legible.
- `Emitter`: gestiona la lista de instrucciones, temporales (reuso) y etiquetas.
	- `new_temp()` devuelve un temporal reciclado si existe o crea `tN` nuevo.
	- `free_temp(t)` marca un temporal como reutilizable.
	- `new_label()` genera etiquetas `L0`, `L1`, ...
	- `__str__()` serializa la lista de instrucciones en texto legible.


```
