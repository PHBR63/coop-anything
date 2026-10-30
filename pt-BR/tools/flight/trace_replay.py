"""Reprodução off-line de registros de eventos: programa de reprodução usado pelos casos escritos por from_failure.py.

Dados de teste "cofr-trace-1" carregam os registros brutos do arquivo .cofr de cada máquina:
  {"version":1, "format":"cofr-trace-1", "headers":{"0":"<hex of the 64 byte header>", "1":"..."},
   "steps":[{"op":"rec","slot":0,"hex":"<hex of one whole record>", "ty":"TxnApplied", "at_ms":123.4}, ...],
   "schema":"<optional schema JSON text that overrides the one stored in the records>",
   "expect":{"converges":false}, "source":{...}}
Cada etapa é um registro independente, permitindo ao redutor (shrink.py) remover qualquer subconjunto (etapa com "pin": true permanece).
A reprodução reconstrói os registros, alinha-os e classifica o que o analisador encontra. O resultado segue o contrato
de shrink.py / regress.py: uma linha JSON em stdout; saída 0 para convergência, 1 para divergência, 2 para dados inválidos.

Uso: python -I tools/flight/trace_replay.py fixture.json

Classes (aparência da falha, na ordem temporal encontrada pelo analisador):
  digest-mismatch   um resumo difere entre máquinas
  divergence        mesma transação com conteúdo diferente, aplicação dupla ou discordância de responsável por um ator
  stuck-sync        transação aplicada em uma máquina e nunca em outra, sem recuperação posterior dessa máquina
  desync-marker     máquina gravou seu próprio marcador de dessincronização
  transient-gap     transação ausente em uma máquina, mas reparo, captura de estado ou estado-base reafirmou seu estado depois: não é falha por si só
Os indicadores de aplicação que reafirmam estado vêm do esquema (restate_mask), mantendo compatibilidade com jogos que usam outros indicadores.
Nada neste arquivo conhece um jogo específico.
"""
import json
import os
import struct
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cofr as C  # noqa: E402
import schema as SC  # noqa: E402
import analyze as A  # noqa: E402

FORMAT = "cofr-trace-1"
KIND_CLASS = {"digest": "digest-mismatch", "txn-hash": "divergence", "txn-double": "divergence", "ownership-conflict": "divergence",
              "ownership-stale": "divergence", "txn-missing": "stuck-sync", "desync-marker": "desync-marker"}
FAILURE_CLASSES = ("digest-mismatch", "divergence", "stuck-sync", "desync-marker")
RECORD_COUNT_OFFSET = 40      # onde o cabeçalho guarda a contagem de registros (seção 2 de FORMAT.md)


class BadFixture(ValueError):
    pass


# ---------------------------------------------------------------- registros brutos

def split_cofr(data):
    "-> (header_bytes, [um objeto bytes por registro inteiro], parsed_header). Um último registro escrito pela metade é descartado."
    data = bytes(data)
    h = C.parse_header(data)
    pos = h["header_size"]
    recs = []
    while len(data) - pos >= C.RECORD_HEADER:
        plen = struct.unpack_from("<H", data, pos + 2)[0]
        if len(data) - pos - C.RECORD_HEADER < plen:
            break
        end = pos + C.RECORD_HEADER + plen
        recs.append(data[pos:end])
        pos = end
    return data[:h["header_size"]], recs, h


def traces_from_fixture(fx):
    if not isinstance(fx, dict) or fx.get("format") != FORMAT or not isinstance(fx.get("steps"), list) or not isinstance(fx.get("headers"), dict):
        raise BadFixture("not a %s fixture" % FORMAT)
    parts = {}
    try:
        schema = SC.from_json(fx["schema"]) if fx.get("schema") else None
        for slot, hx in fx["headers"].items():
            parts[int(slot)] = [bytearray(bytes.fromhex(hx)), []]
        for st in fx["steps"]:
            if st.get("op") == "rec":
                parts[int(st["slot"])][1].append(bytes.fromhex(st["hex"]))
        out = []
        for s, (hdr, recs) in sorted(parts.items()):
            if len(hdr) >= RECORD_COUNT_OFFSET + 8:
                struct.pack_into("<Q", hdr, RECORD_COUNT_OFFSET, len(recs))      # o redutor removeu registros: mantém o cabeçalho fiel aos dados
            out.append(C.loads(bytes(hdr) + b"".join(recs), "slot%d" % s, schema=schema))
        return out
    except (ValueError, KeyError, TypeError, C.CofrError, SC.SchemaError) as ex:
        raise BadFixture("bad %s fixture: %s" % (FORMAT, ex))


