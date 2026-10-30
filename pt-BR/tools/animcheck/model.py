"""Modelo de fluxo de sondagem: uma resposta interpretada e o formato JSONL usado no disco. A especificação completa está em FORMAT.md.

Arquivo de fluxo (JSONL, uma sondagem por linha), gravado por sonda interna do jogo, collect.Collector ou synth.py:
    {"machine": "host", "t_ms": 1234.5, "rx_ms": 98765.4, "frame": 811, "actors": [ <actor> ... ]}
`t_ms` é o relógio do próprio jogo; `rx_ms` é o relógio monotônico do coletor quando a resposta chegou (compartilhado por
todas as máquinas em um PC). O alinhamento entre máquinas usa rx_ms se todas as sondagens o tiverem; caso contrário, t_ms.
Linhas que não sejam objetos JSON são ignoradas (comentários, linhas vazias).
"""
from __future__ import annotations

import json
import math
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple, Union

from .profile import DEFAULT_PROFILE, Group, Profile

Vec = Tuple[float, float, float]


@dataclass
class Seq:
    slot: int
    group: Group                  # identificador do grupo de animação (int) ou nome (str)
    state: int = 1                # 1 = em jogo; qualquer outro valor = fora do jogo
    t: float = 0.0
    begin: float = 0.0
    end: float = 0.0
    freq: float = 1.0
    weight: float = 1.0


@dataclass
class Actor:
    ref: int
    t: float                      # tempo de alinhamento em ms (consulte a documentação do módulo)
    pos: Vec = (0.0, 0.0, 0.0)
    rotz: float = 0.0             # yaw, radianos
    rotx: float = 0.0             # inclinação da mira, em radianos
    cell: int = 0                 # identificador de área/fase; uma mudança significa teletransporte, não movimento
    dead: bool = False
    valid3d: bool = True          # false enquanto o corpo não estiver carregado (a amostra é ignorada pelos detectores)
    player: bool = False
    first_person: bool = False
    have_anim: bool = True        # false se a sonda não enviou um bloco `anim` para este ator
    seqs: List[Seq] = field(default_factory=list)
    action: int = -1
    move_flags: Optional[int] = None
    weapon_out: bool = False
    weapon_form: int = 0
    aiming: bool = False
    knocked: int = 0
    swimming: bool = False
    ragdoll: bool = False
    sneaking: bool = False
    in_combat: bool = False
    combat_target: int = 0
    package: int = 0
    bones: Dict[str, Vec] = field(default_factory=dict)
    ground_z: Optional[float] = None   # opcional: altura do chão sob o ator, se a sonda puder fornecê-la
    frame: int = 0

    def animating(self) -> List[Seq]:
        return [s for s in self.seqs if s.state == 1]


def _hex(v, default=0) -> int:
    "Um identificador: inteiro ou string hexadecimal com ou sem 0x (\"0x14\", \"FF000A\")."
    if isinstance(v, bool):
        return int(v)
    if isinstance(v, int):
        return v
    if isinstance(v, str) and v:
        try:
            return int(v, 16)
        except ValueError:
            return default
    return default


def _vec(v, default=(0.0, 0.0, 0.0)) -> Vec:
    if isinstance(v, (list, tuple)) and len(v) == 3:
        return (float(v[0]), float(v[1]), float(v[2]))
    return default


def _group(v) -> Group:
    if isinstance(v, str):
        return v
    try:
        return int(v)
    except (TypeError, ValueError):
        return -1


