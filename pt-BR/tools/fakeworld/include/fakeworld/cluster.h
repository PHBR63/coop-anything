// Cluster: N máquinas em uma InMemoryNetwork (simulador de enlace com perdas), relógio virtual, entrada / saída / salvar-carregar do host,
// os oráculos de invariantes e reprodução sem jogo de execução gravada. Um fuzzer pode usar diretamente ou conectar
// as próprias Machines.
#pragma once
#include <map>
#include <memory>
#include <string>
#include <vector>
#include "fakeworld/machine.h"
#include "fakeworld/net.h"

namespace coop::fakeworld {

// Uma entrada recebida por uma máquina. A lista delas (mais configuração e semente) reproduz exatamente uma execução.
struct TraceEvent {
    enum Kind : uint8_t { Tick = 0, Action = 1, Msg = 2, PeerUp = 3, PeerDown = 4, HostLoad = 5 };
    uint64_t tMs = 0;
    Kind kind = Tick;
    PlayerId machine = 0;     // máquina em que o evento ocorre
    PlayerId from = 0;        // Msg / PeerUp / PeerDown: a outra ponta
    uint8_t channel = 0;      // Msg
    uint32_t connEpoch = 0;   // PeerUp
    Bytes data;               // Msg: envelope codificado; Action: Action codificada; HostLoad: bytes do save
};

// Observador que captura fluxo de entrada reproduzível (nível de aplicação, após camada de enlace).
class TraceCapture : public IEngineObserver {
public:
    std::vector<TraceEvent> events;
    void onRecv(PlayerId self, uint64_t now, PeerId from, uint8_t channel, const Bytes& env) override;
    void onAction(PlayerId self, uint64_t now, const Action& i) override;
    void note(const TraceEvent& e) { events.push_back(e); }
};

struct ClusterConfig {
    uint64_t seed = 1;
    int players = 2;                 // 1..4 (slot 0 é o host)
    uint32_t tickMs = 10;
    LinkParams link;                 // aplica-se a todas as direções
    MachineConfig machine;           // modelo; self e seed preenchidos por máquina
};

struct Violation { uint64_t tMs = 0; std::string what; };

class Cluster {
public:
    explicit Cluster(const ClusterConfig& cfg, TraceCapture* capture = nullptr);
    ~Cluster();

    uint64_t now() const { return now_; }
    int players() const { return cfg_.players; }
    bool connected(PlayerId p) const { return p < machines_.size() && machines_[p] != nullptr; }
    Machine& machine(PlayerId p) { return *machines_.at(p); }
    const Machine& machine(PlayerId p) const { return *machines_.at(p); }
    Machine& host() { return *machines_.at(0); }
    InMemoryNetwork& net() { return net_; }
    const ClusterConfig& config() const { return cfg_; }

    void join(PlayerId p);       // máquina nova (reinício perde todo estado do cliente), estado completo chega pelo enlace
    void leave(PlayerId p);
    size_t saveHost();           // retorna identificador para loadHost
    bool loadHost(size_t handle);

    void step();                 // um tick para tudo
    void run(uint32_t ms);
    // Executa até nada estar em trânsito e nenhum ator se mover por um tempo, ou decorrer maxMs. True quando em repouso.
    bool quiesce(uint32_t maxMs = 20000);

    // Observador em todas as máquinas (inclusive tardias). O cluster mantém seu observador de oráculo encadeado à frente.
    void setObserver(IEngineObserver* o);
    void setCapture(TraceCapture* c);   // registra o fluxo de entrada reproduzível (ticks, entradas, intenções, mensagens)
    // Injeta envelope de aplicação como se `from` o tivesse enviado (injeção de eco obsoleto, reprodução de mensagens antigas).
    void inject(PlayerId to, PlayerId from, const Bytes& envelope, uint8_t channel = 0);

    // ---- oráculos ----
    // Verificações sempre válidas (seguras durante execução): um responsável por época, um condutor de IA por ator, nada obsoleto aceito,
    // nada aplicado duas vezes, nenhum ator/item duplicado. Retorna novas violações desde a última chamada.
    std::vector<Violation> checkAlways();
    // Válido após quiesce(): toda máquina igual ao host (resumos, estado exato de atores, tabela de responsabilidade),
    // conservação e nenhum reparo desde `repairBaseline`.
    std::vector<Violation> checkQuiescent();
    uint64_t totalRepairs() const;
    uint64_t totalDoubleApplied() const;
    const std::vector<Violation>& allViolations() const { return violations_; }
    std::map<Ref, int64_t> itemCensus() const;   // chão + contêineres (host) + inventário de cada jogador presente
    int64_t baselineItems(const Ref& base) const;
    uint64_t repairBaseline = 0;
    bool checkConservation = true;   // desativado após carga do host (clientes mantêm inventários; só save do host é o mundo)
    void freezeAi(bool f);           // para decisões de NPCs em toda máquina (quiesce() congela e mantém congelado)

private:
    class Oracle;
    void spawnMachine(PlayerId p);
    void pump();
    void deliverAll();

    ClusterConfig cfg_;
    InMemoryNetwork net_;
    std::vector<std::unique_ptr<Machine>> machines_;
    std::vector<Bytes> saves_;
    uint64_t now_ = 0;
    uint32_t connCounter_ = 1;
    IEngineObserver* user_ = nullptr;
    std::unique_ptr<Oracle> oracle_;
    std::vector<Violation> violations_;
    size_t reported_ = 0;
    std::map<Ref, int64_t> baseline_;
    uint64_t lastBusyMs_ = 0;
};

// Reproduz fluxo de eventos capturado em máquinas novas (sem rede). Usado por redutores e testes de regressão.
struct ReplayResult {
    std::vector<uint64_t> digests;   // por máquina, por categoria (máquina primeiro): 4 valores cada, 0 para máquinas ausentes
    std::vector<std::string> violations;
    uint64_t events = 0;
};
ReplayResult replay(const ClusterConfig& cfg, const std::vector<TraceEvent>& events);

}  // namespace coop::fakeworld
