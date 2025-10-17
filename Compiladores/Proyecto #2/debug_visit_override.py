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

class DebugVisitor(SemanticVisitor):
    def visit(self, tree):
        print(f"DEBUG: visit() called with {tree.__class__.__name__}")
        method_name = f"visit{tree.__class__.__name__}"
        print(f"DEBUG: Looking for method: {method_name}")
        print(f"DEBUG: Has method: {hasattr(self, method_name)}")
        
        if hasattr(self, method_name):
            method = getattr(self, method_name)
            print(f"DEBUG: Calling method: {method_name}")
            return method(tree)
        else:
            print(f"DEBUG: Using visitChildren for {tree.__class__.__name__}")
            return self.visitChildren(tree)

def test_debug():
    print("=== Debug visit override test ===")
    
    code = "function f(a: integer): integer { return; }"
    print(f"Code: {code}")
    
    input_stream = InputStream(code)
    lexer = CompiscriptLexer(input_stream)
    tokens = CommonTokenStream(lexer)
    parser = CompiscriptParser(tokens)
    tree = parser.program()
    
    print("AST generated")
    
    visitor = DebugVisitor()
    try:
        visitor.visit(tree)
        print("SUCCESS: No errors")
    except SemanticError as e:
        print(f"SEMANTIC ERROR: {e}")
    except Exception as e:
        print(f"OTHER ERROR: {e}")

if __name__ == "__main__":
    test_debug()
