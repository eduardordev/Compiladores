#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'program'))

from antlr4 import InputStream, CommonTokenStream
from program.CompiscriptLexer import CompiscriptLexer
from program.CompiscriptParser import CompiscriptParser
from program.semantic.visitor import SemanticVisitor

def test_expression_debug():
    print("=== Testing expression debug ===")
    
    # Test case: Simple arithmetic expression
    code = "let x = 1 + 2;"
    print(f"Code: {code}")
    
    input_stream = InputStream(code)
    lexer = CompiscriptLexer(input_stream)
    tokens = CommonTokenStream(lexer)
    parser = CompiscriptParser(tokens)
    tree = parser.program()
    
    visitor = SemanticVisitor()
    try:
        result = visitor.visit(tree)
        print(f"SUCCESS: Result = {result}")
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_expression_debug()