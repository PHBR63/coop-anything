"""Jogo simulado para os testes. É um script Python simples, não um jogo, e não mostra janela visível.

Pode reproduzir comportamentos dos jogos com que as ferramentas precisam lidar:

  --mutex NAME            cria um mutex nomeado; sai com código 3 se já existir (verificação de instância única)
  --rename-mutex          torna o nome exclusivo por processo (como uma correção interna ao processo do jogo)
  --window-class NAME     sai com código 4 se já existir janela de nível superior dessa classe (verificação como FindWindow);
                          caso contrário, cria uma janela invisível dessa classe
  --unique-window-class   torna o nome da classe exclusivo por processo
  --ready-file FILE       grava FILE (relativo à pasta de trabalho) após a inicialização, depois de --ready-delay segundos
  --log FILE              acrescenta linhas de progresso a FILE
  --port-base P           escuta em 127.0.0.1:(P + --i), para a sondagem de prontidão tcp_port encontrar algo
  --role host|client      com --bind-port: o host escuta nessa porta (código de saída 6 se não conseguir); o cliente se conecta
                          (código de saída 5 se nenhum host responder); registra "role=<role> port=<P>"
  --bind-port P           porta do par ao qual esta cópia pertence (consulte --role)
  --crash-after S         grava "CRASH code=1" no log após S segundos e sai com código 1
  --spawn-child           age como carregador: inicia outra cópia deste script (sem esta opção) e encerra
  --lifetime S            encerra sozinho após S segundos (padrão 90), evitando deixar um substituto esquecido em execução
"""
import argparse
import ctypes
import os
import socket
import subprocess
import sys
import time
from ctypes import wintypes


def log(path, text):
    if path:
        with open(path, "a", encoding="utf-8") as f:
            f.write(text + "\n")


