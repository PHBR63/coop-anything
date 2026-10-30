#!/usr/bin/env python3
"""Troca de DLL em execução: coloca uma DLL de núcleo recém-compilada num jogo em execução sem reiniciá-lo.

    python -I tools/hotreload/hotreload.py swap   --pipe mygame --dll build/mod_core.dll
    python -I tools/hotreload/hotreload.py swap   --pipe mygame-0 --pipe mygame-1 --dll build/mod_core.dll   (várias cópias)
    python -I tools/hotreload/hotreload.py swap   --pipe mygame --dll build/mod_core.dll --dry-run
    python -I tools/hotreload/hotreload.py status --pipe mygame

O jogo em execução deve usar a compilação dividida: um pequeno carregador permanente e uma DLL de núcleo recarregável (veja README.md).
O carregador mapeia uma cópia privada em cache do núcleo, permitindo sobrescrever a saída da compilação enquanto o jogo executa.

Por cópia: (1) perguntar a dev.status onde está seu arquivo de núcleo e qual compilação executa; (2) copiar a nova DLL ao lado do arquivo de núcleo
com nome temporário e renomeá-la sobre o arquivo de núcleo (o carregador nunca vê um arquivo parcialmente gravado); (3) chamar
dev.reload (o núcleo salva seu estado, o carregador espera até nenhuma thread executar código do núcleo, descarrega, mapeia a nova cópia e
o novo núcleo restaura o estado); (4) conferir se o carregador agora executa exatamente a DLL copiada (ID de compilação = CRC-32 e
tamanho da cópia mapeada), se a geração aumentou, se nada foi revertido e se o registro de recarregamento do núcleo
não informa falha nem vazamento. Um participante que iniciou do zero em vez de restaurar é informado como aviso.

Todas as cópias são conferidas antes, e nada é alterado a menos que todas possam recarregar em execução. Uma troca para na primeira cópia
que falhar (as demais são informadas como ignoradas).

Saída 0: todas as cópias executam a nova compilação (ou já a executavam), ou --dry-run não encontrou problemas.
Saída 1: uma cópia falhou. O relatório indica qual verificação. O núcleo antigo pode continuar executando (descarregamento recusado) ou ter
         sido restaurado por reversão; a nova DLL já está no lugar, portanto uma segunda tentativa não exige nova cópia.
Saída 2: recusado antes de qualquer alteração, com motivo em stderr e no relatório: sem pipe de controle, compilação
         monolítica sem dev.reload, carregador sem IDs de compilação, --dll não é um núcleo, --dll é o próprio arquivo de núcleo ativo
         ou o arquivo de núcleo está fora de --root.
Relatório JSON em stdout, progresso em stderr.

Não realizado aqui: alterar o próprio CARREGADOR exige reinício normal, porque ele nunca é descarregado. Esta ferramenta
não inicia, interrompe nem altera processos. Apenas se comunica com o pipe de controle e copia um arquivo.
Nunca use isto num jogo online com antitrapaça.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
import zlib
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple

CORE_EXPORT = b"HotCore_Init"   # a única exportação presente em toda DLL de núcleo (include/hotreload/abi.h)
TMP_SUFFIX = ".swap"            # sem ".dll": um carregador ou scanner de plugins que carrega todo *.dll não deve ver a cópia temporária
METHOD_NOT_FOUND = -32601

# Opções exclusivas de teste. Cada uma recria um erro conhecido para os testes provarem que o detectariam. Vazio no uso normal.
FAULTS: set = set()   # "exit1_on_refusal", "no_buildid_check", "dry_run_writes", "root_ignored"


class Refused(Exception):
    "Nada foi alterado e nada será: o chamador sai com 2."


class SwapFailed(Exception):
    "Uma cópia não terminou na nova compilação: o chamador sai com 1. rep: o que se sabe sobre essa cópia até agora."

    def __init__(self, msg: str, rep: Optional[Dict[str, Any]] = None):
        super().__init__(msg)
        self.rep = rep


class ConnectionLost(Exception):
    pass


class RpcError(Exception):
    def __init__(self, code: int, message: str, method: str = ""):
        super().__init__(f"{method}: {message}" if method else message)
        self.code, self.message, self.method = code, message, method


# ----------------------------------------------------------------------------------- o canal de controle
def pipe_path(pipe: str) -> str:
    return pipe if pipe.startswith("\\\\") else "\\\\.\\pipe\\" + pipe


class PipeClient:
    """Uma conexão com um pipe de controle: um objeto JSON por linha, solicitação e resposta (include/hotreload/control_pipe.h).
    Leituras consultam PeekNamedPipe, portanto toda espera tem tempo limite e um jogo travado não pode prender a ferramenta."""

    def __init__(self, f, name: str = ""):
        import ctypes
        import msvcrt
        from ctypes import wintypes
        self._ctypes = ctypes
        self._k32 = ctypes.WinDLL("kernel32", use_last_error=True)
        self._k32.PeekNamedPipe.argtypes = [wintypes.HANDLE, ctypes.c_void_p, wintypes.DWORD, ctypes.c_void_p,
                                            ctypes.POINTER(wintypes.DWORD), ctypes.c_void_p]
        self._k32.PeekNamedPipe.restype = wintypes.BOOL
        self._wintypes = wintypes
        self._f = f
        self._h = msvcrt.get_osfhandle(f.fileno())
        self._buf = b""
        self._next_id = 1
        self.name = name

    @classmethod
    def connect(cls, pipe: str, wait_s: float = 0.0) -> "PipeClient":
        "Abre o pipe; com wait_s > 0, tenta novamente até ele existir ou o tempo acabar."
        path = pipe_path(pipe)
        deadline = time.monotonic() + wait_s
        while True:
            try:
                return cls(open(path, "r+b", buffering=0), path)
            except OSError as e:   # ainda sem pipe, ou o único cliente permitido está ocupado
                if time.monotonic() >= deadline:
                    raise ConnectionLost(f"cannot open {path}: {e}") from e
                time.sleep(0.1)

    def close(self) -> None:
        try:
            self._f.close()
        except Exception:
            pass

    def _available(self) -> int:
        avail = self._wintypes.DWORD(0)
        if not self._k32.PeekNamedPipe(self._h, None, 0, None, self._ctypes.byref(avail), None):
            raise ConnectionLost("pipe closed by the other side")
        return avail.value

    def call(self, method: str, params: Optional[Dict[str, Any]] = None, timeout_s: float = 30.0) -> Any:
        rid = self._next_id
        self._next_id += 1
        req: Dict[str, Any] = {"id": rid, "method": method}
        if params:
            req["params"] = params
        try:
            self._f.write(json.dumps(req).encode("utf-8") + b"\n")
        except OSError as e:
            raise ConnectionLost(f"write failed: {e}") from e
        deadline = time.monotonic() + timeout_s
        delay = 0.0005
        while b"\n" not in self._buf:
            n = self._available()
            if n:
                self._buf += self._f.read(min(n, 1 << 20))
                delay = 0.0005
                continue
            if time.monotonic() >= deadline:
                raise ConnectionLost(f"no reply to {method} within {timeout_s:g} s")
            time.sleep(delay)
            delay = min(delay * 2, 0.01)
        line, self._buf = self._buf.split(b"\n", 1)
        msg = json.loads(line.decode("utf-8"))
        if msg.get("id") != rid:
            raise ConnectionLost(f"reply id {msg.get('id')!r} does not match request id {rid}")
        if "error" in msg:
            e = msg["error"] or {}
            raise RpcError(int(e.get("code", 0)), str(e.get("message", "")), method)
        return msg.get("result")


# ----------------------------------------------------------------------------------- ID de compilação
def build_id_of(path: Path) -> str:
    """CRC-32 (8 dígitos hexadecimais), um hífen e o tamanho em bytes. O carregador calcula o mesmo texto para o arquivo mapeado
    (BuildIdOfFile em src/loader_host.cpp), portanto IDs iguais significam bytes iguais para fins práticos."""
    crc, size = 0, 0
    with open(path, "rb") as f:
        while True:
            chunk = f.read(1 << 20)
            if not chunk:
                break
            crc = zlib.crc32(chunk, crc)
            size += len(chunk)
    return f"{crc & 0xFFFFFFFF:08x}-{size}"


def pe_exports(data: bytes) -> Optional[List[bytes]]:
    """Os nomes exportados por um arquivo PE (32 ou 64 bits), ou None se não for um arquivo PE. Lê a tabela de exportações, para uma DLL que
    apenas contém o nome como texto (o carregador contém) não ser confundida com uma que o exporta."""
    import struct
    if len(data) < 0x40 or data[:2] != b"MZ":
        return None
    pe = struct.unpack_from("<I", data, 0x3C)[0]
    if pe + 24 > len(data) or data[pe:pe + 4] != b"PE\0\0":
        return None
    n_sections, = struct.unpack_from("<H", data, pe + 6)
    opt_size, = struct.unpack_from("<H", data, pe + 20)
    opt = pe + 24
    magic, = struct.unpack_from("<H", data, opt)
    dirs = opt + (96 if magic == 0x10B else 112)
    if magic not in (0x10B, 0x20B) or dirs + 8 > len(data):
        return None
    export_rva, _size = struct.unpack_from("<II", data, dirs)
    sections = []
    for i in range(n_sections):
        s = opt + opt_size + 40 * i
        vsize, va, rawsize, raw = struct.unpack_from("<IIII", data, s + 8)
        sections.append((va, max(vsize, rawsize), raw))

    def at(rva: int) -> int:
        for va, size, raw in sections:
            if va <= rva < va + size:
                return raw + rva - va
        return -1

    if export_rva == 0:
        return []
    ed = at(export_rva)
    if ed < 0 or ed + 40 > len(data):
        return None
    count = struct.unpack_from("<I", data, ed + 24)[0]   # NumberOfNames
    names = at(struct.unpack_from("<I", data, ed + 32)[0])   # AddressOfNames
    out: List[bytes] = []
    for i in range(count):
        if names < 0 or names + 4 * i + 4 > len(data):
            return None
        s = at(struct.unpack_from("<I", data, names + 4 * i)[0])
        if s < 0:
            return None
        out.append(data[s:data.index(b"\0", s)])
    return out


def core_dll_problem(path: Path) -> str:
    """"" quando o arquivo é uma DLL de núcleo; caso contrário, o motivo de não ser. Um núcleo exporta HotCore_Init. A DLL do carregador e uma
    compilação monolítica não exportam, e carregar qualquer uma como núcleo deixaria a cópia sem núcleo."""
    try:
        data = Path(path).read_bytes()
    except OSError as e:
        return f"cannot read {path}: {e}"
    names = pe_exports(data)
    if names is None:
        return f"{path} is not a DLL"
    if CORE_EXPORT not in names:
        return f"{path} has no HotCore_Init export: it is not a reloadable core. Is it the loader or a monolith build?"
    return ""


# ----------------------------------------------------------------------------------- leitura de uma cópia
def _is_method_missing(exc: Exception) -> bool:
    return getattr(exc, "code", None) == METHOD_NOT_FOUND or "unknown method" in str(exc).lower()


def read_status(client: PipeClient) -> Dict[str, Any]:
    "dev.status de uma cópia. Lança Refused quando a cópia não pode recarregar em execução."
    try:
        st = client.call("dev.status", timeout_s=10)
    except RpcError as e:
        if _is_method_missing(e):
            raise Refused("this copy has no dev.status or dev.reload: it runs a monolith build or a loader without hot reload. "
                          "Start it once with the split build (loader plus core DLL)") from e
        raise Refused(f"dev.status failed: {e}") from e
    except ConnectionLost as e:
        raise Refused(f"dev.status got no answer: {e}. Is the game's main loop running?") from e
    if not isinstance(st, dict) or "generation" not in st or not st.get("corePath"):
        raise Refused(f"dev.status answered something that is not a loader status: {st!r}")
    if "buildId" not in st and "no_buildid_check" not in FAULTS:
        raise Refused("this loader has no buildId in dev.status (an old loader), so a swap cannot be proven. "
                      "Restart the copy once with the current loader")
    return st


def check_core_path(st: Dict[str, Any], root: Optional[Path]) -> Path:
    """O arquivo de núcleo carregado pela cópia. Com --root, deve ficar dentro dessa pasta: esta ferramenta sobrescreve esse arquivo, e ele
    nunca deve pertencer a outra instalação."""
    dest = Path(st["corePath"])
    if root is not None and "root_ignored" not in FAULTS:
        a, b = os.path.normcase(str(dest.resolve())), os.path.normcase(str(root.resolve()))
        try:
            inside = os.path.commonpath([a, b]) == b
        except ValueError:
            inside = False
        if not inside:
            raise Refused(f"the copy's core file {dest} is outside --root {root}; not overwriting it")
    return dest


def running_build_id(st: Dict[str, Any]) -> Optional[str]:
    bid = st.get("buildId")
    return bid if isinstance(bid, str) and bid else None


# ----------------------------------------------------------------------------------- decisões
def needs_swap(before_id: Optional[str], expected_id: str, force: bool) -> bool:
    "False quando a cópia já executa estes bytes: recarregar não alteraria nada."
    return force or before_id != expected_id


def verify_after(before: Dict[str, Any], after: Dict[str, Any], expected_id: str) -> Tuple[bool, str]:
    "(ok, detalhe). A prova é o ID do núcleo em execução, nunca apenas 'dev.reload respondeu'."
    last = after.get("last") if isinstance(after.get("last"), dict) else {}
    probs: List[str] = []
    if not after.get("loaded"):
        probs.append("the loader reports no core loaded")
    if last.get("coreDead"):
        probs.append("the core is dead after the reload")
    if last.get("rolledBack"):
        probs.append(f"the new core failed to start and the old one runs again ({last.get('error')})")
    elif last.get("ok") is False:
        probs.append(f"the last reload failed: {last.get('error')}")
    gb, ga = int(before.get("generation", -1)), int(after.get("generation", -1))
    if ga <= gb:
        probs.append(f"generation did not advance ({gb} -> {ga})")
    now_id = running_build_id(after)
    if now_id is None:
        probs.append("cannot tell which build runs (no buildId)")
    elif now_id != expected_id:
        probs.append(f"running build {now_id} is not the one that was copied ({expected_id})")
    return (not probs, "; ".join(probs) or f"build {now_id}, generation {gb} -> {ga}")


def reload_state(client: PipeClient) -> Optional[Dict[str, Any]]:
    "Relatório do registro de recarregamento do núcleo (método reload.state). Melhor esforço: um núcleo sem isso não informa nada."
    try:
        rs = client.call("reload.state", timeout_s=10)
    except Exception:
        return None
    return rs if isinstance(rs, dict) else None


def registry_problems(rs: Optional[Dict[str, Any]]) -> Tuple[str, List[str]]:
    "(problemas que fazem a troca falhar, avisos que não a impedem)."
    if not rs:
        return "", []
    bits = []
    if rs.get("failures"):
        bits.append(f"failures={rs['failures']}")
    if rs.get("leaks"):
        bits.append(f"leaks={rs['leaks']}")
    warn = []
    if rs.get("fresh"):
        notes = [n for n in rs.get("notes", []) if isinstance(n, str) and n.startswith("fresh ")]
        warn.append(f"{rs['fresh']} participant(s) started fresh instead of restoring their state: " + "; ".join(notes))
    return "; ".join(bits), warn


# ----------------------------------------------------------------------------------- a troca de arquivo
def install_dll(src: Path, dest: Path, expected_id: str, sleep: Callable[[float], None] = time.sleep,
                replace_wait_s: float = 5.0) -> None:
    """Copia src para dest por um nome temporário na mesma pasta e o renomeia sobre dest, para um leitor ver o arquivo
    antigo ou o novo inteiro. Verifica a cópia antes e depois da renomeação."""
    tmp = dest.with_name(dest.name + TMP_SUFFIX)
    try:
        with open(src, "rb") as fi, open(tmp, "wb") as fo:
            while True:
                chunk = fi.read(1 << 20)
                if not chunk:
                    break
                fo.write(chunk)
        if build_id_of(tmp) != expected_id:
            raise SwapFailed(f"the copy {tmp} differs from {src} (disk full, or the file changed while copying)")
        last: Optional[Exception] = None
        tries = max(1, int(replace_wait_s / 0.1))
        for _ in range(tries):   # o carregador ou um scanner pode manter o arquivo aberto por um instante
            try:
                os.replace(str(tmp), str(dest))
                last = None
                break
            except PermissionError as e:
                last = e
                sleep(0.1)
        if last is not None:
            raise SwapFailed(f"cannot replace {dest}: {last}. Is the copy mapping the original file instead of a cache copy?")
    finally:
        try:
            if tmp.exists():
                tmp.unlink()
        except OSError:
            pass
    if build_id_of(dest) != expected_id:
        raise SwapFailed(f"{dest} does not hold the new build after the rename")


# ----------------------------------------------------------------------------------- uma cópia
class Plan:
    def __init__(self, pipe: str, client: PipeClient, status: Dict[str, Any], dest: Path):
        self.pipe, self.client, self.status, self.dest = pipe, client, status, dest
        self.before_id = running_build_id(status)


def swap_one(plan: Plan, src: Path, expected_id: str, *, reload_timeout_s: float, force: bool, replace_wait_s: float,
             log: Callable[[str], None]) -> Dict[str, Any]:
    client = plan.client
    rep: Dict[str, Any] = {"pipe": plan.pipe, "core": str(plan.dest), "buildBefore": plan.before_id,
                           "generationBefore": plan.status.get("generation")}
    if not needs_swap(plan.before_id, expected_id, force):
        rep.update(status="unchanged", buildAfter=plan.before_id, generationAfter=plan.status.get("generation"),
                   detail="already runs this build; nothing to do (--force reloads anyway)")
        log(f"{plan.pipe}: already on build {expected_id}")
        return rep
    t0 = time.monotonic()
    try:
        install_dll(src, plan.dest, expected_id, replace_wait_s=replace_wait_s)
        log(f"{plan.pipe}: copied {expected_id} over {plan.dest.name}; reloading")
        reply: Any = None
        try:
            # timeoutMs amplia a espera de 30 s do próprio pipe de controle pelo ciclo principal; timeout_s é nossa espera pela resposta.
            reply = client.call("dev.reload", {"reason": "hotswap", "timeoutMs": int(reload_timeout_s * 1000)}, timeout_s=reload_timeout_s)
        except RpcError as e:
            raise SwapFailed(f"dev.reload refused: {e.message}. The new DLL is already in place for the next try") from e
        except ConnectionLost as e:
            raise SwapFailed(f"lost the control pipe during the reload: {e}. Did the game crash? Check its log") from e
        try:
            after = read_status(client)
        except Refused as e:
            raise SwapFailed(f"dev.status unreadable after the reload: {e}") from e
        ok, detail = verify_after(plan.status, after, expected_id)
        rep.update(msTotal=round((time.monotonic() - t0) * 1000), buildAfter=running_build_id(after),
                   generationAfter=after.get("generation"), reply=reply)
        if not ok:
            raise SwapFailed(detail)
        problems, warnings = registry_problems(reload_state(client))
        if problems:
            raise SwapFailed(f"the core came up but its reload registry reports: {problems}")
        if warnings:
            rep["warnings"] = warnings
            for w in warnings:
                log(f"{plan.pipe}: warning: {w}")
    except SwapFailed as e:
        rep.update(status="failed", detail=str(e))
        e.rep = rep
        raise
    rep.update(status="swapped", detail=detail)
    log(f"{plan.pipe}: now on build {rep['buildAfter']}, generation {rep['generationAfter']}, {rep['msTotal']} ms")
    return rep


# ----------------------------------------------------------------------------------- todas as cópias
def run_swap(pipes: List[str], dll: Path, *, force: bool = False, dry_run: bool = False, root: Optional[Path] = None,
             reload_timeout_s: float = 90.0, replace_wait_s: float = 5.0, connect_wait_s: float = 3.0,
             log: Callable[[str], None] = lambda s: print(s, file=sys.stderr)) -> Tuple[int, Dict[str, Any]]:
    report: Dict[str, Any] = {"ok": False, "dll": str(dll), "copies": []}
    plans: List[Plan] = []
    conns: List[PipeClient] = []
    try:
        # ---- verificações prévias: nada é alterado até conferir todas as cópias ----
        try:
            problem = core_dll_problem(dll)
            if problem:
                raise Refused(problem)
            expected = build_id_of(dll)
            report["buildId"] = expected
            for pipe in pipes:
                try:
                    client = PipeClient.connect(pipe, wait_s=connect_wait_s)
                except ConnectionLost as e:
                    raise Refused(f"{pipe}: no control pipe: {e}. Is the game running with the loader?") from e
                conns.append(client)
                try:
                    st = read_status(client)
                    dest = check_core_path(st, root)
                    if Path(dll).resolve() == dest.resolve():
                        raise Refused(f"--dll is the copy's own core file {dest}; build to another folder and pass that")
                except Refused as e:
                    raise Refused(f"{pipe}: {e}") from e
                plans.append(Plan(pipe, client, st, dest))
        except Refused as e:
            report.update(refused=str(e))
            log(f"refused: {e}")
            return (1 if "exit1_on_refusal" in FAULTS else 2), report
        if dry_run:
            for p in plans:
                if "dry_run_writes" in FAULTS:
                    install_dll(dll, p.dest, expected, replace_wait_s=replace_wait_s)
                report["copies"].append({"pipe": p.pipe, "core": str(p.dest), "buildBefore": p.before_id,
                                         "generationBefore": p.status.get("generation"),
                                         "status": "would swap" if needs_swap(p.before_id, expected, force) else "unchanged"})
            report["ok"] = True
            return 0, report
        # ---- troca uma cópia após a outra; para na primeira falha ----
        failed = False
        for p in plans:
            if failed:
                report["copies"].append({"pipe": p.pipe, "status": "skipped", "detail": "an earlier copy failed"})
                continue
            try:
                report["copies"].append(swap_one(p, dll, expected, reload_timeout_s=reload_timeout_s, force=force,
                                                 replace_wait_s=replace_wait_s, log=log))
            except SwapFailed as e:
                failed = True
                report["copies"].append(e.rep or {"pipe": p.pipe, "status": "failed", "detail": str(e)})
                log(f"{p.pipe}: FAILED: {e}")
        report["ok"] = not failed
        return (0 if report["ok"] else 1), report
    finally:
        for c in conns:
            c.close()


# ----------------------------------------------------------------------------------- linha de comando
def cmd_swap(a: argparse.Namespace) -> int:
    code, rep = run_swap(a.pipe, Path(a.dll), force=a.force, dry_run=a.dry_run, root=Path(a.root) if a.root else None,
                         reload_timeout_s=a.reload_timeout_s, replace_wait_s=a.replace_wait_s, connect_wait_s=a.connect_wait_s)
    text = json.dumps(rep, indent=2)
    print(text)
    if a.out:
        Path(a.out).parent.mkdir(parents=True, exist_ok=True)
        Path(a.out).write_text(text, encoding="utf-8")
    return code


def cmd_status(a: argparse.Namespace) -> int:
    rows = []
    code = 0
    for pipe in a.pipe:
        try:
            c = PipeClient.connect(pipe, wait_s=3.0)
        except ConnectionLost as e:
            rows.append({"pipe": pipe, "error": str(e)})
            code = 2
            continue
        try:
            rows.append({"pipe": pipe, "status": read_status(c)})
        except Refused as e:
            rows.append({"pipe": pipe, "error": str(e)})
            code = 2
        finally:
            c.close()
    print(json.dumps(rows, indent=2))
    return code


def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sw = sub.add_parser("swap", help="trocar a DLL de núcleo por uma recém-compilada em cópias em execução")
    sw.add_argument("--pipe", action="append", required=True, help="pipe de controle de uma cópia em execução; repita para várias cópias")
    sw.add_argument("--dll", required=True, help="a DLL de núcleo recém-compilada")
    sw.add_argument("--root", default="", help="recusar, a menos que o arquivo de núcleo de cada cópia esteja dentro desta pasta")
    sw.add_argument("--force", action="store_true", help="recarregar mesmo quando a cópia já executa esta compilação")
    sw.add_argument("--dry-run", action="store_true", help="conferir todas as cópias e informar o que aconteceria; não alterar nada")
    sw.add_argument("--reload-timeout-s", type=float, default=90.0, help="por quanto tempo esperar a resposta de dev.reload")
    sw.add_argument("--replace-wait-s", type=float, default=5.0, help="por quanto tempo tentar novamente quando o arquivo de núcleo estiver bloqueado")
    sw.add_argument("--connect-wait-s", type=float, default=3.0, help="por quanto tempo esperar um pipe de controle aparecer")
    sw.add_argument("--out", default="", help="também escreve relatório JSON neste arquivo")
    sw.set_defaults(fn=cmd_swap)
    st = sub.add_parser("status", help="imprimir dev.status das cópias em execução (saída 2 se alguma não puder recarregar em execução)")
    st.add_argument("--pipe", action="append", required=True)
    st.set_defaults(fn=cmd_status)
    a = ap.parse_args(argv)
    return a.fn(a)


if __name__ == "__main__":
    sys.exit(main())
