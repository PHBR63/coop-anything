"""Executa uma tabela de variantes de mutação: cada variante deve fazer o teste indicado para ela falhar.

    python -I tools/mutants/run_twins.py TABLE.json [--jobs N] [--only NAME ...] [--verbose] [--json FILE] [--list]

Uma variante é uma versão deliberadamente defeituosa do código, ativada em execução pela variável de ambiente COOP_MUT (veja
coop_mut.h e coop_mut.py). A tabela indica qual teste deve falhar para qual variante. O executor:

  1. compila uma vez (comando "build" opcional),
  2. executa cada teste SEM variante: todos devem passar,
  3. executa os testes indicados COM cada variante: pelo menos um deve falhar ("capturada"),
  4. imprime uma linha por variante e ALL OK na última linha somente quando todas foram capturadas e não há outro problema.

Tabela (JSON, caminhos relativos ao arquivo da tabela, salvo se absolutos):

    {
      "label": "my suite",
      "cmd": ["build/my_tests.exe", "{test}"],      comando; {test} {twin} {dir} são substituídos em cada argumento
      "env_var": "COOP_MUT",                          padrão COOP_MUT
      "build": ["python", "build.py"],                opcional, executado uma vez antes de tudo
      "twin_build": ["python", "build.py"],           opcional, executado para cada variante (variantes de compilação). {twin} é substituído
      "real_regex": ", 0 failed",                     opcional: uma execução real também deve imprimir isto
      "caught_regex": ", [1-9][0-9]* failed",         opcional: uma variante capturada também deve imprimir isto (logo, um travamento não é "capturado")
      "timeout_s": 300, "jobs": 2, "cwd": ".",
      "scan": ["src/**/*.cpp", "py/*.py"],            opcional: confere as fontes com a tabela (veja abaixo)
      "tests": ["test_add", "test_even"],             opcional: todos os testes; o padrão é todo teste indicado por uma variante
      "twins": {"add_wrong_operator": "test_add",     nome da variante -> teste que deve falhar
                "skip_even_check": ["test_even", "test_range"]}    lista: pelo menos um deve falhar
    }

"twins" também pode ser uma lista de objetos {"name", "test" (string ou lista), "mut" (valor de COOP_MUT, padrão: nome), "cmd", "build"}.
Sem {test} em "cmd", o programa inteiro executa uma vez por variante e os nomes dos testes são apenas rótulos.

O que conta como capturada: código de saída diferente de zero que não seja erro de carregamento (DLL ausente, imagem inválida), e correspondência
com "caught_regex", se fornecida. Um bloqueio além de timeout_s conta como captura (a execução real não bloqueia).

Falhas, cada uma impressa e fazendo o código de saída ser 1:
  MISSED        o teste indicado passou com a variante ativada: ele não prova nada sobre esse código, ou a variante não está conectada
  WRONG TEST    o teste indicado passou, mas outro falhou: a variante quebra outra coisa; corrija a tabela ou o teste
  BUILD CRASH   falhou a compilação de uma variante de compilação: a variante deve compilar e depois falhar no teste
  UNLISTED / STALE (com "scan")  um nome de variante usado nas fontes não consta na tabela, ou uma linha da tabela não tem ponto de chamada

Códigos de saída: 0 todas capturadas, 1 uma variante escapou ou a execução real ou compilação falhou, 2 a tabela está errada.
"""
import argparse
import glob
import json
import os
import re
import shlex
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

LOADER_ERRORS = {127, 0xC0000135, 0xC0000139, 0xC000007B, 0xC0000142}  # não encontrado, ponto de entrada, imagem inválida, falha na inicialização de DLL
TAIL = 6

CPP_SITE = re.compile(r"COOP_MUT_IF\(\s*(?:\"([^\"]+)\"|(\d+))\s*\)")
PY_SITE = re.compile(r"\bmut\(\s*(?:([\"'])([^\"']+)\1|(\d+))\s*\)")


class TableError(Exception):
    pass


# ------------------------------------------------------------------------------------------------ tabela
def _as_cmd(v, what):
    if v is None:
        return None
    if isinstance(v, str):
        return shlex.split(v, posix=(os.name != "nt"))
    if isinstance(v, list) and v and all(isinstance(x, str) for x in v):
        return list(v)
    raise TableError(f"{what} must be a non-empty list of strings (or one string)")


def _as_tests(v, what):
    if isinstance(v, str):
        return [v]
    if isinstance(v, list) and v and all(isinstance(x, str) and x for x in v):
        return list(v)
    raise TableError(f"{what}: the test must be a name or a non-empty list of names")


