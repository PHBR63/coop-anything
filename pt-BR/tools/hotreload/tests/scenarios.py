"""Cenários de troca: iniciam host de teste (substituto do jogo), executam ferramenta de troca nele e conferem o que
ocorreu. Cada cenário lança exceção se algo estiver errado. run_tests.py executa cada um sem alterações (deve passar)
e uma vez por variante mutante que protege (deve falhar).

Processos host são iniciados por estes cenários e só encerrados por pid, pelo objeto Popen que os iniciou.
Nada mais na máquina é tocado.
"""
from __future__ import annotations

import contextlib
import hashlib
import io
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple

HERE = Path(__file__).resolve().parent
TOOL = HERE.parent
sys.path.insert(0, str(TOOL))
import hotreload  # noqa: E402


class SetupError(Exception):
    "O próprio aparato de teste quebrou (host não iniciou). Nunca conta como variante detectada."


def expect(cond: Any, msg: str) -> None:
    if not cond:
        raise AssertionError(msg)


def wait_for(fn: Callable[[], Any], timeout_s: float, what: str) -> Any:
    end = time.monotonic() + timeout_s
    last: Any = None
    while time.monotonic() < end:
        try:
            last = fn()
        except Exception:
            last = None
        if last:
            return last
        time.sleep(0.02)
    raise AssertionError(f"timed out waiting for {what}")


class Ctx:
    "Onde está compilação, destino das pastas de cenário e falha (se houver) ativada nesta execução."

    def __init__(self, bin_dir: Path, work_root: Path, env: Optional[Dict[str, str]] = None, faults: Tuple[str, ...] = ()):
        self.bin = Path(bin_dir)
        self.work = Path(work_root)
        self.env = dict(env or {})
        self.faults = set(faults)
        self._n = 0

    def dll(self, name: str) -> Path:
        return self.bin / (name + ".dll")

    def new_dir(self, label: str) -> Path:
        self._n += 1
        d = self.work / f"{label}-{self._n}"
        d.mkdir(parents=True, exist_ok=True)
        return d


_host_count = 0


class Host:
    "Um processo host de teste com pasta própria, arquivo de núcleo e pipe de controle."

    def __init__(self, ctx: Ctx, core: str, mode: str = "split", label: str = "host"):
        global _host_count
        _host_count += 1
        self.ctx = ctx
        self.dir = ctx.new_dir(label)
        self.pipe = f"hr-test-{os.getpid()}-{_host_count}"
        self.core_path = self.dir / "core.dll"
        shutil.copyfile(ctx.dll(core), self.core_path)
        self.cache = self.dir / "cache"
        env = dict(os.environ)
        env["HOTRELOAD_DRAIN_MS"] = "300"
        env.update(ctx.env)
        self.err_file = open(self.dir / "host.err", "wb")
        self.proc = subprocess.Popen(
            [str(ctx.bin / "hotreload_test_host.exe"), "--loader", str(ctx.dll("hotreload_loader")), "--core", str(self.core_path),
             "--cache", str(self.cache), "--pipe", self.pipe, "--mode", mode, "--frame-ms", "3"],
            env=env, stdout=subprocess.DEVNULL, stderr=self.err_file)
        self.mode = mode

    def __enter__(self) -> "Host":
        try:
            def up() -> bool:
                if self.proc.poll() is not None:
                    raise SetupError(f"the test host exited with code {self.proc.returncode} before it was ready: "
                                     + (self.dir / "host.err").read_text(errors="replace"))
                if self.mode != "split":
                    return bool(self.call("host.info"))
                st = self.call("dev.status")
                return bool(st.get("loaded")) and bool(self.call("example.state"))

            end = time.monotonic() + 15
            while True:
                try:
                    if up():
                        break
                except SetupError:
                    raise
                except Exception:
                    pass
                if time.monotonic() > end:
                    raise SetupError("the test host did not become ready in 15 s: " + (self.dir / "host.err").read_text(errors="replace"))
                time.sleep(0.05)
        except BaseException:
            self.stop()
            raise
        return self

    def __exit__(self, *exc: Any) -> None:
        self.stop()

    def call(self, method: str, params: Optional[Dict[str, Any]] = None, timeout_s: float = 10.0) -> Any:
        "Uma solicitação na sua própria conexão curta (o pipe atende um cliente por vez, e a ferramenta de troca precisa dele)."
        c = hotreload.PipeClient.connect(self.pipe, wait_s=5.0)
        try:
            return c.call(method, params, timeout_s=timeout_s)
        finally:
            c.close()

    def state(self) -> Dict[str, Any]:
        return self.call("example.state")

    def status(self) -> Dict[str, Any]:
        return self.call("dev.status")

    def info(self) -> Dict[str, Any]:
        return self.call("host.info")

    def log_text(self) -> str:
        p = self.cache / "hotreload.log"
        return p.read_text(errors="replace") if p.exists() else ""

    def core_hash(self) -> str:
        return hashlib.sha256(self.core_path.read_bytes()).hexdigest()

    def stop(self) -> None:
        if self.proc.poll() is None:
            try:
                self.call("host.quit", timeout_s=3)
            except Exception:
                pass
            try:
                self.proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.proc.kill()   # nosso próprio processo, por seu handle Popen
                self.proc.wait(timeout=5)
        try:
            self.err_file.close()
        except Exception:
            pass


