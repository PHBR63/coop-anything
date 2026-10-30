// Cenários compartilhados pelos testes reais e suas variantes de mutação. Cada um retorna true se, e somente se, todas as invariantes forem mantidas. Uma variante
// ativa uma opção de falha e espera que o mesmo cenário retorne false. `why` (opcional) recebe os primeiros
// problemas encontrados.
#pragma once
#include <string>
#include "coop/ownership.h"

namespace coop::testing {

bool churnHolds(uint64_t seed, int steps, std::string* why = nullptr);   // entradas e saídas aleatórias, confirmações perdidas, mensagens reordenadas e duplicadas
bool staleEchoRejected(std::string* why = nullptr);                      // uma atribuição antiga reproduzida depois não pode prevalecer
bool rejoinEpochsMonotonic(std::string* why = nullptr);                  // as épocas continuam aumentando após saída e retorno
bool noFlap(std::string* why = nullptr);                                 // dois jogadores aproximadamente à mesma distância: a responsabilidade não pode ficar alternando
bool followerStaysWithRecruiter(std::string* why = nullptr);             // um companheiro segue quem o recrutou a todos os lugares
bool handoffKeepsLastState(std::string* why = nullptr);                  // o antigo responsável mantém a autoridade até Ack e Commit

}  // namespace coop::testing
