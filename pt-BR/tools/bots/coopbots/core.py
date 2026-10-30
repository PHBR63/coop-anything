"""Executor de roteiros cooperativos de vários bots (independente de jogo).

Um roteiro controla 2 a 4 bots simultaneamente, um por instância em execução. Após cada etapa, o executor:
  1. estabiliza: espera toda máquina aplicar último número de atualização do host e manter igualdade por duas consultas,
  2. opcionalmente espera janela sem tráfego (enlaces degradados): nada novo enviado, todas devem convergir e nenhum
     reparo pode ocorrer nessa janela,
  3. captura estado de cada máquina e compara parte `shared` do host com cada cliente,
  4. confere se contadores de dessincronização não aumentaram (reparos podem ser registrados em enlace degradado; erros
     graves nunca) e se execução permanece no orçamento de reparos por minuto,
e, em qualquer falha, escreve tudo necessário à pessoa ou analisador em <outdir>/FAIL-<n>-<step>/ e aborta roteiro.

O que precisa do adaptador de cada máquina (adapter.ActionAdapter): status(), snapshot(), opcional capture(),
mais ações chamadas pelo roteiro. Nada mais sobre o jogo.

Também aqui:
  * etapas retomáveis: roteiro que usa `ctx.run_step(name, body, arrange=...)` pode iniciar na etapa N
    (`from_step`) ou executar só uma (`only_step`). `arrange` coloca mundo no estado esperado.
  * estabilização com falha antecipada: settle() para cedo, com motivo, se nenhuma máquina progrediu na janela de estagnação.
  * escala de tempo: run_playbook pede `set_timescale(x)` a todo adaptador antes da primeira etapa e restaura 1 ao final.
"""
import contextlib
import fnmatch
import json
import os
import re
import time
import traceback
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Sequence, Tuple

from .adapter import MissingAction

MUTANT = os.environ.get("COOPBOTS_MUTANT", "")   # opção de variante só para testes: nosettle | nosnapshot | nocounters | skipispass | nostall | allsteps | noarrange | notimescale (adapter.py: nowhy | nopost)


class StepFailure(Exception):
    "Etapa não fez o esperado pelo roteiro. `reason` é mostrado à pessoa."

    def __init__(self, reason: str, kind: str = "check"):
        super().__init__(reason)
        self.reason = reason
        self.kind = kind          # check | action | settle | snapshot | counters | quiescence | budget | bridge | exception | arrange | timescale


class PlaybookAbort(Exception):
    "Lançada após registrar etapa malsucedida; encerra o roteiro."


@dataclass
class Machine:
    idx: int                      # 0 = host
    name: str                     # "host", "client1", ...
    bot: Any                      # um ActionAdapter
    instance: int = 0

    @property
    def role(self) -> str:
        return "host" if self.idx == 0 else "client"


@dataclass
class StepRecord:
    name: str
    ok: bool
    reason: str = ""
    kind: str = ""
    seconds: float = 0.0
    snapshot: str = "skipped"         # equal | different | invalid | skipped
    number: int = 0                   # número da etapa no roteiro (o que --from-step e --only-step contam)
    counters_delta: Dict[str, Dict[str, int]] = field(default_factory=dict)
    fail_dir: str = ""


# ---------------------------------------------------------------------------------------------
# Contadores. Adaptador mapeia contagens do código de rede para estes nomes em status()["counters"]; outros nomes são
# mantidos nos registros, mas nunca reprovam etapa. Contadores ausentes contam como 0.
REPAIR_COUNTERS = ("mismatches", "repairs", "repaired_effects")   # dessincronização encontrada e reparada: aceitável com tráfego em trânsito em enlace ruim
HARD_COUNTERS = ("bad_messages", "apply_failures", "rebases")    # nunca aceitável: entrada malformada, aplicação malsucedida, cliente forçado a redefinir base
MUST_NOT_RISE = REPAIR_COUNTERS + HARD_COUNTERS


def read_counters(status: dict) -> Dict[str, int]:
    c = (status or {}).get("counters") or {}
    out = {k: int(c.get(k, 0) or 0) for k in MUST_NOT_RISE}
    for k, v in c.items():
        if k not in out and isinstance(v, (int, float)):
            out[k] = int(v)
    return out


