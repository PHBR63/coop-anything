#!/usr/bin/env python3
"""Executa simultaneamente um executor de roteiros por par host/cliente (vazão multiplicada pelo número de pares).

Cada par é uma sessão cooperativa própria: par k corresponde às instâncias k*P .. k*P+P-1 (P = --players-per-pair, padrão 2; a primeira é
o host). Você inicia e conecta as cópias do jogo, como em run_coop.py; esta ferramenta nunca inicia um jogo. Depois:

    python -I tools/bots/run_parallel.py --pairs 3 -- --adapter my_game:make_adapter --scenario fight.json --playbook fight
    python -I tools/bots/run_parallel.py --pairs 3 -- --playbook fight --from-step 4 --timescale 3     # argumentos após -- vão para cada executor
    python -I tools/bots/run_parallel.py --only 1,2 -- --adapter my_game:make_adapter --playbook quest_sync   # repete pares escolhidos
    python -I tools/bots/run_parallel.py --pairs 3 --dry-run -- --playbook fight                        # verificações e comandos, sem iniciar nada
    python -I tools/bots/run_parallel.py --pairs 3 --fake -- --playbook all                             # teste básico sem jogo

Cada executor (padrão tools/bots/run_coop.py, ou --runner FILE) recebe `--instances A,B --outdir <outdir>/pair<k>` (e `--fake` com
--fake). Sua saída aparece aqui com prefixo [pair<k>]. Ao final, uma tabela mostra PASS, FAIL, SETUP, BLOCKED, TIMEOUT ou CRASH
por par, com o motivo de toda falha, e <outdir>/parallel_summary.json contém o mesmo.

Cada executor também encontra seu par no ambiente: COOP_PAIR (k), COOP_INSTANCES ("A,B") e, quando --port-base é fornecido,
COOP_PORT (porta base + k), permitindo à fábrica de adaptadores escolher o pipe ou porta corretos. Use uma porta cooperativa por par.

Antes de iniciar qualquer coisa, recusa (saída 2) se dois pares usariam a mesma instância, pasta de saída ou porta cooperativa, se uma
opção desta ferramenta for passada após `--` (--instances, --outdir, --players), se faltar o arquivo do executor, ou se
a verificação opcional de `--preflight module:function` retornar problemas. Essa função recebe a lista de objetos PairPlan
e retorna uma lista de strings de problemas: use para questões conhecidas apenas pelo seu jogo (RAM livre para cópias, locação de uma
instância, porta já em uso).

Código de saída: 0 todos os pares passam, 1 um par falhou, esgotou o tempo ou travou, 3 um par ficou BLOCKED (seu executor saiu com 3: não conseguiu
colocar o jogo no estado necessário ao teste), 2 problema de configuração aqui ou em um executor. Esta ferramenta só encerra processos de executor
que ela mesma iniciou.
"""
from __future__ import annotations

import argparse
import collections
import importlib
import json
import os
import re
import subprocess
import sys
import threading
import time
from typing import Any, Callable, Deque, Dict, IO, List, Optional, Sequence

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_RUNNER = os.path.join(HERE, "run_coop.py")
TAIL_LINES = 400
MUTANT = os.environ.get("COOPBOTS_MUTANT", "")   # opção de variante exclusiva para testes: noprefix | passall | sameids | nokill | noforbid
# Opções que esta ferramenta define para cada executor ou que não podem ser compartilhadas entre pares.
FORBIDDEN_PASSTHROUGH = {
    "--instances": "this tool gives each pair its own instances",
    "--outdir": "this tool gives each pair its own output folder",
    "--players": "the number of players is the number of instances of a pair",
}
FAIL_LINE = re.compile(r"^FAIL\s+(\S+)\s+\d+ steps?\s*(.*)$")


# ---------------------------------------------------------------- o plano
class PairPlan:
    def __init__(self, k: int, instances: List[int], port: int, outdir: str, cmd: List[str]):
        self.k, self.instances, self.port, self.outdir, self.cmd = k, instances, port, outdir, cmd

    @property
    def name(self) -> str:
        return "pair%d" % self.k

    @property
    def host(self) -> int:
        return self.instances[0]

    @property
    def ids(self) -> str:
        return ",".join(str(i) for i in self.instances)


def pair_instances(k: int, per_pair: int) -> List[int]:
    if MUTANT == "sameids":
        k = 0
    return [k * per_pair + j for j in range(per_pair)]


def runner_cmd(runner: str, ids: str, outdir: str, extra: Sequence[str], fake: bool, python: Optional[str] = None) -> List[str]:
    "-X utf8 e -u: a saída é um pipe; sem eles, usaria buffer e a página de código ANSI."
    cmd = [python or sys.executable, "-I", "-X", "utf8", "-u", runner, "--instances", ids, "--outdir", outdir]
    if fake:
        cmd.append("--fake")
    return cmd + list(extra)


