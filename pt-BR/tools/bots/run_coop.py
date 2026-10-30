#!/usr/bin/env python3
"""Executa roteiros cooperativos com vários bots.

Sem jogo (o mundo cooperativo simulado; é o que os testes usam):
    python -I tools/bots/run_coop.py --list
    python -I tools/bots/run_coop.py --fake --playbook all
    python -I tools/bots/run_coop.py --fake --playbook loot_race --players 3 --bug dup_pickup      # deve FALHAR
    python -I tools/bots/run_coop.py --fake --playbook loot_race --link bad_wifi                   # enlace com perdas, janelas sem tráfego
    python -I tools/bots/run_coop.py --fake --playbook fight --from-step 4 --timescale 3           # retoma na etapa 4, jogo em 3x

No seu jogo (você inicia as instâncias e as conecta a uma sessão; esta ferramenta nunca inicia um jogo):
    python -I tools/bots/run_coop.py --adapter my_game:make_adapter --players 2 \\
        --scenario my_scenarios/fight.json --playbook fight

`make_adapter(i)` retorna o ActionAdapter da instância i (0 é o host). Com `--instances 2,3`, a fábrica recebe esses números
de instância, sendo o primeiro o host (é assim que tools/bots/run_parallel.py inicia um executor por par). `--scenario` é um arquivo de cenário cujo bloco `refs`
nomeia o que o roteiro precisa; `--refs file.json` fornece o mesmo como JSON simples.

Após cada etapa, o executor verifica se todas as máquinas convergiram, se as capturas compartilhadas são iguais e se os contadores de
dessincronização não aumentaram. Uma etapa malsucedida escreve FAIL-<n>-<step>/ (failure.json, capturas de estado, captura do adaptador) no diretório
de saída. Código de saída: 0 pelo menos uma aprovação e nenhuma falha, 1 roteiro falhou ou nada passou, 2 erro de uso ou configuração.
SKIP significa que falta ao adaptador uma ação necessária ao roteiro; pular nunca equivale a passar.

Rodadas rápidas. Uma etapa malsucedida imprime seu número. `--from-step N` executa a etapa N e seguintes, `--only-step N` apenas N; a primeira etapa
executada prepara o mundo esperado (veja `ctx.run_step` em coopbots/core.py), então não é preciso recarregar. Apenas roteiros cujas
etapas tenham preparação suportam isso (`--list` os marca). `--timescale X` chama set_timescale(X) do adaptador antes da
primeira etapa e set_timescale(1) ao final, inclusive após falha. `--settle-stall S` é quanto uma espera por sincronização pode ficar sem progresso
antes de falhar com o motivo (0 desativa a parada antecipada; o padrão é max(6, budget / 4) segundos).
"""
import argparse
import importlib
import json
import os
import sys
import time
from typing import Any, Dict, List

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

from coopbots import core, fakecoop, links, refs as refs_mod, registry  # noqa: E402


def log(s: str) -> None:
    print(s, flush=True)


