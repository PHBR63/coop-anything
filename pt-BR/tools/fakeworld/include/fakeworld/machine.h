// Um par simulado: réplica World, visão de propriedade (host também roda OwnershipService),
// protocolo da camada ativa, pequeno enlace confiável e ordenado sobre datagramas com perdas, IA NPC determinística para atores
// que possui. Sem threads ou relógio real: aparato alimenta bytes (receive), avança tempo (tick) e leva
// fila de saída ao transporte usado (InMemoryNetwork em Cluster).
#pragma once
#include <deque>
#include <map>
#include <memory>
#include <set>
#include <string>
#include <vector>
#include "fakeworld/faults.h"
#include "fakeworld/messages.h"
#include "fakeworld/observer.h"
#include "fakeworld/world.h"
#include "coop/ownership.h"
#include "fakeworld/rng.h"
#include "fakeworld/net.h"

namespace coop::fakeworld {

struct MachineConfig {
    PlayerId self = kHostPlayer;
    uint64_t seed = 1;
    WorldSpec spec;
    OwnershipConfig own;
    uint32_t poseMs = 50;          // intervalo de publicação de postura do jogador (20 Hz)
    uint32_t snapshotMs = 50;      // snapshots do proprietário perto de jogadores (20 Hz)
    uint32_t farSnapshotMs = 200;  // snapshots do proprietário longe de todos jogadores (5 Hz)
    uint32_t settleMs = 300;       // ator parado por este tempo -> um snapshot confiável de estabilização
    uint32_t ownEvalMs = 250;      // avaliação host de propriedade / ressurgimento
    uint32_t digestMs = 600;       // intervalo de relatos de digest
    uint32_t rtoMs = 120;          // timeout de retransmissão do enlace confiável
    float aggroRange = 3000, meleeRange = 150, npcSpeed = 300, wanderSpeed = 80;   // unidades, unidades por segundo
    int32_t npcDamage = 5;
    uint32_t npcAttackMs = 1000;
    // verificações de sanidade de impacto pelo proprietário da vítima 
    float maxWeaponRange = 6000, rangeSlack = 700, impactSlack = 400;
    int32_t maxDamage = 500;
    uint32_t maxHitsPerSec = 20;
};

struct Outgoing { PeerId to = 0; Channel ch = Channel::Reliable; Bytes data; };

struct MachineStats {
    uint64_t framesBadCrc = 0, framesStaleConn = 0, linkDuplicates = 0, linkRetransmits = 0, droppedStaleSession = 0, undecodable = 0;
    uint64_t hitsApplied = 0, hitsRejected = 0, hitsForwarded = 0, hitDuplicates = 0;
    uint64_t pickupsWon = 0, pickupsLost = 0, rollbacks = 0, dropsDeduped = 0;
    uint64_t containerOps = 0, containerRefused = 0, closeDigestMismatch = 0;
    uint64_t spawns = 0, spawnRollsIgnored = 0, spawnRollsRepeated = 0;
    uint64_t snapshotsApplied = 0, snapshotsDropped = 0, eventsApplied = 0, eventsDuplicate = 0;
    uint64_t fxApplied = 0, fxDuplicate = 0;
    uint64_t repairsSent = 0, repairsApplied = 0, repairKeys = 0, ownerDiffsSkipped = 0;
    uint64_t doubleApplied = 0;      // id já aplicado pela máquina foi reaplicado (deve continuar 0)
    uint64_t resyncs = 0, hostLoads = 0, finalSnaps = 0, acks = 0;
};

class Machine {
public:
    explicit Machine(const MachineConfig& cfg);

    PlayerId self() const { return cfg_.self; }
    bool isHost() const { return cfg_.self == kHostPlayer; }
    bool synced() const { return synced_; }
    uint32_t sess() const { return sess_; }
    uint64_t now() const { return now_; }
    void setObserver(IEngineObserver* o) { obs_ = o; }

    // ---- conexões ----
    std::vector<Outgoing> takeOutbox();
    void peerConnected(PeerId p, uint32_t connEpoch);   // host: cliente chegou; cliente: enlace host (re)estabelecido
    void peerDisconnected(PeerId p);
    void receive(PeerId from, const Bytes& data);        // um datagrama (quadro de enlace)
    // Entrega de aplicação pulando camada de enlace (reprodução e injeção). channel: 0 confiável, 1 não confiável.
    void receiveEnvelope(PeerId from, const Bytes& envelope, uint8_t channel);
    void tick(uint64_t nowMs);

