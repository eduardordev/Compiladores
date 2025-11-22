# Compiscript - Proyecto listo (Python + ANTLR)

## Pasos
1) Entra a `program/` y genera parser/lexer:

```bash
antlr -Dlanguage=Python3 Compiscript.g4
```

2) Instala dependencias:

```bash
pip install -r requirements.txt
```

3) Prueba el driver:

```bash
python3 program/Driver.py program/program.cps
```

4) IDE mínimo:

```bash
python3 program/ide/mini_ide.py
```

5) Tests:

```bash
pytest -q
```
