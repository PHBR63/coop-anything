// Mensagens de rede da camada ativa do motor simulado (atores, combate, saque, contêineres, criações, resumos).
// Codificado com Archive. Um Envelope por carga útil de datagrama; um quadro ReliableLink o envolve (machine.cpp).
#pragma once
#include <variant>
#include <vector>
#include "fakeworld/effect.h"
#include "fakeworld/types.h"
#include "coop/ownership.h"
#include "fakeworld/net.h"

namespace coop::fakeworld {

constexpr uint8_t kEngineWireVersion = 1;

void io(Archive& a, OwnMsg& m);   // mensagens de responsabilidade trafegam no mesmo formato Archive

using LootList = std::vector<std::pair<Ref, int32_t>>;

struct MFullState { uint32_t sess = 0; uint64_t hostNowMs = 0; uint64_t fxSeq = 0; Bytes world; std::vector<OwnMsg> own; };
struct MPose { PlayerId slot = kNoPlayer; bool present = true; CellId cell = 0; Vec3 pos; float yaw = 0; uint32_t seq = 0; bool settle = false; };   // settle: o jogador parou; enviado uma vez com confiabilidade
struct MVitals { PlayerId slot = kNoPlayer; int32_t health = 100; bool dead = false; uint32_t seq = 0; };
// Responsável -> todos (via host). `final` = último estado do antigo responsável durante uma transferência.
struct MActorSnap { NetId id = 0; OwnerEpoch epoch = 0; uint32_t seq = 0; CellId cell = 0; Vec3 pos; float yaw = 0;
                    int32_t health = 0; bool dead = false; bool settle = false; bool final = false; };
enum class ActorEventKind : uint8_t { Vitals = 0, Death = 1 };
struct MActorEvent { NetId id = 0; OwnerEpoch epoch = 0; uint64_t eventId = 0; ActorEventKind kind = ActorEventKind::Vitals;
                     int32_t health = 0; uint8_t limbMask = 0; bool dead = false; LootList loot;
                     uint32_t seq = 0; CellId cell = 0; Vec3 pos; float yaw = 0; };   // pos/seq: estado do responsável quando ocorreu (o cadáver para onde caiu)
struct MHit { uint64_t hitId = 0; bool attackerIsPlayer = true; uint32_t attacker = 0; bool victimIsPlayer = false; uint32_t victim = 0;
              int32_t damage = 0; Limb limb = Limb::Torso; Vec3 impact; float weaponRange = 0; uint8_t hops = 0; };
struct MOwn { OwnMsg m; };
struct MEffects { uint64_t seq = 0; std::vector<Effect> fx; };
struct MDropReq { uint32_t reqId = 0; Ref base; CellId cell = 0; Vec3 pos; };
struct MItemCreated { NetId id = 0; Ref base; CellId cell = 0; Vec3 pos; uint64_t origin = 0; };
struct MPickup { uint64_t claimId = 0; NetId item = 0; };
struct MItemTaken { NetId item = 0; PlayerId by = kNoPlayer; uint64_t claimId = 0; };
enum class ContainerOpKind : uint8_t { Open = 0, Close = 1, Take = 2, Put = 3 };
struct MContainerReq { uint64_t opId = 0; NetId cont = 0; ContainerOpKind op = ContainerOpKind::Open; Ref base; int32_t count = 0; uint64_t closeHash = 0; };
struct MContainerRes { uint64_t opId = 0; NetId cont = 0; ContainerOpKind op = ContainerOpKind::Open; bool ok = false; Ref base; int32_t count = 0; };
struct MContainerSync { NetId cont = 0; Ref base; int32_t newCount = 0; };
struct MSpawnRoll { NetId site = 0; };
struct MSpawnActor { NetId id = 0; NetId site = 0; Ref base; Ref pick; CellId cell = 0; Vec3 pos; };
struct MSiteState { NetId site = 0; NetId spawned = 0; bool cleared = false; uint64_t clearedAtMs = 0; uint32_t spawnCount = 0; };
struct MActivate { NetId obj = 0; };
struct MDigest { uint8_t cat = 0; uint64_t total = 0; std::vector<std::pair<uint32_t, uint64_t>> keys; };
struct MRepair { uint8_t cat = 0; std::vector<std::pair<uint32_t, Bytes>> states; std::vector<uint32_t> removes; };

using Body = std::variant<MFullState, MPose, MVitals, MActorSnap, MActorEvent, MHit, MOwn, MEffects, MDropReq, MItemCreated,
                          MPickup, MItemTaken, MContainerReq, MContainerRes, MContainerSync, MSpawnRoll, MSpawnActor,
                          MSiteState, MActivate, MDigest, MRepair>;

struct Envelope {
    uint32_t sess = 0;
    PlayerId src = kNoPlayer;
    PlayerId dest = kNoPlayer;   // kNoPlayer = todos exceto src
    Body body;
};

const char* bodyName(const Body& b);
bool reliableByDefault(const Body& b);     // pose, capturas sem estabilização e resumos: não confiáveis; todo o resto é confiável
Bytes encode(const Envelope& e);
bool decode(const Bytes& data, Envelope& out);   // false para qualquer entrada malformada (nunca lança exceção)

// Uma ação local do jogador/host. Tudo que um teste ou fuzzer pode fazer a uma máquina passa por Machine::doAction(Action),
// assim, um fluxo Action registrado é um roteiro completo e reproduzível.
enum class ActionKind : uint8_t {
    Move = 0, Attack, Pickup, Drop, ContainerOpen, ContainerClose, ContainerTake, ContainerPut, Activate, UseDoor,
    Recruit, Dismiss, HostSetStage, HostSetLock, HostKill, Revive, Count_
};
struct Action {
    ActionKind kind = ActionKind::Move;
    uint32_t a = 0;         // cell / victim / item / container / object / actor
    int32_t n = 0;          // damage / count / stage / level
    Vec3 pos;               // destino de movimento / ponto de impacto
    float f = 0;            // rotação horizontal / alcance da arma
    Ref base;           // base do item / missão
    Limb limb = Limb::Torso;
    bool flag = false;      // HostSetLock: locked
};
void io(Archive& a, Action& v);
const char* toString(ActionKind k);

}  // namespace coop::fakeworld
