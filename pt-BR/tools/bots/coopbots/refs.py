"""Referências de roteiro a partir de um arquivo de cenário.

Um roteiro precisa de elementos nomeados ("raiders", "item", "quest"). A ferramenta de cenários (tools/scenarios) permite
um bloco `refs` que os nomeia com strings `$alias`; esta função converte esse bloco em identificadores simples. Ela lê
o próprio JSON, de modo que a ferramenta de bots não precisa importar a ferramenta de cenários.
"""
import json
import re
from pathlib import Path
from typing import Any, Dict

_ALIAS = re.compile(r"^\$([A-Za-z][A-Za-z0-9_]*)$")


def refs_from_scenario(scenario: Any) -> Dict[str, Any]:
    "`scenario` é um dicionário ou caminho de um arquivo JSON de cenário. Retorna {ref name: id, list of ids, or literal value}."
    sc = json.loads(Path(scenario).read_text(encoding="utf-8")) if not isinstance(scenario, dict) else scenario
    objects = sc.get("objects") or {}

    def one(v):
        if isinstance(v, str):
            m = _ALIAS.match(v)
            if m:
                if m.group(1) not in objects:
                    raise KeyError("refs use unknown alias %s" % v)
                return str(objects[m.group(1)]["id"])
            return v
        if isinstance(v, list):
            return [one(x) for x in v]
        if isinstance(v, dict):
            return {k: one(x) for k, x in v.items()}
        return v
    return {k: one(v) for k, v in (sc.get("refs") or {}).items()}
