// Cenários compartilhados pelos testes reais e suas variantes de mutação. Cada um retorna true se, e somente se, todas as invariantes forem mantidas; a
// variante ativa uma opção de falha e espera false. `why` (opcional) recebe os primeiros problemas.
#pragma once
#include <string>
#include "fakeworld/cluster.h"
#include "coop/ownership.h"

namespace coop::fakeworld::testing {

// Auxílio à depuração: chamado com o conjunto de máquinas quando um cenário termina com violações (definido por teste para exibir diagnósticos).
extern void (*dumpHook)(coop::fakeworld::Cluster&);
extern coop::fakeworld::IEngineObserver* debugObserver;   // opcional: associado ao conjunto de máquinas de randomSession

// ---- responsabilidade em um conjunto completo de máquinas ----
bool noFlap(std::string* why = nullptr);                                 // dois jogadores à mesma distância: a responsabilidade não pode ficar alternando 
bool followerStaysWithRecruiter(std::string* why = nullptr);

// ---- cenários do mecanismo (Cluster) ----
coop::fakeworld::ClusterConfig baseConfig(uint64_t seed, int players, const LinkParams& link = {});
LinkParams lossyLink();

bool joinAndSync(uint64_t seed, int players, const LinkParams& link, std::string* why = nullptr);
bool fightScenario(uint64_t seed, const LinkParams& link, std::string* why = nullptr);
bool handoffMidFight(uint64_t seed, std::string* why = nullptr);
bool handoffKeepsLastState(uint64_t seed, std::string* why = nullptr);   // convidado para convidado: último estado do antigo responsável chega ao novo antes de ele assumir
bool lootRace(uint64_t seed, std::string* why = nullptr);
bool spawnOnce(uint64_t seed, std::string* why = nullptr);
bool containerMatrix(uint64_t seed, std::string* why = nullptr);
bool doorsAndLocks(uint64_t seed, std::string* why = nullptr);
bool namedProtected(uint64_t seed, std::string* why = nullptr);
bool questStageSync(uint64_t seed, const LinkParams& link, std::string* why = nullptr);
bool recruitCompanion(uint64_t seed, std::string* why = nullptr);
bool saveLoadRejoin(uint64_t seed, std::string* why = nullptr);
bool healsCorruption(uint64_t seed, std::string* why = nullptr);
bool dropIdempotent(uint64_t seed, std::string* why = nullptr);
bool forgedHitsRejected(uint64_t seed, std::string* why = nullptr);
bool hitToNonOwnerRejected(uint64_t seed, std::string* why = nullptr);
bool lateJoinerGetsOwnership(uint64_t seed, std::string* why = nullptr);
bool formerOwnerSilenced(uint64_t seed, std::string* why = nullptr);
bool randomSession(uint64_t seed, int players, uint32_t ms, const LinkParams& link, std::string* why = nullptr);

}  // namespace coop::fakeworld::testing
