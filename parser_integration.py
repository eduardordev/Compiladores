from YaparParser import YaparParser
from SLRBuilder import SLRBuilder
from SLRParser import SLRParser

def parse_from_tokens(tokens, yapar_path, finales=None, archivo=None, reservadas=None, operadores_reservados=None, tokens_list=None, tabla=None, parser=None):
    print("\n--- INICIANDO ANÁLISIS SINTÁCTICO ---")
    
    try:
        # Si se pasa un parser externo, úsalo, si no, créalo
        if parser is None:
            parser = YaparParser(yapar_path)
        slr = SLRBuilder(parser)
        slr.print_states()          # Opcional: imprime autómata
        slr.print_transitions()     # Opcional: imprime transiciones
        slr.print_tables()          # Opcional: imprime tablas FIRST/FOLLOW

        syntactic_parser = SLRParser(slr)

        # Mostrar tokens que se usarán
        print("\nTokens para análisis sintáctico:")
        for token in tokens:
            print(token)

        # Ejecutar análisis sintáctico
        result = syntactic_parser.parse(tokens)

        print("\n✅ Análisis sintáctico finalizado correctamente.")
        return result

    except Exception as e:
        print("❌ Error en análisis sintáctico:", e)
        raise
