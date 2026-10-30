"""Partes do conjunto de instâncias que interagem com o sistema operacional: Slots reais (tools/gameslot) e Backend real (inicia o jogo).

Importar este módulo não inicia nada. Somente RealBackend.start() inicia um jogo, e apenas o serviço do conjunto
o chama. Os substitutos em memória para testes ficam em fakes.py.
"""
from __future__ import annotations

import re
import subprocess
import sys
from typing import Dict, List

from . import launcher, lowcost, winproc
from .adapter import Adapter, load_adapter
from .config import Config

OWNER = "pool"


class RealSlots:
    "Mantém `n` vagas de jogo por tools/gameslot para que outros agentes vejam a máquina como ocupada."

    def __init__(self, owner: str = OWNER, ttl_s: int = 3600, wait_s: int = 600):
        self.owner, self.ttl_s, self.wait_s = owner, ttl_s, wait_s

    def _cli(self, *a: str):
        cp = subprocess.run([sys.executable, "-I", str(launcher.GAMESLOT), *a], capture_output=True, text=True)
        return cp.returncode, (cp.stdout + cp.stderr).strip()

    def acquire(self, n: int) -> List[int]:
        rc, out = self._cli("acquire", "--owner", self.owner, "--ttl", str(self.ttl_s), "--wait", str(self.wait_s), "--slots", str(n))
        if rc != 0:
            raise RuntimeError(f"game slots unavailable: {out}")
        m = re.search(r"SLOTS ([0-9,]+)", out)
        return [int(x) for x in m.group(1).split(",")] if m else []

    def renew(self, n: int) -> None:
        self._cli("acquire", "--owner", self.owner, "--ttl", str(self.ttl_s), "--wait", "0", "--slots", str(n))

    def register_pid(self, pid: int) -> None:
        self._cli("register-pid", "--owner", self.owner, "--pid", str(pid))

    def release(self) -> None:
        self._cli("release", "--owner", self.owner)


class RealBackend:
    """Inicia cópias reais do jogo a partir das pastas de instância. O jogo, sua forma de inicialização e o modo
    de verificar se está pronto vêm da configuração e do adaptador."""

    def __init__(self, cfg: Config, adapter: Adapter = None, *, lowcost_on: bool = True, options: Dict[str, str] = None,
                 boot_timeout_s: float = 0.0):
        self.cfg = cfg
        self.adapter = adapter or load_adapter(cfg)
        self.lowcost_on, self.options, self.boot_timeout_s = lowcost_on, dict(options or {}), boot_timeout_s
        self.pid_of: Dict[int, int] = {}

    def prepare(self, i: int) -> None:
        d = self.cfg.instance_dir(i)
        if not (d / "instance.json").exists():
            raise RuntimeError(f"instance {i} is not provisioned: run `provision --n N` first")
        if self.lowcost_on and self.cfg["lowcost"]["rows"]:
            lowcost.apply(self.cfg, d, self.options)
        self.adapter.prepare(i)

    def start(self, i: int) -> int:
        pid = launcher.launch_instance(self.cfg, i, owner=OWNER)
        self.pid_of[i] = pid
        return pid

    def alive(self, pid: int) -> bool:
        info = winproc.process_info(pid) if pid else None
        return bool(info) and (not self.cfg.process_name or info["name"] == self.cfg.process_name)

    def ping(self, i: int) -> bool:
        pid = self.pid_of.get(i, 0)
        return bool(pid) and self.alive(pid) and bool(self.adapter.probe(i, pid))

    def wait_ready(self, i: int, pid: int) -> bool:
        return self.adapter.wait_ready(i, pid, self.alive, self.boot_timeout_s)

    def stats(self, pid: int) -> Dict:
        return winproc.proc_stats(pid)

    def kill(self, pid: int) -> None:
        "Somente um pid registrado por este conjunto e apenas enquanto continuar sendo o mesmo processo (protege contra reutilização de pid)."
        if launcher.is_recorded_process(self.cfg, pid, OWNER):
            winproc.kill_pid(pid)
        launcher.forget_pid(self.cfg, pid, OWNER)
        self.pid_of = {i: p for i, p in self.pid_of.items() if p != pid}

    def unlock(self, i: int) -> None:
        try:
            self.adapter.on_release(i)
        except Exception:  # noqa: BLE001 - a game side cleanup problem must not break the pool
            pass
