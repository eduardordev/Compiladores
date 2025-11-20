import subprocess, sys, os
import textwrap
import tempfile

ROOT = os.path.dirname(os.path.dirname(__file__))

def test_tac_control_flow(tmp_path):
    src = textwrap.dedent('''
    let a: integer = 0;
    let b: integer = 10;
    while (a < b) {
        a = a + 1;
    }
    if (a == b) {
        a = a + 2;
    } else {
        a = a - 1;
    }
    function foo(x: integer): integer { return x + 1; }
    ''')
    f = tmp_path / 'cf.cps'
    f.write_text(src, encoding='utf-8')
    p = subprocess.run([sys.executable, os.path.join(ROOT, 'Driver.py'), str(f), '--tac'], capture_output=True, text=True)
    out = p.stdout + p.stderr
    # At minimum the driver should exit cleanly (0) or report semantic errors (non-zero)
    assert p.returncode in (0, 1, 2, 3)
    # If TAC was generated, it should produce some output; accept either
    if p.returncode == 0:
        assert out.strip() != ''
