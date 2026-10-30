#!/usr/bin/env python3
"""Linha de comando de cenários.

    python -I tools/scenarios/scen.py list [DIR]
    python -I tools/scenarios/scen.py validate [FILE_OR_NAME ...]        sem jogo; sai com código 1 diante de qualquer erro
    python -I tools/scenarios/scen.py validate ... --index ids.json      também verifica cada id no arquivo de índice dos dados do jogo
                                                                         ({"id": "kind"}, kind é um dos tipos de objeto ou null)
    python -I tools/scenarios/scen.py validate ... --adapter pkg.mod:factory   o mesmo, com data_index() do adaptador
    python -I tools/scenarios/scen.py plan NAME [--prev NAME]            mostra a decisão do salto (recarregar ou ajustar no local), sem jogo
    python -I tools/scenarios/scen.py run NAME ... --fake                simulação no jogo em memória (sem jogo real)
    python -I tools/scenarios/scen.py run NAME ... --adapter pkg.mod:factory [--players N] [--instances 2,3] [--prepared FILE]
                                                                         executa no seu jogo; factory(i) retorna o GameAdapter
                                                                         da instância i. A ferramenta nunca inicia o jogo por conta própria.
                                                                         --instances fornece os ids entregues à fábrica (padrão
                                                                         0..N-1); --prepared é o manifesto de salvamentos preparados
                                                                         por prepare_save.py (consulte essa ferramenta).

NAME é o nome do arquivo sem .json, procurado na pasta examples (ou na pasta passada com --dir).
"""
import argparse
import importlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import scenlib  # noqa: E402
import runner  # noqa: E402


def _paths(names, directory):
    if not names:
        return scenlib.list_scenarios(directory)
    out = []
    for n in names:
        p = Path(n)
        if p.suffix == ".json":
            out.append(p)
        else:
            hits = sorted(Path(directory).rglob(n + ".json"))
            out.append(hits[0] if hits else Path(directory) / (n + ".json"))
    return out


def cmd_list(a):
    for p in scenlib.list_scenarios(a.dir):
        sc = scenlib.load_scenario(p)
        print("%-24s players=%d  %s" % (sc["name"], scenlib.players_of(sc), sc["title"]))
    return 0


def _factory(spec):
    sys.path.insert(0, str(Path.cwd()))
    mod, _, fn = spec.partition(":")
    return getattr(importlib.import_module(mod), fn)


def _ids(text, n):
    return [int(x) for x in text.split(",") if x.strip()] if text else list(range(n))


def cmd_validate(a):
    paths = _paths(a.names, a.dir)
    hooks = []
    if a.index:
        hooks.append(scenlib.index_hook(json.loads(Path(a.index).read_text(encoding="utf-8"))))
    elif a.adapter:
        idx = _factory(a.adapter)(0).data_index()
        if idx is None:
            print("note: ids were not checked against the game data: the adapter provides no data_index()")
        else:
            hooks.append(scenlib.index_hook(idx))
    bad = 0
    for p in paths:
        errs = scenlib.validate_file(p, hooks=hooks)
        print("%s %s" % ("FAIL" if errs else "ok  ", p.name))
        for e in errs:
            print("    " + e)
        bad += bool(errs)
    print("%d scenario file(s) checked, %d invalid" % (len(paths), bad))
    return 1 if bad else 0


def cmd_plan(a):
    sc = scenlib.load_scenario(_paths([a.name], a.dir)[0])
    state = {"loaded": False}
    if a.prev:
        pv = scenlib.load_scenario(_paths([a.prev], a.dir)[0])
        state = {"loaded": True, "save": pv["start"]["save"], "dirty": sorted(scenlib.footprint(pv)["dirty"]), "failed": False}
    print(json.dumps(scenlib.plan_jump(state, sc), indent=1))
    print("state keys reset in place:", " ".join(scenlib.reset_ids(sc)) or "(none)")
    return 0


def cmd_run(a):
    scs = [scenlib.load_scenario(p) for p in _paths(a.names, a.dir)]
    ids = _ids(a.instances, a.players or max(scenlib.players_of(s) for s in scs))
    n = len(ids)
    if a.fake:
        import fakegame
        w, clock, games = fakegame.make(n)
        rn = runner.Runner(games, runner.StateStore(), sleep=clock.sleep, now=clock.now)
        for s in scs:
            w.load_scenario(s)
    elif a.adapter:
        factory = _factory(a.adapter)
        import prepare_save
        rn = runner.Runner([factory(i) for i in ids], runner.StateStore(a.state), instances=ids,
                           prepared=prepare_save.PreparedSaves(a.prepared) if a.prepared else None)
    else:
        print("run needs --fake or --adapter pkg.mod:factory")
        return 2
    results = [rn.run(s, a.force_reload) for s in scs if scenlib.players_of(s) <= n]
    print(runner.summarize(results))
    if a.json:
        Path(a.json).parent.mkdir(parents=True, exist_ok=True)
        Path(a.json).write_text(json.dumps(results, indent=1), encoding="utf-8")
    return 0 if results and all(r["status"] == "pass" for r in results) else 1


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dir", default=str(scenlib.SCEN_DIR), help="pasta com arquivos de cenário (padrão: exemplos distribuídos)")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("list").set_defaults(fn=cmd_list)
    p = sub.add_parser("validate")
    p.add_argument("names", nargs="*")
    p.add_argument("--index", help="arquivo JSON {id: kind} dos identificadores conhecidos pelos dados do jogo")
    p.add_argument("--adapter", help="pkg.mod:factory; usa seu data_index() (o adaptador é criado para a instância 0)")
    p.set_defaults(fn=cmd_validate)
    p = sub.add_parser("plan")
    p.add_argument("name")
    p.add_argument("--prev")
    p.set_defaults(fn=cmd_plan)
    p = sub.add_parser("run")
    p.add_argument("names", nargs="*")
    p.add_argument("--fake", action="store_true")
    p.add_argument("--adapter")
    p.add_argument("--players", type=int, default=0)
    p.add_argument("--instances", default="", help="identificadores de instância entregues à fábrica do adaptador, por exemplo 2,3 (padrão 0..players-1)")
    p.add_argument("--prepared", help="arquivo de manifesto de salvamentos preparados (padrão $SCEN_PREPARED_FILE ou ./scen_prepared.json, quando existir)")
    p.add_argument("--state", help="arquivo que guarda o que está carregado entre execuções")
    p.add_argument("--json")
    p.add_argument("--force-reload", action="store_true")
    p.set_defaults(fn=cmd_run)
    a = ap.parse_args(argv)
    return a.fn(a)


if __name__ == "__main__":
    sys.exit(main())
