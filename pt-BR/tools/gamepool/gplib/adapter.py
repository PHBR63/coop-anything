"""Adaptador: único ponto em que o conjunto de instâncias conversa com o jogo.

O conjunto precisa de quatro respostas de uma cópia em execução: está pronta?, continua saudável?, algo a fazer quando
ficar pronta (como carregar um salvamento) e a reserva terminou, faça a limpeza. O adaptador padrão responde às duas
primeiras por uma sondagem descrita na configuração (ready.type):

    process     processo ativo (settle_s segundos após iniciar)
    window      processo tem uma janela visível de nível superior
    file        arquivo existe, caminho relativo à pasta da instância, {i} é seu número
    log_line    arquivo contém um texto (ready.path, ready.text)
    tcp_port    127.0.0.1:(base_port + i) aceita conexão
    named_pipe  canal nomeado ready.name existe, {i} é o número da instância

Jogos com ponte interna (plugin de scripts que responde a pings, carrega salvamentos e executa etapas de teste) usam
algumas linhas de Python: defina "adapter": "my_adapter.py:MyAdapter" na configuração (caminho relativo ao arquivo
de configuração), derive Adapter e sobrescreva o necessário. O arquivo do adaptador é seu código e executa com
suas permissões, como qualquer script executado por você.

    class MyAdapter(Adapter):
        def probe(self, i, pid):            # saudável agora?
            return my_bridge_ping(i)
        def after_ready(self, i, pid):      # executa uma vez após cada (re)inicialização
            my_bridge_load_save(i, "base")
        def on_release(self, i):            # reserva terminou; libera travas no jogo
            my_bridge_unlock(i)

Um jogo com ferramenta de recarregamento (substituir código em cópia ativa sem reiniciar) acrescenta dois hooks.
`gamepool.py swap` os chama e não faz mais nada específico do jogo:

        def can_swap(self, i, pid, payload):   # None se a cópia i permitir troca; caso contrário, motivo da recusa
            return None if my_tool_can_reload(i) else "no reload pipe"
        def swap(self, i, pid, payload):       # faz a troca; lança exceção ou retorna {"ok": False, "detail": ...} em falha
            return my_tool_reload(i, **payload)
"""
from __future__ import annotations

import importlib.util
import time
from pathlib import Path
from typing import Callable, Dict, Optional

from . import winproc
from .config import Config, ConfigError


class Adapter:
    def __init__(self, cfg: Config):
        self.cfg = cfg
        self.ready = cfg["ready"]

    # ---- hooks que um adaptador personalizado pode sobrescrever
    def prepare(self, i: int) -> None:
        """Antes de iniciar a instância i. O padrão remove um arquivo de prontidão obsoleto (ready.type 'file'),
        para uma cópia reiniciada não ser considerada pronta por causa do arquivo da execução anterior."""
        if self.ready["type"] == "file":
            (self.cfg.instance_dir(i) / self.cfg.fmt(self.ready["path"], i)).unlink(missing_ok=True)

    def probe(self, i: int, pid: int) -> bool:
        "True quando a instância i (processo pid) está pronta e saudável neste momento."
        return probe(self.cfg, i, pid)

    def after_ready(self, i: int, pid: int) -> None:
        "Depois que a instância fica pronta (a cada inicialização e reinicialização)."

    def on_release(self, i: int) -> None:
        "Uma reserva da instância i terminou."

    def can_swap(self, i: int, pid: int, payload: Dict[str, str]) -> Optional[str]:
        """None se o código da cópia i puder ser substituído em execução; caso contrário, o motivo da impossibilidade. O padrão
        recusa, então `swap` não altera nenhuma cópia, a menos que um adaptador forneça o hook."""
        return "this adapter has no swap hook (override can_swap and swap in your adapter)"

    def swap(self, i: int, pid: int, payload: Dict[str, str]) -> Optional[Dict]:
        """Substitui o código da cópia i em execução. payload contém os pares --arg KEY=VALUE da linha de comando. Lance uma exceção
        ou retorne dicionário com "ok": False e "detail" para relatar falha. Um dicionário retornado é exibido no relatório."""
        raise NotImplementedError("this adapter has no swap hook")

    # ---- controlado pelo backend
    def wait_ready(self, i: int, pid: int, alive: Callable[[int], bool], timeout_s: float = 0.0) -> bool:
        limit = timeout_s or float(self.ready.get("timeout_s", 300))
        t0 = time.monotonic()
        settle = float(self.ready.get("settle_s", 0))
        while time.monotonic() - t0 < limit:
            if not alive(pid):
                return False
            if self.probe(i, pid):
                if settle and time.monotonic() - t0 < settle:
                    time.sleep(min(0.5, settle))
                    continue
                self.after_ready(i, pid)
                return True
            time.sleep(float(self.ready.get("poll_s", 1.0)))
        return False


def probe(cfg: Config, i: int, pid: int) -> bool:
    r = cfg["ready"]
    t = r["type"]
    if t == "process":
        return winproc.pid_alive(pid)
    if t == "window":
        wins = winproc.windows_of({pid})
        need = r.get("title_contains", "")
        return any(need.lower() in title.lower() for _, _, title, _ in wins) if wins else False
    if t in ("file", "log_line"):
        p = cfg.instance_dir(i) / cfg.fmt(r["path"], i)
        if not p.exists():
            return False
        if t == "file":
            return True
        try:
            return r["text"] in p.read_text(errors="replace")
        except OSError:
            return False
    if t == "tcp_port":
        return winproc.tcp_open(int(r["base_port"]) + int(i))
    if t == "named_pipe":
        return winproc.pipe_exists(cfg.fmt(r["name"], i))
    raise ConfigError(f"unknown ready.type {t!r}")


def load_adapter(cfg: Config) -> Adapter:
    spec = cfg["adapter"]
    if not spec:
        return Adapter(cfg)
    path, _, cls = spec.partition(":")
    f = Path(path)
    if not f.is_absolute():
        f = cfg.base_dir / f
    if not f.is_file() or not cls:
        raise ConfigError(f"adapter must be 'file.py:ClassName' pointing at an existing file, got {spec!r}")
    s = importlib.util.spec_from_file_location("gamepool_user_adapter", f)
    mod = importlib.util.module_from_spec(s)
    s.loader.exec_module(mod)
    ad = getattr(mod, cls)(cfg)
    if not isinstance(ad, Adapter):
        raise ConfigError(f"{cls} must subclass gplib.adapter.Adapter")
    return ad