def swap_args(ctx: Ctx, pipes: List[str], dll: Path, *extra: str) -> List[str]:
    a = ["swap"]
    for p in pipes:
        a += ["--pipe", p]
    return a + ["--dll", str(dll), "--reload-timeout-s", "20", "--replace-wait-s", "1", "--connect-wait-s", "0.3"] + list(extra)


def run_client(ctx: Ctx, args: List[str]) -> Tuple[int, Any, str]:
    """Execute ferramenta de troca. Cenário com falha ligada executa neste processo (para defini-la); qualquer
    outro executa como usuário: `python -I hotreload.py ...` num processo novo. Retorna (código de saída, relatório, stderr)."""
    if ctx.faults:
        hotreload.FAULTS.clear()
        hotreload.FAULTS.update(ctx.faults)
        out, err = io.StringIO(), io.StringIO()
        try:
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                code = hotreload.main(args)
        finally:
            hotreload.FAULTS.clear()
        text, errtext = out.getvalue(), err.getvalue()
    else:
        p = subprocess.run([sys.executable, "-I", str(TOOL / "hotreload.py")] + args, capture_output=True, text=True,
                           encoding="utf-8", errors="replace", timeout=120)
        code, text, errtext = p.returncode, p.stdout, p.stderr
    try:
        rep = json.loads(text)
    except ValueError:
        rep = None
    return code, rep, errtext


def first_copy(rep: Any) -> Dict[str, Any]:
    expect(isinstance(rep, dict) and rep.get("copies"), f"no copies in the report: {rep!r}")
    return rep["copies"][0]


# ----------------------------------------------------------------------------------------------------- cenários
def swap_carries_state(ctx: Ctx) -> None:
    "v1 para v2 (layout 2 migra layout 1): estado mantido, id da compilação mudou, threads e host continuaram rodando."
    with Host(ctx, "core_v1") as h:
        h.call("example.set", {"label": "hello"})
        s0 = wait_for(lambda: (lambda s: s if s["counter"] > 30 and s["ticks"] > 10 else None)(h.state()), 15, "the example core to count")
        st0, i0 = h.status(), h.info()
        code, rep, err = run_client(ctx, swap_args(ctx, [h.pipe], ctx.dll("core_v2")))
        expect(code == 0, f"swap exit {code}: {rep} {err}")
        c = first_copy(rep)
        expected = hotreload.build_id_of(ctx.dll("core_v2"))
        expect(c["status"] == "swapped", f"status {c['status']}")
        expect(c["buildBefore"] != expected and c["buildAfter"] == expected, f"build id {c['buildBefore']} -> {c['buildAfter']}, wanted {expected}")
        expect(h.status()["buildId"] == expected, "dev.status does not report the new build id")
        expect(c["generationAfter"] == st0["generation"] + 1, f"generation {c['generationBefore']} -> {c['generationAfter']}")
        s1 = h.state()
        expect(s1["layout"] == 2 and s1["build"] == 2, f"the new core is not running: {s1}")
        expect(s1["counter"] >= s0["counter"], f"counter was not carried over: {s0['counter']} -> {s1['counter']}")
        expect(s1["ticks"] >= s0["ticks"], f"ticks were not carried over: {s0['ticks']} -> {s1['ticks']}")
        expect(s1["label"] == "hello", f"label was not carried over: {s1['label']!r}")
        expect(s1["step"] == 1 and s1["isReload"] == 1 and s1["generation"] == 2, f"unexpected state after the swap: {s1}")
        time.sleep(0.5)
        s2 = h.state()
        expect(s2["counter"] > s1["counter"] and s2["ticks"] > s1["ticks"], "the new core does not keep counting")
        expect(s2["workerAlive"] and s2["tickerRunning"], "the new core's threads are not running")
        expect(s2["messages"] > 0, "the host's messages do not reach the new core")
        i1 = h.info()
        expect(i1["pid"] == i0["pid"] and i1["frames"] > i0["frames"], "the host process did not keep running")
        rs = h.call("reload.state")
        expect(rs["migrated"] == 1 and not rs["failures"] and not rs["leaks"], f"reload.state: {rs}")
        expect("warnings" not in c, f"unexpected warnings: {c.get('warnings')}")


