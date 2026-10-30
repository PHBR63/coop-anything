"""Utilitários de processos e janelas do Windows (somente ctypes, sem pacotes de terceiros).

Nada aqui interfere em outro processo: não fecha identificadores, não acessa memória nem faz injeção. Cada chamada
apenas lê informações de processos, enumera janelas ou encerra um PID fornecido pelo chamador.
"""
from __future__ import annotations

import ctypes
import os
import socket
import subprocess
import time
from ctypes import wintypes
from typing import Dict, List, Optional, Set, Tuple

if os.name != "nt":  # pragma: no cover - the tools target Windows
    raise ImportError("gplib.winproc needs Windows")

k32 = ctypes.WinDLL("kernel32", use_last_error=True)
u32 = ctypes.WinDLL("user32", use_last_error=True)
PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
STILL_ACTIVE = 259
SW_HIDE, SW_SHOWMINNOACTIVE = 0, 7

k32.OpenProcess.restype = wintypes.HANDLE
k32.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
k32.CloseHandle.argtypes = [wintypes.HANDLE]
k32.GetExitCodeProcess.argtypes = [wintypes.HANDLE, ctypes.POINTER(wintypes.DWORD)]
k32.GetProcessTimes.argtypes = [wintypes.HANDLE] + [ctypes.POINTER(wintypes.FILETIME)] * 4
k32.QueryFullProcessImageNameW.argtypes = [wintypes.HANDLE, wintypes.DWORD, wintypes.LPWSTR, ctypes.POINTER(wintypes.DWORD)]
u32.IsIconic.argtypes = [wintypes.HWND]
u32.IsWindowVisible.argtypes = [wintypes.HWND]
u32.ShowWindowAsync.argtypes = [wintypes.HWND, ctypes.c_int]
u32.FindWindowW.argtypes = [wintypes.LPCWSTR, wintypes.LPCWSTR]
u32.FindWindowW.restype = wintypes.HWND
EnumProc = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)


# ------------------------------------------------------------------------------------------ processos
def process_info(pid: int) -> Optional[Dict]:
    """{"name": nome do arquivo de imagem em minúsculas, "created": horário de criação} de um PID em execução, ou None.
    O par (pid, created) identifica um processo definitivamente; um PID reutilizado tem outro horário de criação."""
    h = k32.OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, False, int(pid))
    if not h:
        return None
    try:
        code = wintypes.DWORD()
        k32.GetExitCodeProcess(h, ctypes.byref(code))
        if code.value != STILL_ACTIVE:
            return None
        buf = ctypes.create_unicode_buffer(1024)
        size = wintypes.DWORD(1024)
        name = os.path.basename(buf.value).lower() if k32.QueryFullProcessImageNameW(h, 0, buf, ctypes.byref(size)) else ""
        ft = [wintypes.FILETIME() for _ in range(4)]
        k32.GetProcessTimes(h, *[ctypes.byref(f) for f in ft])
        return {"name": name, "created": (ft[0].dwHighDateTime << 32) | ft[0].dwLowDateTime}
    finally:
        k32.CloseHandle(h)


def pid_alive(pid: int) -> bool:
    return process_info(pid) is not None


def list_pids(image_name: str) -> List[int]:
    "Todo PID em execução com este nome de imagem, nosso ou não. Apenas para leitura e contagem."
    out = subprocess.run(["tasklist", "/FI", f"IMAGENAME eq {image_name}", "/FO", "CSV", "/NH"],
                         capture_output=True, text=True).stdout
    pids = []
    for ln in out.splitlines():
        parts = [p.strip('"') for p in ln.split('","')]
        if len(parts) > 1 and parts[0].strip('"').lower() == image_name.lower():
            try:
                pids.append(int(parts[1]))
            except ValueError:
                pass
    return pids


def kill_pid(pid: int) -> None:
    "Encerra um PID e seus filhos. Os chamadores devem passar apenas um PID que iniciaram (veja Backend.kill)."
    subprocess.run(["taskkill", "/PID", str(int(pid)), "/F", "/T"], capture_output=True)


class PROCESSENTRY32W(ctypes.Structure):
    _fields_ = [("dwSize", wintypes.DWORD), ("cntUsage", wintypes.DWORD), ("th32ProcessID", wintypes.DWORD),
                ("th32DefaultHeapID", ctypes.c_size_t), ("th32ModuleID", wintypes.DWORD), ("cntThreads", wintypes.DWORD),
                ("th32ParentProcessID", wintypes.DWORD), ("pcPriClassBase", ctypes.c_long), ("dwFlags", wintypes.DWORD),
                ("szExeFile", ctypes.c_wchar * 260)]


