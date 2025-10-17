#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'program'))

from antlr4 import InputStream, CommonTokenStream
from program.CompiscriptLexer import CompiscriptLexer
from program.CompiscriptParser import CompiscriptParser

def check_expression_context():
    # Crear un parser y analizar una expresión simple
    code = "1 + 2"
    input_stream = InputStream(code)
    lexer = CompiscriptLexer(input_stream)
    tokens = CommonTokenStream(lexer)
    parser = CompiscriptParser(tokens)
    
    # Crear un programa simple
    program_code = "let x = 1 + 2;"
    input_stream = InputStream(program_code)
    lexer = CompiscriptLexer(input_stream)
    tokens = CommonTokenStream(lexer)
    parser = CompiscriptParser(tokens)
    tree = parser.program()
    
    # Obtener el contexto de expresión
    stmt = tree.statement(0)
    var_decl = stmt.variableDeclaration()
    initializer = var_decl.initializer()
    expression = initializer.expression()
    
    print(f"Expression context type: {expression.__class__.__name__}")
    print(f"Available methods:")
    
    # Listar métodos que contienen 'expr' o 'assign'
    methods = [method for method in dir(expression) if 'expr' in method.lower() or 'assign' in method.lower()]
    for method in methods:
        print(f"  {method}")
    
    # Verificar si tiene assignmentExpr
    if hasattr(expression, 'assignmentExpr'):
        print(f"\n✅ assignmentExpr exists: {expression.assignmentExpr()}")
    else:
        print(f"\n❌ assignmentExpr does not exist")
    
    # Verificar si tiene assignExpr
    if hasattr(expression, 'assignExpr'):
        print(f"✅ assignExpr exists: {expression.assignExpr()}")
    else:
        print(f"❌ assignExpr does not exist")

if __name__ == "__main__":
    check_expression_context()