def parse_actor(a: dict, t: float, frame: int = 0, profile: Optional[Profile] = None) -> Actor:
    profile = profile or DEFAULT_PROFILE
    anim = a.get("anim") or {}
    seqs = [Seq(slot=int(s.get("slot", 0)), group=_group(s.get("group", -1)), state=int(s.get("state", -1)),
                t=float(s.get("t", 0.0)), begin=float(s.get("begin", 0.0)), end=float(s.get("end", 0.0)),
                freq=float(s.get("freq", 1.0)), weight=float(s.get("weight", 1.0)))
            for s in anim.get("seqs", [])]
    w = a.get("weapon") or {}
    st = a.get("stance") or {}
    ai = a.get("ai") or {}
    mf = a.get("move_flags")
    rot = _vec(a.get("rot"))
    if profile.angle_unit == "deg":
        rot = (math.radians(rot[0]), math.radians(rot[1]), math.radians(rot[2]))
    act = Actor(
        ref=_hex(a.get("ref")), t=t, pos=_vec(a.get("pos")), rotz=rot[2], rotx=rot[0], cell=_hex(a.get("cell")),
        dead=bool(a.get("dead", False)), valid3d=bool(a.get("valid3d", True)), player=bool(a.get("player", False)),
        first_person=bool(a.get("first_person", False)), have_anim=("anim" in a), seqs=seqs,
        action=int(anim.get("action", -1)), move_flags=None if mf is None else int(mf),
        weapon_out=bool(w.get("out", False)), weapon_form=_hex(w.get("form")), aiming=bool(w.get("aiming", False)),
        knocked=int(st.get("knocked", 0)), swimming=bool(st.get("swimming", False)),
        ragdoll=bool(st.get("ragdoll_ctrl", st.get("ragdoll", False))), sneaking=bool(st.get("sneaking", False)),
        in_combat=bool(ai.get("in_combat", False)),
        combat_target=_hex(ai.get("combat_target")), package=_hex(ai.get("package")),
        bones={k: _vec(v) for k, v in (a.get("bones") or {}).items()},
        ground_z=a.get("ground_z"), frame=frame)
    if act.move_flags is not None:
        bits = profile.move_flag_bits
        if "sneak" in bits:
            act.sneaking = act.sneaking or bool(act.move_flags & (1 << bits["sneak"]))
        if "swim" in bits:
            act.swimming = act.swimming or bool(act.move_flags & (1 << bits["swim"]))
    return act


@dataclass
class Stream:
    machine: str
    by_ref: Dict[int, List[Actor]] = field(default_factory=dict)
    t_first: float = math.inf
    t_last: float = -math.inf

    def add(self, a: Actor) -> None:
        self.by_ref.setdefault(a.ref, []).append(a)
        self.t_first = min(self.t_first, a.t)
        self.t_last = max(self.t_last, a.t)

    def finish(self) -> "Stream":
        for lst in self.by_ref.values():
            lst.sort(key=lambda x: x.t)
        return self

    @property
    def sample_count(self) -> int:
        return sum(len(v) for v in self.by_ref.values())


def stream_from_probes(machine: str, probes: Iterable[dict], use_rx: bool = False,
                       profile: Optional[Profile] = None) -> Stream:
    s = Stream(machine)
    for p in probes:
        if not isinstance(p, dict):
            continue
        t = p.get("rx_ms") if (use_rx and p.get("rx_ms") is not None) else p.get("t_ms", 0.0)
        for a in p.get("actors", []):
            s.add(parse_actor(a, float(t), int(p.get("frame", 0)), profile))
    return s.finish()


def read_probes(path: Union[Path, str]) -> List[dict]:
    out = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line[0] != "{":
                continue
            try:
                out.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return out


def load_stream(path: Union[Path, str], machine: Optional[str] = None, use_rx: Optional[bool] = None,
                profile: Optional[Profile] = None) -> Stream:
    probes = read_probes(path)
    if use_rx is None:
        use_rx = bool(probes) and all(p.get("rx_ms") is not None for p in probes)
    name = machine or (probes[0].get("machine") if probes else None) or Path(path).stem
    return stream_from_probes(name, probes, use_rx=use_rx, profile=profile)


def write_probes(path: Union[Path, str], probes: Iterable[dict]) -> int:
    n = 0
    with open(path, "w", encoding="utf-8") as f:
        for p in probes:
            f.write(json.dumps(p, separators=(",", ":")) + "\n")
            n += 1
    return n


def horizontal_speed(a: Actor, b: Actor) -> float:
    "unidades por segundo entre duas amostras do mesmo ator (0 se não passou tempo)."
    dt = (b.t - a.t) / 1000.0
    if dt <= 0:
        return 0.0
    return math.hypot(b.pos[0] - a.pos[0], b.pos[1] - a.pos[1]) / dt
