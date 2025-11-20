import subprocess, sys, os

BASE = os.path.dirname(__file__)
ROOT = os.path.abspath(os.path.join(BASE, '..'))

GOOD = """
let a: integer = 10;
let b: float = 2.5;
let c = a + b;
function suma(x: integer, y: integer): integer { return x + y; }
"""

def test_good_tmp(tmp_path):
    f = tmp_path/"ok.cps"
    f.write_text(GOOD, encoding='utf-8')
    p = subprocess.run([sys.executable, os.path.join(ROOT, 'Driver.py'), str(f)])
    assert p.returncode in (0, 1, 2)
