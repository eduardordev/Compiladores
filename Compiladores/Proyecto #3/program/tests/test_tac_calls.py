import subprocess, sys, os, textwrap

ROOT = os.path.dirname(os.path.dirname(__file__))

CODE = textwrap.dedent('''
function inc(x: integer): integer { return x + 1; }
let a = 10;
let b = inc(a);
''')

def test_tac_call_emission(tmp_path):
    f = tmp_path / 'call.cps'
    f.write_text(CODE, encoding='utf-8')
    p = subprocess.run([sys.executable, os.path.join(ROOT, 'Driver.py'), str(f), '--tac'], capture_output=True, text=True)
    out = p.stdout + p.stderr
    assert p.returncode == 0
    # Check that ARG and CALL are present in TAC output
    assert 'ARG' in out and 'CALL' in out
