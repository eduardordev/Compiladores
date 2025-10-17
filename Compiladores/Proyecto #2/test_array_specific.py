#!/usr/bin/env python3
import sys
import os

# Agregar el directorio program al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'program'))

from antlr4 import InputStream, CommonTokenStream
from program.CompiscriptLexer import CompiscriptLexer
from program.CompiscriptParser import CompiscriptParser
from program.semantic.visitor import SemanticVisitor
from program.semantic.errors import SemanticError

def test_array_specific():
    print("=== Testing array specific ===")
    
    # Test case: Array with mixed types
    code = "let xs = [1, true];"
    print(f"Test: {code}")
    
    input_stream = InputStream(code)
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
    test_array_specific()
