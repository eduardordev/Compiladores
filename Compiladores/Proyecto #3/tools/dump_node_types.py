import sys
import os
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from program.Driver import parse_and_semantic
from CompiscriptParser import CompiscriptParser

path = sys.argv[1]
parser, tree, syn, sem = parse_and_semantic(path)

# iterate top-level statements and print their class names and text
for idx, st in enumerate(tree.statement()):
    print(f"Statement {idx}: type={type(st).__name__}, text={st.getText()}")
    # print children types
    for i in range(st.getChildCount()):
        ch = st.getChild(i)
        print(f"  child[{i}] type={type(ch).__name__}, text={ch.getText()}")
    print()