def run_fake(names: List[str], players: int, bugs: set, outroot: str, opts: dict, loss: int, ids: List[int]) -> List[core.RunResult]:
    results = []
    for name in names:
        e = registry.REGISTRY[name]
        world, refs = e.fake(len(ids) or players or e.players, bugs, loss_every=loss)
        o = {"fast": True, "ui_s": 0.3, "barrier_s": 0.3, "stage_s": 0.3, "handoff_s": 0.3, "spawn_s": 0.3, "settle_s": 1.0, "settle_poll_s": 0.0}
        o.update(opts)
        machines = fakecoop.make_machines(world)
        for m, i in zip(machines, ids):
            m.instance = i
        results.append(core.run_playbook(registry.make(name), machines, fakecoop.FakeComparer(),
                                         os.path.join(outroot, name), refs, o, log))
    return results


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--list", action="store_true", help="lista roteiros e sai")
    ap.add_argument("--playbook", default="", help="nome, lista separada por vírgulas ou 'all'")
    ap.add_argument("--players", type=int, default=0, help="número de bots (padrão: o próprio padrão do roteiro)")
    ap.add_argument("--fake", action="store_true", help="execução sem jogo no mundo cooperativo simulado")
    ap.add_argument("--bug", action="append", default=[], help="(simulação) ativa um erro deliberado; a execução deve então falhar")
    ap.add_argument("--adapter", default="", help="pkg.module:factory, factory(i) -> ActionAdapter da instância i")
    ap.add_argument("--scenario", default="", help="JSON de cenário cujo bloco `refs` nomeia os objetos do roteiro")
    ap.add_argument("--refs", default="", help="arquivo JSON com as referências, em vez de --scenario")
    ap.add_argument("--link", default="", help="link profile: " + ", ".join(links.PROFILES))
    ap.add_argument("--profiles", default="", help="arquivo de perfis para orçamentos de reparo (padrão: tools/chaos/profiles.json)")
    ap.add_argument("--no-compare", action="store_true", help="pula a comparação de capturas de estado após cada etapa")
    ap.add_argument("--instances", default="", help="números das instâncias para a fábrica de adaptadores, por exemplo 2,3; a primeira é o host (padrão 0..N-1)")
    ap.add_argument("--from-step", type=int, default=0, help="executa a etapa N e seguintes (a primeira prepara o mundo); somente roteiros retomáveis")
    ap.add_argument("--only-step", type=int, default=0, help="executa apenas a etapa N (preparada primeiro); somente roteiros retomáveis")
    ap.add_argument("--timescale", type=float, default=1.0, help="multiplicador de velocidade do jogo definido pelo adaptador (set_timescale), restaurado ao final")
    ap.add_argument("--settle-stall", type=float, default=None, help="segundos sem progresso antes de uma espera por sincronização falhar antecipadamente (0 = nunca)")
    ap.add_argument("--outdir", default="")
    ap.add_argument("--keep-going", action="store_true", help="executa o próximo roteiro após uma falha")
    a = ap.parse_args(argv)

    if a.list:
        for n, e in registry.REGISTRY.items():
            pb = registry.make(n)
            print("%-28s %dp  %s needs refs: %-40s %s" % (n, e.players, "R" if pb.resumable else "-", ",".join(pb.needs_refs) or "-", pb.summary))
        print("R = steps can be resumed with --from-step / --only-step")
        return 0
    if not a.playbook:
        ap.error("--playbook is required (or --list)")
    names = list(registry.REGISTRY) if a.playbook == "all" else [x for x in a.playbook.split(",") if x]
    unknown = [n for n in names if n not in registry.REGISTRY]
    if unknown:
        print("unknown playbook(s) %s; use --list" % unknown, file=sys.stderr)
        return 2
    if not a.fake and not a.adapter:
        print("give --fake or --adapter pkg.module:factory", file=sys.stderr)
        return 2
    try:
        opts: Dict[str, Any] = links.link_options(a.link, a.profiles or links.default_profiles_path())
    except ValueError as ex:
        print(str(ex), file=sys.stderr)
        return 2
    outroot = a.outdir or os.path.join("coop-bots-out", time.strftime("%Y%m%dT%H%M%S"))
    if a.no_compare:
        opts["compare"] = False
    if a.from_step < 0 or a.only_step < 0 or a.timescale <= 0:
        print("--from-step and --only-step are 1 or more, --timescale is above 0", file=sys.stderr)
        return 2
    if a.from_step and a.only_step:
        print("give --from-step or --only-step, not both", file=sys.stderr)
        return 2
    if a.from_step > 1 or a.only_step:
        not_ok = [n for n in names if not registry.make(n).resumable]
        if not_ok:
            print("%s cannot run from a later step: no arrange part yet. Resumable: %s" % (", ".join(not_ok), ", ".join(sorted(
                n for n in registry.REGISTRY if registry.make(n).resumable))), file=sys.stderr)
            return 2
    opts.update(from_step=a.from_step, only_step=a.only_step, timescale=a.timescale)
    if a.settle_stall is not None:
        opts["settle_stall_s"] = a.settle_stall
    try:
        ids = [int(x) for x in a.instances.split(",") if x.strip() != ""]
    except ValueError:
        print("--instances needs numbers like 2,3", file=sys.stderr)
        return 2
    if ids and a.players and a.players != len(ids):
        print("--players %d does not match --instances %s" % (a.players, a.instances), file=sys.stderr)
        return 2

    os.makedirs(outroot, exist_ok=True)
    results: List[core.RunResult] = []
    if a.fake:
        results = run_fake(names, a.players, set(a.bug), outroot, opts, links.FAKE_LOSS_EVERY.get(a.link or "lan", 0), ids)
    else:
        sys.path.insert(0, os.getcwd())
        mod, _, fn = a.adapter.partition(":")
        factory = getattr(importlib.import_module(mod), fn)
        try:
            if a.scenario:
                refs = refs_mod.refs_from_scenario(a.scenario)
            elif a.refs:
                with open(a.refs, encoding="utf-8") as f:
                    refs = json.load(f)
            else:
                refs = {}
        except (OSError, ValueError, KeyError) as ex:
            print("cannot read the refs: %s" % ex, file=sys.stderr)
            return 2
        for name in names:
            e = registry.REGISTRY[name]
            n = len(ids) or a.players or e.players
            machines = [core.Machine(k, "host" if k == 0 else "client%d" % k, factory(ids[k] if ids else k), ids[k] if ids else k)
                        for k in range(n)]
            r = core.run_playbook(registry.make(name), machines, core.DictComparer(), os.path.join(outroot, name), refs, opts, log)
            results.append(r)
            if r.status == "fail" and not a.keep_going:
                break

    print()
    width = max([len(r.playbook) for r in results] + [8])
    for r in results:
        print("%-4s  %-*s  %d steps  %s" % (r.status.upper(), width, r.playbook, len(r.steps), r.reason))
        bad = next((s for s in r.steps if not s.ok), None)
        if bad is not None and bad.number:
            print("      rerun that step: --playbook %s --from-step %d   (or --only-step %d)" % (r.playbook, bad.number, bad.number)
                  if registry.make(r.playbook).resumable else "      failed at step %d (%s); this playbook runs whole" % (bad.number, bad.name))
    ok = any(r.status == "pass" for r in results) and not any(r.status == "fail" for r in results)
    with open(os.path.join(outroot, "summary.json"), "w", encoding="utf-8") as f:
        json.dump({"ok": ok, "link": a.link or None, "bugs": a.bug, "results": [r.to_json() for r in results]}, f, indent=1, default=str)
    print("summary: %s" % os.path.join(outroot, "summary.json"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
