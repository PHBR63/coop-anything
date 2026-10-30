"""Inicia, observa e encerra várias cópias de jogo e executa comando de teste contra elas.

    gamepool.py --config game.json up --n 2          obtém 2 slots, inicia cópias, espera prontidão
    gamepool.py --config game.json status
    gamepool.py --config game.json down              encerra só processos de `up`, libera slots
    gamepool.py --config game.json job --id t1 --n 2 -- python my_test.py
        obtém n slots, executa comando com GAMEPOOL_INSTANCES=0,1 no ambiente, copia registros
        listados em collect_logs para <state>/runs/<id>/, sempre libera slots

Regras mantidas (cada uma tem teste):
  * Toda inicialização obtém primeiro slot (tools/gameslot). Números de instâncias são números de slots, para dois
    agentes nunca usarem mesma pasta de instância, nome de pipe ou porta.
  * Só processos iniciados pela ferramenta são encerrados, e só enquanto PID, nome de imagem e horário de criação
    corresponderem ao registro de início (PID reutilizado é outro processo).
  * Cópias iniciadas uma após outra: cópia k deve estar pronta antes de k+1 iniciar.
  * Cópia que encerra em watch_s segundos do início é informada com código de saída. Assim uma
    verificação de instância única ("já em execução") aparece. Veja playbook/multi-instance-testing.md.
  * Cópia inicia em grupo de processos destacado duradouro, para não morrer ao fim deste comando.

Pares e troca (veja README.md, "Pairs" e "Swap"):
    gamepool.py --config game.json up --pairs 3            3 pares host/cliente, cada qual na própria porta; recusa se faltar RAM
    gamepool.py --config game.json status --pairs          linha por par: portas, ambas cópias, ativo / parcial / inativo
    gamepool.py --config game.json swap --instances 0,1    pede ao adaptador trocar código em cópias em execução
"""
from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
import threading
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from . import instances, jobqueue, pairs as pairs_mod, winproc
from .adapter import Adapter, load_adapter
from .config import HUB, Config, ConfigError, state_dir

GAMESLOT = HUB / "tools" / "gameslot" / "gameslot.py"
DEFAULT_OWNER = os.environ.get("GAMEPOOL_OWNER", "gamepool")
DETACH_FLAGS = 0x00000008 | 0x00000200 | 0x01000000    # DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP | CREATE_BREAKAWAY_FROM_JOB


class SlotBusy(Exception):
    pass


class LaunchError(Exception):
    pass


# ------------------------------------------------------------------------------------------ slots de jogo
def gameslot_cli(*args: str) -> Tuple[int, str]:
    cp = subprocess.run([sys.executable, "-I", str(GAMESLOT), *args], capture_output=True, text=True)
    return cp.returncode, (cp.stdout + cp.stderr).strip()


def slot_acquire(owner: str = DEFAULT_OWNER, ttl: int = 900, wait: int = 3600, slots: int = 1) -> List[int]:
    "Obtém slots; retorna índices. Idempotente para mesmo responsável (renova)."
    code, out = gameslot_cli("acquire", "--owner", owner, "--ttl", str(ttl), "--wait", str(wait), "--slots", str(slots))
    if code != 0:
        raise SlotBusy(out)
    m = re.search(r"SLOTS ([0-9,]+)", out)
    return [int(x) for x in m.group(1).split(",")] if m else []


def slot_release(owner: str = DEFAULT_OWNER) -> str:
    return gameslot_cli("release", "--owner", owner)[1]


def register_pid(pid: int, owner: str = DEFAULT_OWNER) -> None:
    gameslot_cli("register-pid", "--owner", owner, "--pid", str(pid))


# ------------------------------------------------------------------------------------------ processos registrados
def state_path(cfg: Config, owner: str = DEFAULT_OWNER) -> Path:
    return cfg.instances_root / f"state-{owner}.json"


def load_state(cfg: Config, owner: str = DEFAULT_OWNER) -> Dict:
    try:
        d = json.loads(state_path(cfg, owner).read_text())
        d.setdefault("procs", {})
        return d
    except (OSError, ValueError):
        return {"procs": {}}


def save_state(cfg: Config, st: Dict, owner: str = DEFAULT_OWNER) -> None:
    p = state_path(cfg, owner)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(st, indent=1))


def record_proc(cfg: Config, i: int, pid: int, owner: str = DEFAULT_OWNER) -> None:
    info = winproc.process_info(pid) or {"name": "", "created": 0}
    st = load_state(cfg, owner)
    st["procs"][str(i)] = {"pid": pid, "created": info["created"], "name": info["name"]}
    save_state(cfg, st, owner)