def process_table() -> List[Tuple[int, int, str]]:
    "[(pid, PID do pai, nome da imagem em minúsculas)] para cada processo em execução."
    k32.CreateToolhelp32Snapshot.restype = wintypes.HANDLE
    k32.CreateToolhelp32Snapshot.argtypes = [wintypes.DWORD, wintypes.DWORD]
    k32.Process32FirstW.argtypes = [wintypes.HANDLE, ctypes.POINTER(PROCESSENTRY32W)]
    k32.Process32NextW.argtypes = [wintypes.HANDLE, ctypes.POINTER(PROCESSENTRY32W)]
    snap = k32.CreateToolhelp32Snapshot(2, 0)       # TH32CS_SNAPPROCESS
    out: List[Tuple[int, int, str]] = []
    if not snap or snap == wintypes.HANDLE(-1).value:
        return out
    try:
        e = PROCESSENTRY32W()
        e.dwSize = ctypes.sizeof(e)
        ok = k32.Process32FirstW(snap, ctypes.byref(e))
        while ok:
            out.append((e.th32ProcessID, e.th32ParentProcessID, e.szExeFile.lower()))
            ok = k32.Process32NextW(snap, ctypes.byref(e))
    finally:
        k32.CloseHandle(snap)
    return out


def descendants(root_pid: int, image_name: str = "") -> List[int]:
    """PIDs abaixo de root_pid na árvore de processos (filhos, netos, ...), opcionalmente apenas aqueles com este
    nome de imagem. Funciona depois que a raiz encerra, pois um filho mantém o PID do pai que o criou.
    É assim que um inicializador encontra o processo real do jogo por trás de um carregador, sem adivinhar só pelo nome."""
    table = process_table()
    found: Set[int] = set()
    frontier = {int(root_pid)}
    while frontier:
        nxt = {pid for pid, ppid, _ in table if ppid in frontier and pid not in found and pid != root_pid}
        found |= nxt
        frontier = nxt
    want = image_name.lower()
    return sorted(pid for pid, _, name in table if pid in found and (not want or name == want))


def proc_stats(pid: int) -> Dict:
    "Conjunto de trabalho (MB) e segundos acumulados de CPU de pid; {} se já encerrou."
    class PMC(ctypes.Structure):
        _fields_ = [("cb", wintypes.DWORD), ("PageFaultCount", wintypes.DWORD), ("PeakWorkingSetSize", ctypes.c_size_t),
                    ("WorkingSetSize", ctypes.c_size_t), ("QuotaPeakPagedPoolUsage", ctypes.c_size_t),
                    ("QuotaPagedPoolUsage", ctypes.c_size_t), ("QuotaPeakNonPagedPoolUsage", ctypes.c_size_t),
                    ("QuotaNonPagedPoolUsage", ctypes.c_size_t), ("PagefileUsage", ctypes.c_size_t),
                    ("PeakPagefileUsage", ctypes.c_size_t)]
    h = k32.OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, False, int(pid))
    if not h:
        return {}
    try:
        pm = PMC()
        pm.cb = ctypes.sizeof(pm)
        psapi = ctypes.WinDLL("psapi")
        psapi.GetProcessMemoryInfo.argtypes = [wintypes.HANDLE, ctypes.POINTER(PMC), wintypes.DWORD]
        psapi.GetProcessMemoryInfo(h, ctypes.byref(pm), pm.cb)
        ft = [wintypes.FILETIME() for _ in range(4)]
        k32.GetProcessTimes(h, *[ctypes.byref(f) for f in ft])
        t = lambda f: ((f.dwHighDateTime << 32) | f.dwLowDateTime) / 1e7  # noqa: E731
        return {"ws_mb": round(pm.WorkingSetSize / 2**20), "cpu_s": round(t(ft[2]) + t(ft[3]), 2)}
    finally:
        k32.CloseHandle(h)


