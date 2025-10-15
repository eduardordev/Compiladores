# tests/test_tac_simple.py
import subprocess, sys, os

CODE = """
let a = 1;
let b = 2;
let c = a + b;
"""

def test_tac_simple(tmp_path):
    f = tmp_path/'tac_simple.cps'
    f.write_text(CODE, encoding='utf-8')
    script = os.path.join(os.path.dirname(__file__), '..', 'codegen', 'generate_tac.py')
    p = subprocess.run([sys.executable, script, str(f)], capture_output=True, text=True)
    out = p.stdout
    assert 'STORE' in out or 'ADD' in out
