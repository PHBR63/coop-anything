#!/usr/bin/env python3
"""bridge_client: controla um jogo em execução pelo servidor RPC interno (veja PROTOCOL.md).

Só biblioteca padrão. Dois transportes, escolhidos pelo texto do endpoint:

    tcp://127.0.0.1:27990      (ou apenas 127.0.0.1:27990)   funciona em todo sistema operacional
    pipe://mygame-0            pipe nomeado Windows, \\.\\pipe\\mygame-0

Uso como biblioteca::

    from bridge_client import Bridge
    with Bridge.connect("tcp://127.0.0.1:27990", wait_s=60) as g:
        g.load("base_save")
        g.exec("set quest 10")
        g.wait_for(expr="quest", op=">=", value=10, timeout_ms=5000)
        print(g.eval("health"))

Toda chamada tem limite de tempo e erro distinto:

    RpcError        jogo respondeu com objeto de erro (code, message)
    CallTimeout     sem resposta a tempo (conexão ainda utilizável; resposta tardia ignorada)
    WaitTimeout     wait_for terminou com condição ainda falsa
    ConnectionLost  transporte fechou ou não pode ser aberto
    GameCrashed     ConnectionLost e processo do jogo (PID do ping) não existe mais
    ProtocolError   servidor enviou algo fora do protocolo

Linha de comando::

    python bridge_client.py --endpoint tcp://127.0.0.1:27990 ping
    python bridge_client.py --endpoint-file run/endpoint.json exec "set quest 10"
    python bridge_client.py --endpoint tcp://127.0.0.1:27990 waitfor quest --op ">=" --value 10
    python bridge_client.py --endpoint tcp://127.0.0.1:27990 call my.method '{"a": 1}'

Códigos de saída: 0 ok, 1 problema de conexão ou protocolo, 2 jogo respondeu com erro, 3 espera ou chamada esgotou tempo.
"""
from __future__ import annotations

import argparse
import itertools
import json
import os
import socket
import sys
import threading
import time
from typing import Any, Dict, List, Optional, Tuple

PROTOCOL_VERSION = 1
ENV_ENDPOINT = "COOPBRIDGE_ENDPOINT"


# ------------------------------------------------------------------------------------------------ erros
class BridgeError(Exception):
    "Classe base de toda falha lançada por este módulo."


class RpcError(BridgeError):
    "O jogo respondeu com {\"error\": {...}}."

    def __init__(self, code: int, message: str, method: str = "", data: Any = None):
        super().__init__(f"{method}: [{code}] {message}" if method else f"[{code}] {message}")
        self.code = code
        self.message = message
        self.method = method
        self.data = data


class ProtocolError(BridgeError):
    "Servidor enviou algo que viola o protocolo (JSON inválido, ID do futuro, ...)."


class CallTimeout(BridgeError):
    "Sem resposta dentro do limite. A conexão fica aberta; resposta tardia é ignorada na próxima chamada."

    def __init__(self, method: str, timeout_s: float):
        super().__init__(f"no reply to {method} within {timeout_s:g}s")
        self.method = method
        self.timeout_s = timeout_s


class WaitTimeout(BridgeError):
    def __init__(self, what: str, last: Any = None):
        super().__init__(f"timed out waiting for {what} (last value: {last!r})")
        self.last = last


class ConnectionLost(BridgeError):
    pass


class GameCrashed(ConnectionLost):
    "A conexão morreu e o processo do jogo não existe mais."

    def __init__(self, pid: int, detail: str = ""):
        super().__init__(f"game process {pid} is gone ({detail}); read the game's logs for the cause")
        self.pid = pid


