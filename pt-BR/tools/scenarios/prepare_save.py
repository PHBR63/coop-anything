#!/usr/bin/env python3
"""Saves preparados: o save inicial do cenário com seus popups de carregamento já fechados, para um salto pulá-los.

Alguns jogos geram várias caixas de mensagem após carregar (save anterior aos complementos, avisos, tutoriais), ao longo de muitos
segundos. Uma caixa aberta pode manter o jogo em modo de menu, perdendo a entrada do teste. Feche-as uma vez, salve com um
nome de "pronto" em cada cópia e deixe o executor carregar esse save. O salto mantém a limpeza de popups como proteção, mas
espera apenas alguns segundos quando todas as cópias carregaram um save preparado.

    python -I tools/scenarios/prepare_save.py NAME [NAME ...] --adapter pkg.mod:factory [--instances 0,1]
    python -I tools/scenarios/prepare_save.py --save autosave --adapter pkg.mod:factory
    python -I tools/scenarios/prepare_save.py --status [NAME ...] [--adapter pkg.mod:factory] [--instances 0,1]

NAME é um nome de cenário (seu start.save será preparado). --adapter é o mesmo `pkg.mod:factory` aceito por scen.py: factory(i)
retorna o GameAdapter da instância i. --instances lista os IDs de instâncias passados à fábrica (padrão 0,1), por exemplo 2,3
para um segundo par de cópias. A ferramenta nunca inicia um jogo. Imprime uma linha JSON por save com `ok` true ou false e sai com 1 quando
os popups não cessam, uma cópia recusa salvar ou a verificação de recarregamento ainda mostra popup. Saída 2 indica problema de uso (sem adaptador,
ou adaptador sem ganchos de popup).

O adaptador fornece: popup_count(), dismiss_popup(), prepared_names(save), save_game(name) e, opcionalmente, save_exists(name)
e save_stamp(name) (veja gameadapter.py). Sem popup_count(), nada pode ser preparado e nada é salvo.

Onde ficam os fatos: um arquivo JSON (padrão ./scen_prepared.json, ou o caminho de $SCEN_PREPARED_FILE, ou --prepared FILE),
indexado por ID de instância e save inicial. Uma entrada informa qual nome de save foi escrito, se passou na verificação de recarregamento e a assinatura
do save-fonte. Um save preparado só é usado se o adaptador disser que o arquivo existe, a verificação passou e o
save-fonte não mudou desde então (saves em ROLLING_SAVES são exceção: o próprio jogo os reescreve).

Desativação: defina SCEN_NO_PREPARED=1 no ambiente, ou "start": {"prepared": false} em um arquivo de cenário.
"""
import argparse
import importlib
import json
import os
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

NO_PREPARED_ENV = "SCEN_NO_PREPARED"
MANIFEST_ENV = "SCEN_PREPARED_FILE"
DEFAULT_MANIFEST = "scen_prepared.json"
# somente teste (SCEN_MUTANT): "noverify" | "earlysave" | "nostale" | "unverified" | "posids"
MUTANT = os.environ.get("SCEN_MUTANT", "")
# Após carregar, a janela sem popups da limpeza: nenhum popup em nenhuma instância durante esse tempo. Um save comum pode gerar seus popups
# em ondas com intervalos longos, então espera mais. Um save preparado não gera nenhuma, portanto poucos segundos só protegem contra um aviso isolado.
PLAIN_QUIET_S = 20.0
PREPARED_QUIET_S = 4.0


def opted_out():
    return bool(os.environ.get(NO_PREPARED_ENV))


