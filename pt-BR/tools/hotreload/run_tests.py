"""Compila a ferramenta de recarregamento com CMake, executa seus testes e verifica todas as variantes de mutação.

    python -I tools/hotreload/run_tests.py [--build-dir DIR] [--arch x64|Win32]

Etapas:
  1. Configura e compila com CMake (uma tarefa por vez, para poupar RAM): DLL do carregador, bibliotecas de recarregamento,
     seis núcleos de exemplo, host de teste (substituto do jogo) e testes unitários. Requer cmake e Visual Studio 2022 (Windows).
  2. Executa testes unitários (registro de estado, threads, drenagem, funções auxiliares JSON, canal de controle).
  3. Executa cenários de troca: cada um inicia o host de teste, executa hotreload.py contra ele e confere o resultado.
  4. Verifica todas as variantes de mutação: versões deliberadamente incorretas de uma regra de segurança. O cenário ou teste
     unitário correspondente precisa passar sem a falha (etapas 2 e 3) E falhar com ela (esta etapa).
Exibe ALL OK como última linha somente se tudo isso for atendido. Código de saída 0 em sucesso; 1 nos demais casos.
A pasta de compilação padrão fica sob a pasta temporária do sistema (substitua com --build-dir ou COOP_BUILD_DIR), portanto
nada é gravado no repositório. Hosts de teste são iniciados por este script e encerrados por pid. Nada mais é alterado,
e nenhum jogo é iniciado.
"""
import argparse
import hashlib
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

sys.dont_write_bytecode = True

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "tests"))
import scenarios  # noqa: E402

UNIT_EXE = "hotreload_unit_tests.exe"
HOST_EXE = "hotreload_test_host.exe"
# Variantes unitárias: número -> nome (o próprio programa de testes unitários encontra o teste que cobre cada uma).
UNIT_TWINS = [(14, "crc_unchecked"), (15, "forward_shutdown"), (16, "thread_not_joined"), (17, "drain_ip_only"),
              (18, "drain_timeout_ok"), (19, "preflight_ignored")]
MIN_UNIT_TESTS = 30


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


def scrub(text, limit):
    "Uma linha, sem caminhos absolutos (revelariam o nome de quem executa), limitada a `limit` caracteres."
    text = re.sub(r"[A-Za-z]:(?:\\\\|\\|/)[^'\"\s]*", "<path>", str(text).replace("\n", " "))
    return text[:limit]


def tail(p, n=25):
    return "\n".join(((p.stdout or "") + (p.stderr or "")).splitlines()[-n:])


def main():
    if os.name != "nt":
        fail("the hot reload tool swaps DLLs in a running Windows process; its tests run on Windows only")
    ap = argparse.ArgumentParser()
    ap.add_argument("--build-dir", default=os.environ.get("COOP_BUILD_DIR"))
    ap.add_argument("--arch", default="", help="x64 ou Win32 (padrão: o padrão do gerador)")
    args = ap.parse_args()
    cmake = shutil.which("cmake")
    if not cmake:
        fail("cmake not found on PATH")
    if args.build_dir:
        build = Path(args.build_dir).resolve()
    else:
        build = Path(tempfile.gettempdir()) / ("coop-hotreload-build-" + hashlib.sha1(str(HERE).encode()).hexdigest()[:10])

    # ---- 1. compilação ----
    cfg_cmd = [cmake, "-S", str(HERE), "-B", str(build), "-DHOTRELOAD_MUTATION_TWINS=ON"]
    if args.arch:
        cfg_cmd += ["-A", args.arch]
    cfg = run(cfg_cmd)
    if cfg.returncode != 0:
        fail("cmake could not configure (is Visual Studio 2022 installed?)\n" + tail(cfg))
    b = run([cmake, "--build", str(build), "--config", "Release", "--parallel", "1"])
    if b.returncode != 0:
        fail("build failed\n" + tail(b))
    bin_dir = build / "bin"
    for need in (UNIT_EXE, HOST_EXE, "hotreload_loader.dll", "core_v1.dll", "core_v2.dll", "core_v3_nomigrate.dll",
                 "core_unregistered.dll", "core_failsave.dll", "core_badinit.dll"):
        if not (bin_dir / need).is_file():
            fail(f"{need} was not built (looked in {bin_dir})")

    # ---- 2. testes unitários ----
    r = run([str(bin_dir / UNIT_EXE)])
    out = r.stdout or ""
    results = re.findall(r"^\[(PASS|FAIL)\] (\S+) \((\d+) checks\)", out, re.M)
    failed = [n for s, n, _ in results if s == "FAIL"]
    m = re.search(r"^== (\d+) tests, (\d+) passed, (\d+) failed, (\d+) checks ==", out, re.M)
    if r.returncode != 0 or failed or not m or int(m.group(3)) != 0:
        print(out[-4000:])
        fail("unit tests failed: " + (", ".join(failed) or "see output above"))
    unit_total = int(m.group(1))
    if unit_total < MIN_UNIT_TESTS or unit_total != len(results):
        fail("unexpected unit test count %d (parsed %d, want at least %d)" % (unit_total, len(results), MIN_UNIT_TESTS))
    print("unit tests: %d passed, 0 failed, %s checks" % (unit_total, m.group(4)), flush=True)

    # ---- 3. cenários de troca (com host de teste) ----
    work = build / "work"
    shutil.rmtree(work, ignore_errors=True)
    work.mkdir(parents=True)
    passed = 0
    for name, fn in scenarios.SCENARIOS:
        t = time.time()
        try:
            fn(scenarios.Ctx(bin_dir, work))
        except Exception as e:
            print("[FAIL] %s: %s: %s" % (name, type(e).__name__, scrub(e, 1500)))
            fail("scenario %s failed" % name)
        passed += 1
        print("[PASS] %s (%.1f s)" % (name, time.time() - t), flush=True)
    print("swap scenarios: %d passed, 0 failed" % passed, flush=True)

    # ---- 4. variantes de mutação ----
    caught = 0
    total = len(UNIT_TWINS) + len(scenarios.TWINS)
    for num, name in UNIT_TWINS:
        p = run([str(bin_dir / UNIT_EXE), "--twin", str(num)])
        line = ((p.stdout or "").strip().splitlines() or [""])[-1]
        if p.returncode != 0:
            fail("mutation twin %s (%d) was not caught by the unit tests: %s" % (name, num, line))
        caught += 1
        print("[CAUGHT] %s: %s" % (name, line.replace("[CAUGHT] ", "")), flush=True)
    for name, mut, fault, scenario in scenarios.TWINS:
        fn = dict(scenarios.SCENARIOS)[scenario]
        env = {"HOTRELOAD_MUT": mut} if mut else {}
        t = time.time()
        try:
            fn(scenarios.Ctx(bin_dir, work, env=env, faults=(fault,) if fault else ()))
        except scenarios.SetupError as e:
            fail("twin %s: the test rig broke, so nothing was proven: %s" % (name, scrub(e, 500)))
        except Exception as e:
            caught += 1
            why = scrub(e, 400).split(": {")[0][:100]   # a frase anterior a um relatório extraído
            print("[CAUGHT] %s by %s (%.1f s): %s" % (name, scenario, time.time() - t, why), flush=True)
        else:
            fail("mutation twin %s was NOT caught: scenario %s still passes with it switched on" % (name, scenario))
    if caught != total:
        fail("only %d of %d twins caught" % (caught, total))

    print("mutation twins caught: %d of %d" % (caught, total))
    print("ALL OK")


if __name__ == "__main__":
    main()