def system_memory() -> Dict:
    class MS(ctypes.Structure):
        _fields_ = [("dwLength", wintypes.DWORD), ("dwMemoryLoad", wintypes.DWORD), ("ullTotalPhys", ctypes.c_ulonglong),
                    ("ullAvailPhys", ctypes.c_ulonglong), ("ullTotalPageFile", ctypes.c_ulonglong),
                    ("ullAvailPageFile", ctypes.c_ulonglong), ("ullTotalVirtual", ctypes.c_ulonglong),
                    ("ullAvailVirtual", ctypes.c_ulonglong), ("ullAvailExtendedVirtual", ctypes.c_ulonglong)]
    m = MS()
    m.dwLength = ctypes.sizeof(m)
    k32.GlobalMemoryStatusEx(ctypes.byref(m))
    return {"total_gb": round(m.ullTotalPhys / 2**30, 1), "avail_gb": round(m.ullAvailPhys / 2**30, 1),
            "load_pct": m.dwMemoryLoad}


# ------------------------------------------------------------------------------------------ janelas
def windows_of(pids) -> List[Tuple[int, int, str, bool]]:
    "[(hwnd, pid, title, minimized)] para as janelas visíveis de nível superior desses PIDs."
    want = set(pids)
    out = []

    def cb(h, _):
        p = wintypes.DWORD()
        u32.GetWindowThreadProcessId(h, ctypes.byref(p))
        if p.value in want and u32.IsWindowVisible(h):
            n = u32.GetWindowTextLengthW(h)
            buf = ctypes.create_unicode_buffer(n + 1)
            u32.GetWindowTextW(h, buf, n + 1)
            out.append((h, p.value, buf.value, bool(u32.IsIconic(h))))
        return True
    u32.EnumWindows(EnumProc(cb), 0)
    return out


def minimize_windows(pid: int, timeout_s: float = 60.0, settle_s: float = 3.0) -> int:
    """Minimiza toda janela visível de nível superior de pid SEM ativá-la (SW_SHOWMINNOACTIVE por
    ShowWindowAsync). Nunca assume o primeiro plano nem envia entrada, portanto não perturba o que
    o usuário está fazendo. Continua por settle_s após aparecer a última janela nova, pois muitos jogos
    recriam sua janela depois da tela de abertura."""
    seen: Set[int] = set()

    def cb(hwnd, _):
        p = wintypes.DWORD()
        u32.GetWindowThreadProcessId(hwnd, ctypes.byref(p))
        if p.value == pid and u32.IsWindowVisible(hwnd) and not u32.IsIconic(hwnd):
            u32.ShowWindowAsync(hwnd, SW_SHOWMINNOACTIVE)
            seen.add(hwnd)
        return True
    proc = EnumProc(cb)
    t0 = last = time.time()
    while time.time() - t0 < timeout_s and pid_alive(pid):
        n = len(seen)
        u32.EnumWindows(proc, 0)
        if len(seen) != n:
            last = time.time()
        elif seen and time.time() - last > settle_s:
            break
        time.sleep(0.1)
    return len(seen)


def find_window(class_name: Optional[str] = None, title: Optional[str] = None) -> int:
    """Identificador de janela de nível superior por classe e/ou título, 0 se não houver (janelas ocultas contam). Muitos jogos recusam
    iniciar quando isso encontra uma janela de uma cópia anterior."""
    return int(u32.FindWindowW(class_name, title) or 0)


# ------------------------------------------------------------------------------------------ sondagens de prontidão
def pipe_exists(name: str) -> bool:
    "True se o pipe nomeado existir (os.path.exists não é confiável para pipes). Um pipe ocupado ainda existe."
    ctypes.set_last_error(0)
    if k32.WaitNamedPipeW(name, 1):
        return True
    return ctypes.get_last_error() != 2     # 2 == ERROR_FILE_NOT_FOUND


def mutex_exists(name: str) -> bool:
    "True se existir agora um mutex com esse nome (abre com o direito mínimo e o fecha)."
    k32.OpenMutexW.restype = wintypes.HANDLE
    k32.OpenMutexW.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.LPCWSTR]
    h = k32.OpenMutexW(0x00100000, False, name)    # SYNCHRONIZE
    if h:
        k32.CloseHandle(h)
        return True
    return False


def tcp_open(port: int, host: str = "127.0.0.1", timeout_s: float = 0.5) -> bool:
    try:
        socket.create_connection((host, int(port)), timeout=timeout_s).close()
        return True
    except OSError:
        return False


def startup_info(window: str):
    """STARTUPINFO para uma inicialização: 'minimized' (sem ativação, para o aplicativo em primeiro plano do usuário manter o foco),
    'hidden' ou 'normal' (None: o jogo decide)."""
    if window == "normal":
        return None
    si = subprocess.STARTUPINFO()
    si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    si.wShowWindow = SW_SHOWMINNOACTIVE if window == "minimized" else SW_HIDE
    return si
