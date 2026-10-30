"""Tarefa de compilação simulada para os testes de trava: registra quando começou e terminou, permitindo comprovar que duas tarefas nunca se sobrepuseram.

    python fake_job.py NAME LOG [SECONDS] [EXIT_CODE]

Acrescenta "start NAME <time>" e "end NAME <time>" a LOG (time = time.time()). Com a variável de ambiente FAKE_PIDFILE,
grava primeiro seu próprio pid nesse arquivo. SECONDS determina a duração do trabalho (padrão 0.3).
"""
import os
import sys
import time

name, log = sys.argv[1], sys.argv[2]
seconds = float(sys.argv[3]) if len(sys.argv) > 3 else 0.3
code = int(sys.argv[4]) if len(sys.argv) > 4 else 0
pf = os.environ.get("FAKE_PIDFILE")
if pf:
    with open(pf, "w") as f:
        f.write(str(os.getpid()))
with open(log, "a") as f:
    f.write(f"start {name} {time.time():.4f}\n")
time.sleep(seconds)
with open(log, "a") as f:
    f.write(f"end {name} {time.time():.4f}\n")
sys.exit(code)