def swap_two_copies(ctx: Ctx) -> None:
    "Duas cópias ativas trocadas uma após outra, cada uma com seu estado."
    with Host(ctx, "core_v1", label="a") as a, Host(ctx, "core_v1", label="b") as b:
        a.call("example.set", {"label": "alpha"})
        b.call("example.set", {"label": "beta"})
        code, rep, err = run_client(ctx, swap_args(ctx, [a.pipe, b.pipe], ctx.dll("core_v2")))
        expect(code == 0, f"swap exit {code}: {rep} {err}")
        expect([c["status"] for c in rep["copies"]] == ["swapped", "swapped"], f"statuses: {rep['copies']}")
        expect(a.state()["label"] == "alpha" and b.state()["label"] == "beta", "labels were mixed up between the copies")
        expect(a.state()["build"] == 2 and b.state()["build"] == 2, "a copy still runs the old build")


def unchanged_and_forced(ctx: Ctx) -> None:
    "Mesmos bytes novamente: nada acontece. Com --force: recarga que comprova execução."
    with Host(ctx, "core_v1") as h:
        st0 = h.status()
        code, rep, err = run_client(ctx, swap_args(ctx, [h.pipe], ctx.dll("core_v1")))
        expect(code == 0, f"exit {code}: {rep} {err}")
        c = first_copy(rep)
        expect(c["status"] == "unchanged" and h.status()["generation"] == st0["generation"], f"expected no reload: {c}")
        counter = h.state()["counter"]
        code, rep, err = run_client(ctx, swap_args(ctx, [h.pipe], ctx.dll("core_v1"), "--force"))
        expect(code == 0, f"forced exit {code}: {rep} {err}")
        c = first_copy(rep)
        expect(c["status"] == "swapped" and c["generationAfter"] == st0["generation"] + 1, f"forced swap: {c}")
        expect(c["buildAfter"] == c["buildBefore"], "a forced reload of the same bytes changed the build id")
        expect(h.state()["counter"] >= counter, "state was lost by the forced reload")


def dry_run_changes_nothing(ctx: Ctx) -> None:
    with Host(ctx, "core_v1") as h:
        before_hash, st0 = h.core_hash(), h.status()
        report_file = h.dir / "report.json"
        code, rep, err = run_client(ctx, swap_args(ctx, [h.pipe], ctx.dll("core_v2"), "--dry-run", "--out", str(report_file)))
        expect(code == 0, f"exit {code}: {rep} {err}")
        expect(first_copy(rep)["status"] == "would swap", f"dry run said {first_copy(rep)['status']}")
        expect(json.loads(report_file.read_text(encoding="utf-8")) == rep, "--out did not write the report that was printed")
        expect(h.core_hash() == before_hash, "--dry-run changed the core file")
        expect(not list(h.dir.glob("*.swap")), "--dry-run left a temporary file")
        expect(h.status()["generation"] == st0["generation"] and h.state()["layout"] == 1, "--dry-run reloaded the core")


