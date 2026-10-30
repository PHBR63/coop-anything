"""O adaptador de ações: o único código específico do jogo de que um teste cooperativo precisa.

Um objeto ActionAdapter controla UMA instância de jogo em execução (a máquina de um jogador). Os roteiros chamam estes métodos e nunca
acessam o jogo diretamente, assim o mesmo roteiro funciona em qualquer jogo que tenha adaptador e no mundo cooperativo simulado de
fakecoop.py, sem um jogo.

Como escrever um para seu jogo
------------------------------
1. Crie uma subclasse de ActionAdapter. Implemente apenas o que seu jogo pode fazer. Todo método omitido lança MissingAction, e
   `supports("take")` informa ao roteiro (e ao executor) que ele falta, então esse roteiro é informado como SKIP, nunca PASS.
2. Implemente primeiro os três métodos do motor: `status()`, `snapshot()` e `capture()`. O executor os usa após cada etapa.
3. Ações retornam um Result (ok, reason, data). Nunca lance uma exceção para uma recusa normal ("a porta está trancada"): retorne
   Result(False, "a porta está trancada"). Lance apenas se o jogo ou o enlace estiver morto, para encerrar a execução com um erro claro.
   A classe base transforma qualquer retorno de ação em ActionResult (ok, reason, data, action, elapsed_s), para que toda
   ação de todo adaptador tenha um único modelo de resultado. Veja results.py.
4. Confira a pós-condição dentro da ação: `take` só é ok quando a contagem de itens realmente mudou. Um bot que informa
   sucesso porque a chamada retornou é a principal fonte de aprovações vazias. `self.act(do, pre=[...], post=[...])` executa uma
   pré-condição, a ação e uma pós-condição, e qualquer `raise Fail("code", "o que observei")` vira um resultado malsucedido.
5. IDs ("refs") são strings opacas que você escolhe: um ID de editor, um ID de formulário, um caminho, um nome. Os roteiros apenas as devolvem.
6. Explique o motivo. Uma ação malsucedida mostra "código: o que o bot observou" (unidades restantes de uma caminhada, o menu no caminho, o estado da arma).
   Sobrescreva `blockers()` para listar o que impede a entrada agora (um menu aberto, uma caixa de mensagem, uma arma
   guardada); a classe base acrescenta esse texto a toda falha, e `act(..., free=True)` recusa iniciar enquanto
   houver impedimento. `Why` em results.py formula os motivos comuns (stuck, too_close, too_steep, menu, message_box, holstered).

Semântica de referência usada pelos roteiros
-----------------------------------------
Ações (todas retornam Result)
    goto_ref(ref, dist=150)            caminhar ou teletransportar até ficar a `dist` do objeto
    goto_pos(x, y, z, cell=None)       o mesmo para uma coordenada
    equip(item)  aim_at(ref)  fire(n=1)
    activate(ref)                      usar o objeto como um jogador pressiona a tecla de uso
    open_door(ref)  close_door(ref)  unlock(ref, key=None)
    open_container(ref)  close_container(ref)
    take(item, count, from_ref)  put(item, count, to_ref)
    pickup(ref)                        pegar um item do mundo. Falha com "already taken" para quem perde uma disputa
    drop(item, count)                  data["ref"] é o novo objeto do mundo
    talk(npc)  pick_topic(topic)  end_dialogue()
    use_device(ref, entry)             um terminal, painel de alavancas ou qualquer objeto de menu
    set_stage(quest, stage)  start_quest(quest)
    barrier_pass(quest)                este jogador terminou sua parte de uma etapa que espera todos
    answer_prompt(button)              pressionar um botão da caixa de mensagem aberta (0 = primeiro)
    consent(kind, quest, yes)          responder à confirmação de "pronto" ou "viagem rápida" do grupo
    fast_travel(marker)  spawn(base, at)  save_game(name)  load_game(name)  session_leave()  session_join()
    set_timescale(x)                   multiplicador de tempo do jogo (o executor o chama para --timescale e o restaura para 1)
Consultas (valores de retorno)
    cell()  distance_to(ref)  inventory_count(item, holder=None)  death_count(ref)  target_alive(ref)
    ref_enabled(ref)  in_dialogue()  spectating()  is_locked(ref)  door_open(ref)  device_entry_used(ref, entry)
    quest_stage(quest)  stage_done(quest, stage)  quest_running(quest)  objective_displayed(quest, n)
    objective_completed(quest, n)  owner_of(ref) -> (owner, epoch)  ref_count(base, cell="")
    consent_pending() -> bool  rebases() -> int
    timescale() -> float               opcional: a velocidade real do jogo, para o executor conferir set_timescale
Motor
    status() -> {"seq": int, "synced": bool, "counters": {name: int}}   veja core.py; "acks": {name: int} opcional
    snapshot() -> {"shared": {...}, "per_player": {...}}                veja core.py
    capture(directory) -> dict                                          opcional: escrever registros de uma etapa malsucedida
Ganchos de explicação (todos opcionais)
    blockers() -> [(code, text), ...]  o que impede a entrada agora        explain(action, result) -> str   texto acrescentado a uma falha
"""
import collections
import functools
import os
from typing import Any, Callable, Iterable, List, Sequence, Tuple

