#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'program'))

from program.semantic.visitor import SemanticVisitor

# Crear un visitor y verificar métodos
visitor = SemanticVisitor()

# Buscar métodos que contengan "assignment" o "assign"
methods = [method for method in dir(visitor) if 'assignment' in method.lower() or 'assign' in method.lower()]
print("Métodos que contienen 'assignment' o 'assign':")
for method in methods:
    print(f"  {method}")

# Verificar si existe visitAssignmentExpr
if hasattr(visitor, 'visitAssignmentExpr'):
    print("\n✅ visitAssignmentExpr existe")
else:
    print("\n❌ visitAssignmentExpr NO existe")

# Verificar si existe visitAssignExpr
if hasattr(visitor, 'visitAssignExpr'):
    print("✅ visitAssignExpr existe")
else:
    print("❌ visitAssignExpr NO existe")