def plan_pairs(pair_list: Sequence[int], runner: str, outroot: str, port_base: int, per_pair: int, extra: Sequence[str],
               fake: bool) -> List[PairPlan]:
    out = []
    for k in pair_list:
        ids = pair_instances(k, per_pair)
        od = os.path.join(outroot, "pair%d" % k)
        out.append(PairPlan(k, ids, port_base + k if port_base else 0, od, runner_cmd(runner, ",".join(map(str, ids)), od, extra, fake)))
    return out


def plan_problems(plans: Sequence[PairPlan]) -> List[str]:
    "Problemas no próprio plano: dois pares em uma porta, instância ou pasta de saída."
    problems: List[str] = []
    for what, key in (("co-op port", lambda p: p.port or None), ("output folder", lambda p: os.path.normcase(os.path.abspath(p.outdir)))):
        seen: Dict[Any, PairPlan] = {}
        for p in plans:
            if key(p) is not None and key(p) in seen:
                problems.append("%s and %s would use the same %s (%s)" % (p.name, seen[key(p)].name, what, key(p)))
            seen.setdefault(key(p), p)
    owner: Dict[int, PairPlan] = {}
    for p in plans:
        for i in p.instances:
            if i in owner:
                problems.append("%s and %s would both use instance %d" % (p.name, owner[i].name, i))
            owner.setdefault(i, p)
    return problems


def passthrough_problems(extra: Sequence[str]) -> List[str]:
    if MUTANT == "noforbid":
        return []
    out = []
    for tok in extra:
        opt = tok.split("=", 1)[0]
        if opt in FORBIDDEN_PASSTHROUGH:
            out.append("%s after --: %s" % (opt, FORBIDDEN_PASSTHROUGH[opt]))
    return out


def load_preflight(spec: str) -> Callable[[Sequence[PairPlan]], List[str]]:
    mod, _, fn = spec.partition(":")
    sys.path.insert(0, os.getcwd())
    return getattr(importlib.import_module(mod), fn)


# ---------------------------------------------------------------- execução
class PairRun:
    def __init__(self, plan: PairPlan):
        self.plan = plan
        self.proc: Any = None
        self.thread: Optional[threading.Thread] = None
        self.tail: Deque[str] = collections.deque(maxlen=TAIL_LINES)
        self.t0 = 0.0
        self.t1 = 0.0
        self.rc: Optional[int] = None
        self.timed_out = False
        self.error = ""
        self.status = ""
        self.reasons: List[str] = []

    @property
    def seconds(self) -> float:
        return max(0.0, self.t1 - self.t0)


def default_spawn(cmd: List[str], env: Dict[str, str]) -> "subprocess.Popen[str]":
    return subprocess.Popen(cmd, env=env, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                            text=True, encoding="utf-8", errors="replace", bufsize=1)


def prefixed(name: str, line: str) -> str:
    if MUTANT == "noprefix":
        return line.rstrip()
    return "[%s] %s" % (name, line.rstrip())


def _pump(run: PairRun, out: IO[str], lock: threading.Lock) -> None:
    try:
        for line in run.proc.stdout:
            text = line.rstrip("\r\n")
            run.tail.append(text)
            with lock:
                print(prefixed(run.plan.name, text), file=out, flush=True)
    except (OSError, ValueError):
        pass


def pair_env(plan: PairPlan) -> Dict[str, str]:
    env = dict(os.environ)
    env["COOP_PAIR"] = str(plan.k)
    env["COOP_INSTANCES"] = plan.ids
    if plan.port:
        env["COOP_PORT"] = str(plan.port)
    return env


def read_summary(outdir: str) -> Optional[Dict[str, Any]]:
    try:
        with open(os.path.join(outdir, "summary.json"), encoding="utf-8") as f:
            d = json.load(f)
        return d if isinstance(d, dict) else None
    except (OSError, ValueError):
        return None


