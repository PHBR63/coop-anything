"""Pares de host e cliente: quais cópias ficam juntas, a porta de cada par e se o PC tem RAM para elas.

Um teste cooperativo precisa de cópias em pares: host e cliente que se conecta a ele. Ao executar vários pares, cada um
precisa de sua porta, ou o segundo host não consegue vincular e os clientes entram no host errado. Este módulo só faz
as contas e verificações. Não inicia nada; `launcher.py` e `instances.py` o chamam.

    par k       = duas cópias, primeiro o host e depois seu cliente
    sua porta   = pairs.port_base + número da instância do host
    instâncias  = números obtidos por `up` das vagas de jogo, dois por vez, ou 2k e 2k+1 ao provisionar com --pairs

A porta deriva do número de instância do host, e esses números são exclusivos por vaga de jogo; portanto, dois agentes
executando pares ao mesmo tempo nunca recebem a mesma porta.

Configuração (bloco "pairs" da configuração do jogo):

    port_base    primeira porta, padrão 27960
    copy_gb      memória de uma cópia ativa em GiB, padrão 2.0 (meça com `gamepool.py measure`)
    reserve_gb   memória reservada para Windows e ferramentas de teste, padrão 2.0
    proto        "udp", "tcp" ou "both": o que vincular para conferir se a porta do par está livre; padrão "both"
    edits        {"File.ini": [["Section", "Key", "{port}"], ...]}: linhas escritas no arquivo privado de configurações de cada
                 instância antes de iniciar. {port} {pair} {role} {host} {client} {i} são preenchidos.
                 Os mesmos marcadores funcionam em launch.args e launch.env.
"""
from __future__ import annotations

import socket
from typing import Callable, Dict, Iterable, List, Optional, Sequence, Tuple

GIB = 2 ** 30
DEFAULT_PORT_BASE = 27960
DEFAULT_COPY_GB = 2.0
DEFAULT_RESERVE_GB = 2.0
PROTOS = ("udp", "tcp", "both")


# ---------------------------------------------------------------- disposição
def aligned_ids(pairs: int, first_pair: int = 0) -> List[int]:
    "Instâncias 2k e 2k+1 para os pares first_pair .. first_pair + pairs - 1."
    if pairs < 1:
        raise ValueError(f"--pairs must be 1 or more, got {pairs}")
    if first_pair < 0:
        raise ValueError(f"--first-pair must not be negative, got {first_pair}")
    return list(range(2 * first_pair, 2 * (first_pair + pairs)))


def port_of(host_instance: int, port_base: int = DEFAULT_PORT_BASE) -> int:
    return int(port_base) + int(host_instance)


def plan_pairs(ids: Sequence[int], port_base: int = DEFAULT_PORT_BASE) -> List[Dict]:
    "Agrupa números de instância de dois em dois (host, cliente), na ordem informada. Lança ValueError para quantidade ímpar ou repetição."
    ids = [int(i) for i in ids]
    if len(ids) < 2 or len(ids) % 2:
        raise ValueError(f"pairs need an even number of instances, got {len(ids)}")
    if len(set(ids)) != len(ids):
        raise ValueError(f"an instance appears twice: {ids}")
    out = []
    for k in range(len(ids) // 2):
        host, client = ids[2 * k], ids[2 * k + 1]
        out.append({"pair": k, "host": host, "client": client, "port": port_of(host, port_base)})
    ports = [p["port"] for p in out]
    if max(ports) > 65535 or min(ports) < 1024:
        raise ValueError(f"ports {min(ports)}..{max(ports)} must lie within 1024..65535 (lower pairs.port_base)")
    return out


def aligned_plan(pairs: int, port_base: int = DEFAULT_PORT_BASE, first_pair: int = 0) -> List[Dict]:
    plan = plan_pairs(aligned_ids(pairs, first_pair), port_base)
    for p in plan:
        p["pair"] += first_pair
    return plan


def context_for(plan: Iterable[Dict], i: int) -> Optional[Dict[str, object]]:
    "Marcadores da instância i ({port} {pair} {role} {host} {client}) ou None se i não pertencer a nenhum par do plano."
    for p in plan:
        if i in (p["host"], p["client"]):
            return {"port": p["port"], "pair": p["pair"], "role": "host" if i == p["host"] else "client",
                    "host": p["host"], "client": p["client"]}
    return None


# ---------------------------------------------------------------- RAM
def free_ram_bytes() -> int:
    "Memória física disponível em bytes. Retorna 0 se não puder ser lida, fazendo a verificação de RAM recusar."
    try:
        import ctypes
        if hasattr(ctypes, "windll"):
            class MemStatus(ctypes.Structure):
                _fields_ = [("dwLength", ctypes.c_ulong), ("dwMemoryLoad", ctypes.c_ulong), ("ullTotalPhys", ctypes.c_ulonglong),
                            ("ullAvailPhys", ctypes.c_ulonglong), ("ullTotalPageFile", ctypes.c_ulonglong),
                            ("ullAvailPageFile", ctypes.c_ulonglong), ("ullTotalVirtual", ctypes.c_ulonglong),
                            ("ullAvailVirtual", ctypes.c_ulonglong), ("sullAvailExtendedVirtual", ctypes.c_ulonglong)]
            st = MemStatus()
            st.dwLength = ctypes.sizeof(st)
            if not ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(st)):
                return 0
            return int(st.ullAvailPhys)
        with open("/proc/meminfo", encoding="ascii", errors="replace") as f:
            for line in f:
                if line.startswith("MemAvailable:"):
                    return int(line.split()[1]) * 1024
    except (OSError, ValueError, AttributeError):
        pass
    return 0


