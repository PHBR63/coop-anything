"""Pequeno editor de texto INI que mantém o restante do arquivo como estava (finais de linha, comentários, ordem).

Os nomes de seções e chaves são comparados sem distinguir maiúsculas e minúsculas. Jogos têm particularidades de INI
(espaços nos nomes das chaves, valores vazios), então o editor trabalha sobre linhas de texto e nunca serializa novamente o arquivo.
"""
from __future__ import annotations

import re
from typing import Optional


def ini_set(text: str, section: str, key: str, value: str) -> str:
    "Define key em [section], acrescentando a seção ou a chave se estiver ausente. Mantém arquivos CRLF com CRLF."
    nl = "\r\n" if "\r\n" in text else "\n"
    lines = text.split(nl) if text else []
    sec_re = re.compile(r"^\s*\[(.+?)\]\s*$")
    key_re = re.compile(r"^\s*" + re.escape(key) + r"\s*=", re.I)
    cur = None
    sec_end = None          # índice após a última linha não vazia da seção de destino
    for idx, ln in enumerate(lines):
        m = sec_re.match(ln)
        if m:
            if cur is not None and cur.lower() == section.lower():
                break
            cur = m.group(1)
            if cur.lower() == section.lower():
                sec_end = idx + 1
            continue
        if cur is not None and cur.lower() == section.lower():
            if key_re.match(ln):
                lines[idx] = f"{key}={value}"
                return nl.join(lines)
            if ln.strip():
                sec_end = idx + 1
    if sec_end is None:
        if lines and lines[-1].strip():
            lines.append("")
        lines += [f"[{section}]", f"{key}={value}"]
    else:
        lines.insert(sec_end, f"{key}={value}")
    return nl.join(lines)


def ini_get(text: str, section: str, key: str) -> Optional[str]:
    cur = None
    for ln in text.splitlines():
        m = re.match(r"^\s*\[(.+?)\]\s*$", ln)
        if m:
            cur = m.group(1)
            continue
        if cur and cur.lower() == section.lower():
            m = re.match(r"^\s*" + re.escape(key) + r"\s*=\s*(.*?)\s*$", ln, re.I)
            if m:
                return m.group(1)
    return None