# ------------------------------------------------------------------------------------------------ auxiliares
def pid_alive(pid: int) -> bool:
    "True se processo com este PID estiver executando."
    if pid <= 0:
        return False
    if os.name == "nt":
        import ctypes
        from ctypes import wintypes
        k32 = ctypes.WinDLL("kernel32", use_last_error=True)
        k32.OpenProcess.restype = wintypes.HANDLE
        k32.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
        k32.GetExitCodeProcess.argtypes = [wintypes.HANDLE, ctypes.POINTER(wintypes.DWORD)]
        k32.CloseHandle.argtypes = [wintypes.HANDLE]
        h = k32.OpenProcess(0x1000, False, pid)        # PROCESS_QUERY_LIMITED_INFORMATION
        if not h:
            return False
        code = wintypes.DWORD()
        ok = k32.GetExitCodeProcess(h, ctypes.byref(code))
        k32.CloseHandle(h)
        return bool(ok) and code.value == 259          # STILL_ACTIVE
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    return True


def parse_endpoint(text: str) -> Tuple[str, str, Optional[int]]:
    """'tcp://host:port', 'host:port' ou 'pipe://name' -> (kind, host_or_name, port)."""
    t = text.strip()
    if t.startswith("pipe://"):
        name = t[len("pipe://"):]
        if not name:
            raise BridgeError(f"bad endpoint {text!r}: the pipe name is empty")
        return "pipe", name, None
    if t.startswith("tcp://"):
        t = t[len("tcp://"):]
    host, sep, port = t.rpartition(":")
    if not sep or not host or not port.isdigit():
        raise BridgeError(f"bad endpoint {text!r}: use tcp://HOST:PORT or pipe://NAME")
    return "tcp", host, int(port)


def endpoint_from_file(path: str, wait_s: float = 0.0, prefer: str = "tcp") -> str:
    """Lê arquivo de endpoint escrito pelo servidor ao iniciar (Options::endpointFile) e retorna um endpoint.

    Com wait_s > 0, espera o arquivo aparecer (o jogo pode estar iniciando)."""
    deadline = time.monotonic() + wait_s
    while True:
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            eps = [e for e in data.get("endpoints", []) if isinstance(e, str)]
            if not eps:
                raise BridgeError(f"{path} lists no endpoints")
            for e in eps:
                if e.startswith(prefer + "://"):
                    return e
            return eps[0]
        except (OSError, ValueError):
            if time.monotonic() >= deadline:
                raise ConnectionLost(f"endpoint file {path} is missing or not readable")
            time.sleep(0.1)


# ------------------------------------------------------------------------------------------------ transportes
class _TcpTransport:
    def __init__(self, host: str, port: int, connect_timeout: float):
        try:
            self._s = socket.create_connection((host, port), timeout=connect_timeout)
        except OSError as e:
            raise ConnectionLost(f"cannot connect to tcp://{host}:{port}: {e}") from e
        self._s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)

    def send(self, data: bytes) -> None:
        try:
            self._s.settimeout(30)
            self._s.sendall(data)
        except OSError as e:
            raise ConnectionLost(f"write failed: {e}") from e

    def recv(self, timeout: float) -> Optional[bytes]:
        "Bytes recebidos, ou None se nada chegou em `timeout` segundos."
        try:
            self._s.settimeout(max(timeout, 0.001))
            data = self._s.recv(65536)
        except socket.timeout:
            return None
        except OSError as e:
            raise ConnectionLost(f"read failed: {e}") from e
        if not data:
            raise ConnectionLost("connection closed by the game")
        return data

    def close(self) -> None:
        try:
            self._s.close()
        except OSError:
            pass