def is_recorded_process(cfg: Config, pid: int, owner: str = DEFAULT_OWNER) -> bool:
    "True só se pid for processo registrado por este responsável e ainda for o mesmo processo."
    for rec in load_state(cfg, owner)["procs"].values():
        if rec["pid"] == pid:
            info = winproc.process_info(pid)
            return bool(info) and info["created"] == rec["created"] and info["name"] == rec["name"]
    return False


def all_recorded_pids(cfg: Config) -> List[int]:
    pids: List[int] = []
    root = cfg.instances_root
    if root.exists():
        for f in root.glob("state-*.json"):
            try:
                pids += [r["pid"] for r in json.loads(f.read_text()).get("procs", {}).values()]
            except (OSError, ValueError, KeyError):
                pass
    return pids


def forget_pid(cfg: Config, pid: int, owner: str = DEFAULT_OWNER) -> None:
    st = load_state(cfg, owner)
    st["procs"] = {i: r for i, r in st["procs"].items() if r["pid"] != pid}
    save_state(cfg, st, owner)


def kill_recorded(cfg: Config, i: int, owner: str = DEFAULT_OWNER) -> bool:
    st = load_state(cfg, owner)
    rec = st["procs"].pop(str(i), None)
    save_state(cfg, st, owner)
    if rec and is_recorded_process_rec(rec):
        winproc.kill_pid(rec["pid"])
        return True
    return False


def is_recorded_process_rec(rec: Dict) -> bool:
    info = winproc.process_info(rec["pid"])
    return bool(info) and info["created"] == rec["created"] and info["name"] == rec["name"]


