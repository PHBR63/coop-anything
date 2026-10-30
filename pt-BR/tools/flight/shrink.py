"""Redução automática (depuração delta) de dados de teste que reproduzem uma falha, com construtor de dados e hooks de reprodução intercambiáveis.

O hook de reprodução é a única parte específica do jogo. Recebe dados de teste e informa se houve falha; há duas formas de integrá-lo:
  * comando (CommandOracle): `<program> ... {fixture}`; {fixture} vira o caminho de um arquivo JSON temporário;
  * função Python (PyOracle): "module:function", chamada com o dicionário dos dados de teste.
toy_replay.py nesta pasta é um exemplo completo das duas formas.

JSON de dados de teste v1: {"version":1, "config":{...}, "steps":[{"op":"deliver"|"inject"|"quiesce"|..., ...}]}
Cada etapa precisa ser independente: remover qualquer subconjunto mantém os dados válidos. Etapas com "pin": true nunca
são removidas (use em uma verificação final, como "quiesce"). A lista também pode se chamar "ops" ou ter o nome passado em list_key.

Contrato do resultado de reprodução (comando): saída 0 = convergiu; 1 = divergiu; 2 = dados inválidos. stdout pode terminar
com uma linha JSON {"diverged": bool, "violations": [...], "first": {...}} ou exibir uma linha por regra quebrada:
`VIOLATION <rule-name> <detail>`. A assinatura da falha é o nome da primeira regra (ou a primeira violação sem números e hashes),
para rejeitar uma redução que transforme a falha em outra diferente.

A redução usa o algoritmo ddmin de Zeller e Hildebrandt, "Simplifying and Isolating Failure-Inducing Input" (2002).
"""
import importlib
import json
import os
import re
import subprocess
import sys
import tempfile
import time

import cofr as C
import analyze as A


class OracleError(Exception):
    pass


# ---------------------------------------------------------------- assinaturas

_NORM = re.compile(r"0x[0-9a-fA-F]+|[0-9a-fA-F]{8,}|\d+")


def signature(result):
    """Texto curto que nomeia o tipo de falha, removendo números e hashes, para rejeitar uma redução que
    transforme a falha em outra diferente."""
    if not result.get("diverged"):
        return None
    if result.get("invariant"):
        return str(result["invariant"])
    v = result.get("violations") or []
    if v:
        return _NORM.sub("#", str(v[0]))[:160]
    first = result.get("first") or {}
    return "diverged:" + str(first.get("category", "?"))


# ---------------------------------------------------------------- oráculos