def max_pairs_by_ram(free_bytes: int, up_copies: int = 0, copy_gb: float = DEFAULT_COPY_GB,
                     reserve_gb: float = DEFAULT_RESERVE_GB) -> int:
    """Quantos pares cabem. Cópias já em execução contam como pares em formação (sua memória já saiu de free_bytes);
    cada cópia adicional exige copy_gb da memória livre além de reserve_gb."""
    spare = free_bytes / GIB - reserve_gb
    more = int(spare // copy_gb) if spare > 0 else 0
    return (max(0, up_copies) + more) // 2


def ram_problem(pairs: int, up_copies: int, free_bytes: int, copy_gb: float = DEFAULT_COPY_GB,
                reserve_gb: float = DEFAULT_RESERVE_GB) -> Optional[str]:
    "None se o PC tiver RAM para `pairs` pares; caso contrário, o motivo (exibido antes da recusa)."
    fit = max_pairs_by_ram(free_bytes, up_copies, copy_gb, reserve_gb)
    if pairs <= fit:
        return None
    new = max(0, 2 * pairs - up_copies)
    return (f"refusing {pairs} pair(s): {new} more game copies need {new * copy_gb:.1f} GB plus {reserve_gb:.1f} GB reserve, "
            f"but only {free_bytes / GIB:.1f} GB is free ({up_copies} copies already running); at most {fit} pair(s) fit. "
            "Close other programs, run fewer pairs, set pairs.copy_gb in the config if a copy needs less, or pass --no-ram-check")


# ---------------------------------------------------------------- portas
def port_free(port: int, proto: str = "both") -> bool:
    "True se nada neste PC ocupar a porta nos protocolos verificados (vincular a 127.0.0.1 funciona)."
    kinds = {"udp": [socket.SOCK_DGRAM], "tcp": [socket.SOCK_STREAM], "both": [socket.SOCK_DGRAM, socket.SOCK_STREAM]}[proto]
    for kind in kinds:
        s = socket.socket(socket.AF_INET, kind)
        try:
            s.bind(("127.0.0.1", int(port)))
        except OSError:
            return False
        finally:
            s.close()
    return True


def port_problems(plan: Iterable[Dict], proto: str = "both", skip_pairs: Iterable[int] = (),
                  is_free: Callable[[int, str], bool] = port_free) -> List[str]:
    "Uma mensagem por par cuja porta esteja ocupada. Pares em skip_pairs (nossas cópias já em execução) não são verificados."
    skip = set(skip_pairs)
    out = []
    for p in plan:
        if p["pair"] in skip:
            continue
        if not is_free(p["port"], proto):
            out.append(f"pair {p['pair']}: port {p['port']} is already in use on this PC (another pair, or another program)")
    return out


# ---------------------------------------------------------------- estado
def pair_state(host_alive: bool, client_alive: bool) -> str:
    if host_alive and client_alive:
        return "up"
    if host_alive or client_alive:
        return "partial"
    return "down"
