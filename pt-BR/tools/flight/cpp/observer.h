// Interface de observação do gravador de voo cooperativo.
//
// Único cabeçalho exigido pelos hooks do jogo. Sem dependências além da biblioteca padrão.
// Hooks relatam o ocorrido a IObserver*; gravador (cofr.h) é uma implementação,
// e ponteiro nulo ou classe base inoperante são outros; compilação de distribuição pode dispensar gravador.
//
// Formato: tools/flight/FORMAT.md (registro de voo cooperativo, .cofr, versão 1).
#pragma once
#include <cstddef>
#include <cstdint>
#include <string>
#include <utility>
#include <vector>

namespace cofr {

// ---- constantes compartilhadas com formato de arquivo ----

enum RecType : uint8_t {
    kMeta = 1, kNetOut = 2, kNetIn = 3, kTxnCaptured = 4, kTxnApplied = 5, kOwnership = 6, kDigest = 7, kMarker = 8,
    kSchema = 9,
    kFirstCustom = 32,   // 32..255: tipos de registro definidos pelo jogo, descritos pelo esquema
};
enum RecFlag : uint8_t {
    kFlagTruncated = 1,   // Net: datagrama cortado em maxRawBytes
    kFlagDerived = 2,     // Digest: construído de mensagem recebida, não estado local
    kFlagDetail = 4,      // Digest: leva só entradas por chave (chave, hash do valor)
    kFlagBucketed = 8,    // Digest: fragmentos são grupos de chaves (grupo = chave módulo número de fragmentos)
};
enum DumpReason : uint8_t { kDumpManual = 0, kDumpDesync = 1, kDumpCrash = 2, kDumpShutdown = 3, kDumpTest = 4 };
enum Role : uint8_t { kRoleHost = 0, kRoleClient = 1, kRoleSim = 2 };
enum OwnershipOp : uint8_t { kOwnGrant = 0, kOwnTransfer = 1, kOwnRelease = 2, kOwnRejectStale = 3, kOwnRejectEcho = 4, kOwnRejectNonOwner = 5 };
enum MarkerKind : uint16_t { kMarkNote = 0, kMarkDesync = 1, kMarkJoin = 2, kMarkLeave = 3, kMarkTestStep = 4, kMarkSave = 5, kMarkLoad = 6, kMarkRebase = 7 };
enum ApplyFlag : uint8_t { kApplySnapshot = 1, kApplyRepair = 2, kApplyBaseline = 4, kApplyCatchUp = 8 };
constexpr uint8_t kNoSlot = 0xFF;

// ---- eventos ----

// Digest: hash de parte do estado compartilhado ("category" é número nomeado pelo seu esquema).
struct DigestEvent {
    uint8_t category = 0;
    uint32_t epoch = 0;
    uint64_t seq = 0;
    uint64_t hash = 0;
    uint32_t itemCount = 0;
    bool bucketed = false;                               // fragmentos são grupos de chaves (veja bucketedDigest)
    std::vector<uint32_t> shards;                        // opcional
    std::vector<std::pair<uint64_t, uint32_t>> keys;     // detalhe opcional por chave (no máximo kMaxDigestKeys mantidas por registro)
};

// O que um decodificador do jogo pode informar ao gravador sobre um datagrama (preenchido no dump, nunca no caminho crítico).
struct NetMeta {
    uint8_t msgType = 0;
    uint32_t session = 0, epoch = 0;
    uint64_t seqLo = 0, seqHi = 0;       // intervalo de números de transação levado pelo datagrama
    bool hasDigest = false;              // datagrama leva digest do estado do remetente: gravador inclui registro Digest "derivado"
    DigestEvent digest;
};

// Conjunto de alterações decidido pela máquina local (kind 0, commit host) ou solicitado (kind 1, intenção cliente).
struct CapturedEvent {
    uint8_t kind = 0;
    uint32_t intentId = 0;
    uint64_t seq = 0;            // 0 para intenção ainda sem número
    uint32_t effectCount = 0;
    uint64_t hash = 0;           // hash dos hashes de efeitos, calculado pelo jogo
    uint8_t cause = 0;
    uint32_t epoch = 0;
};

// Um efeito aplicado ao mundo local. (seq, index) identifica efeito; seu hash deve ser igual em todas as máquinas.
struct AppliedEvent {
    uint64_t seq = 0;
    uint32_t epoch = 0;
    uint8_t origin = 0;
    uint32_t index = 0;
    uint8_t flags = 0;           // Bits ApplyFlag; aplicações de snapshot, reparo e referência reafirmam estado, não repetem transação
    uint8_t cause = 0;
    uint8_t effectTag = 0;       // tipo de efeito (definido pelo jogo)
    uint64_t hash = 0;
};

struct OwnershipEvent {
    uint8_t op = kOwnGrant;
    uint64_t actor = 0;
    uint32_t epoch = 0;
    uint8_t fromOwner = kNoSlot, toOwner = kNoSlot;
    uint8_t reason = 0;
    uint64_t txnId = 0;
};

// ---- observador ----

// Todos métodos inoperantes por padrão; próprio `IObserver` é observador nulo.
class IObserver {
public:
    virtual ~IObserver() = default;
    virtual void setFrame(uint32_t /*frame*/) {}
    virtual void netOut(uint32_t /*to*/, const uint8_t* /*data*/, size_t /*size*/, uint8_t /*channel*/ = 0) {}
    virtual void netIn(uint32_t /*from*/, const uint8_t* /*data*/, size_t /*size*/) {}
    virtual void captured(const CapturedEvent&) {}
    virtual void applied(const AppliedEvent&) {}
    virtual void ownership(const OwnershipEvent&) {}
    virtual void digest(const DigestEvent&, uint8_t /*flags*/ = 0) {}
    virtual void marker(uint16_t /*kind*/, const std::string& /*text*/) {}
    // Registro definido pelo jogo. `type` é 32..255 e deve estar no esquema para analisador decodificá-lo.
    virtual void custom(uint8_t /*type*/, const uint8_t* /*payload*/, size_t /*size*/) {}
};

}  // namespace cofr
