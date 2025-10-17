#!/usr/bin/env python3
import sys
import os

# Agregar el directorio program al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'program'))

# Leer el archivo y buscar visitExpression
with open('program/CompiscriptVisitor.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if 'def visitExpression(' in line:
        print(f"Línea {i+1}: {line.strip()}")
        # Mostrar las siguientes 5 líneas
        for j in range(1, 6):
            if i+j < len(lines):
                print(f"Línea {i+j+1}: {lines[i+j].strip()}")
        break
else:
    print("No se encontró visitExpression en CompiscriptVisitor")
