"""CLI do simulador de caos de rede.

  python -I tools/chaos/chaos.py profiles
  python -I tools/chaos/chaos.py relay --target 127.0.0.1:27971 [--listen 0] [--bind 127.0.0.1] [--profile bad_wifi] [--seed N]
                                       [--rpc-port 0] [--log out/chaos/run.jsonl]
  python -I tools/chaos/chaos.py call --rpc-port P set_profile '{"profile":"hell"}'
  python -I tools/chaos/chaos.py call --rpc-port P partition '{"dir":"s2c","on":true}'
  python -I tools/chaos/chaos.py call --rpc-port P disconnect '{"duration_ms":3000}'

O retransmissor exibe uma linha JSON ao iniciar: {"listen": port, "rpc": port}.
"""
import argparse
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from impair import load_profiles  # noqa: E402
from relay import Relay, RpcServer, ChaosClient  # noqa: E402


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("profiles")
    r = sub.add_parser("relay")
    r.add_argument("--target", required=True, help="host:port do servidor real")
    r.add_argument("--listen", type=int, default=0, help="porta UDP à qual o cliente do jogo se conecta (0 = escolher uma)")
    r.add_argument("--bind", default="127.0.0.1", help="endereço de escuta (0.0.0.0 para aceitar outros PCs)")
    r.add_argument("--profile", default="lan")
    r.add_argument("--seed", type=int)
    r.add_argument("--rpc-port", type=int, default=0)
    r.add_argument("--log")
    r.add_argument("--info-file", help="grava aqui o JSON {listen,rpc,log} após iniciar")
    r.add_argument("--seconds", type=float, default=0, help="encerra após esse intervalo (0 = até RPC shutdown / Ctrl+C)")
    c = sub.add_parser("call")
    c.add_argument("--rpc-port", type=int, required=True)
    c.add_argument("method")
    c.add_argument("params", nargs="?", default="{}")
    a = ap.parse_args(argv)

    if a.cmd == "profiles":
        for k, v in load_profiles().items():
            print(f"{k:14s} lat {v.latency_ms}+-{v.jitter_ms} ms  loss {v.loss:.3f} (long-run {v.expected_loss():.3f})  "
                  f"reorder {v.reorder}  dup {v.duplicate}  bw {v.bandwidth_bps or 'unlimited'}  seed {v.seed}")
        return 0
    if a.cmd == "call":
        cl = ChaosClient(a.rpc_port)
        print(json.dumps(cl.call(a.method, **json.loads(a.params)), indent=2))
        return 0
    host, port = a.target.rsplit(":", 1)
    if a.log:
        Path(a.log).parent.mkdir(parents=True, exist_ok=True)
    relay = Relay((host, int(port)), a.listen, a.profile, a.seed, a.log, bind=a.bind).start()
    rpc = RpcServer(relay, a.rpc_port).start()
    info = {"listen": relay.port, "rpc": rpc.port, "log": relay.log_path}
    if a.info_file:
        Path(a.info_file).parent.mkdir(parents=True, exist_ok=True)
        Path(a.info_file).write_text(json.dumps(info), encoding="utf-8")
    print(json.dumps(info), flush=True)
    end = time.monotonic() + a.seconds if a.seconds else None
    try:
        while not relay.shutdown_requested.wait(0.2) and (end is None or time.monotonic() < end):
            pass
    except KeyboardInterrupt:
        pass
    rpc.shutdown()
    relay.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
