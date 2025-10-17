#!/usr/bin/env python3
import sys
import os

# Agregar el directorio program al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'program'))

from antlr4 import FileStream, CommonTokenStream
from program.CompiscriptLexer import CompiscriptLexer
from program.CompiscriptParser import CompiscriptParser
from program.semantic.visitor import SemanticVisitor
from program.semantic.errors import SemanticError

def test_func_bad():
    print("=== Testing func_bad.cps ===")
    
    filepath = "program/tests/func_bad.cps"
    input_stream = FileStream(filepath, encoding='utf-8')
    lexer = CompiscriptLexer(input_stream)
    tokens = CommonTokenStream(lexer)
    parser = CompiscriptParser(tokens)
    tree = parser.program()
    
    print("AST generated successfully")
    print("Tree structure:")
    print(tree.toStringTree(recog=parser))
    
    print("\nTesting semantic analysis:")
    visitor = SemanticVisitor()
    try:
        visitor.visit(tree)
        print("SUCCESS: No semantic errors detected")
        print(f"Visitor state: in_function={visitor.in_function}, expected_return={visitor.expected_return}")
    except SemanticError as e:
        print(f"SEMANTIC ERROR: {e}")
    except Exception as e:
        print(f"OTHER ERROR: {e}")

if __name__ == "__main__":
    test_func_bad()
