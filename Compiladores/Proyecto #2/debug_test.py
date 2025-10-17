#!/usr/bin/env python3
import sys
import os

# Agregar el directorio program al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'program'))

from program.Driver import run
from program.semantic.visitor import SemanticVisitor
from program.semantic.errors import SemanticError
from antlr4 import FileStream, CommonTokenStream
from program.CompiscriptLexer import CompiscriptLexer
from program.CompiscriptParser import CompiscriptParser

def test_file(filepath):
    print(f"\n=== Testing {filepath} ===")
    
    # Test with Driver
    print("Testing with Driver:")
    result = run(filepath)
    print(f"Driver return code: {result}")
    
    # Test manually
    print("\nTesting manually:")
    try:
        input_stream = FileStream(filepath, encoding='utf-8')
        lexer = CompiscriptLexer(input_stream)
        tokens = CommonTokenStream(lexer)
        parser = CompiscriptParser(tokens)
        tree = parser.program()
        
        visitor = SemanticVisitor()
        visitor.visit(tree)
        print("Manual test: SUCCESS (no errors)")
        
    except SemanticError as e:
        print(f"Manual test: SEMANTIC ERROR - {e}")
    except Exception as e:
        print(f"Manual test: OTHER ERROR - {e}")

if __name__ == "__main__":
    test_files = [
        "program/tests/func_bad.cps",
        "program/tests/arrays_bad.cps", 
        "program/tests/class_bad.cps"
    ]
    
    for file in test_files:
        if os.path.exists(file):
            test_file(file)
        else:
            print(f"File not found: {file}")