def load_table(src, base=None):
    "Lê e verifica uma tabela (caminho ou dict). Retorna um dict normalizado. Lança TableError."
    if isinstance(src, (str, Path)):
        p = Path(src)
        try:
            raw = json.loads(p.read_text(encoding="utf-8"))
        except OSError as e:
            raise TableError(f"cannot read {p}: {e}")
        except ValueError as e:
            raise TableError(f"{p} is not valid JSON: {e}")
        base = p.resolve().parent
    else:
        raw = dict(src)
        base = Path(base or os.getcwd()).resolve()
    if not isinstance(raw, dict):
        raise TableError("the table must be a JSON object")
    known = {"label", "cmd", "env_var", "build", "twin_build", "real_regex", "caught_regex", "timeout_s", "jobs", "cwd",
             "scan", "tests", "twins"}
    unknown = [k for k in raw if k not in known and not k.startswith("_")]
    if unknown:
        raise TableError(f"unknown table keys: {unknown}")
    t = {"label": str(raw.get("label") or "twins"), "env_var": str(raw.get("env_var") or "COOP_MUT"),
         "cmd": _as_cmd(raw.get("cmd"), "cmd"), "build": _as_cmd(raw.get("build"), "build"),
         "twin_build": _as_cmd(raw.get("twin_build"), "twin_build"), "real_regex": raw.get("real_regex"),
         "caught_regex": raw.get("caught_regex"), "timeout_s": float(raw.get("timeout_s", 300)),
         "jobs": int(raw.get("jobs", 2)), "base": base, "cwd": str((base / raw.get("cwd", ".")).resolve()),
         "scan": list(raw.get("scan") or [])}
    if not t["cmd"]:
        raise TableError("the table needs a 'cmd'")
    for rx in ("real_regex", "caught_regex"):
        if t[rx]:
            try:
                re.compile(t[rx])
            except re.error as e:
                raise TableError(f"{rx}: {e}")
    twins_raw = raw.get("twins")
    items = []
    if isinstance(twins_raw, dict):
        items = [{"name": k, "test": v} for k, v in twins_raw.items()]
    elif isinstance(twins_raw, list):
        items = list(twins_raw)
    if not items:
        raise TableError("the table needs at least one twin")
    twins, seen = [], set()
    for it in items:
        if not isinstance(it, dict) or "name" not in it:
            raise TableError(f"a twin entry needs a name: {it!r}")
        name = str(it["name"])
        if not name or any(c.isspace() for c in name):
            raise TableError(f"twin name {name!r} must be non-empty text without spaces")
        if name in seen:
            raise TableError(f"twin {name!r} is listed twice")
        seen.add(name)
        tests = _as_tests(it.get("test", "*"), f"twin {name}") if "test" in it else ["*"]
        twins.append({"name": name, "mut": str(it.get("mut", name)), "tests": tests, "cmd": _as_cmd(it.get("cmd"), f"twin {name} cmd"),
                      "build": _as_cmd(it.get("build"), f"twin {name} build")})
    t["twins"] = twins
    uses_test = any("{test}" in a for a in t["cmd"]) or any(tw["cmd"] and any("{test}" in a for a in tw["cmd"]) for tw in twins)
    if uses_test:
        if any("*" in tw["tests"] for tw in twins):
            raise TableError("the command uses {test}: every twin needs a 'test'")
        named = []
        for tw in twins:
            for x in tw["tests"]:
                if x not in named:
                    named.append(x)
        tests = list(raw["tests"]) if raw.get("tests") else named
        missing = [x for x in named if x not in tests]
        if missing:
            raise TableError(f"tests named by twins but missing from 'tests': {missing}")
        t["tests"] = tests
    else:
        t["tests"] = ["*"]
        for tw in twins:                   # sem {test} no comando: os nomes são apenas rótulos e o programa executa uma vez
            tw["labels"] = tw["tests"]
            tw["tests"] = ["*"]
    for tw in twins:
        tw.setdefault("labels", tw["tests"])
    return t


# ------------------------------------------------------------------------------------------------ execução
def clean_env(var):
    env = dict(os.environ)
    env.pop(var, None)
    return env


def expand(argv, test, twin, table):
    out = []
    for a in argv:
        out.append(a.replace("{test}", test).replace("{twin}", twin).replace("{dir}", str(table["base"])))
    return out


def _resolve_exe(argv, cwd):
    "CreateProcess não resolve de forma confiável um caminho relativo de programa em relação ao nosso cwd: torna absoluto um caminho existente."
    if argv and ("/" in argv[0] or "\\" in argv[0]):
        cand = Path(argv[0])
        if not cand.is_absolute():
            cand = Path(cwd) / cand
        if cand.exists():
            argv = [str(cand.resolve())] + argv[1:]
    return argv


