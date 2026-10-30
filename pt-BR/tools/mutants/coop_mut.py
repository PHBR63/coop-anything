"""Variantes de mutação Python ativáveis em tempo de execução (tools/mutants/README.md). Mesma ideia de coop_mut.h.

Uma variante é uma versão deliberadamente incorreta de uma parte do código. O teste que cobre esse código precisa falhar
quando a variante estiver ativa. Escolha-a na inicialização do programa de teste pela variável COOP_MUT (nome ou número):

    set COOP_MUT=add_wrong_operator && python my_tests.py

No código sob teste:

    import coop_mut

    def add(a, b):
        if coop_mut.mut("add_wrong_operator"):
            return a - b                       # variante com defeito
        return a + b

Custo quando desativada: o ambiente é lido uma vez na importação. Depois, `mut()` faz uma leitura global e uma comparação.
Laços muito usados podem verificar primeiro `coop_mut.ENABLED` (False quando nenhuma variante foi escolhida). Distribua
o produto sem os pontos de chamada ou mantenha-os: sem COOP_MUT no ambiente, todas as chamadas retornam False.

Uma variante fica ativa por vez. "0" ou valor vazio significa nenhuma. set() e active() servem para testes no próprio processo.
"""
import contextlib
import os

ENV_VAR = "COOP_MUT"


def _clean(value):
    value = "" if value is None else str(value)
    return "" if value == "0" else value


_current = _clean(os.environ.get(ENV_VAR, ""))
ENABLED = bool(_current)


def mut(name):
    "True quando a variante `name` (string ou inteiro) é a ativa."
    return bool(_current) and _current == str(name)


def any_active():
    return bool(_current)


def current():
    return _current


def set(name):  # noqa: A001  (the name mirrors the C++ header)
    "Escolhe uma variante pelo código (\"\" ou 0 a desativa). Não é seguro para threads: chame durante a preparação do teste."
    global _current, ENABLED
    _current = _clean(name)
    ENABLED = bool(_current)


@contextlib.contextmanager
def active(name):
    "`with coop_mut.active(\"add_wrong_operator\"): ...` ativa uma variante durante o bloco."
    old = _current
    set(name)
    try:
        yield
    finally:
        set(old)


def init_from_args(argv):
    "Aceita `--mut NAME` ou `--mut=NAME` em uma lista de argumentos. Retorna a lista sem esses argumentos."
    out, i = [], 0
    while i < len(argv):
        a = argv[i]
        if a == "--mut" and i + 1 < len(argv):
            set(argv[i + 1])
            i += 2
            continue
        if a.startswith("--mut="):
            set(a[len("--mut="):])
            i += 1
            continue
        out.append(a)
        i += 1
    return out
