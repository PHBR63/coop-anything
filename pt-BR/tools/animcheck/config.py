"""Limiares e tolerâncias. Distâncias em unidades do jogo, para mundo de cerca de 70 unidades/metro; tempos
em milissegundos. Perfil pode redimensionar (`units_per_meter`) e substituir valores (`thresholds`); código pode
substituir qualquer um: Thresholds(slide_min_speed=80, ...). Padrões são pontos iniciais: execute primeiro sessão limpa
do jogo e ajuste por ela (veja README.md, "Tuning")."""
from __future__ import annotations

import os
from dataclasses import dataclass, field, fields, replace
from typing import Dict, Tuple


def mutant() -> str:
    "Nome da variante mutante ativa (só testes), '' no uso normal."
    return os.environ.get("ANIMCHECK_MUTANT", "")


@dataclass(frozen=True)
class Thresholds:
    # ---- amostragem ----
    gap_ms: float = 600.0              # intervalo maior que isto entre amostras de ator interrompe sequência
    min_dt_ms: float = 5.0             # amostras mais próximas que isto são tratadas como uma

    # ---- comparação entre máquinas ----
    interp_delay_ms: float = 100.0     # receptor mostra estado aproximadamente este tempo mais antigo que proprietário
    latency_allow_ms: float = 150.0    # janela extra (latência de rede de ida + variação de amostragem) pesquisada de cada lado
    pose_tol_units: float = 12.0       # limite padrão usado só pelo resumo aprovado/reprovado do relatório
    facing_tol_deg: float = 35.0
    aim_tol_deg: float = 20.0
    state_grace_ms: float = 400.0      # divergência de arma / grupo mais curta que isto é transição, não erro

    # ---- deslizamento (movimento sem animação de locomoção correspondente) ----
    slide_min_speed: float = 40.0      # unidades/s horizontais abaixo das quais ator conta como parado
    slide_ms: float = 300.0
    loco_bands: Dict[str, Tuple[float, float]] = field(default_factory=lambda: {
        "walk": (8.0, 280.0),          # categoria -> faixa plausível de velocidade horizontal enquanto animação executa
        "run": (120.0, 900.0),
        "dodge": (0.0, 1500.0),
    })
    band_ms: float = 500.0             # velocidade fora da faixa por este tempo = divergência animação / velocidade

    # ---- pose T ----
    tpose_ms: float = 300.0
    tpose_arm_dz: float = 5.0          # mãos dentro desta diferença da altura do braço superior ...
    tpose_arm_span: float = 36.0       # ... e pelo menos esta distância horizontal dele: braços esticados

    # ---- flutuação / afundamento ----
    ground_step: float = 30.0          # mudança z em relação ao chão acompanhado que ainda é "terreno"
    float_ms: float = 400.0
    fall_vz: float = 400.0             # velocidade vertical acima da qual ator cai / salta

    # ---- oscilação ----
    jitter_window: int = 8             # amostras
    jitter_amp: float = 2.5            # passo mínimo (unidades) que conta como inversão de direção
    jitter_reversals: int = 5          # inversões dentro da janela

    # ---- correções bruscas de posição ----
    rubber_dist: float = 150.0         # salto de uma amostra
    rubber_speed: float = 2500.0       # unidades/s implícitas nesse salto
    snapback_ms: float = 600.0         # salto seguido de retorno a perto do ponto anterior dentro deste prazo

    # ---- travado ----
    stuck_ms: float = 1500.0
    stuck_speed: float = 5.0

    # ---- postura de morte errada ----
    death_grace_ms: float = 2500.0

    def with_(self, **kw) -> "Thresholds":
        kw = self.coerce(kw)
        if "loco_bands" in kw:   # uma sobreposição parcial mantém as faixas não mencionadas
            kw["loco_bands"] = {**self.loco_bands, **kw["loco_bands"]}
        return replace(self, **kw)

    @classmethod
    def coerce(cls, kw: dict) -> dict:
        "Confira chaves de um dict de sobreposição (por exemplo de perfil) e ajuste a estrutura de loco_bands."
        names = {f.name for f in fields(cls)}
        bad = sorted(k for k in kw if k not in names)
        if bad:
            raise ValueError(f"unknown threshold(s): {', '.join(bad)}")
        out = dict(kw)
        if "loco_bands" in out:
            out["loco_bands"] = {str(k): (float(v[0]), float(v[1])) for k, v in out["loco_bands"].items()}
        return out

    def scaled(self, k: float) -> "Thresholds":
        "Distâncias e velocidades multiplicadas por k (unidades de mundo por metro relativas às 70 presumidas pelos padrões)."
        if k == 1.0:
            return self
        dist = ("pose_tol_units", "slide_min_speed", "tpose_arm_dz", "tpose_arm_span", "ground_step", "fall_vz",
                "jitter_amp", "rubber_dist", "rubber_speed", "stuck_speed")
        kw = {n: getattr(self, n) * k for n in dist}
        kw["loco_bands"] = {c: (lo * k, hi * k) for c, (lo, hi) in self.loco_bands.items()}
        return replace(self, **kw)


DEFAULT = Thresholds()