# ------------------------------------------------------------------------------------------ inicialização
def spawn_detached(cmd, cwd, env, startupinfo=None) -> subprocess.Popen:
    """Inicia processo que sobrevive a nós: fora do nosso objeto job (breakaway), sem console, grupo próprio.
    Sem isto, jogo iniciado por comando breve morre com ele ao fechar o job pai. Se o
    job proibir breakaway (acesso negado), usa as mesmas flags sem ele."""
    kw = dict(cwd=cwd, env=env, startupinfo=startupinfo, close_fds=True,
              stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        return subprocess.Popen(cmd, creationflags=DETACH_FLAGS, **kw)
    except OSError:
        return subprocess.Popen(cmd, creationflags=DETACH_FLAGS & ~0x01000000, **kw)


def launch_command(cfg: Config, i: int, ctx: Optional[Dict] = None) -> Tuple[List[str], str, Dict[str, str]]:
    """(argv, cwd, env) da instância i. Cópia inicia na própria pasta com seu número no ambiente.
    ctx contém substituições do par (port, pair, role, host, client) de pairs.context_for(); preenchem {port} {pair} {role}
    {host} {client} em launch.args e launch.env e também são definidas como GAMEPOOL_PORT, GAMEPOOL_PAIR e GAMEPOOL_ROLE."""
    launch = cfg["launch"]
    if not launch["exe"]:
        raise ConfigError("launch.exe is not set")
    ctx = dict(ctx or {})
    d = cfg.instance_dir(i)
    exe = Path(cfg.fmt(launch["exe"], i, **ctx))
    if not exe.is_absolute():
        exe = d / exe
    env = dict(os.environ)
    env.update({k: cfg.fmt(v, i, **ctx) for k, v in launch["env"].items()})
    env["GAMEPOOL_INSTANCE"] = str(i)
    env["GAMEPOOL_INSTANCE_DIR"] = str(d)
    if ctx:
        env["GAMEPOOL_PAIR"], env["GAMEPOOL_ROLE"], env["GAMEPOOL_PORT"] = str(ctx["pair"]), str(ctx["role"]), str(ctx["port"])
    return [str(exe)] + [cfg.fmt(a, i, **ctx) for a in launch["args"]], str(d), env


def find_game_child(cfg: Config, loader_pid: int, skip: List[int]) -> int:
    """Processo real do jogo por trás de carregador: descendente dele com nome de imagem do jogo.
    Encontrado pela árvore de processos, não por 'apareceu processo novo com esse nome', para nunca selecionar um jogo
    que outro agente ou usuário iniciou no mesmo instante."""
    deadline = time.time() + float(cfg["launch"]["child_wait_s"])
    while time.time() < deadline:
        for cand in winproc.descendants(loader_pid, cfg.require_process_name()):
            if cand not in skip:
                return cand
        time.sleep(0.2)
    raise LaunchError(f"loader pid {loader_pid} started no {cfg.process_name} within {cfg['launch']['child_wait_s']} s")


def launch_instance_ex(cfg: Config, i: int, owner: Optional[str] = DEFAULT_OWNER,
                       ctx: Optional[Dict] = None) -> Tuple[int, subprocess.Popen]:
    """Inicia instância i. Retorna (PID do jogo, Popen do executável iniciado). PID registrado sob owner
    (arquivo de estado e slot de jogo) para só esta ferramenta poder encerrá-lo depois."""
    argv, cwd, env = launch_command(cfg, i, ctx)
    p = spawn_detached(argv, cwd, env, winproc.startup_info(cfg["launch"]["window"]))
    pid = p.pid
    if cfg["launch"]["spawns_game"]:
        pid = find_game_child(cfg, p.pid, all_recorded_pids(cfg))
    if owner:
        record_proc(cfg, i, pid, owner)
        register_pid(pid, owner)
    if cfg["launch"]["window"] == "minimized":
        threading.Thread(target=winproc.minimize_windows, args=(pid,), daemon=True).start()
    return pid, p


def launch_instance(cfg: Config, i: int, owner: Optional[str] = DEFAULT_OWNER) -> int:
    return launch_instance_ex(cfg, i, owner)[0]


def wait_alive(pid: int, seconds: float) -> bool:
    "True se pid ainda executar após `seconds`; retorna False assim que encerrar."
    end = time.time() + seconds
    while time.time() < end:
        if not winproc.pid_alive(pid):
            return False
        time.sleep(0.1)
    return winproc.pid_alive(pid)


# ------------------------------------------------------------------------------------------ ativar / desativar / estado
def start_instances(cfg: Config, ids: List[int], owner: str, adapter: Adapter, stagger_s: float, wait_ready_each: float,
                    pair_ctx: Optional[Dict[int, Dict]] = None) -> int:
    """Inicia cópias em `ids` uma após outra. Retorna 0, 2 (não provisionada) ou 3 (cópia encerrou ou nunca ficou pronta).
    pair_ctx mapeia número de instância às substituições do par: pairs.edits da configuração são escritas primeiro nos arquivos
    privados da instância; substituições chegam aos argumentos de inicialização."""
    st = load_state(cfg, owner)
    for i in ids:
        if not instances.provisioned(cfg, i):
            print(f"instance {i} is not provisioned; run `provision --n {max(ids) + 1}` first", file=sys.stderr)
            return 2
        rec = st["procs"].get(str(i))
        if rec and is_recorded_process_rec(rec):
            print(f"instance {i} already up (pid {rec['pid']})")
            continue
        adapter.prepare(i)
        ctx = (pair_ctx or {}).get(i)
        if ctx:
            instances.apply_pair_edits(cfg, i, ctx)
        pid, popen = launch_instance_ex(cfg, i, owner, ctx)
        time.sleep(stagger_s)
        if not wait_alive(pid, float(cfg["launch"]["watch_s"])):
            code = popen.poll()
            print(f"instance {i} (pid {pid}) exited within {cfg['launch']['watch_s']} s"
                  + (f" with exit code {code}" if code is not None else "")
                  + ". A single-instance check is a common cause; read the instance's logs.", file=sys.stderr)
            return 3
        if not adapter.wait_ready(i, pid, winproc.pid_alive, wait_ready_each):
            print(f"instance {i}: not ready (pid alive={winproc.pid_alive(pid)}) after {wait_ready_each:.0f} s; "
                  "no further copies are started", file=sys.stderr)
            return 3
        print(f"instance {i} ready (pid {pid})")
    return 0


def foreign_pids(cfg: Config) -> List[int]:
    "Processos em execução com nome de imagem do jogo que nenhum responsável desta ferramenta registrou (talvez jogo do usuário)."
    mine = set(all_recorded_pids(cfg))
    return [p for p in winproc.list_pids(cfg.require_process_name()) if p not in mine]


def stop_owner(cfg: Config, owner: str) -> List[int]:
    "Encerra processos registrados de owner (só enquanto forem os mesmos processos) e esquece-os."
    st = load_state(cfg, owner)
    killed = []
    for i, rec in list(st["procs"].items()):
        if is_recorded_process_rec(rec):          # nunca encerra PID reutilizado
            winproc.kill_pid(rec["pid"])
            killed.append(rec["pid"])
            print(f"killed instance {i} (pid {rec['pid']})")
        st["procs"].pop(i)
    st.pop("pairs", None)
    save_state(cfg, st, owner)
    return killed


def up_copies_of(cfg: Config, owner: str) -> int:
    "Quantas cópias deste responsável estão executando agora."
    return sum(1 for rec in load_state(cfg, owner)["procs"].values() if is_recorded_process_rec(rec))


def pair_ram_report(cfg: Config, pairs: int, owner: str, free_ram_gb: Optional[float], check: bool = True) -> Tuple[Dict, Optional[str]]:
    "(números, motivo de recusa ou None) para iniciar `pairs` pares. RAM por cópia vem de pairs.copy_gb na configuração."
    pc = cfg.pairs
    up = up_copies_of(cfg, owner)
    free = int(free_ram_gb * pairs_mod.GIB) if free_ram_gb is not None else pairs_mod.free_ram_bytes()
    copy_gb, reserve_gb = float(pc["copy_gb"]), float(pc["reserve_gb"])
    reason = pairs_mod.ram_problem(pairs, up, free, copy_gb, reserve_gb) if check else None
    return ({"free_gb": round(free / pairs_mod.GIB, 2), "copy_gb": copy_gb, "reserve_gb": reserve_gb, "copies_up": up,
             "max_pairs": pairs_mod.max_pairs_by_ram(free, up, copy_gb, reserve_gb), "checked": check, "ok": reason is None}, reason)


def running_pairs(cfg: Config, plan: List[Dict], owner: str) -> List[int]:
    "Pares do plano cujo host já está executando (segundo `up` não deve reclamar da própria porta)."
    st = load_state(cfg, owner)
    out = []
    for p in plan:
        rec = st["procs"].get(str(p["host"]))
        if rec and is_recorded_process_rec(rec):
            out.append(p["pair"])
    return out


def cmd_up_pairs(cfg: Config, a, adapter: Adapter) -> int:
    n = 2 * a.pairs
    if a.n is not None and a.n != n:
        print(f"--n {a.n} does not match --pairs {a.pairs} (that is {n} instances); give only one", file=sys.stderr)
        return 2
    proto = cfg.pairs["proto"]
    ram, ram_reason = pair_ram_report(cfg, a.pairs, a.owner, a.free_ram_gb, not a.no_ram_check)
    if a.dry_run:
        ids = pairs_mod.aligned_ids(a.pairs)
        plan = pairs_mod.plan_pairs(ids, int(cfg.pairs["port_base"]))
        probs = [] if a.no_port_check else pairs_mod.port_problems(plan, proto, running_pairs(cfg, plan, a.owner))
        print(json.dumps({"dry_run": True, "assumed_instances": ids, "pairs": plan, "ram": ram, "port_problems": probs}, indent=1))
        for msg in ([ram_reason] if ram_reason else []) + probs:
            print(msg, file=sys.stderr)
        return 4 if (ram_reason or probs) else 0
    if ram_reason:
        print(ram_reason, file=sys.stderr)
        return 4
    try:
        ids = slot_acquire(a.owner, ttl=a.ttl, wait=a.slot_wait, slots=n)
    except SlotBusy as e:
        print(f"game slot busy: {e}", file=sys.stderr)
        return 3

    def give_back() -> None:
        if not load_state(cfg, a.owner)["procs"]:       # mantém slots enquanto nossas cópias executam
            slot_release(a.owner)
    try:
        plan = pairs_mod.plan_pairs(sorted(ids), int(cfg.pairs["port_base"]))
    except ValueError as e:
        print(f"cannot form pairs: {e}", file=sys.stderr)
        give_back()
        return 4
    if not a.no_port_check:
        probs = pairs_mod.port_problems(plan, proto, running_pairs(cfg, plan, a.owner))
        if probs:
            for msg in probs:
                print(msg + "; nothing was started (--no-port-check to start anyway)", file=sys.stderr)
            give_back()
            return 4
    foreign = foreign_pids(cfg)
    if foreign and not a.allow_foreign:
        print(f"{cfg.process_name} already running (pids {foreign}) and not ours. It may be the owner's own game; "
              "nothing was started. Use --allow-foreign to start copies next to it.", file=sys.stderr)
        give_back()
        return 2
    st = load_state(cfg, a.owner)
    st["pairs"] = plan
    save_state(cfg, st, a.owner)
    for p in plan:
        print(f"pair {p['pair']}: host instance {p['host']}, client instance {p['client']}, port {p['port']}")
    ctx = {i: pairs_mod.context_for(plan, i) for i in sorted(ids)}
    return start_instances(cfg, sorted(ids), a.owner, adapter, a.stagger, a.wait_ready_each, ctx)


def cmd_up(cfg: Config, a, adapter: Optional[Adapter] = None) -> int:
    cfg.require_dirs()
    cfg.require_process_name()
    adapter = adapter or load_adapter(cfg)
    if a.pairs:
        return cmd_up_pairs(cfg, a, adapter)
    try:
        ids = slot_acquire(a.owner, ttl=a.ttl, wait=a.slot_wait, slots=2 if a.n is None else a.n)
    except SlotBusy as e:
        print(f"game slot busy: {e}", file=sys.stderr)
        return 3
    foreign = foreign_pids(cfg)
    if foreign and not a.allow_foreign:
        print(f"{cfg.process_name} already running (pids {foreign}) and not ours. It may be the owner's own game; "
              "nothing was started. Use --allow-foreign to start copies next to it.", file=sys.stderr)
        if not load_state(cfg, a.owner)["procs"]:       # mantém slots enquanto nossas cópias executam
            slot_release(a.owner)
        return 2
    print("instances:", ids)
    return start_instances(cfg, ids, a.owner, adapter, a.stagger, a.wait_ready_each)


def cmd_down(cfg: Config, a) -> int:
    stop_owner(cfg, a.owner)
    print(slot_release(a.owner))
    return 0


def recorded_everywhere(cfg: Config) -> Dict[str, Dict]:
    "número de instância (texto) -> seu registro mais responsável, em arquivos de estado de todos os responsáveis."
    root = cfg.instances_root
    recorded: Dict[str, Dict] = {}
    if root.exists():
        for f in root.glob("state-*.json"):
            owner = f.stem[len("state-"):]
            for i, rec in load_state(cfg, owner)["procs"].items():
                recorded[i] = dict(rec, owner=owner)
    return recorded


def pair_rows(cfg: Config, adapter: Optional[Adapter] = None) -> List[Dict]:
    "Uma linha por par iniciado por `up --pairs` (ainda não parado por `down`): porta, ambas as cópias, estado."
    root = cfg.instances_root
    rows: List[Dict] = []
    if not root.exists():
        return rows

    def side(st: Dict, i: int) -> Dict:
        rec = st["procs"].get(str(i))
        alive = bool(rec and is_recorded_process_rec(rec))
        ready = False
        if alive and adapter is not None:
            try:
                ready = bool(adapter.probe(i, rec["pid"]))
            except Exception:  # noqa: BLE001  (a probe that fails is "not ready", not a crash of the status command)
                ready = False
        return {"instance": i, "pid": rec["pid"] if rec else None, "alive": alive, "ready": ready}

    for f in sorted(root.glob("state-*.json")):
        owner = f.stem[len("state-"):]
        st = load_state(cfg, owner)
        for p in st.get("pairs", []):
            h, c = side(st, p["host"]), side(st, p["client"])
            rows.append({"pair": p["pair"], "owner": owner, "port": p["port"], "host": h, "client": c,
                         "state": pairs_mod.pair_state(h["alive"], c["alive"])})
    return sorted(rows, key=lambda r: (r["owner"], r["pair"]))


def cmd_status(cfg: Config, a) -> int:
    root = cfg.instances_root
    if getattr(a, "pairs", False):
        print(json.dumps(pair_rows(cfg, load_adapter(cfg)), indent=1))
        return 0
    recorded = recorded_everywhere(cfg)
    roles: Dict[int, Dict] = {}
    for r in pair_rows(cfg):
        roles[r["host"]["instance"]] = {"pair": r["pair"], "role": "host", "port": r["port"]}
        roles[r["client"]["instance"]] = {"pair": r["pair"], "role": "client", "port": r["port"]}
    rows = []
    for dd in sorted(p for p in root.glob("*") if p.name.isdigit()) if root.exists() else []:
        i = dd.name
        rec = recorded.get(i)
        row = {"instance": int(i), "dir": str(dd), "provisioned": (dd / "instance.json").exists(),
               "pid": rec["pid"] if rec else None, "owner": rec["owner"] if rec else None,
               "alive": bool(rec and is_recorded_process_rec(rec)), "lock": jobqueue.holder(root, int(i))}
        if int(i) in roles:
            row.update(roles[int(i)])
        rows.append(row)
    print(json.dumps(rows, indent=1))
    return 0


# ------------------------------------------------------------------------------------------ troca
def parse_ids(spec: str) -> List[int]:
    out = []
    for part in spec.split(","):
        part = part.strip()
        if part:
            out.append(int(part))
    return out


def swap_targets(cfg: Config, a) -> Tuple[List[Dict], Optional[str]]:
    """Cópias em execução às quais uma troca se aplica. Retorna (targets, error). Cópia que `up` não iniciou para este responsável,
    ou não está mais executando, é erro, para a troca nunca atingir processo alheio."""
    st = load_state(cfg, a.owner)
    pair_of: Dict[int, Tuple[int, str]] = {}
    for p in st.get("pairs", []):
        pair_of[p["host"]], pair_of[p["client"]] = (p["pair"], "host"), (p["pair"], "client")
    if a.instances:
        try:
            ids = parse_ids(a.instances)
        except ValueError:
            return [], f"--instances must be numbers separated by commas, got {a.instances!r}"
    elif a.pair:
        ids = []
        for k in a.pair:
            match = [p for p in st.get("pairs", []) if p["pair"] == k]
            if not match:
                return [], f"pair {k} is not running (nothing recorded by `up --pairs` for owner {a.owner})"
            ids += [match[0]["host"], match[0]["client"]]
    else:
        ids = sorted(int(i) for i in st["procs"])
    if not ids:
        return [], f"no running copies recorded for owner {a.owner}; start some with `up` first"
    targets = []
    for i in ids:
        rec = st["procs"].get(str(i))
        if not rec or not is_recorded_process_rec(rec):
            return [], f"instance {i} is not running (not started by `up` for owner {a.owner}, or it has exited)"
        pr = pair_of.get(i)
        targets.append({"instance": i, "pid": rec["pid"], "rec": rec, "pair": pr[0] if pr else None, "role": pr[1] if pr else None})
    return targets, None


def swap_refusals(adapter: Adapter, targets: List[Dict], payload: Dict[str, str]) -> List[Dict]:
    "Cópias que não permitem troca, com motivo do adaptador. Consultadas todas antes de alterar qualquer cópia."
    out = []
    for t in targets:
        try:
            reason = adapter.can_swap(t["instance"], t["pid"], payload)
        except Exception as e:  # noqa: BLE001
            reason = f"can_swap raised {type(e).__name__}: {e}"
        if reason:
            out.append({"instance": t["instance"], "reason": str(reason)})
    return out


def swap_verify(cfg: Config, adapter: Adapter, t: Dict, settle_s: float) -> Optional[str]:
    """None se a cópia ainda for o mesmo processo e saudável; senão, motivo. Troca que reiniciou cópia é falha:
    `up`, `down` e pool conhecem a cópia pelo processo registrado."""
    if not is_recorded_process_rec(t["rec"]):
        return "the copy's process is gone or was replaced during the swap"
    end = time.monotonic() + max(0.0, settle_s)
    while True:
        try:
            ok = bool(adapter.probe(t["instance"], t["pid"]))
        except Exception:  # noqa: BLE001
            ok = False
        if ok:
            return None
        if time.monotonic() >= end:
            return f"the copy is not healthy {settle_s:g} s after the swap"
        time.sleep(min(0.2, max(0.01, end - time.monotonic())))


def run_swap(cfg: Config, adapter: Adapter, targets: List[Dict], payload: Dict[str, str], settle_s: float, say=None,
             stop_on_failure: bool = True) -> Dict:
    "Troca as cópias uma após outra na ordem fornecida. Para na primeira falha; restantes informadas como puladas."
    say = say or (lambda s: None)
    results = []
    failed = False
    for t in targets:
        row = {"instance": t["instance"], "pair": t["pair"], "role": t["role"], "pid": t["pid"], "status": "skipped", "detail": ""}
        results.append(row)
        if failed and stop_on_failure:
            continue
        t0 = time.monotonic()
        say(f"swapping instance {t['instance']} (pid {t['pid']})")
        try:
            res = adapter.swap(t["instance"], t["pid"], payload)
        except Exception as e:  # noqa: BLE001
            row.update(status="failed", detail=f"swap raised {type(e).__name__}: {e}")
            failed = True
            continue
        if isinstance(res, dict) and res.get("ok") is False:
            row.update(status="failed", detail=str(res.get("detail") or "the adapter reported a failure"))
            failed = True
            continue
        problem = swap_verify(cfg, adapter, t, settle_s)
        if problem:
            row.update(status="failed", detail=problem)
            failed = True
            continue
        row.update(status="swapped", detail=str(res.get("detail", "")) if isinstance(res, dict) else "")
        row["seconds"] = round(time.monotonic() - t0, 2)
    return {"ok": not failed, "swapped": sum(1 for r in results if r["status"] == "swapped"), "results": results}


def cmd_swap(cfg: Config, a, adapter: Optional[Adapter] = None) -> int:
    "Saída 0 trocado (ou simulação ok), 1 cópia falhou, 2 recusado antes de alterar algo."
    cfg.require_dirs()
    adapter = adapter or load_adapter(cfg)
    payload: Dict[str, str] = {}
    for kv in a.arg:
        k, sep, v = kv.partition("=")
        if not sep or not k:
            print(f"--arg needs KEY=VALUE, got {kv!r}", file=sys.stderr)
            return 2
        payload[k] = v
    targets, err = swap_targets(cfg, a)
    if err:
        print(err, file=sys.stderr)
        return 2
    refused = swap_refusals(adapter, targets, payload)
    report: Dict
    if refused:
        for r in refused:
            print(f"instance {r['instance']} cannot be swapped: {r['reason']}", file=sys.stderr)
        print("nothing was swapped", file=sys.stderr)
        report = {"ok": False, "refused": refused, "swapped": 0, "results": []}
        rc = 2
    elif a.dry_run:
        report = {"ok": True, "dry_run": True, "swapped": 0,
                  "results": [{"instance": t["instance"], "pair": t["pair"], "role": t["role"], "pid": t["pid"], "status": "can_swap"}
                              for t in targets]}
        rc = 0
    else:
        report = run_swap(cfg, adapter, targets, payload, a.settle_s, lambda s: print(s, file=sys.stderr, flush=True))
        rc = 0 if report["ok"] else 1
    report["payload"] = payload
    text = json.dumps(report, indent=1)
    if a.out:
        Path(a.out).write_text(text, encoding="utf-8")
    print(text)
    return rc


# ------------------------------------------------------------------------------------------ tarefas
def collect_logs(cfg: Config, i: int, since: float, dest: Path) -> List[str]:
    "Copia arquivos da instância i que correspondem aos padrões collect_logs e mudaram após `since` para dest/inst<i>/."
    d = cfg.instance_dir(i)
    out = dest / f"inst{i}"
    got = []
    for pat in cfg["collect_logs"]:
        for f in d.glob(pat):
            if f.is_file() and f.stat().st_mtime >= since:
                rel = f.relative_to(d)
                tgt = out / rel
                tgt.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(f, tgt)
                got.append(str(rel))
    return got


def run_job(cfg: Config, job_id: str, n: int, cmd: List[str], *, timeout_s: float = 900.0, owner: str = DEFAULT_OWNER,
            use_slot: bool = True, pool: int = 2, slot_wait_s: int = 3600, check_pins: bool = True,
            require: Optional[List[str]] = None, extra_env: Optional[Dict[str, str]] = None,
            runs_dir: Optional[Path] = None) -> Dict:
    """Executa cmd com instâncias permitidas em GAMEPOOL_INSTANCES. Com use_slot são os slots
    obtidos de gameslot; caso contrário, locadas por bloqueio de arquivo de range(pool)."""
    runs = Path(runs_dir or state_dir() / "runs") / job_id
    runs.mkdir(parents=True, exist_ok=True)
    result: Dict = {"job": job_id, "n": n, "cmd": cmd, "status": "error"}
    t_queue = time.time()
    held = None
    if use_slot:
        try:
            inst = slot_acquire(owner, ttl=int(timeout_s) + 300, wait=slot_wait_s, slots=n)
        except SlotBusy as e:
            result.update(status="slot_busy", message=str(e))
            (runs / "result.json").write_text(json.dumps(result, indent=1))
            return result
    else:
        held = jobqueue.acquire(cfg.instances_root, n, pool=pool, job=job_id, timeout_s=slot_wait_s)
        inst = jobqueue.instance_ids(held)
    try:
        result.update(instances=inst, queued_s=round(time.time() - t_queue, 2))
        problems: List[str] = []
        if check_pins:
            for i in inst:
                if not instances.provisioned(cfg, i):
                    problems.append(f"inst{i}: not provisioned")
                else:
                    problems += [f"inst{i}: {p}" for p in instances.verify_pins(cfg, i, require)]
        if problems:
            result.update(status="pin_mismatch", problems=problems)
        else:
            env = dict(os.environ)
            env.update(extra_env or {})
            env["GAMEPOOL_INSTANCES"] = ",".join(map(str, inst))
            env["GAMEPOOL_JOB"] = job_id
            t0 = time.time()
            try:
                cp = subprocess.run(cmd, env=env, capture_output=True, text=True, timeout=timeout_s)
                result.update(status="pass" if cp.returncode == 0 else "fail", returncode=cp.returncode)
                (runs / "stdout.txt").write_text(cp.stdout)
                (runs / "stderr.txt").write_text(cp.stderr)
            except subprocess.TimeoutExpired as e:
                result.update(status="timeout")
                so = e.stdout.decode(errors="replace") if isinstance(e.stdout, bytes) else (e.stdout or "")
                (runs / "stdout.txt").write_text(so)
            result["duration_s"] = round(time.time() - t0, 2)
            result["logs"] = {str(i): collect_logs(cfg, i, t0, runs) for i in inst}
    finally:
        if use_slot:
            slot_release(owner)
        else:
            for lk in held or []:
                lk.release()
    (runs / "result.json").write_text(json.dumps(result, indent=1))
    return result


def main(cfg: Config, argv: List[str]) -> int:
    import argparse
    ap = argparse.ArgumentParser(prog="gamepool up|down|status|swap|job")
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("up")
    p.add_argument("--n", type=int, default=None, help="número de cópias (padrão 2)")
    p.add_argument("--pairs", type=int, default=0, help="N pares host/cliente (2N cópias), cada par na própria porta")
    p.add_argument("--no-ram-check", action="store_true", help="com --pairs: inicia mesmo se RAM livre parecer insuficiente")
    p.add_argument("--no-port-check", action="store_true", help="com --pairs: não verifica se porta de cada par está livre")
    p.add_argument("--dry-run", action="store_true", help="com --pairs: imprime plano (portas, RAM), sem iniciar nada")
    p.add_argument("--free-ram-gb", type=float, default=None, help="com --pairs: usa isto como RAM livre em vez de ler o PC")
    p.add_argument("--stagger", type=float, default=cfg["launch"]["stagger_s"])
    p.add_argument("--ttl", type=int, default=1800, help="locação de slot em segundos (liberada por `down`)")
    p.add_argument("--slot-wait", type=int, default=3600)
    p.add_argument("--wait-ready-each", type=float, default=float(cfg["ready"].get("timeout_s", 300)))
    p.add_argument("--allow-foreign", action="store_true", help="inicia cópias mesmo com outra cópia do jogo executando")
    p.add_argument("--owner", default=DEFAULT_OWNER)
    p = sub.add_parser("down")
    p.add_argument("--owner", default=DEFAULT_OWNER)
    p = sub.add_parser("status")
    p.add_argument("--owner", default=DEFAULT_OWNER)
    p.add_argument("--pairs", action="store_true", help="uma linha por par host/cliente em vez de por instância")
    p = sub.add_parser("swap", help="pede ao adaptador trocar código em cópias em execução")
    p.add_argument("--owner", default=DEFAULT_OWNER)
    p.add_argument("--instances", default="", help="lista de números de instância por vírgulas (padrão: toda cópia iniciada por este responsável)")
    p.add_argument("--pair", type=int, action="append", default=[], help="troca ambas as cópias deste par; repetível")
    p.add_argument("--arg", action="append", default=[], metavar="KEY=VALUE", help="passado ao adaptador como carga útil; repetível")
    p.add_argument("--settle-s", type=float, default=20.0, help="quanto tempo uma cópia pode levar para voltar a ficar saudável após troca")
    p.add_argument("--dry-run", action="store_true", help="só pergunta a cada cópia se permite troca")
    p.add_argument("--out", default="", help="também escreve relatório JSON neste arquivo")
    p = sub.add_parser("job")
    p.add_argument("--id", required=True)
    p.add_argument("--n", type=int, default=2)
    p.add_argument("--pool", type=int, default=2, help="instâncias disponíveis com --no-slot")
    p.add_argument("--timeout", type=float, default=900)
    p.add_argument("--owner", default=DEFAULT_OWNER)
    p.add_argument("--require", action="append", default=[], metavar="REL", help="arquivo obrigatório em toda instância")
    p.add_argument("--no-pin-check", action="store_true")
    p.add_argument("--no-slot", action="store_true", help="tarefa não executa jogo: loca instâncias só por bloqueio de arquivo")
    p.add_argument("cmd_", nargs=argparse.REMAINDER)
    a = ap.parse_args(argv)
    if a.cmd == "up":
        return cmd_up(cfg, a)
    if a.cmd == "down":
        return cmd_down(cfg, a)
    if a.cmd == "status":
        return cmd_status(cfg, a)
    if a.cmd == "swap":
        return cmd_swap(cfg, a)
    cmd = [c for c in a.cmd_ if c != "--"]
    if not cmd:
        ap.error("job needs a command after --")
    cfg.require_dirs()
    r = run_job(cfg, a.id, a.n, cmd, timeout_s=a.timeout, owner=a.owner, use_slot=not a.no_slot, pool=a.pool,
                check_pins=not a.no_pin_check, require=a.require)
    print(json.dumps(r, indent=1))
    return 0 if r["status"] == "pass" else 1
