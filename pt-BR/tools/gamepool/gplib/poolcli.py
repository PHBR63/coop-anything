"""Linha de comando do conjunto de instâncias de jogo já inicializadas.

    gamepool.py --config game.json pool up [--size 1] [--fake] [daemon options...]   inicia o serviço em segundo plano e aguarda prontidão
    gamepool.py pool status                                                          instâncias, reservas e contadores (JSON)
    gamepool.py pool lease --owner NAME [--n 1] [--ttl 900] [--timeout 600]          exibe o JSON da reserva; dura até ser liberada ou até o ttl
    gamepool.py pool release --id L3 [--dirty]
    gamepool.py pool down                                                            encerra o serviço e somente os jogos que ele iniciou, liberando as vagas

As opções após `up` são encaminhadas ao serviço (consulte `pool up --help`). Só `up` precisa de --config; os outros comandos
se comunicam com o serviço em execução. Códigos de saída: 0 sucesso, 2 serviço inativo ou uso incorreto, 3 ocupado ou falha.
"""
from __future__ import annotations

import json
import subprocess
import sys
import time
from pathlib import Path
from typing import List

from . import client
from .launcher import DETACH_FLAGS

ENTRY = Path(__file__).resolve().parents[1] / "gamepool.py"


def cmd_up(config_path: str, rest: List[str]) -> int:
    try:
        client._info()
        client.status()
        print("pool already running", file=sys.stderr)
        return 2
    except client.PoolError:
        pass
    pdir = client.pool_dir()
    pdir.mkdir(parents=True, exist_ok=True)
    (pdir / "pool.json").unlink(missing_ok=True)
    log = open(pdir / "daemon.log", "w")
    cmd = [sys.executable, "-I", str(ENTRY), "--config", config_path, "daemon", *rest]
    kw = dict(stdout=log, stderr=log, stdin=subprocess.DEVNULL, close_fds=True)
    try:
        p = subprocess.Popen(cmd, creationflags=DETACH_FLAGS, **kw)
    except OSError:
        p = subprocess.Popen(cmd, creationflags=DETACH_FLAGS & ~0x01000000, **kw)
    deadline = time.time() + 900
    while time.time() < deadline:
        if (pdir / "pool.json").exists():
            print(json.dumps(client.status()["instances"], indent=1))
            return 0
        if p.poll() is not None:
            print("daemon exited early:\n" + (pdir / "daemon.log").read_text(), file=sys.stderr)
            return 3
        time.sleep(0.5)
    print(f"timed out waiting for the pool to warm up; see {pdir / 'daemon.log'}", file=sys.stderr)
    return 3


def main(config_path: str, argv: List[str]) -> int:
    import argparse
    if not argv or argv[0] in ("-h", "--help"):
        print(__doc__)
        return 0
    cmd, rest = argv[0], argv[1:]
    if cmd == "up":
        return cmd_up(config_path, rest)
    ap = argparse.ArgumentParser(prog="gamepool pool " + cmd)
    ap.add_argument("--owner")
    ap.add_argument("--n", type=int, default=1)
    ap.add_argument("--ttl", type=float, default=900)
    ap.add_argument("--timeout", type=float, default=600)
    ap.add_argument("--id")
    ap.add_argument("--dirty", action="store_true")
    a = ap.parse_args(rest)
    try:
        if cmd == "status":
            print(json.dumps(client.status(), indent=1))
        elif cmd == "lease":
            if not a.owner:
                ap.error("--owner required")
            print(json.dumps(client.request("lease", sock_timeout_s=a.timeout + 60, owner=a.owner, n=a.n, ttl_s=a.ttl,
                                            timeout_s=a.timeout)["lease"], indent=1))
        elif cmd == "release":
            if not a.id:
                ap.error("--id required")
            print(json.dumps(client.request("release", id=a.id, dirty=a.dirty)))
        elif cmd == "down":
            client.request("down")
            for _ in range(120):    # o serviço remove pool.json depois de encerrar seus jogos e liberar as vagas
                if not (client.pool_dir() / "pool.json").exists():
                    break
                time.sleep(1)
            print("pool down")
        else:
            ap.error("unknown command " + cmd)
    except client.PoolBusy as e:
        print("busy:", e, file=sys.stderr)
        return 3
    except client.PoolNotRunning as e:
        print(e, file=sys.stderr)
        return 2
    except client.PoolError as e:
        print("error:", e, file=sys.stderr)
        return 3
    return 0
