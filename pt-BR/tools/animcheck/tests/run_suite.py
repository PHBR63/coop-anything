"Executa todos os módulos de teste do animcheck em um processo unittest (usado por run_tests.py e por cada variante de mutação)."
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent.parent))

if __name__ == "__main__":
    suite = unittest.defaultTestLoader.discover(str(HERE), pattern="test_*.py")
    res = unittest.TextTestRunner(verbosity=1).run(suite)
    raise SystemExit(0 if res.wasSuccessful() else 1)