def status_command(ctx: Ctx) -> None:
    "`status` imprime dev.status das cópias ativas e sai com 2 para uma incapaz de recarregar a quente."
    with Host(ctx, "core_v1") as h, Host(ctx, "core_v1", mode="monolith", label="mono") as mono:
        code, rows, err = run_client(ctx, ["status", "--pipe", h.pipe])
        expect(code == 0 and rows[0]["status"]["buildId"] == h.status()["buildId"], f"exit {code}: {rows}")
        code, rows, err = run_client(ctx, ["status", "--pipe", h.pipe, "--pipe", mono.pipe])
        expect(code == 2 and "status" in rows[0] and "monolith" in rows[1]["error"], f"exit {code}: {rows}")


def refuse_no_control_channel(ctx: Ctx) -> None:
    code, rep, err = run_client(ctx, swap_args(ctx, ["hr-test-nobody-listens"], ctx.dll("core_v1")))
    expect(code == 2, f"exit {code} (wanted 2 for a refusal): {rep}")
    expect("pipe" in rep["refused"], f"reason does not name the pipe: {rep['refused']}")
    expect("refused" in err, "the reason is not on stderr")


def refuse_monolith(ctx: Ctx) -> None:
    "Compilação sem carregador: pipe responde, mas não há dev.reload."
    with Host(ctx, "core_v1", mode="monolith") as h:
        before = h.core_hash()
        code, rep, err = run_client(ctx, swap_args(ctx, [h.pipe], ctx.dll("core_v2")))
        expect(code == 2, f"exit {code} (wanted 2): {rep}")
        expect("monolith" in rep["refused"], f"reason: {rep['refused']}")
        expect(h.core_hash() == before, "a refused swap changed a file")


def refuse_old_loader(ctx: Ctx) -> None:
    "Carregador sem ids de compilação: recarga não pode ser comprovada, recusada antes de tocar arquivos."
    with Host(ctx, "core_v1", mode="oldloader") as h:
        before = h.core_hash()
        code, rep, err = run_client(ctx, swap_args(ctx, [h.pipe], ctx.dll("core_v2")))
        expect(code == 2, f"exit {code} (wanted 2): {rep}")
        expect("buildId" in rep["refused"], f"reason: {rep['refused']}")
        expect(h.core_hash() == before, "a refused swap changed the core file")


def refuse_not_a_core(ctx: Ctx) -> None:
    "DLL do carregador e arquivo de texto não são núcleos. Recusados antes de ferramenta procurar jogo."
    code, rep, err = run_client(ctx, swap_args(ctx, ["hr-test-nobody-listens"], ctx.dll("hotreload_loader")))
    expect(code == 2 and "HotCore_Init" in rep["refused"], f"loader DLL: exit {code}, {rep}")
    junk = ctx.new_dir("junk") / "notes.txt"
    junk.write_text("not a dll")
    code, rep, err = run_client(ctx, swap_args(ctx, ["hr-test-nobody-listens"], junk))
    expect(code == 2 and "not a DLL" in rep["refused"], f"text file: exit {code}, {rep}")


def refuse_own_core_file(ctx: Ctx) -> None:
    with Host(ctx, "core_v1") as h:
        code, rep, err = run_client(ctx, swap_args(ctx, [h.pipe], h.core_path))
        expect(code == 2 and "own core file" in rep["refused"], f"exit {code}: {rep}")


def refuse_outside_root(ctx: Ctx) -> None:
    with Host(ctx, "core_v1") as h:
        before = h.core_hash()
        elsewhere = ctx.new_dir("elsewhere")
        code, rep, err = run_client(ctx, swap_args(ctx, [h.pipe], ctx.dll("core_v2"), "--root", str(elsewhere)))
        expect(code == 2 and "outside --root" in rep["refused"], f"exit {code}: {rep}")
        expect(h.core_hash() == before, "a refused swap changed the core file")
        code, rep, err = run_client(ctx, swap_args(ctx, [h.pipe], ctx.dll("core_v2"), "--root", str(h.dir), "--dry-run"))
        expect(code == 0, f"a core file inside --root was refused: {rep}")


