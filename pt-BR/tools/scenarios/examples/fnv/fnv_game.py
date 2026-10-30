"""Exemplo de GameAdapter para um jogo Gamebryo com console de scripts (Fallout: New Vegas), com cerca de 100 linhas.

Mostra toda a tarefa de escrever um adaptador para o jogo: transformar cada operação de cenário em um comando de console,
cada tipo de verificação em uma expressão e informar o que não consegue fazer. Os identificadores dos cenários são
IDs do editor, aceitos pelo console no lugar dos identificadores numéricos de formulário.

O objeto da ponte é seu. Só precisa destes métodos (qualquer ponte interna ao processo do jogo funciona):

    bridge.exec(line)            -> {"ok": bool, "output": str}   executa um comando de console
    bridge.eval(expr)            -> number                        avalia uma expressão de console
    bridge.load_save(name)       / bridge.save_game(name)
    bridge.call(method, params)  -> dict                          opcional, para métodos específicos do projeto

Os comandos abaixo usam a grafia usual. Confira cada um na sua ponte antes de confiar neles.

Os hooks opcionais (gameadapter.py) demonstram outros três recursos, todos controlados por argumentos do construtor,
para um FnvGame(bridge) simples se comportar como um jogo sem eles:

    records={"GSPG01Ref": "ACHR", ...}   índice de IDs do editor para tipos de registro -> data_index() (IDs verificados antes de executar)
    saves_dir=<folder with the .fos files>                                       -> save_exists() e save_stamp() (obsolescência dos salvamentos preparados)
    with_project_methods=True            a ponte tem bot.menu, bot.menu.press e coop.status
                                                                                 -> popup_count(), dismiss_popup(), sync_status()
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import scenlib  # noqa: E402
from gameadapter import GameAdapter, ScenarioError  # noqa: E402

PARSE_ERRORS = ("could not parse", "error line", "unknown", "invalid")


def _who(v):
    return "player" if v == "player" else v


# tipo de registro -> tipos de objeto de cenário nos quais um id desse tipo pode ser usado
SIG_KINDS = {"ACHR": "actor", "ACRE": "actor", "REFR": ["thing", "place"], "CELL": "place", "QUST": "state", "GLOB": "state",
             "NPC_": "base", "CREA": "base", "LVLI": "base",
             **{sig: ["item", "base"] for sig in ("MISC", "WEAP", "ARMO", "AMMO", "ALCH", "NOTE", "KEYM", "CHIP", "IMOD", "BOOK")}}


class FnvGame(GameAdapter):
    "Uma instância do jogo, acessada por `bridge`."

    ROLLING_SAVES = ("autosave", "quicksave")

    def __init__(self, bridge, with_project_methods=False, records=None, saves_dir=None):
        self.bridge = bridge
        self.records = records
        self.saves_dir = Path(saves_dir) if saves_dir else None
        self.project = with_project_methods          # True se a ponte também tiver call() com métodos de desenvolvimento
        ops = {"op:" + o for o in ("move", "spawn", "give", "take", "kill", "revive", "enable", "disable", "lock", "unlock",
                                   "activate", "set_state", "wait", "save", "load")}
        checks = {"check:" + k for k in ("state", "state_reached", "item_count", "dead", "disabled", "locked", "in_area",
                                         "distance", "stat", "follower")}
        self.OPS = ops | checks | ({"check:owner", "check:count"} if with_project_methods else set())

    def _console(self, line):
        r = self.bridge.exec(line)
        out = (r.get("output") or "") if isinstance(r, dict) else ""
        if (isinstance(r, dict) and r.get("ok") is False) or any(p in out.lower() for p in PARSE_ERRORS):
            raise ScenarioError("%s -> %s" % (line, out.strip()[:120] or r))

    def do(self, op, a):
        if op == "set_state":
            self._console("setstage %s %d" % (a["key"], int(a["value"])))
        elif op == "move":
            self._console("%s.moveto %s" % (_who(a["who"]), a["to"]))
        elif op == "spawn":
            self._console("%s.placeatme %s %d" % (_who(a["at"]), a["base"], a.get("count", 1)))
        elif op in ("give", "take"):
            self._console("%s.%s %s %d" % (_who(a["who"]), "additem" if op == "give" else "removeitem", a["item"], a["count"]))
        elif op == "revive":
            self._console("%s.resurrect" % a["ref"])
        elif op in ("kill", "enable", "disable", "unlock"):
            self._console("%s.%s" % (a["ref"], op))
        elif op == "lock":
            self._console("%s.lock %d" % (a["ref"], a["level"]))
        elif op == "activate":
            self._console("%s.activate player 1" % a["ref"])
        else:
            raise ScenarioError("no console line for op %r" % op)

    EXPR = {
        "state": "GetStage {key}",
        "state_reached": "GetStageDone {key} {at}",
        "item_count": "{who}.GetItemCount {item}",
        "dead": "{ref}.GetDead",
        "disabled": "{ref}.GetDisabled",
        "locked": "{ref}.GetLocked",
        "in_area": "{ref}.GetInCell {place}",
        "distance": "{a}.GetDistance {b}",
        "stat": "{ref}.GetAV {stat}",
        "follower": "{ref}.GetPlayerTeammate",
    }

    def read(self, kind, a):
        if kind == "owner":
            return float(self.bridge.call("coop.owner", {"ref": a["ref"]})["owner"])   # método específico do projeto
        if kind == "count":
            return float(self.bridge.call("dev.countRefs", {"base": a["base"]})["count"])
        return float(self.bridge.eval(self.EXPR[kind].format(**a)))

    def load_save(self, name):
        self.bridge.load_save(name)

    def save_game(self, name):
        self.bridge.save_game(name)

    def reset_state(self, ids):
        if self.project:
            self.bridge.call("test.quest.reset", {"quests": list(ids)})
        else:
            for q in ids:
                self._console("setstage %s 0" % q)   # alternativa simples: etapa 0 (não limpa variáveis de script)

    # ---- hooks opcionais
    def data_index(self):
        if not self.records:
            return None
        return scenlib.DataIndex({edid: SIG_KINDS.get(sig) for edid, sig in self.records.items()}, case_sensitive=False,
                                 label="the Fallout data")

    def prepared_names(self, save):
        return ["nvcoop_%s_ready" % save, "autosave_nvcoop_%s_ready" % save]   # o segundo atende a um motor que só aceita nomes de salvamento automático

    def _fos(self, name):
        return self.saves_dir / (name + ".fos") if self.saves_dir else None

    def save_exists(self, name):
        p = self._fos(name)
        return None if p is None else p.is_file()

    def save_stamp(self, name):
        p = self._fos(name)
        if p is None or not p.is_file():
            return None
        st = p.stat()
        return {"size": st.st_size, "mtimeNs": st.st_mtime_ns}

    def popup_count(self):
        if not self.project:
            return None
        return 1 if self.bridge.call("bot.menu").get("kind") == "message" else 0

    def dismiss_popup(self):
        self.bridge.call("bot.menu.press", {"button": 0})
        return True

    def sync_status(self):
        "coop.status desta cópia no formato descrito por gameadapter.py."
        if not self.project:
            return None
        st = self.bridge.call("coop.status")
        role = st.get("role")
        if role == "host":
            ds = st.get("desyncs") or {}
            entries = [{"id": r.get("id", 0), "key": e.get("key"), "host": e.get("host"), "client": e.get("client"),
                        "repaired": bool(r.get("repaired"))} for r in ds.get("desyncs") or [] for e in r.get("entries") or []]
            return {"role": "host", "head": (st.get("host") or {}).get("lastSeq", 0), "digests": ds.get("digests") or {}, "desyncs": entries}
        if role == "client":
            c = st.get("client") or {}
            return {"role": "client", "joined": bool(c.get("joined")), "syncing": bool(c.get("syncing")), "applied": c.get("applied"),
                    "connected": (st.get("transport") or {}).get("connected", True),
                    "rejected": (c.get("rejectText") or c.get("rejectReason") or "no text") if c.get("rejected") else None}
        return {"role": None}
