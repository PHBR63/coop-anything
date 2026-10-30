// Referências e efeitos de história do mundo simulado.
//
// Uma Ref nomeia um elemento como um jogo baseado em plugins: (nome do pacote de conteúdo, id dentro dele). Nunca usa um
// índice bruto da ordem de carregamento, pois a ordem varia entre máquinas. Os ids do mundo simulado são inventados.
//
// Um Effect é uma alteração primitiva do mundo capturada no host e reproduzida em todas as máquinas (captura de efeitos):
// etapa de missão, matar, mover, habilitar, estado de porta, trava, criação e responsável por companheiro. Clientes aplicam efeitos diretamente e
// nunca reexecutam o script que os causou. Este é um subconjunto pequeno do necessário em um jogo real; acrescente seus efeitos aqui.
#pragma once
#include <cstdint>
#include <string>
#include <tuple>
#include <variant>
#include "coop/types.h"
#include "fakeworld/wire.h"

namespace coop::fakeworld {

struct Ref {
    std::string pack;
    uint32_t id = 0;

    Ref() = default;
    Ref(std::string p, uint32_t i) : pack(std::move(p)), id(i) {}
    friend bool operator==(const Ref& a, const Ref& b) { return a.id == b.id && a.pack == b.pack; }
    friend bool operator!=(const Ref& a, const Ref& b) { return !(a == b); }
    friend bool operator<(const Ref& a, const Ref& b) { return std::tie(a.pack, a.id) < std::tie(b.pack, b.id); }
};

// Referências criadas em execução (encontros gerados, itens largados) recebem ids alocados pelo host com este prefixo.
constexpr uint32_t kCreatedRefPrefix = 0xFF000000u;
inline Ref createdRef(uint32_t id) { return Ref("created", id); }

struct SetStage { Ref quest; uint32_t stage = 0; };            // regra de combinação: prevalece a etapa mais alta
struct StartQuest { Ref quest; };
struct StopQuest { Ref quest; };
struct KillActor { Ref actor; };
struct ResurrectActor { Ref actor; };
struct MoveRef { Ref ref; Ref cell; float x = 0, y = 0, z = 0; };
struct EnableRef { Ref ref; };
struct DisableRef { Ref ref; };
// Estado do objeto. mask bit0: define aberto/fechado, bit1: define trava (locked + level), bit2: destruído (persistente), bit3: ativado uma vez (persistente).
constexpr uint8_t kObjOpen = 1, kObjLock = 2, kObjDestroyed = 4, kObjActivated = 8;
struct ObjectState {
    Ref ref;
    uint8_t mask = 0;
    bool open = false, locked = false;
    int32_t level = 0;
    bool destroyed = false, activatedOnce = false;
};
struct SetLock { Ref ref; bool locked = false; int32_t level = 0; };
struct SpawnRef {
    uint32_t id = kCreatedRefPrefix;   // alocado pelo host, com prefixo 0xFF
    Ref base, cell;
    float x = 0, y = 0, z = 0;
    Ref ref() const { return createdRef(id); }
};
struct DespawnRef { uint32_t id = kCreatedRefPrefix; };
struct CompanionOwner { Ref npc; uint8_t owner = 0; bool active = true; };   // recrutar (ativo) ou dispensar seguidor

using Effect = std::variant<SetStage, StartQuest, StopQuest, KillActor, ResurrectActor, MoveRef, EnableRef, DisableRef,
                            ObjectState, SetLock, SpawnRef, DespawnRef, CompanionOwner>;

void io(Archive& a, Ref& v);
void io(Archive& a, Effect& v);

}  // namespace coop::fakeworld