class _PipeTransport:
    """Pipe nomeado Windows. Identificador síncrono serializa E/S, então leitura bloqueada bloquearia escrita:
    recv consulta PeekNamedPipe e lê só o que está disponível."""

    def __init__(self, name: str):
        if os.name != "nt":
            raise BridgeError("pipe:// endpoints need Windows; use a tcp:// endpoint on this OS")
        import ctypes
        import msvcrt
        from ctypes import wintypes
        self._ct = ctypes
        self._wt = wintypes
        self._k32 = ctypes.WinDLL("kernel32", use_last_error=True)
        self._k32.PeekNamedPipe.argtypes = [wintypes.HANDLE, ctypes.c_void_p, wintypes.DWORD, ctypes.c_void_p,
                                            ctypes.POINTER(wintypes.DWORD), ctypes.c_void_p]
        path = name if name.startswith("\\\\") else "\\\\.\\pipe\\" + name
        try:
            self._f = open(path, "r+b", buffering=0)
        except OSError as e:
            raise ConnectionLost(f"cannot open {path}: {e}") from e
        self._h = msvcrt.get_osfhandle(self._f.fileno())

    def send(self, data: bytes) -> None:
        try:
            self._f.write(data)
        except OSError as e:
            raise ConnectionLost(f"write failed: {e}") from e

    def recv(self, timeout: float) -> Optional[bytes]:
        deadline = time.monotonic() + timeout
        delay = 0.0005
        while True:
            avail = self._wt.DWORD(0)
            if not self._k32.PeekNamedPipe(self._h, None, 0, None, self._ct.byref(avail), None):
                raise ConnectionLost("pipe closed by the game")
            if avail.value:
                try:
                    return self._f.read(min(avail.value, 1 << 20))
                except OSError as e:
                    raise ConnectionLost(f"read failed: {e}") from e
            if time.monotonic() >= deadline:
                return None
            time.sleep(delay)
            delay = min(delay * 2, 0.01)

    def close(self) -> None:
        try:
            self._f.close()
        except OSError:
            pass


def _open_transport(endpoint: str, connect_timeout: float):
    kind, host, port = parse_endpoint(endpoint)
    if kind == "pipe":
        return _PipeTransport(host)
    return _TcpTransport(host, int(port), connect_timeout)


