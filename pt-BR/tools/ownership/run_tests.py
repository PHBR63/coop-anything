"""Compila a biblioteca de responsabilidade e seus testes com CMake, executa-os e verifica todas as variantes de mutação.

    python -I tools/ownership/run_tests.py [--build-dir DIR]

Etapas:
  1. Configura e compila com CMake (uma tarefa por vez, para poupar RAM). Requer cmake e um compilador C++17
     (Visual Studio 2022 no Windows, gcc ou clang nos demais sistemas).
  2. Executa o programa de teste. Todos os testes precisam passar.
  3. Confere se todas as variantes de mutação em TWINS foram executadas e passaram. Uma variante só passa quando
     seu cenário passa sem a falha E relata uma violação com a falha ativada.
Exibe ALL OK como última linha somente se tudo isso for atendido. Código de saída 0 em caso de sucesso; 1 nos demais casos.
A pasta de compilação padrão fica sob a pasta temporária do sistema (substitua com --build-dir ou a variável de ambiente
COOP_BUILD_DIR), portanto nada é gravado no repositório.
"""
import argparse
import hashlib
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
EXE = "coop_ownership_tests"
TWINS = [
    "own_no_epoch", "own_stale_epoch", "own_adopt_echo", "own_transfer_no_ack",
    "own_no_hysteresis", "own_follower_ignored", "own_accept_non_owner",
]
MIN_TESTS = 20   # protege contra uma compilação que silenciosamente registra quase nada


def fail(msg):
    print("FAIL: " + msg)
    sys.exit(1)


def clean_env():
    "Um arquivo de cadeia de ferramentas deixado no ambiente (por exemplo, de Android) causaria compilação cruzada dos testes."
    env = dict(os.environ)
    env.pop("CMAKE_TOOLCHAIN_FILE", None)
    return env


def run(cmd, **kw):
    return subprocess.run(cmd, capture_output=True, text=True, errors="replace", env=clean_env(), **kw)


def tail(p, n=25):
    return "\n".join(((p.stdout or "") + (p.stderr or "")).splitlines()[-n:])


def find_exe(build):
    for name in (EXE + ".exe", EXE):
        p = build / "bin" / name
        if p.is_file():
            return p
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--build-dir", default=os.environ.get("COOP_BUILD_DIR"))
    args = ap.parse_args()
    cmake = shutil.which("cmake")
    if not cmake:
        fail("cmake not found on PATH")
    if args.build_dir:
        build = Path(args.build_dir).resolve()
    else:
        build = Path(tempfile.gettempdir()) / ("coop-ownership-build-" + hashlib.sha1(str(HERE).encode()).hexdigest()[:10])
    cfg = run([cmake, "-S", str(HERE), "-B", str(build), "-DCMAKE_BUILD_TYPE=Release"])
    if cfg.returncode != 0:
        fail("cmake could not configure (is a C++17 compiler installed?)\n" + tail(cfg))
    b = run([cmake, "--build", str(build), "--config", "Release", "--parallel", "1"])
    if b.returncode != 0:
        fail("build failed\n" + tail(b))
    exe = find_exe(build)
    if not exe:
        fail("test program not found under " + str(build / "bin"))
    r = run([str(exe)])
    out = r.stdout or ""
    results = re.findall(r"^\[(PASS|FAIL)\] (\S+) \((\d+) checks\)", out, re.M)
    passed = [n for s, n, _ in results if s == "PASS"]
    failed = [n for s, n, _ in results if s == "FAIL"]
    m = re.search(r"^== (\d+) tests, (\d+) passed, (\d+) failed, (\d+) checks ==", out, re.M)
    if r.returncode != 0 or failed or not m or int(m.group(3)) != 0:
        print(out[-4000:])
        fail("tests failed: " + (", ".join(failed) or "see output above"))
    total = int(m.group(1))
    if total < MIN_TESTS or total != len(results):
        fail("unexpected test count %d (parsed %d, want at least %d)" % (total, len(results), MIN_TESTS))
    missing = [t for t in TWINS if "twin." + t not in passed]
    if missing:
        fail("mutation twins not caught or not run: " + ", ".join(missing))
    extra = [n for n in passed if n.startswith("twin.") and n[5:] not in TWINS]
    if extra:
        fail("twins missing from TWINS in run_tests.py: " + ", ".join(extra))
    print("tests: %d passed, 0 failed, %s checks" % (total, m.group(4)))
    print("mutation twins caught: %d of %d" % (len(TWINS), len(TWINS)))
    print("ALL OK")


if __name__ == "__main__":
    main()