def all_or_nothing(ctx: Ctx) -> None:
    "Uma cópia não pode recarregar, então a que poderia também fica intocada."
    with Host(ctx, "core_v1", label="good") as good, Host(ctx, "core_v1", mode="monolith", label="mono") as mono:
        before, gen = good.core_hash(), good.status()["generation"]
        code, rep, err = run_client(ctx, swap_args(ctx, [good.pipe, mono.pipe], ctx.dll("core_v2")))
        expect(code == 2, f"exit {code} (wanted 2): {rep}")
        expect(good.core_hash() == before and good.status()["generation"] == gen and good.state()["layout"] == 1,
               "the copy that could reload was changed although another one was refused")


def version_bump_without_migrate(ctx: Ctx) -> None:
    "Layout 3 sem migração: estado começa novo, troca funciona e relatório informa."
    with Host(ctx, "core_v1") as h:
        h.call("example.set", {"label": "will be lost"})
        s0 = wait_for(lambda: (lambda s: s if s["counter"] > 30 else None)(h.state()), 15, "the example core to count")
        code, rep, err = run_client(ctx, swap_args(ctx, [h.pipe], ctx.dll("core_v3_nomigrate")))
        expect(code == 0, f"exit {code}: {rep} {err}")
        c = first_copy(rep)
        expect(c["status"] == "swapped", f"status {c['status']}")
        expect(c.get("warnings") and "started fresh" in c["warnings"][0], f"no warning about the lost state: {c}")
        s1 = h.state()
        expect(s1["layout"] == 3 and s1["label"] == "unset" and s1["counter"] < s0["counter"], f"state was not started fresh: {s1}")
        rs = h.call("reload.state")
        expect(rs["fresh"] == 1 and rs["restored"] == 0 and not rs["failures"], f"reload.state: {rs}")


def unregistered_thread_refuses(ctx: Ctx) -> None:
    """A LIÇÃO: thread pertencente ao núcleo não registrada impede drenagem bem-sucedida. Recarga
    recusada de forma limpa: núcleo anterior segue com estado, relatório identifica drenagem."""
    with Host(ctx, "core_unregistered") as h:
        s0 = wait_for(lambda: (lambda s: s if s["counter"] > 10 else None)(h.state()), 15, "the example core to count")
        st0 = h.status()
        code, rep, err = run_client(ctx, swap_args(ctx, [h.pipe], ctx.dll("core_v1")))
        expect(code == 1, f"exit {code} (wanted 1, a failed swap): {rep} {err}")
        c = first_copy(rep)
        expect(c["status"] == "failed" and "drain" in c["detail"], f"the report does not name the drain: {c}")
        expect("still inside" in c["detail"], f"the report does not say a thread is still inside: {c['detail']}")
        st1 = h.status()
        expect(st1["generation"] == st0["generation"] and st1["buildId"] == st0["buildId"], "the refused reload changed the running core")
        a = h.state()
        time.sleep(0.3)
        b = h.state()
        expect(a["build"] == 4 and b["counter"] > a["counter"] >= s0["counter"], "the old core does not keep running")
        expect(b["tickerRunning"] and b["workerAlive"], "the old core's threads were stopped by a refused reload")
        expect(h.call("reload.state")["drain"]["drained"] is False, "reload.state does not report the refused drain")
        expect("REFUSED by the drain" in h.log_text(), "the loader log does not mention the refusal")


def save_failure_vetoes(ctx: Ctx) -> None:
    "Participante incapaz de salvar veta recarga antes de parar qualquer coisa."
    with Host(ctx, "core_failsave") as h:
        s0 = wait_for(lambda: (lambda s: s if s["counter"] > 10 else None)(h.state()), 15, "the example core to count")
        st0 = h.status()
        code, rep, err = run_client(ctx, swap_args(ctx, [h.pipe], ctx.dll("core_v1")))
        expect(code == 1, f"exit {code} (wanted 1): {rep} {err}")
        expect("save flaky" in first_copy(rep)["detail"], f"the report does not name the participant: {first_copy(rep)}")
        st1 = h.status()
        expect(st1["generation"] == st0["generation"] and st1["buildId"] == st0["buildId"], "the vetoed reload changed the running core")
        a = h.state()
        time.sleep(0.3)
        b = h.state()
        expect(b["counter"] > a["counter"] >= s0["counter"] and b["tickerRunning"] and b["workerAlive"], "the old core does not keep running")