    // ---- ações locais (todas passam por doAction) ----
    bool doAction(const Action& i);
    bool move(CellId cell, Vec3 pos, float yaw = 0);
    bool attackActor(NetId victim, int32_t damage, Limb limb = Limb::Torso, Vec3 impact = {}, float weaponRange = 1500);
    bool pickup(NetId item);
    bool drop(const Ref& base);
    bool openContainer(NetId c);
    bool closeContainer(NetId c);
    bool containerTake(NetId c, const Ref& base, int32_t n);
    bool containerPut(NetId c, const Ref& base, int32_t n);
    bool activate(NetId obj);
    bool useDoor(NetId obj);
    // ações de história só host (pelo caminho de efeitos)
    bool recruit(NetId actor, PlayerId owner);
    bool dismiss(NetId actor);
    bool setStage(const Ref& quest, uint32_t stage);
    bool setLock(NetId obj, bool locked, int32_t level);
    bool killByStory(NetId actor);
    bool commitEffects(const std::vector<Effect>& fx);

    // ---- salvar / carregar host ----
    Bytes hostSave() const;
    bool hostLoad(const Bytes& save);

    // ---- estado para testes e oráculos ----
    World& world() { return world_; }
    const World& world() const { return world_; }
    OwnershipView& view() { return view_; }
    const OwnershipView& view() const { return view_; }
    const OwnershipService* service() const { return svc_.get(); }
    OwnershipService* service() { return svc_.get(); }
    const MachineStats& stats() const { return stats_; }
    uint64_t healCount() const { return stats_.repairsSent + stats_.repairsApplied; }
    uint64_t digest(Category c) const { return world_.digest(c); }
    // Itens carregados pelo jogador desta máquina.
    int64_t inventoryCount(const Ref& base) const;
    std::map<Ref, int64_t> inventoryTotals() const;
    std::vector<NetId> ownedActors() const;           // atores que a visão diz pertencerem a esta máquina
    const std::vector<std::string>& repairLog() const { return repairLog_; }
    const std::vector<std::string>& rejectLog() const { return rejectLog_; }
    bool handingOff(NetId id) const { return handingOff_.count(id) != 0; }
    size_t outboxSize() const { return outbox_.size(); }
    size_t unackedCount() const { size_t n = 0; for (auto& kv : links_) n += kv.second.unacked.size(); return n; }
    void setAiFrozen(bool f) { aiFrozen_ = f; }   // atores mantêm controle de propriedade e estabilizam, mas sem decisões IA (quiescência)

private:
    struct Unacked { uint64_t seq; Bytes frame; uint64_t sentAt; };
    struct Link {
        uint32_t connEpoch = 0;
        uint64_t nextSend = 1, expect = 1;
        std::deque<Unacked> unacked;
        std::map<uint64_t, Bytes> ahead;
        bool ackDirty = false;
    };
    struct Wander { uint64_t nextMs = 0; float dx = 0, dy = 0; };
    struct Mismatch { uint64_t client = 0, host = 0; };

    // enlace
    void emitFrame(PeerId to, uint8_t type, uint64_t seq, const Bytes& payload, Channel ch);
    void sendPayload(PeerId to, const Bytes& payload, bool reliable);
    void onFrame(PeerId from, const Bytes& data);
    void flushAcks();
    // envelopes
    void sendBody(Body b, PlayerId dest);              // cliente: sempre pelo host; host: direto / distribuição
    void relay(const Envelope& e);                     // host: encaminhar broadcast cliente aos outros clientes
    void dispatch(PeerId from, const Envelope& e);
    bool toHost(const Envelope& e) const { return e.dest == kHostPlayer; }

    // tratadores
    void onFullState(const MFullState& m);
    bool onPose(const Envelope& e, const MPose& m);
    bool onVitals(const Envelope& e, const MVitals& m);
    bool onActorSnap(const Envelope& e, const MActorSnap& m);
    bool onActorEvent(const Envelope& e, const MActorEvent& m);
    void onHit(const Envelope& e, MHit h);
    void onOwn(const Envelope& e, const MOwn& m);
    void onEffects(const MEffects& m);
    void onDropReq(const Envelope& e, const MDropReq& m);
    void onItemCreated(const MItemCreated& m);
    void onPickup(const Envelope& e, const MPickup& m);
    void onItemTaken(const MItemTaken& m);
    void onContainerReq(const Envelope& e, const MContainerReq& m);
    void onContainerRes(const MContainerRes& m);
    void onContainerSync(const MContainerSync& m);
    void onSpawnRoll(const Envelope& e, const MSpawnRoll& m);
    void onSpawnActor(const MSpawnActor& m);
    void onSiteState(const MSiteState& m);
    void onActivate(const Envelope& e, const MActivate& m);
    void onDigest(const Envelope& e, const MDigest& m);
    void onRepair(const MRepair& m);

