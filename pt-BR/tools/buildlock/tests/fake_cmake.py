"""CMake simulado para os testes do controlador de compilação. Nunca compila nada; registra o que foi solicitado e se comporta conforme configurado.

    python fake_cmake.py -S SRC -B TREE [configure args]      configuração: cria TREE/CMakeCache.txt (e build.ninja com -G Ninja)
    python fake_cmake.py --build TREE [--config C] [--target T ...] [-- -n]    compilação ou simulação com -- -n

Ambiente:
  FAKE_CMAKE_LOG     arquivo: uma linha JSON por chamada (argv, alguns valores do ambiente, existência de FAKE_LOCK_DIR naquele instante)
  FAKE_LOCK_DIR      pasta da trava de compilação, para comprovar que a trava está mantida durante esta execução
  FAKE_CONFIGURE_RC  código de saída da configuração (padrão 0)
  FAKE_BUILD_RC      código de saída de uma compilação real (padrão 0)
  FAKE_BUILD_SLEEP   duração em segundos de uma compilação real (padrão 0)
Uma simulação (-- -n) exibe "ninja: no work to do." quando TREE/uptodate existe.
"""
import json
import os
import sys
import time
from pathlib import Path

argv = sys.argv[1:]
log = os.environ.get("FAKE_CMAKE_LOG")
lock = os.environ.get("FAKE_LOCK_DIR")
if log:
    rec = {"argv": argv, "lock_exists": bool(lock and Path(lock).exists()),
           "env": {k: os.environ.get(k) for k in ("CMAKE_TOOLCHAIN_FILE", "FAKEVAR", "CMAKE_BUILD_PARALLEL_LEVEL", "CC")}}
    with open(log, "a", encoding="utf-8") as f:
        f.write(json.dumps(rec) + "\n")
if "-S" in argv:
    tree = Path(argv[argv.index("-B") + 1])
    rc = int(os.environ.get("FAKE_CONFIGURE_RC", "0"))
    if rc == 0:
        tree.mkdir(parents=True, exist_ok=True)
        (tree / "CMakeCache.txt").write_text("fake")
        if "-G" in argv and argv[argv.index("-G") + 1] == "Ninja":
            (tree / "build.ninja").write_text("fake")
    sys.exit(rc)
if "--build" in argv:
    tree = Path(argv[argv.index("--build") + 1])
    if argv[-2:] == ["--", "-n"]:
        print("ninja: no work to do." if (tree / "uptodate").exists() else "ninja: work to do")
        sys.exit(0)
    time.sleep(float(os.environ.get("FAKE_BUILD_SLEEP", "0")))
    sys.exit(int(os.environ.get("FAKE_BUILD_RC", "0")))
sys.exit(0)
