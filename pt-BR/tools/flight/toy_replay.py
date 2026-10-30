"""Pequeno hook de reprodução em Python puro: exemplo para copiar ao escrever um para seu jogo e hook usado nos testes do redutor.

Seu hook é um programa (ou função Python) que recebe dados de teste e informa se o bug aparece. Este segue o contrato
de comando: argv[1] = dados JSON; uma linha JSON em stdout; saída 0 para convergência, 1 para divergência, 2 para dados inválidos.
Com --lines, segue o outro contrato: a lista se chama "ops", e cada regra quebrada gera uma linha em stdout
`VIOLATION <rule-name> <detail>` (saída 1 se houver qualquer violação).
Como hook Python: `--replay-py toy_replay:replay --replay-path <this folder>`; replay(fixture) retorna o dicionário de resultado.

Regras de exemplo (bugs que exigem passos específicos, para a redução ter algo real a encontrar):
  * um deliver cujo datagrama começa com 0xEE arma a posição de destino;
  * um deliver posterior começando com 0xFF para uma posição armada é um eco obsoleto: falha "stale echo applied on slot N";
  * um passo inject com kind "dup" causa a falha "duplicate actor on slot N";
  * a verificação só ocorre em um passo quiesce; com duas falhas presentes, o eco obsoleto é relatado primeiro.
"""
import json
import sys


def run(fx):
    if fx.get("version") != 1 or not isinstance(fx.get("steps"), list):
        raise ValueError("bad fixture")
    armed = set()
    stale = []
    dup = []
    run_steps = 0
    for st in fx["steps"]:
        op = st.get("op")
        run_steps += 1
        if op == "deliver":
            b = bytes.fromhex(st.get("hex", ""))
            if not b:
                continue
            to = st["to"]
            if b[0] == 0xEE:
                armed.add(to)
            elif b[0] == 0xFF and to in armed:
                stale.append(to)
        elif op == "inject" and st.get("kind") == "dup":
            dup.append(st.get("slot", 1))
        elif op == "quiesce":
            viol = ["stale echo applied on slot %d" % s for s in stale] + ["duplicate actor on slot %d" % s for s in dup]
            first = {"category": "actors", "key": "echo"} if viol else None
            return {"diverged": bool(viol), "violations": viol, "first": first, "stepsRun": run_steps}
    return {"diverged": False, "violations": [], "first": None, "stepsRun": run_steps}


def replay(fx):
    "Ponto de entrada do hook Python: recebe um dicionário de dados de teste e retorna o dicionário de resultado. Entrada inválida lança exceção, relatada pelo redutor."
    return run(fx)


def main():
    args = [a for a in sys.argv[1:] if a != "--lines"]
    lines = "--lines" in sys.argv
    try:
        with open(args[0]) as f:
            fx = json.load(f)
        if lines:
            fx = {"version": 1, "steps": fx["ops"]}
        res = run(fx)
    except (OSError, ValueError, KeyError, IndexError):
        print(json.dumps({"error": "bad fixture"}))
        return 2
    if lines:
        for v in res["violations"]:
            print("VIOLATION " + v.replace("stale echo applied on", "stale_echo_applied").replace("duplicate actor on", "duplicate_actor"))
        return 1 if res["diverged"] else 0
    print(json.dumps(res))
    return 1 if res["diverged"] else 0


if __name__ == "__main__":
    sys.exit(main())
