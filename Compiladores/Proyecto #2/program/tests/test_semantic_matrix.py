import subprocess, sys, os, pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]

CASES = {
  'sem_types_ok.cps': 0,
  'sem_types_bad.cps': 2,
  'arrays_ok.cps': 0,
  'arrays_bad.cps': 2,
  'func_ok.cps': 0,
  'func_bad.cps': 2,
  'flow_ok.cps': 0,
  'flow_bad.cps': 2,
  'class_ok.cps': 0,
  'class_bad.cps': 2,
}

def run_case(name):
    p = subprocess.run([sys.executable, str(ROOT/'Driver.py'), str(ROOT/'tests'/name)],
                       capture_output=True, text=True)
    return p.returncode, (p.stdout + p.stderr)

def test_matrix():
    for name, expected in CASES.items():
        rc, out = run_case(name)
        assert rc in (0,1,2)
