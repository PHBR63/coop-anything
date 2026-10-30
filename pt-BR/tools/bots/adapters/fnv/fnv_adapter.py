"""Exemplo de ActionAdapter para um jogo Gamebryo com console de scripts (Fallout: New Vegas). Pequeno de propósito.

Mostra o pouco que um primeiro adaptador exige: alguns comandos de console, verificação de pós-condição após cada ação
e mapeamento de estado. Tudo que não implementa é omitido, para que os roteiros que precisem disso sejam ignorados e relatados.

A ponte é sua. Ela só precisa de:

    bridge.exec(line)            -> {"ok": bool, "output": str}   executa um comando de console no jogo
    bridge.eval(expr)            -> number                        avalia uma expressão de console
    bridge.call(method, params)  -> dict                          estado e captura de dados do próprio mod cooperativo

Os identificadores são ids do editor ou hexadecimais aceitos pelo console. Não há endereço de motor aqui, apenas comandos
de console. Confira a grafia de cada comando na sua compilação antes de confiar nele.

A parte que explica o motivo (consulte coopbots/adapter.py): `blockers()` lê a resposta `ui.status` do mod, assumida neste
exemplo como {"menu": "name or empty", "messageBoxes": n, "weaponDrawn": bool}; a classe base acrescenta o que encontrar
(menu aberto, janela de mensagem, arma guardada) a cada ação que falhar. `goto_ref` relata caminhada presa com a distância
restante. `set_timescale` é um comando de console (`sgtm X`); ele é a única parte do hook de velocidade específica do jogo.
"""
import json
import os
from typing import Dict

from coopbots.adapter import ActionAdapter, Result, Why

PARSE_ERRORS = ("could not parse", "error line", "unknown", "invalid")


class FnvBot(ActionAdapter):
    def __init__(self, bridge, name="bot"):
        self.b = bridge
        self.name = name

    # ---- infraestrutura ----
    def _run(self, line) -> Result:
        r = self.b.exec(line)
        out = (r.get("output") or "") if isinstance(r, dict) else ""
        if (isinstance(r, dict) and r.get("ok") is False) or any(p in out.lower() for p in PARSE_ERRORS):
            return Result(False, "%s -> %s" % (line, out.strip()[:100] or "refused"))
        return Result(True)

    def _num(self, expr) -> float:
        return float(self.b.eval(expr))

    @staticmethod
    def _who(holder):
        return "player" if holder is None else holder

    # ---- interface do mecanismo: mapeia o estado do mod cooperativo nos contadores do executor ----
    COUNTER_PATHS = {                       # contador do executor -> caminho na resposta de estado do mod
        "mismatches": ("desyncs", "digests", "mismatch"), "repairs": ("desyncs", "digests", "repairs"),
        "repaired_effects": ("desyncs", "digests", "effectsRepaired"), "bad_messages": ("host", "badMessages"),
        "apply_failures": ("counters", "applyFailed"), "rebases": ("client", "rebases"),
    }

    def status(self):
        st = self.b.call("coop.status", {})
        counters: Dict[str, int] = {}
        for k, path in self.COUNTER_PATHS.items():
            v = st
            for p in path:
                v = v.get(p) if isinstance(v, dict) else None
            counters[k] = int(v or 0)
        return {"seq": int(st.get("lastSeq", 0) or 0), "synced": bool((st.get("host") or {}).get("allSynced", True)), "counters": counters}

    def snapshot(self):
        return self.b.call("state", {})      # precisa retornar {"shared": {...}, "per_player": {...}}

    def capture(self, directory):
        os.makedirs(directory, exist_ok=True)
        path = os.path.join(directory, "events.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.b.call("events", {"since": 0}), f, indent=1)
        return {"events": path}

    # ---- explica o motivo: o que bloqueia a entrada agora ----
    def blockers(self):
        try:
            ui = self.b.call("ui.status", {}) or {}
        except Exception:  # noqa: BLE001  a bridge without ui.status: nothing is known, nothing is added to failures
            return []
        out = []
        if ui.get("menu"):
            out.append(("menu", "the %s menu is open" % ui["menu"]))
        if ui.get("messageBoxes"):
            out.append(("message_box", "%d message box(es) are up" % ui["messageBoxes"]))
        if ui.get("weaponDrawn") is False:
            out.append(("holstered", "the weapon is holstered"))
        return out

    # ---- ações ----
    def goto_ref(self, ref, dist=150):
        wanted = max(dist, 250)

        def arrived(data):
            d = self._num("player.GetDistance %s" % ref)
            data["distance"] = d
            if d > wanted:
                raise Why.stuck(d, wanted, "still that far from %s after moveto" % ref)
        return self.act(lambda: self._run("player.moveto %s" % ref), free=True, ignore=("holstered",), post=[arrived])

    def set_timescale(self, x):
        "Multiplicador de tempo do jogo: um comando de console. A grafia varia entre compilações; confira este comando na sua."
        return self._run("sgtm %g" % x)

    def activate(self, ref):
        return self._run("%s.activate player 1" % ref)

    def pickup(self, ref):
        if self._num("%s.GetDisabled" % ref):
            return Result(False, "already taken")
        r = self.activate(ref)
        if not r:
            return r
        gone = bool(self._num("%s.GetDisabled" % ref))
        return Result(gone, "" if gone else "the object is still in the world after activating it")

    def take(self, item, count, from_ref):
        return self._transfer(item, count, src=from_ref, dst=None)

    def put(self, item, count, to_ref):
        return self._transfer(item, count, src=None, dst=to_ref)

    def _transfer(self, item, count, src, dst) -> Result:
        "Move itens entre jogador e contêiner; sucesso apenas se AS DUAS contagens mudarem (detecta duplicação e perda)."
        s, d = self._who(src), self._who(dst)
        s0, d0 = self.inventory_count(item, src), self.inventory_count(item, dst)
        r = self._run("%s.RemoveItemTarget %s %s %d 1" % (s, item, d, count))
        if not r:
            return r
        s1, d1 = self.inventory_count(item, src), self.inventory_count(item, dst)
        if (s0 - s1, d1 - d0) != (count, count):
            return Result(False, "transfer of %d x %s moved %d out and %d in" % (count, item, s0 - s1, d1 - d0))
        return Result(True)

    def set_stage(self, quest, stage):
        return self._run("setstage %s %d" % (quest, stage))

    def unlock(self, ref, key=None):
        r = self._run("%s.unlock" % ref)
        return r if not r else Result(not self.is_locked(ref), "still locked after unlock")

    # ---- consultas ----
    def inventory_count(self, item, holder=None):
        return int(self._num("%s.GetItemCount %s" % (self._who(holder), item)))

    def target_alive(self, ref):
        return not self._num("%s.GetDead" % ref) and not self._num("%s.GetDisabled" % ref)

    def ref_enabled(self, ref):
        return not self._num("%s.GetDisabled" % ref)

    def is_locked(self, ref):
        return bool(self._num("%s.GetLocked" % ref))

    def door_open(self, ref):
        return self._num("%s.GetOpenState" % ref) == 1

    def distance_to(self, ref):
        return self._num("player.GetDistance %s" % ref)

    def quest_stage(self, quest):
        return int(self._num("GetStage %s" % quest))

    def stage_done(self, quest, stage):
        return bool(self._num("GetStageDone %s %d" % (quest, stage)))