class PreparedSaves:
    "Qual instância tem uma cópia preparada utilizável de qual save inicial. Os fatos ficam em um arquivo JSON."

    def __init__(self, path=None):
        self.path = Path(path or os.environ.get(MANIFEST_ENV) or DEFAULT_MANIFEST)

    @classmethod
    def auto(cls):
        "O armazenamento padrão quando seu arquivo existe e a variável de desativação não está definida; caso contrário, None."
        if opted_out():
            return None
        s = cls()
        return s if s.path.is_file() else None

    def _read(self):
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            return {"instances": {}}
        if not isinstance(data, dict) or not isinstance(data.get("instances"), dict):
            return {"instances": {}}
        return data

    def record(self, inst, save, name, verified, popups, stamp):
        """Escreve a entrada de um save inicial em uma instância. `stamp` é a assinatura atual do save-fonte, então uma fonte
        substituída aparece como desatualizada depois."""
        data = self._read()
        data["instances"].setdefault(str(inst), {})[save] = {
            "name": name, "verified": bool(verified), "popups": popups, "at": round(time.time()), "source": stamp}
        self.path.parent.mkdir(parents=True, exist_ok=True)
        tmp = self.path.with_name(self.path.name + ".tmp")
        tmp.write_text(json.dumps(data, indent=1, sort_keys=True), encoding="utf-8")
        os.replace(tmp, self.path)

    def pick(self, inst, save, game=None):
        """-> (name, why). name é o save preparado a carregar nesta instância, ou None com o motivo de não usá-lo.
        `game` é o adaptador dessa instância: responde a save_exists e save_stamp. Sem ele, essas duas verificações são puladas."""
        e = (self._read()["instances"].get(str(inst)) or {}).get(save)
        if not e:
            return None, "no prepared save of %r on instance %s" % (save, inst)
        name = e.get("name")
        if not name:
            return None, "the manifest entry of %r has no save name" % save
        if game is not None and _try(game.save_exists, name) is False:
            return None, "prepared save %s is gone" % name
        if not e.get("verified") and MUTANT != "unverified":
            return None, "prepared save %s did not pass the reload check" % name
        src = e.get("source")
        rolling = [r.lower() for r in getattr(game, "ROLLING_SAVES", ())] if game is not None else []
        if src is not None and game is not None and save.lower() not in rolling and MUTANT != "nostale":
            now = _try(game.save_stamp, save)
            if now is not None and now != src:
                return None, "source save %r changed after %s was prepared" % (save, name)
        return name, "prepared save %s" % name

    def status(self, inst, save, game=None):
        name, why = self.pick(inst, save, game)
        return {"instance": inst, "save": save, "prepared": name, "why": why, "checked": game is not None}


class NoPopupHooks(RuntimeError):
    "Os adaptadores não informam popups, então não há nada a preparar."


def _try(fn, *args):
    "Gancho que pode faltar ou não saber responder: NotImplementedError e ScenarioError significam \"não sabe informar\" (None)."
    from gameadapter import ScenarioError
    try:
        return fn(*args)
    except (NotImplementedError, ScenarioError):
        return None


def prepare(games, save, store, instances=None, log=print, verify=True, quiet_s=PLAIN_QUIET_S, max_s=150.0, **runner_kw):
    """Faz a cópia preparada de `save` em cada adaptador: carrega, fecha popups até cessarem, salva o jogo sob o nome
    de pronto, depois (verificação) carrega o save pronto e confere se nenhum popup aparece. `store` é um PreparedSaves. `instances` contém os
    IDs de instâncias dos adaptadores (padrão 0..n-1). Retorna {"save", "ok", "popupsPressed", "perInstance": [...]}.
    Lança NoPopupHooks se os adaptadores não puderem informar popups e RuntimeError se os popups não cessarem (nada é salvo).
    runner_kw vai para runner.Runner (testes passam um relógio simulado)."""
    import runner
    ids = list(instances) if instances is not None else list(range(len(games)))
    rn = runner.Runner(games, runner.StateStore(), prepared=False, **runner_kw)
    for g in games:
        g.load_save(save)
    rn.sleep(rn.load_wait_s)
    boxes = {"pressed": 0, "quiet": True} if MUTANT == "earlysave" else rn.clear_popups(quiet_s=quiet_s, max_s=max_s)
    if boxes is None:
        raise NoPopupHooks("these instances cannot report popups (popup_count() gives None): nothing was saved. "
                           "Implement popup_count() and dismiss_popup() in the adapter")
    if not boxes.get("quiet"):
        raise RuntimeError("popups were still coming after %.0f s (%s pressed): nothing was saved" % (max_s, boxes.get("pressed")))
    out = []
    for k, g in enumerate(games):
        names = list(g.prepared_names(save))
        saved, err = None, None
        for name in names:
            try:
                g.save_game(name)
                saved = name
                break
            except Exception as e:   # noqa: BLE001 - the next name may be the one the engine takes
                err = "%s: %s" % (type(e).__name__, str(e)[:160])
        if saved is None:
            out.append({"instance": ids[k], "ok": False, "error": "save_game failed for %s (%s)" % (", ".join(names), err)})
        else:
            out.append({"instance": ids[k], "ok": True, "name": saved})
    if verify and MUTANT != "noverify":
        for k, g in enumerate(games):
            if out[k].get("ok"):
                g.load_save(out[k]["name"])
        rn.sleep(rn.load_wait_s)
        again = rn.clear_popups(quiet_s=PREPARED_QUIET_S, max_s=max_s) or {}
        clean = bool(again.get("quiet")) and not again.get("pressed")
        for k in range(len(games)):
            if out[k].get("ok"):
                out[k]["verified"] = clean
                if not clean:
                    out[k]["error"] = "a load of %s still raised %s popup(s)" % (out[k]["name"], again.get("pressed"))
    else:
        for r in out:
            r["verified"] = bool(r.get("ok"))
    for k, r in enumerate(out):
        if r.get("ok"):
            inst = k if MUTANT == "posids" else r["instance"]
            store.record(inst, save, r["name"], r["verified"], boxes.get("pressed"), _try(games[k].save_stamp, save))
    ok = all(r.get("ok") and r.get("verified") for r in out)
    log("prepared %r: %s" % (save, "ok" if ok else "FAILED " + json.dumps(out)))
    return {"save": save, "ok": ok, "popupsPressed": boxes.get("pressed"), "perInstance": out}