# ------------------------------------------------------------------------------------------------ cliente
class Bridge:
    "Uma conexão ao servidor RPC do jogo. Chamadas serializadas: uma por vez por Bridge."

    def __init__(self, transport: Any, name: str = "", default_timeout_s: float = 35.0):
        self._t = transport
        self.name = name
        self.default_timeout_s = default_timeout_s
        self._ids = itertools.count(1)
        self._buf = b""
        self._lock = threading.Lock()
        self.game_pid = 0
        self._methods: Optional[List[str]] = None

    # ---- conexão ----
    @classmethod
    def connect(cls, endpoint: Optional[str] = None, wait_s: float = 0.0, timeout_s: float = 35.0,
                ping_timeout_s: float = 5.0) -> "Bridge":
        """Abre o endpoint. Com wait_s > 0, tenta até o jogo abri-lo (ou esgotar o tempo).

        endpoint usa por padrão a variável COOPBRIDGE_ENDPOINT. Um ping vem depois para descobrir o PID do jogo e
        informar travamentos posteriores como GameCrashed; servidor que não responde ao ping é erro."""
        endpoint = endpoint or os.environ.get(ENV_ENDPOINT)
        if not endpoint:
            raise BridgeError(f"no endpoint: pass one or set {ENV_ENDPOINT}")
        deadline = time.monotonic() + wait_s
        while True:
            try:
                t = _open_transport(endpoint, connect_timeout=min(5.0, max(0.5, wait_s)))
                break
            except ConnectionLost:
                if time.monotonic() >= deadline:
                    raise
                time.sleep(0.25)
        b = cls(t, endpoint, timeout_s)
        try:
            b.ping(timeout_s=ping_timeout_s)
        except BridgeError:
            b.close()
            raise
        return b

    def close(self) -> None:
        self._t.close()

    def __enter__(self) -> "Bridge":
        return self

    def __exit__(self, *a: Any) -> None:
        self.close()

    # ---- bruto ----
    def _next_message(self, deadline: float) -> Optional[Dict[str, Any]]:
        "Um objeto de resposta do fluxo em buffer, ou None se o prazo vencer antes."
        while b"\n" not in self._buf:
            left = deadline - time.monotonic()
            if left <= 0:
                return None
            chunk = self._t.recv(left)
            if chunk:
                self._buf += chunk
        line, self._buf = self._buf.split(b"\n", 1)
        try:
            msg = json.loads(line.decode("utf-8", errors="replace"))
        except ValueError as e:
            raise ProtocolError(f"invalid JSON from the game: {line[:200]!r}") from e
        if not isinstance(msg, dict):
            raise ProtocolError(f"reply is not an object: {msg!r}")
        return msg

    def call(self, method: str, params: Optional[Dict[str, Any]] = None, timeout_s: Optional[float] = None) -> Any:
        "Envia uma solicitação e retorna resultado. Lança RpcError, CallTimeout, ConnectionLost, GameCrashed, ProtocolError."
        timeout_s = self.default_timeout_s if timeout_s is None else timeout_s
        with self._lock:
            rid = next(self._ids)
            req: Dict[str, Any] = {"id": rid, "method": method}
            if params:
                req["params"] = params
            deadline = time.monotonic() + timeout_s
            try:
                self._t.send(json.dumps(req).encode("utf-8") + b"\n")
                msg = self._reply_for(rid, method, deadline, timeout_s)
            except ConnectionLost as e:
                if self.game_pid and not pid_alive(self.game_pid):
                    raise GameCrashed(self.game_pid, str(e)) from e
                raise
        if "error" in msg:
            e = msg["error"] if isinstance(msg["error"], dict) else {}
            raise RpcError(int(e.get("code", 0) or 0), str(e.get("message", "")), method, e.get("data"))
        if "result" not in msg:
            raise ProtocolError(f"reply has neither result nor error: {msg!r}")
        return msg["result"]

    def _reply_for(self, rid: int, method: str, deadline: float, timeout_s: float) -> Dict[str, Any]:
        while True:
            msg = self._next_message(deadline)
            if msg is None:
                raise CallTimeout(method, timeout_s)
            mid = msg.get("id")
            if mid is None and "error" in msg:
                return msg                      # servidor nem conseguiu ler a solicitação (erro de análise)
            if isinstance(mid, int) and not isinstance(mid, bool) and mid < rid:
                continue                        # resposta tardia de chamada anterior que esgotou o tempo
            if mid != rid:
                raise ProtocolError(f"reply id {mid!r} does not match request id {rid} ({method})")
            return msg

    # ---- métodos padrão ----
    def ping(self, timeout_s: float = 5.0) -> Dict[str, Any]:
        r = self.call("ping", timeout_s=timeout_s)
        if not isinstance(r, dict) or r.get("pong") is not True:
            raise ProtocolError(f"bad ping reply: {r!r}")
        proto = r.get("protocol", PROTOCOL_VERSION)
        if not isinstance(proto, int) or proto > PROTOCOL_VERSION:
            raise ProtocolError(f"the game speaks protocol {proto!r}, this client knows up to {PROTOCOL_VERSION}: update bridge_client.py")
        self.game_pid = int(r.get("pid", 0) or 0)
        return r

    def version(self) -> Dict[str, Any]:
        "{protocol, game, build, server, pid}. Registre nos metadados de cada execução de teste."
        return self.call("version", timeout_s=5)

    def methods(self, refresh: bool = False) -> List[str]:
        "Nomes dos métodos respondidos pelo jogo (padrões suportados mais personalizados)."
        if self._methods is None or refresh:
            self._methods = list(self.call("methods", timeout_s=5)["methods"])
        return list(self._methods)

    def require(self, *names: str) -> None:
        "Lança BridgeError se faltar um destes métodos no jogo."
        have = set(self.methods())
        missing = [n for n in names if n not in have]
        if missing:
            raise BridgeError("the game does not offer: " + ", ".join(missing))

    def exec(self, cmd: str, timeout_ms: Optional[int] = None, *, ref: Optional[str] = None) -> Dict[str, Any]:
        "Executa linha de console na thread principal do jogo: {'ok': bool, 'output': str}."
        p: Dict[str, Any] = {"cmd": cmd}
        if ref is not None:
            p["ref"] = ref
        if timeout_ms is not None:
            p["timeoutMs"] = timeout_ms
        return self.call("exec", p, timeout_s=(timeout_ms or 30000) / 1000 + 5)

    def eval(self, expr: str, ref: Optional[str] = None, timeout_ms: Optional[int] = None) -> Any:
        "Avalia uma expressão uma vez e retorna valor (número, bool ou string)."
        p: Dict[str, Any] = {"expr": expr}
        if ref is not None:
            p["ref"] = ref
        if timeout_ms is not None:
            p["timeoutMs"] = timeout_ms
        return self.call("eval", p, timeout_s=(timeout_ms or 30000) / 1000 + 5)["value"]

    def wait_for(self, expr: Optional[str] = None, *, cmd: Optional[str] = None, op: str = "truthy", value: float = 0,
                 contains: Optional[str] = None, timeout_ms: int = 10000, poll_ms: int = 100,
                 ref: Optional[str] = None) -> Dict[str, Any]:
        """Consulta `expr` (avaliada) ou `cmd` (linha de console) na thread principal até cumprir a condição.

        op é um de truthy == != < <= > >=; `contains` espera por esse texto na saída. Lança WaitTimeout quando o
        tempo esgota. O resultado tem value e elapsedMs."""
        if (expr is None) == (cmd is None):
            raise ValueError("pass exactly one of expr= or cmd=")
        p: Dict[str, Any] = {"timeoutMs": timeout_ms, "pollMs": poll_ms, "op": op, "value": value}
        if expr is not None:
            p["expr"] = expr
        else:
            p["cmd"] = cmd
        if contains is not None:
            p["contains"] = contains
        if ref is not None:
            p["ref"] = ref
        r = self.call("waitFor", p, timeout_s=timeout_ms / 1000 + 5)
        if not r.get("satisfied"):
            raise WaitTimeout(expr or cmd or "", r.get("value"))
        return r

    def state(self, sections: Optional[List[str]] = None) -> Dict[str, Any]:
        return self.call("state", {"sections": sections} if sections else None)

    def state_to_file(self, path: str, sections: Optional[List[str]] = None) -> Dict[str, Any]:
        """Despeja o estado em arquivo escrito pelo jogo. Caminho relativo torna-se absoluto aqui, pois o diretório
        de trabalho do jogo é sua própria pasta."""
        p: Dict[str, Any] = {"path": os.path.abspath(path)}
        if sections:
            p["sections"] = sections
        return self.call("state", p, timeout_s=120)

    def load(self, name: str, timeout_ms: int = 180000) -> Dict[str, Any]:
        return self.call("load", {"name": name, "timeoutMs": timeout_ms}, timeout_s=timeout_ms / 1000 + 5)

    def save(self, name: str, timeout_ms: int = 30000, overwrite: bool = False) -> Dict[str, Any]:
        p: Dict[str, Any] = {"name": name, "timeoutMs": timeout_ms}
        if overwrite:
            p["overwrite"] = True
        return self.call("save", p, timeout_s=timeout_ms / 1000 + 5)

    def screenshot(self, path: str = "") -> Dict[str, Any]:
        return self.call("screenshot", {"path": os.path.abspath(path)} if path else None)

    def events(self, since: int = 0, limit: int = 0) -> Dict[str, Any]:
        p: Dict[str, Any] = {"since": since}
        if limit:
            p["limit"] = limit
        return self.call("events", p, timeout_s=5)

    def wait_event(self, type_: str, since: int = 0, timeout_s: float = 30.0, poll_s: float = 0.1) -> Dict[str, Any]:
        "Espera evento deste tipo com seq > since. Retorna o evento. Lança WaitTimeout."
        deadline = time.monotonic() + timeout_s
        cur = since
        while True:
            page = self.events(cur)
            for ev in page["events"]:
                if ev["type"] == type_:
                    return ev
            cur = page["next"]
            if time.monotonic() >= deadline:
                raise WaitTimeout(f"event {type_!r}", cur)
            time.sleep(poll_s)


