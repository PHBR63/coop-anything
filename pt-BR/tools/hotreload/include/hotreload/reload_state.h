// Contrato de estado de recarregamento. Independente do jogo: sem cabeçalhos do motor nem Win32 neste cabeçalho.
//
// DLL de núcleo recarregável é descarregada e nova build é carregada no mesmo jogo em execução. Tudo que precisa sobreviver
// passa por este registro. Tudo que NÃO deve sobreviver (threads, hooks, sockets) é parado pelo
// `shutdown` de participante, e sondas de vazamentos conferem antes de carregador poder desmapear DLL.
//
// Sequência (integração em core_glue.h a conduz por before_unload e init do núcleo):
//   núcleo antigo : saveAll(blob)       cada participante grava estado versionado. Falha aborta recarregamento, núcleo antigo continua ativo.
//   núcleo antigo : drenagem               esperar até nenhuma thread (exceto as do núcleo) executar código do núcleo
//   núcleo antigo : shutdownAll()       ordem inversa: parar threads, remover hooks, fechar ou transferir sockets. Depois toda sonda de vazamentos é lida.
//   loader   : FreeLibrary(old), LoadLibrary(new)
//   núcleo novo : inicialização normal, depois restoreAll(blob)
//
// Blob é o que carregador mantém na memória entre os dois núcleos. São bytes simples: sem ponteiros, sem vtables, nada
// que aponte para DLL antiga. Handles do processo (SOCKET, HANDLE) podem ser armazenados como inteiros; permanecem válidos
// após desmapear, desde que shutdown() não os tenha fechado.
#pragma once
#include <cstdint>
#include <functional>
#include <memory>
#include <string>
#include <vector>

namespace hotreload {

using Bytes = std::vector<uint8_t>;

// Gravador e leitor de bytes little-endian. Leitor nunca lança exceções nem lê fora dos limites: após qualquer leitura curta
// ok() é falso e todo get posterior retorna zero ou vazio.
class Writer {
public:
    void u8(uint8_t v) { b_.push_back(v); }
    void u16(uint16_t v) { put(v, 2); }
    void u32(uint32_t v) { put(v, 4); }
    void u64(uint64_t v) { put(v, 8); }
    void i64(int64_t v) { put(static_cast<uint64_t>(v), 8); }
    void f64(double v);
    void boolean(bool v) { u8(v ? 1 : 0); }
    void str(const std::string& s);
    void bytes(const Bytes& v);
    void raw(const void* p, size_t n);
    const Bytes& data() const { return b_; }
    Bytes take() { return std::move(b_); }

private:
    void put(uint64_t v, int n) {
        for (int i = 0; i < n; ++i) b_.push_back(static_cast<uint8_t>(v >> (8 * i)));
    }
    Bytes b_;
};

class Reader {
public:
    Reader(const uint8_t* p, size_t n) : p_(p), n_(n) {}
    explicit Reader(const Bytes& b) : p_(b.data()), n_(b.size()) {}
    uint8_t u8() { return static_cast<uint8_t>(get(1)); }
    uint16_t u16() { return static_cast<uint16_t>(get(2)); }
    uint32_t u32() { return static_cast<uint32_t>(get(4)); }
    uint64_t u64() { return get(8); }
    int64_t i64() { return static_cast<int64_t>(get(8)); }
    double f64();
    bool boolean() { return u8() != 0; }
    std::string str();
    Bytes bytes();
    bool ok() const { return ok_; }
    size_t remaining() const { return n_ - pos_; }
    bool atEnd() const { return pos_ == n_; }

private:
    uint64_t get(int n);
    const uint8_t* p_;
    size_t n_, pos_ = 0;
    bool ok_ = true;
};

uint32_t crc32(const void* data, size_t n);

// Um por parte do estado que deve sobreviver a recarregamento (módulo, sessão, registro). Nomes únicos e estáveis entre builds.
struct Participant {
    const char* name = "";
    uint32_t version = 1;  // incrementar sempre que layout salvo mudar
    int order = 100;       // salvar e restaurar em ordem crescente, encerrar em decrescente

    // Verificação prévia opcional, executada antes de salvar ou parar algo. Retornar "" se módulo pode ser descarregado, senão o
    // motivo (por exemplo, "outro mod encadeou sobre um hook"). Recusa deixa núcleo antigo totalmente funcional.
    std::function<std::string()> canUnload;

