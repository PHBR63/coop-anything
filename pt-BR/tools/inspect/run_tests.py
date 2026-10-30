"""Executa os testes do inspetor e depois todas as variantes de mutação. Exibe ALL OK como última linha somente se tudo passar e todas as variantes forem detectadas.

    python -I tools/inspect/run_tests.py

Etapas:
  1. test_inspect.py: inspetor contra cópias simuladas do jogo (tools/bridge/fake_game.py), incluindo a demonstração.
  2. Variantes: cópia de inspect_live.py com uma proteção quebrada (dados obsoletos, escritas permitidas, lista de avaliações
     permitidas ignorada, uma cópia inativa que derruba toda a tabela, regras que nunca disparam, ...). O teste que cobre
     essa proteção precisa falhar contra a cópia.
Nenhum teste inicia um jogo real.
"""
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
BRIDGE = HERE.parent / "bridge"

# nome -> (texto que precisa aparecer exatamente uma vez em inspect_live.py, substituição, teste que precisa falhar)
TWINS = {
    "reads_stale_data": (
        "        reports = [self.read_copy(st) for st in self.copies]\n",
        "        reports = [self.last.get(st.name) or self.read_copy(st) for st in self.copies]\n",
        "ReadingTests.test_each_refresh_reads_the_game_again"),
    "write_methods_pass_the_wrapper": (
        "        if method not in self.allowed:\n",
        "        if False:\n",
        "ReadOnlyTests.test_only_queries_pass_the_wrapper"),
    "eval_allow_list_ignored": (
        "        if head not in self.eval_allow:\n",
        "        if False:\n",
        "ReadOnlyTests.test_an_expression_off_the_allow_list_is_refused_and_never_sent"),
    "field_list_may_name_write_methods": (
        "            if m in HARD_DENY:\n",
        "            if False:\n",
        "ReadOnlyTests.test_a_field_list_cannot_ask_for_a_write_method"),
    "one_dead_copy_breaks_the_table": (
        "        except bc.BridgeError as e:\n            st.drop()\n",
        "        except bc.RpcError as e:\n            st.drop()\n",
        "ReadingTests.test_unreachable_copy_is_a_column_and_the_others_still_show"),
    "missing_method_shown_as_error": (
        "                    if e.code == -32601:\n",
        "                    if False:\n",
        "ReadingTests.test_a_method_the_game_lacks_is_n_a_not_an_error"),
    "event_cursor_not_kept": (
        '            st.cursor = page["next"]\n',
        "            st.cursor = 0\n",
        "ReadingTests.test_events_are_read_from_a_cursor_and_never_listed_twice"),
    "dead_connection_kept": (
        "        self.bridge = None\n        self.events.clear()\n",
        "        self.events.clear()\n",
        "ReadingTests.test_a_copy_that_goes_away_and_comes_back_is_read_again"),
    "rules_never_fire": (
        "                if hit:\n",
        "                if False:\n",
        "ProblemAndTableTests.test_each_rule_fires_for_its_own_copy_only"),
    "differs_rule_off": (
        "if len({json.dumps(v, sort_keys=True) for v in vals.values()}) > 1:",
        "if False:",
        "ProblemAndTableTests.test_each_rule_fires_for_its_own_copy_only"),
    "columns_not_padded": (
        '" | ".join(c.ljust(col_w) for c in cells)',
        '" | ".join(c for c in cells)',
        "ProblemAndTableTests.test_table_columns_line_up_and_long_cells_wrap"),
}


def unittest_run(test=None, env_extra=None):
    env = dict(os.environ, COOPINSPECT_BRIDGE_DIR=str(BRIDGE), **(env_extra or {}))
    args = [sys.executable, "-I", str(HERE / "test_inspect.py")] + ([test] if test else [])
    p = subprocess.run(args, cwd=HERE, env=env, capture_output=True, text=True, errors="replace", timeout=600)
    out = (p.stdout or "") + (p.stderr or "")
    m = re.search(r"Ran (\d+) tests?", out)
    return p.returncode, out, int(m.group(1)) if m else 0


def caught(rc, out):
    "Uma variante só conta como detectada quando um teste falha. Erro de importação não conta como detecção."
    return rc != 0 and re.search(r"Ran \d+ tests? in", out) is not None and "ImportError" not in out and "SyntaxError" not in out \
        and re.search(r"(FAIL|ERROR): test_", out) is not None


def main():
    print("== Inspector against fake game copies")
    rc, out, n = unittest_run()
    print("\n".join(out.strip().splitlines()[-4:]))
    if rc != 0:
        print(out[-4000:])
        print("RESULT: FAIL (real tests)")
        return 1
    tmp = Path(tempfile.mkdtemp(prefix="coopinspect-twins-"))
    bad = []
    done = 0
    try:
        src = (HERE / "inspect_live.py").read_text(encoding="utf-8")
        for name, (old, new, test) in TWINS.items():
            if src.count(old) != 1:
                print(f"twin setup is stale: {old.strip()[:60]!r} occurs {src.count(old)} times, expected once")
                return 1
            d = tmp / name
            d.mkdir()
            (d / "inspect_live.py").write_text(src.replace(old, new), encoding="utf-8", newline="")
            rc, out, _ = unittest_run(test, {"COOPINSPECT_DIR": str(d)})
            ok = caught(rc, out)
            print(f"twin {name:33s} via {test.split('.')[-1][:50]}: {'caught' if ok else 'NOT CAUGHT'}")
            if ok:
                done += 1
            else:
                bad.append(name)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    if bad:
        print("RESULT: FAIL, twins not caught:", bad)
        return 1
    print(f"tests: {n}; twins caught: {done} of {len(TWINS)}")
    print("ALL OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