from .results import ActionFailed, ActionResult, Fail, Result, Why, ensure, now  # noqa: F401  (re-exported for adapters)

MUTANT = os.environ.get("COOPBOTS_MUTANT", "")   # opção de variante exclusiva para testes: nowhy | nopost


class MissingAction(NotImplementedError):
    "O adaptador não implementa esta ação. O texto informa qual é."


def _stub(name, doc):
    def f(self, *args, **kwargs):
        raise MissingAction("this adapter does not implement %s" % name)
    f.__name__ = name
    f.__doc__ = doc
    f._not_implemented = True
    return f


ACTIONS = {
    "goto_ref": "goto_ref(ref, dist=150) -> Result",
    "goto_pos": "goto_pos(x, y, z, cell=None) -> Result",
    "equip": "equip(item) -> Result",
    "aim_at": "aim_at(ref) -> Result",
    "fire": "fire(n=1) -> Result; fails when nothing is aimed at",
    "activate": "activate(ref) -> Result",
    "open_door": "open_door(ref) -> Result; fails with a reason when locked",
    "close_door": "close_door(ref) -> Result",
    "unlock": "unlock(ref, key=None) -> Result",
    "open_container": "open_container(ref) -> Result; fails while another player has it open",
    "close_container": "close_container(ref) -> Result",
    "take": "take(item, count, from_ref) -> Result; ok only if the container lost and the player gained `count`",
    "put": "put(item, count, to_ref) -> Result",
    "pickup": "pickup(ref) -> Result; the loser of a race gets ok=False",
    "drop": "drop(item, count) -> Result with data['ref'] = the new world object",
    "talk": "talk(npc) -> Result",
    "pick_topic": "pick_topic(topic) -> Result",
    "end_dialogue": "end_dialogue() -> Result",
    "use_device": "use_device(ref, entry) -> Result",
    "set_stage": "set_stage(quest, stage) -> Result",
    "start_quest": "start_quest(quest) -> Result",
    "barrier_pass": "barrier_pass(quest) -> Result",
    "answer_prompt": "answer_prompt(button) -> Result",
    "consent": "consent(kind, quest='', yes=True) -> Result",
    "fast_travel": "fast_travel(marker) -> Result",
    "spawn": "spawn(base, at) -> Result",
    "save_game": "save_game(name) -> Result",
    "load_game": "load_game(name) -> Result",
    "session_leave": "session_leave() -> Result",
    "session_join": "session_join() -> Result",
    "set_timescale": "set_timescale(x) -> Result; the game's time multiplier, 1 = normal speed",
}
QUERIES = {
    "cell": "cell() -> str",
    "distance_to": "distance_to(ref) -> float",
    "inventory_count": "inventory_count(item, holder=None) -> int; holder None = this player",
    "death_count": "death_count(ref) -> int",
    "target_alive": "target_alive(ref) -> bool",
    "ref_enabled": "ref_enabled(ref) -> bool",
    "in_dialogue": "in_dialogue() -> bool",
    "spectating": "spectating() -> bool",
    "is_locked": "is_locked(ref) -> bool",
    "door_open": "door_open(ref) -> bool",
    "device_entry_used": "device_entry_used(ref, entry) -> bool",
    "quest_stage": "quest_stage(quest) -> int",
    "stage_done": "stage_done(quest, stage) -> bool",
    "quest_running": "quest_running(quest) -> bool",
    "objective_displayed": "objective_displayed(quest, n) -> bool",
    "objective_completed": "objective_completed(quest, n) -> bool",
    "owner_of": "owner_of(ref) -> (owner slot, epoch)",
    "ref_count": "ref_count(base, cell='') -> int; live objects of that base",
    "consent_pending": "consent_pending() -> bool",
    "rebases": "rebases() -> int; how often this client had to adopt the host's world",
    "timescale": "timescale() -> float; the speed the game runs at now (optional; lets the runner check set_timescale)",
}


ENGINE = {
    "status": "status() -> {'seq': int, 'synced': bool, 'counters': {name: int}}. seq: number of the last host update this "
              "machine applied (the host reports the last one it sent). synced: host only, False while any client is behind. "
              "counters: desync counters, see core.REPAIR_COUNTERS and core.HARD_COUNTERS. Optional 'acks': {client: last "
              "update number the host knows it has}, which lets a stuck wait say who is behind",
    "snapshot": "snapshot() -> {'shared': {...}, 'per_player': {...}}. `shared` must be equal on every machine once synced",
}


