"""Opções de conexão degradada para o executor: janelas sem atividade e orçamentos de reparo por perfil.

Os nomes dos perfis correspondem a tools/chaos/profiles.json (lan, good_wifi, bad_wifi, mobile_tether, transatlantic, hell).
Este módulo não degrada nada por si só. Inicie o retransmissor de caos (tools/chaos) entre as instâncias e passe
`link_options(profile)` como opções do executor. Em uma conexão degradada:

  * divergências transitórias e reparos enquanto há tráfego em trânsito são registrados, não reprovados (strict_counters desativado);
  * cada etapa termina com uma janela sem atividade (`quiesce_s`): nada novo é enviado, todas as máquinas precisam convergir
    e não pode ocorrer reparo durante uma segunda janela sem atividade;
  * a execução inteira tem um orçamento de reparos por minuto. O padrão é 0 (estrito). Um orçamento acima de 0 exige um
    motivo escrito junto a ele no arquivo de perfis (`repair_budget_reason`), ou a execução se recusa a iniciar;
  * contadores graves (mensagens inválidas, aplicações com falha, redefinições de base) continuam causando falha imediata.
"""
import json
import os
from typing import Any, Dict, Optional

PROFILES = ("lan", "good_wifi", "bad_wifi", "mobile_tether", "transatlantic", "hell")
# segundos sem tráfego novo após os quais o mundo precisa ter convergido com 0 reparos; ajustados à latência mais a variação
QUIESCE_S = {"lan": 1.0, "good_wifi": 2.0, "bad_wifi": 6.0, "mobile_tether": 8.0, "transatlantic": 6.0, "hell": 20.0}
SETTLE_S = {"lan": 20.0, "good_wifi": 30.0, "bad_wifi": 60.0, "mobile_tether": 90.0, "transatlantic": 90.0, "hell": 180.0}
# somente mundo simulado: cada enésima entrega a um cliente é perdida e retransmitida (0 = nenhuma)
FAKE_LOSS_EVERY = {"lan": 0, "good_wifi": 25, "bad_wifi": 5, "mobile_tether": 11, "transatlantic": 40, "hell": 3}


def repair_budget(profiles_path: Optional[str], profile: str) -> float:
    "Reparos por minuto permitidos para um perfil: `repair_budget_per_min` no arquivo de perfis; padrão 0."
    if not profiles_path:
        return 0.0
    try:
        with open(profiles_path, encoding="utf-8") as f:
            p = json.load(f).get(profile, {})
    except (OSError, ValueError):
        return 0.0
    b = float(p.get("repair_budget_per_min", 0.0))
    if b > 0 and not p.get("repair_budget_reason"):
        raise ValueError("%s loosens repair_budget_per_min to %s without a repair_budget_reason" % (profile, b))
    return b


def link_options(profile: Optional[str], profiles_path: Optional[str] = None) -> Dict[str, Any]:
    "Opções do executor para um perfil de conexão. Vazio se não houver perfil ou se for lan: aplicam-se os padrões estritos."
    if not profile or profile == "lan":
        return {}
    if profile not in PROFILES:
        raise ValueError("unknown link profile %r; choose from %s" % (profile, ", ".join(PROFILES)))
    t = SETTLE_S[profile]
    return {"strict_counters": False, "settle_s": t, "barrier_s": t, "stage_s": t, "ui_s": t, "chaos": profile,
            "quiesce_s": QUIESCE_S[profile], "repair_budget_per_min": repair_budget(profiles_path, profile)}


def default_profiles_path() -> Optional[str]:
    "tools/chaos/profiles.json deste repositório, se existir."
    p = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "chaos", "profiles.json")
    return p if os.path.isfile(p) else None
