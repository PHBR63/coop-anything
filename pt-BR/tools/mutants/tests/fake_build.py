"""Etapa de compilação simulada para os testes do executor de variantes.

    python fake_build.py

  BUILD_LOG       arquivo: cada execução acrescenta o valor de variante observado ("-" se não houver)
  BUILD_CRASH_ON  sai com código 2 quando COOP_MUT tem esse valor (uma variante que não compila)
"""
import os
import sys

twin = os.environ.get("COOP_MUT", "")
with open(os.environ["BUILD_LOG"], "a", encoding="utf-8") as f:
    f.write((twin or "-") + "\n")
if twin and twin == os.environ.get("BUILD_CRASH_ON"):
    print("error C2065: undeclared identifier")
    sys.exit(2)
sys.exit(0)
