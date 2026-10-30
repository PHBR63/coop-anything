"""Executa a suíte de cada ferramenta de teste de sincronização (testes e variantes de mutação) e exibe ALL OK se todas passarem.

    python -I tools/test_all.py            executa todas as suítes
    python -I tools/test_all.py chaos bots executa somente estas

Uma suíte só conta como aprovada se sair com código 0 E sua última linha for ALL OK, podendo acrescentar uma nota
entre parênteses se tiver ignorado uma etapa, por exemplo:
"ALL OK (C++ cross-check skipped: cmake not found on PATH)".
As suítes C++ compilam com CMake e precisam de compilador C++17 (Visual Studio 2022 no Windows).
"""
import re
import subprocess
import sys
import time
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
SUITES = ["chaos", "flight", "ownership", "fakeworld", "fuzz",
          "gameslot", "gamepool", "scenarios", "bots", "animcheck",
          "bridge", "inspect", "hotreload", "mutants", "buildlock"]

# Última linha de uma suíte aprovada: ALL OK, ou ALL OK seguido de nota entre colchetes
# informando a etapa que precisou ignorar. Uma suíte reprovada exibe outra coisa e sai
# com valor diferente de zero, e o código de saída também é verificado.
PASS_LINE = re.compile(r"ALL OK(?: \(.*\))?")


def run(name):
    script = TOOLS / name / "run_tests.py"
    if not script.exists():
        return False, "missing run_tests.py"
    t = time.time()
    # -X utf8=1, não PYTHONIOENCODING: -I ignora o ambiente, então a variável que isto
    # definia nunca chegou à suíte, e a saída dela retornou na página
    # de códigos do console (no Windows, uma mensagem de erro do sistema não será decodificada como UTF-8).
    p = subprocess.run([sys.executable, "-I", "-X", "utf8=1", str(script)], cwd=TOOLS.parent,
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    lines = [l.strip() for l in (p.stdout or "").splitlines() if l.strip()]
    ok = p.returncode == 0 and bool(lines) and PASS_LINE.fullmatch(lines[-1]) is not None
    note = f"{time.time() - t:.0f}s"
    if not ok:
        tail = "\n".join(((p.stdout or "") + (p.stderr or "")).splitlines()[-15:])
        note += f", exit {p.returncode}\n{tail}"
    return ok, note


def main():
    # Uma suíte ainda pode fornecer um caractere não codificável neste console: errors="replace"
    # acima converte bytes não decodificáveis de uma ferramenta executada pela própria suíte (cmake, compilador)
    # em U+FFFD. Exiba o caractere substituído em vez de encerrar no meio da execução.
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, OSError, ValueError):
            pass
    names = sys.argv[1:] or SUITES
    failed = []
    for name in names:
        ok, note = run(name)
        print(f"{'PASS' if ok else 'FAIL'}  {name}  ({note})", flush=True)
        if not ok:
            failed.append(name)
    if failed:
        print("FAILED: " + ", ".join(failed))
        sys.exit(1)
    print("ALL OK")


if __name__ == "__main__":
    main()
