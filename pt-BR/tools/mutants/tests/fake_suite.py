"""Programa de teste simulado para os testes do executor de variantes. O comportamento vem do ambiente, permitindo que um único script represente todos os casos.

    python fake_suite.py TEST

  FAKE_SPEC   JSON: {"<twin>": {"<test>": <exit code or "hang">}, "_real_fail": ["<test>", ...]}
              Com a variante <twin> ativada, o teste <test> sai com esse código (e exibe "1 checks, 1 failed" para código 1 ou "crashed" nos demais casos).
              Um teste em _real_fail falha mesmo sem uma variante.
  FAKE_VAR    nome da variável de ambiente que contém a variante (padrão COOP_MUT)
  FAKE_LOG    arquivo: cada execução acrescenta "<test> <twin value>"
"""
import json
import os
import sys
import time

spec = json.loads(os.environ.get("FAKE_SPEC", "{}"))
var = os.environ.get("FAKE_VAR", "COOP_MUT")
test = sys.argv[1] if len(sys.argv) > 1 else "*"
twin = os.environ.get(var, "")
log = os.environ.get("FAKE_LOG")
if log:
    with open(log, "a", encoding="utf-8") as f:
        f.write(f"{test} {twin}\n")
if test in spec.get("_real_fail", []):
    print("1 checks, 1 failed")
    sys.exit(1)
effect = spec.get(twin, {}).get(test) if twin else None
if effect is None:
    print("1 checks, 0 failed")
    sys.exit(0)
if effect == "hang":
    time.sleep(60)
    sys.exit(0)
print("1 checks, 1 failed" if effect == 1 else "crashed")
code = int(effect)
sys.exit(code - (1 << 32) if code >= (1 << 31) else code)  # um código de saída como 0xC0000135 não cabe em um int de C
