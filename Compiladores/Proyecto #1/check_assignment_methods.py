#!/usr/bin/env python3
import sys
import os

# Agregar el directorio program al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'program'))

from program.semantic.visitor import SemanticVisitor

# Buscar métodos que contengan "Assignment" en el nombre
visitor = SemanticVisitor()
methods = [method for method in dir(visitor) if 'Assignment' in method]
print("Métodos que contienen 'Assignment':")
for method in methods:
    print(f"  {method}")

# Buscar métodos que contengan "Assign" en el nombre
methods = [method for method in dir(visitor) if 'Assign' in method]
print("\nMétodos que contienen 'Assign':")
for method in methods:
    print(f"  {method}")