def classify(run: PairRun) -> None:
    "Define run.status e run.reasons a partir do código de saída, do summary.json do executor e do final da saída."
    rc = run.rc
    summ = read_summary(run.plan.outdir)
    reasons: List[str] = []
    if summ:
        for r in summ.get("results") or []:
            if isinstance(r, dict) and r.get("status", "pass" if r.get("ok", True) else "fail") == "fail":
                reasons.append("%s: %s" % (r.get("playbook", "?"), r.get("reason") or "failed"))
    if not reasons:
        for line in run.tail:
            m = FAIL_LINE.match(line.strip())
            if m:
                reasons.append("%s: %s" % (m.group(1), m.group(2) or "failed"))
    if run.error:
        run.status, run.reasons = "CRASH", [run.error]
    elif run.timed_out:
        run.status, run.reasons = "TIMEOUT", ["no result after %.0f s, the runner was stopped" % run.seconds] + reasons
    elif rc == 0 and not (summ and summ.get("ok") is False):
        run.status, run.reasons = "PASS", []
    elif rc == 0:
        run.status, run.reasons = "FAIL", reasons or ["exit code 0 but summary.json says ok=false"]
    else:
        run.status = {1: "FAIL", 2: "SETUP", 3: "BLOCKED"}.get(rc if rc is not None else -1, "CRASH")
        if not reasons:
            keep = [ln.strip() for ln in run.tail if ln.strip()]
            hot = [ln for ln in keep if re.search(r"cannot reach|BLOCKED|error|Traceback|unknown|missing|refus", ln, re.I)]
            reasons = (hot or keep)[-2:] or ["exit code %s and no output" % rc]
        if run.status == "CRASH":
            reasons = ["exit code %s" % rc] + reasons
        run.reasons = reasons


def run_all(plans: Sequence[PairPlan], *, out: IO[str], timeout_s: float = 0.0, stagger_s: float = 0.0,
            spawn: Callable[[List[str], Dict[str, str]], Any] = default_spawn, poll_s: float = 0.05,
            now: Callable[[], float] = time.monotonic, sleep: Callable[[float], None] = time.sleep) -> List[PairRun]:
    "Inicia cada par (separados por stagger_s), transmite a saída com prefixos, aplica o limite de tempo e classifica cada resultado."
    runs = [PairRun(p) for p in plans]
    lock = threading.Lock()
    pending = list(runs)
    next_start = now()
    try:
        while pending or any(r.rc is None and not r.error and r.proc is not None for r in runs):
            if pending and now() >= next_start:
                r = pending.pop(0)
                r.t0 = now()
                try:
                    r.proc = spawn(r.plan.cmd, pair_env(r.plan))
                    r.thread = threading.Thread(target=_pump, args=(r, out, lock), daemon=True)
                    r.thread.start()
                except OSError as e:
                    r.error, r.t1 = "cannot start the runner: %s" % e, now()
                next_start = now() + stagger_s
            for r in runs:
                if r.proc is None or r.rc is not None:
                    continue
                rc = r.proc.poll()
                if rc is None and timeout_s > 0 and now() - r.t0 > timeout_s and MUTANT != "nokill":
                    r.timed_out = True
                    r.proc.kill()
                    rc = r.proc.wait()
                if rc is not None:
                    r.rc, r.t1 = rc, now()
                    if r.thread:
                        r.thread.join(5.0)
            sleep(poll_s)
    finally:
        for r in runs:
            if r.proc is not None and r.rc is None:  # interrompido: nunca deixa um executor para trás
                try:
                    r.proc.kill()
                except OSError:
                    pass
    for r in runs:
        if r.proc is None and not r.error:
            r.error = "not started"
        classify(r)
    return runs


# ---------------------------------------------------------------- o relatório
def combine_exit(runs: Sequence[PairRun]) -> int:
    if MUTANT == "passall":
        return 0
    st = {r.status for r in runs}
    if not runs or st & {"FAIL", "TIMEOUT", "CRASH"}:
        return 1
    if "BLOCKED" in st:
        return 3
    if "SETUP" in st:
        return 2
    return 0


def format_table(runs: Sequence[PairRun], width: int = 100) -> str:
    rows = [("PAIR", "INSTANCES", "PORT", "RESULT", "TIME", "REASON")]
    for r in runs:
        reason = r.reasons[0] if r.reasons else ""
        if len(r.reasons) > 1:
            reason += "  (+%d more)" % (len(r.reasons) - 1)
        if len(reason) > width:
            reason = reason[:width - 3] + "..."
        rows.append((r.plan.name, r.plan.ids, str(r.plan.port or "-"), r.status, "%.0fs" % r.seconds, reason))
    w = [max(len(row[c]) for row in rows) for c in range(5)]
    lines = ["  ".join(row[c].ljust(w[c]) for c in range(5)) + "  " + row[5] for row in rows]
    lines = [ln.rstrip() for ln in lines]
    passed = sum(1 for r in runs if r.status == "PASS")
    lines.append("%d/%d pairs passed" % (passed, len(runs)))
    detail = [r for r in runs if r.reasons]
    if detail:
        lines.append("")
        lines.append("failures:")
        for r in detail:
            for reason in r.reasons:
                lines.append("  %s (%s): %s" % (r.plan.name, r.status, reason))
            lines.append("    folder: %s" % r.plan.outdir)
    return "\n".join(lines)


def summary_json(runs: Sequence[PairRun], extra: Sequence[str]) -> Dict[str, Any]:
    return {"ok": combine_exit(runs) == 0, "runner_args": list(extra),
            "pairs": [{"pair": r.plan.k, "instances": r.plan.instances, "port": r.plan.port, "status": r.status,
                       "exit_code": r.rc, "seconds": round(r.seconds, 1), "reasons": r.reasons, "outdir": r.plan.outdir,
                       "cmd": r.plan.cmd} for r in runs]}