def run_proc(argv, env, timeout, cwd):
    """(returncode, output, timed_out)."""
    argv = _resolve_exe(argv, cwd)
    try:
        p = subprocess.run(argv, capture_output=True, text=True, errors="replace", env=env, timeout=timeout, cwd=cwd)
    except FileNotFoundError:
        return 127, "program not found: " + argv[0], False
    except subprocess.TimeoutExpired:
        return 1, "timeout", True
    return p.returncode, (p.stdout or "") + (p.stderr or ""), False


def tail(text, n=TAIL):
    return "\n    ".join(text.rstrip().splitlines()[-n:])


def run_build(table, argv, twin=None, mut=None):
    "Executa um comando de compilação. Com uma variante, a variável de ambiente informa seu nome para incluí-la na compilação."
    env = clean_env(table["env_var"])
    if twin is not None:
        env[table["env_var"]] = mut
    argv = expand(argv, "*", twin or "", table)
    rc, out, _ = run_proc(argv, env, table["timeout_s"] * 4, table["cwd"])
    return rc, out


def is_caught(rc, out, timed_out, caught_regex):
    "Uma execução malsucedida do teste conta como variante capturada; erro de carregamento ou travamento sem o texto esperado não conta."
    if timed_out:
        return True
    if rc == 0 or (rc & 0xFFFFFFFF) in LOADER_ERRORS:
        return False
    if caught_regex and not re.search(caught_regex, out):
        return False
    return True


def run_test(table, twin_cmd, test, mut):
    "Executa um teste com a variante `mut` ativada, ou desativada quando mut é None."
    env = clean_env(table["env_var"])
    if mut is not None:
        env[table["env_var"]] = mut
    argv = expand(twin_cmd or table["cmd"], test, mut or "", table)
    return run_proc(argv, env, table["timeout_s"], table["cwd"])


def run_real(table):
    "Todo teste sem variante. Retorna (ok, lines)."
    lines = []
    for test in table["tests"]:
        rc, out, to = run_test(table, None, test, None)
        if rc != 0 or to:
            lines.append(f"REAL RUN FAILED: test {test!r} exit {rc}{' (timeout)' if to else ''}\n    {tail(out)}")
        elif table["real_regex"] and not re.search(table["real_regex"], out):
            lines.append(f"REAL RUN: test {test!r} exited 0 but its output does not match {table['real_regex']!r}\n    {tail(out)}")
    return not lines, lines


def find_broken_tests(table, tw, skip):
    "Com a variante ativada, quais outros testes falham? Usado para indicar que uma variante quebrou o teste errado."
    broken = []
    for test in table["tests"]:
        if test in skip or test == "*":
            continue
        rc, out, to = run_test(table, tw["cmd"], test, tw["mut"])
        if is_caught(rc, out, to, table["caught_regex"]):
            broken.append(test)
    return broken


def run_twin(table, tw):
    """-> dict(name, status, detail). status: caught, missed, wrong_test, build_crash."""
    res = {"name": tw["name"], "status": "missed", "detail": "", "tests": tw["labels"]}
    names = ", ".join(tw["labels"])
    build = tw["build"] or table["twin_build"]
    if build:
        rc, out = run_build(table, build, tw["name"], tw["mut"])
        if rc != 0:
            res.update(status="build_crash", detail=f"build exited {rc}\n    {tail(out)}")
            return res
    last = ""
    for test in tw["tests"]:
        rc, out, to = run_test(table, tw["cmd"], test, tw["mut"])
        last = out
        if is_caught(rc, out, to, table["caught_regex"]):
            res.update(status="caught", detail=f"test {names}: " + ("timeout" if to else f"exit {rc}"))
            return res
    other = find_broken_tests(table, tw, set(tw["tests"]))
    if other:
        res.update(status="wrong_test", detail=f"{names} passed, but {', '.join(other)} failed")
    else:
        res.update(status="missed", detail=f"{', '.join(tw['tests'])} passed with {table['env_var']}={tw['mut']}\n    {tail(last)}")
    return res


# ------------------------------------------------------------------------------------------------ varredura
def scan_sites(table):
    "Nomes de variantes usados nas fontes indicadas por 'scan'. Retorna (names, files_seen)."
    names, seen = set(), 0
    for pat in table["scan"]:
        full = pat if os.path.isabs(pat) else str(Path(table["base"]) / pat)
        for f in glob.glob(full, recursive=True):
            fp = Path(f)
            if not fp.is_file():
                continue
            seen += 1
            text = fp.read_text(encoding="utf-8", errors="replace")
            for m in CPP_SITE.finditer(text):
                names.add(m.group(1) or m.group(2))
            if fp.suffix == ".py":
                for m in PY_SITE.finditer(text):
                    names.add(m.group(2) or m.group(3))
    return names, seen


