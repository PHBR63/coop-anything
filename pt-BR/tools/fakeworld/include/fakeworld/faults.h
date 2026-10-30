// Opções de falha EXCLUSIVAS PARA TESTES do mundo simulado (mesma ideia de coop::OwnershipFaults na biblioteca de responsabilidade).
// Cada flag reintroduz um erro clássico; o oráculo de invariantes que o protege deve então disparar. Todas false em produção.
#pragma once

namespace coop::fakeworld {

struct EngineFaults {
    bool noDedupe = false;              // enlaces e IDs de transação deixam de descartar duplicatas: mensagens entregues novamente são aplicadas duas vezes
    bool hitNoValidation = false;       // o responsável pela vítima aplica qualquer acerto (sem verificar alcance, dano, frequência ou ponto de impacto)
    bool hitAppliedByNonOwner = false;  // uma máquina que não é responsável pela vítima aplica um acerto recebido (e o encaminha)
    bool pickupNoArbitration = false;   // o host concede toda solicitação de coleta: ambos os competidores ficam com o item
    bool noPickupRollback = false;      // quem perde a disputa de coleta mantém o item adicionado de forma otimista
    bool spawnNoArbitration = false;    // o host cria para cada sorteio: um encontro aparece uma vez por quem sorteia
    bool lootPerMachine = false;        // cada máquina sorteia o saque do cadáver por conta própria em vez de usar o sorteio do responsável
    bool pickPerMachine = false;        // cada máquina faz sua própria seleção escalonada por nível
    bool containerNoLock = false;       // um contêiner pode estar aberto para dois jogadores ao mesmo tempo
    bool namedActorKillable = false;    // o responsável pode matar NPCs da história em combate
    bool noSessionEpoch = false;        // mensagens anteriores a um carregamento do host são aplicadas depois dele
    bool healDisabled = false;          // divergências de resumos são detectadas, mas nunca reparadas
    bool dropNoIdempotency = false;     // uma solicitação de descarte reenviada cria um segundo item no mundo
    bool ownerKeepsPublishing = false;  // um antigo responsável continua enviando capturas de estado após perder o ator
    bool joinNoOwnership = false;       // o estado completo enviado a quem entra omite a tabela de responsabilidade
};
inline EngineFaults& engineFaults() { static EngineFaults f; return f; }
struct EngineFaultScope {
    EngineFaults saved;
    explicit EngineFaultScope(const EngineFaults& f) : saved(engineFaults()) { engineFaults() = f; }
    ~EngineFaultScope() { engineFaults() = saved; }
};

}  // namespace coop::fakeworld