# ------------------------------------------------------------------------------------------------ linha de comando
def _main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(prog="bridge_client", description="Controla jogo em execução por seu servidor RPC interno")
    ap.add_argument("--endpoint", default=None, help=f"tcp://HOST:PORT or pipe://NAME (default: ${ENV_ENDPOINT})")
    ap.add_argument("--endpoint-file", default=None, help="arquivo JSON escrito pelo jogo ao iniciar (Options::endpointFile)")
    ap.add_argument("--wait", type=float, default=0.0, help="segundos de espera para o endpoint aparecer")
    ap.add_argument("--timeout", type=float, default=35.0, help="segundos de espera por resposta")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("ping")
    sub.add_parser("version")
    sub.add_parser("methods")
    s = sub.add_parser("exec"); s.add_argument("line"); s.add_argument("--ref")
    s = sub.add_parser("eval"); s.add_argument("expr"); s.add_argument("--ref")
    s = sub.add_parser("state"); s.add_argument("sections", nargs="*")
    s = sub.add_parser("waitfor")
    s.add_argument("expr"); s.add_argument("--op", default="truthy"); s.add_argument("--value", type=float, default=0)
    s.add_argument("--timeout-ms", type=int, default=10000)
    s.add_argument("--as-cmd", action="store_true", help="trata EXPR como linha de console em vez de expressão")
    s.add_argument("--contains")
    s = sub.add_parser("events"); s.add_argument("--since", type=int, default=0); s.add_argument("--limit", type=int, default=0)
    s = sub.add_parser("screenshot"); s.add_argument("path", nargs="?", default="")
    s = sub.add_parser("load"); s.add_argument("name"); s.add_argument("--timeout-ms", type=int, default=180000)
    s = sub.add_parser("save"); s.add_argument("name"); s.add_argument("--timeout-ms", type=int, default=30000)
    s.add_argument("--overwrite", action="store_true")
    s = sub.add_parser("call"); s.add_argument("method"); s.add_argument("params", nargs="?", default="{}")
    a = ap.parse_args(argv)

    try:
        endpoint = a.endpoint
        if endpoint is None and a.endpoint_file:
            endpoint = endpoint_from_file(a.endpoint_file, wait_s=a.wait)
        with Bridge.connect(endpoint, wait_s=a.wait, timeout_s=a.timeout) as g:
            if a.cmd == "ping":
                out: Any = g.ping()
            elif a.cmd == "version":
                out = g.version()
            elif a.cmd == "methods":
                out = g.methods()
            elif a.cmd == "exec":
                out = g.exec(a.line, ref=a.ref)
            elif a.cmd == "eval":
                out = g.eval(a.expr, ref=a.ref)
            elif a.cmd == "state":
                out = g.state(a.sections or None)
            elif a.cmd == "waitfor":
                kw = dict(op=a.op, value=a.value, timeout_ms=a.timeout_ms, contains=a.contains)
                out = g.wait_for(cmd=a.expr, **kw) if a.as_cmd else g.wait_for(a.expr, **kw)
            elif a.cmd == "events":
                out = g.events(a.since, a.limit)
            elif a.cmd == "screenshot":
                out = g.screenshot(a.path)
            elif a.cmd == "load":
                out = g.load(a.name, a.timeout_ms)
            elif a.cmd == "save":
                out = g.save(a.name, a.timeout_ms, a.overwrite)
            else:
                out = g.call(a.method, json.loads(a.params))
    except RpcError as e:
        print(json.dumps({"error": {"code": e.code, "message": e.message}}), file=sys.stderr)
        return 2
    except (WaitTimeout, CallTimeout) as e:
        print(str(e), file=sys.stderr)
        return 3
    except BridgeError as e:
        print(str(e), file=sys.stderr)
        return 1
    print(json.dumps(out, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(_main())
