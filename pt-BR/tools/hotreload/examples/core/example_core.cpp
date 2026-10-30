// Exemplo de núcleo recarregável. Copie este arquivo como ponto inicial de sua DLL de núcleo.
//
// Leva três tipos de coisas pela recarga e mostra regra de cada um:
//   estado   contador de quadros, contagem de ticks e rótulo. Salvos por participante de recarga com versão de layout e
//            restaurados pela próxima compilação (com etapa de migração quando layout mudar).
//   threads  uma ManagedThread (o ticker) e um "worker de biblioteca": std::thread comum representando uma thread que uma
//            biblioteca vinculada iniciou. Núcleo possui ambas. Primeira sem trabalho extra; segunda precisa ser
//            registrada com adoptThread(), senão drenagem recusa toda recarga.
//   métodos  example.state e example.set, métodos de controle chamados pelo host e testes de troca.
//
// Mesmo fonte compilado várias vezes com definições diferentes (veja CMakeLists.txt), para testes terem compilações que
// diferem em bytes e comportamento:
//   EX_BUILD        número embutido no binário, dando id próprio a cada compilação
//   EX_LAYOUT       versão de layout do estado salvo: 1, 2 ou 3
//   EX_MIGRATE      1 = esta compilação pode ler layout anterior (v2 lê v1)
//   EX_RAW_THREAD   1 = worker de biblioteca NÃO registrado por adoptThread (erro clássico)
//   EX_FAIL_SAVE    1 = segundo participante recusa salvar, então recarga deve ser recusada
//   EX_FAIL_INIT    1 = init falha, carregador precisa voltar ao núcleo anterior
#ifndef EX_BUILD
#define EX_BUILD 1
#endif
#ifndef EX_LAYOUT
#define EX_LAYOUT 1
#endif
#ifndef EX_MIGRATE
#define EX_MIGRATE 0
#endif
#ifndef EX_RAW_THREAD
#define EX_RAW_THREAD 0
#endif
#ifndef EX_FAIL_SAVE
#define EX_FAIL_SAVE 0
#endif
#ifndef EX_FAIL_INIT
#define EX_FAIL_INIT 0
#endif

#ifndef WIN32_LEAN_AND_MEAN
#define WIN32_LEAN_AND_MEAN
#endif
#include <windows.h>

#include <atomic>
#include <condition_variable>
#include <cstdio>
#include <mutex>
#include <string>
#include <thread>

#include "hotreload/abi.h"
#include "hotreload/control_pipe.h"
#include "hotreload/core_glue.h"
#include "hotreload/reload_state.h"