def _factory(spec):
    sys.path.insert(0, str(Path.cwd()))
    mod, _, fn = spec.partition(":")
    return getattr(importlib.import_module(mod), fn)


def main(argv=None, factory=None, store=None, **kw):
    "`factory` e `store` permitem aos testes passar diretamente uma fábrica de adaptadores e um PreparedSaves. kw vai para prepare()."
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("names", nargs="*", help="nomes de cenários (seus saves iniciais serão preparados)")
    ap.add_argument("--save", action="append", default=[], help="nome de save a preparar (repetível)")
    ap.add_argument("--status", action="store_true", help="mostra o que está preparado, sem alterar nada (não precisa de jogo)")
    ap.add_argument("--no-verify", action="store_true", help="pula a verificação de recarregamento")
    ap.add_argument("--adapter", help="pkg.mod:factory, factory(i) retorna o GameAdapter da instância i (como em scen.py run)")
    ap.add_argument("--instances", default="0,1", metavar="IDS",
                    help="IDs de instâncias passados à fábrica, por exemplo 0,1 (padrão) ou 2,3 para um segundo par de cópias")
    ap.add_argument("--dir", help="pasta com arquivos de cenário (padrão: exemplos distribuídos)")
    ap.add_argument("--prepared", help="the manifest file (default $%s or ./%s)" % (MANIFEST_ENV, DEFAULT_MANIFEST))
    a = ap.parse_args(argv)
    import scenlib
    directory = a.dir or str(scenlib.SCEN_DIR)
    saves = list(a.save)
    for n in a.names:
        p = Path(n)
        hits = [p] if p.suffix == ".json" else sorted(Path(directory).rglob(n + ".json"))
        if not hits:
            print("prepare_save: no scenario named %r under %s" % (n, directory))
            return 2
        s = scenlib.load_scenario(hits[0])["start"]["save"]
        if s not in saves:
            saves.append(s)
    if not a.names and not a.save:
        for p in scenlib.list_scenarios(directory):
            s = scenlib.load_scenario(p)["start"]["save"]
            if s not in saves:
                saves.append(s)
    try:
        ids = [int(x) for x in a.instances.split(",") if x.strip()]
    except ValueError:
        print("prepare_save: --instances wants a comma list of numbers, got %r" % a.instances)
        return 2
    store = store or PreparedSaves(a.prepared)
    make = factory or (_factory(a.adapter) if a.adapter else None)
    if a.status:
        games = {i: make(i) for i in ids} if make else {}
        for s in saves:
            for i in ids:
                print(json.dumps(store.status(i, s, games.get(i))))
        return 0
    if make is None:
        print("prepare_save: needs --adapter pkg.mod:factory (it is the same one scen.py run takes). --status works without it.")
        return 2
    try:
        games = [make(i) for i in ids]
        bad = 0
        for s in saves:
            r = prepare(games, s, store, instances=ids, verify=not a.no_verify, **kw)
            print(json.dumps(r))
            bad += not r["ok"]
        return 1 if bad else 0
    except NoPopupHooks as e:
        print("prepare_save: %s" % e)
        return 2
    except RuntimeError as e:   # popups nunca cessaram
        print("prepare_save: %s" % e)
        return 1


if __name__ == "__main__":
    sys.exit(main())