def parse_pair_list(text: str) -> List[int]:
    ids = [int(x) for x in text.split(",") if x.strip() != ""]
    if not ids or any(i < 0 for i in ids) or len(set(ids)) != len(ids):
        raise ValueError("--only needs different pair numbers, 0 or more, such as 0,2; got %r" % text)
    return ids


def main(argv: Optional[Sequence[str]] = None, *, spawn: Callable[[List[str], Dict[str, str]], Any] = default_spawn,
         out: Optional[IO[str]] = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    extra: List[str] = []
    if "--" in argv:
        k = argv.index("--")
        argv, extra = argv[:k], argv[k + 1:]
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--pairs", type=int, default=0, help="executa pares 0..N-1 (par k = instâncias k*P .. k*P+P-1)")
    ap.add_argument("--only", default="", help="executa apenas estes pares, por exemplo 1,2 (para repetir os que falharam)")
    ap.add_argument("--players-per-pair", type=int, default=2, help="instâncias por par (padrão 2: um host e um cliente)")
    ap.add_argument("--runner", default=DEFAULT_RUNNER, help="executor de roteiros a iniciar para cada par (padrão run_coop.py)")
    ap.add_argument("--outdir", default="", help="padrão coop-bots-out/parallel/<time>; cada par escreve em <outdir>/pair<k>")
    ap.add_argument("--port-base", type=int, default=0, help="porta cooperativa do par 0; par k recebe base + k em COOP_PORT (0 = não usada)")
    ap.add_argument("--fake", action="store_true", help="sem jogo: passa --fake para cada executor")
    ap.add_argument("--timeout", type=float, default=1800.0, help="segundos por par antes de encerrar seu executor (0 = sem limite)")
    ap.add_argument("--stagger", type=float, default=0.0, help="segundos entre as inicializações dos pares")
    ap.add_argument("--dry-run", action="store_true", help="executa verificações e imprime comandos, sem iniciar nada")
    ap.add_argument("--preflight", default="", help="module:function(plans) -> lista de problemas, para verificações exclusivas do seu jogo")
    a = ap.parse_args(argv)
    out = out or sys.stdout

    try:
        pair_list = parse_pair_list(a.only) if a.only else list(range(a.pairs))
        if not pair_list:
            raise ValueError("give --pairs N (pairs 0..N-1) or --only 0,2")
        if a.players_per_pair < 2 or a.players_per_pair > 4:
            raise ValueError("--players-per-pair is 2 to 4")
        if a.port_base and (a.port_base < 1024 or a.port_base + max(pair_list) > 65535):
            raise ValueError("--port-base %d does not leave a valid port for every pair" % a.port_base)
    except ValueError as e:
        print("error: %s" % e, file=sys.stderr)
        return 2
    bad = passthrough_problems(extra)
    if not os.path.isfile(a.runner):
        bad.append("--runner %s: no such file" % a.runner)
    if bad:
        for b in bad:
            print("error: %s" % b, file=sys.stderr)
        return 2

    outroot = a.outdir or os.path.join("coop-bots-out", "parallel", time.strftime("%Y%m%dT%H%M%S"))
    plans = plan_pairs(pair_list, os.path.abspath(a.runner), outroot, a.port_base, a.players_per_pair, extra, a.fake)
    problems = plan_problems(plans)
    if a.preflight:
        try:
            problems += list(load_preflight(a.preflight)(plans) or [])
        except Exception as e:  # noqa: BLE001
            problems.append("--preflight %s failed: %s: %s" % (a.preflight, type(e).__name__, e))
    if problems:
        print("refusing to start:", file=sys.stderr)
        for p in problems:
            print("  %s" % p, file=sys.stderr)
        return 2
    for p in plans:
        print("%s: instances %s, port %s, outdir %s" % (p.name, p.ids, p.port or "-", p.outdir), file=out)
        if a.dry_run:
            print("  " + " ".join(p.cmd), file=out)
    if a.dry_run:
        print("dry run: checks passed, nothing started", file=out)
        return 0

    os.makedirs(outroot, exist_ok=True)
    runs = run_all(plans, out=out, timeout_s=a.timeout, stagger_s=a.stagger, spawn=spawn)
    print(file=out)
    print(format_table(runs), file=out)
    with open(os.path.join(outroot, "parallel_summary.json"), "w", encoding="utf-8") as f:
        json.dump(summary_json(runs, extra), f, indent=1)
    print("summary: %s" % os.path.join(outroot, "parallel_summary.json"), file=out)
    return combine_exit(runs)


if __name__ == "__main__":
    sys.exit(main())