    // Núcleo antigo ainda totalmente ativo. Gravar tudo de que novo núcleo precisa. Retornar false para vetar recarregamento.
    // Pode executar e depois ser descartado (etapa posterior pode recusar), então não deve mudar nada.
    std::function<bool(Writer&)> save;
    // Novo núcleo já executou inicialização normal. `savedVersion` só pode diferir de `version` se migrate não estiver definido.
    // Retornar false para rejeitar blob (participante então recorre a fresh()).
    std::function<bool(uint32_t savedVersion, Reader&)> restore;
    // Opcional: converter layout antigo. Se definido, chamado em vez de restore() quando savedVersion != version.
    std::function<bool(uint32_t savedVersion, Reader&)> migrate;
    // Parar threads, remover hooks, fechar sockets (ou deixar abertos os transferidos). Executa após todo salvamento ter sucesso e drenagem passar.
    std::function<void()> shutdown;
    // Opcional: começar do zero (sem blob, blob inválido, versão divergente sem migrate, restauração rejeitada).
    std::function<void()> fresh;
};

struct Report {
    std::vector<std::string> notes;     // legíveis por pessoas, uma linha cada
    std::vector<std::string> failures;  // qualquer coisa que torne recarregamento inseguro ou com perdas
    std::vector<std::string> leaks;     // sondas de vazamentos com leitura diferente de zero após encerramento
    int restored = 0, freshStarts = 0, migrated = 0, dropped = 0;
    bool ok() const { return failures.empty() && leaks.empty(); }
    std::string text() const;
};

// Sonda de vazamentos retorna quantos elementos continuam vivos (hooks instalados, threads executando, sockets abertos).
// `baseline` é o que está legitimamente vivo quando núcleo está ocioso.
struct LeakProbe {
    std::string name;
    std::function<int()> count;
    int baseline = 0;
};

class Registry {
public:
    // Registrar duas vezes sob mesmo nome substitui entrada anterior (repetição da inicialização estática não deve duplicar).
    void add(const Participant& p);
    void addLeakProbe(const LeakProbe& p);
    void clear();
    size_t size() const { return parts_.size(); }
    std::vector<std::string> names() const;
    uint32_t versionOf(const std::string& name) const;  // 0 = desconhecido

    // Núcleo antigo. False = recarregamento deve ser abortado e núcleo antigo mantido (nada foi encerrado).
    bool saveAll(Bytes* blob, Report* rep);
    // Núcleo antigo. Executa todo shutdown (um que lança exceção não para demais), depois lê toda sonda de vazamentos.
    // Retorna número de vazamentos. Carregador NÃO deve desmapear núcleo se diferente de zero.
    int shutdownAll(Report* rep);
    // Novo núcleo. Blob ausente, curto ou corrompido nunca é fatal: cada participante apenas recebe fresh().
    // Retorna false só quando blob inteiro era inutilizável.
    bool restoreAll(const Bytes& blob, Report* rep);

    // Para testes e chamadas de status: entradas (name, version) de um blob. False se blob estiver danificado.
    static bool inspect(const Bytes& blob, std::vector<std::pair<std::string, uint32_t>>* entries);

private:
    std::vector<Participant> parts_;
    std::vector<LeakProbe> probes_;
};

// Registro de uma DLL de núcleo em todo o processo. Cada núcleo carregado tem o próprio, pois registro vive na imagem do núcleo.
Registry& global();

struct Registrar {
    explicit Registrar(const Participant& p) { global().add(p); }
};
// Registrar participante na inicialização estática. Argumentos são campos de Participant em ordem:
//   name, version, order, canUnload, save, restore, migrate, shutdown, fresh   (os finais podem ser omitidos)
//   COOP_RELOAD_STATE(my_module, "my_module", 2, 50, nullptr, saveFn, restoreFn, migrateFn, shutdownFn, freshFn);
// Ou construir Participant e chamar hotreload::global().add(p) na inicialização.
#define COOP_RELOAD_STATE(ident, ...) \
    static const ::hotreload::Registrar hotreload_participant_##ident(::hotreload::Participant{__VA_ARGS__})

// ---- threads rastreadas -----------------------------------------------------------------------------------------------
// Toda thread iniciada por DLL de núcleo deve ser ManagedThread: destrutor pede parada e aguarda término, e liveThreads()
// é a sonda de vazamentos. Uma std::thread bruta (ou CreateThread) que sobreviva à sua DLL faz o jogo falhar assim que executa.
int liveThreads();

class ManagedThread {
public:
    ManagedThread() = default;
    ~ManagedThread() { stopAndJoin(); }
    ManagedThread(const ManagedThread&) = delete;
    ManagedThread& operator=(const ManagedThread&) = delete;
    // body(stopRequested): deve retornar logo após stopRequested() tornar-se verdadeiro.
    void start(const char* name, std::function<void(const std::function<bool()>& stopRequested)> body);
    void stopAndJoin();
    bool running() const;
    const std::string& name() const { return name_; }

private:
    struct State;
    std::shared_ptr<State> st_;
    std::string name_;
};

// IDs Windows das threads iniciadas por ManagedThread agora, mais adotadas. Drenagem de recarregamento
// as ignora: dono as para e aguarda término, e todo o resto que executa código do núcleo deve ter saído dele.
std::vector<unsigned long> managedThreadIds();

// Thread pertencente ao núcleo, mas não iniciada por ManagedThread: thread de trabalho iniciada por biblioteca vinculada, parada
// esperando trabalhos dentro do seu código. Dono a para e aguarda término no shutdown do participante (que executa após
// drenagem), então a drenagem deve ignorá-la como uma ManagedThread. TODA THREAD DO NÚCLEO DEVE SER REGISTRADA ASSIM OU
// SER UMA ManagedThread. Uma thread que não seja nenhuma das duas faz a drenagem recusar todo recarregamento, para sempre.
void adoptThread(unsigned long tid);
void releaseThread(unsigned long tid);

LeakProbe threadProbe();

}  // namespace hotreload
