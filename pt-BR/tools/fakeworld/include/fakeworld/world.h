// O mundo em memória mantido por uma máquina. Dados puros mais mutações, consultas e resumos determinísticos.
// Cada máquina tem seu próprio World; o protocolo de sincronização (machine.h) os mantém iguais.
#pragma once
#include <functional>
#include <map>
#include <string>
#include <vector>
#include "fakeworld/effect.h"
#include "fakeworld/types.h"
#include "fakeworld/rng.h"
#include "fakeworld/net.h"

namespace coop::fakeworld {

// Descreve o conteúdo estático que cada máquina carrega dos pacotes (igual em todas).
struct WorldSpec {
    uint64_t seed = 1;
    int gridW = 4, gridH = 4;       // células exteriores
    int interiors = 2;
    int actorsPerCell = 3;
    int hostilePercent = 50;
    int namedPerWorld = 2;
    int containersPerCell = 1;
    int itemsPerCell = 1;
    int doorsPerCell = 1;
    int sitesPerCell = 1;
    uint32_t respawnMs = 30000;
};

struct EffectStats {
    uint64_t applied = 0, ignored = 0, unknownTarget = 0;
};

class World {
public:
    static World build(const WorldSpec& spec);

    // ---- células ----
    CellId cellAt(int gx, int gy) const;                 // 0 se fora da grade
    bool cellKnown(CellId c) const { return cells_.count(c) != 0; }
    bool adjacent(CellId a, CellId b) const;             // mesma célula exterior ou vizinha
    std::vector<CellId> loadedAround(CellId c) const;    // células carregadas para jogador em c (proximidade)
    const std::map<CellId, CellDef>& cells() const { return cells_; }
    Vec3 cellCenter(CellId c) const;

    // ---- entidades ----
    std::map<NetId, ActorState>& actors() { return actors_; }
    const std::map<NetId, ActorState>& actors() const { return actors_; }
    std::map<NetId, ContainerState>& containers() { return containers_; }
    const std::map<NetId, ContainerState>& containers() const { return containers_; }
    std::map<NetId, ItemState>& items() { return items_; }
    const std::map<NetId, ItemState>& items() const { return items_; }
    std::map<NetId, WorldObject>& objects() { return objects_; }
    const std::map<NetId, WorldObject>& objects() const { return objects_; }
    std::map<NetId, SpawnSiteState>& sites() { return sites_; }
    const std::map<NetId, SpawnSiteState>& sites() const { return sites_; }
    PlayerState& player(PlayerId p) { return players_[p % kMaxSlots]; }
    const PlayerState& player(PlayerId p) const { return players_[p % kMaxSlots]; }
    std::map<Ref, uint32_t>& quests() { return quests_; }
    const std::map<Ref, uint32_t>& quests() const { return quests_; }

    ActorState* findActor(NetId id) { auto it = actors_.find(id); return it == actors_.end() ? nullptr : &it->second; }
    NetId actorByRef(const Ref& r) const { auto it = refToNet_.find(r); return it == refToNet_.end() ? 0 : it->second; }
    NetId allocCreatedId() { return kCreatedIdBase | ++createdCounter_; }
    void noteCreatedId(NetId id) { if (isCreatedId(id) && (id & 0xFFFFFFu) > createdCounter_) createdCounter_ = id & 0xFFFFFFu; }
    // Insere ou substitui ator e mantém correto o índice de referências.
    ActorState& putActor(const ActorState& a);
    void eraseActor(NetId id);

    // ---- história / efeitos (vocabulário de efeitos que o modelo pode mostrar) ----
    bool applyEffect(const Effect& e);
    const EffectStats& effectStats() const { return fx_; }
    Ref cellRef(CellId c) const;                     // Ref usado por MoveRef para uma célula
    CellId cellFromRef(const Ref& r) const;

    // ---- resumos: por categoria, por chave ----
    uint64_t digest(Category c) const;
    uint64_t keyHash(Category c, uint32_t key) const;   // 0 se a chave não existir
    std::map<uint32_t, uint64_t> keyHashes(Category c) const;
    bool exportKey(Category c, uint32_t key, Archive& a) const;      // false se a chave não existir
    bool importKey(Category c, uint32_t key, Archive& a);            // substitui/cria a entidade
    void removeKey(Category c, uint32_t key);
    // Serialização de todo o mundo (salvar/carregar do host, estado completo para quem entra).
    Bytes save() const;
    bool load(const Bytes& b);

    // ---- utilitários de oráculos ----
    // Identidades duplicadas: mais de um ator ativo de um local, itens compartilhando origem etc. Uma linha por caso.
    std::vector<std::string> duplicates() const;
    // Itens no chão (não coletados) mais conteúdo de cadáveres/contêineres, somados por base. Inventários dos jogadores não incluídos.
    std::map<Ref, int64_t> worldItemCensus() const;
    uint32_t standIns(const std::vector<CellId>& loaded) const;   // atores ativos cuja célula não está carregada aqui

    uint64_t nowMs = 0;   // último horário virtual de alteração do mundo (usado no controle de reaparecimento)

private:
    std::map<CellId, CellDef> cells_;
    std::map<NetId, ActorState> actors_;
    std::map<NetId, ContainerState> containers_;
    std::map<NetId, ItemState> items_;
    std::map<NetId, WorldObject> objects_;
    std::map<NetId, SpawnSiteState> sites_;
    PlayerState players_[kMaxSlots];
    std::map<Ref, uint32_t> quests_;
    std::map<Ref, NetId> refToNet_;   // atores posicionados e criados, objetos posicionados
    uint32_t createdCounter_ = 0;
    EffectStats fx_;
    int gridW_ = 0, gridH_ = 0;

};

// Utilitários de Ref: referências posicionadas ficam no pacote-base de conteúdo.
inline Ref placedRef(NetId id) { return Ref("world.pack", id); }
uint32_t keyOfQuest(const Ref& r);

}  // namespace coop::fakeworld
