#!/usr/bin/env python3
"""Um comando para a ferramenta de bots:   python -I tools/bots/run_tests.py     (exibe ALL OK somente se tudo passar)

Parte 1: testes unitários (tests/), incluindo cada variante de roteiro: um roteiro combinado com comportamento simulado
         deliberadamente incorreto precisa FALHAR. Somente simulações; nenhum jogo é iniciado.
Parte 2: variantes do mecanismo. Os mesmos testes rodam novamente com cada valor de COOPBOTS_MUTANT; cada um quebra uma
         verificação do próprio executor (estabilização, comparação de capturas de estado, contadores, tratamento de etapas ignoradas,
         modelo de resultado de ação, etapas retomáveis, estabilização com falha imediata, escala de tempo e executor paralelo) e precisa
         provocar a falha de pelo menos um teste. As variantes de recursos mais novos executam somente os arquivos de teste que os cobrem.
"""
import os
import subprocess
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
TESTS = HERE / "tests"
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(TESTS))

# nome da variante -> (o que é quebrado, arquivos de teste que precisam detectar; None = suíte inteira)
ENGINE_MUTANTS = {
    "nosettle": ("the runner stops waiting for machines to converge", None),
    "nosnapshot": ("the runner stops comparing snapshots", None),
    "nocounters": ("the runner stops checking the desync counters", None),
    "skipispass": ("a skipped playbook is reported as a pass", None),
    "nowhy": ("failed actions stop saying why (no blockers in the reason)", ["test_actions"]),
    "nopost": ("postconditions of actions are not checked", ["test_actions"]),
    "allsteps": ("--from-step and --only-step run every step", ["test_resume"]),
    "noarrange": ("a resumed run does not arrange the world", ["test_resume"]),
    "nostall": ("settle never stops early when sync makes no progress", ["test_resume"]),
    "notimescale": ("--timescale never reaches the game", ["test_resume"]),
    "noprefix": ("the parallel runner stops prefixing the logs of the pairs", ["test_parallel"]),
    "passall": ("the parallel runner exits 0 whatever the pairs did", ["test_parallel"]),
    "sameids": ("every pair gets the same instances", ["test_parallel"]),
    "nokill": ("a hung runner is never stopped", ["test_parallel"]),
    "noforbid": ("options that belong to the parallel runner are allowed after --", ["test_parallel"]),
}


def run_suite(quiet, modules=None):
    loader = unittest.defaultTestLoader
    if modules:
        suite = loader.loadTestsFromNames(modules)
    else:
        suite = loader.discover(str(TESTS), top_level_dir=str(TESTS))
    stream = open(os.devnull, "w") if quiet else sys.stderr
    return unittest.TextTestRunner(stream=stream, verbosity=0 if quiet else 1, failfast=quiet).run(suite)


def main():
    if os.environ.get("COOPBOTS_MUTANT"):
        mods = [m for m in os.environ.get("COOPBOTS_TEST_MODULES", "").split(",") if m]
        return 0 if run_suite(True, mods).wasSuccessful() else 1
    res = run_suite(False)
    print("tests run: %d" % res.testsRun)
    if not res.wasSuccessful():
        print("FAILED")
        return 1
    from coopbots import registry, fakecoop
    print("playbooks: %d (%d resumable), playbook twins caught: %d, other fake bugs caught: %d (every one of the %d fake bugs has a twin)"
          % (len(registry.REGISTRY), len(registry.RESUMABLE), len(registry.TWINS), len(registry.UNIVERSAL), len(fakecoop.BUGS)))
    bad = []
    for m, (what, modules) in ENGINE_MUTANTS.items():
        env = dict(os.environ, COOPBOTS_MUTANT=m, COOPBOTS_TEST_MODULES=",".join(modules or []))
        p = subprocess.run([sys.executable, "-I", str(Path(__file__).resolve())], env=env, capture_output=True, text=True)
        caught = p.returncode != 0
        print("engine twin %-11s %-60s %s" % (m, what, "caught" if caught else "NOT CAUGHT"))
        if not caught:
            bad.append(m)
    if bad:
        print("FAILED: engine twins not caught: %s" % bad)
        return 1
    print("engine twins caught: %d of %d" % (len(ENGINE_MUTANTS), len(ENGINE_MUTANTS)))
    print("ALL OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
