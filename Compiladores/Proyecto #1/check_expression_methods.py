#!/usr/bin/env python3
import sys
import os

# Agregar el directorio program al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'program'))

from program.semantic.visitor import SemanticVisitor

# Buscar métodos que contengan "Expr" en el nombre
visitor = SemanticVisitor()
methods = [method for method in dir(visitor) if 'Expr' in method]
print("Métodos que contienen 'Expr':")
for method in methods:
    print(f"  {method}")

# Buscar específicamente visitAssignmentExpr
if hasattr(visitor, 'visitAssignmentExpr'):
    print("\n✅ visitAssignmentExpr existe")
else:
    print("\n❌ visitAssignmentExpr NO existe")