# ---------------------------------------------------------------- classificação

def _restating_applies(a):
    "vaga -> tempos alinhados ordenados das aplicações que o esquema considera reafirmação de estado (captura, reparo, estado-base): recuperam transação ausente."
    mask = a.schema.restate_mask
    out = {}
    for s in a.slots:
        out[s] = sorted(a.t(s, r) for r in a.traces[s]["records"]
                        if r["type"] == C.T_TXN_APPLIED and not r.get("malformed") and r["applied_flags"] & mask)
    return out


def classify(traces):
    """Alinha os registros e separa os achados do analisador em classes. -> dicionário compatível com JSON:
    {"found": bool, "primary": resumo candidato ou None, "items": [resumo, ...], "counts": {classe: n}, "slots": [...]}
    Um resumo é {"class","kind","key","suspects","at_ms","detail","healed"}."""
    a = A.align(traces)
    heal = _restating_applies(a)
    items = []
    for c in A.find_all(a):
        cls = KIND_CLASS[c["kind"]]
        later = any(t >= c["aligned_us"] for s in c.get("suspects", []) for t in heal.get(s, ()))
        if c["kind"] == "txn-missing" and later:
            cls = "transient-gap"
        items.append({"class": cls, "kind": c["kind"], "key": c["key"], "suspects": list(c.get("suspects", [])),
                      "at_ms": round((c["aligned_us"] - a.t0) / 1000.0, 3), "detail": c["detail"], "healed": later})
    real = [i for i in items if i["class"] in FAILURE_CLASSES]
    counts = {}
    for i in items:
        counts[i["class"]] = counts.get(i["class"], 0) + 1
    # a primeira descoberta real tem prioridade; o marcador de dessincronização da própria máquina é só seu relato de problema e só assume prioridade quando nada mais é encontrado
    own = [i for i in real if i["class"] != "desync-marker"]
    return {"found": bool(real), "primary": (own or real or [None])[0], "items": items, "counts": counts, "slots": list(a.slots)}


def result_of(cl):
    "Resultado do contrato de reprodução para uma classificação."
    real = [i for i in cl["items"] if i["class"] in FAILURE_CLASSES]
    p = cl["primary"]
    real = ([p] + [i for i in real if i is not p]) if p else real   # violations[0] é o valor comparado por shrink.signature()
    return {"diverged": cl["found"], "violations": ["%s %s" % (i["class"], i["key"]) for i in real[:5]],
            "first": {"category": p["class"], "key": p["key"]} if p else None, "counts": cl["counts"]}


def run(fx):
    traces = traces_from_fixture(fx)
    try:
        return result_of(classify(traces))
    except Exception as ex:   # noqa: BLE001  a shrink candidate can be too thin to align (a machine with no records left): that is "no failure"
        return {"diverged": False, "violations": [], "first": None, "counts": {}, "error": "%s: %s" % (type(ex).__name__, ex)}


def oracle(fx):
    "Oráculo no próprio processo para shrink.shrink_fixture e regress.run_dir (mesmo formato de resultado de shrink.CommandOracle)."
    return run(fx)


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    try:
        with open(argv[0], encoding="utf-8") as f:
            res = run(json.load(f))
    except (OSError, ValueError, IndexError, BadFixture):
        print(json.dumps({"error": "bad fixture"}))
        return 2
    print(json.dumps(res))
    return 1 if res["diverged"] else 0


if __name__ == "__main__":
    sys.exit(main())
