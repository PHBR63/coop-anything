// Gravador de voo cooperativo: rastreamento binário compacto de tudo que máquina enviou, recebeu, decidiu e aplicou.
// C++17 independente, sem código de jogo/motor. Formato: tools/flight/FORMAT.md (.cofr, versão 1).
//
// Buffer circular na memória. Gravado em .cofr na dessincronia, falha, encerramento ou dump explícito.
// Custo no caminho crítico: trava de mutex e memcpy do datagrama (até maxRawBytes); sem alocação ou decodificação.
// Decodificação (tipo de mensagem, sessão, época, faixa seq) ocorre no dump por decodificador opcional fornecido.
#pragma once
#include <atomic>
#include <cstdint>
#include <functional>
#include <mutex>
#include <string>
#include <unordered_map>
#include <utility>
#include <vector>
#include "observer.h"

namespace cofr {

using Bytes = std::vector<uint8_t>;

constexpr uint16_t kFormatVersion = 1;
constexpr size_t kHeaderSize = 64;
constexpr size_t kRecordHeaderSize = 16;
constexpr size_t kNetPrefix = 36;           // bytes de payload Net antes do datagrama bruto
constexpr size_t kMaxDigestKeys = 4000;     // por registro Digest; digestDetail() divide listas maiores em vários registros
constexpr size_t kDefaultBuckets = 256;     // digests por grupos: bucket = key mod número de grupos
constexpr uint64_t kHashSeed = 14695981039346656037ull;   // base de deslocamento FNV-1a 64

// SÓ TESTES: cada indicador reintroduz erro a ser detectado pelos testes do gravador (variantes mutantes).
struct Mutations {
    bool dropNewest = false;           // buffer circular cheio descarta NOVO registro em vez do mais antigo
    bool noNetIn = false;              // datagramas recebidos não gravados
    bool zeroSeq = false;              // campos decodificados session / epoch / seq deixados em zero
    bool noTruncFlag = false;          // datagrama cortado não sinalizado
    bool noDroppedCount = false;       // cabeçalho diz que nada foi descartado
    bool noAppliedFlags = false;       // indicadores de aplicação (reparo / referência / recuperação) sempre 0
    bool noDerivedDigest = false;      // digest de decodificador não gera registro Digest
    bool bucketsIgnoreValue = false;   // hashes de grupos cobrem só chaves: valor alterado invisível
    bool detailDropsKey = false;       // digestDetail perde última entrada
    bool incrementalSkipsUpdate = false;   // BucketedState::set esquece de remover valor antigo de chave substituída
    bool noSchemaRecord = false;       // dumps sem esquema
    bool customCutsPayload = false;    // registros personalizados perdem último byte
};
inline Mutations& mutations() { static Mutations m; return m; }

// Esquema é texto JSON do jogo: nomes de categorias digest, tipos de marcadores e mensagens, entre outros, e
// layout dos registros definidos pelo jogo. Veja seção 5 de FORMAT.md. schemaJson vazio significa exemplos padrão.
const char* defaultSchemaJson();

// Decodificador de datagramas, chamado no dump em cada datagrama gravado não cortado. Retorne false se bytes não forem
// mensagem do protocolo. Preencha só o que ele tem.
using NetDecoder = std::function<bool(const uint8_t* data, size_t size, NetMeta& out)>;

struct Config {
    size_t ringBytes = 16u << 20;     // registros mais antigos sobrescritos quando cheio
    size_t maxRawBytes = 48000;       // bytes de datagrama por registro Net (restante cortado e sinalizado)
    uint8_t slot = kNoSlot;
    uint8_t role = kRoleSim;
    uint32_t protoVersion = 0;        // versão do protocolo ou esquema, vai ao cabeçalho do arquivo
    std::string label = "cofr";       // vai ao registro Meta e nome do arquivo de dump
    std::string dir;                  // pasta padrão de dumpToDir()
    uint32_t autoDumpMinIntervalMs = 30000;   // onDesync() gera dumps no máximo com esta frequência ...
    uint32_t autoDumpMax = 8;                 // ... e no máximo esta quantidade de arquivos por execução
    std::string schemaJson;           // vazio: defaultSchemaJson()
    NetDecoder decoder;               // opcional
};

// ---- auxiliares de hash (mesmos algoritmos em tools/flight/cofr.py) ----

uint64_t hash64(const void* data, size_t size, uint64_t seed = kHashSeed);   // FNV-1a, 64 bits
uint32_t bucketMix(uint64_t key, uint32_t valueHash);                        // 32 bits baixos de mistura de 64 bits de (chave, hash do valor)

// Digest com hashes de grupos independentes da ordem sobre entradas (chave, hash do valor): bucket = key mod buckets, hash do grupo =
// soma (mod 2^32) de bucketMix das entradas, `hash` cobre grupos e contagem. Duas máquinas cujas
// listas de entradas diferem num valor têm exatamente um grupo divergente.
DigestEvent bucketedDigest(uint8_t category, uint32_t epoch, uint64_t seq, const std::vector<std::pair<uint64_t, uint32_t>>& entries,
                           size_t buckets = kDefaultBuckets);

// Mesmo digest atualizado uma entrada por vez; jogo que muda poucas por quadro não percorre todo estado.
class BucketedState {
public:
    explicit BucketedState(size_t buckets = kDefaultBuckets) : sums_(buckets ? buckets : 1, 0) {}
    void set(uint64_t key, uint32_t valueHash);   // inserir ou substituir
    bool erase(uint64_t key);
    size_t size() const { return map_.size(); }
    DigestEvent digest(uint8_t category, uint32_t epoch, uint64_t seq) const;   // custa percurso dos grupos, não entradas
    std::vector<std::pair<uint64_t, uint32_t>> entries() const;
private:
    std::unordered_map<uint64_t, uint32_t> map_;
    std::vector<uint32_t> sums_;
};

// ---- gravador ----

class Recorder : public IObserver {
public:
    explicit Recorder(Config cfg = Config());

