"""Executor de cenários: salta a cenário em instâncias de jogo já ativas e executa etapas e verificações.

Executor usa tipagem duck sobre objetos GameAdapter (veja adapter.py), um por jogador, host primeiro. Testes usam
simulação em memória de fakegame.py; execução real recebe adaptadores do seu jogo.

Salto = (recarregar salvamento inicial só quando plan_jump indicar) -> redefinir chaves de estado no lugar -> etapas de preparação.
Numa instância ativa com mundo limpo, isso é poucas chamadas em vez de carregar salvamento inteiro.

Três recursos opcionais ativados quando adaptador fornece hooks (veja gameadapter.py), com retorno ao comportamento
simples quando não fornece:
  * esperas de sincronização por eventos (sync_status): após recarga, espera cada cliente aplicar commits do host
    e host aprovar um digest de estado, retorna assim que ocorrer e desiste cedo com motivo se nada avança;
  * salvamentos preparados (popup_count, dismiss_popup, prepare_save.py): recarga usa salvamento cujos popups já foram dispensados;
  * verificações contra dados do jogo (data_index): ids desconhecidos rejeitados antes de chamar jogo.
"""
import json
import os
import threading
import time
from pathlib import Path

import prepare_save
import scenlib
from gameadapter import ScenarioError

# opção de variante só de teste: noreload | passall | firsthost | nodirty
#   esperas sync: nostall | fullwait | hairtrigger | latesuccess | nodesyncs; salvamentos preparados: noprepared | longquiet
MUTANT = os.environ.get("SCEN_MUTANT", "")

MISSING = (NotImplementedError, ScenarioError)   # hook ausente no adaptador ou que não pode responder agora


def _applied(client_status):
    "Quanto do fluxo host cliente aplicou; -1 enquanto nada informa."
    v = client_status.get("applied")
    return -1 if v is None else v


class StateStore:
    """Memória do carregado em cada instância e alterado pelo cenário anterior. Chave por instância e
    geração; jogo reiniciado (nova geração) conta como vazio."""

    def __init__(self, path=None):
        self.path = Path(path) if path else None
        self.data = {}
        if self.path and self.path.exists():
            try:
                self.data = json.loads(self.path.read_text(encoding="utf-8"))
            except ValueError:
                self.data = {}

    def get(self, key):
        return self.data.get(key)

    def put(self, key, st):
        self.data[key] = st
        if self.path:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            self.path.write_text(json.dumps(self.data, indent=1, sort_keys=True), encoding="utf-8")

    @staticmethod
    def key(instance, generation):
        return "%s@%s" % (instance, generation)