def scan_problems(table):
    if not table["scan"]:
        return []
    names, seen = scan_sites(table)
    if not seen:
        return [f"SCAN: no source file matches {table['scan']}"]
    listed = {tw["mut"] for tw in table["twins"]}
    probs = [f"UNLISTED: twin {n!r} is used in the sources but is not in the table (it is never run)" for n in sorted(names - listed)]
    probs += [f"STALE: twin {n!r} is in the table but no call site uses it" for n in sorted(listed - names)]
    return probs


def restore_build(table, say):
    "Após variantes de compilação: compila novamente sem variante para deixar a árvore com o código real. True se funcionar."
    if not table["build"]:
        return True
    rc, bout = run_build(table, table["build"])
    if rc != 0:
        say(f"{table['label']}: the rebuild without a twin failed (exit {rc})\n    {tail(bout)}")
        return False
    return True


def all_ok(results, real_ok, build_ok, problems):
    return real_ok and build_ok and not problems and all(r["status"] == "caught" for r in results)


# ------------------------------------------------------------------------------------------------ controlador
def run_table(table, jobs=None, only=None, verbose=False, json_path=None, out=None):
    "Executa tudo. Retorna o código de saída (0 ou 1). Imprime em `out` (padrão stdout)."
    out = out or sys.stdout

    def say(s=""):
        print(s, file=out, flush=True)

    label = table["label"]
    twins = [tw for tw in table["twins"] if not only or tw["name"] in only]
    if only and len(twins) != len(set(only)):
        missing = sorted(set(only) - {tw["name"] for tw in table["twins"]})
        say(f"{label}: no such twin: {missing}")
        return 2
    problems = scan_problems(table)
    for p in problems:
        say(p)
    build_ok = True
    if table["build"]:
        rc, bout = run_build(table, table["build"])
        if rc != 0:
            say(f"{label}: BUILD FAILED (exit {rc})\n    {tail(bout)}")
            build_ok = False
    report = {"label": label, "real": None, "twins": [], "scan_problems": problems}
    if not build_ok:
        report["ok"] = False
        _write_json(json_path, report)
        return 1
    real_ok, real_lines = run_real(table)
    for ln in real_lines:
        say(ln)
    report["real"] = real_ok
    if not real_ok:
        say(f"{label}: the real run fails, so no twin result can be trusted")
        report["ok"] = False
        _write_json(json_path, report)
        return 1
    serial = bool(table["twin_build"] or any(tw["build"] for tw in twins))
    workers = 1 if serial else max(1, jobs or table["jobs"])
    results = []
    try:
        with ThreadPoolExecutor(max_workers=workers) as ex:
            for r in ex.map(lambda tw: run_twin(table, tw), twins):
                results.append(r)
                _print_result(say, r, verbose)
    finally:
        if serial and not restore_build(table, say):
            build_ok = False
    report["twins"] = results
    ok = all_ok(results, real_ok, build_ok, problems)
    report["ok"] = ok
    _write_json(json_path, report)
    bad = [r for r in results if r["status"] != "caught"]
    if ok:
        say(f"{label}: real tests pass, all {len(results)} twins caught - ALL OK")
        return 0
    parts = []
    if bad:
        parts.append(f"{len(bad)} of {len(results)} twin(s) not caught: {[r['name'] for r in bad]}")
    if problems:
        parts.append(f"{len(problems)} table/source problem(s)")
    if not build_ok:
        parts.append("the final rebuild failed")
    say(f"{label}: " + "; ".join(parts or ["failed"]))
    return 1


def _print_result(say, r, verbose):
    s = r["status"]
    if s == "caught":
        if verbose:
            say(f"  twin {r['name']}: caught ({r['detail']})")
    elif s == "missed":
        say(f"MISSED: twin {r['name']}: {r['detail']}")
    elif s == "wrong_test":
        say(f"WRONG TEST: twin {r['name']}: {r['detail']}")
    else:
        say(f"BUILD CRASH: twin {r['name']}: {r['detail']}")


def _write_json(path, report):
    if path:
        Path(path).write_text(json.dumps(report, indent=1, default=str), encoding="utf-8")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("table")
    ap.add_argument("--jobs", type=int, default=None)
    ap.add_argument("--only", nargs="+")
    ap.add_argument("--verbose", action="store_true")
    ap.add_argument("--json", dest="json_path")
    ap.add_argument("--list", action="store_true", help="imprime as variantes e seus testes, sem executar nada")
    a = ap.parse_args(argv)
    try:
        table = load_table(a.table)
    except TableError as e:
        print(f"table error: {e}", file=sys.stderr)
        return 2
    if a.list:
        for tw in table["twins"]:
            print(f"{tw['name']}\t{','.join(tw['tests'])}")
        return 0
    return run_table(table, a.jobs, set(a.only) if a.only else None, a.verbose, a.json_path)


if __name__ == "__main__":
    sys.exit(main())
