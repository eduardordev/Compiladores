from .Driver import run
import sys

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Uso: python -m program <archivo.cps>')
        sys.exit(64)
    sys.exit(run(sys.argv[1]))
