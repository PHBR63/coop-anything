// Propriedade de atores com épocas. C++17 puro, sem dependências, rede ou relógio.
//
// Regra: cada ator ativo simulado por exatamente uma máquina, seu PROPRIETÁRIO. Propriedade tem ÉPOCA que aumenta a
// cada mudança. Só proprietário na época atual pode publicar movimento, atributos, morte ou inventário do ator.
//
//   OwnershipService  lado host. Decide quem possui o quê (mais próximo, preferência host, histerese, exceção
//                     para seguidores) e emite OwnMsg para transmissão. Tempo recebido, nunca lido.
//   OwnershipView     cada máquina (também host). Aplica OwnMsg e julga atualizações de atores recebidas (aceitar ou
//                     rejeitar com motivo). Ordem das épocas torna toda mensagem idempotente e independente da ordem.
//
// Transferência é handshake, sem perder estado ou duplicar IA:
//   Transfer(e+1, to) -> proprietário anterior segue publicando na época e -> novo aplica último estado e envia Ack
//   -> host envia Commit(e+1) -> novo proprietário inicia IA e publica em e+1; anterior para.
// Sem Ack a tempo, host confirma mesmo assim (novo proprietário ainda conectado) ou concede
// ator de volta ao proprietário anterior.
//
// Limites: até 8 slots (kMaxSlots), 0 é host. Não seguro entre threads: use uma instância por thread.
#pragma once
#include <cstddef>
#include <cstdint>
#include <map>
#include <vector>
#include "coop/types.h"

namespace coop {

using ActorNetId = uint32_t;
using OwnerEpoch = uint32_t;

struct OwnMsg {
    enum Kind : uint8_t {
        Grant = 1,     // ator pertence a `owner` em `epoch` (sem proprietário -> com, ou transferência abortada)
        Transfer = 2,  // iniciar transferência prevOwner -> owner; só efetiva (epoch) no Commit
        Ack = 3,       // novo proprietário -> host: último estado aplicado, pronto para assumir (leva época do Transfer)
        Commit = 4,    // host -> todos: transferência concluída, `owner` tem autoridade em `epoch`
        Release = 5,   // ator sem proprietário em `epoch` (célula descarregada para todos, proprietário saiu)
    };
    Kind kind = Grant;
    ActorNetId netId = 0;
    OwnerEpoch epoch = 0;
    PlayerId owner = kNoPlayer;
    PlayerId prevOwner = kNoPlayer;
    friend bool operator==(const OwnMsg& a, const OwnMsg& b) {
        return a.kind == b.kind && a.netId == b.netId && a.epoch == b.epoch && a.owner == b.owner && a.prevOwner == b.prevOwner;
    }
};
const char* toString(OwnMsg::Kind k);

// Formato de rede compacto opcional (varints LEB128). Use-o ou crie próprio: biblioteca nunca toca numa rede.
void encode(const OwnMsg& m, std::vector<uint8_t>& out);              // acrescenta a `out`
bool decode(const uint8_t* data, size_t size, OwnMsg& out);           // false para entrada malformada ou truncada

// O que host sabe sobre um jogador em relação a um ator, na avaliação.
struct Presence {
    PlayerId player = kNoPlayer;
    bool connected = true;
    bool inCell = false;     // jogador carregado na célula do ator
    bool adjacent = false;   // jogador numa célula vizinha carregada
    float distance = 0;      // até ator (qualquer unidade, só comparação)
    bool eligible() const { return connected && (inCell || adjacent); }
};

struct OwnershipConfig {
    uint32_t minHoldMs = 1500;         // após mudança, proprietário mantido este tempo salvo tornar-se inelegível
    double switchMargin = 0.25;        // desafiante precisa estar esta fração mais perto que atual proprietário
    uint32_t handoffTimeoutMs = 1000;  // espera por Ack antes de host forçar resultado
};

// Opções de falha SÓ TESTES (variantes mutantes). Cada uma recria erro conhecido para teste provar que o teria
// detectado. Todas false em produção. Globais ao processo: defina só em OwnershipFaultScope.
struct OwnershipFaults {
    bool noEpochBump = false;       // mudanças mantêm época antiga: proprietários antigos/novos indistinguíveis
    bool acceptStaleEpoch = false;  // visões aplicam mensagens antigas e aceitam atualizações de época anterior (erro de eco antigo)
    bool adoptEcho = false;         // visão deixa atribuição antiga reproduzida sobrescrever nova
    bool transferNoAck = false;     // transferência confirma imediatamente: último estado do proprietário anterior perdido
    bool noHysteresis = false;      // propriedade oscila com distância
    bool followerIgnored = false;   // companheiros pertencem a quem está mais perto
    bool acceptNonOwner = false;    // visões aceitam atualizações de qualquer jogador
};
inline OwnershipFaults& ownershipFaults() { static OwnershipFaults f; return f; }
struct OwnershipFaultScope {
    OwnershipFaults saved;
    explicit OwnershipFaultScope(const OwnershipFaults& f) : saved(ownershipFaults()) { ownershipFaults() = f; }
    ~OwnershipFaultScope() { ownershipFaults() = saved; }
};

struct OwnershipStats {
    uint64_t grants = 0, transfers = 0, commits = 0, releases = 0, forcedCommits = 0, abortedHandoffs = 0;
};

// Regra pura de escolha (exposta para testes). `current` é kNoPlayer se sem proprietário; `held` é true enquanto
// minHoldMs desde última mudança AINDA NÃO passou. Retorna proprietário a usar (kNoPlayer = ninguém).
PlayerId pickOwner(const std::vector<Presence>& who, PlayerId current, bool held, const OwnershipConfig& cfg);

class OwnershipService {
public:
    using Out = std::vector<OwnMsg>;
    explicit OwnershipService(OwnershipConfig cfg = {}) : cfg_(cfg) {}

