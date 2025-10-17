import sys
from antlr4 import FileStream, CommonTokenStream
from antlr4.error.ErrorListener import ErrorListener

from CompiscriptLexer import CompiscriptLexer
from CompiscriptParser import CompiscriptParser

from semantic.visitor import SemanticVisitor
from semantic.errors import SemanticError
from tac.generator import TACGenerator

class ThrowingSyntaxErrorListener(ErrorListener):
    def __init__(self):
        super().__init__()
        self.errors = []
    def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
        self.errors.append(f"[Syntax] line {line}:{column} {msg}")

def run(filepath: str, generate_tac: bool = False) -> int:
    input_stream = FileStream(filepath, encoding='utf-8')
    lexer = CompiscriptLexer(input_stream)
    tokens = CommonTokenStream(lexer)
    parser = CompiscriptParser(tokens)

    syn = ThrowingSyntaxErrorListener()
    parser.removeErrorListeners()
    parser.addErrorListener(syn)

    tree = parser.program()

    if syn.errors:
        for e in syn.errors:
            print(e)
        return 1

    if generate_tac:
        # Generate TAC
        generator = TACGenerator()
        try:
            tac_program = generator.generate_tac(tree)
            print("TAC Generated Successfully!")
            print("=" * 50)
            print(tac_program)
            print("=" * 50)
            
            # Print statistics
            stats = generator.temp_manager.get_stats()
            print(f"Temporary Variables: {stats['total_temps']}")
            print(f"Active Temporaries: {stats['active_temps']}")
            print(f"Reused Temporaries: {stats['reused_temps']}")
            
            mem_stats = generator.symtab.get_memory_stats()
            print(f"Global Memory: {mem_stats['global_size']} bytes")
            print(f"Local Memory: {mem_stats['local_size']} bytes")
            print(f"String Literals: {mem_stats['string_literals']}")
            
        except SemanticError as se:
            print(se)
            return 2
    else:
        # Semantic analysis only
        visitor = SemanticVisitor()
        try:
            visitor.visit(tree)
        except SemanticError as se:
            print(se)
            return 2

        for w in visitor.warnings:
            print(f"[Warn] {w}")
    
    return 0

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python3 Driver.py <archivo.cps> [--tac]")
        print("  --tac: Generate TAC intermediate code")
        sys.exit(64)
    
    generate_tac = "--tac" in sys.argv
    filepath = sys.argv[1]
    
    sys.exit(run(filepath, generate_tac))