    // relógio e quadro: reais por padrão; simulador injeta relógio virtual
    void setClockSource(std::function<uint64_t()> nowUs);    // microssegundos, monotônico; tempo gravador = valor - valor nesta chamada
    void setFrame(uint32_t frame) override { frame_.store(frame, std::memory_order_relaxed); }
    uint32_t frame() const { return frame_.load(std::memory_order_relaxed); }
    void setIdentity(uint8_t slot, uint8_t role);
    void setSession(uint32_t session, uint32_t epoch);       // para cabeçalho do arquivo
    void setWallStart(uint64_t unixMs) { wallStartMs_ = unixMs; }   // testes: torna arquivo determinístico
    void setEnabled(bool on) { enabled_.store(on, std::memory_order_relaxed); }
    bool enabled() const { return enabled_.load(std::memory_order_relaxed); }

    // Metadados escritos no registro Meta do próximo dump.
    void meta(const std::string& key, const std::string& value);
    // Informe ao analisador slot de máquina correspondente a id de par de transporte nesta máquina (Meta "peer.<id>").
    void mapPeer(uint32_t peerId, uint8_t slot) { meta("peer." + std::to_string(peerId), std::to_string(slot)); }

    // gravação (IObserver)
    void netOut(uint32_t to, const uint8_t* data, size_t size, uint8_t channel = 0) override;
    void netIn(uint32_t from, const uint8_t* data, size_t size) override;
    void netOut(uint32_t to, const Bytes& data, uint8_t channel = 0) { netOut(to, data.data(), data.size(), channel); }
    void netIn(uint32_t from, const Bytes& data) { netIn(from, data.data(), data.size()); }
    void captured(const CapturedEvent& e) override;
    void applied(const AppliedEvent& e) override;
    void ownership(const OwnershipEvent& e) override;
    void digest(const DigestEvent& d, uint8_t flags = 0) override;
    void marker(uint16_t kind, const std::string& text) override;
    void custom(uint8_t type, const uint8_t* payload, size_t size) override;
    void custom(uint8_t type, const Bytes& payload) { custom(type, payload.data(), payload.size()); }