    void playerJoined(PlayerId p);
    // Marca jogador ausente. Atores dele liberados (mensagens Release acrescentadas) e retornados para chamador
    // poder usar evaluate() novamente; transferência a ele abortada; vínculos de recrutador para ele limpos.
    std::vector<ActorNetId> playerLeft(PlayerId p, uint32_t nowMs, Out& out);

    // Começa a acompanhar ator e escolhe primeiro proprietário (Grant acrescentado se alguém elegível).
    void track(ActorNetId id, const std::vector<Presence>& who, uint32_t nowMs, Out& out);
    void untrack(ActorNetId id, Out& out);   // Release acrescentado se tinha proprietário

    // Redecide ator com dados de presença novos. Idempotente: sem mudança -> nada acrescentado.
    void evaluate(ActorNetId id, const std::vector<Presence>& who, uint32_t nowMs, Out& out);

    // Exceção para seguidor: companheiro pertence a seu recrutador onde for (kNoPlayer limpa).
    void setRecruiter(ActorNetId id, PlayerId recruiter, const std::vector<Presence>& who, uint32_t nowMs, Out& out);

    // Ack cliente para Transfer pendente. Confirmações antigas ou desconhecidas ignoradas (retorna false).
    bool onAck(const OwnMsg& ack, PlayerId from, uint32_t nowMs, Out& out);
    // Controla timeouts de transferência. Chame uma vez por tick host.
    void tick(uint32_t nowMs, Out& out);

    // Atribuição atual como mensagens Grant (entrada / retorno / ressincronização). Transferências pendentes informam anterior.
    void snapshot(Out& out) const;
    // Igual, para exatamente um ator (responde a cliente reclamando de época antiga).
    bool current(ActorNetId id, OwnMsg& out) const;

