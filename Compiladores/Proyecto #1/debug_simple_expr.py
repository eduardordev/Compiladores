#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'program'))

from antlr4 import InputStream, CommonTokenStream
from program.CompiscriptLexer import CompiscriptLexer
from program.CompiscriptParser import CompiscriptParser

def debug_simple_expr():
    code = "let x = 1 + 2;"
    input_stream = InputStream(code)
    lexer = CompiscriptLexer(input_stream)
    tokens = CommonTokenStream(lexer)
    parser = CompiscriptParser(tokens)
    tree = parser.program()
    
    stmt = tree.statement(0)
    var_decl = stmt.variableDeclaration()
    initializer = var_decl.initializer()
    expression = initializer.expression()
    
    print(f"Expression: {expression.getText()}")
    print(f"Has assignmentExpr: {hasattr(expression, 'assignmentExpr')}")
    
    if hasattr(expression, 'assignmentExpr'):
        ae_list = expression.assignmentExpr()
        print(f"assignmentExpr count: {len(ae_list)}")
        if len(ae_list) > 0:
            ae = ae_list[0]
            print(f"First assignmentExpr: {ae.getText()}")
            print(f"Has conditionalExpr: {hasattr(ae, 'conditionalExpr')}")
            if hasattr(ae, 'conditionalExpr'):
                ce_list = ae.conditionalExpr()
                print(f"conditionalExpr count: {len(ce_list)}")
                if len(ce_list) > 0:
                    ce = ce_list[0]
                    print(f"First conditionalExpr: {ce.getText()}")
                    print(f"Has logicalOrExpr: {hasattr(ce, 'logicalOrExpr')}")

if __name__ == "__main__":
    debug_simple_expr()