namespace {

const HrLoaderApi* g_api = nullptr;

// ---- estado: só thread principal toca, salvo g_ticks pertencente à thread ticker ----
uint64_t g_counter = 0;
std::string g_label = "unset";
uint32_t g_step = 1;
std::atomic<uint64_t> g_ticks{0};
uint64_t g_messages = 0;

// ---- threads. Alocadas no heap e nunca liberadas; nenhum destrutor estático faz join na saída do processo ----
hotreload::ManagedThread* g_ticker = new hotreload::ManagedThread();

struct LibWorker {
    std::thread th;
    std::mutex m;
    std::condition_variable cv;
    bool stop = false;
    unsigned long tid = 0;
};
LibWorker* g_worker = new LibWorker();

void startWorker() {
    LibWorker& w = *g_worker;
    w.stop = false;
    w.th = std::thread([&w] {
        std::unique_lock<std::mutex> lk(w.m);
        while (!w.stop) w.cv.wait_for(lk, std::chrono::milliseconds(2));   // parado dentro do código do núcleo, esperando tarefas
    });
    w.tid = GetThreadId(static_cast<HANDLE>(w.th.native_handle()));
#if !EX_RAW_THREAD
    hotreload::adoptThread(w.tid);   // A LIÇÃO: cada thread pertencente ao núcleo precisa ser registrada
#endif
}

void stopWorker() {
    LibWorker& w = *g_worker;
    if (!w.th.joinable()) return;
    {
        std::lock_guard<std::mutex> g(w.m);
        w.stop = true;
    }
    w.cv.notify_all();
    w.th.join();
    hotreload::releaseThread(w.tid);
    w.tid = 0;
}

void startTicker() {
    g_ticker->start("ticker", [](const std::function<bool()>& stopRequested) {
        while (!stopRequested()) {
            ++g_ticks;
            Sleep(2);
        }
    });
}

// ---- participante de recarga: layout versionado ----
bool save(hotreload::Writer& w) {
#if EX_LAYOUT == 1
    w.u64(g_counter);
    w.u64(g_ticks.load());
    w.str(g_label);
#elif EX_LAYOUT == 2
    w.u32(g_step);
    w.u64(g_counter);
    w.u64(g_ticks.load());
    w.str(g_label);
#else
    w.u8(0x7E);   // byte de indicador na frente: layout 3 não pode ser lido como layout 2
    w.u32(g_step);
    w.u64(g_counter);
    w.u64(g_ticks.load());
    w.str(g_label);
#endif
    return true;
}

bool restore(uint32_t, hotreload::Reader& r) {
#if EX_LAYOUT == 1
    g_counter = r.u64();
    g_ticks = r.u64();
    g_label = r.str();
#elif EX_LAYOUT == 2
    g_step = r.u32();
    g_counter = r.u64();
    g_ticks = r.u64();
    g_label = r.str();
#else
    if (r.u8() != 0x7E) return false;
    g_step = r.u32();
    g_counter = r.u64();
    g_ticks = r.u64();
    g_label = r.str();
#endif
    return true;
}

#if EX_MIGRATE
// Layout 2 incluiu `step`. Blob layout 1 não tem step, mantém padrão.
bool migrate(uint32_t savedVersion, hotreload::Reader& r) {
    if (savedVersion != 1) return false;
    g_counter = r.u64();
    g_ticks = r.u64();
    g_label = r.str();
    g_step = 1;
    return true;
}
#endif

void shutdown() {
    g_ticker->stopAndJoin();   // parar cada thread antes de seu código desaparecer
    stopWorker();
}

void fresh() {
    g_counter = 0;
    g_ticks = 0;
    g_label = "unset";
    g_step = 1;
}

#if EX_MIGRATE
COOP_RELOAD_STATE(example, "example", EX_LAYOUT, 50, nullptr, save, restore, migrate, shutdown, fresh);
#else
COOP_RELOAD_STATE(example, "example", EX_LAYOUT, 50, nullptr, save, restore, nullptr, shutdown, fresh);
#endif

#if EX_FAIL_SAVE
bool flakySave(hotreload::Writer&) { return false; }
COOP_RELOAD_STATE(flaky, "flaky", 1, 60, nullptr, flakySave, nullptr, nullptr, nullptr, nullptr);
#endif

// ---- métodos de controle ----
int methodState(void*, const char*, HrOut* out) {
    char b[512];
    std::snprintf(b, sizeof b,
                  "{\"layout\":%d,\"build\":%d,\"counter\":%llu,\"ticks\":%llu,\"step\":%u,\"label\":\"%s\",\"generation\":%u,\"isReload\":%u,"
                  "\"messages\":%llu,\"workerAlive\":%s,\"tickerRunning\":%s}",
                  EX_LAYOUT, EX_BUILD, static_cast<unsigned long long>(g_counter), static_cast<unsigned long long>(g_ticks.load()), g_step,
                  hotreload::JsonEscape(g_label).c_str(), g_api ? g_api->generation : 0u, g_api ? g_api->is_reload : 0u,
                  static_cast<unsigned long long>(g_messages), g_worker->th.joinable() ? "true" : "false", g_ticker->running() ? "true" : "false");
    out->set(out->h, b);
    return 1;
}

int methodSet(void*, const char* params, HrOut* out) {
    const std::string p = params ? params : "{}";
    std::string label;
    long long step = 0;
    if (hotreload::JsonGetString(p, "label", label)) g_label = label;
    if (hotreload::JsonGetInt(p, "step", step) && step > 0 && step < 1000) g_step = static_cast<uint32_t>(step);
    out->set(out->h, "true");
    return 1;
}

// ---- pontos de entrada do núcleo ----
int coreInit() {
#if EX_FAIL_INIT
    return 0;
#else
    g_api->log(("example core: build " + std::to_string(EX_BUILD) + ", layout " + std::to_string(EX_LAYOUT) + ", generation " + std::to_string(g_api->generation)).c_str());
    g_api->register_method("example.state", &methodState, nullptr);
    g_api->register_method("example.set", &methodSet, nullptr);
    startTicker();
    startWorker();
    return hotreload::AfterLoad(g_api) ? 1 : 0;   // restaura estado salvo (ou executa fresh() no início a frio)
#endif
}

void coreOnFrame() { g_counter += g_step; }
void coreOnMessage(uint32_t, void*, uint32_t) { ++g_messages; }
int coreBeforeUnload() { return hotreload::BeforeUnload(g_api) ? 1 : 0; }

}  // namespace

extern "C" __declspec(dllexport) int HotCore_Init(const HrLoaderApi* api, HrCoreApi* out) {
    if (!api || !out || api->abi_version != HR_ABI_VERSION) return 0;
    g_api = api;
    out->abi_version = HR_ABI_VERSION;
    out->size = sizeof(HrCoreApi);
    out->init = &coreInit;
    out->on_frame = &coreOnFrame;
    out->on_message = &coreOnMessage;
    out->before_unload = &coreBeforeUnload;
    return 1;
}