def _coerce(name: str, out: Any) -> ActionResult:
    if isinstance(out, ActionResult):
        return out
    if isinstance(out, Result):
        return ActionResult.of(out, name)
    if isinstance(out, bool):
        return ActionResult(out, "" if out else "the action returned False", {}, name)
    raise TypeError("action %s returned %r; return a Result (ok, reason, data)" % (name, out))


def _wrap_action(name: str, fn: Callable) -> Callable:
    @functools.wraps(fn)
    def action(self, *args, **kwargs):
        t0 = now()
        try:
            res = _coerce(name, fn(self, *args, **kwargs))
        except Fail as f:
            res = ActionResult(False, f.reason, dict(f.data), name)
        res.action = res.action or name
        res.elapsed_s = res.elapsed_s or (now() - t0)
        if not res.ok and not getattr(res, "_explained", False):
            res._explained = True
            self._say_why(name, res)
        self._record(res)
        if self.strict and not res.ok:
            raise ActionFailed(res)
        return res
    action._action_wrapped = True
    return action


class ActionAdapter:
    "Classe base. Veja a docstring do módulo."

    name = "bot"
    strict = False                    # True: uma ação malsucedida lança ActionFailed em vez de retornar seu resultado

    # status() e snapshot() também são implementações provisórias (veja ENGINE acima); o executor as usa após cada etapa.

    def __init_subclass__(cls, **kw):
        super().__init_subclass__(**kw)
        for n in ACTIONS:
            f = cls.__dict__.get(n)
            if callable(f) and not getattr(f, "_not_implemented", False) and not getattr(f, "_action_wrapped", False):
                setattr(cls, n, _wrap_action(n, f))

    def capture(self, directory):
        "Opcional: escreve registros ou despejos de uma etapa malsucedida em `directory`; retorna um pequeno dict que os descreve."
        return {}

    def supports(self, action):
        m = getattr(self, action, None)
        return callable(m) and not getattr(getattr(m, "__func__", m), "_not_implemented", False)

    # ---- o modelo de resultado das ações ----
    def blockers(self) -> List[Tuple[str, str]]:
        """O que impede a entrada agora, como [(code, text), ...]: ("menu", "o menu de inventário está aberto"),
        ("message_box", "há uma caixa de mensagem aberta"), ("holstered", "a arma está guardada"). Padrão: nada conhecido."""
        return []

    def require_free(self, ignore: Iterable[str] = ()) -> None:
        "Falha com o primeiro impedimento (todos constam no texto), salvo se seu código estiver em `ignore`."
        skip = set(ignore)
        bl = [b for b in self.blockers() if b[0] not in skip]
        if bl:
            raise Fail(bl[0][0], "; ".join(t for _, t in bl))

    def explain(self, action: str, result: ActionResult) -> str:
        "Texto acrescentado a todo resultado malsucedido para que o motivo nomeie a causa. Padrão: os impedimentos atuais."
        return "; ".join(t for _, t in self.blockers())

    def _say_why(self, action: str, result: ActionResult) -> None:
        if MUTANT == "nowhy":
            return
        try:
            note = self.explain(action, result)
        except Exception:  # noqa: BLE001  a broken explain hook must not hide the real failure
            return
        if note and note not in result.reason:
            result.reason += ("; " if ": " in result.reason else ": ") + note

    def _record(self, res: ActionResult) -> None:
        log = self.__dict__.get("_action_log")
        if log is None:
            log = self._action_log = collections.deque(maxlen=200)
        log.append(res)

    def recent_actions(self, n: int = 8) -> List[dict]:
        "As últimas n ações deste adaptador como dicionários simples (o executor as guarda em failure.json)."
        return [r.to_json() for r in list(self.__dict__.get("_action_log") or [])[-n:]]

    def act(self, do: Callable[[], Any], *, pre: Sequence[Callable[[], Any]] = (), post: Sequence[Callable[[dict], Any]] = (),
            free: bool = False, ignore: Iterable[str] = ()) -> ActionResult:
        """Executa uma ação com suas verificações: `free` (nada pode bloquear a entrada), depois cada `pre()`, `do()` e cada `post(data)`.
        Uma verificação falha ao lançar Fail (ou por `ensure(cond, code, say)`); a fase da verificação malsucedida é adicionada aos dados como
        "phase": "pre", "do" ou "post". `do()` retorna um dict, um Result ou None; um Result malsucedido é repassado sem executar `post`."""
        phase = "pre"
        try:
            if free:
                self.require_free(ignore)
            for p in pre:
                p()
            phase = "do"
            out = do()
            if isinstance(out, Result) and not out.ok:
                return ActionResult.of(out, "")
            data = dict(out.data) if isinstance(out, Result) else dict(out or {})
            phase = "post"
            if MUTANT != "nopost":
                for q in post:
                    q(data)
        except Fail as f:
            f.data.setdefault("phase", phase)
            raise
        return ActionResult(True, "", data)


for _n, _d in {**ENGINE, **ACTIONS, **QUERIES}.items():
    setattr(ActionAdapter, _n, _stub(_n, _d))
