// coopfuzz: fuzzer de sessões cooperativas com semente e oráculos de invariantes.
//
// O fuzzer cria uma sessão aleatória de N jogadores (lista de operações temporizadas), aciona seu núcleo de sincronização pela
// interface ITarget, restaura a rede, espera a inatividade e pergunta aos oráculos se todas as máquinas terminaram no mesmo
// mundo e se o log de aplicação mostra comportamento proibido. Quando algo falha, reduz a sessão a um
// cenário pequeno e reproduzível e grava um relatório JSON.
//
// Você implementa ITarget (veja GUIDE.md). example/example_target.cpp é um exemplo completo, independente de jogo.
#pragma once
#include <cstdint>
#include <functional>
#include <map>
#include <memory>
#include <string>
#include <vector>
#include "coopfuzz/net.h"

namespace coopfuzz {

// ------------------------------------------------------------------ cenário
// O vocabulário genérico do que um jogador pode fazer. Um alvo mapeia cada operação para o que seu jogo oferece e pode ignorar operações que
// não consegue expressar (por exemplo, um jogo sem portas ignora Activate).
enum class OpKind : uint8_t { Move, Hit, Pickup, Drop, Spawn, Activate, Join, Leave, Save, Load, SetLink, Stale, Count };
const char* opName(OpKind k);
bool opFromName(const std::string& s, OpKind& out);

// Cada operação contém seu próprio horário absoluto e pequenos inteiros explícitos. Referências são números de slots que o alvo mapeia para
// o que existir naquele momento (módulo), portanto remover outras operações na redução nunca invalida uma operação.
//   Move      m, a=x(0..1000) b=y(0..1000) c=cell(0..2)
//   Hit       m, a=slot da vítima (módulo atores vivos), b=dano
//   Pickup    m, a=slot do item (módulo itens no chão)
//   Drop      m, a=slot do item carregado, b=x c=y d=célula
//   Spawn     m, a=local (0..4): encontro que deve ser criado uma vez na sessão inteira
//   Activate  m, a=slot da porta
//   Join/Leave  m (máquina 0, o anfitrião, nunca sai)
//   Save/Load   ponto de save do anfitrião / carregar o save mais recente
//   SetLink   a=minLatencyMs b=maxLatencyMs c=perda por mil d=duplicação por mil
//   Stale     m=receptor, a=remetente, b=qual mensagem gravada, c=0 reproduzir conteúdo antigo (pacote novo) / 1 duplicata bruta
struct Op {
    uint32_t t = 0;
    OpKind kind = OpKind::Move;
    int m = 0, a = 0, b = 0, c = 0, d = 0;
};

struct Scenario {
    uint64_t seed = 1;
    int machines = 3;                 // 2..4, máquina 0 é o anfitrião
    uint32_t durationMs = 20000;      // duração da fase de caos (tempo virtual)
    LinkParams link;                  // conexão inicial com caos
    std::vector<std::string> bugs;    // classes de erros injetadas (gêmeos mutantes); vazio = sem erros
    std::string profile;              // nome de predefinição de conexão (veja linkProfileNames); vazio = usar `link` e operações SetLink
    std::string target;               // alvo para o qual o cenário foi criado; vazio = alvo padrão
    std::string expect;               // preparações de regressão: a invariante que deve falhar enquanto o erro estiver injetado
    std::vector<Op> ops;              // ordenado por t
};

Scenario generate(uint64_t seed, int machines, uint32_t durationMs);
std::string toJson(const Scenario& s);
bool fromJson(const std::string& text, Scenario& out, std::string* err = nullptr);

// ------------------------------------------------------------------ observações (o que os oráculos leem)
enum class ApplyKind : uint8_t { Pos, PlayerPos, Hp, Owner, Holder, Door, Spawn, Remove, Reset, Intent };
const char* applyKindName(ApplyKind k);

// Uma chamada por mensagem aplicada ou rejeitada por uma máquina.
struct ApplyEvent {
    int machine = 0;
    uint64_t tMs = 0;
    uint64_t ord = 0;         // ordem global de ocorrência, compartilhada com OwnEvent
    uint64_t idem = 0;        // identidade da mensagem aplicada; o mesmo ID aceito duas vezes numa máquina = aplicado duas vezes
    int ref = -1;             // ID de rede do elemento, ou -1
    uint32_t epoch = 0;       // época de autoridade contida na mensagem (0 = não se aplica)
    uint32_t seq = 0;         // sequência dentro de (ref, epoch) para fluxos ordenados (0 = não se aplica)
    int origin = -1;          // máquina que produziu o conteúdo
    ApplyKind kind = ApplyKind::Pos;
    bool accepted = true;
    uint32_t worldEpoch = 0;  // época do mundo (salvar/carregar) na qual a mensagem foi criada
    std::string why;          // motivo da rejeição ou nota
};

// Uma chamada por decisão de autoridade feita por quem a distribui (normalmente o anfitrião).
struct OwnEvent {
    uint64_t tMs = 0;
    uint64_t ord = 0;
    enum Kind : uint8_t { Grant, Transfer, Release, WorldEpoch } kind = Grant;
    int ref = -1;
    int owner = -1;           // novo proprietário (-1 na liberação)
    int prevOwner = -1;
    uint32_t epoch = 0;       // época da autoridade (WorldEpoch: a nova época do mundo)
};

// Um ator, item, jogador ou porta como visto por uma máquina.
struct Thing {
    uint32_t netId = 0;
    uint8_t type = 0;         // 0 jogador 1 ator 2 item 3 porta
    uint32_t ident = 0;       // identidade independente de netId (slot de ponto de criação / item original); 0 = nenhuma
    int x = 0, y = 0, cell = 0, hp = 0;
    bool dead = false;
    int owner = -1;
    uint32_t epoch = 0;
    int holder = -1;          // itens: máquina que o carrega, -1 no chão
    bool open = false;
    bool operator==(const Thing& o) const;
    std::string str() const;
};

struct Violation {
    std::string invariant;   // converge, double_apply, multi_owner, dup_thing, stale_applied, echo_adopted, repairs_after_quiescence, not_quiescent
    std::string detail;
    uint64_t tMs = 0;
};

constexpr int kDigestCats = 4;   // categorias de resumos comparadas entre máquinas (story, actors, containers, objects no exemplo)

// ------------------------------------------------------------------ interface do alvo: encapsule SEU núcleo de sincronização nisto
class ITarget {
public:
    virtual ~ITarget() = default;
    virtual void apply(const Op& op) = 0;          // executa uma operação "agora" na máquina op.m
    virtual void advance(uint64_t toMs) = 0;       // avança o relógio virtual até toMs (o alvo atualiza suas máquinas e rede)
    virtual uint64_t now() const = 0;
    virtual void heal() = 0;                       // conexão perfeita, todos reconectados, nova atividade congelada
    virtual int machines() const = 0;
    virtual bool connected(int m) const = 0;
    virtual bool quiescent() const = 0;            // nada em trânsito, todos atualizados, atividade congelada
    virtual std::vector<Thing> view(int m) const = 0;   // tudo que a máquina m tem atualmente, ordenado por netId
    virtual uint64_t digest(int m, int cat) const = 0;  // hash do estado da máquina m para uma categoria; igual em todas as máquinas em repouso
    virtual uint64_t repairs(int m) const = 0;     // ações de reparo ou ressincronização realizadas pela máquina m até agora (contador, nunca diminui)
    virtual const std::vector<ApplyEvent>& applyLog() const = 0;
    virtual const std::vector<OwnEvent>& ownLog() const = 0;
    virtual std::map<std::string, uint64_t> stats() const = 0;   // contadores livres, impressos como cobertura
    // Interceptações opcionais.
    virtual void markQuiescent() {}                            // chamado uma vez ao atingir a quiescência
    virtual std::vector<Violation> nativeViolations() { return {}; }   // suas próprias verificações, mapeadas para os nomes de invariantes acima
};

// Base de conveniência: armazena os dois logs e contadores. Chame logApply para cada mensagem aplicada ou rejeitada por uma máquina e
// logOwn para cada decisão de autoridade. Uma aplicação rejeitada é contada como "reject_<why>" em stats().
class TargetBase : public ITarget {
public:
    const std::vector<ApplyEvent>& applyLog() const override { return apply_; }
    const std::vector<OwnEvent>& ownLog() const override { return own_; }
    std::map<std::string, uint64_t> stats() const override { return counters_; }

protected:
    void logApply(int machine, uint64_t idem, int ref, uint32_t epoch, uint32_t seq, int origin, ApplyKind k, bool accepted, uint32_t worldEpoch,
                  const std::string& why);
    void logOwn(OwnEvent::Kind k, int ref, int owner, int prev, uint32_t epoch);
    std::vector<ApplyEvent> apply_;
    std::vector<OwnEvent> own_;
    std::map<std::string, uint64_t> counters_;
    uint64_t ord_ = 0;
};

// ------------------------------------------------------------------ registro de alvos
// Um alvo se registra a partir de seu próprio arquivo .cpp com um TargetRegistrar estático (veja example/example_target.cpp).
struct TargetInfo {
    std::string name;
    std::string description;
    std::vector<std::string> bugs;   // nomes das classes de erros injetáveis (gêmeos mutantes)
    std::function<std::unique_ptr<ITarget>(const Scenario&, std::string*)> make;   // define *err e retorna null para erros desconhecidos
};
void registerTarget(TargetInfo info);
struct TargetRegistrar { explicit TargetRegistrar(TargetInfo info) { registerTarget(std::move(info)); } };
const TargetInfo* findTarget(const std::string& name);   // nome vazio = primeiro alvo registrado
std::vector<const TargetInfo*> allTargets();
std::unique_ptr<ITarget> makeTarget(const std::string& name, const Scenario& s, std::string* err = nullptr);
std::vector<std::string> knownBugs(const std::string& target);

// ------------------------------------------------------------------ oráculos
// Verificações por log (válidas a qualquer momento): double_apply, multi_owner, stale_applied, echo_adopted.
void checkLogs(const ITarget& t, std::vector<Violation>& out);
// Verificações de estado (só significativas quando o alvo está quiescente): converge, dup_thing.
void checkConverged(const ITarget& t, std::vector<Violation>& out);

// ------------------------------------------------------------------ executar / reduzir / relatar
struct RunResult {
    bool ok = true;
    std::vector<Violation> violations;
    std::map<std::string, uint64_t> stats;
    uint64_t virtualMs = 0;
    uint64_t opsRun = 0;
};
struct RunOptions {
    std::string target;                // vazio = alvo do cenário; caso contrário, alvo padrão
    uint32_t quiesceCapMs = 60000;     // espera máxima pela quiescência após restaurar a rede
    uint32_t afterQuiesceMs = 10000;   // reparos devem permanecer constantes por este tempo
    std::string reportDir;             // não vazio: em caso de falha, grava <name>.scenario.json e <name>.report.json aqui
    std::string reportName = "fail";
    std::string reportExtra;           // membros JSON brutos (sem chaves) acrescentados ao relatório, por exemplo, "\"shrunk_from_ops\": 500"
};
RunResult run(const Scenario& s, const RunOptions& opt);
// Reduz por depuração delta as operações (depois a conexão, a contagem de máquinas e a duração) a um cenário menor que ainda viole `invariant`.
Scenario shrink(const Scenario& s, const RunOptions& opt, const std::string& invariant, int* runs = nullptr);
bool writeReport(const ITarget& t, const Scenario& s, const RunResult& r, const std::string& dir, const std::string& name, const std::string& extra);

std::string fnvHex(const std::string& s);
std::string jsonEscape(const std::string& s);

}  // namespace coopfuzz
