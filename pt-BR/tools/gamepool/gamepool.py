#!/usr/bin/env python3
"""Executa várias cópias de um jogo Windows em um PC para testes. Uma linha de comando para tudo.

    python -I tools/gamepool/gamepool.py [--config game.json] COMMAND [options]

Cópias (consulte README.md, "Quick start")
    provision --n 2        cria n instalações isoladas com hardlinks (--pairs N: N pares host/cliente)
    show / destroy         descreve ou remove as cópias
    up --n 2               reserva vagas, inicia as cópias uma a uma e aguarda prontidão
    up --pairs 3           3 pares host/cliente, cada um em sua porta (recusa se a RAM livre for insuficiente)
    status [--pairs]       quais cópias existem e estão ativas; --pairs: uma linha por par host/cliente
    swap --instances 0,1   solicita ao adaptador substituir código nas cópias em execução (hook de recarregamento)
    down                   encerra somente as cópias iniciadas por `up` e libera as vagas
    job --id X --n 2 -- CMD     executa CMD com GAMEPOOL_INSTANCES=0,1 e coleta logs
    smoke --n 2 --minutes 10    inicia cópias e as verifica por algum tempo
    probe --seconds 30          registra os estados das janelas de uma cópia recém-iniciada
Conjunto de instâncias já inicializadas
    pool up --size 2       mantém n cópias ativas e as cede por reservas temporárias
    pool status | lease | release | down
Funções auxiliares
    lowcost apply|doc|verify    configurações de baixo custo por instância definidas na configuração
    crashlog DEST               coleta logs e o registro de falha do Windows
    measure --label L           RAM e CPU das cópias do conjunto

--config FILE (ou a variável GAMEPOOL_CONFIG) indica o JSON específico do jogo. O estado fica no local definido por GAMEPOOL_DIR
ou, na ausência dele, em <repo>/local/gamepool (o Git ignora local/). Todo comando altera somente pastas privadas de instância
e processos que ele próprio iniciou.
"""
import argparse
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from gplib.config import Config, ConfigError, expand  # noqa: E402

CONFIGLESS_POOL = {"status", "lease", "release", "down"}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--config")
    ap.add_argument("command", choices=["provision", "show", "destroy", "up", "down", "status", "swap", "job", "smoke", "probe",
                                        "pool", "daemon", "lowcost", "crashlog", "measure"])
    ap.add_argument("rest", nargs=argparse.REMAINDER)
    a = ap.parse_args(argv)
    rest = list(a.rest)
    cfg_path = a.config or os.environ.get("GAMEPOOL_CONFIG")
    try:
        if a.command == "pool" and rest and rest[0] in CONFIGLESS_POOL:
            from gplib import poolcli
            return poolcli.main(cfg_path or "", rest)
        if a.command == "measure":
            from gplib import measure
            return measure.main(None, rest)
        cfg = Config.load(cfg_path)
        if a.command in ("provision", "show", "destroy"):
            from gplib import instances
            return instances.main(cfg, [a.command] + rest)
        if a.command in ("up", "down", "status", "swap", "job"):
            from gplib import launcher
            return launcher.main(cfg, [a.command] + rest)
        if a.command in ("smoke", "probe"):
            from gplib import smoke
            return smoke.main(cfg, [a.command] + rest)
        if a.command == "pool":
            from gplib import poolcli
            return poolcli.main(str(Path(expand(cfg_path)).resolve()), rest)
        if a.command == "daemon":
            from gplib import daemon
            return daemon.main(cfg, rest)
        if a.command == "lowcost":
            from gplib import lowcost
            return lowcost.main(cfg, rest)
        from gplib import crashlog
        return crashlog.main(cfg, rest)
    except ConfigError as e:
        print(f"config error: {e}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