def _msvcrt_split(s):
    """Interpreta aspas de argumentos do Windows, incluindo a saída de list2cmdline e aspas
    duplicadas dentro de um argumento entre aspas. Não é interpretação de shell: metacaracteres
    são passados literalmente. shlex(posix=False) mantém incorretamente as aspas dos caminhos."""
    args, i, n = [], 0, len(s)
    while True:
        while i < n and s[i] in " \t":
            i += 1
        if i >= n:
            return args
        cur, inq = [], False
        while True:
            if i >= n or (not inq and s[i] in " \t"):
                args.append("".join(cur))
                if i >= n:
                    return args
                i += 1
                break
            c = s[i]
            if c == "\\":
                bs = 0
                while i < n and s[i] == "\\":
                    bs += 1
                    i += 1
                if i < n and s[i] == '"':
                    cur.append("\\" * (bs // 2))
                    if bs % 2:
                        cur.append('"')
                        i += 1
                    else:
                        if inq and i + 1 < n and s[i + 1] == '"':
                            cur.append('"')
                            i += 2
                        else:
                            inq = not inq
                            i += 1
                else:
                    cur.append("\\" * bs)
            elif c == '"':
                if inq and i + 1 < n and s[i + 1] == '"':
                    cur.append('"')
                    i += 2
                else:
                    inq = not inq
                    i += 1
            else:
                cur.append(c)
                i += 1


class CommandOracle:
    "Executa programa externo de reprodução. cmd é lista de argumentos (ou string), substituindo {fixture} por um arquivo temporário."

    def __init__(self, cmd, tmpdir=None, timeout=60):
        if isinstance(cmd, str):
            if os.name == "nt":
                cmd = _msvcrt_split(cmd)
            else:
                import shlex
                cmd = shlex.split(cmd, posix=True)
        if not any("{fixture}" in c for c in cmd):
            raise OracleError("replay command must contain {fixture}")
        self.cmd = cmd
        self.tmpdir = tmpdir
        self.timeout = timeout
        self.runs = 0

    def __call__(self, fixture):
        self.runs += 1
        fd, path = tempfile.mkstemp(suffix=".json", prefix="shrink_", dir=self.tmpdir)
        try:
            with os.fdopen(fd, "w") as f:
                json.dump(fixture, f)
            args = [c.replace("{fixture}", path) for c in self.cmd]
            try:
                p = subprocess.run(args, capture_output=True, text=True, timeout=self.timeout, errors="replace")
            except subprocess.TimeoutExpired:
                raise OracleError("replay timed out after %ss" % self.timeout)
            except OSError as e:
                raise OracleError("cannot start replay: %s" % e)
        finally:
            try:
                os.remove(path)
            except OSError:
                pass
        if p.returncode not in (0, 1):
            raise OracleError("replay exited with %d: %s" % (p.returncode, (p.stdout + p.stderr).strip()[-300:]))
        result = {}
        viol = []
        for line in p.stdout.splitlines():
            line = line.strip()
            if line.startswith("VIOLATION "):           # VIOLATION <rule-name> <detail>
                parts = line.split(None, 2)
                viol.append(parts[1] + (" " + parts[2] if len(parts) > 2 else ""))
                result.setdefault("invariant", parts[1])
        for line in reversed(p.stdout.splitlines()):
            line = line.strip()
            if line.startswith("{"):
                try:
                    result = dict(json.loads(line), **{k: v for k, v in result.items() if k == "invariant"})
                except ValueError:
                    pass
                break
        if viol and not result.get("violations"):
            result["violations"] = viol
        if p.returncode == 1:
            result["diverged"] = True
        else:
            result["diverged"] = False
        return result


class PyOracle:
    """Chama uma função Python "module:function" com o dicionário de dados de teste. Retorna {"diverged": bool, ...}, como no contrato de comando.
    `path` é acrescentado primeiro ao caminho de importação (python -I não pesquisa a pasta atual)."""

    def __init__(self, spec, path=None):
        if ":" not in spec:
            raise OracleError("a replay function is written module:function")
        mod, fn = spec.split(":", 1)
        if path:
            sys.path.insert(0, os.path.abspath(path))
        try:
            self.fn = getattr(importlib.import_module(mod), fn)
        except (ImportError, AttributeError) as e:
            raise OracleError("cannot load %s: %s" % (spec, e))
        self.runs = 0

    def __call__(self, fixture):
        self.runs += 1
        try:
            result = self.fn(json.loads(json.dumps(fixture)))
        except Exception as e:   # um hook que falha com dados de teste inválidos é tratado como dados de teste inválidos
            raise OracleError("the replay function raised %s: %s" % (type(e).__name__, e))
        if not isinstance(result, dict) or "diverged" not in result:
            raise OracleError("the replay function must return a dict with a 'diverged' key")
        return result


# ---------------------------------------------------------------- dados de teste a partir de registros

def fixture_from_traces(traces, config=None):
    """Transforma registros gravados em dados de teste de reprodução: cada datagrama recebido por cada máquina vira uma
    etapa deliver, ordenada pelo tempo alinhado e seguida de uma etapa quiesce fixada."""
    a = A.align(traces)
    items = []
    skipped = 0
    for s in a.slots:
        for r in a.traces[s]["records"]:
            if r.get("malformed"):
                continue
            t = a.t(s, r)
            if r["type"] == C.T_NET_IN:
                if r["truncated"] or not r["raw"]:
                    skipped += 1
                    continue
                items.append((t, s, r["idx"], {"op": "deliver", "to": s, "from": r["peer"], "hex": r["raw"].hex()}))
    items.sort(key=lambda x: (x[0], x[1], x[2]))
    t0 = items[0][0] if items else 0
    steps = []
    for t, _, _, st in items:
        st["t"] = int((t - t0) / 1000)
        steps.append(st)
    steps.append({"op": "quiesce", "pin": True})
    cfg = {"seed": 1, "clients": max(1, len(a.slots) - 1)}
    cfg.update(config or {})
    return {"version": 1, "config": cfg, "steps": steps, "source": {"slots": a.slots, "skipped_steps": skipped}}


# ---------------------------------------------------------------- ddmin

def ddmin(count, fails, max_runs=5000, deadline=None):
    """ddmin sobre índices de itens 0..count-1. fails(list_of_indices) -> True se a falha persistir.
    Retorna (kept_indices, runs, complete); complete é False se um orçamento interromper antes do fim."""
    runs = [0]
    cache = {}

    def test(idx):
        key = tuple(idx)
        if key in cache:
            return cache[key]
        if runs[0] >= max_runs or (deadline is not None and time.time() > deadline):
            raise _Budget()
        runs[0] += 1
        cache[key] = bool(fails(list(idx)))
        return cache[key]

    cur = list(range(count))
    n = 2
    complete = True
    try:
        if count and test([]):
            return [], runs[0], True
        while len(cur) >= 2:
            size = max(1, len(cur) // n)
            chunks = [cur[i:i + size] for i in range(0, len(cur), size)]
            reduced = False
            for ch in chunks:
                if len(ch) < len(cur) and test(ch):
                    cur, n, reduced = ch, 2, True
                    break
            if not reduced:
                for ch in chunks:
                    comp = [x for x in cur if x not in set(ch)]
                    if comp and len(comp) < len(cur) and test(comp):
                        cur, n, reduced = comp, max(n - 1, 2), True
                        break
            if not reduced:
                if n >= len(cur):
                    break
                n = min(len(cur), n * 2)
    except _Budget:
        complete = False
    return cur, runs[0], complete


class _Budget(Exception):
    pass


def list_key_of(fixture, list_key=None):
    if list_key:
        if list_key not in fixture:
            raise OracleError("the fixture has no list called %r" % list_key)
        return list_key
    return "ops" if "ops" in fixture and "steps" not in fixture else "steps"


def shrink_fixture(fixture, oracle, max_runs=2000, max_seconds=None, list_key=None):
    "Reduz fixture[list_key] a uma lista (1-)mínima que ainda falha com a mesma assinatura."
    key = list_key_of(fixture, list_key)
    steps = fixture[key]
    pinned = [i for i, s in enumerate(steps) if s.get("pin")]
    free = [i for i in range(len(steps)) if i not in set(pinned)]
    base = oracle(fixture)
    sig = signature(base)
    if sig is None:
        raise OracleError("the original fixture does not diverge; nothing to shrink")

    def build(sel):
        keep = sorted(set(pinned) | {free[j] for j in sel})
        f = dict(fixture)
        f[key] = [steps[i] for i in keep]
        return f

    def fails(sel):
        r = oracle(build(sel))
        return r.get("diverged") and signature(r) == sig

    deadline = time.time() + max_seconds if max_seconds else None
    kept, runs, complete = ddmin(len(free), fails, max_runs=max_runs, deadline=deadline)
    out = build(kept)
    final = oracle(out)
    out["shrunk"] = {"signature": sig, "original_steps": len(steps), "reduced_steps": len(out[key]), "list_key": key,
                     "oracle_runs": runs + 2, "complete": complete, "first": final.get("first"),
                     "violations": final.get("violations", [])[:5]}
    return out