def make_window(cls):
    u32 = ctypes.WinDLL("user32", use_last_error=True)
    k32 = ctypes.WinDLL("kernel32", use_last_error=True)
    WNDPROC = ctypes.WINFUNCTYPE(ctypes.c_ssize_t, wintypes.HWND, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM)
    u32.DefWindowProcW.argtypes = [wintypes.HWND, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM]
    u32.DefWindowProcW.restype = ctypes.c_ssize_t

    class WNDCLASSW(ctypes.Structure):
        _fields_ = [("style", wintypes.UINT), ("lpfnWndProc", WNDPROC), ("cbClsExtra", ctypes.c_int),
                    ("cbWndExtra", ctypes.c_int), ("hInstance", wintypes.HINSTANCE), ("hIcon", wintypes.HANDLE),
                    ("hCursor", wintypes.HANDLE), ("hbrBackground", wintypes.HANDLE), ("lpszMenuName", wintypes.LPCWSTR),
                    ("lpszClassName", wintypes.LPCWSTR)]
    proc = WNDPROC(lambda h, m, w, l: u32.DefWindowProcW(h, m, w, l))
    k32.GetModuleHandleW.restype = wintypes.HINSTANCE
    wc = WNDCLASSW()
    wc.lpfnWndProc, wc.hInstance, wc.lpszClassName = proc, k32.GetModuleHandleW(None), cls
    u32.RegisterClassW.argtypes = [ctypes.POINTER(WNDCLASSW)]
    u32.CreateWindowExW.restype = wintypes.HWND
    u32.CreateWindowExW.argtypes = [wintypes.DWORD, wintypes.LPCWSTR, wintypes.LPCWSTR, wintypes.DWORD, ctypes.c_int,
                                    ctypes.c_int, ctypes.c_int, ctypes.c_int, wintypes.HWND, wintypes.HANDLE,
                                    wintypes.HINSTANCE, wintypes.LPVOID]
    if not u32.RegisterClassW(ctypes.byref(wc)):
        raise OSError("RegisterClassW failed")
    # WS_OVERLAPPED sem WS_VISIBLE: janela real de nível superior que ninguém consegue ver
    h = u32.CreateWindowExW(0, cls, "stand-in", 0, 0, 0, 10, 10, None, None, wc.hInstance, None)
    if not h:
        raise OSError("CreateWindowExW failed")
    return h, proc, wc


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--i", type=int, default=0)
    ap.add_argument("--mutex")
    ap.add_argument("--rename-mutex", action="store_true")
    ap.add_argument("--window-class")
    ap.add_argument("--unique-window-class", action="store_true")
    ap.add_argument("--ready-file")
    ap.add_argument("--ready-delay", type=float, default=0.0)
    ap.add_argument("--log")
    ap.add_argument("--port-base", type=int, default=0)
    ap.add_argument("--role", default="")
    ap.add_argument("--bind-port", type=int, default=0)
    ap.add_argument("--crash-after", type=float, default=0.0)
    ap.add_argument("--spawn-child", action="store_true")
    ap.add_argument("--lifetime", type=float, default=90.0)
    ap.add_argument("--tag", default="", help="ignorado; permite que um teste encontre seus próprios processos substitutos pela linha de comando")
    a = ap.parse_args()
    pid = os.getpid()
    if a.spawn_child:
        argv = [x for x in sys.argv[1:] if x != "--spawn-child"]
        subprocess.Popen([sys.executable, "-I", os.path.abspath(__file__)] + argv, stdin=subprocess.DEVNULL,
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, close_fds=True)
        log(a.log, f"loader {pid} started a child and exits")
        return 0
    keep = []
    if a.mutex:
        k32 = ctypes.WinDLL("kernel32", use_last_error=True)
        k32.CreateMutexW.restype = wintypes.HANDLE
        k32.CreateMutexW.argtypes = [wintypes.LPVOID, wintypes.BOOL, wintypes.LPCWSTR]
        name = a.mutex + (f"-{pid}" if a.rename_mutex else "")
        ctypes.set_last_error(0)
        h = k32.CreateMutexW(None, False, name)
        if ctypes.get_last_error() == 183:           # ERROR_ALREADY_EXISTS
            log(a.log, f"pid {pid}: another instance is already running (mutex {name})")
            return 3
        keep.append(h)
    if a.window_class:
        cls = a.window_class + (f"-{pid}" if a.unique_window_class else "")
        u32 = ctypes.WinDLL("user32", use_last_error=True)
        u32.FindWindowW.argtypes = [wintypes.LPCWSTR, wintypes.LPCWSTR]
        u32.FindWindowW.restype = wintypes.HWND
        if u32.FindWindowW(cls, None):
            log(a.log, f"pid {pid}: another instance is already running (window class {cls})")
            return 4
        keep.append(make_window(cls))
    if a.port_base:
        srv = socket.socket()
        srv.bind(("127.0.0.1", a.port_base + a.i))
        srv.listen(5)
        keep.append(srv)
    if a.bind_port and a.role == "host":
        srv = socket.socket()
        try:
            srv.bind(("127.0.0.1", a.bind_port))
        except OSError:
            log(a.log, f"pid {pid}: cannot listen on port {a.bind_port}")
            return 6
        srv.listen(5)
        keep.append(srv)
    elif a.bind_port and a.role == "client":
        try:
            socket.create_connection(("127.0.0.1", a.bind_port), timeout=2).close()
        except OSError:
            log(a.log, f"pid {pid}: no host on port {a.bind_port}")
            return 5
    if a.role:
        log(a.log, f"role={a.role} port={a.bind_port}")
    log(a.log, f"pid {pid}: started instance {a.i}")
    t0 = time.time()
    ready_done = False
    while time.time() - t0 < a.lifetime:
        if not ready_done and time.time() - t0 >= a.ready_delay:
            if a.ready_file:
                with open(a.ready_file, "w") as f:
                    f.write("ready")
            log(a.log, f"pid {pid}: ready")
            ready_done = True
        if a.crash_after and time.time() - t0 >= a.crash_after:
            log(a.log, "CRASH code=1")
            return 1
        time.sleep(0.05)
    return 0


if __name__ == "__main__":
    sys.exit(main())
