"""Coleta evidências após uma falha do jogo: logs do jogo e registro de falha do Windows em uma única pasta.

    from gplib.crashlog import collect_crash_report
    summary = collect_crash_report(cfg, "runs/t1/crash", instance=0)

    gamepool.py --config game.json crashlog DEST [--instance 0] [--minutes 30]

O que é lido vem da configuração (bloco crash): `logs` são caminhos relativos à pasta da instância (ou à pasta
do jogo se nenhuma instância for informada); `markers` são textos que identificam linhas de falha nesses logs;
`wer_match` é uma expressão regular para o log Application do Windows (evento 1000, falha de aplicativo),
com padrão igual ao nome da imagem do jogo sem ".exe".

Um jogo que falha ao sair ou mostra sua própria janela de "critical error" frequentemente nem grava o restante do log;
portanto, não haver erro no log não comprova nada. O registro do Windows e o código de saída são a segunda fonte.
"""
from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import time
from pathlib import Path
from typing import Callable, Dict, List, Optional

from .config import Config

_PS = ("Get-WinEvent -FilterHashtable @{LogName='Application';Id=1000;StartTime=(Get-Date).AddMinutes(-$env:GP_MINUTES)} "
       "-ErrorAction SilentlyContinue | ? { $_.Message -match $env:GP_MATCH } | select -First 3 | "
       "% { $_.TimeCreated.ToString('s') + ' ' + ($_.Message -replace \"`r?`n\", ' | ') }")


def _wer_events(minutes: int, match: str) -> List[str]:
    env = dict(os.environ, GP_MINUTES=str(int(minutes)), GP_MATCH=match)
    try:
        r = subprocess.run(["powershell", "-NoProfile", "-Command", _PS], capture_output=True, text=True, timeout=60, env=env)
        return [l for l in r.stdout.splitlines() if l.strip()]
    except Exception as e:  # noqa: BLE001
        return [f"(could not query the event log: {e})"]


def collect_crash_report(cfg: Config, dest, instance: Optional[int] = None, event_minutes: int = 30,
                         event_query: Optional[Callable[[int], List[str]]] = None) -> Dict:
    """Copia os logs para `dest` e grava summary.json (últimas linhas dos logs, linhas com marcadores e registros de falha do Windows).
    event_query(minutes) -> list of text pode ser injetada (como nos testes) em vez de ler o log real de eventos."""
    base = cfg.instance_dir(instance) if instance is not None else cfg.game_dir
    dest = Path(dest)
    dest.mkdir(parents=True, exist_ok=True)
    crash = cfg["crash"]
    copied, tails, marked = [], {}, []
    for rel in crash["logs"]:
        src = base / rel
        if src.is_file():
            shutil.copy2(src, dest / src.name)
            copied.append(src.name)
            lines = src.read_text(errors="replace").splitlines()
            tails[src.name] = lines[-8:]
            marked += [f"{src.name}: {l}" for l in lines if any(m in l for m in crash["markers"])][-5:]
    match = crash["wer_match"] or re.escape(re.sub(r"\.exe$", "", cfg.process_name or cfg.name))
    events = (event_query or (lambda m: _wer_events(m, match)))(event_minutes)
    summary = {"collected_at": time.strftime("%Y-%m-%dT%H:%M:%S"), "base_dir": str(base), "files": copied,
               "marker_lines": marked, "windows_crash_records": events, "log_tails": tails}
    (dest / "summary.json").write_text(json.dumps(summary, indent=2))
    return summary


def main(cfg: Config, argv: List[str]) -> int:
    import argparse
    ap = argparse.ArgumentParser(prog="gamepool crashlog")
    ap.add_argument("dest")
    ap.add_argument("--instance", type=int)
    ap.add_argument("--minutes", type=int, default=30)
    a = ap.parse_args(argv)
    print(json.dumps(collect_crash_report(cfg, a.dest, a.instance, a.minutes), indent=2)[:4000])
    return 0
