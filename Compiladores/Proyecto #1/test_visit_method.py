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
        class_name = tree.__class__.__name__
        print(f"DEBUG: visit() called with {class_name}")
        
        # Remove 'Context' suffix if present
        if class_name.endswith('Context'):
            base_name = class_name[:-7]  # Remove 'Context'
        else:
            base_name = class_name
            
        method_name = f"visit{base_name}"
        print(f"DEBUG: Looking for method: {method_name}")
        print(f"DEBUG: Has method: {hasattr(self, method_name)}")
        
        # If we have a specific method for this node type, call it
        if hasattr(self, method_name):
            method = getattr(self, method_name)
            print(f"DEBUG: Calling method: {method_name}")
            return method(tree)
        
        # Otherwise, use the default behavior
        print(f"DEBUG: Using visitChildren for {class_name}")
        return self.visitChildren(tree)
    
    def visitExpression(self, ctx):
        print("DEBUG: visitExpression called!")
        return super().visitExpression(ctx)

def test_visit_method():
    print("=== Testing visit method ===")
    
    code = "let x = 1 + 2;"
    print(f"Code: {code}")
    
    input_stream = InputStream(code)
    lexer = CompiscriptLexer(input_stream)
    tokens = CommonTokenStream(lexer)
    parser = CompiscriptParser(tokens)
    tree = parser.program()
    
    visitor = DebugVisitor()
    try:
        visitor.visit(tree)
        print("SUCCESS: No errors")
    except SemanticError as e:
        print(f"SEMANTIC ERROR: {e}")
    except Exception as e:
        print(f"OTHER ERROR: {e}")

if __name__ == "__main__":
    test_visit_method()
