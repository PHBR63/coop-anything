"""Modelo de resultado de ação: o que cada ação de bot retorna e como informa POR QUE falhou.

    ActionResult(ok, reason, data, action, elapsed_s)

`reason` contém "code: what the bot saw". O código é curto e estável ("stuck", "too_close", "holstered", "menu"), para
um roteiro ou script poder tomar decisões por `result.code`. A parte após os dois-pontos é para quem lê uma etapa que
falhou: distância restante, menu que bloqueou, estado da arma. Uma falha só com código é fraca: diga o que observou.

As ações têm uma pré-condição (o mundo permite que isto funcione?), a ação e uma pós-condição (o mundo realmente mudou?).
Consulte `ActionAdapter.act` em adapter.py. Uma verificação que falha lança `Fail`, convertido pelo adaptador em
ActionResult de falha. Uma recusa comum nunca é exceção: somente jogo ou conexão inativos são.

A classe `Why` constrói as falhas comuns à maioria dos jogos, para todos os adaptadores usarem a mesma redação.
"""
import time
from dataclasses import dataclass, field
from typing import Any, Dict

# Códigos de falha usados pelas funções auxiliares compartilhadas. Um adaptador pode acrescentar os próprios; mantenha-os curtos e em minúsculas.
CODES = ("stuck", "too_close", "too_steep", "menu", "message_box", "holstered", "precondition", "postcondition", "timeout",
         "refused", "not_found", "dead", "unsupported")


@dataclass
class Result:
    ok: bool
    reason: str = ""
    data: Dict[str, Any] = field(default_factory=dict)

    def __bool__(self) -> bool:
        return self.ok

    @property
    def code(self) -> str:
        "Código curto da falha. Compare códigos por este campo, nunca pelo motivo inteiro."
        return self.reason.split(":", 1)[0].strip()


@dataclass
class ActionResult(Result):
    action: str = ""
    elapsed_s: float = 0.0

    def __str__(self) -> str:
        return "%s: %s (%.2fs)%s" % (self.action or "action", "ok" if self.ok else "FAILED " + self.reason, self.elapsed_s,
                                     " %s" % (self.data,) if self.data else "")

    def to_json(self) -> dict:
        return {"action": self.action, "ok": self.ok, "reason": self.reason, "code": "" if self.ok else self.code,
                "elapsed_s": round(self.elapsed_s, 3), "data": self.data}

    @classmethod
    def of(cls, res: Result, action: str, elapsed_s: float = 0.0) -> "ActionResult":
        if isinstance(res, ActionResult):
            return res
        return cls(res.ok, res.reason, dict(res.data), action, elapsed_s)


class Fail(Exception):
    "Lance dentro de uma ação (ou pré/pós-condição) para reprová-la com um código e texto que explique o motivo."

    def __init__(self, code: str, say: str = "", **data: Any):
        self.code = code
        self.say = say
        self.data = data
        self.reason = "%s: %s" % (code, say) if say else code
        super().__init__(self.reason)


class ActionFailed(Exception):
    "Lançada em vez de retornar um resultado de falha quando o adaptador está em modo estrito (adapter.strict = True)."

    def __init__(self, result: ActionResult):
        super().__init__(str(result))
        self.result = result


def ensure(cond: Any, code: str, say: str = "", **data: Any) -> None:
    "Verificação de uma linha para pré e pós-condições: ensure(count == 1, \"postcondition\", \"the item count did not move\")."
    if not cond:
        raise Fail(code, say, **data)


class Why:
    "Falhas prontas com a redação que todos os adaptadores devem compartilhar. Use como `raise Why.stuck(left, 150)`."

    @staticmethod
    def stuck(left: float, wanted: float, note: str = "") -> Fail:
        "Caminhada que terminou longe demais do destino: quantas unidades faltaram."
        say = "%.0f units left (wanted within %g)" % (left, wanted)
        return Fail("stuck", say + ("; " + note if note else ""), distance=left, wanted=wanted)

    @staticmethod
    def too_close(distance: float, minimum: float) -> Fail:
        return Fail("too_close", "the player is %.0f units from the target (minimum %g); stand further away" % (distance, minimum),
                    distance=distance, minimum=minimum)

    @staticmethod
    def too_steep(pitch: float, limit: float, distance: float) -> Fail:
        return Fail("too_steep", "aiming at the target needs %.0f degrees of pitch (limit %g) at %.0f units; "
                    "move so the target is closer to eye level" % (pitch, limit, distance), pitch=pitch, limit=limit, distance=distance)

    @staticmethod
    def menu_open(menu: str = "a menu") -> Fail:
        return Fail("menu", "%s is open and takes the input; close it first" % menu, menu=menu)

    @staticmethod
    def message_box(text: str = "") -> Fail:
        return Fail("message_box", "a message box is up%s and blocks the action" % (" (%s)" % text if text else ""), text=text)

    @staticmethod
    def holstered(weapon: str = "") -> Fail:
        return Fail("holstered", "the weapon%s is holstered; draw it first" % (" " + weapon if weapon else ""), weapon=weapon)

    @staticmethod
    def postcondition(say: str, **data: Any) -> Fail:
        return Fail("postcondition", say, **data)

    @staticmethod
    def precondition(say: str, **data: Any) -> Fail:
        return Fail("precondition", say, **data)


def now() -> float:
    return time.monotonic()