def last_seq(status: dict) -> int:
    return int((status or {}).get("seq", 0) or 0)


# ---------------------------------------------------------------------------------------------
class Comparer:
    "Captura estado de cada máquina e compara duas. Substitua se seu jogo tiver comparação melhor."

    def snapshot(self, m: Machine) -> Any:
        raise NotImplementedError

    def diff(self, a: Any, b: Any, ignore: Sequence[str]) -> Tuple[int, List[str]]:
        "Retorna (code, lines): 0 iguais, 1 diferentes, 2 entrada inválida."
        raise NotImplementedError


class DictComparer(Comparer):
    """Compara dict `shared` de duas capturas, caminho a caminho. `ignore` contém padrões fnmatch nas linhas impressas,
    como "shared/refs/*/in_use*". `shared` vazio é recusado (código 2): comparar nada não prova nada."""

    def snapshot(self, m: Machine) -> Any:
        return m.bot.snapshot()

    def diff(self, a, b, ignore):
        sa, sb = a.get("shared"), b.get("shared")
        if not sa or not sb:
            return 2, ["snapshot has an empty 'shared' section: nothing to compare"]
        lines: List[str] = []

        def walk(x, y, path):
            if isinstance(x, dict) and isinstance(y, dict):
                for k in sorted(set(x) | set(y)):
                    if k not in x:
                        lines.append("%s/%s: only on B" % (path, k))
                    elif k not in y:
                        lines.append("%s/%s: only on A" % (path, k))
                    else:
                        walk(x[k], y[k], "%s/%s" % (path, k))
            elif x != y:
                lines.append("%s: %r != %r" % (path, x, y))

        walk(sa, sb, "shared")
        lines = [l for l in lines if not any(fnmatch.fnmatch(l, g) for g in ignore)]
        return (1 if lines else 0), lines