    // integração de propriedade
    void emitOwn(const std::vector<OwnMsg>& out);      // host: aplicar à própria visão, executar hooks, transmitir
    void onOwnApplied(const OwnMsg& m, ApplyResult r);
    std::vector<Presence> presenceFor(const ActorState& a) const;
    void evalOwnership();
    void maybeAck(NetId id);
    // simulação
    void aiStep(ActorState& a, uint32_t dtMs);
    void publishActor(ActorState& a, bool settle, bool final);
    void declareDeath(ActorState& a, const char* why);
    void applyDamage(ActorState& a, int32_t damage, Limb limb, bool fromHit);
    LootList rollLoot(Rng& r) const;
    void makeCorpse(ActorState& a, const LootList& loot);
    void applyHitToSelf(const Envelope& e, const MHit& h);
    bool validateHit(const MHit& h, const ActorState& victim, PlayerId from, std::string& why);
    // lógica do mundo host
    NetId hostSpawnAt(SpawnSiteState& site, PlayerId roller);
    void evalSites();
    void onActorDiedHost(NetId id);
    void pushRepair(PlayerId target, Category cat, const std::vector<uint32_t>& keys, const std::vector<uint32_t>& removes);
    MFullState buildFullState() const;
    void loadCellsFor(CellId cell);
    void publishPose(bool force);
    void refreshAi(NetId id);   // um ator: aiOn = pertence a nós e não estamos transferindo
    void refreshAiFlags();   // aiOn = pertence a nós e não estamos transferindo
    void sendHit(const MHit& h, PlayerId dest);
    bool applyOnce(uint64_t key);                      // false se `key` já aplicado (e falha de deduplicação desligada)
    uint64_t nextId() { return (static_cast<uint64_t>(cfg_.self) << 48) | (static_cast<uint64_t>(connEpoch_ & 0xFFFFu) << 32) | ++idCounter_; }
    uint32_t seqBase() const { return connEpoch_ * 100000u; }

    MachineConfig cfg_;
    Rng rng_;
    World world_;
    OwnershipView view_;
    std::unique_ptr<OwnershipService> svc_;   // só host
    IEngineObserver* obs_ = nullptr;
    MachineStats stats_;
    std::vector<Outgoing> outbox_;
    std::map<PeerId, Link> links_;
    bool synced_ = false;
    uint32_t sess_ = 1, connEpoch_ = 1;
    uint64_t now_ = 0, lastTick_ = ~0ull, idCounter_ = 0;
    bool poseDirty_ = true;
    bool aiFrozen_ = false;
    bool poseUnsettled_ = false;
    uint64_t lastPoseChangeMs_ = 0;
    std::map<NetId, OwnerEpoch> lastOwnedEpoch_;
    uint64_t nextPoseMs_ = 0, nextOwnEvalMs_ = 0, nextDigestMs_ = 0;
    uint32_t poseCounter_ = 0, vitalsCounter_ = 0;
    uint64_t fxSeq_ = 0, lastFxSeq_ = 0;
    std::vector<CellId> loaded_;
    std::set<uint64_t> applied_;                       // chaves de idempotência
    std::set<NetId> handingOff_;                       // atores que cedemos (IA parada, estado final enviado)
    std::set<NetId> acked_;
    std::vector<NetId> diedAfterRelay_, ackAfterRelay_;
    std::map<NetId, Wander> wander_;
    std::map<NetId, uint64_t> lastMoveMs_, lastPublishMs_, lastAttackMs_, settledAt_;
    std::map<PlayerId, std::deque<uint64_t>> hitTimes_;
    std::map<uint64_t, NetId> pendingClaims_;          // claimId -> item (coletas otimistas aguardando host)
    std::map<uint64_t, std::pair<Ref, int32_t>> pendingPuts_;
    std::map<std::pair<PlayerId, uint8_t>, Mismatch> mismatch_;   // host: última divergência não reparada por informante e categoria
    std::set<NetId> rolledSites_;                      // cliente: locais já informados no carregamento atual de célula
    std::set<uint64_t> dropOrigins_;
    std::vector<std::string> repairLog_, rejectLog_;
    uint32_t dropCounter_ = 0;
};

}  // namespace coop::fakeworld