def bad_core_rolls_back(ctx: Ctx) -> None:
    "Novo núcleo cujo init falha: carregador mapeia anterior novamente, com seu estado."
    with Host(ctx, "core_v1") as h:
        h.call("example.set", {"label": "keep me"})
        s0 = wait_for(lambda: (lambda s: s if s["counter"] > 30 else None)(h.state()), 15, "the example core to count")
        st0 = h.status()
        code, rep, err = run_client(ctx, swap_args(ctx, [h.pipe], ctx.dll("core_badinit")))
        expect(code == 1, f"exit {code} (wanted 1): {rep} {err}")
        expect("rolled back" in first_copy(rep)["detail"], f"the report does not say the old core runs again: {first_copy(rep)}")
        st1 = h.status()
        expect(st1["loaded"] and st1["last"]["rolledBack"], f"status after the rollback: {st1}")
        expect(st1["generation"] == st0["generation"] and st1["buildId"] == st0["buildId"], "the rollback is not the previous build")
        s1 = h.state()
        expect(s1["build"] == 1 and s1["label"] == "keep me" and s1["counter"] >= s0["counter"], f"the rolled back core lost its state: {s1}")
        expect(s1["workerAlive"] and s1["tickerRunning"], "the rolled back core has no threads")
        # próxima troca válida funciona a partir daí
        code, rep, err = run_client(ctx, swap_args(ctx, [h.pipe], ctx.dll("core_v2")))
        expect(code == 0 and h.state()["build"] == 2, f"a swap after a rollback failed: exit {code} {rep}")


SCENARIOS: List[Tuple[str, Callable[[Ctx], None]]] = [
    ("swap_carries_state", swap_carries_state),
    ("swap_two_copies", swap_two_copies),
    ("unchanged_and_forced", unchanged_and_forced),
    ("dry_run_changes_nothing", dry_run_changes_nothing),
    ("status_command", status_command),
    ("refuse_no_control_channel", refuse_no_control_channel),
    ("refuse_monolith", refuse_monolith),
    ("refuse_old_loader", refuse_old_loader),
    ("refuse_not_a_core", refuse_not_a_core),
    ("refuse_own_core_file", refuse_own_core_file),
    ("refuse_outside_root", refuse_outside_root),
    ("all_or_nothing", all_or_nothing),
    ("version_bump_without_migrate", version_bump_without_migrate),
    ("unregistered_thread_refuses", unregistered_thread_refuses),
    ("save_failure_vetoes", save_failure_vetoes),
    ("bad_core_rolls_back", bad_core_rolls_back),
]

# Variantes mutantes detectadas por cenário: (nome, número HOTRELOAD_MUT ou "", falha cliente ou "", cenário protetor).
TWINS: List[Tuple[str, str, str, str]] = [
    ("drain_off", "1", "", "unregistered_thread_refuses"),
    ("adopt_ignored", "2", "", "swap_carries_state"),
    ("managed_ids_ignored", "3", "", "swap_carries_state"),
    ("no_cache_copy", "4", "", "swap_carries_state"),          # compilação travada: ferramenta de troca não pode sobrescrever arquivo mapeado
    ("stale_build_id", "5", "", "swap_carries_state"),
    ("version_ignored", "6", "", "swap_carries_state"),         # divergência de versão de estado não tratada
    ("no_state_blob", "7", "", "swap_carries_state"),
    ("save_failure_ignored", "8", "", "save_failure_vetoes"),
    ("no_rollback", "9", "", "bad_core_rolls_back"),
    ("veto_ignored", "10", "", "save_failure_vetoes"),
    ("exit1_on_refusal", "", "exit1_on_refusal", "refuse_no_control_channel"),   # código de saída diferente de 2 na recusa
    ("no_buildid_check", "", "no_buildid_check", "refuse_old_loader"),
    ("dry_run_writes", "", "dry_run_writes", "dry_run_changes_nothing"),
    ("root_ignored", "", "root_ignored", "refuse_outside_root"),
]
