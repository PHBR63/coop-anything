"""Perfil de baixo custo: configurações privadas por instância que reduzem o custo de manter uma cópia do jogo ativa.

O perfil é dado no arquivo de configuração do jogo (lowcost.rows), não código. Cada linha é
{file, section, key, value, why, status, opt_in?}. Exemplos comuns: janela pequena, sem vsync, limite de quadros,
sem sombras, sem antisserrilhamento e pular vídeos de introdução.

Edita SOMENTE arquivos de uma pasta de instância (consulte instances.guard_write): nunca as configurações do usuário,
a instalação, um arquivo com mais de um hardlink ou um link.

    python -I tools/gamepool/gamepool.py --config game.json lowcost apply --instance 0 [--opt grids=3]
    python -I tools/gamepool/gamepool.py --config game.json lowcost doc        # tabela Markdown de todas as linhas
    python -I tools/gamepool/gamepool.py --config game.json lowcost verify     # quais chaves existem nos arquivos base

Estado de uma linha (texto livre exibido na tabela): required (necessário para a operação local à instância), standard
(chave que se espera que o jogo leia), guess (nome retirado de um jogo do mesmo motor; a maioria dos motores ignora
chaves desconhecidas, portanto uma hipótese errada não custa nada, mas a economia só é conhecida após medição), opt-in.

Uma linha opt-in contém "opt_in": "<option name>" e só é aplicada se a opção for passada com --opt
NAME=VALUE (ou options={"NAME": "VALUE"} no código). "value_from_option": true usa o valor da opção como valor
da linha. "option_regex" rejeita valores que não correspondam ao padrão (por exemplo, apenas números ímpares).
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Dict, List, Optional

from .config import Config
from .inifile import ini_get, ini_set
from .instances import UnsafeTarget, base_text, guard_write


def rows(cfg: Config, options: Optional[Dict[str, str]] = None) -> List[Dict]:
    opts = dict(options or {})
    out = []
    for r in cfg["lowcost"]["rows"]:
        r = dict(r)
        name = r.get("opt_in")
        if name:
            if name not in opts:
                continue
            if r.get("option_regex") and not re.fullmatch(r["option_regex"], str(opts[name])):
                raise ValueError(f"option {name}={opts[name]!r} does not match {r['option_regex']}")
            if r.get("value_from_option"):
                r["value"] = str(opts[name])
        out.append(r)
    unknown = set(opts) - {r.get("opt_in") for r in cfg["lowcost"]["rows"]}
    if unknown:
        raise ValueError(f"unknown option(s) {sorted(unknown)}; the config defines {sorted(x for x in {r.get('opt_in') for r in cfg['lowcost']['rows']} if x)}")
    return out


def _enc(cfg: Config, name: str) -> str:
    return cfg["config_files"].get(name, {}).get("encoding", "latin-1")


def apply(cfg: Config, instance_dir: Path, options: Optional[Dict[str, str]] = None, check: bool = True) -> Dict[str, int]:
    "Edita os arquivos da instância no próprio local. Retorna {file: rows written}. Idempotente."
    d = Path(instance_dir)
    selected = rows(cfg, options)
    texts: Dict[str, str] = {}
    for name in sorted({r["file"] for r in selected}):
        f = d / name
        if check:
            guard_write(cfg, f)
        texts[name] = f.read_text(encoding=_enc(cfg, name)) if f.exists() else ""
    n = {name: 0 for name in texts}
    for r in selected:
        texts[r["file"]] = ini_set(texts[r["file"]], r["section"], r["key"], str(r["value"]))
        n[r["file"]] += 1
    for name, t in texts.items():
        (d / name).write_text(t, encoding=_enc(cfg, name), newline="")
    for fname, section, key, want in cfg["lowcost"]["post_checks"]:
        f = d / fname
        got = ini_get(f.read_text(encoding=_enc(cfg, fname)) if f.exists() else "", section, key)
        if got != want:
            raise UnsafeTarget(f"{fname} [{section}] {key} is {got!r} after apply, expected {want!r}")
    return n


def verify(cfg: Config) -> Dict[str, List[str]]:
    "Somente leitura: quais chaves de perfil existem nos arquivos base usados para iniciar as instâncias."
    found: Dict[str, List[str]] = {"present": [], "absent": []}
    base = {name: base_text(cfg, name) for name in cfg["config_files"]}
    for r in cfg["lowcost"]["rows"]:
        has = r["file"] in base and ini_get(base[r["file"]], r["section"], r["key"]) is not None
        found["present" if has else "absent"].append(f"{r['file']}:{r['section']}:{r['key']}")
    return found


def render_doc(cfg: Config) -> str:
    lines = ["| File | Section | Key | Value | Why | Status |", "|---|---|---|---|---|---|"]
    for r in cfg["lowcost"]["rows"]:
        lines.append(f"| {r['file']} | {r['section']} | `{r['key']}` | `{r['value']}` | {r.get('why', '')} | {r.get('status', '')} |")
    return "\n".join(lines)


def main(cfg: Config, argv: List[str]) -> int:
    import argparse
    import json
    ap = argparse.ArgumentParser(prog="gamepool lowcost")
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("apply")
    p.add_argument("--instance", type=int, required=True)
    p.add_argument("--opt", action="append", default=[], metavar="NAME=VALUE")
    sub.add_parser("doc")
    sub.add_parser("verify")
    a = ap.parse_args(argv)
    if a.cmd == "doc":
        print(render_doc(cfg))
    elif a.cmd == "verify":
        cfg.require_dirs()
        print(json.dumps(verify(cfg), indent=1))
    else:
        cfg.require_dirs()
        opts = dict(o.partition("=")[::2] for o in a.opt)
        print(apply(cfg, cfg.instance_dir(a.instance), opts))
    return 0
