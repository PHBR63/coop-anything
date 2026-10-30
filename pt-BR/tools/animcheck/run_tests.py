"""Um comando para toda a ferramenta animcheck:  python -I tools/animcheck/run_tests.py   -> última linha ALL OK

1. A suíte unitária (tests/) precisa passar no código real.
2. Cada variante de mutação (ANIMCHECK_MUTANT=<name>, um bug deliberado em cada uma) precisa fazer a suíte FALHAR e
   fazer falhar os testes nomeados abaixo. Uma variante não detectada, ou detectada só por um teste sem relação, reprova a execução.
Os testes usam apenas fluxos sintéticos de sondagem. Nenhum jogo e nenhuma rede fora do loopback.
"""
from __future__ import annotations

import os
import re
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
sys.path.insert(0, str(HERE.parent))

# nome da variante -> testes que precisam falhar quando aquele comportamento é quebrado
MUTANTS = {
    "sliding": ("test_sliding_moves_without_locomotion",),
    "tpose": ("test_tpose_no_sequence", "test_tpose_arms_out"),
    "floating": ("test_floating", "test_sinking"),
    "jitter": ("test_jitter",),
    "rubberband": ("test_rubberband_with_snapback",),
    "stuck": ("test_stuck_only_when_movement_is_expected",),
    "deathpose": ("test_deathpose_alive_animation_on_dead_actor",),
    "group_compare": ("test_group_mismatch",),
    "weapon_compare": ("test_wrong_weapon_needs_to_persist",),
    "facing_compare": ("test_wrong_facing",),
    "pose_compare": ("test_pose_defect_is_scored",),
    "aim_compare": ("test_anim_weapon_aim_facing_mismatches",),
    "stance_compare": ("test_stance_mismatch",),
    "counters": ("test_counters_check",),
    "profile_bones": ("test_tpose_arms_out_uses_the_profile_bones",),
}


def run(script: Path, mutant: str = "") -> subprocess.CompletedProcess:
    env = dict(os.environ)
    env.pop("ANIMCHECK_MUTANT", None)
    if mutant:
        env["ANIMCHECK_MUTANT"] = mutant
    return subprocess.run([sys.executable, "-I", str(script)], cwd=ROOT, capture_output=True, text=True, env=env,
                          errors="replace")


def failed_tests(output: str) -> set:
    "Nomes dos métodos de teste que unittest relatou como FAIL ou ERROR."
    return set(re.findall(r"^(?:FAIL|ERROR): (\w+) ", output, flags=re.M))


def main() -> int:
    t0 = time.time()
    suite = HERE / "tests" / "run_suite.py"
    r = run(suite)
    out = r.stdout + r.stderr
    if r.returncode != 0:
        print(out[-3000:])
        print("FAIL: unit suite on the real code")
        return 1
    ran = [ln for ln in out.splitlines() if ln.startswith("Ran ")]
    print(f"unit suite passes ({ran[0] if ran else 'no count'})")

    def twin(name: str):
        rm = run(suite, name)
        return name, rm.returncode, failed_tests(rm.stdout + rm.stderr)

    bad = 0
    with ThreadPoolExecutor(max_workers=4) as ex:
        results = list(ex.map(twin, MUTANTS))
    caught = 0
    for name, code, failed in results:
        want = set(MUTANTS[name])
        if code == 0:
            print(f"SURVIVED: twin {name} (the suite still passed)")
            bad += 1
        elif not want <= failed:
            print(f"WRONG CATCH: twin {name} did not break {sorted(want - failed)}; broke {sorted(failed)}")
            bad += 1
        else:
            caught += 1
    print(f"mutation twins: {len(MUTANTS)} run, {caught} caught, {len(MUTANTS) - caught} not")
    print(f"({time.time() - t0:.0f}s)")
    print("FAILED" if bad else "ALL OK")
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
