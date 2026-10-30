// Metade permanente da separação para recarregamento a quente, sem jogo: nenhum cabeçalho do motor. Use por hotreload_loader.dll
// (loader_exports.h) ou vincule a biblioteca estática `hotreload_host` ao seu plugin e use CoreHost diretamente.
//
// Um CoreHost por processo. Mantém cópia privada em cache da DLL do núcleo, sequência de carga, descarga e recarga,
// armazenamento de blocos que sobrevive às recargas, métodos de controle (dev.status, dev.reload e os registrados pelo núcleo) e
// o pipe de controle.
//
// Por que cópia em cache: Windows não deixa sobrescrever DLL carregada na compilação. O carregador mapeia cópia privada
// (<cache>\<core stem>.<pid>.<n>.dll) e deixa o núcleo original desbloqueado para compilação e ferramenta de troca poderem
// substituí-lo a qualquer momento.
//
// ID de compilação: CRC-32 da cópia mapeada e seu tamanho, "a1b2c3d4-1981440". tools/hotreload/hotreload.py calcula o mesmo
// texto para o arquivo instalado, permitindo verificar como fato que "o núcleo em execução é a compilação que acabei de copiar".
//
// Threads: Start, Load, Reload, Service, OnFrame, OnMessage e Shutdown devem ser chamados na thread principal, entre
// quadros. RequestReload pode ser chamado de qualquer thread.
#pragma once
#include <atomic>
#include <cstdint>
#include <functional>
#include <map>
#include <memory>
#include <mutex>
#include <string>
#include <vector>

#include "hotreload/abi.h"
#include "hotreload/control_pipe.h"

namespace hotreload {

struct HostEnv {
    std::string corePath;   // DLL escrita pela compilação
    std::string cacheDir;   // "" = <diretório de corePath>\hr_cache
    std::string gameDir;    // passado ao núcleo, pode ser ""
    std::string pipeName;   // "" = sem pipe de controle
    std::string logPath;    // "" = <cacheDir>\hotreload.log
    void* userContext = nullptr;
};

struct ReloadResult {
    bool ok = false;
    bool rolledBack = false;   // novo núcleo falhou e o anterior voltou a executar
    bool coreDead = false;     // nada executando (reversão também falhou)
    std::string error;
    uint32_t generation = 0;   // geração em execução (0 se morto)
    std::string buildId;       // ID de compilação do núcleo em execução; "" se morto
    double msUnload = 0, msLoad = 0;
};

class CoreHost {
public:
    explicit CoreHost(HostEnv env);
    ~CoreHost();
    CoreHost(const CoreHost&) = delete;
    CoreHost& operator=(const CoreHost&) = delete;

    // Registra dev.status e dev.reload, inicia pipe de controle (se HostEnv::pipeName definido) e carrega núcleo.
    // False só se o pipe não pôde ser criado. Falha de carga do núcleo não é erro aqui (veja status()).
    bool Start(std::string& err);
    // Primeira carga (geração 1). Seguro chamar novamente após falha.
    bool Load(std::string& err);
    ReloadResult Reload(const char* reason);
    // Limite de quadro: executa solicitações de controle enfileiradas, recarregamento pendente e on_frame do núcleo.
    void OnFrame();
    void OnMessage(uint32_t type, void* data, uint32_t len);
    // Executa solicitação pendente de recarregamento (de RequestReload ou do núcleo). True se houve recarregamento.
    bool Service();
    // Descarregamento ordenado sem substituição (testes). Mesma sequência de repouso de Reload.
    bool Unload(std::string& err);
    // O processo está encerrando: para o pipe de controle. Não descarrega o núcleo (o sistema operacional o faz).
    void Shutdown();

    void RequestReload(const char* reason);

    // Método de controle pertencente ao host. Executa na thread principal e sobrevive a recarregamentos.
    void RegisterHostMethod(const std::string& name, HrMethodFn fn, void* user);

    bool loaded() const { return loaded_; }
    uint32_t generation() const { return generation_; }
    uint32_t reloadCount() const { return reloadCount_; }
    const std::string& coreBuildId() const { return cur_.buildId; }
    const std::string& lastError() const { return startError_; }
    std::string StatusJson() const;

    // ---- usado pelos callbacks da API ----
    struct Blob {
        std::vector<uint8_t> data;
        uint32_t version = 0;
    };
    std::mutex blobMu;
    std::map<std::string, Blob> blobs;
    std::atomic<bool> reloadPending{false};
    std::string pendingReason;
    std::mutex pendingMu;
    std::string vetoReason;
    void Log(const char* line);
    void RegisterMethod(const std::string& name, std::function<bool(const std::string&, std::string&)> fn, int owner);
    HrLoaderApi api{};

private:
    struct LoadedCore {
        void* module = nullptr;   // HMODULE
        std::string cachePath;
        std::string buildId;      // CRC-32 e tamanho da cópia em cache mapeada
        HrCoreApi core{};
    };
    bool LoadCoreFrom(const std::string& sourcePath, bool isReload, uint32_t generation, LoadedCore& out, std::string& err);
    void UnloadCore(LoadedCore& c);
    void CleanStaleCache();
    std::string MakeCachePath(uint32_t seq) const;
    void FillApi(uint32_t generation, bool isReload);
    void RegisterDevMethods();
    bool Dispatch(const std::string& method, const std::string& params, std::string& out, int& code);
    void UnregisterOwner(int owner);

    struct MethodEntry {
        std::function<bool(const std::string&, std::string&)> fn;
        int owner = 0;
    };

    HostEnv env_;
    LoadedCore cur_;
    std::string cachePath_;
    std::string coreDir_;
    std::string startError_;
    std::unique_ptr<ControlServer> control_;
    std::map<std::string, MethodEntry> methods_;
    bool loaded_ = false;
    bool devRegistered_ = false;
    uint32_t generation_ = 0;
    uint32_t reloadCount_ = 0;
    int depth_ = 0;   // > 0 dentro de chamada ao núcleo
    ReloadResult last_;
    std::string lastReason_;
    std::mutex logMu_;
};

CoreHost* Current();

}  // namespace hotreload