    PlayerId ownerOf(ActorNetId id) const;
    OwnerEpoch epochOf(ActorNetId id) const;
    bool handoffPending(ActorNetId id) const;
    size_t actorCount() const { return actors_.size(); }
    template <class F> void forEach(F&& f) const { for (auto& kv : actors_) f(kv.first, kv.second.owner, kv.second.epoch); }
    const OwnershipStats& stats() const { return stats_; }
    const OwnershipConfig& config() const { return cfg_; }

private:
    struct Rec {
        PlayerId owner = kNoPlayer;
        OwnerEpoch epoch = 0;
        uint32_t changedAtMs = 0;
        PlayerId recruiter = kNoPlayer;
        // transferência pendente
        bool pending = false;
        PlayerId to = kNoPlayer;
        OwnerEpoch pendingEpoch = 0;
        uint32_t pendingSinceMs = 0;
    };
    OwnerEpoch bump(const Rec& r) const;
    void grant(ActorNetId id, Rec& r, PlayerId owner, uint32_t nowMs, Out& out);
    void beginTransfer(ActorNetId id, Rec& r, PlayerId to, uint32_t nowMs, Out& out);
    void commit(ActorNetId id, Rec& r, uint32_t nowMs, bool forced, Out& out);
    void release(ActorNetId id, Rec& r, uint32_t nowMs, Out& out);
    bool isConnected(PlayerId p) const { return p < kMaxSlots && ((connected_ >> p) & 1u); }

    OwnershipConfig cfg_;
    OwnershipStats stats_;
    uint8_t connected_ = 0;
    std::map<ActorNetId, Rec> actors_;
};

enum class ApplyResult : uint8_t { Applied, Duplicate, Stale };
enum class UpdateVerdict : uint8_t {
    Accept,
    NotOwner,       // remetente não é proprietário conhecido
    StaleEpoch,     // remetente usou época anterior à nossa (antigo proprietário ainda transmitindo)
    FutureEpoch,    // remetente alega época ainda não vista (visão atrasada: consultar host)
    NotYetActive,   // remetente é novo proprietário pendente, transferência não confirmada
    EchoOfSelf,     // atualização veio de nós (nossa própria publicação refletida)
    UnknownActor,
};
const char* toString(UpdateVerdict v);
const char* toString(ApplyResult v);

struct ViewStats {
    uint64_t applied = 0, duplicates = 0, staleMsgs = 0;
    uint64_t accepted = 0, notOwner = 0, staleEpoch = 0, futureEpoch = 0, notYetActive = 0, echoes = 0, unknown = 0;
};

class OwnershipView {
public:
    explicit OwnershipView(PlayerId self = kNoPlayer) : self_(self) {}
    void setSelf(PlayerId p) { self_ = p; }
    PlayerId self() const { return self_; }

    ApplyResult apply(const OwnMsg& m);
    UpdateVerdict check(ActorNetId id, PlayerId from, OwnerEpoch epoch);   // contado nas estatísticas
    // Época a marcar numa atualização publicada para `id`, ou false se não podemos publicar.
    bool mayPublish(ActorNetId id, OwnerEpoch& epochOut) const;
    // True enquanto somos NOVO proprietário de transferência ainda não confirmada (aplique estado, depois Ack).
    bool handoffIncoming(ActorNetId id, OwnerEpoch& epochOut) const;

    PlayerId ownerOf(ActorNetId id) const;
    OwnerEpoch epochOf(ActorNetId id) const;
    bool known(ActorNetId id) const { return actors_.count(id) != 0; }
    void forget(ActorNetId id) { actors_.erase(id); }
    void clear() { actors_.clear(); }
    template <class F> void forEach(F&& f) const { for (auto& kv : actors_) f(kv.first, kv.second.owner, kv.second.epoch); }
    const ViewStats& stats() const { return stats_; }
    uint64_t digest() const;   // hash de (id, owner, epoch) das atribuições confirmadas; visões iguais dão digests iguais

private:
    struct Rec {
        PlayerId owner = kNoPlayer;
        OwnerEpoch epoch = 0;
        bool pending = false;
        PlayerId to = kNoPlayer;
        OwnerEpoch pendingEpoch = 0;
    };
    PlayerId self_;
    ViewStats stats_;
    std::map<ActorNetId, Rec> actors_;
};

}  // namespace coop
