"""Perfil de jogo: tudo que o analisador precisa saber sobre um jogo, carregado de um pequeno arquivo JSON.

Um perfil informa:
  * qual nome de osso cumpre cada papel usado pelo analisador (raiz, ossos dos braços);
  * tabela de grupos de animação: id (ou nome) de grupo -> nome;
  * categoria geral de cada grupo (idle, walk, run, ... consulte CATEGORIES);
  * unidade angular, escala do mundo e substituições opcionais de limiares.

Sem perfil, o analisador usa GENERIC, pequena tabela neutra dos testes sintéticos. Para um jogo real, escreva
um perfil (exemplo completo em examples/fnv/profile.json) e passe-o com `--profile`.

JSON de perfil (todas as chaves são opcionais):

    {
      "name": "mygame",
      "bones": {"root": "Hips", "left_upper_arm": "UpperArm_L", "left_hand": "Hand_L",
                "right_upper_arm": "UpperArm_R", "right_hand": "Hand_R"},
      "groups": ["Idle", "Walk", "Run"],                 // índice = id do grupo. Ou {"0": "Idle", "5": "Walk"}
      "categories": {"idle": ["Idle"], "walk": ["Walk"], "run": ["Run", 12]},   // nomes ou ids exatos
      "category_prefixes": {"attack": ["Attack"], "reload": ["Reload"]},
      "default_category": "misc",                        // grupo conhecido que não corresponde a regra alguma
      "angle_unit": "rad",                               // ou "deg"
      "units_per_meter": 70.0,                           // limiares definidos para 70; ajustados a este valor
      "move_flag_bits": {"sneak": 9, "swim": 11},        // opcional: números dos bits de um inteiro `move_flags`
      "thresholds": {"slide_min_speed": 50.0}            // qualquer campo de config.Thresholds
    }
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union

Group = Union[int, str]

# Categorias reconhecidas pelos detectores. Os perfis mapeiam grupos para elas.
CATEGORIES = ("idle", "walk", "run", "dodge", "turn", "aim", "attack", "reload", "jam", "equip", "hit", "death",
              "jump", "block", "misc")
# Categorias que significam que o corpo está se deslocando sob controle de animação
LOCOMOTION = {"walk", "run", "dodge"}
# Categorias executadas somente por ator vivo e em pé
ALIVE_ONLY = {"idle", "walk", "run", "dodge", "turn", "aim", "attack", "reload", "jam", "equip", "block", "misc"}
AIRBORNE = {"jump"}

# Papéis dos ossos. O analisador precisa de "root" e dos quatro papéis de braço; os demais são usados somente por synth.py.
ANALYZER_ROLES = ("root", "left_upper_arm", "left_hand", "right_upper_arm", "right_hand")
SYNTH_ROLES = ("root", "spine1", "spine2", "neck", "head", "left_upper_arm", "left_forearm", "left_hand",
               "right_upper_arm", "right_forearm", "right_hand", "left_calf", "left_foot", "right_calf", "right_foot",
               "weapon")

_KNOWN_KEYS = {"name", "bones", "groups", "categories", "category_prefixes", "default_category", "angle_unit",
               "units_per_meter", "move_flag_bits", "thresholds"}


@dataclass(frozen=True)
class Profile:
    name: str = "generic"
    bones: Dict[str, str] = field(default_factory=dict)
    groups: Tuple[str, ...] = ()
    categories: Dict[str, Tuple[Group, ...]] = field(default_factory=dict)
    category_prefixes: Dict[str, Tuple[str, ...]] = field(default_factory=dict)
    default_category: str = "misc"
    angle_unit: str = "rad"
    units_per_meter: float = 70.0
    move_flag_bits: Dict[str, int] = field(default_factory=dict)
    threshold_overrides: Dict[str, object] = field(default_factory=dict)
    # id de grupo -> nome para tabelas fornecidas como dicionário esparso; preenchido por from_dict
    sparse_groups: Dict[int, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        exact: Dict[Group, str] = {}
        for cat, items in self.categories.items():
            for it in items:
                exact.setdefault(it, cat)
        prefixes: List[Tuple[str, str]] = []
        for cat, items in self.category_prefixes.items():
            for pre in items:
                prefixes.append((pre, cat))
        object.__setattr__(self, "_exact", exact)
        object.__setattr__(self, "_prefixes", prefixes)
        object.__setattr__(self, "_cache", {})

    # ---- ossos ----
    @property
    def root_bone(self) -> str:
        return self.bone("root")

    def bone(self, role: str) -> str:
        "Nome do osso de um papel; se o perfil não nomear o papel, ele próprio é usado como nome do osso."
        return self.bones.get(role, role)

    # ---- grupos ----
    def known(self, group: Group) -> bool:
        if isinstance(group, int):
            return (0 <= group < len(self.groups)) or group in self.sparse_groups
        return group in self.groups or group in self._exact

    def group_name(self, group: Group) -> str:
        if isinstance(group, str):
            return group
        if group in self.sparse_groups:
            return self.sparse_groups[group]
        if 0 <= group < len(self.groups):
            return self.groups[group]
        return f"group{group}"

    def category(self, group: Group) -> str:
        "Uma das CATEGORIES ou 'unknown' para um grupo totalmente desconhecido pelo perfil."
        c = self._cache.get(group)
        if c is not None:
            return c
        c = self._category(group)
        self._cache[group] = c
        return c

    def _category(self, group: Group) -> str:
        if group in self._exact:
            return self._exact[group]
        if isinstance(group, int) and group < 0:
            return "unknown"
        n = self.group_name(group)
        if n in self._exact:
            return self._exact[n]
        for pre, cat in self._prefixes:
            if n.startswith(pre):
                return cat
        if self.known(group):
            return self.default_category
        return "unknown"

    def first_group(self, category: str) -> Group:
        "Primeiro id (ou nome) de grupo de uma categoria; usado pelos fluxos sintéticos."
        for i in range(len(self.groups)):
            if self.category(i) == category:
                return i
        for gid, n in sorted(self.sparse_groups.items()):
            if self.category(gid) == category:
                return gid
        for it in self.categories.get(category, ()):
            return it
        raise KeyError(f"profile {self.name!r} has no group in category {category!r}")

    # ---- limiares ----
    def thresholds(self, base=None):
        "Limiares padrão ajustados às unidades do mundo deste jogo, seguidos das substituições do próprio perfil."
        from .config import DEFAULT, Thresholds
        th = (base or DEFAULT).scaled(self.units_per_meter / 70.0)
        return th.with_(**Thresholds.coerce(self.threshold_overrides)) if self.threshold_overrides else th

    # ---- carregamento ----
    @classmethod
    def from_dict(cls, d: dict) -> "Profile":
        if not isinstance(d, dict):
            raise ValueError("profile must be a JSON object")
        unknown = sorted(k for k in d if k not in _KNOWN_KEYS and not k.startswith("_") and not k.startswith("//"))
        if unknown:
            raise ValueError(f"unknown profile keys: {', '.join(unknown)}")
        for key in ("bones", "categories", "category_prefixes", "move_flag_bits", "thresholds"):
            if d.get(key) is not None and not isinstance(d[key], dict):
                raise ValueError(f"{key} must be an object")
        groups: Tuple[str, ...] = ()
        sparse: Dict[int, str] = {}
        g = d.get("groups", [])
        if isinstance(g, list):
            groups = tuple(str(x) for x in g)
        elif isinstance(g, dict):
            sparse = {int(k): str(v) for k, v in g.items()}
        else:
            raise ValueError("groups must be a list or an object")
        cats = {}
        for cat, items in (d.get("categories") or {}).items():
            if cat not in CATEGORIES:
                raise ValueError(f"unknown category {cat!r} (use one of {', '.join(CATEGORIES)})")
            if not isinstance(items, list):
                raise ValueError(f"categories.{cat} must be a list")
            cats[cat] = tuple(items)
        pres = {}
        for cat, items in (d.get("category_prefixes") or {}).items():
            if cat not in CATEGORIES:
                raise ValueError(f"unknown category {cat!r} (use one of {', '.join(CATEGORIES)})")
            if not isinstance(items, list):
                raise ValueError(f"category_prefixes.{cat} must be a list")
            pres[cat] = tuple(str(x) for x in items)
        dc = d.get("default_category", "misc")
        if dc not in CATEGORIES:
            raise ValueError(f"unknown default_category {dc!r}")
        unit = d.get("angle_unit", "rad")
        if unit not in ("rad", "deg"):
            raise ValueError("angle_unit must be 'rad' or 'deg'")
        bones = {str(k): str(v) for k, v in (d.get("bones") or {}).items()}
        bits = {str(k): int(v) for k, v in (d.get("move_flag_bits") or {}).items()}
        if set(bits) - {"sneak", "swim"}:
            raise ValueError("move_flag_bits keys must be 'sneak' and/or 'swim'")
        upm = float(d.get("units_per_meter", 70.0))
        if upm <= 0:
            raise ValueError("units_per_meter must be positive")
        ov = dict(d.get("thresholds") or {})
        from .config import Thresholds
        Thresholds.coerce(ov)   # valida as chaves agora, em vez de na análise
        return cls(name=str(d.get("name", "unnamed")), bones=bones, groups=groups, categories=cats,
                   category_prefixes=pres, default_category=dc, angle_unit=unit, units_per_meter=upm,
                   move_flag_bits=bits, threshold_overrides=ov, sparse_groups=sparse)

    @classmethod
    def load(cls, path: Union[str, Path]) -> "Profile":
        with open(path, "r", encoding="utf-8") as f:
            return cls.from_dict(json.load(f))

    def summary(self) -> str:
        cats: Dict[str, int] = {}
        n = len(self.groups) + len(self.sparse_groups)
        for i in list(range(len(self.groups))) + sorted(self.sparse_groups):
            c = self.category(i)
            cats[c] = cats.get(c, 0) + 1
        parts = ", ".join(f"{k}={v}" for k, v in sorted(cats.items()))
        return (f"profile {self.name!r}: {n} groups ({parts}); root bone {self.root_bone!r}; "
                f"angle unit {self.angle_unit}; {self.units_per_meter:g} units per meter")


# Pequeno perfil neutro: id do grupo = posição nesta lista; nome do grupo = sua categoria.
GENERIC = Profile(
    name="generic",
    bones={"root": "pelvis", "spine1": "spine_1", "spine2": "spine_2", "neck": "neck", "head": "head",
           "left_upper_arm": "upper_arm_l", "left_forearm": "forearm_l", "left_hand": "hand_l",
           "right_upper_arm": "upper_arm_r", "right_forearm": "forearm_r", "right_hand": "hand_r",
           "left_calf": "calf_l", "left_foot": "foot_l", "right_calf": "calf_r", "right_foot": "foot_r",
           "weapon": "weapon"},
    groups=("idle", "walk", "run", "dodge", "turn", "aim", "attack", "reload", "equip", "hit", "death", "jump",
            "block", "talk"),
    categories={"idle": ("idle",), "walk": ("walk",), "run": ("run",), "dodge": ("dodge",), "turn": ("turn",),
                "aim": ("aim",), "attack": ("attack",), "reload": ("reload",), "equip": ("equip",), "hit": ("hit",),
                "death": ("death",), "jump": ("jump",), "block": ("block",), "misc": ("talk",)},
)

DEFAULT_PROFILE = GENERIC
