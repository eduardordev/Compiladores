#!/usr/bin/env python3
import sys
import os

# Agregar el directorio program al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'program'))

from antlr4 import FileStream, CommonTokenStream, InputStream
from program.CompiscriptLexer import CompiscriptLexer
from program.CompiscriptParser import CompiscriptParser
from program.semantic.visitor import SemanticVisitor
from program.semantic.errors import SemanticError

def test_specific_case():
    print("=== Testing specific semantic analysis ===")
    
    # Test case 1: Function with wrong return
    code1 = "function f(a: integer): integer { return; }"
    print(f"\nTest 1: {code1}")
    
    input_stream = InputStream(code1)
    lexer = CompiscriptLexer(input_stream)
    tokens = CommonTokenStream(lexer)
    parser = CompiscriptParser(tokens)
    tree = parser.program()
    
    visitor = SemanticVisitor()
    try:
        visitor.visit(tree)
        print("❌ PROBLEM: Should have detected semantic error!")
    except SemanticError as e:
        print(f"✅ CORRECT: Detected error - {e}")
    except Exception as e:
        print(f"❌ OTHER ERROR: {e}")
    
    # Test case 2: Return outside function
    code2 = "return 1;"
    print(f"\nTest 2: {code2}")
    
    input_stream = InputStream(code2)
    lexer = CompiscriptLexer(input_stream)
    tokens = CommonTokenStream(lexer)
    parser = CompiscriptParser(tokens)
    tree = parser.program()
    
    visitor = SemanticVisitor()
    try:
        visitor.visit(tree)
        print("❌ PROBLEM: Should have detected semantic error!")
    except SemanticError as e:
        print(f"✅ CORRECT: Detected error - {e}")
    except Exception as e:
        print(f"❌ OTHER ERROR: {e}")

if __name__ == "__main__":
    test_specific_case()
