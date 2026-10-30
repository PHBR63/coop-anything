"""Executa todos os testes do chaos e depois todas as variantes de mutação (cada comportamento quebrado precisa provocar falha em um teste).

    python -I tools/chaos/run_tests.py [--no-twins] [--no-cpp]

Etapas:
  1. Testes Python (test_chaos.py): estatísticas do modelo em tempo virtual, viagens UDP reais de ida e volta em loopback,
     cliente RPC e linha de comando.
  2. Variantes de mutação Python: COOPCHAOS_MUTANT quebra um comportamento em impair.py ou client.py; o teste nomeado precisa falhar.
  3. Implementação C++ equivalente: compila cpp/ com cmake (uma tarefa por vez, para poupar RAM), executa a verificação cruzada
     com o modelo Python (precisam ser idênticos), verifica se o cabeçalho gerado está atualizado e executa 4 compilações
     mutantes e uma variante de cabeçalho desatualizado (todas precisam ser detectadas).
Exibe ALL OK se tudo passar e todos os mutantes forem detectados. Se cmake ou um compilador C++ estiver ausente, a etapa 3
exibe uma linha SKIP e a última linha informa isso.
"""
import hashlib
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
CPP = HERE / "cpp"

# nome da variante -> teste que ela precisa quebrar (nomeado para manter curtas as execuções de variantes)
MUTANTS = {
    "no_loss": "ModelTests.test_loss_matches_expected_per_profile",
    "no_burst": "ModelTests.test_burst_loss_is_clustered",
    "half_latency": "ModelTests.test_latency_matches_per_profile",
    "no_reorder": "ModelTests.test_reorder_and_duplicate",
    "no_duplicate": "ModelTests.test_reorder_and_duplicate",
    "no_bandwidth": "ModelTests.test_bandwidth_cap",
    "no_partition": "ModelTests.test_partition_is_one_way_and_reversible",
}
UDP_MUTANTS = {
    "client_partition_both": "ClientModuleTests.test_partition_direction_and_self_heal",
    "no_loss": "UdpTests.test_profiles_over_real_udp",
    "half_latency": "UdpTests.test_profiles_over_real_udp",
    "no_partition": "UdpTests.test_midrun_changes_one_way_partition_and_disconnect",
}
CPP_MUTANTS = {
    "chaos_xcheck_m1": "bandwidth serialization time 10 percent short",
    "chaos_xcheck_m2": "jitter only adds, never subtracts",
    "chaos_xcheck_m3": "bandwidth queue delay not added",
    "chaos_xcheck_m4": "partition ignored",
}


def run(args, mutant=""):
    env = dict(os.environ, COOPCHAOS_MUTANT=mutant)
    return subprocess.run([sys.executable, "-I", str(HERE / "test_chaos.py"), *args], cwd=HERE, env=env,
                          capture_output=True, text=True, errors="replace")


def py(script, *args):
    return subprocess.run([sys.executable, "-I", str(HERE / script), *args], cwd=HERE,
                          capture_output=True, text=True, errors="replace")


def find_exe(build, name):
    for pat in (name + ".exe", name):
        for p in build.rglob(pat):
            if p.is_file():
                return p
    return None


def host_env():
    """Cópia do ambiente para uma compilação neste PC. Um CMAKE_TOOLCHAIN_FILE deixado no ambiente para outro alvo
    (como um NDK Android) direcionaria a compilação ao compilador errado; por isso é removido."""
    env = dict(os.environ)
    for k in ("CMAKE_TOOLCHAIN_FILE", "CMAKE_GENERATOR", "CMAKE_GENERATOR_PLATFORM", "CMAKE_GENERATOR_TOOLSET"):
        env.pop(k, None)
    return env


def build_cpp():
    "Retorna (pasta de compilação, None) ou (None, motivo para ignorar)."
    cmake = shutil.which("cmake")
    if not cmake:
        return None, "cmake not found on PATH"
    build = Path(tempfile.gettempdir()) / ("coopchaos-build-" + hashlib.sha1(str(HERE).encode()).hexdigest()[:10])
    cfg = subprocess.run([cmake, "-S", str(CPP), "-B", str(build), "-DCMAKE_BUILD_TYPE=Release"],
                         env=host_env(), capture_output=True, text=True, errors="replace")
    if cfg.returncode != 0:
        return None, "cmake could not configure (no C++ compiler?): " + " ".join((cfg.stdout + cfg.stderr).split())[-200:]
    b = subprocess.run([cmake, "--build", str(build), "--config", "Release", "--parallel", "1"],
                       env=host_env(), capture_output=True, text=True, errors="replace")
    if b.returncode != 0:
        print((b.stdout + b.stderr)[-3000:])
        return None, "C++ build FAILED"
    return build, None


def cpp_stage():
    "Retorna (lista de falhas, motivo para ignorar ou None, quantidade de variantes C++ detectadas)."
    bad = []
    caught_n = 0
    r = py("gen_header.py", "--check")
    print("header fresh:", (r.stdout + r.stderr).strip())
    if r.returncode != 0:
        bad.append("header_stale")
    r = py("gen_header.py", "--check", "--mutate")
    caught = r.returncode == 1
    print(f"twin stale_header: {'caught' if caught else 'NOT CAUGHT'}")
    if caught:
        caught_n += 1
    else:
        bad.append("stale_header")
    build, why = build_cpp()
    if why:
        if why == "C++ build FAILED":
            return bad + ["cpp_build"], None, caught_n
        print("SKIP: C++ cross-check not run:", why)
        return bad, why, caught_n
    exe = find_exe(build, "chaos_xcheck")
    if not exe:
        return bad + ["cpp_exe_missing"], None, caught_n
    r = py("xcheck.py", str(exe))
    print("xcheck:", (r.stdout + r.stderr).strip())
    if r.returncode != 0 or not r.stdout.startswith("OK"):
        bad.append("xcheck")
    for name, what in CPP_MUTANTS.items():
        m = find_exe(build, name)
        if not m:
            bad.append(name)
            print(f"twin {name}: executable missing")
            continue
        r = py("xcheck.py", str(m))
        caught = r.returncode == 1 and r.stdout.startswith("FAIL")
        print(f"twin {name:16s} ({what}): {'caught' if caught else 'NOT CAUGHT'}")
        if caught:
            caught_n += 1
        else:
            bad.append(name)
    return bad, None, caught_n


def main():
    p = run([])
    out = (p.stdout + p.stderr).strip()
    print("\n".join(out.splitlines()[-4:]) if out else "no output")
    if p.returncode != 0:
        print(out)
        print("RESULT: FAIL (real tests)")
        return 1
    if "--no-twins" in sys.argv:
        print("ALL OK (twins skipped)")
        return 0
    bad = []
    caught_n = 0
    for table in (MUTANTS, UDP_MUTANTS):
        for m, test in table.items():
            q = run([test], m)
            caught = q.returncode != 0
            print(f"twin {m:13s} via {test.split('.')[-1]}: {'caught' if caught else 'NOT CAUGHT'}")
            if caught:
                caught_n += 1
            else:
                bad.append(m)
    skipped = None
    if "--no-cpp" in sys.argv:
        skipped = "--no-cpp given"
        print("SKIP: C++ cross-check not run: --no-cpp given")
    else:
        cpp_bad, skipped, cpp_caught = cpp_stage()
        bad += cpp_bad
        caught_n += cpp_caught
    if bad:
        print("RESULT: FAIL, problems:", bad)
        return 1
    print(f"mutants caught: {caught_n}")
    print("ALL OK" + (f" (C++ cross-check skipped: {skipped})" if skipped else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