class Runner:
    def __init__(self, adapters, store=None, keys=None, capabilities=None, sleep=time.sleep, now=time.monotonic,
                 load_wait_s=1.0, settle_s=0.2, poll_s=0.25, hooks=(), instances=None, prepared=None, sync=None,
                 quiet_plain_s=prepare_save.PLAIN_QUIET_S, quiet_prepared_s=prepare_save.PREPARED_QUIET_S):
        """instances: id de cada adaptador conhecido pela fábrica (padrão: atributo `instance`, senão sua
        posição); salvamentos preparados buscados por ele. prepared: None = arquivo PreparedSaves padrão se existir, False =
        nunca, ou um PreparedSaves. $SCEN_NO_PREPARED desativa independentemente do dado. sync: limites das esperas, dict
        para wait_synced() (timeout_s, stall_s, digest_timeout_s, digest_stall_s, repeat_limit, stale_limit, poll_s)."""
        self.games = list(adapters)
        self.store = store or StateStore()
        self.keys = list(keys) if keys else [StateStore.key(i, 0) for i in range(len(self.games))]
        self.sleep, self.now = sleep, now
        self.load_wait_s, self.settle_s, self.poll_s, self.hooks = load_wait_s, settle_s, poll_s, hooks
        self.sync_opts = dict(sync or {})
        self.quiet_plain_s, self.quiet_prepared_s = quiet_plain_s, quiet_prepared_s
        ids = list(instances) if instances is not None else [getattr(g, "instance", None) for g in self.games]
        self.instance_ids = [k if x is None else x for k, x in enumerate(ids)]
        if prepare_save.opted_out() or prepared is False:
            self.prepared = None
        else:
            self.prepared = prepared if prepared is not None else prepare_save.PreparedSaves.auto()
        self._index = False   # False = ainda não solicitado, None = adaptadores sem índice de dados
        if capabilities is not None:
            self.caps = set(capabilities)
        else:
            sets = [g.capabilities() for g in self.games]
            known = [s for s in sets if s is not None]
            self.caps = None if not known else set.intersection(*known)   # None: tudo disponível

    # ---- estado compartilhado do mundo, guardado por instância
    def _same_world(self):
        sts = [self.store.get(k) for k in self.keys]
        return sts[0] if all(s == sts[0] for s in sts) else None

    # ---- uma etapa numa instância
    def _do(self, game, step, res):
        op = step["op"]
        if op == "wait":
            self.sleep(float(step["seconds"]))
        elif op == "load":
            game.load_save(step["name"])
            self.sleep(self.load_wait_s)
        elif op == "save":
            game.save_game(step["name"])
        else:
            game.do(op, scenlib.resolve_args(step, res))

    def _check(self, sc, st, res):
        idx = scenlib.step_target(st, sc)
        args = scenlib.resolve_args(st, res)
        cmp_, value, agg = st.get("cmp", "=="), st.get("value"), st.get("agg")
        tol, timeout = st.get("tol", 0), float(st.get("timeout", 5))
        t0 = self.now()
        while True:
            vals = [float(self.games[i].read(st["kind"], args)) for i in idx]
            if scenlib.compare(vals, cmp_, value, agg, tol) or MUTANT == "passall":
                return {"status": "pass", "values": vals}
            if self.now() - t0 >= timeout:
                return {"status": "fail", "values": vals,
                        "detail": "%s %s %s%s (agg %s) not met after %.1fs; values per player %s" % (
                            st["kind"], cmp_, value, " +-%s" % tol if tol else "", agg, timeout, vals)}
            self.sleep(self.poll_s)

    def _step(self, sc, st, res):
        rec = {"id": st["id"], "op": st["op"], "status": "pass"}
        miss = sorted(scenlib.needs_of(st) - self.caps) if self.caps is not None else []
        if miss:
            rec.update(status="blocked", detail="the adapter does not provide: %s" % ", ".join(miss))
            return rec
        try:
            if st["op"] == "check":
                rec.update(self._check(sc, st, res))
            else:
                idx = scenlib.step_target(st, sc)
                if MUTANT == "firsthost":
                    idx = [0]
                if st.get("parallel") and len(idx) > 1:
                    errs = []

                    def guarded(i):
                        try:
                            self._do(self.games[i], st, res)
                        except Exception as ex:   # noqa: BLE001
                            errs.append(ex)
                    ths = [threading.Thread(target=guarded, args=(i,)) for i in idx]
                    for t in ths:
                        t.start()
                    for t in ths:
                        t.join()
                    if errs:
                        raise errs[0]
                else:
                    for i in idx:
                        self._do(self.games[i], st, res)
                if st["op"] in scenlib.SETTLE_OPS:
                    self.sleep(self.settle_s)
                    # com leituras sync, esperar também brevemente cada cliente aplicar commits host
                    w = self._wait_synced(**{"timeout_s": 10.0, "stall_s": 5.0, **self.sync_opts, "digest": False, "final_settle_s": 0.0})
                    if w is not None and not w.get("synced"):
                        rec["syncWait"] = w
        except ScenarioError as e:
            rec.update(status="error", detail=str(e))
        except Exception as e:   # noqa: BLE001
            rec.update(status="error", detail="%s: %s" % (type(e).__name__, str(e)[:200]))
        return rec

    # ---- salto
    def jump(self, sc, force_reload=False):
        "Leve cada instância ao estado inicial do cenário. Retorna {reload, reasons, seconds, setup, reset}."
        t0 = self.now()
        res = scenlib.Resolver(sc)
        fp = scenlib.footprint(sc)
        st = self._same_world()
        plan = scenlib.plan_jump(st, sc, fp, force_reload)
        if MUTANT == "noreload":
            plan = {"reload": False, "reasons": []}
        save = sc["start"]["save"]
        loaded = popups = coop_sync = None
        if plan["reload"]:
            loaded = self._load_start_save(sc)
            self.sleep(self.load_wait_s)
            # Salvamento preparado já tem popups dispensados: janela curta de silêncio só protege de aviso perdido.
            all_prepared = bool(loaded) and all(x["prepared"] for x in loaded) and MUTANT != "longquiet"
            popups = self.clear_popups(quiet_s=self.quiet_prepared_s if all_prepared else self.quiet_plain_s)
            # Cada cliente recarregou próprio salvamento e retorna à sessão. Etapas anteriores atingiriam um
            # jogo ainda carregando; carregamento sobrescreveria mudanças. Espere sessão sincronizada (por eventos).
            coop_sync = self.wait_synced()
        ids = scenlib.reset_ids(sc)
        prev = set((st or {}).get("state_ids") or [])
        # estado deixado alterado pelo cenário anterior também redefinido: salto no lugar não pode herdar
        ids = sorted(set(ids) | (prev if not plan["reload"] else set()))
        for g in self.games:
            g.reset_state(ids)
        out = []
        for s in sc.get("setup") or []:
            rec = self._step(sc, s, res)
            out.append(rec)
            if rec["status"] in ("error", "blocked"):
                break
        new = {"loaded": True, "save": save, "dirty": sorted(fp["dirty"]), "failed": False, "state_ids": ids, "scenario": sc["name"]}
        for k in self.keys:
            self.store.put(k, new)
        return {"reload": plan["reload"], "reasons": plan["reasons"], "seconds": round(self.now() - t0, 2), "setup": out, "reset": ids,
                "coopSync": coop_sync, "popups": popups, "loadedSaves": loaded}

    def _load_start_save(self, sc):
        """Carregue salvamento inicial em cada instância, cópia preparada onde houver (prepare_save.py) e onde
        jogo aceitar. -> [{"instance", "save" (carregado), "prepared", "why"}], para log informar origem de cada cópia."""
        save = sc["start"]["save"]
        wanted = (sc.get("start") or {}).get("prepared", True)
        out = []
        for k, g in enumerate(self.games):
            name, why = None, "prepared saves are off"
            if self.prepared and not wanted:
                why = "scenario sets start.prepared false"
            elif self.prepared and MUTANT != "noprepared":
                name, why = self.prepared.pick(self.instance_ids[k], save, g)
            used = save
            if name:
                try:
                    g.load_save(name)
                    used = name
                except ScenarioError as e:   # jogo recusou salvamento preparado: simples ainda funciona
                    name, why = None, "prepared save refused (%s); loaded %s" % (str(e)[:80], save)
            if not name:
                g.load_save(save)
            out.append({"instance": self.instance_ids[k], "save": used, "prepared": bool(name), "why": why})
        return out

    # ---- avisos
    def clear_popups(self, quiet_s=prepare_save.PLAIN_QUIET_S, max_s=150.0, poll_s=0.5):
        """Após carregar: dispense popups gerados até nenhum aparecer em instância alguma por `quiet_s`. Popup aberto pode manter
        jogo em menu, perdendo entrada de teste. Retorna {pressed, seconds, quiet}, ou None se adaptador não informa popups
        (popup_count() dá None ou não existe): nesse caso nada é esperado."""
        t0 = last = self.now()
        pressed = 0
        while True:
            seen = False
            for g in self.games:
                try:
                    n = g.popup_count()
                except MISSING:
                    n = None
                if n is None:
                    return None if not pressed else {"pressed": pressed, "seconds": round(self.now() - t0, 2), "quiet": False}
                if n > 0:
                    seen = True
                    try:
                        if g.dismiss_popup():
                            pressed += 1
                    except MISSING:   # popup fechando recusa pressão: repetir na próxima consulta
                        pass
            now = self.now()
            if seen:
                last = now
            if now - last >= quiet_s or now - t0 >= max_s:
                return {"pressed": pressed, "seconds": round(now - t0, 2), "quiet": now - last >= quiet_s}
            self.sleep(poll_s)

    # ---- esperas de sincronização por eventos
    def _statuses(self):
        "sync_status() de cada adaptador, ou None se algum não pode informar (então nada a esperar)."
        out = []
        for g in self.games:
            try:
                s = g.sync_status()
            except MISSING:
                return None
            if s is None:
                return None
            out.append(s)
        return out

    def wait_synced(self, **limits):
        "Espera de sincronização com limites deste Runner (argumento `sync`) e quaisquer `limits` extras. Veja _wait_synced."
        return self._wait_synced(**{**self.sync_opts, **limits})

    def _wait_synced(self, timeout_s=180.0, poll_s=0.5, stall_s=30.0, digest=True, digest_timeout_s=60.0, digest_stall_s=20.0,
                     repeat_limit=3, stale_limit=3, final_settle_s=1.0):
        """Espere cada cliente entrar e aplicar tudo que host confirmou, depois (digest=True) host aprovar
        mais um digest de estado. Retorna ao satisfazer condição, nunca por tempo fixo. None se nada a esperar
        (adaptador sem sync_status(), menos de duas instâncias ou sem host e cliente).

        Desiste cedo, com motivo, se nada avança: cliente recusou entrada ou progresso cliente (joined, applied,
        baseline, connection) parado por stall_s. Parte digest (_wait_digest_ok) desiste sem digest, com digests antigos
        ou mesma divergência repetida. timeout_s e digest_timeout_s são limites externos; stall_s, digest_stall_s,
        repeat_limit e stale_limit são antecipados. stall_s 0 desliga essa saída antecipada.
        Resultado: head, applied, synced (bool), seconds e, se não sincronizado, reason; mais chaves do resultado digest."""
        if len(self.games) < 2:
            return None
        t0 = self.now()
        sig, sig_at = None, t0
        while True:
            sts = self._statuses()
            if sts is None:
                return None
            hosts = [k for k, s in enumerate(sts) if s.get("role") == "host"]
            clients = [s for s in sts if s.get("role") == "client"]
            if not hosts or not clients:
                return None
            head = sts[hosts[0]].get("head", 0)
            syncing = [bool(c.get("syncing")) for c in clients]
            conn = [c.get("connected", True) for c in clients]
            ready = all(c.get("joined") and not sy and _applied(c) >= head and cn for c, sy, cn in zip(clients, syncing, conn))
            last = {"head": head, "applied": [c.get("applied") for c in clients]}
            now = self.now()
            if ready:
                if final_settle_s:
                    self.sleep(final_settle_s)   # deixar últimas mudanças aplicadas chegarem ao jogo
                out = dict(last, synced=True, seconds=round(self.now() - t0, 2))
                if digest:
                    out.update(self._wait_digest_ok(self.games[hosts[0]], digest_timeout_s, poll_s, digest_stall_s, repeat_limit, stale_limit))
                return out
            rej = [c for c in clients if c.get("rejected")]
            if rej:
                return dict(last, synced=False, seconds=round(now - t0, 2), reason="client rejected the join: %s" % rej[0]["rejected"])
            # progresso = qualquer mudança do lado cliente; avanço só da cabeça host não é progresso de cliente preso
            cur = (tuple(c.get("applied") for c in clients), tuple(bool(c.get("joined")) for c in clients), tuple(syncing), tuple(conn))
            if cur != sig:
                sig, sig_at = cur, now
            elif stall_s and now - sig_at >= stall_s and MUTANT != "nostall":
                why = []
                for n, (c, sy, cn) in enumerate(zip(clients, syncing, conn)):
                    if not cn:
                        why.append("client %d: link not connected" % n)
                    elif not c.get("joined"):
                        why.append("client %d: not joined" % n)
                    elif sy:
                        why.append("client %d: baseline still running" % n)
                    elif _applied(c) < head:
                        why.append("client %d: applied %s of %s" % (n, c.get("applied"), head))
                return dict(last, synced=False, seconds=round(now - t0, 2),
                            reason="no client progress for %.0f s (%s)" % (now - sig_at, "; ".join(why) or "unknown"))
            if now - t0 > timeout_s:
                return dict(last, synced=False, seconds=round(now - t0, 2), reason="timeout after %.0f s" % timeout_s)
            self.sleep(poll_s)

    @staticmethod
    def _new_desync_entries(entries, since_id, limit=8):
        "Entradas divergentes posteriores ao relatório since_id, mais novas primeiro: [{id, key, host, client, repaired}]."
        new = [e for e in entries or [] if e.get("id", 0) > since_id]
        new.sort(key=lambda e: e.get("id", 0), reverse=True)
        return [{"id": e.get("id"), "key": e.get("key"), "host": e.get("host"), "client": e.get("client"),
                 "repaired": bool(e.get("repaired"))} for e in new[:limit]]

    def _wait_digest_ok(self, host, timeout_s, poll_s, stall_s=20.0, repeat_limit=3, stale_limit=3):
        """Espere digests host contarem um 'ok' a mais que agora; retorne assim que ocorrer. Desiste cedo, com settleReason
        e entradas divergentes (desyncEntries), quando:
          * mesma divergência volta repeat_limit vezes (mesmas chaves com mesmos valores host/cliente: reparo
            não funciona),
          * stale_limit digests estavam antigos (host não pode julgá-los),
          * nenhum digest chegou por stall_s (cliente não envia ou enlace caiu).
        Digests com taxa limitada são normais e contam como recebidos. timeout_s é limite externo. {} se host não relata digests."""
        def status():
            s = host.sync_status() or {}
            return s.get("digests") or {}, s.get("desyncs") or []

        try:
            d0, e0 = status()
        except MISSING:
            return {}
        if not d0:
            return {}
        base_id = max([e.get("id", 0) for e in e0] or [0])
        t0 = self.now()
        rx, rx_at = d0.get("received", 0), t0
        mismatch, repeats, prev_sig = d0.get("mismatch", 0), 0, None
        limit = 1 if MUTANT == "hairtrigger" else repeat_limit

        def failed(reason, d, ents):
            out = {"digestOk": False, "settleReason": reason, "settleRepairs": d.get("repairs", 0) - d0.get("repairs", 0),
                   "settleSeconds": round(self.now() - t0, 2),
                   "digestDelta": {k: d.get(k, 0) - d0.get(k, 0) for k in ("received", "ok", "mismatch", "stale", "rateLimited")}}
            if MUTANT != "nodesyncs":
                out["desyncEntries"] = self._new_desync_entries(ents, base_id)
            return out

        d, ents = d0, e0
        while self.now() - t0 <= timeout_s:
            d, ents = status()
            now = self.now()
            if d.get("ok", 0) > d0.get("ok", 0):
                if MUTANT == "latesuccess":   # só teste: perceber sucesso só após timeout inteiro
                    self.sleep(max(0.0, timeout_s - (self.now() - t0)))
                return {"digestOk": True, "settleReason": "ok", "settleRepairs": d.get("repairs", 0) - d0.get("repairs", 0),
                        "settleSeconds": round(self.now() - t0, 2)}
            if MUTANT != "fullwait":
                if d.get("received", 0) != rx:
                    rx, rx_at = d.get("received", 0), now
                grown = d.get("mismatch", 0) - mismatch
                if grown > 0:
                    mismatch = d.get("mismatch", 0)
                    newest = self._new_desync_entries(ents, base_id, limit=1000)
                    top = max([e["id"] for e in newest] or [0])
                    sig = frozenset((e["key"], e["host"], e["client"]) for e in newest if e["id"] == top)
                    repeats = repeats + grown if sig == prev_sig else 1
                    prev_sig = sig
                    if repeats >= limit:
                        return failed("same mismatch %d times in a row and the repair did not fix it (%d repairs so far)" % (
                            repeats, d.get("repairs", 0) - d0.get("repairs", 0)), d, ents)
                if d.get("stale", 0) - d0.get("stale", 0) >= stale_limit:
                    return failed("%d stale digests: the host cannot judge them" % (d.get("stale", 0) - d0.get("stale", 0)), d, ents)
                if stall_s and now - rx_at >= stall_s:
                    return failed("no digest arrived for %.0f s" % (now - rx_at), d, ents)
            self.sleep(poll_s)
        return failed("no ok digest within %.0f s" % timeout_s, d, ents)

    # ---- índice de dados do jogo
    def data_index(self):
        "DataIndex do primeiro adaptador que possui um, ou None. Consultado uma vez por Runner."
        if self._index is False:
            self._index = None
            for g in self.games:
                try:
                    idx = scenlib.as_index(g.data_index())
                except MISSING:
                    idx = None
                if idx is not None:
                    self._index = idx
                    break
        return self._index

    # ---- execução
    def run(self, sc, force_reload=False):
        t0 = self.now()
        index = self.data_index()
        errs = scenlib.validate(sc, hooks=list(self.hooks) + ([scenlib.index_hook(index)] if index is not None else []))
        if errs:
            return {"scenario": sc.get("name"), "status": "invalid", "errors": errs, "steps": [], "seconds": 0.0}
        notes = [] if index is not None else ["ids were not checked against the game data: the adapter provides no data_index()"]
        res = scenlib.Resolver(sc)
        j = self.jump(sc, force_reload)
        steps = list(j["setup"])
        if not [r for r in steps if r["status"] == "error"]:
            blocked_by = None
            for s in sc["steps"]:
                if blocked_by:
                    # resultado após etapa que não pôde executar é indefinido: relatar bloqueado em vez de adivinhar
                    steps.append({"id": s["id"], "op": s["op"], "status": "blocked", "detail": "skipped: depends on blocked step %s" % blocked_by})
                    continue
                rec = self._step(sc, s, res)
                steps.append(rec)
                if rec["status"] == "blocked":
                    blocked_by = s["id"]
        fp = scenlib.footprint(sc)
        stats = [r["status"] for r in steps]
        if "fail" in stats:
            status = "fail"
        elif "error" in stats:
            status = "error"
        elif "blocked" in stats:
            status = "partial"
        else:
            status = "pass"
        if MUTANT == "nodirty":
            fp = {"dirty": set(), "touched": fp["touched"], "state": fp["state"]}
        st = {"loaded": True, "save": sc["start"]["save"], "dirty": sorted(fp["dirty"]), "failed": status in ("fail", "error"),
              "state_ids": j["reset"], "scenario": sc["name"]}
        for k in self.keys:
            self.store.put(k, st)
        out = {"scenario": sc["name"], "status": status,
               "jump": {k: j[k] for k in ("reload", "reasons", "seconds", "loadedSaves", "coopSync", "popups")},
               "steps": steps, "seconds": round(self.now() - t0, 2)}
        if notes:
            out["notes"] = notes
        return out


def summarize(results):
    lines, seen = [], set()
    for r in results:
        j = r.get("jump") or {}
        lines.append("%-8s %-28s %6.1fs  jump:%s" % (r["status"].upper(), r["scenario"], r["seconds"], "reload" if j.get("reload") else "in-place"))
        for s in r.get("steps", []):
            if s["status"] != "pass":
                lines.append("    %s %s: %s" % (s["status"], s["id"], s.get("detail", "")))
        for e in r.get("errors", []):
            lines.append("    invalid: %s" % e)
        for n in r.get("notes", []):
            if n not in seen:   # nota repetida em todos cenários é dita uma vez
                seen.add(n)
                lines.append("    note: %s" % n)
    return "\n".join(lines)