# ---------------------------------------------------------------------------------------------
def _safe(name: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", name)


class Ctx:
    "O que o roteiro vê. Crie com Ctx(machines, comparer, outdir, refs, opts)."

    DEFAULTS = {"settle_s": 20.0, "settle_poll_s": 0.1, "compare": True, "strict_counters": True, "snapdiff_ignore": [],
                "save_snapshots": True, "chaos": None, "quiesce_s": None, "repair_budget_per_min": None, "fast": False,
                "settle_stall_s": None,        # settle(): desiste após este tempo sem avanço; None: max(6, budget / 4), 0: nunca
                "timescale": 1.0,              # multiplicador de velocidade do jogo (run_playbook define pelo adaptador); pausas reduzidas por ele
                "from_step": 0, "only_step": 0}  # executa só algumas etapas (Ctx.run_step); 0: sem limite

    def __init__(self, machines: List[Machine], comparer: Optional[Comparer], outdir: str, refs: Optional[dict] = None,
                 opts: Optional[dict] = None, playbook: str = "", log: Optional[Callable[[str], None]] = None):
        self.machines = machines
        self.comparer = comparer
        self.outdir = outdir
        self.refs = dict(refs or {})
        self.opts = dict(self.DEFAULTS)
        self.opts.update(opts or {})
        self.playbook = playbook
        self.records: List[StepRecord] = []
        self._log = log or (lambda s: None)
        self._fail_n = 0
        self._counter_base: Dict[str, Dict[str, int]] = {}
        self._step_n = 0
        self.notes: List[str] = []
        self.absent: set = set()        # nomes de máquinas que saíram da sessão (excluídas de estabilização, comparação e consultas)
        self._t_start = time.monotonic()
        self._repairs_at_start = 0
        self._pool: Optional[ThreadPoolExecutor] = None
        self.timescale = max(float(self.opts.get("timescale") or 1.0), 1e-3)
        self.from_step = int(self.opts.get("from_step") or 0)
        self.only_step = int(self.opts.get("only_step") or 0)
        self.skipped: List[str] = []    # etapas omitidas por from_step / only_step
        self.ran_selected = 0
        self._arranged = False          # primeira etapa realmente executada numa execução parcial recebe arrange() uma vez

    # ---- quem ----
    @property
    def host(self) -> Machine:
        return self.machines[0]

    @property
    def clients(self) -> List[Machine]:
        return self.machines[1:]

    @property
    def present(self) -> List[Machine]:
        return [m for m in self.machines if m.name not in self.absent]

    def log(self, s: str) -> None:
        self._log("[%s] %s" % (self.playbook, s))

    # ---- utilitários para autores de roteiros ----
    def ref(self, key: str) -> Any:
        if key not in self.refs:
            raise StepFailure("scenario has no ref named %r (have: %s)" % (key, sorted(self.refs)), "check")
        return self.refs[key]

    def must(self, result: Any, what: str) -> Any:
        "Resultados de ações nunca lançam exceções; converte resultado malsucedido em falha de etapa com motivo."
        ok = getattr(result, "ok", result is True)
        if not ok:
            raise StepFailure("%s: %s" % (what, getattr(result, "reason", "") or "no reason given"), "action")
        return result

    def expect(self, cond: Any, msg: str) -> None:
        if not cond:
            raise StepFailure(msg, "check")

    def equip_all(self) -> None:
        "Todos equipam refs['weapon']. Sem essa referência, confia no cenário para armar jogadores."
        w = self.refs.get("weapon")
        if not w:
            return
        for m in self.machines:
            self.must(m.bot.equip(w), "%s equips %s" % (m.name, w))

    def on_all(self, fn: Callable[[Machine], Any], machines: Optional[Sequence[Machine]] = None) -> Dict[str, Any]:
        "Executa fn(machine) em todas as máquinas ao mesmo tempo (threads; cada bot tem conexão própria)."
        ms = list(machines if machines is not None else self.present)
        if self._pool is None:
            self._pool = ThreadPoolExecutor(max_workers=max(4, len(self.machines)), thread_name_prefix="bot")
        futures = [(m.name, self._pool.submit(fn, m)) for m in ms]
        out: Dict[str, Any] = {}
        first: Optional[BaseException] = None
        for name, fut in futures:           # espera toda máquina; depois lança primeiro erro na thread chamadora
            try:
                out[name] = fut.result()
            except BaseException as e:  # noqa: BLE001
                first = first or e
        if first is not None:
            raise first
        return out

    def close(self) -> None:
        if self._pool is not None:
            self._pool.shutdown(wait=True)
            self._pool = None

    def same_everywhere(self, label: str, query: Callable[[Machine], Any], machines: Optional[Sequence[Machine]] = None) -> Any:
        "Faz mesma pergunta a toda máquina e exige respostas idênticas."
        ms = list(machines if machines is not None else self.present)
        vals = {m.name: query(m) for m in ms}
        distinct = {json.dumps(v, sort_keys=True, default=str) for v in vals.values()}
        if len(distinct) != 1:
            raise StepFailure("%s differs between machines: %s" % (label, vals), "check")
        return vals[ms[0].name]

    def optional(self, label: str, fn: Callable[[], Any], default: Any = None) -> Any:
        "Executa verificação que exige ação talvez ausente no adaptador. Se faltar, registra e retorna `default`."
        try:
            return fn()
        except MissingAction as e:
            self.notes.append("%s skipped: %s" % (label, e))
            return default

    def wait_until(self, label: str, pred: Callable[[], bool], timeout_s: float = 10.0, poll_s: float = 0.1) -> None:
        end = time.monotonic() + timeout_s
        while True:
            self._tick()
            if pred():
                return
            if time.monotonic() >= end:
                raise StepFailure("timed out after %gs waiting for: %s" % (timeout_s, label), "check")
            if not self.opts.get("fast"):
                time.sleep(poll_s)

    def pause(self, seconds: float) -> None:
        """Deixa jogo executar por um tempo (mundos simulados: alguns ticks em vez de tempo real). Jogo X vezes mais rápido
        (--timescale X) precisa de apenas 1/X do tempo real para os mesmos segundos de jogo."""
        if self.opts.get("fast"):
            for _ in range(3):
                self._tick()
            return
        end = time.monotonic() + seconds / self.timescale
        while time.monotonic() < end:
            self._tick()
            time.sleep(0.1)

    def _tick(self) -> None:
        "Consulta estados uma vez (também avança mundos simulados)."
        for m in self.machines:
            m.bot.status()

    # ---- estabilização, janela sem tráfego, contadores ----
    def statuses(self) -> Dict[str, dict]:
        return {m.name: m.bot.status() for m in self.present}

    def _stall_window(self, nominal_s: float) -> float:
        "Quanto tempo nada pode avançar antes de settle() desistir cedo (0: nunca)."
        w = self.opts.get("settle_stall_s")
        w = max(6.0, nominal_s / 4.0) if w is None else float(w)
        return 0.0 if (w <= 0 or MUTANT == "nostall") else w

    @staticmethod
    def _progress(st: Dict[str, dict], host_name: str) -> tuple:
        """Tudo que avança enquanto máquinas se atualizam: número de atualização de cada uma e o que o host diz que cada cliente
        confirmou. Contadores de reparos excluídos de propósito: reparo que repete mesma divergência é laço, não progresso."""
        acks = (st[host_name] or {}).get("acks")
        return (tuple((n, last_seq(s)) for n, s in sorted(st.items())), json.dumps(acks, sort_keys=True, default=str))

    def _stuck_detail(self, st: Dict[str, dict], seqs: Dict[str, int], host_ok: bool, mismatch0: int) -> str:
        out = "last update number per machine %s, host synced=%s" % (seqs, host_ok)
        acks = (st[self.host.name] or {}).get("acks")
        if acks:
            out += ", client acks %s" % (acks,)
        rose = read_counters(st[self.host.name])["mismatches"] - mismatch0
        if rose > 0:
            out += ", the host's mismatch counter rose by %d while nothing moved (the same mismatch keeps coming back)" % rose
        return out

    def settle(self, timeout_s: Optional[float] = None) -> None:
        """Espera até todo cliente aplicar último número de atualização do host e manter igualdade por 2 consultas. Falha cedo, com
        motivo, se nada avançou (número de toda máquina, visão do host das confirmações) pela janela de estagnação enquanto
        máquinas ainda divergem: esperar todo orçamento só repetiria a resposta."""
        if MUTANT == "nosettle":
            return
        timeout_s = self.opts["settle_s"] if timeout_s is None else timeout_s
        window = self._stall_window(float(timeout_s))
        t_begin = time.monotonic()
        end = t_begin + timeout_s
        stable, last = 0, {}
        sig, moved_at, mismatch0 = None, t_begin, None
        while True:
            st = self.statuses()
            host_seq = last_seq(st[self.host.name])
            seqs = {m.name: last_seq(st[m.name]) for m in self.present}
            synced = all(seqs[m.name] == host_seq for m in self.present[1:])
            host_ok = st[self.host.name].get("synced", True)
            if mismatch0 is None:
                mismatch0 = read_counters(st[self.host.name])["mismatches"]
            if synced and host_ok and seqs == last:
                stable += 1
                if stable >= 2:
                    return
            else:
                stable = 0
            last = seqs
            now = time.monotonic()
            p = self._progress(st, self.host.name)
            if p != sig:
                sig, moved_at = p, now
            if now >= end:
                raise StepFailure("machines did not converge within %gs: last update number per machine %s, host synced=%s"
                                  % (timeout_s, seqs, host_ok), "settle")
            if window and window < timeout_s and not (synced and host_ok) and now - moved_at >= window:
                raise StepFailure("machines did not converge: no progress for %.1fs (stopped early, the budget was %gs): %s"
                                  % (now - moved_at, timeout_s, self._stuck_detail(st, seqs, host_ok, mismatch0)), "settle")
            if self.opts["settle_poll_s"] > 0:
                time.sleep(self.opts["settle_poll_s"])

    def _read_all_counters(self) -> Dict[str, Dict[str, int]]:
        return {n: read_counters(s) for n, s in self.statuses().items()}

    def quiesce(self) -> None:
        """Regra de enlace degradado: divergências transitórias aceitas com tráfego em trânsito, mas quando nada novo é enviado
        por `quiesce_s`, toda máquina deve convergir e NENHUM reparo pode ocorrer durante janela adicional sem tráfego."""
        q = float(self.opts["quiesce_s"])
        self.pause(q)
        self.settle()
        base = self._read_all_counters()
        self.pause(q)
        self.settle()
        now = self._read_all_counters()
        bad = ["%s.%s +%d" % (n, k, now[n][k] - base[n][k]) for n in now for k in REPAIR_COUNTERS if now[n][k] > base[n][k]]
        if bad:
            raise StepFailure("repairs during the %gs quiet window (must be 0): %s" % (q, "; ".join(bad)), "quiescence")

    def check_repair_budget(self) -> None:
        "Total de reparos por minuto durante execução deve ficar no orçamento (padrão 0: começar estrito)."
        budget = self.opts.get("repair_budget_per_min")
        if budget is None:
            return
        total = sum(c["repairs"] for c in self._read_all_counters().values()) - self._repairs_at_start
        minutes = max((time.monotonic() - self._t_start) / 60.0, 1.0)
        if total / minutes > budget:
            raise StepFailure("repairs per minute %.2f exceed the %s budget %s (%d repairs in %.1f min)"
                              % (total / minutes, self.opts.get("chaos") or "run", budget, total, minutes), "budget")

    def mark_counters(self) -> None:
        self._counter_base = self._read_all_counters()

    def check_counters(self, allow_repairs: bool = False, allow_rebase: bool = False) -> Dict[str, Dict[str, int]]:
        now = self._read_all_counters()
        delta = {n: {k: now[n][k] - self._counter_base.get(n, now[n]).get(k, 0) for k in now[n]} for n in now}
        bad = []
        for n, d in delta.items():
            for k in MUST_NOT_RISE:
                if allow_rebase and k == "rebases":
                    continue
                if (allow_repairs or not self.opts["strict_counters"]) and k in REPAIR_COUNTERS:
                    continue            # dessincronização reparada em enlace degradado é registrada, não reprovada
                if d[k] > 0:
                    bad.append("%s.%s rose by %d" % (n, k, d[k]))
        self._counter_base = now
        if bad and MUTANT != "nocounters":
            raise StepFailure("desync counters rose: " + "; ".join(bad), "counters")
        return delta

    def compare_snapshots(self, tag: str) -> str:
        "Host contra cada cliente. Retorna 'equal', 'skipped' ou lança StepFailure."
        if not self.comparer or not self.opts["compare"]:
            return "skipped"
        if MUTANT == "nosnapshot":
            return "equal"
        snapdir = os.path.join(self.outdir, "snap", _safe(tag))
        os.makedirs(snapdir, exist_ok=True)
        snaps = {}
        for m in self.present:
            snaps[m.name] = self.comparer.snapshot(m)
            with open(os.path.join(snapdir, m.name + ".json"), "w", encoding="utf-8") as f:
                json.dump(snaps[m.name], f, indent=1, sort_keys=True, default=str)
        problems = []
        for c in self.present[1:]:
            code, lines = self.comparer.diff(snaps[self.host.name], snaps[c.name], self.opts["snapdiff_ignore"])
            if code == 2:
                raise StepFailure("the snapshot comparison refused the input (%s): %s" % (c.name, "; ".join(lines[:3])), "snapshot")
            if code == 1:
                problems.append("host vs %s: %d difference(s), first: %s" % (c.name, len(lines), "; ".join(lines[:3])))
        if problems:
            raise StepFailure("snapshots differ. " + " | ".join(problems), "snapshot")
        return "equal"

    # ---- etapas ----
    @contextlib.contextmanager
    def step(self, name: str, *, settle: bool = True, compare: bool = True, allow_repairs: bool = False, allow_rebase: bool = False):
        """with ctx.step("both shoot"): ... Ao sair: estabilização, janela sem tráfego, comparação de capturas, contadores.
        Qualquer falha aborta roteiro após salvar evidências."""
        self._step_n += 1
        t0 = time.monotonic()
        rec = StepRecord(name=name, ok=False, number=self._step_n)
        label = "%02d-%s" % (self._step_n, name)
        self.log("step " + label)
        try:
            if not self._counter_base:
                self.mark_counters()
                self._repairs_at_start = sum(c["repairs"] for c in self._counter_base.values())
            yield self
            if settle:
                self.settle()
                if self.opts.get("quiesce_s"):
                    self.quiesce()
            if compare:
                rec.snapshot = self.compare_snapshots(label)
            rec.counters_delta = self.check_counters(allow_repairs, allow_rebase)
            self.check_repair_budget()
            rec.ok = True
        except StepFailure as e:
            rec.reason, rec.kind = e.reason, e.kind
            if e.kind == "snapshot":
                rec.snapshot = "different"
        except PlaybookAbort:
            raise
        except MissingAction as e:
            rec.reason, rec.kind = "%s (a playbook step needs it; list it in the playbook's `requires`)" % e, "missing"
        except Exception as e:  # noqa: BLE001  a bot or link crash is also a failed step, with a trace
            rec.reason, rec.kind = "%s: %s" % (type(e).__name__, e), "exception"
            self.notes.append(traceback.format_exc())
        finally:
            rec.seconds = round(time.monotonic() - t0, 3)
            if not rec.ok:
                rec.fail_dir = self.save_failure(label, rec)
            self.records.append(rec)
        if not rec.ok:
            self.log("FAIL %s: %s" % (label, rec.reason))
            raise PlaybookAbort(rec.reason)

    # ---- etapas retomáveis: --from-step N / --only-step N ----
    @property
    def partial(self) -> bool:
        "True se só algumas etapas do roteiro executam (etapa 4 malsucedida repetida sem 1 a 3)."
        return self.only_step > 0 or self.from_step > 1

    def selected(self, n: int) -> bool:
        if MUTANT == "allsteps":
            return True
        if self.only_step > 0:
            return n == self.only_step
        return n >= max(self.from_step, 1)

    def run_step(self, name: str, body: Callable[[], Any], *, arrange: Optional[Callable[[], Any]] = None, **step_kw) -> None:
        """Etapa que execução parcial pode pular ou iniciar: `with ctx.step(name, **step_kw): body()`, omitida
        se seu número não for selecionado. `arrange` coloca mundo no estado esperado. Deve ser idempotente e
        usar só ações de bots e operações de cenários. Executa dentro da etapa, uma vez, na primeira realmente executada de
        uma execução parcial; nunca numa completa, que se comporta como sem ela. Etapas seguintes usam o que anteriores
        fizeram. Se arrange não conseguir, lança StepFailure(reason, "arrange") e informa o que fazer (recarregar cenário)."""
        n = self._step_n + 1
        if not self.selected(n):
            self._step_n = n
            self.skipped.append("%02d-%s" % (n, name))
            self.log("skip step %02d-%s" % (n, name))
            return
        first = self.partial and not self._arranged
        self.ran_selected += 1
        with self.step(name, **step_kw):
            if first:
                self._arranged = True
                if arrange is not None and MUTANT != "noarrange":
                    self.log("arranging the world for step %02d-%s" % (n, name))
                    arrange()
            body()

    # ---- artefatos de falha ----
    def save_failure(self, label: str, rec: StepRecord) -> str:
        self._fail_n += 1
        d = os.path.join(self.outdir, "FAIL-%d-%s" % (self._fail_n, _safe(label)))
        os.makedirs(d, exist_ok=True)
        manifest: Dict[str, Any] = {"playbook": self.playbook, "step": label, "reason": rec.reason, "kind": rec.kind,
                                    "machines": [], "chaos": self.opts.get("chaos")}
        for m in self.machines:
            info: Dict[str, Any] = {"name": m.name, "role": m.role, "instance": m.instance}
            try:
                info["status"] = m.bot.status()
            except Exception as e:  # noqa: BLE001
                info["status_error"] = str(e)
            try:
                info["capture"] = m.bot.capture(os.path.join(d, m.name))
            except Exception as e:  # noqa: BLE001
                info["capture_error"] = str(e)
            try:
                info["recent_actions"] = m.bot.recent_actions(8)      # últimas ações com motivos
            except Exception:  # noqa: BLE001  an adapter without the action log
                pass
            try:
                if self.comparer and self.opts["save_snapshots"]:
                    sp = os.path.join(d, m.name + ".snapshot.json")
                    with open(sp, "w", encoding="utf-8") as f:
                        json.dump(self.comparer.snapshot(m), f, indent=1, sort_keys=True, default=str)
                    info["snapshot"] = sp
            except Exception as e:  # noqa: BLE001
                info["snapshot_error"] = str(e)
            manifest["machines"].append(info)
        manifest["steps_so_far"] = [r.__dict__ for r in self.records] + [rec.__dict__]
        manifest["notes"] = self.notes[-3:]
        with open(os.path.join(d, "failure.json"), "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=1, default=str)
        return d


# ---------------------------------------------------------------------------------------------
class Playbook:
    "Crie subclasse, defina atributos de classe e implemente run(ctx)."

    name = ""
    summary = ""
    min_players = 2
    max_players = 4
    needs_refs: Tuple[str, ...] = ()          # chaves obrigatórias no bloco `refs` do cenário
    requires: Tuple[str, ...] = ()            # métodos de adaptador exigidos em toda máquina; senão, roteiro pulado
    snapdiff_ignore: Tuple[str, ...] = ()     # padrões fnmatch para linhas de capturas que podem diferir
    allow_repairs = False
    resumable = False                         # True: toda etapa passa por ctx.run_step com arrange(), então --from-step / --only-step funcionam

    def run(self, ctx: Ctx) -> None:
        raise NotImplementedError


@dataclass
class RunResult:
    playbook: str
    status: str                       # pass | fail | skip
    steps: List[StepRecord]
    outdir: str
    reason: str = ""
    skipped: List[str] = field(default_factory=list)     # etapas omitidas por --from-step / --only-step
    from_step: int = 0
    only_step: int = 0
    timescale: Optional[dict] = None   # {"requested": X, "set": {máquina: motivo ou ""}, "reset": {...}} quando X != 1

    @property
    def ok(self) -> bool:
        return self.status == "pass"

    def to_json(self) -> dict:
        out = {"playbook": self.playbook, "status": self.status, "ok": self.ok, "reason": self.reason, "outdir": self.outdir,
               "steps": [s.__dict__ for s in self.steps]}
        if self.skipped or self.from_step or self.only_step:
            out.update({"skipped": self.skipped, "from_step": self.from_step, "only_step": self.only_step})
        if self.timescale is not None:
            out["timescale"] = self.timescale
        return out


def format_timescale(x: float) -> str:
    return "%g" % x


def _set_timescale(machines: List[Machine], x: float, verify: bool = True) -> Dict[str, str]:
    """Pede velocidade x a toda máquina. -> {nome: "" se aceitou, senão motivo}. Se adaptador puder reler velocidade
    (`timescale()`), também informa cópia que aceitou chamada mas executa em outra velocidade."""
    out: Dict[str, str] = {}
    for m in machines:
        try:
            r = m.bot.set_timescale(x)
            if not r:
                out[m.name] = "refused: %s" % (r.reason or "no reason given")
                continue
            out[m.name] = ""
            if verify and m.bot.supports("timescale"):
                got = float(m.bot.timescale())
                if abs(got - x) > 1e-6 * max(1.0, abs(x)):
                    out[m.name] = "accepted the speed but reports %s instead of %s" % (format_timescale(got), format_timescale(x))
        except Exception as e:  # noqa: BLE001
            out[m.name] = "%s: %s" % (type(e).__name__, e)
    return out


def run_playbook(pb: Playbook, machines: List[Machine], comparer: Optional[Comparer], outdir: str,
                 refs: Optional[dict] = None, opts: Optional[dict] = None, log: Optional[Callable[[str], None]] = None) -> RunResult:
    n = len(machines)
    if not (pb.min_players <= n <= pb.max_players):
        return RunResult(pb.name, "fail", [], outdir, "%s needs %d to %d players, got %d" % (pb.name, pb.min_players, pb.max_players, n))
    missing = [k for k in pb.needs_refs if k not in (refs or {})]
    if missing:
        return RunResult(pb.name, "fail", [], outdir, "scenario is missing refs %s" % missing)
    lacking = sorted({r for r in pb.requires for m in machines if not m.bot.supports(r)})
    if lacking:
        return RunResult(pb.name, "pass" if MUTANT == "skipispass" else "skip", [], outdir, "adapter does not implement: %s" % ", ".join(lacking))
    o = dict(opts or {})
    scale = max(float(o.get("timescale") or 1.0), 1e-3)
    if scale != 1.0:
        no_scale = [m.name for m in machines if not m.bot.supports("set_timescale")]
        if no_scale:
            return RunResult(pb.name, "fail", [], outdir, "--timescale %s needs the adapter action set_timescale; missing on %s"
                             % (format_timescale(scale), ", ".join(no_scale)))
    os.makedirs(outdir, exist_ok=True)
    o["snapdiff_ignore"] = list(o.get("snapdiff_ignore", [])) + list(pb.snapdiff_ignore)
    ctx = Ctx(machines, comparer, outdir, refs, o, pb.name, log)
    if ctx.partial and not pb.resumable:
        return RunResult(pb.name, "fail", [], outdir, "%s cannot run from a later step (--from-step / --only-step): its steps have no "
                         "arrange part yet; run it whole" % pb.name, from_step=ctx.from_step, only_step=ctx.only_step)
    reason = ""
    scale_info: Optional[dict] = None
    try:
        try:
            if ctx.timescale != 1.0:
                # Após preparar cenário (feito pelo chamador): daqui em diante jogo executa ctx.timescale vezes mais rápido. Uma cópia por
                # velocidade distinta seria dessincronização por si só; cópia que recusa para execução antes de qualquer etapa.
                scale_info = {"requested": ctx.timescale, "set": {}, "reset": {}}
                if MUTANT != "notimescale":
                    scale_info["set"] = _set_timescale(machines, ctx.timescale)
                refused = {k: v for k, v in scale_info["set"].items() if v}
                if refused:
                    raise StepFailure("could not set the game speed (set_timescale %s): %s" % (format_timescale(ctx.timescale), refused), "timescale")
            pb.run(ctx)
            if ctx.partial and ctx.ran_selected == 0:
                raise StepFailure("no step was selected: %s has %d steps, --from-step %s --only-step %s"
                                  % (pb.name, ctx._step_n, ctx.from_step or "-", ctx.only_step or "-"), "check")
            ok = all(r.ok for r in ctx.records) and bool(ctx.records)
            if not ctx.records:
                reason = "playbook ran no steps"
        except PlaybookAbort as e:
            ok, reason = False, str(e)
        except Exception as e:  # noqa: BLE001  a failure outside a step block
            kind = e.kind if isinstance(e, StepFailure) else "exception"
            text = e.reason if isinstance(e, StepFailure) else "%s: %s" % (type(e).__name__, e)
            rec = StepRecord("(outside step)", False, text, kind)
            rec.fail_dir = ctx.save_failure("outside-step", rec)
            ctx.records.append(rec)
            ok, reason = False, text
    finally:
        ctx.close()
        if scale_info is not None:        # também após etapa malsucedida e Ctrl-C: nunca deixa cópia em outra velocidade
            scale_info["reset"] = _set_timescale(machines, 1.0)
    stuck = {k: v for k, v in (scale_info or {}).get("reset", {}).items() if v}
    if stuck:
        ok = False
        reason = (reason + "; " if reason else "") + "could not put the game speed back to 1: %s" % stuck
    res = RunResult(pb.name, "pass" if ok else "fail", ctx.records, outdir, reason, ctx.skipped, ctx.from_step, ctx.only_step, scale_info)
    with open(os.path.join(outdir, "result.json"), "w", encoding="utf-8") as f:
        json.dump(res.to_json(), f, indent=1, default=str)
    return res
