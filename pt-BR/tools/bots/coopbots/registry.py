"Nome -> roteiro, construtor do mundo simulado e quantidade padrão de jogadores; mais as variantes de mutação."
from typing import Callable, Dict, NamedTuple, Optional

from .core import Playbook
from .playbooks import combat, loot, session, social, story, world


class Entry(NamedTuple):
    cls: type
    fake: Optional[Callable]
    players: int


REGISTRY: Dict[str, Entry] = {
    "fight": Entry(combat.FightPlaybook, combat.build_fight, 2),
    "ownership_handoff": Entry(combat.OwnershipHandoffPlaybook, combat.build_handoff, 2),
    "loot_race": Entry(loot.LootRacePlaybook, loot.build_loot, 2),
    "container_share": Entry(loot.ContainerSharePlaybook, loot.build_container, 2),
    "door_lock": Entry(world.DoorLockPlaybook, world.build_doors, 2),
    "fast_travel_tether": Entry(world.FastTravelTetherPlaybook, world.build_travel, 2),
    "dialogue_spectator": Entry(social.DialogueSpectatorPlaybook, social.build_dialogue, 3),
    "consent_vote": Entry(story.ConsentVotePlaybook, story.build_consent, 3),
    "consent_vote_guest_declines": Entry(story.ConsentVoteGuestDeclinesPlaybook, story.build_consent, 2),
    "quest_sync": Entry(story.QuestSyncPlaybook, story.build_sync, 2),
    "save_load_rejoin": Entry(session.SaveLoadRejoinPlaybook, session.build_saveload, 3),
    "spawn_once": Entry(session.SpawnOncePlaybook, session.build_spawn, 2),
}

# Variantes: pares (roteiro, bug simulado) em que o roteiro PRECISA falhar. Os testes executam todos e também listam
# o que cada roteiro consegue detectar.
TWINS = [
    ("fight", "dup_kill"), ("fight", "stale_echo"), ("fight", "no_fight_sync"),
    ("ownership_handoff", "owner_split"), ("ownership_handoff", "flap_owner"),
    ("loot_race", "dup_pickup"),
    ("container_share", "no_container_sync"), ("container_share", "no_container_lock"),
    ("door_lock", "door_unsynced"), ("door_lock", "lock_unsynced"), ("door_lock", "device_unsynced"),
    ("fast_travel_tether", "tether_off"), ("fast_travel_tether", "consent_ignored"), ("fast_travel_tether", "travel_in_combat"),
    ("dialogue_spectator", "spectator_stuck"), ("dialogue_spectator", "dialogue_not_bridged"),
    ("consent_vote", "barrier_early"), ("consent_vote", "veto_ignored"), ("consent_vote", "no_stage_sync"),
    ("consent_vote_guest_declines", "veto_ignored"),
    ("quest_sync", "no_stage_sync"), ("quest_sync", "no_objective_sync"), ("quest_sync", "client_frozen"),
    ("save_load_rejoin", "no_rebase"), ("save_load_rejoin", "reward_dup_on_rejoin"), ("save_load_rejoin", "no_stage_sync"),
    ("spawn_once", "double_spawn"),
]
# Bugs não vinculados a um roteiro: counter_noise precisa ser detectado por todos os roteiros (os contadores de dessincronização subiram);
# os próximos três são bugs de conexão degradada, exercitados pelos testes de conexão, e os dois últimos são bugs de velocidade do jogo, exercitados pelos
# testes --timescale (tests/test_resume.py).
UNIVERSAL = {"counter_noise", "no_retransmit", "repair_after_quiet", "repairs_in_flight", "timescale_ignored", "speed_not_reset"}
# Roteiros cujas etapas usam ctx.run_step com uma parte de preparação: --from-step e --only-step funcionam neles.
RESUMABLE = ("fight", "quest_sync", "loot_race")


def make(name: str) -> Playbook:
    return REGISTRY[name].cls()
