// Mundo de jogo simulado: dados simples das partes de um mundo típico que você sincroniza (atores, contêineres, itens, portas,
// locais de criação, jogadores, missões). Sem jogo e determinístico. Renomeie e remodele para seu jogo.
#pragma once
#include <cstdint>
#include <map>
#include <string>
#include <vector>
#include "coop/types.h"
#include "fakeworld/effect.h"
#include "fakeworld/wire.h"

namespace coop::fakeworld {

using NetId = uint32_t;     // uma identidade por objeto; referências criadas usam prefixo 0xFF (veja isCreatedId)
using CellId = uint32_t;
constexpr uint32_t kCreatedIdBase = 0xFF000000u;
inline bool isCreatedId(NetId id) { return (id >> 24) == 0xFF; }

constexpr float kCellSize = 4096.0f;

struct Vec3 {
    float x = 0, y = 0, z = 0;
    friend bool operator==(const Vec3& a, const Vec3& b) { return a.x == b.x && a.y == b.y && a.z == b.z; }
};
float distance(const Vec3& a, const Vec3& b);
float distance2d(const Vec3& a, const Vec3& b);

enum class Limb : uint8_t { Torso = 0, Head, LeftArm, RightArm, LeftLeg, RightLeg, Count_ };

enum class Category : uint8_t { Story = 0, Actors = 1, Containers = 2, Objects = 3, Count_ };
const char* toString(Category c);

struct CellDef {
    CellId id = 0;
    bool interior = false;
    int32_t gx = 0, gy = 0;   // posição na grade exterior (interiores: não usada)
};

struct ActorState {
    NetId id = 0;
    Ref ref, base;
    bool created = false;       // criado em execução (ID 0xFF alocado pelo host)
    CellId cell = 0;
    Vec3 pos;
    float yaw = 0;
    int32_t health = 100, maxHealth = 100;
    bool dead = false, enabled = true, aiOn = false;   // aiOn é por máquina (responsável true, outros false): não entra no resumo
    bool hostile = false;
    bool named = false;         // NPC de história: só um efeito KillActor da história pode matá-lo
    PlayerId recruiter = kNoPlayer;
    NetId site = 0;             // local de criação que o produziu (0 = posicionado)
    uint8_t limbMask = 0;       // membros incapacitados
    uint32_t snapSeq = 0;       // contador de capturas do responsável (o mais recente vence)
    Ref pick;               // seleção escalonada por nível, feita uma vez pelo host (igual a base quando não escalonada)
};

struct ContainerState {
    NetId id = 0;
    CellId cell = 0;
    Vec3 pos;
    bool corpse = false;
    std::map<Ref, int32_t> items;
    PlayerId inUseBy = kNoPlayer;   // transitório: não entra no resumo
    std::vector<uint64_t> appliedOps;   // IDs de idempotência de operações take/put já aplicadas (lado do host, limitado)
};

struct ItemState {
    NetId id = 0;
    Ref base;
    CellId cell = 0;
    Vec3 pos;
    bool taken = false;
    PlayerId takenBy = kNoPlayer;
    uint64_t origin = 0;        // (slot de quem descarta << 32 | ID da solicitação): um descarte = um item
};

enum class ObjKind : uint8_t { Door = 0, Terminal = 1, Switch = 2 };
struct WorldObject {
    NetId id = 0;
    ObjKind kind = ObjKind::Door;
    CellId cell = 0;
    Vec3 pos;
    bool open = false, locked = false;
    int32_t lockLevel = 0;
    bool destroyed = false, activatedOnce = false, enabled = true;
    CellId targetCell = 0;      // portas que teletransportam
    Vec3 targetPos;
};

struct SpawnSiteState {
    NetId id = 0;
    CellId cell = 0;
    Vec3 pos;
    Ref variantA, variantB;   // escolhas escalonadas por nível
    uint32_t respawnMs = 30000;
    NetId spawned = 0;            // ator ativo deste local (0 = nenhum)
    PlayerId rolledBy = kNoPlayer;   // vencedor da arbitragem (diagnóstico)
    uint32_t spawnCount = 0;
    uint64_t clearedAtMs = 0;     // horário virtual da morte de seu ator
    bool cleared = false;
    bool permanent = false;       // interior eliminado permanece eliminado
};

struct PlayerState {
    PlayerId slot = kNoPlayer;
    bool present = false;
    CellId cell = 0;
    Vec3 pos;
    float yaw = 0;
    int32_t health = 100, maxHealth = 100;
    bool dead = false;
    uint32_t poseSeq = 0, vitalsSeq = 0;
    std::map<Ref, int32_t> inventory;   // autoritativo só na máquina responsável
};

// serialização (simétrica, via Archive)
void io(Archive& a, Vec3& v);
void io(Archive& a, CellDef& v);
void io(Archive& a, ActorState& v);
void io(Archive& a, ContainerState& v);
void io(Archive& a, ItemState& v);
void io(Archive& a, WorldObject& v);
void io(Archive& a, SpawnSiteState& v);
void io(Archive& a, PlayerState& v);

}  // namespace coop::fakeworld
