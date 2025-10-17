#!/usr/bin/env python3
import sys
import os

# Agregar el directorio program al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'program'))

from program.semantic.visitor import SemanticVisitor

# Buscar métodos que contengan "Expression" en el nombre
visitor = SemanticVisitor()
methods = [method for method in dir(visitor) if 'Expression' in method]
print("Métodos que contienen 'Expression':")
for method in methods:
    print(f"  {method}")

# Buscar específicamente visitExpression
if hasattr(visitor, 'visitExpression'):
    print("\n✅ visitExpression existe")
else:
    print("\n❌ visitExpression NO existe")