    // Cada entrada do estado que originou digest, como registros Digest marcados kFlagDetail (mesmos category, epoch, seq).
    void digestDetail(uint8_t category, uint32_t epoch, uint64_t seq, const std::vector<std::pair<uint64_t, uint32_t>>& entries);
    // Linha legível por entrada, exibida pelo analisador junto dos hashes: "entry <key as 16 hex digits> <value hash> <text>".
    void entryText(uint64_t key, uint32_t valueHash, const std::string& text);

    // despejo
    // Grava buffer circular em `path`. Retorna false em falha de E/S. Nunca lança exceção.
    bool dump(const std::string& path, uint8_t reason = kDumpManual);
    // Grava <cfg.dir>/<label>-<reason>-<unixms>-<n>.cofr; retorna caminho ou "" na falha (ou dir vazio).
    std::string dumpToDir(uint8_t reason = kDumpManual);
    // Dessincronia detectada: marca buffer e, com diretório configurado, gera dump (taxa limitada). Retorna caminho ou "".
    std::string onDesync(const std::string& what);
    // Caminho de falha: não espera trava se outra thread a possui. Melhor esforço.
    std::string dumpCrash();

    struct Stats {
        uint64_t records = 0, dropped = 0, bytesRing = 0, dumps = 0, dumpFailures = 0, autoDumpsSkipped = 0;
    };
    Stats stats() const;
    const Config& config() const { return cfg_; }

private:
    void push(uint8_t type, uint8_t flags, const uint8_t* a, size_t an, const uint8_t* b = nullptr, size_t bn = 0);
    uint64_t nowUs() const;
    bool dumpImpl(const std::string& path, uint8_t reason, bool lock);

    Config cfg_;
    std::function<uint64_t()> clock_;
    uint64_t clock0_ = 0;
    uint64_t wallStartMs_ = 0;
    std::atomic<uint32_t> frame_{0};
    std::atomic<bool> enabled_{true};
    uint32_t session_ = 0, epoch_ = 0;
    std::vector<std::pair<std::string, std::string>> meta_;

    mutable std::mutex mu_;
    std::vector<uint8_t> ring_;
    size_t head_ = 0, used_ = 0;          // offset da entrada mais antiga, bytes em uso
    uint64_t count_ = 0, dropped_ = 0, dumps_ = 0, dumpFailures_ = 0, autoSkipped_ = 0;
    uint64_t lastAutoDumpMs_ = 0;
    uint32_t autoDumps_ = 0;
    std::atomic<uint32_t> fileSeq_{0};
};

// ---- leitor (testes e ferramentas próprias; leitor Python em tools/flight/cofr.py) ----

struct TraceHeader {
    uint16_t version = 0, headerSize = 0;
    uint8_t slot = 0, role = 0, reason = 0;
    uint32_t protoVersion = 0;
    uint64_t wallStartMs = 0, dumpTUs = 0, dropped = 0, recordCount = 0;
    uint32_t sessionId = 0, epoch = 0;
};
struct TraceRecord {
    uint8_t type = 0, flags = 0;
    uint32_t frame = 0;
    uint64_t tUs = 0;
    std::vector<uint8_t> payload;
};
struct Trace {
    TraceHeader header;
    std::vector<TraceRecord> records;
    std::string schemaJson;                     // texto do registro Schema, vazio se arquivo não tiver
};
bool readTrace(const std::string& path, Trace& out, std::string* err = nullptr);
bool parseTrace(const std::vector<uint8_t>& bytes, Trace& out, std::string* err = nullptr);

struct NetInfo {
    uint32_t peer = 0; uint8_t channel = 0, mux = 0, msgType = 0, decode = 0;   // decode: 0 decodificado, 1 decodificador recusou ou datagrama cortado, 2 sem decodificador
    uint32_t session = 0, epoch = 0; uint64_t seqLo = 0, seqHi = 0; uint32_t rawLen = 0;
    std::vector<uint8_t> raw;
};
bool parseNet(const TraceRecord& r, NetInfo& out);
bool parseDigest(const TraceRecord& r, DigestEvent& out);
bool parseOwnership(const TraceRecord& r, OwnershipEvent& out);
bool parseCaptured(const TraceRecord& r, CapturedEvent& out);
bool parseApplied(const TraceRecord& r, AppliedEvent& out);

}  // namespace cofr
